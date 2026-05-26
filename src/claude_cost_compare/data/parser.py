from collections import defaultdict
from datetime import date
from typing import Any

from claude_cost_compare.config import model_family
from claude_cost_compare.data.models import DailyRecord
from claude_cost_compare.errors import CliError


def parse_daily_records(raw: dict[str, Any]) -> list[DailyRecord]:
    records_by_date: dict[date, DailyRecord] = {}
    for day in raw.get("daily", []):
        day_date = _parse_day_date(day)
        mix = _day_model_mix(day)
        record = DailyRecord(
            date=day_date,
            cost=float(day.get("totalCost", 0.0)),
            tokens=int(day.get("totalTokens", 0)),
            mix=mix,
        )
        if existing := records_by_date.get(day_date):
            records_by_date[day_date] = DailyRecord(
                date=day_date,
                cost=existing.cost + record.cost,
                tokens=existing.tokens + record.tokens,
                mix=_merge_mix(existing.mix, record.mix),
            )
        else:
            records_by_date[day_date] = record
    return sorted(records_by_date.values(), key=lambda record: record.date)


def _parse_day_date(day: dict[str, Any]) -> date:
    raw = day.get("date", day.get("period"))
    if raw is None:
        raise CliError(
            "Unrecognized ccusage daily JSON: expected 'date' or 'period' on each daily row. "
            "Use `ccusage daily --json` and ccusage >=18 with claude-cost-compare."
        )
    if isinstance(raw, date):
        return raw
    text = str(raw)
    if "T" in text:
        text = text.split("T", 1)[0]
    return date.fromisoformat(text)


def _day_model_mix(day: dict[str, Any]) -> dict[str, float]:
    mix: dict[str, float] = defaultdict(float)
    for breakdown in day.get("modelBreakdowns", []):
        family = model_family(breakdown["modelName"])
        mix[family] += float(breakdown.get("cost", 0.0))
    return dict(mix)


def _merge_mix(left: dict[str, float], right: dict[str, float]) -> dict[str, float]:
    merged: dict[str, float] = defaultdict(float, left)
    for family, cost in right.items():
        merged[family] += cost
    return dict(merged)
