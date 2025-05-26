import pygame
from game_core.game_settings import *
from game_core.game_state import GameState
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
        # Always blit the baked cell first, then the value overlay
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
        super().__init__(cell_width, label=None, font=font, text_color=text_color if text_color is not None else TEXT1_COL, value_font_size=value_font_size, label_text_size=label_text_size)
        self.custom_label = label
        self.icon = icon  # icon should be a pygame.Surface or None
        self._draw_text()

    def _draw_icon(self):
        # Icon rendering is now handled by draw_icons; do nothing here
        return 10

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

# Store baked panel cells and headers globally
_baked_panel = None


def bake_resource_panel(font=None):
    """
    Bake the static resource panel (cells, headers, icons) ONCE and return the structure.
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
    return {
        'panel_surface': panel_surface,
        'cell_map': cell_map,
        'general_grid': general_grid,
        'problems_grid': problems_grid,
        'system_grid': system_grid,
        'start_x': start_x,
        'start_y': start_y,
        'surf_x': None,  # to be set at draw time
        'surf_y': None,
        'total_width': total_width,
        'total_height': total_height,
    }


def get_baked_panel(font=None):
    global _baked_panel
    if _baked_panel is None:
        _baked_panel = bake_resource_panel(font)
    return _baked_panel


def draw_resource_panel(surface, font=None):
    """
    Draws the resource panel by blitting the baked static panel, then updating and blitting only the value overlays.
    """
    from game_core.game_state import GameState
    baked = get_baked_panel(font)
    panel_surface = baked['panel_surface'].copy()  # Copy so we can blit values on top
    surf_x = (surface.get_width() - baked['total_width']) // 2
    surf_y = 0
    baked['surf_x'] = surf_x
    baked['surf_y'] = surf_y
    gs = GameState()
    for key, cell, cell_x, cell_y in baked['cell_map']:
        if key == 'employees':
            value = gs.total_employees
        elif key == 'money':
            value = gs.total_money
        elif key == 'power drain':
            value = gs.total_power_drain
        elif key == 'breaker strength':
            value = gs.total_breaker_strength
        elif key == 'risk factor':
            value = gs.total_risky_entities
        elif key == 'problems':
            value = gs.total_broken_entities
        else:
            value = 0
        cell.draw_value(value, font or get_font1(18))
        cell.blit_to(panel_surface, (cell_x, cell_y))
    surface.blit(panel_surface, (surf_x, surf_y))


def update_icon_surfaces(is_internet_online, font=None):
    """
    Tint and cache the icon surfaces for the current is_internet_online state.
    This should be called only at game start and when is_internet_online changes.
    """
    icon_files = ["internet.png", "nas.png", "wifi.png", "storage.png"]
    icon_size = 40
    if not hasattr(update_icon_surfaces, "_icon_cache"):
        update_icon_surfaces._icon_cache = [pygame.image.load(f"data/graphics/{fname}").convert_alpha() for fname in icon_files]
    system_icons = update_icon_surfaces._icon_cache
    def tint_icon(icon, color):
        icon = pygame.transform.smoothscale(icon, (icon_size, icon_size))
        tinted = icon.copy()
        arr = pygame.surfarray.pixels3d(tinted)
        arr[:, :, 0] = color[0]
        arr[:, :, 1] = color[1]
        arr[:, :, 2] = color[2]
        del arr
        return tinted
    ONLINE = (0, 255, 0)
    OFFLINE = (0, 0, 0)
    icon_surfaces = []
    for idx, icon in enumerate(system_icons):
        if idx in (0, 2):
            color = ONLINE if is_internet_online else OFFLINE
        else:
            color = ONLINE
        icon_surfaces.append(tint_icon(icon, color))
    update_icon_surfaces._icon_surfaces = icon_surfaces
    update_icon_surfaces._icon_state = is_internet_online


def draw_icons(surface, font=None):
    from game_core.game_state import GameState
    font = font or get_font1(18)
    gs = GameState()
    is_internet_online = gs.is_internet_online
    # Only update icon surfaces if state changed or never initialized
    if (not hasattr(update_icon_surfaces, "_icon_state") or
        update_icon_surfaces._icon_state != is_internet_online):
        update_icon_surfaces(is_internet_online, font)
    icon_surfaces = update_icon_surfaces._icon_surfaces
    # Get baked panel and system cell positions
    baked = get_baked_panel(font)
    system_grid = baked['system_grid']
    general_width = 5 * GeneralCell().cell_width
    problems_width = 2 * ProblemCell().cell_width
    gap = 10
    start_x = 0
    start_y = Header.header_height
    system_x = start_x + general_width + gap + problems_width + gap
    surf_x = baked['surf_x'] or 0
    surf_y = baked['surf_y'] or 0
    icon_size = 40
    # Cache icon positions for performance
    if not hasattr(draw_icons, '_icon_positions'):
        icon_positions = []
        icon_idx = 0
        for row_idx, row in enumerate(system_grid):
            for col_idx, cell in enumerate(row):
                x = surf_x + system_x + col_idx * SystemCell().cell_width + 10
                y = surf_y + start_y + row_idx * SystemCell().cell_height + (SystemCell().cell_height - icon_size) // 2
                icon_positions.append((x, y))
                icon_idx += 1
        draw_icons._icon_positions = icon_positions
    icon_positions = draw_icons._icon_positions
    for icon_idx, (x, y) in enumerate(icon_positions):
        surface.blit(icon_surfaces[icon_idx], (x, y))


