.PHONY: black black-check flake8 format have-poetry install install-dev isort isort-check lint mypy pylint style tests

black:
	poetry run black raiden_synapse_modules

black-check:
	poetry run black --check --diff raiden_synapse_modules

flake8:
	poetry run flake8 raiden_synapse_modules

isort:
	poetry run isort raiden_synapse_modules

isort-check:
	poetry run isort --diff --check-only raiden_synapse_modules

pylint:
	poetry run pylint raiden_synapse_modules

tests:
	poetry run pytest --cov=raiden_synapse_modules

mypy:
	poetry run mypy raiden_synapse_modules tests

have-poetry:
	@command -v poetry > /dev/null 2>&1 || (echo "poetry is required. Installing." && python3 -m pip install --user poetry)

install: have-poetry
	poetry install --no-dev

install-dev: have-poetry
	poetry install

format: style

lint: mypy flake8 pylint black-check isort-check

style: isort black

test: tests
