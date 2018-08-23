from typing import Optional, TextIO, Dict, Tuple
import click
from kronbute import Kronbute, pass_server, ServerException
from terminaltables import SingleTable, AsciiTable

import util


@click.group(help='Group for all the commands related to jobs')
@pass_server
def job(server: Kronbute):
    pass


@job.command('list', help='List all the jobs in the server')
@pass_server
def list_(server: Kronbute):
    try:
        jobs = server.list_jobs()
        data = [['Id', 'Name/Description', 'Schedule', 'Cron entry', 'Last Status', 'Status on', 'Next run']]
        for job in jobs:
            data.append(
                [job['id'], job['name'], job['schedule'], job['cron'],
                 util.format_status(job['lastStatus']), job['statusUpdateOn'], job['nextRun']])

        table = AsciiTable(data)
        click.echo(table.table)
    except ServerException as err:
        click.echo(util.error("Problem when trying to retrieve job list", err), err=True)


@job.command(help='View information about a job with given id')
@click.argument('job_id', type=int, required=True)
@pass_server
def view(server: Kronbute, job_id: int):
    current_job = server.get_job(job_id)

    data = [
        ['Id', job_id],
        ['Name/Description', current_job['name']],
        ['Image:tag', f'{current_job["image"]}:{current_job["tag"]}'],
        ['Schedule', current_job['schedule']],
        ['Cron entry', current_job['cron']],
        ['EntryPoint', current_job['entryPoint']],
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


def process_job(ctx, _, value):
    server = ctx.obj
    ctx.job = server.get_job(value)
    return value


def set_default(param):
    return lambda: click.get_current_context().job[param]


def parse_env(values: Tuple[str], env_file: Optional[TextIO]) -> Dict[str, str]:
    res = {}
    entries = (env_file.readlines() if env_file else []) + list(values)

    for entry in entries:
        if '=' in entry:
            key, value = entry.split('=', 1)
            res[key] = value.strip('\n')
        else:
            res[entry.strip('\n')] = None
    return res


@job.command(help='Create a job in the server')
@click.option('--name', help='Name or description for the job', required=True, prompt=True)
@click.option('--image', help='Docker image for the job', required=True, prompt=True)
@click.option('--tag', help='Docker image tag to use for the job', default='latest')
@click.option('--schedule', help='Cron schedule for the job, in UNIX cron format', required=True, prompt=True, type=util.CRON)
@click.option('--entrypoint', help='Entrypoint for the docker command', required=False)
@click.option('--environment', '-e', help='Environment variable to set in form key=value', multiple=True)
@click.option('--env-file', help='env file with environment variables to set', type=click.File('r'))
@pass_server
def create(server: Kronbute, name: str, image: str, tag: str, schedule: str, environment: Tuple[str], env_file: TextIO,
           entrypoint: str):
    try:
        job_id = server.create_job(name, image, tag, schedule, parse_env(environment, env_file), entrypoint)
    except ServerException as err:
        click.echo(util.error('Problem when creating job', err), err=True)

    message = click.style(f'{job_id}', fg='white', bold=True)
    click.echo(util.success(f"Job created, id is {message}."))


@job.command(help="Edit a job with a given job id")
@click.argument('job_id', type=int, required=True, callback=process_job)
@click.option('--name', help='Name or description for the job', required=True, prompt=True, default=set_default('name'))
@click.option('--image', help='Docker image for the job', required=True, prompt=True, default=set_default('image'))
@click.option('--tag', help='Docker image tag to use for the job', prompt=True, default=set_default('tag'))
@click.option('--schedule', help='Cron schedule for the job, in UNIX cron format', required=True, prompt=True,
              default=set_default('cron'), type=util.CRON)
@click.option('--environment', '-e', help='Environment variable to set in form key=value', multiple=True)
@click.option('--env-file', help='env file with environment variables to set', type=click.File('r'))
@click.option('--entrypoint', help='Entrypoint for the docker command', prompt=True, default=set_default('entryPoint'))
@pass_server
def edit(server: Kronbute, job_id: int, name: str, image: str, tag: str, schedule: str, environment: Tuple[str],
         env_file: TextIO, entrypoint: str):
    try:
        server.edit_job(job_id, name, image, tag, schedule,  parse_env(environment, env_file), entrypoint)
    except ServerException as err:
        click.echo(util.error(f'Problem when updating job {job_id}', err), err=True)

    message = click.style(f'{job_id}', fg='white', bold=True)
    click.echo(util.success(f"Job with id {message} edited."))


@job.command(help='Delete a job in the server, this operation has no undo.')
@click.argument('job_id', type=int, required=True)
@pass_server
def delete(server: Kronbute, job_id: int):
    if click.confirm(f"Do you really want to delete job {job_id}?"):
        try:
            server.delete_job(job_id)
        except ServerException as err:
            click.echo(util.error(f"Problem when deleting job {job_id}", err))

        message = click.style(f'{job_id}', fg='white', bold=True)
        click.echo(util.success(f"Job {message} was deleted."))
