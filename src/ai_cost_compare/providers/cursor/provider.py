from typing import Any

from ai_cost_compare.core.errors import CursorDataError
from ai_cost_compare.providers.base import (
    FetchContext,
    ReportTitles,
    UsageProvider,
    VerdictProfile,
)
from ai_cost_compare.providers.cursor import parse
from ai_cost_compare.providers.cursor import verdicts
from ai_cost_compare.providers.cursor.taxonomy import CURSOR_TAXONOMY


class CursorProvider:
    id = "cursor"
    display_name = "Cursor"

    def fetch(self, ctx: FetchContext) -> str:
        if ctx.file is None:
            raise CursorDataError(
                "Cursor usage requires --file PATH with a CSV from "
                "https://cursor.com/dashboard/usage"
            )
        return ctx.file.read_text(encoding="utf-8")

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
