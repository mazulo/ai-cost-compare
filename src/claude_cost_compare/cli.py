import sys
from datetime import date
from typing import Annotated

from cyclopts import App, Parameter

from claude_cost_compare.analysis.windows import compute_since, split_records, window_stats
from claude_cost_compare.data.ccusage import fetch_daily
from claude_cost_compare.data.parser import parse_daily_records
from claude_cost_compare.errors import CliError
from claude_cost_compare.render.console import make_console
from claude_cost_compare.render.report import render_report

app = App(name="claude-cost-compare", help_format="markdown")


@app.default
def main(
    range_days: Annotated[int, Parameter(name=["--range", "-r"])] = 5,
    cutoff: Annotated[date | None, Parameter(name=["--cutoff", "-c"])] = None,
    since: Annotated[date | None, Parameter(name=["--since", "-s"])] = None,
    summary: Annotated[bool, Parameter(name="--summary")] = False,
    plain: Annotated[bool, Parameter(name="--plain")] = False,
) -> None:
    """Daily Claude cost analysis.

    Shows daily cost table, before/after comparison, and model health signal.

    Parameters
    ----------
    range_days
        Days before cutoff to use as "before" baseline (default: 5).
    cutoff
        Before/after split date YYYY-MM-DD (default: today).
    since
        Explicit start date — overrides --range.
    summary
        Daily cost table only — no comparison tables.
    plain
        Disable color output (also respects NO_COLOR).
    """
    split_date = cutoff or date.today()
    since_date = compute_since(split_date, range_days, since)
    until_date = date.today()

    raw = fetch_daily(since_date, until_date)
    records = parse_daily_records(raw)
    before_records, after_records = split_records(records, split_date)
    before = window_stats(before_records)
    after = window_stats(after_records)

    console = make_console(plain=plain)
    render_report(
        console,
        records=records,
        cutoff=split_date,
        summary_mode=summary,
        before=before,
        after=after,
    )


def run() -> None:
    try:
        app()
    except CliError as exc:
        print(exc.message, file=sys.stderr)
        raise SystemExit(exc.exit_code) from exc
