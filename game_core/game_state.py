# Singleton class for game state
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
        return cls._instance

    def summarize_entities(self, grid):
        """
        Returns a list of dicts summarizing all entities on the grid and their public properties.
        """
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

    def count_employees(self, grid):
        """
        Returns the number of entities on the grid with is_person == 1.
        """
        count = 0
        for row in grid:
            for entity in row:
                if entity is not None and getattr(entity, 'is_person', 0) == 1:
                    count += 1
        return count

    def count_breaker_strength(self, grid):
        """
        Returns the sum of breaker_strength for all entities on the grid that have this attribute.
        """
        total = 0
        for row in grid:
            for entity in row:
                if entity is not None and hasattr(entity, 'breaker_strength'):
                    total += getattr(entity, 'breaker_strength', 0)
        return total

    def count_risky_entities(self, grid):
        """
        Returns the number of entities on the grid with is_risky == 1.
        """
        count = 0
        for row in grid:
            for entity in row:
                if entity is not None and getattr(entity, 'is_risky', 0) == 1:
                    count += 1
        return count

    def count_broken_entities(self, grid):
        """
        Returns the number of entities on the grid with is_risky == 1.
        """
        count = 0
        for row in grid:
            for entity in row:
                if entity is not None and getattr(entity, 'is_broken', 0) == 1:
                    count += 1
        return count

    def count_power_drain(self, grid):
        """
        Returns the sum of power_drain for all entities on the grid that have this attribute.
        """
        total = 0
        for row in grid:
            for entity in row:
                if entity is not None and hasattr(entity, 'power_drain'):
                    total += getattr(entity, 'power_drain', 0)
        return total

    def update_totals_from_grid(self, grid):
        """
        Updates all global total_* variables based on the current grid state.
        Call this whenever the grid changes.
        """
        self.total_employees = self.count_employees(grid)
        self.total_power_drain = self.count_power_drain(grid)
        self.total_breaker_strength = self.count_breaker_strength(grid)
        self.total_risky_entities = self.count_risky_entities(grid)
        self.total_broken_entities = self.count_broken_entities(grid)

    def get_totals_dict(self):
        """
        Returns a dict of the current values of all global total_* variables for debug or UI use.
        """
        return {
            'total_money': self.total_money,
            'total_power_drain': self.total_power_drain,
            'total_breaker_strength': self.total_breaker_strength,
            'total_employees': self.total_employees,
            'total_risky_entities': self.total_risky_entities,
            'total_broken_entities': self.total_broken_entities,
            'is_internet_online': self.is_internet_online,
            'is_wifi_online': self.is_wifi_online,
        }

# Module-level helper functions for compatibility

def get_totals_dict():
    """
    Returns a dict of the current values of all global total_* variables for debug or UI use.
    """
    return GameState().get_totals_dict()

def update_totals_from_grid(grid):
    """
    Updates all global total_* variables based on the current grid state.
    Call this whenever the grid changes.
    """
    GameState().update_totals_from_grid(grid)

# Usage: state = GameState()
# state.total_money += 100
# state.update_totals_from_grid(grid)

