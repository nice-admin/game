import pygame
from game_core.game_state import GameState
from game_core.config import FONT1

class EntityInfo:
    BG_COL = (0, 0, 0, 50)  # Semi-transparent black
    BG_ROUNDING = 4         # Border radius for background rectangle
    FONT_SIZE = 15          # Default font size (can be scaled)

    def __init__(self, entity, cell_size):
        self.entity = entity
        self.cell_size = cell_size
        self.display_name = getattr(entity, 'display_name', type(entity).__name__)
        self.purchase_cost = getattr(entity, 'purchase_cost', None)
        self.font = pygame.font.Font(FONT1, max(self.FONT_SIZE, cell_size // 2))
        self.name_surf = self.font.render(self.display_name, True, (255, 255, 255))
        cost_text = f"-${self.purchase_cost}" if isinstance(self.purchase_cost, (int, float)) and self.purchase_cost > 0 else ""
        self.cost_surf = self.font.render(cost_text, True, (255, 0, 0)) if cost_text else None
        self.pad_x, self.pad_y = 10, 6
        self.text_width = max(self.name_surf.get_width(), self.cost_surf.get_width() if self.cost_surf else 0)
        self.text_height = self.name_surf.get_height() + (self.cost_surf.get_height() if self.cost_surf else 0) + 8
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
        # Draw display_name and price on top of the rectangle, left-aligned
        name_rect = self.name_surf.get_rect(topleft=(rect_x + self.pad_x, rect_y + self.pad_y))
        surface.blit(self.name_surf, name_rect)
        if self.cost_surf:
            cost_rect = self.cost_surf.get_rect(topleft=(rect_x + self.pad_x, name_rect.bottom + 2))
            surface.blit(self.cost_surf, cost_rect)

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
