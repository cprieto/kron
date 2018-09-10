import click
from terminaltables import AsciiTable

from kron import util
from kron.kronbute import Kronbute


@click.group(help='Group for all the commands related to job runs')
def runs(server: Kronbute):
    pass


@runs.command('list', help='List all the jobs in the server')
def list_runs(server: Kronbute):
    job_runs = server.list_runs()
    data = [['Id', 'Job id', 'Job name', 'Last Status', 'Updated on']]
    for job_run in job_runs:
        data.append([job_run['id'], job_run['jobId'], job_run['jobName'], util.format_status(job_run['status']), job_run['on']])

    table = AsciiTable(data)
    click.echo(table.table)
