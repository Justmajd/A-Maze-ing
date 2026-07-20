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