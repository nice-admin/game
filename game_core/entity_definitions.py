from .entity_base import *
import random
from game_other.audio import play_breaker_break_sound

# --- Entity subclasses ---
class BasicComputer(ComputerEntity):
    _icon = "data/graphics/computer-basic.png"

    has_bar2 = True
    power_drain = 1  # Set as class attribute

    satisfaction_check_type = 'outlet'

class Monitor(SatisfiableEntity):
    _icon = "data/graphics/monitor.png"
    has_bar2 = False
    satisfaction_check_type = ComputerEntity
    satisfaction_check_radius = 1
    satisfaction_check_threshold = 1

class Artist(SatisfiableEntity):
    _icon = "data/graphics/artist.png"
    satisfaction_check_type = 'monitor'
    satisfaction_check_radius = 1
    satisfaction_check_threshold = 1
    is_person = True

class EspressoMachine(BaseEntity):
    _icon = "data/graphics/coffee-machine.png"

class Outlet(BaseEntity):
    _icon = "data/graphics/outlet.png"

class ProjectManager(SatisfiableEntity):
    _icon = "data/graphics/project-manager.png"
    satisfaction_check_type = 'router'
    satisfaction_check_radius = 30
    satisfaction_check_threshold = 1

class Snacks(BaseEntity):
    _icon = "data/graphics/snacks.png"

class Router(BaseEntity):
    _icon = "data/graphics/router.png"   

class Breaker(SatisfiableEntity):
    _icon = "data/graphics/breaker.png"
    _icon_broken = "data/graphics/breaker-broken.png"
    satisfaction_check_type = 'breaker'
    satisfaction_check_radius = 1
    satisfaction_check_threshold = 5
    bar1_hidden = True
    is_satisfied = True
    warning_hidden = True
    breaker_strength = 5

    def on_satisfaction_check(self, count=1, threshold=1):
        if getattr(self, 'is_broken', False):
            self.is_risky = 0
            self.is_satisfied = 0
            return
        self.is_risky = int(count >= threshold)
        self.is_satisfied = 1
        if self.is_risky and random.random() < 0.1:
            self.breaker_strength = 0
            self.is_broken = True
            self.is_risky = 0
            self.is_satisfied = 0
            play_breaker_break_sound()
        # Do not call super().on_satisfaction_check, as we handle is_satisfied here

    def check_satisfaction(self, grid):
        # Only count breakers with is_broken == 0
        entity_type = getattr(self, 'satisfaction_check_type', None)
        radius = getattr(self, 'satisfaction_check_radius', 2)
        threshold = getattr(self, 'satisfaction_check_threshold', 1)
        count = self.count_entities_in_proximity(
            grid, entity_type, radius, predicate=lambda e: getattr(e, 'is_broken', 0) == 0
        )
        self.on_satisfaction_check(count, threshold)
        return self.is_satisfied
