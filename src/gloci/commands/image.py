# my_project/commands/image.py
import click
import yaml
import os
import json
import oras.client
import oras.container
from gloci.oras.helper import construct_local_artifact_paths, append_layer, create_oci_manifest
from gloci.oras.registry import Registry as GlociRegistry

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
    registry = GlociRegistry("http://localhost:8081")
    container = oras.container.Container("yolo:v1", "localhost:8081")
    registry.push(container, info_yaml)

@image.command()
@click.option('--digest', required=True, type=click.Path(), help='Digest of the target oci manifest')
@click.option('--data', required=True, type=click.Path(), help='file to attach to the manifest')
def attach(digest, data):
    """Attach data to an existing image manifest"""

    # TODO: Create Connection to OCI Registry

    # TODO: Pull target Image

    # TODO: retrieve manifest json from oci registry

    # TODO: Check status of image. If final, abort with error that image is already final.

    click.echo(f"Attached layer from {data} to manifest at {digest}")


@image.command()
@click.option('--reference', required=True, help='oci image reference')
def status(reference):
    """Get status of image"""
    click.echo(f"Requesting status of {reference}")


@image.command()
def list():
    """List available images with status"""
    click.echo(f"Requesting status of all available images")
