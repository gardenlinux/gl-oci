# my_project/commands/image.py
import json
import os
import click
import oras.client
import oras.container
from gloci.oras.registry import GlociRegistry
import pprint


@click.group()
def image():
    """Manage images"""
    pass


def setup_registry(container, container_name):
    container = oras.container.Container(container_name)
    username = os.getenv("GLOCI_REGISTRY_USERNAME")
    token = os.getenv("GLOCI_REGISTRY_TOKEN")
    if username is None:
        click.echo("No username")
        exit(-1)
    if token is None:
        click.echo("No token")
        exit(-1)
    return GlociRegistry(
        container.registry,
        username,
        token,
    )

@image.command()
@click.option(
    "--container",
    "container_name",
    required=True,
    type=click.Path(),
    help="Container Name",
)
@click.option(
    "--architecture",
    required=True,
    type=click.Path(),
    help="Target Image CPU Architecture",
)
@click.option(
    "--cname", required=True, type=click.Path(), help="Canonical Name of Image"
)
@click.option(
    "--info_yaml",
    required=True,
    type=click.Path(),
    help="info.yaml file of the Garden Linux flavor. The info.yaml specifies the data (layers)",
)
def push(container_name, architecture, cname, info_yaml):
    container = oras.container.Container(container_name)
    registry = setup_registry(container, container_name)
    registry.push_image_manifest(container_name, architecture, cname, info_yaml)
    click.echo(f"Pushed {container_name}")


@image.command()
@click.option(
    "--container",
    "container_name",
    required=True,
    type=click.Path(),
    help="container string e.g. ghcr.io/gardenlinux/gardenlinux:1337",
)
@click.option("--cname", required=True, type=click.Path(), help="cname of target image")
@click.option(
    "--architecture", required=True, type=click.Path(), help="architecture of image"
)
@click.option(
    "--file_path",
    required=True,
    type=click.Path(),
    help="file to attach to the manifest",
)
@click.option(
    "--media_type", required=True, type=click.Path(), help="mediatype of file"
)
def attach(container_name, cname, architecture, file_path, media_type):
    """Attach data to an existing image manifest"""
    container = oras.container.Container(container_name)
    registry = setup_registry(container, container_name)

    registry.attach_layer(container_name, cname, architecture, file_path, media_type)

    click.echo(f"Attached {file_path} to {container}")


@image.command()
def remove():
    click.echo("Image removal not supported")


@image.command()
@click.option("--container","container_name", required=True, help="oci image reference")
def status(container_name):
    """Get status of image"""
    container = oras.container.Container(container_name)
    registry = setup_registry(container, container_name)
    registry.status_all(container)


@image.command()
@click.option("--container", "container_name", required=True, help="oci image reference")
@click.option("--cname", required=True, help="cname of image")
@click.option("--architecture", required=True, help="architecture of image")
def inspect(container_name, cname, architecture):
    """inspect container"""
    container = oras.container.Container(container_name)
    registry = setup_registry(container, container_name)
    print(
        json.dumps(
            registry.get_manifest_by_cname(container, cname, architecture), indent=4
        )
    )


@image.command()
@click.option("--container", "container_name", required=True, help="oci image reference")
def inspect_index(container_name):
    """inspects complete index"""
    container = oras.container.Container(container_name)
    registry = setup_registry(container, container_name)
    print(json.dumps(registry.get_index(container), indent=4))


@image.command()
def list():
    """List available images with status"""
    click.echo("Requesting status of all available images")
