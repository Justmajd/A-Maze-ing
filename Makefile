.PHONY: install run debug clean lint lint-strict test build

install:
	poetry install

run:
	poetry run python3 a_maze_ing.py config.txt

debug:
	poetry run python -m pdb a_maze_ing.py config.txt

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
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

test:
	poetry run pytest

build:
	poetry build
	cp dist/mazegen-*.whl .
