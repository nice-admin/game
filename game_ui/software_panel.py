import pygame
import math
from game_core.config import UI_BG1_COL

SOFTWARE_BUTTON_SIZE = 70

class SoftwareButton:
    def __init__(self, center, size=40, color=(100, 150, 255), rotation_deg=0):
        self.center = center
        self.size = size
        self.color = color
        self.rotation_rad = math.radians(rotation_deg)

    def get_hexagon_points(self):
        x, y = self.center
        s = self.size
        points = [
            (x + s * math.cos(self.rotation_rad + a), y + s * math.sin(self.rotation_rad + a))
            for a in [i * math.pi / 3 for i in range(6)]
        ]
        return points

    def draw(self, surface):
        points = self.get_hexagon_points()
        pygame.draw.polygon(surface, self.color, points)

def draw_software_buttons(surface, origin=(100, 100), size=40, color=UI_BG1_COL):
    x0, y0 = origin
    spacing = 2
    dx = size * math.sqrt(3) + spacing
    dy = size * 1.5 + spacing / 2
    btn1 = SoftwareButton((x0, y0 + dy), size, color, rotation_deg=30)
    btn2 = SoftwareButton((x0 + dx, y0 + dy), size, color, rotation_deg=30)
    btn3 = SoftwareButton((x0 + dx / 2, y0), size, color, rotation_deg=30)
    for btn in [btn1, btn2, btn3]:
        btn.draw(surface)

def draw_software_panel(surface, size=SOFTWARE_BUTTON_SIZE, color=UI_BG1_COL, margin_ratio=0.05):
    surf_w, surf_h = surface.get_width(), surface.get_height()
    spacing = 2
    dx = size * math.sqrt(3) + spacing
    dy = size * 1.5 + spacing / 2
    group_height = dy * 2
    group_width = dx
    # Place from left edge instead of right
    x = int(surf_w * margin_ratio)
    y = int(surf_h * (1 - margin_ratio*0.3) - group_height)
    btn1 = SoftwareButton((x, y + dy), size, color, rotation_deg=30)
    btn2 = SoftwareButton((x + dx, y + dy), size, color, rotation_deg=30)
    btn3 = SoftwareButton((x + dx / 2, y), size, color, rotation_deg=30)
    for btn in [btn1, btn2, btn3]:
        btn.draw(surface)
