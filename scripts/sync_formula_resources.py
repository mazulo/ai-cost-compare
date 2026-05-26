#!/usr/bin/env python3
"""Sync Homebrew formula Python resource blocks from PyPI dependencies."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

FORMULA_PATH = Path("Formula/claude-cost-compare.rb")
RESOURCE_BLOCK = re.compile(
    r'\n  resource "[^"]+" do\n(?:    .+\n)+?  end',
    re.MULTILINE,
)
INSTALL_MARKER = re.compile(r"\n  def install\n", re.MULTILINE)
SDIST_NAME = re.compile(r"^(.+)-(.+)\.tar\.gz$")


def pypi_sdist(name: str, version: str) -> tuple[str, str]:
    url = f"https://pypi.org/pypi/{name}/{version}/json"
    with urllib.request.urlopen(url, timeout=30) as response:
        data = json.load(response)
    for artifact in data["urls"]:
        if artifact["packagetype"] == "sdist":
            return artifact["url"], artifact["digests"]["sha256"]
    raise RuntimeError(f"No sdist on PyPI for {name}=={version}")


def pip_resource_name(filename: str) -> tuple[str, str]:
    match = SDIST_NAME.match(filename)
    if not match:
        raise RuntimeError(f"Unexpected sdist filename: {filename}")
    distribution, version = match.group(1), match.group(2)
    pypi_name = distribution.replace("_", "-").lower()
    return pypi_name, version


def python_with_pip() -> str:
    """Return a Python interpreter that can run `python -m pip`.

    uv project venvs often omit pip; GitHub Actions runners provide system python3.
    """
    candidates: list[str | None] = [
        os.environ.get("SYNC_FORMULA_PYTHON"),
        shutil.which("python3"),
        "/usr/bin/python3",
    ]
    if Path(sys.executable).name != "python":
        candidates.append(sys.executable)

    seen: set[str] = set()
    for candidate in candidates:
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        proc = subprocess.run(
            [candidate, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0:
            return candidate
    raise RuntimeError("No Python interpreter with pip found")


def collect_dependencies(*, package: str, version: str) -> dict[str, tuple[str, str]]:
    pip_python = python_with_pip()
    with tempfile.TemporaryDirectory() as tmp:
        proc = subprocess.run(
            [
                pip_python,
                "-m",
                "pip",
                "download",
                f"{package}=={version}",
                "--dest",
                tmp,
                "--no-binary",
                ":all:",
            ],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            message = proc.stderr.strip() or proc.stdout.strip() or "unknown pip error"
            raise RuntimeError(f"pip download failed using {pip_python}: {message}")
        resources: dict[str, tuple[str, str]] = {}
        for path in sorted(Path(tmp).glob("*.tar.gz")):
            pypi_name, dep_version = pip_resource_name(path.name)
            if pypi_name == package:
                continue
            url, sha256 = pypi_sdist(pypi_name, dep_version)
            resources[pypi_name] = (url, sha256)
        return resources


def render_resources(resources: dict[str, tuple[str, str]]) -> str:
    blocks: list[str] = []
    for name in sorted(resources):
        url, sha256 = resources[name]
        blocks.append(
            f'  resource "{name}" do\n'
            f'    url "{url}"\n'
            f'    sha256 "{sha256}"\n'
            f"  end"
        )
    return "\n\n".join(blocks)


def sync_formula_resources(
    *,
    package: str,
    version: str,
    path: Path = FORMULA_PATH,
) -> bool:
    resources = collect_dependencies(package=package, version=version)
    text = path.read_text(encoding="utf-8")

    install_match = INSTALL_MARKER.search(text)
    if not install_match:
        raise RuntimeError(f"Could not find 'def install' in {path}")

    prefix = text[: install_match.start()]
    suffix = text[install_match.start() :]

    prefix = RESOURCE_BLOCK.sub("", prefix).rstrip() + "\n\n"
    updated = prefix + render_resources(resources) + suffix
    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", default="claude-cost-compare")
    parser.add_argument("--version", required=True)
    parser.add_argument("--formula", type=Path, default=FORMULA_PATH)
    args = parser.parse_args()

    changed = sync_formula_resources(
        package=args.package.replace("_", "-"),
        version=args.version,
        path=args.formula,
    )
    print("updated" if changed else "unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
