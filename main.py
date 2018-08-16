import click
from kronbute import Kronbute
from job import job as job_commands


@click.group()
@click.option("--server", envvar="KRONBUTE_URL", default='http://localhost:8080', help='Kronbute server url')
@click.pass_context
def cli(ctx, server: str):
    server = Kronbute(server)
    ctx.obj = server


cli.add_command(job_commands)

if __name__ == '__main__':
    cli()
