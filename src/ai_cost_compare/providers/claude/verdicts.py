from ai_cost_compare.providers.base import VerdictEngine, VerdictProfile
from ai_cost_compare.providers.claude import config


class ClaudeVerdicts(VerdictEngine):
    def opus(self, now_p: int, was_p: int | None) -> tuple[str, str]:
        delta = self._delta_suffix(was_p, now_p)
        if now_p > config.OPUS_LEAK:
            return "red", f"❌  Routing leak — shift to Sonnet/Haiku{delta}"
        if now_p > config.OPUS_HIGH:
            return "yellow", f"⚠️  Still high — check routing rules{delta}"
        if now_p > config.OPUS_IMPROVING:
            return "yellow", f"⚡  Improving{delta}"
        return "green", f"✅  On target{delta}"

    def sonnet(self, now_p: int, was_p: int | None) -> tuple[str, str]:
        delta = self._delta_suffix(was_p, now_p)
        if now_p > config.SONNET_ACTIVE:
            return "green", f"✅  Routing active{delta}"
        if now_p > config.SONNET_GROWING:
            return "yellow", f"⚡  Growing{delta}"
        if now_p > 0:
            return "yellow", f"⚠️  Low — check 3-tier routing{delta}"
        return "grey70", "⚪  Unused"

    def haiku(self, now_p: int, was_p: int | None) -> tuple[str, str]:
        delta = self._delta_suffix(was_p, now_p)
        if now_p > config.HAIKU_HEAVY:
            return "green", f"✅  Heavy delegation{delta}"
        if now_p > config.HAIKU_DELEGATING:
            return "green", f"✅  Delegating{delta}"
        if now_p > 0:
            return "bright_cyan", f"⚡  Light{delta}"
        return "grey70", "⚪  Unused — use for lookups/reviews"

    def profile(self) -> VerdictProfile:
        return VerdictProfile(
            families=(
                ("opus", self.opus),
                ("sonnet", self.sonnet),
                ("haiku", self.haiku),
            ),
            legend_items=(
                ("Opus >80%", "bold red"),
                ("50–80%", "yellow"),
                ("<50%", "green"),
                ("Sonnet >30%", "bold green"),
                ("Cost >$50", "bold red"),
                (">$20", "yellow"),
            ),
        )
