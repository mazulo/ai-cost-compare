"""CLI exit codes and typed errors."""


class CliError(Exception):
    """Base error with a process exit code."""

    exit_code = 1

    def __init__(self, message: str, *, exit_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        if exit_code is not None:
            self.exit_code = exit_code


class CcusageNotFoundError(CliError):
    exit_code = 1


class CursorDataError(CliError):
    exit_code = 1


class NoDataError(CliError):
    exit_code = 3
