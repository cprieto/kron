import click
from pyfiglet import Figlet
from terminaltables import SingleTable

from kronbute import Kronbute, pass_server

__version__ = "1.4"


@click.command(help='Show information about Kron and Kronbute')
@pass_server
def info(server: Kronbute):
    name = Figlet(font='slant')
    click.echo(click.style(name.renderText('Kron'), fg='white', bold=True))

    info_table = SingleTable([
        ['Kron version', __version__],
        ['Kronbute version', server.version],
        ['Kronbute server', server.url]
    ])

    click.echo(info_table.table)
