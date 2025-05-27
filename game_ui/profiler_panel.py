# profiler_panel.py (moved from profiler.py)
# Place your profiling utilities here. If you have custom profiling code, paste it below.

import time
import pygame

# Draws a profiler panel showing FPS, draw calls, and tick count in the top left area of the screen
DP_FONT_SIZE = 25
DP_ROW_SPACING = 20
DP_BG_COLOR = (0, 0, 100, int(0.7 * 255))  # RGBA: blue, 70% opacity
DP_TEXT_COLOR = (180, 180, 180)
DP_PAD_X = 16
DP_PAD_Y = 16
DP_WIDTH = 250

_profiler_panel_visible = True

def handle_profiler_panel_toggle():
    global _profiler_panel_visible
    _profiler_panel_visible = not _profiler_panel_visible

def _get_ms_history():
    if not hasattr(_get_ms_history, 'history'):
        _get_ms_history.history = []  # list of (timestamp, ms)
    return _get_ms_history.history

def draw_profiler_panel(screen, clock, font, draw_call_count=None, tick_count=None, timings=None):
    if not _profiler_panel_visible:
        return
    """
    Draws a profiler panel showing FPS, draw calls, tick count, and timings in the top left area of the screen.
    Renders both the background and text onto a semi-transparent surface, then blits it to the main screen.
    """
    w, h = screen.get_width(), screen.get_height()
    px = 0  # Absolute top-left
    py = 0  # Absolute top-left
    rows = [
        (f"FPS: {int(clock.get_fps())}", DP_TEXT_COLOR)
    ]
    total_ms = None
    if draw_call_count is not None:
        rows.append((f"Draw calls: {draw_call_count}", DP_TEXT_COLOR))
    if tick_count is not None:
        rows.append((f"Tick: {tick_count}", DP_TEXT_COLOR))
    if timings:
        for label, ms in timings.items():
            rows.append((f"{label}: {ms:.2f} ms", DP_TEXT_COLOR))
        total_ms = sum(timings.values())
        rows.append((f"Total: {total_ms:.2f} ms", DP_TEXT_COLOR))
        # --- ms in last 10s ---
        ms_history = _get_ms_history()
        now = int(time.time())
        # Only add a new record if the second has changed
        if not ms_history or ms_history[-1][0] != now:
            ms_history.append((now, total_ms))
        # Keep only the last 10 seconds
        ms_history[:] = [(t, ms) for t, ms in ms_history if now - t < 10]
        if ms_history:
            avg_ms = sum(ms for t, ms in ms_history) / len(ms_history)
            rows.append((f"ms in last 10s: {avg_ms:.2f}", DP_TEXT_COLOR))
    ph = DP_PAD_Y + len(rows) * DP_ROW_SPACING + 10  # Add 10px padding after last row
    pw = DP_WIDTH
    surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
    surf.fill(DP_BG_COLOR)
    y = DP_PAD_Y
    for text, color in rows:
        if text:
            text_surf = font.render(text, True, color)
            surf.blit(text_surf, (DP_PAD_X, y))
        y += DP_ROW_SPACING
    screen.blit(surf, (px, py))

