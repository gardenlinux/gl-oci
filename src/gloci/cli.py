#!/bin/env python3

import click

from gloci.commands import image, remote, ocm

@click.group()
def cli():
    """My Project Command Line Interface"""
    pass

cli.add_command(image.image)
cli.add_command(remote.remote)
cli.add_command(ocm.ocm)



if __name__ == '__main__':
    cli()

