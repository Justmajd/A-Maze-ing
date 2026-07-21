"""End-to-end and failure-path tests for the command-line application."""

from pathlib import Path

import pytest

import a_maze_ing as application


def write_config(path: Path, output_path: Path) -> None:
    """Write a deterministic valid configuration for CLI tests."""
    path.write_text(
        "\n".join(
            [
                "WIDTH=6",
                "HEIGHT=6",
                "ENTRY=0,0",
                "EXIT=5,5",
                f"OUTPUT_FILE={output_path}",
                "PERFECT=false",
                "SEED=42",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_main_requires_exactly_one_argument(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Missing configuration arguments should exit non-zero and explain why."""
    monkeypatch.setattr(application, "argv", ["a_maze_ing.py"])

    with pytest.raises(SystemExit) as error:
        application.main()

    assert error.value.code == 1
    assert "no config" in capsys.readouterr().out


def test_main_handles_unreadable_config_without_traceback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """An OSError while opening configuration should be reported cleanly."""
    monkeypatch.setattr(
        application,
        "argv",
        ["a_maze_ing.py", str(tmp_path)],
    )

    with pytest.raises(SystemExit) as error:
        application.main()

    assert error.value.code == 1
    output = capsys.readouterr().out
    assert "directory" in output.lower()
    assert "Traceback" not in output


def test_complete_cli_pipeline_writes_output_and_quits(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Config-to-render pipeline should run and create valid output."""
    config_path = tmp_path / "config.txt"
    output_path = tmp_path / "maze.txt"
    write_config(config_path, output_path)
    monkeypatch.setattr(
        application,
        "argv",
        ["a_maze_ing.py", str(config_path)],
    )
    monkeypatch.setattr("builtins.input", lambda: "6")

    application.main()

    lines = output_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 10
    assert lines[7] == "0,0"
    assert lines[8] == "5,5"
    output = capsys.readouterr().out
    assert "A-Maze-ing Menu" in output
    assert "thanks for trying" in output


def test_closed_input_exits_menu_gracefully(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """EOF from a non-interactive terminal should not produce a traceback."""
    config_path = tmp_path / "config.txt"
    output_path = tmp_path / "maze.txt"
    write_config(config_path, output_path)
    monkeypatch.setattr(
        application,
        "argv",
        ["a_maze_ing.py", str(config_path)],
    )

    def closed_input() -> str:
        """Simulate a closed standard-input stream."""
        raise EOFError

    monkeypatch.setattr("builtins.input", closed_input)
    application.main()

    output = capsys.readouterr().out
    assert "Input closed" in output
    assert "Traceback" not in output
