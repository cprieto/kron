from typing import Optional, TextIO, Dict, Tuple, Union
import click
import yaml
from kronbute import Kronbute, pass_server, ServerError
from terminaltables import SingleTable, AsciiTable

import util


@click.group(help='Group for all the commands related to jobs')
@pass_server
def job(server: Kronbute):
    pass


@job.command('list', help='List all the jobs in the server')
@pass_server
def list_(server: Kronbute):
    jobs = server.list_jobs()
    data = [['Id', 'Alias', 'Name/Description', 'Schedule', 'Cron entry', 'Last Status', 'Status on', 'Next run']]
    for job in jobs:
        data.append(
            [job['id'], util.format_none(job['alias'] if 'alias' in job else ''), job['name'], job['schedule'],
             job['cron'], util.format_status(job['lastStatus']), job['statusUpdateOn'], job['nextRun']])

    table = AsciiTable(data)
    click.echo(table.table)


@job.command(help='View information about a job with given id')
@click.argument('job_id', type=util.INT_ALIAS, required=True)
@pass_server
def view(server: Kronbute, job_id: Union[int, str]):
    current_job = server.get_job(job_id)

    data = [
        ['Id', current_job['id']],
        ['Name/Description', current_job['name']],
        ['Alias', util.format_none(current_job['alias'] if 'alias' in current_job else '')],
        ['Image:tag', f'{current_job["image"]}:{current_job["tag"]}'],
        ['Schedule', current_job['schedule']],
        ['Cron entry', current_job['cron']],
        ['EntryPoint', util.format_none(current_job['entryPoint'])],
        ['Created on', current_job['createdOn']],
        ['Last status', util.format_status(current_job['lastStatus'])],
        ['Updated on', current_job['statusUpdateOn']],
        ['Next run on', current_job['nextRun']]]

    if 'environment' in current_job and len(current_job['environment']) > 0:
        e = SingleTable([[key, value] for key, value in current_job['environment'].items()])
        e.inner_heading_row_border = False
        e.outer_border = False
        e.inner_column_border = False
        data.append(['Environment', e.table])

    table = SingleTable(data)
    table.inner_heading_row_border = False
    click.echo(table.table)


def parse_env(values: Union[Tuple[str],Dict[str, str]], env_file: Optional[TextIO]) -> Dict[str, str]:
    if isinstance(values, dict):
        return values

    entries = (env_file.readlines() if env_file else []) + list(values)

    res = {}
    for entry in entries:
        if '=' in entry:
            key, value = entry.split('=', 1)
            res[key] = value.strip('\n')
        else:
            res[entry.strip('\n')] = None
    return res


@job.command(help='Create a job in the server')
@click.option('--import', help='Import file for job', cls=util.SetImportFile, type=click.Path(exists=True),
              expose_value=False)
@click.option('--name', help='Name or description for the job', required=True, cls=util.CanBeImported)
@click.option('--image', help='Docker image for the job', required=True,
              cls=util.can_be_imported(name='image', fn=lambda x: x.split(':')[0]))
@click.option('--tag', help='Docker image tag to use for the job', default='latest',
              cls=util.can_be_imported(name='image', fn=lambda x: x.split(':')[1]))
@click.option('--schedule', help='Cron schedule for the job, in UNIX cron format', required=True, type=util.CRON,
              cls=util.CanBeImported)
@click.option('--entrypoint', help='Entrypoint for the docker command', required=False, cls=util.CanBeImported)
@click.option('--environment', '-e', help='Environment variable to set in form key=value', multiple=True,
              cls=util.CanBeImported)
@click.option('--env-file', help='env file with environment variables to set', type=click.File('r'))
@click.option('--alias', help='Optional alias for the job', type=util.ALIAS, cls=util.CanBeImported)
@pass_server
def create(server: Kronbute, name: str, image: str, tag: str, schedule: str,
           environment: Union[Tuple[str], Dict[str, str]], env_file: TextIO,
           entrypoint: str, alias: Optional[str] = None):
    job_id = server.create_job(name, image, tag, schedule, parse_env(environment, env_file), entrypoint, alias)
    message = click.style(f'{job_id}', fg='white', bold=True)
    click.echo(util.success(f"Job created, id is {message}."))


@job.command(help="Edit a job with a given job id")
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
@pass_server
def edit(server: Kronbute, job_id: Union[int, str], name: str, image: str, tag: str, schedule: str,
         environment: Tuple[str], env_file: Optional[TextIO], entrypoint: Optional[str], alias: Optional[str]):

    if not util.at_least_one(name, image, tag, schedule, environment, env_file, entrypoint, alias):
        raise util.AtLeastOneParameterError()

    server.edit_job(job_id, name, image, tag, schedule, alias, parse_env(environment, env_file), entrypoint)
    message = click.style(f'{job_id}', fg='white', bold=True)
    click.echo(util.success(f"Job with id {message} edited."))


@job.command(help='Delete a job in the server, this operation has no undo.')
@click.argument('job_id', type=util.INT_ALIAS, required=True)
@pass_server
def delete(server: Kronbute, job_id: Union[int, str]):
    if click.confirm(f"Do you really want to delete job {job_id}?"):
        server.delete_job(job_id)
        message = click.style(f'{job_id}', fg='white', bold=True)
        click.echo(util.success(f"Job {message} was deleted."))


@job.command(help="Export a job as a YAML file")
@click.argument('job_id', type=util.INT_ALIAS, required=True)
@pass_server
def export(server: Kronbute, job_id: Union[str, int]):
    current_job = server.get_job(job_id)
    data = {
        'name': current_job['name'],
        'image': f"{current_job['image']}:{current_job['tag']}",
        'schedule': current_job['cron'],
    }
    if 'alias' in current_job:
        data['alias'] = current_job['alias']
    if 'entryPoint' in current_job and current_job['entryPoint']:
        data['entrypoint'] = current_job['entryPoint']

    if 'environment' in current_job:
        data['environment'] = current_job['environment']

    click.echo(yaml.dump(data, default_flow_style=False))