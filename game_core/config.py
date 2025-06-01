import pygame

def exposure_color(color, factor):
    if len(color) == 4:
        return tuple(min(int(c * factor), 255) for c in color[:3]) + (color[3],)
    return tuple(min(int(c * factor), 255) for c in color)

GRID_WIDTH = 70
GRID_HEIGHT = 35
CELL_SIZE = 64
FPS = 60

FULLSCREEN = True
RESOLUTION = (0, 0)

UI_BG1_COL = (40, 45, 50, 255)
BASE_COL = (255, 100, 100, 255)
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

