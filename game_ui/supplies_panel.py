import pygame
pygame.font.init()
from game_core.config import UI_BG1_COL, UI_BORDER1_COL, BASE_COL, adjust_color, get_font1, resource_path
from game_core.game_state import GameState, SUPPLIES_RND_MAX, SUPPLIES_MAX
from game_other.audio import play_purchase_sound
from game_core.config import CURRENCY_SYMBOL

FOLDED_WIDTH = 80
FOLDED_HEIGHT = 80
ROUNDING = 6
SUPPLIES_PANEL_X = 0
TOP_MARGIN = 0.38

UNFOLDED_WIDTH = 500
UNFOLDED_HEIGHT = 270

MAX_RANGE = 50


def draw_progress_bar_with_label(surface, label, progress, font, x, y, bar_width, bar_height=20, num_cells=10, cell_spacing=2, text_color=(0,0,0), value=None, max_value=None):
    filled = int(num_cells * max(0.0, min(progress, 1.0)) + 0.0001)
    # Show actual value/max if provided, else fallback to filled/num_cells
    if value is not None and max_value is not None:
        text = f"{value} / {max_value} {label}"
    else:
        text = f"{filled} / {num_cells} {label}"
    text_surf = font.render(text, True, text_color)
    surface.blit(text_surf, (x, y))
    bar_y = y + text_surf.get_height() + 2
    # Use float division for cell_w
    cell_ws = []
    cell_xs = []
    acc_x = x
    total_width = 0.0
    # Compute ideal cell width (float), but accumulate rounding error and compensate in last cell
    cell_w_float = (bar_width - (num_cells - 1) * cell_spacing) / num_cells
    for i in range(num_cells):
        # For all but last cell, round width, for last cell, use remaining width
        if i < num_cells - 1:
            width = round(cell_w_float)
        else:
            width = round(x + bar_width - acc_x)  # Ensure last cell ends at bar end
        cell_ws.append(width)
        cell_xs.append(int(round(acc_x)))
        acc_x += width + cell_spacing
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
        color = fill_color if i < filled else empty_color
        pygame.draw.rect(surface, color, (cell_xs[i], bar_y, cell_ws[i], bar_height), border_radius=2)
    return bar_y + bar_height + 10


class ExpandingPanelContent:
    def __init__(self, header, lines=None, font=None, header_font=None, icon_path=None, progress_values=None, value_pairs=None):
        self.header = header
        self.lines = lines or []
        self.font = font or get_font1(20)
        self.header_font = header_font or get_font1(36)
        self.header_color = adjust_color(BASE_COL, white_factor=0.0, exposure=5)
        self.text_color = adjust_color(BASE_COL, white_factor=0.0, exposure=5)
        self.icon_path = icon_path
        self.progress_values = progress_values or [1.0] * len(self.lines)
        self.value_pairs = value_pairs or [(None, None)] * len(self.lines)

    def draw(self, surface, x, y, icon_width=0, icon_height=0):
        header_x = x + 20
        header_y = y + 20
        header_surf = self.header_font.render(self.header, True, self.header_color)
        surface.blit(header_surf, (header_x, header_y))
        text_y = header_y + header_surf.get_height() + 12
        bar_width = UNFOLDED_WIDTH * 0.9
        for idx, line in enumerate(self.lines):
            progress = self.progress_values[idx] if idx < len(self.progress_values) else 1.0
            value, max_value = self.value_pairs[idx] if idx < len(self.value_pairs) else (None, None)
            text_y = draw_progress_bar_with_label(
                surface, line, progress, self.font, header_x, text_y, bar_width,
                bar_height=20, num_cells=MAX_RANGE, cell_spacing=2, text_color=self.text_color,
                value=value, max_value=max_value
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

class ResupplyButton:
    def __init__(self, x, y, width=FOLDED_WIDTH, height=30, label="Resupply", font=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.font = font or get_font1(15)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.hovered = False

    def draw(self, surface):
        if self.hovered:
            color = (0, 255, 0)  # bright green
        else:
            color = adjust_color(BASE_COL, white_factor=0.0, exposure=1)
        text_color = adjust_color(BASE_COL, white_factor=0.0, exposure=3)
        pygame.draw.rect(surface, color, self.rect, border_radius=2)
        text_surf = self.font.render(self.label, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

        # Draw the second rectangle below the main button, at 0.8x width and centered
        second_rect_height = 20
        second_rect_width = int(self.width * 0.8)
        second_rect_x = self.x + (self.width - second_rect_width) // 2
        second_rect_y = self.y + self.height  # 4px gap
        second_rect = pygame.Rect(second_rect_x, second_rect_y, second_rect_width, second_rect_height)
        second_color = adjust_color(BASE_COL, white_factor=0.0, exposure=2)
        second_text_color = adjust_color(BASE_COL, white_factor=0.0, exposure=5)
        pygame.draw.rect(surface, second_color, second_rect, border_radius=2)
        price = get_resupply_price()
        price_font = get_font1(14)
        price_surf = price_font.render(f"{price}{CURRENCY_SYMBOL}", True, second_text_color)
        price_rect = price_surf.get_rect(center=second_rect.center)
        surface.blit(price_surf, price_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

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
    }
]

def get_panel_progress_and_values(lines):
    gs = GameState()
    progress_values = []
    value_pairs = []
    for line in lines:
        attr = line.get('attr')
        if attr and hasattr(gs, attr):
            val = getattr(gs, attr, 0)
            progress_values.append(val / MAX_RANGE)
            value_pairs.append((val, MAX_RANGE))
        else:
            progress_values.append(1.0)
            value_pairs.append((None, MAX_RANGE))
    return progress_values, value_pairs

def get_resupply_price():
    """
    Calculate the resupply price as the sum of all missing singleton supply values (from supplies panel) times 50.
    """
    gs = GameState()
    total_missing = 0
    for cfg in panel_configs:
        for line in cfg['lines']:
            attr = line.get('attr')
            if attr and hasattr(gs, attr):
                current = getattr(gs, attr, 0)
                missing = MAX_RANGE - current
                if missing > 0:
                    total_missing += missing
    return total_missing * 10

def create_panels(surface):
    panels = []
    panel_spacing = FOLDED_HEIGHT * 1.1
    screen_height = surface.get_height()
    for i, cfg in enumerate(panel_configs):
        y_ratio = TOP_MARGIN + i * (panel_spacing / screen_height)
        progress_values, value_pairs = get_panel_progress_and_values(cfg['lines'])
        labels = [line['label'] for line in cfg['lines']]
        panel = IconButton(
            SUPPLIES_PANEL_X,
            y_ratio,
            (FOLDED_WIDTH, FOLDED_HEIGHT),
            (UNFOLDED_WIDTH, UNFOLDED_HEIGHT),
            content=ExpandingPanelContent(cfg['header'], labels, icon_path=cfg['icon_path'], progress_values=progress_values, value_pairs=value_pairs),
            icon_path=cfg['icon_path']
        )
        panel.lines_config = cfg['lines']  # Store the original config for updates
        panels.append(panel)
    return panels

# Remove old panels list and creation
panels = []  # will be set in init or first draw
resupply_button = None  # global button instance

def handle_supplies_panel_event(event, surface):
    global panels, resupply_button
    if not panels or len(panels) != len(panel_configs):
        panels = create_panels(surface)
    # Place resupply button 10px above the first IconButton
    if resupply_button is None:
        first_panel_y = int(surface.get_size()[1] * TOP_MARGIN)
        resupply_button = ResupplyButton(SUPPLIES_PANEL_X, first_panel_y - 10 - 50)  # 30 is button height
    if resupply_button.handle_event(event):
        play_purchase_sound()
        gs = GameState()
        price = get_resupply_price()
        gs.total_money -= price
        gs.total_cables = SUPPLIES_MAX
        gs.total_mouses = SUPPLIES_MAX
        gs.total_keyboards = SUPPLIES_MAX
        gs.total_coffee_beans = SUPPLIES_MAX
        gs.total_milk = SUPPLIES_MAX
        gs.total_sugar = SUPPLIES_MAX
        gs.total_ibalgin = SUPPLIES_MAX
        gs.total_bandages = SUPPLIES_MAX
        gs.total_pcr_test = SUPPLIES_MAX
        update_panel_contents()
        return True
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

def update_panel_contents():
    """
    Update each panel's progress_values and value_pairs from the current GameState.
    """
    for panel in panels:
        lines = getattr(panel, 'lines_config', None)
        if lines is not None:
            progress_values, value_pairs = get_panel_progress_and_values(lines)
            if hasattr(panel, 'content'):
                panel.content.progress_values = progress_values
                panel.content.value_pairs = value_pairs

def draw_supplies_panel(surface):
    global panels, resupply_button
    if not panels or len(panels) != len(panel_configs):
        panels = create_panels(surface)
    # Place resupply button 10px above the first IconButton
    if resupply_button is None:
        first_panel_y = int(surface.get_size()[1] * TOP_MARGIN)
        resupply_button = ResupplyButton(SUPPLIES_PANEL_X, first_panel_y - 10 - 30)  # 30 is button height
    update_panel_contents()
    rects = []
    resupply_button.draw(surface)
    for panel in panels:
        rects.append(panel.draw(surface))
    return rects
