import pygame
from game_core.config import resource_path

SPEECH_BUBBLE_PATH = resource_path("data/graphics/speech_bubble/speech-bubble.png")

# Loads the speech bubble image as a pygame Surface
# Returns None if loading fails

def load_speech_bubble():
    try:
        return pygame.image.load(SPEECH_BUBBLE_PATH).convert_alpha()
    except Exception as e:
        print(f"Failed to load speech bubble: {e}")
        return None
