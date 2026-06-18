from typing import Any

from ai_cost_compare.providers.base import FetchContext, ReportTitles, UsageProvider
from ai_cost_compare.providers.cursor.fetch import CursorFetcher
from ai_cost_compare.providers.cursor.parse import CursorParser
from ai_cost_compare.providers.cursor.taxonomy import CURSOR_TAXONOMY
from ai_cost_compare.providers.cursor.verdicts import CursorVerdicts


class CursorProvider:
    id = "cursor"
    display_name = "Cursor"

    def __init__(self) -> None:
        self.fetcher = CursorFetcher()
        self.parser = CursorParser()
        self.verdicts = CursorVerdicts()
        self._taxonomy = CURSOR_TAXONOMY

    def fetch(self, ctx: FetchContext) -> str:
        return self.fetcher.fetch(ctx)

    def parse(self, raw: Any) -> list:
        return self.parser.parse(raw)

    def taxonomy(self):
        return self._taxonomy

    def verdict_profile(self):
        return self.verdicts.profile()

    def titles(self) -> ReportTitles:
        return ReportTitles(daily="CURSOR DAILY COST", signal="USAGE SIGNAL")


provider: UsageProvider = CursorProvider()
