import pygame

# game_core/game_settings.py

# Game window and grid configuration
GRID_WIDTH = 70  # Number of columns
GRID_HEIGHT = 35  # Number of rows
CELL_SIZE = 64
# SCREEN_SIZE and GRID_SIZE are deprecated in favor of GRID_WIDTH/HEIGHT
FPS = 60

# Window mode
FULLSCREEN = True  # Set to True for fullscreen windowed mode
# Resolution for fullscreen (0, 0) means use current display size
RESOLUTION = (0, 0)

# Colors
UI_BG1_COL = (40, 40, 40)        # Some grey color
UI_BORDER1_COL = (100, 100, 100) # Some light grey color
TEXT1_COL = (180, 180, 180)   # Standard text color
GRID_BG_COL = (80, 80, 80)    # Grid background color (main play area)
GRID_BORDER_COL = (120, 120, 120) # Grid line color (main play area)
# Color for the background outside the grid
BG_OUTSIDE_GRID_COL = GRID_BG_COL
STATUS_INIT_COL = (120, 150, 180)
STATUS_BAD_COL = (255, 0, 0)
STATUS_MIDDLE_COL = (255, 220, 0)
STATUS_GOOD_COL = (0, 255, 0) 

# Font
FONT1_PATH = "data/fonts/font1.ttf"

def get_font1(size=18):
    """
    Returns a pygame.font.Font object for FONT1_PATH at the given size.
    Call only after pygame.init().
    """
    return pygame.font.Font(FONT1_PATH, size)

# Audio settings
MIXER_NUM_CHANNELS = 32  # Allow up to 32 simultaneous sound effects

def get_display_mode():
    """
    Returns (resolution, flags) for pygame.display.set_mode based on settings.
    """
    if FULLSCREEN:
        return RESOLUTION, pygame.FULLSCREEN | pygame.NOFRAME  # True fullscreen, borderless
    else:
        return (GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE), 0
