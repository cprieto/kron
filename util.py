import re
import click
from typing import Optional


from kronbute import ServerException


def success(text: str) -> str:
    return f'\n{click.style("[SUCCESS]", fg="green")} {text}'


def error(text: str, err: ServerException) -> str:
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
            self.fail("This doesn't look like a cron expression", value)

        return parsed


CRON = CronParamType()


def format_status(status: str) -> str:
    colors = {
        "FAILED": 'red',
        "SUCCESS": 'green',
        "RUNNING": 'yellow'
    }
    return click.style(status, fg=(colors[status] if status in colors else None))
