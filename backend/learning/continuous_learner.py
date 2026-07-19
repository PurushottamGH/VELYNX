"""
VELYNX Continuous Learning Loop — Phase 14
============================================
Every query makes VELYNX smarter.
This module closes the learning loop:

  Query → Answer → Integrate into Knowledge Graph
  → Discover gaps → Schedule follow-up learning
  → VELYNX improves continuously

Usage:
    from learning.continuous_learner import continuous_learner
    await continuous_learner.learn_from_query(query, sources, answer, confidence)
    report = continuous_learner.get_learning_report()
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger("velynx.continuous_learner")

_DATA_DIR = Path(os.getenv("VELYNX_DATA_DIR", ".")) / "velynx_data" / "learning"
_DATA_DIR.mkdir(parents=True, exist_ok=True)
_STATS_FILE = _DATA_DIR / "learning_stats.json"
_QUEUE_FILE = _DATA_DIR / "learning_queue.json"


@dataclass
class LearningEvent:
    query: str
    answer_length: int
    confidence: str
    source_count: int
    domain: str
    graph_node_created: bool
    graph_node_updated: bool
    gaps_found: list[str]
    timestamp: float = field(default_factory=time.time)


@dataclass
class LearningStats:
    total_queries: int = 0
    total_concepts_learned: int = 0
    total_concepts_updated: int = 0
    domains_covered: dict = field(default_factory=dict)
    avg_confidence: float = 0.0
    learning_rate: float = 0.0  # concepts per hour
    session_start: float = field(default_factory=time.time)
    gaps_queue_size: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "LearningStats":
        return cls(**d)


class ContinuousLearner:
    """
    Closes the learning loop for VELYNX.
    Integrates every query result into the knowledge graph
    and maintains a queue of gaps to fill.
    """

    def __init__(self):
        self._stats = LearningStats()
        self._gap_queue: list[str] = []  # Concepts VELYNX should learn next
        self._recent_events: list[LearningEvent] = []
        self._load()

    async def learn_from_query(
        self,
        query: str,
        sources: list[dict],
        answer: str,
        confidence: str = "UNKNOWN",
        tags: list[str] | None = None,
    ) -> LearningEvent:
        """
        Main learning entry point.
        Call this after every successful query.
        """
        # Integrate into knowledge graph
        node_created = False
        node_updated = False
        gaps: list[str] = []
        domain = "general"

        try:
            from memory.knowledge_graph import knowledge_graph

            # Quality gate: reject bad answers before storing
            _OFF_TOPIC = ["mars", "nasa", "disney", "monty python", "observatoire",
                          "spacecraft", "animated series", "television series"]
            answer_lower = answer.lower()
            if any(sig in answer_lower for sig in _OFF_TOPIC):
                logger.warning("Rejected off-topic answer for KG: %r", answer[:60])
                return LearningEvent(
                    query=query, answer_length=len(answer), confidence=confidence,
                    source_count=len(sources), domain="general",
                    graph_node_created=False, graph_node_updated=False, gaps=[],
                )
            if len(answer) < 30:
                logger.warning("Rejected too-short answer for KG: %d chars", len(answer))
                return LearningEvent(
                    query=query, answer_length=len(answer), confidence=confidence,
                    source_count=len(sources), domain="general",
                    graph_node_created=False, graph_node_updated=False, gaps=[],
                )

            # Check if this is new knowledge or an update
            existing = knowledge_graph.lookup(query)
            node_created = existing is None

            node = knowledge_graph.integrate(
                query=query,
                sources=sources,
                answer=answer,
                confidence=confidence,
                tags=tags or [],
            )
            domain = node.domain
            node_updated = not node_created

            # Find knowledge gaps
            gaps = knowledge_graph.get_gaps(query)

            # Add gaps to learning queue
            for gap in gaps:
                if gap not in self._gap_queue:
                    self._gap_queue.append(gap)

            # Trim queue (keep most recent 100)
            self._gap_queue = self._gap_queue[-100:]

        except Exception as e:
            logger.debug("Knowledge graph integration failed: %s", e)

        # Record learning event
        event = LearningEvent(
            query=query,
            answer_length=len(answer),
            confidence=confidence,
            source_count=len(sources),
            domain=domain,
            graph_node_created=node_created,
            graph_node_updated=node_updated,
            gaps_found=gaps,
        )
        self._recent_events.append(event)
        self._recent_events = self._recent_events[-50:]  # Keep last 50

        # Update stats
        self._update_stats(event)
        self._save()

        logger.debug("Learning event: query=%r, new=%s, domain=%s, gaps=%d",
                     query[:50], node_created, domain, len(gaps))

        return event

    def get_next_to_learn(self) -> Optional[str]:
        """Get the next gap concept VELYNX should proactively learn."""
        if self._gap_queue:
            return self._gap_queue.pop(0)
        return None

    def get_learning_report(self) -> dict:
        """Get comprehensive learning report."""
        session_hours = (time.time() - self._stats.session_start) / 3600
        rate = (self._stats.total_concepts_learned / max(0.01, session_hours))

        try:
            from memory.knowledge_graph import knowledge_graph
            graph_stats = knowledge_graph.stats()
        except Exception:
            graph_stats = {}

        return {
            "session": {
                "total_queries": self._stats.total_queries,
                "new_concepts_learned": self._stats.total_concepts_learned,
                "concepts_updated": self._stats.total_concepts_updated,
                "learning_rate_per_hour": round(rate, 2),
                "session_hours": round(session_hours, 2),
            },
            "knowledge_graph": graph_stats,
            "domains_covered": self._stats.domains_covered,
            "gaps_queue_size": len(self._gap_queue),
            "next_to_learn": self._gap_queue[:5] if self._gap_queue else [],
            "avg_confidence": round(self._stats.avg_confidence, 3),
        }

    def get_improvement_delta(self) -> str:
        """Human-readable description of how much VELYNX has learned this session."""
        n = self._stats.total_concepts_learned
        u = self._stats.total_concepts_updated
        q = self._stats.total_queries

        if q == 0:
            return "No queries processed yet"

        parts = []
        if n > 0:
            parts.append(f"learned {n} new concept{'s' if n != 1 else ''}")
        if u > 0:
            parts.append(f"deepened {u} existing concept{'s' if u != 1 else ''}")
        if self._gap_queue:
            parts.append(f"{len(self._gap_queue)} gaps identified for future learning")

        return f"After {q} queries: " + (", ".join(parts) if parts else "building knowledge base")

    # ── Internal ──────────────────────────────────────────────────────────

    def _update_stats(self, event: LearningEvent):
        self._stats.total_queries += 1
        if event.graph_node_created:
            self._stats.total_concepts_learned += 1
        if event.graph_node_updated:
            self._stats.total_concepts_updated += 1

        domain = event.domain
        self._stats.domains_covered[domain] = (
            self._stats.domains_covered.get(domain, 0) + 1
        )

        conf_map = {"CERTAIN": 1.0, "PROBABLE": 0.75, "DEBATED": 0.5, "LOW": 0.25, "UNKNOWN": 0.1}
        conf_val = conf_map.get(event.confidence.upper(), 0.1)

        # Running average confidence
        n = self._stats.total_queries
        self._stats.avg_confidence = (
            (self._stats.avg_confidence * (n - 1) + conf_val) / n
        )
        self._stats.gaps_queue_size = len(self._gap_queue)

    def _save(self):
        try:
            _STATS_FILE.write_text(json.dumps(self._stats.to_dict(), indent=2))
            _QUEUE_FILE.write_text(json.dumps(self._gap_queue, indent=2))
        except Exception as e:
            logger.debug("Learning stats save failed: %s", e)

    def _load(self):
        try:
            if _STATS_FILE.exists():
                self._stats = LearningStats.from_dict(
                    json.loads(_STATS_FILE.read_text())
                )
            if _QUEUE_FILE.exists():
                self._gap_queue = json.loads(_QUEUE_FILE.read_text())
        except Exception as e:
            logger.debug("Learning stats load failed: %s", e)


# ── Proactive Learning Runner (Phase 15 preview) ──────────────────────────────

class ProactiveLearner:
    """
    Background process that fills knowledge gaps proactively.
    Runs during idle time — doesn't block main pipeline.
    """

    def __init__(self, interval_seconds: float = 300):
        self.interval = interval_seconds
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        """Start proactive learning in background."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._learning_loop())
        logger.info("Proactive learner started (interval=%ds)", self.interval)

    async def stop(self):
        """Stop proactive learning."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Proactive learner stopped")

    async def _learning_loop(self):
        """Background loop — fills gaps when idle."""
        while self._running:
            try:
                await asyncio.sleep(self.interval)
                if not self._running:
                    break

                # --- Phase 43B: REM Sleep Cycle ---
                try:
                    from backend.soul.soul_graph import run_sleep_cycle
                    import asyncio as _asyncio

                    # Execute the pruning engine in a non-blocking thread
                    sleep_stats = await _asyncio.to_thread(run_sleep_cycle, decay_rate=0.05, prune_threshold=0.15)

                    # Log the autonomic function so the operator can monitor graph health
                    if sleep_stats.get('edges_decayed', 0) > 0 or sleep_stats.get('edges_pruned', 0) > 0:
                        print(f"[VELYNX AUTONOMIC] REM Sleep Complete: Decayed {sleep_stats['edges_decayed']} | Pruned {sleep_stats['edges_pruned']} | Forgotten {sleep_stats['concepts_forgotten']}")
                except Exception as e:
                    print(f"[VELYNX AUTONOMIC] Sleep cycle interrupted: {e}")
                # ----------------------------------

                next_concept = continuous_learner.get_next_to_learn()
                if next_concept:
                    logger.info("Proactive learning: %r", next_concept[:60])
                    await self._learn_concept(next_concept)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug("Proactive learning error: %s", e)

    async def _learn_concept(self, concept: str):
        """Learn a specific concept proactively."""
        try:
            from retrieval.unified_retriever import unified_retriever
            report = await unified_retriever.retrieve(concept)
            if report.sources:
                from pipeline.reasoning_core import reason
                result = reason(sources=report.source_dicts, query=concept)
                answer = result.get("draft", "") if isinstance(result, dict) else str(result)
                confidence = result.get("confidence", "UNKNOWN") if isinstance(result, dict) else "UNKNOWN"
                await continuous_learner.learn_from_query(
                    query=concept,
                    sources=report.source_dicts,
                    answer=answer,
                    confidence=confidence,
                    tags=["proactive", "background"],
                )
                logger.info("Proactive: learned %r", concept[:40])
        except Exception as e:
            logger.debug("Proactive learning failed for %r: %s", concept, e)


# Module-level singletons
continuous_learner = ContinuousLearner()
proactive_learner = ProactiveLearner(interval_seconds=300)
