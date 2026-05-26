import json
from datetime import date
from pathlib import Path

import pytest

from claude_cost_compare.analysis.deltas import compare_windows, pct
from claude_cost_compare.analysis.verdicts import verdict_opus, verdict_sonnet
from claude_cost_compare.analysis.windows import split_records, window_stats
from claude_cost_compare.data.parser import parse_daily_records

FIXTURE = Path(__file__).parent / "fixtures" / "sample_daily.json"


@pytest.fixture
def records():
    raw = json.loads(FIXTURE.read_text())
    return parse_daily_records(raw)


def test_parse_daily_records(records):
    assert len(records) >= 5
    assert records[0].date == date(2026, 5, 6)
    assert records[0].cost > 0
    assert "opus" in records[0].mix


def test_window_stats(records):
    stats = window_stats(records[:3])
    assert stats is not None
    assert stats.n == 3
    assert stats.avg == pytest.approx(stats.total / 3)


def test_split_records(records):
    cutoff = date(2026, 5, 8)
    before, after = split_records(records, cutoff)
    assert all(record.date < cutoff for record in before)
    assert all(record.date >= cutoff for record in after)


def test_compare_windows(records):
    cutoff = date(2026, 5, 8)
    before, after = split_records(records, cutoff)
    comparison = compare_windows(window_stats(before), window_stats(after))
    assert comparison is not None
    assert isinstance(comparison.delta_avg, float)


def test_verdict_opus_leak():
    style, text = verdict_opus(81, 90)
    assert style == "red"
    assert "Routing leak" in text


def test_verdict_sonnet_active():
    style, text = verdict_sonnet(31, 10)
    assert style == "green"
    assert "Routing active" in text


def test_pct():
    assert pct(25, 100) == 25
    assert pct(0, 0) == 0
