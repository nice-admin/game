import pygame
import sys
from game_core.entity_definitions import *
from game_core.game_loop import run_game
from game_core.config import GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, FPS
import game_other.logger as logger
import game_other.audio as audio

# --- Game Grid ---
def create_grid():
    from game_core.config import GRID_WIDTH, GRID_HEIGHT
    return [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def main():
    import game_core.config as config
    pygame.mixer.init()
    pygame.mixer.set_num_channels(config.MIXER_NUM_CHANNELS)
    audio.play_random_music_wav()
    run_game()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.log_crash(e)
        raise