from GameEnums import GameState
from parse_config import PAUSE_DURATION, HIDE_DURATION

"""
Game state management system for the OnionRun game.
Centralizes state transitions between menu, playing, and game over states,
while managing pause/resume functionality with countdown timer.
"""

class GameStateManager:
    """Manages game states and state transitions"""
    
    def __init__(self):
        self.current_state = GameState.MENU
        self.paused = False
        self.resuming = False
        self.pause_timer = 0
        self.pause_duration = PAUSE_DURATION
        self.hide_duration = HIDE_DURATION
    
    def get_state(self) -> GameState:
        """Get current game state"""
        return self.current_state
    
    def is_playing(self) -> bool:
        """Check if game is in playing state"""
        return self.current_state == GameState.PLAYING
    
    def is_paused(self) -> bool:
        """Check if the game is paused"""
        return self.paused
    
    def is_resuming(self) -> bool:
        """Check if the game is resuming from pause"""
        return self.resuming
    
    def pause_game(self):
        """Pause the game"""
        if self.is_playing():
            self.paused = True
            self.resuming = False
            self.pause_timer = 0
    
    def resume_game(self):
        """Start resuming from pause"""
        if self.paused:
            self.resuming = True
            self.pause_timer = 0
    
    def update_pause(self, dt: int):
        """Update pause state (for countdown)"""
        if self.resuming:
            self.pause_timer += dt
            if self.pause_timer >= self.pause_duration:
                self.paused = False
                self.resuming = False
                self.pause_timer = 0
    
    def start_new_game(self):
        """Start a new game"""
        self.current_state = GameState.PLAYING
        self.paused = False
        self.resuming = False
        self.pause_timer = 0
    
    def go_to_menu(self):
        """Return to the main menu"""
        self.current_state = GameState.MENU
        self.paused = False
        self.resuming = False
    
    def game_over(self):
        """Set game over state"""
        self.current_state = GameState.GAME_OVER
        self.paused = False
        self.resuming = False
    
    def go_to_skin_selection(self):
        """Go to a skin selection menu"""
        self.current_state = GameState.SKIN_SELECTION