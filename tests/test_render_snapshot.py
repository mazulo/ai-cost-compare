import json
from datetime import date
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest
from rich.console import Console

from ai_cost_compare.analysis.windows import split_records, window_stats
from ai_cost_compare.data.parser import parse_daily_records
from ai_cost_compare.render.report import render_report

FIXTURE = Path(__file__).parent / "fixtures" / "sample_daily.json"


def test_render_report_contains_sections():
    records = parse_daily_records(json.loads(FIXTURE.read_text()))
    cutoff = date(2026, 5, 8)
    before, after = split_records(records, cutoff)
    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100, color_system="truecolor")
    render_report(
        console,
        records=records,
        cutoff=cutoff,
        summary_mode=False,
        before=window_stats(before),
        after=window_stats(after),
    )
    text = output.getvalue()
    assert "CLAUDE DAILY COST" in text
    assert "BEFORE vs AFTER" in text
    assert "REAL SIGNAL" in text


def test_render_summary_mode_skips_comparison():
    records = parse_daily_records(json.loads(FIXTURE.read_text()))
    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100, color_system="truecolor")
    render_report(
        console,
        records=records,
        cutoff=date(2026, 5, 8),
        summary_mode=True,
        before=None,
        after=None,
    )
    text = output.getvalue()
    assert "BEFORE vs AFTER" not in text
    assert "REAL SIGNAL" not in text


def test_find_ccusage_from_path(tmp_path):
    fake = tmp_path / "ccusage"
    fake.write_text("#!/bin/sh\necho '{\"daily\":[]}'\n")
    fake.chmod(0o755)
    from ai_cost_compare.data.ccusage import fetch_daily

    with patch("ai_cost_compare.data.ccusage.find_ccusage", return_value=fake):
        data = fetch_daily(date(2026, 5, 1), date(2026, 5, 2), ccusage_bin=fake)
    assert data == {"daily": []}


def test_find_ccusage_missing():
    from ai_cost_compare.data.ccusage import find_ccusage
    from ai_cost_compare.errors import CcusageNotFoundError

    with patch("ai_cost_compare.data.ccusage._nvm_ccusage_paths", return_value=[]):
        with patch("shutil.which", return_value=None):
            with pytest.raises(CcusageNotFoundError):
                find_ccusage()
