from a_maze_ing import validate_config


def expect_error(
    name: str,
    config: dict[str, str],
) -> None:
    try:
        validate_config(config)
    except ValueError as error:
        print(f"{name}: PASS")
        print(f"  {error}")
        return

    print(f"{name}: FAIL")


def main() -> None:
    base = {
        "WIDTH": "20",
        "HEIGHT": "15",
        "ENTRY": "0,0",
        "EXIT": "19,14",
        "OUTPUT_FILE": "maze.txt",
        "PERFECT": "False",
        "SEED": "42",
    }

    tests = [
        (
            "Zero width",
            {**base, "WIDTH": "0"},
        ),
        (
            "Negative height",
            {**base, "HEIGHT": "-1"},
        ),
        (
            "Entry outside left",
            {**base, "ENTRY": "-1,0"},
        ),
        (
            "Entry outside right",
            {**base, "ENTRY": "20,0"},
        ),
        (
            "Exit outside bottom",
            {**base, "EXIT": "19,15"},
        ),
        (
            "Same entry and exit",
            {**base, "EXIT": "0,0"},
        ),
        (
            "Invalid perfect",
            {**base, "PERFECT": "maybe"},
        ),
        (
            "Invalid seed",
            {**base, "SEED": "hello"},
        ),
        (
            "Missing width",
            {
                key: value
                for key, value in base.items()
                if key != "WIDTH"
            },
        ),
    ]

    for name, config in tests:
        expect_error(name, config)

    valid = validate_config(base)

    print("\nValid configuration: PASS")
    print(valid)


if __name__ == "__main__":
    main()