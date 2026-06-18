"""Cursor model tier thresholds and verdict configuration."""

from ai_cost_compare.providers.verdict_spec import ShareVerdictSpec, VerdictConfig

PREMIUM_SHARE_HIGH = 70
PREMIUM_SHARE_WARN = 50
FAST_SHARE_GOOD = 20

VERDICTS = VerdictConfig(
    bucket_order=("premium", "fast"),
    legend_items=(
        ("Premium >70%", "bold red"),
        ("50–70%", "yellow"),
        ("Fast >20%", "bold green"),
        ("Cost >$50", "bold red"),
        (">$20", "yellow"),
    ),
    specs={
        "premium": ShareVerdictSpec(
            thresholds=(
                (PREMIUM_SHARE_HIGH, "red", "❌  Premium-heavy — try Fast tier models"),
                (PREMIUM_SHARE_WARN, "yellow", "⚠️  Premium share elevated"),
            ),
            default=("green", "✅  Premium share OK"),
        ),
        "fast": ShareVerdictSpec(
            thresholds=(
                (FAST_SHARE_GOOD, "green", "✅  Good Fast-tier usage"),
                (0, "yellow", "⚡  Some Fast usage"),
            ),
            default=("grey70", "⚪  No Fast-tier usage"),
        ),
    },
)
