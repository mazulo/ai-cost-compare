from typing import Any

from ai_cost_compare.providers.base import (
    FetchContext,
    ReportTitles,
    UsageProvider,
    VerdictProfile,
)
from ai_cost_compare.providers.claude import fetch as claude_fetch
from ai_cost_compare.providers.claude import parse as claude_parse
from ai_cost_compare.providers.claude import verdicts
from ai_cost_compare.providers.claude.taxonomy import CLAUDE_TAXONOMY


class ClaudeProvider:
    id = "claude"
    display_name = "Claude Code"

    def fetch(self, ctx: FetchContext) -> dict[str, Any]:
        return claude_fetch.fetch_daily(
            ctx.since,
            ctx.until,
            ccusage_bin=ctx.ccusage_bin,
        )

    def parse(self, raw: dict[str, Any]) -> list:
        return claude_parse.parse_daily_records(raw)

    def taxonomy(self):
        return CLAUDE_TAXONOMY

    def verdict_profile(self) -> VerdictProfile:
        return VerdictProfile(
            families=(
                ("opus", verdicts.verdict_opus),
                ("sonnet", verdicts.verdict_sonnet),
                ("haiku", verdicts.verdict_haiku),
            ),
            legend_items=(
                ("Opus >80%", "bold red"),
                ("50–80%", "yellow"),
                ("<50%", "green"),
                ("Sonnet >30%", "bold green"),
                ("Cost >$50", "bold red"),
                (">$20", "yellow"),
            ),
        )

    def titles(self) -> ReportTitles:
        return ReportTitles(daily="CLAUDE DAILY COST", signal="REAL SIGNAL")


provider: UsageProvider = ClaudeProvider()
