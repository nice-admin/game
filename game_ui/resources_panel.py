import pygame
from game_core import game_state
from game_core.game_settings import *

DESCRIPTION_SIZE = 0.3  # Multiplier for row_h for the label
VALUE_SIZE = 0.4        # Multiplier for row_h for the value
SPACING = 0.20          # Multiplier for row_h for the gap
TOP_MARGIN = 5         # Offset in pixels for the vertical position of text in the cell

# Cache fonts globally to avoid creating them every draw call
_number_font_cache = {}
_label_font_cache = {}

def get_number_font(row_h):
    size = int(row_h * VALUE_SIZE)
    if size not in _number_font_cache:
        _number_font_cache[size] = pygame.font.Font(FONT1, size)
    return _number_font_cache[size]

def get_label_font(row_h):
    size = int(row_h * DESCRIPTION_SIZE)
    if size not in _label_font_cache:
        _label_font_cache[size] = pygame.font.Font(FONT1, size)
    return _label_font_cache[size]

def _draw_panel_block(surface, panel, cols, col_w, row_h, x, y, special_color_fn=None):
    number_font = get_number_font(row_h)
    label_font = get_label_font(row_h)
    for idx, (label, value) in enumerate(panel):
        row, col = divmod(idx, cols)
        cx = x + col * col_w + col_w // 2
        cy = y + row * row_h + row_h // 2 + TOP_MARGIN
        color = special_color_fn() if special_color_fn and label == "Power Drain" else TEXT1_COL
        label_y = cy + row_h * 0.15
        value_y = cy - row_h * SPACING
        if label != "-":
            value_is_string = isinstance(value, str) and not value.isdigit()
            value_img = label_font.render(str(value), True, color) if value_is_string else number_font.render(str(value), True, color)
            value_rect = value_img.get_rect(center=(cx, value_y))
            surface.blit(value_img, value_rect)
            label_img = label_font.render(label, True, TEXT1_COL) if label else label_font.render(" ", True, (0,0,0,0))
            label_rect = label_img.get_rect(center=(cx, label_y))
            surface.blit(label_img, label_rect)
    for col in range(1, cols):
        xline = x + col * col_w
        pygame.draw.line(surface, UI_BORDER1_COL, (xline, y), (xline, y + row_h * 2), 1)
    yline = y + row_h
    pygame.draw.line(surface, UI_BORDER1_COL, (x, yline), (x + col_w * cols, yline), 1)

def draw_general_panel(surface, panel_x, panel_y, panel_height, general_w):
    panel = [
        ("Money", game_state.total_money),
        ("Power Drain", game_state.total_power_drain),
        ("Breaker Strength", game_state.total_breaker_strength),
        ("Employees", game_state.total_employees),
        *( ("-", "-") for _ in range(6) )
    ]
    cols = 5
    col_w = general_w / cols
    row_h = panel_height / 2
    rect = pygame.Rect(round(panel_x), panel_y, round(general_w), round(panel_height))
    pygame.draw.rect(surface, UI_BG1_COL, rect)
    pygame.draw.rect(surface, UI_BORDER1_COL, rect, 2)
    def power_drain_color():
        d, s = game_state.total_power_drain, game_state.total_breaker_strength
        ratio = 0 if s > 0 and d <= s-15 else min(max((d-(s-15))/15,0),1) if s>0 else 1
        import colorsys
        r,g,b = [int(x*255) for x in colorsys.hsv_to_rgb((120*(1-ratio))/360,1,1)]
        return (r,g,b)
    _draw_panel_block(surface, panel, cols, col_w, row_h, panel_x, panel_y, special_color_fn=power_drain_color)

def draw_problems_panel(surface, panel_x, panel_y, panel_height, problems_w, col_w):
    panel = [
        ("Risk Factor", game_state.total_risky_entities),
        ("Problems", game_state.total_broken_entities),
        ("-", "-"),
        ("-", "-"),
        ("-", "-")
    ]
    cols = 3
    row_h = panel_height / 2
    rect = pygame.Rect(round(panel_x), panel_y, round(problems_w), round(panel_height))
    pygame.draw.rect(surface, UI_BG1_COL, rect)
    pygame.draw.rect(surface, UI_BORDER1_COL, rect, 2)
    _draw_panel_block(surface, panel, cols, col_w, row_h, panel_x, panel_y)

def draw_internet_panel(surface, panel_x, panel_y, panel_height, panel_w, col_w, cols=2, items=None):
    row_h = panel_height / 2
    rect = pygame.Rect(round(panel_x), panel_y, round(panel_w), round(panel_height))
    pygame.draw.rect(surface, UI_BG1_COL, rect)
    pygame.draw.rect(surface, UI_BORDER1_COL, rect, 2)
    # Draw horizontal splitting line between rows
    yline = panel_y + row_h
    pygame.draw.line(surface, UI_BORDER1_COL, (panel_x, yline), (panel_x + panel_w, yline), 1)
    # Draw vertical separation lines between columns
    for col in range(1, cols):
        xline = panel_x + col * col_w
        pygame.draw.line(surface, UI_BORDER1_COL, (xline, panel_y), (xline, panel_y + panel_height), 1)
    # Ensure items are ordered so that wifi is below internet (row 1, col 0)
    # Fill all 2x2 cells: (0,0)=internet, (0,1)=Running, (1,0)=wifi, (1,1)=storage
    items = [
        ("data/graphics/internet.png", "Connected"),   # col 0, row 0
        ("data/graphics/nas.png", "Running"),                             # col 1, row 0 (no icon, just text)
        ("data/graphics/wifi.png", "Connected"),       # col 0, row 1
        ("data/graphics/storage.png", "15 / 25 TB")                       # col 1, row 1 (no icon, just text)
    ]
    for idx, (icon_path, label) in enumerate(items):
        row = idx // cols
        col = idx % cols
        cell_x = panel_x + col * col_w
        cell_y = panel_y + row * row_h
        try:
            icon = pygame.image.load(icon_path).convert_alpha()
            alpha_arr = pygame.surfarray.array_alpha(icon)
            bright_green = pygame.Surface(icon.get_size(), pygame.SRCALPHA)
            bright_green.fill((0, 255, 64, 255))
            pygame.surfarray.pixels_alpha(bright_green)[:,:] = alpha_arr
            icon = bright_green
            iw, ih = icon.get_size()
            scale = min((col_w * 0.35) / iw, (row_h * 0.6) / ih)
            icon_w, icon_h = int(iw * scale), int(ih * scale)
            icon = pygame.transform.smoothscale(icon, (icon_w, icon_h))
            icon_x = cell_x + col_w * 0.10
            icon_y = cell_y + (row_h - icon_h) / 2
            surface.blit(icon, (icon_x, icon_y))
            label_font = get_label_font(row_h)
            label_img = label_font.render(label, True, TEXT1_COL)
            label_rect = label_img.get_rect()
            label_rect.x = icon_x + icon_w + col_w * 0.05
            label_rect.centery = cell_y + row_h / 2 + 1
            surface.blit(label_img, label_rect)
        except Exception:
            pass

def draw_resources_panel(surface, font=None):
    w, h = surface.get_width(), surface.get_height()
    panel_width = int(w * 0.6)
    panel_height = h * 0.08
    panel_x = (w - panel_width) // 2
    panel_y = 0
    gap = 10
    general_cols = 5
    problems_cols = 2
    general_w = panel_width * 5 / 8
    general_col_w = general_w / general_cols
    problems_col_w = general_col_w * 0.7
    problems_w = problems_col_w * problems_cols
    # Set internet_col_w and internet_w to match general_col_w (width of a cell in generals panel)
    internet_col_w = general_col_w * 0.9
    internet_panel_cols = 2
    internet_w = internet_col_w * internet_panel_cols  # Fix: make panel wide enough for all columns
    draw_general_panel(surface, panel_x, panel_y, panel_height, general_w)
    problems_panel_x = panel_x + general_w + gap
    draw_problems_panel(surface, problems_panel_x, panel_y, panel_height, problems_w, problems_col_w)
    internet_panel_x = problems_panel_x + problems_w + gap
    draw_internet_panel(surface, internet_panel_x, panel_y, panel_height, internet_w, internet_col_w, cols=internet_panel_cols)
