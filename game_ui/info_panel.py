import pygame
from game_core.entity_definitions import get_icon_surface
from collections import Counter

def get_info_panel_width(screen_width):
    """Return the width of the info panel in pixels."""
    return int(screen_width * 0.11)


def get_entity_counts(grid):
    """Count entities in the grid and collect their icon paths."""
    counts = Counter()
    icon_paths = {}
    for row in grid:
        for e in row:
            if e is not None:
                cls = type(e)
                counts[cls] += 1
                icon_path = getattr(e, 'get_icon_path', None)
                if callable(icon_path):
                    icon_path = icon_path()
                else:
                    icon_path = getattr(e, '_icon', None)
                if icon_path:
                    icon_paths[cls] = icon_path
    return counts, icon_paths


def draw_info_panel(surface, font, screen_width, screen_height, grid=None):
    """Draw the info panel with entity icons and counts in a grid layout."""
    panel_width = get_info_panel_width(screen_width)
    panel_height = int(screen_height * 0.7)
    panel_x = screen_width - panel_width
    panel_y = int(screen_height * 0.15)
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    pygame.draw.rect(surface, (30, 30, 80), panel_rect)
    pygame.draw.rect(surface, (255, 255, 255), panel_rect, 2)

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

def draw_hovered_entity_info(surface, font, screen_width, screen_height, entity):
    """
    Draws a small info box in the info panel for the currently hovered entity.
    Shows the entity's icon, class name, and optionally other attributes.
    """
    if entity is None:
        return
    panel_width = get_info_panel_width(screen_width)
    panel_x = screen_width - panel_width
    panel_y = int(screen_height * 0.15)
    box_width = panel_width - 16
    box_height = 80
    box_x = panel_x + 8
    box_y = panel_y + 8
    box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
    pygame.draw.rect(surface, (40, 40, 100), box_rect, border_radius=8)
    pygame.draw.rect(surface, (255, 255, 255), box_rect, 2, border_radius=8)
    # Icon
    icon_path = getattr(entity, 'get_icon_path', None)
    if callable(icon_path):
        icon_path = icon_path()
    else:
        icon_path = getattr(entity, '_icon', None)
    icon_surf = get_icon_surface(icon_path) if icon_path else None
    icon_size = 48
    if icon_surf:
        icon_surf = pygame.transform.smoothscale(icon_surf, (icon_size, icon_size))
        icon_rect = icon_surf.get_rect(topleft=(box_x + 8, box_y + (box_height - icon_size) // 2))
        surface.blit(icon_surf, icon_rect)
    # Name
    name = getattr(entity, 'display_name', entity.__class__.__name__)
    name_text = font.render(name, True, (255, 255, 255))
    name_rect = name_text.get_rect(topleft=(box_x + icon_size + 18, box_y + 12))
    surface.blit(name_text, name_rect)
    # Optionally, show more info (e.g., status, power, etc.)
    # Example: show 'status' if present
    status = getattr(entity, 'status', None)
    if status:
        status_text = font.render(str(status), True, (200, 220, 255))
        status_rect = status_text.get_rect(topleft=(box_x + icon_size + 18, box_y + 38))
        surface.blit(status_text, status_rect)
