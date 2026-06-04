from ai_cost_compare.core.deltas import compare_windows, pct
from ai_cost_compare.core.models import WindowStats
from ai_cost_compare.core.windows import split_records, window_stats


def test_compare_windows_returns_none_when_missing_side():
    before = WindowStats(n=1, total=10.0, avg=10.0, mix={"opus": 10.0})
    assert compare_windows(before, None, buckets=("opus",)) is None
    assert compare_windows(None, before, buckets=("opus",)) is None


def test_compare_windows_delta_mix_pp(claude_records, cutoff_date):
    before, after = split_records(claude_records, cutoff_date)
    result = compare_windows(
        window_stats(before),
        window_stats(after),
        buckets=("opus", "sonnet", "haiku"),
    )
    assert result is not None
    assert "opus" in result.delta_mix_pp
    assert "sonnet" in result.delta_mix_pp
    assert "haiku" in result.delta_mix_pp


def test_pct_zero_total():
    assert pct(5, 0) == 0
