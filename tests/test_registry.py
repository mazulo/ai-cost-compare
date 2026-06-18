import pytest

from ai_cost_compare.providers.registry import get, list_ids


def test_list_ids():
    assert set(list_ids()) == {"claude", "cursor"}


def test_get_known_providers():
    assert get("claude").id == "claude"
    assert get("cursor").id == "cursor"


def test_get_unknown_provider():
    with pytest.raises(KeyError, match="Unknown provider"):
        get("codex")
