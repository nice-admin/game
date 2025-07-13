import random
from game_core.config import GAME_AREA_WIDTH, GAME_AREA_HEIGHT
from game_core.entity_definitions import Wall, HighlightedWall

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

    # Identify neighboring rooms and highlight separating walls
    def rooms_are_neighbors(r1, r2):
        x1, y1, w1, h1 = r1
        x2, y2, w2, h2 = r2
        # Check for vertical adjacency
        if x1 + w1 == x2 and y1 < y2 + h2 and y1 + h1 > y2:
            return 'vertical', x1 + w1 - 1
        if x2 + w2 == x1 and y2 < y1 + h1 and y2 + h2 > y1:
            return 'vertical', x2 + w2 - 1
        # Check for horizontal adjacency
        if y1 + h1 == y2 and x1 < x2 + w2 and x1 + w1 > x2:
            return 'horizontal', y1 + h1 - 1
        if y2 + h2 == y1 and x2 < x1 + w1 and x2 + w2 > x1:
            return 'horizontal', y2 + h2 - 1
        return None, None

    highlighted_walls = []
    for i, r1 in enumerate(rooms):
        for j, r2 in enumerate(rooms):
            if i >= j:
                continue
            direction, wall_coord = rooms_are_neighbors(r1, r2)
            if direction == 'vertical':
                # Find shared vertical wall tiles
                y_start = max(r1[1], r2[1])
                y_end = min(r1[1] + r1[3], r2[1] + r2[3])
                for gy in range(y_start, y_end):
                    gx = wall_coord
                    if isinstance(grid[gy][gx], Wall):
                        highlighted_walls.append((gx, gy))
                        grid[gy][gx] = Wall(x=gx, y=gy)
            elif direction == 'horizontal':
                x_start = max(r1[0], r2[0])
                x_end = min(r1[0] + r1[2], r2[0] + r2[2])
                for gx in range(x_start, x_end):
                    gy = wall_coord
                    if isinstance(grid[gy][gx], Wall):
                        highlighted_walls.append((gx, gy))
                        grid[gy][gx] = Wall(x=gx, y=gy)

    # Remove corner highlighted walls (with 3 or more neighboring walls)
    def count_wall_neighbors(gx, gy):
        count = 0
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = gx+dx, gy+dy
            if 0 <= nx < GAME_AREA_WIDTH and 0 <= ny < GAME_AREA_HEIGHT:
                if isinstance(grid[ny][nx], (Wall, HighlightedWall)):
                    count += 1
        return count

    for gx, gy in highlighted_walls[:]:
        if count_wall_neighbors(gx, gy) >= 3:
            grid[gy][gx] = Wall(x=gx, y=gy)
            highlighted_walls.remove((gx, gy))

    # Group highlighted walls into continuous segments and make a hole in the middle of each
    from collections import defaultdict, deque
    visited = set()
    segments = []
    # Helper to get neighbors
    def get_neighbors(gx, gy):
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = gx+dx, gy+dy
            if (nx, ny) in highlighted_walls:
                yield (nx, ny)

    highlighted_set = set(highlighted_walls)
    for gx, gy in highlighted_walls:
        if (gx, gy) in visited:
            continue
        # BFS to collect a segment
        segment = []
        queue = deque()
        queue.append((gx, gy))
        visited.add((gx, gy))
        while queue:
            cx, cy = queue.popleft()
            segment.append((cx, cy))
            for nx, ny in get_neighbors(cx, cy):
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        segments.append(segment)

    # For each segment, make a hole in the middle (only if segment length > 1)
    for segment in segments:
        if not segment:
            continue
        if len(segment) == 1:
            continue  # Do not make a door in segments of length 1
        # Sort segment for consistency (by x then y)
        segment_sorted = sorted(segment)
        mid_idx = len(segment_sorted) // 2
        hx, hy = segment_sorted[mid_idx]
        grid[hy][hx] = None  # Remove wall to create hole
