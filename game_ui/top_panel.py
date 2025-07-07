import pygame
import pygame.freetype
import random
from game_core.config import UI_BG1_COL, resource_path, adjust_color, CURRENCY_SYMBOL, FONT1
from game_core.game_state import gs

ICON_PATH = resource_path("data/graphics/top_panel/day.png")

# Helper to resolve icon paths by filename
ICON_DIR = "data/graphics/top_panel/"
def get_icon_path(filename):
    return resource_path(ICON_DIR + filename)

DEFAULT_GREEN = (75, 230, 50)

# Track the maximum money ever reached
max_money_ever = [0]

def update_max_money(current):
    if current > max_money_ever[0]:
        max_money_ever[0] = current
    return max_money_ever[0]

DATA = [
    {
        "id": 0,
        "label": "Day",
        "icon": get_icon_path("day.png"),
        "value": lambda: gs.game_time_days,
    },
    {
        "id": 6,
        "label": "Money",
        "icon": get_icon_path("money.png"),
        "value": lambda: gs.total_money,
        "prefix": CURRENCY_SYMBOL,
        "has_bar": True,
        "bar_min": 0,
        "bar_max": lambda: update_max_money(gs.total_money),
        "progress": lambda: gs.total_money,
        "color": lambda: DEFAULT_GREEN,
    },
    {
        "id": 7,
        "label": "Monthly expenses",
        "icon": get_icon_path("expenses.png"),
        "value": lambda: gs.total_upkeep,
        "prefix": f"-{CURRENCY_SYMBOL}",
        "has_bar": True,
        "bar_min": 0,
        "bar_max": lambda: gs.total_money * 1.2 if gs.total_money > 0 else 1,
        "progress": lambda: min(gs.total_upkeep, gs.total_money * 1.2 if gs.total_money > 0 else 1),
        "color": lambda: interpolate_expenses_color(gs.total_upkeep, gs.total_money),
    },
    {
        "id": 4,
        "label": "Employees",
        "icon": get_icon_path("employees.png"),
        "value": lambda: gs.total_employees,
    },
    {
        "id": 5,
        "label": "Happiness",
        "icon": get_icon_path("happiness.png"),
        "value": 10,
    },
    {
        "id": 1,
        "label": "Air temp",
        "icon": get_icon_path("temperature.png"),
        "value": lambda: gs.temperature,
        "bar_min": 15,
        "bar_max": 32,
        "suffix": "°C",
        "decimals": 1,
        "has_bar": True,
        "color": lambda: interpolate_temp_color(getattr(gs, 'temperature', 23)),
    },
    {
        "id": 2,
        "label": "Power drain",
        "value": lambda: gs.total_power_drain / 1000,
        "icon": get_icon_path("power-drain.png"),
        "suffix": " KW",
        "decimals": 1,
        "bar_min": 0,
        "bar_max": lambda: gs.total_breaker_strength / 1000,
        "has_bar": True,
    },
    {
        "id": 3,
        "label": "Breaker limit",
        "value": lambda: int(gs.total_breaker_strength // 1000),
        "icon": get_icon_path("breaker-limit.png"),
        "suffix": " KW",
    },
    {
        "id": 8,
        "label": "Office quality",
        "icon": get_icon_path("office-quality.png"),
        "value": lambda: [
            "Hellhole",
            "Irritating",
            "Average",
            "Good",
            "Excellent",
            "Heavenly",
        ][int(gs.office_quality)] if 0 <= int(gs.office_quality) <= 5 else str(gs.office_quality),
        "color": lambda: [
            (255, 0, 0),
            (255, 100, 0),
            (255, 220, 0),
            (120, 200, 60),
            (100, 230, 0),
            (0, 255, 0),
        ][int(gs.office_quality)] if 0 <= int(gs.office_quality) <= 5 else (200, 220, 255),
        "has_bar": True,
        "bar_min": 0,
        "bar_max": 100,
        # Custom progress calculation based on breakpoints
        "progress": lambda: (
            [10, 25, 40, 55, 70, 100][int(gs.office_quality)] if 0 <= int(gs.office_quality) <= 5 else float(getattr(gs, 'office_quality', 0))
        ),
    },
]

def interpolate_temp_color(t):
    t = max(15, min(32, float(t or 23)))
    # Use bright blue, green, red
    blue = (0, 180, 255)
    green = DEFAULT_GREEN
    red = (255, 60, 60)
    if t <= 23:
        # Blue to green
        f = (t - 15) / 8
        r = int(blue[0] + (green[0] - blue[0]) * f)
        g = int(blue[1] + (green[1] - blue[1]) * f)
        b = int(blue[2] + (green[2] - blue[2]) * f)
        return (r, g, b)
    else:
        # Green to red
        f = (t - 23) / 12
        r = int(green[0] + (red[0] - green[0]) * f)
        g = int(green[1] + (red[1] - green[1]) * f)
        b = int(green[2] + (red[2] - green[2]) * f)
        return (r, g, b)

def interpolate_power_color(norm):
    # norm: 0.0 to 1.0 (progress bar fill percent)
    # Use bright green, yellow, and bright red for interpolation
    green = DEFAULT_GREEN
    yellow = (255, 220, 0)
    red = (255, 60, 60)
    if norm < 0.6:
        return green
    elif norm < 0.8:
        # Green to yellow
        f = (norm - 0.6) / 0.2
        r = int(green[0] + (yellow[0] - green[0]) * f)
        g = int(green[1] + (yellow[1] - green[1]) * f)
        b = int(green[2] + (yellow[2] - green[2]) * f)
        return (r, g, b)
    else:
        # Yellow to red
        f = (norm - 0.8) / 0.2
        f = max(0.0, min(1.0, f))
        r = int(yellow[0] + (red[0] - yellow[0]) * f)
        g = int(yellow[1] + (red[1] - yellow[1]) * f)
        b = int(yellow[2] + (red[2] - yellow[2]) * f)
        return (r, g, b)

def interpolate_expenses_color(upkeep, money):
    # Green if upkeep <= 0.65 money, yellow in the middle, red if upkeep >= money
    if money <= 0:
        return (255, 60, 60)  # Red if no money
    norm = upkeep / money
    norm = max(0.0, min(1.0, norm))
    green = (75, 230, 50)
    yellow = (255, 220, 0)
    red = (255, 60, 60)
    green_zone = 0.65
    if norm <= green_zone:
        # Green to yellow
        f = norm / green_zone
        r = int(green[0] + (yellow[0] - green[0]) * f)
        g = int(green[1] + (yellow[1] - green[1]) * f)
        b = int(green[2] + (yellow[2] - green[2]) * f)
        return (r, g, b)
    else:
        # Yellow to red
        f = (norm - green_zone) / (1 - green_zone)
        f = max(0.0, min(1.0, f))
        r = int(yellow[0] + (red[0] - yellow[0]) * f)
        g = int(yellow[1] + (red[1] - yellow[1]) * f)
        b = int(yellow[2] + (red[2] - yellow[2]) * f)
        return (r, g, b)

class BasicCell:
    CONTENT_TOP_MARGIN = 2  # px
    def __init__(self, screen_width, screen_height, color=None, icon_path=None, label=None, value=None, key=None, icon_size=None, font=None, progress=None, progress_min=0.0, progress_max=1.0, has_bar=False):
        self.width = int(screen_width * 0.0755)
        self.height = int(screen_height * 0.04)
        self.x = 0
        self.y = 0
        self.color = color if color is not None else UI_BG1_COL
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.icon = None
        # Icon size logic: larger if no bar
        self.icon_size = 32 if has_bar else 40
        self.label = label
        self.value = value  # New: value text to display below label
        self.key = key
        # Use FONT1 for all text, but retain the original font sizes
        self.font = pygame.font.Font(FONT1, 20)
        self.large_font = pygame.font.Font(FONT1, 16)
        # Value font: larger if no bar
        self.value_font = pygame.font.Font(FONT1, 18 if has_bar else 22)
        self.progress = progress  # Value between 0.0 and 1.0 or None
        self.progress_min = progress_min
        self.progress_max = progress_max
        self.has_bar = has_bar
        # Always use the default icon unless overridden
        icon_path = icon_path if icon_path is not None else ICON_PATH
        if icon_path:
            try:
                icon_img = pygame.image.load(icon_path)
                self.icon = pygame.transform.smoothscale(icon_img, (self.icon_size, self.icon_size))
            except Exception:
                self.icon = None
        # --- Caching ---
        self._static_surface = None  # Cache for static parts
        self._last_value = None      # Last rendered value
        self._value_surface = None   # Cached value surface
        self._last_progress = None   # Last rendered progress
        self._progress_surface = None
        self._office_quality_color = None
        self._render_static()
        self._render_value()  # Initial value render

    def _render_static(self):
        # Pre-render static parts: bg, icon, label
        self._static_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self._static_surface, self.color, (0, 0, self.width, self.height))
        icon_x = 5
        icon_y = 5 + self.CONTENT_TOP_MARGIN
        if self.icon:
            self._static_surface.blit(self.icon, (icon_x, icon_y))
        label_text = self.label if self.label is not None else ""
        label_col = adjust_color(self.color, white_factor=0.0, exposure=4)
        label_surface = self.large_font.render(label_text, True, label_col)
        label_x = icon_x + (self.icon_size if self.icon else 0) + 8
        label_y = icon_y + self.CONTENT_TOP_MARGIN
        self._static_surface.blit(label_surface, (label_x, label_y))
        self._label_x = label_x
        self._label_y = label_y
        self._label_height = label_surface.get_height()

    def _render_value(self):
        # Only re-render value if it changed (compare as string for robustness)
        display_value = self.value
        # Always convert to float if decimals is set and value is int
        decimals = None
        for cell_def in DATA:
            if cell_def.get('label') == self.label:
                decimals = cell_def.get('decimals', None)
                break
        if decimals is not None:
            try:
                display_value = float(display_value)
                display_value = f"{display_value:.{decimals}f}"
            except Exception:
                pass
        # Use prefix/suffix from data if present
        prefix = ''
        suffix = ''
        color = (200, 220, 255)
        for cell_def in DATA:
            if cell_def.get('label') == self.label:
                prefix = cell_def.get('prefix', '')
                suffix = cell_def.get('suffix', '')
                color_func = cell_def.get('color', None)
                if color_func is not None and callable(color_func):
                    color = color_func()
                break
        if prefix and display_value is not None:
            display_value = f"{prefix}{display_value}"
        if suffix and display_value is not None:
            display_value = f"{display_value}{suffix}"
        value_str = str(display_value) if display_value is not None else None
        last_value_str = str(self._last_value) if self._last_value is not None else None
        if value_str != last_value_str:
            if display_value is not None:
                self._value_surface = self.value_font.render(value_str, True, color)
            else:
                self._value_surface = None
            self._last_value = display_value

    def _render_progress(self):
        # Only re-render progress bar if it changed
        if self.progress != self._last_progress or self.progress_min != getattr(self, '_last_progress_min', None) or self.progress_max != getattr(self, '_last_progress_max', None):
            if self.progress is not None:
                bar_width = int(self.width * 0.95)
                bar_height = int(self.height * 0.15)
                bar_x = (self.width - bar_width) // 2
                bar_y = int(self.height * 0.95) - bar_height
                surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                pygame.draw.rect(surf, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height), border_radius=1)
                # Normalize progress to min/max
                norm = (self.progress - self.progress_min) / (self.progress_max - self.progress_min) if self.progress_max != self.progress_min else 0.0
                norm = max(0.0, min(1.0, norm))
                fill_width = int(bar_width * norm)
                # Use the same color function as the value text for Air temp, otherwise use DEFAULT_GREEN or override
                fill_color = DEFAULT_GREEN
                if self.label == "Air temp":
                    fill_color = interpolate_temp_color(self.value)
                elif self.label == "Power drain":
                    fill_color = interpolate_power_color(norm)
                else:
                    # Check for color override in DATA
                    for cell_def in DATA:
                        if cell_def.get('label') == self.label:
                            color_func = cell_def.get('color', None)
                            if color_func is not None and callable(color_func):
                                fill_color = color_func()
                            break
                if fill_width > 0:
                    pygame.draw.rect(surf, fill_color, (bar_x, bar_y, fill_width, bar_height), border_radius=2)
                self._progress_surface = surf
            else:
                self._progress_surface = None
            self._last_progress = self.progress
            self._last_progress_min = self.progress_min
            self._last_progress_max = self.progress_max

    def update(self, value=None, progress=None, progress_min=None, progress_max=None, has_bar=None):
        # Call this to update value/progress and re-render only if changed
        if value is not None:
            self.value = value
        if progress is not None:
            self.progress = progress
        if progress_min is not None:
            self.progress_min = progress_min
        if progress_max is not None:
            self.progress_max = progress_max
        if has_bar is not None and has_bar != self.has_bar:
            # If has_bar changes, update icon and value font sizes
            self.has_bar = has_bar
            self.icon_size = 35 if has_bar else 45
            self.value_font = pygame.font.Font(FONT1, 22 if has_bar else 26)
            # Re-load icon at new size
            if self.icon is not None:
                try:
                    icon_img = pygame.image.load(self.icon_path)
                    self.icon = pygame.transform.smoothscale(icon_img, (self.icon_size, self.icon_size))
                except Exception:
                    self.icon = None
            self._render_static()
        self._render_value()
        self._render_progress()

    def draw(self, surface):
        # Draw static parts
        surface.blit(self._static_surface, (self.rect.x, self.rect.y))
        # Draw value text below label, if present
        if self._value_surface is not None:
            value_x = self.rect.x + self._label_x
            value_y = self.rect.y + self._label_y + self._label_height
            surface.blit(self._value_surface, (value_x, value_y))
        # Draw progress bar if defined and allowed
        if self.has_bar and self.progress is not None and self._progress_surface is not None:
            surface.blit(self._progress_surface, (self.rect.x, self.rect.y))


class TopPanel:
    def __init__(self, surface, num_cells=13, cell_color=None, cell_gap=4, cell_defs=None, widecell_defs=None, shortcell_defs=None, font=None, cell_progresses=None, num_shortcells=7):
        self.surface = surface
        self.num_cells = num_cells or 5
        self.cell_color = cell_color
        self.cell_gap = cell_gap or 4
        self.font = font
        self.num_shortcells = num_shortcells or 7
        self.screen_width, self.screen_height = surface.get_width(), surface.get_height()
        self.cell_progresses = cell_progresses or [0.45 for _ in range(self.num_cells)]
        self.cell_defs = cell_defs or DATA
        self.cells = []
        self._init_cells()

    def _init_cells(self):
        self.cells = []
        for i in range(self.num_cells):
            cell_def = self.cell_defs[i] if i < len(self.cell_defs) else {}
            value_func = cell_def.get("value")
            value = value_func() if callable(value_func) else value_func
            # Evaluate bar_min and bar_max if they are callables
            bar_min = cell_def.get("bar_min", 0.0)
            if callable(bar_min):
                bar_min = bar_min()
            bar_max = cell_def.get("bar_max", 1.0)
            if callable(bar_max):
                bar_max = bar_max()
            has_bar = cell_def.get("has_bar", False)
            # Use explicit progress if present, else fallback
            progress_func = cell_def.get("progress", None)
            if progress_func is not None:
                progress = progress_func() if callable(progress_func) else progress_func
            else:
                progress = value if (cell_def.get("bar_min") is not None or cell_def.get("bar_max") is not None) and has_bar else (self.cell_progresses[i] if i < len(self.cell_progresses) and has_bar else None)
            cell = BasicCell(
                self.screen_width, self.screen_height,
                color=self.cell_color,
                icon_path=cell_def.get("icon"),
                label=cell_def.get("label"),
                value=value,
                key=cell_def.get("key"),
                font=self.font,
                progress=progress,
                progress_min=bar_min,
                progress_max=bar_max,
                has_bar=has_bar
            )
            cell.rect.x = i * (cell.width + self.cell_gap)
            cell.rect.y = 0
            self.cells.append(cell)

    def update(self):
        # Call this every frame to update only dynamic elements
        for i, cell in enumerate(self.cells):
            cell_def = self.cell_defs[i] if i < len(self.cell_defs) else {}
            value_func = cell_def.get("value")
            value = value_func() if callable(value_func) else value_func
            # Evaluate bar_min and bar_max if they are callables
            bar_min = cell_def.get("bar_min", cell.progress_min)
            if callable(bar_min):
                bar_min = bar_min()
            bar_max = cell_def.get("bar_max", cell.progress_max)
            if callable(bar_max):
                bar_max = bar_max()
            has_bar = cell_def.get("has_bar", False)
            # Use explicit progress if present, else fallback
            progress_func = cell_def.get("progress", None)
            if progress_func is not None:
                progress = progress_func() if callable(progress_func) else progress_func
            else:
                progress = value if (cell_def.get("bar_min") is not None or cell_def.get("bar_max") is not None) and has_bar else (self.cell_progresses[i] if i < len(self.cell_progresses) and has_bar else None)
            cell.update(value=value, progress=progress, progress_min=bar_min, progress_max=bar_max, has_bar=has_bar)

    def draw(self, target_surface=None):
        if target_surface is None:
            target_surface = self.surface
        # Draw a big adjusted color rectangle as the background for the entire top panel
        bg_height = int(self.screen_height * 0.043)
        bg_col = adjust_color(UI_BG1_COL, white_factor=0.0, exposure=1.4)
        pygame.draw.rect(target_surface, bg_col, (0, 0, self.screen_width, bg_height))
        for cell in self.cells:
            cell.draw(target_surface)

