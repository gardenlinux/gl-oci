import click


@click.group()
def ocm():
    """Manage ocm"""
    pass


@ocm.command()
def generate(oci_reference):
    """create an OCM component for a given oci artifact"""
    print("Not Implemented")
