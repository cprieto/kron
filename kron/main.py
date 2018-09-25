import click

from .util import KronbuteExceptionHandler
from .kronbute import BaseServer
from .job import job_group
from .info import info as info_command
from .runs import runs_group
from .groups import group as groups_group


@click.group(cls=KronbuteExceptionHandler)
@click.option("--server", envvar="KRONBUTE_SERVER", default='http://localhost:8080', help='Kronbute server url')
@click.pass_context
def cli(ctx, server: str):
    server = BaseServer(server)
    ctx.obj = server


cli.add_command(job_group)
cli.add_command(info_command)
cli.add_command(runs_group)
cli.add_command(groups_group)

if __name__ == '__main__':
    cli()
