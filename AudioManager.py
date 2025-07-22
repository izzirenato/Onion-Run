import pygame
from parse_config import *

"""
Audio management system for the OnionRun game.
Handles background music playback for different game states (menu, gameplay, game over)
with volume control.
"""

class AudioManager:
    def __init__(self):
        try:
            pygame.mixer.init()
        except pygame.error as _:
            print(f"Error initializing audio: {_}")
            # Continue without audio
        
        self.menu_music = None
        self.game_music = None
        self.game_over_music = None
        self.current_music = None
        self.setup_audio()

    def setup_audio(self):
        try:
            self.menu_music = pygame.mixer.Sound(ASSETS["SOUNDS"]["MENU_MUSIC"])
            self.game_music = pygame.mixer.Sound(ASSETS["SOUNDS"]["GAME_MUSIC"])
            self.game_over_music = pygame.mixer.Sound(ASSETS["SOUNDS"]["GAME_OVER_MUSIC"])
            
            self.menu_music.set_volume(MENU_MUSIC_VOLUME)
            self.game_music.set_volume(GAME_MUSIC_VOLUME)
            self.game_over_music.set_volume(GAME_OVER_MUSIC_VOLUME)
        except pygame.error as _:
            print(f"Error loading audio: {_}")

    def stop_all_music(self):
        if self.menu_music:
            self.menu_music.stop()
        if self.game_music:
            self.game_music.stop()
        if self.game_over_music:
            self.game_over_music.stop()
        self.current_music = None

    def play_menu_music(self):
        if self.current_music != "menu":
            self.stop_all_music()
            if self.menu_music:
                try:
                    self.menu_music.play(-1)
                    self.current_music = "menu"
                except pygame.error as _:
                    print(f"Error playing menu music: {_}")

    def play_game_music(self):
        if self.current_music != "game":
            self.stop_all_music()
            if self.game_music:
                try:
                    self.game_music.play(-1)
                    self.current_music = "game"
                except pygame.error as _:
                    print(f"Error playing game music: {_}")

    def play_game_over_music(self):
        if self.current_music != "game_over":
            self.stop_all_music()
            if self.game_over_music:
                try:
                    self.game_over_music.play()
                    self.current_music = "game_over"
                except pygame.error as _:
                    print(f"Error playing game over music: {_}")

    @staticmethod
    def is_music_playing() -> bool:
        return pygame.mixer.get_busy()

    def get_game_over_channels(self) -> int:
        return self.game_over_music.get_num_channels() if self.game_over_music else 0