# game/settings.py
import pygame

# Screen dimensions for full screen 1920x1080
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# Frames per second
FPS = 60

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARK_GRAY = (80, 80, 80)

# Default sound volume (0.0 to 1.0)
DEFAULT_VOLUME = 0.5

# Game states
STATE_MAIN_MENU = "main_menu"
STATE_GAME = "game"
STATE_PAUSE = "pause"
STATE_OPTIONS = "options"
STATE_QUIT = "quit"

# Levels
LEVEL_EASY = "easy"
LEVEL_HARD = "hard"
