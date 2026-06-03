"""
VELYNX Wikipedia Client — Phase 12 Fix
========================================
Drop-in replacement for backend/retrieval/wiki_client.py
Fixes: User-Agent header, timeout, proper API endpoints, fallback chain.

Replace your existing wiki_client.py with this file.
"""

from __future__ import annotations

import json
import logging
import re
import urllib.parse
import urllib.request
from typing import Optional

logger = logging.getLogger("velynx.wiki")

_HEADERS = {
    "User-Agent": "VELYNX/1.0 (cognitive-reasoning-system; open-source research AI)",
    "Accept": "application/json",
}
_TIMEOUT = 3
WIKI_PAGE = "https://en.wikipedia.org/wiki/"


def _strip_html(text: str) -> str:
    import html as _html
    text = re.sub(r"<[^>]+>", "", text)
    return _html.unescape(text)


def parse_results(payload: dict) -> list[dict]:
    """Parse MediaWiki search API response into normalized result dicts."""
    results: list[dict] = []
    for item in payload.get("query", {}).get("search", []):
        title = item.get("title", "")
        snippet = _strip_html(item.get("snippet", ""))
        url = f"{WIKI_PAGE}{urllib.parse.quote(title.replace(' ', '_'))}"
        results.append(
            {
                "source": "wikipedia",
                "title": title,
                "snippet": snippet,
                "url": url,
            }
        )
    return results


def search(query: str, limit: int = 3) -> list[dict]:
    """
    Search Wikipedia and return sources list.
    Tries REST summary API first, falls back to MediaWiki search API.
    Never raises — returns empty list on total failure.
    """
    sources = []

    # ── Strategy 1: REST summary (best for direct factual queries) ─────────
    try:
        slug = urllib.parse.quote(query.replace(" ", "_"), safe="")
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}"
        req = urllib.request.Request(url, headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            data = json.loads(resp.read())
            extract = data.get("extract", "")
            if extract and len(extract) > 60:
                page_url = (data.get("content_urls", {})
                            .get("desktop", {})
                            .get("page", f"https://en.wikipedia.org/wiki/{slug}"))
                sources.append({
                    "url": page_url,
                    "title": data.get("title", query),
                    "snippet": extract[:1000],
                    "source": "wikipedia",
                    "score": 0.90,
                })
                logger.debug("Wikipedia REST summary: found for %r", query)
                return sources  # Single high-quality result is enough
    except Exception as e:
        logger.debug("Wikipedia REST summary failed for %r: %s", query, e)

    # ── Strategy 2: MediaWiki search API ──────────────────────────────────
    try:
        q = urllib.parse.quote(query, safe="")
        search_url = (
            f"https://en.wikipedia.org/w/api.php"
            f"?action=query&list=search&srsearch={q}"
            f"&format=json&srlimit={limit}&utf8=1"
        )
        req = urllib.request.Request(search_url, headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            data = json.loads(resp.read())
            for item in data.get("query", {}).get("search", []):
                title = item.get("title", "")
                snippet = item.get("snippet", "")
                # Clean HTML tags and entities from snippet
                snippet = re.sub(r"<[^>]+>", "", snippet)
                import html as _html
                snippet = _html.unescape(snippet)
                page_slug = urllib.parse.quote(title.replace(" ", "_"), safe="")
                sources.append({
                    "url": f"https://en.wikipedia.org/wiki/{page_slug}",
                    "title": title,
                    "snippet": snippet[:600],
                    "source": "wikipedia",
                    "score": 0.75,
                })
            if sources:
                logger.debug("Wikipedia search API: %d results for %r", len(sources), query)
                return sources
    except Exception as e:
        logger.debug("Wikipedia search API failed for %r: %s", query, e)

    # ── Strategy 3: OpenSearch API (lightweight) ──────────────────────────
    try:
        q = urllib.parse.quote(query, safe="")
        opensearch_url = (
            f"https://en.wikipedia.org/w/api.php"
            f"?action=opensearch&search={q}&limit={limit}&format=json"
        )
        req = urllib.request.Request(opensearch_url, headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            data = json.loads(resp.read())
            # OpenSearch returns [query, [titles], [descriptions], [urls]]
            titles = data[1] if len(data) > 1 else []
            descs = data[2] if len(data) > 2 else []
            urls = data[3] if len(data) > 3 else []
            for i, title in enumerate(titles):
                sources.append({
                    "url": urls[i] if i < len(urls) else f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title)}",
                    "title": title,
                    "snippet": descs[i][:500] if i < len(descs) else "",
                    "source": "wikipedia",
                    "score": 0.65,
                })
        if sources:
            logger.debug("Wikipedia OpenSearch: %d results for %r", len(sources), query)
    except Exception as e:
        logger.debug("Wikipedia OpenSearch failed for %r: %s", query, e)

    return sources


def get_page_content(title: str) -> Optional[str]:
    """Fetch full text of a Wikipedia page (for deep learning mode)."""
    try:
        t = urllib.parse.quote(title.replace(" ", "_"), safe="")
        url = (
            f"https://en.wikipedia.org/w/api.php"
            f"?action=query&titles={t}&prop=extracts"
            f"&exintro=1&format=json&redirects=1"
        )
        req = urllib.request.Request(url, headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            data = json.loads(resp.read())
            pages = data.get("query", {}).get("pages", {})
            for page in pages.values():
                extract = page.get("extract", "")
                if extract:
                    return re.sub(r"<[^>]+>", "", extract)
    except Exception as e:
        logger.debug("Wikipedia page content failed for %r: %s", title, e)
    return None
