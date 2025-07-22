import pygame
from parse_config import SCORE_RATE

"""
Score management system for the OnionRun game.
Handles time-based score calculation, high score persistence to file,
and automatic new record detection with saving.
"""

class ScoreManager:
    """Manages game score and high-score persistence"""
    
    def __init__(self, record_file: str = "high_score.txt"):
        self.current_score = 0.0
        self.record_score = 0
        self.last_score_time = 0
        self.record_file = record_file
        self.load_record()
    
    def update_score(self, dt: int):
        """Update the current score based on time elapsed"""
        current_time = pygame.time.get_ticks()
        if current_time > self.last_score_time:
            self.current_score += dt * SCORE_RATE
            self.last_score_time = current_time
    
    def reset_score(self):
        """Reset the current score to 0 (for new game)"""
        self.current_score = 0.0
        self.last_score_time = pygame.time.get_ticks()
    
    def get_current_score(self) -> int:
        """Get the current score as integer"""
        return int(self.current_score)
    
    def get_record_score(self) -> int:
        """Get a high score"""
        return self.record_score
    
    def is_new_record(self) -> bool:
        """Check if the current score is a new record"""
        return self.get_current_score() > self.record_score
    
    def save_new_record(self) -> bool:
        """Save current score as new record if it's higher"""
        if self.is_new_record():
            self.record_score = self.get_current_score()
            self.save_record()
            return True
        return False
    
    def load_record(self):
        """Load high score from a file"""
        try:
            with open(self.record_file, "r") as f:
                self.record_score = int(f.read().strip())
        except (FileNotFoundError, ValueError):
            self.record_score = 0
    
    def save_record(self):
        """Save high score to file"""
        try:
            with open(self.record_file, "w") as f:
                f.write(str(self.record_score))
        except IOError as e:
            print(f"Error saving record: {e}")   
