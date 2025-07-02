from game_ui.profiler_panel import draw_profiler_panel
from game_ui.hidden_info_panel import draw_hidden_info_panel
from game_ui.alerts_panel import draw_alert_panel, check_alerts
import pygame
from game_ui.resource_panel_general import draw_resource_panel_general, get_baked_panel
from game_ui.resource_panel_system import draw_resource_panel_system, get_system_panel_bg
from game_ui.project_overview_panel import draw_project_overview_panel
from game_core.gameplay_events import power_outage
from game_ui.construction_panel import draw_construction_panel
from game_ui.details_panel import draw_details_panel
from game_ui.grid_overview_panel import draw_overview_panel, OVERVIEW_PANEL_WIDTH, OVERVIEW_PANEL_HEIGHT
from game_core.game_state import GameState
from game_core.config import UI_BG1_COL, UI_BORDER1_COL
from game_ui.cursor_info import draw_cursor_construction_overlay
from game_ui.arrow_pointer import draw_arrow_pointer, show_arrow_pointer
from game_ui.supplies_panel import draw_supplies_panel
from game_ui.software_panel import draw_software_panel
from game_ui.quest_panel import QuestItem, draw_quest_panel_baked
import game_ui.quest_panel as quest_panel
import math
from game_ui.experience_panel import draw_experience_panel
from game_ui.zone_panel import draw_zone_panel, set_zone_panel_grid_params, draw_zone_info_overlay

ALLOW_HIDDEN_INFO_PANEL = 1
ALLOW_RESOURCE_PANEL = 1
ALLOW_ALERTS_PANEL = 0
ALLOW_GRID_OVERVIEW_PANEL = 0
ALLOW_ARROW_POINTER = 0
ALLOW_PROJECT_OVERVIEW_PANEL = 1
ALLOW_CONSTRUCTION_PANEL = 1
ALLOW_SUPPLIES_PANEL = 1
ALLOW_EXPERIENCE_PANEL = 1
ALLOW_SOFTWARE_PANEL = 1
ALLOW_QUEST_PANEL = 1
ALLOW_SAVE_AND_LOAD = 0

def draw_all_panels(surface, selected_index, font, clock=None, draw_call_count=None, tick_count=None, timings=None, grid=None, hovered_entity=None, selected_entity_type=None, camera_offset=None, cell_size=None, GRID_WIDTH=None, GRID_HEIGHT=None, selected_section=0, selected_item=0, panel_btn_rects=None, entity_buttons=None, controls=None):
    
    pickup_offset = (0, 0)
    if controls is not None and getattr(controls, '_pickup_mode', False):
        pickup_offset = getattr(controls, 'pickup_offset', (0, 0))
    if all(v is not None for v in [camera_offset, cell_size, GRID_WIDTH, GRID_HEIGHT, grid]) and callable(GameState().current_construction_class):
        draw_cursor_construction_overlay(surface, None, camera_offset, cell_size, GRID_WIDTH, GRID_HEIGHT, grid, pickup_offset=pickup_offset)
    selected_entity_class = None
    if entity_buttons is not None and selected_item is not None and 0 <= selected_item < len(entity_buttons):
        selected_entity_class = entity_buttons[selected_item].entity_class
    else:
        selected_entity_class = selected_entity_type
    if all(v is not None for v in [selected_entity_class, camera_offset, cell_size, GRID_WIDTH, GRID_HEIGHT, grid]):
        draw_cursor_construction_overlay(surface, selected_entity_class, camera_offset, cell_size, GRID_WIDTH, GRID_HEIGHT, grid)
    power_outage.draw_overlay(surface)

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
    if ALLOW_SUPPLIES_PANEL:
        draw_supplies_panel(surface)
    if ALLOW_CONSTRUCTION_PANEL:
        section_btn_rects, item_btn_rects = draw_construction_panel(
            surface, selected_section=selected_section, selected_item=selected_item, font=font, extend_below=0
        )
        if panel_btn_rects is not None:
            panel_btn_rects['section'] = section_btn_rects
            panel_btn_rects['item'] = item_btn_rects

    overview_panel_x = 0
    overview_panel_y = surface.get_height() - OVERVIEW_PANEL_HEIGHT
    if ALLOW_GRID_OVERVIEW_PANEL:
        draw_overview_panel(surface, font, overview_panel_x, overview_panel_y, width=OVERVIEW_PANEL_WIDTH, height=OVERVIEW_PANEL_HEIGHT, grid=grid)

    show_details_bg = hovered_entity is not None
    draw_details_panel(surface, font, entity=hovered_entity, show_bg=show_details_bg)

    if ALLOW_EXPERIENCE_PANEL:
        draw_experience_panel(surface)

    check_alerts(grid, surface.get_width())
    if ALLOW_ALERTS_PANEL:
        draw_alert_panel(surface, font, surface.get_width(), surface.get_height())
    if ALLOW_PROJECT_OVERVIEW_PANEL:
        draw_project_overview_panel(surface, font, surface.get_width(), resource_panel_height = 130)
    if ALLOW_ARROW_POINTER:
        show_arrow_pointer()
        draw_arrow_pointer(surface, 1440, 85)

    if ALLOW_SOFTWARE_PANEL:
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        software_buttons, hovered_software_idx, selected_software_idx = draw_software_panel(
            surface, mouse_pos=mouse_pos, mouse_pressed=mouse_pressed
        )

    if ALLOW_QUEST_PANEL:
        draw_quest_panel_baked(surface, quest_panel.active_quests, quest_panel.random_active_quests)
    if ALLOW_HIDDEN_INFO_PANEL:
        draw_hidden_info_panel(surface, font, hovered_entity=hovered_entity)
        draw_profiler_panel(surface, clock, font, draw_call_count, tick_count, timings)
        
    set_zone_panel_grid_params(camera_offset, cell_size, GRID_WIDTH, GRID_HEIGHT)
    draw_zone_panel(surface)
    draw_zone_info_overlay(surface)


def draw_entity_hover_label_if_needed(screen, font):
    import pygame
    from game_ui.construction_panel import get_entity_button_hover, draw_entity_hover_label
    from game_ui import construction_panel
    try:
        entity_buttons = getattr(construction_panel, '_baked_panel_cache', {}).get('entity_buttons', None)
        if entity_buttons:
            mouse_pos = pygame.mouse.get_pos()
            entity_class, _ = get_entity_button_hover(entity_buttons, mouse_pos)
            draw_entity_hover_label(screen, entity_class, mouse_pos, font)
    except Exception:
        pass
