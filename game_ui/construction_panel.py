import pygame
import inspect
from game_core import entity_definitions
from game_core.entity_base import *
from game_core.entity_definitions import *

# --- Constants ---
BG_COLOR = (40, 40, 40)
BTN_COLOR = (80, 80, 80)
BTN_SELECTED = (120, 120, 120)
TEXT_COLOR = (255, 255, 255)
SECTION_LABELS = ["Computers", "Monitors", "Utility", "Artists", "Management", "Decoration"] + ["empty"]

def get_computer_entities():
    classes = [obj for name, obj in inspect.getmembers(entity_definitions)
               if inspect.isclass(obj) and issubclass(obj, ComputerEntity) and obj is not ComputerEntity]
    return sorted(classes, key=lambda cls: getattr(cls, 'tier', 99))

def get_monitor_entities():
    classes = [obj for name, obj in inspect.getmembers(entity_definitions)
            if inspect.isclass(obj) and issubclass(obj, SatisfiableEntity) and obj.__name__.lower().endswith('monitor')]
    return sorted(classes, key=lambda cls: getattr(cls, 'tier', 99))

def get_utility_entities():
    classes = [Outlet, Breaker, Router, EspressoMachine, Snacks]
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
    def __init__(self, rect, label, icon_path=None, selected=False, height=None, width=None, icon_width=None, icon_height=None, icon_top_margin=None, entity_class=None):
        self.rect = rect
        self.label = label
        self.icon_path = icon_path
        self.selected = selected
        self.height = height or self.DEFAULT_HEIGHT
        self.width = width or self.DEFAULT_WIDTH
        self.icon_width = icon_width or self.DEFAULT_ICON_WIDTH
        self.icon_height = icon_height or self.DEFAULT_ICON_HEIGHT
        self.icon_top_margin = icon_top_margin or self.DEFAULT_ICON_TOP_MARGIN
        self.entity_class = entity_class

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

def get_entity_labels_and_icons(entity_classes, num_buttons):
    def get_display_name(cls):
        return getattr(cls, 'display_name', cls.__name__)
    items = [(get_display_name(cls), getattr(cls, '_icon', None), cls) for cls in entity_classes]
    if not items:
        return [], [], []
    items += [("-", None, None)] * (num_buttons - len(items))
    item_labels, entity_icons, entity_classes_out = zip(*items)
    return list(item_labels), list(entity_icons), list(entity_classes_out)

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

def draw_construction_panel(surface, selected_section=0, selected_item=None, font=None, x=None, y=None, width=None, height=100, number_of_entity_buttons=8):
    """
    Draws a new construction panel with two rows:
    - First row: 7 section buttons ("Computers", "Monitors", rest are "empty")
    - Second row: N item buttons (dynamically filled for section)
    Returns: (section_buttons, entity_buttons)
    """
    # Panel sizing and positioningw
    item_btn_w = EntityButton.DEFAULT_WIDTH
    num_entity_buttons = number_of_entity_buttons
    width = item_btn_w * num_entity_buttons
    x = (surface.get_width() - width) // 2
    y = surface.get_height() - (SectionButton.DEFAULT_HEIGHT + EntityButton.DEFAULT_HEIGHT)

    # Panel background
    panel_height = SectionButton.DEFAULT_HEIGHT + EntityButton.DEFAULT_HEIGHT
    panel_rect = pygame.Rect(x, y, width, panel_height)
    pygame.draw.rect(surface, BG_COLOR, panel_rect)

    # First row: Section buttons
    section_btn_w = width // 7
    section_btn_h = SectionButton.DEFAULT_HEIGHT
    section_buttons = []
    for i, label in enumerate(SECTION_LABELS):
        # For the last button, extend to the right edge
        if i == len(SECTION_LABELS) - 1:
            btn_rect = pygame.Rect(x + i * section_btn_w + 2, y + 2, width - (section_btn_w * i) - 4, section_btn_h - 4)
        else:
            btn_rect = pygame.Rect(x + i * section_btn_w + 2, y + 2, section_btn_w - 4, section_btn_h - 4)
        selected = (i == selected_section)
        color = BTN_SELECTED if selected else BTN_COLOR
        draw_button(surface, btn_rect, color, label, font)
        section_buttons.append(SectionButton(btn_rect, label, selected, height=section_btn_h - 4, width=btn_rect.width))

    # Second row: Entity buttons
    section_entity_defs = get_section_entity_defs()
    if 0 <= selected_section < len(section_entity_defs):
        entity_classes = section_entity_defs[selected_section]()
        item_labels, entity_icons, entity_classes_out = get_entity_labels_and_icons(entity_classes, num_entity_buttons)
    else:
        item_labels = ["empty button"] * num_entity_buttons
        entity_icons = [None] * num_entity_buttons
        entity_classes_out = [None] * num_entity_buttons
    item_btn_h = EntityButton.DEFAULT_HEIGHT
    entity_buttons = []
    for i, label in enumerate(item_labels):
        btn_rect = pygame.Rect(x + i * item_btn_w + 2, y + section_btn_h + 2, item_btn_w - 4, item_btn_h - 4)
        selected = (selected_item is not None and i == selected_item)
        color = BTN_SELECTED if selected else BTN_COLOR
        pygame.draw.rect(surface, color, btn_rect)
        icon_path = entity_icons[i]
        icon_width = EntityButton.DEFAULT_ICON_WIDTH
        icon_height = EntityButton.DEFAULT_ICON_HEIGHT
        icon_top_margin = EntityButton.DEFAULT_ICON_TOP_MARGIN
        draw_icon(surface, icon_path, btn_rect, icon_width, icon_height, icon_top_margin)
        if font:
            text_surf = font.render(label, True, TEXT_COLOR)
            text_rect = text_surf.get_rect(center=(btn_rect.centerx, btn_rect.bottom - 25))
            surface.blit(text_surf, text_rect)
        entity_buttons.append(EntityButton(
            btn_rect, label, icon_path, selected,
            height=item_btn_h - 4, width=btn_rect.width,
            icon_width=icon_width, icon_height=icon_height, icon_top_margin=icon_top_margin,
            entity_class=entity_classes_out[i]
        ))
    return section_buttons, entity_buttons
