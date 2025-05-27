import pygame
import time
from game_core.entity_definitions import *
from game_core.game_settings import *

PANEL_WIDTH = 1532
PANEL_HEIGHT = 30
ANIMATION_DURATION = 1.0  # seconds

_render_queue_panel_expanded = False
_render_queue_panel_current_height = PANEL_HEIGHT
_render_queue_panel_target_height = PANEL_HEIGHT
_render_queue_panel_anim_start_time = None

SHOT_ROWS = 10
SHOT_HEIGHT = 40
SHOT_SPACING = 8
TOP_MARGIN = 50


def get_expanded_extra_height():
    return SHOT_ROWS * SHOT_HEIGHT + (SHOT_ROWS - 1) * SHOT_SPACING + TOP_MARGIN


def handle_render_queue_panel_event(event, screen_width, resource_panel_height):
    global _render_queue_panel_expanded, _render_queue_panel_target_height, _render_queue_panel_anim_start_time
    panel_x = (screen_width - PANEL_WIDTH) // 2
    panel_y = resource_panel_height
    panel_rect = pygame.Rect(panel_x, panel_y, PANEL_WIDTH, _render_queue_panel_current_height)
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and panel_rect.collidepoint(*event.pos):
        _render_queue_panel_expanded = not _render_queue_panel_expanded
        expanded_height = get_expanded_extra_height()
        _render_queue_panel_target_height = PANEL_HEIGHT + (expanded_height if _render_queue_panel_expanded else 0)
        _render_queue_panel_anim_start_time = time.time()
        return True
    return False


class RenderQueueItem:
    def __init__(self, name, progress=0.5):
        self.name = name
        self.progress = progress  # 0.0 to 1.0

    def draw(self, surface, x, y, width, height, font):
        bar_width = int(width * 0.9)
        bar_height = 30
        bar_x = x + (width - bar_width) // 2
        bar_y = y
        bg_col = tuple(int(c * 0.5) for c in UI_BG1_COL)
        pygame.draw.rect(surface, bg_col, (bar_x, bar_y, bar_width, bar_height))
        teal = (0, 255, 220)
        fill_width = int(bar_width * self.progress)
        pygame.draw.rect(surface, teal, (bar_x, bar_y, fill_width, bar_height))
        name_text = font.render(self.name, True, TEXT1_COL)
        name_rect = name_text.get_rect(midleft=(bar_x + 10, bar_y + bar_height // 2))
        surface.blit(name_text, name_rect)


def draw_render_queue_panel(surface, font, screen_width, resource_panel_height, render_queue_items=None):
    global _render_queue_panel_expanded, _render_queue_panel_current_height, _render_queue_panel_target_height, _render_queue_panel_anim_start_time
    panel_x = (screen_width - PANEL_WIDTH) // 2
    panel_y = resource_panel_height

    # Animate height
    if _render_queue_panel_anim_start_time is not None:
        elapsed = time.time() - _render_queue_panel_anim_start_time
        t = min(elapsed / ANIMATION_DURATION, 1.0)
        _render_queue_panel_current_height = int(
            _render_queue_panel_current_height + (_render_queue_panel_target_height - _render_queue_panel_current_height) * t
        )
        if t >= 1.0:
            _render_queue_panel_current_height = _render_queue_panel_target_height
            _render_queue_panel_anim_start_time = None
    else:
        _render_queue_panel_current_height = _render_queue_panel_target_height

    panel_height = _render_queue_panel_current_height
    panel_rect = pygame.Rect(panel_x, panel_y, PANEL_WIDTH, panel_height)
    pygame.draw.rect(surface, UI_BG1_COL, panel_rect)
    pygame.draw.rect(surface, UI_BORDER1_COL, panel_rect, 2)

    # Title
    title_text = font.render("Render Queue", True, TEXT1_COL)
    title_rect = title_text.get_rect(midtop=(panel_x + PANEL_WIDTH // 2, panel_y + 7))
    surface.blit(title_text, title_rect)

    # Masked bars
    mask_surface = pygame.Surface((PANEL_WIDTH, panel_height), pygame.SRCALPHA)
    if render_queue_items is None:
        render_queue_items = [RenderQueueItem(f"Shot {i+1}", progress=0.5) for i in range(SHOT_ROWS)]
    for idx in range(SHOT_ROWS):
        if idx < len(render_queue_items) and isinstance(render_queue_items[idx], RenderQueueItem):
            y = TOP_MARGIN + idx * (SHOT_HEIGHT + SHOT_SPACING)
            render_queue_items[idx].draw(mask_surface, 0, y, PANEL_WIDTH, SHOT_HEIGHT, font)
    surface.blit(mask_surface, (panel_x, panel_y))
    return panel_rect
