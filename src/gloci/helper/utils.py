import configparser
import hashlib
import os
import yaml
import json

CONFIG_FILE = 'config.ini'


def get_config():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    return config


def save_config(config):
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)


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


def create_oci_manifest(output, layer_file):
    layers = parse_layer_file(layer_file)

    manifest = {
        "schemaVersion": 2,
        "mediaType": "application/vnd.oci.image.manifest.v1+json",
        "config": {
            "mediaType": "application/vnd.oci.image.config.v1+json",
            "size": 0,  # Placeholder size
            "digest": "sha256:placeholder"  # Placeholder digest
        },
        "layers": layers
    }

    with open(output, 'w') as f:
        json.dump(manifest, f, indent=4)
