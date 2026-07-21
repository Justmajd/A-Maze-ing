*This activity has been created as part of the 42 curriculum by malhodal, omjarada.*

# A-Maze-ing

## Description

A-Maze-ing is a configurable maze generator written in Python. It creates a
maze, finds a shortest route from its entrance to its exit, writes a compact
hexadecimal representation to a file, and displays the result in a colored
terminal interface.

The project supports both generation modes required by subject version 1.4:

- `PERFECT=True` creates a connected spanning-tree maze. There is exactly one
  route between any two accessible cells and no loops.
- `PERFECT=False` creates a connected Pac-Man-like board. The four corners and
  centre remain usable, the board contains at least two independent loops,
  and no more than two dead ends are tolerated.

When the dimensions permit it, fully closed cells form a visible `42` in the
centre of the maze. A smaller maze omits the pattern and prints a warning.

### Features

- Reproducible recursive-backtracking generation through an optional seed.
- Perfect and braided/playable generation modes.
- Breadth-first shortest-path solving using `N`, `E`, `S`, and `W` steps.
- Symmetric four-bit wall encoding with hexadecimal output.
- Connectivity, loop-count, dead-end, corner, and centre validation.
- Protection against completely open 3-by-3 areas.
- ANSI terminal rendering with colored walls, entry, exit, path, and `42`.
- Interactive regeneration, path visibility, wall-color, and seed controls.
- A reusable `mazegen` wheel that can be installed independently.

## Instructions

### Requirements

- Python 3.10 or later.
- [Poetry](https://python-poetry.org/) for development, checks, and building.

### Installation

Install the project and its development dependencies:

```bash
make install
```

The equivalent Poetry command is:

```bash
poetry install
```

### Running the program

Run with the repository's default configuration:

```bash
make run
```

Or pass any configuration file directly:

```bash
python3 a_maze_ing.py config.txt
```

Exactly one configuration path is accepted.

### Interactive controls

After generation, the terminal menu provides:

1. Regenerate the current maze.
2. Show the shortest path.
3. Hide the shortest path.
4. Change the wall color.
5. Change the seed and regenerate. A blank seed restores random generation.
6. Quit.

### Debugging and checks

```bash
make debug
make lint
make lint-strict
make test
```

`make lint` runs the subject's mandatory Flake8 and mypy flags.
`make lint-strict` additionally runs `mypy --strict`.

## Configuration file

The configuration is plain UTF-8 text with one `KEY=VALUE` pair per line.
Blank lines and lines beginning with `#` are ignored. Duplicate keys and
malformed assignments are rejected.

| Key | Required | Meaning | Example |
| --- | --- | --- | --- |
| `WIDTH` | Yes | Number of maze columns | `WIDTH=20` |
| `HEIGHT` | Yes | Number of maze rows | `HEIGHT=20` |
| `ENTRY` | Yes | Entry coordinates `(x,y)` | `ENTRY=0,0` |
| `EXIT` | Yes | Exit coordinates `(x,y)` | `EXIT=19,18` |
| `OUTPUT_FILE` | Yes | Destination for encoded output | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Yes | `True` for one path, `False` for playable mode | `PERFECT=False` |
| `SEED` | No | Integer seed for reproducibility | `SEED=42` |

Coordinates use zero-based `(x, y)` order. `x` is the column and `y` is the
row. Entry and exit must be distinct and inside the configured dimensions.
Playable mode requires width and height of at least three cells so that the
board can contain two independent loops.

Example:

```text
WIDTH=20
HEIGHT=20
ENTRY=0,0
EXIT=19,18
OUTPUT_FILE=maze.txt
PERFECT=False
SEED=42
```

## Output format

Each maze cell is written as one uppercase hexadecimal digit. The four bits
describe closed walls:

| Bit value | Direction |
| --- | --- |
| `1` | North |
| `2` | East |
| `4` | South |
| `8` | West |

A set bit is a closed wall and a cleared bit is an open passage. Cells are
written row by row. After the grid, the file contains a blank line followed
by the entry, exit, and shortest path on separate lines. Every line ends with
`\n`.

```text
<hexadecimal grid rows>

0,0
19,18
SSEEN...
```

## Algorithm and technical choices

### Recursive backtracker

Generation begins with every cell fully closed. A depth-first recursive-
backtracking process starts at the entry, chooses a random unvisited neighbor,
opens the matching wall in both cells, and backtracks when no unvisited
neighbor remains.

This algorithm was chosen because it is compact, reproducible with a seeded
random generator, and naturally produces a spanning tree. A spanning tree is
connected and contains exactly one path between any two cells, which directly
satisfies `PERFECT=True`.

### The `42` reservation

Before carving, the generator centers an 8-by-5 bitmap shaped like `42` when
there is room for a one-cell margin. Pattern cells remain `0xF` and are
excluded from generation and solving. When the maze is too small, the pattern
is omitted and a console warning is printed.

### Playable non-perfect mode

For `PERFECT=False`, the spanning tree is braided by removing additional
coherent walls. A candidate removal is reverted if it would create a fully
open 3-by-3 area. Remaining dead ends are opened where possible.

The completed board is then checked for:

- Full connectivity.
- Open and reachable corners and centre.
- At least two independent loops.
- No more than two dead ends.
- No completely open 3-by-3 area.

### Breadth-first solver

The solver performs breadth-first search over open passages. Because every
move has equal cost, the first route found to the exit is a shortest route.
Predecessors are traced backward and converted to `N`, `E`, `S`, and `W`.

## Reusable package documentation

The reusable part of the project is the `mazegen` package. Its public API
exports `MazeGenerator`:

```python
from mazegen import MazeGenerator

maze = MazeGenerator(
    width=20,
    height=20,
    entry=(0, 0),
    exit_=(19, 18),
    perfect=False,
    seed=42,
)

maze.generate()
solution = maze.solve()

print(maze.grid)           # grid[y][x] wall bitmasks
print(maze.pattern_cells)  # reserved cells forming "42"
print(solution)            # for example: ["S", "E", "E", "N"]
```

The default mode is `perfect=False`. Pass `perfect=True` for a single-path
maze. Passing the same dimensions, endpoints, mode, and seed produces the same
grid and solution.

Useful methods and attributes:

| API | Purpose |
| --- | --- |
| `generate()` | Generate or regenerate the maze. |
| `solve()` | Return a shortest path as cardinal letters. |
| `grid` | Access wall masks as `grid[y][x]`. |
| `pattern_cells` | Access reserved `42` coordinates. |
| `verify_connectivity()` | Confirm all non-pattern cells are reachable. |
| `count_independent_loops()` | Return the graph's independent loop count. |
| `count_dead_ends()` | Count non-pattern dead ends. |
| `output(filename, path)` | Write the subject-defined output format. |

### Building and installing the package

Build from source:

```bash
make build
```

This creates a standard wheel under `dist/` and copies the wheel to the
repository root as required by the subject.

Install the root artifact in another environment:

```bash
python3 -m pip install ./mazegen-1.0.0-py3-none-any.whl
```

Then import it normally:

```python
from mazegen import MazeGenerator
```

## Testing

Run the complete automated suite with:

```bash
make test
```

The suite covers parsing, validation, perfect-maze uniqueness, wall coherence,
external borders, connectivity, playable-board loops and dead ends, the 3-by-3
rule, seed reproducibility, `42` reservation, shortest paths, output format,
ANSI rendering, CLI execution, and graceful failure paths.

## Resources

Classic references used while designing and implementing the project:

- [Python `random` documentation](https://docs.python.org/3/library/random.html)
- [Python `collections.deque` documentation](https://docs.python.org/3/library/collections.html#collections.deque)
- [Python packaging tutorial](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [Think Labyrinth: maze algorithms](https://www.jamisbuck.org/mazes/)
- The A-Maze-ing subject, versions 1.3 and 1.4.

### AI usage

AI assistance was used to review error handling, design additional tests, and draft documentation and docstrings. It was not treated as an authority: generated suggestions were checked against the subject, exercised with automated tests, Flake8, mypy, andmanual CLI runs, and remain the team's responsibility to understand and writing code and reasoning.

## Team and project management

### Roles

- **Majd (`malhodal`)**: configuration parsing and validation, recursive
  backtracking, `42` reservation, non-perfect braiding, rendering and colors,
  menu integration.
- **Omar (`omjarada`)**: BFS shortest-path solving, connectivity verification,
  hexadecimal output, Makefile integration, and shared review/testing, packaging, and final integration.

### Planning and evolution

The project was developed in parallel rounds with stable interfaces between
the grid, solver, writer, and renderer. Work began with parsing and the wall
model, followed by independent generator and solver development. Pattern
reservation, connectivity, braiding, output, rendering, packaging, and the
interactive menu were then integrated incrementally.

Version 1.4 arrived after the first implementation and expanded non-perfect
mode into a Pac-Man-like board. The plan therefore evolved to add explicit
loop, corner, centre, and dead-end validation, stronger tests, and the new
license requirement.

### What worked well

- A small and stable wall-bitmask interface let both team members work in
  parallel.
- Symmetric carving made wall coherence an invariant rather than a later fix.
- Seeded generation made failures reproducible.
- Flake8, strict mypy, and pytest provided fast integration feedback.

### Tools

The team used Python, Poetry, pytest, Flake8, mypy, Git, GitHub, terminal ANSI
rendering, and AI-assisted review/documentation.

## License

The reusable maze generator is released under the MIT License. See
[LICENSE.md](LICENSE.md) for the complete terms.
