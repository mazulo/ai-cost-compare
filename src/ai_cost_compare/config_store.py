"""User config (~/.config/ai-cost-compare/config.toml)."""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "ai-cost-compare" / "config.toml"


def config_path() -> Path:
    override = os.environ.get("AI_COST_COMPARE_CONFIG")
    if override:
        return Path(override).expanduser()
    return DEFAULT_CONFIG_PATH


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
