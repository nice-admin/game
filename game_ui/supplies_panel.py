import pygame
pygame.font.init()
from game_core.config import UI_BG1_COL, UI_BORDER1_COL, BASE_COL, adjust_color, get_font1, resource_path
from game_core.game_state import GameState, SUPPLIES_MAX

FOLDED_WIDTH = 80
FOLDED_HEIGHT = 80
ROUNDING = 6
SUPPLIES_PANEL_X = 0
SUPPLIES_PANEL_Y_RATIO = 0.32

UNFOLDED_WIDTH = 500
UNFOLDED_HEIGHT = 270


def draw_progress_bar_with_label(surface, label, progress, font, x, y, bar_width, bar_height=20, num_cells=10, cell_spacing=2, text_color=(0,0,0)):
    filled = int(num_cells * max(0.0, min(progress, 1.0)) + 0.0001)
    text = f"{filled} / {num_cells} {label}"
    text_surf = font.render(text, True, text_color)
    surface.blit(text_surf, (x, y))
    bar_y = y + text_surf.get_height() + 2
    cell_w = (bar_width - (num_cells - 1) * cell_spacing) // num_cells
    # Use the same gradient as indicators
    def get_gradient_color(progress):
        if progress <= 0.5:
            r = 255
            g = int(255 * (progress / 0.5))
            b = 0
        else:
            r = int(255 * (1 - (progress - 0.5) / 0.5))
            g = 255
            b = 0
        return (r, g, b)
    fill_color = get_gradient_color(max(0.0, min(progress, 1.0)))
    empty_color = adjust_color(BASE_COL, white_factor=0.0, exposure=2)
    for i in range(num_cells):
        cell_x = x + i * (cell_w + cell_spacing)
        color = fill_color if i < filled else empty_color
        pygame.draw.rect(surface, color, (cell_x, bar_y, cell_w, bar_height), border_radius=2)
    return bar_y + bar_height + 10


class ExpandingPanelContent:
    def __init__(self, header, lines=None, font=None, header_font=None, icon_path=None, progress_values=None):
        self.header = header
        self.lines = lines or []
        self.font = font or get_font1(20)
        self.header_font = header_font or get_font1(36)
        self.header_color = adjust_color(BASE_COL, white_factor=0.0, exposure=5)
        self.text_color = adjust_color(BASE_COL, white_factor=0.0, exposure=5)
        self.icon_path = icon_path
        self.progress_values = progress_values or [1.0] * len(self.lines)

    def draw(self, surface, x, y, icon_width=0, icon_height=0):
        header_x = x + 20
        header_y = y + 10
        header_surf = self.header_font.render(self.header, True, self.header_color)
        surface.blit(header_surf, (header_x, header_y))
        text_y = header_y + header_surf.get_height() + 12
        bar_width = int(UNFOLDED_WIDTH * 0.92)
        for idx, line in enumerate(self.lines):
            progress = self.progress_values[idx] if idx < len(self.progress_values) else 1.0
            text_y = draw_progress_bar_with_label(
                surface, line, progress, self.font, header_x, text_y, bar_width,
                bar_height=20, num_cells=10, cell_spacing=2, text_color=self.text_color
            )
            text_y += 10  # Add 10px spacing between bars


class ExpandingPanel:
    def __init__(self, x, y, width, height, content, icon_size=None, animation_duration=0.1):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.content = content
        self.icon_size = icon_size
        self.animation_duration = animation_duration  # seconds
        self.animating = False
        self.anim_start_time = None
        self.current_width = 0
        self.current_height = 0

    def start_animation(self):
        self.animating = True
        self.anim_start_time = pygame.time.get_ticks()
        self.current_width = 0
        self.current_height = 0

    def update_animation(self):
        if not self.animating:
            self.current_width = self.width
            self.current_height = self.height
            return
        elapsed = (pygame.time.get_ticks() - self.anim_start_time) / 1000.0
        t = min(elapsed / self.animation_duration, 1.0)
        self.current_width = int(self.width * t)
        self.current_height = self.height  # Keep height constant during animation
        if t >= 1.0:
            self.animating = False
            self.current_width = self.width
            self.current_height = self.height

    def draw(self, surface):
        self.update_animation()
        content_rect = pygame.Rect(self.x, self.y, self.current_width, self.current_height)
        pygame.draw.rect(surface, UI_BG1_COL, content_rect, border_radius=ROUNDING)
        pygame.draw.rect(surface, UI_BORDER1_COL, content_rect, width=3, border_radius=ROUNDING)
        # Only draw content if panel is visible
        if self.current_width > 20 and self.current_height > 20:
            # Use a temporary surface with alpha for masking
            panel_surface = pygame.Surface((self.current_width, self.current_height), pygame.SRCALPHA)
            icon_w = self.icon_size if self.icon_size is not None else 0
            icon_h = self.icon_size if self.icon_size is not None else 0
            self.content.draw(panel_surface, 0, 0, icon_width=icon_w, icon_height=icon_h)
            surface.blit(panel_surface, (self.x, self.y))


class Indicators:
    def __init__(self, iconbutton, rect_size=15, spacing=4):
        self.iconbutton = iconbutton
        self.rect_size = rect_size
        self.spacing = spacing

    def get_gradient_color(self, progress):
        # 0.0 = red, 0.5 = yellow, 1.0 = green
        if progress <= 0.5:
            # Red to yellow
            r = 255
            g = int(255 * (progress / 0.5))
            b = 0
        else:
            # Yellow to green
            r = int(255 * (1 - (progress - 0.5) / 0.5))
            g = 255
            b = 0
        return (r, g, b)

    def draw(self, surface):
        # Get the number of bars and their fullness from the content
        content = self.iconbutton.content
        num = len(content.lines)
        # Use progress_values if available, else full
        progresses = content.progress_values if hasattr(content, 'progress_values') else [1.0]*num
        # Position: right of the iconbutton
        x = self.iconbutton.x + self.iconbutton.button_width
        y0 = int(surface.get_size()[1] * self.iconbutton.y_ratio)
        total_height = num * self.rect_size + (num-1)*self.spacing if num > 0 else 0
        y = y0 + (self.iconbutton.button_height - total_height)//2
        for i, prog in enumerate(progresses):
            color = self.get_gradient_color(max(0.0, min(prog, 1.0)))
            rect = pygame.Rect(x, y + i*(self.rect_size+self.spacing), self.rect_size, self.rect_size)
            pygame.draw.rect(surface, color, rect, border_radius=2)


class IconButton:
    def __init__(self, x, y_ratio, button_size, expanded_size, animation_duration=None, content=None, icon_path=None):
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
        # Use animation_duration if provided, else use ExpandingPanel default
        panel_anim_duration = animation_duration if animation_duration is not None else 0.1
        self.expanding_panel = ExpandingPanel(
            self.x + self.button_width, int(pygame.display.get_surface().get_size()[1] * self.y_ratio),
            self.expanded_width, self.expanded_height, self.content, icon_size=min(self.button_width, self.button_height) - 16,
            animation_duration=panel_anim_duration
        )
        self.indicators = Indicators(self)

    def handle_event(self, event, surface):
        y = int(surface.get_size()[1] * self.y_ratio)
        rect = pygame.Rect(self.x, y, self.button_width, self.button_height)
        expanded_rect = pygame.Rect(self.x + self.button_width, y, self.expanded_width, self.expanded_height)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if rect.collidepoint(*event.pos) or (self.expanded and expanded_rect.collidepoint(*event.pos)):
                self.expanded = not self.expanded
                if self.expanded:
                    self.expanding_panel.start_animation()
                return True
        return False

    def update_animation(self):
        # No animation needed for this layout
        self.current_width = self.button_width
        self.current_height = self.button_height

    def update_expanding_panel(self, surface):
        y = int(surface.get_size()[1] * self.y_ratio)
        icon_size = min(self.button_width, self.button_height) - 16
        self.expanding_panel.x = self.x + self.button_width
        self.expanding_panel.y = y
        self.expanding_panel.width = self.expanded_width
        self.expanding_panel.height = self.expanded_height
        self.expanding_panel.icon_size = icon_size

    def draw(self, surface):
        y = int(surface.get_size()[1] * self.y_ratio)
        # Draw the main button (icon panel)
        panel_rect = pygame.Rect(self.x, y, self.button_width, self.button_height)
        pygame.draw.rect(surface, UI_BG1_COL, panel_rect, border_radius=ROUNDING)
        pygame.draw.rect(surface, UI_BORDER1_COL, panel_rect, width=3, border_radius=ROUNDING)
        icon_path = resource_path(self.icon_path) if self.icon_path else resource_path('data/graphics/supplies_panel/supplies.png')
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
        # Draw indicators to the right of the button (below the expanding panel)
        self.indicators.draw(surface)
        # Draw the expanded content area to the right using ExpandingPanel (draw after indicators so it covers them)
        if self.expanded or self.expanding_panel.animating:
            self.update_expanding_panel(surface)
            self.expanding_panel.draw(surface)
        return panel_rect

# --- Multiple panels setup ---
panel_configs = [
    {
        'header': 'Electronics:',
        'lines': [
            {'label': 'Cables', 'attr': 'total_cables'},
            {'label': 'Mouse', 'attr': 'total_mouses'},
            {'label': 'Keyboard', 'attr': 'total_keyboards'},
        ],
        'icon_path': 'data/graphics/supplies_panel/supplies.png',
    },
    {
        'header': 'Coffee:',
        'lines': [
            {'label': 'Coffee Beans', 'attr': 'total_coffee_beans'},
            {'label': 'Milk', 'attr': 'total_milk'},
            {'label': 'Sugar', 'attr': 'total_sugar'},
        ],
        'icon_path': 'data/graphics/supplies_panel/coffee.png',
    },
    {
        'header': 'Medicine:',
        'lines': [
            {'label': 'Ibalgin', 'attr': 'total_ibalgin'},
            {'label': 'Bandages', 'attr': 'total_bandages'},
            {'label': 'PCR Test', 'attr': 'total_pcr_test'},
        ],
        'icon_path': 'data/graphics/supplies_panel/medicine.png',
    },
    {
        'header': 'Tools:',
        'lines': [
            {'label': 'Hammer', 'attr': 'total_hammer'},
            {'label': 'Wrench', 'attr': 'total_wrench'},
            {'label': 'Screwdriver', 'attr': 'total_screwdriver'},
        ],
        'icon_path': 'data/graphics/supplies_panel/tools.png',
    },
    {
        'header': 'Misc:',
        'lines': [
            {'label': 'Rope', 'attr': 'total_rope'},
            {'label': 'Tape', 'attr': 'total_tape'},
            {'label': 'Glue', 'attr': 'total_glue'},
        ],
        'icon_path': 'data/graphics/supplies_panel/misc.png',
    },
]

def get_panel_progress_values(lines):
    gs = GameState()
    values = []
    for line in lines:
        attr = line.get('attr')
        if attr and hasattr(gs, attr):
            val = getattr(gs, attr, 0)
            values.append(val / SUPPLIES_MAX)
        else:
            values.append(1.0)
    return values

def create_panels(surface):
    panels = []
    panel_spacing = FOLDED_HEIGHT * 1.1
    screen_height = surface.get_height()
    for i, cfg in enumerate(panel_configs):
        y_ratio = SUPPLIES_PANEL_Y_RATIO + i * (panel_spacing / screen_height)
        progress_values = get_panel_progress_values(cfg['lines'])
        labels = [line['label'] for line in cfg['lines']]
        panel = IconButton(
            SUPPLIES_PANEL_X,
            y_ratio,
            (FOLDED_WIDTH, FOLDED_HEIGHT),
            (UNFOLDED_WIDTH, UNFOLDED_HEIGHT),
            content=ExpandingPanelContent(cfg['header'], labels, icon_path=cfg['icon_path'], progress_values=progress_values),
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
