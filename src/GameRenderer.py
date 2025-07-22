import pygame
from parse_config import *
from TextRenderer import TextRenderer

"""
Game rendering system for the OnionRun gameplay screen.
Handles sprite rendering with viewport culling, pause overlays, and in-game UI elements
like score display and control hints.
"""

class GameRenderer(TextRenderer):
    def __init__(self, screen):
        super().__init__(screen)
        # Cache expensive surfaces
        self.pause_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.pause_overlay.fill(COLORS["TRANSPARENT_BLACK"])


    def render_game(self, game_background, sorted_sprites, score, paused, resuming, pause_timer, pause_duration):
        game_background.draw(self.screen)
        
        # Sprite culling - only render visible sprites
        viewport_buffer = 100  # Buffer for smooth transitions
        viewport_rect = pygame.Rect(-viewport_buffer, -viewport_buffer, 
                                   WIDTH + 2 * viewport_buffer, HEIGHT + 2 * viewport_buffer)
        
        for sprite in sorted_sprites:
            # Only render sprites that are visible or close to viewport
            if viewport_rect.colliderect(sprite.rect):
                self.screen.blit(sprite.image, sprite.rect)
        
        if paused:
            self.render_pause_overlay(resuming, pause_timer, pause_duration)
        else:
            self.render_game_ui(score)

    def render_pause_overlay(self, resuming, pause_timer, pause_duration):
        # Use cached pause overlay
        self.screen.blit(self.pause_overlay, (0, 0))
        
        if resuming:
            seconds_remaining = max(0, (pause_duration - pause_timer) // 1000) + 1
            countdown_text = f"Resuming in {seconds_remaining:.0f}"
            self.draw_text(countdown_text, self.large_size, COLORS["ORANGE"], WIDTH // 2, HEIGHT // 3)
        else:
            self.draw_text("PAUSED", self.title_size, COLORS["ORANGE"], WIDTH // 2, HEIGHT // 3)
            self.draw_text("Press SPACE to continue", self.normal_size, COLORS["ORANGE"], WIDTH // 2, HEIGHT // 3 + 50)
            self.draw_text("Press ESC to return to menu", self.small_size, (*COLORS["ORANGE"], 180), WIDTH // 2, HEIGHT - 35)

    def render_game_ui(self, score):
        score_text = f"Score: {int(score)}"
        self.draw_text(score_text, self.mini_size, COLORS["WHITE"], UI["SCORE_BOX"]["X"], UI["SCORE_BOX"]["Y"], 
                      bg_color=COLORS["PURPLE"], padding=5, width=UI["SCORE_BOX"]["WIDTH"])
        
        controls_bg_rect = self.draw_text("Controls", self.mini_size, COLORS["WHITE"], 
                                         WIDTH - UI["CONTROLS_BOX"]["X"], UI["CONTROLS_BOX"]["Y"],
                                         bg_color=COLORS["PURPLE"], padding=5, width=UI["CONTROLS_BOX"]["WIDTH"])
        
        if controls_bg_rect:
            y_offset = controls_bg_rect.bottom + 5
            instructions = ["↑ / W: Jump", "↓ / S: Crouch", "← / A: Left", "→ / D: Right", "SPACE: Pause"]
            
            instr_bg_rect = pygame.Rect(WIDTH - UI["CONTROLS_BOX"]["WIDTH"], y_offset, 
                                       UI["CONTROLS_BOX"]["WIDTH"], len(instructions) * 22 + 10)
            pygame.draw.rect(self.screen, (*COLORS["PURPLE"], 180), instr_bg_rect)
            pygame.draw.rect(self.screen, COLORS["DARK_GREY"], instr_bg_rect, 2)
            
            for i, instr in enumerate(instructions):
                self.draw_text(instr, self.micro_size, COLORS["WHITE"], 
                              WIDTH - UI["CONTROLS_BOX"]["X"], y_offset + 15 + (i * 22))

