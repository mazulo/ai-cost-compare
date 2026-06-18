from datetime import date

from ai_cost_compare.providers.base import FetchContext
from ai_cost_compare.providers.cursor.provider import CursorProvider


def test_provider_metadata():
    provider = CursorProvider()
    assert provider.id == "cursor"
    assert provider.titles().daily == "CURSOR DAILY COST"


def test_provider_fetch_parse(tmp_path, cursor_csv_text):
    path = tmp_path / "usage.csv"
    path.write_text(cursor_csv_text)
    provider = CursorProvider()
    ctx = FetchContext(since=date(2026, 5, 1), until=date(2026, 5, 31), file=path)
    records = provider.parse(provider.fetch(ctx))
    assert records
