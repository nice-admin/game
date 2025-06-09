import pygame
pygame.font.init()
from game_core.config import UI_BG1_COL, UI_BORDER1_COL, BASE_COL, adjust_color, get_font1

FOLDED_WIDTH = 80
FOLDED_HEIGHT = 80
ROUNDING = 6
SUPPLIES_PANEL_X = 0
SUPPLIES_PANEL_Y_RATIO = 0.2  # 20% from the top

UNFOLDED_WIDTH = 500
UNFOLDED_HEIGHT = 300


class PanelContent:
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
        if isinstance(content, PanelContent):
            self.content = content
        elif isinstance(content, (list, tuple)) and content:
            self.content = PanelContent(content[0], content[1:], self.font, icon_path=icon_path)
        else:
            self.content = PanelContent("", [], self.font, icon_path=icon_path)

    def handle_event(self, event, surface):
        y = int(surface.get_size()[1] * self.y_ratio)
        if self.expanded or self.animating:
            rect = pygame.Rect(self.x, y, self.current_width, self.current_height)
        else:
            rect = pygame.Rect(self.x, y, self.button_width, self.button_height)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if rect.collidepoint(*event.pos):
                self.expanded = not self.expanded
                self.animating = True
                self.anim_start_time = pygame.time.get_ticks()
                return True
        return False

    def update_animation(self):
        if not self.animating:
            self.current_width = self.expanded_width if self.expanded else self.button_width
            self.current_height = self.expanded_height if self.expanded else self.button_height
            return
        now = pygame.time.get_ticks()
        elapsed = (now - self.anim_start_time) / 1000.0
        t = min(elapsed / self.animation_duration, 1.0)
        if self.expanded:
            start_w, end_w = self.button_width, self.expanded_width
            start_h, end_h = self.button_height, self.expanded_height
        else:
            start_w, end_w = self.expanded_width, self.button_width
            start_h, end_h = self.expanded_height, self.button_height
        self.current_width = int(start_w + (end_w - start_w) * t)
        self.current_height = int(start_h + (end_h - start_h) * t)
        if t >= 1.0:
            self.current_width = end_w
            self.current_height = end_h
            self.animating = False

    def draw(self, surface):
        self.update_animation()
        y = int(surface.get_size()[1] * self.y_ratio)
        left_shift = 20
        panel_rect = pygame.Rect(self.x - left_shift, y, self.current_width + left_shift, self.current_height)
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
        # Draw content to a temporary surface, then blit it masked
        if self.expanded or self.animating:
            padding_x = 0
            padding_y = 0
            content_x = padding_x
            content_y = padding_y
            temp_surf = pygame.Surface((self.current_width + left_shift, self.current_height), pygame.SRCALPHA)
            # Draw header and lines, header to the right of icon
            self.content.draw(temp_surf, content_x, content_y, icon_width=icon_size, icon_height=icon_size)
            surface.blit(temp_surf, (self.x - left_shift, y))
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
        panel = ExpandingPanel(
            SUPPLIES_PANEL_X,
            y_ratio,
            (FOLDED_WIDTH, FOLDED_HEIGHT),
            (UNFOLDED_WIDTH, UNFOLDED_HEIGHT),
            content=PanelContent(cfg['header'], cfg['lines'], icon_path=cfg['icon_path']),
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
