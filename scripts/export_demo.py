#!/usr/bin/env python3
"""Export demo SVG/PNG assets for README and social posts."""

from __future__ import annotations

import base64
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

from rich.console import Console

from ai_cost_compare.core.windows import split_records, window_stats
from ai_cost_compare.providers.claude.parse import parse_daily_records
from ai_cost_compare.render.report import (
    COST_COL,
    DATE_COL,
    DAYS_COL,
    ERA_COL,
    HAIKU_COL,
    MIX_COL,
    MODEL_COL,
    OPUS_COL,
    SHARE_COL,
    SONNET_COL,
    TOKENS_COL,
    VERDICT_COL,
    WINDOW_COL,
    render_report,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "sample_daily.json"
ASSETS = ROOT / "docs" / "assets"
FONT_DIR = Path(__file__).resolve().parent / "assets"
SVG_OUTPUT = ASSETS / "demo.svg"
PNG_OUTPUT = ASSETS / "demo.png"
SOCIAL_OUTPUT = ROOT / "plans" / "demo.png"

DAILY_WIDTH = (
    DATE_COL + ERA_COL + COST_COL + TOKENS_COL + MIX_COL + OPUS_COL + SONNET_COL + HAIKU_COL
)
COMPARISON_WIDTH = (
    WINDOW_COL + DAYS_COL + COST_COL + COST_COL + MIX_COL + OPUS_COL + SONNET_COL + HAIKU_COL
)
SIGNAL_WIDTH = MODEL_COL + COST_COL + COST_COL + SHARE_COL + MIX_COL + VERDICT_COL
DEFAULT_WIDTH = max(DAILY_WIDTH, COMPARISON_WIDTH, SIGNAL_WIDTH) + 16

_FONT_FACE_RE = re.compile(
    r'@font-face \{\s*font-family: "Fira Code";\s*src: local\("[^"]+"\),'
    r'[\s\S]*?font-weight: (\d+);\s*\}'
)
_VIEWBOX_RE = re.compile(r'viewBox="0 0 ([\d.]+) ([\d.]+)"')
_CHROME_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
)


def export_demo(
    *,
    svg_output: Path = SVG_OUTPUT,
    png_output: Path | None = PNG_OUTPUT,
    social_png_output: Path | None = SOCIAL_OUTPUT,
    width: int = DEFAULT_WIDTH,
    png_width: int = 1400,
) -> Path:
    records = parse_daily_records(json.loads(FIXTURE.read_text(encoding="utf-8")))
    cutoff = date(2026, 5, 8)
    before, after = split_records(records, cutoff)

    console = Console(
        record=True,
        width=width,
        height=40,
        color_system="truecolor",
        _environ={"COLUMNS": str(width), "LINES": "40"},
    )
    from ai_cost_compare.providers.registry import get

    render_report(
        console,
        provider=get("claude"),
        records=records,
        cutoff=cutoff,
        summary_mode=False,
        before=window_stats(before),
        after=window_stats(after),
    )

    svg_output.parent.mkdir(parents=True, exist_ok=True)
    svg = _prepare_svg_for_raster(console.export_svg(title="ai-cost-compare"))
    svg_output.write_text(svg, encoding="utf-8")

    for png_path in (png_output, social_png_output):
        if png_path is None:
            continue
        png_path.parent.mkdir(parents=True, exist_ok=True)
        _svg_to_png(svg_output, png_path, width=png_width)

    return svg_output


def _prepare_svg_for_raster(svg: str) -> str:
    """Embed fonts so rsvg/librsvg matches browser metrics for textLength borders."""
    svg = _embed_fonts(svg)
    return svg.replace("font-variant-east-asian: full-width;", "")


def _embed_fonts(svg: str) -> str:
    regular = (FONT_DIR / "FiraCode-Regular.woff2").read_bytes()
    bold = (FONT_DIR / "FiraCode-Bold.woff2").read_bytes()
    faces = {
        "400": base64.b64encode(regular).decode(),
        "700": base64.b64encode(bold).decode(),
    }

    def replace_face(match: re.Match[str]) -> str:
        weight = match.group(1)
        data = faces[weight]
        style = "normal" if weight == "400" else "bold"
        return (
            '@font-face {\n'
            '        font-family: "Fira Code";\n'
            f'        src: url("data:font/woff2;base64,{data}") format("woff2");\n'
            f'        font-style: {style};\n'
            f'        font-weight: {weight};\n'
            "    }"
        )

    return _FONT_FACE_RE.sub(replace_face, svg)


def _svg_to_png(svg_path: Path, png_path: Path, *, width: int) -> None:
    if chrome := _find_chrome():
        _svg_to_png_chrome(chrome, svg_path, png_path, width=width)
        return

    print(
        "warning: Chrome/Chromium not found; PNG may misalign Rich table borders. "
        "Install Chrome or run on macOS for best results.",
        file=sys.stderr,
    )
    rsvg = _find_rsvg_convert()
    subprocess.run(
        [rsvg, "-w", str(width), str(svg_path), "-o", str(png_path)],
        check=True,
    )


def _parse_viewbox(svg: str) -> tuple[float, float]:
    match = _VIEWBOX_RE.search(svg)
    if not match:
        raise ValueError("SVG is missing a viewBox attribute")
    return float(match.group(1)), float(match.group(2))


def _svg_to_png_chrome(chrome: str, svg_path: Path, png_path: Path, *, width: int) -> None:
    svg = svg_path.read_text(encoding="utf-8")
    viewbox_width, viewbox_height = _parse_viewbox(svg)
    height = max(1, round(viewbox_height * width / viewbox_width))
    subprocess.run(
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--force-device-scale-factor=1",
            f"--window-size={width},{height}",
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=5000",
            f"--screenshot={png_path}",
            svg_path.resolve().as_uri(),
        ],
        check=True,
        capture_output=True,
    )


def _find_chrome() -> str | None:
    import shutil

    for candidate in _CHROME_CANDIDATES:
        if candidate.startswith("/"):
            if Path(candidate).is_file():
                return candidate
            continue
        if path := shutil.which(candidate):
            return path
    return None


def _find_rsvg_convert() -> str:
    import shutil

    if path := shutil.which("rsvg-convert"):
        return path
    raise RuntimeError("rsvg-convert not found; install with: brew install librsvg")


if __name__ == "__main__":
    path = export_demo()
    print(path)
    if PNG_OUTPUT.exists():
        print(PNG_OUTPUT)
    if SOCIAL_OUTPUT.exists():
        print(SOCIAL_OUTPUT)
