import pygame
import math

_border_cache = {}

def draw_stylish_border(surface, rect, color, width=3, border_radius=6, corner_darkness=1.0, edge_brightness=0.5):
    # Draw the base border (for anti-aliasing and fallback)
    pygame.draw.rect(surface, color, rect, width=width, border_radius=border_radius)
    # Create a mask for the border
    border_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(border_surf, (0,0,0,0), border_surf.get_rect(), border_radius=border_radius)
    pygame.draw.rect(border_surf, (255,255,255,255), border_surf.get_rect(), width=width, border_radius=border_radius)
    arr = pygame.surfarray.pixels_alpha(border_surf)
    w, h = rect.width, rect.height
    for y in range(h):
        for x in range(w):
            if arr[x, y] > 0:
                # Distance to nearest corner
                dist_tl = math.hypot(x, y)
                dist_tr = math.hypot(w-x-1, y)
                dist_bl = math.hypot(x, h-y-1)
                dist_br = math.hypot(w-x-1, h-y-1)
                min_dist = min(dist_tl, dist_tr, dist_bl, dist_br)
                # Distance to nearest edge center from this corner
                edge_center_dists = [
                    math.hypot(w//2, 0),  # top
                    math.hypot(0, h//2),  # left
                    math.hypot(w//2, h-1),  # bottom
                    math.hypot(w-1, h//2)   # right
                ]
                max_dist = min(edge_center_dists)
                t = min(min_dist / max_dist, 1.0)
                brightness = corner_darkness + (edge_brightness - corner_darkness) * t
                arr[x, y] = int(arr[x, y] * brightness)
    del arr
    # Tint the border to the desired color
    tint = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    tint.fill(color)
    border_surf.blit(tint, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
    surface.blit(border_surf, rect.topleft, special_flags=pygame.BLEND_PREMULTIPLIED)

def get_baked_stylish_border(size, color, width=3, border_radius=6, corner_darkness=1.0, edge_brightness=0.5):
    key = (size, color, width, border_radius, corner_darkness, edge_brightness)
    if key in _border_cache:
        return _border_cache[key]
    surf = pygame.Surface(size, pygame.SRCALPHA)
    rect = pygame.Rect(0, 0, size[0], size[1])
    draw_stylish_border(surf, rect, color, width, border_radius, corner_darkness, edge_brightness)
    _border_cache[key] = surf
    return surf
