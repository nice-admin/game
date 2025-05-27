class GameState:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameState, cls).__new__(cls)
            cls._instance.total_money = 10000
            cls._instance.total_power_drain = 0
            cls._instance.total_breaker_strength = 0
            cls._instance.total_employees = 0
            cls._instance.total_risky_entities = 0
            cls._instance.total_broken_entities = 0
            cls._instance.is_internet_online = 1
            cls._instance.is_wifi_online = 1
            cls._instance.is_nas_online = 1
            cls._instance.render_progress = 0
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

    def update_totals_from_grid(self, grid):
        self.total_employees = self.count_employees(grid)
        self.total_power_drain = self.count_power_drain(grid)
        self.total_breaker_strength = self.count_breaker_strength(grid)
        self.total_risky_entities = self.count_risky_entities(grid)
        self.total_broken_entities = self.count_broken_entities(grid)

    def get_totals_dict(self):
        return {
            'total_money': self.total_money,
            'total_power_drain': self.total_power_drain,
            'total_breaker_strength': self.total_breaker_strength,
            'total_employees': self.total_employees,
            'total_risky_entities': self.total_risky_entities,
            'total_broken_entities': self.total_broken_entities,
            'is_internet_online': self.is_internet_online,
            'is_wifi_online': self.is_wifi_online,
            'is_nas_online': self.is_nas_online,  # Added NAS status
        }

def get_totals_dict():
    return GameState().get_totals_dict()

def update_totals_from_grid(grid):
    GameState().update_totals_from_grid(grid)
