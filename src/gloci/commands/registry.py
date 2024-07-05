import click
from gloci.helper.utils import get_config, save_config

@click.group()
def registry():
    """Manage registry configurations."""
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

