from ai_cost_compare.providers.base import VerdictEngine
from ai_cost_compare.providers.claude import config
from ai_cost_compare.providers.verdict_spec import ShareVerdictSpec


class ClaudeVerdicts(VerdictEngine):
    bucket_order = ("opus", "sonnet", "haiku")
    legend_items = (
        ("Opus >80%", "bold red"),
        ("50–80%", "yellow"),
        ("<50%", "green"),
        ("Sonnet >30%", "bold green"),
        ("Cost >$50", "bold red"),
        (">$20", "yellow"),
    )
    specs = {
        "opus": ShareVerdictSpec(
            thresholds=(
                (config.OPUS_LEAK, "red", "❌  Routing leak — shift to Sonnet/Haiku"),
                (config.OPUS_HIGH, "yellow", "⚠️  Still high — check routing rules"),
                (config.OPUS_IMPROVING, "yellow", "⚡  Improving"),
            ),
            default=("green", "✅  On target"),
        ),
        "sonnet": ShareVerdictSpec(
            thresholds=(
                (config.SONNET_ACTIVE, "green", "✅  Routing active"),
                (config.SONNET_GROWING, "yellow", "⚡  Growing"),
                (0, "yellow", "⚠️  Low — check 3-tier routing"),
            ),
            default=("grey70", "⚪  Unused"),
        ),
        "haiku": ShareVerdictSpec(
            thresholds=(
                (config.HAIKU_HEAVY, "green", "✅  Heavy delegation"),
                (config.HAIKU_DELEGATING, "green", "✅  Delegating"),
                (0, "bright_cyan", "⚡  Light"),
            ),
            default=("grey70", "⚪  Unused — use for lookups/reviews"),
        ),
    }
