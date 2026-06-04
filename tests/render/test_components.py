from datetime import date
from io import StringIO

from rich.console import Console

from ai_cost_compare.providers.claude.verdicts import ClaudeVerdicts
from ai_cost_compare.render.components import (
    base_table,
    era_cell,
    legend,
    section,
    styled_cost,
    styled_pct,
)


def test_section_and_legend():
    output = StringIO()
    console = Console(file=output, force_terminal=True, width=80)
    section(console, "TITLE", "subtitle")
    legend(console, ClaudeVerdicts().profile())
    text = output.getvalue()
    assert "TITLE" in text
    assert "Legend" in text


def test_era_cell_today():
    cell = era_cell(date(2026, 5, 8), date(2026, 5, 8))
    assert "Today" in str(cell)


def test_styled_helpers():
    assert "$" in str(styled_cost(10.0))
    assert "%" in str(styled_pct(50, "green"))


def test_base_table_column_width():
    table = base_table(("A", {"width": 5}))
    assert table.columns[0].width == 5
