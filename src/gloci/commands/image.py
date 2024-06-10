# my_project/commands/image.py
import click
import yaml
import os
import json
import oras.client
from gloci.helper.utils import create_oci_manifest, construct_local_artifact_paths, append_layer


@click.group()
def image():
    """Manage images"""
    pass


@image.command()
@click.option('--output', required=True, type=click.Path(), help='Output path for the manifest file')
@click.option('--info_yaml', required=True, type=click.Path(),
              help='info.yaml file of the Garden Linux flavor. The info.yaml specifies the data (layers) to expect to '
                   'be attached later.')
def create(output, info_yaml):
    """Bootstrap an image manifest"""

    with open(info_yaml, 'r') as f:
        info_data = yaml.safe_load(f)
    layers = construct_local_artifact_paths(os.path.dirname(info_yaml), info_data)

    manifest = create_oci_manifest(layers)

    # Attach info.yaml to manifest. This info.yaml specifies the layout of the manifest
    #   The info.yaml specifies what layers to expect and how to annotate the
    manifest = append_layer(manifest, info_yaml)
    with open(output, 'w') as f:
        json.dump(manifest, f, indent=4)

    click.echo(f"Created manifest at {output}")


@image.command()
@click.option('--digest', required=True, type=click.Path(), help='Digest of the target oci manifest')
@click.option('--data', required=True, type=click.Path(), help='file to attach to the manifest')
def attach(input, data):
    """Attach data to an existing image manifest"""

    # TODO: Create Connection to OCI Registry

    # TODO: Pull target Image

    # TODO: retrieve manifest json from oci registry

    # TODO: Check status of image. If final, abort with error that image is already final.

    click.echo(f"Attached layer from {data} to manifest at {input}")


@image.command()
@click.option('--reference', required=True, help='oci image reference')
def status(reference):
    """Get status of image"""
    click.echo(f"Requesting status of {reference}")


@image.command()
def list():
    """List available images with status"""
    click.echo(f"Requesting status of all available images")
