import pygame
from game_core.entity_definitions import BaseEntity
import time
import random

# List of alert conditions: each is a tuple (condition_fn, message)
# condition_fn(grid) -> bool
ALERT_CONDITIONS = [
    # Example: Too many unsatisfied computers
    (lambda grid: sum(1 for row in grid for e in row if isinstance(e, BaseEntity) and getattr(e, 'is_satisfied', 1) == 0 and hasattr(e, 'power_drain')) > 10,
     "Warning: More than 10 computers are unsatisfied!"),
    # Example: Any breaker is broken
    (lambda grid: any(getattr(e, 'is_broken', False) for row in grid for e in row if e),
     "Alert: At least one breaker is broken!"),
    # Add more conditions as needed
]

_ALERT_INTERVAL = 2.0  # seconds
_alert_cycle_idx = 0
_last_alert_time = 0
_active_alert = None

# Store visible alerts as a list of (message, timestamp, y_offset, x_offset)
_visible_alerts = []
_ALERT_DISPLAY_TIME = 20.0  # seconds each alert stays visible
_ALERT_ANIMATION_SPEED = 400  # pixels/sec

INFO_PANEL_WIDTH_FRAC = 0.15  # Fraction of screen width for info panel
ALERT_PANEL_WIDTH_FRAC = 0.2  # Fraction of screen width for alert panel


def get_info_panel_width(screen_width):
    return int(screen_width * INFO_PANEL_WIDTH_FRAC)


def check_alerts(grid, screen_width=None):
    global _alert_cycle_idx, _last_alert_time, _active_alert, _visible_alerts
    now = time.time()
    panel_height = 60
    # Always require screen_width for correct animation
    if screen_width is None:
        raise ValueError("screen_width must be provided to check_alerts for correct alert animation.")
    panel_width = int(screen_width * 0.3)
    if now - _last_alert_time >= _ALERT_INTERVAL:
        # Pick a random condition each time
        cond, msg = random.choice(ALERT_CONDITIONS)
        if cond(grid):
            # Only add if not already the most recent alert
            if not _visible_alerts or _visible_alerts[0][0] != msg:
                # Insert new alert at the top, with y_offset and x_offset for animation
                # x_offset starts at panel_width (offscreen right)
                _visible_alerts.insert(0, (msg, now, -panel_height, panel_width))
        _alert_cycle_idx += 1
        _last_alert_time = now
    # Remove expired alerts
    _visible_alerts = [(m, t, y, x) for m, t, y, x in _visible_alerts if now - t < _ALERT_DISPLAY_TIME]
    # Set the top alert for legacy compatibility
    _active_alert = _visible_alerts[0][0] if _visible_alerts else None
    return _active_alert


def draw_alert_panel(surface, font, screen_width, screen_height):
    # No offset from the right
    panel_width = int(screen_width * ALERT_PANEL_WIDTH_FRAC)
    panel_height = 60
    panel_x = screen_width - panel_width  # flush with right edge
    panel_y = 300
    now = time.time()
    dt = 1/40.0  # Assume 60 FPS for animation step
    slide_speed = 1000  # pixels/sec for horizontal slide
    # Animate y_offset and x_offset for each alert
    for i in range(len(_visible_alerts)):
        msg, t, y_offset, x_offset = _visible_alerts[i]
        if i == 0:
            y_offset = 0  # Newest alert always at the top, no vertical animation
            # Animate x_offset toward 0 (slide in from right)
            if x_offset > 0:
                x_offset = max(0, x_offset - slide_speed * dt)
        else:
            target_offset = i * (panel_height + 8)
            if y_offset < target_offset:
                y_offset = min(y_offset + _ALERT_ANIMATION_SPEED * dt, target_offset)
            elif y_offset > target_offset:
                y_offset = max(y_offset - _ALERT_ANIMATION_SPEED * dt, target_offset)
            x_offset = 0  # Only the newest alert slides in
        _visible_alerts[i] = (msg, t, y_offset, x_offset)
    # Draw alerts
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

