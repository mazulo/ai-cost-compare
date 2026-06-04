from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Protocol

from ai_cost_compare.core.models import DailyRecord


@dataclass(frozen=True)
class FetchContext:
    since: date
    until: date
    file: Path | None = None
    ccusage_bin: Path | None = None


class UsageProvider(Protocol):
    id: str
    display_name: str

    def fetch(self, ctx: FetchContext) -> Any: ...
    def parse(self, raw: Any) -> list[DailyRecord]: ...
