from __future__ import annotations

import asyncio
import time
from typing import Callable

from backend.pipeline import truth_filter
from backend.retrieval import arxiv_client, brave_client, searxng_client, tavily_client, wiki_client
from backend.retrieval import duckduckgo_client
from backend.retrieval import browser as browser_client

_CACHE_TTL_SECONDS = 180
_CACHE: dict[str, tuple[float, list[dict], dict]] = {}

_RATE_LIMIT_WINDOW = 60
_RATE_LIMIT_MAX = 30
_RATE_EVENTS: list[float] = []


def _rate_limit_ok() -> bool:
    now = time.time()
    cutoff = now - _RATE_LIMIT_WINDOW
    while _RATE_EVENTS and _RATE_EVENTS[0] < cutoff:
        _RATE_EVENTS.pop(0)
    if len(_RATE_EVENTS) >= _RATE_LIMIT_MAX:
        return False
    _RATE_EVENTS.append(now)
    return True


def _get_cached(query: str) -> tuple[list[dict], dict] | None:
    entry = _CACHE.get(query)
    if not entry:
        return None
    expires_at, data, report = entry
    if time.time() > expires_at:
        _CACHE.pop(query, None)
        return None
    return data, report


def _set_cache(query: str, data: list[dict], report: dict) -> None:
    _CACHE[query] = (time.time() + _CACHE_TTL_SECONDS, data, report)


def clean_query_for_search(query: str) -> str:
    """Strip question prefixes to get a clean search query.

    'What is the speed of light?' → 'speed of light'
    'How does quantum computing work?' → 'quantum computing work'
    'Tell me about Einstein' → 'Einstein'
    """
    import re as _re
    cleaned = query.strip()
    # Remove question prefixes
    cleaned = _re.sub(
        r"^(?:what\s+(?:is|are|was|were|does|do|did|will|would|could|should|can)\s+(?:the\s+|a\s+|an\s+)?|"
        r"how\s+(?:does|do|did|is|are|was|were|can|could|would|should|to)\s+(?:the\s+|a\s+|an\s+)?|"
        r"tell\s+me\s+(?:about|of)\s+|"
        r"explain\s+(?:the\s+|a\s+|an\s+)?|"
        r"describe\s+(?:the\s+|a\s+|an\s+)?|"
        r"define\s+(?:the\s+|a\s+|an\s+)?|"
        r"who\s+(?:is|are|was|were)\s+(?:the\s+|a\s+|an\s+)?|"
        r"where\s+(?:is|are|was|were|can\s+(?:i|we))\s+(?:the\s+|a\s+|an\s+)?|"
        r"when\s+(?:was|were|did|is|are)\s+(?:the\s+|a\s+|an\s+)?|"
        r"why\s+(?:is|are|was|were|do|does|did)\s+(?:the\s+|a\s+|an\s+)?)",
        "",
        cleaned,
        flags=_re.IGNORECASE,
    )
    # Remove trailing question marks and extra whitespace
    cleaned = _re.sub(r"\?+$", "", cleaned).strip()
    return cleaned if cleaned else query.strip()


def _normalize_item(item: dict) -> dict:
    url = (item.get("url") or "").strip()
    title = (item.get("title") or "").strip() or None
    snippet = (item.get("snippet") or "").strip() or None
    source = (item.get("source") or "").strip() or None
    return {
        "url": url,
        "title": title,
        "snippet": snippet,
        "source": source,
    }


_PER_SOURCE_TIMEOUT = 3.0  # seconds — hard cap per source


async def _run_source(name: str, func: Callable[[str], list[dict]], query: str) -> tuple[str, list[dict], dict]:
    start = time.time()
    try:
        results = await asyncio.wait_for(asyncio.to_thread(func, query), timeout=_PER_SOURCE_TIMEOUT)
        duration_ms = int((time.time() - start) * 1000)
        normalized = [_normalize_item(item) for item in results if item.get("url")]
        return name, normalized, {"count": len(normalized), "duration_ms": duration_ms, "error": None}
    except asyncio.TimeoutError:
        duration_ms = int((time.time() - start) * 1000)
        return name, [], {"count": 0, "duration_ms": duration_ms, "error": f"timeout ({_PER_SOURCE_TIMEOUT}s)"}
    except Exception as exc:  # noqa: BLE001 - report errors without breaking
        duration_ms = int((time.time() - start) * 1000)
        return name, [], {"count": 0, "duration_ms": duration_ms, "error": str(exc)}


async def retrieve_with_report(query: str) -> dict:
    """Retrieve results plus a per-source report."""
    cached = _get_cached(query)
    if cached is not None:
        data, report = cached
        return {"results": data, "report": {**report, "cached": True}}

    if not _rate_limit_ok():
        report = {"query": query, "cached": False, "rate_limited": True, "sources": {}, "total_ms": 0}
        return {"results": [], "report": report}

    # Use clean query for actual searching
    search_query = clean_query_for_search(query)

    sources: list[tuple[str, Callable[[str], list[dict]]]] = [
        ("wikipedia", wiki_client.search),
        ("duckduckgo", duckduckgo_client.search),
        ("searxng", searxng_client.search),
        ("brave", brave_client.search),
        ("tavily", tavily_client.search),
        ("arxiv", arxiv_client.search),
    ]

    start = time.time()
    tasks = [_run_source(name, func, search_query) for name, func in sources]
    results = await asyncio.gather(*tasks)

    flattened: list[dict] = []
    source_report: dict[str, dict] = {}
    for name, items, meta in results:
        source_report[name] = meta
        flattened.extend(items)

    browser_items: list[dict] = []
    browser_meta = {"count": 0, "duration_ms": 0, "error": None}
    try:
        ranked = truth_filter.score_sources(flattened)["sources"]
        top_sources = ranked[:3]
        browser_start = time.time()
        browser_items = await asyncio.wait_for(
            browser_client.fetch_sources(top_sources, limit=3),
            timeout=2.0,
        )
        browser_meta = {
            "count": len(browser_items),
            "duration_ms": int((time.time() - browser_start) * 1000),
            "error": None,
        }
    except asyncio.TimeoutError:
        browser_meta = {
            "count": 0,
            "duration_ms": 5000,
            "error": "browser timeout (5s)",
        }
    except Exception as exc:  # noqa: BLE001 - keep retrieval resilient
        browser_meta = {
            "count": 0,
            "duration_ms": 0,
            "error": str(exc),
        }

    if browser_items:
        source_report["browser"] = browser_meta
        flattened.extend(browser_items)

    report = {
        "query": query,
        "cached": False,
        "rate_limited": False,
        "sources": source_report,
        "total_ms": int((time.time() - start) * 1000),
    }
    _set_cache(query, flattened, report)
    return {"results": flattened, "report": report}


async def retrieve_all(query: str) -> list[dict]:
    """Retrieve results from all sources in parallel with caching and rate limits."""
    payload = await retrieve_with_report(query)
    return payload["results"]


def retrieve_all_sync(query: str) -> list[dict]:
    """Sync wrapper for retrieval when not already in an event loop."""
    return asyncio.run(retrieve_all(query))
