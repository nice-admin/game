import pygame
import inspect
from game_core import entity_definitions
from game_core.entity_base import ComputerEntity

def get_computer_entities():
    # Find all classes in entity_definitions that are subclass of ComputerEntity (but not ComputerEntity itself)
    computers = []
    for name, obj in inspect.getmembers(entity_definitions):
        if inspect.isclass(obj) and issubclass(obj, ComputerEntity) and obj is not ComputerEntity:
            computers.append(obj)
    return computers

class SectionButton:
    DEFAULT_HEIGHT = 40
    DEFAULT_WIDTH = None  # Not used for panel sizing
    def __init__(self, rect, label, selected=False, height=None, width=None):
        self.rect = rect
        self.label = label
        self.selected = selected
        self.height = height if height is not None else self.DEFAULT_HEIGHT
        self.width = width if width is not None else rect.width

class EntityButton:
    DEFAULT_HEIGHT = 120
    DEFAULT_WIDTH = 150
    def __init__(self, rect, label, icon_path=None, selected=False, height=None, width=None):
        self.rect = rect
        self.label = label
        self.icon_path = icon_path
        self.selected = selected
        self.height = height if height is not None else self.DEFAULT_HEIGHT
        self.width = width if width is not None else self.DEFAULT_WIDTH

def draw_construction_panel(surface, selected_section=0, selected_item=0, font=None, x=None, y=None, width=None, height=100, number_of_entity_buttons=8):
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

    # Colors
    BG_COLOR = (40, 40, 40)
    BTN_COLOR = (80, 80, 80)
    BTN_SELECTED = (120, 120, 120)
    TEXT_COLOR = (255, 255, 255)
    
    # Panel background
    panel_height = SectionButton.DEFAULT_HEIGHT + EntityButton.DEFAULT_HEIGHT
    panel_rect = pygame.Rect(x, y, width, panel_height)
    pygame.draw.rect(surface, BG_COLOR, panel_rect)

    # First row: Section buttons
    section_labels = ["Computers", "Monitors"] + ["empty"] * 5
    section_btn_w = width // 7
    section_btn_h = SectionButton.DEFAULT_HEIGHT
    section_buttons = []
    for i, label in enumerate(section_labels):
        # For the last button, extend to the right edge
        if i == len(section_labels) - 1:
            btn_rect = pygame.Rect(x + i * section_btn_w + 2, y + 2, width - (section_btn_w * i) - 4, section_btn_h - 4)
        else:
            btn_rect = pygame.Rect(x + i * section_btn_w + 2, y + 2, section_btn_w - 4, section_btn_h - 4)
        selected = (i == selected_section)
        color = BTN_SELECTED if selected else BTN_COLOR
        pygame.draw.rect(surface, color, btn_rect)
        if font:
            text_surf = font.render(label, True, TEXT_COLOR)
            text_rect = text_surf.get_rect(center=btn_rect.center)
            surface.blit(text_surf, text_rect)
        section_buttons.append(SectionButton(btn_rect, label, selected, height=section_btn_h - 4, width=btn_rect.width))

    # Second row: Entity buttons
    from game_core.entity_base import SatisfiableEntity
    section_entity_defs = [
        lambda: get_computer_entities(),
        lambda: [obj for name, obj in inspect.getmembers(entity_definitions)
                 if inspect.isclass(obj) and issubclass(obj, SatisfiableEntity) and obj is not SatisfiableEntity],
    ]
    if 0 <= selected_section < len(section_entity_defs):
        entity_classes = section_entity_defs[selected_section]()
        item_labels = [cls.__name__ for cls in entity_classes]
        item_labels += ["empty button"] * (num_entity_buttons - len(item_labels))
        entity_icons = [getattr(cls, '_icon', None) for cls in entity_classes]
        entity_icons += [None] * (num_entity_buttons - len(entity_icons))
    else:
        item_labels = ["empty button"] * num_entity_buttons
        entity_icons = [None] * num_entity_buttons
    item_btn_h = EntityButton.DEFAULT_HEIGHT
    entity_buttons = []
    for i, label in enumerate(item_labels):
        btn_rect = pygame.Rect(x + i * item_btn_w + 2, y + section_btn_h + 2, item_btn_w - 4, item_btn_h - 4)
        selected = (i == selected_item)
        color = BTN_SELECTED if selected else BTN_COLOR
        pygame.draw.rect(surface, color, btn_rect)
        icon_path = entity_icons[i]
        if icon_path:
            try:
                icon_surf = pygame.image.load(icon_path).convert_alpha()
                icon_surf = pygame.transform.smoothscale(icon_surf, (item_btn_w - 8, item_btn_w - 8))
                icon_rect = icon_surf.get_rect(center=(btn_rect.centerx, btn_rect.top + (item_btn_w - 8)//2 + 2))
                surface.blit(icon_surf, icon_rect)
            except Exception:
                pass
        if font:
            text_surf = font.render(label, True, TEXT_COLOR)
            text_rect = text_surf.get_rect(center=(btn_rect.centerx, btn_rect.bottom - 14))
            surface.blit(text_surf, text_rect)
        entity_buttons.append(EntityButton(btn_rect, label, icon_path, selected, height=item_btn_h - 4, width=btn_rect.width))
    return section_buttons, entity_buttons
