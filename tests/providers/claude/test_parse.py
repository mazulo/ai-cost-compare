from datetime import date

import pytest

from ai_cost_compare.core.errors import CliError
from ai_cost_compare.providers.claude.parse import ClaudeParser


@pytest.fixture
def parser():
    return ClaudeParser()


def test_parse_daily_records(parser, claude_records):
    assert len(claude_records) >= 5
    assert claude_records[0].date == date(2026, 5, 6)
    assert claude_records[0].cost > 0
    assert "opus" in claude_records[0].mix


def test_parse_v20_period_field(parser, claude_daily_v20_raw):
    raw = claude_daily_v20_raw
    records = parser.parse(raw)
    assert len(records) == 2
    assert records[1].mix["haiku"] == pytest.approx(3.0)


def test_parse_merges_duplicate_period_rows(parser):
    raw = {
        "daily": [
            {
                "period": "2026-05-08",
                "totalCost": 10.0,
                "totalTokens": 100,
                "modelBreakdowns": [{"modelName": "claude-opus-4-7", "cost": 10.0}],
            },
            {
                "period": "2026-05-08",
                "totalCost": 5.0,
                "totalTokens": 50,
                "modelBreakdowns": [{"modelName": "claude-sonnet-4-6", "cost": 5.0}],
            },
        ]
    }
    records = parser.parse(raw)
    assert len(records) == 1
    assert records[0].cost == pytest.approx(15.0)


def test_parse_missing_date_raises(parser):
    with pytest.raises(CliError, match="date.*period"):
        parser.parse({"daily": [{"totalCost": 1.0, "totalTokens": 0, "modelBreakdowns": []}]})


def test_parse_iso_date_with_time(parser):
    raw = {
        "daily": [
            {
                "date": "2026-05-07T12:00:00",
                "totalCost": 1.0,
                "totalTokens": 10,
                "modelBreakdowns": [],
            }
        ]
    }
    records = parser.parse(raw)
    assert records[0].date == date(2026, 5, 7)
