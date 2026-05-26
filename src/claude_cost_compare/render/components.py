from datetime import date

from rich.console import Console
from rich.table import Table
from rich.text import Text

from claude_cost_compare.render.formatters import (
    cost_style,
    era_label,
    era_style,
    fmt_cost,
)
from claude_cost_compare.render.theme import (
    MUTED,
    SECTION_TITLE,
    TABLE_BORDER,
    TABLE_BOX,
    TABLE_HEADER,
)


def section(console: Console, title: str, subtitle: str = "") -> None:
    line = Text()
    line.append(title, style=SECTION_TITLE)
    if subtitle:
        line.append("  ·  ", style=MUTED)
        line.append(subtitle, style=MUTED)
    console.print()
    console.print(line)


def base_table(*columns: tuple[str, dict]) -> Table:
    table = Table(
        box=TABLE_BOX,
        show_header=True,
        header_style=TABLE_HEADER,
        border_style=TABLE_BORDER,
        padding=(0, 1),
        expand=False,
        show_edge=True,
    )
    for name, kwargs in columns:
        table.add_column(name, **kwargs)
    return table


def print_table(console: Console, table: Table) -> None:
    console.print(table, justify="left")


def styled_cost(amount: float) -> Text:
    return Text(fmt_cost(amount), style=cost_style(amount) or "white")


def styled_pct(share: int, style: str) -> Text:
    return Text(f"{share}%", style=style or "white")


def era_cell(record_date: date, cutoff: date) -> Text:
    era = era_label(record_date, cutoff)
    labels = {"BEFORE": "Before", "TODAY ": "Today", "AFTER ": "After"}
    return Text(labels.get(era, era.strip()), style=era_style(era))


def legend(console: Console) -> None:
    console.print()
    line = Text("Legend  ", style=MUTED)
    for label, color in (
        ("Opus >80%", "bold red"),
        ("50–80%", "yellow"),
        ("<50%", "green"),
        ("Sonnet >30%", "bold green"),
        ("Cost >$50", "bold red"),
        (">$20", "yellow"),
    ):
        line.append(" ● ", style=color)
        line.append(label, style=MUTED)
        line.append("   ")
    console.print(line, justify="left")
