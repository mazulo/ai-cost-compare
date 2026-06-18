from datetime import date

from ai_cost_compare.core import config as core_config
from ai_cost_compare.providers.claude.taxonomy import CLAUDE_TAXONOMY
from ai_cost_compare.render.formatters import (
    cost_style,
    era_label,
    era_style,
    fmt_cost,
    fmt_tokens,
    mix_bar,
    mix_bar_for_taxonomy,
    pct,
    pp_style,
    share_bar,
)


def test_fmt_cost_and_tokens():
    assert fmt_cost(12.5) == "$12.50"
    assert fmt_tokens(1_500_000) == "1.5M"
    assert fmt_tokens(12_000) == "12K"
    assert fmt_tokens(42) == "42"


def test_cost_style_thresholds():
    assert cost_style(core_config.COST_ALERT + 1) == "bold red"
    assert cost_style(core_config.COST_WARN + 1) == "yellow"
    assert cost_style(1.0) == "green"


def test_pp_style_directions():
    assert pp_style(-1, good_if_neg=True) == "bold green"
    assert pp_style(1, good_if_neg=False) == "bold green"
    assert pp_style(0, good_if_neg=True) == "grey62"


def test_era_labels():
    cutoff = date(2026, 5, 8)
    assert era_label(date(2026, 5, 7), cutoff) == "BEFORE"
    assert era_label(date(2026, 5, 8), cutoff) == "TODAY "
    assert era_label(date(2026, 5, 9), cutoff) == "AFTER "
    assert era_style("TODAY ") == "bold bright_cyan"


def test_mix_bar_empty_and_filled():
    empty = mix_bar([0, 0, 0], ["red", "green", "cyan"], width=10)
    assert "░" in str(empty)
    filled = mix_bar([50, 50, 0], ["red", "green", "cyan"], width=10)
    assert "█" in str(filled)


def test_mix_bar_for_taxonomy():
    bar = mix_bar_for_taxonomy(
        {"opus": 80.0, "sonnet": 20.0, "haiku": 0.0},
        100.0,
        CLAUDE_TAXONOMY,
        width=10,
    )
    assert "█" in str(bar)


def test_share_bar_minimum_fill():
    bar = share_bar(1, "red", width=10)
    assert "█" in str(bar)


def test_pct():
    assert pct(1, 3) == 33
