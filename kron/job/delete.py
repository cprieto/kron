from typing import Union

import click
from .. import util
from ..kronbute import JobServer


@click.command(help='Delete a job in the server, this operation has no undo.')
@click.argument('job_id', type=util.INT_ALIAS, required=True)
@click.pass_obj
def delete(server: JobServer, job_id: Union[int, str]):
    if click.confirm(f"Do you really want to delete job {job_id}?"):
        server.delete(job_id)
        message = click.style(f'{job_id}', fg='white', bold=True)
        click.echo(util.success(f"Job {message} was deleted."))
