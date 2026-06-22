"""
VELYNX — Symbolic Decomposer DAG Audit (read-only dry run)
==========================================================

Standalone, READ-ONLY audit harness for the Phase 58 Symbolic Query Decomposer
(``backend.pipeline.agentic_loop.agentic_controller``).

It feeds a single nested multi-hop query through the planner and prints the
resulting execution DAG so the step-by-step decomposition can be eyeballed for
hallucination / mis-nesting.

Specifically it exercises the two PURE, side-effect-free entry points:

    * ``agentic_controller.should_plan(query)``   — the grammatical router
    * ``agentic_controller.formulate_plan(query)`` — the symbolic decomposer

It does NOT call ``execute_plan`` (that would touch the Knowledge Graph / web
retrieval mesh), and it does NOT modify any core engine file. Planning is a pure
spaCy-driven heuristic, so this run is deterministic and safe to repeat.

Usage
-----
    cd backend
    python -m tests.dry_run_multihop
    # or
    python tests/dry_run_multihop.py
"""
from __future__ import annotations

import json
import os
import sys

# ── Make the repo root importable so ``backend.*`` resolves regardless of CWD ──
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# Windows consoles default to cp1252; the planner's dependency trace may contain
# non-ASCII glyphs. Best-effort switch stdout to UTF-8 (no-op if unsupported).
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

from backend.pipeline.agentic_loop import agentic_controller  # noqa: E402


# The multi-hop sentence under audit: three nested relative/possessive clauses
#   "my favorite software" -> "the creator of [that]" -> "country associated with [that]"
QUERY = "What country is associated with the creator of my favorite software?"

# A genuine multi-hop plan for this query needs at least 3 steps
#   (resolve software -> resolve creator -> resolve country).
EXPECTED_MIN_STEPS = 3


def _hr(char: str = "=") -> str:
    return char * 72


def _print_step_summary(plan_dict: dict) -> None:
    """Human-readable, indented walk of the DAG so dependencies are obvious."""
    steps = plan_dict.get("steps", [])
    print("\n[STEP-BY-STEP DAG (dependency order)]:")
    if not steps:
        print("  <no steps emitted>")
        return
    for step in steps:
        deps = step.get("dependencies") or []
        dep_str = f"depends on {deps}" if deps else "no dependencies (root input)"
        print(f"  - Step {step.get('id')}  [{step.get('action')}]  ({dep_str})")
        print(f"      desc   : {step.get('description')}")
        if step.get("params"):
            print(f"      params : {step.get('params')}")
        print(f"      status : {step.get('status')}")


def main() -> int:
    print(_hr())
    print("VELYNX SYMBOLIC DECOMPOSER — MULTI-HOP DAG AUDIT (READ-ONLY)")
    print(_hr())
    print(f"\n[QUERY UNDER AUDIT]:\n  {QUERY}\n")

    # 1) Router gate — does the planner even recognise this as multi-hop?
    should_plan = agentic_controller.should_plan(QUERY)
    print(f"[ROUTER]  should_plan = {should_plan}")
    if not should_plan:
        print(
            "\nAUDIT RESULT: ROUTER REJECTED the query — it was NOT routed to the\n"
            "multi-hop planner. No DAG to inspect. (This is the failure mode to flag.)"
        )
        return 1

    # 2) Symbolic decomposition — build the DAG (pure, no execution).
    print("\n[DECOMPOSING via spaCy dependency grammar — no LLM, no execution]...")
    plan = agentic_controller.formulate_plan(QUERY)
    plan_dict = plan.to_dict()

    # 3a) Full DAG as indented JSON (machine-verifiable).
    print("\n[GENERATED EXECUTION DAG — full JSON]:")
    print(json.dumps(plan_dict, indent=2, default=str))

    # 3b) The dependency-parse observability trace, if the planner attached one.
    dep_trace = plan_dict.get("context", {}).get("dep_trace")
    if dep_trace:
        print("\n[DEPENDENCY-PARSE TRACE (planner observability)]:")
        print(dep_trace)

    # 3c) Readable step walk.
    _print_step_summary(plan_dict)

    # 4) Lightweight audit verdict (read-only — informational, no mutation).
    num_steps = len(plan_dict.get("steps", []))
    print("\n" + _hr("-"))
    print(f"[AUDIT] steps emitted          : {num_steps}")
    print(f"[AUDIT] expected minimum steps : {EXPECTED_MIN_STEPS}")
    if num_steps >= EXPECTED_MIN_STEPS:
        print("[AUDIT] VERDICT: PASS — decomposition produced a genuine multi-hop DAG.")
        verdict = 0
    else:
        print(
            "[AUDIT] VERDICT: REVIEW — fewer steps than a full 3-hop plan; inspect\n"
            "        the JSON above to confirm the nested clauses were captured."
        )
        verdict = 2
    print(_hr())
    print("Inspect the DAG above to verify the nested relative clauses map to")
    print("distinct retrieval hops without hallucinated entities.")
    print(_hr())
    return verdict


if __name__ == "__main__":
    raise SystemExit(main())
