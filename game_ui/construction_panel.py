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

def draw_construction_panel(surface, selected_section=0, selected_item=0, font=None, x=None, y=None, width=None, height=100):
    """
    Draws a new construction panel with two rows:
    - First row: 7 section buttons ("Computers", "Monitors", rest are "empty")
    - Second row: 10 item buttons (dynamically filled for Computers section)
    Returns: (section_btn_rects, item_btn_rects)
    """
    # Panel sizing and positioning (always width=1000, centered, bottom)
    width = 1000
    height = 100
    x = (surface.get_width() - width) // 2
    y = surface.get_height() - height

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
    section_btn_h = height // 2
    section_btn_rects = []
    for i, label in enumerate(section_labels):
        btn_rect = pygame.Rect(x + i * section_btn_w, y, section_btn_w, section_btn_h)
        section_btn_rects.append(btn_rect)
        color = BTN_SELECTED if i == selected_section else BTN_COLOR
        pygame.draw.rect(surface, color, btn_rect)
        if font:
            text_surf = font.render(label, True, TEXT_COLOR)
            text_rect = text_surf.get_rect(center=btn_rect.center)
            surface.blit(text_surf, text_rect)

    # Second row: Item buttons
    if selected_section == 0:  # Computers
        computer_classes = get_computer_entities()
        item_labels = [cls.__name__ for cls in computer_classes]
        # Pad to 10
        item_labels += ["empty button"] * (10 - len(item_labels))
        computer_icons = [getattr(cls, '_icon', None) for cls in computer_classes]
        computer_icons += [None] * (10 - len(computer_icons))
    else:
        item_labels = ["empty button"] * 10
        computer_icons = [None] * 10
    item_btn_w = width // 10
    item_btn_h = height // 2
    item_btn_rects = []
    for i, label in enumerate(item_labels):
        btn_rect = pygame.Rect(x + i * item_btn_w, y + section_btn_h, item_btn_w, item_btn_h)
        item_btn_rects.append(btn_rect)
        color = BTN_SELECTED if i == selected_item else BTN_COLOR
        pygame.draw.rect(surface, color, btn_rect)
        # Draw icon if available
        icon_path = computer_icons[i] if selected_section == 0 else None
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
    return section_btn_rects, item_btn_rects
