import random
import sys
from typing import Dict, Any, Optional

import pygame

from Background import Background
from Chef import Chef
from Onion import Onion
from parse_config import *
from MenuRenderer import MenuRenderer
from GameRenderer import GameRenderer
from InputHandler import InputHandler
from AudioManager import AudioManager
from GameEnums import GameState, InputAction
from ObstaclePool import ObstaclePool
from GameStateManager import GameStateManager
from ScoreManager import ScoreManager
from CollisionSystem import CollisionSystem
from AssetManager import AssetManager

"""
Main entry point and game coordinator
This file contains the GameManager class which orchestrates all game systems
"""


class GameManager:
    """Main game coordinator using a composition pattern"""

    # ctor
    def __init__(self):
        pygame.init()
        
        # Initialize display
        self._setup_display()
        
        # Initialize managers
        self.asset_manager = AssetManager()
        self.state_manager = GameStateManager()
        self.score_manager = ScoreManager(RECORD_FILE)
        self.collision_system = CollisionSystem()
        self.menu_renderer = MenuRenderer(self.screen)
        self.game_renderer = GameRenderer(self.screen)
        self.input_handler = InputHandler()
        self.audio_manager = AudioManager()
        
        
        # Game objects
        self.allSprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.obstacle_pool = ObstaclePool()
        self.player = None
        self.chef = None
        
        # Game variables
        self.clock = pygame.time.Clock()
        self.running = True
        self.difficulty_timer = 0
        self.difficulty_multiplier = INITIAL_DIFFICULTY
        self.obstacle_timer = 0
        self.is_new_record = False
        
        # UI variables
        self.blink_timer = 0
        self.show_press_enter = True
        self.game_over_flash_timer = 0
        self.game_over_flash_state = True
        self.game_over_flash_speed = GAME_OVER_FLASH_SPEED
        
        # Skin system
        self.selected_skin = "the_onion"
        self.available_skins = ["the_onion"]
        self.skin_menu_index = 0
        self.all_possible_skins = list(ASSETS["IMAGES"]["SKINS"].keys())
        self.skin_previews = \
        {
            skin_name: pygame.image.load(ASSETS["IMAGES"]["SKINS"][skin_name]).convert_alpha()
            for skin_name in self.all_possible_skins
        }
        
        # Backgrounds and sprites
        self.game_background = Background \
        ([
            {'image_path': ASSETS["IMAGES"]["GAME_BG"], 'scroll_factor': 1},
            {'image_path': ASSETS["IMAGES"]["GAME_BG_FLOOR"], 'scroll_factor': 0.6}
        ])
        
        self.sprite_needs_sorting = True
        self.sorted_sprites = []
        self.last_sprite_count = 0
        
        # Initialize based on a loaded record
        self.update_available_skins()
    
    
    def _setup_display(self):
        """Setup pygame display"""
        # Double buffering draws off-screen first to reduce flicker and improve smoothness
        flags = pygame.DOUBLEBUF
        try:
            # hardware acceleration if available
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), flags | pygame.HWSURFACE)
        except pygame.error:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
        
        try:
            icon = pygame.image.load(ASSETS["IMAGES"]["ICON"])
            pygame.display.set_icon(icon)
        except (pygame.error, FileNotFoundError, OSError):
            pass  # Continue without an icon

        pygame.display.set_caption("Onion Run")






    def update_available_skins(self):
        """Update available skins based on record score"""
        self.available_skins = ["the_onion"]
        record_score = self.score_manager.get_record_score()
        
        if record_score >= PURPLE_UNLOCK_SCORE:
            self.available_skins.append("purple")
        if record_score >= WHITE_UNLOCK_SCORE:
            self.available_skins.append("white")






    # updates player z-index based on knife block positioning for visual layering
    def update_player_layering(self):
        # Reset to normal z-index based on state
        normal_z_index = PLAYER_Z_INDICES[self.player.state]
        
        # Check if the player is behind any knife block in the same lane
        player_behind_knife = False
        for obstacle in self.obstacles:
            if (obstacle.type == "knife_block" and 
                obstacle.lane == self.player.current_lane):
                # Only go behind knife block if player has completely passed under it
                # AND there's no collision happening (player must be well below)
                if (self.player.collision_rect.bottom > obstacle.rect.bottom + 20 and
                    not self.collision_system.check_collision(self.player, [obstacle])):
                    player_behind_knife = True
                    break
        
        if player_behind_knife:
            # Set z-index lower than knife block (knife_block z-index is 7)
            self.player.z_index = 6
            self.sprite_needs_sorting = True
        else:
            # Use normal z-index for the player's current state
            if self.player.z_index != normal_z_index:
                self.player.z_index = normal_z_index
                self.sprite_needs_sorting = True


    # adds sprites, * variadic parameter, can accept more values
    @staticmethod
    def add_sprites_to_group(group: pygame.sprite.Group, *sprites):
        for sprite in sprites:
            group.add(sprite)


    def start_game(self):
        """Start a new game"""
        self.audio_manager.play_game_music()
        
        # Clear game objects
        self.allSprites.empty()
        self.obstacles.empty()
        self.obstacle_pool.clear()
        
        # Initialize new game objects
        self.player = Onion(skin=self.selected_skin)
        self.chef = Chef(self.asset_manager)
        self.add_sprites_to_group(self.allSprites, self.chef, self.player)
        
        # Reset game state
        self.state_manager.start_new_game()
        self.score_manager.reset_score()
        self.difficulty_timer = 0
        self.difficulty_multiplier = INITIAL_DIFFICULTY
        self.obstacle_timer = 0
        self.sprite_needs_sorting = True
        self.is_new_record = False


    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key)

    def handle_keydown(self, key: int):
        """Process keyboard input"""
        result = self.input_handler.process_input \
        (
            key, self.state_manager.get_state().value, 
            self.state_manager.is_paused(), 
            self.skin_menu_index, self.all_possible_skins
        )
        if result:
            self.process_input_result(result)


    def process_input_result(self, result: Dict[str, Any]):
        """Process input action results"""
        action = result["action"]
        
        match action:
            case InputAction.QUIT.value:
                self.running = False
            case InputAction.TO_MENU.value:
                self.state_manager.go_to_menu()
                self.audio_manager.play_menu_music()
                self._clear_render_caches()
            case InputAction.PAUSE.value:
                self.state_manager.pause_game()
            case InputAction.RESUME.value:
                self.state_manager.resume_game()
            case InputAction.TO_SKIN_SELECTION.value:
                self.update_available_skins()
                self.skin_menu_index = 0
                self.state_manager.go_to_skin_selection()
            case InputAction.CHANGE_SKIN.value:
                self.skin_menu_index = result["index"]
                self.selected_skin = self.all_possible_skins[self.skin_menu_index]
            case InputAction.START_GAME.value:
                if self.can_use_skin():
                    self.start_game()
            case InputAction.RESTART.value:
                self.start_game()
            case InputAction.MOVE_LEFT.value:
                if self.player:
                    self.player.move_left()
            case InputAction.MOVE_RIGHT.value:
                if self.player:
                    self.player.move_right()
            case InputAction.JUMP.value:
                if self.player:
                    self.player.start_jump()
            case InputAction.CROUCH.value:
                if self.player:
                    self.player.start_crouch()
                    self.sprite_needs_sorting = True
    
    def _clear_render_caches(self):
        """Clear rendering caches"""
        self.menu_renderer.clear_cache()
        self.game_renderer.clear_cache()


    def can_use_skin(self) -> bool:
        """Check if the selected skin is available"""
        return self.selected_skin in self.available_skins




    def update_game(self, dt: int, dt_seconds: float):
        """Update game logic based on the current state"""
        if self.state_manager.is_playing():
            if not self.state_manager.is_paused():
                self.update_gameplay(dt, dt_seconds)
            else:
                self.state_manager.update_pause(dt)


    def update_gameplay(self, dt: int, dt_seconds: float):
        """Update gameplay when playing"""
        self.obstacle_timer += dt
        self.difficulty_timer += dt
        
        # Update background
        self.game_background.update(dt_seconds)
        
        # Update difficulty and publish events
        self._update_difficulty()
        
        # Spawn obstacles
        if self.obstacle_timer > OBSTACLE_INTERVAL / self.difficulty_multiplier:
            self.spawn_obstacle()

        # Update game objects
        if self.chef:
            self.chef.update(dt_seconds, self.player)
        if self.player:
            self.player.update(dt_seconds)
            self.update_player_layering()
        
        # Update obstacles
        self.obstacle_pool.update(dt_seconds)

        # Update score
        self.score_manager.update_score(dt)

        # Check collisions
        if self.player and self.collision_system.check_collision(self.player, self.obstacles):
            # Check if it's a new record before transitioning to game over
            self.is_new_record = self.score_manager.is_new_record()
            self.state_manager.game_over()
            self._clear_render_caches()
    
    def _update_difficulty(self):
        """Update game difficulty over time"""
        if self.difficulty_timer >= DIFFICULTY_INCREASE_INTERVAL:
            self.difficulty_timer = 0
            self.difficulty_multiplier = min \
            (
                self.difficulty_multiplier + DIFFICULTY_INCREASE_RATE, 
                MAX_DIFFICULTY
            )
            
            # Update obstacle speeds
            new_speed = SPEED * self.difficulty_multiplier
            for obstacle in self.obstacles:
                obstacle.speed = new_speed
            


    def spawn_obstacle(self):
        """Spawn a new obstacle if possible"""
        if not self._can_spawn_obstacle():
            return
        
        lane = self._find_available_lane()
        if lane is not None:
            self._create_obstacle_in_lane(lane)
        else:
            self._handle_spawn_failure()
    
    def _can_spawn_obstacle(self):
        """Check if we can spawn a new obstacle"""
        return len(self.obstacles) < MAX_OBSTACLES
    
    def _find_available_lane(self) -> Optional[int]:
        """Find a lane where we can spawn an obstacle"""
        for _ in range(MAX_SPAWN_ATTEMPTS):
            lane = random.randint(0, len(LANES) - 1)
            if self._is_lane_available(lane):
                return lane
        return None
    
    def _is_lane_available(self, lane: int):
        """Check if a lane is available for spawning"""
        for obstacle in self.obstacles:
            if obstacle.lane == lane and obstacle.rect.top < OBSTACLE_SPAWN_THRESHOLD:
                return False
        return True
    
    def _create_obstacle_in_lane(self, lane: int):
        """Create an obstacle in the specified lane"""
        self.obstacle_pool.get_obstacle(lane, [self.obstacles, self.allSprites])
        self.sprite_needs_sorting = True
        self.obstacle_timer = 0

    def _handle_spawn_failure(self):
        """Handle case when no lane is available"""
        self.obstacle_timer = OBSTACLE_INTERVAL / OBSTACLE_FALLBACK_TIMER_DIVISOR




    def render(self, dt: int):
        """Render the current game state"""
        self._update_ui_timers(dt)
        
        current_state = self.state_manager.get_state()
        match current_state:
            case GameState.MENU:
                self.render_menu()
            case GameState.SKIN_SELECTION:
                self.render_skin_selection()
            case GameState.PLAYING:
                self.render_playing()
            case GameState.GAME_OVER:
                self.render_game_over()

        pygame.display.flip()
    
    def _update_ui_timers(self, dt: int):
        """Update UI animation timers"""
        self.blink_timer += dt
        if self.blink_timer > BLINK_INTERVAL:
            self.blink_timer = 0
            self.show_press_enter = not self.show_press_enter
        
        if self.state_manager.get_state() == GameState.GAME_OVER:
            self.game_over_flash_timer += dt
            if self.game_over_flash_timer >= self.game_over_flash_speed:
                self.game_over_flash_timer = 0
                self.game_over_flash_state = not self.game_over_flash_state


    def render_menu(self):
        """Render main menu"""
        if not self.audio_manager.is_music_playing():
            self.audio_manager.play_menu_music()
        
        self.menu_renderer.render_menu \
        (
            self.score_manager.get_record_score(), 
            self.show_press_enter
        )


    def render_skin_selection(self):
        """Render skin selection menu"""
        self.menu_renderer.render_skin_selection \
        (
            self.selected_skin, 
            self.skin_previews,
            self.score_manager.get_record_score(), 
            self.show_press_enter, 
            self.can_use_skin()
        )


    def render_playing(self):
        """Render gameplay screen"""
        self._update_sprite_sorting()
        
        self.game_renderer.render_game \
        (
            self.game_background, 
            self.sorted_sprites, 
            self.score_manager.get_current_score(),
            self.state_manager.is_paused(), 
            self.state_manager.is_resuming(),
            self.state_manager.pause_timer, 
            self.state_manager.pause_duration
        )
    
    def _update_sprite_sorting(self):
        """Update sprite sorting if needed"""
        current_sprite_count = len(self.allSprites)
        if self.sprite_needs_sorting or current_sprite_count != self.last_sprite_count:
            self.sorted_sprites = sorted \
            (
                self.allSprites, 
                key=lambda obj: getattr(obj, 'z_index', 0)
            )
            self.sprite_needs_sorting = False
            self.last_sprite_count = current_sprite_count




    def render_game_over(self):
        """Render game over screen"""
        if self.audio_manager.get_game_over_channels() == 0:
            self.audio_manager.play_game_over_music()
        
        flash_color_red = COLORS["RED"] if self.game_over_flash_state else COLORS["DARK_RED"]
        # The * operator "unpacks" the tuple, spreading its elements into a new tuple
        flash_color_grey = (*COLORS["WHITE"], 200) if self.game_over_flash_state else (*COLORS["LIGHT_GREY"], 200)
        
        # Handle new record (save only once)
        if self.is_new_record:
            self.score_manager.save_new_record()
            self.update_available_skins()  # Update skins when new record achieved
        
        self.menu_renderer.render_game_over \
        (
            self.score_manager.get_current_score(), 
            self.score_manager.get_record_score(), 
            flash_color_red,
            flash_color_grey, 
            self.is_new_record
        )




    # handles the fps management
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            # converts from milliseconds to seconds (20 FPS minimum)
            dt_seconds = min(dt / 1000.0, 0.05)
            
            self.handle_events()
            self.update_game(dt, dt_seconds)
            self.render(dt)
        
        pygame.quit()
        sys.exit()


def main():
    """Main entry point for the game"""
    game = GameManager()
    game.run()


if __name__ == "__main__":
    main()