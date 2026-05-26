# Releasing

Releases are automated. You bump the version locally; GitHub Actions handles PyPI, tags, GitHub Releases, and the Homebrew formula.

## One-time setup

### GitHub repository

Repo: [github.com/mazulo/claude-cost-compare](https://github.com/mazulo/claude-cost-compare) (public).

### PyPI trusted publishing

1. Register [pypi.org](https://pypi.org) account and project `claude-cost-compare`.
2. **Account settings → Publishing → Add a new pending publisher:**
   - **PyPI project name:** `claude-cost-compare`
   - **Owner:** `patrickmazulo`
   - **Repository name:** `claude-cost-compare`
   - **Workflow name:** `publish.yml`
   - **Environment name:** `pypi`
3. In GitHub **Settings → Environments**, create environment `pypi` (OIDC — no secrets needed).

### Homebrew

Users install from the `Formula/` directory in this repo:

```bash
brew tap mazulo/claude-cost-compare https://github.com/mazulo/claude-cost-compare
brew install claude-cost-compare
npm install -g ccusage
```

The publish workflow updates `url` / `sha256` and refreshes pinned Python resources automatically.

## Release checklist

1. **Bump version** in both files (must match):
   - `pyproject.toml` → `[project].version`
   - `src/claude_cost_compare/__init__.py` → `__version__`
2. **Commit and push** to `main`:

   ```bash
   git commit -am "chore: bump version to 0.2.0"
   git push github main
   ```

3. **Run the Publish workflow** — GitHub → Actions → **Publish** → **Run workflow**.
   - Optional `version` input must match `pyproject.toml` if provided.
   - Workflow will fail if the tag already exists or versions mismatch.

4. **What the workflow does:**
   - Runs ruff + pytest
   - Builds and publishes to PyPI (OIDC)
   - Fetches the published sdist URL + sha256 from PyPI
   - Updates `Formula/claude-cost-compare.rb`
   - Commits the formula change, creates tag `vX.Y.Z`, pushes to `main`
   - Creates a GitHub Release with auto-generated notes
   - On macOS: runs `brew update-python-resources` and commits if deps changed

5. **Verify:**

   ```bash
   pip install claude-cost-compare
   brew update
   brew upgrade claude-cost-compare
   claude-cost-compare --help
   ```

## Manual formula maintenance

Normally unnecessary. If you need to refresh resources locally:

```bash
brew update-python-resources Formula/claude-cost-compare.rb \
  --package-name claude-cost-compare \
  --version 0.1.0
```

Update checksum only (without a full release):

```bash
uv run python scripts/update_formula.py \
  --url "https://files.pythonhosted.org/packages/.../claude_cost_compare-0.1.0.tar.gz" \
  --sha256 "<sha256>"
```

## Demo asset

Regenerate the README terminal screenshot after UI changes:

```bash
uv run python scripts/export_demo.py
git add docs/assets/demo.svg
```
