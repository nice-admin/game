import pygame
from game_core.config import BASE_COL, adjust_color

PANEL_WIDTH = 1300
PANEL_HEIGHT = 30
SEGMENTS = 50
BG_COLOR = (30, 30, 40, 220)
BAR_COLOR = (160, 49, 197)
BAR_BG_COLOR = (60, 60, 70)
BORDER_RADIUS = 4
ONSCREEN_TOP_MARGIN = 0.854  # Ratio for top margin placement (70% of screen height)
BAR_EMPTY_COLOR = adjust_color(BASE_COL, white_factor=0, exposure=2)

class Header:
    def __init__(self, level, current_exp, max_exp, font, x, y):
        self.level = level
        self.current_exp = current_exp
        self.max_exp = max_exp
        self.font = font
        self.x = x
        self.y = y

    def render(self, surface):
        text = f"Level {self.level} (Noob) - Experience {self.current_exp} / {self.max_exp}"
        text_surf = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(self.x, self.y))
        surface.blit(text_surf, text_rect)


class ExperiencePanel:
    def __init__(self, level=1, current_exp=0, max_exp=100, progress=0.0, font=None):
        self.level = level
        self.current_exp = current_exp
        self.max_exp = max_exp
        self.progress = progress
        self.font = font

    def draw(self, surface):
        surf_w, surf_h = surface.get_width(), surface.get_height()
        x = (surf_w - PANEL_WIDTH) // 2
        y = int(surf_h * ONSCREEN_TOP_MARGIN)
        # Draw background
        panel_rect = pygame.Rect(x, y, PANEL_WIDTH, PANEL_HEIGHT)
        panel_surf = pygame.Surface((PANEL_WIDTH, PANEL_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, BG_COLOR, panel_surf.get_rect(), border_radius=BORDER_RADIUS)
        surface.blit(panel_surf, (x, y))
        # Draw progress bar background
        bar_margin = 7
        bar_rect = pygame.Rect(x + bar_margin, y + bar_margin, PANEL_WIDTH - 2 * bar_margin, PANEL_HEIGHT - 2 * bar_margin)
        pygame.draw.rect(surface, BAR_BG_COLOR, bar_rect, border_radius=2)
        # Draw progress segments with perfectly uniform gaps
        segment_gap = 2
        total_gap = (SEGMENTS - 1) * segment_gap
        segment_width = (bar_rect.width - total_gap) / SEGMENTS
        filled_segments = int(self.progress * SEGMENTS)
        for i in range(SEGMENTS):
            seg_left_f = bar_rect.x + i * (segment_width + segment_gap)
            seg_right_f = seg_left_f + segment_width
            seg_left = int(round(seg_left_f))
            seg_right = int(round(seg_right_f))
            seg_rect = pygame.Rect(seg_left, bar_rect.y, seg_right - seg_left, bar_rect.height)
            color = BAR_COLOR if i < filled_segments else BAR_EMPTY_COLOR
            pygame.draw.rect(surface, color, seg_rect, border_radius=2)
            

def draw_experience_panel(surface, level=1, current_exp=0, max_exp=100, progress=0.0, font=None):
    """
    Draws the experience panel (header and bar) using the ExperiencePanel and Header classes.
    """
    if font is None:
        font = pygame.font.SysFont(None, 28)
    surf_w, surf_h = surface.get_width(), surface.get_height()
    x = (surf_w - PANEL_WIDTH) // 2
    y = int(surf_h * ONSCREEN_TOP_MARGIN)
    header = Header(level, current_exp, max_exp, font, x + PANEL_WIDTH // 2, y - 24)
    header.render(surface)
    panel = ExperiencePanel(level=level, current_exp=current_exp, max_exp=max_exp, progress=progress, font=font)
    panel.draw(surface)