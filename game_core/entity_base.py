import pygame
import re
import random
import time
from .config import *
from game_core.game_state import GameState, EntityStats
from game_other.audio import *

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

# region BaseEntity

class BaseEntity:
    _icon = None
    _id_counter = 0
    state = "Basic"
    purchase_cost = 0
    upkeep = 0
    decoration = 0
    tier = 1
    width = 1  # Default entity width (in grid cells)
    height = 1  # Default entity height (in grid cells)
    
    power_drain = 0  # Intended power drain when initialized (override in subclasses)
    _intended_power_drain = None  # Store intended value for restoration
    display_name = None  # Enforce as a class attribute for all entities

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Only set display_name if not set on the class itself (not inherited)
        if 'display_name' not in cls.__dict__ or cls.display_name is None:
            cls.display_name = to_display_name_from_classname(cls.__name__)

    def __init__(self, x, y):
        self.x, self.y = x, y
        # Always set display_name instance attribute, using class attribute
        self.display_name = self.__class__.display_name
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
            width = getattr(self, 'width', 1)
            height = getattr(self, 'height', 1)
            margin = cell_size - CELL_SIZE_INNER
            icon_w = cell_size * width - margin
            icon_h = cell_size * height - margin
            icon = pygame.transform.smoothscale(self._icon_surface, (int(icon_w), int(icon_h)))
            cell_x = self.x * cell_size + offset[0]
            cell_y = self.y * cell_size + offset[1]
            icon_x = cell_x + (cell_size * width - icon_w) // 2
            icon_y = cell_y + (cell_size * height - icon_h) // 2
            surface.blit(icon, (icon_x, icon_y))
        # Draw highlight overlay if initialized and unsatisfied, or if broken, and warning_hidden is 0
        highlight_color = None
        if (
            getattr(self, 'is_initialized', 0) and not getattr(self, 'is_satisfied', 1)
        ):
            highlight_color = STATUS_MID_COL
        if getattr(self, 'is_broken', 0):
            highlight_color = STATUS_BAD_COL
        if highlight_color and not getattr(self, 'warning_hidden', 0) and not static_only:
            width = getattr(self, 'width', 1)
            height = getattr(self, 'height', 1)
            margin = cell_size - CELL_SIZE_INNER
            rect_size_w = cell_size * width - margin
            rect_size_h = cell_size * height - margin
            x = self.x * cell_size + offset[0] + (cell_size * width - rect_size_w) // 2
            y = self.y * cell_size + offset[1] + (cell_size * height - rect_size_h) // 2
            border_radius = 3
            pygame.draw.rect(surface, highlight_color, (x, y, rect_size_w, rect_size_h), 3, border_radius=border_radius)
        if not static_only:
            if getattr(self, "has_bar1", 1) and not getattr(self, 'has_sat_check_bar_hidden', 0) and hasattr(self, 'draw_bar1'):
                self.draw_bar1(surface, offset[0], offset[1], cell_size)
            if getattr(self, "has_special", 0) and not getattr(self, 'special_hidden', 0) and hasattr(self, 'draw_special'):
                self.draw_special(surface, offset[0], offset[1], cell_size)

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

    def on_built(self, is_move=False):
        """Call this after the entity is actually built/placed to deduct its purchase cost from total_money and add upkeep to total_upkeep. If is_move is True, do not deduct money or play purchase sound."""
        gs = GameState()
        cost = getattr(self, 'purchase_cost', 0)
        if not is_move:
            gs.total_money -= cost
            if cost > 0:
                from game_other.audio import play_purchase_sound
                play_purchase_sound()
            else:
                play_build_sound()
        # 10% chance to increase current_lvl_experience by 1 (with level up)
        if hasattr(gs, 'add_experience') and random.random() < 0.1:
            gs.add_experience(1)

    def on_initialized(self):
        self.power_drain = self._intended_power_drain

# region SatisfiableEntity

class SatisfiableEntity(BaseEntity):
    _icon = None
    _icon_broken = None
    _BAR1_COL = (60, 60, 60)
    _BAR1_COL_FILL_INIT = STATUS_INIT_COL
    _BAR1_COL_FILL_UNSAT = STATUS_MID_COL
    _BAR1_COL_FILL_SAT = STATUS_GOOD_COL
    _SPECIAL_COL_BG = (100, 100, 100)
    _SPECIAL_COL_FILL = (203, 33, 255)
    _BAR_HEIGHT_RATIO = 0.15
    _BAR_DURATION_FRAMES = 300
    _BAR_REFRESH_RATE = 1
    has_sat_check_bar = 1
    has_sat_check_bar_hidden = 0
    has_special = 0
    has_special_hidden = 0  # New: allows hiding special bar
    special_chance = 1
    warning_hidden = 0
    is_satisfied = 0
    is_initialized = 0
    is_risky = 0
    is_broken = 0
    state = "Init"

    def __init__(self, x, y):
        super().__init__(x, y)
        self.bar1 = 0.0 if self.has_sat_check_bar else None
        self.bar1_timer = 0 if self.has_sat_check_bar else None
        self.special = 0.0 if self.has_special else None
        self.special_timer = 0 if self.has_special else None
        self._progress_bar_frame_counter = 0
        self.on_spawn()

    def on_spawn(self):
        pass

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
                    if match:
                        # Check all tiles occupied by the entity
                        ex, ey = entity.x, entity.y
                        ew = getattr(entity, 'width', 1)
                        eh = getattr(entity, 'height', 1)
                        found = False
                        for dx in range(ew):
                            for dy in range(eh):
                                tile_x = ex + dx
                                tile_y = ey + dy
                                dist = abs(tile_x - self.x) + abs(tile_y - self.y)
                                if dist <= radius:
                                    found = True
                                    break
                            if found:
                                break
                        if found:
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
        elif self.is_satisfied == 1 and self.is_initialized == 1:
            self.state = "Good"
        elif self.is_broken == 1:
            self.state = "Bad"

    def update(self, grid):
        self._progress_bar_frame_counter += 1
        if self._progress_bar_frame_counter >= self._BAR_REFRESH_RATE:
            self._progress_bar_frame_counter = 0
            self._update_sat_check_bar(grid)
            self._update_special_bar(grid)



    def _update_sat_check_bar(self, grid):
        if self.has_sat_check_bar:
            prev_initialized = self.is_initialized
            self.bar1_timer += self._BAR_REFRESH_RATE
            if self.bar1_timer >= self._BAR_DURATION_FRAMES:
                self.bar1_timer = 0
                if not self.is_initialized:
                    self.is_initialized = 1
                    self.on_initialized()
                # Remove special roll logic here (now handled in satisfaction_check)
                entity_type = getattr(self, 'satisfaction_check_type', None)
                radius = getattr(self, 'satisfaction_check_radius', 2)
                if entity_type:
                    self.satisfaction_check(grid)
                self._set_status()
                self.on_sat_check_finish()
            self.bar1 = self.bar1_timer / self._BAR_DURATION_FRAMES
        else:
            self.bar1 = None

    def _update_special_bar(self, grid):
        if self.has_special and self.is_initialized and self.is_satisfied:
            # Only progress the special bar if it is active
            if self.special is not None and self.special_timer is not None:
                self.special_timer += self._BAR_REFRESH_RATE
                if self.special_timer >= self._BAR_DURATION_FRAMES:
                    self.special_timer = None
                    self.special = None
                    self.on_special_finish()  # Fire on_special when special completes
                else:
                    self.special = self.special_timer / self._BAR_DURATION_FRAMES
        else:
            self.special = None
            self.special_timer = None
            if hasattr(self, '_special_spawn_attempted'):
                del self._special_spawn_attempted

    def get_icon_path(self):
        if getattr(self, 'is_broken', 0) and getattr(self, '_icon_broken', None):
            return self._icon_broken
        return self._icon

    def draw(self, surface, offset=(0, 0), cell_size=64, static_only=False):
        super().draw(surface, offset, cell_size, static_only)
        if not static_only:
            if getattr(self, "has_bar1", 1) and not getattr(self, 'has_sat_check_bar_hidden', 0) and hasattr(self, 'draw_bar1'):
                self.draw_bar1(surface, offset[0], offset[1], cell_size)
            if getattr(self, "has_special", 0) and not getattr(self, 'special_hidden', 0) and hasattr(self, 'draw_special'):
                self.draw_special(surface, offset[0], offset[1], cell_size)

    def draw_bar1(self, surface, ox, oy, cell_size):
        bar_height = int(cell_size * self._BAR_HEIGHT_RATIO)
        bar_width = CELL_SIZE_INNER
        # Center bar horizontally in the cell
        x = self.x * cell_size + ox + (cell_size - bar_width) // 2
        y = self.y * cell_size + oy + cell_size - bar_height
        if self.is_initialized and not self.is_satisfied:
            bar_color = self._BAR1_COL_FILL_UNSAT
        else:
            bar_color = self._BAR1_COL_FILL_INIT if not self.is_initialized else self._BAR1_COL_FILL_SAT
        pygame.draw.rect(surface, self._BAR1_COL, (x, y, bar_width, bar_height))
        fill_width = int(bar_width * self.bar1)
        pygame.draw.rect(surface, bar_color, (x, y, fill_width, bar_height))

    def draw_special(self, surface, ox, oy, cell_size):
        if not (getattr(self, "has_special", 0) and self.is_initialized and self.is_satisfied):
            return
        if self.special is None:
            return
        bar_height = int(cell_size * self._BAR_HEIGHT_RATIO)
        bar_width = CELL_SIZE_INNER
        # Center bar horizontally in the cell, stack above bar1
        x = self.x * cell_size + ox + (cell_size - bar_width) // 2
        y = self.y * cell_size + oy + cell_size - 2 * bar_height
        pygame.draw.rect(surface, self._SPECIAL_COL_BG, (x, y, bar_width, bar_height))
        fill_width = int(bar_width * self.special)
        pygame.draw.rect(surface, self._SPECIAL_COL_FILL, (x, y, fill_width, bar_height))

    def satisfaction_check(self, grid):
        gs = GameState()
        # Existing logic
        entity_type = getattr(self, 'satisfaction_check_type', None)
        radius = getattr(self, 'satisfaction_check_radius', 2)
        threshold = getattr(self, 'satisfaction_check_threshold', 1)
        gs_var = getattr(self, 'satisfaction_check_gamestate', None)
        predicate = getattr(self, 'satisfaction_check_predicate', None)
        # All conditions must be satisfied
        # 1. If a GameState variable is specified, it must be True
        if gs_var is not None:
            if not hasattr(gs, gs_var) or getattr(gs, gs_var) != 1:
                self.is_satisfied = 0
                self.power_drain = 0
                return
        # 2. If an entity_type is specified, proximity count must meet threshold
        if entity_type:
            if predicate:
                count = self.count_entities_in_proximity(grid, entity_type, radius, predicate=lambda e: predicate(self, e))
            else:
                count = self.count_entities_in_proximity(grid, entity_type, radius)
            if count < threshold:
                self.is_satisfied = 0
                self.power_drain = 0
                return
        # If all conditions passed, mark as satisfied
        self.is_satisfied = 1
        # Roll for special bar if applicable
        if getattr(self, 'has_special', 0):
            if getattr(self, 'special', None) is None and getattr(self, 'special_timer', None) is None:
                if random.random() < getattr(self, 'special_chance', 0.1):
                    self.special = 0.0
                    self.special_timer = 0
                    self.on_special_start()
                else:
                    self.special = None
                    self.special_timer = None

    def on_sat_check_finish(self):
        pass

    def on_special_finish(self):
        pass

    def on_special_start(self):
        # Only multiply if not already multiplied (avoid stacking)
        if self.power_drain == self._intended_power_drain:
            self.power_drain = self._intended_power_drain * 3
        # If already multiplied, do nothing

# region Custom classes

class DecorationEntity(BaseEntity):
    upkeep = 20
    decoration = 5

class UtilityEntity(BaseEntity):
    pass

class ComputerEntity(SatisfiableEntity):
    satisfaction_check_type = 'outlet'
    has_special = 1
    special_chance = 0.5
    power_drain = 0
    satisfaction_check_gamestate = 'is_nas_online'
    heating_multiplier = 1
    decoration = -5

    def on_spawn(self):
        self.is_rendering = 1 if self.special is not None else 0

    def on_sat_check_finish(self):
        if self.is_satisfied == 1:
            gs = GameState()
            if hasattr(gs, 'temperature'):
                gs.temperature += 0.005 * self.heating_multiplier
            # Check render progress and set has_special accordingly
            if hasattr(gs, 'render_progress_current') and hasattr(gs, 'render_progress_allowed'):
                if gs.render_progress_current == gs.render_progress_allowed:
                    self.has_special = 0
                elif gs.render_progress_allowed > gs.render_progress_current:
                    self.has_special = 1

    def on_special_start(self):
        self.power_drain = self.power_drain * 3

    def on_special_finish(self):
        self.power_drain = self.power_drain / 3
        gs = GameState()
        if hasattr(gs, 'temperature'):
            gs.temperature += 0.02 * self.heating_multiplier
        # Increment render_progress_current if not at max
        if gs.render_progress_current < gs.render_progress_allowed:
            gs.render_progress_current += 1

class LaptopEntity(SatisfiableEntity):
    is_initialized = 1
    is_satisfied = 1
    has_bar1 = 0
    decoration = 1
    pass

class MonitorEntity(SatisfiableEntity):
    has_special = 0
    satisfaction_check_type = ComputerEntity
    satisfaction_check_radius = 1
    satisfaction_check_threshold = 1
    decoration = -1

    def satisfaction_check(self, grid):
        # Standard proximity check for ComputerEntity in radius 1
        count = self.count_entities_in_proximity(
            grid, ComputerEntity, self.satisfaction_check_radius
        )
        # If any adjacent ComputerEntity is rendering, 20% chance to become unsatisfied
        for row in grid:
            for entity in row:
                if (
                    isinstance(entity, ComputerEntity)
                    and abs(entity.x - self.x) + abs(entity.y - self.y) <= self.satisfaction_check_radius
                    and getattr(entity, 'is_rendering', 0) == 1
                ):
                    if random.random() < 0.2:
                        self.is_satisfied = 0
                        self.state = "Mid"
                        return
        # Otherwise, use normal logic
        if count >= self.satisfaction_check_threshold:
            self.is_satisfied = 1
            self.state = "Good"
        else:
            self.is_satisfied = 0
            self.state = "Mid"

class PersonEntity(SatisfiableEntity):
    is_person = 1
    happiness = 0
    hunger = 0
    toilet_need = 0
    has_coffee = 0
    max_temp_tolerance = 0
    names = [
        "Marek Sosna",
        "Radim Zeifart",
        "Simon Lansky",
        "Ondrej Skalnik",
        "Jaroslav Novotny",
        "Jan Reeh",
        "Martina Svojikova",
        "Jachym Nadvornik",
        "Petr Kollarcik"
    ]
    def on_spawn(self):
        self.person_name = random.choice(self.names)
        self.display_name = getattr(self, 'display_name', 'Person')
        self.happiness = random.randint(1, 10)
        self.hunger = random.randint(1, 10)
        self.toilet_need = random.randint(1, 10)
        self.max_temp_tolerance = random.randint(25, 35)

    def on_sat_check_finish(self):
        gs = GameState()
        if hasattr(gs, 'temperature') and getattr(self, 'max_temp_tolerance', None) is not None:
            if gs.temperature > self.max_temp_tolerance:
                if random.random() < 0.3:
                    self.is_satisfied = 0
                    self.state = "Mid"
        # 0.01 chance for medical items
        if random.random() < 0.01:
            if hasattr(gs, 'total_ibalgin') and gs.total_ibalgin > 0:
                gs.total_ibalgin -= 1
        if random.random() < 0.01:
            if hasattr(gs, 'total_bandages') and gs.total_bandages > 0:
                gs.total_bandages -= 1
        if random.random() < 0.01:
            if hasattr(gs, 'total_pcr_test') and gs.total_pcr_test > 0:
                gs.total_pcr_test -= 1
        # 0.005 chance for cables, mouses, keyboards
        if random.random() < 0.005:
            if hasattr(gs, 'total_cables') and gs.total_cables > 0:
                gs.total_cables -= 1
        if random.random() < 0.005:
            if hasattr(gs, 'total_mouses') and gs.total_mouses > 0:
                gs.total_mouses -= 1
        if random.random() < 0.005:
            if hasattr(gs, 'total_keyboards') and gs.total_keyboards > 0:
                gs.total_keyboards -= 1
        if getattr(self, 'has_coffee', 0) == 1 and random.random() < 0.2:
            self.has_coffee = 0
        if hasattr(self, 'hunger'):
            self.hunger = max(0, self.hunger - 0.1)
        if getattr(self, 'has_coffee', 0) == 0 and random.random() < 0.1:
            if (
                hasattr(gs, 'total_coffee_beans') and gs.total_coffee_beans > 0 and
                EntityStats().total_coffeemachine_entities > 0
            ):
                gs.total_coffee_beans -= 1
                self.has_coffee = 1
                if hasattr(gs, 'total_milk') and gs.total_milk > 0 and random.random() < 0.2:
                    gs.total_milk -= 1
                if hasattr(gs, 'total_sugar') and gs.total_sugar > 0 and random.random() < 0.2:
                    gs.total_sugar -= 1

class WideEntity(SatisfiableEntity):
    """A test entity that occupies 2x1 tiles. Use for multi-tile placement testing."""
    width = 2
    height = 2
    _icon = "data/graphics/entites/fridge.png"  # Use any existing icon for testing
    display_name = "Fridge"