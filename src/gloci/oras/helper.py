import hashlib

import click
import oras.client
import os
import oras.oci
import oras.defaults
import yaml


def get_client_from_config(config_path) -> oras.client.OrasClient:
    host = "localhost:8081"
    port = "8081"
    return oras.client.OrasClient(hostname=host)

def create_layer(list_of_files):
    layers = []
    for blob in list_of_files:
        layer = oras.oci.NewLayer(blob, is_dir=False, media_type="org.dinosaur.tools.blobish")

        # This is important so oras clients can derive the relative name you want to download to
        # Using basename assumes a flat directory of files - it doesn't have to be.
        # You can add more annotations here!
        layer["annotations"] = {oras.defaults.annotation_title: os.path.basename(blob)}
        layers.append(layer)
    return layers


def create_manifest(list_of_files):
    conf, config_file = oras.oci.ManifestConfig()

    # Prepare a new manifest
    manifest = oras.oci.NewManifest()

    # update the manifest with layers
    layers = create_layer(list_of_files)
    manifest["layers"] = layers

    # Note that you can add annotations to the manifest too
    manifest['annotations'] = {'org.dinosaur.tool.food': 'avocado'}

    # Add your previously created config to it!
    manifest["config"] = conf

    return manifest


def upload_manifest(manifest):
   pass


def construct_local_artifact_paths(base_path, data):
    return [os.path.join(base_path, artifact['file_name']) for artifact in data['oci_artifacts']]


def calculate_digest(file_path):
    """Calculate the SHA256 digest of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return f"sha256:{sha256.hexdigest()}"


def parse_layer_file(layer_file_path):
    """Parse the layer YAML file and return a list of dictionaries with mediaType, size, and digest."""
    with open(layer_file_path, 'r') as f:
        data = yaml.safe_load(f)

    layers = []
    base_dir = os.path.dirname(layer_file_path)
    for layer in data['layers']:
        file_path = os.path.join(base_dir, layer['filePath'].strip())
        layers.append({
            "mediaType": layer['mediaType'].strip(),
            "size": os.path.getsize(file_path),
            "digest": calculate_digest(file_path)
        })

    return layers


def append_layer(manifest: dict, data_path: str) -> dict:
    """Appends data to a manifest as a layer"""
    with open(data_path, 'rb') as f:
        content = f.read()
        digest = f"sha256:{hashlib.sha256(content).hexdigest()}"
        size = len(content)

        layer_info = {
            "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
            "digest": digest,
            "size": size,
            "annotations": {
                "org.opencontainers.image.title": os.path.basename(data_path)
            }
        }

        manifest["layers"].append(layer_info)

    return manifest


def create_oci_manifest(layers):
    manifest = {
        "schemaVersion": 2,
        "mediaType": "application/vnd.oci.image.manifest.v1+json",
        "config": {
            "mediaType": "application/vnd.oci.image.config.v1+json",
            "digest": "",
            "size": 0
        },
        "layers": []
    }

    for layer in layers:
        click.echo(f"Adding {layer} to manifest")
        if not os.path.isfile(layer):
            raise FileNotFoundError(f"File not found: {layer}")

        manifest = append_layer(manifest, layer)

    manifest["config"] = {}
    return manifest
