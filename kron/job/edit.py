from typing import Union, Tuple, TextIO, Optional

import click
from .. import util
from ..kronbute import JobServer


@click.command(help="Edit a job with a given job id")
@click.argument('job_id', type=util.INT_ALIAS, required=True)
@click.option('--import', help='Import file for job', cls=util.SetImportFile, type=click.Path(exists=True),
              expose_value=False)
@click.option('--name', help='Name or description for the job', cls=util.CanBeImported)
@click.option('--image', help='Docker image for the job',
              cls=util.can_be_imported(name='image', fn=lambda x: x.split(':')[0]))
@click.option('--tag', help='Docker image tag to use for the job',
              cls=util.can_be_imported(name='image', fn=lambda x: x.split(':')[1]))
@click.option('--schedule', help='Cron schedule for the job, in UNIX cron format', type=util.CRON,
              cls=util.CanBeImported)
@click.option('--environment', '-e', help='Environment variable to set in form key=value', multiple=True,
              cls=util.CanBeImported)
@click.option('--env-file', help='env file with environment variables to set', type=click.File('r'))
@click.option('--entrypoint', help='Entrypoint for the docker command',
              cls=util.CanBeImported)
@click.option('--alias', help='Alias for the job', type=util.ALIAS, cls=util.CanBeImported)
@click.pass_obj
def edit(server: JobServer, job_id: Union[int, str], name: str, image: str, tag: str, schedule: str,
         environment: Tuple[str], env_file: Optional[TextIO], entrypoint: Optional[str], alias: Optional[str]):

    if not util.at_least_one(name, image, tag, schedule, environment, env_file, entrypoint, alias):
        raise util.AtLeastOneParameterError()

    server.edit(job_id, name, image, tag, schedule, alias, util.parse_env(environment, env_file), entrypoint)
    message = click.style(f'{job_id}', fg='white', bold=True)
    click.echo(util.success(f"Job with id {message} edited."))
