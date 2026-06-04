from ai_cost_compare.providers.claude.config import model_family


def test_model_family_mapping():
    assert model_family("claude-opus-4-6") == "opus"
    assert model_family("claude-sonnet-4-6") == "sonnet"
    assert model_family("claude-haiku-4-5") == "haiku"
    assert model_family("gpt-4o") == "other"
