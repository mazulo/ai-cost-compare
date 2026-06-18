"""Claude-specific thresholds, taxonomy, and verdict configuration."""

from ai_cost_compare.providers.verdict_spec import ShareVerdictSpec, VerdictConfig

OPUS_LEAK = 80
OPUS_HIGH = 60
OPUS_IMPROVING = 40
SONNET_ACTIVE = 30
SONNET_GROWING = 10
HAIKU_HEAVY = 10
HAIKU_DELEGATING = 3


def model_family(name: str) -> str:
    normalized = name.lower()
    if "opus" in normalized:
        return "opus"
    if "sonnet" in normalized:
        return "sonnet"
    if "haiku" in normalized:
        return "haiku"
    return "other"


VERDICTS = VerdictConfig(
    bucket_order=("opus", "sonnet", "haiku"),
    legend_items=(
        ("Opus >80%", "bold red"),
        ("50–80%", "yellow"),
        ("<50%", "green"),
        ("Sonnet >30%", "bold green"),
        ("Cost >$50", "bold red"),
        (">$20", "yellow"),
    ),
    specs={
        "opus": ShareVerdictSpec(
            thresholds=(
                (OPUS_LEAK, "red", "❌  Routing leak — shift to Sonnet/Haiku"),
                (OPUS_HIGH, "yellow", "⚠️  Still high — check routing rules"),
                (OPUS_IMPROVING, "yellow", "⚡  Improving"),
            ),
            default=("green", "✅  On target"),
        ),
        "sonnet": ShareVerdictSpec(
            thresholds=(
                (SONNET_ACTIVE, "green", "✅  Routing active"),
                (SONNET_GROWING, "yellow", "⚡  Growing"),
                (0, "yellow", "⚠️  Low — check 3-tier routing"),
            ),
            default=("grey70", "⚪  Unused"),
        ),
        "haiku": ShareVerdictSpec(
            thresholds=(
                (HAIKU_HEAVY, "green", "✅  Heavy delegation"),
                (HAIKU_DELEGATING, "green", "✅  Delegating"),
                (0, "bright_cyan", "⚡  Light"),
            ),
            default=("grey70", "⚪  Unused — use for lookups/reviews"),
        ),
    },
)
