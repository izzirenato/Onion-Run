import pygame
from parse_config import ASSETS

"""
Manages game assets (images and fonts) including:
- Player sprite retrieval based on skin and animation state
- Obstacle sprite management
- Automatic caching to prevent redundant loading
"""


class AssetManager:
    """Simple asset manager with caching"""
    
    def __init__(self):
        self.image_cache = {}
        self.font_cache = {}
    
    def load_image(self, path: str) -> pygame.Surface:
        """Load an image with error handling"""
        # Check cache
        if path in self.image_cache:
            return self.image_cache[path]
        
        try:
            # Load image
            surface = pygame.image.load(path)
            # Optimize surface
            if surface.get_alpha():
                surface = surface.convert_alpha()
            else:
                surface = surface.convert()
            
            # Save to cache
            self.image_cache[path] = surface
            return surface
            
        except Exception:
            # Create magenta placeholder on error
            placeholder = pygame.Surface((64, 64))
            placeholder.fill((255, 0, 255))
            return placeholder
    
    def load_font(self, path: str, size: int) -> pygame.font.Font:
        """Load a font with error handling"""
        cache_key = f"{path}_{size}"
        
        # Check cache
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]
        
        try:
            font = pygame.font.Font(path, size)
            self.font_cache[cache_key] = font
            return font
        except Exception:
            # Use system font if error
            font = pygame.font.Font(None, size)
            self.font_cache[cache_key] = font
            return font
    
    def get_player_images(self, skin: str, state: str):
        """Get player images for skin and state"""
        skin_key = skin.upper().replace(" ", "_")
        
        try:
            player_assets = ASSETS["IMAGES"]["PLAYER"]
            
            if state == "running":
                return \
                [
                    self.load_image(player_assets[skin_key]["LEFT_FOOT_UP"]),
                    self.load_image(player_assets[skin_key]["BACK"]),
                    self.load_image(player_assets[skin_key]["RIGHT_FOOT_UP"])
                ]
            elif state == "jump":
                return self.load_image(player_assets[skin_key]["JUMP"])
            elif state == "crouch":
                return self.load_image(player_assets[skin_key]["CROUCH"])
        except Exception:
            # Fallback to default skin
            if skin != "the_onion":
                return self.get_player_images("the_onion", state)
            # If default also fails, create placeholder
            placeholder = pygame.Surface((32, 32))
            placeholder.fill((0, 255, 0))
            return placeholder
    
    def get_obstacle_image(self, obstacle_type: str) -> pygame.Surface:
        """Get obstacle image"""
        try:
            obstacle_assets = ASSETS["IMAGES"]["OBSTACLES"]
            
            type_mapping = \
            {
                "pan": "PAN",
                "knife_block": "KNIFE_BLOCK", 
                "cabbage": "CABBAGE"
            }
            
            config_key = type_mapping.get(obstacle_type, "PAN")
            return self.load_image(obstacle_assets[config_key])
        except Exception:
            # Red placeholder for obstacles
            placeholder = pygame.Surface((32, 32))
            placeholder.fill((255, 0, 0))
            return placeholder