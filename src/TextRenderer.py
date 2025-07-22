import pygame
from typing import Tuple, Optional
from parse_config import *

"""
Text rendering utility system for the OnionRun game.
Provides centralized text rendering with font caching, multiple size presets,
and optional background boxes for consistent UI across the game.
"""

class TextRenderer:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.cache = {}
        
        # Initialize font sizes (in order from smallest to largest)
        self.micro_size = UI["FONT_SIZES"]["MICRO"]     # 10
        self.mini_size = UI["FONT_SIZES"]["MINI"]       # 12
        self.tiny_size = UI["FONT_SIZES"]["TINY"]       # 14
        self.small_size = UI["FONT_SIZES"]["SMALL"]     # 18
        self.normal_size = UI["FONT_SIZES"]["NORMAL"]   # 24
        self.medium_size = UI["FONT_SIZES"]["MEDIUM"]   # 28
        self.subtitle_size = UI["FONT_SIZES"]["SUBTITLE"] # 32
        self.large_size = UI["FONT_SIZES"]["LARGE"]     # 36
        self.bigger_size = UI["FONT_SIZES"]["BIGGER"]   # 42
        self.title_size = UI["FONT_SIZES"]["TITLE"]     # 48

    def get_font(self, size: int) -> pygame.font.Font:
        """Get a font of specified size, cache for reuse"""
        if size not in self.cache:
            try:
                self.cache[size] = pygame.font.Font(ASSETS["FONTS"]["MAIN"], size)
            except (pygame.error, FileNotFoundError):
                self.cache[size] = pygame.font.Font(None, size)
        return self.cache[size]

    def get_text_surface(self, text: str, size: int, color: Tuple[int, ...]) -> pygame.Surface:
        """Get rendered text surface with simple caching"""
        key = (text, size, color)
        
        if key not in self.cache:
            font = self.get_font(size)
            self.cache[key] = font.render(text, True, color)
        
        return self.cache[key]

    def draw_text(self, text: str, size: int, color: Tuple[int, ...], x: int, y: int, 
                 center: bool = True, font_arg: Optional[pygame.font.Font] = None, 
                 bg_color: Optional[Tuple[int, ...]] = None, padding: int = 0, 
                 width: Optional[int] = None) -> Optional[pygame.Rect]:
        """Draw text with optional background"""
        if font_arg is None:
            text_surface = self.get_text_surface(text, size, color)
        else:
            text_surface = font_arg.render(text, True, color)

        rect = text_surface.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)

        bg_rect = None
        if bg_color:
            bg_rect = rect.copy()
            bg_rect.inflate_ip(padding * 2, padding * 2)
            if width:
                original_width = bg_rect.width
                bg_rect.width = width
                if center:
                    bg_rect.centerx = x
                if width > original_width:
                    rect.centerx = bg_rect.centerx
            
            pygame.draw.rect(self.screen, bg_color, bg_rect)
            pygame.draw.rect(self.screen, COLORS["DARK_GREY"], bg_rect, 2)
        
        self.screen.blit(text_surface, rect)
        return bg_rect

    def clear_cache(self) -> None:
        """Clear the cache"""
        self.cache.clear()