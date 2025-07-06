import pygame
import pygame.freetype
import random
from game_core.config import UI_BG1_COL, resource_path
from game_core.game_state import gs

ICON_PATH = resource_path("data/graphics/top_panel/day.png")

class BasicCell:
    def __init__(self, screen_width, screen_height, color=None, icon_path=None, label=None, value=None, key=None, icon_size=None, font=None, progress=None):
        self.width = int(screen_width * 0.06)
        self.height = int(screen_height * 0.04)
        self.x = 0
        self.y = 0
        self.color = color if color is not None else UI_BG1_COL
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.icon = None
        self.icon_size = 35
        self.label = label
        self.value = value  # New: value text to display below label
        self.key = key
        self.font = font or pygame.font.SysFont(None, 20)
        self.progress = progress  # Value between 0.0 and 1.0 or None
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
        self._render_static()
        self._render_value()  # Initial value render

    def _render_static(self):
        # Pre-render static parts: bg, icon, label
        self._static_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self._static_surface, self.color, (0, 0, self.width, self.height))
        icon_x = 5
        icon_y = 5
        if self.icon:
            self._static_surface.blit(self.icon, (icon_x, icon_y))
        label_text = self.label if self.label is not None else ""
        large_font = pygame.font.SysFont(None, 25)
        label_surface = large_font.render(label_text, True, (255, 255, 255))
        label_x = icon_x + (self.icon_size if self.icon else 0) + 8
        label_y = icon_y
        self._static_surface.blit(label_surface, (label_x, label_y))
        self._label_x = label_x
        self._label_y = label_y
        self._label_height = label_surface.get_height()

    def _render_value(self):
        # Only re-render value if it changed (compare as string for robustness)
        value_str = str(self.value) if self.value is not None else None
        last_value_str = str(self._last_value) if self._last_value is not None else None
        if value_str != last_value_str:
            if self.value is not None:
                value_font = pygame.font.SysFont(None, 20)
                self._value_surface = value_font.render(value_str, True, (200, 220, 255))
            else:
                self._value_surface = None
            self._last_value = self.value

    def _render_progress(self):
        # Only re-render progress bar if it changed
        if self.progress != self._last_progress:
            if self.progress is not None:
                bar_width = int(self.width * 0.9)
                bar_height = int(self.height * 0.1)
                bar_x = (self.width - bar_width) // 2
                bar_y = int(self.height * 0.95) - bar_height
                surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                pygame.draw.rect(surf, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height), border_radius=3)
                fill_width = int(bar_width * max(0.0, min(1.0, self.progress)))
                if fill_width > 0:
                    pygame.draw.rect(surf, (120, 200, 80), (bar_x, bar_y, fill_width, bar_height), border_radius=3)
                self._progress_surface = surf
            else:
                self._progress_surface = None
            self._last_progress = self.progress

    def update(self, value=None, progress=None):
        # Call this to update value/progress and re-render only if changed
        if value is not None:
            self.value = value
        if progress is not None:
            self.progress = progress
        self._render_value()
        self._render_progress()

    def draw(self, surface):
        # Draw static parts
        surface.blit(self._static_surface, (self.rect.x, self.rect.y))
        # Draw value text below label, if present
        if self._value_surface is not None:
            value_x = self.rect.x + self._label_x
            value_y = self.rect.y + self._label_y + self._label_height + 2
            surface.blit(self._value_surface, (value_x, value_y))
        # Draw progress bar if defined
        if self.progress is not None and self._progress_surface is not None:
            surface.blit(self._progress_surface, (self.rect.x, self.rect.y))


SECTION1 = [
    {"id": 0, "label": "Day", "icon": resource_path("data/graphics/top_panel/day.png"), "value": lambda: gs.game_time_days},
    {"id": 1, "label": "Air temp", "icon": resource_path("data/graphics/top_panel/temperature.png"), "value": lambda: gs.temperature},
    {"id": 2, "label": "Power drain"},
    {"id": 3, "label": "Breaker limit"},
    {"id": 4, "label": "Employees"},
    {"id": 5, "label": "Happiness"},
    {"id": 6, "label": "Money"},
    {"id": 7, "label": "Monthly expenses"},
    {"id": 8, "label": "Office quality"},
]

class TopPanel:
    def __init__(self, surface, num_cells=16, cell_color=None, cell_gap=4, cell_defs=None, widecell_defs=None, shortcell_defs=None, font=None, cell_progresses=None, num_shortcells=7):
        self.surface = surface
        self.num_cells = num_cells or 5
        self.cell_color = cell_color
        self.cell_gap = cell_gap or 4
        self.font = font
        self.num_shortcells = num_shortcells or 7
        self.screen_width, self.screen_height = surface.get_width(), surface.get_height()
        self.cell_progresses = cell_progresses or [0.45 for _ in range(self.num_cells)]
        self.cell_defs = cell_defs or SECTION1
        self.cells = []
        self._init_cells()

    def _init_cells(self):
        self.cells = []
        for i in range(self.num_cells):
            cell_def = self.cell_defs[i] if i < len(self.cell_defs) else {}
            value_func = cell_def.get("value")
            value = value_func() if callable(value_func) else value_func
            cell = BasicCell(
                self.screen_width, self.screen_height,
                color=self.cell_color,
                icon_path=cell_def.get("icon"),
                label=cell_def.get("label"),
                value=value,
                key=cell_def.get("key"),
                font=self.font,
                progress=self.cell_progresses[i] if i < len(self.cell_progresses) else None
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
            progress = self.cell_progresses[i] if i < len(self.cell_progresses) else None
            cell.update(value=value, progress=progress)

    def draw(self, target_surface=None):
        if target_surface is None:
            target_surface = self.surface
        for cell in self.cells:
            cell.draw(target_surface)

