#!/bin/env python3


import click
import configparser
import os

CONFIG_FILE = 'config.ini'

def get_config():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    return config

def save_config(config):
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

@click.group()
def cli():
    """Garden Linux OCI CLI"""
    pass

@cli.group()
def manifest():
    """Manage manifests."""
    pass

@manifest.command()
@click.option('--output', required=True, type=click.Path(), help='Output path for the manifest file')
@click.option('--layer_file', required=True, type=click.Path(), help='Layer file for the manifest')
def create(output, layer_file):
    """Create a manifest from the specified layer file."""
    click.echo(f"Creating manifest with output {output} and layer file {layer_file}")

@manifest.command()
@click.option('--input', required=True, type=click.Path(), help='Input path for the manifest file')
@click.option('--layer_file', required=True, type=click.Path(), help='Layer file to attach to the manifest')
def attach(input, layer_file):
    """Attach to a manifest using the specified layer file."""
    click.echo(f"Attaching to manifest {input} with layer file {layer_file}")

@manifest.command()
@click.option('--input', required=True, type=click.Path(), help='Input path for the manifest file')
def upload(input):
    """Upload a manifest using the specified file."""
    click.echo(f"Uploading manifest from {input}")

@manifest.command()
@click.option('--input', required=True, type=click.Path(), help='Input path for the manifest file')
@click.option('--key', required=True, type=str, help='Key for the annotation')
@click.option('--value', required=True, type=str, help='Value for the annotation')
def annotate(input, key, value):
    """Annotate a manifest with a key-value pair."""
    click.echo(f"Annotating manifest {input} with key {key} and value {value}")

@cli.group()
def remote():
    """Manage remote configurations."""
    pass

@remote.command()
def show():
    """Show the current remote configuration."""
    config = get_config()
    if 'DEFAULT' in config:
        click.echo(f"Registry URL: {config['DEFAULT'].get('registry_url', 'Not set')}")
        click.echo(f"Registry Port: {config['DEFAULT'].get('registry_port', 'Not set')}")
        click.echo(f"Output Path: {config['DEFAULT'].get('output_path', 'Not set')}")
    else:
        click.echo("No configuration found")

@remote.command()
@click.option('--remote_url', required=True, type=str, help='URL of the remote')
@click.option('--remote_port', required=True, type=int, help='Port of the remote')
def set(remote_url, remote_port):
    """Set the remote configuration."""
    config = get_config()
    config['DEFAULT']['registry_url'] = remote_url
    config['DEFAULT']['registry_port'] = str(remote_port)
    save_config(config)
    click.echo(f"Setting remote URL to {remote_url} and port to {remote_port}")



if __name__ == '__main__':
    cli()

