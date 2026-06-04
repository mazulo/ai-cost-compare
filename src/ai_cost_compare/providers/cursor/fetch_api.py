"""Fetch Cursor usage CSV via dashboard API (unofficial)."""

from ai_cost_compare.core.errors import CursorDataError

CURSOR_EXPORT_URL = "https://cursor.com/api/dashboard/export-usage-events-csv?strategy=tokens"


def fetch_usage_csv(session_token: str) -> str:
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
