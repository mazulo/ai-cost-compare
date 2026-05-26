from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DailyRecord:
    date: date
    cost: float
    tokens: int
    mix: dict[str, float]


@dataclass
class WindowStats:
    n: int
    total: float
    avg: float
    mix: dict[str, float]


@dataclass
class ComparisonResult:
    before: WindowStats | None
    after: WindowStats | None
    delta_avg: float
    delta_opus_pp: int
    delta_sonnet_pp: int
    delta_haiku_pp: int
