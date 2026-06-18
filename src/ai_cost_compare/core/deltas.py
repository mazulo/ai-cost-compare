from ai_cost_compare.core.models import ComparisonResult, WindowStats


def pct(value: float, total: float) -> int:
    return round(value / total * 100) if total else 0


def compare_windows(
    before: WindowStats | None,
    after: WindowStats | None,
    *,
    buckets: tuple[str, ...],
) -> ComparisonResult | None:
    if not before or not after:
        return None
    delta_mix_pp: dict[str, int] = {}
    for bucket in buckets:
        delta_mix_pp[bucket] = pct(after.mix.get(bucket, 0.0), after.total) - pct(
            before.mix.get(bucket, 0.0),
            before.total,
        )
    return ComparisonResult(
        before=before,
        after=after,
        delta_avg=after.avg - before.avg,
        delta_mix_pp=delta_mix_pp,
    )
