from typing import Optional

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

        