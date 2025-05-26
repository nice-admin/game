# game_ui/construction_panel.py

import pygame
import inspect
import game_core.entity_definitions as entities_mod
from game_core.entity_definitions import to_display_name_from_classname, get_icon_surface
from game_core.game_settings import FONT1_PATH, get_font1

# Build ENTITY_CHOICES once at import
ENTITY_CHOICES = [
    {
        "name": getattr(obj, 'display_name', to_display_name_from_classname(obj.__name__)),
        "class": obj,
        "icon": getattr(obj, '_icon', None)
    }
    for obj in entities_mod.__dict__.values()
    if inspect.isclass(obj)
    and issubclass(obj, entities_mod.BaseEntity)
    and obj is not entities_mod.BaseEntity
    and obj is not getattr(entities_mod, 'SatisfiableEntity', None)
    and obj.__module__ == entities_mod.__name__  # Only top-level classes from entity_definitions.py
]

def get_construction_panel_size(screen_width, screen_height):
    panel_width = int(screen_width * 0.5)
    panel_height = int(screen_height * 0.07)
    panel_x = (screen_width - panel_width) // 2  # Center horizontally
    panel_y = screen_height - panel_height - 10
    return panel_x, panel_y, panel_width, panel_height

def draw_construction_panel(surface, selected_index, font, x=10, y=10, width=220, height=200):
    if font is None:
        font = pygame.font.Font(FONT1_PATH, int(height * 0.18))
    panel_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, (40, 40, 40), panel_rect)
    pygame.draw.rect(surface, (80, 80, 80), panel_rect, 2)

    n = len(ENTITY_CHOICES)
    if n == 0:
        return
    margin = 6
    col_width = (width - (n + 1) * margin) // n
    icon_size = min(col_width - 8, height - 48)
    for i, entity in enumerate(ENTITY_CHOICES):
        bx = x + margin + i * (col_width + margin)
        by = y + margin
        entry_rect = pygame.Rect(bx, by, col_width, height - 2 * margin)
        pygame.draw.rect(surface, (90, 90, 90) if i == selected_index else (60, 60, 60), entry_rect)
        icon_path = entity["icon"]
        if icon_path:
            icon_surf = get_icon_surface(icon_path)
            if icon_surf:
                icon_surf = pygame.transform.smoothscale(icon_surf, (icon_size, icon_size))
                icon_rect = icon_surf.get_rect(center=(entry_rect.centerx, entry_rect.centery - 12))
                surface.blit(icon_surf, icon_rect)
        display_name = getattr(entity["class"], 'display_name', entity["name"])
        label = font.render(display_name, True, (220, 220, 220))
        label_rect = label.get_rect(center=(entry_rect.centerx, entry_rect.bottom - 18))
        surface.blit(label, label_rect)
