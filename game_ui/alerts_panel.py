import pygame
import time
import random
from game_core.entity_definitions import BaseEntity

# --- Configurable constants ---
INFO_PANEL_WIDTH_FRAC = 0.15  # Fraction of screen width for info panel
ALERT_PANEL_WIDTH_FRAC = 0.2  # Fraction of screen width for alert panel
ALERT_DISPLAY_TIME = 20.0     # Seconds each alert stays visible
ALERT_ANIMATION_SPEED = 400   # Vertical animation speed (pixels/sec)
ALERT_SLIDE_SPEED = 1000      # Horizontal slide-in speed (pixels/sec)
ALERT_INTERVAL = 2.0          # Minimum seconds between alert checks
ALERT_PANEL_HEIGHT = 60       # Height of each alert panel (pixels)
ALERT_PANEL_Y = 300           # Y position of the alert panel stack
ALERT_PANEL_SPACING = 8       # Vertical spacing between alerts

# --- Alert state ---
_alert_cycle_idx = 0
_last_alert_time = 0
_active_alert = None
_visible_alerts = []  # List of (message, timestamp, y_offset, x_offset)

# --- Alert conditions: (condition_fn, message) ---
ALERT_CONDITIONS = [
    (lambda grid: sum(1 for row in grid for e in row if isinstance(e, BaseEntity) and getattr(e, 'is_satisfied', 1) == 0 and hasattr(e, 'power_drain')) > 10,
     "Warning: More than 10 computers are unsatisfied!"),
    (lambda grid: any(getattr(e, 'is_broken', False) for row in grid for e in row if e),
     "Alert: At least one breaker is broken!"),
    # Add more conditions as needed
]


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
        cond, msg = random.choice(ALERT_CONDITIONS)
        if cond(grid):
            if not _visible_alerts or _visible_alerts[0][0] != msg:
                # Insert new alert at the top, with y_offset and x_offset for animation
                _visible_alerts.insert(0, (msg, now, -ALERT_PANEL_HEIGHT, panel_width))
        _alert_cycle_idx += 1
        _last_alert_time = now
    # Remove expired alerts
    _visible_alerts = [(m, t, y, x) for m, t, y, x in _visible_alerts if now - t < ALERT_DISPLAY_TIME]
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
        msg, t, y_offset, x_offset = _visible_alerts[i]
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
        _visible_alerts[i] = (msg, t, y_offset, x_offset)
    # Draw alerts (oldest at bottom)
    for i, (alert, t, y_offset, x_offset) in enumerate(reversed(_visible_alerts)):
        y = panel_y + y_offset
        x = panel_x + x_offset
        panel_rect = pygame.Rect(int(x), int(y), panel_width, panel_height)
        pygame.draw.rect(surface, (200, 40, 40), panel_rect)
        pygame.draw.rect(surface, (255, 255, 255), panel_rect, 3)
        if font is not None:
            text = font.render(alert, True, (255, 255, 255))
            text_rect = text.get_rect(center=panel_rect.center)
            surface.blit(text, text_rect)

