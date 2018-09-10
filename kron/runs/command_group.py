import click
from terminaltables import AsciiTable

from .. import util
from ..kronbute import BaseServer, RunsServer


@click.group(help='Group for all the commands related to job runs')
@click.pass_obj
@click.pass_context
def runs(ctx, server: BaseServer):
    ctx.obj = RunsServer(server)


@runs.command('list', help='List all the jobs in the server')
def list_runs(server: RunsServer):
    job_runs = server.list()
    data = [['Id', 'Job id', 'Job name', 'Last Status', 'Updated on']]
    for job_run in job_runs:
        data.append([job_run['id'], job_run['jobId'], job_run['jobName'], util.format_status(job_run['status']), job_run['on']])

    table = AsciiTable(data)
    click.echo(table.table)
