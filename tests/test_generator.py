"""Behavioral and invariant tests for :class:`MazeGenerator`."""

from collections import deque

import pytest

from mazegen import MazeGenerator


def open_neighbors(
    maze: MazeGenerator,
    x: int,
    y: int,
) -> list[tuple[int, int]]:
    """Return coordinates reachable through open walls from one cell."""
    result: list[tuple[int, int]] = []
    for direction, (dx, dy) in maze.OFFSET.items():
        nx, ny = x + dx, y + dy
        if (
            0 <= nx < maze.width
            and 0 <= ny < maze.height
            and (nx, ny) not in maze.pattern_cells
            and (maze.grid[y][x] & direction) == 0
        ):
            result.append((nx, ny))
    return result


def independent_shortest_distance(maze: MazeGenerator) -> int:
    """Compute the shortest distance independently from ``solve``."""
    queue: deque[tuple[tuple[int, int], int]] = deque([(maze.entry, 0)])
    visited = {maze.entry}
    while queue:
        (x, y), distance = queue.popleft()
        if (x, y) == maze.exit:
            return distance
        for neighbor in open_neighbors(maze, x, y):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, distance + 1))
    raise AssertionError("Generated maze has no solution")


def assert_walls_are_coherent_and_bounded(maze: MazeGenerator) -> None:
    """Assert reciprocal walls agree and no external passage is open."""
    for y, row in enumerate(maze.grid):
        for x, cell in enumerate(row):
            if x == 0:
                assert cell & maze.WEST
            if x == maze.width - 1:
                assert cell & maze.EAST
            if y == 0:
                assert cell & maze.NORTH
            if y == maze.height - 1:
                assert cell & maze.SOUTH
            for direction, (dx, dy) in maze.OFFSET.items():
                nx, ny = x + dx, y + dy
                if 0 <= nx < maze.width and 0 <= ny < maze.height:
                    reciprocal = maze.OPPOSITE[direction]
                    assert bool(cell & direction) == bool(
                        maze.grid[ny][nx] & reciprocal
                    )


def follow_solution(maze: MazeGenerator, path: list[str]) -> tuple[int, int]:
    """Follow solution letters and return the final coordinates."""
    direction_by_letter = {
        "N": maze.NORTH,
        "E": maze.EAST,
        "S": maze.SOUTH,
        "W": maze.WEST,
    }
    x, y = maze.entry
    for letter in path:
        direction = direction_by_letter[letter]
        assert (maze.grid[y][x] & direction) == 0
        dx, dy = maze.OFFSET[direction]
        x, y = x + dx, y + dy
    return x, y


def test_constructor_defaults_to_playable_mode() -> None:
    """The reusable API should follow v1.4's non-perfect default."""
    maze = MazeGenerator(6, 6, (0, 0), (5, 5))

    assert maze.perfect is False


@pytest.mark.parametrize(
    "arguments",
    [
        (0, 3, (0, 0), (0, 1), True),
        (3, 3, (-1, 0), (2, 2), True),
        (3, 3, (0, 0), (3, 2), True),
        (3, 3, (0, 0), (0, 0), True),
        (2, 2, (0, 0), (1, 1), False),
    ],
)
def test_constructor_rejects_impossible_parameters(
    arguments: tuple[int, int, tuple[int, int], tuple[int, int], bool],
) -> None:
    """Invalid dimensions, points, and tiny playable boards should fail."""
    with pytest.raises(ValueError):
        MazeGenerator(*arguments)


def test_perfect_generation_is_a_connected_tree_with_shortest_path() -> None:
    """Perfect mode should be coherent, connected, and have no cycles."""
    maze = MazeGenerator(20, 15, (0, 0), (19, 14), True, seed=42)
    maze.generate()
    path = maze.solve()

    node_count = maze.width * maze.height - len(maze.pattern_cells)
    degree_sum = sum(
        len(open_neighbors(maze, x, y))
        for y in range(maze.height)
        for x in range(maze.width)
        if (x, y) not in maze.pattern_cells
    )

    assert maze.verify_connectivity()
    assert degree_sum // 2 == node_count - 1
    assert maze.count_independent_loops() == 0
    assert not maze.has_open_3x3()
    assert follow_solution(maze, path) == maze.exit
    assert len(path) == independent_shortest_distance(maze)
    assert_walls_are_coherent_and_bounded(maze)


@pytest.mark.parametrize("seed", [0, 1, 42, 99])
def test_non_perfect_generation_meets_v14_playable_rules(seed: int) -> None:
    """Playable mode should satisfy every new v1.4 graph invariant."""
    maze = MazeGenerator(20, 20, (0, 0), (19, 18), False, seed)
    maze.generate()

    required_corridors = {
        (0, 0),
        (19, 0),
        (0, 19),
        (19, 19),
        (10, 10),
    }
    assert maze.verify_connectivity()
    assert maze.count_independent_loops() >= 2
    assert maze.count_dead_ends() <= 2
    assert not maze.has_open_3x3()
    assert all(open_neighbors(maze, *cell) for cell in required_corridors)
    assert_walls_are_coherent_and_bounded(maze)


def test_seed_reproducibility() -> None:
    """Equal inputs and seeds should produce equal grids and paths."""
    first = MazeGenerator(12, 10, (0, 0), (11, 9), False, seed=7)
    second = MazeGenerator(12, 10, (0, 0), (11, 9), False, seed=7)
    first.generate()
    second.generate()

    assert first.grid == second.grid
    assert first.solve() == second.solve()


def test_small_maze_omits_pattern_and_prints_warning(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A small maze should omit ``42`` and report the omission."""
    maze = MazeGenerator(6, 6, (0, 0), (5, 5), True, seed=1)

    assert maze.pattern_cells == set()
    assert "too small" in capsys.readouterr().out


def test_pattern_cells_remain_fully_closed() -> None:
    """Every reserved ``42`` cell should keep all four walls."""
    maze = MazeGenerator(20, 15, (0, 0), (19, 14), True, seed=2)
    maze.generate()

    assert maze.pattern_cells
    assert all(maze.grid[y][x] == 15 for x, y in maze.pattern_cells)


def test_entry_or_exit_cannot_overlap_pattern() -> None:
    """Generation should reject endpoints placed inside the ``42``."""
    maze = MazeGenerator(20, 15, (6, 5), (19, 14), True, seed=2)

    with pytest.raises(ValueError, match="Entry overlaps"):
        maze.generate()
