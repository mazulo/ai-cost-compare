from datetime import date

from rich.console import Console
from rich.table import Table
from rich.text import Text

from ai_cost_compare.core.deltas import compare_windows
from ai_cost_compare.core.models import DailyRecord, WindowStats
from ai_cost_compare.core.windows import window_stats
from ai_cost_compare.providers.claude.verdicts import verdict_haiku, verdict_opus, verdict_sonnet
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
    mix_bar,
    model_name_style,
    opus_share_style,
    pct,
    pp_style,
    share_bar,
    sonnet_share_style,
)
from ai_cost_compare.render.theme import INACTIVE, MUTED, ZERO

MIX_WIDTH = 10
MIX_COL = MIX_WIDTH + 2
DATE_COL = 12
ERA_COL = 8
COST_COL = 11
TOKENS_COL = 8
OPUS_COL = 6
SONNET_COL = 8
HAIKU_COL = 7
WINDOW_COL = 24
DAYS_COL = 6
MODEL_COL = 9
SHARE_COL = 7
VERDICT_COL = 58


def render_report(
    console: Console,
    *,
    records: list[DailyRecord],
    cutoff: date,
    summary_mode: bool,
    before: WindowStats | None,
    after: WindowStats | None,
) -> None:
    start = records[0].date if records else "—"
    end = date.today()
    section(console, "CLAUDE DAILY COST", f"{start} → {end}")

    if not records:
        console.print(f"[{MUTED}]No usage data for this window.[/]")
        return

    if summary_mode:
        _render_daily_summary(console, records)
        return

    _render_daily_with_eras(console, records, cutoff)
    _render_comparison(console, cutoff, before, after)
    _render_signal(console, cutoff, records, before, after)
    legend(console)


def _daily_columns(*, with_era: bool) -> Table:
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
            ("Opus", {"justify": "right", "no_wrap": True, "width": OPUS_COL}),
            ("Sonnet", {"justify": "right", "no_wrap": True, "width": SONNET_COL}),
            ("Haiku", {"justify": "right", "no_wrap": True, "width": HAIKU_COL}),
        ]
    )
    return base_table(*columns)


def _add_daily_row(
    table: Table,
    record: DailyRecord,
    *,
    cutoff: date | None = None,
) -> None:
    mix = record.mix
    op = pct(mix.get("opus", 0.0), record.cost)
    so = pct(mix.get("sonnet", 0.0), record.cost)
    ha = pct(mix.get("haiku", 0.0), record.cost)

    row: list[object] = [str(record.date)]
    if cutoff is not None:
        row.append(era_cell(record.date, cutoff))
    row.extend(
        [
            styled_cost(record.cost),
            Text(fmt_tokens(record.tokens), style=MUTED),
            mix_bar(op, so, ha, width=MIX_WIDTH),
            styled_pct(op, opus_share_style(op)),
            styled_pct(so, sonnet_share_style(so)),
            styled_pct(ha, "bright_cyan" if ha else ZERO),
        ]
    )
    table.add_row(*row)


def _render_daily_summary(console: Console, records: list[DailyRecord]) -> None:
    table = _daily_columns(with_era=False)
    for record in records:
        _add_daily_row(table, record)
    print_table(console, table)


def _render_daily_with_eras(
    console: Console,
    records: list[DailyRecord],
    cutoff: date,
) -> None:
    table = _daily_columns(with_era=True)
    prev_era: str | None = None
    for record in records:
        era = era_label(record.date, cutoff)
        if prev_era and era != prev_era:
            table.add_section()
        prev_era = era
        _add_daily_row(table, record, cutoff=cutoff)
    print_table(console, table)


def _render_comparison(
    console: Console,
    cutoff: date,
    before: WindowStats | None,
    after: WindowStats | None,
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
        ("Opus", {"justify": "right", "no_wrap": True, "width": OPUS_COL}),
        ("Sonnet", {"justify": "right", "no_wrap": True, "width": SONNET_COL}),
        ("Haiku", {"justify": "right", "no_wrap": True, "width": HAIKU_COL}),
    )

    def add_window(label: str, stats: WindowStats | None, label_style: str) -> None:
        if not stats:
            table.add_row(
                Text(label, style=label_style),
                "—",
                "—",
                "—",
                "",
                "—",
                "—",
                "—",
            )
            return
        mix = stats.mix
        op = pct(mix.get("opus", 0.0), stats.total)
        so = pct(mix.get("sonnet", 0.0), stats.total)
        ha = pct(mix.get("haiku", 0.0), stats.total)
        table.add_row(
            Text(label, style=label_style),
            str(stats.n),
            styled_cost(stats.avg),
            Text(f"${stats.total:,.2f}", style="white"),
            mix_bar(op, so, ha, width=MIX_WIDTH),
            styled_pct(op, opus_share_style(op)),
            styled_pct(so, sonnet_share_style(so)),
            styled_pct(ha, "bright_cyan" if ha else ZERO),
        )

    add_window(f"Before (<{cutoff_str})", before, INACTIVE)
    add_window(f"After (≥{cutoff_str})", after, "bold cyan")

    comparison = compare_windows(before, after)
    if comparison:
        table.add_section()
        delta_avg = comparison.delta_avg
        table.add_row(
            Text("Δ Change", style="bold"),
            "",
            Text(f"${delta_avg:+.2f}/d", style="bold green" if delta_avg < 0 else "bold red"),
            "",
            "",
            Text(
                f"{'+' if comparison.delta_opus_pp >= 0 else ''}{comparison.delta_opus_pp}pp",
                style=pp_style(comparison.delta_opus_pp, good_if_neg=True),
            ),
            Text(
                f"{'+' if comparison.delta_sonnet_pp >= 0 else ''}{comparison.delta_sonnet_pp}pp",
                style=pp_style(comparison.delta_sonnet_pp, good_if_neg=False),
            ),
            Text(
                f"{'+' if comparison.delta_haiku_pp >= 0 else ''}{comparison.delta_haiku_pp}pp",
                style=pp_style(comparison.delta_haiku_pp, good_if_neg=False),
            ),
        )

    print_table(console, table)


def _render_signal(
    console: Console,
    cutoff: date,
    records: list[DailyRecord],
    before: WindowStats | None,
    after: WindowStats | None,
) -> None:
    signal = after or (window_stats([records[-1]]) if records else None)
    if not signal:
        return

    cutoff_str = cutoff.isoformat()
    if after:
        days_label = "day" if signal.n == 1 else "days"
        subtitle = f"Post-{cutoff_str} · {signal.n} {days_label}"
    else:
        subtitle = f"Latest day only — no post-{cutoff_str} data yet"

    section(console, "REAL SIGNAL", subtitle)

    table = base_table(
        ("Model", {"style": "white", "no_wrap": True, "width": MODEL_COL}),
        ("Avg/Day", {"justify": "right", "no_wrap": True, "width": COST_COL}),
        ("Total", {"justify": "right", "no_wrap": True, "width": COST_COL}),
        ("Share", {"justify": "right", "no_wrap": True, "width": SHARE_COL}),
        ("Mix", {"no_wrap": True, "width": MIX_COL}),
        ("Verdict", {"width": VERDICT_COL, "no_wrap": True}),
    )

    b_op = pct(before.mix.get("opus", 0.0), before.total) if before else None
    b_so = pct(before.mix.get("sonnet", 0.0), before.total) if before else None
    b_ha = pct(before.mix.get("haiku", 0.0), before.total) if before else None

    families = [
        ("opus", verdict_opus, b_op),
        ("sonnet", verdict_sonnet, b_so),
        ("haiku", verdict_haiku, b_ha),
    ]

    mix = signal.mix
    total = signal.total
    for family, verdict_fn, baseline_share in families:
        family_cost = mix.get(family, 0.0)
        if family_cost == 0 and (baseline_share or 0) == 0:
            continue
        share = pct(family_cost, total)
        verdict_style, verdict_text = verdict_fn(share, baseline_share)
        bar_color = {"opus": "red", "sonnet": "green", "haiku": "cyan"}[family]
        table.add_row(
            Text(family.title(), style=model_name_style(family, share)),
            styled_cost(family_cost / signal.n),
            Text(f"${family_cost:,.2f}", style="white"),
            styled_pct(share, model_name_style(family, share)),
            share_bar(share, bar_color, width=MIX_WIDTH),
            Text(verdict_text, style=verdict_style),
        )

    table.add_section()
    table.add_row(
        Text("Total", style="bold"),
        styled_cost(signal.avg),
        Text(f"${signal.total:,.2f}", style="bold white"),
        Text("100%", style="bold"),
        mix_bar(
            pct(mix.get("opus", 0.0), total),
            pct(mix.get("sonnet", 0.0), total),
            pct(mix.get("haiku", 0.0), total),
            width=MIX_WIDTH,
        ),
        "",
    )
    print_table(console, table)
