import pygame

BASE_COL = (40, 45, 50, 255)

def exposure_color(color, factor):
    if len(color) == 4:
        return tuple(min(int(c * factor), 255) for c in color[:3]) + (color[3],)
    return tuple(min(int(c * factor), 255) for c in color)

def adjust_color(base_color=BASE_COL, white_factor=0.0, exposure=1.0):
    """
    Adjusts a color by mixing with white and applying an exposure factor.
    - base_color: tuple (R,G,B) or (R,G,B,A)
    - white_factor: float between 0.0 (no white) and 1.0 (full white)
    - exposure: float, multiplies the color (default 1.0)
    Returns: tuple of same length as base_color
    """
    # Exposure adjustment
    if len(base_color) == 4:
        col = tuple(min(int(c * exposure), 255) for c in base_color[:3]) + (base_color[3],)
    else:
        col = tuple(min(int(c * exposure), 255) for c in base_color)
    # White mix
    white = (255, 255, 255) if len(col) < 4 else (255, 255, 255, col[3])
    return tuple(
        int((1 - white_factor) * c + white_factor * w)
        for c, w in zip(col, white)
    )

GRID_WIDTH = 70
GRID_HEIGHT = 35
CELL_SIZE = 64
FPS = 60

FULLSCREEN = True
RESOLUTION = (0, 0)

UI_BG1_COL = (40, 45, 50, 255)
UI_BORDER1_COL = (100, 100, 100, 128)
TEXT1_COL = (180, 180, 180)
GRID_BG_COL = exposure_color(UI_BG1_COL, 1.6)
GRID_BORDER_COL = exposure_color(UI_BG1_COL, 2)
BG_OUTSIDE_GRID_COL = GRID_BG_COL
STATUS_BASIC_COL =(180, 180, 180)
STATUS_INIT_COL = (120, 150, 180)
STATUS_BAD_COL = (255, 0, 0)
STATUS_MID_COL = (255, 220, 0)
STATUS_GOOD_COL = (0, 255, 0)

FONT1_PATH = "data/fonts/font1.ttf"

def get_font1(size=18):
    return pygame.font.Font(FONT1_PATH, size)

MIXER_NUM_CHANNELS = 32

def get_display_mode():
    if FULLSCREEN:
        return RESOLUTION, pygame.FULLSCREEN | pygame.NOFRAME
    else:
        return (GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE), 0

