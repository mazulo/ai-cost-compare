from collections import defaultdict
from datetime import date, timedelta

from claude_cost_compare.data.models import DailyRecord, WindowStats


def compute_since(
    cutoff: date,
    range_days: int,
    since_override: date | None,
) -> date:
    if since_override is not None:
        return since_override
    return cutoff - timedelta(days=range_days)


def split_records(
    records: list[DailyRecord],
    cutoff: date,
) -> tuple[list[DailyRecord], list[DailyRecord]]:
    before = [record for record in records if record.date < cutoff]
    after = [record for record in records if record.date >= cutoff]
    return before, after


def window_stats(records: list[DailyRecord]) -> WindowStats | None:
    if not records:
        return None
    total_cost = sum(record.cost for record in records)
    mix: dict[str, float] = defaultdict(float)
    for record in records:
        for family, value in record.mix.items():
            mix[family] += value
    count = len(records)
    return WindowStats(
        n=count,
        total=total_cost,
        avg=total_cost / count,
        mix=dict(mix),
    )
