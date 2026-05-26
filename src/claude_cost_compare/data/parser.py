from collections import defaultdict
from datetime import date
from typing import Any

from claude_cost_compare.config import model_family
from claude_cost_compare.data.models import DailyRecord


def parse_daily_records(raw: dict[str, Any]) -> list[DailyRecord]:
    records: list[DailyRecord] = []
    for day in raw.get("daily", []):
        mix: dict[str, float] = defaultdict(float)
        for breakdown in day.get("modelBreakdowns", []):
            family = model_family(breakdown["modelName"])
            mix[family] += float(breakdown.get("cost", 0.0))
        day_date = day["date"]
        if not isinstance(day_date, date):
            day_date = date.fromisoformat(day_date)
        records.append(
            DailyRecord(
                date=day_date,
                cost=float(day.get("totalCost", 0.0)),
                tokens=int(day.get("totalTokens", 0)),
                mix=dict(mix),
            )
        )
    records.sort(key=lambda record: record.date)
    return records
