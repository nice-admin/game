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

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        icon_x = self.rect.x + 5
        icon_y = self.rect.y + 5
        if self.icon:
            surface.blit(self.icon, (icon_x, icon_y))
        # Draw label next to the icon, white and larger, aligned with icon Y
        label_text = self.label if self.label is not None else ""
        large_font = pygame.font.SysFont(None, 25)
        label_surface = large_font.render(label_text, True, (255, 255, 255))
        label_x = icon_x + (self.icon_size if self.icon else 0) + 8
        label_y = icon_y  # Align label Y with icon Y
        surface.blit(label_surface, (label_x, label_y))
        # Draw value text below label, if present
        if self.value is not None:
            value_font = pygame.font.SysFont(None, 20)
            value_surface = value_font.render(str(self.value), True, (200, 220, 255))
            value_x = label_x
            value_y = label_y + label_surface.get_height() + 2
            surface.blit(value_surface, (value_x, value_y))
        # Draw progress bar if defined
        if self.progress is not None:
            bar_width = int(self.width * 0.9)
            bar_height = int(self.height * 0.1)
            bar_x = self.rect.x + (self.width - bar_width) // 2
            bar_y = self.rect.y + int(self.height * 0.95) - bar_height
            # Draw background
            pygame.draw.rect(surface, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height), border_radius=3)
            # Draw progress
            fill_width = int(bar_width * max(0.0, min(1.0, self.progress)))
            if fill_width > 0:
                pygame.draw.rect(surface, (120, 200, 80), (bar_x, bar_y, fill_width, bar_height), border_radius=3)


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

    def draw(self, target_surface=None):
        if target_surface is None:
            target_surface = self.surface
        x_offset = 0
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
            cell.rect.x = x_offset
            cell.rect.y = 0
            cell.draw(target_surface)
            self.cells.append(cell)
            x_offset += cell.width + self.cell_gap

