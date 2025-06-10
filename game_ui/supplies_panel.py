import pygame
pygame.font.init()
from game_core.config import UI_BG1_COL, UI_BORDER1_COL, BASE_COL, adjust_color, get_font1

FOLDED_WIDTH = 80
FOLDED_HEIGHT = 80
ROUNDING = 6
SUPPLIES_PANEL_X = 0
SUPPLIES_PANEL_Y_RATIO = 0.3

UNFOLDED_WIDTH = 500
UNFOLDED_HEIGHT = 300


class ExpandingPanelContent:
    def __init__(self, header, lines=None, font=None, header_font=None, icon_path=None):
        self.header = header
        self.lines = lines if lines is not None else []
        self.font = font or get_font1(24)
        self.header_font = header_font or get_font1(36)
        self.header_color = adjust_color(BASE_COL, white_factor=0.0, exposure=5)
        self.text_color = (0, 0, 0)
        self.icon_path = icon_path

    def draw(self, surface, x, y, icon_width=0, icon_height=0):
        # Use SUPPLIES_PANEL_WIDTH as left margin for header, and 10px top margin
        header_x = FOLDED_WIDTH + 20
        header_y = y + 10
        header_surf = self.header_font.render(self.header, True, self.header_color)
        surface.blit(header_surf, (header_x, header_y))
        # Draw lines below, left-aligned with header
        text_y = header_y + header_surf.get_height() + 12
        for line in self.lines:
            text_surf = self.font.render(line, True, self.text_color)
            surface.blit(text_surf, (header_x, text_y))
            text_y += text_surf.get_height() + 6


class ExpandingPanel:
    def __init__(self, x, y, width, height, content, icon_size=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.content = content
        self.icon_size = icon_size

    def draw(self, surface):
        content_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, UI_BG1_COL, content_rect, border_radius=ROUNDING)
        pygame.draw.rect(surface, UI_BORDER1_COL, content_rect, width=3, border_radius=ROUNDING)
        # Draw content inside the expanded area
        icon_w = self.icon_size if self.icon_size is not None else 0
        icon_h = self.icon_size if self.icon_size is not None else 0
        self.content.draw(surface, self.x, self.y, icon_width=icon_w, icon_height=icon_h)


class IconButton:
    def __init__(self, x, y_ratio, button_size, expanded_size, animation_duration=0.07, content=None, icon_path=None):
        self.button_width, self.button_height = button_size
        self.expanded_width, self.expanded_height = expanded_size
        self.x = x
        self.y_ratio = y_ratio
        self.expanded = False
        self.animating = False
        self.anim_start_time = None
        self.animation_duration = animation_duration
        self.current_width = self.button_width
        self.current_height = self.button_height
        self.font = pygame.font.SysFont(None, 24)
        self.icon_path = icon_path
        if isinstance(content, ExpandingPanelContent):
            self.content = content
        elif isinstance(content, (list, tuple)) and content:
            self.content = ExpandingPanelContent(content[0], content[1:], self.font, icon_path=icon_path)
        else:
            self.content = ExpandingPanelContent("", [], self.font, icon_path=icon_path)
        self.expanding_panel = None  # Will be created on demand

    def handle_event(self, event, surface):
        y = int(surface.get_size()[1] * self.y_ratio)
        rect = pygame.Rect(self.x, y, self.button_width, self.button_height)
        expanded_rect = pygame.Rect(self.x + self.button_width, y, self.expanded_width, self.expanded_height)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if rect.collidepoint(*event.pos) or (self.expanded and expanded_rect.collidepoint(*event.pos)):
                self.expanded = not self.expanded
                return True
        return False

    def update_animation(self):
        # No animation needed for this layout
        self.current_width = self.button_width
        self.current_height = self.button_height

    def draw(self, surface):
        y = int(surface.get_size()[1] * self.y_ratio)
        # Draw the main button (icon panel)
        panel_rect = pygame.Rect(self.x, y, self.button_width, self.button_height)
        pygame.draw.rect(surface, UI_BG1_COL, panel_rect, border_radius=ROUNDING)
        pygame.draw.rect(surface, UI_BORDER1_COL, panel_rect, width=3, border_radius=ROUNDING)
        from game_core.config import resource_path
        icon_path = self.icon_path or resource_path('data/graphics/supplies_panel/supplies.png')
        icon = None
        icon_size = min(self.button_width, self.button_height) - 16
        icon_x = self.x + (self.button_width - icon_size) // 2
        icon_y = y + (self.button_height - icon_size) // 2
        try:
            icon = pygame.image.load(icon_path).convert_alpha()
            icon = pygame.transform.smoothscale(icon, (icon_size, icon_size))
            surface.blit(icon, (icon_x, icon_y))
        except Exception:
            pass
        # Draw the expanded content area to the right using ExpandingPanel
        if self.expanded:
            if not self.expanding_panel:
                self.expanding_panel = ExpandingPanel(
                    self.x + self.button_width, y, self.expanded_width, self.expanded_height, self.content, icon_size=icon_size
                )
            else:
                # Update position in case of window resize
                self.expanding_panel.x = self.x + self.button_width
                self.expanding_panel.y = y
                self.expanding_panel.width = self.expanded_width
                self.expanding_panel.height = self.expanded_height
                self.expanding_panel.icon_size = icon_size
            self.expanding_panel.draw(surface)
        return panel_rect

# --- Multiple panels setup ---
panel_configs = [
    {
        'header': 'Supplies:',
        'lines': ['- Food', '- Water', '- Tools'],
        'icon_path': 'data/graphics/supplies_panel/supplies.png',
    },
    {
        'header': 'Equipment:',
        'lines': ['- Radios', '- Flashlights', '- Batteries'],
        'icon_path': 'data/graphics/supplies_panel/equipment.png',
    },
    {
        'header': 'Medical:',
        'lines': ['- Bandages', '- Medicine', '- First Aid'],
        'icon_path': 'data/graphics/supplies_panel/medical.png',
    },
    {
        'header': 'Tools:',
        'lines': ['- Hammer', '- Wrench', '- Screwdriver'],
        'icon_path': 'data/graphics/supplies_panel/tools.png',
    },
    {
        'header': 'Misc:',
        'lines': ['- Rope', '- Tape', '- Glue'],
        'icon_path': 'data/graphics/supplies_panel/misc.png',
    },
]

def create_panels(surface):
    panels = []
    panel_spacing = FOLDED_HEIGHT * 1.1
    screen_height = surface.get_height()
    for i, cfg in enumerate(panel_configs):
        y_ratio = SUPPLIES_PANEL_Y_RATIO + i * (panel_spacing / screen_height)
        panel = IconButton(
            SUPPLIES_PANEL_X,
            y_ratio,
            (FOLDED_WIDTH, FOLDED_HEIGHT),
            (UNFOLDED_WIDTH, UNFOLDED_HEIGHT),
            content=ExpandingPanelContent(cfg['header'], cfg['lines'], icon_path=cfg['icon_path']),
            icon_path=cfg['icon_path']
        )
        panels.append(panel)
    return panels

# Remove old panels list and creation
panels = []  # will be set in init or first draw

def handle_supplies_panel_event(event, surface):
    global panels
    if not panels or len(panels) != len(panel_configs):
        panels = create_panels(surface)
    clicked_idx = None
    for idx, panel in enumerate(panels):
        if panel.handle_event(event, surface):
            clicked_idx = idx
            break
    if clicked_idx is not None:
        # Collapse all other panels
        for j, other_panel in enumerate(panels):
            if j != clicked_idx and other_panel.expanded:
                other_panel.expanded = False
                other_panel.animating = True
                other_panel.anim_start_time = pygame.time.get_ticks()
        # Move the clicked panel to the end of the list (drawn last, on top)
        panels.append(panels.pop(clicked_idx))
        return True
    return False

def update_supplies_panel_animation():
    for panel in panels:
        panel.update_animation()

def draw_supplies_panel(surface):
    global panels
    if not panels or len(panels) != len(panel_configs):
        panels = create_panels(surface)
    rects = []
    for panel in panels:
        rects.append(panel.draw(surface))
    return rects
