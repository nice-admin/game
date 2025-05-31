class GameState:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameState, cls).__new__(cls)
            cls._instance.game_time_seconds = 0
            cls._instance.game_time_days = 0
            cls._instance.total_money = 20000
            cls._instance.total_upkeep = 0
            cls._instance.total_power_drain = 0
            cls._instance.total_breaker_strength = 0
            cls._instance.total_employees = 0
            cls._instance.total_risky_entities = 0
            cls._instance.total_broken_entities = 0
            cls._instance.is_internet_online = 1
            cls._instance.is_wifi_online = 1
            cls._instance.is_nas_online = 1
            cls._instance.artist_progress_current = 0
            cls._instance.artist_progress_goal = 0
            cls._instance.render_progress_current = 0
            cls._instance.render_progress_allowed = 0
            cls._instance.render_progress_goal = 0
            cls._instance.total_shots_finished = 0
            cls._instance.total_shots_goal = 0
            cls._instance.current_job_finished = 1
            cls._instance.jobs_finished = 0
            cls._instance.job_id = 0
            cls._instance.current_construction_class = None  # Track what the user is currently constructing
        return cls._instance

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
        self.total_upkeep = self.count_upkeep(grid)
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

    def cap_render_progress_allowed(self):
        if self.artist_progress_current > 0 and self.artist_progress_current % 10 == 0:
            self.render_progress_allowed = self.artist_progress_current * 10

    def cap_artist_progress_current(self):
        if self.artist_progress_current < self.artist_progress_goal:
            self.artist_progress_current += 1
        else:
            self.artist_progress_current = self.artist_progress_goal

def get_totals_dict():
    return GameState().get_totals_dict()

def update_totals_from_grid(grid):
    GameState().update_totals_from_grid(grid)
