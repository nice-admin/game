import random
from game_core.config import GAME_AREA_WIDTH, GAME_AREA_HEIGHT
from game_core.entity_definitions import Wall

def generate_rooms(area_width, area_height, min_room_size=6, max_room_size=16):
    """
    Recursively divides the area into rectangular rooms.
    Returns a list of rooms, each as (x, y, w, h).
    """
    rooms = []

    def split(x, y, w, h):
        # Stop splitting if room is small enough
        if w <= max_room_size and h <= max_room_size and w >= min_room_size and h >= min_room_size:
            rooms.append((x, y, w, h))
            return
        # Decide split direction
        if w > h:
            # Vertical split
            if w < 2 * min_room_size:
                rooms.append((x, y, w, h))
                return
            split_w = random.randint(min_room_size, w - min_room_size)
            split(x, y, split_w, h)
            split(x + split_w, y, w - split_w, h)
        else:
            # Horizontal split
            if h < 2 * min_room_size:
                rooms.append((x, y, w, h))
                return
            split_h = random.randint(min_room_size, h - min_room_size)
            split(x, y, w, split_h)
            split(x, y + split_h, w, h - split_h)

    split(0, 0, area_width, area_height)
    return rooms

def construct_floor_plan(grid):
    """
    Fills the grid with FloorTile entities for each room.
    """
    rooms = generate_rooms(GAME_AREA_WIDTH, GAME_AREA_HEIGHT)
    for room in rooms:
        x, y, w, h = room
        # Draw bottom walls
        for gx in range(x, x + w):
            gy = y + h - 1
            if grid[gy][gx] is None:
                grid[gy][gx] = Wall(x=gx, y=gy)
        # Draw right walls
        for gy in range(y, y + h):
            gx = x + w - 1
            if grid[gy][gx] is None:
                grid[gy][gx] = Wall(x=gx, y=gy)
        # Draw top walls only for rooms at the top edge
        if y == 0:
            for gx in range(x, x + w):
                if grid[y][gx] is None:
                    grid[y][gx] = Wall(x=gx, y=y)
        # Draw left walls only for rooms at the left edge
        if x == 0:
            for gy in range(y, y + h):
                if grid[gy][x] is None:
                    grid[gy][x] = Wall(x=x, y=gy)
