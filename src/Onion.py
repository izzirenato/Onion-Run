import pygame
from typing import List, TYPE_CHECKING
from parse_config import (LANES, GROUND_Y, FPS, GRAVITY, PLAYER_Z_INDICES, 
                          PLAYER_COLLISION_FACTORS, PLAYER_MOVEMENT_FACTOR, 
                          PLAYER_ANIMATION_DELAY, PLAYER_CROUCH_DURATION)
from AssetManager import AssetManager
from PlayerStates import PlayerState, RunningState
from GameEnums import InputAction


# Used only for type checking (editors), not actually imported when running
if TYPE_CHECKING:
    from pygame import Surface, Rect

"""
Player character class for the OnionRun game.
Implements state-based behavior (running, jumping, crouching) with smooth lane switching,
animated sprites, and support for multiple skins.
"""

class Onion(pygame.sprite.Sprite):
    """Player character class with state-based behavior"""
    
    def __init__(self, skin: str = "the_onion") -> None:
        super().__init__()
        self.skin: str = skin
        self.asset_manager: AssetManager = AssetManager()

        # Load images using centralized asset manager
        self.images_running: List['Surface'] = self.asset_manager.get_player_images(skin, "running")
        self.image_jump: 'Surface' = self.asset_manager.get_player_images(skin, "jump")
        self.image_crouch: 'Surface' = self.asset_manager.get_player_images(skin, "crouch")

        # Pre-calculate rectangles for each frame
        self.running_rects: List['Rect'] = [img.get_rect() for img in self.images_running]
        self.jump_rect: 'Rect' = self.image_jump.get_rect()
        self.crouch_rect: 'Rect' = self.image_crouch.get_rect()

        # Set initial image and position
        self.image: 'Surface' = self.images_running[1]
        self.rect: 'Rect' = self.image.get_rect()
        self.current_lane: int = 1
        self.rect.centerx = LANES[self.current_lane]
        self.rect.bottom = GROUND_Y

        # Animation variables
        self.anim_index: int = 0
        self.anim_timer: float = 0.0
        self.anim_delay: int = PLAYER_ANIMATION_DELAY  # in ms

        # State pattern implementation
        self.state_obj: PlayerState = RunningState()
        self.state_obj.enter(self)

        # Physics variables for jumping
        self.jump_velocity: float = 0.0
        self.gravity: float = GRAVITY
        self.fps: int = FPS  # Store for state access

        # Variables for animation
        self.crouch_duration: int = PLAYER_CROUCH_DURATION  # ms
        self.crouch_timer: int = 0

        # Custom hitbox (collision_rect)
        self.collision_rect: 'Rect'
        self.update_collision_rect(PLAYER_COLLISION_FACTORS["width"], PLAYER_COLLISION_FACTORS["height"])

        # z-index for drawing order:
        # When running or jumping, must be above obstacles
        # When crouching, can be lower
        self.z_index: int = PLAYER_Z_INDICES["running"]
        
        # Pre-calculate movement factor for performance
        self.movement_factor: float = PLAYER_MOVEMENT_FACTOR * FPS
    
    @property
    def state(self) -> str:
        """Compatibility property for accessing state name"""
        return self.state_obj.get_state_name()
    
    def change_state(self, new_state: PlayerState):
        """Change to a new state"""
        self.state_obj = new_state
        self.state_obj.enter(self)

    def update_collision_rect(self, width_factor: float, height_factor: float, align_bottom: bool = False) -> None:
        """Update collision rectangle with given scale factors"""
        self.collision_rect = self.rect.copy()
        self.collision_rect.width = int(self.rect.width * width_factor)
        self.collision_rect.height = int(self.rect.height * height_factor)
        
        if align_bottom:
            self.collision_rect.bottom = self.rect.bottom
        else:
            self.collision_rect.center = self.rect.center

    def move_left(self):
        """Change lane to the left smoothly"""
        if self.current_lane > 0:
            self.current_lane -= 1
            # Don't move self.rect.centerx immediately, interpolation is handled in update()

    def move_right(self):
        """Change lane to the right smoothly"""
        if self.current_lane < len(LANES) - 1:
            self.current_lane += 1

    def start_jump(self):
        """Start jumping state"""
        new_state = self.state_obj.handle_input(self, InputAction.JUMP)
        if new_state != self.state_obj:
            self.change_state(new_state)

    def start_crouch(self):
        """Start crouching state"""
        new_state = self.state_obj.handle_input(self, InputAction.CROUCH)
        if new_state != self.state_obj:
            self.change_state(new_state)

    def update(self, dt_seconds: float):
        """Update the state, position and animation of the player"""
        # Smooth movement between lanes:
        target_x = LANES[self.current_lane]
        self.rect.centerx += int((target_x - self.rect.centerx) * self.movement_factor * dt_seconds)
        self.collision_rect.centerx = self.rect.centerx

        # Update current state
        self.state_obj.update(self, dt_seconds)
        
        # Check for state transitions based on current conditions
        new_state = self.state_obj.handle_input(self, None)  # Check automatic transitions
        if new_state != self.state_obj:
            self.change_state(new_state)