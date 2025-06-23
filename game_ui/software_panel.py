import pygame
import math
import time
from game_core.config import UI_BG1_COL, resource_path
from game_other.audio import play_software_select_sound

SOFTWARE_BUTTON_SIZE = 70

class Selected:
    def __init__(self, size=40, color=(0, 255, 180)):
        self.size = size
        self.color = color

    def draw(self, surface, center, rotation_deg=0):
        # Draw a hexagon with alpha fading from edge (opaque) to center (transparent),
        # but the 0 alpha is only at the very edge (outer 20%)
        steps = 16  # More steps = smoother gradient
        max_alpha = 100  # Edge alpha (0-255)
        min_alpha = 0    # Center alpha
        rotation_rad = math.radians(rotation_deg)
        s = self.size
        x, y = center
        temp_surf = pygame.Surface((s*2+4, s*2+4), pygame.SRCALPHA)
        cx, cy = s+2, s+2
        min_frac = 0.5  # 0.0 = center, 1.0 = edge; so 0.8 means fade only in outer 20%
        for i in range(steps):
            frac = 1 - i / (steps-1)  # 1 at edge, 0 at center
            # Only fade in the outer 20%
            size_frac = min_frac + (1 - min_frac) * frac  # from 0.8 to 1.0
            curr_size = s * size_frac
            # Alpha is 0 for inner 80%, fades in outer 20%
            if size_frac < min_frac:
                alpha = max_alpha
            else:
                fade_frac = (size_frac - min_frac) / (1 - min_frac)
                alpha = int(max_alpha * fade_frac + min_alpha * (1-fade_frac))
            color = (*self.color, alpha)
            points = [
                (cx + curr_size * math.cos(rotation_rad + a), cy + curr_size * math.sin(rotation_rad + a))
                for a in [j * math.pi / 3 for j in range(6)]
            ]
            pygame.draw.polygon(temp_surf, color, points)
        temp_rect = temp_surf.get_rect(center=center)
        surface.blit(temp_surf, temp_rect)

class SoftwareButton:
    def __init__(self, center, size=40, color=(100, 150, 255), rotation_deg=0, icon_path=None, desc_text=None):
        self.center = center
        self.size = size
        self.color = color
        self.rotation_deg = rotation_deg
        self.rotation_rad = math.radians(rotation_deg)
        self.icon = None
        self.desc_text = desc_text
        if icon_path:
            try:
                icon_img = pygame.image.load(resource_path(icon_path)).convert_alpha()
                # Scale icon to fit nicely inside the hexagon
                icon_size = int(self.size * 1.1)
                self.icon = pygame.transform.smoothscale(icon_img, (icon_size, icon_size))
            except Exception as e:
                print(f"Failed to load icon: {icon_path} - {e}")

    def get_hexagon_points(self):
        x, y = self.center
        s = self.size
        points = [
            (x + s * math.cos(self.rotation_rad + a), y + s * math.sin(self.rotation_rad + a))
            for a in [i * math.pi / 3 for i in range(6)]
        ]
        return points

    def collidepoint(self, point):
        # Point-in-polygon test for hexagon
        px, py = point
        points = self.get_hexagon_points()
        n = len(points)
        inside = False
        xints = 0
        p1x, p1y = points[0]
        for i in range(n+1):
            p2x, p2y = points[i % n]
            if py > min(p1y, p2y):
                if py <= max(p1y, p2y):
                    if p1y != p2y:
                        xints = (py - p1y) * (p2x - p1x) / (p2y - p1y + 1e-8) + p1x
                    if p1x == p2x or px <= xints:
                        if px <= max(p1x, p2x):
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def draw(self, surface, highlight=False, pressed=False):
        points = self.get_hexagon_points()
        draw_color = self.color
        if highlight:
            # Make the color brighter on hover
            draw_color = tuple(min(255, int(c * 1.35)) for c in self.color)
        # If pressed, offset all points by (2, 2)
        if pressed:
            points = [(x + 2, y + 2) for (x, y) in points]
        pygame.draw.polygon(surface, draw_color, points)
        # Draw icon if available, centered
        if self.icon:
            icon_rect = self.icon.get_rect(center=(self.center[0] + (2 if pressed else 0), self.center[1] + (2 if pressed else 0)))
            surface.blit(self.icon, icon_rect)


def draw_software_buttons(surface, origin=(100, 100), size=40, color=UI_BG1_COL):
    x0, y0 = origin
    spacing = 2
    dx = size * math.sqrt(3) + spacing
    dy = size * 1.5 + spacing / 2
    icon_path = "data/graphics/software_panel/c4d.png"
    btn1 = SoftwareButton((x0, y0 + dy), size, color, rotation_deg=30, icon_path=icon_path)
    btn2 = SoftwareButton((x0 + dx, y0 + dy), size, color, rotation_deg=30, icon_path=icon_path)
    btn3 = SoftwareButton((x0 + dx / 2, y0), size, color, rotation_deg=30, icon_path=icon_path)
    for btn in [btn1, btn2, btn3]:
        btn.draw(surface)

class Description:
    def __init__(self, color, width=400, height=200, duration=0.1):
        self.color = color
        self.width = width
        self.height = height
        self.duration = duration
        self.start_time = None
        self.active = False
        self.x = 0
        self.y = 0
        self.text = ""

    def start(self, x, y, text=None):
        self.start_time = time.time()
        self.active = True
        self.x = x
        self.y = y
        if text is not None:
            self.text = text

    def stop(self):
        self.active = False
        self.start_time = None

    def update_position(self, x, y):
        self.x = x
        self.y = y

    def update_text(self, text):
        self.text = text

    def draw(self, surface):
        if not self.active or self.start_time is None:
            return
        elapsed = time.time() - self.start_time
        progress = min(1.0, max(0.0, elapsed / self.duration))
        rect_w = int(self.width * progress)
        if rect_w > 0:
            pygame.draw.rect(surface, self.color, (self.x, self.y - self.height, rect_w, self.height))
            # Draw text if rectangle is at least 100px wide
            if rect_w > 100:
                font = pygame.font.SysFont(None, 28)
                text = self.text
                text_surf = font.render(text, True, (255, 255, 255))
                text_rect = text_surf.get_rect()
                text_rect.topleft = (self.x + 20, self.y - self.height + 10)
                # Only blit if at least part of the text is visible
                if text_rect.left < self.x + rect_w:
                    # Clip the text if needed
                    clip_rect = pygame.Rect(self.x, self.y - self.height, rect_w, self.height)
                    prev_clip = surface.get_clip()
                    surface.set_clip(clip_rect)
                    surface.blit(text_surf, text_rect)
                    surface.set_clip(prev_clip)

def draw_software_panel(surface, size=SOFTWARE_BUTTON_SIZE, color=UI_BG1_COL, margin_ratio=0.05, cache={}, mouse_pos=None, mouse_pressed=False, selected_idx=None):
    surf_w, surf_h = surface.get_width(), surface.get_height()
    spacing = 2
    dx = size * math.sqrt(3) + spacing
    dy = size * 1.5 + spacing / 2
    icon_path = "data/graphics/software_panel/c4d.png"
    # Calculate button centers (relative to panel)
    btn_centers = [
        (0, dy),
        (dx, dy),
        (dx / 2, 0)
    ]
    # Find bounds
    min_x = min(c[0] for c in btn_centers) - size
    max_x = max(c[0] for c in btn_centers) + size
    min_y = min(c[1] for c in btn_centers) - size
    max_y = max(c[1] for c in btn_centers) + size
    panel_w = int(max_x - min_x)
    panel_h = int(max_y - min_y)
    # Use a cache key based on size, color, icon_path
    cache_key = (size, color, icon_path)
    offset_x = -min_x
    offset_y = -min_y
    # Place 10% from left and 10% from bottom
    x = int(surf_w * 0.04)
    y = int(surf_h * 0.96) - panel_h
    # Compute absolute button centers (on main surface)
    abs_btn_centers = [
        (btn_centers[0][0] + offset_x, btn_centers[0][1] + offset_y),
        (btn_centers[1][0] + offset_x, btn_centers[1][1] + offset_y),
        (btn_centers[2][0] + offset_x, btn_centers[2][1] + offset_y),
    ]
    # --- Caching logic ---
    if 'panel_cache' not in cache or cache.get('panel_cache_key') != cache_key:
        # Bake static panel (background + buttons, no hover/press)
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        buttons = [
            SoftwareButton(abs_btn_centers[0], size, color, rotation_deg=30, icon_path="data/graphics/software_panel/houdini.png", desc_text="Houdini is versatile something"),
            SoftwareButton(abs_btn_centers[1], size, color, rotation_deg=30, icon_path="data/graphics/software_panel/blender.png", desc_text="Blender is versatile something"),
            SoftwareButton(abs_btn_centers[2], size, color, rotation_deg=30, icon_path="data/graphics/software_panel/c4d.png", desc_text="Cinema 4D is versatile something"),
        ]
        for btn in buttons:
            btn.draw(panel_surf)
        cache['panel_cache'] = panel_surf
        cache['panel_buttons'] = buttons
        cache['panel_cache_key'] = cache_key
        cache['panel_abs_btn_centers'] = abs_btn_centers
        cache['panel_rect'] = pygame.Rect(x, y, panel_w, panel_h)
    # Blit cached panel
    panel_surf = cache['panel_cache']
    panel_rect = cache['panel_rect']
    surface.blit(panel_surf, (x, y))
    buttons = cache['panel_buttons']
    hovered_idx = None
    # Animation state for unfolding rectangle
    if 'panel_anim' not in cache:
        cache['panel_anim'] = {'hovered_idx': None, 'desc': Description(UI_BG1_COL)}
    anim = cache['panel_anim']
    desc = anim['desc']
    show_desc = False
    # Track previous mouse_pressed state in cache
    prev_mouse_pressed = cache.get('prev_mouse_pressed', False)
    # Draw hover/pressed overlays only if needed
    for i, btn in enumerate(buttons):
        # Adjust mouse_pos to panel-local coordinates
        local_mouse = (mouse_pos[0] - x, mouse_pos[1] - y) if mouse_pos else None
        is_hover = local_mouse and btn.collidepoint(local_mouse)
        is_pressed = is_hover and mouse_pressed
        if is_hover or is_pressed:
            # Animation: track hover start
            desc.update_text(btn.desc_text)
            if anim['hovered_idx'] != i:
                anim['hovered_idx'] = i
                desc.start(mouse_pos[0], mouse_pos[1], text=btn.desc_text)
            else:
                desc.update_position(mouse_pos[0], mouse_pos[1])
            hovered_idx = i
            # Draw overlay at correct screen position
            btn_screen = SoftwareButton(
                (btn.center[0] + x, btn.center[1] + y), btn.size, btn.color, btn.rotation_deg, icon_path
            )
            btn_screen.icon = btn.icon  # reuse loaded icon
            btn_screen.draw(surface, highlight=is_hover, pressed=is_pressed)
            if is_hover and mouse_pos:
                show_desc = True
            if mouse_pressed:
                cache['selected_idx'] = i
                # Set software_choice in GameState singleton
                from game_core.game_state import GameState
                gs = GameState()
                if i == 2:  # C4D
                    gs.software_choice = 1
                elif i == 1:  # Blender
                    gs.software_choice = 2
                elif i == 0:  # Houdini
                    gs.software_choice = 3
                # Play software select sound only on new click
                if not prev_mouse_pressed:
                    play_software_select_sound()
                print(f"SoftwareButton {i} clicked! software_choice set to {gs.software_choice}")
        else:
            # Reset animation if not hovered
            if anim['hovered_idx'] == i:
                anim['hovered_idx'] = None
                desc.stop()
    # Update previous mouse_pressed state
    cache['prev_mouse_pressed'] = bool(mouse_pressed)
    # Draw selected fill if a button is selected
    selected = cache.get('selected')
    if selected is None or selected.size != size:
        selected = Selected(size=size, color=(0, 255, 150))
        cache['selected'] = selected
    idx = cache.get('selected_idx', None) if selected_idx is None else selected_idx
    if idx is not None and 0 <= idx < len(buttons):
        btn = buttons[idx]
        btn_center_screen = (btn.center[0] + x, btn.center[1] + y)
        selected.draw(surface, btn_center_screen, rotation_deg=btn.rotation_deg)
    # Draw description on top of everything if active
    if desc.active:
        desc.draw(surface)
    return buttons, hovered_idx, cache.get('selected_idx', None)
