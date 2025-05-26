import pygame
import sys
from game_core.entity_definitions import *
from game_core.game_settings import GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, FPS, get_display_mode, GRID_BG_COL, GRID_BORDER_COL, BG_OUTSIDE_GRID_COL
from game_core.controls import handle_global_controls, CameraDrag, get_construction_panel_key, handle_construction_panel_selection, PaintBrush, handle_entity_pickup
from game_ui.construction_panel import draw_construction_panel, ENTITY_CHOICES, get_construction_panel_size
from game_ui.ui import draw_all_ui, draw_entity_preview
from game_core.entity_state import EntityStateList
from game_ui.entity_state_panel import *
import game_other.savegame as savegame
import game_other.feature_toggle as feature_toggle
import game_other.testing_layout as testing_layout
from game_core.game_events import handle_event
from game_core.game_state import update_totals_from_grid
import game_core.situation_manager


# --- Game Grid ---
def create_grid():
    return [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def place_entity(grid, entity_states, entity):
    gx, gy = entity.x, entity.y
    grid[gy][gx] = entity
    entity_states.add_entity(entity)

def remove_entity(grid, entity_states, gx, gy):
    grid[gy][gx] = None
    entity_states.remove_entity_at(gx, gy)

# --- Main Game Loop ---
def run_game():
    pygame.init()
    # Always use monitor resolution
    info = pygame.display.Info()
    resolution = (info.current_w, info.current_h)
    flags = pygame.SCALED
    screen = pygame.display.set_mode(resolution, flags=flags, vsync=1)
    pygame.display.set_caption("3D Artist Team Manager")
    clock = pygame.time.Clock()

    # Start situation manager (random events)
    game_core.situation_manager.start_situation_manager()

    grid = create_grid()
    # Load game state if available
    entity_states, camera_offset, cell_size = savegame.load_game(grid)
    camera_drag = CameraDrag()
    camera_drag.left_drag_enabled = True
    paint_brush = PaintBrush()
    font = pygame.font.SysFont(None, 24)
    selected_index = None
    selected_entity_type = None

    # Center camera if no saved offset (i.e., default [0, 0])
    if camera_offset == [0, 0]:
        screen_width, screen_height = screen.get_width(), screen.get_height()
        camera_offset[0] = -(GRID_WIDTH * cell_size // 2 - screen_width // 2)
        camera_offset[1] = -(GRID_HEIGHT * cell_size // 2 - screen_height // 2)

    # Get construction panel size (only needs to be recalculated if window size changes)
    panel_x, panel_y, panel_width, panel_height = get_construction_panel_size(screen.get_width(), screen.get_height())

    # Load icons for all entities in grid at startup
    for row in grid:
        for entity in row:
            if entity and hasattr(entity, 'load_icon'):
                entity.load_icon()

    # --- Static Entities Baking ---
    background_surface = pygame.Surface((GRID_WIDTH * cell_size, GRID_HEIGHT * cell_size))
    def bake_static_entities():
        background_surface.fill(GRID_BG_COL)
        # Draw grid lines onto background
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(background_surface, GRID_BORDER_COL, (x * cell_size, 0), (x * cell_size, GRID_HEIGHT * cell_size))
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(background_surface, GRID_BORDER_COL, (0, y * cell_size), (GRID_WIDTH * cell_size, y * cell_size))
        # Draw all entities onto background (static layer, no progress bars)
        for row in grid:
            for entity in row:
                if entity and hasattr(entity, 'draw'):
                    entity.draw(background_surface, (0, 0), cell_size, static_only=True)

    # Initial bake
    bake_static_entities()

    def update_game_state(grid):
        import game_core.game_state as game_state
        game_state.total_employees = game_state.count_employees(grid)
        game_state.total_breaker_strength = game_state.count_breaker_strength(grid)
        game_state.total_risky_entities = game_state.count_risky_entities(grid)
        game_state.total_power_drain = game_state.count_power_drain(grid)
        game_state.total_broken_entities = game_state.count_broken_entities(grid)

    frame_count = 0
    running = True
    prev_camera_offset = camera_offset
    prev_cell_size = cell_size
    # State dict for brevity
    state = dict(grid=grid, entity_states=entity_states, camera_offset=camera_offset, cell_size=cell_size, camera_drag=camera_drag, paint_brush=paint_brush, selected_index=selected_index, selected_entity_type=selected_entity_type, panel_x=panel_x, panel_y=panel_y, panel_width=panel_width, panel_height=panel_height, line_start=None, erase_line_start=None, GRID_WIDTH=GRID_WIDTH, GRID_HEIGHT=GRID_HEIGHT)
    while running:
        frame_start = pygame.time.get_ticks()
        grid_changed = False
        for event in pygame.event.get():
            result, changed = handle_event(event, state, remove_entity, place_entity)
            if result == 'exit':
                running = False
                break
            if changed:
                grid_changed = True
        # WSAD camera
        state['camera_offset'] = camera_drag.handle_wsad(state['camera_offset'])
        # Paint brush continuous
        paint_result = paint_brush.handle_continuous_paint(state['selected_entity_type'], state['camera_offset'], state['cell_size'], state['grid'])
        if paint_result:
            gx, gy, entity, erase = paint_result
            if erase:
                if state['grid'][gy][gx] is not None:
                    remove_entity(state['grid'], state['entity_states'], gx, gy)
                    grid_changed = True
            else:
                if state['grid'][gy][gx] is None:
                    place_entity(state['grid'], state['entity_states'], entity)
                    grid_changed = True
        # Only re-bake static entities if grid changed or cell size changed (not camera offset)
        if grid_changed or prev_cell_size != state['cell_size']:
            if background_surface.get_width() != GRID_WIDTH * state['cell_size'] or background_surface.get_height() != GRID_HEIGHT * state['cell_size']:
                background_surface = pygame.Surface((GRID_WIDTH * state['cell_size'], GRID_HEIGHT * state['cell_size']))
            bake_static_entities()
            prev_cell_size = state['cell_size']
            # Update all game state totals when grid changes
            update_totals_from_grid(state['grid'])
        prev_camera_offset = state['camera_offset']
        # --- Update Entities ---
        if frame_count % 2 == 0:
            entities_to_update = [entity for row in state['grid'] for entity in row if entity]
            for entity in entities_to_update:
                entity.update(state['grid'])
            update_game_state(state['grid'])
        # --- Draw ---
        screen.fill(BG_OUTSIDE_GRID_COL)
        screen.blit(background_surface, state['camera_offset'])
        min_x = max(0, int(-state['camera_offset'][0] // state['cell_size']))
        max_x = min(GRID_WIDTH, int((-state['camera_offset'][0] + screen.get_width()) // state['cell_size']) + 1)
        min_y = max(0, int(-state['camera_offset'][1] // state['cell_size']))
        max_y = min(GRID_HEIGHT, int((-state['camera_offset'][1] + screen.get_height()) // state['cell_size']) + 1)
        grid_ref = state['grid']
        cam_offset = state['camera_offset']
        cell_sz = state['cell_size']
        for gy in range(min_y, max_y):
            for gx in range(min_x, max_x):
                entity = grid_ref[gy][gx]
                if getattr(entity, 'draw', None):
                    entity.draw(screen, cam_offset, cell_sz, static_only=False)
        # --- Hovered entity detection ---
        mx, my = pygame.mouse.get_pos()
        gx = int((mx - cam_offset[0]) // cell_sz)
        gy = int((my - cam_offset[1]) // cell_sz)
        hovered_entity = grid_ref[gy][gx] if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT else None
        frame_end = pygame.time.get_ticks()
        frame_ms = frame_end - frame_start
        timings = {"Frame": frame_ms}
        # Draw UI, pass hovered_entity
        draw_all_ui(
            screen,
            state['selected_index'],
            font,
            panel_x,
            panel_y,
            panel_width,
            panel_height,
            clock=clock,
            draw_call_count=None,
            tick_count=None,
            timings=timings,
            grid=grid_ref,
            hovered_entity=hovered_entity
        )
        draw_entity_preview(screen, state['selected_entity_type'], cam_offset, cell_sz, GRID_WIDTH, GRID_HEIGHT, grid_ref)
        if feature_toggle.ENTITY_STATE_PANEL:
            draw_entity_state_panel(
                screen,
                font,
                hovered_entity=hovered_entity
            )
        draw_construction_panel(screen, state['selected_index'], font, x=panel_x, y=panel_y, width=panel_width, height=panel_height)
        pygame.display.flip()
        clock.tick(FPS)
        frame_count += 1
    # Save game state on exit
    savegame.save_game(state['entity_states'], state['camera_offset'], state['cell_size'])
    pygame.quit()
    sys.exit()
