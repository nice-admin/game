import pygame
import math

# entity_state_panel.py
# Helper function to display the contents of entity_states in the top right corner for debugging.

ENTITY_PANEL_VISIBLE = True

def toggle_entity_panel():
    global ENTITY_PANEL_VISIBLE
    ENTITY_PANEL_VISIBLE = not ENTITY_PANEL_VISIBLE

def draw_entity_state_panel(surface, font=None, grid=None, x_offset=5, y_offset=20, font_size=15, col_spacing=150, cell_size=None, camera_offset=None):
    """
    Draws a debug panel in the top right corner showing the contents of the entity under the mouse cursor.
    font_size: If font is not provided, creates a font of this size.
    cell_size: Size of each grid cell (required).
    camera_offset: (x, y) tuple for panning/scrolling (required).
    """
    if grid is None or not ENTITY_PANEL_VISIBLE or cell_size is None or camera_offset is None:
        return
    if font is None:
        font = pygame.font.SysFont(None, font_size)
    # Get mouse position and determine grid cell, accounting for camera offset
    mouse_x, mouse_y = pygame.mouse.get_pos()
    grid_x = int((mouse_x - camera_offset[0]) // cell_size)
    grid_y = int((mouse_y - camera_offset[1]) // cell_size)
    # Clamp to grid bounds
    grid_x = max(0, min(grid_x, len(grid[0]) - 1))
    grid_y = max(0, min(grid_y, len(grid) - 1))
    entity = grid[grid_y][grid_x] if grid and grid[grid_y][grid_x] is not None else None
    lines = []
    if entity is not None:
        lines.append(f"Entity at ({grid_x}, {grid_y}): {type(entity).__name__}")
        if hasattr(entity, 'get_public_attrs'):
            attrs = entity.get_public_attrs().items()
        else:
            attrs = [(k, v) for k, v in vars(entity).items() if not k.startswith('_') and not callable(v)]
        for k, v in attrs:
            lines.append(f"    {k}: {v}")
    else:
        lines.append(f"No entity at ({grid_x}, {grid_y})")
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
