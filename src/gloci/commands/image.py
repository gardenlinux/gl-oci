# my_project/commands/image.py
import json
import os
import click
import oras.client
import oras.container
from oras.container import Container as OrasContainer
from gloci.oras.registry import GlociRegistry

from typing import Optional


@click.group()
def image():
    """Manage images"""
    pass


def setup_registry(
    container_name: str,
    private_key: Optional[str] = None,
    public_key: Optional[str] = None,
):
    username = os.getenv("GLOCI_REGISTRY_USERNAME")
    token = os.getenv("GLOCI_REGISTRY_TOKEN")
    if username is None:
        click.echo("No username")
        exit(-1)
    if token is None:
        click.echo("No token")
        exit(-1)
    return GlociRegistry(
        container_name,
        token,
        private_key=private_key,
        public_key=public_key,
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
@click.option("--version", required=True, type=click.Path(), help="Version of Image")
@click.option(
    "--info_yaml",
    required=True,
    type=click.Path(),
    help="info.yaml file of the Garden Linux flavor. The info.yaml specifies the data (layers)",
)
@click.option(
    "--private_key",
    required=False,
    type=click.Path(),
    help="Path to private key to use for signing",
    default="cert/oci-sign.key",
    show_default=True,
)
@click.option(
    "--public_key",
    required=False,
    type=click.Path(),
    help="Path to public key to use for verification of signatures",
    default="cert/oci-sign.crt",
    show_default=True,
)
def push(
    container_name, architecture, cname, version, info_yaml, private_key, public_key
):
    container_name = f"{container_name}:{version}"
    registry = setup_registry(
        container_name, private_key=private_key, public_key=public_key
    )
    registry.push_image_manifest(architecture, cname, version, info_yaml)
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
@click.option("--version", required=True, type=click.Path(), help="Version of Image")
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
@click.option(
    "--private_key",
    required=False,
    type=click.Path(),
    help="Path to private key to use for signing",
    default="cert/oci-sign.key",
    show_default=True,
)
@click.option(
    "--public_key",
    required=False,
    type=click.Path(),
    help="Path to public key to use for verification of signatures",
    default="cert/oci-sign.crt",
    show_default=True,
)
def attach(
    container_name,
    cname,
    version,
    architecture,
    file_path,
    media_type,
    private_key,
    public_key,
):
    """Attach data to an existing image manifest"""
    container_name = f"{container_name}:{version}"
    registry = setup_registry(container_name, private_key, public_key)

    registry.attach_layer(cname, version, architecture, file_path, media_type)

    click.echo(f"Attached {file_path} to {container_name}")


@image.command()
def remove():
    click.echo("Image removal not supported")


@image.command()
@click.option(
    "--container", "container_name", required=True, help="oci image reference"
)
@click.option("--version", required=True, type=click.Path(), help="Version of Image")
def status(container_name, version):
    """Get status of image"""
    container_name = f"{container_name}:{version}"
    registry = setup_registry(container_name)
    registry.status_all(container_name)


@image.command()
@click.option(
    "--container", "container_name", required=True, help="oci image reference"
)
@click.option("--cname", required=True, help="cname of image")
@click.option("--version", required=True, type=click.Path(), help="Version of Image")
@click.option("--architecture", required=True, help="architecture of image")
@click.option(
    "--public_key",
    required=False,
    type=click.Path(),
    help="Path to public key to use for verification of signatures",
    default="cert/oci-sign.crt",
    show_default=True,
)
def inspect(container_name, cname, version, architecture, public_key):
    """inspect container"""
    container_name = f"{container_name}:{version}"
    container = oras.container.Container(container_name)
    registry = setup_registry(container_name, public_key=public_key)
    print(
        json.dumps(
            registry.get_manifest_by_cname(container, cname, version, architecture),
            indent=4,
        )
    )


@image.command()
@click.option(
    "--container", "container_name", required=True, help="oci image reference"
)
@click.option("--version", required=True, type=click.Path(), help="Version of Image")
@click.option(
    "--public_key",
    required=False,
    type=click.Path(),
    help="Path to public key to use for verification of signatures",
    default="cert/oci-sign.crt",
    show_default=True,
)
def inspect_index(container_name, version, public_key):
    """inspects complete index"""
    container_name = f"{container_name}:{version}"
    registry = setup_registry(container_name, public_key=public_key)
    print(json.dumps(registry.get_index(), indent=4))


@image.command()
def list():
    """List available images with status"""
    click.echo("Requesting status of all available images")
