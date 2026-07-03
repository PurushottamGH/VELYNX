"""EXP-0 detector wrappers.

Three tiers, matching the ORDER the live pipeline actually tries them
(backend/app/pipeline.py:527-529):

  Tier 1 (V2 / semantic)   -- backend.pipeline.soul_router.soul_lookup
      -> backend.cognition.scenario_engine.parse_scenario
      -> backend.soul.soul_graph.resonate  (sentence-embedding cosine
         similarity against a prebuilt index + a living_edges DB read)
      Requires: sentence-transformers model + embedding index + brain_stem.db
      with a populated living_edges table. No LLM call (see scenario_engine.py
      docstring: "No LLM call for scenario parsing. Pure local inference.").

  Tier 2 (legacy / lexical) -- backend.pipeline.soul_router.soul_lookup_legacy
      Exact substring OR Porter-stem match against the 32 concept names in
      backend/soul/concepts.json. No DB, no model, no network. Pure function.

  Tier 3 (full pipeline)   -- backend.app.pipeline.answer_question
      The end-to-end system a real user talks to. Tries Tier 1 then Tier 2
      internally, then falls through to retrieval + LLM synthesis if neither
      fires. Requires the full stack (DB, embedding model, LLM API access,
      network).

All imports of backend.*/cognition.* are LAZY (inside functions), so this
module can be imported for --dry-run / dataset inspection without the
VELYNX backend being importable.

IMPORTANT (state contamination): Tier 1's resonate() reads AND Tier 3's
pipeline can WRITE living_edges via Hebbian plasticity
(backend/soul/soul_graph.py: apply_plasticity, triggered by pipeline.py
whenever a soul concept was matched with CERTAIN/PROBABLE confidence). A
later trial's Tier-1/Tier-3 score can therefore be contaminated by an
earlier trial's side effects within the SAME run. Tier 2 has no such state
and is immune. See EXP0_PROTOCOL.md section 5 (Randomization Procedure) and
EXP0_RUNBOOK.md for the mandatory reset-before-every-trial procedure this
module assumes the CALLER (run_exp0.py) performs -- this module does not
reset state itself, so it stays a pure, testable unit.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass(frozen=True)
class DetectorResult:
    tier: str                 # "tier1_v2" | "tier2_legacy" | "tier3_full"
    query: str
    concepts_detected: list[str] = field(default_factory=list)
    confidence: str | None = None      # populated for tier3_full only
    answer_text: str | None = None     # populated for tier3_full only
    latency_seconds: float = 0.0
    error: str | None = None           # non-None if the call raised

    def hit(self, target_concept: str) -> bool:
        """Whether ``target_concept`` is among the concepts this call
        detected. This is the sole basis for every DV in EXP-0 -- no text
        parsing, no LLM judge, no researcher-set threshold."""
        return target_concept in self.concepts_detected


def tier1_v2(query: str) -> DetectorResult:
    """Call the V2 semantic soul lookup directly (no full pipeline)."""
    t0 = time.perf_counter()
    try:
        from backend.pipeline.soul_router import soul_lookup
        result = soul_lookup(query)
    except Exception as exc:  # noqa: BLE001 -- surfaced in the artifact, not swallowed
        return DetectorResult(
            tier="tier1_v2", query=query,
            latency_seconds=time.perf_counter() - t0, error=f"{type(exc).__name__}: {exc}",
        )
    elapsed = time.perf_counter() - t0
    if not result:
        return DetectorResult(tier="tier1_v2", query=query, latency_seconds=elapsed)
    return DetectorResult(
        tier="tier1_v2", query=query,
        concepts_detected=list(result.get("concepts", [])),
        latency_seconds=elapsed,
    )


def tier2_legacy(query: str) -> DetectorResult:
    """Call the legacy stem/substring soul lookup directly. Pure function,
    no DB, no model -- safe to call in any order with no state reset."""
    t0 = time.perf_counter()
    try:
        from backend.pipeline.soul_router import soul_lookup_legacy
        result = soul_lookup_legacy(query)
    except Exception as exc:  # noqa: BLE001
        return DetectorResult(
            tier="tier2_legacy", query=query,
            latency_seconds=time.perf_counter() - t0, error=f"{type(exc).__name__}: {exc}",
        )
    elapsed = time.perf_counter() - t0
    if not result:
        return DetectorResult(tier="tier2_legacy", query=query, latency_seconds=elapsed)
    return DetectorResult(
        tier="tier2_legacy", query=query,
        concepts_detected=list(result.get("concepts", [])),
        latency_seconds=elapsed,
    )


async def tier3_full(query: str, session_id: str) -> DetectorResult:
    """Call the full live pipeline. Async -- the caller must run this inside
    an event loop (see run_exp0.py). ``session_id`` must be unique per trial
    (see EXP0_PROTOCOL.md section 5) so working-memory/session state from one
    trial cannot leak into the next via pronoun resolution or turn buffers."""
    t0 = time.perf_counter()
    try:
        from backend.app.pipeline import answer_question
        resp = await answer_question(query, session_id=session_id)
    except Exception as exc:  # noqa: BLE001
        return DetectorResult(
            tier="tier3_full", query=query,
            latency_seconds=time.perf_counter() - t0, error=f"{type(exc).__name__}: {exc}",
        )
    elapsed = time.perf_counter() - t0
    concepts_detected = list(getattr(resp, "resonance_scores", {}) or {}).copy()
    return DetectorResult(
        tier="tier3_full", query=query,
        concepts_detected=concepts_detected,
        confidence=str(getattr(resp, "confidence", "") or ""),
        answer_text=str(getattr(resp, "answer", "") or ""),
        latency_seconds=elapsed,
    )
