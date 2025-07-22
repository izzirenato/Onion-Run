from xml.etree.ElementTree import parse

"""
Configuration parser for the OnionRun game.

This module loads and parses the XML configuration file, providing centralized access
to all game settings, constants, and asset paths. It converts XML data into Python
data structures used throughout the game.
"""

# Convert a color string like 'R, G, B' or 'R, G, B, A' into a tuple of integers.
# Example: '255,0,0' -> (255, 0, 0)
def parse_color(text: str) -> tuple[int, ...]:
    return tuple(int(c) for c in text.split(','))

# Parse the XML configuration file
try:
    tree = parse("config.xml")
    root = tree.getroot()
except Exception as e:
    print(f"Error parsing config.xml: {e}")
    print("Using default configuration values")
    # You could set default values here or exit
    raise SystemExit("Cannot continue without valid configuration")

# Window configuration
WIDTH = int(root.find("window/width").text)
HEIGHT = int(root.find("window/height").text)

# Game configuration
SPEED = int(root.find("game/speed").text)
FPS = int(root.find("game/fps").text)
GROUND_Y = int(root.find("game/ground_y").text)

# List of lane positions
LANES = [int(lane.text) for lane in root.findall("game/lanes/lane")]

# Obstacles configuration
OBSTACLE_INTERVAL = int(root.find("game/obstacles/interval").text)
MAX_OBSTACLES = int(root.find("game/obstacles/max").text)
MAX_SPAWN_ATTEMPTS = int(root.find("game/obstacles/max_spawn_attempts").text)
OBSTACLE_FALLBACK_TIMER_DIVISOR = int(root.find("game/obstacles/fallback_timer_divisor").text)

# Obstacle Z-indices
OBSTACLE_Z_INDICES = \
{
    "pan": int(root.find("game/obstacles/z_indices/pan").text),
    "knife_block": int(root.find("game/obstacles/z_indices/knife_block").text),
    "cabbage": int(root.find("game/obstacles/z_indices/cabbage").text),
    "default": int(root.find("game/obstacles/z_indices/default").text)
}

# Player Z-indices for different states
PLAYER_Z_INDICES = \
{
    "running": int(root.find("game/collision/player_z_indices/running").text),
    "jumping": int(root.find("game/collision/player_z_indices/jumping").text),
    "crouching": int(root.find("game/collision/player_z_indices/crouching").text)
}

# Difficulty settings
DIFFICULTY_INCREASE_RATE = float(root.find("game/difficulty/increase_rate").text)
INITIAL_DIFFICULTY = float(root.find("game/difficulty/initial").text)
MAX_DIFFICULTY = float(root.find("game/difficulty/max").text)
DIFFICULTY_INCREASE_INTERVAL = int(root.find("game/difficulty/interval").text)

# Score configuration
SCORE_RATE = float(root.find("game/score/rate").text)

# Pause settings
HIDE_DURATION = int(root.find("game/pause/hide_duration").text)
PAUSE_DURATION = int(root.find("game/pause/pause_duration").text)

# Visual effects timing
BLINK_INTERVAL = int(root.find("game/effects/blink_interval").text)
GAME_OVER_FLASH_SPEED = int(root.find("game/effects/game_over_flash_speed").text)

# Collision detection constants
COLLISION_DISTANCE_THRESHOLD = int(root.find("game/collision/distance_threshold").text)
OBSTACLE_SPAWN_THRESHOLD = int(root.find("game/collision/obstacle_spawn_threshold").text)

# Physics constants
JUMP_VELOCITY = int(root.find("game/physics/jump_velocity").text)
GRAVITY = float(root.find("game/physics/gravity").text)

# Player configuration constants
PLAYER_COLLISION_FACTORS = {
    "width": float(root.find("game/player/collision_factors/width").text),
    "height": float(root.find("game/player/collision_factors/height").text),
    "jump_width": float(root.find("game/player/collision_factors/jump_width").text),
    "jump_height": float(root.find("game/player/collision_factors/jump_height").text),
    "crouch_width": float(root.find("game/player/collision_factors/crouch_width").text),
    "crouch_height": float(root.find("game/player/collision_factors/crouch_height").text)
}
PLAYER_MOVEMENT_FACTOR = float(root.find("game/player/movement_factor").text)
PLAYER_ANIMATION_DELAY = int(root.find("game/player/animation_delay").text)
PLAYER_CROUCH_DURATION = int(root.find("game/player/crouch_duration").text)

# Skins configuration
PURPLE_UNLOCK_SCORE = int(root.find("skins/purple_unlock_score").text)
WHITE_UNLOCK_SCORE = int(root.find("skins/white_unlock_score").text)

# File where the high score is saved
RECORD_FILE = root.find("record_file").text

# Volume levels for different game music/sounds
MENU_MUSIC_VOLUME = float(root.find("volumes/menu_music").text)
GAME_MUSIC_VOLUME = float(root.find("volumes/game_music").text)
GAME_OVER_MUSIC_VOLUME = float(root.find("volumes/game_over_music").text)

# Colors dictionary: converts color strings to tuples of ints
COLORS = {color.tag: parse_color(color.text) for color in root.find("colors")}

# Paths to game assets (fonts, images, sounds)
ASSETS = \
{
    "FONTS":
    {
        "MAIN": root.find("assets/fonts/main").text
    },
    "IMAGES":
    {
        "ICON": root.find("assets/images/icon").text,
        "MENU_BG": root.find("assets/images/menu_bg").text,
        "GAME_BG": root.find("assets/images/game_bg").text,
        "GAME_BG_FLOOR": root.find("assets/images/game_bg_floor").text,
        "GAME_OVER_BG": root.find("assets/images/game_over_bg").text,
        
        "OBSTACLES":
        {
            "CABBAGE": root.find("assets/images/obstacles/cabbage").text,
            "KNIFE_BLOCK": root.find("assets/images/obstacles/knife_block").text,
            "PAN": root.find("assets/images/obstacles/pan").text,
        },
        
        "CHEF":
        {
            "LEFT": root.find("assets/images/chef/left").text,
            "BACK": root.find("assets/images/chef/back").text,
            "RIGHT": root.find("assets/images/chef/right").text,
        },
        
        "PLAYER":
        {
            "THE_ONION":
            {
                "BACK": root.find("assets/images/player/the_onion/back").text,
                "CROUCH": root.find("assets/images/player/the_onion/crouch").text,
                "CRYING": root.find("assets/images/player/the_onion/crying").text,
                "JUMP": root.find("assets/images/player/the_onion/jump").text,
                "LEFT_FOOT_UP": root.find("assets/images/player/the_onion/left_foot_up").text,
                "RIGHT_FOOT_UP": root.find("assets/images/player/the_onion/right_foot_up").text,
            },
            "PURPLE":
            {
                "BACK": root.find("assets/images/player/purple/back").text,
                "CROUCH": root.find("assets/images/player/purple/crouch").text,
                "JUMP": root.find("assets/images/player/purple/jump").text,
                "LEFT_FOOT_UP": root.find("assets/images/player/purple/left_foot_up").text,
                "RIGHT_FOOT_UP": root.find("assets/images/player/purple/right_foot_up").text,
            },
            "WHITE":
            {
                "BACK": root.find("assets/images/player/white/back").text,
                "CROUCH": root.find("assets/images/player/white/crouch").text,
                "JUMP": root.find("assets/images/player/white/jump").text,
                "LEFT_FOOT_UP": root.find("assets/images/player/white/left_foot_up").text,
                "RIGHT_FOOT_UP": root.find("assets/images/player/white/right_foot_up").text,
            },
        },
        
        "SKINS":
        {
            skin.tag: skin.text
            for skin in root.findall("assets/images/skins/*")
        }
    },
    "SOUNDS":
    {
        "MENU_MUSIC": root.find("assets/sounds/menu_music").text,
        "GAME_MUSIC": root.find("assets/sounds/game_music").text,
        "GAME_OVER_MUSIC": root.find("assets/sounds/game_over_music").text
    }
}

# UI configuration details: sizes and positions of UI elements and fonts
UI = \
{
    "SCORE_BOX":
    {
        "WIDTH": int(root.find("ui/score_box/width").text),
        "X": int(root.find("ui/score_box/x").text),
        "Y": int(root.find("ui/score_box/y").text),
    },

    "CONTROLS_BOX":
    {
        "WIDTH": int(root.find("ui/controls_box/width").text),
        "X": int(root.find("ui/controls_box/x").text),
        "Y": int(root.find("ui/controls_box/y").text),
    },

    "OVAL_BUTTON":
    {
        "WIDTH": int(root.find("ui/oval_button/width").text),
        "HEIGHT": int(root.find("ui/oval_button/height").text),
    },

    "FONT_SIZES":
    {
        # Convert all font size tags to uppercase keys for consistency
        key.upper(): int(value.text)
        for key, value in ((el.tag, el) for el in root.find("ui/font_sizes"))
    }
}