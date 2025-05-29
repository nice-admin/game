# game_core/controls.py
import pygame
import game_other.audio as audio
from game_core.config import GRID_WIDTH, GRID_HEIGHT
# --- Merged from input_events.py ---
import game_other.testing_layout as testing_layout

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
        screen = pygame.display.get_surface()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if screen and my > screen.get_height() * 0.8:
                return None
            if event.button == self.button and selected_entity_type is not None:
                self.active = True
                # Paint immediately on click
                gx, gy = self._get_grid_coords(camera_offset, CELL_SIZE)
                if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT and grid[gy][gx] is None:
                    audio.play_build_sound()
                    return gx, gy, selected_entity_type(gx, gy), False
            elif event.button == self.erase_button:
                self.erase_active = True
                # Erase immediately on click
                gx, gy = self._get_grid_coords(camera_offset, CELL_SIZE)
                if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT and grid[gy][gx] is not None:
                    audio.play_build_sound()
                    return gx, gy, None, True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == self.button:
                self.active = False
            elif event.button == self.erase_button:
                self.erase_active = False
        elif event.type == pygame.MOUSEMOTION:
            mx, my = pygame.mouse.get_pos()
            if screen and my > screen.get_height() * 0.8:
                return None
            gx, gy = self._get_grid_coords(camera_offset, CELL_SIZE)
            if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                if self.active and selected_entity_type is not None and grid[gy][gx] is None:
                    audio.play_build_sound()
                    return gx, gy, selected_entity_type(gx, gy), False
                if self.erase_active and grid[gy][gx] is not None:
                    audio.play_build_sound()
                    return gx, gy, None, True
        return None

    def handle_continuous_paint(self, selected_entity_type, camera_offset, CELL_SIZE, grid):
        # This method can be used for continuous painting in the main loop if needed
        mx, my = pygame.mouse.get_pos()
        screen = pygame.display.get_surface()
        if screen and my > screen.get_height() * 0.8:
            return None
        if self.active and selected_entity_type is not None:
            gx, gy = self._get_grid_coords(camera_offset, CELL_SIZE)
            if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT and grid[gy][gx] is None:
                audio.play_build_sound()
                return gx, gy, selected_entity_type(gx, gy), False
        if self.erase_active:
            gx, gy = self._get_grid_coords(camera_offset, CELL_SIZE)
            if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT and grid[gy][gx] is not None:
                audio.play_build_sound()
                return gx, gy, None, True
        return None
        
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

class GameControls:
    def __init__(self):
        self.selected_item = None
        self.selected_section = None
        self.paint_brush = PaintBrush()
        self.camera_drag = CameraDrag()
        # Add more state as needed

    def handle_event(self, event, state, remove_entity, place_entity):
        grid_changed = False
        idx = keybinds(event)
        if isinstance(idx, int):
            entity_buttons = state.get('panel_btn_rects', {}).get('item', [])
            if 0 <= idx < len(entity_buttons):
                if self.selected_item == idx:
                    self.selected_item = None
                else:
                    self.selected_item = idx
                state['selected_item'] = self.selected_item
                return None, grid_changed
        # PaintBrush drag-to-paint/erase logic
        paint_brush = self.paint_brush
        selected_item = self.selected_item
        panel_btn_rects = state.get('panel_btn_rects', {})
        entity_buttons = panel_btn_rects.get('item', [])
        entity_class = None
        if selected_item is not None and 0 <= selected_item < len(entity_buttons):
            entity_btn = entity_buttons[selected_item]
            entity_class = getattr(entity_btn, 'entity_class', None)
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
                    return None, grid_changed
            # Item buttons
            for idx, button in enumerate(panel_btn_rects.get('item', [])):
                if button.rect.collidepoint(mx, my):
                    # Deselect if already selected
                    if self.selected_item == idx:
                        self.selected_item = None
                    else:
                        self.selected_item = idx
                    state['selected_item'] = self.selected_item
                    return None, grid_changed
            # Handle left-click construction
            if self.left_click_construction(event, state, place_entity):
                return None, True
        # Handle right-click deselect
        if self.right_click_deselect(event, state):
            return None, grid_changed
        # Handle right-click deconstruction
        if self.right_click_deconstruction(event, state, remove_entity):
            return None, True
        # Testing layout (leave as is, not migrated)
        testing_layout.handle_testing_layout(event, state['grid'], state['entity_states'], state['GRID_WIDTH'], state['GRID_HEIGHT'])
        global_result = keybinds(event, grid=state['grid'], entity_states=state['entity_states'])
        if global_result == 'exit' or event.type == pygame.QUIT:
            return 'exit', grid_changed
        if global_result == 'cleared':
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
            selected_item = self.selected_item
            panel_btn_rects = state.get('panel_btn_rects', {})
            entity_buttons = panel_btn_rects.get('item', [])
            if selected_item is not None and 0 <= selected_item < len(entity_buttons):
                entity_btn = entity_buttons[selected_item]
                entity_class = getattr(entity_btn, 'entity_class', None)
                if entity_class is not None:
                    mx, my = pygame.mouse.get_pos()
                    camera_offset = state['camera_offset']
                    cell_size = state['cell_size']
                    gx = int((mx - camera_offset[0]) // cell_size)
                    gy = int((my - camera_offset[1]) // cell_size)
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
            if self.selected_item is not None:
                self.selected_item = None
                state['selected_item'] = None
                return True
        return False

    def right_click_deconstruction(self, event, state, remove_entity):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if self.selected_item is None:
                mx, my = pygame.mouse.get_pos()
                camera_offset = state['camera_offset']
                cell_size = state['cell_size']
                gx = int((mx - camera_offset[0]) // cell_size)
                gy = int((my - camera_offset[1]) // cell_size)
                grid = state['grid']
                entity_states = state['entity_states']
                if 0 <= gx < state['GRID_WIDTH'] and 0 <= gy < state['GRID_HEIGHT']:
                    if grid[gy][gx] is not None:
                        remove_entity(grid, entity_states, gx, gy)
                        return True
        return False
