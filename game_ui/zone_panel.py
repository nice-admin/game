import pygame
from typing import Optional
from game_core.zone_state import zone_state
from game_core.config import resource_path

ZONE_BUTTON_COLOR = (80, 180, 255)
ZONE_BUTTON_HOVER_COLOR = (120, 220, 255)
ZONE_BUTTON_BORDER_COLOR = (40, 60, 90)
ZONE_BUTTON_TEXT_COLOR = (255, 255, 255)
ZONE_BUTTON_WIDTH = 40
ZONE_BUTTON_HEIGHT = ZONE_BUTTON_WIDTH
ZONE_BUTTON_RADIUS = 5
ZONE_BUTTON_IMAGE_PATH = resource_path("data/graphics/tool_panel/zone.png")

class ZoneButton:
    WIDTH = ZONE_BUTTON_WIDTH
    HEIGHT = ZONE_BUTTON_HEIGHT
    def __init__(self, center_pos):
        self.rect = pygame.Rect(0, 0, self.WIDTH, self.HEIGHT)
        self.rect.center = center_pos
        self.tooltip_font = pygame.font.SysFont(None, 24)
        self.color = ZONE_BUTTON_COLOR
        self.hover_color = ZONE_BUTTON_HOVER_COLOR
        self.border_color = ZONE_BUTTON_BORDER_COLOR
        self.clicked = False
        try:
            self.image = pygame.transform.smoothscale(
                pygame.image.load(ZONE_BUTTON_IMAGE_PATH).convert_alpha(),
                (self.WIDTH, self.HEIGHT))
        except Exception as e:
            print(f"Failed to load button image: {e}")
            self.image = None

    def draw(self, surface: pygame.Surface, active=False):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        if self.image:
            surface.blit(self.image, self.rect)
        else:
            pygame.draw.rect(surface, self.hover_color if is_hovered else self.color, self.rect, border_radius=ZONE_BUTTON_RADIUS)
        # Draw border: green if active, else normal
        if active:
            pygame.draw.rect(surface, (0,255,0), self.rect, 4, border_radius=ZONE_BUTTON_RADIUS)
        else:
            pygame.draw.rect(surface, self.border_color, self.rect, 3, border_radius=ZONE_BUTTON_RADIUS)
        if is_hovered:
            tooltip = self.tooltip_font.render("Zone tool", True, (255,255,255))
            padding = 8
            tw, th = tooltip.get_size()
            tooltip_rect = pygame.Rect(mouse_pos[0]+16, mouse_pos[1]-th//2, tw+padding*2, th+padding)
            pygame.draw.rect(surface, (30,30,30,230), tooltip_rect, border_radius=6)
            pygame.draw.rect(surface, (80,180,255), tooltip_rect, 2, border_radius=6)
            surface.blit(tooltip, (tooltip_rect.x+padding, tooltip_rect.y+padding//2))

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.clicked = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.clicked and self.rect.collidepoint(event.pos):
                self.clicked = False
                return True
            self.clicked = False
        return False

# Singleton instance for the panel's button
_zone_button: Optional[ZoneButton] = None

# --- Zone creation state ---
_zone_creation_active = False
_zone_start = None  # type: Optional[tuple]
_zone_end = None    # type: Optional[tuple]

ZONE_MIN_W, ZONE_MIN_H = 1, 1
ZONE_MAX_W, ZONE_MAX_H = 15, 15
ZONE_COLOR = (255, 0, 255, 40)  # Transparent purple

# These must be set from the main game for correct snapping
_zone_panel_camera_offset = (0, 0)
_zone_panel_cell_size = 60
_zone_panel_grid_width = 70
_zone_panel_grid_height = 35

def set_zone_panel_grid_params(camera_offset, cell_size, grid_width, grid_height):
    global _zone_panel_camera_offset, _zone_panel_cell_size, _zone_panel_grid_width, _zone_panel_grid_height
    _zone_panel_camera_offset = camera_offset
    _zone_panel_cell_size = cell_size
    _zone_panel_grid_width = grid_width
    _zone_panel_grid_height = grid_height

def _screen_to_grid(pos):
    x, y = pos
    cx, cy = _zone_panel_camera_offset
    gx = int((x - cx) // _zone_panel_cell_size)
    gy = int((y - cy) // _zone_panel_cell_size)
    gx = max(0, min(_zone_panel_grid_width - 1, gx))
    gy = max(0, min(_zone_panel_grid_height - 1, gy))
    return gx, gy

def _grid_to_screen(gx, gy):
    cx, cy = _zone_panel_camera_offset
    x = gx * _zone_panel_cell_size + cx
    y = gy * _zone_panel_cell_size + cy
    return x, y

def _clamp_zone_end(start, end):
    sx, sy = start
    ex, ey = end
    dx = ex - sx
    dy = ey - sy
    # Clamp dx, dy to max/min allowed
    if dx >= 0:
        dx = min(dx, ZONE_MAX_W - 1)
    else:
        dx = max(dx, -(ZONE_MAX_W - 1))
    if dy >= 0:
        dy = min(dy, ZONE_MAX_H - 1)
    else:
        dy = max(dy, -(ZONE_MAX_H - 1))
    # Clamp for min size
    if abs(dx) < ZONE_MIN_W - 1:
        dx = (ZONE_MIN_W - 1) if dx >= 0 else -(ZONE_MIN_W - 1)
    if abs(dy) < ZONE_MIN_H - 1:
        dy = (ZONE_MIN_H - 1) if dy >= 0 else -(ZONE_MIN_H - 1)
    return (sx + dx, sy + dy)

current_zone_type = "zone_render"  # Default zone type

# --- NEW CODE ---
_zone_id_counter = 1  # For unique zone IDs
_last_created_zone = None  # Store last created zone for UI

def handle_zone_panel_event(event: pygame.event.Event):
    global _zone_button, _zone_creation_active, _zone_start, _zone_end, current_zone_type, _zone_id_counter, _last_created_zone
    # First, check if the button was clicked and consume the event if so
    if _zone_button is not None and _zone_button.handle_event(event):
        if _zone_creation_active:
            _zone_creation_active = False
            _zone_start = None
            _zone_end = None
        else:
            _zone_creation_active = True
            _zone_start = None
            _zone_end = None
        return True  # Do not process further for this event
    # Only allow right-click zone deletion in zone mode
    if _zone_creation_active and event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
        mx, my = event.pos
        for i, (zone_id, zx, zy, zw, zh, zone_type) in enumerate(zone_state.get_zones()):
            x, y = _grid_to_screen(zx, zy)
            w = zw * _zone_panel_cell_size
            h = zh * _zone_panel_cell_size
            rect = pygame.Rect(x, y, w, h)
            if rect.collidepoint(mx, my):
                zone_state.remove_zone_by_id(zone_id)
                return True
    if _zone_creation_active:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Prevent starting zone creation if mouse is over the button
            if _zone_button is not None and _zone_button.rect.collidepoint(event.pos):
                return True
            _zone_start = _screen_to_grid(event.pos)
            _zone_end = _zone_start
            return True  # Consume event so entity pickup doesn't happen
        elif event.type == pygame.MOUSEMOTION and _zone_start:
            raw_end = _screen_to_grid(event.pos)
            _zone_end = _clamp_zone_end(_zone_start, raw_end)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and _zone_start:
            raw_end = _screen_to_grid(event.pos)
            _zone_end = _clamp_zone_end(_zone_start, raw_end)
            gx0, gy0 = _zone_start
            gx1, gy1 = _zone_end
            left, top = min(gx0, gx1), min(gy0, gy1)
            right, bottom = max(gx0, gx1), max(gy0, gy1)
            w = max(ZONE_MIN_W, min(ZONE_MAX_W, right - left + 1))
            h = max(ZONE_MIN_H, min(ZONE_MAX_H, bottom - top + 1))
            # Clamp to grid
            if left + w > _zone_panel_grid_width:
                w = _zone_panel_grid_width - left
            if top + h > _zone_panel_grid_height:
                h = _zone_panel_grid_height - top
            # Prevent overlap with existing zones
            if not _zone_overlaps_existing(left, top, w, h):
                zone_id = _zone_id_counter
                _zone_id_counter += 1
                zone = (zone_id, left, top, w, h, current_zone_type)
                zone_state.add_zone(zone)
                _last_created_zone = zone
            # Stay in zone creation mode for continuous drawing
            _zone_creation_active = True
            _zone_start = None
            _zone_end = None
            return True
        return False
    return False

def draw_zone_panel(surface: pygame.Surface):
    """Draws the zone panel button at 10% from bottom and 20% from right (no zone rectangles)."""
    global _zone_button
    btn_x = int(surface.get_width() * 0.749)
    btn_y = int(surface.get_height() * 0.84)
    btn_center = (btn_x, btn_y)
    if _zone_button is None:
        _zone_button = ZoneButton(btn_center)
    else:
        _zone_button.rect.center = btn_center
    _zone_button.draw(surface, active=_zone_creation_active)

def draw_zones_only(surface: pygame.Surface):
    """Draws only the zone rectangles (not the button or UI)."""
    global _zone_creation_active, _zone_start, _zone_end
    # Draw existing zones
    for zone_id, zx, zy, zw, zh, zone_type in zone_state.get_zones():
        x, y = _grid_to_screen(zx, zy)
        w = zw * _zone_panel_cell_size
        h = zh * _zone_panel_cell_size
        zone_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        zone_surf.fill(ZONE_COLOR)  # In the future, use zone_type to pick color
        surface.blit(zone_surf, (x, y))
    # Draw zone being created
    if _zone_creation_active and _zone_start and _zone_end:
        gx0, gy0 = _zone_start
        gx1, gy1 = _zone_end
        left, top = min(gx0, gx1), min(gy0, gy1)
        right, bottom = max(gx0, gx1), max(gy0, gy1)
        w = max(ZONE_MIN_W, min(ZONE_MAX_W, right - left + 1))
        h = max(ZONE_MIN_H, min(ZONE_MAX_H, bottom - top + 1))
        if left + w > _zone_panel_grid_width:
            w = _zone_panel_grid_width - left
        if top + h > _zone_panel_grid_height:
            h = _zone_panel_grid_height - top
        x, y = _grid_to_screen(left, top)
        zone_surf = pygame.Surface((w * _zone_panel_cell_size, h * _zone_panel_cell_size), pygame.SRCALPHA)
        zone_surf.fill(ZONE_COLOR)
        surface.blit(zone_surf, (x, y))

def format_zone_info(zone):
    zone_id, left, top, w, h, zone_type = zone
    start = (left, top)
    end = (left + w - 1, top + h - 1)
    return f"Zone ID: {zone_id}  Type: {zone_type}  Start: {start}  End: {end}"

def draw_zone_info_overlay(surface: pygame.Surface):
    """Draws info about all zones aligned to the right, starting 15% from the top edge of the screen."""
    zones = zone_state.get_zones()
    if not zones:
        return
    info_lines = [format_zone_info(z) for z in zones]
    font = pygame.font.SysFont(None, 25)
    width = max(font.size(line)[0] for line in info_lines) + 40
    height = len(info_lines) * font.get_height() + 30
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    for i, line in enumerate(info_lines):
        text = font.render(line, True, (255, 255, 255))
        surf.blit(text, (20, 15 + i * font.get_height()))
    # Align to right, 15% from top
    x = surface.get_width() - width  # 20px from right edge
    y = int(surface.get_height() * 0.15)
    surface.blit(surf, (x, y))

def _zone_overlaps_existing(left, top, w, h):
    """Returns True if the proposed zone overlaps any existing zone."""
    return any(
        left < ex_left + ex_w and left + w > ex_left and
        top < ex_top + ex_h and top + h > ex_top
        for _, ex_left, ex_top, ex_w, ex_h, _ in zone_state.get_zones()
    )
