import pygame
import inspect
import hashlib
from game_core import entity_definitions
from game_core.entity_base import *
from game_core.entity_definitions import *
from game_core.config import BASE_COL, UI_BG1_COL, exposure_color

# --- Constants ---
BG_COLOR = UI_BG1_COL
BTN_COLOR = exposure_color(UI_BG1_COL, 1.3)
BTN_SELECTED = exposure_color(UI_BG1_COL, 1.7)
TEXT_COLOR = (255, 255, 255)
SECTION_LABELS = ["Computers", "Monitors", "Utility", "Artists", "Management", "Decoration"]

def get_computer_entities():
    classes = set()
    for base in (ComputerEntity, LaptopEntity):
        for name, obj in inspect.getmembers(entity_definitions):
            if inspect.isclass(obj) and issubclass(obj, base) and obj is not base:
                classes.add(obj)
    return sorted(classes, key=lambda cls: getattr(cls, 'tier', 99))

def get_monitor_entities():
    classes = [obj for name, obj in inspect.getmembers(entity_definitions)
            if inspect.isclass(obj) and issubclass(obj, SatisfiableEntity) and obj.__name__.lower().endswith('monitor')]
    return sorted(classes, key=lambda cls: getattr(cls, 'tier', 99))

def get_utility_entities():
    classes = []
    # Add Breaker first
    classes.append(entity_definitions.Breaker)
    for base in (UtilityEntity,):
        for name, obj in inspect.getmembers(entity_definitions):
            if inspect.isclass(obj) and issubclass(obj, base) and obj is not base and obj is not entity_definitions.Breaker:
                classes.append(obj)
    return sorted(classes, key=lambda cls: getattr(cls, 'tier', 99))

def get_artist_entities():
    classes = [obj for name, obj in inspect.getmembers(entity_definitions)
            if inspect.isclass(obj)
            and issubclass(obj, SatisfiableEntity)
            and 'artist' in obj.__name__.lower()]
    return sorted(classes, key=lambda cls: getattr(cls, 'tier', 99))

def get_management_entities():
    classes = [obj for name, obj in inspect.getmembers(entity_definitions)
            if inspect.isclass(obj)
            and issubclass(obj, SatisfiableEntity)
            and ('manager' in obj.__name__.lower() or 'project' in obj.__name__.lower())]
    return sorted(classes, key=lambda cls: getattr(cls, 'tier', 99))

def get_decoration_entities():
    classes = [obj for name, obj in inspect.getmembers(entity_definitions)
               if inspect.isclass(obj) and issubclass(obj, DecorationEntity) and obj is not DecorationEntity]
    return sorted(classes, key=lambda cls: getattr(cls, 'tier', 99))

class SectionButton:
    DEFAULT_HEIGHT = 40
    DEFAULT_WIDTH = 150
    def __init__(self, rect, label, selected=False, height=None, width=None):
        self.rect = rect
        self.label = label
        self.selected = selected
        self.height = height if height is not None else self.DEFAULT_HEIGHT
        self.width = width if width is not None else self.DEFAULT_WIDTH

class EntityButton:
    DEFAULT_HEIGHT = 130
    DEFAULT_WIDTH = 150
    DEFAULT_ICON_WIDTH = 60
    DEFAULT_ICON_HEIGHT = 60
    DEFAULT_ICON_TOP_MARGIN = 10
    DEFAULT_LABEL_BOTTOM_MARGIN = 33
    ROUNDING = 10  # Default corner radius for button rounding
    BG_COL = (211,218,221) # Default background color for entity button
    BG_COL_GRAD_START = (230,240,245)  # Gradient start color
    BG_COL_GRAD_END = (180,190,200)    # Gradient end color
    TEXT_COL = (46, 62, 79)  # Default text color for entity button
    INNER_SHADOW_COLOR = (0, 0, 0, 60)  # RGBA for subtle shadow
    INNER_SHADOW_OFFSET = -7  # How far the shadow is offset (for 45°)
    INNER_SHADOW_BLUR = 7  # Blur radius (not true blur, but feathering)
    def __init__(self, rect, entity_class=None, selected=False, height=None, width=None, icon_width=None, icon_height=None, icon_top_margin=None):
        self.rect = rect
        self.entity_class = entity_class
        self.selected = selected
        self.height = height or self.DEFAULT_HEIGHT
        self.width = width or self.DEFAULT_WIDTH
        self.icon_width = icon_width or self.DEFAULT_ICON_WIDTH
        self.icon_height = icon_height or self.DEFAULT_ICON_HEIGHT
        self.icon_top_margin = icon_top_margin or self.DEFAULT_ICON_TOP_MARGIN
        self.label_bottom_margin = self.DEFAULT_LABEL_BOTTOM_MARGIN
        # Extract label, icon, and price from entity_class
        if entity_class is not None:
            self.label = getattr(entity_class, 'display_name', entity_class.__name__).upper()
            self.icon_path = getattr(entity_class, '_icon', None)
            self.purchase_cost = getattr(entity_class, 'purchase_cost', None)
        else:
            self.label = "-"
            self.icon_path = None
            self.purchase_cost = None

    def _draw_gradient(self, surface):
        grad_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        # Offset the gradient start/end lower by shifting the ratio
        offset = int(self.rect.height * 0.18)  # 18% down
        for y in range(self.rect.height):
            # Shift the gradient so it starts lower
            shifted_y = max(0, y - offset)
            ratio = shifted_y / max(1, self.rect.height - 1 - offset)
            ratio = min(max(ratio, 0), 1)  # Clamp between 0 and 1
            r = int(self.BG_COL_GRAD_START[0] * (1 - ratio) + self.BG_COL_GRAD_END[0] * ratio)
            g = int(self.BG_COL_GRAD_START[1] * (1 - ratio) + self.BG_COL_GRAD_END[1] * ratio)
            b = int(self.BG_COL_GRAD_START[2] * (1 - ratio) + self.BG_COL_GRAD_END[2] * ratio)
            pygame.draw.line(grad_surf, (r, g, b), (0, y), (self.rect.width, y))
        grad_surf_rounded = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(grad_surf_rounded, (255,255,255), grad_surf_rounded.get_rect(), border_radius=self.ROUNDING)
        grad_surf_rounded.blit(grad_surf, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
        surface.blit(grad_surf_rounded, self.rect)

    def _draw_inner_shadow(self, surface):
        # Create a transparent surface for the shadow
        shadow_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        # Draw a semi-transparent black rounded rect, offset up/left for 45°
        for i in range(self.INNER_SHADOW_BLUR):
            alpha = int(self.INNER_SHADOW_COLOR[3] * (1 - i / self.INNER_SHADOW_BLUR))
            color = (*self.INNER_SHADOW_COLOR[:3], alpha)
            pygame.draw.rect(
                shadow_surf,
                color,
                pygame.Rect(
                    i + self.INNER_SHADOW_OFFSET,  # x offset (right)
                    i + self.INNER_SHADOW_OFFSET,  # y offset (down)
                    self.rect.width - 2 * i - self.INNER_SHADOW_OFFSET,
                    self.rect.height - 2 * i - self.INNER_SHADOW_OFFSET
                ),
                border_radius=max(1, self.ROUNDING - i)
            )
        # Mask with the button shape
        mask = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255,255,255,255), mask.get_rect(), border_radius=self.ROUNDING)
        shadow_surf.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
        surface.blit(shadow_surf, self.rect)

    def draw(self, surface, font, text_color=None):
        self._draw_gradient(surface)
        self._draw_inner_shadow(surface)
        if self.selected:
            pygame.draw.rect(surface, BTN_SELECTED, self.rect, border_radius=self.ROUNDING)
        # Draw icon
        if self.icon_path:
            try:
                icon_surf = pygame.image.load(self.icon_path).convert_alpha()
                icon_surf = pygame.transform.smoothscale(icon_surf, (self.icon_width, self.icon_height))
                icon_rect = icon_surf.get_rect(center=(self.rect.centerx, self.rect.top + self.icon_top_margin + self.icon_height//2))
                surface.blit(icon_surf, icon_rect)
            except Exception as e:
                print(f"Error loading icon {self.icon_path}: {e}")
        # Draw label
        col = text_color if text_color is not None else self.TEXT_COL
        if font:
            text_surf = font.render(self.label, True, col)
            text_rect = text_surf.get_rect(center=(self.rect.centerx, self.rect.bottom - self.label_bottom_margin))
            surface.blit(text_surf, text_rect)
        # Draw price/rental with smaller font
        if font:
            small_font_size = max(20, font.get_height() - 4)
            small_font = pygame.font.Font(None, small_font_size)
            if self.purchase_cost == 0:
                cost_surf = small_font.render("(subscription)", True, col)
                cost_rect = cost_surf.get_rect(center=(self.rect.centerx, self.rect.bottom + 20 - self.label_bottom_margin))
                surface.blit(cost_surf, cost_rect)
            elif self.purchase_cost not in (None, 0):
                cost_surf = small_font.render(f"${self.purchase_cost}", True, col)
                cost_rect = cost_surf.get_rect(center=(self.rect.centerx, self.rect.bottom + 20 - self.label_bottom_margin))
                surface.blit(cost_surf, cost_rect)

class Background:
    DEFAULT_COLOR = BG_COLOR
    DEFAULT_WIDTH = EntityButton.DEFAULT_WIDTH * 8 + 25  # Default for 8 entity buttons
    DEFAULT_HEIGHT = SectionButton.DEFAULT_HEIGHT + EntityButton.DEFAULT_HEIGHT
    ROUNDING = 12  # Default corner radius for background rounding

    def __init__(self, x=0, y=0, width=None, height=None, color=None, rounding=None):
        self.x = x
        self.y = y
        self.width = width if width is not None else self.DEFAULT_WIDTH
        self.height = height if height is not None else self.DEFAULT_HEIGHT
        self.color = color if color is not None else self.DEFAULT_COLOR
        self.rounding = rounding if rounding is not None else self.ROUNDING
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        pygame.draw.rect(
            surface,
            self.color,
            self.rect,
            border_top_left_radius=self.rounding,
            border_top_right_radius=self.rounding,
            border_bottom_left_radius=0,
            border_bottom_right_radius=0
        )

# --- Helper Functions ---
def draw_button(surface, rect, color, label=None, font=None, text_color=TEXT_COLOR):
    pygame.draw.rect(surface, color, rect)
    if label and font:
        text_surf = font.render(label, True, text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)

def get_section_entity_defs():
    return [
        lambda: get_computer_entities(),
        lambda: get_monitor_entities(),
        lambda: get_utility_entities(),
        lambda: get_artist_entities(),
        lambda: get_management_entities(),
        lambda: get_decoration_entities(),
    ]

def get_entity_labels_icons_costs(entity_classes, num_buttons):
    def get_display_name(cls):
        return getattr(cls, 'display_name', cls.__name__)
    def get_purchase_cost(cls):
        return getattr(cls, 'purchase_cost', None)
    items = [(get_display_name(cls), getattr(cls, '_icon', None), cls, get_purchase_cost(cls)) for cls in entity_classes]
    if not items:
        return [], [], [], []
    items += [("-", None, None, None)] * (num_buttons - len(items))
    item_labels, entity_icons, entity_classes_out, purchase_costs = zip(*items)
    return list(item_labels), list(entity_icons), list(entity_classes_out), list(purchase_costs)

def draw_icon(surface, icon_path, btn_rect, icon_width, icon_height, icon_top_margin):
    if not icon_path:
        return
    try:
        icon_surf = pygame.image.load(icon_path).convert_alpha()
        icon_surf = pygame.transform.smoothscale(icon_surf, (icon_width, icon_height))
        icon_rect = icon_surf.get_rect(center=(btn_rect.centerx, btn_rect.top + icon_top_margin + icon_height//2))
        surface.blit(icon_surf, icon_rect)
    except Exception as e:
        print(f"Error loading icon {icon_path}: {e}")

_baked_panel_cache = {
    'surface': None,
    'section_buttons': None,
    'entity_buttons': None,
    'state': None,
    'size': None,
}


def draw_construction_panel(surface, selected_section=0, selected_item=None, font=None, x=None, y=None, width=None, height=100, number_of_entity_buttons=8):
    """
    Draws a new construction panel with two rows:
    - First row: 7 section buttons ("Computers", "Monitors", rest are "empty")
    - Second row: N item buttons (dynamically filled for section)
    Returns: (section_buttons, entity_buttons)
    """
    # Panel sizing and positioning
    background = Background()
    width = background.width
    panel_height = background.height
    x = (surface.get_width() - width) // 2
    y = surface.get_height() - panel_height
    panel_rect = pygame.Rect(x, y, width, panel_height)

    # Create a hash of the current panel state for cache invalidation
    state_tuple = (selected_section, selected_item, surface.get_width(), surface.get_height())
    state_hash = hashlib.md5(str(state_tuple).encode()).hexdigest()
    size_tuple = (width, panel_height)

    # Check if we can use the cached panel
    if (
        _baked_panel_cache['surface'] is not None and
        _baked_panel_cache['state'] == state_hash and
        _baked_panel_cache['size'] == size_tuple
    ):
        # Blit the cached panel
        surface.blit(_baked_panel_cache['surface'], (x, y))
        return _baked_panel_cache['section_buttons'], _baked_panel_cache['entity_buttons']

    # Otherwise, bake a new panel
    panel_surf = pygame.Surface((width, panel_height), pygame.SRCALPHA)
    background.draw(panel_surf)

    # First row: Section buttons
    section_btn_w = SectionButton.DEFAULT_WIDTH
    section_btn_h = SectionButton.DEFAULT_HEIGHT
    num_sections = len(SECTION_LABELS)
    total_section_width = num_sections * section_btn_w
    section_btns_x_offset = (width - total_section_width) // 2
    section_buttons = []
    for i, label in enumerate(SECTION_LABELS):
        btn_rect = pygame.Rect(section_btns_x_offset + i * section_btn_w + 2, 2, section_btn_w - 4, section_btn_h - 4)
        selected = (i == selected_section)
        color = BTN_SELECTED if selected else BTN_COLOR
        draw_button(panel_surf, btn_rect, color, label, font)
        section_buttons.append(SectionButton(btn_rect.move(x, y), label, selected, height=section_btn_h - 4, width=btn_rect.width))

    # Second row: Entity buttons
    section_entity_defs = get_section_entity_defs()
    if 0 <= selected_section < len(section_entity_defs):
        entity_classes = section_entity_defs[selected_section]()
        entity_classes_out = list(entity_classes) + [None] * (number_of_entity_buttons - len(entity_classes))
    else:
        entity_classes_out = [None] * number_of_entity_buttons
    item_btn_w = EntityButton.DEFAULT_WIDTH
    item_btn_h = EntityButton.DEFAULT_HEIGHT
    entity_buttons = []
    # Center entity buttons horizontally in the panel
    total_btns_width = number_of_entity_buttons * item_btn_w
    entity_btns_x_offset = (width - total_btns_width) // 2
    for i, entity_class in enumerate(entity_classes_out):
        btn_rect = pygame.Rect(entity_btns_x_offset + i * item_btn_w + 2, section_btn_h + 2, item_btn_w - 4, item_btn_h - 4)
        selected = (selected_item is not None and i == selected_item)
        entity_button = EntityButton(
            btn_rect,  # Do NOT move(x, y) here!
            entity_class=entity_class,
            selected=selected,
            height=item_btn_h - 4,
            width=btn_rect.width,
            icon_width=EntityButton.DEFAULT_ICON_WIDTH,
            icon_height=EntityButton.DEFAULT_ICON_HEIGHT,
            icon_top_margin=EntityButton.DEFAULT_ICON_TOP_MARGIN,
        )
        entity_button.draw(panel_surf, font)
        # For event handling, store the button rect relative to the main surface
        entity_buttons.append(EntityButton(
            btn_rect.move(x, y),
            entity_class=entity_class,
            selected=selected,
            height=item_btn_h - 4,
            width=btn_rect.width,
            icon_width=EntityButton.DEFAULT_ICON_WIDTH,
            icon_height=EntityButton.DEFAULT_ICON_HEIGHT,
            icon_top_margin=EntityButton.DEFAULT_ICON_TOP_MARGIN,
        ))

    # Cache the baked panel
    _baked_panel_cache['surface'] = panel_surf
    _baked_panel_cache['section_buttons'] = section_buttons
    _baked_panel_cache['entity_buttons'] = entity_buttons
    _baked_panel_cache['state'] = state_hash
    _baked_panel_cache['size'] = size_tuple

    # Blit the baked panel
    surface.blit(panel_surf, (x, y))
    return section_buttons, entity_buttons
