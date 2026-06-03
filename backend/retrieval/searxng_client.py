from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request


def search(query: str, limit: int = 8, timeout: int = 3) -> list[dict]:
    """Query SearXNG and return normalized results."""
    base_url = os.getenv("SEARXNG_BASE_URL", "").strip().rstrip("/")
    if not base_url or not query.strip():
        return []

    params = {
        "q": query,
        "format": "json",
        "categories": "general",
        "language": "en",
    }
    url = f"{base_url}/search?{urllib.parse.urlencode(params)}"

    with urllib.request.urlopen(url, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))

    results: list[dict] = []
    import html as _html
    for item in payload.get("results", [])[:limit]:
        results.append(
            {
                "source": "searxng",
                "title": _html.unescape(item.get("title") or ""),
                "snippet": _html.unescape(item.get("content") or ""),
                "url": item.get("url"),
            }
        )
    return results
