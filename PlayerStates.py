from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import pygame
from parse_config import (PLAYER_Z_INDICES, JUMP_VELOCITY, GROUND_Y, 
                         PLAYER_COLLISION_FACTORS, PLAYER_CROUCH_DURATION)
from GameEnums import InputAction

if TYPE_CHECKING:
    from Onion import Onion

"""
State pattern implementation for player character behavior in the OnionRun game.
Defines running, jumping, and crouching states with their own animations, collision boxes,
and transition logic for clean behavior management.
"""

# Abstract class for player states
class PlayerState(ABC):
    """Abstract base class for player states"""
    
    @abstractmethod
    def enter(self, player: 'Onion') -> None:
        """Called when entering this state"""
        pass
    
    @abstractmethod
    def update(self, player: 'Onion', dt_seconds: float) -> None:
        """Update player in this state"""
        pass
    
    @abstractmethod
    def handle_input(self, player: 'Onion', action: InputAction) -> 'PlayerState':
        """Handle input and return the next state (or self to stay in the same state)"""
        pass
    
    @abstractmethod
    def get_state_name(self) -> str:
        """Get a state name for compatibility"""
        pass


class RunningState(PlayerState):
    """Player running state"""
    
    def enter(self, player: 'Onion') -> None:
        player.z_index = PLAYER_Z_INDICES["running"]
        
        # Set running animation
        bottom = player.rect.bottom
        centerx = player.rect.centerx
        player.anim_index = 1  # Center image
        player.image = player.images_running[player.anim_index]
        player.rect = player.running_rects[player.anim_index].copy()
        player.rect.centerx = centerx
        player.rect.bottom = bottom

        player.update_collision_rect \
        (
            PLAYER_COLLISION_FACTORS["width"], 
            PLAYER_COLLISION_FACTORS["height"]
        )
    
    def update(self, player: 'Onion', dt_seconds: float) -> None:
        player.z_index = PLAYER_Z_INDICES["running"]
        
        # Handle running animation
        player.anim_timer += dt_seconds * 1000  # dt_seconds in ms
        if player.anim_timer >= player.anim_delay:
            player.anim_timer -= player.anim_delay
            player.anim_index = (player.anim_index + 1) % len(player.images_running)

            bottom = player.rect.bottom
            centerx = player.rect.centerx
            player.image = player.images_running[player.anim_index]
            player.rect = player.running_rects[player.anim_index].copy()
            player.rect.centerx = centerx
            player.rect.bottom = bottom

            player.update_collision_rect \
            (
                PLAYER_COLLISION_FACTORS["width"], 
                PLAYER_COLLISION_FACTORS["height"]
            )
    
    def handle_input(self, player: 'Onion', action: InputAction) -> 'PlayerState':
        if action == InputAction.JUMP:
            return JumpingState()
        elif action == InputAction.CROUCH:
            return CrouchingState()
        return self
    
    def get_state_name(self) -> str:
        return "running"


class JumpingState(PlayerState):
    """Player jumping state"""
    
    def enter(self, player: 'Onion') -> None:
        player.jump_velocity = JUMP_VELOCITY  # Initial velocity upward
        player.z_index = PLAYER_Z_INDICES["jumping"]
        
        center = player.rect.center
        player.image = player.image_jump
        player.rect = player.jump_rect.copy()
        player.rect.center = center

        player.update_collision_rect \
        (
            PLAYER_COLLISION_FACTORS["jump_width"],
            PLAYER_COLLISION_FACTORS["jump_height"]
        )
    
    def update(self, player: 'Onion', dt_seconds: float) -> None:
        player.z_index = PLAYER_Z_INDICES["jumping"]
        player.jump_velocity += player.gravity * dt_seconds * player.fps
        player.rect.y += player.jump_velocity * dt_seconds * player.fps
        player.collision_rect.center = player.rect.center

        # Check if landed
        if player.rect.bottom >= GROUND_Y and player.jump_velocity > 0:
            player.rect.bottom = GROUND_Y
            # Will transition to running state in the next frame
    
    def handle_input(self, player: 'Onion', action: InputAction) -> 'PlayerState':
        # Check if landed and should transition to running
        if player.rect.bottom >= GROUND_Y and player.jump_velocity > 0:
            return RunningState()
        
        # Can crouch while jumping to fast-fall
        if action == InputAction.CROUCH:
            player.jump_velocity = 0
            player.rect.bottom = GROUND_Y
            return RunningState()
        
        return self
    
    def get_state_name(self) -> str:
        return "jumping"


class CrouchingState(PlayerState):
    """Player-crouching state"""
    
    def __init__(self):
        self.crouch_timer = 0
    
    def enter(self, player: 'Onion') -> None:
        # If it was jumping, land immediately
        if hasattr(player, 'jump_velocity'):
            player.jump_velocity = 0
            player.rect.bottom = GROUND_Y
        
        player.z_index = PLAYER_Z_INDICES["crouching"]
        self.crouch_timer = pygame.time.get_ticks()

        bottom = player.rect.bottom
        centerx = player.rect.centerx
        player.image = player.image_crouch
        player.rect = player.image.get_rect()
        player.rect.centerx = centerx
        player.rect.bottom = bottom
        
        player.update_collision_rect \
        (
            PLAYER_COLLISION_FACTORS["crouch_width"], 
            PLAYER_COLLISION_FACTORS["crouch_height"], 
            align_bottom=True
        )
        player.collision_rect.centerx = player.rect.centerx
    
    def update(self, player: 'Onion', dt_seconds: float) -> None:
        player.z_index = PLAYER_Z_INDICES["crouching"]
        
        # Check if crouch duration is over
        current_time = pygame.time.get_ticks()
        if current_time - self.crouch_timer >= PLAYER_CROUCH_DURATION:
            # Will transition to running state in the next frame
            pass
    
    def handle_input(self, player: 'Onion', action: InputAction) -> 'PlayerState':
        # Check if crouch duration is over
        current_time = pygame.time.get_ticks()
        if current_time - self.crouch_timer >= PLAYER_CROUCH_DURATION:
            return RunningState()
        
        # Can jump while crouching
        if action == InputAction.JUMP:
            return JumpingState()
        
        return self
    
    def get_state_name(self) -> str:
        return "crouching"