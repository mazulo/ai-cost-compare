from rich.text import Text

from ai_cost_compare.core import config
from ai_cost_compare.providers.base import ModelTaxonomy
from ai_cost_compare.render.theme import BAR_EMPTY, ERA_AFTER, ERA_BEFORE, ERA_TODAY, FAINT


def pct(value: float, total: float) -> int:
    return round(value / total * 100) if total else 0


def fmt_cost(amount: float) -> str:
    return f"${amount:,.2f}"


def fmt_tokens(tokens: int) -> str:
    if tokens >= 1_000_000:
        return f"{tokens / 1_000_000:.1f}M"
    if tokens >= 1_000:
        return f"{tokens / 1_000:.0f}K"
    return str(tokens)


def cost_style(amount: float) -> str:
    if amount > config.COST_ALERT:
        return "bold red"
    if amount > config.COST_WARN:
        return "yellow"
    return "green"


def pp_style(value: int, *, good_if_neg: bool) -> str:
    if good_if_neg:
        if value < 0:
            return "bold green"
        if value > 0:
            return "bold red"
        return FAINT
    if value > 0:
        return "bold green"
    if value == 0:
        return FAINT
    return "red"


def era_label(record_date, cutoff) -> str:
    if record_date < cutoff:
        return "BEFORE"
    if record_date == cutoff:
        return "TODAY "
    return "AFTER "


def era_style(era: str) -> str:
    if era == "TODAY ":
        return ERA_TODAY
    if era == "AFTER ":
        return ERA_AFTER
    return ERA_BEFORE


def mix_bar(shares: list[int], colors: list[str], width: int = 14) -> Text:
    total = sum(shares)
    if total == 0:
        return Text("░" * width, style=BAR_EMPTY)

    blocks = [round(share / total * width) for share in shares]
    drift = width - sum(blocks)
    if drift:
        largest = max(range(len(shares)), key=lambda index: shares[index])
        blocks[largest] += drift

    bar = Text()
    for count, color in zip(blocks, colors, strict=True):
        if count > 0:
            bar.append("█" * count, style=color)
    return bar


def mix_bar_for_taxonomy(
    mix: dict[str, float],
    total: float,
    taxonomy: ModelTaxonomy,
    *,
    width: int = 14,
) -> Text:
    shares = [pct(mix.get(bucket, 0.0), total) for bucket in taxonomy.buckets]
    colors = [taxonomy.bar_colors.get(bucket, "white") for bucket in taxonomy.buckets]
    return mix_bar(shares, colors, width=width)


def share_bar(share: int, color: str, width: int = 14) -> Text:
    filled = round(share / 100 * width)
    if share > 0 and filled == 0:
        filled = 1
    bar = Text()
    if filled:
        bar.append("█" * filled, style=color)
    if filled < width:
        bar.append("░" * (width - filled), style=BAR_EMPTY)
    return bar
