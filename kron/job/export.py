from typing import Union

import click
import yaml

from .. import util
from ..kronbute import JobServer


@click.command(help="Export a job as a YAML file")
@click.argument('job_id', type=util.INT_ALIAS, required=True)
@click.pass_obj
def export(server: JobServer, job_id: Union[str, int]):
    current_job = server.view(job_id)
    data = {
        'name': current_job['name'],
        'image': f"{current_job['image']}:{current_job['tag']}",
        'schedule': current_job['cron'],
        'timezone': current_job['timeZone']
    }
    if 'alias' in current_job:
        data['alias'] = current_job['alias']
    if 'entryPoint' in current_job and current_job['entryPoint']:
        data['entrypoint'] = current_job['entryPoint']

    if 'environment' in current_job:
        data['environment'] = current_job['environment']

    if 'groups' in current_job:
        data['groups'] = current_job['groups']

    click.echo(yaml.dump(data, default_flow_style=False))
