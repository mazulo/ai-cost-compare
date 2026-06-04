from ai_cost_compare.core.models import ComparisonResult, WindowStats


def pct(value: float, total: float) -> int:
    return round(value / total * 100) if total else 0


def compare_windows(
    before: WindowStats | None,
    after: WindowStats | None,
) -> ComparisonResult | None:
    if not before or not after:
        return None
    before_mix = before.mix
    after_mix = after.mix
    return ComparisonResult(
        before=before,
        after=after,
        delta_avg=after.avg - before.avg,
        delta_opus_pp=pct(after_mix.get("opus", 0.0), after.total)
        - pct(before_mix.get("opus", 0.0), before.total),
        delta_sonnet_pp=pct(after_mix.get("sonnet", 0.0), after.total)
        - pct(before_mix.get("sonnet", 0.0), before.total),
        delta_haiku_pp=pct(after_mix.get("haiku", 0.0), after.total)
        - pct(before_mix.get("haiku", 0.0), before.total),
    )
