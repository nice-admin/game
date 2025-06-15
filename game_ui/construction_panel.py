import pygame
import inspect
import hashlib
from game_core import entity_definitions
from game_core.entity_base import *
from game_core.entity_definitions import *
from game_core.config import BASE_COL, UI_BG1_COL, adjust_color, FONT1, CURRENCY_SYMBOL

# --- Constants ---
BG_COLOR = UI_BG1_COL
TEXT_COLOR = (255, 255, 255)
SECTION_LABELS = ["Computers", "Monitors", "Utility", "Production", "Management", "Decoration"]
BUTTON_SPACING = 8  # Spacing between entity buttons
BUTTONS_TOP_MARGIN = 10  # Top margin for section buttons
PANEL_Y_OFFSET = 10  # Offset to move the construction panel downwards
ENTITY_BUTTON_COUNT = 10  # Default number of entity buttons in the construction panel

def get_computer_entities():
    classes = set()
    for base in (ComputerEntity, LaptopEntity):
        for name, obj in inspect.getmembers(entity_definitions):
            if inspect.isclass(obj) and issubclass(obj, base) and obj is not base:
                classes.add(obj)
    return sorted(classes, key=lambda cls: getattr(cls, 'tier', 99))

def monitors_section(extra_classes=TV):
    classes = [obj for name, obj in inspect.getmembers(entity_definitions)
            if inspect.isclass(obj) and issubclass(obj, SatisfiableEntity) and (obj.__name__.lower().endswith('monitor') or obj.__name__ == 'TV')]
    classes = sorted(classes, key=lambda cls: getattr(cls, 'tier', 99))
    if extra_classes:
        # Accepts a list or single class
        if isinstance(extra_classes, (list, tuple, set)):
            classes.extend(extra_classes)
        else:
            classes.append(extra_classes)
    return classes

def get_utility_entities():
    classes = []
    # Add Breaker and AirConditioner first
    classes.append(entity_definitions.Breaker)
    classes.append(entity_definitions.AirConditioner)
    classes.append(entity_definitions.Humidifier)
    for base in (UtilityEntity,):
        for name, obj in inspect.getmembers(entity_definitions):
            if inspect.isclass(obj) and issubclass(obj, base) and obj is not base and obj is not entity_definitions.Breaker and obj is not entity_definitions.AirConditioner:
                classes.append(obj)
    return sorted(classes, key=lambda cls: getattr(cls, 'tier', 99))

def get_management_entities():
    classes = [obj for name, obj in inspect.getmembers(entity_definitions)
            if inspect.isclass(obj)
            and issubclass(obj, SatisfiableEntity)
            and ('manager' in obj.__name__.lower() or 'project' in obj.__name__.lower())]
    return sorted(classes, key=lambda cls: getattr(cls, 'tier', 99))

def get_decoration_entities():
    classes = [obj for name, obj in inspect.getmembers(entity_definitions)
               if inspect.isclass(obj) and issubclass(obj, DecorationEntity) and obj is not DecorationEntity]
    return sorted(classes, key=lambda cls: getattr(cls, 'tier', 99))

def get_production_entities():
    # List your desired production classes here
    production_classes = [
        entity_definitions.Artist,
        entity_definitions.TechnicalDirector,
    ]
    return [cls for cls in production_classes if cls is not None]

class SectionButton:
    DEFAULT_HEIGHT = 40
    DEFAULT_WIDTH = 150
    FONT_SIZE = 18
    BG_COL = adjust_color(BASE_COL, white_factor=0, exposure=1.5)
    BG_COL_SELECTED = adjust_color(BASE_COL, white_factor=0, exposure=2.2)  # Added for selected state
    def __init__(self, rect, label, selected=False, height=None, width=None):
        self.rect = rect
        self.label = label
        self.selected = selected
        self.height = height if height is not None else self.DEFAULT_HEIGHT
        self.width = width if width is not None else self.DEFAULT_WIDTH

class EntityButton:
    DEFAULT_HEIGHT = 120
    DEFAULT_WIDTH = 120
    DEFAULT_ICON_WIDTH = 75
    DEFAULT_ICON_HEIGHT = DEFAULT_ICON_WIDTH
    DEFAULT_ICON_TOP_MARGIN = DEFAULT_HEIGHT // 14
    DEFAULT_LABEL_BOTTOM_MARGIN = 33
    FONT_SIZE = 18
    ROUNDING = 5  # Default corner radius for button rounding
    BG_COL_GRAD_START = adjust_color(BASE_COL, white_factor=0.8, exposure=1)  # Use adjust_color for gradient start
    BG_COL_GRAD_END = adjust_color(BASE_COL, white_factor=0.7, exposure=1)    # Gradient end color
    BG_COL_GRAD_EMPTY = adjust_color(BASE_COL, white_factor=0, exposure=0.9)  # For empty entity buttons
    BG_COL_SELECTED = adjust_color(BASE_COL, white_factor=0.9, exposure=1)
    TEXT_COL = (46, 62, 79)  # Default text color for entity button
    INNER_SHADOW_COLOR = (0, 0, 0, 60)  # RGBA for subtle shadow
    INNER_SHADOW_OFFSET = -7  # How far the shadow is offset (for 45°)
    INNER_SHADOW_BLUR = 7  # Blur radius (not true blur, but feathering)
    LABEL_TEXT_SIZE = 25  # Font size for purchase cost/label text
    LABEL_BOTTOM_MARGIN = 36  # Margin for label/cost text from bottom
    def __init__(self, rect, entity_class=None, selected=False, height=None, width=None, icon_width=None, icon_height=None, icon_top_margin=None):
        self.rect = rect
        self.entity_class = entity_class
        self.selected = selected
        self.height = height or self.DEFAULT_HEIGHT
        self.width = width or self.DEFAULT_WIDTH
        self.icon_width = icon_width or self.DEFAULT_ICON_WIDTH
        self.icon_height = icon_height or self.DEFAULT_ICON_HEIGHT
        self.icon_top_margin = icon_top_margin or self.DEFAULT_ICON_TOP_MARGIN
        # Extract icon and price from entity_class (label is not used)
        if entity_class is not None:
            self.icon_path = getattr(entity_class, '_icon', None)
            self.purchase_cost = getattr(entity_class, 'purchase_cost', None)
        else:
            self.icon_path = None
            self.purchase_cost = None

    def _draw_gradient(self, surface):
        grad_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        # Offset the gradient start/end lower by shifting the ratio
        offset = int(self.rect.height * 0.18)  # 18% down
        for y in range(self.rect.height):
            # Shift the gradient so it starts lower
            shifted_y = max(0, y - offset)
            ratio = shifted_y / max(1, self.rect.height - 1 - offset)
            ratio = min(max(ratio, 0), 1)  # Clamp between 0 and 1
            if self.entity_class is None:
                r = int(self.BG_COL_GRAD_EMPTY[0])
                g = int(self.BG_COL_GRAD_EMPTY[1])
                b = int(self.BG_COL_GRAD_EMPTY[2])
            else:
                r = int(self.BG_COL_GRAD_START[0] * (1 - ratio) + self.BG_COL_GRAD_END[0] * ratio)
                g = int(self.BG_COL_GRAD_START[1] * (1 - ratio) + self.BG_COL_GRAD_END[1] * ratio)
                b = int(self.BG_COL_GRAD_START[2] * (1 - ratio) + self.BG_COL_GRAD_END[2] * ratio)
            pygame.draw.line(grad_surf, (r, g, b), (0, y), (self.rect.width, y))
        grad_surf_rounded = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(grad_surf_rounded, (255,255,255), grad_surf_rounded.get_rect(), border_radius=self.ROUNDING)
        grad_surf_rounded.blit(grad_surf, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
        surface.blit(grad_surf_rounded, self.rect)

    def _draw_inner_shadow(self, surface):
        # Create a transparent surface for the shadow
        shadow_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        # Draw a semi-transparent black rounded rect, offset up/left for 45°
        for i in range(self.INNER_SHADOW_BLUR):
            alpha = int(self.INNER_SHADOW_COLOR[3] * (1 - i / self.INNER_SHADOW_BLUR))
            color = (*self.INNER_SHADOW_COLOR[:3], alpha)
            pygame.draw.rect(
                shadow_surf,
                color,
                pygame.Rect(
                    i + self.INNER_SHADOW_OFFSET,  # x offset (right)
                    i + self.INNER_SHADOW_OFFSET,  # y offset (down)
                    self.rect.width - 2 * i - self.INNER_SHADOW_OFFSET,
                    self.rect.height - 2 * i - self.INNER_SHADOW_OFFSET
                ),
                border_radius=max(1, self.ROUNDING - i)
            )
        # Mask with the button shape
        mask = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255,255,255,255), mask.get_rect(), border_radius=self.ROUNDING)
        shadow_surf.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
        surface.blit(shadow_surf, self.rect)

    def draw(self, surface, font, text_color=None):
        self._draw_gradient(surface)
        # Only draw bevel/inner shadow if entity_class is not None
        if self.entity_class is not None:
            self._draw_inner_shadow(surface)
        if self.selected:
            pygame.draw.rect(surface, self.BG_COL_SELECTED, self.rect, border_radius=self.ROUNDING)
        # Draw icon
        if self.icon_path:
            try:
                icon_surf = pygame.image.load(self.icon_path).convert_alpha()
                icon_surf = pygame.transform.smoothscale(icon_surf, (self.icon_width, self.icon_height))
                icon_rect = icon_surf.get_rect(center=(self.rect.centerx, self.rect.top + self.icon_top_margin + self.icon_height//2))
                surface.blit(icon_surf, icon_rect)
            except Exception as e:
                print(f"Error loading icon {self.icon_path}: {e}")
        # Draw price/rental with fixed font size
        entity_font = pygame.font.Font(FONT1, self.FONT_SIZE)
        col = text_color if text_color is not None else self.TEXT_COL
        if self.purchase_cost == 0:
            upkeep = getattr(self.entity_class, 'upkeep', None)
            if upkeep is not None:
                upkeep_surf = entity_font.render(f"-{CURRENCY_SYMBOL}{upkeep} / mo", True, col)
                upkeep_rect = upkeep_surf.get_rect(center=(self.rect.centerx, self.rect.bottom + 20 - self.LABEL_BOTTOM_MARGIN))
                surface.blit(upkeep_surf, upkeep_rect)
            else:
                cost_surf = entity_font.render("(monthly)", True, col)
                cost_rect = cost_surf.get_rect(center=(self.rect.centerx, self.rect.bottom + 20 - self.LABEL_BOTTOM_MARGIN))
                surface.blit(cost_surf, cost_rect)
        elif self.purchase_cost not in (None, 0):
            cost_surf = entity_font.render(f"{CURRENCY_SYMBOL}{self.purchase_cost}", True, col)
            cost_rect = cost_surf.get_rect(center=(self.rect.centerx, self.rect.bottom + 20 - self.LABEL_BOTTOM_MARGIN))
            surface.blit(cost_surf, cost_rect)

class Background:
    DEFAULT_COLOR = adjust_color(BASE_COL, white_factor=0.0, exposure=1)
    DEFAULT_WIDTH = EntityButton.DEFAULT_WIDTH * ENTITY_BUTTON_COUNT + ENTITY_BUTTON_COUNT * BUTTON_SPACING + 40  # Panel width matches entity button count
    DEFAULT_HEIGHT = SectionButton.DEFAULT_HEIGHT + EntityButton.DEFAULT_HEIGHT + 30
    ROUNDING = 12  # Default corner radius for background rounding
    BORDER_COLOR = UI_BORDER1_COL  # Use UI_BORDER1_COL for border color
    BORDER_WIDTH = 5

    def __init__(self, x=0, y=0, width=None, height=None, color=None, rounding=None, border_color=None, border_width=None, extend_below=0):
        self.x = x
        self.y = y
        self.width = width if width is not None else self.DEFAULT_WIDTH
        self.height = (height if height is not None else self.DEFAULT_HEIGHT) + extend_below
        self.color = color if color is not None else self.DEFAULT_COLOR
        self.rounding = rounding if rounding is not None else self.ROUNDING
        self.border_color = border_color if border_color is not None else self.BORDER_COLOR
        self.border_width = border_width if border_width is not None else self.BORDER_WIDTH
        self.extend_below = extend_below
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        # Draw filled background
        pygame.draw.rect(
            surface,
            self.color,
            self.rect,
            border_top_left_radius=self.rounding,
            border_top_right_radius=self.rounding,
            border_bottom_left_radius=0,
            border_bottom_right_radius=0
        )
        # Draw border
        pygame.draw.rect(
            surface,
            self.border_color,
            self.rect,
            width=self.border_width,
            border_top_left_radius=self.rounding,
            border_top_right_radius=self.rounding,
            border_bottom_left_radius=0,
            border_bottom_right_radius=0
        )

# --- Helper Functions ---
def draw_button(surface, rect, color, label=None, font=None, text_color=TEXT_COLOR):
    pygame.draw.rect(surface, color, rect)
    if label and font:
        text_surf = font.render(label, True, text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)

def get_section_entity_defs():
    return [
        lambda: get_computer_entities(),
        lambda: monitors_section(),
        lambda: get_utility_entities(),
        lambda: get_production_entities(),  # Use custom production entities
        lambda: get_management_entities(),
        lambda: get_decoration_entities(),
    ]

def get_entity_labels_icons_costs(entity_classes, num_buttons):
    def get_display_name(cls):
        return getattr(cls, 'display_name', cls.__name__)
    def get_purchase_cost(cls):
        return getattr(cls, 'purchase_cost', None)
    items = [(get_display_name(cls), getattr(cls, '_icon', None), cls, get_purchase_cost(cls)) for cls in entity_classes]
    if not items:
        return [], [], [], []
    items += [("-", None, None, None)] * (num_buttons - len(items))
    item_labels, entity_icons, entity_classes_out, purchase_costs = zip(*items)
    return list(item_labels), list(entity_icons), list(entity_classes_out), list(purchase_costs)

def draw_icon(surface, icon_path, btn_rect, icon_width, icon_height, icon_top_margin):
    if not icon_path:
        return
    try:
        icon_surf = pygame.image.load(icon_path).convert_alpha()
        icon_surf = pygame.transform.smoothscale(icon_surf, (icon_width, icon_height))
        icon_rect = icon_surf.get_rect(center=(btn_rect.centerx, btn_rect.top + icon_top_margin + icon_height//2))
        surface.blit(icon_surf, icon_rect)
    except Exception as e:
        print(f"Error loading icon {icon_path}: {e}")

_baked_panel_cache = {
    'surface': None,
    'section_buttons': None,
    'entity_buttons': None,
    'state': None,
    'size': None,
}

def draw_construction_panel(surface, selected_section=0, selected_item=None, font=None, x=None, y=None, width=None, height=100, number_of_entity_buttons=ENTITY_BUTTON_COUNT, extend_below=0):
    """
    Draws a new construction panel with two rows:
    - First row: 7 section buttons ("Computers", "Monitors", rest are "empty")
    - Second row: N item buttons (dynamically filled for section)
    Returns: (section_buttons, entity_buttons)
    """
    # Panel sizing and positioning
    background = Background(extend_below=extend_below)
    width = background.width
    panel_height = background.height
    x = (surface.get_width() - width) // 2
    y = surface.get_height() - panel_height + extend_below + PANEL_Y_OFFSET
    panel_rect = pygame.Rect(x, y, width, panel_height)

    # Create a hash of the current panel state for cache invalidation
    state_tuple = (selected_section, selected_item, surface.get_width(), surface.get_height())
    state_hash = hashlib.md5(str(state_tuple).encode()).hexdigest()
    size_tuple = (width, panel_height)

    # Check if we can use the cached panel
    if (
        _baked_panel_cache['surface'] is not None and
        _baked_panel_cache['state'] == state_hash and
        _baked_panel_cache['size'] == size_tuple
    ):
        # Blit the cached panel
        surface.blit(_baked_panel_cache['surface'], (x, y))
        return _baked_panel_cache['section_buttons'], _baked_panel_cache['entity_buttons']

    # Otherwise, bake a new panel
    panel_surf = pygame.Surface((width, panel_height), pygame.SRCALPHA)
    background.draw(panel_surf)

    # First row: Section buttons
    section_btn_w = SectionButton.DEFAULT_WIDTH
    section_btn_h = SectionButton.DEFAULT_HEIGHT
    num_sections = len(SECTION_LABELS)
    total_section_width = num_sections * section_btn_w
    section_btns_x_offset = (width - total_section_width) // 2
    section_buttons = []
    for i, label in enumerate(SECTION_LABELS):
        btn_rect = pygame.Rect(section_btns_x_offset + i * section_btn_w + 2, BUTTONS_TOP_MARGIN, section_btn_w - 4, section_btn_h - 4)
        selected = (i == selected_section)
        color = SectionButton.BG_COL_SELECTED if selected else SectionButton.BG_COL
        section_font = pygame.font.Font(FONT1, SectionButton.FONT_SIZE)
        draw_button(panel_surf, btn_rect, color, label, section_font)
        section_buttons.append(SectionButton(btn_rect.move(x, y), label, selected, height=section_btn_h - 4, width=btn_rect.width))

    # Second row: Entity buttons
    section_entity_defs = get_section_entity_defs()
    if 0 <= selected_section < len(section_entity_defs):
        entity_classes = section_entity_defs[selected_section]()
        entity_classes_out = list(entity_classes) + [None] * (number_of_entity_buttons - len(entity_classes))
    else:
        entity_classes_out = [None] * number_of_entity_buttons
    item_btn_w = EntityButton.DEFAULT_WIDTH
    item_btn_h = EntityButton.DEFAULT_HEIGHT
    entity_buttons = []
    # Center entity buttons horizontally in the panel with spacing
    total_btns_width = number_of_entity_buttons * item_btn_w + (number_of_entity_buttons - 1) * BUTTON_SPACING
    entity_btns_x_offset = (width - total_btns_width) // 2
    entity_btns_y = BUTTONS_TOP_MARGIN + section_btn_h + 2
    for i, entity_class in enumerate(entity_classes_out):
        btn_x = entity_btns_x_offset + i * (item_btn_w + BUTTON_SPACING)
        btn_rect = pygame.Rect(btn_x, entity_btns_y, item_btn_w, item_btn_h - 4)
        # Only allow selection if entity_class is not None
        selected = (selected_item is not None and i == selected_item and entity_class is not None)
        entity_button = EntityButton(
            btn_rect,  # Do NOT move(x, y) here!
            entity_class=entity_class,
            selected=selected,
            height=item_btn_h - 4,
            width=btn_rect.width,
            icon_width=EntityButton.DEFAULT_ICON_WIDTH,
            icon_height=EntityButton.DEFAULT_ICON_HEIGHT,
            icon_top_margin=EntityButton.DEFAULT_ICON_TOP_MARGIN,
        )
        entity_font = pygame.font.Font(FONT1, EntityButton.FONT_SIZE)
        entity_button.draw(panel_surf, entity_font)
        # For event handling, store the button rect relative to the main surface
        entity_buttons.append(EntityButton(
            btn_rect.move(x, y),
            entity_class=entity_class,
            selected=selected,
            height=item_btn_h - 4,
            width=btn_rect.width,
            icon_width=EntityButton.DEFAULT_ICON_WIDTH,
            icon_height=EntityButton.DEFAULT_ICON_HEIGHT,
            icon_top_margin=EntityButton.DEFAULT_ICON_TOP_MARGIN,
        ))

    # Cache the baked panel
    _baked_panel_cache['surface'] = panel_surf
    _baked_panel_cache['section_buttons'] = section_buttons
    _baked_panel_cache['entity_buttons'] = entity_buttons
    _baked_panel_cache['state'] = state_hash
    _baked_panel_cache['size'] = size_tuple

    # Blit the baked panel
    surface.blit(panel_surf, (x, y))
    return section_buttons, entity_buttons

def get_entity_button_hover(entity_buttons, mouse_pos):
    for btn in entity_buttons:
        if btn.entity_class is not None and btn.rect.collidepoint(mouse_pos):
            return btn.entity_class, btn.rect
    return None, None

def draw_entity_hover_label(surface, entity_class, mouse_pos, font=None):
    if entity_class is None:
        return
    display_name = getattr(entity_class, 'display_name', entity_class.__name__)
    font = pygame.font.Font(FONT1, 20)
    text_surf = font.render(display_name, True, (255,255,255))
    text_rect = text_surf.get_rect()
    # Expand the background rect more for padding
    bg_rect = text_rect.inflate(24, 14)  # Wider and taller for more padding
    bg_rect.topleft = (mouse_pos[0] + 18, mouse_pos[1] + 8)
    # Center the text in the background rect
    text_rect.center = bg_rect.center
    text_rect.y += 1  # Move text 1px lower
    temp_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(temp_surf, (0,0,0,180), temp_surf.get_rect(), border_radius=4)
    surface.blit(temp_surf, bg_rect.topleft)
    surface.blit(text_surf, text_rect)
