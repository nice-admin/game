import pygame
from game_core.config import UI_BG1_COL

MARGIN_FROM_TOP = 10  # Move all content down by this many pixels
ROWS_SPACING = 10    # Space between rows (icon, name, person_name, status, attributes)
TEXT_COL = (255, 255, 255)  # Default text color for all non-status text
DETAILS_PANEL_WIDTH = 400
DETAILS_PANEL_HEIGHT = 160
# --- Status message logic migrated from info_panel.py ---
def draw_status_by_state(surface, font, hovered_entity, box_x, box_y, icon_size):
    """Draws a status message based on the entity's state."""
    from game_core.entity_base import SatisfiableEntity, BaseEntity
    from game_core.config import STATUS_GOOD_COL, STATUS_INIT_COL, STATUS_MID_COL, STATUS_BAD_COL, STATUS_BASIC_COL
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
    import random
    if require_cls is not None and not isinstance(entity, require_cls):
        return
    global _last_hovered_entity_id, _last_ok_message
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
        if not hasattr(_draw_status, '_last_hovered_entity_id') or _draw_status._last_hovered_entity_id != entity_id:
            _draw_status._last_ok_message = random.choice(messages)
            _draw_status._last_hovered_entity_id = entity_id
        y_offset = 0  # Already positioned by y argument
        msg_text = font.render(_draw_status._last_ok_message, True, color)
        msg_rect = msg_text.get_rect(topleft=(box_x, box_y + y_offset))
        surface.blit(msg_text, msg_rect)

class Header:
    """Renders the header section (icon + display_name) for an entity."""
    def __init__(self, entity, font, x, y):
        self.entity = entity
        self.font = font
        self.x = x
        self.y = y
        self.icon_rect = None
        self.name_rect = None

    def render(self, surface):
        icon_path = getattr(self.entity, 'get_icon_path', None)
        if callable(icon_path):
            icon_path = icon_path()
        else:
            icon_path = getattr(self.entity, '_icon', None)
        icon_surf = None
        if icon_path:
            try:
                icon_surf = pygame.image.load(icon_path).convert_alpha()
                icon_surf = pygame.transform.smoothscale(icon_surf, (64, 64))
                surface.blit(icon_surf, (self.x + 16, self.y + MARGIN_FROM_TOP + ROWS_SPACING))
                self.icon_rect = pygame.Rect(self.x + 16, self.y + MARGIN_FROM_TOP + ROWS_SPACING, 64, 64)
            except Exception:
                self.icon_rect = None
        entity_name = getattr(self.entity, 'display_name', self.entity.__class__.__name__)
        if self.font:
            try:
                big_font = pygame.font.Font(self.font.get_name(), 32)
            except Exception:
                big_font = pygame.font.SysFont(None, 32)
            name_surf = big_font.render(entity_name, True, TEXT_COL)
            name_rect = name_surf.get_rect(topleft=(self.x + 96, self.y + MARGIN_FROM_TOP + ROWS_SPACING))
            surface.blit(name_surf, name_rect)
            self.name_rect = name_rect
        else:
            self.name_rect = None

def draw_details_panel(surface, font, x, y, width=DETAILS_PANEL_WIDTH, height=DETAILS_PANEL_HEIGHT, entity=None):
    """
    Draws a details panel at (x, y) with the given width and height.
    If an entity is provided, show its details; otherwise, show a placeholder.
    """
    # Panel background using UI_BG1_COL (with alpha if present)
    bg_col = UI_BG1_COL
    panel_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(panel_surf, bg_col, panel_surf.get_rect())
    surface.blit(panel_surf, (x, y))
    # --- HEADER ---
    if entity is not None:
        header = Header(entity, font, x, y)
        header.render(surface)
        # --- MAIN SECTION (10px below header) ---
        section_y = (header.name_rect.bottom if header.name_rect else y + MARGIN_FROM_TOP + ROWS_SPACING + 32) + 5
        # person_name (if present) under display_name, with dynamic spacing
        if hasattr(entity, 'person_name'):
            person_name = getattr(entity, 'person_name')
            person_name_surf = font.render(person_name, True, TEXT_COL)
            person_name_rect = person_name_surf.get_rect(topleft=(x + 96, section_y))
            surface.blit(person_name_surf, person_name_rect)
            y_status = person_name_rect.bottom + ROWS_SPACING
        else:
            y_status = section_y + ROWS_SPACING
        # Status message row (same mechanic as info_panel)
        draw_status_by_state(surface, font, entity, x + 96, y_status - 8, 0)
        # List public attributes (skip person_name/display_name)
        attr_y = y_status + ROWS_SPACING
        for idx, (k, v) in enumerate(sorted(entity.__dict__.items())):
            if not k.startswith('_') and k not in ("person_name", "display_name"):
                attr_surf = font.render(f"{k}: {v}", True, TEXT_COL)
                surface.blit(attr_surf, (x + 16, attr_y + idx * (22 + ROWS_SPACING)))
