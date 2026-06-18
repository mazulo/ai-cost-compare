from io import StringIO

from rich.console import Console

from ai_cost_compare.core.windows import split_records, window_stats
from ai_cost_compare.providers.registry import get
from ai_cost_compare.render.report import render_report


def test_render_report_contains_sections(claude_records, cutoff_date):
    before, after = split_records(claude_records, cutoff_date)
    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100, color_system="truecolor")
    render_report(
        console,
        provider=get("claude"),
        records=claude_records,
        cutoff=cutoff_date,
        summary_mode=False,
        before=window_stats(before),
        after=window_stats(after),
    )
    text = output.getvalue()
    assert "CLAUDE DAILY COST" in text
    assert "BEFORE vs AFTER" in text
    assert "REAL SIGNAL" in text


def test_render_summary_mode_skips_comparison(claude_records, cutoff_date):
    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100, color_system="truecolor")
    render_report(
        console,
        provider=get("claude"),
        records=claude_records,
        cutoff=cutoff_date,
        summary_mode=True,
        before=None,
        after=None,
    )
    text = output.getvalue()
    assert "BEFORE vs AFTER" not in text
    assert "REAL SIGNAL" not in text
