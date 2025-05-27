import pygame
from game_core.entity_definitions import get_icon_surface
from collections import Counter
import random
from game_core.entity_base import *
from game_core.game_settings import *

# Store the last hovered entity and its chosen message
_last_hovered_entity_id = None
_last_ok_message = None

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

def draw_status_by_state(surface, font, hovered_entity, box_x, box_y, icon_size):
    """Draws a status message based on the entity's state."""
    state_messages = {
        'Good': (['Is okay', 'Is good', 'Seems fine', 'Looking good', 'No issues', 'Checks out', 'Keeping busy', 'Doing well', 'No trouble'], STATUS_GOOD_COL, SatisfiableEntity),
        'Init': (['Is preparing', 'Getting ready', 'Almost ready', 'Busy soon', 'Warming up', 'Booting up'], STATUS_INIT_COL, None),
        'Mid': (['Doesn\'t look good', 'Having issues', 'Has a problem', 'Needs help', 'Requires attention'], STATUS_MID_COL, None),
        'Bad': (['Beyond repair', 'Is out for good', "Won't be back", 'Totalled', 'Out of order', 'Needs replacement'], STATUS_BAD_COL, None),
        'Basic': (["Requires no attention", "Of no interest", "Simply exists", "Nothing to check", "Very boring"],  STATUS_BASIC_COL, BaseEntity),
    }
    state = getattr(hovered_entity, 'state', None)
    for key, (messages, color, require_cls) in state_messages.items():
        if state == key and (require_cls is None or isinstance(hovered_entity, require_cls)):
            _draw_status(
                surface, font, messages, color, hovered_entity,
                box_x=box_x, box_y=box_y, icon_size=icon_size, always_show=True, require_cls=require_cls
            )
            break

def _draw_status(surface, font, messages, color, entity, attr_name=None, box_x=0, box_y=0, icon_size=0, value=0, op='==', require_cls=None, always_show=False, conditions=None):
    """
    Draws a random message from messages in the given color if all conditions are met.
    conditions: list of (attr_name, op, value) tuples. All must be satisfied.
    If not provided, falls back to single-attribute logic for backward compatibility.
    Only shows the message if require_cls is None or entity is an instance of require_cls.
    The message is stable for the same entity and attr value.
    """
    global _last_hovered_entity_id, _last_ok_message
    if require_cls is not None and not isinstance(entity, require_cls):
        return
    if always_show:
        match = True
        attr_name_for_id = 'always_show'
        value_for_id = 0
        op_for_id = '=='
        entity_id = id(entity) + hash(attr_name_for_id) + hash(str(value_for_id)) + hash(op_for_id)
    elif conditions:
        ops = {
            '==': lambda a, b: a == b,
            '!=': lambda a, b: a != b,
            '<': lambda a, b: a < b,
            '<=': lambda a, b: a <= b,
            '>': lambda a, b: a > b,
            '>=': lambda a, b: a >= b,
        }
        match = True
        id_parts = [id(entity)]
        for cond_attr, cond_op, cond_val in conditions:
            attr_val = getattr(entity, cond_attr, None)
            if attr_val is None or not ops.get(cond_op, lambda a, b: False)(attr_val, cond_val):
                match = False
                break
            id_parts.append(hash(cond_attr))
            id_parts.append(hash(str(cond_val)))
            id_parts.append(hash(cond_op))
        entity_id = sum(id_parts)
        attr_name_for_id = str(conditions)
        value_for_id = 0
        op_for_id = ''
    else:
        attr_val = getattr(entity, attr_name, None)
        ops = {
            '==': lambda a, b: a == b,
            '!=': lambda a, b: a != b,
            '<': lambda a, b: a < b,
            '<=': lambda a, b: a <= b,
            '>': lambda a, b: a > b,
            '>=': lambda a, b: a >= b,
        }
        match = attr_val is not None and ops.get(op, lambda a, b: False)(attr_val, value)
        attr_name_for_id = attr_name
        value_for_id = value
        op_for_id = op
        entity_id = id(entity) + hash(attr_name_for_id) + hash(str(value_for_id)) + hash(op_for_id)
    if match:
        if _last_hovered_entity_id != entity_id:
            _last_ok_message = random.choice(messages)
            _last_hovered_entity_id = entity_id
        y_offset = 40  # Fixed vertical offset for all status messages
        msg_text = font.render(_last_ok_message, True, color)
        msg_rect = msg_text.get_rect(topleft=(box_x + icon_size + 18, box_y + y_offset))
        surface.blit(msg_text, msg_rect)


def draw_info_panel(surface, font, screen_width, screen_height, grid=None, hovered_entity=None):
    global _last_hovered_entity_id, _last_ok_message
    """Draw the info panel with entity icons and counts in a grid layout. Optionally show hovered entity info."""
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

    # Draw hovered entity info box at the top of the panel if provided
    if hovered_entity is not None:
        box_width = panel_width - 16
        box_height = 80
        box_x = panel_x + 8
        # Start at 50% height of the panel
        box_y = panel_y + (panel_height // 2)
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(surface, UI_BG1_COL, box_rect, border_radius=8)
        # Icon
        icon_path = get_entity_icon_path(hovered_entity)
        icon_surf = get_icon_surface(icon_path) if icon_path else None
        icon_size = 48
        if icon_surf:
            icon_surf = pygame.transform.smoothscale(icon_surf, (icon_size, icon_size))
            icon_rect = icon_surf.get_rect(topleft=(box_x + 8, box_y - 5 + (box_height - icon_size) // 2))
            surface.blit(icon_surf, icon_rect)
        # Name
        name = getattr(hovered_entity, 'display_name', hovered_entity.__class__.__name__)
        name_text = font.render(name, True, (255, 255, 255))
        name_rect = name_text.get_rect(topleft=(box_x + icon_size + 18, box_y + 20))
        surface.blit(name_text, name_rect)
        # Optionally, show more info (e.g., status, power, etc.)
        status = getattr(hovered_entity, 'status', None)
        if status:
            status_text = font.render(str(status), True, (200, 220, 255))
            status_rect = status_text.get_rect(topleft=(box_x + icon_size + 18, box_y + 38))
            surface.blit(status_text, status_rect)
        # Show a status message based on entity state
        draw_status_by_state(surface, font, hovered_entity, box_x, box_y, icon_size)


    return panel_width