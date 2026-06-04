from ai_cost_compare.providers.cursor import config


def _delta_suffix(was_p: int | None, now_p: int) -> str:
    if was_p is not None and was_p != now_p:
        return f"  (was {was_p}%)"
    return ""


def verdict_premium(now_p: int, was_p: int | None) -> tuple[str, str]:
    delta = _delta_suffix(was_p, now_p)
    if now_p > config.PREMIUM_SHARE_HIGH:
        return "red", f"❌  Premium-heavy — try Fast tier models{delta}"
    if now_p > config.PREMIUM_SHARE_WARN:
        return "yellow", f"⚠️  Premium share elevated{delta}"
    return "green", f"✅  Premium share OK{delta}"


def verdict_fast(now_p: int, was_p: int | None) -> tuple[str, str]:
    delta = _delta_suffix(was_p, now_p)
    if now_p > config.FAST_SHARE_GOOD:
        return "green", f"✅  Good Fast-tier usage{delta}"
    if now_p > 0:
        return "yellow", f"⚡  Some Fast usage{delta}"
    return "grey70", f"⚪  No Fast-tier usage{delta}"
