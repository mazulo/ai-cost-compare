from ai_cost_compare.providers.base import VerdictEngine, VerdictProfile
from ai_cost_compare.providers.cursor import config


class CursorVerdicts(VerdictEngine):
    def premium(self, now_p: int, was_p: int | None) -> tuple[str, str]:
        delta = self._delta_suffix(was_p, now_p)
        if now_p > config.PREMIUM_SHARE_HIGH:
            return "red", f"❌  Premium-heavy — try Fast tier models{delta}"
        if now_p > config.PREMIUM_SHARE_WARN:
            return "yellow", f"⚠️  Premium share elevated{delta}"
        return "green", f"✅  Premium share OK{delta}"

    def fast(self, now_p: int, was_p: int | None) -> tuple[str, str]:
        delta = self._delta_suffix(was_p, now_p)
        if now_p > config.FAST_SHARE_GOOD:
            return "green", f"✅  Good Fast-tier usage{delta}"
        if now_p > 0:
            return "yellow", f"⚡  Some Fast usage{delta}"
        return "grey70", f"⚪  No Fast-tier usage{delta}"

    def profile(self) -> VerdictProfile:
        return VerdictProfile(
            families=(
                ("premium", self.premium),
                ("fast", self.fast),
            ),
            legend_items=(
                ("Premium >70%", "bold red"),
                ("50–70%", "yellow"),
                ("Fast >20%", "bold green"),
                ("Cost >$50", "bold red"),
                (">$20", "yellow"),
            ),
        )
