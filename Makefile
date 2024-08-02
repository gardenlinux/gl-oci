ZOT_CONFIG_FILE := "./zot/config.json"
VENV := .venv
PYTHON := python3
#EXAMPLECONTAINERNAME := localhost:8081/examplecontainer2
#EXAMPLECONTAINERNAME := ghcr.io/gardenlinux/gl-oci
CONTAINER_NAME_example-zot := localhost:8081/examplecontainer2
CONTAINER_NAME_example-ghcr := ghcr.io/gardenlinux/gl-oci

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

include .env

example-%:
	@echo "==== DEMO ===="
	@echo "=== Push dummy container 1 arm64"
	$(PYTHON) -m gloci.cli image push --container $(CONTAINER_NAME_$@):latest --architecture arm64 --cname yolo-example_dev --info_yaml example-data/info_1.yaml
	@echo "=== Push dummy container 1 amd64"
	$(PYTHON) -m gloci.cli image push --container $(CONTAINER_NAME_$@)):latest --architecture amd64 --cname yolo-example_dev --info_yaml example-data/info_1.yaml
	@echo "=== Push dummy container 2 arm64"
	$(PYTHON) -m gloci.cli image push --container $(CONTAINER_NAME_$@):latest --architecture arm64 --cname yolo2-example_dev --info_yaml example-data/info_2.yaml
	@echo "=== Push dummy container 2 amd64"
	$(PYTHON) -m gloci.cli image push --container $(CONTAINER_NAME_$@):latest --architecture amd64 --cname yolo2-example_dev --info_yaml example-data/info_2.yaml
	@echo "=== Attach an Extra file to dummy container 2 arm64"
	$(PYTHON) -m gloci.cli image attach --container $(CONTAINER_NAME_$@):latest --cname yolo-example_dev --architecture arm64 --file_path example-data/extras --media_type application/vnd.oci.image.layer.v1.tar
	@echo ""
	@echo ""
	@echo ""
	@echo "=== Inspect oci-index"
	$(PYTHON) -m gloci.cli image inspect-index --container $(CONTAINER_NAME_$@):latest
	@echo "=== Inspect single manigest"
	$(PYTHON) -m gloci.cli image inspect --container $(CONTAINER_NAME_$@):latest --cname yolo-example_dev --architecture arm64
	@echo "=== Inspect single manigest"
	$(PYTHON) -m gloci.cli image inspect --container $(CONTAINER_NAME_$@):latest --cname yolo-example_dev --architecture amd64

clean:
	rm -rf output gl-oci.log
