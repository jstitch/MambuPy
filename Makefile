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
		echo ""; \
		echo "black"; \
		black ./MambuPy  -l 90 --exclude ".venv|docs|mambupy|MambuPy" --check; \
	)

isort:
	@( \
		echo ""; \
		echo "isort"; \
		isort ./MambuPy --check-only; \
	)

ruff:
	@( \
		echo ""; \
		echo "ruff"; \
		ruff check --exclude ".venv,docs,mambupy,MambuPy" --exclude "python" --exclude "flycheck_*" --ignore E501 ./ --quiet; \
	)

lint2: ruff black isort

lint2-fix:
	@( \
		black ./ -l 90 --exclude ".venv|docs|mambupy|MambuPy"; \
		isort ./ --force-single-line-imports --quiet --apply -l=250; \
		ruff check --exclude ".venv,docs,mambupy,MambuPy" --exclude "python" --exclude "flycheck_*" --ignore E501 ./ --fix; \
		isort ./ --quiet --apply; \
	)
