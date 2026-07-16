from mazegen.generator import MazeGenerator

def is_even(num) -> bool:
    return num % 2 == 0

def is_odd(num) -> bool:
    return num % 2 != 0

def render(grid: list[list[int]], entry: tuple[int, int], exit_: tuple[int, int]) -> str:
    wall = "█" * 2
    space = " " * 2

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
                if y_below < height:
                    if grid[y_below][x] & MazeGenerator.NORTH:
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
                if x_right < width:
                    if grid[y][x_right] & MazeGenerator.WEST:
                        current_row.append(wall)
                    else:
                        current_row.append(space)
                else:
                    if grid[y][x_right-1] & MazeGenerator.EAST:
                        current_row.append(wall)
                    else:
                        current_row.append(space)
            else:
                current_row.append(space)
        lines.append("".join(current_row))
    return "\n".join(lines)
        


result = render([[15,15],[15,15]], (0,0), (1,1))
print(len(result.split("\n")))

print(result)