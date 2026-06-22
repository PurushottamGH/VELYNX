# Phase 57 — Agentic Loop Architecture

## 1. Problem Statement

The current pipeline (`backend/app/pipeline.py`) is a **single-pass reactive DAG**.
Every query cascades unconditionally through: reflex → knowledge acquisition → soul resonance → self-model → KG fast path → learning tutor → retrieval → symbolic reasoning → synthesis → reflection. The answer is returned; the process terminates.

**What VELYNX cannot do today:**
- Formulate a goal from an ambiguous query ("Tell me about renewable energy trends")
- Decompose a multi-part question into sub-goals ("Compare fusion vs fission and tell me which countries lead in each")
- Iteratively refine: retrieve → find a gap → retrieve more → re-reason
- Ask clarifying questions when the plan is underspecified
- Self-verify: check if the synthesized answer actually satisfies the goal
- Abandon a hopeless path and replan rather than returning a low-confidence result
- Persist an in-progress plan across multiple user turns

Phase 57 wraps the existing pipeline in an **Agentic Loop** that transforms VELYNX from a reactive responder into an autonomous planner.

---

## 2. Interception Point

The loop intercepts the query after the trivial short-circuits but *before* the
heavy single-pass machinery. Concretely, in `_answer_question_impl`:

```
  reflex check ──YES──> return (bypass)
       │
      NO
       │
  knowledge acquisition ──YES──> return (statement, not a question)
       │
      NO
       │
  ┌─────────────────────────────────────────────┐
  │  AGENTIC LOOP GATE  ← NEW                   │
  │                                              │
  │  should_plan(query, intent) ──YES──>         │
  │    planner.formulate(query)                  │
  │    → Plan goal, Plan steps                   │
  │    executor.run(plan)                        │
  │    → AnswerResponse                          │
  │    return                                    │
  │                                              │
  │  NO (simple query) ────────────────>         │
  └─────────────────────────────────────────────┘
       │
      fall through to existing pipeline
  (soul → self → KG → learning → retrieval → reasoning → synthesis)
```

**Rationale:** Reflex and knowledge acquisition are terminal gates — greetings
and factual statements don't need planning. Everything else is a reasonable
candidate for the planner, but only complex/ambiguous queries should actually
trigger it. The `should_plan` heuristic keeps simple lookups fast.

---

## 3. Plan Schema

New file: `backend/pipeline/plan_schema.py`

```python
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StepStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class PlanStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"
    NEEDS_CLARIFICATION = "needs_clarification"


class PlanAction(Enum):
    """The set of primitive actions the executor can dispatch."""
    RETRIEVE = "retrieve"               # retrieval_mesh.retrieve_all
    KG_LOOKUP = "kg_lookup"             # knowledge_graph.lookup
    KG_RELATED = "kg_related"           # knowledge_graph.get_related (triples)
    SOUL_LOOKUP = "soul_lookup"         # soul_lookup / soul_lookup_legacy
    REASON = "reason"                   # symbolic reasoning engine
    SYNTHESIZE = "synthesize"           # AnswerSynthesizer.synthesize
    CLARIFY = "clarify"                 # Generate clarification question
    WEB_SEARCH = "web_search"           # retrieval_mesh with expanded query
    VERIFY = "verify"                   # Self-consistency check / reflection
    MEMORY_RECALL = "memory_recall"     # memory_manager.recall (semantic/episodic)
    CURIOSITY = "curiosity"             # curiosity_engine.select_question


@dataclass
class PlanStep:
    """A single atomic step in a plan."""
    id: str                              # "step_1", "step_2", ...
    goal: str                            # Human-readable purpose
    action: PlanAction                   # Which primitive to invoke
    params: dict[str, Any] = field(default_factory=dict)  # Input params
    status: StepStatus = StepStatus.PENDING
    result: dict[str, Any] | None = None
    dependencies: list[str] = field(default_factory=list)  # Step IDs
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Plan:
    """A multi-step execution plan derived from a user query."""
    id: str                              # UUID
    original_query: str
    goal: str                            # The formulated goal
    steps: list[PlanStep]
    context: dict[str, Any] = field(default_factory=dict)  # Cross-step state
    status: PlanStatus = PlanStatus.ACTIVE
    created_at: float = field(default_factory=import_time)
    completed_at: float | None = None
    session_id: str = ""


def import_time() -> float:
    import time
    return time.time()
```

**Key design decisions:**
- `PlanAction` is an *enum*, not free-form strings, so the executor has a
  closed switch/if-elif dispatch. Each action maps to exactly one existing
  pipeline primitive.
- `dependencies` encodes the step DAG as explicit IDs (not implicit ordering),
  allowing the executor to parallelize independent steps later.
- `context` is the cross-step accumulator. Step 1's fact → Step 2's input.
  Stored as a flat dict keyed by step ID so any step can read any predecessor.

---

## 4. Planner

New file: `backend/pipeline/planner.py`

### 4.1 Responsibilities

1. **Goal formulation** — Given a raw user query, produce a crisp, single-sentence goal.
   - "Compare fusion vs fission and tell me which countries lead in each"
     → `Goal: "Compare nuclear fusion and fission and identify leading countries for each."`
   - "Tell me about renewable energy trends"
     → `Goal: "Summarize current trends in renewable energy adoption, costs, and policy."`

2. **Step decomposition** — Break the goal into a DAG of `PlanStep` objects.
   - Each step has one `PlanAction`, one `goal`, and explicit `dependencies`.
   - Steps are ordered so the DAG is acyclic (verified on construction).

3. **Replanning** — Given a partial plan + results so far + a signal that the
   current path is insufficient, produce additional steps or adjust existing ones.

### 4.2 Decomposition Strategy

The planner uses **deterministic pattern matching** (no LLM call) for common
query structures, falling back to the intent engine's dimension scores when
nothing specific matches.

**Pattern → Step skeleton examples:**

| Query pattern | Generated steps |
|---|---|
| `"Compare X and Y..."` | `[KG_LOOKUP(X), KG_LOOKUP(Y), WEB_SEARCH("X vs Y"), REASON, SYNTHESIZE]` |
| `"What is X and how does it work?"` | `[KG_LOOKUP(X), WEB_SEARCH(X), REASON, SYNTHESIZE]` |
| `"Tell me about X"` | `[MEMORY_RECALL(X), SOUL_LOOKUP(X), WEB_SEARCH(X), REASON, SYNTHESIZE]` |
| `"Why did X happen?"` | `[KG_LOOKUP(X), WEB_SEARCH("X cause"), WEB_SEARCH("X history"), REASON, SYNTHESIZE]` |
| Single concept, low ambiguity | Falls through to existing single-pass pipeline (no planning) |

### 4.3 `should_plan` heuristic

A query triggers planning when ANY of these is true:
- Contains comparison keywords ("compare", "vs", "versus", "difference between")
- Contains two named entities separated by a conjunction
- Dimension-level ambiguity: 3+ dimensions score > 0.3 in intent_engine
- Explicit scaffolding keywords ("first...then...", "steps", "outline", "break down")
- Contains a referential pronoun chain that requires iterative resolution
- Is a follow-up to an active plan (session has an `ACTIVE` plan)

---

## 5. Execution Loop

New file: `backend/pipeline/agentic_loop.py`

### 5.1 Core Loop

```python
class AgenticLoop:
    """Wraps the existing pipeline primitives in an iterative execution loop."""

    def __init__(self, planner: Planner, executor: StepExecutor, tracker: PlanTracker):
        ...

    async def run(self, plan: Plan) -> AnswerResponse:
        """Execute steps until the plan is complete or abandoned."""

        while plan.status == PlanStatus.ACTIVE:
            ready = self._next_ready_steps(plan)
            if not ready:
                break  # All done or all blocked

            for step in ready:
                step.status = StepStatus.IN_PROGRESS
                result = await self.executor.execute(step, plan.context)
                plan.context[step.id] = result

                if result.get("status") == "clarification_needed":
                    plan.status = PlanStatus.NEEDS_CLARIFICATION
                    return self._build_clarification_response(plan, step, result)

                if step.action == PlanAction.VERIFY:
                    verified = result.get("passed", False)
                    if not verified:
                        # Replan — inject additional steps
                        new_steps = self.planner.replan(plan, step, result)
                        plan.steps.extend(new_steps)
                        step.status = StepStatus.COMPLETED
                        continue

                if self._is_terminal_error(result):
                    step.status = StepStatus.FAILED
                    plan.status = PlanStatus.FAILED
                    return self._build_error_response(plan, step)

                step.status = StepStatus.COMPLETED

            # Check goal satisfaction after each round
            if self._goal_satisfied(plan):
                plan.status = PlanStatus.COMPLETED

        return self._synthesize_final_answer(plan)
```

### 5.2 Step Completion Detection

A step is "complete" when:
- **RETRIEVE / WEB_SEARCH / MEMORY_RECALL** — sources are returned (empty list = complete but flagged as low-evidence)
- **REASON** — reasoning_trace contains at least one resolved path
- **SYNTHESIZE** — answer text is non-empty
- **KG_LOOKUP / KG_RELATED** — result dict returned (None = empty hit, still considered complete)
- **VERIFY** — `passed: True/False` with supporting evidence
- **CLARIFY** — clarification question generated

A step is *not* "complete" when:
- Result contains `error` key set to a non-empty string
- Primitive raised an exception (caught, logged, step marked FAILED)

### 5.3 Context Passing Between Steps

Step i's results are written to `plan.context[step_i.id]`. Step j reads
predecessors via `plan.context[pred_id]` where `pred_id` is in its
`dependencies` list.

Example for "Compare fusion and fission":

```
step_1: KG_LOOKUP("nuclear fusion")
  → context["step_1"] = {"concept": "fusion", "summary": "...", "triples": [...]}

step_2: KG_LOOKUP("nuclear fission")
  → context["step_2"] = {"concept": "fission", "summary": "...", "triples": [...]}

step_3: WEB_SEARCH("nuclear fusion vs fission comparison")
  depends_on: ["step_1", "step_2"]
  → reads context["step_1"], context["step_2"] to build search query
  → context["step_3"] = {"sources": [... comparison articles ...]}

step_4: REASON
  depends_on: ["step_1", "step_2", "step_3"]
  → reads all three predecessors for evidence
  → context["step_4"] = {"reasoning_trace": ..., "concepts": [...]}

step_5: SYNTHESIZE
  depends_on: ["step_4"]
  → reads reasoning_trace
  → context["step_5"] = {"answer": "...", "confidence": "PROBABLE"}

step_6: VERIFY
  depends_on: ["step_5"]
  → checks answer against original goal
  → if failed → planner.replan(...) → injects step_7 (another search)
```

This is explicit, debuggable, and requires zero shared mutable state.

### 5.4 Goal Satisfaction

A plan's goal is satisfied when the synthesized answer:
- Covers all entities mentioned in the goal formulation
- Has confidence ≥ PROBABLE OR has at least one cited source per entity
- Does not contain an unresolved uncertainty marker (unless the goal is inherently speculative)

If satisfaction fails after exhausting all planned steps, the plan transitions to
`FAILED` and returns the best answer so far (with lowered confidence and a
transparent gap description).

---

## 6. Plan Persistence (PlanTracker)

New file: `backend/pipeline/plan_tracker.py`

### 6.1 In-Memory State (per session)

```python
@dataclass
class SessionPlanState:
    active_plan: Plan | None
    plan_history: list[Plan]          # Completed/failed plans for context
    last_plan_timestamp: float | None
```

### 6.2 Key operations

- `get_active_plan(session_id) → Plan | None` — resume an in-progress plan
- `save_plan(plan)` — persist (to `plan_tracker` dict in memory)
- `get_plan_history(session_id, limit=5) → list[Plan]` — for referential resolution

### 6.3 Serialization (future-proofing)

Plans are JSON-serializable so they *could* be persisted to SQLite later.
`Plan.context` is limited to plain dicts (no complex objects); binary artifacts
like embedding vectors stay in the memory manager.

---

## 7. StepExecutor

Shared responsibility between `agentic_loop.py` and the existing primitives
(pipelines, engines). The executor is a **dispatch table**:

```python
class StepExecutor:
    def __init__(self, symbolic_kg, reasoning_engine, answer_synthesizer, ...):
        ...

    async def execute(self, step: PlanStep, context: dict) -> dict:
        match step.action:
            case PlanAction.RETRIEVE | PlanAction.WEB_SEARCH:
                return await self._do_retrieve(step.params)
            case PlanAction.KG_LOOKUP:
                return self._do_kg_lookup(step.params)
            case PlanAction.KG_RELATED:
                return self._do_kg_related(step.params)
            case PlanAction.REASON:
                return self._do_reason(step, context)
            case PlanAction.SYNTHESIZE:
                return await self._do_synthesize(step, context)
            case PlanAction.VERIFY:
                return self._do_verify(step, context)
            case PlanAction.CLARIFY:
                return self._do_clarify(step.params)
            case PlanAction.MEMORY_RECALL:
                return await self._do_memory_recall(step.params)
            case PlanAction.SOUL_LOOKUP:
                return self._do_soul_lookup(step.params)
            case PlanAction.CURIOSITY:
                return self._do_curiosity(step.params)
```

Each `_do_*` method delegates to the **existing** pipeline/cognition module
for that action. The executor does not implement any new logic — it just
normalizes parameters and return values into a consistent `dict` shape.

---

## 8. File Manifest

### 8.1 New files

| File | Purpose |
|---|---|
| `backend/pipeline/plan_schema.py` | `Plan`, `PlanStep`, `PlanAction`, `StepStatus`, `PlanStatus` data classes |
| `backend/pipeline/planner.py` | `Planner` class — goal formulation, step decomposition, replanning |
| `backend/pipeline/agentic_loop.py` | `AgenticLoop` class — execution loop, step dispatch, goal satisfaction check, final answer synthesis |
| `backend/pipeline/plan_tracker.py` | `PlanTracker` class — per-session plan persistence and lookup |

### 8.2 Modified files

| File | Change |
|---|---|
| `backend/app/pipeline.py` | Add `should_plan()` gate in `_answer_question_impl` after the knowledge-acquisition block; route to `AgenticLoop.run()` when triggered |
| `backend/pipeline/__init__.py` | Export `plan_schema`, `planner`, `agentic_loop`, `plan_tracker` |
| `backend/pipeline/synthesizer.py` | Add `synthesize_from_plan(plan, context)` — builds an `AnswerResponse` directly from a completed plan |

---

## 9. Edge Cases & Guardrails

### 9.1 Infinite loop prevention

- Hard step limit per plan: **max 12 steps**. If exceeded, the plan is
  abandoned and the best partial result is returned.
- Time limit per plan: **30 seconds wall-clock**. Enforced by an `asyncio.wait_for`
  wrapping `AgenticLoop.run()`. Existing 30-second route timeout remains.
- Replan limit: **max 3 replan cycles**. Beyond that, the plan transitions to
  `FAILED`.

### 9.2 Clarification loop

When a step returns `"clarification_needed"`, the loop pauses, returns the
clarification question to the user, and stores the plan as `NEEDS_CLARIFICATION`.
The user's next message is checked against the session's active plan; if the
message provides the missing information, the planner injects a `RESOLVE`
step and resumes execution.

### 9.3 Empty search results

When a RETRIEVE/WEB_SEARCH step returns zero results:
- The executor flags the step as `COMPLETED` with `"sources": []` and
  `"evidence_score": 0.0`
- The planner checks this score in the next round and may inject a `CLARIFY`
  step or a follow-up search with an expanded query

### 9.4 Fallback to existing pipeline

If `should_plan` returns `False`, or if the planner raises an unexpected
exception, the query falls through to the existing single-pass pipeline
unchanged. Zero regression risk for simple queries.

---

## 10. Migration Path

### Phase 57a — Skeleton (proof of concept)
1. Create `plan_schema.py` with all data classes
2. Create `planner.py` with `should_plan()` and the pattern-matcher decomposition
3. Create `agentic_loop.py` with the loop skeleton that executes steps sequentially
4. Create `plan_tracker.py` with in-memory dict storage
5. Wire the gate into `pipeline.py` with a feature flag `AGENTIC_LOOP_ENABLED=False`
6. Acceptance test: "Compare fusion and fission" → plan with 5+ steps executes without error

### Phase 57b — Robustness (QA)
1. Add replanning logic to the planner
2. Add goal satisfaction check to the loop
3. Add VERIFY action and self-consistency check
4. Wire the clarification flow (NEEDS_CLARIFICATION → user response → resume)
5. Add all guardrails (step limit, time limit, replan limit)
6. Acceptance test: ambiguous query triggers CLARIFY; follow-up answer completes the plan

### Phase 57c — Production (flip the flag)
1. Set `AGENTIC_LOOP_ENABLED=True` by default
2. Benchmark: latency distribution for planned vs unplanned queries
3. Profiling: identify bottleneck primitives under loop execution
4. Documentation: update architecture docs with loop flowchart
