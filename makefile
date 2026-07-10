MAP = maps/easy/01_linear_path.txt
FILES = fly_in.py graph.py hubs.py map_parser.py network.py visuals.py

.PHONY: install run debug clean lint lint-strict

install:
	python3 -m venv env
	. env/bin/activate && pip install -r requirements.txt

run:
	python3 fly_in.py $(MAP)

debug:
	python3 -m pdb fly_in.py $(MAP)

clean:
	rm -rf __pycache__ .mypy_cache

lint:
	flake8 $(FILES)
	mypy $(FILES) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 $(FILES)
	mypy $(FILES) --strict
