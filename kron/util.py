import re
import sys
from enum import Enum

import yaml
import click
from typing import Optional, Any, Union, Callable, Tuple, TextIO, Dict

import requests
import pytz

from .kronbute import ServerError, NotFoundError, ArgumentValidationError, AliasAlreadyExistsError


def success(text: str) -> str:
    return f'\n{click.style("[SUCCESS]", fg="green")} {text}'


def error(text: str, err: ServerError) -> str:
    msg_type = click.style('[ERROR]', fg='red')

    return f'{msg_type} {text}, code: {err.code}, message: {err.body}'


cron_regex = re.compile(r'^(\*|([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])|\*\/([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])) (\*|([0-9]|1[0-9]|2[0-3])|\*\/([0-9]|1[0-9]|2[0-3])) (\*|([1-9]|1[0-9]|2[0-9]|3[0-1])|\*\/([1-9]|1[0-9]|2[0-9]|3[0-1])) (\*|([1-9]|1[0-2])|\*\/([1-9]|1[0-2])) (\*|([0-6])|\*\/([0-6]))$')
quartz_regex = re.compile(r'^\s*($|#|\w+\s*=|(\?|\*|(?:[0-5]?\d)(?:(?:-|\/|\,)(?:[0-5]?\d))?(?:,(?:[0-5]?\d)(?:(?:-|\/|\,)(?:[0-5]?\d))?)*)\s+(\?|\*|(?:[0-5]?\d)(?:(?:-|\/|\,)(?:[0-5]?\d))?(?:,(?:[0-5]?\d)(?:(?:-|\/|\,)(?:[0-5]?\d))?)*)\s+(\?|\*|(?:[01]?\d|2[0-3])(?:(?:-|\/|\,)(?:[01]?\d|2[0-3]))?(?:,(?:[01]?\d|2[0-3])(?:(?:-|\/|\,)(?:[01]?\d|2[0-3]))?)*)\s+(\?|\*|(?:0?[1-9]|[12]\d|3[01])(?:(?:-|\/|\,)(?:0?[1-9]|[12]\d|3[01]))?(?:,(?:0?[1-9]|[12]\d|3[01])(?:(?:-|\/|\,)(?:0?[1-9]|[12]\d|3[01]))?)*)\s+(\?|\*|(?:[1-9]|1[012])(?:(?:-|\/|\,)(?:[1-9]|1[012]))?(?:L|W)?(?:,(?:[1-9]|1[012])(?:(?:-|\/|\,)(?:[1-9]|1[012]))?(?:L|W)?)*|\?|\*|(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)(?:(?:-)(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC))?(?:,(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)(?:(?:-)(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC))?)*)\s+(\?|\*|(?:[0-6])(?:(?:-|\/|\,|#)(?:[0-6]))?(?:L)?(?:,(?:[0-6])(?:(?:-|\/|\,|#)(?:[0-6]))?(?:L)?)*|\?|\*|(?:MON|TUE|WED|THU|FRI|SAT|SUN)(?:(?:-)(?:MON|TUE|WED|THU|FRI|SAT|SUN))?(?:,(?:MON|TUE|WED|THU|FRI|SAT|SUN)(?:(?:-)(?:MON|TUE|WED|THU|FRI|SAT|SUN))?)*)(|\s)+(\?|\*|(?:|\d{4})(?:(?:-|\/|\,)(?:|\d{4}))?(?:,(?:|\d{4})(?:(?:-|\/|\,)(?:|\d{4}))?)*))$')
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

        if quartz_regex.match(self.value):
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
image_regex = re.compile(r"^[\w][\w\-.]+/?[\w][\w\-.]+$")
tag_regex = re.compile(r"")


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


class TimeZoneNameParamType(click.ParamType):
    name = 'TimeZoneName'

    def convert(self, value, param, ctx) -> str:
        if value not in pytz.all_timezones:
            self.fail(f"TimeZone does not exist", param, ctx=ctx)
        return value


TIMEZONE = TimeZoneNameParamType()


class DockerImageName(click.ParamType):
    name = 'DockerImageName'

    def convert(self, value, param, ctx) -> str:
        if not image_regex.match(value):
            self.fail(f"Invalid docker image name", ctx=ctx)
        return value


DOCKER_IMAGE = DockerImageName()


class DockerTagName(click.ParamType):
    name = 'DockerTagName'

    def convert(self, value, param, ctx):
        if not tag_regex.match(value):
            self.fail("Invalid docker tag name", ctx=ctx)
        return value


DOCKER_TAG = DockerTagName()


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

        except AliasAlreadyExistsError:
            click.secho(f"[ERROR] This alias/name is already taken", err=True, fg='red')
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


class SetImportFile(click.Option):
    @staticmethod
    def fill_context(ctx, value):
        with open(value, 'r') as document:
            ctx.file_defaults = yaml.load(document)

    def full_process_value(self, ctx, value):
        file_name = super().full_process_value(ctx, value)
        if file_name:
            self.fill_context(ctx, file_name)
        return file_name


class CanBeImported(click.Option):
    def get_default(self, ctx):
        try:
            return ctx.file_defaults[str(self.name)]
        except (AttributeError, KeyError):
            return super().get_default(ctx)


def can_be_imported(name: Optional[str] = None, fn: Optional[Callable[[Any], Any]] = None):
    class CanBeImportedWith(click.Option):
        def get_default(self, ctx):
            try:
                value = ctx.file_defaults[name if name else str(self.name)]
                return fn(value) if fn else value
            except (AttributeError, IndexError, KeyError):
                return super().get_default(ctx)

    return CanBeImportedWith


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

class CronTypeParamType(click.ParamType):
    name = 'crontype'
    available_cron_types = ['UNIX', 'QUARTZ']

    @property
    def default(self):
        return self.available_cron_types[0]

    def convert(self, value, param, ctx):
        if value is None:
            self.fail("Cron Type expression cannot be null")

        if value.upper() not in self.available_cron_types:
            self.fail(f"Cron Type only supports {self.available_cron_types}")

        return value.upper()


CRONTYPE = CronTypeParamType()
