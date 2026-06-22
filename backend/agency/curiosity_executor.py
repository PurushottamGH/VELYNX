"""
VELYNX Phase 59.1 — Curiosity Execution Loop
=============================================

Phase 59 (``backend/agency/curiosity.py``) gives VELYNX the *drive*: it scans the
Knowledge Graph and emits ``PENDING`` :class:`~backend.agency.curiosity.Goal`
objects for missing attributes. Phase 58
(``backend/pipeline/agentic_loop.py``) gives VELYNX the *means*: a symbolic
planner that decomposes a natural-language question into a multi-hop DAG and
executes it.

This module is the **wire** between drive and means — the closed curiosity
control loop::

    new knowledge consolidated
        -> CuriosityEngine.scan_for_gaps()           (generate PENDING goals)
        -> for each pending goal (priority order):
               formulate "What is the <attribute> of <entity>?"
               agentic_controller.formulate_plan(query)
               await agentic_controller.execute_plan(plan)
               success -> write attribute back to KG, mark SATISFIED
               failure -> mark BLOCKED (retry later) / ABANDONED (out of retries)

Two entry points drive it, both **non-blocking** to the user-facing event loop:

* :func:`consolidate_and_explore` — chained off the pipeline's
  fire-and-forget consolidation task, so curiosity reacts immediately whenever
  fresh knowledge lands.
* :class:`CuriosityExecutor.start` — a low-frequency background loop (started in
  the app lifespan) that drains any pending goals that accumulated between
  consolidations.

Concurrency safety
------------------
All graph mutations and plan executions happen on background tasks/threads, never
inline on a request. A single :class:`asyncio.Lock` serialises execution cycles
so the consolidation-triggered explore and the periodic loop can never run (and
write to the SQLite graph) at the same time.
"""
from __future__ import annotations

import asyncio
import logging
import re
import time
from typing import Optional

from backend.agency.curiosity import (
    Goal,
    GoalManager,
    GoalStatus,
    goal_manager,
    scan_for_gaps,
)

logger = logging.getLogger("velynx.curiosity.exec")

# Synthesis confidences we treat as a successful resolution.
_SUCCESS_CONFIDENCES = {"CERTAIN", "PROBABLE", "HIGH", "VERIFIED"}


class CuriosityExecutor:
    """Pursues PENDING curiosity goals via the Phase 58 symbolic planner."""

    def __init__(
        self,
        *,
        interval_seconds: float = 180.0,
        max_per_cycle: int = 3,
        max_attempts: int = 2,
        controller=None,
        graph=None,
        manager: Optional[GoalManager] = None,
    ) -> None:
        self.interval = interval_seconds
        self.max_per_cycle = max_per_cycle
        self.max_attempts = max_attempts
        self._controller = controller     # injectable for tests; lazy by default
        self._graph = graph               # injectable KnowledgeGraph
        self.manager = manager or goal_manager
        self._running = False
        self._task: Optional[asyncio.Task] = None
        # Serialises execution cycles (periodic loop vs. consolidation trigger).
        self._cycle_lock = asyncio.Lock()
        self._stats = {"pursued": 0, "satisfied": 0, "blocked": 0, "abandoned": 0}
        # Observability (Phase 59.2).
        self._started_at: Optional[float] = None
        self._last_run_at: Optional[float] = None
        self._last_cycle: dict = {}
        self._cycles_run = 0

    # ── Lazy dependencies ─────────────────────────────────────────────────
    def _get_controller(self):
        if self._controller is not None:
            return self._controller
        from backend.pipeline.agentic_loop import agentic_controller

        self._controller = agentic_controller
        return self._controller

    def _get_graph(self):
        if self._graph is not None:
            return self._graph
        from backend.knowledge.knowledge_graph import KnowledgeGraph

        self._graph = KnowledgeGraph()
        return self._graph

    # ── Lifecycle (mirrors proactive_cognition / night_learner) ───────────
    async def start(self, interval_override: Optional[float] = None) -> None:
        if self._running:
            return
        if interval_override:
            self.interval = interval_override
        self._running = True
        self._started_at = time.time()
        self._task = asyncio.create_task(self._loop())
        logger.info("Curiosity executor started — cycle every %.0fs", self.interval)

    async def stop(self) -> None:
        self._running = False
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Curiosity executor stopped — %s", self._stats)

    async def _loop(self) -> None:
        # Let the app finish booting before the first cycle.
        await asyncio.sleep(45)
        while self._running:
            try:
                await self.run_once()
            except asyncio.CancelledError:
                break
            except Exception as exc:  # never let the loop die
                logger.debug("Curiosity cycle error: %s", exc)
            await asyncio.sleep(self.interval)

    # ── Core cycle ────────────────────────────────────────────────────────
    async def run_once(self) -> dict:
        """Pursue up to ``max_per_cycle`` pending goals (priority order).

        Returns a small summary dict. Serialised by ``_cycle_lock`` so it never
        overlaps another cycle (avoids concurrent SQLite writers on the graph).
        """
        async with self._cycle_lock:
            pending = [
                g for g in self.manager.pending()  # already priority-sorted
            ][: self.max_per_cycle]
            if not pending:
                return self._record_cycle(
                    {"pursued": 0, "satisfied": 0, "blocked": 0, "abandoned": 0}
                )

            cycle = {"pursued": 0, "satisfied": 0, "blocked": 0, "abandoned": 0}
            for goal in pending:
                outcome = await self._pursue_goal(goal)
                cycle["pursued"] += 1
                cycle[outcome] = cycle.get(outcome, 0) + 1
            logger.info("Curiosity cycle complete: %s", cycle)
            return self._record_cycle(cycle)

    def _record_cycle(self, cycle: dict) -> dict:
        """Stamp observability metrics for the cycle that just ran."""
        self._last_run_at = time.time()
        self._last_cycle = cycle
        self._cycles_run += 1
        return cycle

    # ── Observability (Phase 59.2) ────────────────────────────────────────
    @property
    def running(self) -> bool:
        return self._running

    def get_status(self) -> dict:
        """High-level executor metrics for the ops snapshot endpoint."""
        now = time.time()
        return {
            "running": self._running,
            "cycle_active": self._cycle_lock.locked(),
            "interval_seconds": self.interval,
            "max_per_cycle": self.max_per_cycle,
            "max_attempts": self.max_attempts,
            "cycles_run": self._cycles_run,
            "started_at": self._started_at,
            "uptime_seconds": (round(now - self._started_at, 1)
                               if self._started_at else None),
            "last_run_at": self._last_run_at,
            "seconds_since_last_run": (round(now - self._last_run_at, 1)
                                       if self._last_run_at else None),
            "last_cycle": self._last_cycle or None,
            "lifetime_totals": dict(self._stats),
        }

    async def _pursue_goal(self, goal: Goal) -> str:
        """Resolve one goal end-to-end. Returns 'satisfied'|'blocked'|'abandoned'."""
        query = self._formulate_query(goal)
        self.manager.set_status(goal.id, GoalStatus.ACTIVE)
        self._stats["pursued"] += 1
        logger.info("Curiosity pursuing goal %s: %r", goal.id, query)

        controller = self._get_controller()
        success = False
        answer = ""
        try:
            from backend.pipeline.agentic_loop import PlanStatus

            plan = controller.formulate_plan(query)
            synthesis = await controller.execute_plan(plan)
            answer = (synthesis.get("answer") or "").strip()
            confidence = str(synthesis.get("confidence") or "").upper()
            success = (
                getattr(plan, "status", None) == PlanStatus.DONE
                and confidence in _SUCCESS_CONFIDENCES
            )
        except Exception as exc:
            logger.warning("Curiosity goal %s execution failed: %s", goal.id, exc)
            success = False

        if success:
            value = self._extract_value(synthesis)
            self._record_to_graph(goal, value)
            self.manager.set_status(goal.id, GoalStatus.SATISFIED)
            self._stats["satisfied"] += 1
            logger.info("Curiosity goal %s SATISFIED: %s -> %s",
                        goal.id, goal.target_attribute, value or "<no concise value>")
            return "satisfied"

        # Failure path: BLOCKED for a retry, or ABANDONED once out of attempts.
        goal.attempts += 1
        if goal.attempts >= self.max_attempts:
            self.manager.set_status(goal.id, GoalStatus.ABANDONED)
            self._stats["abandoned"] += 1
            logger.info("Curiosity goal %s ABANDONED after %d attempt(s)",
                        goal.id, goal.attempts)
            return "abandoned"

        self.manager.set_status(goal.id, GoalStatus.BLOCKED)
        self._stats["blocked"] += 1
        logger.info("Curiosity goal %s BLOCKED (attempt %d/%d)",
                    goal.id, goal.attempts, self.max_attempts)
        return "blocked"

    @staticmethod
    def _formulate_query(goal: Goal) -> str:
        """Turn a goal into a natural-language question for the planner."""
        attribute = goal.target_attribute.replace("_", " ").strip()
        entity = goal.target_entity.strip()
        return f"What is the {attribute} of {entity}?"

    # Markers that betray a planner *narrative* / debug payload rather than a
    # concise attribute value. If any appears (or the text is over-long), we
    # refuse to write it into the graph.
    _DEBUG_MARKERS = (
        "resolved via", "step plan", "[web", "[kg", "stub", "could not",
        "retrieval mesh", "no external result",
    )
    _MAX_VALUE_LEN = 80

    def _extract_value(self, synthesis: dict) -> Optional[str]:
        """Extract a CONCISE attribute value from a synthesis result.

        The planner's ``answer`` is a human-readable narrative
        ("Resolved via a 3-step plan — ... ; population: <snippet>"), NOT a value
        to store verbatim. Writing it into the graph pollutes the node space and
        breaks downstream alias/entity matching. We therefore:

          1. take the text after the final ``:`` (the planner appends
             "<attribute>: <value>"), else the whole answer;
          2. keep only the first sentence / line;
          3. reject anything that still looks like planner/debug output or is
             implausibly long.

        Returns a short value string, or ``None`` if nothing concise/clean is
        recoverable (in which case we do NOT write to the graph).
        """
        raw = (synthesis.get("answer") or "").strip()
        if not raw:
            return None
        text = raw.rsplit(":", 1)[-1] if ":" in raw else raw
        text = re.split(r"[\n.;]", text, maxsplit=1)[0]
        text = text.strip().strip("[]").strip()
        low = text.lower()
        if not text or len(text) > self._MAX_VALUE_LEN:
            return None
        if any(marker in low for marker in self._DEBUG_MARKERS):
            return None
        return text

    def _record_to_graph(self, goal: Goal, value: Optional[str]) -> None:
        """Write the resolved attribute back into the KG (closes the loop).

        Storing the attribute as a relationship ``(entity, attribute, value)``
        means a subsequent :func:`scan_for_gaps` sees the attribute as *known*
        and will not regenerate the same goal.

        IMPORTANT: only a concise, clean value is written. If extraction could
        not recover one (``value is None``), we write NOTHING — never the
        planner's narrative/debug string, which would pollute the graph.
        """
        if not value:
            logger.debug(
                "Curiosity: no concise value for goal %s (%s of %s) — skipping "
                "write-back to avoid graph pollution",
                goal.id, goal.target_attribute, goal.target_entity,
            )
            return
        try:
            graph = self._get_graph()
            graph.add_relationship(goal.target_entity, goal.target_attribute, value)
        except Exception as exc:
            logger.debug("Curiosity: KG write-back failed for goal %s: %s", goal.id, exc)
            return

        # ── Phase 61: Episodic memory ──────────────────────────────────────
        # The curiosity loop just learned a value — record a KNOWLEDGE_ACQUIRED
        # episode, causally linked (by the manager) to the GOAL_CREATED episode
        # that sought this attribute. This closes the failure -> goal -> learned
        # narrative chain. Best-effort.
        try:
            from backend.memory.episodic import episodic_manager

            episodic_manager.record_knowledge_acquired(
                goal.target_entity,
                attribute=goal.target_attribute,
                value=value,
                source="curiosity",
            )
        except Exception as exc:
            logger.debug("Episodic: knowledge-acquired logging failed for goal %s: %s",
                         goal.id, exc)

    # ── Trigger after fresh knowledge is consolidated ─────────────────────
    async def scan_and_execute(self, limit: int = 25) -> dict:
        """Scan for new gaps, then immediately pursue them (bounded)."""
        try:
            new_goals = scan_for_gaps(limit, graph=self._graph, manager=self.manager)
            logger.info("Curiosity scan after consolidation: %d new goal(s)", len(new_goals))
        except Exception as exc:
            logger.warning("Curiosity scan failed: %s", exc)
        return await self.run_once()


# Process-wide singleton.
curiosity_executor = CuriosityExecutor()


async def consolidate_and_explore(consolidate: bool = True) -> None:
    """Pipeline hook: consolidate fresh knowledge, then act on curiosity.

    Designed to be dispatched fire-and-forget
    (``asyncio.create_task(consolidate_and_explore())``) from the request path so
    it never blocks the user-facing response. It:

      1. awaits the existing async consolidation (raw triples -> active KG), then
      2. scans the now-updated graph for gaps and pursues the new goals.

    Both steps are best-effort and fully guarded; any failure is logged and
    swallowed so a background curiosity cycle can never break a user turn.
    """
    if consolidate:
        try:
            from backend.knowledge.consolidator import consolidate_pending_async

            report = await consolidate_pending_async()
            logger.debug("Curiosity trigger: consolidation report %s",
                         getattr(report, "as_dict", lambda: report)())
        except Exception as exc:
            logger.warning("Curiosity trigger: consolidation failed: %s", exc)

    try:
        await curiosity_executor.scan_and_execute()
    except Exception as exc:
        logger.warning("Curiosity trigger: scan/execute failed: %s", exc)


__all__ = [
    "CuriosityExecutor",
    "curiosity_executor",
    "consolidate_and_explore",
]
