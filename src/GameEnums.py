from enum import Enum

"""
Enumeration definitions for the OnionRun game.
Defines GameState (menu, playing, game over) and InputAction (movement, jumping, menu navigation)
enums for type-safe state management and input handling.
"""

class GameState(Enum):
    MENU = "menu"
    SKIN_SELECTION = "skin_selection"
    PLAYING = "playing"
    GAME_OVER = "game_over"



class InputAction(Enum):
    QUIT = "quit"
    TO_MENU = "to_menu"
    PAUSE = "pause"
    RESUME = "resume"
    TO_SKIN_SELECTION = "to_skin_selection"
    CHANGE_SKIN = "change_skin"
    START_GAME = "start_game"
    RESTART = "restart"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    JUMP = "jump"
    CROUCH = "crouch"
