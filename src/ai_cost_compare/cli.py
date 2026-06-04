import sys
from datetime import date
from typing import Annotated

from cyclopts import App, Parameter

from ai_cost_compare.core.errors import CliError
from ai_cost_compare.core.windows import compute_since, split_records, window_stats
from ai_cost_compare.providers.base import FetchContext
from ai_cost_compare.providers.registry import get
from ai_cost_compare.render.console import make_console
from ai_cost_compare.render.report import render_report

app = App(name="ai-cost-compare", help_format="markdown")


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
    """
    provider = get("claude")
    split_date = cutoff or date.today()
    since_date = compute_since(split_date, range_days, since)
    until_date = date.today()

    ctx = FetchContext(since=since_date, until=until_date)
    raw = provider.fetch(ctx)
    records = provider.parse(raw)
    before_records, after_records = split_records(records, split_date)
    before = window_stats(before_records)
    after = window_stats(after_records)

    console = make_console(plain=plain)
    render_report(
        console,
        provider=provider,
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
