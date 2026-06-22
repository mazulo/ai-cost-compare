import os
from pathlib import Path

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "ai-cost-compare" / "config.toml"

_CONFIG_TEMPLATE = """\
# ai-cost-compare configuration
# https://github.com/mazulo/ai-cost-compare

[cursor]
# WorkosCursorSessionToken — required for automatic Cursor usage fetch.
#
# How to get it:
#   1. Open https://cursor.com/settings (or any cursor.com page while logged in)
#   2. Open browser DevTools  →  Application tab  →  Cookies  →  cursor.com
#   3. Find the cookie named  WorkosCursorSessionToken
#   4. Copy its Value and paste it below (keep the quotes)
#
# Alternatively, export a CSV from https://cursor.com/dashboard/usage and pass
# it with:  ai-cost-compare cursor --file ~/Downloads/usage.csv
#
# session_token = "paste-your-token-here"
"""


def config_path() -> Path:
    override = os.environ.get("AI_COST_COMPARE_CONFIG")
    if override:
        return Path(override).expanduser()
    return DEFAULT_CONFIG_PATH


def ensure_config(path: Path | None = None) -> bool:
    """Create config file with template if it doesn't exist. Returns True if created."""
    cfg = path or config_path()
    if cfg.exists():
        return False
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text(_CONFIG_TEMPLATE, encoding="utf-8")
    return True


def load_cursor_token(path: Path | None = None) -> str | None:
    cfg = path or config_path()
    if not cfg.is_file():
        return None
    try:
        import tomllib
    except ImportError:
        return _load_cursor_token_ini(cfg)

    data = tomllib.loads(cfg.read_text(encoding="utf-8"))
    cursor = data.get("cursor", {})
    token = cursor.get("session_token")
    return str(token).strip() if token else None


def _load_cursor_token_ini(path: Path) -> str | None:
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("session_token") and "=" in stripped:
            return stripped.split("=", 1)[1].strip().strip('"').strip("'")
    return None
