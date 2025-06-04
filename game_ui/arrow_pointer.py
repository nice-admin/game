import pygame
import os
import threading
import time
import random

# Cache for the baked arrow pointer surface
_baked_arrow_pointer = None

ARROW_CANVAS_WIDTH = 800
ARROW_CANVAS_HEIGHT = 300
ARROW_LABEL = "THIS IS YOUR PROJECT, FINISH IT FAST (click to unfold)"
ARROW_LABEL_COLOR = (255, 255, 0)
ARROW_LABEL_FONT_SIZE = 40

ARROW_IMAGE_PATH = os.path.join("data", "graphics", "arrow.png")

# Shake effect parameters
SHAKE_AMPLITUDE = 2  # pixels
SHAKE_FREQUENCY = 20  # Hz (how many shakes per second, for reference)
_last_shake_time = 0
_last_shake_offsets = [(0,0), (0,0), (0,0)]


def bake_arrow_pointer():
    global _last_shake_time, _last_shake_offsets
    now = time.time()
    # Only update shake offsets at the specified frequency
    if now - _last_shake_time > 1.0 / SHAKE_FREQUENCY:
        _last_shake_offsets = [
            (random.randint(-SHAKE_AMPLITUDE, SHAKE_AMPLITUDE), random.randint(-SHAKE_AMPLITUDE, SHAKE_AMPLITUDE)),
            (random.randint(-SHAKE_AMPLITUDE, SHAKE_AMPLITUDE), random.randint(-SHAKE_AMPLITUDE, SHAKE_AMPLITUDE)),
            (random.randint(-SHAKE_AMPLITUDE, SHAKE_AMPLITUDE), random.randint(-SHAKE_AMPLITUDE, SHAKE_AMPLITUDE)),
        ]
        _last_shake_time = now
    surface = pygame.Surface((ARROW_CANVAS_WIDTH, ARROW_CANVAS_HEIGHT), pygame.SRCALPHA)
    # Arrow shake offset (use a different phase/seed from text)
    arrow_seed = int(time.time() * SHAKE_FREQUENCY * 1.7)  # 1.7 is an arbitrary offset for phase
    arrow_rng = random.Random(arrow_seed)
    arrow_offset = (
        arrow_rng.randint(-SHAKE_AMPLITUDE, SHAKE_AMPLITUDE),
        arrow_rng.randint(-SHAKE_AMPLITUDE, SHAKE_AMPLITUDE)
    )
    # Draw arrow image if available
    try:
        arrow_img = pygame.image.load(ARROW_IMAGE_PATH).convert_alpha()
        arrow_img = pygame.transform.smoothscale(arrow_img, (120, 120))
        img_rect = arrow_img.get_rect(center=(ARROW_CANVAS_WIDTH // 2 + arrow_offset[0], ARROW_CANVAS_HEIGHT // 2 - 40 + arrow_offset[1]))
        surface.blit(arrow_img, img_rect)
    except Exception:
        pass  # If image not found, skip
    label_font = pygame.font.Font(None, ARROW_LABEL_FONT_SIZE)
    # Row 1
    row1 = "THIS IS YOUR PROJECT"
    row1_surf = label_font.render(row1, True, ARROW_LABEL_COLOR)
    # Row 2
    row2 = "FINISH IT FAST"
    row2_surf = label_font.render(row2, True, ARROW_LABEL_COLOR)
    # Row 3
    row3 = "(click the panel to unfold)"
    row3_font = pygame.font.Font(None, 28)
    row3_surf = row3_font.render(row3, True, ARROW_LABEL_COLOR)
    # Use cached shake offsets for text
    row1_offset = _last_shake_offsets[0]
    row2_offset = _last_shake_offsets[1]
    row3_offset = _last_shake_offsets[2]
    # Center positions (moved all text 5px lower)
    row1_rect = row1_surf.get_rect(center=(ARROW_CANVAS_WIDTH // 2 + row1_offset[0], ARROW_CANVAS_HEIGHT // 2 + 35 + row1_offset[1]))
    row2_rect = row2_surf.get_rect(center=(ARROW_CANVAS_WIDTH // 2 + row2_offset[0], ARROW_CANVAS_HEIGHT // 2 + 75 + row2_offset[1]))
    row3_rect = row3_surf.get_rect(center=(ARROW_CANVAS_WIDTH // 2 + row3_offset[0], ARROW_CANVAS_HEIGHT // 2 + 110 + row3_offset[1]))
    surface.blit(row1_surf, row1_rect)
    surface.blit(row2_surf, row2_rect)
    surface.blit(row3_surf, row3_rect)
    return surface

# Arrow pointer display state
_arrow_pointer_visible = False
_arrow_pointer_timer = None
_arrow_pointer_alpha = 0  # 0 = fully transparent, 255 = fully opaque
_arrow_pointer_fading_in = False
_arrow_pointer_fading_out = False

FADE_DURATION = 0.2  # seconds
FPS = 60  # assumed for fade timing


def _fade_in():
    global _arrow_pointer_alpha, _arrow_pointer_fading_in
    _arrow_pointer_fading_in = True
    steps = int(FADE_DURATION * FPS)
    for i in range(steps):
        _arrow_pointer_alpha = int(255 * (i + 1) / steps)
        time.sleep(1 / FPS)
    _arrow_pointer_alpha = 255
    _arrow_pointer_fading_in = False


def _fade_out():
    global _arrow_pointer_alpha, _arrow_pointer_fading_out
    _arrow_pointer_fading_out = True
    steps = int(FADE_DURATION * FPS)
    for i in range(steps):
        _arrow_pointer_alpha = int(255 * (steps - i - 1) / steps)
        time.sleep(1 / FPS)
    _arrow_pointer_alpha = 0
    _arrow_pointer_fading_out = False


def _arrow_pointer_thread(show_time=6):
    global _arrow_pointer_visible, _arrow_pointer_timer
    _arrow_pointer_visible = True
    threading.Thread(target=_fade_in, daemon=True).start()
    time.sleep(show_time)
    threading.Thread(target=_fade_out, daemon=True).start()
    # Wait for fade out to finish before hiding
    time.sleep(FADE_DURATION)
    _arrow_pointer_visible = False
    _arrow_pointer_timer = None


def show_arrow_pointer(delay=2, show_time=6):
    global _arrow_pointer_timer
    if _arrow_pointer_timer is not None:
        return  # Already scheduled
    def delayed_show():
        time.sleep(delay)
        _arrow_pointer_thread(show_time)
    _arrow_pointer_timer = threading.Thread(target=delayed_show, daemon=True)
    _arrow_pointer_timer.start()


def draw_arrow_pointer(surface, x=0, y=0):
    if not _arrow_pointer_visible and _arrow_pointer_alpha == 0:
        return
    pointer_surf = bake_arrow_pointer().copy()
    pointer_surf.set_alpha(_arrow_pointer_alpha)
    surface.blit(pointer_surf, (x, y))
