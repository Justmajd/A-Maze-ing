"""Tests for hexadecimal output and ANSI terminal rendering."""

from pathlib import Path

from mazegen import MazeGenerator
from renderer import get_path_positions, render


def generated_maze() -> tuple[MazeGenerator, list[str]]:
    """Return a deterministic generated maze and its solution."""
    maze = MazeGenerator(6, 6, (0, 0), (5, 5), True, seed=12)
    maze.generate()
    return maze, maze.solve()


def test_output_file_has_exact_subject_structure(tmp_path: Path) -> None:
    """Writer should emit hex rows, a blank line, endpoints, and path."""
    maze, path = generated_maze()
    destination = tmp_path / "maze.txt"
    maze.output(str(destination), path)
    lines = destination.read_text(encoding="utf-8").splitlines()

    assert len(lines) == maze.height + 4
    assert all(
        len(line) == maze.width
        and set(line).issubset(set("0123456789ABCDEF"))
        for line in lines[:maze.height]
    )
    assert lines[maze.height] == ""
    assert lines[maze.height + 1] == "0,0"
    assert lines[maze.height + 2] == "5,5"
    assert lines[maze.height + 3] == "".join(path)
    assert destination.read_bytes().endswith(b"\n")


def test_get_path_positions_includes_rooms_and_corridors() -> None:
    """Expanded path positions should cover each room and connector."""
    assert get_path_positions((0, 0), ["E", "S"]) == {
        (1, 1),
        (1, 2),
        (1, 3),
        (2, 3),
        (3, 3),
    }


def test_renderer_shows_entry_exit_and_optional_path() -> None:
    """Rendering should color endpoints and only show a requested path."""
    maze, path = generated_maze()
    hidden = render(
        maze.grid,
        maze.entry,
        maze.exit,
        maze.pattern_cells,
        path,
        False,
        1,
    )
    visible = render(
        maze.grid,
        maze.entry,
        maze.exit,
        maze.pattern_cells,
        path,
        True,
        1,
    )

    assert "\033[32m" in hidden
    assert "\033[31m" in hidden
    assert "\033[33m" not in hidden
    assert "\033[33m" in visible


def test_renderer_applies_selected_wall_color() -> None:
    """Wall palette choices should map to white, blue, and purple ANSI."""
    maze, path = generated_maze()
    expected_codes = {1: "\033[0;37m", 2: "\033[0;34m", 3: "\033[0;35m"}

    for color, code in expected_codes.items():
        rendered = render(
            maze.grid,
            maze.entry,
            maze.exit,
            maze.pattern_cells,
            path,
            False,
            color,
        )
        assert code in rendered
