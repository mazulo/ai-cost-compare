from datetime import date
from unittest.mock import patch

import pytest

from ai_cost_compare.core.errors import CcusageNotFoundError
from ai_cost_compare.providers.base import FetchContext
from ai_cost_compare.providers.claude.fetch import ClaudeFetcher


def test_fetch_daily_via_context(tmp_path):
    fake = tmp_path / "ccusage"
    fake.write_text("#!/bin/sh\necho '{\"daily\":[]}'\n")
    fake.chmod(0o755)
    fetcher = ClaudeFetcher()
    ctx = FetchContext(
        since=date(2026, 5, 1),
        until=date(2026, 5, 2),
        ccusage_bin=fake,
    )
    with patch.object(fetcher, "find_ccusage", return_value=fake):
        assert fetcher.fetch(ctx) == {"daily": []}


def test_find_ccusage_missing():
    fetcher = ClaudeFetcher()
    with patch.object(ClaudeFetcher, "_nvm_ccusage_paths", return_value=[]):
        with patch("shutil.which", return_value=None):
            with pytest.raises(CcusageNotFoundError):
                fetcher.find_ccusage()


def test_nvm_ccusage_paths_used(tmp_path, monkeypatch):
    nvm_bin = tmp_path / "versions" / "v20.0.0" / "bin"
    nvm_bin.mkdir(parents=True)
    ccusage = nvm_bin / "ccusage"
    ccusage.write_text("#!/bin/sh\necho '{\"daily\":[]}'\n")
    ccusage.chmod(0o755)
    monkeypatch.setattr(ClaudeFetcher, "_nvm_ccusage_paths", lambda self: [ccusage])
    with patch("shutil.which", return_value=None):
        assert ClaudeFetcher().find_ccusage() == ccusage


def test_fetch_daily_ccusage_failure_stderr(tmp_path):
    fake = tmp_path / "ccusage"
    fake.write_text("#!/bin/sh\necho err 1>&2\nexit 1\n")
    fake.chmod(0o755)
    fetcher = ClaudeFetcher()
    with pytest.raises(CcusageNotFoundError, match="err"):
        fetcher.fetch_daily(date(2026, 5, 1), date(2026, 5, 2), ccusage_bin=fake)
