import pygame
from game_core.config import BASE_COL, UI_BG1_COL, adjust_color
from game_core.game_state import GameState

PANEL_WIDTH = 1320
PANEL_HEIGHT = 35
SEGMENTS = 50
BG_COLOR = UI_BG1_COL
BAR_COLOR = (160, 49, 197)
BAR_BG_COLOR = (60, 60, 70)
BORDER_RADIUS = 1
BAR_EMPTY_COLOR = adjust_color(BASE_COL, white_factor=0, exposure=2)

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
        y = surf_h - PANEL_HEIGHT  # Align to bottom edge
        # Draw background
        panel_rect = pygame.Rect(x, y, PANEL_WIDTH, PANEL_HEIGHT)
        panel_surf = pygame.Surface((PANEL_WIDTH, PANEL_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, BG_COLOR, panel_surf.get_rect(), border_radius=BORDER_RADIUS)
        surface.blit(panel_surf, (x, y))
        # Draw progress bar background
        bar_margin = 4
        bar_rect = pygame.Rect(x + bar_margin, y + bar_margin, PANEL_WIDTH - 2 * bar_margin, PANEL_HEIGHT - 2 * bar_margin)
        pygame.draw.rect(surface, BAR_BG_COLOR, bar_rect, border_radius=2)
        # Draw progress segments with gradient color
        segment_gap = 1
        total_gap = (SEGMENTS - 1) * segment_gap
        segment_width = (bar_rect.width - total_gap) / SEGMENTS
        filled_segments = int(self.progress * SEGMENTS)
        # Define a less dark base color for the gradient
        DARK_BAR_COLOR = (BAR_COLOR[0] // 2, BAR_COLOR[1] // 2, BAR_COLOR[2] // 2)
        def lerp(a, b, t):
            return int(a + (b - a) * t)
        for i in range(SEGMENTS):
            seg_left_f = bar_rect.x + i * (segment_width + segment_gap)
            seg_right_f = seg_left_f + segment_width
            seg_left = int(round(seg_left_f))
            seg_right = int(round(seg_right_f))
            seg_rect = pygame.Rect(seg_left, bar_rect.y, seg_right - seg_left, bar_rect.height)
            if i < filled_segments:
                t = i / max(1, SEGMENTS - 1)
                color = (
                    lerp(DARK_BAR_COLOR[0], BAR_COLOR[0], t),
                    lerp(DARK_BAR_COLOR[1], BAR_COLOR[1], t),
                    lerp(DARK_BAR_COLOR[2], BAR_COLOR[2], t)
                )
            else:
                color = BAR_EMPTY_COLOR
            pygame.draw.rect(surface, color, seg_rect, border_radius=1)
            

class TextOverlay:
    FONT_SIZE = 25  # Common font size for all text in the overlay
    LEFT_MARGIN = 15
    RIGHT_MARGIN = 15

    def __init__(self, level, current_exp, max_exp, font, x, y, width):
        self.level = level
        self.current_exp = current_exp
        self.max_exp = max_exp
        # Use the common font size
        self.font = pygame.font.SysFont(None, self.FONT_SIZE)
        self.x = x
        self.y = y
        self.width = width

    def render(self, surface):
        # Vertically center text in the panel
        text_y = self.y + PANEL_HEIGHT // 2
        # Left: gs.total_level
        try:
            from game_core.game_state import GameState
            gs = GameState()
            left_value = getattr(gs, 'total_level', self.level)
        except Exception:
            left_value = self.level
        left_text = f"Level {left_value}"
        left_surf = self.font.render(left_text, True, (255, 255, 255))
        left_rect = left_surf.get_rect(midleft=(self.x + self.LEFT_MARGIN, text_y))
        # Middle: rank text based on level
        rank_names = [
            "Executive Time Waster",
            "Overlord of Oversight",
            "Chief Chaos Coordinator",
            "KPI Jedi",
            "Morale Booster-in-Chief",
            "Growth Guru",
            "Lord of Success"
        ]
        rank_index = max(0, min(left_value - 1, len(rank_names) - 1))
        rank_text = rank_names[rank_index]
        mid_surf = self.font.render(rank_text, True, (255, 255, 255))
        mid_rect = mid_surf.get_rect(center=(self.x + self.width // 2, text_y))
        # Right: XX %
        percent = int(100 * self.current_exp / self.max_exp) if self.max_exp > 0 else 0
        right_text = f"{percent} %"
        right_surf = self.font.render(right_text, True, (255, 255, 255))
        right_rect = right_surf.get_rect(midright=(self.x + self.width - self.RIGHT_MARGIN, text_y))
        # Blit all
        surface.blit(left_surf, left_rect)
        surface.blit(mid_surf, mid_rect)
        surface.blit(right_surf, right_rect)


def draw_experience_panel(surface, font=None):
    """
    Draws the experience panel (header and bar) using the ExperiencePanel and Header classes.
    Always uses GameState for all values.
    Aligns the panel to the bottom edge of the screen.
    """
    gs = GameState()
    level = getattr(gs, 'level', 1)
    current_exp = getattr(gs, 'current_exp', 0)
    max_exp = getattr(gs, 'max_exp', 100)
    current_lvl_exp = getattr(gs, 'current_lvl_experience', 0)
    progress = min(1.0, current_lvl_exp / max_exp) if max_exp > 0 else 0.0
    if font is None:
        font = pygame.font.SysFont(None, 28)
    surf_w, surf_h = surface.get_width(), surface.get_height()
    x = (surf_w - PANEL_WIDTH) // 2
    y = surf_h - PANEL_HEIGHT  # Align to bottom edge
    panel = ExperiencePanel(level=level, current_exp=current_exp, max_exp=max_exp, progress=progress, font=font)
    panel.draw(surface)
    text_overlay = TextOverlay(level=level, current_exp=current_exp, max_exp=max_exp, font=font, x=x, y=y, width=PANEL_WIDTH)
    text_overlay.render(surface)