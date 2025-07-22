from collections import deque
from Obstacles import Obstacles
from parse_config import HEIGHT

"""
Object pooling system for obstacle management in the OnionRun game.
Implements object pool pattern to reuse obstacle sprites, minimizing memory allocation
and improving performance through pre-allocation and recycling.
"""

# Constants
OFFSCREEN_BUFFER = 100


class ObstaclePool:
    """Object pool for obstacle reuse instead of creation/destruction"""

    def __init__(self, initial_size: int = 20):
        # Create a double-ended queue to manage available elements
        self.available = deque()
        self.active = []
        
        # Pre-create obstacles
        for _ in range(initial_size):
            obstacle = Obstacles(0)         # Lane will be set on activation
            obstacle.kill()                 # Remove from sprite groups
            self.available.append(obstacle)
    
    def get_obstacle(self, lane: int, sprite_groups: list) -> Obstacles:
        """Get an obstacle from pool or create new one if needed"""
        if self.available:
            obstacle = self.available.popleft()
        else:
            # Pool exhausted, create a new one
            obstacle = Obstacles(0)
            obstacle.kill()
        
        # Reset and configure obstacle
        obstacle.reset(lane)
        
        # Add to sprite groups
        for group in sprite_groups:
            group.add(obstacle)
        
        self.active.append(obstacle)
        return obstacle
    
    def return_obstacle(self, obstacle: Obstacles) -> None:
        """Return an obstacle to the pool for reuse"""
        if obstacle in self.active:
            self.active.remove(obstacle)
        
        obstacle.kill()                 # Remove from all sprite groups
        obstacle.should_remove = False
        self.available.append(obstacle)
    
    def update(self, dt_seconds: float) -> list:
        """Update active obstacles and return those that need removal"""
        obstacles_to_return = []
        
        for obstacle in self.active[:]:         # Copy list to avoid modification during iteration
            obstacle.update(dt_seconds)
            if obstacle.should_remove or obstacle.rect.top > HEIGHT + OFFSCREEN_BUFFER:
                obstacles_to_return.append(obstacle)
        
        # Return obstacles to the pool
        for obstacle in obstacles_to_return:
            self.return_obstacle(obstacle)
        
        return obstacles_to_return
    
    def clear(self) -> None:
        """Clear all active obstacles"""
        for obstacle in self.active[:]:
            self.return_obstacle(obstacle)