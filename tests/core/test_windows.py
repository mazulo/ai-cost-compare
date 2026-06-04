from datetime import date

from ai_cost_compare.core.windows import compute_since, split_records, window_stats


def test_compute_since_default_range():
    cutoff = date(2026, 5, 10)
    assert compute_since(cutoff, 5, None) == date(2026, 5, 5)


def test_compute_since_override():
    cutoff = date(2026, 5, 10)
    since = date(2026, 4, 1)
    assert compute_since(cutoff, 5, since) == since


def test_window_stats_empty():
    assert window_stats([]) is None


def test_window_stats_aggregates_mix(claude_records):
    stats = window_stats(claude_records[:2])
    assert stats is not None
    assert stats.n == 2
    assert stats.total == sum(record.cost for record in claude_records[:2])
    assert stats.avg == stats.total / 2


def test_split_records_includes_cutoff_in_after(claude_records, cutoff_date):
    before, after = split_records(claude_records, cutoff_date)
    assert before and after
    assert any(record.date == cutoff_date for record in after)
    assert all(record.date < cutoff_date for record in before)
