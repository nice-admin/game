from .entity_base import *
import random
from game_other.audio import play_breaker_break_sound

# --- Entity subclasses ---
class Computer(SatisfiableEntity):
    _icon = "data/graphics/computer.png"

    has_satisfaction_check = True
    has_bar2 = True
    power_drain = 1  # Set as class attribute

    satisfaction_check_type = 'outlet'

class Monitor(SatisfiableEntity):
    _icon = "data/graphics/monitor.png"

    has_bar2 = False
    has_satisfaction_check = True
    satisfaction_check_type = 'computer'
    satisfaction_check_radius = 1
    satisfaction_check_threshold = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only count computers that are satisfied
        self.satisfaction_check_predicate = lambda e: getattr(e, 'is_satisfied', False)

class Artist(SatisfiableEntity):
    _icon = "data/graphics/artist.png"
    has_satisfaction_check = True
    satisfaction_check_type = 'router'
    satisfaction_check_radius = 30
    satisfaction_check_threshold = 1

    is_person = True

class EspressoMachine(BaseEntity):
    _icon = "data/graphics/coffee-machine.png"

class Outlet(BaseEntity):
    _icon = "data/graphics/outlet.png"

class ProjectManager(SatisfiableEntity):
    _icon = "data/graphics/project-manager.png"
    has_satisfaction_check = True
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
    has_satisfaction_check = True
    satisfaction_check_type = 'breaker'
    satisfaction_check_radius = 1
    satisfaction_check_threshold = 5
    bar1_hidden = True
    is_satisfied = True
    warning_hidden = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.breaker_strength = 5
        self.satisfaction_check_predicate = lambda e: not getattr(e, 'is_broken', True)

    def on_satisfaction_check(self, count=1, threshold=1):
        if not getattr(self, 'is_broken', False) and count >= threshold:
            self.is_risky = 1
            self.is_satisfied = 0
            if random.random() < 0.1:
                self.is_broken = True
                self.is_risky = 0
                play_breaker_break_sound()
        else:
            self.is_risky = 0
            self.is_satisfied = 1
        # Do not call super().on_satisfaction_check, as we handle is_satisfied here
