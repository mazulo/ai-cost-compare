from ai_cost_compare.render.console import make_console


def test_make_console_plain():
    console = make_console(plain=True)
    assert console.no_color is True


def test_make_console_respects_no_color_env(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    console = make_console(plain=False)
    assert console.no_color is True
