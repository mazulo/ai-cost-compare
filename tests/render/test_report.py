from datetime import date
from io import StringIO

from rich.console import Console

from ai_cost_compare.core.models import WindowStats
from ai_cost_compare.providers.registry import get
from ai_cost_compare.render.report import render_report


def test_render_empty_records():
    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    render_report(
        console,
        provider=get("claude"),
        records=[],
        cutoff=date(2026, 5, 8),
        summary_mode=False,
        before=None,
        after=None,
    )
    assert "No usage data" in output.getvalue()


def test_render_signal_latest_day_only(claude_records):
    """No after-window data: signal falls back to latest day."""
    cutoff = date(2099, 1, 1)
    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    render_report(
        console,
        provider=get("claude"),
        records=claude_records,
        cutoff=cutoff,
        summary_mode=False,
        before=None,
        after=None,
    )
    text = output.getvalue()
    assert "Latest day only" in text
    assert "REAL SIGNAL" in text


def test_render_comparison_one_sided_window(claude_records):
    cutoff = date(2026, 5, 6)
    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    after = WindowStats(n=1, total=10.0, avg=10.0, mix={"opus": 10.0})
    render_report(
        console,
        provider=get("claude"),
        records=claude_records,
        cutoff=cutoff,
        summary_mode=False,
        before=None,
        after=after,
    )
    assert "BEFORE vs AFTER" in output.getvalue()


def test_render_cursor_provider(cursor_csv_text):
    from ai_cost_compare.providers.cursor.parse import CursorParser

    records = CursorParser().parse_csv(cursor_csv_text)
    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    render_report(
        console,
        provider=get("cursor"),
        records=records,
        cutoff=date(2026, 5, 8),
        summary_mode=False,
        before=None,
        after=WindowStats(n=2, total=5.0, avg=2.5, mix={"premium": 5.0}),
    )
    assert "CURSOR DAILY COST" in output.getvalue()
    assert "USAGE SIGNAL" in output.getvalue()
