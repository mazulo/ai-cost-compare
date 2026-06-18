import os

from rich.console import Console


def make_console(*, plain: bool = False) -> Console:
    no_color = plain or bool(os.environ.get("NO_COLOR"))
    return Console(
        force_terminal=not no_color,
        no_color=no_color,
        highlight=False,
    )
