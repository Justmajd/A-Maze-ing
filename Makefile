.PHONY: install run debug clean lint lint-strict

install:
	poetry install

run:
	poetry run python a_maze_ing.py

debug:
	poetry run python -m pdb a_maze_ing.py

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache
	rm -f maze.txt

# --- LINT FLAG EXPLANATIONS ---
# --warn-return-any       : Warns if a function returns 'Any' instead of a strict type.
# --warn-unused-ignores   : Warns if a '# type: ignore' comment is used where it isn't needed.
# --ignore-missing-imports: Prevents errors when importing external libraries (like mlx) that lack type hints.
# --disallow-untyped-defs : Forces every function definition to have explicit type hints.
# --check-untyped-defs    : Type-checks the inside of functions even if their definition is missing hints.

lint:
	poetry run flake8 .
	poetry run mypy \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs \
		.

lint-strict:
	poetry run flake8 .
	poetry run mypy --strict .