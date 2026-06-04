import json
from datetime import date
from pathlib import Path

import pytest

from ai_cost_compare.core.deltas import compare_windows, pct
from ai_cost_compare.core.windows import split_records, window_stats
from ai_cost_compare.providers.claude.parse import ClaudeParser
from ai_cost_compare.providers.claude.verdicts import ClaudeVerdicts

FIXTURE = Path(__file__).parent / "fixtures" / "sample_daily.json"


@pytest.fixture
def records():
    raw = json.loads(FIXTURE.read_text())
    return ClaudeParser().parse(raw)


@pytest.fixture
def verdicts():
    return ClaudeVerdicts()


def test_parse_daily_records(records):
    assert len(records) >= 5
    assert records[0].date == date(2026, 5, 6)
    assert records[0].cost > 0
    assert "opus" in records[0].mix


def test_parse_daily_records_ccusage_v20_period_field():
    raw = json.loads((Path(__file__).parent / "fixtures" / "sample_daily_v20.json").read_text())
    records = ClaudeParser().parse(raw)
    assert len(records) == 2
    assert records[0].date == date(2026, 5, 6)
    assert records[1].date == date(2026, 5, 7)
    assert records[1].mix["haiku"] == pytest.approx(3.0)


def test_parse_daily_records_merges_duplicate_period_rows():
    raw = {
        "daily": [
            {
                "period": "2026-05-08",
                "totalCost": 10.0,
                "totalTokens": 100,
                "modelBreakdowns": [
                    {"modelName": "claude-opus-4-7", "cost": 10.0},
                ],
            },
            {
                "period": "2026-05-08",
                "totalCost": 5.0,
                "totalTokens": 50,
                "modelBreakdowns": [
                    {"modelName": "claude-sonnet-4-6", "cost": 5.0},
                ],
            },
        ]
    }
    records = ClaudeParser().parse(raw)
    assert len(records) == 1
    assert records[0].cost == pytest.approx(15.0)
    assert records[0].tokens == 150
    assert records[0].mix["opus"] == pytest.approx(10.0)
    assert records[0].mix["sonnet"] == pytest.approx(5.0)


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
    comparison = compare_windows(
        window_stats(before),
        window_stats(after),
        buckets=("opus", "sonnet", "haiku"),
    )
    assert comparison is not None
    assert isinstance(comparison.delta_avg, float)


def test_verdict_opus_leak(verdicts):
    style, text = verdicts.evaluate("opus", 81, 90)
    assert style == "red"
    assert "Routing leak" in text


def test_verdict_sonnet_active(verdicts):
    style, text = verdicts.evaluate("sonnet", 31, 10)
    assert style == "green"
    assert "Routing active" in text


def test_pct():
    assert pct(25, 100) == 25
    assert pct(0, 0) == 0
