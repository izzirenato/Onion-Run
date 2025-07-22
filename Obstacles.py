import pygame
import random
from parse_config import LANES, HEIGHT, SPEED, FPS, OBSTACLE_Z_INDICES
from AssetManager import AssetManager

"""
Obstacle sprite system for the OnionRun game.
Defines three obstacle types (pan, cabbage, knife block) with unique collision rules
and avoidance mechanics, designed for object pool reuse.
"""

class Obstacles(pygame.sprite.Sprite):
    """Game obstacle sprite with collision detection"""

    def __init__(self, lane):
        super().__init__()
        self.asset_manager = AssetManager()
        self.lane = None
        self.type = None
        self.should_remove = False
        self.speed = SPEED
        self.z_index = 0
        self.collision_rect = None
        self.image = None
        self.rect = None
        self.reset(lane)
    
    def reset(self, lane):
        """Reset obstacle for reuse from pool"""
        self.lane = lane
        self.type = random.choice(["pan", "knife_block", "cabbage"])
        
        # Mark for removal when off-screen
        self.should_remove = False

        # Load image using the asset manager
        self.image = self.asset_manager.get_obstacle_image(self.type)

        # Set z-index based on the obstacle type
        # Use z-index from config
        self.z_index = OBSTACLE_Z_INDICES.get(self.type, OBSTACLE_Z_INDICES["default"])

        # Set the initial position
        self.rect = self.image.get_rect()
        self.rect.centerx = LANES[lane]
        self.rect.bottom = 0
        self.speed = SPEED
        
        # Setup collision rectangle
        self.setup_collision_rect()
    
    def setup_collision_rect(self):
        """Set up a collision rectangle based on an obstacle type"""
        if self.type == "knife_block":
            self.collision_rect = self.rect.copy()
            self._update_knife_collision_rect()
        else:
            self.collision_rect = self.rect
    
    def _update_knife_collision_rect(self):
        """Update knife block collision rectangle"""
        self.collision_rect.height = self.rect.height // 2
        self.collision_rect.bottom = self.rect.bottom
        self.collision_rect.width = int(self.rect.width * 0.8)
        self.collision_rect.centerx = self.rect.centerx

    def update(self, dt_seconds):
        """Update obstacle position and collision rect"""
        # Moves obstacle down
        self.rect.y += self.speed * dt_seconds * FPS
        
        # Update collision rectangle for knife_block to maintain the bottom half
        if self.type == "knife_block":
            self._update_knife_collision_rect()
        
        # Mark for removal if off-screen
        if self.rect.top > HEIGHT + 100:
            self.should_remove = True

        # Remove when off the viewport
        if self.rect.top > HEIGHT:
            self.kill()