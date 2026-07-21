"""Command-line configuration, orchestration, and interactive maze menu."""

from dataclasses import dataclass
from sys import argv, exit
from typing import Optional

from mazegen import MazeGenerator
from renderer import render


@dataclass
class MazeConfig:
    """Validated configuration values used to construct a maze."""

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: Optional[int] = None


def parse_config(path: str) -> dict[str, str]:
    """Parse ``KEY=VALUE`` configuration lines from a UTF-8 text file.

    Empty lines and lines beginning with ``#`` are ignored.

    Args:
        path: Configuration file path.

    Returns:
        A mapping containing each parsed key and value.

    Raises:
        OSError: If the file cannot be opened or read.
        UnicodeError: If the file is not valid UTF-8 text.
        ValueError: If a line is malformed or repeats a key.
    """
    result: dict[str, str] = {}
    with open(path, "r", encoding="utf-8") as file:
        for lineno, line in enumerate(file, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("=", 1)
            if len(parts) != 2:
                raise ValueError(
                    f"malformed config line: line [{lineno}]\n content: {line}"
                )
            key = parts[0].strip()
            value = parts[1].strip()
            if not key or not value:
                raise ValueError(
                    f"malformed config line: line [{lineno}]\n content: {line}"
                )
            if key in result:
                raise ValueError(
                    "duplicated config line: line "
                    f"[{lineno}]\n content: {line}"
                )
            result[key] = value
    return result


def validate_config(raw: dict[str, str]) -> MazeConfig:
    """Validate raw configuration values and convert them to typed values.

    Args:
        raw: Parsed configuration mapping.

    Returns:
        A validated :class:`MazeConfig` instance.

    Raises:
        ValueError: If a required key, value, coordinate, or playable-board
            dimension is invalid.
    """
    required = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"}
    keys = raw.keys()
    not_filled = required - set(keys)
    if not_filled:
        raise ValueError(
            "please fill the following keys in the 'config.txt' file : "
            f"{', '.join(sorted(not_filled))}"
        )
    try:
        temp_width = int(raw["WIDTH"])
    except ValueError:
        raise ValueError(
            f"Width is not entered correctly : {raw['WIDTH']}"
        )
    if temp_width <= 0:
        raise ValueError("Width should be greater than zero")
    try:
        temp_height = int(raw["HEIGHT"])
    except ValueError:
        raise ValueError(f"Height is not entered correctly : {raw['HEIGHT']}")
    if temp_height <= 0:
        raise ValueError("Height should be greater than zero")

    entry_list = raw["ENTRY"].split(",")
    if len(entry_list) != 2:
        raise ValueError(f"Entry format is not correct: {raw['ENTRY']}")
    try:
        entryx = int(entry_list[0])
        entryy = int(entry_list[1])
    except ValueError:
        raise ValueError(f"the entry should be numbers only : {raw['ENTRY']}")
    if entryx < 0 or entryx >= temp_width:
        raise ValueError(f"Entry x is not in range : 0 - {temp_width-1}")
    if entryy < 0 or entryy >= temp_height:
        raise ValueError(f"Entry y is not in range : 0 - {temp_height-1}")

    exit_list = raw["EXIT"].split(",")
    if len(exit_list) != 2:
        raise ValueError(f"Exit format is not correct: {raw['EXIT']}")
    try:
        exitx = int(exit_list[0])
        exity = int(exit_list[1])
    except ValueError:
        raise ValueError(f"the exit should be numbers only : {raw['EXIT']}")
    if exitx < 0 or exitx >= temp_width:
        raise ValueError(f"Exit x is not in range : 0 - {temp_width-1}")
    if exity < 0 or exity >= temp_height:
        raise ValueError(f"Exit y is not in range : 0 - {temp_height-1}")

    if entryx == exitx and entryy == exity:
        raise ValueError("Entry and exit coordinates must be different")

    perfect_value = raw["PERFECT"].lower()
    if perfect_value == "true":
        perfect = True
    elif perfect_value == "false":
        perfect = False
    else:
        raise ValueError(
            "Perfect value is not written in correct syntax "
            f"(True or False) : {raw['PERFECT']}"
        )
    output_file = raw["OUTPUT_FILE"].strip()

    if not output_file:
        raise ValueError("OUTPUT_FILE must not be empty")
    if "SEED" in raw:
        try:
            seed = int(raw["SEED"])
        except ValueError:
            raise ValueError(f"The seed is not a number : {raw['SEED']}")
    else:
        seed = None

    if not perfect and (temp_width < 3 or temp_height < 3):
        raise ValueError(
            "Non-perfect mazes require width and height of at least 3"
        )

    maze_config = MazeConfig(
        width=temp_width,
        height=temp_height,
        entry=(entryx, entryy),
        exit=(exitx, exity),
        output_file=output_file,
        perfect=perfect,
        seed=seed,
    )

    return maze_config


def main() -> None:
    """Run the complete maze pipeline and interactive terminal menu."""
    if len(argv) < 2:
        print("no config was passed")
        exit(1)
    elif len(argv) > 2:
        print("pass only the config file")
        exit(1)
    else:
        path = argv[1]
        try:
            config_dict = parse_config(path)
        except (OSError, UnicodeError, ValueError) as e:
            print(e)
            exit(1)
        try:
            config = validate_config(config_dict)
        except ValueError as e:
            print(e)
            exit(1)

        try:
            maze = MazeGenerator(
                width=config.width,
                height=config.height,
                entry=config.entry,
                exit_=config.exit,
                perfect=config.perfect,
                seed=config.seed,
            )
            maze.generate()
        except Exception as e:
            print(f"Failed to generate maze: {e}")
            exit(1)
        try:
            solution = maze.solve()
        except Exception as e:
            print(f"Failed to solve maze: {e}")
            exit(1)
    while True:
        try:
            maze.output(config.output_file, solution)
        except Exception as e:
            print(f"Failed to write output file: {e}")
            exit(1)
        try:
            rendered_maze = render(
                maze.grid,
                maze.entry,
                maze.exit,
                maze.pattern_cells,
                solution,
                maze.show_path,
                maze.wall_color
            )
            print(rendered_maze)
        except Exception as e:
            print(f"Failed to render maze: {e}")
            exit(1)
        print("=== A-Maze-ing Menu ===\n")
        print("1. Regenerate maze")
        print("2. Show shortest path")
        print("3. Hide shortest path")
        print("4. Change wall color")
        print("5. Change seed and regenerate")
        print("6. Quit\n")
        print("Choose an option:", end="")
        try:
            choice: int = int(input())
            if (choice > 6 or choice < 1):
                raise ValueError("choose a number from 1-6")
        except (EOFError, KeyboardInterrupt):
            print("\nInput closed. Exiting.")
            return
        except ValueError as e:
            print(e)
            continue
        if choice == 1:
            try:
                maze.generate()
            except Exception as e:
                print(f"Failed to generate maze: {e}")
                exit(1)
            try:
                solution = maze.solve()
            except Exception as e:
                print(f"Failed to solve maze: {e}")
                exit(1)
        elif choice == 2:
            maze.show_path = True
        elif choice == 3:
            maze.show_path = False
        elif choice == 4:
            while True:
                print("1. White")
                print("2. Blue")
                print("3. Purple")
                print("4. Go back")
                print("Choose a color:", end="")
                try:
                    color_choice: int = int(input())
                    if (color_choice > 4 or color_choice < 1):
                        raise ValueError("choose a number from 1-4")
                except (EOFError, KeyboardInterrupt):
                    print("\nInput closed. Exiting.")
                    return
                except ValueError as e:
                    print(e)
                    continue
                if color_choice == 1:
                    maze.wall_color = 1
                elif color_choice == 2:
                    maze.wall_color = 2
                elif color_choice == 3:
                    maze.wall_color = 3
                elif color_choice == 4:
                    break
                break
        elif choice == 5:
            try:
                print("Enter new seed(blank is random generation):", end="")
                str_seed = input()
            except (EOFError, KeyboardInterrupt):
                print("\nInput closed. Exiting.")
                return

            try:
                maze.seed = None if str_seed == "" else int(str_seed)
            except ValueError:
                print("enter a valid seed")
                continue

            if maze.seed is None:
                print("Generation is random because seed isn't entered")

            try:
                maze.generate()
            except Exception as e:
                print(f"Failed to generate maze: {e}")
                exit(1)
            try:
                solution = maze.solve()
            except Exception as e:
                print(f"Failed to solve maze: {e}")
                exit(1)
        elif choice == 6:
            print("thanks for trying our maze!")
            print("Made with love by malhodal and omjarada")
            break


if __name__ == "__main__":
    main()
