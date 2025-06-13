import pygame
import math

# hidden_info_panel.py (renamed from entity_state_panel.py)
# Helper function to display the contents of entity_states in the top right corner for debugging.

ENTITY_PANEL_VISIBLE = False

def toggle_entity_panel():
    global ENTITY_PANEL_VISIBLE
    ENTITY_PANEL_VISIBLE = not ENTITY_PANEL_VISIBLE

def draw_hidden_info_panel(surface, font=None, hovered_entity=None, x_offset=5, y_offset=170, font_size=15, col_spacing=350):
    """
    Draws a debug panel in the bottom left corner showing the contents of the hovered entity
    and the current game_state global variables.
    font_size: If font is not provided, creates a font of this size.
    """
    if not ENTITY_PANEL_VISIBLE:
        return
    if font is None:
        font = pygame.font.SysFont(None, font_size)
    entity_lines = []
    # Show hovered entity info
    if hovered_entity is not None:
        entity_lines.append(f"Entity: {type(hovered_entity).__name__}")
        bases = type(hovered_entity).__bases__
        if bases:
            parent = bases[0]
            entity_lines.append(f"Parent class: {parent.__module__}.{parent.__name__}")
        else:
            entity_lines.append("Parent class: None")
        if hasattr(hovered_entity, 'get_public_attrs'):
            attrs = hovered_entity.get_public_attrs().items()
        else:
            attrs = [(k, v) for k, v in vars(hovered_entity).items() if not k.startswith('_') and not callable(v)]
        for k, v in attrs:
            if k == "names":
                continue
            entity_lines.append(f"    {k}: {v}")
    else:
        entity_lines.append("No entity under cursor")
    # Game state lines
    game_lines = []
    try:
        from game_core.game_state import get_totals_dict
        totals = get_totals_dict()
        game_lines.append("Game State Totals:")
        for k, v in totals.items():
            if k == "game_time_seconds":
                game_lines.append(f"    {k}: {int(v)}")
            else:
                game_lines.append(f"    {k}: {v}")
    except Exception as e:
        game_lines.append(f"[Game state unavailable: {e}]")
    # Prepare to render columns (swap order: game state first, then entity info)
    x = x_offset
    y = surface.get_height() - y_offset
    columns = [game_lines, entity_lines]
    for col_lines in columns:
        # Render lines for this column
        rendered_imgs = []
        max_line_width = 0
        total_height = 0
        for line in reversed(col_lines):
            img = font.render(line, True, (200, 220, 255))
            rendered_imgs.append(img)
            max_line_width = max(max_line_width, img.get_width())
            total_height += img.get_height() + 1
        total_height -= 1  # Remove last extra spacing
        # Draw semi-transparent background for this column
        bg_surf = pygame.Surface((max_line_width, total_height), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, int(255 * 0.4)))  # 80% opacity
        surface.blit(bg_surf, (x, y - total_height))
        # Draw text
        y_draw = y
        for img in rendered_imgs:
            rect = img.get_rect(topleft=(x, y_draw - img.get_height()))
            surface.blit(img, rect)
            y_draw -= img.get_height() + 1
        x += col_spacing

def handle_panel_toggle_event(event):
    if event.type == pygame.KEYDOWN and event.key == pygame.K_SEMICOLON:
        toggle_entity_panel()
