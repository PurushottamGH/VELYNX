from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request

BRAVE_ENDPOINT = "https://api.search.brave.com/res/v1/web/search"


def search(query: str, limit: int = 6, timeout: int = 3) -> list[dict]:
    """Query Brave Search API and return normalized results."""
    api_key = os.getenv("BRAVE_SEARCH_API_KEY", "").strip()
    if not api_key or not query.strip():
        return []

    params = {
        "q": query,
        "count": str(limit),
        "freshness": "",  # allow all
    }
    url = f"{BRAVE_ENDPOINT}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "X-Subscription-Token": api_key,
        },
    )

    with urllib.request.urlopen(req, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))

    import html as _html
    results: list[dict] = []
    for item in payload.get("web", {}).get("results", [])[:limit]:
        results.append(
            {
                "source": "brave",
                "title": _html.unescape(item.get("title") or ""),
                "snippet": _html.unescape(item.get("description") or ""),
                "url": item.get("url"),
            }
        )
    return results
