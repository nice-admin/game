from game_ui.profiler_panel import draw_profiler_panel
from game_ui.hidden_info_panel import draw_entity_state_panel
from game_ui.alerts_panel import draw_alert_panel, check_alerts
from game_ui.info_panel import draw_info_panel, get_info_panel_width
from game_other.feature_toggle import *
import pygame
from game_ui.resource_panel import draw_resource_panel, get_baked_panel
from game_ui.render_queue_panel import draw_render_queue_panel
from game_core.gameplay_events import power_outage
from game_ui.construction_panel import draw_construction_panel
from game_ui.details_panel import draw_details_panel, DETAILS_PANEL_WIDTH, DETAILS_PANEL_HEIGHT
from game_ui.overview_panel import draw_overview_panel, OVERVIEW_PANEL_WIDTH, OVERVIEW_PANEL_HEIGHT
from game_core.game_state import GameState


def draw_all_panels(surface, selected_index, font, clock=None, draw_call_count=None, tick_count=None, timings=None, grid=None, hovered_entity=None, selected_entity_type=None, camera_offset=None, cell_size=None, GRID_WIDTH=None, GRID_HEIGHT=None, selected_section=0, selected_item=0, panel_btn_rects=None, entity_buttons=None):
    from game_core.game_state import GameState
    # Always preview the current construction class if set
    if all(v is not None for v in [camera_offset, cell_size, GRID_WIDTH, GRID_HEIGHT, grid]) and callable(GameState().current_construction_class):
        draw_entity_preview(surface, None, camera_offset, cell_size, GRID_WIDTH, GRID_HEIGHT, grid)
    selected_entity_class = None
    if entity_buttons is not None and selected_item is not None and 0 <= selected_item < len(entity_buttons):
        selected_entity_class = entity_buttons[selected_item].entity_class
    else:
        selected_entity_class = selected_entity_type
    if all(v is not None for v in [selected_entity_class, camera_offset, cell_size, GRID_WIDTH, GRID_HEIGHT, grid]):
        draw_entity_preview(surface, selected_entity_class, camera_offset, cell_size, GRID_WIDTH, GRID_HEIGHT, grid)
    if ALLOW_RESOURCE_PANEL:
        draw_resource_panel(surface, font)
        baked = get_baked_panel(font)
        resource_panel_height = baked['total_height']
    section_btn_rects, item_btn_rects = draw_construction_panel(
        surface, selected_section=selected_section, selected_item=selected_item, font=font
    )
    if panel_btn_rects is not None:
        panel_btn_rects['section'] = section_btn_rects
        panel_btn_rects['item'] = item_btn_rects

    # Anchor overview panel to bottom left
    overview_panel_x = 0
    overview_panel_y = surface.get_height() - OVERVIEW_PANEL_HEIGHT
    draw_overview_panel(surface, font, overview_panel_x, overview_panel_y, width=OVERVIEW_PANEL_WIDTH, height=OVERVIEW_PANEL_HEIGHT, grid=grid)

    # Anchor details panel to bottom right
    details_panel_x = surface.get_width() - DETAILS_PANEL_WIDTH
    details_panel_y = surface.get_height() - DETAILS_PANEL_HEIGHT
    draw_details_panel(surface, font, details_panel_x, details_panel_y, width=DETAILS_PANEL_WIDTH, height=DETAILS_PANEL_HEIGHT, entity=hovered_entity)

    info_panel_width = get_info_panel_width(surface.get_width())
    check_alerts(grid, surface.get_width())
    if ALLOW_ALERTS_PANEL:
        draw_alert_panel(surface, font, surface.get_width() - info_panel_width, surface.get_height())
    if ALLOW_INFO_PANEL:
        draw_info_panel(surface, font, surface.get_width(), surface.get_height(), grid=grid)
    if ENTITY_STATE_PANEL:
        draw_entity_state_panel(surface, font, hovered_entity=hovered_entity)
    draw_profiler_panel(surface, clock, font, draw_call_count, tick_count, timings)
    if ALLOW_RENDER_QUEUE_PANEL:
        draw_render_queue_panel(surface, font, surface.get_width(), resource_panel_height)
    power_outage.draw_overlay(surface)


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
    if grid[grid_y][grid_x] is not None:
        return
    preview_entity = entity_type(grid_x, grid_y)
    icon_path = getattr(preview_entity, '_icon', None)
    icon_surf = get_icon_surface(icon_path) if icon_path else None
    if icon_surf:
        icon_surf = pygame.transform.smoothscale(icon_surf, (cell_size, cell_size)).copy()
        icon_surf.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(icon_surf, (grid_x * cell_size + camera_offset[0], grid_y * cell_size + camera_offset[1]))
