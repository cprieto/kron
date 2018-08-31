import re
import sys
import click
from typing import Optional, Any, Union

import requests

from kronbute import ServerError, NotFoundError, ArgumentValidationError, AliasAlreadyExistsError


def success(text: str) -> str:
    return f'\n{click.style("[SUCCESS]", fg="green")} {text}'


def error(text: str, err: ServerError) -> str:
    msg_type = click.style('[ERROR]', fg='red')

    return f'{msg_type} {text}, code: {err.code}, message: {err.body}'


cron_regex = re.compile(r'^(\*|([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])|\*\/([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])) (\*|([0-9]|1[0-9]|2[0-3])|\*\/([0-9]|1[0-9]|2[0-3])) (\*|([1-9]|1[0-9]|2[0-9]|3[0-1])|\*\/([1-9]|1[0-9]|2[0-9]|3[0-1])) (\*|([1-9]|1[0-2])|\*\/([1-9]|1[0-2])) (\*|([0-6])|\*\/([0-6]))$')
meta_regex = re.compile(r'(@hourly|@daily|@weekly|@monthly)', re.IGNORECASE)


meta = {
    '@hourly': '0 * * * *',
    '@daily': '0 0 * * *',
    '@weekly': '0 0 * * 0',
    '@monthly': '0 0 1 * *'
}


# NOTE: This is a poor man evaluator, but it has the potential, with time, to fully transform into a good evaluator
# for example, support '@hourly at 23' or '@daily at 3:45pm', feel free to submit the patch
class CronEvaluator:
    def __init__(self, value: str):
        self.value = value

    def parse(self) -> Optional[str]:
        if cron_regex.match(self.value):
            return self.value

        if meta_regex.match(self.value):
            return meta[self.value.strip().lower()]

        return None


class CronParamType(click.ParamType):
    name = 'cron'

    def convert(self, value, param, ctx):
        if value is None:
            self.fail("Cron expression cannot be null")

        parsed = CronEvaluator(value).parse()
        if parsed is None:
            self.fail(f"'{value}' is not a cron expression", ctx=ctx)

        return parsed


CRON = CronParamType()

alias_regex = re.compile(r'^[A-Za-z][A-Za-z\d_]*$')


class AliasParamType(click.ParamType):
    name = 'alias'

    def convert(self, value, param, ctx):
        if not alias_regex.match(value):
            self.fail(f'Alias supports only letters and underscores', ctx=ctx)
        return value


ALIAS = AliasParamType()


class IntOrAliasParamType(click.ParamType):
    name = 'IdOrAlias'

    def convert(self, value, param, ctx) -> Union[int, str]:
        parsed = None
        try:
            parsed = click.INT.convert(value, param, ctx)
        except click.exceptions.BadParameter:
            pass

        try:
            parsed = ALIAS.convert(value, param, ctx)
        except click.exceptions.BadParameter:
            pass

        if not parsed:
            self.fail("Neither a valid id or valid alias")

        return parsed


INT_ALIAS = IntOrAliasParamType()


def format_status(status: str) -> str:
    colors = {
        "FAILED": 'red',
        "SUCCESS": 'green',
        "RUNNING": 'yellow'
    }
    return click.style(status, fg=(colors[status] if status in colors else None))


class AtLeastOneParameterError(Exception):
    pass


class KronbuteExceptionHandler(click.Group):
    def __call__(self, *args, **kwargs):
        try:
            self.main(*args, **kwargs)

        except requests.exceptions.ConnectionError:
            click.secho("[ERROR] Problem when trying to connect to Kronbute server", err=True, fg='red')
            sys.exit(10)

        except AtLeastOneParameterError:
            click.secho("[ERROR] You should provide at least one parameter", err=True, fg='red')
            sys.exit(11)

        except AliasAlreadyExistsError as alias:
            click.secho(f"[ERROR] This alias is already taken: {alias.alias}", err=True, fg='red')
            sys.exit(12)

        except NotFoundError as not_found:
            click.secho(f"[ERROR] {not_found.entity} with query {not_found.query} not found", err=True, fg='red')
            sys.exit(13)

        except ArgumentValidationError as validation:
            click.secho(f"[ERROR] Invalid argument(s): {validation.message}", err=True, fg='red')
            sys.exit(14)

        except ServerError as ex:
            click.secho(f"[ERROR] Server returned unexpected code {ex.code}", err=True, fg='red')
            sys.exit(15)


def at_least_one(*args: Optional[Any]) -> bool:
    return any(x for x in args if x)


def format_none(value: Optional[Any]) -> str:
    return value if value else ''
