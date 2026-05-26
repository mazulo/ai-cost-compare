#!/usr/bin/env python3
"""Export a Rich terminal demo SVG for the README."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from rich.console import Console

from claude_cost_compare.analysis.windows import split_records, window_stats
from claude_cost_compare.data.parser import parse_daily_records
from claude_cost_compare.render.report import render_report

FIXTURE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "sample_daily.json"
OUTPUT = Path(__file__).resolve().parents[1] / "docs" / "assets" / "demo.svg"


def export_demo(*, output: Path = OUTPUT, width: int = 100) -> Path:
    records = parse_daily_records(json.loads(FIXTURE.read_text(encoding="utf-8")))
    cutoff = date(2026, 5, 8)
    before, after = split_records(records, cutoff)

    console = Console(record=True, width=width, color_system="truecolor")
    render_report(
        console,
        records=records,
        cutoff=cutoff,
        summary_mode=False,
        before=window_stats(before),
        after=window_stats(after),
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(console.export_svg(title="claude-cost-compare"), encoding="utf-8")
    return output


if __name__ == "__main__":
    path = export_demo()
    print(path)
