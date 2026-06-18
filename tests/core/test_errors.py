from ai_cost_compare.core.errors import (
    CcusageNotFoundError,
    CliError,
    CursorDataError,
    NoDataError,
)


def test_cli_error_custom_exit_code():
    err = CliError("boom", exit_code=42)
    assert err.message == "boom"
    assert err.exit_code == 42


def test_typed_errors_exit_codes():
    assert CcusageNotFoundError("x").exit_code == 1
    assert CursorDataError("x").exit_code == 1
    assert NoDataError("x").exit_code == 3
