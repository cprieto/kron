from typing import Union

import click

from .. import util
from ..kronbute import JobServer

@click.command('pause', help='Pause a job')
@click.argument('job_id', type=util.INT_ALIAS, required=True)
@click.pass_obj
def pause(server: JobServer, job_id: Union[int, str]):
    if click.confirm(f"Do you really want to pause automatic execution of the job {job_id}?"):
        server.pause(job_id)
        click.secho(f"Job {job_id} was paused for automatic execution", fg='white')