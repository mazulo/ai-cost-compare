from dataclasses import dataclass

from ai_cost_compare.providers.base import ModelTaxonomy
from ai_cost_compare.providers.claude import config
from ai_cost_compare.providers.claude.config import model_family

INACTIVE = "grey78"
ZERO = "grey62"


@dataclass(frozen=True)
class ClaudeTaxonomy(ModelTaxonomy):
    def classify(self, model_name: str) -> str:
        return model_family(model_name)

    def share_style(self, bucket: str, share: int) -> str:
        if bucket == "opus":
            if share > config.OPUS_LEAK:
                return "bold red"
            if share > 50:
                return "yellow"
            return "white"
        if bucket == "sonnet":
            if share > config.SONNET_ACTIVE:
                return "bold green"
            if share > 0:
                return "white"
            return INACTIVE
        if bucket == "haiku":
            if share > config.HAIKU_DELEGATING:
                return "bright_cyan"
            if share > 0:
                return "cyan"
            return INACTIVE
        if share > 0:
            return "white"
        return ZERO


CLAUDE_TAXONOMY = ClaudeTaxonomy(
    buckets=("opus", "sonnet", "haiku"),
    labels={"opus": "Opus", "sonnet": "Sonnet", "haiku": "Haiku", "other": "Other"},
    bar_colors={"opus": "red", "sonnet": "green", "haiku": "bright_cyan", "other": "grey70"},
)
