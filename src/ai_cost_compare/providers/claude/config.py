"""Claude-specific thresholds and model family mapping."""

COST_WARN = 20.0
COST_ALERT = 50.0
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
