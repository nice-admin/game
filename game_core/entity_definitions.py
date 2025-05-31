from .entity_base import *
import random
from game_other.audio import play_breaker_break_sound

# region Tech
class BasicComputer(ComputerEntity):
    _icon = "data/graphics/computer-basic.png"
    has_special = 1
    power_drain = 200
    upkeep = 50


class AdvancedComputer(ComputerEntity):
    _icon = "data/graphics/computer-advanced.png"
    tier = 2
    has_special = 1
    power_drain = 400
    upkeep = 100
    satisfaction_check_type = 'outlet'
    satisfaction_check_gamestate = 'is_nas_online'

class Macbook(LaptopEntity):
    _icon = "data/graphics/macbook.png"
    tier = 3
    upkeep = 100
    power_drain = 50

class BasicMonitor(MonitorEntity):
    _icon = "data/graphics/basic-monitor.png"
    upkeep = 20
    power_drain = 20

class AdvancedMonitor(MonitorEntity):
    _icon = "data/graphics/advanced-monitor.png"
    tier = 2
    upkeep = 40
    power_drain = 40

# region Humans
class Artist(PersonEntity):
    _icon = "data/graphics/artist.png"
    satisfaction_check_type = BasicMonitor
    satisfaction_check_radius = 1
    satisfaction_check_threshold = 1
    is_person = 1
    upkeep = 2000

class ProjectManager(SatisfiableEntity):
    _icon = "data/graphics/project-manager.png"
    satisfaction_check_type = 'router'
    satisfaction_check_radius = 30
    satisfaction_check_threshold = 1
    upkeep = 3000

# region Utility
class EspressoMachine(UtilityEntity):
    _icon = "data/graphics/coffee-machine.png"

class Outlet(UtilityEntity):
    _icon = "data/graphics/outlet.png"
    has_satisfaction_check = 0
    purchase_cost = 50

class Snacks(UtilityEntity):
    _icon = "data/graphics/snacks.png"

class Router(UtilityEntity):
    _icon = "data/graphics/router.png"
    purchase_cost = 100

class Ac(UtilityEntity):
    _icon = "data/graphics/ac.png"
    purchase_cost = 1000

class Breaker(SatisfiableEntity):
    _icon = "data/graphics/breaker.png"
    _icon_broken = "data/graphics/breaker-broken.png"
    satisfaction_check_type = 'breaker'
    satisfaction_check_radius = 1
    satisfaction_check_threshold = 4
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
        if count >= self.satisfaction_check_threshold:
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

# region Decoration

class FlowerPot(DecorationEntity):
    _icon = "data/graphics/flower-pot.png"


class Cactus(DecorationEntity):
    _icon = "data/graphics/cactus.png"