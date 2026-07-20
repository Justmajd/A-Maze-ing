from collections import deque
from typing import Optional

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
        self.pattern_cells = self.build_42_pattern()

    def carve(self, x: int, y: int, direction: int) -> None:
        dx, dy = self.OFFSET[direction]
        nx = x + dx
        ny = y + dy
        self.grid[y][x] = self.grid[y][x] & (15 - direction)
        self.grid[ny][nx] = self.grid[ny][nx] & (15 - self.OPPOSITE[direction])

    def has_open_3x3(self) -> bool:
        for y in range(self.height - 2):
            for x in range(self.width - 2):
                block_open = True

                for local_y in range(3):
                    for local_x in range(2):
                        cellx = x + local_x
                        celly = y + local_y

                        if (self.grid[celly][cellx] & self.EAST) != 0:
                            block_open = False
                            break
                    if not block_open:
                        break
                if block_open:
                    for local_y in range(2):
                        for local_x in range(3):
                            cellx = x + local_x
                            celly = y + local_y
                            if (self.grid[celly][cellx] & self.SOUTH) != 0:
                                block_open = False
                                break
                        if not block_open:
                            break
                if block_open:
                    return True

        return False

    def restore_wall(self, x: int, y: int, direction: int) -> None:
        dx, dy = self.OFFSET[direction]
        nx = x + dx
        ny = y + dy
        self.grid[y][x] |= direction
        self.grid[ny][nx] |= self.OPPOSITE[direction]

    def count_open_passages(self, x: int, y: int) -> int:
        open_count = 0
        directions: list[int] = [
            self.EAST,
            self.SOUTH,
            self.NORTH,
            self.WEST,
        ]
        for direction in directions:
            dx, dy = self.OFFSET[direction]
            nx = x + dx
            ny = y + dy
            if (
                0 <= nx < self.width
                and 0 <= ny < self.height
                and (nx, ny) not in self.pattern_cells
                and (self.grid[y][x] & direction) == 0
                and (self.grid[ny][nx]
                     & self.OPPOSITE[direction]) == 0
            ):
                open_count += 1
        return open_count

    def count_dead_ends(self) -> int:
        dead_count = 0

        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern_cells:
                    continue
                if self.count_open_passages(x, y) == 1:
                    dead_count += 1
        return dead_count

    def get_dead_end_cells(self) -> list[tuple[int, int]]:
        dead_ends: list[tuple[int, int]] = []

        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern_cells:
                    continue
                if self.count_open_passages(x, y) == 1:
                    dead_ends.append((x, y))
        return dead_ends

    def get_closed_neighbor_walls(
        self,
        x: int,
        y: int,
    ) -> list[int]:
        closed_directions: list[int] = []

        for direction in self.OFFSET:
            dx, dy = self.OFFSET[direction]
            nx = x + dx
            ny = y + dy

            if (
                0 <= nx < self.width
                and 0 <= ny < self.height
                and (nx, ny) not in self.pattern_cells
                and (self.grid[y][x] & direction) != 0
                and (
                    self.grid[ny][nx]
                    & self.OPPOSITE[direction]
                ) != 0
            ):
                closed_directions.append(direction)

        return closed_directions

    def open_dead_end(
        self,
        x: int,
        y: int,
        rng: random.Random,
    ) -> bool:
        if self.count_open_passages(x, y) != 1:
            return False
        closed_directions = self.get_closed_neighbor_walls(x, y)
        rng.shuffle(closed_directions)

        for direction in closed_directions:
            self.carve(x, y, direction)
            if self.has_open_3x3():
                self.restore_wall(x, y, direction)
                continue
            return True
        return False

    def reduce_dead_ends(self, rng: random.Random) -> int:
        dead_ends = self.get_dead_end_cells()
        rng.shuffle(dead_ends)

        fixed_count = 0

        for x, y in dead_ends:
            if self.open_dead_end(x, y, rng):
                fixed_count += 1
        return fixed_count

    def braid(self, rng: random.Random) -> int:
        candidates: list[tuple[int, int, int]] = []
        directions: list[int] = [
            self.EAST,
            self.SOUTH,
        ]
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern_cells:
                    continue
                for direction in directions:
                    dx, dy = self.OFFSET[direction]
                    nx = x + dx
                    ny = y + dy
                    if (
                        0 <= nx < self.width
                        and 0 <= ny < self.height
                        and (nx, ny) not in self.pattern_cells
                        and (self.grid[y][x] & direction) != 0
                        and (self.grid[ny][nx] & self.OPPOSITE[direction]) != 0
                    ):
                        candidates.append((x, y, direction))
        rng.shuffle(candidates)
        target_removal = max(2, len(candidates) // 10)
        removed = 0
        for x, y, direction in candidates:
            if removed >= target_removal:
                break
            self.carve(x, y, direction)
            if self.has_open_3x3():
                self.restore_wall(x, y, direction)
            else:
                removed += 1
        return removed

    def generate(self) -> None:
        self.grid = [
            [15] * self.width
            for _ in range(self.height)
        ]

        stack: list[tuple[int, int]] = [self.entry]
        visited: set[tuple[int, int]] = {self.entry}
        rng = random.Random(self.seed)
        if self.entry in self.pattern_cells:
            raise ValueError("Entry overlaps the 42 pattern")

        if self.exit in self.pattern_cells:
            raise ValueError("Exit overlaps the 42 pattern")
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
                    and (nx, ny) not in self.pattern_cells
                ):
                    around_info.append((nx, ny, direct))
            if around_info:
                goto_cell = rng.choice(around_info)
                x, y, direction = goto_cell
                self.carve(x=cx, y=cy, direction=direction)
                stack.append((x, y))
                visited.add((x, y))
            else:
                stack.pop()
        if not self.perfect:
            self.braid(rng=rng)
            self.reduce_dead_ends(rng=rng)

    def solve(self) -> list[str]:
        queue: deque[tuple[int, int]] = deque([self.entry])
        visited_rooms: set[tuple[int, int]] = {self.entry}
        path: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}
        directions: list[tuple[int, str]] = [
            (self.NORTH, "N"),
            (self.EAST, "E"),
            (self.SOUTH, "S"),
            (self.WEST, "W"),
        ]

        while queue:
            current = queue.popleft()
            if current == self.exit:
                final_path: list[str] = []
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

                if (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                    and (self.grid[y][x] & direction) == 0
                    and (nx, ny) not in visited_rooms
                    and (nx, ny) not in self.pattern_cells
                ):
                    visited_rooms.add((nx, ny))
                    path[(nx, ny)] = (current, letter)
                    queue.append((nx, ny))

        raise ValueError("No path found from entry to exit")

    def verify_connectivity(self) -> bool:
        queue: deque[tuple[int, int]] = deque([self.entry])
        visited_rooms: set[tuple[int, int]] = {self.entry}
        directions: list[int] = [
            self.NORTH,
            self.EAST,
            self.SOUTH,
            self.WEST,
        ]
        target_count = (self.width * self.height) - len(self.pattern_cells)
        while queue:
            current = queue.popleft()
            x, y = current

            for direction in directions:
                dx, dy = self.OFFSET[direction]
                nx, ny = x + dx, y + dy

                if (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                    and (self.grid[y][x] & direction) == 0
                    and (nx, ny) not in visited_rooms
                    and (nx, ny) not in self.pattern_cells
                ):
                    visited_rooms.add((nx, ny))
                    queue.append((nx, ny))
        return len(visited_rooms) == target_count

    def build_42_pattern(self) -> set[tuple[int, int]]:
        pattern: list[str] = [
            "#    ###",
            "#      #",
            "###  ###",
            "  #  #  ",
            "  #  ###",
        ]
        pattern_cells: set[tuple[int, int]] = set()
        pattern_height = len(pattern)
        pattern_width = len(pattern[0])
        minimum_width = pattern_width + 2
        minimum_height = pattern_height + 2
        if self.width < minimum_width or self.height < minimum_height:
            print("Maze is too small to display the 42 pattern")
            return pattern_cells
        start_x = (self.width - pattern_width) // 2
        start_y = (self.height - pattern_height) // 2
        for local_y, row in enumerate(pattern):
            for local_x, character in enumerate(row):
                if character == "#":
                    pattern_cells.add((start_x + local_x, start_y + local_y))
        return pattern_cells

    def output(self, filename: str, path: list[str]) -> None:
        with open(filename, "w") as file:
            for row in self.grid:
                hex_chars = [f"{cell:X}" for cell in row]
                row_string = "".join(hex_chars)

                file.write(row_string + "\n")

            file.write(f"\n{self.entry[0]},{self.entry[1]}")
            file.write(f"\n{self.exit[0]},{self.exit[1]}")
            file.write(f"\n{''.join(path)}\n")
