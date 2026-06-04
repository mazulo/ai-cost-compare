from ai_cost_compare.providers.cursor.taxonomy import CURSOR_TAXONOMY, classify_cursor_model


def test_classify_premium_and_fast():
    assert classify_cursor_model("claude-opus-4-6") == "premium"
    assert classify_cursor_model("claude-haiku-4") == "fast"
    assert classify_cursor_model("unknown-model") == "other"


def test_share_style_premium_warn():
    assert CURSOR_TAXONOMY.share_style("premium", 60) == "yellow"


def test_share_style_fast_inactive():
    assert CURSOR_TAXONOMY.share_style("fast", 0) == "grey78"


def test_share_style_other_bucket():
    assert CURSOR_TAXONOMY.share_style("other", 10) == "white"
