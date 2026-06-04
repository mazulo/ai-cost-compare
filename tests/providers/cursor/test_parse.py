import json
from datetime import date
from pathlib import Path

import pytest

from ai_cost_compare.providers.cursor.parse import parse_usage_csv

FIXTURE = Path(__file__).parents[2] / "fixtures" / "cursor" / "sample_usage.csv"


def test_parse_cursor_csv():
    records = parse_usage_csv(FIXTURE.read_text())
    assert len(records) == 4
    assert records[0].date == date(2026, 5, 6)
    assert records[0].mix["premium"] == pytest.approx(1.2)
    assert records[0].mix["fast"] == pytest.approx(0.15)


def test_parse_cursor_csv_aggregates_same_day():
    csv_text = """Date,Model,Cost,Cost to you
2026-05-10,claude-opus-4-6,5.00,5.00
2026-05-10,claude-haiku-4-5,1.00,1.00
"""
    records = parse_usage_csv(csv_text)
    assert len(records) == 1
    assert records[0].cost == pytest.approx(6.0)
    assert records[0].mix["premium"] == pytest.approx(5.0)
    assert records[0].mix["fast"] == pytest.approx(1.0)
