from typing import Union

import click

from .. import util
from ..kronbute import JobServer


@click.command('run', help='Immediate execution of job')
@click.argument('job_id', type=util.INT_ALIAS, required=True)
@click.pass_obj
def run(server: JobServer, job_id: Union[int, str]):
    if click.confirm(f"Do you really want to immediate execute job {job_id}?"):
        server.run_now(job_id)
        click.secho(f"Scheduled job {job_id} for immediate execution", fg='white')
