from ai_cost_compare.providers.claude.taxonomy import CLAUDE_TAXONOMY


def test_classify_delegates_to_model_family():
    assert CLAUDE_TAXONOMY.classify("claude-opus-4") == "opus"


def test_share_style_opus_leak():
    assert CLAUDE_TAXONOMY.share_style("opus", 85) == "bold red"


def test_share_style_sonnet_inactive():
    assert CLAUDE_TAXONOMY.share_style("sonnet", 0) == "grey78"


def test_share_style_haiku_active():
    assert CLAUDE_TAXONOMY.share_style("haiku", 5) == "bright_cyan"
    assert CLAUDE_TAXONOMY.share_style("haiku", 2) == "cyan"


def test_label():
    assert CLAUDE_TAXONOMY.label("opus") == "Opus"
