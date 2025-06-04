import pygame
from game_core.config import UI_BG1_COL, UI_BORDER1_COL, TEXT1_COL, resource_path
from game_core.game_state import GameState
from typing import Optional, Tuple

def get_cached_font(size: int):
    from game_core.config import get_font1
    return get_font1(size)

class SystemCell:
    cell_width = 160
    cell_height = 50
    def __init__(self, label: str = "Connected", font: Optional[pygame.font.Font] = None, text_color: Optional[Tuple[int, int, int]] = None, value_font_size: int = 25, label_text_size: int = 15, icon: Optional[pygame.Surface] = None, dynamic_label_func=None):
        self.font = font or get_cached_font(label_text_size)
        self.label_text_size = int(label_text_size)
        self.text_color = text_color if text_color is not None else TEXT1_COL
        self.custom_label = label
        self.icon = icon
        self.dynamic_label_func = dynamic_label_func
        self.dynamic_text_surface = None
        self.last_dynamic_text = None
        self.x = 0
        self.y = 0

    def _draw_icon(self):
        return 10  # Icon rendering is handled elsewhere

    def update_dynamic_text(self, base_font: pygame.font.Font):
        x_offset = self._draw_icon() + 50
        label = self.custom_label
        if self.dynamic_label_func:
            label = self.dynamic_label_func()
        if label != self.last_dynamic_text or self.dynamic_text_surface is None:
            label_font = get_cached_font(self.label_text_size)
            surf = pygame.Surface((self.cell_width, self.cell_height), pygame.SRCALPHA)
            surf.fill((0,0,0,0))
            text_surf = label_font.render(str(label), True, self.text_color)
            rect = text_surf.get_rect(midleft=(x_offset, self.cell_height//2))
            surf.blit(text_surf, rect)
            self.dynamic_text_surface = surf
            self.last_dynamic_text = label

    def blit_dynamic_text(self, target_surface: pygame.Surface, pos: Tuple[int, int], base_font: pygame.font.Font):
        self.update_dynamic_text(base_font)
        if self.dynamic_text_surface:
            target_surface.blit(self.dynamic_text_surface, pos)

def get_system_panel_cells(font=None):
    icon_files = [
        resource_path("data/graphics/internet.png"),
        resource_path("data/graphics/nas.png"),
        resource_path("data/graphics/wifi.png"),
        resource_path("data/graphics/storage.png"),
    ]
    system_labels = [
        "Connected", "Running",
        "WiFi OK", "15 / 25 TB"
    ]
    system_icons = [pygame.image.load(fname).convert_alpha() for fname in icon_files]
    def get_internet_label():
        gs = GameState()
        return "Online" if getattr(gs, 'is_internet_online', True) else "Offline"
    system_grid = [
        [
            SystemCell(label=None, font=font, icon=system_icons[0], dynamic_label_func=get_internet_label),
            SystemCell(label=system_labels[1], font=font, icon=system_icons[1])
        ],
        [
            SystemCell(label=system_labels[2], font=font, icon=system_icons[2]),
            SystemCell(label=system_labels[3], font=font, icon=system_icons[3])
        ]
    ]
    return system_grid

# --- System Panel Robust Logic (from resource_panel_system_old.py) ---
def update_icon_surfaces(is_internet_online, is_nas_online, font: Optional[pygame.font.Font] = None):
    """
    Tint and cache the icon surfaces for the current is_internet_online and is_nas_online state.
    This should be called only at game start and when either state changes.
    """
    icon_files = [
        resource_path("data/graphics/internet.png"),
        resource_path("data/graphics/nas.png"),
        resource_path("data/graphics/wifi.png"),
        resource_path("data/graphics/storage.png"),
    ]
    icon_size = 40
    if not hasattr(update_icon_surfaces, "_icon_cache"):
        update_icon_surfaces._icon_cache = [pygame.image.load(fname).convert_alpha() for fname in icon_files]
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
        if idx == 0:  # internet.png
            color = ONLINE if is_internet_online else OFFLINE
        elif idx == 1:  # nas.png
            color = ONLINE if is_nas_online else OFFLINE
        elif idx == 2:  # wifi.png
            color = ONLINE if is_internet_online else OFFLINE
        else:
            color = ONLINE
        icon_surfaces.append(tint_icon(icon, color))
    update_icon_surfaces._icon_surfaces = icon_surfaces
    update_icon_surfaces._icon_state = (is_internet_online, is_nas_online)

def get_system_panel_bg():
    # Calculate width and height based on cell size and grid
    cols = 2
    rows = 2
    width = SystemCell.cell_width * cols
    height = Header.header_height + SystemCell.cell_height * rows
    if not hasattr(get_system_panel_bg, "_bg_surface") or get_system_panel_bg._bg_surface.get_width() != width or get_system_panel_bg._bg_surface.get_height() != height:
        bg = pygame.Surface((width, height), pygame.SRCALPHA)
        bg.fill(UI_BG1_COL)  # Use UI_BG1_COL from config.py
        pygame.draw.rect(bg, (100, 100, 100), bg.get_rect(), 2)  # border
        get_system_panel_bg._bg_surface = bg
    return get_system_panel_bg._bg_surface

def get_system_panel_state():
    gs = GameState()
    return (
        gs.is_internet_online,
        getattr(gs, 'is_nas_online', True),
        # Add more state here if needed
    )

def bake_system_panel_surface(font, state):
    bg = get_system_panel_bg()
    panel_surface = bg.copy()
    header = Header(320, text="SYSTEM HEALTH", font=font)
    panel_surface.blit(header.get_surface(), (0, 0))
    header_height = header.header_height
    is_internet_online, is_nas_online = state
    update_icon_surfaces(is_internet_online, is_nas_online, font)
    icon_surfaces = update_icon_surfaces._icon_surfaces
    icon_size = 40
    system_grid = get_system_panel_cells(font)
    system_x = 0
    system_y = header_height
    for row_idx, row in enumerate(system_grid):
        for col_idx, cell in enumerate(row):
            icon_x = system_x + col_idx * cell.cell_width + 10
            icon_y = system_y + row_idx * cell.cell_height + (cell.cell_height - icon_size) // 2
            icon_idx = row_idx * 2 + col_idx
            cell_rect = pygame.Rect(system_x + col_idx * cell.cell_width, system_y + row_idx * cell.cell_height, cell.cell_width, cell.cell_height)
            pygame.draw.rect(panel_surface, UI_BORDER1_COL, cell_rect, 1)
            if icon_idx < len(icon_surfaces):
                panel_surface.blit(icon_surfaces[icon_idx], (icon_x, icon_y))
            cell.blit_dynamic_text(panel_surface, (system_x + col_idx * cell.cell_width, system_y + row_idx * cell.cell_height), font)
    return panel_surface

def draw_resource_panel_system(surface: pygame.Surface, font: Optional[pygame.font.Font] = None, x: int = 0, y: int = 0):
    font = font or get_cached_font(18)
    state = get_system_panel_state()
    cache = draw_resource_panel_system
    if (not hasattr(cache, "_last_state") or
        not hasattr(cache, "_last_surface") or
        cache._last_state != state):
        cache._last_surface = bake_system_panel_surface(font, state)
        cache._last_state = state
    surface.blit(cache._last_surface, (x, y))

class Header:
    header_height = 30
    def __init__(self, width: int, height: Optional[int] = None, text: str = "SYSTEM HEALTH", font: Optional[pygame.font.Font] = None, text_color: Optional[Tuple[int, int, int]] = None):
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
