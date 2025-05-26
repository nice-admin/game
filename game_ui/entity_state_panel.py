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
    Draws a debug panel in the bottom left corner showing the contents of the hovered entity
    and the current game_state global variables.
    font_size: If font is not provided, creates a font of this size.
    """
    if not ENTITY_PANEL_VISIBLE:
        return
    if font is None:
        font = pygame.font.SysFont(None, font_size)
    lines = []
    # Show hovered entity info
    if hovered_entity is not None:
        lines.append(f"Entity: {type(hovered_entity).__name__}")
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
    # Add a separator
    lines.append("-")
    # Show game_state global variables
    try:
        from game_core.game_state import get_totals_dict
        totals = get_totals_dict()
        lines.append("Game State Totals:")
        for k, v in totals.items():
            lines.append(f"    {k}: {v}")
    except Exception as e:
        lines.append(f"[Game state unavailable: {e}]")
    # Render lines in bottom left
    x = x_offset
    y = surface.get_height() - y_offset
    max_height = y_offset  # The topmost y position allowed
    for line in reversed(lines):
        img = font.render(line, True, (200, 220, 255))
        rect = img.get_rect(topleft=(x, y - img.get_height()))
        if y - img.get_height() < max_height:
            y = surface.get_height() - y_offset
            x += col_spacing
            rect = img.get_rect(topleft=(x, y - img.get_height()))
        surface.blit(img, rect)
        y -= img.get_height() + 1

def handle_panel_toggle_event(event):
    if event.type == pygame.KEYDOWN and event.key == pygame.K_SEMICOLON:
        toggle_entity_panel()
