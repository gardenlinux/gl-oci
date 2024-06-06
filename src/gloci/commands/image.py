# my_project/commands/image.py
import click
import oras.client
from gloci.helper.utils import create_oci_manifest


@click.group()
def image():
    """Manage images"""
    pass


@image.command()
@click.option('--output', required=True, type=click.Path(), help='Output path for the manifest file')
@click.option('--info_yaml', required=True, type=click.Path(),
              help='info.yaml file of the Garden Linux flavor. The info.yaml specifies the data (layers) to expect to be attached later.')
def create(output, info_yaml):
    """Bootstrap an image manifest"""
    create_oci_manifest(output, info_yaml)
    click.echo(f"Created manifest at {output}")


@image.command()
@click.option('--input', required=True, type=click.Path(), help='Input path for the manifest file')
@click.option('--data', required=True, type=click.Path(), help='file to attach to the manifest')
def attach(input, data):
    """Attach data to an existing image manifest"""
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
