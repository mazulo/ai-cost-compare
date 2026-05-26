# claude-cost-compare

Daily Claude cost analysis with before/after comparison and model health signals.

Parses local usage data via [ccusage](https://github.com/ryoppippi/ccusage) and prints three tables:

1. **Daily cost** — date, era, cost, tokens, model mix (Opus / Sonnet / Haiku)
2. **Before vs After** — window comparison split at a cutoff date
3. **Real Signal** — per-model health verdicts vs your baseline

## Prerequisites

- Python 3.11+ (pip/uv install) or Homebrew
- [ccusage](https://www.npmjs.com/package/ccusage): `npm install -g ccusage`

## Install

### PyPI

```bash
pip install claude-cost-compare
# or
uv tool install claude-cost-compare
```

### Homebrew

The formula lives in this repo’s `Formula/` directory. Tap with an explicit URL (Homebrew otherwise looks for a separate `homebrew-claude-cost-compare` repo):

```bash
brew tap mazulo/claude-cost-compare https://github.com/mazulo/claude-cost-compare
brew install claude-cost-compare
npm install -g ccusage
```

Or install the formula directly:

```bash
brew install https://raw.githubusercontent.com/mazulo/claude-cost-compare/main/Formula/claude-cost-compare.rb
npm install -g ccusage
```

Requires a **public** GitHub repo. Homebrew installs the CLI only; `ccusage` remains a separate npm peer dependency.

## Usage

```bash
# Last 5 days vs today (default)
claude-cost-compare --range 5

# 7-day window split at a specific date
claude-cost-compare --range 7 --cutoff 2026-05-13

# Full billing period, split at May 13
claude-cost-compare --since 2026-05-01 --cutoff 2026-05-13

# Daily summary only — no comparisons
claude-cost-compare --summary --since 2026-05-01
```

### Options

| Flag | Description |
|------|-------------|
| `--range`, `-r` | Days before cutoff for "before" window (default: 5) |
| `--cutoff`, `-c` | Before/after split date `YYYY-MM-DD` (default: today) |
| `--since`, `-s` | Explicit start date — overrides `--range` |
| `--summary` | Daily cost table only |
| `--plain` | Disable color (also respects `NO_COLOR`) |

## Development

```bash
uv sync --dev
uv run pytest
uv run claude-cost-compare --range 5
```

## Releasing

See [docs/RELEASING.md](docs/RELEASING.md) for PyPI trusted publishing and Homebrew formula updates.

## License

MIT
