import pygame
from parse_config import COLLISION_DISTANCE_THRESHOLD

"""
Collision detection system for the OnionRun game.
Handles player-obstacle collisions with lane-based detection and obstacle-specific rules
(pan: crouch to avoid, cabbage: jump to avoid, knife block: change lane to avoid).
"""

class CollisionSystem:
    """Collision detection system"""
    
    @staticmethod
    def check_collision(player, obstacles: pygame.sprite.Group) -> bool:
        """Check if the player collides with any obstacle"""
        player_rect = player.collision_rect
        
        for obstacle in obstacles:
            if CollisionSystem._check_single_collision(player, obstacle, player_rect):
                return True
        
        return False
    
    @staticmethod
    def _check_single_collision(player, obstacle, player_rect: pygame.Rect) -> bool:
        """Check collision between player and single obstacle"""
        # Get obstacle collision rectangle (custom for knife_block, regular rect for others)
        obstacle_rect = getattr(obstacle, 'collision_rect', obstacle.rect)
        
        # Skip if too far apart vertically
        if (obstacle_rect.top - player_rect.bottom > COLLISION_DISTANCE_THRESHOLD or 
            player_rect.top - obstacle_rect.bottom > COLLISION_DISTANCE_THRESHOLD):
            return False

        # Lane-based collision: must be in the same lane for collision
        if player.current_lane != obstacle.lane:
            return False

        # Z-index "behind" mechanic: if the player is behind an obstacle vertically, no collision
        # This handles the knife_block "behind" mechanic for all obstacles
        if player.z_index < obstacle.z_index and player_rect.centery >= obstacle_rect.centery:
            return False

        # Rectangle collision check
        if not player_rect.colliderect(obstacle_rect):
            return False
        
        # Apply obstacle-specific collision rules
        return CollisionSystem._check_obstacle_specific_rules(player, obstacle)

    @staticmethod
    def _check_obstacle_specific_rules(player, obstacle) -> bool:
        """Apply obstacle-specific collision rules"""
        # Simple collision rules based on the obstacle type
        if obstacle.type == "pan":
            # Pan: avoid by crouching
            return player.state != "crouching"
        elif obstacle.type == "cabbage":
            # Cabbage: avoid by jumping
            return player.state != "jumping"
        elif obstacle.type == "knife_block":
            # Knife block: can pass behind if positioned correctly
            player_rect = player.collision_rect
            obstacle_rect = obstacle.collision_rect
            # If a player is behind the knife block, allow passing
            if player_rect.centery > obstacle_rect.bottom + 10:
                return False
            return True
        else:
            # Default: collision occurs
            return True

