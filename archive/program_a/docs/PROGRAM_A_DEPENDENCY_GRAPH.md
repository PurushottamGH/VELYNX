# PROGRAM A — DEPENDENCY GRAPH

**Authority:** Chief Systems Architect design review, 2026-07-07.
(Deliverable requested as `PROGRAM_A_DEPICENCY_GRAPH.md`; filename corrected.)
Every existing edge below was verified against actual import statements this
session or in `DEPENDENCY_GRAPH.md` (same-day verification). Tags: `[FACT]`,
`[PLANNED]`, `[FORBIDDEN]`.

---

## 1. The graph

```
                         [PLANNED] Program A emission surface
                         (location per Q4: research/ or program_a/)
                              │            │
             [PLANNED] uses   │            │  [PLANNED] uses (allowed)
                              ▼            ▼
        backend/retrieval/unified_retriever.py     stdlib only
        (engineering substrate; sources only)
                              │
     [FORBIDDEN] ✗            │      [FORBIDDEN] ✗
  backend/cognition/          │   backend/soul/*  backend/self_model/*
  answer_synthesizer.py       │   research/policies/free_energy.py
  reasoning_engine.py         │   backend/cognition/dream_state.py
  (must never be imported by the emission surface or binding)

                    [PLANNED] Program A binding (Form A/B)
                              │ implements / is wrapped by
                              ▼
        experiments/EXP1/program_a_adapter.py          [FACT]
            ProgramAAdapter · CallableProgramAAdapter
                              │ injected into (by the caller, never imported
                              │ by the runner)
                              ▼
        experiments/EXP1/run.py                        [FACT]
          ├─▶ experiments/EXP1/dataset.py   (run.py:16-24)
          ├─▶ experiments/EXP1/decision.py  (run.py:25)
          │       ├─▶ experiments/EXP1/calibration.py (decision.py:8)
          │       └─▶ experiments/EXP1/dataset.py     (decision.py:9-14)
          ├─▶ experiments/EXP1/manifest.py  (run.py:26-31)
          │       └─▶ experiments/EXP1/dataset.py     (manifest.py:12)
          └─▶ experiments/EXP1/program_a_adapter.py   (run.py:32-36)
                  └─▶ experiments/EXP1/dataset.py     (program_a_adapter.py:12)

        experiments/EXP1/dataset.py ─▶ experiments/EXP1/rubric.py  [FACT]
        experiments/EXP1/report.py  ─▶ {calibration, decision}     [FACT, unwired: TD-05]
        experiments/EXP1/artifact_specs.py ─▶ (nothing in EXP1)    [FACT, unwired: TD-05]

        core/measurement/proper_scoring.py (ECE primitive)         [FACT]
            └── consumed conceptually by experiments/EXP1/calibration.py
                (EXP-1 wrapper is self-contained; EXP1_TRACE.md ML-15)
```

## 2. Edge rules (binding)

| Rule | Direction | Source |
|---|---|---|
| `core/` imports nothing in-project | leaf | architecture.md §4 rule 1; verified `DEPENDENCY_GRAPH.md` §1 |
| `experiments/` MUST NOT import `backend/` (except via `research/` composition) | ✗ experiments→backend | architecture.md §4 rule 2; `PROGRAM_A_ADAPTER_AUDIT.md` F-6 |
| The runner never imports Program A; the adapter is caller-injected | inversion of control | `EXP1_TRACE.md` §3e; run.py:50-70 |
| `research/` composes backend components without mutating them | research→backend (read-compose) | architecture.md §4 evidence 4 |
| `backend/` may import `core/`, never the reverse | backend→core only | architecture.md §4 rule 3 |
| No import cycles | — | architecture.md §4 rule 4; none found in shipped tree (`DEPENDENCY_GRAPH.md` §2) |

## 3. Consequences for the two missing components

**[FACT → placement constraint]** If the emission surface imports
`backend.retrieval`, it cannot live in `experiments/EXP1/`. Lawful homes:
`research/` (existing composition precedent) or `program_a/` (empty; needs
packaging addition — not in `pyproject.toml` packages.find). Architect
decision pending (`PROGRAM_A_BINDING_SPEC.md` open item 1).

**[FACT]** The binding depends only on: the emission surface + 
`experiments.EXP1.dataset` (`AnswerRecord`) + `experiments.EXP1.
program_a_adapter` (Protocol). Both EXP1 imports are boundary-legal from
anywhere; the backend-touching import must sit outside `experiments/`.

## 4. Forbidden edges (deny-list for the eventual import guard)

**[FACT]** grounded in canon `:90`, TD-08, F-4/F-5, and preregistration §4-§6:

```
{emission surface, binding}  ✗→  backend.cognition.answer_synthesizer
{emission surface, binding}  ✗→  backend.cognition.reasoning_engine
{emission surface, binding}  ✗→  backend.cognition.dream_state
{emission surface, binding}  ✗→  backend.soul.*
{emission surface, binding}  ✗→  backend.self_model.*
{emission surface, binding}  ✗→  research.policies.free_energy
{emission surface, binding}  ✗→  experiments.EXP1.calibration   (no tier→p_i knowledge)
{emission surface, binding}  ✗→  experiments.EXP1.decision      (no gate knowledge)
experiments.EXP1.*           ✗→  backend.*                      (boundary rule)
experiments.EXP1.*           ✗→  program_a.*                    (runner stays injection-only)
```

**[RISK]** No CI guard currently enforces any of these (TD-08). An
import-guard test is recommended in `PROGRAM_A_ARCHITECTURE.md` §4 and
scheduled in `PROGRAM_A_IMPLEMENTATION_ROADMAP.md` T7.
