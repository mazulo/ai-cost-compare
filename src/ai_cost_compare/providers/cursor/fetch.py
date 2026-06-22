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
        from ai_cost_compare.config_store import config_path

        cfg = config_path()
        raise CursorDataError(
            "Cursor usage requires --file PATH or a session token.\n\n"
            "Option A — CSV export:\n"
            "  1. Go to https://cursor.com/dashboard/usage and export a CSV\n"
            "  2. Run: ai-cost-compare cursor --file ~/Downloads/usage.csv\n\n"
            "Option B — session token (auto-fetch):\n"
            "  1. Open https://cursor.com/settings in your browser\n"
            "  2. DevTools → Application → Cookies → cursor.com\n"
            "  3. Copy the value of WorkosCursorSessionToken\n"
            f"  4. Edit {cfg}:\n"
            "       [cursor]\n"
            '       session_token = "paste-your-token-here"\n'
            "  (requires: pip install 'ai-cost-compare[cursor-api]')"
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
