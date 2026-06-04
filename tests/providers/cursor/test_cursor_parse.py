from datetime import date

import pytest

from ai_cost_compare.core.errors import CliError, CursorDataError
from ai_cost_compare.providers.cursor.parse import CursorParser


@pytest.fixture
def parser():
    return CursorParser()


def test_parse_cursor_csv(parser, cursor_csv_text):
    records = parser.parse_csv(cursor_csv_text)
    assert len(records) == 4
    assert records[0].date == date(2026, 5, 6)
    assert records[0].mix["premium"] == pytest.approx(1.2)


def test_parse_csv_aggregates_same_day(parser):
    csv_text = """Date,Model,Cost,Cost to you
2026-05-10,claude-opus-4-6,5.00,5.00
2026-05-10,claude-haiku-4-5,1.00,1.00
"""
    records = parser.parse_csv(csv_text)
    assert len(records) == 1
    assert records[0].cost == pytest.approx(6.0)


def test_parse_file(parser, cursor_csv_text, tmp_path):
    path = tmp_path / "usage.csv"
    path.write_text(cursor_csv_text)
    records = parser.parse_file(path)
    assert len(records) == 4


def test_parse_file_missing(parser, tmp_path):
    with pytest.raises(CursorDataError, match="not found"):
        parser.parse_file(tmp_path / "missing.csv")


def test_parse_empty_csv_header_only(parser):
    with pytest.raises(CursorDataError, match="header"):
        parser.parse_csv("")


def test_parse_missing_column(parser):
    with pytest.raises(CursorDataError, match="date"):
        parser.parse_csv("Model,Cost\nm,1\n")


def test_parse_empty_date(parser):
    with pytest.raises(CliError, match="empty date"):
        parser.parse_csv("Date,Model,Cost,Cost to you\n,claude-opus,1,1\n")


def test_parse_invalid_cost(parser):
    with pytest.raises(CursorDataError, match="Invalid cost"):
        parser.parse_csv("Date,Model,Cost,Cost to you\n2026-05-01,m,abc,abc\n")


def test_parse_us_date_format(parser):
    records = parser.parse_csv(
        "Date,Model,Cost,Cost to you\n05/10/2026,claude-opus-4-6,2.00,2.00\n"
    )
    assert records[0].date == date(2026, 5, 10)


def test_parse_skips_blank_rows(parser):
    records = parser.parse_csv("Date,Model,Cost,Cost to you\n2026-05-01,claude-opus-4-6,1,1\n,,,\n")
    assert len(records) == 1
