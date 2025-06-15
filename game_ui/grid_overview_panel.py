import pygame
from game_core.entity_definitions import get_icon_surface
from collections import Counter
from game_core.config import UI_BG1_COL, TEXT1_COL
from game_ui.details_panel import ROWS_SPACING

MARGIN_FROM_TOP = 10
OVERVIEW_PANEL_WIDTH = 400
OVERVIEW_PANEL_HEIGHT = 160

class OverviewPanelHeader:
    """Header for the overview panel (empty, no title)."""
    def __init__(self, font, x, y):
        self.font = font
        self.x = x
        self.y = y
        self.name_rect = None

    def render(self, surface):
        # No title or text rendered
        self.name_rect = pygame.Rect(self.x, self.y, 0, 0)

def get_entity_icon_path(entity):
    """Return the icon path for an entity, or None if not available."""
    return getattr(entity, '_icon', None)

def get_entity_counts(grid):
    from collections import Counter
    counts = Counter()
    icon_paths = {}
    for row in grid:
        for e in row:
            if e is not None:
                cls = type(e)
                counts[cls] += 1
                icon_paths[cls] = get_entity_icon_path(e)
    return counts, icon_paths

def draw_overview_panel(surface, font, x, y, width=OVERVIEW_PANEL_WIDTH, height=OVERVIEW_PANEL_HEIGHT, grid=None):
    """
    Draws an overview panel at (x, y) with entity icons and counts, similar to details_panel design.
    """
    panel_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, UI_BG1_COL, panel_rect)
    # --- HEADER ---
    header = OverviewPanelHeader(font, x, y)
    header.render(surface)
    section_y = y + MARGIN_FROM_TOP
    # --- ICON GRID ---
    if grid is not None:
        counts, icon_paths = get_entity_counts(grid)
        if counts:
            cols = 6
            icon_size = min(width // cols - 12, 48)
            spacing_x = width // cols
            spacing_y = icon_size + 28
            start_y = section_y
            start_x = x + 8
            for idx, (cls, count) in enumerate(counts.most_common()):
                col = idx % cols
                row = idx // cols
                icon_x = start_x + col * spacing_x
                icon_y = start_y + row * spacing_y
                icon_path = icon_paths.get(cls)
                icon_surf = get_icon_surface(icon_path) if icon_path else None
                if icon_surf:
                    icon_surf = pygame.transform.smoothscale(icon_surf, (icon_size, icon_size))
                    icon_rect = icon_surf.get_rect(topleft=(icon_x, icon_y))
                    surface.blit(icon_surf, icon_rect)
                # Draw count in bottom right corner
                count_text = font.render(str(count), True, (255, 255, 255))
                count_rect = count_text.get_rect(bottomright=(icon_x + icon_size - 2, icon_y + icon_size - 2))
                bg_rect = count_rect.inflate(6, 4)
                pygame.draw.rect(surface, (0, 0, 0), bg_rect)
                surface.blit(count_text, count_rect)
