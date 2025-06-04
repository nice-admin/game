import pygame
from game_core.game_state import GameState
from game_core.config import FONT1
    
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
    BG_COL = (0, 0, 0, 30)  # Semi-transparent black
    BG_ROUNDING = 5         # Border radius for background rectangle
    FONT_SIZE = 15          # Default font size (can be scaled)
    margin_from_top = 0     # Margin from top of background to NameLabel

    def __init__(self, entity, cell_size):
        self.entity = entity
        self.cell_size = cell_size
        self.display_name = getattr(entity, 'display_name', type(entity).__name__)
        self.purchase_cost = getattr(entity, 'purchase_cost', None)
        self.font = pygame.font.Font(FONT1, max(self.FONT_SIZE, cell_size // 2))
        self.name = NameLabel(self.display_name, self.font)
        # Only show cost and money if purchase_cost > 0
        if isinstance(self.purchase_cost, (int, float)) and self.purchase_cost > 0:
            # Make purchase cost label larger (font size 18)
            self.detail_cost = DetailLabel("-$", self.purchase_cost, self.font, color=(255,0,0), font_size=20)
            total_money = getattr(GameState(), 'total_money', None)
            self.detail_money = DetailLabel("$", total_money, self.font, color=(0,255,0)) if isinstance(total_money, (int, float)) else None
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

def draw_entity_preview(surface, selected_entity_type, camera_offset, cell_size, GRID_WIDTH, GRID_HEIGHT, grid):
    # Always use the global singleton for construction class
    entity_type = GameState().current_construction_class
    if not callable(entity_type):
        return
    from game_core.entity_definitions import get_icon_surface
    mx, my = pygame.mouse.get_pos()
    grid_x = int((mx - camera_offset[0]) // cell_size)
    grid_y = int((my - camera_offset[1]) // cell_size)
    if not (0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT):
        return
    # Remove the check for existing entity so preview always shows
    preview_entity = entity_type(grid_x, grid_y)
    icon_path = getattr(preview_entity, '_icon', None)
    icon_surf = get_icon_surface(icon_path) if icon_path else None
    if icon_surf:
        icon_surf = pygame.transform.smoothscale(icon_surf, (cell_size, cell_size)).copy()
        icon_surf.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)
        icon_x = grid_x * cell_size + camera_offset[0]
        icon_y = grid_y * cell_size + camera_offset[1]
        surface.blit(icon_surf, (icon_x, icon_y))
        # Use EntityInfo for overlay
        info = EntityInfo(preview_entity, cell_size)
        info.draw(surface, icon_x, icon_y)
