import pygame
from game_core.entity_definitions import get_icon_surface
from collections import Counter
from game_core.config import *

def get_info_panel_width(screen_width):
    """Return the width of the info panel in pixels (fixed 260px)."""
    return 260


def get_entity_counts(grid):
    """Count entities in the grid and collect their icon paths."""
    counts = Counter()
    icon_paths = {}
    for row in grid:
        for e in row:
            if e is not None:
                cls = type(e)
                counts[cls] += 1
                icon_paths[cls] = get_entity_icon_path(e)
    return counts, icon_paths


def get_entity_icon_path(entity):
    """Helper to get the icon path from an entity."""
    icon_path = getattr(entity, 'get_icon_path', None)
    if callable(icon_path):
        return icon_path()
    return getattr(entity, '_icon', None)


def draw_info_panel(surface, font, screen_width, screen_height, grid=None):
    """Draw the info panel with entity icons and counts in a grid layout."""
    panel_width = get_info_panel_width(screen_width)
    panel_height = int(screen_height * 0.7)
    panel_x = screen_width - panel_width
    panel_y = int(screen_height * 0.15)
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    pygame.draw.rect(surface, UI_BG1_COL, panel_rect)
    pygame.draw.rect(surface, UI_BORDER1_COL, panel_rect, 2)
    
    # Draw entity counts grid if grid is provided
    if grid is not None:
        counts, icon_paths = get_entity_counts(grid)
        if counts:
            cols = 4
            icon_size = min(panel_width // cols - 12, 48)
            spacing_x = panel_width // cols
            spacing_y = icon_size + 28
            start_y = panel_y + 15
            start_x = panel_x + 8
            for idx, (cls, count) in enumerate(counts.most_common()):
                col = idx % cols
                row = idx // cols
                x = start_x + col * spacing_x
                y = start_y + row * spacing_y
                icon_path = icon_paths.get(cls)
                icon_surf = get_icon_surface(icon_path) if icon_path else None
                if icon_surf:
                    icon_surf = pygame.transform.smoothscale(icon_surf, (icon_size, icon_size))
                    icon_rect = icon_surf.get_rect(topleft=(x, y))
                    surface.blit(icon_surf, icon_rect)
                # Draw count in bottom right corner with white text and black background
                count_text = font.render(str(count), True, (255, 255, 255))
                count_rect = count_text.get_rect(bottomright=(x + icon_size - 2, y + icon_size - 2))
                bg_rect = count_rect.inflate(6, 4)
                pygame.draw.rect(surface, (0, 0, 0), bg_rect)
                surface.blit(count_text, count_rect)

    return panel_width