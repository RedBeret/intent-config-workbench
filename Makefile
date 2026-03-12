.PHONY: install validate render diff-demo health test demo
.RECIPEPREFIX := >

PYTHON ?= python3.12
CLI = $(PYTHON) -m intent_config_workbench.cli

install:
> $(PYTHON) -m pip install --upgrade pip
> $(PYTHON) -m pip install -e ".[dev]"

validate:
> $(CLI) validate --workspace .

render:
> $(CLI) render --workspace .

diff-demo:
> $(CLI) demo --workspace .

health:
> $(CLI) health --workspace .

test:
> pytest

demo: validate render diff-demo
