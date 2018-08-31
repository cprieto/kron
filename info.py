import click
from pyfiglet import Figlet
from terminaltables import SingleTable

from kronbute import Kronbute, pass_server


@click.command(help='Show information about Kron and Kronbute')
@pass_server
def info(server: Kronbute):
    name = Figlet(font='slant')
    click.echo(click.style(name.renderText('Kron'), fg='white', bold=True))

    info_table = SingleTable([
        ['Kron version', '1.1'],
        ['Kronbute version', server.version],
        ['Kronbute server', server.url]
    ])

    click.echo(info_table.table)
