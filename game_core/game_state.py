import random

SUPPLIES_MIN = 4
SUPPLIES_MAX = 9

class GameState:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameState, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, '_initialized', False):
            return
        self.game_time_seconds = 0
        self.game_time_days = 0
        self.total_money = 20000
        self.total_upkeep = 0
        self.total_power_drain = 0
        self.total_breaker_strength = 0
        self.total_employees = 0
        self.total_risky_entities = 0
        self.total_broken_entities = 0
        self.is_internet_online = 1
        self.is_wifi_online = 1
        self.is_nas_online = 1
        self.temperature = 23
        self.office_quality = 1
        self.artist_progress_required_per_shot = 15
        self.render_progress_required_per_shot = 50
        self.artist_progress_current = 0
        self.artist_progress_goal = 0
        self.render_progress_current = 0
        self.render_progress_allowed = 0
        self.render_progress_goal = 0
        self.total_shots_finished = 0
        self.total_shots_goal = 0
        self.current_job_finished = 1
        self.jobs_finished = 0
        self.job_id = 0
        self.job_budget = 0
        self.current_construction_class = None
        self._initialized = True
        # supplies
        self.total_cables = random.randint(SUPPLIES_MIN, SUPPLIES_MAX)
        self.total_mouses = random.randint(SUPPLIES_MIN, SUPPLIES_MAX)
        self.total_keyboards = random.randint(SUPPLIES_MIN, SUPPLIES_MAX)
        self.total_coffee_beans = random.randint(SUPPLIES_MIN, SUPPLIES_MAX)
        self.total_milk = random.randint(SUPPLIES_MIN, SUPPLIES_MAX)
        self.total_sugar = random.randint(SUPPLIES_MIN, SUPPLIES_MAX)
        self.total_ibalgin = random.randint(SUPPLIES_MIN, SUPPLIES_MAX)
        self.total_bandages = random.randint(SUPPLIES_MIN, SUPPLIES_MAX)
        self.total_pcr_test = random.randint(SUPPLIES_MIN, SUPPLIES_MAX)


    def summarize_entities(self, grid):
        summary = []
        for row in grid:
            for entity in row:
                if entity is not None:
                    if hasattr(entity, 'get_public_attrs'):
                        summary.append(entity.get_public_attrs())
                    else:
                        summary.append({
                            k: v for k, v in vars(entity).items()
                            if not k.startswith('_') and not callable(v)
                        })
        return summary

    def _count_entities(self, grid, attr, sum_mode=False):
        count = 0
        for row in grid:
            for entity in row:
                if entity is not None:
                    if sum_mode and hasattr(entity, attr):
                        count += getattr(entity, attr, 0)
                    elif not sum_mode and getattr(entity, attr, 0) == 1:
                        count += 1
        return count

    def count_employees(self, grid):
        return self._count_entities(grid, 'is_person')

    def count_breaker_strength(self, grid):
        return self._count_entities(grid, 'breaker_strength', sum_mode=True)

    def count_risky_entities(self, grid):
        return self._count_entities(grid, 'is_risky')

    def count_broken_entities(self, grid):
        return self._count_entities(grid, 'is_broken')

    def count_power_drain(self, grid):
        return self._count_entities(grid, 'power_drain', sum_mode=True)

    def count_upkeep(self, grid):
        total = 0
        for row in grid:
            for entity in row:
                if entity is not None and hasattr(entity, 'upkeep'):
                    try:
                        val = float(getattr(entity, 'upkeep', 0))
                        if val > 0:
                            total += val
                    except Exception:
                        pass
        return int(round(total))

    def update_totals_from_grid(self, grid):
        self.total_employees = self.count_employees(grid)
        self.total_power_drain = self.count_power_drain(grid)
        self.total_breaker_strength = self.count_breaker_strength(grid)
        self.total_risky_entities = self.count_risky_entities(grid)
        self.total_broken_entities = self.count_broken_entities(grid)
        self.total_upkeep = self.count_upkeep(grid) + 100
        from game_core.gameplay_events import power_outage
        power_outage.trigger()

    def get_totals_dict(self):
        # Return all public (non-callable, non-underscore) attributes as a dict
        return {k: v for k, v in vars(self).items() if not k.startswith('_') and not callable(v)}

    def finish_job(self):
        if (
            self.total_shots_goal == self.total_shots_finished
            and self.total_shots_finished > 0
        ):
            self.jobs_finished += 1
            self.total_shots_goal = 0
            self.total_shots_finished = 0

    def calculate_render_progress_allowed(self):
        # Allow render progress for each full 'shot' of artist progress
        shots_allowed = self.artist_progress_current // self.artist_progress_required_per_shot
        self.render_progress_allowed = shots_allowed * self.render_progress_required_per_shot

    def increment_current_artist_progress(self, multiplier=1):
        if self.artist_progress_current < self.artist_progress_goal:
            self.artist_progress_current = min(self.artist_progress_current + multiplier, self.artist_progress_goal)
        else:
            self.artist_progress_current = self.artist_progress_goal

class EntityStats:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EntityStats, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, '_initialized', False):
            return
        self.reset()
        self._initialized = True

    def reset(self):
        self.total_decor_entities = 0
        self.total_computer_entities = 0
        self.total_coffeemachine_entities = 0  # Track number of coffee machines
        # Add more entity counters as needed

    def update_from_grid(self, grid):
        self.reset()
        from game_core.entity_definitions import DecorationEntity, ComputerEntity, EspressoMachine
        for row in grid:
            for entity in row:
                if isinstance(entity, DecorationEntity):
                    self.total_decor_entities += 1
                if isinstance(entity, ComputerEntity):
                    self.total_computer_entities += 1
                if isinstance(entity, EspressoMachine):
                    self.total_coffeemachine_entities += 1
        # Add more entity type checks as needed

def get_totals_dict():
    return GameState().get_totals_dict()

def update_totals_from_grid(grid):
    GameState().update_totals_from_grid(grid)
