import pygame
from game_core.game_state import GameState
from game_core.config import FONT1, CURRENCY_SYMBOL, CELL_SIZE_INNER
    
class NameLabel:
    def __init__(self, display_name, font, pad_x=10, pad_y=6):
        self.display_name = display_name
        self.font = font
        self.pad_x = pad_x
        self.pad_y = pad_y
        self.surf = self.font.render(self.display_name, True, (255, 255, 255))
        self.width = self.surf.get_width()
        self.height = self.surf.get_height()

    def draw(self, surface, x, y):
        surface.blit(self.surf, (x + self.pad_x, y + self.pad_y))

class DetailLabel:
    def __init__(self, label, value, font=None, color=(255,255,255), pad_x=10, pad_y=0, font_size=None):
        self.label = label
        self.value = value
        self.color = color
        self.pad_x = pad_x
        self.pad_y = pad_y
        # Use font_size if provided, otherwise default to 15
        if font_size is not None:
            self.font = pygame.font.Font(FONT1, font_size)
        else:
            self.font = pygame.font.Font(FONT1, 15)
        self.surf = self.font.render(f"{self.label}{self.value}", True, self.color)
        self.width = self.surf.get_width()
        self.height = self.surf.get_height()

    def draw(self, surface, x, y):
        surface.blit(self.surf, (x + self.pad_x, y + self.pad_y))

class EntityInfo:
    BG_COL = (0, 0, 0, 60)  # Semi-transparent black
    BG_ROUNDING = 5         # Border radius for background rectangle
    FONT_SIZE = 25          # Default font size (can be scaled)
    margin_from_top = 0     # Margin from top of background to NameLabel

    def __init__(self, entity, cell_size):
        self.entity = entity
        self.cell_size = cell_size
        self.display_name = getattr(entity, 'display_name', type(entity).__name__)
        self.purchase_cost = getattr(entity, 'purchase_cost', None)
        # Always use FONT_SIZE for the name font size
        self.font = pygame.font.Font(FONT1, self.FONT_SIZE)
        self.name = NameLabel(self.display_name, self.font)
        # Only show cost and money if purchase_cost > 0
        if isinstance(self.purchase_cost, (int, float)) and self.purchase_cost > 0:
            # Use CURRENCY_SYMBOL from config.py
            self.detail_cost = DetailLabel(f"-{CURRENCY_SYMBOL}", self.purchase_cost, self.font, color=(255,0,0), font_size=20)
            total_money = getattr(GameState(), 'total_money', None)
            self.detail_money = DetailLabel(f"{CURRENCY_SYMBOL}", total_money, self.font, color=(0,255,0)) if isinstance(total_money, (int, float)) else None
        else:
            self.detail_cost = None
            self.detail_money = None
        self.pad_x = 10
        self.pad_y = self.margin_from_top
        self.label_gap = 5  # Space between NameLabel and the rest
        self.text_width = max(self.name.width, self.detail_cost.width if self.detail_cost else 0, self.detail_money.width if self.detail_money else 0)
        self.text_height = self.name.height + (self.label_gap if self.detail_cost or self.detail_money else 0) + (self.detail_cost.height if self.detail_cost else 0) + (self.detail_money.height if self.detail_money else 0) + 8
        self.rect_w = self.text_width + 2 * self.pad_x
        self.rect_h = self.text_height + 2 * self.pad_y

    def draw(self, surface, icon_x, icon_y):
        # Place the rectangle so its top left corner matches the icon's bottom right corner
        rect_x = icon_x + self.cell_size
        rect_y = icon_y + self.cell_size
        # Create a temporary surface for alpha blending
        temp_surf = pygame.Surface((self.rect_w, self.rect_h), pygame.SRCALPHA)
        pygame.draw.rect(temp_surf, self.BG_COL, temp_surf.get_rect(), border_radius=self.BG_ROUNDING)
        surface.blit(temp_surf, (rect_x, rect_y))
        y = rect_y + self.margin_from_top
        self.name.draw(surface, rect_x, y)
        y += self.name.height
        if self.detail_cost or self.detail_money:
            y += self.label_gap  # Add gap after name if there are detail labels
        if self.detail_cost:
            self.detail_cost.draw(surface, rect_x, y)
            y += self.detail_cost.height + 2
        if self.detail_money:
            self.detail_money.draw(surface, rect_x, y)

def draw_cursor_construction_overlay(surface, selected_entity_type, camera_offset, cell_size, GRID_W, GRID_H, grid, pickup_offset=(0, 0)):
    entity_type = GameState().current_construction_class
    if not callable(entity_type): return
    from game_core.entity_definitions import get_icon_surface
    from game_core.game_loop import can_place_entity  # Use the correct area-aware function
    mx, my = pygame.mouse.get_pos()
    mouse_gx, mouse_gy = int((mx - camera_offset[0]) // cell_size), int((my - camera_offset[1]) // cell_size)
    gx = mouse_gx - pickup_offset[0]
    gy = mouse_gy - pickup_offset[1]
    if not (0 <= gx < GRID_W and 0 <= gy < GRID_H): return
    preview = entity_type(gx, gy)
    icon_path = getattr(preview, '_icon', None)
    icon = get_icon_surface(icon_path) if icon_path else None
    width = getattr(preview, 'width', 1)
    height = getattr(preview, 'height', 1)
    if icon:
        from game_core.config import CELL_SIZE_INNER
        margin = (cell_size - CELL_SIZE_INNER)
        icon_w = cell_size * width - margin
        icon_h = cell_size * height - margin
        icon_scaled = pygame.transform.smoothscale(icon, (int(icon_w), int(icon_h))).copy()
        ix = gx * cell_size + camera_offset[0] + (cell_size * width - icon_w) // 2
        iy = gy * cell_size + camera_offset[1] + (cell_size * height - icon_h) // 2
        if not hasattr(draw_cursor_construction_overlay, 'last_cell'):
            draw_cursor_construction_overlay.last_cell = None
        mouse_held = pygame.mouse.get_pressed()[0]
        if mouse_held:
            draw_cursor_construction_overlay.last_cell = (gx, gy)
        else:
            draw_cursor_construction_overlay.last_cell = None
        # Use area-aware can_place_entity
        can_place = mouse_held and draw_cursor_construction_overlay.last_cell == (gx, gy) or can_place_entity(grid, preview, gx, gy)
        color = (0,255,0,80) if can_place else (255,0,0,80)
        highlight_w = cell_size * width - margin
        highlight_h = cell_size * height - margin
        highlight_x = gx * cell_size + camera_offset[0] + margin // 2
        highlight_y = gy * cell_size + camera_offset[1] + margin // 2
        rect = pygame.Surface((highlight_w, highlight_h), pygame.SRCALPHA)
        pygame.draw.rect(rect, color, rect.get_rect(), border_radius=4)
        surface.blit(rect, (highlight_x, highlight_y))
        icon_scaled.fill((255,255,255,128), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(icon_scaled, (ix, iy))
        EntityInfo(preview, cell_size).draw(surface, ix, iy)

