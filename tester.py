from sys import argv

from a_maze_ing import parse_config, validate_config
from mazegen.generator import MazeGenerator
from renderer import render


def main() -> None:
    parsed = parse_config(argv[1])
    valid = validate_config(parsed)

    maze = MazeGenerator(
        width=valid.width,
        height=valid.height,
        entry=valid.entry,
        exit_=valid.exit,
        perfect=valid.perfect,
        seed=valid.seed,
    )

    maze.generate()
    solution = maze.solve()

    print(
        render(
            maze.grid,
            maze.entry,
            maze.exit,
            maze.pattern_cells,
            solution,
        )
    )

    print("Shortest path:", "".join(solution))


if __name__ == "__main__":
    main()