<div align="center">

# claude-cost-compare

**Daily Claude spend, before/after windows, and model routing health — in your terminal.**

[![PyPI](https://img.shields.io/pypi/v/claude-cost-compare?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/claude-cost-compare/)
[![Python](https://img.shields.io/pypi/pyversions/claude-cost-compare?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/claude-cost-compare/)
[![CI](https://img.shields.io/github/actions/workflow/status/mazulo/claude-cost-compare/ci.yml?branch=main&style=flat-square&logo=github)](https://github.com/mazulo/claude-cost-compare/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

Turn local [ccusage](https://github.com/ryoppippi/ccusage) data into three Rich tables: daily cost, split-window comparison, and per-model verdicts.

**Not a ccusage fork** — an interpretation layer on top. ccusage reports what you spent; this CLI adds before/after windows, mix shifts, and routing health verdicts.

[Quick start](#-quick-start) · [Demo](#-demo) · [ccusage vs this tool](#-ccusage-vs-this-tool) · [Install](#-install) · [Usage](#-usage) · [How it works](#-how-it-works)

</div>

---

## ✨ Why this exists

Claude Code usage can spike fast — especially when Opus routing leaks or Sonnet/Haiku tiers stop doing their job. This CLI answers three questions at a glance:

| Question | Table |
|----------|-------|
| What did I spend each day? | **Daily cost** — cost, tokens, model mix |
| Did things change after a date? | **Before vs After** — avg/day, totals, mix shift |
| Are models routed correctly? | **Real Signal** — Opus / Sonnet / Haiku verdicts |

No cloud upload. Reads your local ccusage JSON and prints a terminal report.

---

## 🔀 ccusage vs this tool

| | [ccusage](https://github.com/ryoppippi/ccusage) | **claude-cost-compare** |
|---|-----|-----|
| **Role** | Usage analytics — read local logs, report spend | Interpretation layer — explain *what changed* and *if routing looks healthy* |
| **Scope** | Many agents, daily/weekly/monthly/session views | Claude Code focus: before/after split + model mix verdicts |
| **Output** | Descriptive tables & totals | Daily cost + **Before vs After** + **Real Signal** (Opus/Sonnet/Haiku) |
| **Install both?** | ✅ Required (data source) | ✅ Optional companion on top |

Use ccusage for *“what did I spend?”* Use this when *“did something break after I changed config on Tuesday?”*

---

## 🖥 Demo

<p align="center">
  <img src="docs/assets/demo.svg" alt="claude-cost-compare terminal output showing daily cost, before/after comparison, and model health verdicts" width="920" />
</p>

<p align="center">
  <sub>Sample fixture output · <code>--range 7 --cutoff 2026-05-08</code></sub>
</p>

<details>
<summary><strong>Same output as plain text</strong></summary>

```bash
claude-cost-compare --range 7 --cutoff 2026-05-08
```

```
CLAUDE DAILY COST  ·  2026-05-06 → 2026-05-26
┌─────────────┬────────┬───────────┬────────┬───────────┬──────┬────────┬──────┐
│ Date        │ Era    │      Cost │ Tokens │ Mix       │ Opus │ Sonnet │ Haiku│
├─────────────┼────────┼───────────┼────────┼───────────┼──────┼────────┼──────┤
│ 2026-05-06  │ Before │     $2.68 │   3.2M │ ████████… │ 100% │     0% │   0% │
│ 2026-05-08  │ Today  │    $80.88 │ 117.9M │ ████████… │  97% │     0% │   3% │
│ 2026-05-09  │ After  │     $9.92 │  12.1M │ ████████… │  45% │    55% │   0% │
└─────────────┴────────┴───────────┴────────┴───────────┴──────┴────────┴──────┘

BEFORE vs AFTER  ·  Split at 2026-05-08
REAL SIGNAL      ·  Post-2026-05-08 · per-model routing verdicts
```

</details>

---

## 🚀 Quick start

**1. Install ccusage** (peer dependency — reads your local usage data):

```bash
npm install -g ccusage
```

**2. Install the CLI:**

```bash
pip install claude-cost-compare
# or
uv tool install claude-cost-compare
```

**3. Run:**

```bash
claude-cost-compare --range 5
```

---

## 📦 Install

### PyPI / uv

```bash
pip install claude-cost-compare
uv tool install claude-cost-compare
uvx claude-cost-compare --help          # run without installing
```

### Homebrew

```bash
brew tap mazulo/claude-cost-compare https://github.com/mazulo/claude-cost-compare
brew install claude-cost-compare
npm install -g ccusage                  # still required
```

One-liner (no tap):

```bash
brew install https://raw.githubusercontent.com/mazulo/claude-cost-compare/main/Formula/claude-cost-compare.rb
```

### Requirements

- Python **3.11+** (pip/uv) or Homebrew
- [ccusage](https://www.npmjs.com/package/ccusage) on your `PATH`

---

## 📖 Usage

```bash
# Last 5 days vs today (default)
claude-cost-compare --range 5

# 7-day window split at a specific date
claude-cost-compare --range 7 --cutoff 2026-05-13

# Full billing period from a start date
claude-cost-compare --since 2026-05-01 --cutoff 2026-05-13

# Daily summary only — skip comparison tables
claude-cost-compare --summary --since 2026-05-01

# Plain output (also respects NO_COLOR)
claude-cost-compare --plain --range 5
```

### Flags

| Flag | Short | Description |
|------|-------|-------------|
| `--range` | `-r` | Days before cutoff for the "before" window (default: `5`) |
| `--cutoff` | `-c` | Before/after split date `YYYY-MM-DD` (default: today) |
| `--since` | `-s` | Explicit start date — overrides `--range` |
| `--summary` | | Daily cost table only |
| `--plain` | | Disable color |

---

## 🧠 How it works

```mermaid
flowchart LR
  A[ccusage JSON] --> B[Parser]
  B --> C[Window stats]
  C --> D[Before / After deltas]
  C --> E[Model verdicts]
  D --> F[Rich terminal report]
  E --> F
```

1. **Fetch** — shells out to `ccusage` for daily usage JSON (NVM-aware discovery).
2. **Parse** — normalizes dates, costs, and per-model breakdowns.
3. **Analyze** — splits records at `--cutoff`, computes averages and mix shifts.
4. **Verdict** — flags Opus routing leaks, low Sonnet share, Haiku usage patterns.
5. **Render** — Rich tables with era labels, mix bars, and color-coded costs.

---

## 🛠 Development

```bash
git clone https://github.com/mazulo/claude-cost-compare.git
cd claude-cost-compare
uv sync --dev
uv run pytest
uv run claude-cost-compare --range 5
```

Regenerate the README demo SVG after UI changes:

```bash
uv run python scripts/export_demo.py
```

---

## 🚢 Releasing

Bump `version` in `pyproject.toml` and `src/claude_cost_compare/__init__.py`, push to `main`, then run the **Publish** workflow from GitHub Actions. It will:

1. Run tests and publish to PyPI
2. Update the Homebrew formula checksum
3. Create a git tag and GitHub Release
4. Refresh Homebrew Python resources on macOS

Details: [docs/RELEASING.md](docs/RELEASING.md)

---

## 📄 License

MIT — see [LICENSE](LICENSE).

---

<div align="center">

Built for Claude Code power users who want spend visibility without leaving the terminal.

**[⭐ Star on GitHub](https://github.com/mazulo/claude-cost-compare)** if this saves you from an Opus routing surprise.

</div>
