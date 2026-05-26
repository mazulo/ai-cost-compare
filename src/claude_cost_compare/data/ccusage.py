import json
import os
import subprocess
from datetime import date
from pathlib import Path

from claude_cost_compare.errors import CcusageNotFoundError


def _nvm_ccusage_paths() -> list[Path]:
    nvm_root = Path.home() / ".nvm" / "versions" / "node"
    if not nvm_root.is_dir():
        return []
    bins = sorted(nvm_root.glob("*/bin/ccusage"), reverse=True)
    return [path for path in bins if os.access(path, os.X_OK)]


def find_ccusage() -> Path:
    for candidate in _nvm_ccusage_paths():
        return candidate
    from shutil import which

    found = which("ccusage")
    if found:
        return Path(found)
    raise CcusageNotFoundError(
        "ccusage not found. Install: npm install -g ccusage",
    )


def fetch_daily(since: date, until: date, *, ccusage_bin: Path | None = None) -> dict:
    binary = ccusage_bin or find_ccusage()
    since_str = since.strftime("%Y%m%d")
    until_str = until.strftime("%Y%m%d")
    result = subprocess.run(
        [str(binary), "daily", "-j", "-b", "--since", since_str, "--until", until_str],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 and not result.stdout.strip():
        stderr = result.stderr.strip() or f"ccusage exited with code {result.returncode}"
        raise CcusageNotFoundError(stderr)
    return json.loads(result.stdout)
