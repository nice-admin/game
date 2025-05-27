"""
Event handling logic for the main game loop.

This module provides the handle_event function, which processes all user and system events for the game:
- Handles global controls (exit, clear, etc.)
- Handles entity pickup, placement, and removal
- Handles construction panel interactions
- Handles paint brush actions for placing/erasing entities
- Handles toggling the entity state panel
- Updates the game grid and entity states as needed

Intended to be called from the main game loop to keep event logic modular and concise.
"""

import pygame
from game_core.controls import handle_global_controls, handle_entity_pickup, handle_construction_panel_selection
from game_ui.construction_panel import ENTITY_CHOICES
import game_other.testing_layout as testing_layout

def handle_event(event, state, remove_entity, place_entity):
    grid_changed = False
    testing_layout.handle_testing_layout(event, state['grid'], state['entity_states'], state['GRID_WIDTH'], state['GRID_HEIGHT'])
    global_result = handle_global_controls(event, grid=state['grid'], entity_states=state['entity_states'])
    if global_result == 'exit' or event.type == pygame.QUIT:
        return 'exit', grid_changed
    if global_result == 'cleared':
        return None, True
    state['selected_index'], state['selected_entity_type'], pickup_grid_changed = handle_entity_pickup(
        event, state['selected_index'], state['selected_entity_type'], state['grid'], state['entity_states'], ENTITY_CHOICES, remove_entity, place_entity, state['camera_offset'], state['cell_size']
    )
    if pickup_grid_changed:
        return None, True
    entity_preview_active = state['selected_entity_type'] is not None
    state['camera_offset'] = state['camera_drag'].handle_event(event, state['camera_offset'], entity_preview_active)
    args = (event, state['panel_x'], state['panel_y'], state['panel_width'], state['panel_height'], ENTITY_CHOICES, state['selected_index'], state['selected_entity_type'], state['camera_offset'], state['cell_size'], state['GRID_WIDTH'], state['GRID_HEIGHT'], state['grid'], state.get('line_start'), state.get('erase_line_start'))
    (state['selected_index'], state['selected_entity_type'], placed_entity, removed_coords, line_entities, state['line_start'], erase_line_coords, state['erase_line_start']) = handle_construction_panel_selection(*args)
    def place(e):
        if hasattr(e, 'load_icon'): e.load_icon()
        place_entity(state['grid'], state['entity_states'], e)
        if hasattr(e, 'on_built'):
            e.on_built()
    if placed_entity is not None:
        place(placed_entity)
        grid_changed = True
    if line_entities:
        for e in line_entities: place(e)
        grid_changed = True
    if erase_line_coords:
        for gx, gy in erase_line_coords:
            if state['grid'][gy][gx] is not None:
                remove_entity(state['grid'], state['entity_states'], gx, gy)
                grid_changed = True
    if removed_coords is not None:
        gx, gy = removed_coords
        remove_entity(state['grid'], state['entity_states'], gx, gy)
        grid_changed = True
    paint_result = state['paint_brush'].handle_event(event, state['selected_entity_type'], state['camera_offset'], state['cell_size'], state['grid'])
    if paint_result:
        gx, gy, entity, erase = paint_result
        if erase:
            if state['grid'][gy][gx] is not None:
                remove_entity(state['grid'], state['entity_states'], gx, gy)
                grid_changed = True
        else:
            if state['grid'][gy][gx] is None:
                place_entity(state['grid'], state['entity_states'], entity)
                if hasattr(entity, 'on_built'):
                    entity.on_built()
                grid_changed = True
    if event.type == pygame.KEYDOWN and event.key == pygame.K_SEMICOLON:
        from game_ui.hidden_info_panel import handle_panel_toggle_event
        from game_ui.profiler_panel import handle_profiler_panel_toggle
        handle_panel_toggle_event(event)
        handle_profiler_panel_toggle()
        return None, grid_changed
    return None, grid_changed
