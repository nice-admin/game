import pygame
import sys
from game_core.entity_definitions import *
from game_core.config import GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, FPS, get_display_mode, GRID_BG_COL, GRID_BORDER_COL, BG_OUTSIDE_GRID_COL
from game_core.controls import *
from game_ui.ui import *
from game_core.entity_state import EntityStateList
from game_ui.hidden_info_panel import *
import game_other.savegame as savegame
import game_other.feature_toggle as feature_toggle
import game_other.testing_layout as testing_layout
from game_core.game_state import update_totals_from_grid
import game_core.gameplay_events
from game_ui.project_overview_panel import handle_render_queue_panel_event


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

    # Start gameplay evennts
    game_core.gameplay_events.start_random_gameplay_events()
    game_core.gameplay_events.start_deterministic_gameplay_events()

    grid = create_grid()
    # Load game state if available
    entity_states, camera_offset, cell_size = savegame.load_game(grid)
    # --- Use new GameControls class for all input ---
    from game_core.controls import GameControls
    game_controls = GameControls()
    font = pygame.font.SysFont(None, 24)
    selected_index = None
    selected_entity_type = None

    # Center camera if no saved offset (i.e., default [0, 0])
    if camera_offset == [0, 0]:
        screen_width, screen_height = screen.get_width(), screen.get_height()
        camera_offset[0] = -(GRID_WIDTH * cell_size // 2 - screen_width // 2)
        camera_offset[1] = -(GRID_HEIGHT * cell_size // 2 - screen_height // 2)

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
        from game_core.game_state import GameState
        state = GameState()
        state.total_employees = state.count_employees(grid)
        state.total_breaker_strength = state.count_breaker_strength(grid)
        state.total_risky_entities = state.count_risky_entities(grid)
        state.total_power_drain = state.count_power_drain(grid)
        state.total_broken_entities = state.count_broken_entities(grid)

    frame_count = 0
    running = True
    prev_camera_offset = camera_offset
    prev_cell_size = cell_size
    state = dict(grid=grid, entity_states=entity_states, camera_offset=camera_offset, cell_size=cell_size, camera_drag=game_controls.camera_drag, paint_brush=game_controls.paint_brush, selected_index=selected_index, selected_entity_type=selected_entity_type, line_start=None, erase_line_start=None, GRID_WIDTH=GRID_WIDTH, GRID_HEIGHT=GRID_HEIGHT)
    from game_core.game_state import GameState
    gs = GameState()
    while running:
        frame_start = pygame.time.get_ticks()
        # Handle events (all input via GameControls)
        running, _ = handle_events(state, game_controls, remove_entity, place_entity)
        # Camera WSAD movement
        state['camera_offset'] = game_controls.camera_drag.handle_wsad(state['camera_offset'])
        # --- Update all entities every 2 frames ---
        if frame_count % 2 == 0:
            for row in state['grid']:
                for entity in row:
                    if entity:
                        entity.update(state['grid'])
            from game_core.game_state import update_totals_from_grid
            update_totals_from_grid(state['grid'])
        dt = clock.tick(FPS)
        # 1 in-game day = 10 seconds, so 30 days = 300 seconds
        seconds_per_month = 30 * 10
        # Update total_money
        if not hasattr(gs, '_upkeep_accumulator'):
            gs._upkeep_accumulator = 0.0
        deduction = gs.total_upkeep * (dt / 1000.0) / seconds_per_month
        gs._upkeep_accumulator += deduction
        int_deduction = int(gs._upkeep_accumulator)
        if int_deduction > 0:
            gs.total_money -= int_deduction
            gs._upkeep_accumulator -= int_deduction
        prev_camera_offset = state['camera_offset']
        # Render
        frame_end = pygame.time.get_ticks()
        frame_ms = frame_end - frame_start
        gs.game_time_seconds += dt / 1000.0
        gs.game_time_days = int(gs.game_time_seconds // 10) + 1
        timings = {"Frame": frame_ms}
        render_game(state, screen, background_surface, font, timings, clock)
        frame_count += 1
    # Save game state on exit
    savegame.save_game(state['entity_states'], state['camera_offset'], state['cell_size'])
    pygame.quit()
    sys.exit()

# --- All event handling now routed through GameControls ---
def handle_events(state, game_controls, remove_entity, place_entity):
    font = state.get('font', None)
    screen_width = pygame.display.get_surface().get_width()
    baked = get_baked_panel(font)
    resource_panel_height = baked['total_height']

    # Define the callback for async grid changes (must be in this scope)
    def handle_testing_layout_grid_change():
        state['testing_layout_grid_changed'] = True

    for event in pygame.event.get():
        # Handle render queue panel click/expand
        handle_render_queue_panel_event(event, screen_width, resource_panel_height)
        # Wire up testing layout async grid change callback
        testing_layout.handle_testing_layout(
            event,
            state['grid'],
            state['entity_states'],
            state['GRID_WIDTH'],
            state['GRID_HEIGHT'],
            on_entity_placed=state.setdefault('testing_layout_grid_change_cb', handle_testing_layout_grid_change)
        )
        result, grid_changed = game_controls.handle_event(event, state, remove_entity, place_entity)
        if result == 'exit':
            return False, False
    return True, False

def update_game_logic(state, frame_count, update_game_state):
    # No construction/game logic update
    return False

def render_game(state, screen, background_surface, font, timings, clock):
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
    # Draw UI, pass hovered_entity and preview args
    panel_btn_rects = {}
    # Draw construction panel and get entity_buttons for preview
    from game_ui.construction_panel import draw_construction_panel
    section_btn_rects, entity_buttons = draw_construction_panel(
        screen,
        selected_section=state.get('selected_section', 0),
        selected_item=state.get('selected_item', None),
        font=font
    )
    # Now pass entity_buttons to draw_all_panels
    draw_all_panels(
        screen,
        state['selected_index'],
        font,
        clock=clock,
        draw_call_count=None,
        tick_count=None,
        timings=timings,
        grid=grid_ref,
        hovered_entity=hovered_entity,
        selected_entity_type=state['selected_entity_type'],
        camera_offset=cam_offset,
        cell_size=cell_sz,
        GRID_WIDTH=GRID_WIDTH,
        GRID_HEIGHT=GRID_HEIGHT,
        selected_section=state.get('selected_section', 0),
        selected_item=state.get('selected_item', None),
        panel_btn_rects=panel_btn_rects,
        entity_buttons=entity_buttons
    )
    state['panel_btn_rects'] = panel_btn_rects
    pygame.display.flip()
