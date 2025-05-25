# debug_panel.py
# Draws a debug panel showing FPS, draw calls, and tick count in the top left area of the screen
import pygame
import time

DP_FONT_SIZE = 25
DP_ROW_SPACING = 20
DP_BG_COLOR = (0, 0, 100, int(0.7 * 255))  # RGBA: blue, 70% opacity
DP_TEXT_COLOR = (180, 180, 180)
DP_PAD_X = 16
DP_PAD_Y = 16
DP_WIDTH = 250

# Store ms history for the last 10 seconds
def _get_ms_history():
    if not hasattr(_get_ms_history, 'history'):
        _get_ms_history.history = []  # list of (timestamp, ms)
    return _get_ms_history.history

def draw_debug_panel(screen, clock, font=None, draw_call_count=None, tick_count=None, timings=None):
    """
    Draws a debug panel showing FPS, draw calls, tick count, and timings in the top left area of the screen.
    """
    font = pygame.font.SysFont(None, DP_FONT_SIZE)
    w, h = screen.get_width(), screen.get_height()
    px = int(w * 0.108)
    py = int(h * 0.1)
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
    # --- Feature toggles state ---
    try:
        import engine_others.feature_toggle as feature_toggle
        toggles = []
        for k in dir(feature_toggle):
            if k.isupper() and not k.startswith('__'):
                state = getattr(feature_toggle, k)
                state_str = 'ON' if state else 'OFF'
                color = (0, 255, 0) if state else (255, 0, 0)
                toggles.append((f"{state_str} {k}", color))
        if toggles:
            rows.append(("", DP_TEXT_COLOR))  # blank line
            rows.append(("Feature toggles:", DP_TEXT_COLOR))
            for t, color in toggles:
                rows.append((t.upper(), color))
    except Exception as e:
        rows.append((f"[Toggle error]", (255,0,0)))
    ph = DP_PAD_Y + len(rows) * DP_ROW_SPACING + 10  # Add 10px padding after last row
    pw = DP_WIDTH
    surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
    surf.fill(DP_BG_COLOR)
    screen.blit(surf, (px, py))
    y = py + DP_PAD_Y
    for text, color in rows:
        if text:
            text_surf = font.render(text, True, color)
            screen.blit(text_surf, (px + DP_PAD_X, y))
        y += DP_ROW_SPACING
