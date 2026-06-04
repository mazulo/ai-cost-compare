"""Fetch Cursor usage CSV from file or dashboard API."""

from pathlib import Path

from ai_cost_compare.config_store import load_cursor_token
from ai_cost_compare.core.errors import CursorDataError
from ai_cost_compare.providers.base import FetchContext, UsageFetcher

CURSOR_EXPORT_URL = (
    "https://cursor.com/api/dashboard/export-usage-events-csv?strategy=tokens"
)


class CursorFetcher(UsageFetcher):
    def fetch(self, ctx: FetchContext) -> str:
        if ctx.file is not None:
            return self.read_file(ctx.file)
        token = ctx.cursor_token or load_cursor_token()
        if token:
            return self.fetch_from_api(token)
        raise CursorDataError(
            "Cursor usage requires --file PATH or a session token.\n"
            "  CSV: export from https://cursor.com/dashboard/usage\n"
            "  API: pip install 'ai-cost-compare[cursor-api]' and set "
            "[cursor] session_token in ~/.config/ai-cost-compare/config.toml"
        )

    def read_file(self, path: Path) -> str:
        if not path.is_file():
            raise CursorDataError(f"File not found: {path}")
        return path.read_text(encoding="utf-8")

    def fetch_from_api(self, session_token: str) -> str:
        try:
            import httpx
        except ImportError as exc:
            raise CursorDataError(
                "Cursor API fetch requires httpx. Install with: "
                "pip install 'ai-cost-compare[cursor-api]'"
            ) from exc

        response = httpx.get(
            CURSOR_EXPORT_URL,
            cookies={"WorkosCursorSessionToken": session_token},
            timeout=60.0,
            follow_redirects=True,
        )
        if response.status_code == 401:
            raise CursorDataError(
                "Cursor session token rejected (401). "
                "Export a fresh WorkosCursorSessionToken from cursor.com dashboard cookies."
            )
        if response.status_code != 200:
            raise CursorDataError(
                f"Cursor API returned HTTP {response.status_code}. "
                "Use --file with a CSV export instead."
            )
        body = response.text.strip()
        if not body or "Date" not in body.splitlines()[0]:
            raise CursorDataError("Cursor API response does not look like a usage CSV.")
        return body
