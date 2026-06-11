"""
VELYNX Night Learner
====================
Background asyncio loop that runs scheduled learning jobs:

Every 30 minutes:
  - Call knowledge_graph.get_gaps()
  - For each gap call deep_learner.deep_learn(gap)
  - Log result to backend/velynx_data/learning_log.json

Every 2 hours:
  - Scan KG nodes with confidence < 0.4
  - Re-learn those topics
  - Update nodes

Every night at 2am:
  - Prune KG nodes with confidence < 0.2 and query_count == 0
  - Log pruned count

Start with: asyncio.create_task(night_learner.start())
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path

from backend.memory.knowledge_graph import KnowledgeGraph
from backend.memory.vector_store import VectorStore
from backend.learning.deep_learner import DeepLearner

logger = logging.getLogger("velynx.night_learner")

_DATA_DIR = Path(os.getenv("VELYNX_DATA_DIR", ".")) / "velynx_data"
_DATA_DIR.mkdir(parents=True, exist_ok=True)
_LEARNING_LOG = _DATA_DIR / "learning_log.json"


class NightLearner:
    def __init__(self):
        self.kg = KnowledgeGraph()
        self.vs = VectorStore()
        self.dl = DeepLearner(self.kg, self.vs)
        self._tasks: list[asyncio.Task] = []

    # ── logging helpers ──────────────────────────────────────────────

    def _load_log(self) -> list[dict]:
        if _LEARNING_LOG.exists():
            return json.loads(_LEARNING_LOG.read_text(encoding="utf-8"))
        return []

    def _write_log(self, entries: list[dict]) -> None:
        _LEARNING_LOG.write_text(json.dumps(entries, indent=2), encoding="utf-8")

    def _append_entry(self, entry: dict) -> None:
        data = self._load_log()
        data.append(entry)
        self._write_log(data)

    # ── job: gap learning (every 30 min) ─────────────────────────────

    async def _learn_gaps(self) -> None:
        try:
            gaps = self.kg.get_gaps()
            if not gaps:
                logger.debug("No gaps found")
                return

            logger.info("Found %d gap(s) to learn", len(gaps))
            for gap in gaps:
                topic = gap.split("'")[1] if "'" in gap else gap
                try:
                    result = await self.dl.deep_learn(topic)
                    self._append_entry({
                        "timestamp": datetime.now().isoformat(),
                        "job": "gap_learning",
                        "topic": topic,
                        "gap_description": gap,
                        "triples_learned": result,
                        "status": "success" if result > 0 else "empty",
                    })
                    logger.info("Learned '%s': +%d triples", topic, result)
                except Exception as e:
                    logger.error("deep_learn failed for '%s': %s", topic, e)
                    self._append_entry({
                        "timestamp": datetime.now().isoformat(),
                        "job": "gap_learning",
                        "topic": topic,
                        "error": str(e),
                        "status": "error",
                    })
        except Exception as e:
            logger.error("_learn_gaps error: %s", e)

    # ── job: low-confidence re-learn (every 2 hours) ─────────────────

    async def _relearn_low_confidence(self) -> None:
        try:
            nodes = self.kg.get_low_confidence_nodes(threshold=0.4)
            if not nodes:
                logger.debug("No low-confidence nodes found")
                return

            logger.info("Re-learning %d low-confidence topic(s)", len(nodes))
            for topic, conf in nodes:
                try:
                    result = await self.dl.deep_learn(topic)
                    self._append_entry({
                        "timestamp": datetime.now().isoformat(),
                        "job": "relearn",
                        "topic": topic,
                        "previous_confidence": round(conf, 3),
                        "triples_learned": result,
                        "status": "success" if result > 0 else "empty",
                    })
                    logger.info("Re-learned '%s' (was %.0f%%): +%d triples", topic, conf * 100, result)
                except Exception as e:
                    logger.error("relearn failed for '%s': %s", topic, e)
                    self._append_entry({
                        "timestamp": datetime.now().isoformat(),
                        "job": "relearn",
                        "topic": topic,
                        "error": str(e),
                        "status": "error",
                    })
        except Exception as e:
            logger.error("_relearn_low_confidence error: %s", e)

    # ── job: nightly prune (2am) ─────────────────────────────────────

    async def _prune(self) -> None:
        try:
            removed = self.kg.prune_low_value_nodes(confidence_threshold=0.2)
            self._append_entry({
                "timestamp": datetime.now().isoformat(),
                "job": "prune",
                "nodes_pruned": removed,
                "status": "success",
            })
            logger.info("Pruned %d low-value node(s)", removed)
        except Exception as e:
            logger.error("_prune error: %s", e)

    # ── scheduler ────────────────────────────────────────────────────

    async def start(self) -> None:
        logger.info("Night learner started — gap_learn=30m, relearn=2h, prune=2am")
        last_gap = 0.0
        last_relearn = 0.0

        while True:
            now = time.time()

            if now - last_gap >= 30 * 60:
                logger.debug("Running gap learning job")
                await self._learn_gaps()
                last_gap = now

            if now - last_relearn >= 2 * 60 * 60:
                logger.debug("Running re-learn job")
                await self._relearn_low_confidence()
                last_relearn = now

            # Check for 2am nightly prune
            dt = datetime.now()
            if dt.hour == 2 and dt.minute < 5:
                # Guard: only prune once per night
                today_key = dt.strftime("%Y-%m-%d")
                last_prune_key = getattr(self, "_last_prune_key", "")
                if last_prune_key != today_key:
                    logger.debug("Running nightly prune job")
                    await self._prune()
                    self._last_prune_key = today_key

            await asyncio.sleep(60)  # check every 60 seconds

    def stop(self) -> None:
        for task in self._tasks:
            task.cancel()


night_learner = NightLearner()
