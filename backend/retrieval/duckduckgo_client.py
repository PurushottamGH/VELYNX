"""DuckDuckGo search client — free, no API key required."""
from __future__ import annotations

import html
import json
import urllib.parse
import urllib.request


def _query_ddg(query: str, limit: int, timeout: int) -> list[dict]:
    """Internal: query DuckDuckGo instant answer API."""
    params = {
        "q": query,
        "format": "json",
        "no_html": "1",
        "skip_disambig": "1",
    }
    url = f"https://api.duckduckgo.com/?{urllib.parse.urlencode(params)}"

    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "VELYNX/1.0 (cognitive-reasoning-system)"
        })
        with urllib.request.urlopen(req, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return []

    results: list[dict] = []

    # Abstract (best result)
    abstract = html.unescape(payload.get("AbstractText", ""))
    abstract_url = payload.get("AbstractURL", "")
    if abstract and abstract_url:
        results.append({
            "source": "duckduckgo",
            "title": html.unescape(payload.get("Heading", query)),
            "snippet": abstract[:600],
            "url": abstract_url,
            "score": 0.85,
        })

    # Related topics
    for topic in payload.get("RelatedTopics", [])[:limit]:
        if isinstance(topic, dict):
            text = topic.get("Text", "")
            first_url = topic.get("FirstURL", "")
            if text and first_url:
                results.append({
                    "source": "duckduckgo",
                    "title": html.unescape(text[:80]),
                    "snippet": html.unescape(text[:400]),
                    "url": first_url,
                    "score": 0.65,
                })

    return results[:limit]


def search(query: str, limit: int = 5, timeout: int = 3) -> list[dict]:
    """Query DuckDuckGo with fallback: try full query, then key terms only."""
    if not query.strip():
        return []

    # Try full query first
    results = _query_ddg(query, limit, timeout)
    if results:
        return results

    # Fallback: extract key terms (nouns, 3+ chars, no stop words)
    stop = {"what", "is", "the", "a", "an", "how", "why", "when", "where", "who",
            "does", "do", "are", "can", "with", "of", "in", "on", "to", "for",
            "and", "or", "but", "it", "its", "this", "that", "was", "were"}
    terms = [w.rstrip("?.,!") for w in query.lower().split()
             if w.rstrip("?.,!") not in stop and len(w) >= 2]
    if terms:
        # Try first 2 key terms
        fallback = " ".join(terms[:2])
        results = _query_ddg(fallback, limit, timeout)
        if results:
            return results

    # Last resort: try just the first key term
    if terms:
        results = _query_ddg(terms[0], limit, timeout)
        return results

    return []
