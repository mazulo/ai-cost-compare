from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from functools import partial
from pathlib import Path
from typing import Any, Protocol

from ai_cost_compare.core.models import DailyRecord
from ai_cost_compare.providers.verdict_spec import ShareVerdictSpec

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


class UsageFetcher(ABC):
    @abstractmethod
    def fetch(self, ctx: FetchContext) -> Any: ...


class UsageParser(ABC):
    @abstractmethod
    def parse(self, raw: Any) -> list[DailyRecord]: ...


class VerdictEngine:
    """Evaluate share-% verdicts from declarative specs per bucket."""

    bucket_order: tuple[str, ...] = ()
    specs: dict[str, ShareVerdictSpec] = {}
    legend_items: tuple[tuple[str, str], ...] = ()

    @staticmethod
    def _delta_suffix(was_p: int | None, now_p: int) -> str:
        if was_p is not None and was_p != now_p:
            return f"  (was {was_p}%)"
        return ""

    def evaluate(self, bucket: str, now_p: int, was_p: int | None) -> tuple[str, str]:
        spec = self.specs[bucket]
        delta = self._delta_suffix(was_p, now_p)
        for bound, style, message in spec.thresholds:
            if now_p > bound:
                return style, f"{message}{delta}"
        default_style, default_message = spec.default
        return default_style, f"{default_message}{delta}"

    def profile(self) -> VerdictProfile:
        return VerdictProfile(
            families=tuple(
                (bucket, partial(self.evaluate, bucket)) for bucket in self.bucket_order
            ),
            legend_items=self.legend_items,
        )


class UsageProvider(Protocol):
    id: str
    display_name: str

    def fetch(self, ctx: FetchContext) -> Any: ...
    def parse(self, raw: Any) -> list[DailyRecord]: ...
    def taxonomy(self) -> ModelTaxonomy: ...
    def verdict_profile(self) -> VerdictProfile: ...
    def titles(self) -> ReportTitles: ...
