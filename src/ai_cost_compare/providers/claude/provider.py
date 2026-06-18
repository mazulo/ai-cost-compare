from typing import Any

from ai_cost_compare.providers.base import (
    FetchContext,
    ReportTitles,
    UsageProvider,
)
from ai_cost_compare.providers.claude.fetch import ClaudeFetcher
from ai_cost_compare.providers.claude.parse import ClaudeParser
from ai_cost_compare.providers.claude.taxonomy import CLAUDE_TAXONOMY
from ai_cost_compare.providers.claude.verdicts import ClaudeVerdicts


class ClaudeProvider:
    id = "claude"
    display_name = "Claude Code"

    def __init__(self) -> None:
        self.fetcher = ClaudeFetcher()
        self.parser = ClaudeParser()
        self.verdicts = ClaudeVerdicts()
        self._taxonomy = CLAUDE_TAXONOMY

    def fetch(self, ctx: FetchContext) -> dict[str, Any]:
        return self.fetcher.fetch(ctx)

    def parse(self, raw: dict[str, Any]) -> list:
        return self.parser.parse(raw)

    def taxonomy(self):
        return self._taxonomy

    def verdict_profile(self):
        return self.verdicts.profile()

    def titles(self) -> ReportTitles:
        return ReportTitles(daily="CLAUDE DAILY COST", signal="REAL SIGNAL")


provider: UsageProvider = ClaudeProvider()
