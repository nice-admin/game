import pygame
import sys
import os

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

GAME_AREA_WIDTH = 70
GAME_AREA_HEIGHT = 35
CELL_SIZE = 60
CELL_SIZE_INNER = CELL_SIZE - 10
FPS = 60

FULLSCREEN = True
RESOLUTION = (0, 0)

GRID_FILL_COL = adjust_color(BASE_COL, white_factor=0.0, exposure=1.6) 
GRID_EMPTY_SPACE_COL = adjust_color(BASE_COL, white_factor=0.0, exposure=1.7) 
BG_OUTSIDE_GRID_COL = GRID_EMPTY_SPACE_COL

UI_BG1_COL = adjust_color(BASE_COL, white_factor=0.0, exposure=1) 
UI_BORDER1_COL = adjust_color(BASE_COL, white_factor=0.0, exposure=1.5) 
TEXT1_COL = (180, 180, 180)

STATUS_BASIC_COL = (180, 180, 180)
STATUS_INIT_COL = (120, 150, 180)
STATUS_BAD_COL = (255, 0, 0)
STATUS_MID_COL = (255, 220, 0)
STATUS_GOOD_COL = (0, 255, 0)

# Audio/Font/Data resource path helper

def resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller .exe
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

FONT1 = resource_path("data/fonts/font1.ttf")

def get_font1(size=18):
    return pygame.font.Font(FONT1, size)

MIXER_NUM_CHANNELS = 32

def get_display_mode():
    if FULLSCREEN:
        return RESOLUTION, pygame.FULLSCREEN | pygame.NOFRAME
    else:
        return (GAME_AREA_WIDTH * CELL_SIZE, GAME_AREA_HEIGHT * CELL_SIZE), 0

CURRENCY_SYMBOL = "§"  # You can change this to any symbol, e.g., 'S', '₴', etc.
