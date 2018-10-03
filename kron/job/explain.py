from typing import Union

import click
import requests

from kron.kronbute import NotFoundError, ServerError
from .. import util
from ..kronbute import JobServer


@click.command(help="Edit a job with a given job id")
@click.argument('job_id', type=util.INT_ALIAS, required=True)
@click.pass_obj
def explain(server: JobServer, job_id: Union[str, int]):
    reason = requests.get(f'{server.server.url}/api/jobs/{job_id}/explain')
    if reason.status_code == 400:
        raise NotFoundError(job_id)
    if reason.status_code != 200:
        raise ServerError("Problem with the server", reason.status_code, reason.text)
    click.echo(reason.text)
