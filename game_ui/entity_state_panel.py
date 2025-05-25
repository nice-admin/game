import pygame
import math

# entity_state_panel.py
# Helper function to display the contents of entity_states in the top right corner for debugging.

ENTITY_PANEL_VISIBLE = True

def toggle_entity_panel():
    global ENTITY_PANEL_VISIBLE
    ENTITY_PANEL_VISIBLE = not ENTITY_PANEL_VISIBLE

def draw_entity_state_panel(surface, font=None, hovered_entity=None, x_offset=5, y_offset=20, font_size=15, col_spacing=150):
    """
    Draws a debug panel in the top right corner showing the contents of the hovered entity.
    font_size: If font is not provided, creates a font of this size.
    """
    if not ENTITY_PANEL_VISIBLE:
        return
    if font is None:
        font = pygame.font.SysFont(None, font_size)
    lines = []
    if hovered_entity is not None:
        lines.append(f"Entity: {type(hovered_entity).__name__}")
        # Show parent (base) class
        bases = type(hovered_entity).__bases__
        if bases:
            parent = bases[0]
            lines.append(f"Parent class: {parent.__module__}.{parent.__name__}")
        else:
            lines.append("Parent class: None")
        if hasattr(hovered_entity, 'get_public_attrs'):
            attrs = hovered_entity.get_public_attrs().items()
        else:
            attrs = [(k, v) for k, v in vars(hovered_entity).items() if not k.startswith('_') and not callable(v)]
        for k, v in attrs:
            lines.append(f"    {k}: {v}")
    else:
        lines.append("No entity under cursor")
    # Render lines
    y = y_offset
    x = x_offset
    max_height = surface.get_height() - y_offset
    for line in lines:
        img = font.render(line, True, (200, 220, 255))
        rect = img.get_rect(topright=(surface.get_width() - x, y))
        if y + img.get_height() > max_height:
            y = y_offset
            x += col_spacing
            rect = img.get_rect(topright=(surface.get_width() - x, y))
        surface.blit(img, rect)
        y += img.get_height() + 1

def handle_panel_toggle_event(event):
    if event.type == pygame.KEYDOWN and event.key == pygame.K_SEMICOLON:
        toggle_entity_panel()
