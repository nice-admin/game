# game_core/controls.py
import pygame
import game_other.audio as audio
from game_core.config import GRID_WIDTH, GRID_HEIGHT
from game_core.game_state import GameState
# --- Merged from input_events.py ---
import game_other.testing_layout as testing_layout

def keybinds(event, grid=None, entity_states=None):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            return 'exit'
        if event.key == pygame.K_DELETE:
            if grid is not None and entity_states is not None:
                for y, row in enumerate(grid):
                    for x, entity in enumerate(row):
                        if entity is not None:
                            entity_states.remove_entity_at(x, y)
                            row[x] = None
                return 'cleared'
        if pygame.K_1 <= event.key <= pygame.K_9:
            return event.key - pygame.K_1
    return None

def line_build(x0, y0, x1, y1, grid, entity_class):
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

def line_deconstruct(x0, y0, x1, y1, grid):
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
    
def mouse_to_grid(camera_offset, cell_size):
    """Convert mouse position to grid coordinates."""
    mx, my = pygame.mouse.get_pos()
    gx = int((mx - camera_offset[0]) // cell_size)
    gy = int((my - camera_offset[1]) // cell_size)
    return gx, gy

class PaintBrush:
    def __init__(self):
        self.active = False
        self.button = 1
        self.erase_active = False
        self.erase_button = 3

    def handle_event(self, event, selected_entity_type, camera_offset, cell_size, grid):
        """Handle painting and erasing entities on the grid."""
        screen = pygame.display.get_surface()
        mx, my = pygame.mouse.get_pos()
        if screen and my > screen.get_height() * 0.8:
            return None
        gx, gy = mouse_to_grid(camera_offset, cell_size)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == self.button and selected_entity_type is not None:
                self.active = True
                if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT and grid[gy][gx] is None:
                    audio.play_build_sound()
                    return gx, gy, selected_entity_type(gx, gy), False
            elif event.button == self.erase_button:
                self.erase_active = True
                if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT and grid[gy][gx] is not None:
                    audio.play_build_sound()
                    return gx, gy, None, True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == self.button:
                self.active = False
            elif event.button == self.erase_button:
                self.erase_active = False
        elif event.type == pygame.MOUSEMOTION:
            if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                if self.active and selected_entity_type is not None and grid[gy][gx] is None:
                    audio.play_build_sound()
                    return gx, gy, selected_entity_type(gx, gy), False
                if self.erase_active and grid[gy][gx] is not None:
                    audio.play_build_sound()
                    return gx, gy, None, True
        return None

class GameControls:
    def __init__(self):
        self.selected_item = None
        self.selected_section = None
        self.paint_brush = PaintBrush()
        self.camera_drag = CameraDrag()
        self.line_starting_position = None  # Always track last clicked cell
        self.just_changed_section = False  # Track if section was just changed


    def pipette(self, state):
        """Set the current construction class to the entity under the mouse cursor."""
        gx, gy = mouse_to_grid(state['camera_offset'], state['cell_size'])
        grid = state['grid']
        if 0 <= gx < state['GRID_WIDTH'] and 0 <= gy < state['GRID_HEIGHT']:
            entity = grid[gy][gx]
            if entity is not None:
                panel_btn_rects = state.get('panel_btn_rects', {})
                entity_buttons = panel_btn_rects.get('item', [])
                for idx, button in enumerate(entity_buttons):
                    if hasattr(button, 'entity_class') and type(entity) == button.entity_class:
                        self.selected_item = idx
                        state['selected_item'] = idx
                        GameState().current_construction_class = button.entity_class
                        return
                self.selected_item = None
                state['selected_item'] = None
                GameState().current_construction_class = type(entity)
            else:
                self.selected_item = None
                state['selected_item'] = None
                GameState().current_construction_class = None

    def handle_line_action(self, event, state, remove_entity, place_entity, gx, gy):
        """Handle shift+click line build/deconstruct logic."""
        if (pygame.key.get_mods() & pygame.KMOD_SHIFT) and self.line_starting_position is not None and (gx, gy) != self.line_starting_position:
            start = self.line_starting_position
            if event.button == 1:  # Shift + Left Click: Line Build
                entity_class = GameState().current_construction_class
                if entity_class is not None:
                    for e in line_build(start[0], start[1], gx, gy, state['grid'], entity_class):
                        if hasattr(e, 'load_icon'):
                            e.load_icon()
                        place_entity(state['grid'], state['entity_states'], e)
                        if hasattr(e, 'on_built'):
                            e.on_built()
                    self.line_starting_position = (gx, gy)
                    return True
            elif event.button == 3:  # Shift + Right Click: Line Deconstruct
                for x, y in line_deconstruct(start[0], start[1], gx, gy, state['grid']):
                    if state['grid'][y][x] is not None:
                        remove_entity(state['grid'], state['entity_states'], x, y)
                self.line_starting_position = (gx, gy)
                return True
        return False

    def handle_event(self, event, state, remove_entity, place_entity):
        """Main event handler for all game controls."""
        grid_changed = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            gx, gy = mouse_to_grid(state['camera_offset'], state['cell_size'])
            grid = state['grid']
            if 0 <= gx < state['GRID_WIDTH'] and 0 <= gy < state['GRID_HEIGHT']:
                if self.handle_line_action(event, state, remove_entity, place_entity, gx, gy):
                    return None, True
                self.line_starting_position = (gx, gy)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            self.pipette(state)
            return None, grid_changed
        idx = keybinds(event)
        if isinstance(idx, int):
            entity_buttons = state.get('panel_btn_rects', {}).get('item', [])
            if 0 <= idx < len(entity_buttons):
                # If section was just changed, always select the entity
                if self.just_changed_section:
                    self.selected_item = idx
                    entity_btn = entity_buttons[idx]
                    GameState().current_construction_class = getattr(entity_btn, 'entity_class', None)
                    self.just_changed_section = False
                else:
                    if self.selected_item == idx:
                        self.selected_item = None
                        GameState().current_construction_class = None
                    else:
                        self.selected_item = idx
                        entity_btn = entity_buttons[idx]
                        GameState().current_construction_class = getattr(entity_btn, 'entity_class', None)
                state['selected_item'] = self.selected_item
                return None, grid_changed
        # PaintBrush drag-to-paint/erase logic
        paint_brush = self.paint_brush
        entity_class = GameState().current_construction_class
        paint_result = paint_brush.handle_event(
            event,
            entity_class,
            state['camera_offset'],
            state['cell_size'],
            state['grid']
        )
        if paint_result:
            gx, gy, entity, erase = paint_result
            if erase:
                if state['grid'][gy][gx] is not None:
                    remove_entity(state['grid'], state['entity_states'], gx, gy)
                    return None, True
            else:
                if state['grid'][gy][gx] is None and entity is not None:
                    # Only clear current_construction_class if it was set by pickup feature
                    if getattr(self, '_pickup_mode', False):
                        place_entity(state['grid'], state['entity_states'], entity)
                        if hasattr(entity, 'on_built'):
                            entity.on_built()
                        if hasattr(entity, 'update'):
                            entity.update(state['grid'])
                        GameState().current_construction_class = None
                        self._pickup_mode = False
                        return None, True
                    else:
                        place_entity(state['grid'], state['entity_states'], entity)
                        if hasattr(entity, 'on_built'):
                            entity.on_built()
                        if hasattr(entity, 'update'):
                            entity.update(state['grid'])
                        return None, True
        # Section and item button clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            panel_btn_rects = state.get('panel_btn_rects', {})
            # Section buttons
            for idx, button in enumerate(panel_btn_rects.get('section', [])):
                if button.rect.collidepoint(mx, my):
                    self.selected_section = idx
                    self.selected_item = None
                    state['selected_section'] = self.selected_section
                    state['selected_item'] = self.selected_item
                    GameState().current_construction_class = None
                    return None, grid_changed
            # Item buttons
            for idx, button in enumerate(panel_btn_rects.get('item', [])):
                if button.rect.collidepoint(mx, my):
                    # Deselect if already selected
                    if self.selected_item == idx:
                        self.selected_item = None
                        GameState().current_construction_class = None
                    else:
                        self.selected_item = idx
                        GameState().current_construction_class = getattr(button, 'entity_class', None)
                    state['selected_item'] = self.selected_item
                    return None, grid_changed
            # Handle left-click construction
            if self.left_click_construction(event, state, place_entity):
                return None, True
            # --- NEW: Left click on entity to pick up and move ---
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                gx, gy = mouse_to_grid(state['camera_offset'], state['cell_size'])
                grid = state['grid']
                entity_states = state['entity_states']
                if 0 <= gx < state['GRID_WIDTH'] and 0 <= gy < state['GRID_HEIGHT']:
                    # Only if not holding any entity
                    if GameState().current_construction_class is None and grid[gy][gx] is not None:
                        entity = grid[gy][gx]
                        remove_entity(grid, entity_states, gx, gy)
                        GameState().current_construction_class = type(entity)
                        self.selected_item = None
                        state['selected_item'] = None
                        self._pickup_mode = True  # Mark that next placement should clear
                        return None, True
        # Handle right-click deselect
        if self.right_click_deselect(event, state):
            GameState().current_construction_class = None
            return None, grid_changed
        # Handle right-click deconstruction
        if self.right_click_deconstruction(event, state, remove_entity):
            GameState().current_construction_class = None
            return None, True
        # Testing layout (leave as is, not migrated)
        testing_layout.handle_testing_layout(event, state['grid'], state['entity_states'], state['GRID_WIDTH'], state['GRID_HEIGHT'])
        global_result = keybinds(event, grid=state['grid'], entity_states=state['entity_states'])
        if global_result == 'exit' or event.type == pygame.QUIT:
            return 'exit', grid_changed
        if global_result == 'cleared':
            GameState().current_construction_class = None
            return None, True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SEMICOLON:
            from game_ui.hidden_info_panel import handle_panel_toggle_event
            from game_ui.profiler_panel import handle_profiler_panel_toggle
            handle_panel_toggle_event(event)
            handle_profiler_panel_toggle()
            return None, grid_changed
        return None, grid_changed

    def left_click_construction(self, event, state, place_entity):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            entity_class = GameState().current_construction_class
            if entity_class is not None:
                gx, gy = mouse_to_grid(state['camera_offset'], state['cell_size'])
                grid = state['grid']
                entity_states = state['entity_states']
                if 0 <= gx < state['GRID_WIDTH'] and 0 <= gy < state['GRID_HEIGHT'] and grid[gy][gx] is None:
                    entity = entity_class(gx, gy)
                    if hasattr(entity, 'load_icon'):
                        entity.load_icon()
                    place_entity(grid, entity_states, entity)
                    if hasattr(entity, 'on_built'):
                        entity.on_built()
                    if hasattr(entity, 'update'):
                        entity.update(grid)
                    return True
        return False

    def right_click_deselect(self, event, state):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if self.selected_item is not None or GameState().current_construction_class is not None:
                self.selected_item = None
                state['selected_item'] = None
                GameState().current_construction_class = None
                return True
        return False

    def right_click_deconstruction(self, event, state, remove_entity):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if self.selected_item is None:
                gx, gy = mouse_to_grid(state['camera_offset'], state['cell_size'])
                grid = state['grid']
                entity_states = state['entity_states']
                if 0 <= gx < state['GRID_WIDTH'] and 0 <= gy < state['GRID_HEIGHT']:
                    if grid[gy][gx] is not None:
                        remove_entity(grid, entity_states, gx, gy)
                        return True
        return False
