from ai_cost_compare.providers.base import VerdictEngine
from ai_cost_compare.providers.cursor import config
from ai_cost_compare.providers.verdict_spec import ShareVerdictSpec


class CursorVerdicts(VerdictEngine):
    bucket_order = ("premium", "fast")
    legend_items = (
        ("Premium >70%", "bold red"),
        ("50–70%", "yellow"),
        ("Fast >20%", "bold green"),
        ("Cost >$50", "bold red"),
        (">$20", "yellow"),
    )
    specs = {
        "premium": ShareVerdictSpec(
            thresholds=(
                (config.PREMIUM_SHARE_HIGH, "red", "❌  Premium-heavy — try Fast tier models"),
                (config.PREMIUM_SHARE_WARN, "yellow", "⚠️  Premium share elevated"),
            ),
            default=("green", "✅  Premium share OK"),
        ),
        "fast": ShareVerdictSpec(
            thresholds=(
                (config.FAST_SHARE_GOOD, "green", "✅  Good Fast-tier usage"),
                (0, "yellow", "⚡  Some Fast usage"),
            ),
            default=("grey70", "⚪  No Fast-tier usage"),
        ),
    }
