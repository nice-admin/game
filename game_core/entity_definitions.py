from .entity_base import *
import random
from game_other.audio import play_breaker_break_sound
from game_core.config import resource_path

# region Tech
class ComputerT1(ComputerEntity):
    _icon = resource_path("data/graphics/computer-basic.png")
    display_name = 'Basic Computer'
    power_drain = 200
    upkeep = 50
    heating_multiplier = 2


class ComputerT2(ComputerEntity):
    _icon = resource_path("data/graphics/computer-advanced.png")
    display_name = 'Gaming Computer'
    tier = 2
    power_drain = 400
    upkeep = 100
    heating_multiplier = 1

class Macbook(LaptopEntity):
    _icon = resource_path("data/graphics/macbook.png")
    tier = 3
    upkeep = 100
    power_drain = 50

<<<<<<< HEAD
    def satisfaction_check(self, grid):
=======
    def on_sat_check_finish(self):
>>>>>>> satisfaction-check-overhaul
        from game_core.game_state import GameState
        gs = GameState()
        value = 1 if getattr(gs, "is_wifi_online", 0) == 1 else 0
        self.is_satisfied = value
        return value

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
    has_project_manager = 0
    upkeep = 2000

    def on_special_finish(self):
        gs = GameState()
        multiplier = 2 if getattr(self, 'has_project_manager', 0) else 1
        gs.increment_current_artist_progress(multiplier=multiplier)
        gs.calculate_render_progress_allowed()

    def check_project_manager_proximity(self, grid):
        found = 0
        for row in grid:
            for entity in row:
                if entity is not None and entity.__class__.__name__ == 'ProjectManager':
                    if abs(entity.x - self.x) <= 4 and abs(entity.y - self.y) <= 4:
                        found = 1
                        break
            if found:
                break
        self.has_project_manager = found

    def update(self, grid):
        super().update(grid)
        self.check_project_manager_proximity(grid)


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

<<<<<<< HEAD
    def satisfaction_check(self, grid):
        self.state = 'Good'
        self.power_drain = self._intended_power_drain
        # DEBUG: Print before and after temperature
=======
    def on_sat_check_finish(self):
        self.is_satisfied = 1
        self.state = "Good"
>>>>>>> satisfaction-check-overhaul
        from game_core.game_state import GameState
        gs = GameState()
        if gs.temperature > 23:
            gs.temperature = max(23, gs.temperature - 0.25)



class Humidifier(SatisfiableEntity):
    _icon = resource_path("data/graphics/entities/humidifier.png")
    has_special = 0
    power_drain = 20
    has_sat_check_bar_hidden = 1
    purchase_cost = 500

    def satisfaction_check(self, grid):
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