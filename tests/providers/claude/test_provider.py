from datetime import date
from unittest.mock import MagicMock

from ai_cost_compare.providers.base import FetchContext
from ai_cost_compare.providers.claude.provider import ClaudeProvider


def test_provider_wires_components():
    provider = ClaudeProvider()
    assert provider.id == "claude"
    assert provider.fetcher is not None
    assert provider.parser is not None
    assert provider.verdicts is not None


def test_provider_fetch_parse_integration(monkeypatch):
    provider = ClaudeProvider()
    sample = {"daily": []}
    monkeypatch.setattr(provider.fetcher, "fetch", MagicMock(return_value=sample))
    ctx = FetchContext(since=date(2026, 5, 1), until=date(2026, 5, 2))
    assert provider.parse(provider.fetch(ctx)) == []
