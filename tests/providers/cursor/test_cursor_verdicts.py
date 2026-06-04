from ai_cost_compare.providers.cursor.verdicts import CursorVerdicts


def test_premium_warn_and_ok():
    verdicts = CursorVerdicts()
    assert verdicts.evaluate("premium", 55, None)[0] == "yellow"
    assert verdicts.evaluate("premium", 30, None)[0] == "green"


def test_fast_some_usage():
    verdicts = CursorVerdicts()
    assert verdicts.evaluate("fast", 5, None)[0] == "yellow"
