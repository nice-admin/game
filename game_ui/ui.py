# game_ui/ui.py

from game_ui.construction_panel import draw_construction_panel
from game_ui.profiler_panel import draw_profiler_panel
from game_ui.hidden_info_panel import draw_entity_state_panel
from game_ui.alerts_panel import draw_alert_panel, check_alerts
from game_ui.info_panel import draw_info_panel, get_info_panel_width
from game_other.feature_toggle import *
import pygame
from game_ui.resource_panel import draw_resource_panel, draw_icons, get_baked_panel
from game_ui.render_queue_panel import draw_render_queue_panel
from game_core.situation_manager import power_outage


def draw_all_panels(surface, selected_index, font, panel_x, panel_y, panel_width, panel_height, clock=None, draw_call_count=None, tick_count=None, timings=None, grid=None, hovered_entity=None, selected_entity_type=None, camera_offset=None, cell_size=None, GRID_WIDTH=None, GRID_HEIGHT=None):
    """
    Draw all UI elements that are on top of the game area.
    This is the single entry point for all UI overlays.
    """
    if ALLOW_RESOURCE_PANEL:
        draw_resource_panel(surface, font)
        draw_icons(surface, font)
        baked = get_baked_panel(font)
        resource_panel_height = baked['total_height']
    
    draw_construction_panel(surface, selected_index, font, x=panel_x, y=panel_y, width=panel_width, height=panel_height)
    
    info_panel_width = get_info_panel_width(surface.get_width())
    
    check_alerts(grid, surface.get_width())
    
    if ALLOW_ALERTS_PANEL:
        draw_alert_panel(surface, font, surface.get_width() - info_panel_width, surface.get_height())

    if ALLOW_INFO_PANEL:
        draw_info_panel(surface, font, surface.get_width(), surface.get_height(), grid=grid, hovered_entity=hovered_entity)
    
    if all(v is not None for v in [selected_entity_type, camera_offset, cell_size, GRID_WIDTH, GRID_HEIGHT, grid]):
        draw_entity_preview(surface, selected_entity_type, camera_offset, cell_size, GRID_WIDTH, GRID_HEIGHT, grid)
    
    if ENTITY_STATE_PANEL:
        draw_entity_state_panel(surface, font, hovered_entity=hovered_entity)
    
    draw_profiler_panel(surface, clock, font, draw_call_count, tick_count, timings)
    # Draw render queue panel at the top, centered, below resource panel

    if ALLOW_RENDER_QUEUE_PANEL:
        draw_render_queue_panel(surface, font, surface.get_width(), resource_panel_height)
    # Draw power outage overlay LAST if active
    power_outage.draw_overlay(surface)


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
