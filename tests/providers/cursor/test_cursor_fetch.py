from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest

from ai_cost_compare.core.errors import CursorDataError
from ai_cost_compare.providers.base import FetchContext
from ai_cost_compare.providers.cursor.fetch import CursorFetcher


def test_fetch_from_file(tmp_path, cursor_csv_text):
    path = tmp_path / "usage.csv"
    path.write_text(cursor_csv_text)
    fetcher = CursorFetcher()
    ctx = FetchContext(since=date(2026, 5, 1), until=date(2026, 5, 31), file=path)
    assert "Date,Model" in fetcher.fetch(ctx)


def test_read_file_missing():
    with pytest.raises(CursorDataError, match="not found"):
        CursorFetcher().read_file(Path("/nonexistent/usage.csv"))


def test_fetch_requires_file_or_token():
    fetcher = CursorFetcher()
    ctx = FetchContext(since=date(2026, 5, 1), until=date(2026, 5, 31))
    with patch("ai_cost_compare.providers.cursor.fetch.load_cursor_token", return_value=None):
        with pytest.raises(CursorDataError, match="--file"):
            fetcher.fetch(ctx)


def test_fetch_from_api_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "Date,Model,Cost,Cost to you\n2026-05-01,m,1,1\n"
    with patch.object(httpx, "get", return_value=mock_response):
        body = CursorFetcher().fetch_from_api("token")
    assert body.startswith("Date,Model")


def test_fetch_from_api_401():
    mock_response = MagicMock(status_code=401, text="")
    with patch.object(httpx, "get", return_value=mock_response):
        with pytest.raises(CursorDataError, match="401"):
            CursorFetcher().fetch_from_api("bad")


def test_fetch_from_api_non_csv_body():
    mock_response = MagicMock(status_code=200, text="not csv")
    with patch.object(httpx, "get", return_value=mock_response):
        with pytest.raises(CursorDataError, match="usage CSV"):
            CursorFetcher().fetch_from_api("token")


def test_fetch_from_api_requires_httpx(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "httpx":
            raise ImportError("no httpx")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(CursorDataError, match="httpx"):
        CursorFetcher().fetch_from_api("token")


def test_fetch_from_api_http_error():
    mock_response = MagicMock(status_code=500, text="error")
    with patch.object(httpx, "get", return_value=mock_response):
        with pytest.raises(CursorDataError, match="HTTP 500"):
            CursorFetcher().fetch_from_api("token")
