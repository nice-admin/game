import pygame
import sys
from game_core.entity_definitions import *
from game_core.config import GAME_AREA_WIDTH, GAME_AREA_HEIGHT, CELL_SIZE, FPS, get_display_mode, GRID_FILL_COL, GRID_EMPTY_SPACE_COL, BG_OUTSIDE_GRID_COL, adjust_color, BASE_COL
from game_core.controls import *
from game_ui.ui import *
from game_core.entity_state import EntityStateList
from game_ui.hidden_info_panel import *
import game_other.savegame as savegame
import game_other.feature_toggle as feature_toggle
import game_other.testing_layout as testing_layout
import game_core.gameplay_events
from game_ui.project_overview_panel import handle_render_queue_panel_event
from game_ui.supplies_panel import handle_supplies_panel_event
from game_ui.ui import draw_entity_hover_label_if_needed
import random
from game_ui.zone_panel import handle_zone_panel_event, draw_zones_only, _zone_creation_active


# --- Game Grid ---
def create_grid():
    return [[None for _ in range(GAME_AREA_WIDTH)] for _ in range(GAME_AREA_HEIGHT)]

def can_place_entity(grid, entity, x, y):
    width = getattr(entity, 'width', 1)
    height = getattr(entity, 'height', 1)
    for dx in range(width):
        for dy in range(height):
            gx, gy = x + dx, y + dy
            if not (0 <= gx < GAME_AREA_WIDTH and 0 <= gy < GAME_AREA_HEIGHT):
                return False
            if grid[gy][gx] is not None:
                return False
    return True

def place_entity(grid, entity_states, entity):
    gx, gy = entity.x, entity.y
    width = getattr(entity, 'width', 1)
    height = getattr(entity, 'height', 1)
    for dx in range(width):
        for dy in range(height):
            grid[gy + dy][gx + dx] = entity
    entity_states.add_entity(entity)

def remove_entity(grid, entity_states, gx, gy):
    entity = grid[gy][gx]
    if entity is not None:
        width = getattr(entity, 'width', 1)
        height = getattr(entity, 'height', 1)
        ex, ey = entity.x, entity.y
        for dx in range(width):
            for dy in range(height):
                if 0 <= ey + dy < GAME_AREA_HEIGHT and 0 <= ex + dx < GAME_AREA_WIDTH:
                    if grid[ey + dy][ex + dx] == entity:
                        grid[ey + dy][ex + dx] = None
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
    entity_states, camera_offset, _ = savegame.load_game(grid)
    cell_size = CELL_SIZE  # Always use config value, ignore saved value

    # --- Use new GameControls class for all input ---
    from game_core.controls import GameControls
    game_controls = GameControls()
    font = pygame.font.SysFont(None, 24)
    selected_index = None
    selected_entity_type = None

    # Center camera if no saved offset (i.e., default [0, 0])
    if camera_offset == [0, 0]:
        screen_width, screen_height = screen.get_width(), screen.get_height()
        camera_offset[0] = -(GAME_AREA_WIDTH * cell_size // 2 - screen_width // 2)
        camera_offset[1] = -(GAME_AREA_HEIGHT * cell_size // 2 - screen_height // 2)

    # Load icons for all entities in grid at startup
    for row in grid:
        for entity in row:
            if entity and hasattr(entity, 'load_icon'):
                entity.load_icon()

    # --- Static Entities Baking ---
    background_surface = pygame.Surface((GAME_AREA_WIDTH * cell_size, GAME_AREA_HEIGHT * cell_size))
    def bake_static_entities():
        background_surface.fill(GRID_EMPTY_SPACE_COL)
        cell_margin = 4  # Space in pixels between cells
        color = GRID_FILL_COL
        for gy in range(GAME_AREA_HEIGHT):
            for gx in range(GAME_AREA_WIDTH):
                rect = pygame.Rect(
                    gx * cell_size + cell_margin,
                    gy * cell_size + cell_margin,
                    cell_size - 2 * cell_margin,
                    cell_size - 2 * cell_margin
                )
                # Draw rounded rectangle for cell
                pygame.draw.rect(background_surface, color, rect, border_radius=2)
                # Draw 2px border with adjusted color
                border_col = adjust_color(BASE_COL, white_factor=0.0, exposure=1.3)
                pygame.draw.rect(background_surface, border_col, rect, width=1, border_radius=3)
    # Do NOT draw static entities here anymore

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
    state = dict(grid=grid, entity_states=entity_states, camera_offset=camera_offset, cell_size=cell_size, camera_drag=game_controls.camera_drag, paint_brush=game_controls.paint_brush, selected_index=selected_index, selected_entity_type=selected_entity_type, line_start=None, erase_line_start=None, GRID_WIDTH=GAME_AREA_WIDTH, GRID_HEIGHT=GAME_AREA_HEIGHT)
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
            # Update each unique entity only once per frame
            unique_entities = set()
            for row in state['grid']:
                for entity in row:
                    if entity and entity not in unique_entities:
                        unique_entities.add(entity)
                        entity.update(state['grid'])
            from game_core.game_state import update_totals_from_grid, EntityStats
            update_totals_from_grid(state['grid'])
            EntityStats().update_from_grid(state['grid'])
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
        render_game(state, screen, background_surface, font, timings, clock, game_controls)
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

    def handle_testing_layout_grid_change():
        state['testing_layout_grid_changed'] = True

    num_sections = 6  # Number of construction panel sections (update if dynamic)

    for event in pygame.event.get():
        # Allow zone panel to handle mouse events for zone creation
        zone_event_handled = handle_zone_panel_event(event)
        # If the zone panel handled the event, skip further processing
        if zone_event_handled:
            continue
        # If zone mode is active, skip all entity/game controls for this event
        if _zone_creation_active:
            continue
        # Handle music end event for random music playback
        if event.type == pygame.USEREVENT + 1:
            from game_other.audio import play_random_music_wav
            play_random_music_wav()
        # Handle render queue panel click/expand
        handle_render_queue_panel_event(event, screen_width, resource_panel_height)
        # --- Supplies panel click/slide ---
        handle_supplies_panel_event(event, pygame.display.get_surface())
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

def render_game(state, screen, background_surface, font, timings, clock, controls):
    screen.fill(BG_OUTSIDE_GRID_COL)
    screen.blit(background_surface, state['camera_offset'])
    # Draw zones underneath entities
    draw_zones_only(screen)
    min_x = max(0, int(-state['camera_offset'][0] // state['cell_size']))
    max_x = min(GAME_AREA_WIDTH, int((-state['camera_offset'][0] + screen.get_width()) // state['cell_size']) + 1)
    min_y = max(0, int(-state['camera_offset'][1] // state['cell_size']))
    max_y = min(GAME_AREA_HEIGHT, int((-state['camera_offset'][1] + screen.get_height()) // state['cell_size']) + 1)
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
    hovered_entity = grid_ref[gy][gx] if 0 <= gx < GAME_AREA_WIDTH and 0 <= gy < GAME_AREA_HEIGHT else None
    # Draw UI, pass hovered_entity and preview args
    panel_btn_rects = {}
    # Do NOT draw construction panel here; handled in draw_all_panels
    entity_buttons = None  # Will be set by draw_all_panels if needed
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
        GRID_WIDTH=GAME_AREA_WIDTH,
        GRID_HEIGHT=GAME_AREA_HEIGHT,
        selected_section=state.get('selected_section', 0),
        selected_item=state.get('selected_item', None),
        panel_btn_rects=panel_btn_rects,
        entity_buttons=entity_buttons,
        controls=controls
    )
    state['panel_btn_rects'] = panel_btn_rects

    draw_entity_hover_label_if_needed(screen, font)

    pygame.display.flip()
