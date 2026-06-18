from datetime import date

from rich.console import Console
from rich.table import Table
from rich.text import Text

from ai_cost_compare.core.deltas import compare_windows, pct
from ai_cost_compare.core.models import DailyRecord, WindowStats
from ai_cost_compare.core.windows import window_stats
from ai_cost_compare.providers.base import ModelTaxonomy, UsageProvider
from ai_cost_compare.render.components import (
    base_table,
    era_cell,
    legend,
    print_table,
    section,
    styled_cost,
    styled_pct,
)
from ai_cost_compare.render.formatters import (
    era_label,
    fmt_tokens,
    mix_bar_for_taxonomy,
    pp_style,
    share_bar,
)
from ai_cost_compare.render.theme import INACTIVE, MUTED

MIX_WIDTH = 10
MIX_COL = MIX_WIDTH + 2
DATE_COL = 12
ERA_COL = 8
COST_COL = 11
TOKENS_COL = 8
BUCKET_COL = 8
WINDOW_COL = 24
DAYS_COL = 6
MODEL_COL = 9
SHARE_COL = 7
VERDICT_COL = 58

# Legacy aliases for export_demo column sizing
OPUS_COL = SONNET_COL = HAIKU_COL = BUCKET_COL


def render_report(
    console: Console,
    *,
    provider: UsageProvider,
    records: list[DailyRecord],
    cutoff: date,
    summary_mode: bool,
    before: WindowStats | None,
    after: WindowStats | None,
) -> None:
    taxonomy = provider.taxonomy()
    profile = provider.verdict_profile()
    titles = provider.titles()

    start = records[0].date if records else "—"
    end = cutoff
    section(console, titles.daily, f"{start} → {end}")

    if not records:
        console.print(f"[{MUTED}]No usage data for this window.[/]")
        return

    if summary_mode:
        _render_daily_summary(console, records, taxonomy)
        return

    _render_daily_with_eras(console, records, cutoff, taxonomy)
    _render_comparison(console, cutoff, before, after, taxonomy)
    _render_signal(console, cutoff, records, before, after, provider)
    legend(console, profile)


def _bucket_columns(taxonomy: ModelTaxonomy) -> list[tuple[str, dict]]:
    return [
        (taxonomy.label(bucket), {"justify": "right", "no_wrap": True, "width": BUCKET_COL})
        for bucket in taxonomy.buckets
    ]


def _daily_columns(*, with_era: bool, taxonomy: ModelTaxonomy) -> Table:
    columns: list[tuple[str, dict]] = [
        ("Date", {"style": "white", "no_wrap": True, "width": DATE_COL}),
    ]
    if with_era:
        columns.append(("Era", {"style": MUTED, "no_wrap": True, "width": ERA_COL}))
    columns.extend(
        [
            ("Cost", {"justify": "right", "no_wrap": True, "width": COST_COL}),
            ("Tokens", {"justify": "right", "style": MUTED, "no_wrap": True, "width": TOKENS_COL}),
            ("Mix", {"no_wrap": True, "width": MIX_COL}),
            *_bucket_columns(taxonomy),
        ]
    )
    return base_table(*columns)


def _bucket_cells(
    mix: dict[str, float],
    total: float,
    taxonomy: ModelTaxonomy,
) -> list[Text]:
    return [
        styled_pct(
            pct(mix.get(bucket, 0.0), total),
            taxonomy.share_style(bucket, pct(mix.get(bucket, 0.0), total)),
        )
        for bucket in taxonomy.buckets
    ]


def _add_daily_row(
    table: Table,
    record: DailyRecord,
    taxonomy: ModelTaxonomy,
    *,
    cutoff: date | None = None,
) -> None:
    row: list[Text | str] = [str(record.date)]
    if cutoff is not None:
        row.append(era_cell(record.date, cutoff))
    row.extend(
        [
            styled_cost(record.cost),
            Text(fmt_tokens(record.tokens), style=MUTED),
            mix_bar_for_taxonomy(record.mix, record.cost, taxonomy, width=MIX_WIDTH),
            *_bucket_cells(record.mix, record.cost, taxonomy),
        ]
    )
    table.add_row(*row)


def _render_daily_summary(
    console: Console,
    records: list[DailyRecord],
    taxonomy: ModelTaxonomy,
) -> None:
    table = _daily_columns(with_era=False, taxonomy=taxonomy)
    for record in records:
        _add_daily_row(table, record, taxonomy)
    print_table(console, table)


def _render_daily_with_eras(
    console: Console,
    records: list[DailyRecord],
    cutoff: date,
    taxonomy: ModelTaxonomy,
) -> None:
    table = _daily_columns(with_era=True, taxonomy=taxonomy)
    prev_era: str | None = None
    for record in records:
        era = era_label(record.date, cutoff)
        if prev_era and era != prev_era:
            table.add_section()
        prev_era = era
        _add_daily_row(table, record, taxonomy, cutoff=cutoff)
    print_table(console, table)


def _render_comparison(
    console: Console,
    cutoff: date,
    before: WindowStats | None,
    after: WindowStats | None,
    taxonomy: ModelTaxonomy,
) -> None:
    if not before and not after:
        return

    cutoff_str = cutoff.isoformat()
    section(console, "BEFORE vs AFTER", f"Split at {cutoff_str}")

    table = base_table(
        ("Window", {"style": "white", "no_wrap": True, "width": WINDOW_COL}),
        ("Days", {"justify": "right", "no_wrap": True, "width": DAYS_COL}),
        ("Avg/Day", {"justify": "right", "no_wrap": True, "width": COST_COL}),
        ("Total", {"justify": "right", "no_wrap": True, "width": COST_COL}),
        ("Mix", {"no_wrap": True, "width": MIX_COL}),
        *_bucket_columns(taxonomy),
    )

    ref_n = after.n if after else (before.n if before else 1)

    def add_window(label: str, stats: WindowStats | None, label_style: str) -> None:
        if not stats:
            table.add_row(
                Text(label, style=label_style),
                "—",
                "—",
                "—",
                "",
                *[Text("—", style=MUTED) for _ in taxonomy.buckets],
            )
            return
        normalized_total = stats.avg * ref_n
        table.add_row(
            Text(label, style=label_style),
            str(stats.n),
            styled_cost(stats.avg),
            Text(f"${normalized_total:,.2f}", style="white"),
            mix_bar_for_taxonomy(stats.mix, stats.total, taxonomy, width=MIX_WIDTH),
            *_bucket_cells(stats.mix, stats.total, taxonomy),
        )

    add_window(f"Before (<{cutoff_str})", before, INACTIVE)
    add_window(f"After (≥{cutoff_str})", after, "bold cyan")

    comparison = compare_windows(before, after, buckets=taxonomy.buckets)
    if comparison:
        table.add_section()
        delta_avg = comparison.delta_avg
        delta_cells = [
            Text(
                f"{'+' if comparison.delta_mix_pp.get(bucket, 0) >= 0 else ''}"
                f"{comparison.delta_mix_pp.get(bucket, 0)}pp",
                style=pp_style(
                    comparison.delta_mix_pp.get(bucket, 0),
                    good_if_neg=(bucket == taxonomy.buckets[0]),
                ),
            )
            for bucket in taxonomy.buckets
        ]
        table.add_row(
            Text("Δ Change", style="bold"),
            "",
            Text(f"${delta_avg:+.2f}/d", style="bold green" if delta_avg < 0 else "bold red"),
            "",
            "",
            *delta_cells,
        )

    print_table(console, table)


def _render_signal(
    console: Console,
    cutoff: date,
    records: list[DailyRecord],
    before: WindowStats | None,
    after: WindowStats | None,
    provider: UsageProvider,
) -> None:
    taxonomy = provider.taxonomy()
    profile = provider.verdict_profile()
    titles = provider.titles()

    signal = after or (window_stats([records[-1]]) if records else None)
    if not signal:
        return

    cutoff_str = cutoff.isoformat()
    if after:
        days_label = "day" if signal.n == 1 else "days"
        subtitle = f"Post-{cutoff_str} · {signal.n} {days_label}"
    else:
        subtitle = f"Latest day only — no post-{cutoff_str} data yet"

    section(console, titles.signal, subtitle)

    table = base_table(
        ("Model", {"style": "white", "no_wrap": True, "width": MODEL_COL}),
        ("Avg/Day", {"justify": "right", "no_wrap": True, "width": COST_COL}),
        ("Total", {"justify": "right", "no_wrap": True, "width": COST_COL}),
        ("Share", {"justify": "right", "no_wrap": True, "width": SHARE_COL}),
        ("Mix", {"no_wrap": True, "width": MIX_COL}),
        ("Verdict", {"width": VERDICT_COL, "no_wrap": True}),
    )

    mix = signal.mix
    total = signal.total

    for bucket, verdict_fn in profile.families:
        baseline_share = pct(before.mix.get(bucket, 0.0), before.total) if before else None
        family_cost = mix.get(bucket, 0.0)
        if family_cost == 0 and (baseline_share or 0) == 0:
            continue
        share = pct(family_cost, total)
        verdict_style, verdict_text = verdict_fn(share, baseline_share)
        bar_color = taxonomy.bar_colors.get(bucket, "white")
        table.add_row(
            Text(taxonomy.label(bucket), style=taxonomy.share_style(bucket, share)),
            styled_cost(family_cost / signal.n),
            Text(f"${family_cost:,.2f}", style="white"),
            styled_pct(share, taxonomy.share_style(bucket, share)),
            share_bar(share, bar_color, width=MIX_WIDTH),
            Text(verdict_text, style=verdict_style),
        )

    table.add_section()
    table.add_row(
        Text("Total", style="bold"),
        styled_cost(signal.avg),
        Text(f"${signal.total:,.2f}", style="bold white"),
        Text("100%", style="bold"),
        mix_bar_for_taxonomy(mix, total, taxonomy, width=MIX_WIDTH),
        "",
    )
    print_table(console, table)
