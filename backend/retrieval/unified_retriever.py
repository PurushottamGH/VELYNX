"""
VELYNX Unified Retriever — Phase 12 (Patched)
===============================================
Never-fail retrieval chain with per-source timeouts.
Always returns something — never silently dies.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Callable

logger = logging.getLogger("velynx.retriever")


@dataclass
class RetrievalSource:
    url: str = ""
    title: str = ""
    snippet: str = ""
    source: str = ""
    score: float = 0.5
    retrieved_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "title": self.title,
            "snippet": self.snippet,
            "source": self.source,
            "score": self.score,
        }


@dataclass
class RetrievalReport:
    query: str
    sources: list[RetrievalSource]
    attempts: dict[str, str]  # source_name → "ok" | "failed: reason"
    elapsed: float

    @property
    def source_dicts(self) -> list[dict]:
        return [s.to_dict() for s in self.sources]

    def __repr__(self):
        ok = [k for k, v in self.attempts.items() if v == "ok"]
        fail = [k for k, v in self.attempts.items() if v != "ok"]
        return (f"RetrievalReport(query={self.query!r}, "
                f"sources={len(self.sources)}, ok={ok}, failed={fail})")


class UnifiedRetriever:
    """
    Unified retrieval client with ordered fallback chain.
    Never raises — always returns at least an empty list with a report.
    """

    def __init__(self, timeout: float = 3.0, max_sources: int = 6):
        self.timeout = timeout
        self.max_sources = max_sources
        self._last_wiki_request = 0.0
        self._wiki_min_interval = 0.5

    def _wiki_rate_limit(self):
        """Enforce minimum interval between Wikipedia API requests."""
        import time as _time
        elapsed = _time.time() - self._last_wiki_request
        if elapsed < self._wiki_min_interval:
            _time.sleep(self._wiki_min_interval - elapsed)
        self._last_wiki_request = _time.time()

    def _wiki_fetch(self, url: str, timeout: int = 5) -> dict | None:
        """Fetch a Wikipedia URL with 429 retry logic."""
        import urllib.error
        for attempt in range(3):
            self._wiki_rate_limit()
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": "VELYNX/1.0 (cognitive-reasoning-system)"
                })
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    return json.loads(r.read())
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    import time as _time
                    _time.sleep(3 * (attempt + 1))
                    continue
                return None
            except Exception:
                return None
        return None

    _STOP = {"what", "is", "the", "a", "an", "how", "why", "when", "where",
             "who", "does", "do", "are", "was", "were", "of", "in", "on",
             "at", "to", "for", "with", "by", "from", "and", "or", "but",
             "it", "its", "that", "this", "explain", "describe", "does"}

    _SKIP_ARXIV_PATTERNS = [
        r"how to (install|setup|configure|run|start|use|open|download)",
        r"what (is the best|should I|can I)",
        r"(download|install|setup|configure)\s+\w+",
        r"(beginner|tutorial|guide|learn|start)",
        r"vs\s+|compare|difference between",
        r"(salary|job|career|cost|price|buy)",
        r"(fix|error|bug|issue|problem|troubleshoot)",
    ]

    _ACADEMIC_KEYWORDS = {
        "paper", "research", "arxiv", "study", "journal",
        "theorem", "proof", "algorithm", "neural", "quantum",
        "equation", "mathematical", "physics", "chemistry", "biology",
    }

    def _should_skip_arxiv(self, query: str) -> bool:
        q = query.lower()
        return any(re.search(p, q) for p in self._SKIP_ARXIV_PATTERNS)

    def _is_academic(self, query: str) -> bool:
        q = query.lower()
        return any(w in q for w in self._ACADEMIC_KEYWORDS)

    def _extract_keywords(self, query: str) -> str:
        """Extract 2-4 key terms from a natural language query."""
        words = re.sub(r"[^\w\s]", "", query.lower()).split()
        keywords = [w for w in words if w not in self._STOP and len(w) > 2]
        return " ".join(keywords[:4])

    async def _safe_fetch(
        self, fn: Callable, query: str, timeout: float
    ) -> tuple[str, list[RetrievalSource], str]:
        """Run a single source with its own timeout. Never raises."""
        try:
            results = await asyncio.wait_for(
                asyncio.to_thread(fn, query),
                timeout=timeout,
            )
            if results:
                return "ok", results, "ok"
            return "empty", [], "empty"
        except asyncio.TimeoutError:
            return "timeout", [], "failed: timeout"
        except Exception as exc:
            return "error", [], f"failed: {exc}"

    async def retrieve(self, query: str) -> RetrievalReport:
        """Retrieve from all available sources with per-source timeouts."""
        t_start = time.time()
        attempts: dict[str, str] = {}
        all_sources: list[RetrievalSource] = []

        # Build chain with per-source timeouts
        tasks = [
            self._safe_fetch(self._wikipedia_direct, query, timeout=8.0),
            self._safe_fetch(self._wikipedia_client, query, timeout=8.0),
            self._safe_fetch(self._duckduckgo_client, query, timeout=8.0),
            self._safe_fetch(self._brave_client, query, timeout=10.0),
            self._safe_fetch(self._tavily_client, query, timeout=10.0),
        ]
        labels = [
            "wikipedia_direct",
            "wikipedia_client",
            "duckduckgo",
            "brave",
            "tavily",
        ]

        # arXiv only for academic queries
        if self._is_academic(query) and not self._should_skip_arxiv(query):
            tasks.append(self._safe_fetch(self._arxiv_client, query, timeout=12.0))
            labels.append("arxiv")

        results = await asyncio.gather(*tasks)

        for label, (status, sources, msg) in zip(labels, results):
            attempts[label] = msg
            if status == "ok" and sources:
                all_sources.extend(sources)

        # Deduplicate by URL
        seen: set[str] = set()
        deduped: list[RetrievalSource] = []
        for s in all_sources:
            if s.url not in seen:
                seen.add(s.url)
                deduped.append(s)

        elapsed = time.time() - t_start
        return RetrievalReport(
            query=query,
            sources=deduped[:self.max_sources],
            attempts=attempts,
            elapsed=elapsed,
        )

    # ── Individual client wrappers ────────────────────────────────────────

    def _wikipedia_direct(self, query: str) -> list[RetrievalSource]:
        """Direct Wikipedia REST API — no external library needed."""
        sources = []
        kw = self._extract_keywords(query)

        # Try keyword search first (fastest, most reliable for long queries)
        search_terms = kw if kw else query
        q = urllib.parse.quote(search_terms)
        search_url = (f"https://en.wikipedia.org/w/api.php"
                      f"?action=query&list=search&srsearch={q}"
                      f"&format=json&srlimit=3")
        data = self._wiki_fetch(search_url)
        if data:
            for item in data.get("query", {}).get("search", []):
                title = item.get("title", "")
                snippet = item.get("snippet", "").replace("<span class=\"searchmatch\">", "").replace("</span>", "")
                page_url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
                sources.append(RetrievalSource(
                    url=page_url,
                    title=title,
                    snippet=snippet[:500],
                    source="wikipedia",
                    score=0.80,
                ))

        # Try summary endpoint for exact match (best quality)
        if not sources:
            slug = urllib.parse.quote(query.replace(" ", "_"))
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}"
            data = self._wiki_fetch(url)
            if data:
                extract = data.get("extract", "")
                if extract and len(extract) > 50:
                    page_url = (data.get("content_urls", {})
                                .get("desktop", {}).get("page", url))
                    sources.append(RetrievalSource(
                        url=page_url,
                        title=data.get("title", "Wikipedia"),
                        snippet=extract[:1000],
                        source="wikipedia",
                        score=0.90,
                    ))

        return sources

    def _wikipedia_client(self, query: str) -> list[RetrievalSource]:
        """Use existing wiki_client.py if available."""
        try:
            self._wiki_rate_limit()
            from retrieval.wiki_client import search
            results = search(query)
            # Fallback: try keywords if full query returns empty
            if not results:
                kw = self._extract_keywords(query)
                if kw and kw != query.lower():
                    self._wiki_rate_limit()
                    results = search(kw)
            if not results:
                return []
            if isinstance(results, list):
                return [RetrievalSource(**r) if isinstance(r, dict) else
                        RetrievalSource(url=str(r)) for r in results]
            if isinstance(results, dict):
                return [RetrievalSource(**results)]
        except Exception:
            pass
        return []

    def _arxiv_client(self, query: str) -> list[RetrievalSource]:
        """arXiv search — great for science and math."""
        try:
            from retrieval.arxiv_client import search
            results = search(query)
            if not results:
                return []
            r = results if isinstance(results, list) else [results]
            return [RetrievalSource(**(item if isinstance(item, dict) else {"url": str(item), "source": "arxiv"}))
                    for item in r]
        except Exception:
            pass

        # Direct arXiv API fallback
        try:
            q = urllib.parse.quote(query)
            url = f"https://export.arxiv.org/api/query?search_query=all:{q}&max_results=3"
            req = urllib.request.Request(url, headers={"User-Agent": "VELYNX/1.0"})
            with urllib.request.urlopen(req, timeout=6) as r:
                content = r.read().decode("utf-8")
                sources = []
                entries = re.findall(r"<entry>(.*?)</entry>", content, re.DOTALL)
                for entry in entries[:3]:
                    title_m = re.search(r"<title>(.*?)</title>", entry, re.DOTALL)
                    summ_m = re.search(r"<summary>(.*?)</summary>", entry, re.DOTALL)
                    id_m = re.search(r"<id>(.*?)</id>", entry)
                    if title_m and summ_m:
                        sources.append(RetrievalSource(
                            url=id_m.group(1).strip() if id_m else "",
                            title=title_m.group(1).strip(),
                            snippet=summ_m.group(1).strip()[:500],
                            source="arxiv",
                            score=0.70,
                        ))
                return sources
        except Exception:
            pass
        return []

    def _duckduckgo_client(self, query: str) -> list[RetrievalSource]:
        """DuckDuckGo — free general web search."""
        try:
            from retrieval.duckduckgo_client import search
            results = search(query)
            if not results:
                return []
            r = results if isinstance(results, list) else [results]
            return [RetrievalSource(**(item if isinstance(item, dict) else {"url": str(item), "source": "duckduckgo"}))
                    for item in r]
        except Exception:
            pass
        return []

    def _searxng_client(self, query: str) -> list[RetrievalSource]:
        """SearXNG — only if configured."""
        searxng_url = os.getenv("SEARXNG_BASE_URL", "").strip()
        if not searxng_url:
            return []
        try:
            from retrieval.searxng_client import search
            results = search(query)
            if not results:
                return []
            r = results if isinstance(results, list) else [results]
            return [RetrievalSource(**(item if isinstance(item, dict) else {"url": str(item), "source": "searxng"}))
                    for item in r]
        except Exception:
            pass
        return []

    def _brave_client(self, query: str) -> list[RetrievalSource]:
        """Brave Search — only if API key is set."""
        if not os.getenv("BRAVE_SEARCH_API_KEY", "").strip():
            return []
        try:
            from retrieval.brave_client import search
            results = search(query)
            if not results:
                return []
            r = results if isinstance(results, list) else [results]
            return [RetrievalSource(**(item if isinstance(item, dict) else {"url": str(item), "source": "brave"}))
                    for item in r]
        except Exception:
            pass
        return []

    def _tavily_client(self, query: str) -> list[RetrievalSource]:
        """Tavily — only if API key is set."""
        if not os.getenv("TAVILY_API_KEY", "").strip():
            return []
        try:
            from retrieval.tavily_client import search
            results = search(query)
            if not results:
                return []
            r = results if isinstance(results, list) else [results]
            return [RetrievalSource(**(item if isinstance(item, dict) else {"url": str(item), "source": "tavily"}))
                    for item in r]
        except Exception:
            pass
        return []


# Module-level singleton
unified_retriever = UnifiedRetriever()
