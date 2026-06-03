"""
VELYNX Proactive Cognition Engine — Phase 20
=============================================
VELYNX thinks without being asked.

Every 5 minutes while idle:
1. Scans knowledge graph for gaps and weak nodes
2. Identifies connected concepts not yet learned
3. Proactively retrieves and learns them
4. Strengthens low-confidence nodes with new sources
5. Resolves contradictions between stored beliefs
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import random
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger("velynx.proactive")

_DATA_DIR = Path(os.getenv("VELYNX_DATA_DIR", ".")) / "velynx_data" / "proactive"
_DATA_DIR.mkdir(parents=True, exist_ok=True)
_LOG_FILE = _DATA_DIR / "cognition_log.json"
_STATE_FILE = _DATA_DIR / "proactive_state.json"


@dataclass
class CognitionEvent:
    event_type: str
    concept: str
    result: str
    confidence_before: float
    confidence_after: float
    sources_found: int
    timestamp: float = field(default_factory=time.time)
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ProactiveState:
    total_events: int = 0
    gaps_filled: int = 0
    nodes_strengthened: int = 0
    contradictions_resolved: int = 0
    curiosity_explorations: int = 0
    last_run: float = 0.0
    session_start: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "ProactiveState":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


class ProactiveCognitionEngine:
    """VELYNX's autonomous thinking process."""

    def __init__(
        self,
        interval_seconds: float = 300,
        max_per_cycle: int = 5,
        min_confidence_threshold: float = 0.6,
    ):
        self.interval = interval_seconds
        self.max_per_cycle = max_per_cycle
        self.min_conf = min_confidence_threshold
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._state = ProactiveState()
        self._event_log: list[CognitionEvent] = []
        self._load_state()

    async def start(self, interval_override: Optional[float] = None):
        if self._running:
            return
        if interval_override:
            self.interval = interval_override
        self._running = True
        self._task = asyncio.create_task(self._cognition_loop())
        logger.info("Proactive cognition started — cycle every %.0fs", self.interval)

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._save_state()
        logger.info("Proactive cognition stopped — %d total events", self._state.total_events)

    async def run_once(self) -> list[CognitionEvent]:
        return await self._run_cycle()

    async def _cognition_loop(self):
        await asyncio.sleep(30)
        while self._running:
            try:
                events = await self._run_cycle()
                if events:
                    logger.info("Proactive cycle — %d events", len(events))
                self._state.last_run = time.time()
                self._save_state()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug("Proactive cycle error: %s", e)
            await asyncio.sleep(self.interval)

    async def _run_cycle(self) -> list[CognitionEvent]:
        events: list[CognitionEvent] = []

        gap_events = await self._fill_gaps()
        events.extend(gap_events)

        if len(events) < self.max_per_cycle:
            strengthen_events = await self._strengthen_weak_nodes()
            events.extend(strengthen_events)

        if len(events) < self.max_per_cycle:
            contradiction_events = await self._resolve_contradictions()
            events.extend(contradiction_events)

        remaining = self.max_per_cycle - len(events)
        if remaining > 0:
            curiosity_events = await self._curiosity_exploration(remaining)
            events.extend(curiosity_events)

        self._record_events(events)
        return events

    async def _fill_gaps(self) -> list[CognitionEvent]:
        events = []
        try:
            from learning.continuous_learner import continuous_learner
            for _ in range(min(2, self.max_per_cycle)):
                gap = continuous_learner.get_next_to_learn()
                if not gap:
                    break
                concept = self._extract_concept_from_gap(gap)
                if not concept or len(concept) < 4:
                    continue
                # Skip stop words and garbage entries
                stop = {"system", "When", "Most", "without", "Disney", "Star Trek", "Recent", "Here"}
                if concept in stop or concept.lower() in {"what", "how", "why", "when", "where"}:
                    continue
                logger.info("Proactive: filling gap '%s'", concept[:40])
                event = await self._learn_concept(concept, "gap_filled")
                if event:
                    events.append(event)
                    self._state.gaps_filled += 1
                    await asyncio.sleep(2)
        except (ImportError, Exception) as e:
            logger.debug("Gap filling error: %s", e)
        return events

    async def _strengthen_weak_nodes(self) -> list[CognitionEvent]:
        events = []
        try:
            from memory.knowledge_graph import knowledge_graph
            # Lower thresholds: find nodes that could benefit from more sources
            weak_nodes = [
                node for node in knowledge_graph._nodes.values()
                if node.effective_confidence < 0.80
                and node.source_count < 5
            ]
            weak_nodes.sort(key=lambda n: n.effective_confidence)
            logger.info("Proactive: found %d weak nodes to strengthen", len(weak_nodes))
            for node in weak_nodes[:2]:
                event = await self._learn_concept(node.concept, "node_strengthened")
                if event:
                    events.append(event)
                    self._state.nodes_strengthened += 1
                    await asyncio.sleep(2)
        except (ImportError, Exception) as e:
            logger.debug("Node strengthening error: %s", e)
        return events

    async def _resolve_contradictions(self) -> list[CognitionEvent]:
        events = []
        try:
            from memory.knowledge_graph import knowledge_graph
            contradicted = [
                node for node in knowledge_graph._nodes.values()
                if node.contradictions and len(node.contradictions) > 0
            ]
            for node in contradicted[:1]:
                event = await self._learn_concept(node.concept, "contradiction_resolved", force_refresh=True)
                if event:
                    if event.confidence_after > 0.7:
                        node.contradictions.clear()
                        knowledge_graph._save()
                    events.append(event)
                    self._state.contradictions_resolved += 1
        except (ImportError, Exception) as e:
            logger.debug("Contradiction resolution error: %s", e)
        return events

    async def _curiosity_exploration(self, budget: int) -> list[CognitionEvent]:
        events = []
        try:
            from memory.knowledge_graph import knowledge_graph
            if not knowledge_graph._nodes:
                return events
            strong_nodes = [
                node for node in knowledge_graph._nodes.values()
                if node.effective_confidence > 0.7
            ]
            if not strong_nodes:
                return events
            weights = [n.query_count + 1 for n in strong_nodes]
            total = sum(weights)
            probs = [w / total for w in weights]
            seed_node = random.choices(strong_nodes, weights=probs, k=1)[0]
            unknown_connected = [
                concept for concept in seed_node.connected_concepts
                if not knowledge_graph.lookup(concept)
            ]
            for concept in unknown_connected[:budget]:
                logger.info("Curiosity: exploring '%s'", concept[:40])
                event = await self._learn_concept(concept, "curiosity")
                if event:
                    events.append(event)
                    self._state.curiosity_explorations += 1
                    await asyncio.sleep(3)
        except (ImportError, Exception) as e:
            logger.debug("Curiosity exploration error: %s", e)
        return events

    async def _learn_concept(self, concept: str, event_type: str, force_refresh: bool = False) -> Optional[CognitionEvent]:
        conf_before = 0.0
        try:
            from memory.knowledge_graph import knowledge_graph
            existing = knowledge_graph.lookup(concept)
            if existing:
                conf_before = existing.effective_confidence
                if not force_refresh and conf_before > 0.85:
                    return None

            sources = await self._retrieve(concept)
            if not sources:
                return CognitionEvent(event_type=event_type, concept=concept, result="failed",
                    confidence_before=conf_before, confidence_after=conf_before, sources_found=0, notes="No sources found")

            answer = self._synthesize_answer(concept, sources)
            if not answer:
                return None

            confidence = "PROBABLE" if len(sources) >= 2 else "LOW"
            node = knowledge_graph.integrate(
                query=concept, sources=sources, answer=answer,
                confidence=confidence, tags=["proactive", event_type],
            )
            try:
                from learning.continuous_learner import continuous_learner
                await continuous_learner.learn_from_query(
                    query=concept, sources=sources, answer=answer,
                    confidence=confidence, tags=["proactive", event_type],
                )
            except Exception:
                pass

            return CognitionEvent(event_type=event_type, concept=concept, result="learned",
                confidence_before=conf_before, confidence_after=node.effective_confidence,
                sources_found=len(sources), notes=f"domain={node.domain}")
        except Exception as e:
            logger.debug("Proactive learning failed for %r: %s", concept, e)
            return CognitionEvent(event_type=event_type, concept=concept, result="failed",
                confidence_before=conf_before, confidence_after=conf_before, sources_found=0, notes=str(e)[:100])

    async def _retrieve(self, concept: str) -> list[dict]:
        try:
            from retrieval.unified_retriever import unified_retriever
            report = await asyncio.wait_for(unified_retriever.retrieve(concept), timeout=15.0)
            return report.source_dicts
        except asyncio.TimeoutError:
            return []
        except ImportError:
            return await self._wikipedia_direct(concept)
        except Exception:
            return []

    async def _wikipedia_direct(self, concept: str) -> list[dict]:
        import urllib.parse, urllib.request, json as _json
        try:
            slug = urllib.parse.quote(concept.replace(" ", "_"))
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}"
            req = urllib.request.Request(url, headers={"User-Agent": "VELYNX/1.0"})
            def _fetch():
                with urllib.request.urlopen(req, timeout=8) as r:
                    return _json.loads(r.read())
            data = await asyncio.to_thread(_fetch)
            extract = data.get("extract", "")
            if extract and len(extract) > 50:
                return [{"url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                    "title": data.get("title", concept), "snippet": extract[:800],
                    "source": "wikipedia", "score": 0.85}]
        except Exception:
            pass
        return []

    def _synthesize_answer(self, concept: str, sources: list[dict]) -> str:
        import html, re
        texts = []
        for s in sources:
            text = s.get("snippet") or s.get("content") or ""
            if text and len(text) > 30:
                texts.append(text[:400])
        if not texts:
            return ""
        combined = " ".join(texts[:2])
        combined = html.unescape(combined)
        combined = re.sub(r"<[^>]+>", "", combined)
        combined = re.sub(r"\s+", " ", combined)
        return combined[:800].strip()

    def _extract_concept_from_gap(self, gap: str) -> str:
        import re
        match = re.search(r"'([^']+)'", gap)
        if match:
            return match.group(1)
        return gap[:60]

    def _record_events(self, events: list[CognitionEvent]):
        self._event_log.extend(events)
        self._event_log = self._event_log[-200:]
        self._state.total_events += len(events)
        try:
            existing = []
            if _LOG_FILE.exists():
                existing = json.loads(_LOG_FILE.read_text())
            existing.extend([e.to_dict() for e in events])
            existing = existing[-500:]
            _LOG_FILE.write_text(json.dumps(existing, indent=2))
        except Exception:
            pass

    def _save_state(self):
        try:
            _STATE_FILE.write_text(json.dumps(self._state.to_dict(), indent=2))
        except Exception:
            pass

    def _load_state(self):
        try:
            if _STATE_FILE.exists():
                self._state = ProactiveState.from_dict(json.loads(_STATE_FILE.read_text()))
        except Exception:
            pass

    def get_status(self) -> dict:
        recent = self._event_log[-10:]
        return {
            "running": self._running,
            "interval_seconds": self.interval,
            "total_events": self._state.total_events,
            "gaps_filled": self._state.gaps_filled,
            "nodes_strengthened": self._state.nodes_strengthened,
            "contradictions_resolved": self._state.contradictions_resolved,
            "curiosity_explorations": self._state.curiosity_explorations,
            "last_run": self._state.last_run,
            "recent_events": [
                {"type": e.event_type, "concept": e.concept[:40], "result": e.result,
                 "conf": f"{e.confidence_before:.0%}→{e.confidence_after:.0%}"}
                for e in recent
            ],
        }


# Module singleton
proactive_cognition = ProactiveCognitionEngine(
    interval_seconds=300,
    max_per_cycle=5,
    min_confidence_threshold=0.60,
)

if __name__ == "__main__":
    async def run_manual():
        print("\nVELYNX Proactive Cognition — Manual Cycle\n")
        engine = ProactiveCognitionEngine(interval_seconds=300, max_per_cycle=5)
        t0 = time.time()
        events = await engine.run_once()
        elapsed = time.time() - t0
        print(f"Completed in {elapsed:.1f}s — {len(events)} events:\n")
        for e in events:
            icon = "✓" if e.result == "learned" else "✗"
            print(f"  {icon} [{e.event_type}] {e.concept[:45]}")
            print(f"    Confidence: {e.confidence_before:.0%} → {e.confidence_after:.0%}")
            print(f"    Sources: {e.sources_found}")
        print(engine.get_status())
    asyncio.run(run_manual())
