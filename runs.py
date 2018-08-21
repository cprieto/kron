import click
from terminaltables import AsciiTable

import util
from kronbute import Kronbute, pass_server, ServerException


@click.group(help='Group for all the commands related to job runs')
@pass_server
def runs(server: Kronbute):
    pass


@runs.command('list', help='List all the jobs in the server')
@pass_server
def list_(server: Kronbute):
    try:
        job_runs = server.list_runs()
        data = [['Id', 'Last Status', 'Updated on']]
        for job_run in job_runs:
            data.append([job_run['id'], job_run['status'], job_run['on']])

        table = AsciiTable(data)
        click.echo(table.table)
    except ServerException as err:
        click.echo(util.error("Problem when trying to retrieve job list", err), err=True)