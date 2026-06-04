from typing import Any

from ai_cost_compare.providers.base import FetchContext, UsageProvider
from ai_cost_compare.providers.claude import fetch as claude_fetch
from ai_cost_compare.providers.claude import parse as claude_parse


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


provider: UsageProvider = ClaudeProvider()
