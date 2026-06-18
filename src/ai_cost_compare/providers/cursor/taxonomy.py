from dataclasses import dataclass

from ai_cost_compare.providers.base import ModelTaxonomy
from ai_cost_compare.providers.cursor import config

INACTIVE = "grey78"
ZERO = "grey62"

_PREMIUM_HINTS = (
    "opus",
    "o1",
    "o3",
    "gpt-4",
    "gpt-5",
    "sonnet",
    "pro",
    "ultra",
    "max",
)
_FAST_HINTS = (
    "haiku",
    "mini",
    "flash",
    "fast",
    "nano",
    "3.5",
    "small",
    "lite",
)


def classify_cursor_model(model_name: str) -> str:
    normalized = model_name.lower()
    if any(hint in normalized for hint in _PREMIUM_HINTS):
        return "premium"
    if any(hint in normalized for hint in _FAST_HINTS):
        return "fast"
    return "other"


@dataclass(frozen=True)
class CursorTaxonomy(ModelTaxonomy):
    def classify(self, model_name: str) -> str:
        return classify_cursor_model(model_name)

    def share_style(self, bucket: str, share: int) -> str:
        if bucket == "premium":
            if share > config.PREMIUM_SHARE_HIGH:
                return "bold red"
            if share > config.PREMIUM_SHARE_WARN:
                return "yellow"
            return "white"
        if bucket == "fast":
            if share > config.FAST_SHARE_GOOD:
                return "bold green"
            if share > 0:
                return "bright_cyan"
            return INACTIVE
        if share > 0:
            return "white"
        return ZERO


CURSOR_TAXONOMY = CursorTaxonomy(
    buckets=("premium", "fast"),
    labels={"premium": "Premium", "fast": "Fast", "other": "Other"},
    bar_colors={"premium": "red", "fast": "bright_cyan", "other": "grey70"},
)
