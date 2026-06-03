from __future__ import annotations

import json
import os
import urllib.request

TAVILY_ENDPOINT = "https://api.tavily.com/search"


def search(query: str, limit: int = 6, timeout: int = 3) -> list[dict]:
    """Query Tavily API and return normalized results."""
    api_key = os.getenv("TAVILY_API_KEY", "").strip()
    if not api_key or not query.strip():
        return []

    payload = {
        "api_key": api_key,
        "query": query,
        "max_results": limit,
        "include_raw_content": False,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        TAVILY_ENDPOINT,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=timeout) as response:
        response_payload = json.loads(response.read().decode("utf-8"))

    import html as _html
    results: list[dict] = []
    for item in response_payload.get("results", [])[:limit]:
        results.append(
            {
                "source": "tavily",
                "title": _html.unescape(item.get("title") or ""),
                "snippet": _html.unescape(item.get("content") or ""),
                "url": item.get("url"),
            }
        )
    return results
