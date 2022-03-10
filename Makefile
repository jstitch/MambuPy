SHELL=/bin/bash

lint:
	@( \
		find ./MambuPy -iname "*.py" | xargs pylint --disable=all --enable=trailing-whitespace,trailing-newlines,missing-final-newline --output-format=parseable; \
		find ./tests -iname "*.py" | xargs pylint --disable=all --enable=trailing-whitespace,trailing-newlines,missing-final-newline --output-format=parseable; \
	)

ifndef APIV2
APIV2 := "apiv2"
endif
test:
	@( \
		./tests/unit.sh -a $(APIV2); \
	)

black:
	@( \
		black ./  -l 90 --exclude ".venv|docs" --check; \
	)

isort:
	@( \
		isort ./ --check-only; \
	)

autoflake:
	@( \
		autoflake --recursive --exclude ".venv,docs" --check --remove-all-unused-imports --remove-unused-variables ./; \
	)

lint2: black isort autoflake

lint2-fix:
	@( \
		black ./ -l 90 --exclude ".venv|docs"; \
		isort ./ --force-single-line-imports --quiet --apply -l=250; \
		autoflake ./ --recursive --exclude ".venv,docs" --in-place --remove-all-unused-imports; \
		isort ./ --quiet --apply; \
	)
