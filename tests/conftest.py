import json
from datetime import date
from pathlib import Path

import pytest

from ai_cost_compare.providers.claude.parse import ClaudeParser

FIXTURES = Path(__file__).parent / "fixtures"
CLAUDE_DAILY = FIXTURES / "sample_daily.json"
CLAUDE_DAILY_V20 = FIXTURES / "sample_daily_v20.json"
CURSOR_CSV = FIXTURES / "cursor" / "sample_usage.csv"


@pytest.fixture
def claude_daily_raw() -> dict:
    return json.loads(CLAUDE_DAILY.read_text())


@pytest.fixture
def claude_daily_v20_raw() -> dict:
    return json.loads(CLAUDE_DAILY_V20.read_text())


@pytest.fixture
def claude_records(claude_daily_raw):
    return ClaudeParser().parse(claude_daily_raw)


@pytest.fixture
def cursor_csv_text() -> str:
    return CURSOR_CSV.read_text()


@pytest.fixture
def cutoff_date() -> date:
    return date(2026, 5, 8)
