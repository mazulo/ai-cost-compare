#!/usr/bin/env python3
"""Print PyPI sdist url and sha256 for GitHub Actions (GITHUB_OUTPUT format)."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


def fetch_sdist(version: str) -> tuple[str, str]:
    url = f"https://pypi.org/pypi/claude-cost-compare/{version}/json"
    with urllib.request.urlopen(url, timeout=30) as response:
        data = json.load(response)
    for artifact in data["urls"]:
        if artifact["packagetype"] == "sdist":
            return artifact["url"], artifact["digests"]["sha256"]
    raise RuntimeError(f"No sdist found for claude-cost-compare {version}")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: fetch_pypi_sdist.py VERSION", file=sys.stderr)
        return 1

    version = sys.argv[1]
    try:
        sdist_url, sha256 = fetch_sdist(version)
    except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as exc:
        print(f"fetch failed: {exc}", file=sys.stderr)
        return 1

    output = os.environ.get("GITHUB_OUTPUT")
    lines = f"url={sdist_url}\nsha256={sha256}\n"
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(lines)
    else:
        print(lines, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
