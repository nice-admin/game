import pygame
from game_core.config import UI_BG1_COL, UI_BORDER1_COL, TEXT1_COL
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
    icon_files = ["internet.png", "nas.png", "wifi.png", "storage.png"]
    system_labels = [
        "Connected", "Running",
        "WiFi OK", "15 / 25 TB"
    ]
    system_icons = [pygame.image.load(f"data/graphics/{fname}").convert_alpha() for fname in icon_files]
    def get_internet_label():
        gs = GameState()
        return "Connected" if getattr(gs, 'is_internet_online', True) else "Disconnected"
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

def update_icon_surfaces(is_internet_online, is_nas_online, font=None):
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
    return icon_surfaces

def draw_system_panel(surface, font, x, y, system_grid=None):
    if system_grid is None:
        system_grid = get_system_panel_cells(font)
    icon_size = 40
    for row_idx, row in enumerate(system_grid):
        for col_idx, cell in enumerate(row):
            icon_x = x + col_idx * cell.cell_width + 10
            icon_y = y + row_idx * cell.cell_height + (cell.cell_height - icon_size) // 2
            # Draw icon (should be tinted by update_icon_surfaces)
            if hasattr(update_icon_surfaces, '_icon_surfaces'):
                icon_surf = update_icon_surfaces._icon_surfaces[row_idx*2+col_idx]
                surface.blit(icon_surf, (icon_x, icon_y))
            # Draw dynamic label
            cell.blit_dynamic_text(surface, (x + col_idx * cell.cell_width, y + row_idx * cell.cell_height), font)
