from typing import Union

import click
from terminaltables import SingleTable

from .. import util
from ..kronbute import JobServer


@click.command(help='View information about a job with given id')
@click.argument('job_id', type=util.INT_ALIAS, required=True)
@click.pass_obj
def view(server: JobServer, job_id: Union[int, str]):
    current_job = server.view(job_id)

    data = [['Id', current_job['id']], ['Name/Description', current_job['name']],
            ['Alias', util.format_none(current_job['alias'] if 'alias' in current_job else '')],
            ['Image:tag', f'{current_job["image"]}:{current_job["tag"]}'],
            ['Schedule', current_job['scheduleText']],
            ['Time Zone', current_job['timeZone']],
            ['Paused', current_job['paused']],
            ['Cron entry', current_job['schedule']],
            ['Cron Type', current_job['cronType']],
            ['EntryPoint', util.format_none(current_job['entryPoint'])],
            ['Groups', ','.join(current_job['groups'])],
            ['Created on', f"{current_job['createdOn']} (UTC)"],
            ['Last status', util.format_status(current_job['lastStatus'])],
            ['Updated on', f"{current_job['statusUpdateOn']} (UTC)"],
            ['Last run on', f"{current_job['lastRun']} ({current_job['timeZone']})"],
            ['Next run on', f"{current_job['nextRun']} ({current_job['timeZone']})"]]

    if 'environment' in current_job and len(current_job['environment']) > 0:
        e = SingleTable([[key, value[:9] + ' ...' if len(value) > 14 else value]
                         for key, value in current_job['environment'].items()])
        e.inner_heading_row_border = False
        e.outer_border = False
        e.inner_column_border = False
        data.append(['Environment', e.table])

    table = SingleTable(data)
    table.inner_heading_row_border = False
    click.echo(table.table)
