import pygame
import time
import random
from game_core.entity_definitions import BaseEntity, ComputerEntity, ProjectManager, Artist
from game_core.config import *
from game_core.game_state import GameState

# --- Configurable constants ---
INFO_PANEL_WIDTH_FRAC = 0.15  # Fraction of screen width for info panel
ALERT_PANEL_WIDTH_FRAC = 0.2  # Fraction of screen width for alert panel
ALERT_DISPLAY_TIME = 20.0     # Seconds each alert stays visible
ALERT_ANIMATION_SPEED = 400   # Vertical animation speed (pixels/sec)
ALERT_SLIDE_SPEED = 1000      # Horizontal slide-in speed (pixels/sec)
ALERT_INTERVAL = 10          # Minimum seconds between alert checks
ALERT_PANEL_HEIGHT = 40       # Height of each alert panel (pixels)
ALERT_PANEL_Y = 300           # Y position of the alert panel stack
ALERT_PANEL_SPACING = 8       # Vertical spacing between alerts

# --- Alert state ---
_alert_cycle_idx = 0
_last_alert_time = 0
_active_alert = None
_visible_alerts = []  # List of (message, timestamp, y_offset, x_offset)

# --- Alert conditions by type ---
ALERT_CONDITIONS_GOOD = [
    (lambda grid: not any((getattr(e, 'is_broken', 0) == 1 or getattr(e, 'is_satisfied', 1) == 0) for row in grid for e in row if e),
     "All systems optimal!", "good"),
]
ALERT_CONDITIONS_MID = [
    (lambda grid: any(isinstance(e, ComputerEntity) and getattr(e, 'is_initialized', 0) == 1 and getattr(e, 'is_satisfied', 1) == 0 for row in grid for e in row if e),
     "Our computers are lonely.", "mid"),
    (lambda grid: any(isinstance(e, ProjectManager) and getattr(e, 'is_initialized', 0) == 1 and getattr(e, 'is_satisfied', 1) == 0 for row in grid for e in row if e),
     "Project Managers are growing nervous.", "mid"),
    (lambda grid: any(isinstance(e, Artist) and getattr(e, 'is_initialized', 0) == 1 and getattr(e, 'is_satisfied', 1) == 0 for row in grid for e in row if e),
     "Artist's mind wanders.", "mid"),
] 
ALERT_CONDITIONS_BAD = [
    (lambda grid: any(getattr(e, 'is_broken', False) for row in grid for e in row if e),
     "Electrical systems are not in a good shape.", "bad"),
    (lambda grid: GameState().is_internet_online == 0,
     "We cannot argue with strangers on the internet anymore!", "bad"),
    (lambda grid: GameState().is_nas_online == 0,
     "Quickly, save on local disk!", "bad"),
]

# Combine all for random selection
ALERT_CONDITIONS = ALERT_CONDITIONS_GOOD + ALERT_CONDITIONS_MID + ALERT_CONDITIONS_BAD

# Map alert type to color
ALERT_TYPE_COLORS = {
    "good": STATUS_GOOD_COL,
    "mid": STATUS_MID_COL,
    "bad": STATUS_BAD_COL,
}


def get_info_panel_width(screen_width):
    """Return the width of the info panel in pixels."""
    return int(screen_width * INFO_PANEL_WIDTH_FRAC)


def get_alert_panel_width(screen_width):
    """Return the width of the alert panel in pixels."""
    return int(screen_width * ALERT_PANEL_WIDTH_FRAC)


def check_alerts(grid, screen_width):
    """Check alert conditions and update the visible alerts list."""
    global _alert_cycle_idx, _last_alert_time, _active_alert, _visible_alerts
    now = time.time()
    if screen_width is None:
        raise ValueError("screen_width must be provided to check_alerts for correct alert animation.")
    panel_width = get_alert_panel_width(screen_width)
    if now - _last_alert_time >= ALERT_INTERVAL:
        cond, msg, alert_type = random.choice(ALERT_CONDITIONS)
        if cond(grid):
            if not _visible_alerts or _visible_alerts[0][0] != msg:
                # Insert new alert at the top, with y_offset and x_offset for animation
                _visible_alerts.insert(0, (msg, now, -ALERT_PANEL_HEIGHT, panel_width, alert_type))
        _alert_cycle_idx += 1
        _last_alert_time = now
    # Remove expired alerts
    _visible_alerts = [(m, t, y, x, typ) for m, t, y, x, typ in _visible_alerts if now - t < ALERT_DISPLAY_TIME]
    _active_alert = _visible_alerts[0][0] if _visible_alerts else None
    return _active_alert


def draw_alert_panel(surface, font, screen_width, screen_height):
    """Draw the animated alert panel stack, right-aligned and offset by info panel width."""
    panel_width = get_alert_panel_width(screen_width)
    panel_height = ALERT_PANEL_HEIGHT
    panel_x = screen_width - panel_width  # flush with right edge
    panel_y = ALERT_PANEL_Y
    now = time.time()
    dt = 1/40.0  # Assume ~40 FPS for animation step
    # Animate y_offset and x_offset for each alert
    for i in range(len(_visible_alerts)):
        msg, t, y_offset, x_offset, alert_type = _visible_alerts[i]
        if i == 0:
            y_offset = 0  # Newest alert always at the top
            if x_offset > 0:
                x_offset = max(0, x_offset - ALERT_SLIDE_SPEED * dt)
        else:
            target_offset = i * (panel_height + ALERT_PANEL_SPACING)
            if y_offset < target_offset:
                y_offset = min(y_offset + ALERT_ANIMATION_SPEED * dt, target_offset)
            elif y_offset > target_offset:
                y_offset = max(y_offset - ALERT_ANIMATION_SPEED * dt, target_offset)
            x_offset = 0  # Only the newest alert slides in
        _visible_alerts[i] = (msg, t, y_offset, x_offset, alert_type)
    # Draw alerts (oldest at bottom)
    for i, (alert, t, y_offset, x_offset, alert_type) in enumerate(reversed(_visible_alerts)):
        y = panel_y + y_offset
        x = panel_x + x_offset
        alert_col = ALERT_TYPE_COLORS.get(alert_type, STATUS_MID_COL)
        if font is not None:
            text = font.render(alert, True, (255, 255, 255))
            text_rect = text.get_rect()
            # Add padding to the text background
            padding_x = 32
            padding_y = 12
            bg_width = text_rect.width + padding_x * 2
            bg_height = max(panel_height, text_rect.height + padding_y * 2)
            # Right-align the background
            bg_rect = pygame.Rect(int(x + panel_width - bg_width), int(y), bg_width, bg_height)
            # Draw main background
            pygame.draw.rect(surface, UI_BG1_COL, bg_rect)
            # Draw alert type color as a 5px high bar at the top
            bar_rect = pygame.Rect(bg_rect.left, bg_rect.top, bg_rect.width, 5)
            pygame.draw.rect(surface, alert_col, bar_rect)
            # Right-align the text inside the background
            text_rect.midright = (bg_rect.right - padding_x, bg_rect.centery + 1)
            surface.blit(text, text_rect)

