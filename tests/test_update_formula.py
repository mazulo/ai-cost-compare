import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_update_formula_script_replaces_main_artifact_only(tmp_path: Path) -> None:
    formula = tmp_path / "claude-cost-compare.rb"
    formula.write_text(
        'class ClaudeCostCompare < Formula\n'
        '  url "https://example.com/old.tar.gz"\n'
        '  sha256 "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"\n'
        '  resource "attrs" do\n'
        '    sha256 "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"\n'
        "  end\n",
        encoding="utf-8",
    )

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "update_formula.py"),
            "--url",
            "https://example.com/new.tar.gz",
            "--sha256",
            "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
            "--formula",
            str(formula),
        ],
        check=True,
        cwd=ROOT,
    )

    text = formula.read_text(encoding="utf-8")
    assert 'url "https://example.com/new.tar.gz"' in text
    assert 'sha256 "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"' in text
    assert 'sha256 "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"' in text
