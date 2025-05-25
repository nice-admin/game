import pygame
from game_core import game_state
from game_core.game_settings import FONT1, BG1_COL, BORDER1_COL, TEXT1_COL

# Draws a resources panel at the top of the screen, showing all game_state variables

def draw_resources_panel(surface, font=None):
    """
    Draws a panel at the top of the screen showing resource values from game_state.py.
    The panel is 70% wide, 10% tall, horizontally centered, and at the top edge.
    Content is arranged in 2 rows and 8 columns.
    """
    w, h = surface.get_width(), surface.get_height()
    panel_width = int(w * 0.6)
    panel_height = int(h * 0.08)
    panel_x = (w - panel_width) // 2
    panel_y = 0
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    pygame.draw.rect(surface, BG1_COL, panel_rect)
    pygame.draw.rect(surface, BORDER1_COL, panel_rect, 2)

    if font is None:
        font = pygame.font.Font(FONT1, int(panel_height * 0.4))

    # Resource names and values (first row, then second row)
    resources = [
        ("Money", game_state.total_money),
        ("Power Drain", game_state.total_power_drain),
        ("Breaker Strength", game_state.total_breaker_strength),
        *[("-", "-")]*5,  # Fill to 8 columns
        ("Employees", game_state.total_employees),
        ("Risk Factor", game_state.total_risky_entities),
        *[("-", "-")]*6  # Fill to 8 columns
    ]

    col_w = panel_width // 8
    row_h = panel_height // 2
    for idx, (label, value) in enumerate(resources):
        row = idx // 8
        col = idx % 8
        text = "-" if label == "-" and value == "-" else f"{label}: {value}"
        img = font.render(text, True, TEXT1_COL)
        rect = img.get_rect(center=(panel_x + col_w * col + col_w // 2, panel_y + row_h * row + row_h // 2))
        surface.blit(img, rect)

    # Draw grid lines (vertical)
    for col in range(1, 8):
        x = panel_x + col * col_w
        pygame.draw.line(surface, BORDER1_COL, (x, panel_y), (x, panel_y + panel_height), 1)
    # Draw grid lines (horizontal)
    y = panel_y + row_h
    pygame.draw.line(surface, BORDER1_COL, (panel_x, y), (panel_x + panel_width, y), 1)
