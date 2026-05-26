# Releasing

## One-time setup

### 1. GitHub repository

Push this repo to GitHub (if not already):

```bash
git remote add origin git@github.com:patrickmazulo/claude-cost-compare.git
git push -u origin main
```

### 2. PyPI trusted publishing

1. Create an account on [pypi.org](https://pypi.org) if needed.
2. Register the project name `claude-cost-compare` on PyPI (can happen on first upload).
3. Open **Account settings → Publishing → Add a new pending publisher**:
   - **PyPI project name:** `claude-cost-compare`
   - **Owner:** `patrickmazulo`
   - **Repository name:** `claude-cost-compare`
   - **Workflow name:** `publish.yml`
   - **Environment name:** `pypi`
4. In GitHub repo **Settings → Environments**, create environment `pypi` (no extra secrets required for OIDC).

### 3. Homebrew tap

The formula lives in `Formula/claude-cost-compare.rb` in this repo. Users install with:

```bash
brew install patrickmazulo/claude-cost-compare/claude-cost-compare
```

No separate tap repo required — Homebrew reads the `Formula/` directory from the GitHub repo.

## Release checklist

1. Bump `version` in `pyproject.toml` and `__init__.py`.
2. Update `Formula/claude-cost-compare.rb`:
   - `url` / version segment
   - `sha256` from `shasum -a 256 dist/claude_cost_compare-<version>.tar.gz`
   - Python resources if dependencies changed (`brew update-python-resources Formula/claude-cost-compare.rb`)
3. Run tests: `uv sync --dev && uv run pytest && uv run ruff check .`
4. Build locally: `uv build`
5. Commit, tag, push:

```bash
git commit -am "chore: release v0.1.0"
git tag v0.1.0
git push origin main --tags
```

6. GitHub Actions `Publish` workflow uploads to PyPI.
7. Verify:

```bash
pip install claude-cost-compare
brew update
brew install patrickmazulo/claude-cost-compare/claude-cost-compare
claude-cost-compare --help
```

## Updating Homebrew resources

After dependency changes:

```bash
brew update-python-resources Formula/claude-cost-compare.rb \
  --package-name claude-cost-compare \
  --version 0.1.0
```

Review the diff, then commit the formula update with the release.
