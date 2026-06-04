from unittest.mock import MagicMock, patch

import httpx
import pytest

from ai_cost_compare.core.errors import CursorDataError
from ai_cost_compare.providers.cursor.fetch import CursorFetcher


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


def test_fetch_from_api_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "Date,Model,Cost,Cost to you\n2026-05-01,claude-opus-4-6,1.0,1.0\n"

    with patch.object(httpx, "get", return_value=mock_response) as mock_get:
        body = CursorFetcher().fetch_from_api("test-token")

    assert "Date,Model" in body
    mock_get.assert_called_once()
