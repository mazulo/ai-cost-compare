from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Protocol

from ai_cost_compare.core.models import DailyRecord

VerdictFn = Callable[[int, int | None], tuple[str, str]]


@dataclass(frozen=True)
class FetchContext:
    since: date
    until: date
    file: Path | None = None
    cursor_token: str | None = None
    ccusage_bin: Path | None = None


@dataclass(frozen=True)
class ModelTaxonomy:
    buckets: tuple[str, ...]
    labels: dict[str, str]
    bar_colors: dict[str, str]

    def classify(self, model_name: str) -> str:
        raise NotImplementedError

    def label(self, bucket: str) -> str:
        return self.labels.get(bucket, bucket.title())

    def share_style(self, bucket: str, share: int) -> str:
        raise NotImplementedError


@dataclass(frozen=True)
class VerdictProfile:
    families: tuple[tuple[str, VerdictFn], ...]
    legend_items: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class ReportTitles:
    daily: str
    signal: str = "REAL SIGNAL"


class UsageProvider(Protocol):
    id: str
    display_name: str

    def fetch(self, ctx: FetchContext) -> Any: ...
    def parse(self, raw: Any) -> list[DailyRecord]: ...
    def taxonomy(self) -> ModelTaxonomy: ...
    def verdict_profile(self) -> VerdictProfile: ...
    def titles(self) -> ReportTitles: ...
