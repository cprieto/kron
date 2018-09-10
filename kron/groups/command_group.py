from typing import Union, Tuple, Dict, Optional, TextIO, Any

import click
from terminaltables import AsciiTable, SingleTable

from .. import util
from ..kronbute import GroupsServer


@click.group(help='Environment group commands')
@click.pass_context
def groups(ctx):
    ctx.obj = GroupsServer(ctx.obj)


@groups.command('list', help='List all environment groups')
@click.pass_obj
def list_groups(server: GroupsServer):
    data = [['Id', 'Name', 'Variables']]
    for group in server.list():
        data.append([group['id'], group['name'], group['variables']])

    table = AsciiTable(data)
    click.echo(table.table)


@groups.command(help='Create a new environment group')
@click.option('--name', type=str, required=True, help='Name for the new environment group, it must be unique')
@click.option('--environment', '-e', multiple=True, help='Environment variable in form key=value')
@click.option('--env-file', help='env file with environment variables to set', type=click.File('r'))
@click.pass_obj
def create(server: GroupsServer, name: str, environment: Union[Tuple[str], Dict[str, str]], env_file: Optional[TextIO]):
    response = server.create(name, util.parse_env(environment, env_file))
    message = click.style(f'{response}', fg='white', bold=True)
    click.echo(util.success(f"Group {name} created, id is {message}."))


@groups.command(help='View details of environment group')
@click.argument('group_id', type=util.INT_ALIAS, required=True)
@click.pass_obj
def view(server: GroupsServer, group_id: Union[str, int]):
    group = server.view(group_id)

    data = [
        ['Id', group['id']],
        ['Name', group['name']]]

    if 'environment' in group and len(group['environment']) > 0:
        e = SingleTable([[key, value] for key, value in group['environment'].items()])
        e.inner_heading_row_border = False
        e.outer_border = False
        e.inner_column_border = False
        data.append(['Environment', e.table])

    table = SingleTable(data)
    table.inner_heading_row_border = False
    click.echo(table.table)


@groups.command(help='Edit an existing environment group')
@click.argument('group_id', type=util.INT_ALIAS, required=True)
@click.option('--name', type=str, help='Name for the environment group, it must not previously exist')
@click.option('--environment', '-e', help='Environment variable in form key=value', multiple=True)
@click.option('--env-file', help='env file with environment variables to set', type=click.File('r'))
@click.pass_obj
def edit(server: GroupsServer, group_id: Union[str, int], name: Optional[str],
         environment: Optional[Dict[str, Optional[Any]]], env_file: TextIO):
    if not util.at_least_one(name, environment, env_file):
        raise util.AtLeastOneParameterError()

    server.edit(group_id, name, util.parse_env(environment, env_file))

    message = click.style(f'{group_id}', fg='white', bold=True)
    click.echo(util.success(f"Group with id {message} edited."))


@groups.command(help='Delete an existing environment group')
@click.argument('group_id', type=util.INT_ALIAS, required=True)
@click.pass_obj
def delete(server: GroupsServer, group_id: Union[str, int]):
    if click.confirm(f"Do you really want to delete environment group {group_id}?"):
        server.delete(group_id)
        message = click.style(f'{group_id}', fg='white', bold=True)
        click.echo(util.success(f"Environment group {message} was deleted."))
