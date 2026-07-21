"""Reusable maze generation, validation, solving, and output support."""

from collections import deque
from typing import Optional

import random


class MazeGenerator:
    """Generate perfect mazes or connected Pac-Man-like playable boards.

    Grid cells store closed walls as a four-bit mask.  North, east, south,
    and west use bits 1, 2, 4, and 8 respectively.  Clearing a bit opens the
    passage in that direction.
    """

    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8
    OPPOSITE = {NORTH: SOUTH, SOUTH: NORTH, EAST: WEST, WEST: EAST}
    OFFSET = {NORTH: (0, -1), SOUTH: (0, 1), EAST: (1, 0), WEST: (-1, 0)}

    def __init__(self, width: int, height: int,
                 entry: tuple[int, int], exit_: tuple[int, int],
                 perfect: bool = False, seed: Optional[int] = None) -> None:
        """Initialize a maze with every wall closed.

        Args:
            width: Number of maze columns.
            height: Number of maze rows.
            entry: Entrance coordinates as ``(x, y)``.
            exit_: Exit coordinates as ``(x, y)``.
            perfect: Produce a single-path maze when true.  The default false
                produces a connected board with multiple independent loops.
            seed: Optional seed used for reproducible generation.

        Raises:
            ValueError: If dimensions or coordinates are invalid, or a
                non-perfect board is too small to support two loops.
        """
        if width <= 0 or height <= 0:
            raise ValueError("Maze width and height must be greater than zero")
        if not self._coordinates_in_bounds(entry, width, height):
            raise ValueError("Entry coordinates must be inside the maze")
        if not self._coordinates_in_bounds(exit_, width, height):
            raise ValueError("Exit coordinates must be inside the maze")
        if entry == exit_:
            raise ValueError("Entry and exit coordinates must be different")
        if not perfect and (width < 3 or height < 3):
            raise ValueError(
                "Non-perfect mazes require width and height of at least 3"
            )
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit_
        self.perfect = perfect
        self.seed = seed
        self.grid = [[15] * self.width for _ in range(self.height)]
        self.pattern_cells = self.build_42_pattern()
        self.show_path = False
        self.wall_color = 1

    @staticmethod
    def _coordinates_in_bounds(
        coordinates: tuple[int, int],
        width: int,
        height: int,
    ) -> bool:
        """Return whether coordinates fall inside the requested dimensions."""
        x, y = coordinates
        return 0 <= x < width and 0 <= y < height

    def carve(self, x: int, y: int, direction: int) -> None:
        """Open a passage and its matching wall in the neighboring cell.

        Callers must provide an in-bounds direction with a valid neighbor.

        Args:
            x: Source cell column.
            y: Source cell row.
            direction: One of ``NORTH``, ``EAST``, ``SOUTH``, or ``WEST``.
        """
        dx, dy = self.OFFSET[direction]
        nx = x + dx
        ny = y + dy
        self.grid[y][x] = self.grid[y][x] & (15 - direction)
        self.grid[ny][nx] = self.grid[ny][nx] & (15 - self.OPPOSITE[direction])

    def has_open_3x3(self) -> bool:
        """Return whether the grid contains a completely open 3-by-3 area."""
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
        """Close a passage in a cell and the neighboring cell.

        Args:
            x: Source cell column.
            y: Source cell row.
            direction: Direction of the passage to close.
        """
        dx, dy = self.OFFSET[direction]
        nx = x + dx
        ny = y + dy
        self.grid[y][x] |= direction
        self.grid[ny][nx] |= self.OPPOSITE[direction]

    def count_open_passages(self, x: int, y: int) -> int:
        """Count in-bounds passages from a non-pattern cell.

        Args:
            x: Cell column.
            y: Cell row.

        Returns:
            The number of open passages to neighboring non-pattern cells.
        """
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
        """Return the number of non-pattern cells with one open passage."""
        dead_count = 0

        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern_cells:
                    continue
                if self.count_open_passages(x, y) == 1:
                    dead_count += 1
        return dead_count

    def get_dead_end_cells(self) -> list[tuple[int, int]]:
        """Return coordinates of every non-pattern dead-end cell."""
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
        """Return closed walls that lead to valid non-pattern neighbors.

        Args:
            x: Cell column.
            y: Cell row.

        Returns:
            Directions whose wall and reciprocal wall are both closed.
        """
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
        """Try to open one dead end without creating a 3-by-3 open area.

        Args:
            x: Dead-end cell column.
            y: Dead-end cell row.
            rng: Random source used to order candidate walls.

        Returns:
            True if a wall was removed, otherwise false.
        """
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
        """Open as many existing dead ends as the corridor rule permits.

        Args:
            rng: Random source used to shuffle dead ends.

        Returns:
            The number of dead ends opened.
        """
        dead_ends = self.get_dead_end_cells()
        rng.shuffle(dead_ends)

        fixed_count = 0

        for x, y in dead_ends:
            if self.open_dead_end(x, y, rng):
                fixed_count += 1
        return fixed_count

    def braid(self, rng: random.Random) -> int:
        """Add loops while preventing completely open 3-by-3 areas.

        Args:
            rng: Random source used to shuffle candidate walls.

        Returns:
            The number of extra walls removed.
        """
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

    def count_independent_loops(self) -> int:
        """Return the cycle rank of the connected non-pattern maze graph."""
        degree_sum = 0
        node_count = 0
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern_cells:
                    continue
                node_count += 1
                degree_sum += self.count_open_passages(x, y)
        edge_count = degree_sum // 2
        return max(0, edge_count - node_count + 1)

    def _validate_playable_board(self) -> None:
        """Validate the v1.4 requirements for ``PERFECT=False``.

        Raises:
            ValueError: If connectivity, corridor access, loop count, or the
                tolerated dead-end limit is not satisfied.
        """
        if not self.verify_connectivity():
            raise ValueError("Non-perfect maze is not fully connected")

        required_corridors = {
            (0, 0),
            (self.width - 1, 0),
            (0, self.height - 1),
            (self.width - 1, self.height - 1),
            (self.width // 2, self.height // 2),
        }
        for x, y in required_corridors:
            if (
                (x, y) in self.pattern_cells
                or self.count_open_passages(x, y) == 0
            ):
                raise ValueError(
                    "Non-perfect maze must keep its corners and centre open"
                )

        if self.count_independent_loops() < 2:
            raise ValueError(
                "Non-perfect maze must contain at least two independent loops"
            )
        if self.count_dead_ends() > 2:
            raise ValueError(
                "Non-perfect maze must contain no more than two dead ends"
            )

    def generate(self) -> None:
        """Generate the maze deterministically when a seed is provided.

        Perfect mode produces a spanning tree.  Non-perfect mode adds loops,
        reduces dead ends, and validates the v1.4 playable-board rules.

        Raises:
            ValueError: If entry or exit overlaps the reserved pattern, or the
                generated non-perfect board violates its required invariants.
        """
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
            self._validate_playable_board()

    def solve(self) -> list[str]:
        """Find a shortest entry-to-exit path with breadth-first search.

        Returns:
            A list containing ``N``, ``E``, ``S``, and ``W`` path steps.

        Raises:
            ValueError: If no route exists between entry and exit.
        """
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
        """Return whether every non-pattern cell is reachable from entry."""
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
        """Build centered reserved cells shaped like the digits ``42``.

        Returns:
            Pattern coordinates, or an empty set when the maze is too small.
        """
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
        """Write the hexadecimal grid, endpoints, and solution path.

        Args:
            filename: Destination path.
            path: Shortest solution represented by cardinal letters.

        Raises:
            OSError: If the destination cannot be opened or written.
        """
        with open(filename, "w", encoding="utf-8", newline="\n") as file:
            for row in self.grid:
                hex_chars = [f"{cell:X}" for cell in row]
                row_string = "".join(hex_chars)

                file.write(row_string + "\n")

            file.write(f"\n{self.entry[0]},{self.entry[1]}")
            file.write(f"\n{self.exit[0]},{self.exit[1]}")
            file.write(f"\n{''.join(path)}\n")
