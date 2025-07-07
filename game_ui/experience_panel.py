import pygame
from game_core.config import BASE_COL, UI_BG1_COL, adjust_color
from game_core.game_state import GameState

PANEL_HEIGHT = 45
SEGMENTS = 100
BG_COLOR = UI_BG1_COL
BAR_COLOR = (160, 49, 197)
BAR_BG_COLOR = (60, 60, 70)
BORDER_RADIUS = 1
BAR_EMPTY_COLOR = adjust_color(BASE_COL, white_factor=0, exposure=2)
BASE_COLOR = (0, 200, 0)
BAR_SPACING = 0  # Space between bar segments

class ExperiencePanel:
    def __init__(self, level=1, current_exp=0, max_exp=100, progress=0.0, font=None, panel_width=None):
        self.level = level
        self.current_exp = current_exp
        self.max_exp = max_exp
        self.progress = progress
        self.font = font
        self.panel_width = panel_width  # Allow dynamic width

    def draw(self, surface):
        surf_w, surf_h = surface.get_width(), surface.get_height()
        panel_width = self.panel_width if self.panel_width is not None else surf_w
        x = 0
        y = surf_h - PANEL_HEIGHT  # Align to bottom edge
        # Draw background
        panel_rect = pygame.Rect(x, y, panel_width, PANEL_HEIGHT)
        panel_surf = pygame.Surface((panel_width, PANEL_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, BG_COLOR, panel_surf.get_rect(), border_radius=BORDER_RADIUS)
        surface.blit(panel_surf, (x, y))
        # Draw progress bar background (rounded corners)
        bar_margin = 4
        bar_rect = pygame.Rect(x + bar_margin, y + bar_margin, panel_width - 2 * bar_margin, PANEL_HEIGHT - 2 * bar_margin)
        pygame.draw.rect(surface, BAR_BG_COLOR, bar_rect, border_radius=8)
        # Create a surface for the filled progress bar (with per-pixel alpha)
        bar_surf = pygame.Surface((bar_rect.width, bar_rect.height), pygame.SRCALPHA)
        # Draw filled segments with glassy gradient onto bar_surf
        segment_gap = BAR_SPACING
        total_gap = (SEGMENTS - 1) * segment_gap
        segment_width = (bar_rect.width - total_gap) / SEGMENTS
        filled_segments = int(self.progress * SEGMENTS)
        for i in range(filled_segments):
            seg_left_f = i * (segment_width + segment_gap)
            seg_right_f = seg_left_f + segment_width
            seg_left = int(round(seg_left_f))
            seg_right = int(round(seg_right_f))
            seg_rect = pygame.Rect(seg_left, 0, seg_right - seg_left, bar_rect.height)
            for y_off in range(seg_rect.height):
                y_frac = y_off / (seg_rect.height - 1) if seg_rect.height > 1 else 0.5
                if y_frac < 0.45:
                    brightness = 0.7 + 1.0 * (y_frac / 0.5)
                elif y_frac < 0.5:
                    brightness = 1.7 - 0.7 * ((y_frac - 0.45) / 0.05)
                else:
                    brightness = 1.0 - 0.4 * ((y_frac - 0.5) / 0.5)
                r = min(255, max(0, int(BASE_COLOR[0] * brightness)))
                g = min(255, max(0, int(BASE_COLOR[1] * brightness)))
                b = min(255, max(0, int(BASE_COLOR[2] * brightness)))
                pygame.draw.line(bar_surf, (r, g, b), (seg_left, y_off), (seg_right - 1, y_off))
        # Mask the bar_surf with a rounded rectangle
        mask_surf = pygame.Surface((bar_rect.width, bar_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask_surf, (255, 255, 255, 255), mask_surf.get_rect(), border_radius=8)
        bar_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        # Blit the masked progress bar onto the main surface
        surface.blit(bar_surf, (bar_rect.x, bar_rect.y))
        # Draw empty segments onto a separate surface and mask it too
        empty_bar_surf = pygame.Surface((bar_rect.width, bar_rect.height), pygame.SRCALPHA)
        for i in range(filled_segments, SEGMENTS):
            seg_left_f = i * (segment_width + segment_gap)
            seg_right_f = seg_left_f + segment_width
            seg_left = int(round(seg_left_f))
            seg_right = int(round(seg_right_f))
            seg_rect = pygame.Rect(seg_left, 0, seg_right - seg_left, bar_rect.height)
            pygame.draw.rect(empty_bar_surf, BAR_EMPTY_COLOR, seg_rect, border_radius=1)
        empty_bar_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surface.blit(empty_bar_surf, (bar_rect.x, bar_rect.y))
        # Overlay 10 evenly spaced 2px white vertical lines over the progress bar
        num_lines = 10
        line_color = (255, 255, 255, 70)  # 20% opacity (51/255)
        line_width = 2
        overlay_surf = pygame.Surface((bar_rect.width, bar_rect.height), pygame.SRCALPHA)
        for i in range(1, num_lines + 1):
            frac = i / (num_lines + 1)
            line_x = int(frac * bar_rect.width)
            pygame.draw.rect(overlay_surf, line_color, (line_x - line_width // 2, 0, line_width, bar_rect.height), border_radius=1)
        # Add 50 short lines from bottom up to 30% of bar height
        num_short_lines = 54    
        short_line_color = (255, 255, 255, 70)  # 20% opacity
        short_line_width = 1
        short_line_height = int(bar_rect.height * 0.3)
        for i in range(1, num_short_lines + 1):
            frac = i / (num_short_lines + 1)
            line_x = int(frac * bar_rect.width)
            pygame.draw.rect(
                overlay_surf,
                short_line_color,
                (line_x - short_line_width // 2, bar_rect.height - short_line_height, short_line_width, short_line_height),
                border_radius=1
            )
        surface.blit(overlay_surf, (bar_rect.x, bar_rect.y))
            

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
    x = 0
    y = surf_h - PANEL_HEIGHT  # Align to bottom edge
    panel = ExperiencePanel(level=level, current_exp=current_exp, max_exp=max_exp, progress=progress, font=font, panel_width=surf_w)
    panel.draw(surface)
    text_overlay = TextOverlay(level=level, current_exp=current_exp, max_exp=max_exp, font=font, x=x, y=y, width=surf_w)
    text_overlay.render(surface)