.PHONY: dev test lint format pick deploy

DEV_PYTHON := python

dev:
$(DEV_PYTHON) -m pip install -e .[dev]

lint:
ruff check dsp tests

format:
black dsp tests

test:
pytest

pick:
$(DEV_PYTHON) -m dsp.pick_today

deploy:
scripts/deploy.sh
