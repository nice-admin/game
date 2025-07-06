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
        large_font = pygame.font.SysFont(None, 28)
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

# Example cell definitions
SECTION1 = [
    {"id": 0, "label": "Day", "icon": resource_path("data/graphics/top_panel/day.png")},
    {"id": 1, "label": "Air temp", "icon": resource_path("data/graphics/top_panel/temperature.png")},
    {"id": 2, "label": "Power\ndrain"},
    {"id": 3, "label": "Breaker\nlimit"},
    {"id": 4, "label": "Employees"},
    {"id": 5, "label": "Happiness"},
    {"id": 6, "label": "Money"},
    {"id": 7, "label": "Monthly\nexpenses"},
    {"id": 8, "label": "Office\nquality"},
]

SECTION2 = [
    {"id": 0, "label": "Day"},
    {"id": 1, "label": "Air temp"},
    {"id": 2, "label": "Power\ndrain"},
    {"id": 3, "label": "Breaker\nlimit"},
    {"id": 4, "label": "Employees"},
    {"id": 5, "label": "Happiness"},
    {"id": 6, "label": "Money"},
    {"id": 7, "label": "Monthly\nexpenses"},
    {"id": 8, "label": "Office\nquality"},
]

def draw_top_panel(surface, num_cells=5, cell_color=None, cell_gap=4, cell_defs=None, widecell_defs=None, font=None, cell_progresses=None):
    """
    Draws a row of BasicCell instances followed by WideCell instances at the top of the screen, left-aligned.
    Each cell is separated by cell_gap pixels.
    Optionally, pass lists of cell definition dicts for each cell type.
    Optionally, pass a list of progress values (0.0-1.0) for each BasicCell via cell_progresses.
    """
    screen_width, screen_height = surface.get_width(), surface.get_height()
    cells = []
    x_offset = 0
    # Set all progress bars to 45%
    cell_progresses = [0.45 for _ in range(num_cells)]
    # Use section arrays for cell content
    if cell_defs is None:
        cell_defs = SECTION1
    if widecell_defs is None:
        widecell_defs = SECTION2
    # Draw BasicCells
    for i in range(num_cells):
        cell_def = cell_defs[i] if i < len(cell_defs) else {}
        progress = cell_progresses[i] if i < len(cell_progresses) else None
        cell = BasicCell(
            screen_width, screen_height,
            color=cell_color,
            icon_path=cell_def.get("icon"),
            label=cell_def.get("label"),
            key=cell_def.get("key"),
            font=font,
            progress=progress
        )
        cell.rect.x = x_offset
        cell.rect.y = 0
        cell.draw(surface)
        cells.append(cell)
        x_offset += cell.width + cell_gap
    # Draw WideCells
    for i in range(num_cells):
        cell_def = widecell_defs[i] if i < len(widecell_defs) else {}
        progress = cell_progresses[i] if i < len(cell_progresses) else None
        cell = WideCell(
            screen_width, screen_height,
            color=cell_color,
            icon_path=cell_def.get("icon"),
            label=cell_def.get("label"),
            key=cell_def.get("key"),
            font=font,
            progress=progress
        )
        cell.rect.x = x_offset
        cell.rect.y = 0
        cell.draw(surface)
        cells.append(cell)
        x_offset += cell.width + cell_gap
    return cells, cell_progresses


# Example usage (to be called from your main UI loop):
# cell = BasicCell(surface.get_width(), surface.get_height())
# cell.draw(surface)
