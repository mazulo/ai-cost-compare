from ai_cost_compare.providers.claude.verdicts import ClaudeVerdicts


def test_opus_improving_and_on_target():
    verdicts = ClaudeVerdicts()
    assert verdicts.evaluate("opus", 45, None)[0] == "yellow"
    assert verdicts.evaluate("opus", 30, None)[0] == "green"


def test_sonnet_growing_and_unused():
    verdicts = ClaudeVerdicts()
    assert verdicts.evaluate("sonnet", 15, None)[0] == "yellow"
    assert verdicts.evaluate("sonnet", 0, None)[0] == "grey70"


def test_haiku_delegation_levels():
    verdicts = ClaudeVerdicts()
    assert verdicts.evaluate("haiku", 15, None)[0] == "green"
    assert verdicts.evaluate("haiku", 5, None)[0] == "green"
    assert verdicts.evaluate("haiku", 2, None)[0] == "bright_cyan"
