"""
VELYNX Deep Learner v2
======================
Learns by building conceptual understanding, not just storing scraped text.

Each learned topic becomes a set of triples:
  (concept, CAUSES, effect)
  (concept, IS_TYPE_OF, category)
  (concept, ENABLES, capability)
  (concept, CONTRASTS_WITH, other)
  (concept, DEFINED_AS, definition)

These triples are stored in KnowledgeGraph and used by ReasoningEngine
to answer WHY/HOW questions without hallucinating.
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
import os
from groq import Groq as _Groq

_groq = _Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

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
    Learns a topic by:
    1. Fetching 3 high-quality sources (Wikipedia + 2 web)
    2. Extracting concept triples via LLM
    3. Deduplicating against existing KG nodes
    4. Storing to KG + vector store
    5. Generating a WHY/HOW summary stored as a special node
    """

    SOURCE_LIMIT = 3
    TRIPLE_LIMIT = 30   # per topic
    CHUNK_SIZE   = 2000 # characters per LLM extraction pass

    def __init__(self, kg, vs):
        self.kg = kg
        self.vs = vs

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    async def deep_learn(self, topic: str) -> int:
        t0 = time.perf_counter()
        result = LearningResult(topic=topic)

        try:
            # 1. Fetch sources
            texts = await self._fetch_sources(topic)
            if not texts:
                return 0

            # 2. Extract triples
            all_triples: list[ConceptTriple] = []
            for text, url in texts:
                triples = await self._extract_triples(topic, text, url)
                all_triples.extend(triples)

            # 3. Deduplicate
            unique = self._deduplicate(all_triples)

            # 4. Store
            for triple in unique[:self.TRIPLE_LIMIT]:
                await self.kg.add_triple(triple)
                await self.vs.add_concept(
                    f"{triple.subject} {triple.relation} {triple.obj}",
                    metadata={"subject": triple.subject, "relation": triple.relation,
                               "obj": triple.obj, "source": triple.source}
                )

            # 5. Generate + store WHY/HOW summary
            summary = await self._generate_summary(topic, unique)
            await self.kg.store_understanding(topic, summary)

            result.nodes_added = len(unique)
            result.triples = unique
            result.duration_s = time.perf_counter() - t0

            print(f"[DeepLearner] '{topic}': +{result.nodes_added} triples in {result.duration_s:.1f}s")
            return result.nodes_added

        except Exception as e:
            print(f"[DeepLearner] Error learning '{topic}': {e}")
            return 0

    async def fill_gap(self, query: str) -> int:
        """Called by Brain when answer confidence is too low. Learn just enough."""
        # Extract the key concepts from the query
        concepts = await self._extract_key_concepts(query)
        total = 0
        for concept in concepts[:2]:   # learn top 2 concepts
            n = await self.deep_learn(concept)
            total += n
        return total

    # ------------------------------------------------------------------ #
    #  Source fetching                                                     #
    # ------------------------------------------------------------------ #

    async def _fetch_sources(self, topic: str) -> list[tuple[str, str]]:
        results = []
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            # Always try Wikipedia first — clean, factual
            wiki_text = await self._fetch_wikipedia(client, topic)
            if wiki_text:
                results.append((wiki_text, f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"))

            # DuckDuckGo for 2 more
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
                # Also fetch the full intro
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
            from duckduckgo_search import DDGS
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
                        # strip nav, footer, ads
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
    #  Triple extraction                                                   #
    # ------------------------------------------------------------------ #

    async def _extract_triples(self, topic: str, text: str, source_url: str) -> list[ConceptTriple]:
        """Use LLM to extract structured concept triples from raw text."""
        prompt = f"""Extract concept triples from this text about "{topic}".

TEXT:
{text[:self.CHUNK_SIZE]}

Extract up to 15 factual triples. Each triple must have:
- subject: a concept (noun phrase)
- relation: one of {RELATION_TYPES}
- obj: another concept or definition

Return ONLY a JSON array. No explanation. No markdown. Example:
[
  {{"subject": "photosynthesis", "relation": "REQUIRES", "obj": "sunlight"}},
  {{"subject": "photosynthesis", "relation": "PRODUCES", "obj": "glucose"}},
  {{"subject": "chlorophyll", "relation": "ENABLES", "obj": "photosynthesis"}}
]"""

        try:
            resp = _groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=800,
            )
            raw = resp.choices[0].message.content.strip()
            raw = raw.replace("```json", "").replace("```", "").strip()
            data = json.loads(raw)
            triples = []
            for item in data:
                if isinstance(item, dict) and all(k in item for k in ["subject", "relation", "obj"]):
                    if item["relation"] in RELATION_TYPES:
                        triples.append(ConceptTriple(
                            subject=item["subject"].lower().strip(),
                            relation=item["relation"],
                            obj=item["obj"].lower().strip(),
                            source=source_url,
                        ))
            return triples
        except Exception as e:
            print(f"[DeepLearner] Triple extraction failed: {e}")
            return []

    async def _generate_summary(self, topic: str, triples: list[ConceptTriple]) -> str:
        """Generate a WHY/HOW understanding summary from triples."""
        triple_str = "\n".join(f"  {t.subject} --[{t.relation}]--> {t.obj}" for t in triples[:20])
        prompt = f"""Given these concept triples about "{topic}":

{triple_str}

Write a 3-paragraph understanding summary:
1. WHAT: What is {topic}?
2. HOW: How does it work mechanically?
3. WHY: Why does it matter? What does it enable or cause?

Be precise. No fluff. Use the triples as your factual basis."""

        try:
            resp = _groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=600,
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            return f"Learned {len(triples)} concepts about {topic}."

    async def _extract_key_concepts(self, query: str) -> list[str]:
        """Extract 2-3 key concepts to learn from a query that had low confidence."""
        prompt = f"""Extract 2-3 key concepts to learn from this query: "{query}"
Return a JSON array of strings. Example: ["neural networks", "backpropagation"]
Only the array. Nothing else."""
        try:
            resp = _groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=100,
            )
            raw = resp.choices[0].message.content.strip().replace("```json","").replace("```","")
            return json.loads(raw)
        except Exception:
            return [query.split()[0]]   # fallback: first word

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