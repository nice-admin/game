import pygame
import inspect
import hashlib
from game_core import entity_definitions
from game_core.entity_base import *
from game_core.entity_definitions import *

# --- Constants ---
BG_COLOR = (40, 40, 40)
BTN_COLOR = (60, 60, 60)
BTN_SELECTED = (100, 100, 100)
TEXT_COLOR = (255, 255, 255)
SECTION_LABELS = ["Computers", "Monitors", "Utility", "Artists", "Management", "Decoration"] + ["empty"]

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
    def __init__(self, rect, label, selected=False, height=None, width=None):
        self.rect = rect
        self.label = label
        self.selected = selected
        self.height = height if height is not None else self.DEFAULT_HEIGHT
        self.width = width if width is not None else rect.width

class EntityButton:
    DEFAULT_HEIGHT = 120
    DEFAULT_WIDTH = 180
    DEFAULT_ICON_WIDTH = 60
    DEFAULT_ICON_HEIGHT = 60
    DEFAULT_ICON_TOP_MARGIN = 10
    DEFAULT_LABEL_BOTTOM_MARGIN = 33
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
            self.label = getattr(entity_class, 'display_name', entity_class.__name__)
            self.icon_path = getattr(entity_class, '_icon', None)
            self.purchase_cost = getattr(entity_class, 'purchase_cost', None)
        else:
            self.label = "-"
            self.icon_path = None
            self.purchase_cost = None

    def draw(self, surface, font, text_color=TEXT_COLOR):
        pygame.draw.rect(surface, BTN_SELECTED if self.selected else BTN_COLOR, self.rect)
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
        if font:
            text_surf = font.render(self.label, True, text_color)
            text_rect = text_surf.get_rect(center=(self.rect.centerx, self.rect.bottom - self.label_bottom_margin))
            surface.blit(text_surf, text_rect)
        # Draw price/rental with smaller font
        if font:
            small_font_size = max(20, font.get_height() - 4)
            small_font = pygame.font.Font(None, small_font_size)
            if self.purchase_cost == 0:
                cost_surf = small_font.render("(subscription)", True, text_color)
                cost_rect = cost_surf.get_rect(center=(self.rect.centerx, self.rect.bottom + 20 - self.label_bottom_margin))
                surface.blit(cost_surf, cost_rect)
            elif self.purchase_cost not in (None, 0):
                cost_surf = small_font.render(f"${self.purchase_cost}", True, text_color)
                cost_rect = cost_surf.get_rect(center=(self.rect.centerx, self.rect.bottom + 20 - self.label_bottom_margin))
                surface.blit(cost_surf, cost_rect)

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
    item_btn_w = EntityButton.DEFAULT_WIDTH
    num_entity_buttons = number_of_entity_buttons
    width = item_btn_w * num_entity_buttons
    x = (surface.get_width() - width) // 2
    y = surface.get_height() - (SectionButton.DEFAULT_HEIGHT + EntityButton.DEFAULT_HEIGHT)
    panel_height = SectionButton.DEFAULT_HEIGHT + EntityButton.DEFAULT_HEIGHT
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
    panel_surf.fill(BG_COLOR)

    # First row: Section buttons
    section_btn_w = width // 7
    section_btn_h = SectionButton.DEFAULT_HEIGHT
    section_buttons = []
    for i, label in enumerate(SECTION_LABELS):
        if i == len(SECTION_LABELS) - 1:
            btn_rect = pygame.Rect(x + i * section_btn_w + 2 - x, 2, width - (section_btn_w * i) - 4, section_btn_h - 4)
        else:
            btn_rect = pygame.Rect(x + i * section_btn_w + 2 - x, 2, section_btn_w - 4, section_btn_h - 4)
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
    item_btn_h = EntityButton.DEFAULT_HEIGHT
    entity_buttons = []
    for i, entity_class in enumerate(entity_classes_out):
        btn_rect = pygame.Rect(i * item_btn_w + 2, section_btn_h + 2, item_btn_w - 4, item_btn_h - 4)
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
