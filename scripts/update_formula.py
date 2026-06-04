#!/usr/bin/env python3
"""Update the Homebrew formula's PyPI sdist url and sha256."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

FORMULA_PATH = Path("Formula/ai-cost-compare.rb")
ARTIFACT_PATTERN = re.compile(
    r'(  url ")[^"]+("\n  sha256 ")[a-f0-9]{64}(")',
    re.MULTILINE,
)


def update_formula(*, url: str, sha256: str, path: Path = FORMULA_PATH) -> bool:
    text = path.read_text(encoding="utf-8")
    updated, count = ARTIFACT_PATTERN.subn(rf"\g<1>{url}\g<2>{sha256}\g<3>", text, count=1)
    if count != 1:
        raise RuntimeError(f"Expected one url/sha256 pair in {path}, updated {count}")
    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="PyPI sdist URL")
    parser.add_argument("--sha256", required=True, help="PyPI sdist sha256")
    parser.add_argument("--formula", type=Path, default=FORMULA_PATH)
    args = parser.parse_args()

    changed = update_formula(url=args.url, sha256=args.sha256, path=args.formula)
    print("updated" if changed else "unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
