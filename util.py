import click


def success(text: str) -> str:
    return f'\n[{click.style("SUCCESS", fg="green")}] {text}'
