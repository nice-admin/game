import pygame

def draw_construction_panel_new(surface, selected_section=0, selected_item=0, font=None, x=0, y=0, width=400, height=100):
    """
    Draws a new construction panel with two rows:
    - First row: 7 section buttons ("Computers", "Monitors", rest are "empty")
    - Second row: 10 item buttons (all say "empty button")
    Returns: (section_btn_rects, item_btn_rects)
    """
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
    item_labels = ["empty button"] * 10
    item_btn_w = width // 10
    item_btn_h = height // 2
    item_btn_rects = []
    for i, label in enumerate(item_labels):
        btn_rect = pygame.Rect(x + i * item_btn_w, y + section_btn_h, item_btn_w, item_btn_h)
        item_btn_rects.append(btn_rect)
        color = BTN_SELECTED if i == selected_item else BTN_COLOR
        pygame.draw.rect(surface, color, btn_rect)
        if font:
            text_surf = font.render(label, True, TEXT_COLOR)
            text_rect = text_surf.get_rect(center=btn_rect.center)
            surface.blit(text_surf, text_rect)

    return section_btn_rects, item_btn_rects
