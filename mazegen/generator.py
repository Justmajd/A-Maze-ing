from typing import Optional
from collections import deque
import random

class MazeGenerator:
    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8
    OPPOSITE = {NORTH: SOUTH, SOUTH: NORTH, EAST: WEST, WEST: EAST}
    OFFSET = {NORTH: (0, -1), SOUTH: (0, 1), EAST: (1, 0), WEST: (-1, 0)}

    def __init__(self, width: int, height: int,
                 entry: tuple[int, int], exit_: tuple[int, int],
                 perfect: bool = True, seed: Optional[int] = None) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit_
        self.perfect = perfect
        self.seed = seed
        self.grid = [[15] * self.width for _ in range(self.height)]

    def carve(self, x: int, y: int, direction: int) -> None:
        dx, dy = self.OFFSET[direction]
        nx = x + dx
        ny = y + dy
        self.grid[y][x] = self.grid[y][x] & (15 - direction)
        self.grid[ny][nx] = self.grid[ny][nx] & (15 - self.OPPOSITE[direction])

    def generate(self) -> None:
        stack: list[tuple[int, int]] = [self.entry]
        visited: set[tuple[int, int]] = {self.entry}
        rng = random.Random(self.seed)
        while stack:
            cx, cy = stack[-1]
            around_info: list[tuple[int, int, int]] = []
            for direct in self.OFFSET:
                dx, dy = self.OFFSET[direct]
                nx = cx + dx
                ny = cy + dy
                if (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                    and (nx, ny) not in visited
                ):
                    around_info.append((nx, ny, direct))
            if around_info:
                goto_cell = rng.choice(around_info)
                x , y, direction = goto_cell
                self.carve(x=cx,y=cy,direction=direction)
                stack.append((x,y))
                visited.add((x,y))
            else:
                stack.pop()

    def solve(self) -> list[str]:
        queue = deque([self.entry])
        visited_rooms = {self.entry}
        path = {}

        directions = [
            (self.NORTH, 'N'),
            (self.EAST, 'E'),
            (self.SOUTH, 'S'),
            (self.WEST, 'W')
        ]
        while queue:
            current = queue.popleft()
            if current == self.exit:
                final_path = []
                trace_cell = self.exit

                while trace_cell != self.entry:
                    previous_cell, letter = path[trace_cell]
                    final_path.append(letter)
                    trace_cell = previous_cell

                final_path.reverse()
                return final_path

            x, y = current
            for direction, letter in directions:
                dx, dy = self.OFFSET[direction]
                nx, ny = x + dx, y + dy

                if (self.grid[y][x] & direction) == 0 and (nx, ny) not in visited_rooms:
                    visited_rooms.add((nx, ny))
                    path[(nx, ny)] = (current, letter)
                    queue.append((nx, ny))

    def verify_connectivity(self) -> bool:
        queue = deque([self.entry])
        visited_rooms = {self.entry}

        target_count = (self.width * self.height)

        directions = [self.NORTH, self.EAST, self.SOUTH, self.WEST]
        while queue:
            current = queue.popleft()
            x, y = current

            for direction in directions:
                dx, dy = self.OFFSET[direction]
                nx, ny = x + dx, y + dy

                if (self.grid[y][x] & direction) == 0 and (nx, ny) not in visited_rooms:
                    visited_rooms.add((nx, ny))
                    queue.append((nx, ny))
        return len(visited_rooms) == target_count