from typing import Union, Tuple, Dict, TextIO, Optional, List

import click
from .. import util
from ..kronbute import JobServer


@click.command(help='Create a job in the server')
@click.option('--import', help='Import file for job', cls=util.SetImportFile, type=click.Path(exists=True),
              expose_value=False)
@click.option('--name', help='Name or description for the job', required=True, cls=util.CanBeImported)
@click.option('--image', help='Docker image for the job', required=True, type=util.DOCKER_IMAGE,
              cls=util.can_be_imported(name='image', fn=lambda x: x.split(':')[0]))
@click.option('--tag', help='Docker image tag to use for the job', default='latest', type=util.DOCKER_TAG,
              cls=util.can_be_imported(name='image', fn=lambda x: x.split(':')[1]))
@click.option('--schedule', help='Cron schedule for the job, in UNIX cron format', required=True, type=util.CRON,
              cls=util.CanBeImported)
@click.option('--timezone', help='TimeZone to run the job, default is UTC', default='UTC', cls=util.CanBeImported,
              type=util.TIMEZONE)
@click.option('--entrypoint', help='Entrypoint for the docker command', required=False, cls=util.CanBeImported)
@click.option('--environment', '-e', help='Environment variable to set in form key=value', multiple=True,
              cls=util.CanBeImported)
@click.option('--group', '-g', help='Environment group for the job', type=str,
              multiple=True, cls=util.can_be_imported('groups'))
@click.option('--env-file', help='env file with environment variables to set', type=click.File('r'))
@click.option('--alias', help='Optional alias for the job', type=util.ALIAS, cls=util.CanBeImported)
@click.pass_obj
def create(server: JobServer, name: str, image: str, tag: str, schedule: str, timezone: Optional[str],
           environment: Union[Tuple[str], Dict[str, str]], group: Tuple[str], env_file: TextIO,
           entrypoint: str, alias: Optional[str] = None):

    job_id = server.create(name, image, tag, schedule, util.parse_env(environment, env_file), entrypoint, alias,
                           group, timezone)

    message = click.style(f'{job_id}', fg='white', bold=True)
    click.echo(util.success(f"Job created, id is {message}."))
