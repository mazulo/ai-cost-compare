import sys
from datetime import date
from io import StringIO
from unittest.mock import patch

import pytest

from ai_cost_compare.cli import _run_provider, run, run_claude_legacy
from ai_cost_compare.core.errors import CliError, CursorDataError


def test_run_exits_on_cli_error(capsys):
    with patch("ai_cost_compare.cli.app", side_effect=CliError("fail", exit_code=7)):
        with pytest.raises(SystemExit) as exc:
            run()
    assert exc.value.code == 7
    assert "fail" in capsys.readouterr().err


def test_run_claude_legacy_prepends_subcommand(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["claude-cost-compare", "--range", "3"])
    seen: list[str] = []

    def fake_app():
        seen.append(list(sys.argv))

    monkeypatch.setattr("ai_cost_compare.cli.app", fake_app)
    run_claude_legacy()
    assert seen[0][1] == "claude"


def test_run_provider_cursor_filters_by_date_range(cursor_csv_text, tmp_path):
    path = tmp_path / "usage.csv"
    path.write_text(cursor_csv_text)
    output = StringIO()

    with patch("ai_cost_compare.cli.make_console") as mock_console:
        mock_console.return_value = __import__("rich").console.Console(
            file=output,
            force_terminal=True,
            width=100,
        )
        _run_provider(
            "cursor",
            range_days=5,
            cutoff=date(2026, 5, 8),
            since=date(2026, 5, 7),
            summary=True,
            plain=True,
            file=path,
        )
    assert "CURSOR DAILY COST" in output.getvalue()


def test_run_provider_unknown_id():
    with pytest.raises(KeyError):
        _run_provider(
            "codex",
            range_days=5,
            cutoff=None,
            since=None,
            summary=False,
            plain=False,
        )


def test_cursor_command_requires_data():
    from ai_cost_compare.providers.cursor.fetch import CursorFetcher

    fetcher = CursorFetcher()
    with patch.object(fetcher, "fetch", side_effect=CursorDataError("need file")):
        provider = __import__(
            "ai_cost_compare.providers.cursor.provider", fromlist=["CursorProvider"]
        ).CursorProvider()
        provider.fetcher = fetcher
        with patch("ai_cost_compare.cli.get", return_value=provider):
            with pytest.raises(CursorDataError):
                _run_provider(
                    "cursor",
                    range_days=5,
                    cutoff=None,
                    since=None,
                    summary=False,
                    plain=False,
                )
