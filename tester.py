from typing import Optional

from mazegen.generator import MazeGenerator
from renderer import render


def run_test(
    width: int,
    height: int,
    entry: tuple[int, int],
    exit_: tuple[int, int],
    seed: Optional[int],
) -> None:
    maze = MazeGenerator(
        width=width,
        height=height,
        entry=entry,
        exit_=exit_,
        perfect=True,
        seed=seed,
    )

    maze.generate()

    print(f"\nSize: {width}x{height}")
    print(f"Entry: {entry}")
    print(f"Exit: {exit_}")
    print(f"Seed: {seed}")
    print(render(maze.grid, maze.entry, maze.exit, maze.pattern_cells))
    print(maze.verify_connectivity())
    print(maze.solve())

run_test(20, 15, (0, 0), (19,13 ),None)


