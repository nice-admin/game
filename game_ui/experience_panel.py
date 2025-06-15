import pygame

PANEL_WIDTH = 1100
PANEL_HEIGHT = 30
SEGMENTS = 50
BG_COLOR = (30, 30, 40, 220)
BAR_COLOR = (160, 49, 197)
BAR_BG_COLOR = (60, 60, 70)
BORDER_RADIUS = 10
ONSCREEN_TOP_MARGIN = 0.85  # Ratio for top margin placement (70% of screen height)


def draw_experience_panel(surface, progress=0.0):
    """
    Draws the experience panel centered horizontally, 20% from the bottom of the screen.
    progress: float between 0.0 and 1.0
    """
    surf_w, surf_h = surface.get_width(), surface.get_height()
    x = (surf_w - PANEL_WIDTH) // 2
    y = int(surf_h * ONSCREEN_TOP_MARGIN)  # Use the defined margin for vertical placement

    # Draw background
    panel_rect = pygame.Rect(x, y, PANEL_WIDTH, PANEL_HEIGHT)
    panel_surf = pygame.Surface((PANEL_WIDTH, PANEL_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(panel_surf, BG_COLOR, panel_surf.get_rect(), border_radius=BORDER_RADIUS)
    surface.blit(panel_surf, (x, y))

    # Draw progress bar background
    bar_margin = 7
    bar_rect = pygame.Rect(x + bar_margin, y + bar_margin, PANEL_WIDTH - 2 * bar_margin, PANEL_HEIGHT - 2 * bar_margin)
    pygame.draw.rect(surface, BAR_BG_COLOR, bar_rect, border_radius=BORDER_RADIUS // 2)

    # Draw progress segments with perfectly uniform gaps
    segment_gap = 2
    total_gap = (SEGMENTS - 1) * segment_gap
    segment_width = (bar_rect.width - total_gap) / SEGMENTS
    filled_segments = int(progress * SEGMENTS)
    for i in range(SEGMENTS):
        seg_left_f = bar_rect.x + i * (segment_width + segment_gap)
        seg_right_f = seg_left_f + segment_width
        seg_left = int(round(seg_left_f))
        seg_right = int(round(seg_right_f))
        seg_rect = pygame.Rect(seg_left, bar_rect.y, seg_right - seg_left, bar_rect.height)
        color = BAR_COLOR if i < filled_segments else (100, 100, 100)
        pygame.draw.rect(surface, color, seg_rect, border_radius=1)
