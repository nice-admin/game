import pygame
from game_core.entity_definitions import *
import threading
import time
import random

def handle_testing_layout(event, grid, entity_states, GRID_WIDTH, GRID_HEIGHT):
    """
    When INSERT key is pressed, spawn 5 rows of 20 Breakers (with a space below), a line of 20 Outlets, a line of 20 Computers, a line of 20 Monitors below it,
    and a line of 20 Artists below the Monitors (with 50% chance of being one row lower),
    centered horizontally and vertically in the grid, with a random delay (0-2s) since the key press for each entity.
    Leaves one empty space halfway in each line.
    """
    if event.type == pygame.KEYDOWN and event.key == pygame.K_INSERT:
        n = min(40, GRID_WIDTH)
        x_start = (GRID_WIDTH - n) // 2
        y_computer = GRID_HEIGHT // 2 - 1
        y_monitor = y_computer + 1
        y_artist_base = y_monitor + 1
        y_outlet = y_computer - 1
        y_breaker_base = y_outlet - 2  # Start of breaker rows (topmost)
        mid = n // 2  # Index to skip (leave empty)

        def spawn_entity(entity_cls, x, y):
            delay = random.uniform(0, 2)
            time.sleep(delay)
            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT and grid[y][x] is None:
                entity = entity_cls(x, y)
                grid[y][x] = entity
                if entity_states is not None:
                    entity_states.add_entity(entity)
                if hasattr(entity, 'on_built'):
                    entity.on_built()

        for i in range(n):
            if i == mid:
                continue  # Leave this space empty
            x = x_start + i
            # 5 rows of Breakers (with a space below)
            for row in range(5):
                y_breaker = y_breaker_base - row
                if 0 <= x < GRID_WIDTH and 0 <= y_breaker < GRID_HEIGHT and grid[y_breaker][x] is None:
                    threading.Thread(target=spawn_entity, args=(Breaker, x, y_breaker), daemon=True).start()
            # Outlets (below the space)
            if 0 <= x < GRID_WIDTH and 0 <= y_outlet < GRID_HEIGHT and grid[y_outlet][x] is None:
                threading.Thread(target=spawn_entity, args=(Outlet, x, y_outlet), daemon=True).start()
            # Computers
            if 0 <= x < GRID_WIDTH and 0 <= y_computer < GRID_HEIGHT and grid[y_computer][x] is None:
                threading.Thread(target=spawn_entity, args=(BasicComputer, x, y_computer), daemon=True).start()
            # Monitors
            if 0 <= x < GRID_WIDTH and 0 <= y_monitor < GRID_HEIGHT and grid[y_monitor][x] is None:
                threading.Thread(target=spawn_entity, args=(Monitor, x, y_monitor), daemon=True).start()
            # Artists (50% chance to be one row lower)
            y_artist = y_artist_base + (1 if random.random() < 0.5 and y_artist_base + 1 < GRID_HEIGHT else 0)
            if 0 <= x < GRID_WIDTH and 0 <= y_artist < GRID_HEIGHT and grid[y_artist][x] is None:
                threading.Thread(target=spawn_entity, args=(Artist, x, y_artist), daemon=True).start()
            # ProjectManagers (30% chance, two rows below the base Artist row)
            y_pm = y_artist_base + 2
            if y_pm < GRID_HEIGHT and random.random() < 0.3 and grid[y_pm][x] is None:
                threading.Thread(target=spawn_entity, args=(ProjectManager, x, y_pm), daemon=True).start()
        print(f"Spawn threads for 5x{n-1} Breakers at y={y_breaker_base} to y={y_breaker_base-4}, (space), {n-1} Outlets at y={y_outlet}, {n-1} Computers at y={y_computer}, {n-1} Monitors at y={y_monitor}, and {n-1} Artists at y={y_artist_base} or y={y_artist_base+1}, centered, with one empty space at index {mid}. Also, up to {int((n-1)*0.3)} ProjectManagers at y={y_pm} (30% chance per cell, skipping the empty space).")
