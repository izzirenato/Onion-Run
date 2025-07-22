import pygame
from typing import Dict, Any, Optional, List
from GameEnums import GameState, InputAction

"""
Input handling system for the OnionRun game.
Processes keyboard input and translates it into game actions based on current state,
supporting both arrow keys and WASD controls.
"""

class InputHandler:
    def __init__(self) -> None:
        pass

    @staticmethod
    def handle_escape(game_state: str, paused: bool) -> Optional[Dict[str, Any]]:
        if game_state in [GameState.MENU.value, GameState.SKIN_SELECTION.value]:
            return {"action": InputAction.QUIT.value}
        elif game_state == GameState.PLAYING.value:
            if paused:
                return {"action": InputAction.TO_MENU.value}
            else:
                return {"action": InputAction.PAUSE.value}
        elif game_state == GameState.GAME_OVER.value:
            return {"action": InputAction.TO_MENU.value}
        return None

    @staticmethod
    def handle_menu_input(key: int) -> Optional[Dict[str, Any]]:
        if key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            return {"action": InputAction.TO_SKIN_SELECTION.value}
        return None

    @staticmethod
    def handle_skin_selection_input(key: int, all_possible_skins: List[str], skin_menu_index: int) -> Optional[Dict[str, Any]]:
        if key in (pygame.K_LEFT, pygame.K_a):
            new_index = (skin_menu_index - 1) % len(all_possible_skins)
            return {"action": InputAction.CHANGE_SKIN.value, "direction": "left", "index": new_index}
        elif key in (pygame.K_RIGHT, pygame.K_d):
            new_index = (skin_menu_index + 1) % len(all_possible_skins)
            return {"action": InputAction.CHANGE_SKIN.value, "direction": "right", "index": new_index}
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            return {"action": InputAction.START_GAME.value}
        return None

    def handle_playing_input(self, key: int, paused: bool) -> Optional[Dict[str, Any]]:
        if key == pygame.K_SPACE:
            if paused:
                return {"action": InputAction.RESUME.value}
            else:
                return {"action": InputAction.PAUSE.value}
        elif not paused:
            return self.handle_player_movement(key)
        return None

    @staticmethod
    def handle_player_movement(key: int) -> Optional[Dict[str, Any]]:
        if key in (pygame.K_LEFT, pygame.K_a):
            return {"action": InputAction.MOVE_LEFT.value}
        elif key in (pygame.K_RIGHT, pygame.K_d):
            return {"action": InputAction.MOVE_RIGHT.value}
        elif key in (pygame.K_UP, pygame.K_w):
            return {"action": InputAction.JUMP.value}
        elif key in (pygame.K_DOWN, pygame.K_s):
            return {"action": InputAction.CROUCH.value}
        return None

    @staticmethod
    def handle_game_over_input(key: int) -> Optional[Dict[str, Any]]:
        if key == pygame.K_r:
            return {"action": InputAction.RESTART.value}
        elif key == pygame.K_m:
            return {"action": InputAction.TO_MENU.value}
        return None

    def process_input(self, key: int, game_state: str, paused: bool = False, 
                     skin_menu_index: int = 0, all_possible_skins: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        if key == pygame.K_ESCAPE:
            return self.handle_escape(game_state, paused)
        
        if game_state == "menu":
            return self.handle_menu_input(key)
        elif game_state == "skin_selection":
            return self.handle_skin_selection_input(key, all_possible_skins, skin_menu_index)
        elif game_state == "playing":
            return self.handle_playing_input(key, paused)
        elif game_state == "game_over":
            return self.handle_game_over_input(key)
        
        return None