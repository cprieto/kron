import click

from ..kronbute import JobServer

from .create import create as create_command
from .edit import edit as edit_command
from .view import view as view_command
from .list import list_jobs as list_command
from .export import export as export_command


@click.group(help='Group for all the commands related to jobs')
@click.pass_context
def job(ctx):
    ctx.obj = JobServer(ctx.obj)


job.add_command(create_command)
job.add_command(edit_command)
job.add_command(view_command)
job.add_command(list_command)
job.add_command(export_command)
