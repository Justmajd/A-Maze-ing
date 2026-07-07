from sys import argv
def parse_config(path: str) -> dict[str, str]:
    result: dict[str, str] = {}
    with open(path, "r") as file:
        for lineno, line in enumerate(file, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("=", 1)
            if len(parts) != 2:
                raise ValueError(f"malformed config line: line [{lineno}]\n content: {line}")
            result[parts[0].strip()] = parts[1].strip()
    return result
