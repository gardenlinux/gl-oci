# my_project/commands/manifest.py

import click
from gloci.utils import get_config, save_config, parse_layer_file, create_oci_manifest

@click.group()
def manifest():
    """Manage manifests."""
    pass

@manifest.command()
@click.option('--output', required=True, type=click.Path(), help='Output path for the manifest file')
@click.option('--layer_file', required=True, type=click.Path(), help='Layer file for the manifest')
def create(output, layer_file):
    """Create a manifest from the specified layer file."""
    create_oci_manifest(output, layer_file) 
    click.echo(f"Created manifest at {output}")

@manifest.command()
@click.option('--input', required=True, type=click.Path(), help='Input path for the manifest file')
@click.option('--layer_file', required=True, type=click.Path(), help='Layer file to attach to the manifest')
def attach(input, layer_file):
    """Attach to a manifest using the specified layer file."""
    layers = parse_layer_file(layer_file)
    
    with open(input, 'r') as f:
        manifest = json.load(f)
    
    manifest['layers'].extend(layers)
    
    with open(input, 'w') as f:
        json.dump(manifest, f, indent=4)
    
    click.echo(f"Attached layers from {layer_file} to manifest at {input}")

