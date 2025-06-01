import pygame
from game_core.config import *
from game_core.game_state import GameState
from game_core.config import get_font1
from typing import Optional, Tuple, Dict, Any
import colorsys

_font_cache: Dict[int, pygame.font.Font] = {}
def get_cached_font(size: int) -> pygame.font.Font:
    if size not in _font_cache:
        _font_cache[size] = get_font1(size)
    return _font_cache[size]

# --- Resource Panel Cell Definitions ---
RESOURCE_PANEL_CELLS = {
    # General cells (row, col): properties
    (0, 0): {
        "key": "day",
        "label": "Day",
        "icon": "data/graphics/resource_panel/day.png",
        "value_getter": lambda gs: int(gs.game_time_days),
        "format": lambda v, gs: str(v),
    },
    (0, 3): {
        "key": "temperature",
        "label": "Temperature",
        "icon": "data/graphics/resource_panel/temperature.png",
        "value_getter": lambda gs: int(gs.temperature),
        "format": lambda v, gs: f"{v} °C",
    },
    (1, 4): {
        "key": "power_drain",
        "label": "Power\ndrain",
        "icon": "data/graphics/resource_panel/power.png",
        "value_getter": lambda gs: gs.total_power_drain*0.001,
        "format": lambda v, gs: f"{v:.1f} KW",
        "color": lambda v, gs: (
            (255,255,255) if v == 0 else
            (255,0,0) if gs.total_breaker_strength <= 0 else
            tuple(int(x*255) for x in colorsys.hsv_to_rgb((120-120*min(max(1-(gs.total_breaker_strength-v)/15,0),1))/360,1,1))
        ),
        "extra_key": lambda gs: gs.total_breaker_strength,
    },
    (0, 4): {
        "key": "breaker_strength",
        "label": "Breaker\nlimit",
        "icon": "data/graphics/resource_panel/breakers.png",
        "value_getter": lambda gs: gs.total_breaker_strength*0.001,
        "format": lambda v, gs: f"{int(v)} KW",
    },
    (0, 1): {
        "key": "employees",
        "label": "Employees",
        "icon": "data/graphics/resource_panel/employees.png",
        "value_getter": lambda gs: gs.total_employees,
        "format": lambda v, gs: str(v),
    },
    (0, 2): {
        "key": "employees",
        "label": "Happiness",
        "icon": "data/graphics/resource_panel/happiness.png",
        "value_getter": lambda gs: gs.total_employees,
        "format": lambda v, gs: str(v),
    },
    (1, 0): {
        "key": "money",
        "label": "Money",
        "icon": "data/graphics/resource_panel/money.png",
        "value_getter": lambda gs: gs.total_money,
        "format": lambda v, gs: f"${v}",
    },
    (1, 1): {
        "key": "expenses",
        "label": "Monthly\nexpenses",
        "icon": "data/graphics/resource_panel/expenses.png",
        "value_getter": lambda gs: gs.total_upkeep,
        "format": lambda v, gs: f"-${v}",
    },
    # Add more as needed
}
PROBLEM_PANEL_CELLS = {
    (0, 0): {
        "key": "risk",
        "label": "Risk",
        "icon": "data/graphics/resource_panel/risk.png",
        "value_getter": lambda gs: gs.total_risky_entities,
        "format": lambda v, gs: str(v),
    },
    (0, 1): {
        "key": "problems",
        "label": "Problems",
        "icon": "data/graphics/resource_panel/problem.png",
        "value_getter": lambda gs: gs.total_broken_entities,
        "format": lambda v, gs: str(v),
    },
    # Add more as needed
}

class BasicCell:
    cell_width = 200
    cell_height = 50
    ICON_COLOR = adjust_color(BASE_COL, white_factor=0.5, exposure=1)
    def __init__(self, label: str = "", font: Optional[pygame.font.Font] = None, value_font_size: int = 23, label_text_size: int = 17, icon: Optional[pygame.Surface] = None):
        self.label = label or ""
        self.font = font or get_cached_font(label_text_size)
        self.value_font_size = int(value_font_size)
        self.label_text_size = int(label_text_size)
        self.icon = None
        if isinstance(icon, str):
            loaded_icon = pygame.image.load(icon).convert_alpha()
            loaded_icon = pygame.transform.smoothscale(loaded_icon, (36, 36))
            color = self.ICON_COLOR
            colored_icon = pygame.Surface(loaded_icon.get_size(), pygame.SRCALPHA)
            colored_icon.fill(color)  # Fill with color, alpha 0
            alpha = pygame.surfarray.pixels_alpha(loaded_icon)
            pygame.surfarray.pixels_alpha(colored_icon)[:, :] = alpha[:, :]
            self.icon = colored_icon
        self.surface = self._create_surface()
        self.value_surface = None
        self.last_value = None
        self.last_extra_key = None
        self.x = 0  # Set during panel baking
        self.y = 0

    def _create_surface(self) -> pygame.Surface:
        surface = pygame.Surface((self.cell_width, self.cell_height), pygame.SRCALPHA)
        surface.fill(UI_BG1_COL)
        pygame.draw.rect(surface, UI_BORDER1_COL, surface.get_rect(), 1)
        icon_offset = 0
        if self.icon is not None:
            icon_y = (self.cell_height - self.icon.get_height()) // 2
            surface.blit(self.icon, (6, icon_y))
            icon_offset = self.icon.get_width() + 12
        if self.label:
            label_font = get_cached_font(self.label_text_size)
            # Support multi-line labels
            lines = str(self.label).split("\n")
            total_height = sum([label_font.size(line)[1] for line in lines])
            y = (self.cell_height - total_height) // 2
            for line in lines:
                text_width, text_height = label_font.size(line)
                x = 0 + icon_offset
                surf = label_font.render(line, True, TEXT1_COL)
                surface.blit(surf, (x, y))
                y += text_height
        return surface

    def get_surface(self) -> pygame.Surface:
        return self.surface

    def get_label_pos(self, font: pygame.font.Font) -> Tuple[int, int]:
        # Left align, vertically centered
        text_width, text_height = font.size(str(self.label))
        x = 5
        y = (self.cell_height - text_height) // 2 + 2
        return x, y

    def get_value_font(self, base_font: pygame.font.Font) -> pygame.font.Font:
        return get_cached_font(self.value_font_size)

    def get_value_pos(self, font: pygame.font.Font, value_str: str = "0") -> Tuple[int, int]:
        # Right align, vertically centered
        text_width, text_height = font.size(str(value_str))
        x = self.cell_width - text_width - 10
        y = (self.cell_height - text_height) // 2 + 2
        return x, y

    def draw_value(self, value: Any, base_font: pygame.font.Font, color: Tuple[int, int, int] = (255,255,255), extra_key: Any = None):
        """
        Draws/updates the value surface only if the value or extra_key has changed.
        """
        if value == self.last_value and self.value_surface is not None and extra_key == self.last_extra_key:
            return  # No need to redraw
        self.last_value = value
        self.last_extra_key = extra_key
        value_str = str(value)
        font = self.get_value_font(base_font)
        x, y = self.get_value_pos(font, value_str)
        self.value_surface = pygame.Surface((self.cell_width, self.cell_height), pygame.SRCALPHA)
        value_surf = font.render(value_str, True, color)
        self.value_surface.blit(value_surf, (x, y))

    def blit_to(self, target_surface: pygame.Surface, pos: Tuple[int, int]):
        target_surface.blit(self.surface, pos)
        if self.value_surface:
            target_surface.blit(self.value_surface, pos)

class GeneralCell(BasicCell):
    cell_width = 220
    def __init__(self, label: Optional[str] = None, font: Optional[pygame.font.Font] = None, text_color: Optional[Tuple[int, int, int]] = None, value_font_size: int = 22, label_text_size: int = 16, icon: Optional[pygame.Surface] = None):
        super().__init__(label=label, font=font, value_font_size=value_font_size, label_text_size=label_text_size, icon=icon)
        self.text_color = text_color if text_color is not None else TEXT1_COL

    def _draw_text(self):
        pass  # No-op to prevent double label rendering

class ProblemCell(GeneralCell):
    cell_width = 160
    def __init__(self, label: Optional[str] = None, font: Optional[pygame.font.Font] = None, text_color: Optional[Tuple[int, int, int]] = None, icon: Optional[pygame.Surface] = None):
        super().__init__(label=label, font=font, text_color=text_color if text_color is not None else TEXT1_COL, icon=icon)

class Header:
    header_height = 30
    def __init__(self, width: int, height: Optional[int] = None, text: str = "hello", font: Optional[pygame.font.Font] = None, text_color: Optional[Tuple[int, int, int]] = None):
        self.width = width
        self.height = height if height is not None else self.header_height
        self.text = text
        self.font = font or pygame.font.SysFont(None, 24)
        self.text_color = text_color if text_color is not None else TEXT1_COL
        self.surface = self._create_surface()

    def _create_surface(self) -> pygame.Surface:
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        surface.fill(UI_BG1_COL)
        pygame.draw.rect(surface, UI_BORDER1_COL, surface.get_rect(), 2)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=(self.width//2, self.height//2 + 2))
        surface.blit(text_surf, text_rect)
        return surface

    def get_surface(self) -> pygame.Surface:
        return self.surface

_baked_panel = None

def bake_resource_panel(font: Optional[pygame.font.Font] = None) -> Dict[str, Any]:
    """
    Bake the static resource panel (cells, headers, icons) ONCE and return the structure.
    """
    font = font or get_cached_font(18)
    gap = 10
    # Build general grid from RESOURCE_PANEL_CELLS
    general_grid = [[None for _ in range(5)] for _ in range(2)]
    for (row, col), props in RESOURCE_PANEL_CELLS.items():
        general_grid[row][col] = GeneralCell(label=props["label"], font=font, icon=props.get("icon"))
    # Fill empty cells
    for row in range(2):
        for col in range(5):
            if general_grid[row][col] is None:
                general_grid[row][col] = GeneralCell(label="", font=font)
    # Build problems grid from PROBLEM_PANEL_CELLS
    problems_grid = [[None for _ in range(2)] for _ in range(2)]
    for (row, col), props in PROBLEM_PANEL_CELLS.items():
        problems_grid[row][col] = ProblemCell(label=props["label"], font=font, icon=props.get("icon"))
    for row in range(2):
        for col in range(2):
            if problems_grid[row][col] is None:
                problems_grid[row][col] = ProblemCell(label="", font=font)
    # --- SYSTEM PANEL: Restore to 2 rows x 2 columns ---
    # (System panel logic removed; now handled in resource_panel_systems.py)
    general_width = 5 * GeneralCell.cell_width
    problems_width = 2 * ProblemCell.cell_width
    # system_width = 2 * SystemCell.cell_width  # No longer needed here
    total_width = general_width + gap + problems_width  # Removed system panel width
    total_height = 2 * GeneralCell.cell_height + Header.header_height
    panel_surface = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
    start_x = 0
    start_y = Header.header_height
    def draw_grid(grid, start_x, start_y, cell_cls):
        for row_idx, row in enumerate(grid):
            for col_idx, cell in enumerate(row):
                x = start_x + col_idx * cell_cls.cell_width
                y = start_y + row_idx * cell_cls.cell_height
                cell.x = x
                cell.y = y
                panel_surface.blit(cell.surface, (x, y))
    for header_text, width, x, grid, cell_cls in [
        ("GENERAL INFORMATION", general_width, start_x, general_grid, GeneralCell),
        ("WARNING PANEL", problems_width, start_x + general_width + gap, problems_grid, ProblemCell)
        # System panel removed
    ]:
        header = Header(width, text=header_text, font=font)
        panel_surface.blit(header.get_surface(), (x, 0))
        draw_grid(grid, x, start_y, cell_cls)
    problems_x = start_x + general_width + gap
    return {
        'panel_surface': panel_surface,
        'general_grid': general_grid,
        'problems_grid': problems_grid,
        # 'system_grid': system_grid,  # Removed
        'start_x': start_x,
        'start_y': start_y,
        'surf_x': None,
        'surf_y': None,
        'total_width': total_width,
        'total_height': total_height,
    }

def get_baked_panel(font: Optional[pygame.font.Font] = None) -> Dict[str, Any]:
    global _baked_panel
    if _baked_panel is None:
        _baked_panel = bake_resource_panel(font)
    return _baked_panel

def draw_resource_panel_general(surface: pygame.Surface, font: Optional[pygame.font.Font] = None):
    """
    Draws the resource panel by blitting the baked static panel, then updating and blitting only the value overlays.
    """
    baked = get_baked_panel(font)
    panel_surface = baked['panel_surface'].copy()  # Copy so we can blit values on top
    surf_x = (surface.get_width() - baked['total_width']) // 2
    surf_y = 0
    baked['surf_x'] = surf_x
    baked['surf_y'] = surf_y
    gs = GameState()
    # Draw all general cells using RESOURCE_PANEL_CELLS definitions
    for (row, col), props in RESOURCE_PANEL_CELLS.items():
        cell = baked['general_grid'][row][col]
        value = props["value_getter"](gs) if "value_getter" in props else None
        value_str = props["format"](value, gs) if "format" in props else str(value)
        color = (props["color"](value, gs) if callable(props.get("color")) else props.get("color", (255,255,255))) if "color" in props else (255,255,255)
        extra_key = props["extra_key"](gs) if "extra_key" in props else None
        cell.draw_value(value_str, font or get_font1(18), color=color, extra_key=extra_key)
        cell.blit_to(panel_surface, (cell.x, cell.y))
    # Draw all problem cells using PROBLEM_PANEL_CELLS definitions
    for (row, col), props in PROBLEM_PANEL_CELLS.items():
        cell = baked['problems_grid'][row][col]
        value = props["value_getter"](gs) if "value_getter" in props else None
        value_str = props["format"](value, gs) if "format" in props else str(value)
        color = (props["color"](value, gs) if callable(props.get("color")) else props.get("color", (255,255,255))) if "color" in props else (255,255,255)
        extra_key = props["extra_key"](gs) if "extra_key" in props else None
        cell.draw_value(value_str, font or get_font1(18), color=color, extra_key=extra_key)
        cell.blit_to(panel_surface, (cell.x, cell.y))
    # System cells can be handled similarly if desired
    surface.blit(panel_surface, (surf_x, surf_y))


