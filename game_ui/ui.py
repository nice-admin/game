from game_ui.profiler_panel import draw_profiler_panel
from game_ui.hidden_info_panel import draw_hidden_info_panel
from game_ui.alerts_panel import draw_alert_panel, check_alerts
from game_ui.info_panel import draw_info_panel, get_info_panel_width
from game_other.feature_toggle import *
import pygame
from game_ui.resource_panel_general import draw_resource_panel_general, get_baked_panel
from game_ui.resource_panel_system import draw_resource_panel_system, get_system_panel_bg
from game_ui.project_overview_panel import draw_project_overview_panel
from game_core.gameplay_events import power_outage
from game_ui.construction_panel import draw_construction_panel
from game_ui.details_panel import draw_details_panel, DETAILS_PANEL_WIDTH, DETAILS_PANEL_HEIGHT
from game_ui.grid_overview_panel import draw_overview_panel, OVERVIEW_PANEL_WIDTH, OVERVIEW_PANEL_HEIGHT
from game_core.game_state import GameState
from game_core.config import UI_BG1_COL, UI_BORDER1_COL
from game_ui.cursor_info import draw_entity_preview
from game_ui.arrow_pointer import draw_arrow_pointer, show_arrow_pointer


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
        baked = get_baked_panel(font)
        general_width, general_height = baked['total_width'], baked['total_height']
        system_bg = get_system_panel_bg()
        system_width, system_height = system_bg.get_width(), system_bg.get_height()
        panel_gap = 10
        total_width = general_width + panel_gap + system_width
        total_height = max(general_height, system_height)
        x0 = (surface.get_width() - total_width) // 2
        y0 = 0
        draw_resource_panel_general(surface.subsurface(pygame.Rect(x0, y0 + (total_height - general_height) // 2, general_width, general_height)),font)
        draw_resource_panel_system(surface,font,x0 + general_width + panel_gap,y0 + (total_height - system_height) // 2)
        resource_panel_height = total_height
    if ALLOW_CONSTRUCTION_PANEL:
        section_btn_rects, item_btn_rects = draw_construction_panel(
            surface, selected_section=selected_section, selected_item=selected_item, font=font, extend_below=0
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
        draw_alert_panel(surface, font, surface.get_width(), surface.get_height())
    if ALLOW_INFO_PANEL:
        draw_info_panel(surface, font, surface.get_width(), surface.get_height(), grid=grid)
    if ALLOW_HIDDEN_INFO_PANEL:
        draw_hidden_info_panel(surface, font, hovered_entity=hovered_entity)
    draw_profiler_panel(surface, clock, font, draw_call_count, tick_count, timings)
    if ALLOW_PROJECT_OVERVIEW_PANEL:
        draw_project_overview_panel(surface, font, surface.get_width(), resource_panel_height = 130)
    power_outage.draw_overlay(surface)
    show_arrow_pointer()  # Ensure the pointer is scheduled to appear (will only trigger once)
    draw_arrow_pointer(surface, 1440, 85)
