import click

from kronbute import ServerException


def success(text: str) -> str:
    return f'\n{click.style("[SUCCESS]", fg="green")} {text}'


def error(text: str, err: ServerException) -> str:
    msg_type = click.style('[ERROR]', fg='red')

    return f'{msg_type} {text}, code: {err.code}, message: {err.body}'
