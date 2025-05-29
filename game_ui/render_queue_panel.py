import pygame
import time
from game_core.entity_definitions import *
from game_core.config import *
from game_core.game_state import GameState

RQ_WIDTH = 1000
RQ_FOLDED_HEIGHT = 30
ANIMATION_DURATION = 0.3  # seconds

_render_queue_panel_expanded = False
_render_queue_panel_current_height = RQ_FOLDED_HEIGHT
_render_queue_panel_target_height = RQ_FOLDED_HEIGHT
_render_queue_panel_anim_start_time = None

RQI_HEIGHT = 40
RQI_SPACING = 8
RQI_TOP_MARGIN = 50


def get_expanded_extra_height():
    gs = GameState()
    shot_rows = getattr(gs, 'total_shots_unfinished', 10)
    return shot_rows * RQI_HEIGHT + max(0, shot_rows - 1) * RQI_SPACING + RQI_TOP_MARGIN


def handle_render_queue_panel_event(event, screen_width, resource_panel_height):
    global _render_queue_panel_expanded, _render_queue_panel_target_height, _render_queue_panel_anim_start_time
    panel_x = (screen_width - RQ_WIDTH) // 2
    panel_y = resource_panel_height
    panel_rect = pygame.Rect(panel_x, panel_y, RQ_WIDTH, _render_queue_panel_current_height)
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and panel_rect.collidepoint(*event.pos):
        _render_queue_panel_expanded = not _render_queue_panel_expanded
        expanded_height = get_expanded_extra_height()
        _render_queue_panel_target_height = RQ_FOLDED_HEIGHT + (expanded_height if _render_queue_panel_expanded else 0)
        _render_queue_panel_anim_start_time = time.time()
        return True
    return False


class RenderQueueItem:
    def __init__(self, name, progress=0.0):
        self.name = name
        self.progress = progress  # 0.0 to 1.0

    def draw(self, surface, x, y, width, height, font):
        bar_width = int(width * 0.9)
        bar_height = 20
        bar_x = x + (width - bar_width) // 2
        bar_y = y
        bg_col = tuple(int(c * 0.5) for c in UI_BG1_COL)
        border_radius = bar_height // 3
        # Draw background with rounded corners
        pygame.draw.rect(surface, bg_col, (bar_x, bar_y, bar_width, bar_height), border_radius=border_radius)
        # Gradient progress bar with rounded corners
        left_col, right_col = (69, 79, 95), (0, 187, 133)
        fill_width = max(0, min(int(bar_width * self.progress), bar_width))
        if fill_width > 0:
            grad_surf = pygame.Surface((fill_width, bar_height), pygame.SRCALPHA)
            for i in range(fill_width):
                t = i / (fill_width - 1) if fill_width > 1 else 0
                r = int(left_col[0] + (right_col[0] - left_col[0]) * t)
                g = int(left_col[1] + (right_col[1] - left_col[1]) * t)
                b = int(left_col[2] + (right_col[2] - left_col[2]) * t)
                pygame.draw.line(grad_surf, (r, g, b), (i, 0), (i, bar_height - 1))
            mask = pygame.Surface((fill_width, bar_height), pygame.SRCALPHA)
            if fill_width >= bar_width:
                pygame.draw.rect(mask, (255,255,255,255), (0,0,fill_width,bar_height), border_radius=border_radius)
            else:
                pygame.draw.rect(mask, (255,255,255,255), (0,0,fill_width,bar_height), border_top_left_radius=border_radius, border_bottom_left_radius=border_radius)
            grad_surf.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(grad_surf, (bar_x, bar_y))
        # Draw the name text above the bar, aligned to the left
        name_text = font.render(self.name, True, TEXT1_COL)
        name_rect = name_text.get_rect(topleft=(bar_x + 10, bar_y - 4 - name_text.get_height()))
        surface.blit(name_text, name_rect)
        # Draw progress number in the center of the bar
        percent = int(self.progress * 100)
        progress_text = font.render(f"{percent} / 100%", True, TEXT1_COL)
        progress_rect = progress_text.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
        surface.blit(progress_text, progress_rect)

_last_job_id = None
_last_job_start_render_progress = 0  # Track render_progress at job start
_last_shot_rows = None
_last_render_queue_items = None
_last_baked_panel = None
_last_baked_panel_job_id = None
_last_baked_panel_shot_rows = None
_last_baked_panel_width = None
_last_baked_panel_height = None
_last_render_progress = None
_last_progress_items = None

def bake_render_queue_items(job_id, shot_rows):
    """Create and return a baked list of RenderQueueItem objects for the current job."""
    return [RenderQueueItem(f"Shot {i+1}", progress=0.5) for i in range(shot_rows)]

def get_progress_items(job_id, shot_rows, render_progress):
    """Return a list of RenderQueueItem with progress distributed according to render_progress.
    Each bar represents 0-100 units. Only one bar fills at a time.
    When a bar fills, increment GameState().total_shots_finished if not already counted."""
    gs = GameState()
    items = [RenderQueueItem(f"Shot {i+1}") for i in range(shot_rows)]
    finished_count = 0
    for i in range(shot_rows):
        if render_progress >= (i + 1) * 100:
            items[i].progress = 1.0
            finished_count += 1
        elif render_progress >= i * 100:
            items[i].progress = (render_progress - i * 100) / 100.0
        else:
            break  # All subsequent bars remain at 0.0
    # Update global finished shots if needed
    if gs.total_shots_finished != finished_count:
        gs.total_shots_finished = finished_count
    return items

class Header:
    def __init__(self, width, font, total_finished, total_unfinished):
        self.width = width
        self.font = font
        self.total_finished = total_finished
        self.total_unfinished = total_unfinished

    def draw(self, surface, y=0):
        shots_in_queue = self.total_finished + self.total_unfinished
        title_str = f"Render Queue - 0 / {shots_in_queue} shots in queue"
        title_text = self.font.render(title_str, True, TEXT1_COL)
        title_rect = title_text.get_rect(midtop=(self.width // 2, y + 7))
        surface.blit(title_text, title_rect)

def bake_render_queue_panel(font, screen_width, resource_panel_height):
    """Bake the static render queue panel (background, border, title, and RenderQueueItems) into a surface."""
    global _last_baked_panel, _last_baked_panel_job_id, _last_baked_panel_shot_rows, _last_baked_panel_width, _last_baked_panel_height
    panel_x = (screen_width - RQ_WIDTH) // 2
    panel_y = resource_panel_height
    panel_height = _render_queue_panel_current_height
    panel_width = RQ_WIDTH
    gs = GameState()
    shot_rows = getattr(gs, 'total_shots_unfinished', 10)
    job_id = getattr(gs, 'job_id', 0)
    total_shots_finished = getattr(gs, 'total_shots_finished', 0)
    total_shots_unfinished = getattr(gs, 'total_shots_unfinished', 0)
    render_progress_current = getattr(gs, 'render_progress_current', 0)
    # Only re-bake if job_id, shot_rows, panel size, or render_progress changed
    global _last_render_progress, _last_progress_items
    if (
        _last_baked_panel is not None and
        _last_baked_panel_job_id == job_id and
        _last_baked_panel_shot_rows == shot_rows and
        _last_baked_panel_width == panel_width and
        _last_baked_panel_height == panel_height and
        _last_render_progress == render_progress_current
    ):
        return _last_baked_panel
    # Bake new panel
    panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    pygame.draw.rect(panel_surface, UI_BG1_COL, (0, 0, panel_width, panel_height))
    pygame.draw.rect(panel_surface, UI_BORDER1_COL, (0, 0, panel_width, panel_height), 2)
    # Header
    header = Header(panel_width, font, total_shots_finished, total_shots_unfinished)
    header.draw(panel_surface, y=0)
    # RenderQueueItems with progress
    items = get_progress_items(job_id, shot_rows, render_progress_current)
    _last_progress_items = items
    for idx, item in enumerate(items):
        y = RQI_TOP_MARGIN + idx * (RQI_HEIGHT + RQI_SPACING)
        item.draw(panel_surface, 0, y, panel_width, RQI_HEIGHT, font)
    # Cache
    _last_baked_panel = panel_surface
    _last_baked_panel_job_id = job_id
    _last_baked_panel_shot_rows = shot_rows
    _last_baked_panel_width = panel_width
    _last_baked_panel_height = panel_height
    _last_render_progress = render_progress_current
    return panel_surface

def draw_render_queue_panel(surface, font, screen_width, resource_panel_height, render_queue_items=None):
    global _render_queue_panel_expanded, _render_queue_panel_current_height, _render_queue_panel_target_height, _render_queue_panel_anim_start_time
    panel_x = (screen_width - RQ_WIDTH) // 2
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
    panel_rect = pygame.Rect(panel_x, panel_y, RQ_WIDTH, panel_height)
    # Use baked panel for static content
    baked_panel = bake_render_queue_panel(font, screen_width, resource_panel_height)
    surface.blit(baked_panel, (panel_x, panel_y))
    return panel_rect
