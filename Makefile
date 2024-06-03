
CONFIG_FILE := config.json
VENV := .venv
PYTHON := python3

serve-oci-registry:
	zot serve $(CONFIG_FILE)



create_venv: ## Create a virtual environment.
	$(PYTHON) -m venv $(VENV)

install_deps: ## Install dependencies.
	$(VENV)/bin/pip install -r requirements.txt

