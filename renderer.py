from mazegen.generator import MazeGenerator


def is_even(num: int) -> bool:
    return num % 2 == 0


def is_odd(num: int) -> bool:
    return num % 2 != 0


def get_path_positions(
    entry: tuple[int, int],
    path: list[str],
) -> set[tuple[int, int]]:
    x, y = entry

    offsets: dict[str, tuple[int, int]] = {
        "N": (0, -1),
        "E": (1, 0),
        "S": (0, 1),
        "W": (-1, 0),
    }

    row = (2 * y) + 1
    column = (2 * x) + 1

    positions: set[tuple[int, int]] = {
        (row, column),
    }

    for direction in path:
        dx, dy = offsets[direction]

        next_x = x + dx
        next_y = y + dy

        next_row = (2 * next_y) + 1
        next_column = (2 * next_x) + 1

        corridor_row = (row + next_row) // 2
        corridor_column = (column + next_column) // 2

        positions.add((corridor_row, corridor_column))
        positions.add((next_row, next_column))

        x = next_x
        y = next_y
        row = next_row
        column = next_column

    return positions


def render(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit_: tuple[int, int],
    pattern_cells: set[tuple[int, int]],
    path: list[str],
) -> str:
    wall = "█" * 2
    space = " " * 2

    pattern_color = "\033[96m"
    path_color = "\033[33m"
    entry_color = "\033[32m"
    exit_color = "\033[31m"
    reset = "\033[0m"

    pattern_block = f"{pattern_color}{wall}{reset}"
    path_block = f"{path_color}{wall}{reset}"
    entry_block = f"{entry_color}{wall}{reset}"
    exit_block = f"{exit_color}{wall}{reset}"

    height = len(grid)
    width = len(grid[0]) if grid else 0
    path_positions = get_path_positions(entry, path)

    lines: list[str] = []

    for row in range((2 * height) + 1):
        current_row: list[str] = []

        for column in range((2 * width) + 1):
            if is_even(row) and is_even(column):
                current_row.append(wall)

            elif is_even(row) and is_odd(column):
                x = (column - 1) // 2
                y_below = row // 2

                upper_cell = (
                    (column - 1) // 2,
                    (row // 2) - 1,
                )
                lower_cell = (
                    (column - 1) // 2,
                    row // 2,
                )

                if (row, column) in path_positions:
                    current_row.append(path_block)
                    continue

                if y_below < height:
                    if grid[y_below][x] & MazeGenerator.NORTH:
                        if (
                            upper_cell in pattern_cells
                            and lower_cell in pattern_cells
                        ):
                            current_row.append(pattern_block)
                        else:
                            current_row.append(wall)
                    else:
                        current_row.append(space)
                else:
                    if grid[y_below - 1][x] & MazeGenerator.SOUTH:
                        current_row.append(wall)
                    else:
                        current_row.append(space)

            elif is_odd(row) and is_even(column):
                x_right = column // 2
                y = (row - 1) // 2

                left_cell = (
                    (column // 2) - 1,
                    (row - 1) // 2,
                )
                right_cell = (
                    column // 2,
                    (row - 1) // 2,
                )

                if (row, column) in path_positions:
                    current_row.append(path_block)
                    continue

                if x_right < width:
                    if grid[y][x_right] & MazeGenerator.WEST:
                        if (
                            left_cell in pattern_cells
                            and right_cell in pattern_cells
                        ):
                            current_row.append(pattern_block)
                        else:
                            current_row.append(wall)
                    else:
                        current_row.append(space)
                else:
                    if grid[y][x_right - 1] & MazeGenerator.EAST:
                        current_row.append(wall)
                    else:
                        current_row.append(space)

            else:
                x = (column - 1) // 2
                y = (row - 1) // 2

                if (x, y) in pattern_cells:
                    current_row.append(pattern_block)
                elif (x, y) == entry:
                    current_row.append(entry_block)
                elif (x, y) == exit_:
                    current_row.append(exit_block)
                elif (row, column) in path_positions:
                    current_row.append(path_block)
                else:
                    current_row.append(space)

        lines.append("".join(current_row))

    return "\n".join(lines)
