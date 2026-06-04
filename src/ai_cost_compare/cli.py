import sys
from datetime import date
from pathlib import Path
from typing import Annotated

from cyclopts import App, Parameter

from ai_cost_compare.core.errors import CliError
from ai_cost_compare.core.windows import compute_since, split_records, window_stats
from ai_cost_compare.providers.base import FetchContext
from ai_cost_compare.providers.registry import get
from ai_cost_compare.render.console import make_console
from ai_cost_compare.render.report import render_report

app = App(name="ai-cost-compare", help_format="markdown")


def _run_provider(
    provider_id: str,
    *,
    range_days: int,
    cutoff: date | None,
    since: date | None,
    summary: bool,
    plain: bool,
    file: Path | None = None,
    cursor_token: str | None = None,
) -> None:
    provider = get(provider_id)
    split_date = cutoff or date.today()
    since_date = compute_since(split_date, range_days, since)
    until_date = date.today()

    ctx = FetchContext(
        since=since_date,
        until=until_date,
        file=file,
        cursor_token=cursor_token,
    )
    raw = provider.fetch(ctx)
    records = provider.parse(raw)
    if provider_id == "cursor":
        records = [record for record in records if since_date <= record.date <= until_date]

    before_records, after_records = split_records(records, split_date)
    console = make_console(plain=plain)
    render_report(
        console,
        provider=provider,
        records=records,
        cutoff=split_date,
        summary_mode=summary,
        before=window_stats(before_records),
        after=window_stats(after_records),
    )


@app.default
@app.command(name="claude")
def claude(
    range_days: Annotated[int, Parameter(name=["--range", "-r"])] = 5,
    cutoff: Annotated[date | None, Parameter(name=["--cutoff", "-c"])] = None,
    since: Annotated[date | None, Parameter(name=["--since", "-s"])] = None,
    summary: Annotated[bool, Parameter(name="--summary")] = False,
    plain: Annotated[bool, Parameter(name="--plain")] = False,
) -> None:
    """Daily Claude Code cost analysis (via ccusage).

    Shows daily cost table, before/after comparison, and model health signal.
    """
    _run_provider(
        "claude",
        range_days=range_days,
        cutoff=cutoff,
        since=since,
        summary=summary,
        plain=plain,
    )


@app.command(name="cursor")
def cursor(
    range_days: Annotated[int, Parameter(name=["--range", "-r"])] = 5,
    cutoff: Annotated[date | None, Parameter(name=["--cutoff", "-c"])] = None,
    since: Annotated[date | None, Parameter(name=["--since", "-s"])] = None,
    summary: Annotated[bool, Parameter(name="--summary")] = False,
    plain: Annotated[bool, Parameter(name="--plain")] = False,
    file: Annotated[
        Path | None,
        Parameter(name=["--file", "-f"], help="CSV exported from Cursor dashboard"),
    ] = None,
    cursor_token: Annotated[
        str | None,
        Parameter(name="--cursor-token", help="WorkosCursorSessionToken (overrides config)"),
    ] = None,
) -> None:
    """Daily Cursor IDE cost analysis from dashboard CSV export."""
    _run_provider(
        "cursor",
        range_days=range_days,
        cutoff=cutoff,
        since=since,
        summary=summary,
        plain=plain,
        file=file,
        cursor_token=cursor_token,
    )


def run() -> None:
    try:
        app()
    except CliError as exc:
        print(exc.message, file=sys.stderr)
        raise SystemExit(exc.exit_code) from exc


def run_claude_legacy() -> None:
    sys.argv = [sys.argv[0], "claude", *sys.argv[1:]]
    run()
