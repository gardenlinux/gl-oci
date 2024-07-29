# my_project/commands/image.py
import click
import yaml
import os
import json
import oras.client
import oras.container
from gloci.oras.registry import Registry as GlociRegistry
import pprint


@click.group()
def image():
    """Manage images"""
    pass


@image.command()
@click.option('--container', 'container_name', required=True, type=click.Path(), help='Container Name')
@click.option('--architecture', required=True, type=click.Path(), help='Target Image CPU Architecture')
@click.option('--cname', required=True, type=click.Path(), help='Canonical Name of Image')
@click.option('--info_yaml', required=True, type=click.Path(),
              help='info.yaml file of the Garden Linux flavor. The info.yaml specifies the data (layers) to expect to '
                   'be attached later.')
def push(container_name, architecture, cname, info_yaml):
    container = oras.container.Container(container_name)
    registry = GlociRegistry(container.registry)

    # TODO: cname can be computed from info_yaml content,
    #  but for consistency we let the caller who knows the cname already provide the cname

    # Create and Push image manifest
    registry.push_image_manifest(container_name, architecture, cname, info_yaml)


@image.command()
@click.option('--container', required=True, type=click.Path(), help='container string e.g. ghcr.io/gardenlinux/gardenlinux:1337')
@click.option('--cname', required=True, type=click.Path(), help='cname of target image')
@click.option('--architecture', required=True, type=click.Path(), help='architecture of image')
@click.option('--file_path', required=True, type=click.Path(), help='file to attach to the manifest')
@click.option('--media_type', required=True, type=click.Path(), help='mediatype of file')
def attach(container, cname, architecture, file_path, media_type):
    """Attach data to an existing image manifest"""
    container = oras.container.Container(container)
    registry = GlociRegistry(container.registry)

    registry.attach_layer(container,cname, architecture, file_path, media_type)

    click.echo(f"Attached {file_path} to {container}")


@image.command()
def remove():
    click.echo("Image removal not supported")


@image.command()
@click.option('--container', required=True, help='oci image reference')
def status(container):
    """Get status of image"""
    click.echo(f"Requesting status of {container}")
    container = oras.container.Container(container)
    registry = GlociRegistry(container.registry)
    pprint.pprint(registry.status_all(container), compact=True)


@image.command()
@click.option('--container', required=True, help='oci image reference')
@click.option('--cname', required=True, help='cname of image')
@click.option('--architecture', required=True, help='architecture of image')
def inspect(container, cname, architecture):
    """inspect container"""
    container = oras.container.Container(container)
    registry = GlociRegistry(container.registry)
    pprint.pprint(registry.get_manifest(container, cname, architecture), compact=True)


@image.command()
@click.option('--container', required=True, help='oci image reference')
def inspect_index(container):
    """inspects complete index"""
    container = oras.container.Container(container)
    registry = GlociRegistry(container.registry)
    pprint.pprint(registry.get_index_manifest(container), compact=True)


@image.command()
def list():
    """List available images with status"""
    click.echo(f"Requesting status of all available images")
