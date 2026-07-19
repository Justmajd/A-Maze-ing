from mazegen.generator import MazeGenerator


def is_even(num: int) -> bool:
    return num % 2 == 0


def is_odd(num: int) -> bool:
    return num % 2 != 0


def render(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit_: tuple[int, int],
    pattern_cells: set[tuple[int, int]],
) -> str:
    wall = "█" * 2
    space = " " * 2
    PATTERN_COLOR = "\033[96m"
    RESET = "\033[0m"
    height = len(grid)
    width = len(grid[0]) if grid else 0
    lines: list[str] = []
    for row in range((2*height) + 1):
        current_row: list[str] = []
        for column in range((2*width) + 1):
            if is_even(row) and is_even(column):
                current_row.append(wall)
            elif is_even(row) and is_odd(column):
                x = (column - 1) // 2
                y_below = row // 2
                upper_cell = ((column - 1) // 2, (row // 2) - 1)
                lower_cell = ((column - 1) // 2, row // 2)
                if y_below < height:
                    if grid[y_below][x] & MazeGenerator.NORTH:
                        if (
                            upper_cell in pattern_cells
                            and lower_cell in pattern_cells
                        ):
                            current_row.append(
                                f"{PATTERN_COLOR}{wall}{RESET}"
                            )
                        else:
                            current_row.append(wall)
                    else:
                        current_row.append(space)
                else:
                    if grid[y_below-1][x] & MazeGenerator.SOUTH:
                        current_row.append(wall)
                    else:
                        current_row.append(space)

            elif is_odd(row) and is_even(column):
                x_right = column // 2
                y = (row - 1) // 2
                left_cell = ((column // 2) - 1, (row - 1) // 2)
                right_cell = (column // 2, (row - 1) // 2)
                if x_right < width:
                    if grid[y][x_right] & MazeGenerator.WEST:
                        if (
                            left_cell in pattern_cells
                            and right_cell in pattern_cells
                        ):
                            current_row.append(
                                f"{PATTERN_COLOR}{wall}{RESET}"
                            )
                        else:
                            current_row.append(wall)
                    else:
                        current_row.append(space)
                else:
                    if grid[y][x_right-1] & MazeGenerator.EAST:
                        current_row.append(wall)
                    else:
                        current_row.append(space)
            else:
                x = (column-1) // 2
                y = (row - 1) // 2
                if (x,y) in pattern_cells:
                    current_row.append(f"\033[96m{wall}\033[0m")
                elif x == entry[0] and y == entry[1]:
                    current_row.append(f"\033[32m{wall}\033[0m")
                elif x == exit_[0] and y == exit_[1]:
                    current_row.append(f"\033[31m{wall}\033[0m")
                else:
                    current_row.append(space)
                    
        lines.append("".join(current_row))
    return "\n".join(lines)
