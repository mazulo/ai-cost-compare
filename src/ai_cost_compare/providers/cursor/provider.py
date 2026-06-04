from typing import Any

from ai_cost_compare.config_store import load_cursor_token
from ai_cost_compare.core.errors import CursorDataError
from ai_cost_compare.providers.base import (
    FetchContext,
    ReportTitles,
    UsageProvider,
    VerdictProfile,
)
from ai_cost_compare.providers.cursor import fetch_api, parse, verdicts
from ai_cost_compare.providers.cursor.taxonomy import CURSOR_TAXONOMY


class CursorProvider:
    id = "cursor"
    display_name = "Cursor"

    def fetch(self, ctx: FetchContext) -> str:
        if ctx.file is not None:
            return ctx.file.read_text(encoding="utf-8")
        token = ctx.cursor_token or load_cursor_token()
        if token:
            return fetch_api.fetch_usage_csv(token)
        raise CursorDataError(
            "Cursor usage requires --file PATH or a session token.\n"
            "  CSV: export from https://cursor.com/dashboard/usage\n"
            "  API: pip install 'ai-cost-compare[cursor-api]' and set "
            "[cursor] session_token in ~/.config/ai-cost-compare/config.toml"
        )

    def parse(self, raw: Any) -> list:
        return parse.parse_usage_csv(raw)

    def taxonomy(self):
        return CURSOR_TAXONOMY

    def verdict_profile(self) -> VerdictProfile:
        return VerdictProfile(
            families=(
                ("premium", verdicts.verdict_premium),
                ("fast", verdicts.verdict_fast),
            ),
            legend_items=(
                ("Premium >70%", "bold red"),
                ("50–70%", "yellow"),
                ("Fast >20%", "bold green"),
                ("Cost >$50", "bold red"),
                (">$20", "yellow"),
            ),
        )

    def titles(self) -> ReportTitles:
        return ReportTitles(daily="CURSOR DAILY COST", signal="USAGE SIGNAL")


provider: UsageProvider = CursorProvider()
