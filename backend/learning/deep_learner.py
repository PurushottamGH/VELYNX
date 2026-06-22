"""
VELYNX Deep Learner v2 — MEMORY-ONLY MODE
==========================================
LLM-dependent methods have been removed. This module is structurally preserved
for backward compatibility but never calls an external LLM.

All deep learning and gap-filling methods return 0 (no new nodes), ensuring the
system never falls through to an LLM for concept extraction or summary generation.
"""

import asyncio
import hashlib
import json
import re
import time
from dataclasses import dataclass, field
from typing import Any

import httpx
from bs4 import BeautifulSoup

RELATION_TYPES = [
    "CAUSES", "IS_TYPE_OF", "ENABLES", "CONTRASTS_WITH",
    "DEFINED_AS", "PART_OF", "REQUIRES", "PRODUCES",
    "EXAMPLE_OF", "SIMILAR_TO",
]

BLACKLIST_DOMAINS = ["facebook.com", "twitter.com", "reddit.com", "instagram.com"]


@dataclass
class ConceptTriple:
    subject: str
    relation: str
    obj: str
    confidence: float = 0.8
    source: str = ""


@dataclass
class LearningResult:
    topic: str
    triples: list[ConceptTriple] = field(default_factory=list)
    nodes_added: int = 0
    sources: list[str] = field(default_factory=list)
    duration_s: float = 0.0
    error: str = ""


class DeepLearner:
    """
    Memory-only deep learner. All LLM-dependent methods have been nuked.

    deep_learn()   → returns 0 (no LLM to extract triples)
    fill_gap()     → returns 0 (no LLM to bootstrap knowledge)
    Web fetching methods are preserved for potential symbolic extraction use.
    """

    SOURCE_LIMIT = 3
    TRIPLE_LIMIT = 30
    CHUNK_SIZE   = 2000

    def __init__(self, kg, vs):
        self.kg = kg
        self.vs = vs

    # ------------------------------------------------------------------ #
    #  Public API (both return 0 — no LLM available)                       #
    # ------------------------------------------------------------------ #

    async def deep_learn(self, topic: str) -> int:
        """LLM-free: returns 0. No external model to extract triples."""
        return 0

    async def fill_gap(self, query: str) -> int:
        """LLM-free: returns 0. No external model to bootstrap knowledge."""
        return 0

    # ------------------------------------------------------------------ #
    #  Source fetching (pure text retrieval, no LLM)                       #
    # ------------------------------------------------------------------ #

    async def _fetch_sources(self, topic: str) -> list[tuple[str, str]]:
        results = []
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            wiki_text = await self._fetch_wikipedia(client, topic)
            if wiki_text:
                results.append((wiki_text, f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"))
            web_texts = await self._fetch_duckduckgo(client, topic, limit=2)
            results.extend(web_texts)
        return results[:self.SOURCE_LIMIT]

    async def _fetch_wikipedia(self, client: httpx.AsyncClient, topic: str) -> str:
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic.replace(' ', '_')}"
            r = await client.get(url, headers={"User-Agent": "VELYNX/2.0"})
            if r.status_code == 200:
                data = r.json()
                extract = data.get("extract", "")
                url2 = f"https://en.wikipedia.org/w/api.php?action=query&titles={topic.replace(' ', '_')}&prop=extracts&exintro=1&format=json"
                r2 = await client.get(url2, headers={"User-Agent": "VELYNX/2.0"})
                if r2.status_code == 200:
                    pages = r2.json().get("query", {}).get("pages", {})
                    for page in pages.values():
                        raw_html = page.get("extract", "")
                        soup = BeautifulSoup(raw_html, "html.parser")
                        extract += "\n" + soup.get_text()
                return extract[:self.CHUNK_SIZE * 2]
        except Exception as e:
            print(f"[DeepLearner] Wikipedia fetch failed: {e}")
        return ""

    async def _fetch_duckduckgo(self, client: httpx.AsyncClient, topic: str, limit: int = 2) -> list[tuple[str, str]]:
        results = []
        try:
            from ddgs import DDGS
            with DDGS() as ddgs:
                hits = list(ddgs.text(topic + " explained", max_results=limit + 2))
            for hit in hits:
                url = hit.get("href", "")
                if any(bad in url for bad in BLACKLIST_DOMAINS):
                    continue
                try:
                    r = await client.get(url, headers={"User-Agent": "VELYNX/2.0"}, timeout=10.0)
                    if r.status_code == 200:
                        soup = BeautifulSoup(r.text, "html.parser")
                        for tag in soup(["nav", "footer", "script", "style", "aside"]):
                            tag.decompose()
                        text = soup.get_text(separator="\n", strip=True)
                        text = re.sub(r"\n{3,}", "\n\n", text)
                        if len(text) > 200:
                            results.append((text[:self.CHUNK_SIZE], url))
                except Exception:
                    continue
                if len(results) >= limit:
                    break
        except Exception as e:
            print(f"[DeepLearner] DDG fetch failed: {e}")
        return results

    # ------------------------------------------------------------------ #
    #  Deduplication                                                       #
    # ------------------------------------------------------------------ #

    def _deduplicate(self, triples: list[ConceptTriple]) -> list[ConceptTriple]:
        seen = set()
        unique = []
        for t in triples:
            key = hashlib.md5(f"{t.subject}|{t.relation}|{t.obj}".encode()).hexdigest()
            if key not in seen:
                seen.add(key)
                unique.append(t)
        return unique