from ai_cost_compare.providers.base import VerdictEngine
from ai_cost_compare.providers.claude.config import VERDICTS


class ClaudeVerdicts(VerdictEngine):
    bucket_order = VERDICTS.bucket_order
    specs = VERDICTS.specs
    legend_items = VERDICTS.legend_items
