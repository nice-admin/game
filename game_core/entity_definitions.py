from .entity_base import *
import random
from game_other.audio import play_breaker_break_sound
from game_core.config import resource_path

# region Tech
class ComputerT1(ComputerEntity):
    _icon = resource_path("data/graphics/computer-basic.png")
    power_drain = 200
    upkeep = 50


class ComputerT2(ComputerEntity):
    _icon = resource_path("data/graphics/computer-advanced.png")
    tier = 2
    power_drain = 400
    upkeep = 100
    satisfaction_check_type = 'outlet'
    satisfaction_check_gamestate = 'is_nas_online'

class Macbook(LaptopEntity):
    _icon = resource_path("data/graphics/macbook.png")
    tier = 3
    upkeep = 100
    power_drain = 50

class BasicMonitor(MonitorEntity):
    _icon = resource_path("data/graphics/basic-monitor.png")
    upkeep = 20
    power_drain = 20

class AdvancedMonitor(MonitorEntity):
    _icon = resource_path("data/graphics/advanced-monitor.png")
    tier = 2
    upkeep = 40
    power_drain = 40

class TV(BaseEntity):
    _icon = resource_path("data/graphics/entities/tv.png")
    tier = 1
    upkeep = 10
    power_drain = 40

# region Humans
class Artist(PersonEntity):
    _icon = resource_path("data/graphics/artist.png")
    has_special = 1
    satisfaction_check_type = MonitorEntity
    satisfaction_check_radius = 1
    satisfaction_check_threshold = 1
    is_person = 1
    upkeep = 2000

    def _update_special(self, grid):
        prev_special = self.special if hasattr(self, 'special') else None
        prev_special_timer = self.special_timer if hasattr(self, 'special_timer') else None
        super()._update_special(grid)
        # Increment artist_progress_current if special just completed
        if prev_special is not None and prev_special >= 0.99:
            if (self.special is None or (self.special == 0.0 and self.special_timer == 0)):
                gs = GameState()
                gs.cap_artist_progress_current()
                gs.cap_render_progress_allowed()


class TechnicalDirector(PersonEntity):
    _icon = resource_path("data/graphics/entities/technical-director.png")
    satisfaction_check_type = 'router'
    satisfaction_check_radius = 30
    satisfaction_check_threshold = 1
    upkeep = 2000

class ProjectManager(SatisfiableEntity):
    _icon = resource_path("data/graphics/project-manager.png")
    satisfaction_check_type = 'router'
    satisfaction_check_radius = 30
    satisfaction_check_threshold = 1
    upkeep = 2000

class AccountManager(SatisfiableEntity):
    _icon = resource_path("data/graphics/account-manager.png")
    satisfaction_check_type = 'router'
    satisfaction_check_radius = 30
    satisfaction_check_threshold = 1
    upkeep = 2000


# region Utility
class EspressoMachine(UtilityEntity):
    _icon = resource_path("data/graphics/coffee-machine.png")
    purchase_cost = 500

class Outlet(UtilityEntity):
    _icon = resource_path("data/graphics/outlet.png")
    has_satisfaction_check = 0
    purchase_cost = 50

class Snacks(UtilityEntity):
    _icon = resource_path("data/graphics/snacks.png")

class Router(UtilityEntity):
    _icon = resource_path("data/graphics/router.png")
    purchase_cost = 100

class AirConditioner(SatisfiableEntity):
    _icon = resource_path("data/graphics/ac.png")
    has_special = 0
    power_drain = 100
    has_sat_check_bar_hidden = 1
    purchase_cost = 5000

    def do_on_satisfaction_check(self, grid):
        self.state = 'Good'
        self.power_drain = self._intended_power_drain
        # DEBUG: Print before and after temperature
        from game_core.game_state import GameState
        gs = GameState()
        print(f"[AC] Before: gs.temperature={getattr(gs, 'temperature', None)}")
        if hasattr(gs, 'temperature'):
            if gs.temperature > 23:
                gs.temperature = max(23, gs.temperature - 0.2)
        print(f"[AC] After: gs.temperature={getattr(gs, 'temperature', None)}")
        return 1


class Breaker(SatisfiableEntity):
    _icon = resource_path("data/graphics/breaker.png")
    _icon_broken = resource_path("data/graphics/breaker-broken.png")
    satisfaction_check_type = 'breaker'
    satisfaction_check_radius = 1
    satisfaction_check_threshold = 4
    has_sat_check_bar_hidden = 1
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
    _icon = resource_path("data/graphics/flower-pot.png")


class Cactus(DecorationEntity):
    _icon = resource_path("data/graphics/cactus.png")