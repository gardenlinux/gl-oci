ZOT_CONFIG_FILE := "./zot/config.json"
VENV := .venv
PYTHON := python3
EXAMPLECONTAINERNAME := examplecontainer2

serve-oci:
	zot serve $(ZOT_CONFIG_FILE)

#serve-oci-registry:
#	mkdir -p output/registry
#	podman run --rm -p 5000:8081 -v ./output/registry:/tmp/zot ghcr.io/project-zot/zot-linux-arm64:latest

activate_venv:
	@echo "To activate venv in your shell run:"
	@echo "source $(VENV)/bin/activate"

create_venv: ## Create a virtual environment.
	$(PYTHON) -m venv $(VENV)

install_deps: ## Install dependencies.
	$(VENV)/bin/pip install -r requirements.txt

example:
	@echo "Push first image..."
	$(PYTHON) -m gloci.cli image push --container localhost:8081/$(EXAMPLECONTAINERNAME):latest  --info_yaml example-data/info.yaml
	@echo "Attach some file to image..."
	$(PYTHON) -m gloci.cli image attach --container localhost:8081/$(EXAMPLECONTAINERNAME):latest  --file_path config.ini --media_type application/vnd.oci.image.layer.v1.tar
	@echo "Inspect final oci image"
	@echo "\n"
	$(PYTHON) -m gloci.cli image inspect --container  localhost:8081/$(EXAMPLECONTAINERNAME):latest
