# game_ui/ui.py

from game_ui.construction_panel import draw_construction_panel, ENTITY_CHOICES
from game_ui.profiler_panel import draw_profiler_panel
from game_ui.hidden_info_panel import draw_entity_state_panel
from game_ui.alerts_panel import draw_alert_panel, check_alerts
from game_ui.info_panel import draw_info_panel, get_info_panel_width
from game_other.feature_toggle import ALLOW_RESOURCES_PANEL
import pygame
from game_core.entity_state import EntityStateList
from game_ui.resource_panel import *

def draw_all_panels(surface, selected_index, font, panel_x, panel_y, panel_width, panel_height, clock=None, draw_call_count=None, tick_count=None, timings=None, grid=None, hovered_entity=None):
    """
    Draw all UI elements that are on top of the game area.
    Extend this function to include more UI overlays as needed.
    """
    if ALLOW_RESOURCES_PANEL:
        draw_resource_panel(surface, font)
        draw_icons(surface, font)
    # Draw new resource panel below the original one (standalone feature)
    draw_construction_panel(surface, selected_index, font, x=panel_x, y=panel_y, width=panel_width, height=panel_height)
    # Draw info panel and get its width
    info_panel_width = get_info_panel_width(surface.get_width())
    # Offset alerts panel by the actual info panel width
    from game_ui.alerts_panel import check_alerts, draw_alert_panel
    if grid is not None:
        check_alerts(grid, surface.get_width())
        draw_alert_panel(surface, font, surface.get_width() - info_panel_width, surface.get_height())
    if clock is not None:
        draw_profiler_panel(surface, clock, font, draw_call_count, tick_count, timings)
    draw_info_panel(surface, font, surface.get_width(), surface.get_height(), grid=grid, hovered_entity=hovered_entity)
    # Future: draw other UI overlays here

def draw_entity_preview(surface, selected_entity_type, camera_offset, cell_size, GRID_WIDTH, GRID_HEIGHT, grid):
    """
    Draws a preview of the selected entity at the mouse position, snapped to the grid, at 50% opacity.
    """
    if selected_entity_type is None:
        return
    from game_core.entity_definitions import get_icon_surface
    mx, my = pygame.mouse.get_pos()
    gx = int((mx - camera_offset[0]) // cell_size)
    gy = int((my - camera_offset[1]) // cell_size)
    if not (0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT):
        return

    # Check if the cell is already occupied
    if grid[gy][gx] is not None:
        return

    preview_entity = selected_entity_type(gx, gy)
    icon_path = getattr(preview_entity, '_icon', None)
    icon_surf = get_icon_surface(icon_path) if icon_path else None
    if icon_surf:
        icon_surf = pygame.transform.smoothscale(icon_surf, (cell_size, cell_size)).copy()
        icon_surf.fill((255,255,255,128), special_flags=pygame.BLEND_RGBA_MULT)  # 50% opacity
        surface.blit(icon_surf, (gx * cell_size + camera_offset[0], gy * cell_size + camera_offset[1]))
    # No fallback to color rectangle
