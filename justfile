install:
	poetry install
	poetry run pre-commit install

test:
	poetry run pytest

lint:
	poetry run pre-commit run --all-files

run:
	poetry run dagster dev
