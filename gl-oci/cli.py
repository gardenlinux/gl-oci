#!/bin/env python3

import click
from .commands import manifest, remote

@click.group()
def cli():
    """My Project Command Line Interface"""
    pass

cli.add_command(manifest.manifest)
cli.add_command(remote.remote)

if __name__ == '__main__':
    cli()

