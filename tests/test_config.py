"""Tests for configuration parsing and validation."""

from pathlib import Path

import pytest

from a_maze_ing import MazeConfig, parse_config, validate_config


def valid_raw_config() -> dict[str, str]:
    """Return a minimal valid non-perfect configuration mapping."""
    return {
        "WIDTH": "20",
        "HEIGHT": "15",
        "ENTRY": "0,0",
        "EXIT": "19,14",
        "OUTPUT_FILE": "maze.txt",
        "PERFECT": "false",
    }


def test_parse_config_ignores_comments_and_whitespace(tmp_path: Path) -> None:
    """Parser should normalize values and ignore blank/comment lines."""
    config_path = tmp_path / "config.txt"
    config_path.write_text(
        "# example\n\nWIDTH = 20\nHEIGHT=15\n",
        encoding="utf-8",
    )

    assert parse_config(str(config_path)) == {
        "WIDTH": "20",
        "HEIGHT": "15",
    }


@pytest.mark.parametrize(
    "content",
    [
        "WIDTH",
        "=20",
        "WIDTH=",
        "WIDTH=   ",
        "WIDTH=20\nWIDTH=21",
    ],
)
def test_parse_config_rejects_malformed_or_duplicate_lines(
    tmp_path: Path,
    content: str,
) -> None:
    """Malformed and duplicate assignments should raise clear errors."""
    config_path = tmp_path / "invalid.txt"
    config_path.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError):
        parse_config(str(config_path))


def test_validate_config_converts_types_and_optional_seed() -> None:
    """Validation should return typed values including an optional seed."""
    raw = valid_raw_config()
    raw["SEED"] = "42"

    assert validate_config(raw) == MazeConfig(
        width=20,
        height=15,
        entry=(0, 0),
        exit=(19, 14),
        output_file="maze.txt",
        perfect=False,
        seed=42,
    )


def test_validate_config_accepts_perfect_small_maze() -> None:
    """Perfect mode may use dimensions that cannot support two loops."""
    raw = valid_raw_config()
    raw.update({"WIDTH": "2", "HEIGHT": "2", "EXIT": "1,1"})
    raw["PERFECT"] = "true"

    assert validate_config(raw).perfect is True


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("WIDTH", "0"),
        ("HEIGHT", "word"),
        ("ENTRY", "20,0"),
        ("EXIT", "0,0"),
        ("PERFECT", "sometimes"),
        ("OUTPUT_FILE", "   "),
        ("SEED", "random"),
    ],
)
def test_validate_config_rejects_invalid_values(key: str, value: str) -> None:
    """Every invalid typed or coordinate value should be rejected."""
    raw = valid_raw_config()
    raw[key] = value

    with pytest.raises(ValueError):
        validate_config(raw)


def test_validate_config_rejects_missing_required_key() -> None:
    """All six subject-defined configuration keys are mandatory."""
    raw = valid_raw_config()
    del raw["ENTRY"]

    with pytest.raises(ValueError, match="ENTRY"):
        validate_config(raw)


def test_validate_config_rejects_tiny_non_perfect_board() -> None:
    """Playable mode should reject boards that cannot contain two loops."""
    raw = valid_raw_config()
    raw.update({"WIDTH": "2", "HEIGHT": "2", "EXIT": "1,1"})

    with pytest.raises(ValueError, match="at least 3"):
        validate_config(raw)
