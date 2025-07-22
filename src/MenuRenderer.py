import pygame
from parse_config import *
from TextRenderer import TextRenderer

"""
Menu and UI rendering system for the OnionRun game.
Renders main menu, skin selection with unlock status, and game over screens
with score displays and special effects for new records.
"""

class MenuRenderer(TextRenderer):
    def __init__(self, screen):
        super().__init__(screen)
        
        try:
            self.menu_background = pygame.image.load(ASSETS["IMAGES"]["MENU_BG"]).convert()
        except (pygame.error, FileNotFoundError) as _:
            print(f"Error loading menu background: {_}")
            self.menu_background = pygame.Surface((WIDTH, HEIGHT))
            self.menu_background.fill(COLORS["BLACK"])
            
        try:
            self.game_over_background = pygame.image.load(ASSETS["IMAGES"]["GAME_OVER_BG"]).convert()
        except (pygame.error, FileNotFoundError) as _:
            print(f"Error loading game over background: {_}")
            self.game_over_background = pygame.Surface((WIDTH, HEIGHT))
            self.game_over_background.fill(COLORS["DARK_RED"])
            
        self.dark_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.dark_overlay.fill(COLORS["TRANSPARENT_BLACK"])
        
        # Cache expensive surfaces
        self.game_over_overlay = None


    def render_menu(self, record_score, show_press_enter):
        self.screen.blit(self.menu_background, (0, 0))
        
        record_text = f"High Score: {record_score}"
        self.draw_text(record_text, self.normal_size, COLORS["TRANSPARENT_WHITE"], WIDTH // 2, HEIGHT - 35)
        
        if show_press_enter:
            oval_rect = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 5 * 4 - 50, UI["OVAL_BUTTON"]["WIDTH"], UI["OVAL_BUTTON"]["HEIGHT"])
            pygame.draw.ellipse(self.screen, (*COLORS["BROWN"], 128), oval_rect)
            pygame.draw.ellipse(self.screen, COLORS["GREY"], oval_rect, 3)
            self.draw_text("Press ENTER to start", self.normal_size, COLORS["BLACK"], WIDTH // 2, HEIGHT // 5 * 4)

    def render_skin_selection(self, selected_skin, skin_previews, record_score, show_press_enter, can_use_skin):
        self.screen.blit(self.menu_background, (0, 0))
        self.screen.blit(self.dark_overlay, (0, 0))
        
        text_rect = self.draw_text("SELECT SKIN", self.subtitle_size, COLORS["BROWN"], WIDTH // 2, HEIGHT // 10 * 3,
                                  bg_color=COLORS["BLACK"], padding=30)
        pygame.draw.rect(self.screen, COLORS["WHITE"], text_rect.inflate(20, 20), 3)
        
        preview = skin_previews[selected_skin]
        preview_scaled = pygame.transform.scale(preview, (preview.get_width() * 3, preview.get_height() * 3))
        preview_rect = preview_scaled.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(preview_scaled, preview_rect)
        
        skin_name = selected_skin.capitalize()
        if skin_name == "The_onion":
            skin_name = "The onion"
        self.draw_text(skin_name, self.bigger_size, COLORS["WHITE"], WIDTH // 2, HEIGHT // 2 + 120)
        
        record_text = f"High Score: {record_score}"
        self.draw_text(record_text, self.normal_size, COLORS["BROWN"], WIDTH // 2, HEIGHT - 75)
        
        self.draw_text("← ", self.large_size, COLORS["WHITE"], WIDTH // 4, HEIGHT // 2)
        self.draw_text(" →", self.large_size, COLORS["WHITE"], WIDTH // 4 * 3, HEIGHT // 2)
        
        if can_use_skin:
            if show_press_enter:
                self.draw_text("Press ENTER to play", self.normal_size, COLORS["BROWN"], WIDTH // 2, HEIGHT - 35)
        else:
            unlock_score = PURPLE_UNLOCK_SCORE if selected_skin == "purple" else WHITE_UNLOCK_SCORE
            unlock_text = f"Locked (Unlock at {unlock_score} points)"
            self.draw_text(unlock_text, self.small_size, COLORS["TRANSPARENT_WHITE"], WIDTH // 2, HEIGHT - 35)

    def render_game_over(self, score, record_score, flash_color_red, flash_color_grey, is_new_record):
        self.screen.blit(self.game_over_background, (0, 0))
        
        self.draw_text("GAME OVER", self.title_size, flash_color_red, WIDTH // 2, HEIGHT // 3)
        self.draw_text("Press R to restart", self.tiny_size, flash_color_grey, WIDTH // 2, HEIGHT - 50)
        self.draw_text("Press M for menu", self.tiny_size, flash_color_grey, WIDTH // 2, HEIGHT - 25)
        
        if is_new_record:
            self.render_new_record(record_score, flash_color_red)
        else:
            self.render_regular_game_over(score, record_score)

    def render_new_record(self, record_score, flash_color_red):
        record_text = f"New Record! {record_score} Points!"
        self.draw_text(record_text, self.medium_size, flash_color_red, WIDTH // 2, HEIGHT // 5 * 4 - 65)
        
        if record_score >= PURPLE_UNLOCK_SCORE:
            self.draw_text("Purple Onion Skin Unlocked!", 28, COLORS["MAGENTA"], WIDTH // 2, HEIGHT // 5 * 4 - 25)
        elif record_score >= WHITE_UNLOCK_SCORE:
            self.draw_text("White Onion Skin Unlocked!", 28, COLORS["WHITE"], WIDTH // 2, HEIGHT // 5 * 4 - 25)

    def render_regular_game_over(self, score, record_score):
        # Cache the game over overlay surface
        if self.game_over_overlay is None:
            self.game_over_overlay = pygame.Surface((400, 100), pygame.SRCALPHA)
            self.game_over_overlay.fill((*COLORS["BLACK"], 160))
        
        overlay_rect = self.game_over_overlay.get_rect(center=(WIDTH // 2, HEIGHT // 5 * 4 - 10))
        self.screen.blit(self.game_over_overlay, overlay_rect)
        
        final_score_text = f"Score: {int(score)}"
        record_text = f"Record: {record_score}"
        self.draw_text(final_score_text, self.medium_size, COLORS["ORANGE"], WIDTH // 2, HEIGHT // 5 * 4 - 36)
        self.draw_text(record_text, self.medium_size, COLORS["ORANGE"], WIDTH // 2, HEIGHT // 5 * 4 + 10)

