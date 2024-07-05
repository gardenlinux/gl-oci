ZOT_CONFIG_FILE := "./zot/config.json"
VENV := .venv
PYTHON := python3

serve-oci-registry:
	mkdir -p output/registry
	podman run --rm -p 8081:8081 -v $(ZOT_CONFIG_FILE):/etc/zot/config.json -v ./output/registry:/tmp/zot ghcr.io/project-zot/zot-linux-arm64:latest

activate_venv:
	@echo "To activate venv in your shell run:"
	@echo "source $(VENV)/bin/activate"

create_venv: ## Create a virtual environment.
	$(PYTHON) -m venv $(VENV)

install_deps: ## Install dependencies.
	$(VENV)/bin/pip install -r requirements.txt

example:
	@echo "Create example manifest"
	$(PYTHON) -m gloci.cli image push --container examplecontainer:latest  --info_yaml example-data/info.yaml
