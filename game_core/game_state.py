# Global game state variables

total_money = 10000
total_power_drain = 0
total_breaker_strength = 0
total_employees = 0
total_risky_entities = 0
total_broken_entities = 0
is_internet_online = 1
is_wifi_online = 1

def summarize_entities(grid):
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

def count_employees(grid):
    """
    Returns the number of entities on the grid with is_person == 1.
    """
    count = 0
    for row in grid:
        for entity in row:
            if entity is not None and getattr(entity, 'is_person', 0) == 1:
                count += 1
    return count

def sum_breaker_strength(grid):
    """
    Returns the sum of breaker_strength for all entities on the grid that have this attribute.
    """
    total = 0
    for row in grid:
        for entity in row:
            if entity is not None and hasattr(entity, 'breaker_strength'):
                total += getattr(entity, 'breaker_strength', 0)
    return total

def count_risky_entities(grid):
    """
    Returns the number of entities on the grid with is_risky == 1.
    """
    count = 0
    for row in grid:
        for entity in row:
            if entity is not None and getattr(entity, 'is_risky', 0) == 1:
                count += 1
    return count

def count_broken_entities(grid):
    """
    Returns the number of entities on the grid with is_risky == 1.
    """
    count = 0
    for row in grid:
        for entity in row:
            if entity is not None and getattr(entity, 'is_broken', 0) == 1:
                count += 1
    return count

def sum_power_drain(grid):
    """
    Returns the sum of power_drain for all entities on the grid that have this attribute.
    """
    total = 0
    for row in grid:
        for entity in row:
            if entity is not None and hasattr(entity, 'power_drain'):
                total += getattr(entity, 'power_drain', 0)
    return total
