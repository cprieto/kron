from typing import Union

import click

from .. import util
from ..kronbute import JobServer

@click.command('resume', help='Resume a paused job')
@click.argument('job_id', type=util.INT_ALIAS, required=True)
@click.pass_obj
def resume(server: JobServer, job_id: Union[int, str]):
    if click.confirm(f"Do you really want to continue the automatic execution of the job {job_id}?"):
        server.resume(job_id)
        click.secho(f"Job {job_id} resume", fg='white')