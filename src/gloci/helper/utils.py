import configparser
import hashlib
import os

import click
import yaml
import json

CONFIG_FILE = 'config.ini'


def read_layers_from_yaml(yaml_file):
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)
    base_path = os.path.dirname(yaml_file)
    layers = data.get('oci_layer', [])
    full_paths = [os.path.join(base_path, layer) for layer in layers]
    return full_paths


def validate_yaml_syntax(yaml_data):
    try:
        yaml.safe_load(yaml_data)
        print(f"YAML data is valid.")
        return True
    except yaml.YAMLError as e:
        print(f"YAML data is invalid: {e}")
        return False


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

        with open(layer, 'rb') as f:
            content = f.read()
            digest = f"sha256:{hashlib.sha256(content).hexdigest()}"
            size = len(content)

            layer_info = {
                "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
                "digest": digest,
                "size": size,
                "annotations": {
                    "org.opencontainers.image.title": os.path.basename(layer)
                }
            }

            manifest["layers"].append(layer_info)

    manifest["config"] = {}
    return manifest