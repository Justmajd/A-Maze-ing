from sys import argv, exit
from dataclasses import dataclass
from typing import Optional


@dataclass
class MazeConfig:
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: Optional[int] = None


def parse_config(path: str) -> dict[str, str]:
    result: dict[str, str] = {}
    with open(path, "r") as file:
        for lineno, line in enumerate(file, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("=", 1)
            key = parts[0].strip()
            if len(parts) != 2 or not parts[0] or not parts[1]:
                raise ValueError(
                    f"malformed config line: line [{lineno}]\n content: {line}"
                )
            if key in result.keys():
                raise ValueError(
                    "duplicated config line: line "
                    f"[{lineno}]\n content: {line}"
                )
            result[key] = parts[1].strip()
    return result


def validate_config(raw: dict[str, str]) -> MazeConfig:
    required = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"}
    keys = raw.keys()
    not_filled = required - set(keys)
    if not_filled:
        raise ValueError(
            "please fill the following keys in the 'config.txt' file : "
            f"{', '.join(not_filled)}"
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
    if "SEED" in raw:
        try:
            seed = int(raw["SEED"])
        except ValueError:
            raise ValueError(f"The seed is not a number : {raw['SEED']}")
    else:
        seed = None

    maze_config = MazeConfig(
        width=temp_width,
        height=temp_height,
        entry=(entryx, entryy),
        exit=(exitx, exity),
        output_file=raw["OUTPUT_FILE"],
        perfect=perfect,
        seed=seed,
    )

    return maze_config


def main() -> None:
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
        except (FileNotFoundError, ValueError) as e:
            print(e)
            exit(1)
        try:
            validate_config(config_dict)
        except ValueError as e:
            print(e)
            exit(1)

if __name__ == "__main__":
    main()
