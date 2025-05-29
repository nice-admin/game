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
    def __init__(self, rect, label, selected=False, height=None):
        self.rect = rect
        self.label = label
        self.selected = selected
        self.height = height if height is not None else self.DEFAULT_HEIGHT

class EntityButton:
    DEFAULT_HEIGHT = 120
    def __init__(self, rect, label, icon_path=None, selected=False, height=None):
        self.rect = rect
        self.label = label
        self.icon_path = icon_path
        self.selected = selected
        self.height = height if height is not None else self.DEFAULT_HEIGHT

def draw_construction_panel(surface, selected_section=0, selected_item=0, font=None, x=None, y=None, width=None, height=100):
    """
    Draws a new construction panel with two rows:
    - First row: 7 section buttons ("Computers", "Monitors", rest are "empty")
    - Second row: 10 item buttons (dynamically filled for Computers section)
    Returns: (section_buttons, entity_buttons)
    """
    # Panel sizing and positioning (always width=1000, centered, bottom)
    width = 1000
    # height is determined by button heights, so no need to set it here
    x = (surface.get_width() - width) // 2
    y = surface.get_height() - (SectionButton.DEFAULT_HEIGHT + EntityButton.DEFAULT_HEIGHT)

    # Colors
    BG_COLOR = (40, 40, 40)
    BTN_COLOR = (80, 80, 80)
    BTN_SELECTED = (120, 180, 255)
    TEXT_COLOR = (255, 255, 255)
    
    # Panel background
    panel_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, BG_COLOR, panel_rect)

    # First row: Section buttons
    section_labels = ["Computers", "Monitors"] + ["empty"] * 5
    section_btn_w = width // 7
    section_btn_h = SectionButton.DEFAULT_HEIGHT  # Use class default
    section_buttons = []
    for i, label in enumerate(section_labels):
        btn_rect = pygame.Rect(x + i * section_btn_w, y, section_btn_w, section_btn_h)
        selected = (i == selected_section)
        color = BTN_SELECTED if selected else BTN_COLOR
        pygame.draw.rect(surface, color, btn_rect)
        if font:
            text_surf = font.render(label, True, TEXT_COLOR)
            text_rect = text_surf.get_rect(center=btn_rect.center)
            surface.blit(text_surf, text_rect)
        section_buttons.append(SectionButton(btn_rect, label, selected, height=section_btn_h))

    # Second row: Entity buttons
    # Section entity definitions as a list of lambdas or functions
    from game_core.entity_base import SatisfiableEntity
    section_entity_defs = [
        lambda: get_computer_entities(),
        lambda: [obj for name, obj in inspect.getmembers(entity_definitions)
                 if inspect.isclass(obj) and issubclass(obj, SatisfiableEntity) and obj is not SatisfiableEntity],
    ]
    # Get entity classes for the selected section, or empty if out of range
    if 0 <= selected_section < len(section_entity_defs):
        entity_classes = section_entity_defs[selected_section]()
        item_labels = [cls.__name__ for cls in entity_classes]
        item_labels += ["empty button"] * (10 - len(item_labels))
        entity_icons = [getattr(cls, '_icon', None) for cls in entity_classes]
        entity_icons += [None] * (10 - len(entity_icons))
    else:
        item_labels = ["empty button"] * 10
        entity_icons = [None] * 10
    item_btn_w = width // 10
    item_btn_h = EntityButton.DEFAULT_HEIGHT  # Use class default
    entity_buttons = []
    for i, label in enumerate(item_labels):
        btn_rect = pygame.Rect(x + i * item_btn_w, y + section_btn_h, item_btn_w, item_btn_h)
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
        entity_buttons.append(EntityButton(btn_rect, label, icon_path, selected, height=item_btn_h))
    return section_buttons, entity_buttons
