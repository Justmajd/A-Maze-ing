from mazegen.generator import MazeGenerator
from renderer import render


def run_test(
    width: int,
    height: int,
    entry: tuple[int, int],
    exit_: tuple[int, int],
    seed: int,
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
    print(render(maze.grid, maze.entry, maze.exit))


run_test(20, 15, (0, 0), (19,13 ),0)
run_test(20, 15, (0, 0), (19,13 ),0)
run_test(20, 15, (0, 0), (19,13 ),42)
run_test(20, 15, (0, 0), (19,13 ),None)
run_test(20, 15, (0, 0), (19,13 ),None)


