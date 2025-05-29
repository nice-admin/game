# game_core/controls.py
import pygame
import game_other.audio as audio
from game_core.config import GRID_WIDTH, GRID_HEIGHT
# --- Merged from input_events.py ---
import game_other.testing_layout as testing_layout

def handle_global_controls(event, grid=None, entity_states=None):
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        return 'exit'
    if event.type == pygame.KEYDOWN and event.key == pygame.K_DELETE:
        if grid is not None and entity_states is not None:
            for y, row in enumerate(grid):
                for x, entity in enumerate(row):
                    if entity is not None:
                        entity_states.remove_entity_at(x, y)
                        row[x] = None
            return 'cleared'
    return None

def get_construction_panel_key(event):
    if event.type == pygame.KEYDOWN and pygame.K_1 <= event.key <= pygame.K_9:
        return event.key - pygame.K_1
    return None

def _handle_line_build(prev_game_click, gx, gy, shift_held, selected_entity_type, grid):
    if shift_held and prev_game_click is not None and prev_game_click != (gx, gy):
        x0, y0 = prev_game_click
        x1, y1 = gx, gy
        return line_build(x0, y0, x1, y1, grid, selected_entity_type)
    return []

def _handle_line_erase(prev_game_right_click, gx, gy, shift_held):
    if shift_held and prev_game_right_click is not None and prev_game_right_click != (gx, gy):
        x0, y0 = prev_game_right_click
        x1, y1 = gx, gy
        return line_deconstruct(x0, y0, x1, y1)
    return []

def _handle_single_erase(gx, gy, grid):
    if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT and grid[gy][gx] is not None:
        return (gx, gy)
    return None

def _handle_pipette_select(mx, my, camera_offset, CELL_SIZE, panel_x, panel_y, panel_width, panel_height, grid):
    gx = int((mx - camera_offset[0]) // CELL_SIZE)
    gy = int((my - camera_offset[1]) // CELL_SIZE)
    over_panel = panel_x <= mx <= panel_x + panel_width and panel_y <= my <= panel_y + panel_height
    if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
        entity = grid[gy][gx]
        if entity is not None:
            # ENTITY_CHOICES removed, so pipette select is now a no-op or could be replaced with new logic
            return None, None
    return None, None

def handle_construction_panel_selection(event, panel_x, panel_y, panel_width, panel_height, selected_index, selected_entity_type, camera_offset, CELL_SIZE, GRID_WIDTH, GRID_HEIGHT, grid, last_game_click=None, last_game_right_click=None):
    placed_entity = None
    removed_coords = None
    line_entities = []
    erase_line_coords = []
    shift_held = pygame.key.get_mods() & pygame.KMOD_SHIFT
    idx = get_construction_panel_key(event)
    if idx is not None:
        if selected_index == idx:
            selected_index = None
            selected_entity_type = None
        else:
            selected_index = idx
            # ENTITY_CHOICES removed, directly use index for selection
            selected_entity_type = None  # Reset entity type on index change
    if event.type == pygame.MOUSEBUTTONDOWN:
        mx, my = pygame.mouse.get_pos()
        screen = pygame.display.get_surface()
        gx = int((mx - camera_offset[0]) // CELL_SIZE)
        gy = int((my - camera_offset[1]) // CELL_SIZE)
        over_panel = panel_x <= mx <= panel_x + panel_width and panel_y <= my <= panel_y + panel_height
        if event.button == 1:
            if over_panel:
                pass  # Do nothing when clicking the panel
            elif selected_entity_type is not None:
                prev_game_click = last_game_click
                last_game_click = (gx, gy)
                line_entities = _handle_line_build(prev_game_click, gx, gy, shift_held, selected_entity_type, grid)
                if line_entities:
                    audio.play_build_sound()
                elif not shift_held:
                    placed_entity = handle_single_left_click_build(gx, gy, selected_entity_type, grid)
                    if placed_entity:
                        audio.play_build_sound()
        elif event.button == 3:
            selected_index = None
            selected_entity_type = None
            prev_game_right_click = last_game_right_click
            last_game_right_click = (gx, gy)
            erase_line_coords = _handle_line_erase(prev_game_right_click, gx, gy, shift_held)
            if erase_line_coords:
                audio.play_build_sound()
            elif not shift_held:
                mx, my = pygame.mouse.get_pos()
                screen = pygame.display.get_surface()
                gx = int((mx - camera_offset[0]) // CELL_SIZE)
                gy = int((my - camera_offset[1]) // CELL_SIZE)
                over_panel = panel_x <= mx <= panel_x + panel_width and panel_y <= my <= panel_y + panel_height
                removed_coords = _handle_single_erase(gx, gy, grid)
                if removed_coords:
                    audio.play_build_sound()
    if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
        mx, my = pygame.mouse.get_pos()
        screen = pygame.display.get_surface()
        selected_index, selected_entity_type = _handle_pipette_select(mx, my, camera_offset, CELL_SIZE, panel_x, panel_y, panel_width, panel_height, grid)
    return selected_index, selected_entity_type, placed_entity, removed_coords, line_entities, last_game_click, erase_line_coords, last_game_right_click

class CameraDrag:
    def __init__(self):
        self.dragging = False
        self.last_mouse_pos = None
        self.button = 2  # Use middle mouse button for drag
        self.left_drag_enabled = False
        self.wsad_step = 25
        self._block_next_drag = False  # Initialize the block flag

    def handle_event(self, event, camera_offset, entity_preview_active=False, entity_held=False, grid=None, cell_size=None, GRID_SIZE=None):
        # Prevent camera drag if an entity is being held for placement
        if entity_preview_active or entity_held:
            self.dragging = False  # Always cancel drag if entity is held
            self.last_mouse_pos = None
            self._block_next_drag = True  # Block drag on next mouse up/down
            return camera_offset
        # Only allow drag with middle mouse button, and only if not right mouse button
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == self.button and pygame.mouse.get_pressed()[2] == 0:  # right button not pressed
                if self._block_next_drag:
                    self._block_next_drag = False
                    return camera_offset  # Ignore this drag start
                self.dragging = True
                self.last_mouse_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == self.button:
                self.dragging = False
                self.last_mouse_pos = None
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # If right mouse button is pressed, cancel drag
            if pygame.mouse.get_pressed()[2]:
                self.dragging = False
                self.last_mouse_pos = None
                return camera_offset
            mx, my = event.pos
            lx, ly = self.last_mouse_pos
            camera_offset[0] += mx - lx
            camera_offset[1] += my - ly
            self.last_mouse_pos = event.pos
        return camera_offset

    def handle_wsad(self, camera_offset, step=None):
        if step is None:
            step = self.wsad_step
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            camera_offset[1] += step
        if keys[pygame.K_s]:
            camera_offset[1] -= step
        if keys[pygame.K_a]:
            camera_offset[0] += step
        if keys[pygame.K_d]:
            camera_offset[0] -= step
        return camera_offset
    
class PaintBrush:
    def __init__(self):
        self.active = False
        self.button = 1
        self.erase_active = False
        self.erase_button = 3

    def _get_grid_coords(self, camera_offset, CELL_SIZE):
        mx, my = pygame.mouse.get_pos()
        return int((mx - camera_offset[0]) // CELL_SIZE), int((my - camera_offset[1]) // CELL_SIZE)

    def handle_event(self, event, selected_entity_type, camera_offset, CELL_SIZE, grid):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            screen = pygame.display.get_surface()
            if screen and my > screen.get_height() * 0.8:
                return None
            if event.button == self.button and selected_entity_type is not None:
                self.active = True
            elif event.button == self.erase_button:
                self.erase_active = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == self.button:
                self.active = False
            elif event.button == self.erase_button:
                self.erase_active = False
        elif event.type == pygame.MOUSEMOTION:
            mx, my = pygame.mouse.get_pos()
            screen = pygame.display.get_surface()
            if screen and my > screen.get_height() * 0.8:
                return None
            gx, gy = self._get_grid_coords(camera_offset, CELL_SIZE)
            if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                if self.active and selected_entity_type is not None and grid[gy][gx] is None:
                    audio.play_build_sound()  # Play sound for paintbrush build
                    return gx, gy, selected_entity_type(gx, gy), False
                if self.erase_active and grid[gy][gx] is not None:
                    audio.play_build_sound()  # Play sound for paintbrush erase
                    return gx, gy, None, True
        return None

    def handle_continuous_paint(self, selected_entity_type, camera_offset, CELL_SIZE, grid):
        mx, my = pygame.mouse.get_pos()
        screen = pygame.display.get_surface()
        if screen and my > screen.get_height() * 0.8:
            return None
        if self.active and selected_entity_type is not None:
            gx, gy = self._get_grid_coords(camera_offset, CELL_SIZE)
            if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT and grid[gy][gx] is None:
                audio.play_build_sound()  # Play sound for paintbrush build
                return gx, gy, selected_entity_type(gx, gy), False
        if self.erase_active:
            gx, gy = self._get_grid_coords(camera_offset, CELL_SIZE)
            if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT and grid[gy][gx] is not None:
                audio.play_build_sound()  # Play sound for paintbrush erase
                return gx, gy, None, True
        return None
        
def handle_entity_pickup(event, selected_index, selected_entity_type, grid, entity_states, remove_entity_fn, place_entity_fn, camera_offset, cell_size):
    from game_core.config import GRID_WIDTH, GRID_HEIGHT
    grid_changed = False
    if selected_index is not None:
        return selected_index, selected_entity_type, grid_changed
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        mx, my = pygame.mouse.get_pos()
        screen = pygame.display.get_surface()
        # Only block if not over construction panel
        panel_x, panel_y, panel_width, panel_height = 0, 0, 0, 0
        try:
            from game_ui.construction_panel import get_construction_panel_size
            panel_x, panel_y, panel_width, panel_height = get_construction_panel_size(screen.get_width(), screen.get_height())
        except Exception:
            pass
        over_panel = panel_x <= mx <= panel_x + panel_width and panel_y <= my <= panel_y + panel_height
        if screen and my > screen.get_height() * 0.8 and not over_panel:
            return selected_index, selected_entity_type, grid_changed  # Prevent operation in bottom 20% unless over panel
        gx = int((mx - camera_offset[0]) // cell_size)
        gy = int((my - camera_offset[1]) // cell_size)
        if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
            if selected_entity_type is None and grid[gy][gx] is not None:
                entity = grid[gy][gx]
                # Removed ENTITY_CHOICES loop, directly use entity class
                selected_entity_type = entity.__class__
                selected_index = None
                remove_entity_fn(grid, entity_states, gx, gy)
                audio.play_build_sound()  # Play sound for pickup remove
                grid_changed = True
                # --- Fix: allow immediate camera drag after pickup ---
                try:
                    from game_core.controls import CameraDrag
                    if hasattr(CameraDrag, '_block_next_drag'):
                        CameraDrag._block_next_drag = False
                except Exception:
                    pass
                return selected_index, selected_entity_type, grid_changed
            elif selected_entity_type is not None and grid[gy][gx] is None:
                entity = selected_entity_type(gx, gy)
                if hasattr(entity, 'load_icon'):
                    entity.load_icon()
                place_entity_fn(grid, entity_states, entity)
                selected_index = None
                selected_entity_type = None
                audio.play_build_sound()  # Play sound for pickup place
                grid_changed = True
                # --- Fix: allow immediate camera drag after place ---
                try:
                    from game_core.controls import CameraDrag
                    if hasattr(CameraDrag, '_block_next_drag'):
                        CameraDrag._block_next_drag = False
                except Exception:
                    pass
                return selected_index, selected_entity_type, grid_changed
    return selected_index, selected_entity_type, grid_changed

def line_build(x0, y0, x1, y1, grid, entity_class):
    """Return a list of entities to build along a line from (x0, y0) to (x1, y1)."""
    line_entities = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    x, y = x0, y0
    while True:
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT and grid[y][x] is None:
            line_entities.append(entity_class(x, y))
        if (x, y) == (x1, y1):
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy
    return line_entities

def line_deconstruct(x0, y0, x1, y1):
    """Return a list of (x, y) coordinates to deconstruct along a line from (x0, y0) to (x1, y1)."""
    erase_line_coords = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    x, y = x0, y0
    while True:
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            erase_line_coords.append((x, y))
        if (x, y) == (x1, y1):
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy
    return erase_line_coords

def handle_event(event, state, remove_entity, place_entity):
    grid_changed = False
    # Handle 1-9 key selection for entity buttons
    idx = get_construction_panel_key(event)
    if idx is not None:
        # Only update if the index is in range of current entity buttons
        entity_buttons = state.get('panel_btn_rects', {}).get('item', [])
        if 0 <= idx < len(entity_buttons):
            # Toggle selection if already selected
            if state.get('selected_item', None) == idx:
                state['selected_item'] = None
            else:
                state['selected_item'] = idx
            return None, grid_changed
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        mx, my = pygame.mouse.get_pos()
        panel_btn_rects = state.get('panel_btn_rects', {})
        # Section buttons
        for idx, button in enumerate(panel_btn_rects.get('section', [])):
            if button.rect.collidepoint(mx, my):
                state['selected_section'] = idx
                state['selected_item'] = None
                return None, grid_changed
        # Item buttons
        for idx, button in enumerate(panel_btn_rects.get('item', [])):
            if button.rect.collidepoint(mx, my):
                # Deselect if already selected
                if state.get('selected_item', None) == idx:
                    state['selected_item'] = None
                else:
                    state['selected_item'] = idx
                return None, grid_changed
    testing_layout.handle_testing_layout(event, state['grid'], state['entity_states'], state['GRID_WIDTH'], state['GRID_HEIGHT'])
    global_result = handle_global_controls(event, grid=state['grid'], entity_states=state['entity_states'])
    if global_result == 'exit' or event.type == pygame.QUIT:
        return 'exit', grid_changed
    if global_result == 'cleared':
        return None, True
    state['selected_index'], state['selected_entity_type'], pickup_grid_changed = handle_entity_pickup(
        event, state['selected_index'], state['selected_entity_type'], state['grid'], state['entity_states'], remove_entity, place_entity, state['camera_offset'], state['cell_size']
    )
    if pickup_grid_changed:
        return None, True
    entity_preview_active = state['selected_entity_type'] is not None
    state['camera_offset'] = state['camera_drag'].handle_event(event, state['camera_offset'], entity_preview_active)
    args = (event, None, None, None, None, state['selected_index'], state['selected_entity_type'], state['camera_offset'], state['cell_size'], state['GRID_WIDTH'], state['GRID_HEIGHT'], state['grid'], state.get('line_start'), state.get('erase_line_start'))
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

def handle_single_left_click_build(gx, gy, selected_entity_type, grid):
    """
    Handles single left-click construction logic: attempts to place an entity of selected_entity_type at (gx, gy).
    Returns the placed entity if successful, else None.
    """
    if (
        selected_entity_type is not None
        and 0 <= gx < GRID_WIDTH
        and 0 <= gy < GRID_HEIGHT
        and grid[gy][gx] is None
    ):
        entity = selected_entity_type(gx, gy)
        if hasattr(entity, 'load_icon'):
            entity.load_icon()
        return entity
    return None
