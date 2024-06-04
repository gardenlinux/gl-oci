
ZOT_CONFIG_FILE := "./zot/config.json"
VENV := .venv
PYTHON := python3

serve-oci-registry:
	zot serve $(ZOT_CONFIG_FILE)

activate_venv:
	@echo "To activate venv in your shell run:"
	@echo "source $(VENV)/bin/activate"

create_venv: ## Create a virtual environment.
	$(PYTHON) -m venv $(VENV)

install_deps: ## Install dependencies.
	$(VENV)/bin/pip install -r requirements.txt

example_manifest:
	$(PYTHON) -m gloci.cli manifest create --output example.manifest.json --layer_file example-data/layers.yaml
