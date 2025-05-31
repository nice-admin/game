import pygame
import time
from game_core.entity_definitions import *
from game_core.config import *
from game_core.config import exposure_color
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
    shot_rows = getattr(gs, 'total_shots_goal', 10)
    return shot_rows * RQI_HEIGHT + max(0, shot_rows - 1) * RQI_SPACING + RQI_TOP_MARGIN


def handle_render_queue_panel_event(event, screen_width, resource_panel_height):
    global _render_queue_panel_expanded, _render_queue_panel_target_height, _render_queue_panel_anim_start_time, _last_baked_panel_job_id
    panel_x = (screen_width - RQ_WIDTH) // 2
    panel_y = resource_panel_height
    panel_rect = pygame.Rect(panel_x, panel_y, RQ_WIDTH, _render_queue_panel_current_height)
    gs = GameState()
    # If job_id changed while expanded, update expanded area
    if _render_queue_panel_expanded:
        if _last_baked_panel_job_id != gs.job_id:
            expanded_height = get_expanded_extra_height()
            _render_queue_panel_target_height = RQ_FOLDED_HEIGHT + expanded_height
            _render_queue_panel_anim_start_time = time.time()
            _last_baked_panel_job_id = gs.job_id
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and panel_rect.collidepoint(*event.pos):
        _render_queue_panel_expanded = not _render_queue_panel_expanded
        expanded_height = get_expanded_extra_height()
        _render_queue_panel_target_height = RQ_FOLDED_HEIGHT + (expanded_height if _render_queue_panel_expanded else 0)
        _render_queue_panel_anim_start_time = time.time()
        return True
    return False


class BaseItem:
    def __init__(self, name, progress=0.0, grad_start_col=(69, 79, 95), grad_end_col=(0, 187, 133), partitions=100):
        self.name = name
        self.progress = progress  # 0.0 to 1.0
        self.grad_start_col = grad_start_col
        self.grad_end_col = grad_end_col
        self.partitions = partitions  # The value the bar represents (e.g., 10 or 100)

    def draw(self, surface, x, y, width, height, font):
        bar_width = int(width * 0.9)
        bar_height = 20
        bar_x = x + (width - bar_width) // 2
        bar_y = y
        bg_col = exposure_color(UI_BG1_COL, 0.5)
        border_radius = bar_height // 3
        # Draw background with rounded corners
        pygame.draw.rect(surface, bg_col, (bar_x, bar_y, bar_width, bar_height), border_radius=border_radius)
        # Gradient progress bar with rounded corners
        left_col, right_col = self.grad_start_col, self.grad_end_col
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
        # Draw progress number in the center of the bar as integer value (0-partitions)
        value = int(self.progress * self.partitions)
        progress_text = font.render(f"{value} / {self.partitions}", True, TEXT1_COL)
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
_last_artist_progress = None

def bake_render_queue_items(job_id, shot_rows):
    """Create and return a baked list of RenderQueueItem objects for the current job."""
    return [BaseItem(f"Shot {i+1}", progress=0.5) for i in range(shot_rows)]

def get_progress_items(job_id, shot_rows, render_progress):
    """Return a list of RenderQueueItem with progress distributed according to render_progress.
    Each bar represents 0-100 units. Only one bar fills at a time.
    When a bar fills, increment GameState().total_shots_finished if not already counted."""
    gs = GameState()
    items = [BaseItem(f"Shot {i+1}") for i in range(shot_rows)]
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
    def __init__(self, width, font):
        self.width = width
        self.font = font

    def draw(self, surface, y=0):
        gs = GameState()
        shots_in_queue = gs.total_shots_finished + gs.total_shots_goal
        # Title (centered)
        title_str = f"Project overview - {gs.total_shots_finished} / {shots_in_queue} shots finished"
        title_text = self.font.render(title_str, True, TEXT1_COL)
        title_rect = title_text.get_rect(midtop=(self.width // 2, y + 7))
        surface.blit(title_text, title_rect)
        # Artist work (left, same row)
        artist_str = f"Artist work: {gs.artist_progress_current} / {gs.artist_progress_goal}"
        artist_text = self.font.render(artist_str, True, TEXT1_COL)
        artist_rect = artist_text.get_rect(midleft=(20, title_rect.centery))
        surface.blit(artist_text, artist_rect)
        # Render work (right, same row)
        render_str = f"Render work: {gs.render_progress_current} / {gs.render_progress_goal}"
        render_text = self.font.render(render_str, True, TEXT1_COL)
        render_rect = render_text.get_rect(midright=(self.width - 20, title_rect.centery))
        surface.blit(render_text, render_rect)

def bake_project_overview_panel(font, screen_width, resource_panel_height):
    """Bake the static render queue panel (background, border, title, and RenderQueueItems) into a surface."""
    global _last_baked_panel, _last_baked_panel_job_id, _last_baked_panel_shot_rows, _last_baked_panel_width, _last_baked_panel_height
    panel_x = (screen_width - RQ_WIDTH) // 2
    panel_y = resource_panel_height
    panel_height = _render_queue_panel_current_height
    panel_width = RQ_WIDTH
    gs = GameState()
    # Use total_shots_goal for shot_rows
    shot_rows = getattr(gs, 'total_shots_goal', 10)
    job_id = getattr(gs, 'job_id', 0)
    total_shots_finished = getattr(gs, 'total_shots_finished', 0)
    total_shots_goal = getattr(gs, 'total_shots_goal', 0)
    render_progress_current = getattr(gs, 'render_progress_current', 0)
    artist_progress_current = getattr(gs, 'artist_progress_current', 0)
    # Only re-bake if job_id, shot_rows, panel size, render_progress, or artist_progress changed
    global _last_render_progress, _last_progress_items, _last_artist_progress
    if (
        _last_baked_panel is not None and
        _last_baked_panel_job_id == job_id and
        _last_baked_panel_shot_rows == shot_rows and
        _last_baked_panel_width == panel_width and
        _last_baked_panel_height == panel_height and
        _last_render_progress == render_progress_current and
        _last_artist_progress == artist_progress_current
    ):
        return _last_baked_panel
    # Bake new panel
    panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    pygame.draw.rect(panel_surface, UI_BG1_COL, (0, 0, panel_width, panel_height))
    pygame.draw.rect(panel_surface, UI_BORDER1_COL, (0, 0, panel_width, panel_height), 2)
    # Header
    header = Header(panel_width, font)
    header.draw(panel_surface, y=0)
    # RenderQueueItems with progress
    items = get_progress_items(job_id, shot_rows, render_progress_current)
    _last_progress_items = items
    # Two columns: left for artist_progress_current, right for render_progress_current
    num_cols = 2
    col_width = panel_width // num_cols
    # Get artist progress for each shot (clearer version)
    artist_items = []
    for idx in range(len(items)):
        start = idx * 10
        end = (idx + 1) * 10
        if artist_progress_current >= end:
            progress = 1.0
        elif artist_progress_current > start:
            progress = (artist_progress_current - start) / 10.0
        else:
            progress = 0.0
        artist_items.append(BaseItem(
            f"Shot {idx+1}",
            progress=progress,
            grad_start_col=(86, 60, 52),
            grad_end_col=(203, 186, 72),
            partitions=10
        ))
    for idx in range(len(items)):
        # Left column: artist progress
        left_item = artist_items[idx]
        x_left = 0
        y = RQI_TOP_MARGIN + idx * (RQI_HEIGHT + RQI_SPACING)
        left_item.draw(panel_surface, x_left, y, col_width, RQI_HEIGHT, font)
        # Right column: render progress (use previous gradient colors, partitions=100)
        right_item = items[idx]
        right_item.grad_start_col = (69, 79, 95)  # Previous left color
        right_item.grad_end_col = (0, 187, 133)   # Previous right color
        right_item.partitions = 100
        x_right = col_width
        right_item.draw(panel_surface, x_right, y, col_width, RQI_HEIGHT, font)
    # Cache
    _last_baked_panel = panel_surface
    _last_baked_panel_job_id = job_id
    _last_baked_panel_shot_rows = shot_rows
    _last_baked_panel_width = panel_width
    _last_baked_panel_height = panel_height
    _last_render_progress = render_progress_current
    _last_artist_progress = artist_progress_current
    return panel_surface

def draw_project_overview_panel(surface, font, screen_width, resource_panel_height, render_queue_items=None):
    global _render_queue_panel_expanded, _render_queue_panel_current_height, _render_queue_panel_target_height, _render_queue_panel_anim_start_time, _last_baked_panel_job_id
    panel_x = (screen_width - RQ_WIDTH) // 2
    panel_y = resource_panel_height
    gs = GameState()
    # Update expansion/height if job_id changed while expanded
    if _render_queue_panel_expanded and _last_baked_panel_job_id != gs.job_id:
        _render_queue_panel_target_height = RQ_FOLDED_HEIGHT + get_expanded_extra_height()
        _render_queue_panel_anim_start_time = time.time()
        _last_baked_panel_job_id = gs.job_id
    # Animate height
    if _render_queue_panel_anim_start_time:
        t = min((time.time() - _render_queue_panel_anim_start_time) / ANIMATION_DURATION, 1.0)
        _render_queue_panel_current_height += int((_render_queue_panel_target_height - _render_queue_panel_current_height) * t)
        if t >= 1.0:
            _render_queue_panel_current_height = _render_queue_panel_target_height
            _render_queue_panel_anim_start_time = None
    else:
        _render_queue_panel_current_height = _render_queue_panel_target_height
    panel_rect = pygame.Rect(panel_x, panel_y, RQ_WIDTH, _render_queue_panel_current_height)
    surface.blit(bake_project_overview_panel(font, screen_width, resource_panel_height), (panel_x, panel_y))
    return panel_rect
