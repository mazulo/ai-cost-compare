from dataclasses import dataclass


@dataclass(frozen=True)
class ShareVerdictSpec:
    """Share % verdict: check thresholds in order; first where now_p > bound wins."""

    thresholds: tuple[tuple[int, str, str], ...]  # (bound, style, message)
    default: tuple[str, str]  # (style, message) when no threshold matches
