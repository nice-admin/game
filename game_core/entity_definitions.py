from .entity_base import *
import random
from game_other.audio import play_breaker_break_sound

# --- Entity subclasses ---
class BasicComputer(ComputerEntity):
    _icon = "data/graphics/computer-basic.png"
    has_special = 1
    power_drain = 200
    satisfaction_check_type = 'outlet'
    satisfaction_check_gamestate = 'is_nas_online'

class Monitor(SatisfiableEntity):
    _icon = "data/graphics/monitor.png"
    has_special = 0
    power_drain = 20
    satisfaction_check_type = ComputerEntity
    satisfaction_check_radius = 1
    satisfaction_check_threshold = 1

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

class Artist(SatisfiableEntity):
    _icon = "data/graphics/artist.png"
    satisfaction_check_type = 'monitor'
    satisfaction_check_radius = 1
    satisfaction_check_threshold = 1
    is_person = 1
    upkeep = 2000

class EspressoMachine(BaseEntity):
    _icon = "data/graphics/coffee-machine.png"

class Outlet(BaseEntity):
    _icon = "data/graphics/outlet.png"
    purchase_cost = 20

class ProjectManager(SatisfiableEntity):
    _icon = "data/graphics/project-manager.png"
    satisfaction_check_type = 'router'
    satisfaction_check_radius = 30
    satisfaction_check_threshold = 1
    upkeep = 3000

class Snacks(BaseEntity):
    _icon = "data/graphics/snacks.png"

class Router(BaseEntity):
    _icon = "data/graphics/router.png"
    purchase_cost = 100

class Breaker(SatisfiableEntity):
    _icon = "data/graphics/breaker.png"
    _icon_broken = "data/graphics/breaker-broken.png"
    satisfaction_check_type = 'breaker'
    satisfaction_check_radius = 1
    satisfaction_check_threshold = 5
    bar1_hidden = 1
    is_satisfied = 1
    warning_hidden = 0
    breaker_strength = 1000
    purchase_cost = 500

    def satisfaction_check(self, grid):
        # Use DRY proximity check for unbroken breakers in radius 1 (including self)
        count = self.count_entities_in_proximity(
            grid, Breaker, 1, predicate=lambda e: getattr(e, 'is_broken', 0) == 0
        )
        if count >= 5:
            self.is_risky = 1
            # Roll 10% chance to break
            if random.random() < 0.1:
                self.has_bar1 = 0
                self.breaker_strength = 0
                self.is_broken = 1
                self.is_risky = 0
                self.is_satisfied = 0
                self.state = "Bad"
                play_breaker_break_sound()
                return
            self.is_satisfied = 1
            self.state = "Mid"
        else:
            self.is_risky = 0
            self.is_satisfied = 1
            self.state = "Good"
