import pygame
import math
from game_core.config import UI_BG1_COL, resource_path

SOFTWARE_BUTTON_SIZE = 70

class SoftwareButton:
    def __init__(self, center, size=40, color=(100, 150, 255), rotation_deg=0, icon_path=None):
        self.center = center
        self.size = size
        self.color = color
        self.rotation_deg = rotation_deg
        self.rotation_rad = math.radians(rotation_deg)
        self.icon = None
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

def draw_software_panel(surface, size=SOFTWARE_BUTTON_SIZE, color=UI_BG1_COL, margin_ratio=0.05, cache={}, mouse_pos=None, mouse_pressed=False):
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
            SoftwareButton(abs_btn_centers[0], size, color, rotation_deg=30, icon_path=icon_path),
            SoftwareButton(abs_btn_centers[1], size, color, rotation_deg=30, icon_path=icon_path),
            SoftwareButton(abs_btn_centers[2], size, color, rotation_deg=30, icon_path=icon_path),
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
    # Draw hover/pressed overlays only if needed
    for i, btn in enumerate(buttons):
        # Adjust mouse_pos to panel-local coordinates
        local_mouse = (mouse_pos[0] - x, mouse_pos[1] - y) if mouse_pos else None
        is_hover = local_mouse and btn.collidepoint(local_mouse)
        is_pressed = is_hover and mouse_pressed
        if is_hover or is_pressed:
            # Draw overlay at correct screen position
            btn_screen = SoftwareButton(
                (btn.center[0] + x, btn.center[1] + y), btn.size, btn.color, btn.rotation_deg, icon_path
            )
            btn_screen.icon = btn.icon  # reuse loaded icon
            btn_screen.draw(surface, highlight=is_hover, pressed=is_pressed)
            hovered_idx = i
            if mouse_pressed:
                print(f"SoftwareButton {i} clicked!")
    return buttons, hovered_idx
