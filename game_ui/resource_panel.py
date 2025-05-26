import pygame
from game_core.game_settings import *
from game_core.game_state import get_totals_dict
from game_core.game_settings import get_font1

# --- UI Resource Panel Cells and Header ---
class BasicCell:
    def __init__(self, cell_width=100, cell_height=60, label="", font=None, value_font_size=23, label_text_size=17):
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.label = label
        self.font = font or get_font1(label_text_size)
        self.value_font_size = int(value_font_size)  # always in pixels, default 25
        self.label_text_size = int(label_text_size)
        self.surface = self._create_surface()  # static bg, border, label
        self.value_surface = None  # dynamic value layer
        self.last_value = None

    def _create_surface(self):
        surface = pygame.Surface((self.cell_width, self.cell_height), pygame.SRCALPHA)
        surface.fill(UI_BG1_COL)
        pygame.draw.rect(surface, UI_BORDER1_COL, surface.get_rect(), 1)
        # Draw label if present
        label_font = get_font1(self.label_text_size)
        if self.label:
            text_width, text_height = label_font.size(str(self.label))
            x = (self.cell_width - text_width) // 2
            y = self.cell_height - text_height - 7
            surf = label_font.render(str(self.label), True, TEXT1_COL)
            surface.blit(surf, (x, y))
        return surface

    def get_surface(self):
        return self.surface

    def get_label_pos(self, font):
        text_width, text_height = font.size(str(self.label))
        x = (self.cell_width - text_width) // 2
        y = self.cell_height - text_height - 10
        return x, y

    def get_value_font(self, base_font):
        return get_font1(self.value_font_size)

    def get_value_pos(self, font, value_str="0"):
        text_width, _ = font.size(str(value_str))
        x = (self.cell_width - text_width) // 2
        y = 13
        return x, y

    def draw_value(self, value, base_font, color=(255,255,255)):
        """
        Draws/updates the value surface only if the value has changed.
        """
        if value == self.last_value and self.value_surface is not None:
            return  # No need to redraw
        self.last_value = value
        value_str = str(value)
        font = self.get_value_font(base_font)
        x, y = self.get_value_pos(font, value_str)
        # Clear previous value surface
        self.value_surface = pygame.Surface((self.cell_width, self.cell_height), pygame.SRCALPHA)
        value_surf = font.render(value_str, True, color)
        self.value_surface.blit(value_surf, (x, y))

    def blit_to(self, target_surface, pos):
        target_surface.blit(self.surface, pos)
        if self.value_surface:
            target_surface.blit(self.value_surface, pos)

class GeneralCell(BasicCell):
    def __init__(self, cell_width=190, label=None, font=None, text_color=None, value_font_size=25, label_text_size=15):
        super().__init__(cell_width, label=label, font=font, value_font_size=value_font_size, label_text_size=label_text_size)
        self.text_color = text_color if text_color is not None else TEXT1_COL

    def _draw_text(self):
        pass  # No-op to prevent double label rendering

class ProblemCell(GeneralCell):
    def __init__(self, cell_width=120, label=None, font=None, text_color=None):
        super().__init__(cell_width, label=label, font=font, text_color=text_color if text_color is not None else TEXT1_COL)

class SystemCell(GeneralCell):
    def __init__(self, cell_width=160, label="Connected", font=None, text_color=None, value_font_size=25, label_text_size=15, icon=None):
        # Use default text color (TEXT1_COL) for label text
        super().__init__(cell_width, label=None, font=font, text_color=text_color if text_color is not None else TEXT1_COL, value_font_size=value_font_size, label_text_size=label_text_size)
        self.custom_label = label
        self.icon = icon  # icon should be a pygame.Surface or None
        self._draw_text()

    def _draw_icon(self):
        x_offset = 10
        if self.icon:
            # Resize icon to 40x40px
            icon_surf = pygame.transform.smoothscale(self.icon, (40, 40))
            # Tint icon to bright green, preserving alpha
            arr = pygame.surfarray.pixels3d(icon_surf)
            arr[:, :, 0] = 0   # R
            arr[:, :, 1] = 255 # G
            arr[:, :, 2] = 80  # B
            del arr  # unlock the surface
            # Alpha is preserved
            icon_rect = icon_surf.get_rect()
            icon_rect.left = x_offset
            icon_rect.centery = self.cell_height // 2
            self.surface.blit(icon_surf, icon_rect)
            x_offset += icon_rect.width + 6  # 6px gap after icon
        return x_offset

    def _draw_text(self):
        x_offset = self._draw_icon()
        x_offset += 4  # Add 4px offset to the right for the text
        if self.custom_label:
            label_font = get_font1(self.label_text_size)
            surf = label_font.render(str(self.custom_label), True, self.text_color)
            rect = surf.get_rect(midleft=(x_offset, self.cell_height//2))
            self.surface.blit(surf, rect)

class Header:
    header_height = 30
    def __init__(self, width, height=None, text="hello", font=None, text_color=None):
        self.width = width
        self.height = height if height is not None else self.header_height
        self.text = text
        self.font = font or pygame.font.SysFont(None, 24)
        self.text_color = text_color if text_color is not None else TEXT1_COL
        self.surface = self._create_surface()

    def _create_surface(self):
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        surface.fill(UI_BG1_COL)
        pygame.draw.rect(surface, UI_BORDER1_COL, surface.get_rect(), 2)
        text_surf = self.font.render(self.text, True, self.text_color)
        # Offset header text by 2px down
        text_rect = text_surf.get_rect(center=(self.width//2, self.height//2 + 2))
        surface.blit(text_surf, text_rect)
        return surface

    def get_surface(self):
        return self.surface

# --- Panel Baking and Drawing ---
def make_cell_grid(cell_width, cell_height, row_spacing=0, col_spacing=0, cell_extra_spacing=10):
    """
    Creates a 2D list (2 rows x 9 columns) of BasicCell objects.
    """
    return [[BasicCell(cell_width, cell_height) for _ in range(9)] for _ in range(2)], row_spacing, col_spacing, cell_extra_spacing

def bake_panel_design(cell_width=64, cell_height=64, row_spacing=0, col_spacing=0, cell_extra_spacing=10, font=None):
    """
    Creates and returns the static resource panel surface. Call this ONCE and reuse the returned surface.
    The Employees cell will be labeled 'Employees:' and the value will be drawn dynamically.
    Uses FONT1 as the default font if none is provided.
    """
    font = font or get_font1(18)
    gap = 10
    general_labels = ["Money", "Power Drain", "Breaker Strength", "Employees"] + ["" for _ in range(6)]
    general_grid = [[GeneralCell(label=general_labels[row*5+col], font=font) for col in range(5)] for row in range(2)]
    problems_labels = ["Risk Factor", "Problems", "", ""]
    problems_grid = [[ProblemCell(label=problems_labels[row*2+col], font=font) for col in range(2)] for row in range(2)]
    icon_files = ["internet.png", "nas.png", "wifi.png", "storage.png"]
    system_labels = ["Connected", "Running", "Connected", "15 / 25 TB"]
    system_icons = [pygame.image.load(f"data/graphics/{fname}").convert_alpha() for fname in icon_files]
    system_grid = [[SystemCell(label=system_labels[row*2+col], font=font, icon=system_icons[row*2+col]) for col in range(2)] for row in range(2)]
    general_width = 5 * GeneralCell().cell_width
    problems_width = 2 * ProblemCell().cell_width
    system_width = 2 * SystemCell().cell_width
    total_width = general_width + gap + problems_width + gap + system_width
    total_height = 2 * GeneralCell().cell_height + Header.header_height
    panel_surface = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
    start_x = 0
    start_y = Header.header_height
    def draw_grid(grid, start_x, start_y, cell_cls):
        for row_idx, row in enumerate(grid):
            for col_idx, cell in enumerate(row):
                x = start_x + col_idx * (cell_cls().cell_width)
                y = start_y + row_idx * (cell_cls().cell_height)
                panel_surface.blit(cell.surface, (x, y))
    # Draw headers and all grids
    for header_text, width, x, grid, cell_cls in [
        ("GENERAL INFORMATION", general_width, start_x, general_grid, GeneralCell),
        ("WARNING PANEL", problems_width, start_x + general_width + gap, problems_grid, ProblemCell),
        ("SYSTEM HEALTH", system_width, start_x + general_width + gap + problems_width + gap, system_grid, SystemCell)
    ]:
        header = Header(width, text=header_text, font=font)
        panel_surface.blit(header.get_surface(), (x, 0))
        draw_grid(grid, x, start_y, cell_cls)
    problems_x = start_x + general_width + gap
    cell_map = [
        ('employees', general_grid[0][3], start_x + 3 * GeneralCell().cell_width, start_y),
        ('money', general_grid[0][0], start_x, start_y),
        ('power drain', general_grid[0][1], start_x + 1 * GeneralCell().cell_width, start_y),
        ('breaker strength', general_grid[0][2], start_x + 2 * GeneralCell().cell_width, start_y),
        ('risk factor', problems_grid[0][0], problems_x, start_y),
        ('problems', problems_grid[0][1], problems_x + 1 * ProblemCell().cell_width, start_y),
    ]
    cell_refs = {key: (x, y, cell) for key, cell, x, y in cell_map}
    return panel_surface, cell_refs


def draw_cell_value(cell, value, surface, font, surf_x, surf_y, color=(255,255,255)):
    """
    Draws a value centered in the given cell on the surface, using the cell's font logic and centering.
    """
    value_str = str(value)
    value_font = cell.get_value_font(font)
    value_x, value_y = cell.get_value_pos(value_font, value_str)
    value_pos = (surf_x + value_x, surf_y + value_y)
    value_surf = value_font.render(value_str, True, color)
    surface.blit(value_surf, value_pos)

def draw_resource_panel(surface, baked_panel_surface_and_cells, font=None):
    """
    Blits the pre-baked static resource panel to the main surface (centered horizontally),
    and overlays the current values in the dynamic cells (e.g. Employees, Money).
    Only the value layer is updated when the value changes.
    """
    font = font or get_font1(18)
    baked_panel_surface, cell_references = baked_panel_surface_and_cells
    total_width = baked_panel_surface.get_width()
    surf_x = (surface.get_width() - total_width) // 2
    surf_y = 0  # or wherever you want it
    surface.blit(baked_panel_surface, (surf_x, surf_y))
    totals = get_totals_dict()
    # Map cell keys to totals keys
    key_map = {
        'employees': 'total_employees',
        'money': 'total_money',
        'power drain': 'total_power_drain',
        'breaker strength': 'total_breaker_strength',
        'risk factor': 'total_risky_entities',
        'problems': 'total_broken_entities',
    }
    for key, (cell_x, cell_y, cell) in cell_references.items():
        value = totals.get(key_map.get(key, ''), 0)
        cell.draw_value(value, font)
        cell.blit_to(surface, (surf_x + cell_x, surf_y + cell_y))


