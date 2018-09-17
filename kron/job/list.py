import click
from terminaltables import AsciiTable

from .. import util
from ..kronbute import JobServer


@click.command('list', help='List all the jobs in the server')
@click.pass_obj
def list_jobs(server: JobServer):
    jobs = server.list()
    data = [['Id', 'Alias', 'Name/Description', 'Schedule', 'Last Status', 'Last run', 'Next run']]
    for job in jobs:
        data.append(
            [job['id'], util.format_none(job['alias'] if 'alias' in job else ''), job['name'], job['schedule'],
             util.format_status(job['lastStatus']), job['statusUpdateOn'], job['nextRun']])

    table = AsciiTable(data)
    click.echo(table.table)
