from mazegen.generator import MazeGenerator

def is_even(num) -> bool:
    return num % 2 == 0

def is_odd(num) -> bool:
    return num % 2 != 0

def render(grid: list[list[int]], entry: tuple[int, int], exit_: tuple[int, int]) -> str:

    height = len(grid)
    width = len(grid[0]) if grid else 0
    lines: list[str] = []
    for row in range((2*height) + 1):
        current_row: list[str] = []
        for column in range((2*width) + 1):
            x = (column - 1) // 2
            y = row // 2
            if is_even(row) and is_even(column):
                current_row.append("█")
            elif is_even(row) and is_odd(column):
                if grid[y][x] & MazeGenerator.NORTH:
                    current_row.append("█")
                else:
                    current_row.append(" ")
            elif is_odd(row) and is_even(column):
                if grid[y][x] & MazeGenerator.EAST:
                    current_row.append("█")
                else:
                    current_row.append(" ")
            else:
                current_row.append(" ")