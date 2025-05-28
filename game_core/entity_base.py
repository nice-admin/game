import pygame
import re
import random
import time
from .config import *
from game_core.game_state import GameState


CELL_SIZE = 64  # Default cell size, can be overridden by main.py

# --- ICON CACHE ---
_ICON_CACHE = {}

def get_icon_surface(path):
    if path in _ICON_CACHE:
        return _ICON_CACHE[path]
    try:
        surf = pygame.image.load(path).convert_alpha()
        _ICON_CACHE[path] = surf
        return surf
    except Exception:
        _ICON_CACHE[path] = None
        return None

def to_type_from_classname(name):
    return name[0].lower() + name[1:]

def to_display_name_from_classname(name):
    return re.sub(r'([a-z])([A-Z])', r'\1 \2', name).capitalize()

class BaseEntity:
    _icon = None
    _id_counter = 0
    state = "Basic"
    purchase_cost = 0
    upkeep = 0
    power_drain = 0  # Intended power drain when initialized (override in subclasses)
    _intended_power_drain = None  # Store intended value for restoration

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.display_name = to_display_name_from_classname(self.__class__.__name__)
        self._icon_surface = None
        self.id = BaseEntity._id_counter
        BaseEntity._id_counter += 1
        self.timestamp = time.strftime('%Y-%m-%d %H:%M:%S')  # Human-readable creation time       
        # Store intended power_drain and start with 0 until initialized
        self._intended_power_drain = getattr(self.__class__, 'power_drain', 0)
        self.power_drain = 0

    def update(self, grid):
        pass  # No-op for base class, avoids AttributeError in main loop

    def draw(self, surface, offset=(0, 0), cell_size=64, static_only=False):
        icon_path = self._icon if hasattr(self, '_icon') else self.__class__._icon
        if getattr(self, '_last_icon_path', None) != icon_path:
            self._icon_surface = get_icon_surface(icon_path)
            self._last_icon_path = icon_path
        if self._icon_surface and not static_only:
            icon = pygame.transform.smoothscale(self._icon_surface, (cell_size, cell_size))
            surface.blit(icon, (self.x * cell_size + offset[0], self.y * cell_size + offset[1]))
        # Draw highlight overlay if initialized and unsatisfied, or if broken, and warning_hidden is 0
        highlight_color = None
        if (
            getattr(self, 'is_initialized', 0) and not getattr(self, 'is_satisfied', 1)
        ):
            highlight_color = STATUS_MID_COL
        if getattr(self, 'is_broken', 0):
            highlight_color = STATUS_BAD_COL
        if highlight_color and not getattr(self, 'warning_hidden', 0) and not static_only:
            x = self.x * cell_size + offset[0]
            y = self.y * cell_size + offset[1]
            pygame.draw.rect(surface, highlight_color, (x, y, cell_size, cell_size), 3)
        if not static_only:
            if getattr(self, "has_bar1", 1) and not getattr(self, 'bar1_hidden', 0) and hasattr(self, 'draw_bar1'):
                self.draw_bar1(surface, offset[0], offset[1], cell_size)
            if getattr(self, "has_bar2", 0) and not getattr(self, 'bar2_hidden', 0) and hasattr(self, 'draw_bar2'):
                self.draw_bar2(surface, offset[0], offset[1], cell_size)

    def to_dict(self):
        from game_core.entity_definitions import to_type_from_classname
        d = {'type': to_type_from_classname(type(self).__name__)}
        # Add instance attributes
        for k, v in self.__dict__.items():
            if not k.startswith('_') and k != 'color' and k != 'type':
                d[k] = v
        # Add class attributes if not already present
        for k in dir(self.__class__):
            if (not k.startswith('_') and k not in d and not callable(getattr(self.__class__, k))
                and not k.startswith('$')):
                d[k] = getattr(self.__class__, k)
        return d

    @classmethod
    def from_dict(cls, data):
        obj = cls(data['x'], data['y'])
        for k, v in data.items():
            if k in ('x', 'y'):
                continue  # Already set
            setattr(obj, k, v)
        return obj


    def get_public_attrs(self):
        from game_core.entity_definitions import to_type_from_classname
        # Collect all public instance attributes (not starting with '_', not 'color' or 'type')
        attrs = set(k for k in self.__dict__ if not k.startswith('_') and k != 'color' and k != 'type')
        # Add all public class attributes (not starting with '_', not callable)
        for k in dir(self.__class__):
            if not k.startswith('_') and not callable(getattr(self.__class__, k)):
                attrs.add(k)
        d = {'type': to_type_from_classname(type(self).__name__)}
        for k in sorted(attrs):
            d[k] = getattr(self, k, getattr(self.__class__, k, None))
        return d

    def on_built(self):
        """Call this after the entity is actually built/placed to deduct its purchase cost from total_money and add upkeep to total_upkeep."""
        gs = GameState()
        cost = getattr(self, 'purchase_cost', 0)
        gs.total_money -= cost
        if cost > 0:
            from game_other.audio import play_purchase_sound
            play_purchase_sound()

    def on_initialized(self):
        """Call this when the entity becomes initialized to set power_drain to intended value."""
        self.power_drain = self._intended_power_drain

class SatisfiableEntity(BaseEntity):
    _icon = None
    _icon_broken = None
    _BAR1_COL = (60, 60, 60)
    _BAR1_COL_FILL_INIT = STATUS_INIT_COL
    _BAR1_COL_FILL_UNSAT = STATUS_MID_COL
    _BAR1_COL_FILL_SAT = STATUS_GOOD_COL
    _BAR2_COL_BG = (100, 100, 100)
    _BAR2_COL_FILL = (203, 33, 255)
    _BAR_HEIGHT_RATIO = 0.15
    _BAR_DURATION_FRAMES = 300
    _BAR_REFRESH_RATE = 1
    has_bar1 = 1
    has_bar2 = 0
    bar1_hidden = 0  # New: allows hiding bar1
    bar2_hidden = 0  # New: allows hiding bar2
    warning_hidden = 0
    is_satisfied = 0
    is_initialized = 0
    is_risky = 0
    is_broken = 0
    state = "Init"

    def __init__(self, x, y):
        super().__init__(x, y)
        self.is_initialized = 0
        self.bar1 = 0.0 if self.has_bar1 else None
        self.bar1_timer = 0 if self.has_bar1 else None
        self.bar2 = 0.0 if self.has_bar2 else None
        self.bar2_timer = 0 if self.has_bar2 else None
        self._progress_bar_frame_counter = 0

    def count_entities_in_proximity(self, grid, entity_type, radius, predicate=None):
        count = 0
        for row in grid:
            for entity in row:
                if entity is not None:
                    # Accept class or string for entity_type
                    if isinstance(entity_type, type):
                        match = isinstance(entity, entity_type)
                    elif isinstance(entity_type, (list, tuple)) and all(isinstance(t, type) for t in entity_type):
                        match = any(isinstance(entity, t) for t in entity_type)
                    else:
                        match = to_type_from_classname(entity.__class__.__name__) == entity_type
                    # Only count if is_satisfied == 1 (unless a predicate is provided)
                    if match:
                        dist = abs(entity.x - self.x) + abs(entity.y - self.y)
                        if dist <= radius:
                            if predicate is not None:
                                if predicate(entity):
                                    count += 1
                            else:
                                if getattr(entity, 'is_satisfied', 1) == 1:
                                    count += 1
        return count

    def _set_status(self):
        # Set to 'Mid' if (not satisfied AND initialized AND not broken) OR risky
        if ((self.is_satisfied == 0 and self.is_initialized == 1 and self.is_broken == 0) or self.is_risky == 1):
            self.state = "Mid"
        elif self.is_satisfied and self.is_initialized:
            self.state = "Good"
        elif self.is_broken:
            self.state = "Bad"

    def update(self, grid):
        self._progress_bar_frame_counter += 1
        if self._progress_bar_frame_counter >= self._BAR_REFRESH_RATE:
            self._progress_bar_frame_counter = 0
            self._update_bar1(grid)
            self._update_bar2(grid)
        self._set_status()

    def _update_bar1(self, grid):
        if self.has_bar1:
            prev_initialized = self.is_initialized
            self.bar1_timer += self._BAR_REFRESH_RATE
            if self.bar1_timer >= self._BAR_DURATION_FRAMES:
                self.bar1_timer = 0
                if not self.is_initialized:
                    self.is_initialized = True
                    self.on_initialized()  # Set power_drain when initialized
                    if self.has_bar2 and not hasattr(self, '_bar2_spawned'):
                        if random.random() < 0.1:
                            self.has_bar2 = True
                            self.bar2 = 0.0
                            self.bar2_timer = 0
                        self._bar2_spawned = True
                self.is_satisfied = self.check_satisfaction(grid)
                entity_type = getattr(self, 'satisfaction_check_type', None)
                radius = getattr(self, 'satisfaction_check_radius', 2)
                if entity_type:
                    self.satisfaction_check(grid)
            self.bar1 = self.bar1_timer / self._BAR_DURATION_FRAMES
        else:
            self.bar1 = None

    def _update_bar2(self, grid):
        if self.has_bar2 and self.is_initialized and self.is_satisfied:
            if not hasattr(self, '_bar2_spawn_attempted'):
                if self.bar2 is None and self.bar2_timer is None:
                    if random.random() < 0.1:
                        self.bar2 = 0.0
                        self.bar2_timer = 0
                    else:
                        self.bar2 = None
                        self.bar2_timer = None
                self._bar2_spawn_attempted = True
            if self.bar2 is not None and self.bar2_timer is not None:
                self.bar2_timer += self._BAR_REFRESH_RATE
                if self.bar2_timer >= self._BAR_DURATION_FRAMES:
                    self.bar2_timer = 0
                self.bar2 = self.bar2_timer / self._BAR_DURATION_FRAMES
        else:
            self.bar2 = None
            self.bar2_timer = None
            if hasattr(self, '_bar2_spawn_attempted'):
                del self._bar2_spawn_attempted

    def get_icon_path(self):
        if getattr(self, 'is_broken', 0) and getattr(self, '_icon_broken', None):
            return self._icon_broken
        return self._icon

    def draw(self, surface, offset=(0, 0), cell_size=64, static_only=False):
        icon_path = self.get_icon_path() if hasattr(self, 'get_icon_path') else (self._icon if hasattr(self, '_icon') else self.__class__._icon)
        if getattr(self, '_last_icon_path', None) != icon_path:
            self._icon_surface = get_icon_surface(icon_path)
            self._last_icon_path = icon_path
        if self._icon_surface and not static_only:
            icon = pygame.transform.smoothscale(self._icon_surface, (cell_size, cell_size))
            surface.blit(icon, (self.x * cell_size + offset[0], self.y * cell_size + offset[1]))
        # Draw highlight overlay if initialized and unsatisfied, or if broken, and warning_hidden is 0
        highlight_color = None
        if (
            getattr(self, 'is_initialized', 0) and not getattr(self, 'is_satisfied', 1)
        ):
            highlight_color = STATUS_MID_COL
        if getattr(self, 'is_broken', 0):
            highlight_color = STATUS_BAD_COL
        if highlight_color and not getattr(self, 'warning_hidden', 0) and not static_only:
            x = self.x * cell_size + offset[0]
            y = self.y * cell_size + offset[1]
            pygame.draw.rect(surface, highlight_color, (x, y, cell_size, cell_size), 3)
        if not static_only:
            if getattr(self, "has_bar1", 1) and not getattr(self, 'bar1_hidden', 0) and hasattr(self, 'draw_bar1'):
                self.draw_bar1(surface, offset[0], offset[1], cell_size)
            if getattr(self, "has_bar2", 0) and not getattr(self, 'bar2_hidden', 0) and hasattr(self, 'draw_bar2'):
                self.draw_bar2(surface, offset[0], offset[1], cell_size)

    def draw_bar1(self, surface, ox, oy, cell_size):
        bar_height = int(cell_size * self._BAR_HEIGHT_RATIO)
        bar_width = cell_size
        x = self.x * cell_size + ox
        y = self.y * cell_size + oy + cell_size - bar_height
        if self.is_initialized and not self.is_satisfied:
            bar_color = self._BAR1_COL_FILL_UNSAT
        else:
            bar_color = self._BAR1_COL_FILL_INIT if not self.is_initialized else self._BAR1_COL_FILL_SAT
        pygame.draw.rect(surface, self._BAR1_COL, (x, y, bar_width, bar_height))
        fill_width = int(bar_width * self.bar1)
        pygame.draw.rect(surface, bar_color, (x, y, fill_width, bar_height))

    def draw_bar2(self, surface, ox, oy, cell_size):
        if not (getattr(self, "has_bar2", 0) and self.is_initialized and self.is_satisfied):
            return
        if self.bar2 is None:
            return
        bar_height = int(cell_size * self._BAR_HEIGHT_RATIO)
        bar_width = cell_size
        x = self.x * cell_size + ox
        y = self.y * cell_size + oy + cell_size - 2 * bar_height
        pygame.draw.rect(surface, self._BAR2_COL_BG, (x, y, bar_width, bar_height))
        fill_width = int(bar_width * self.bar2)
        pygame.draw.rect(surface, self._BAR2_COL_FILL, (x, y, fill_width, bar_height))

    def check_satisfaction(self, grid):
        return False

    def satisfaction_check(self, grid):
        entity_type = getattr(self, 'satisfaction_check_type', None)
        radius = getattr(self, 'satisfaction_check_radius', 2)
        threshold = getattr(self, 'satisfaction_check_threshold', 1)
        gs = GameState()
        gs_var = getattr(self, 'satisfaction_check_gamestate', None)
        predicate = getattr(self, 'satisfaction_check_predicate', None)
        # All conditions must be satisfied
        # 1. If a GameState variable is specified, it must be 1
        if gs_var is not None:
            if not hasattr(gs, gs_var) or getattr(gs, gs_var) != 1:
                self.is_satisfied = 0
                return
        # 2. If an entity_type is specified, proximity count must meet threshold
        if entity_type:
            if predicate:
                count = self.count_entities_in_proximity(grid, entity_type, radius, predicate=lambda e: predicate(self, e))
            else:
                count = self.count_entities_in_proximity(grid, entity_type, radius)
            if hasattr(self, 'on_satisfaction_check'):
                self.on_satisfaction_check(count, threshold)
                return
            if count < threshold:
                self.is_satisfied = 0
                return
        # If all conditions passed, mark as satisfied
        self.is_satisfied = 1

class ComputerEntity(SatisfiableEntity):
    satisfaction_check_type = 'outlet'
    power_drain = 1  # Set intended value here

    def __init__(self, x, y):
        super().__init__(x, y)
        self.is_rendering = 1 if self.bar2 is not None else 0

    def _update_bar2(self, grid):
        prev_bar2 = self.bar2 if hasattr(self, 'bar2') else None
        prev_bar2_timer = self.bar2_timer if hasattr(self, 'bar2_timer') else None
        super()._update_bar2(grid)
        # Update is_rendering based on bar2 presence
        self.is_rendering = 1 if self.bar2 is not None else 0
        # Only increment render_progress if bar2 just completed (allow for float rounding)
        if (
            prev_bar2 is not None and prev_bar2_timer is not None and
            prev_bar2 >= 0.99 and self.bar2 == 0.0 and self.bar2_timer == 0
        ):
            gs = GameState()
            gs.render_progress_current += 1

class PersonEntity(SatisfiableEntity):
    is_person = 1
    # You can add more attributes or override methods as needed
    def __init__(self, x, y):
        super().__init__(x, y)
        # Example: Give a default display name or other person-specific logic
        self.display_name = getattr(self, 'display_name', 'Person')
        # Add more initialization if needed