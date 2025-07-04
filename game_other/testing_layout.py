import pygame
from game_core.entity_definitions import *
import threading
import time
import random
import inspect

class LineSpawn:
    start_y = 0  # Class variable to define the starting y position for all lines

    def __init__(self, entity_cls, y_position, vertical_spread=0.0, on_entity_placed=None, probability=1.0):
        self.entity_cls = entity_cls
        self.y_position = LineSpawn.start_y + y_position  # Use class variable for offset
        self.vertical_spread = vertical_spread  # 0.0 = no spread, 1.0 = up to 1 row below
        self.n = 10
        self.on_entity_placed = on_entity_placed
        self.probability = probability  # Chance to spawn at each position (default 1.0 = 100%)
        # If entity_cls is a class and has subclasses, gather them
        if inspect.isclass(entity_cls):
            self.subclasses = [cls for cls in entity_cls.__subclasses__() if cls is not entity_cls]
        else:
            self.subclasses = []

    def spawn(self, grid, entity_states, GRID_WIDTH, GRID_HEIGHT):
        x_start = (GRID_WIDTH - self.n) // 2
        mid = self.n // 2
        for i in range(self.n):
            if i == mid:
                continue  # Leave this space empty
            x = x_start + i
            y = self.y_position
            # Apply vertical spread
            if self.vertical_spread > 0.0 and random.random() < self.vertical_spread and y + 1 < GRID_HEIGHT:
                y = y + 1
            # Probability check
            if random.random() > self.probability:
                continue
            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT and grid[y][x] is None:
                # If subclasses exist, pick one at random, else use entity_cls
                if self.subclasses:
                    chosen_cls = random.choice(self.subclasses)
                else:
                    chosen_cls = self.entity_cls
                threading.Thread(target=self._spawn_entity, args=(chosen_cls, x, y, grid, entity_states), daemon=True).start()

    def _spawn_entity(self, entity_cls, x, y, grid, entity_states):
        delay = random.uniform(0, 2)
        time.sleep(delay)
        if 0 <= x < len(grid[0]) and 0 <= y < len(grid) and grid[y][x] is None:
            entity = entity_cls(x, y)
            grid[y][x] = entity
            if entity_states is not None:
                entity_states.add_entity(entity)
            if hasattr(entity, 'on_built'):
                entity.on_built()
            # Notify grid change if callback is set
            if self.on_entity_placed:
                self.on_entity_placed()

def handle_testing_layout(event, grid, entity_states, GRID_WIDTH, GRID_HEIGHT, on_entity_placed=None):
    """
    When INSERT key is pressed, spawn 5 rows of 40 Breakers (with a space below), a line of 40 Outlets, a line of 40 Computers, a line of 40 Monitors below it,
    and a line of 40 Artists below the Monitors (with vertical spread), centered horizontally and vertically in the grid, with a random delay (0-2s) for each entity.
    Leaves one empty space halfway in each line.
    """
    if event.type == pygame.KEYDOWN and event.key == pygame.K_INSERT:
        # Set gs.software_choice to a random value between 1 and 3
        gs = GameState()
        gs.software_choice = random.randint(1, 3)
        n = 40
        LineSpawn.start_y = 8  # Set the starting y position for this test layout
        line_spawns = [
            LineSpawn(Breaker, 4, on_entity_placed=on_entity_placed),
            LineSpawn(Outlet, 6, on_entity_placed=on_entity_placed),
            LineSpawn(ComputerEntity, 7, on_entity_placed=on_entity_placed),
            LineSpawn(MonitorEntity, 8, on_entity_placed=on_entity_placed),
            LineSpawn(Artist, 9, vertical_spread=0.5, on_entity_placed=on_entity_placed),
            LineSpawn(ProjectManager, 11, on_entity_placed=on_entity_placed, probability=0.3),
            LineSpawn(LaptopEntity, 12, on_entity_placed=on_entity_placed, probability=0.3),
            LineSpawn(ComputerEntity, 16, on_entity_placed=on_entity_placed),
            LineSpawn(Outlet, 17, on_entity_placed=on_entity_placed),
            LineSpawn(ComputerEntity, 18, on_entity_placed=on_entity_placed),
            LineSpawn(Breaker, 19, on_entity_placed=on_entity_placed),
            LineSpawn(Breaker, 20, on_entity_placed=on_entity_placed),
        ]
        for line in line_spawns:
            line.spawn(grid, entity_states, GRID_WIDTH, GRID_HEIGHT)
        # Example: Randomly spawn all DecorationEntity subclasses across the grid
        def all_subclasses(cls):
            return set(cls.__subclasses__()).union(
                [s for c in cls.__subclasses__() for s in all_subclasses(c)]
            )
        class_list = list(all_subclasses(DecorationEntity))
        class_list.append(AirConditioner)
        class_list.append(Router)
        class_list.append(EspressoMachine)
        RandomSpawn(class_list, probability=0.01, on_entity_placed=on_entity_placed).spawn(grid, entity_states, GRID_WIDTH, GRID_HEIGHT)
        x_start = (GRID_WIDTH - n) // 2
        y_pm = LineSpawn.start_y + 11  # 2 rows below the base Artist row (start_y + 9)
        for i in range(n):
            if i == n // 2:
                continue
            x = x_start + i
            if y_pm < GRID_HEIGHT and random.random() < 0.3 and grid[y_pm][x] is None:
                threading.Thread(target=LineSpawn(ProjectManager, y_pm, on_entity_placed=on_entity_placed)._spawn_entity, args=(x, y_pm, grid, entity_states), daemon=True).start()
        print(f"Spawned 5x{n-1} Breakers (y={LineSpawn.start_y}-{{LineSpawn.start_y+4}}), {n-1} Outlets (y={LineSpawn.start_y+6}), {n-1} Computers, {n-1} Monitors, {n-1} Artists (spread), {n-1} + {n-1} extra Computers, and up to {int((n-1)*0.3)} ProjectManagers.")

class RandomSpawn:
    def __init__(self, entity_classes, probability=0.01, on_entity_placed=None):
        self.entity_classes = entity_classes  # List of entity classes to choose from
        self.probability = probability        # Chance to spawn on each tile
        self.on_entity_placed = on_entity_placed

    def spawn(self, grid, entity_states, GRID_WIDTH, GRID_HEIGHT):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if grid[y][x] is None and random.random() < self.probability:
                    chosen_cls = random.choice(self.entity_classes)
                    threading.Thread(target=self._spawn_entity, args=(chosen_cls, x, y, grid, entity_states), daemon=True).start()

    def _spawn_entity(self, entity_cls, x, y, grid, entity_states):
        delay = random.uniform(0, 2)
        time.sleep(delay)
        if 0 <= x < len(grid[0]) and 0 <= y < len(grid) and grid[y][x] is None:
            entity = entity_cls(x, y)
            grid[y][x] = entity
            if entity_states is not None:
                entity_states.add_entity(entity)
            if hasattr(entity, 'on_built'):
                entity.on_built()
            if self.on_entity_placed:
                self.on_entity_placed()
