from ai_cost_compare.config_store import _load_cursor_token_ini, config_path, load_cursor_token


def test_config_path_default():
    assert config_path().name == "config.toml"


def test_config_path_override(monkeypatch, tmp_path):
    cfg = tmp_path / "custom.toml"
    monkeypatch.setenv("AI_COST_COMPARE_CONFIG", str(cfg))
    assert config_path() == cfg


def test_load_cursor_token_missing_file(tmp_path):
    assert load_cursor_token(tmp_path / "nope.toml") is None


def test_load_cursor_token_toml(tmp_path):
    cfg = tmp_path / "config.toml"
    cfg.write_text('[cursor]\nsession_token = "secret-token"\n')
    assert load_cursor_token(cfg) == "secret-token"


def test_load_cursor_token_ini_fallback(tmp_path):
    cfg = tmp_path / "config.toml"
    cfg.write_text("session_token = 'ini-token'\n")
    assert _load_cursor_token_ini(cfg) == "ini-token"
