import csv
import io
from collections import defaultdict
from collections.abc import Sequence
from datetime import date, datetime
from pathlib import Path

from ai_cost_compare.core.errors import CliError, CursorDataError
from ai_cost_compare.core.models import DailyRecord
from ai_cost_compare.providers.base import ModelTaxonomy, UsageParser
from ai_cost_compare.providers.cursor.taxonomy import CURSOR_TAXONOMY


class CursorParser(UsageParser):
    def __init__(self, taxonomy: ModelTaxonomy = CURSOR_TAXONOMY) -> None:
        self._taxonomy = taxonomy

    def parse(self, raw: str) -> list[DailyRecord]:
        return self.parse_csv(raw)

    def parse_csv(self, text: str) -> list[DailyRecord]:
        reader = csv.DictReader(io.StringIO(text))
        if not reader.fieldnames:
            raise CursorDataError("Cursor CSV is empty or missing a header row.")

        date_col = self._find_column(reader.fieldnames, ("date",))
        model_col = self._find_column(reader.fieldnames, ("model",))
        cost_col = self._find_column(reader.fieldnames, ("cost to you", "cost"))
        tokens_col = self._find_column(
            reader.fieldnames,
            ("total tokens", "tokens"),
            required=False,
        )

        by_date: dict[date, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        tokens_by_date: dict[date, int] = defaultdict(int)

        for row in reader:
            if not any(row.values()):
                continue
            day = self._parse_date(row[date_col])
            model = row[model_col].strip()
            bucket = self._taxonomy.classify(model)
            cost = self._parse_money(row[cost_col])
            by_date[day][bucket] += cost
            if tokens_col:
                tokens_by_date[day] += self._parse_int(row.get(tokens_col, "0"))

        records: list[DailyRecord] = []
        for day in sorted(by_date):
            mix = dict(by_date[day])
            records.append(
                DailyRecord(
                    date=day,
                    cost=sum(mix.values()),
                    tokens=tokens_by_date.get(day, 0),
                    mix=mix,
                )
            )
        return records

    def parse_file(self, path: Path) -> list[DailyRecord]:
        if not path.is_file():
            raise CursorDataError(f"File not found: {path}")
        return self.parse_csv(path.read_text(encoding="utf-8"))

    def _find_column(
        self,
        fieldnames: Sequence[str],
        candidates: tuple[str, ...],
        *,
        required: bool = True,
    ) -> str | None:
        normalized = {name.strip().lower(): name for name in fieldnames}
        for candidate in candidates:
            if candidate in normalized:
                return normalized[candidate]
        if required:
            raise CursorDataError(
                f"Cursor CSV missing expected column ({', '.join(candidates)}). "
                f"Found: {', '.join(fieldnames)}"
            )
        return None

    def _parse_date(self, raw: str) -> date:
        text = raw.strip()
        if not text:
            raise CliError("Cursor CSV row has an empty date.")
        if "T" in text:
            text = text.split("T", 1)[0]
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue
        return date.fromisoformat(text)

    def _parse_money(self, raw: str) -> float:
        text = raw.strip().replace("$", "").replace(",", "")
        if not text:
            return 0.0
        try:
            return float(text)
        except ValueError as exc:
            raise CursorDataError(f"Invalid cost value in CSV: {raw!r}") from exc

    @staticmethod
    def _parse_int(raw: str) -> int:
        text = raw.strip().replace(",", "")
        if not text:
            return 0
        try:
            return int(float(text))
        except ValueError:
            return 0
