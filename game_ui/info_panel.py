import pygame
from game_core.entity_definitions import get_icon_surface
from collections import Counter, defaultdict

def get_info_panel_width(screen_width):
    return int(screen_width * 0.11)

def get_entity_counts(grid):
    counts = Counter()
    icon_paths = {}
    for row in grid:
        for e in row:
            if e is not None:
                cls = type(e)
                counts[cls] += 1
                # Prefer get_icon_path if available, else _icon
                if hasattr(e, 'get_icon_path'):
                    icon_path = e.get_icon_path()
                else:
                    icon_path = getattr(e, '_icon', None)
                if icon_path:
                    icon_paths[cls] = icon_path
    return counts, icon_paths

def draw_info_panel(surface, font, screen_width, screen_height, grid=None):
    panel_width = get_info_panel_width(screen_width)
    panel_height = int(screen_height * 0.7)
    panel_x = screen_width - panel_width
    panel_y = int(screen_height * 0.15)
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    pygame.draw.rect(surface, (30, 30, 80), panel_rect)
    pygame.draw.rect(surface, (255, 255, 255), panel_rect, 2)
    # Draw entity counts grid if grid is provided
    if grid is not None:
        counts, icon_paths = get_entity_counts(grid)
        if counts:
            # Layout: 4 columns, dynamic rows
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
                # Draw count in bottom right corner
                count_text = font.render(str(count), True, (255, 255, 0))
                count_rect = count_text.get_rect(bottomright=(x + icon_size - 2, y + icon_size - 2))
                surface.blit(count_text, count_rect)
                # Optionally, show class name below icon (uncomment if needed)
                # name = getattr(cls, 'display_name', cls.__name__)
                # name_text = font.render(name, True, (200, 200, 255))
                # name_rect = name_text.get_rect(midtop=(x + icon_size // 2, y + icon_size + 2))
                # surface.blit(name_text, name_rect)
    return panel_width
