from ai_cost_compare.providers.claude.verdicts import ClaudeVerdicts
from ai_cost_compare.providers.cursor.verdicts import CursorVerdicts


def test_delta_suffix_shown_when_share_changed():
    verdicts = ClaudeVerdicts()
    _, text = verdicts.evaluate("opus", 50, 80)
    assert "was 80%" in text


def test_delta_suffix_hidden_when_unchanged():
    verdicts = ClaudeVerdicts()
    _, text = verdicts.evaluate("opus", 50, 50)
    assert "was" not in text


def test_claude_verdict_profile_families():
    profile = ClaudeVerdicts().profile()
    assert [bucket for bucket, _ in profile.families] == ["opus", "sonnet", "haiku"]
    assert profile.legend_items


def test_cursor_verdict_paths():
    verdicts = CursorVerdicts()
    assert verdicts.evaluate("premium", 80, None)[0] == "red"
    assert verdicts.evaluate("fast", 25, None)[0] == "green"
    assert verdicts.evaluate("fast", 0, None)[0] == "grey70"
