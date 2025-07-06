import pygame
import pygame.freetype
import random
from game_core.config import UI_BG1_COL, resource_path

ICON_PATH = resource_path("data/graphics/top_panel/day.png")

class BasicCell:
    """
    A simple rectangular cell drawn at the top left of the screen.
    The cell is 3% of the screen width and 2% of the screen height.
    Optionally displays an icon and a label in the top left corner.
    """
    def __init__(self, screen_width, screen_height, color=None, icon_path=None, label=None, key=None, icon_size=None, font=None, progress=None):
        self.width = int(screen_width * 0.06)
        self.height = int(screen_height * 0.04)
        self.x = 0
        self.y = 0
        self.color = color if color is not None else UI_BG1_COL
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.icon = None
        self.icon_size = 35
        self.label = label
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

class WideCell(BasicCell):
    """
    A larger cell, 8% of the screen width, other properties derived from BasicCell.
    """
    def __init__(self, screen_width, screen_height, color=None, icon_path=None, label=None, key=None, icon_size=None, font=None, progress=None):
        super().__init__(screen_width, screen_height, color, icon_path, label, key, icon_size, font, progress)
        self.width = int(screen_width * 0.08)
        self.rect.width = self.width

class ShortCell(BasicCell):
    """
    A smaller cell, 4% of the screen width, other properties derived from BasicCell.
    """
    def __init__(self, screen_width, screen_height, color=None, icon_path=None, label=None, key=None, icon_size=None, font=None, progress=None):
        super().__init__(screen_width, screen_height, color, icon_path, label, key, icon_size, font, progress)
        self.width = int(screen_width * 0.04)
        self.rect.width = self.width

SECTION1 = [
    {"id": 0, "label": "Day", "icon": resource_path("data/graphics/top_panel/day.png")},
    {"id": 1, "label": "Air temp", "icon": resource_path("data/graphics/top_panel/temperature.png")},
    {"id": 2, "label": "Power drain"},
    {"id": 3, "label": "Breaker limit"},
    {"id": 4, "label": "Employees"},
    {"id": 5, "label": "Happiness"},
    {"id": 6, "label": "Money"},
    {"id": 7, "label": "Monthly expenses"},
    {"id": 8, "label": "Office quality"},
]

SECTION2 = [
    {"id": 0, "label": "Day"},
    {"id": 1, "label": "Air temp"},
    {"id": 2, "label": "Power drain"},
    {"id": 3, "label": "Breaker limit"},
    {"id": 4, "label": "Employees"},
    {"id": 5, "label": "Happiness"},
    {"id": 6, "label": "Money"},
    {"id": 7, "label": "Monthly expenses"},
    {"id": 8, "label": "Office quality"},
]

class TopPanel:
    """
    Efficient top panel UI: bakes static elements, only redraws dynamic ones (progress bars).
    Usage:
        panel = TopPanel(surface, ...)
        panel.bake_static()
        panel.draw(surface)  # draws static + dynamic
        panel.update_progress(cell_idx, new_value)  # only redraws changed bar
    """
    def __init__(self, surface, num_cells=5, cell_color=None, cell_gap=4, cell_defs=None, widecell_defs=None, shortcell_defs=None, font=None, cell_progresses=None, num_shortcells=7):
        self.surface = surface
        self.num_cells = num_cells or 5
        self.cell_color = cell_color
        self.cell_gap = cell_gap or 4
        self.font = font
        self.num_shortcells = num_shortcells or 7
        self.screen_width, self.screen_height = surface.get_width(), surface.get_height()
        self.cell_progresses = cell_progresses or [0.45 for _ in range(self.num_cells)]
        self.cell_defs = cell_defs or SECTION1
        self.widecell_defs = widecell_defs or SECTION2
        self.shortcell_defs = shortcell_defs or [{} for _ in range(self.num_shortcells)]
        self.cells = []
        self.static_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self._baked = False

    def bake_static(self):
        """Draw all static UI (background, icons, labels) to static_surface."""
        self.static_surface.fill((0,0,0,0))  # transparent
        x_offset = 0
        self.cells = []
        # BasicCells
        for i in range(self.num_cells):
            cell_def = self.cell_defs[i] if i < len(self.cell_defs) else {}
            cell = BasicCell(
                self.screen_width, self.screen_height,
                color=self.cell_color,
                icon_path=cell_def.get("icon"),
                label=cell_def.get("label"),
                key=cell_def.get("key"),
                font=self.font,
                progress=None  # don't draw progress bar here
            )
            cell.rect.x = x_offset
            cell.rect.y = 0
            cell.draw(self.static_surface)
            self.cells.append(cell)
            x_offset += cell.width + self.cell_gap
        # WideCells
        for i in range(self.num_cells):
            cell_def = self.widecell_defs[i] if i < len(self.widecell_defs) else {}
            cell = WideCell(
                self.screen_width, self.screen_height,
                color=self.cell_color,
                icon_path=cell_def.get("icon"),
                label=cell_def.get("label"),
                key=cell_def.get("key"),
                font=self.font,
                progress=None
            )
            cell.rect.x = x_offset
            cell.rect.y = 0
            cell.draw(self.static_surface)
            self.cells.append(cell)
            x_offset += cell.width + self.cell_gap
        # ShortCells
        for i in range(self.num_shortcells):
            cell_def = self.shortcell_defs[i] if i < len(self.shortcell_defs) else {}
            cell = ShortCell(
                self.screen_width, self.screen_height,
                color=self.cell_color,
                icon_path=cell_def.get("icon"),
                label=cell_def.get("label"),
                key=cell_def.get("key"),
                font=self.font,
                progress=None
            )
            cell.rect.x = x_offset
            cell.rect.y = 0
            cell.draw(self.static_surface)
            self.cells.append(cell)
            x_offset += cell.width + self.cell_gap
        self._baked = True

    def draw(self, target_surface=None):
        """Blit static UI, then draw all progress bars (dynamic) on top."""
        if not self._baked:
            self.bake_static()
        if target_surface is None:
            target_surface = self.surface
        target_surface.blit(self.static_surface, (0,0))
        # Draw progress bars only (dynamic)
        for idx, cell in enumerate(self.cells):
            progress = self.cell_progresses[idx] if idx < len(self.cell_progresses) else None
            if progress is not None:
                self._draw_progress_bar(target_surface, cell, progress)

    def _draw_progress_bar(self, surface, cell, progress):
        # Copied from BasicCell.draw, but only draws the progress bar
        bar_width = int(cell.width * 0.9)
        bar_height = int(cell.height * 0.1)
        bar_x = cell.rect.x + (cell.width - bar_width) // 2
        bar_y = cell.rect.y + int(cell.height * 0.95) - bar_height
        pygame.draw.rect(surface, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height), border_radius=3)
        fill_width = int(bar_width * max(0.0, min(1.0, progress)))
        if fill_width > 0:
            pygame.draw.rect(surface, (120, 200, 80), (bar_x, bar_y, fill_width, bar_height), border_radius=3)

    def update_progress(self, idx, new_value, target_surface=None):
        """Update a single progress bar and redraw only its region."""
        if idx < 0 or idx >= len(self.cells):
            return
        self.cell_progresses[idx] = new_value
        cell = self.cells[idx]
        if target_surface is None:
            target_surface = self.surface
        # Redraw just the progress bar region
        self._draw_progress_bar(target_surface, cell, new_value)
        pygame.display.update(cell.rect)

