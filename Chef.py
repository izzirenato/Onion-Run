import pygame
from parse_config import LANES, HEIGHT, FPS, ASSETS
from AssetManager import AssetManager

"""
Chef enemy character for the OnionRun game.
Chases the player down the screen, following their lane movements with animated sprites
at the start of the game.
"""

# Constants
CHEF_VERTICAL_OFFSET = 150
CHEF_SPEED = 0.6
CHEF_ANIMATION_DELAY = 160
CHEF_Z_INDEX = 30
CHEF_MOVEMENT_FACTOR = 0.1


class Chef(pygame.sprite.Sprite):
    # ctor with optional AssetManager; defaults to None if not provided
    def __init__(self, asset_manager: AssetManager = None):
        super().__init__()
        
        self.asset_manager = asset_manager or AssetManager()
        
        # Load images using AssetManager
        self.images_chasing = [
            self.asset_manager.load_image(ASSETS['IMAGES']['CHEF']['LEFT']),
            self.asset_manager.load_image(ASSETS['IMAGES']['CHEF']['BACK']),
            self.asset_manager.load_image(ASSETS['IMAGES']['CHEF']['RIGHT']),
        ]

        # Pre-calculate rects for all animation frames
        self.image_rects = [img.get_rect() for img in self.images_chasing]

        self.image = self.images_chasing[1]
        self.rect = self.image.get_rect()
        self.z_index = CHEF_Z_INDEX

        self.rect.bottom = HEIGHT - CHEF_VERTICAL_OFFSET
        self.rect.centerx = LANES[1]

        self.speed = CHEF_SPEED
        self.current_lane = 1

        self.animation_timer = 0
        self.animation_delay = CHEF_ANIMATION_DELAY
        self.current_image_index = 0


    # updates the chef image following the player
    def update(self, dt_seconds, player):
        # update lane position to follow player
        if self.current_lane > player.current_lane:
            self.current_lane -= 1
        elif self.current_lane < player.current_lane:
            self.current_lane += 1

        # move smoothly towards the target position
        target_x = LANES[self.current_lane]
        self.rect.centerx += (target_x - self.rect.centerx) * CHEF_MOVEMENT_FACTOR * dt_seconds * FPS
        self.rect.y += self.speed * dt_seconds * FPS

        # remove the chef when it goes below the screen
        if self.rect.top > HEIGHT:
            self.kill()

        # Update animation
        self.animation_timer += dt_seconds * 1000  # Convert seconds to ms
        if self.animation_timer >= self.animation_delay:
            self.animation_timer -= self.animation_delay
            self.current_image_index = (self.current_image_index + 1) % len(self.images_chasing)

            # Keep current position when changing animation frame
            current_pos = self.rect.center
            self.image = self.images_chasing[self.current_image_index]
            self.rect = self.image_rects[self.current_image_index].copy()
            self.rect.center = current_pos