# Program A Binding Specification

> [!NOTE]
> **Reconciliation Note (F-10 Resolution):** The F-10 direct-construction bypass is fully resolved on disk per `dataset.py:112-122`, rendering any warning of bypass risk stale.
>
> **Reconciliation Note (Package Layout Resolution):** The empty stub layout references are stale. The package layout has been resolved to the 4-package design documented in `PROGRAM_A_FINAL_ARCHITECTURE.md`.

**Status:** Specification produced by the VELYNX Director in the Builder role
slot, under explicit one-time user authorization (2026-07-07). The Architect,
Builder, Reviewer, and ScientificAuditor specialist agents returned no
output across invocation attempts in this session (matching the documented
specialist-runtime failure in `EXP1_TRACE.md` and `PROGRAM_A_ADAPTER_AUDIT.md`).
This document is a **binding specification**, not a formal Architect adjudication
and not a formal ScientificAuditor verdict. No specialist approvals are claimed
or implied. Every claim is verified against the file on disk this session and
cited to `file:line`.

**Scope:** Identify the *missing concrete Program A binding* for EXP-1, i.e.
the exact object that must connect Program A's answer-emission surface to the
EXP-1 `AnswerRecord` contract. Determine what component should produce
`AnswerRecord`, where Program A currently terminates, where EXP-1 currently
begins, and exactly what object must be connected. Reuse existing interfaces;
invent no scientific logic.

**Out of scope:** redesigning the adapter framework (already exists and is
fully tested), inventing Program A architecture, embedding scientific
tier logic in the adapter, binding `[REJECTED]` mechanisms, modifying any
preregistration or frozen constant, and any tier mapping / calibration /
ECE / rubric / decision logic.

**Relationship to prior work:** This specification supersedes nothing. It
narrowly extends `PROGRAM_A_ADAPTER_AUDIT.md` Section 3 (the contract-gap
finding) by pinning the exact binding seam and the implementation-feasibility
verdict. `PROGRAM_A_ADAPTER_TEST_PLAN.md` already covers the adapter
*framework* tests; this document does not duplicate them.

---

## 1. Current pipeline (verified)

The EXP-1 execution chain from `EXP1_TRACE.md` (Link 1-6):

```
[Program A]  --(answer + tier)-->  [Adapter]  --(AnswerRecord)-->
[EXP-1 runner]  --(QueryRecord, AnswerRecord)-->  [Adjudicator]  --(correctness)-->
[EvaluatedRecord]  --(records)-->  [Calibration / ECE]  --(CalibrationResult)-->
[Decision]  --(SeedDecision / ExperimentDecision)-->
```

Links 2, 4, 5, 6 (per-seed artifacts + manifest) are **[WIRED]**. The four
`[MISSING]` concrete links blocking a real end-to-end run are
(`EXP1_TRACE.md:269-275`):

1. the frozen 210-row dataset (`data/exp1_queries.json`),
2. a concrete `ProgramAAdapter` binding `program_a/retrieval/` (**this spec**),
3. a concrete rubric adjudicator implementing `EXP1_PREREGISTRATION.md`
   Section 3, and
4. wiring of `report.py` and `artifact_specs.py` into `run.py`.

This specification addresses **link 2 only**.

---

## 2. Where Program A currently terminates

Program A is the retrieval-plus-synthesis product surface. Three surfaces
exist in the repository; none terminates at the EXP-1 contract.

### 2a. `backend/retrieval/unified_retriever.py` - the retriever
- `UnifiedRetriever.retrieve(query: str) -> RetrievalReport`
  (`unified_retriever.py:154`).
- `RetrievalReport` (`unified_retriever.py:43-58`) emits **only**:
  `query`, `sources` (list of `RetrievalSource`), `attempts`, `elapsed`.
- `RetrievalSource` (`unified_retriever.py:24-40`) emits:
  `url`, `title`, `snippet`, `source`, `score` (heuristic retrieval
  relevance, default `0.5`), `retrieved_at`.
- **No answer text. No confidence tier.** `score` is retrieval-relevance,
  not answer confidence.

### 2b. `backend/cognition/answer_synthesizer.py` - the synthesizer
- `AnswerSynthesizer.synthesize(query, reasoning_trace, vec_results=None)
  -> SynthesisResult` (`answer_synthesizer.py:106-133`).
- `SynthesisResult` (`answer_synthesizer.py:63-75`) emits `text`,
  `confidence` (float in `[0,1]`), `confidence_label` from the
  5-grade enum `ConfidenceGrade` = `{CERTAIN, PROBABLE, UNCERTAIN,
  SPECULATIVE, INSUFFICIENT}` (`answer_synthesizer.py:32-47`), `sources`,
  `reasoning_used`, `why`, `how`, `contradiction_count`,
  `unresolved_concepts`.
- Depends on a `ReasoningTrace` (`reasoning engine`), a
  `thermodynamic_state`, and a knowledge graph `kg`
  (`answer_synthesizer.py:106-133`) - all marked `[REJECTED]` as
  load-bearing *science* by `PROGRAM_D_CANONICAL.md` Section 5 line 90 and
  `architecture.md` Section 6 item 6 (reasoning engine's type-lifting,
  `resonance / sleep-replay / thermodynamic state` permanently removed).

### 2c. `program_a/` - empty stubs
- `program_a/retrieval/__init__.py` and `program_a/nlp/__init__.py` are
  **0-byte** files (verified this session).
- `program_a/` contains nothing else.
- `ARCHITECTURE_MAP.md` row 6 claims `program_a/` is "LIVE" with a
  "Unified retriever (Arxiv, Brave, DuckDuckGo, etc.)" - this is the
  TD-13-style parallel-skeleton inaccuracy already recorded in
  `PROGRAM_A_ADAPTER_AUDIT.md` F-2.

### 2d. Termination verdict

Program A currently terminates at one of two surfaces, neither of which
emits the EXP-1 contract:

- **Retriever** terminates at `RetrievalReport` (sources-only; no answer,
  no tier).
- **Synthesizer** terminates at `SynthesisResult` (answer text + a 5-grade
  label + a raw float) but sits on `[REJECTED]` science and emits the
  wrong tier taxonomy.

There is **no** Program A surface that terminates at
`AnswerRecord(query_id, answer, tier in {UNKNOWN, DEBATED, PROBABLE,
CERTAIN}, seed, ...)`.

---

## 3. Where EXP-1 currently begins

EXP-1 begins at the injected adapter/answer callable, never at Program A
machinery. By design (dependency boundary, `architecture.md` Section 4
rule 2: `experiments/` must not import `backend/`).

### 3a. Entry points
- `experiments/EXP1/run.py:50` `run_seed(..., answer_fn=None,
  program_a_adapter=None, program_a_adapter_id=None, adjudicator_fn=None,
  ...)`.
- `experiments/EXP1/run.py:114` `run_experiment(...)` - same injection
  parameters.
- `experiments/EXP1/run.py:224,230` synchronous wrappers
  `run_seed_sync` / `run_experiment_sync`.

### 3b. Normalization
- `experiments/EXP1/run.py:66-70` (`run_seed`) and `:130-134`
  (`run_experiment`) call `coerce_program_a_adapter`.
- `experiments/EXP1/program_a_adapter.py:55-76`: accepts either an
  explicit `adapter` (a `ProgramAAdapter`) or an `answer_fn`; raises
  `ValueError("Program A adapter or answer_fn is required")` if both are
  `None` (`:72`).

### 3c. Per-query call
- `experiments/EXP1/run.py:84` (`run_seed`) and `:181`
  (`run_experiment`): `answer_result = await _maybe_await(
  adapter.answer(query, seed))`.
- `experiments/EXP1/run.py:85,182`: `answer = _coerce_answer_record(
  answer_result, query.query_id, seed)` (`:242-258`).

### 3d. EXP-1's required adapter contract
- `ProgramAAdapter` Protocol (`program_a_adapter.py:18-27`):
  `adapter_id: str` property + `answer(query: QueryRecord, seed: int)
  -> ProgramAAnswer`.
- `ProgramAAnswer` (`program_a_adapter.py:15`) =
  `AnswerRecord | Mapping[str, Any] | Awaitable[Any]`.
- `AnswerRecord` (`dataset.py:101-151`): requires `query_id`,
  `answer: str`, `tier in CONFIDENCE_TIERS` (`dataset.py:17` =
  `("UNKNOWN","DEBATED","PROBABLE","CERTAIN")`), optional `seed`,
  `raw_numeric_confidence`, `metadata`.

### 3e. EXP-1 begin verdict

EXP-1 begins at the **caller-injected adapter or `answer_fn`**. The
runner never imports or calls any Program A surface. The concrete binding
is therefore the responsibility of whoever constructs the runner's
arguments, not of the runner itself.

---

## 4. The missing connection (exact object)

The missing object is a **concrete binding** that satisfies one of the two
following forms, both of which the existing framework already accepts:

### Form A - an `answer_fn` callable (simplest)
```python
def program_a_answer(query: QueryRecord, seed: int) -> AnswerRecord | Mapping:
    # 1. Drive a real Program A retrieval+synthesis surface with query.query.
    # 2. Produce nswer text and a canonical 	ier in
    #    {UNKNOWN, DEBATED, PROBABLE, CERTAIN}.
    # 3. Return AnswerRecord(query_id=query.query_id, answer=..., tier=...,
    #    seed=seed, raw_numeric_confidence=..., metadata=...).
    ...
```
Injected via `run_experiment(answer_fn=program_a_answer,
program_a_adapter_id="program-a-public-v1", ...)`.
`coerce_program_a_adapter` (`program_a_adapter.py:73-76`) wraps it in a
`CallableProgramAAdapter` whose `adapter_id` defaults to
`callable_identity(answer_fn)` or honors an explicit `program_a_adapter_id`.

### Form B - a `ProgramAAdapter` implementation (structured)
```python
class ProgramAAdapterBinding:                       # implements the Protocol
    @property
    def adapter_id(self) -> str: return "program-a-public-v1"
    def answer(self, query: QueryRecord, seed: int) -> ProgramAAnswer: ...
```
Injected via `run_experiment(program_a_adapter=ProgramAAdapterBinding(),
adjudicator_fn=..., ...)`. `coerce_program_a_adapter` accepts it
unchanged after the `isinstance(adapter, ProgramAAdapter)` and non-empty
`adapter_id` checks (`program_a_adapter.py:65-70`).

### What the binding must produce

Per `AnswerRecord` (`dataset.py:101-151`) and `EXP1_PREREGISTRATION.md`
Section 1, the binding must emit, for every frozen query row `i`:

| Field | Required | Source / constraint |
|---|---|---|
| `query_id` | yes | echo `query.query_id` |
| `answer` (`answer_i`) | yes | natural-language answer/refusal from a real Program A surface |
| `tier` (`tier_i`) | yes | one of `UNKNOWN / DEBATED / PROBABLE / CERTAIN` - **must come from Program A's public confidence emission, not retrieval relevance, not a post-hoc remap** (`EXP1_PREREGISTRATION.md` Section 1 line 33; Section 5) |
| `seed` | optional but recommended | the injected `seed` (`run.py:85,182` stamps it on mapping returns; `AnswerRecord` instances must carry it) |
| `raw_numeric_confidence` | optional | logged exploratory only; **ignored for ECE** (`EXP1_PREREGISTRATION.md` Section 1 line 35; Section 6) |
| `metadata` | optional | dict |

The binding must be **deterministic** (explicit `seed`, no hidden state),
**side-effect free** within the experiment (no DB writes, no telemetry
perturbation of the run), and **replay-compatible** (the
`ExecutionManifest.program_a_adapter_id`, `manifest.py:29`, records its
stable identity).

---

## 5. Implementation plan (feasibility-gated)

The plan is **feasibility-gated**: each step either reuses an existing
interface (no scientific logic) or is blocked.

### Step 1 - Reuse the framework (no code) - FEASIBLE
The adapter framework already provides everything the binding needs to
plug in: `ProgramAAdapter` Protocol, `CallableProgramAAdapter`,
`coerce_program_a_adapter`, `callable_identity`, the runner injection
points, and `AnswerRecord`/`from_mapping` coercion. `CallableProgramAAdapter`
already IS a thin dependency-injected binding around an externally-injected
`answer_fn` (`PROGRAM_A_ADAPTER_AUDIT.md` Section 1; verified this
session). **No new adapter class is required.**

### Step 2 - Obtain a canonical Program A answer+tier surface - BLOCKED
No existing Program A surface emits both `answer: str` and
`tier in {UNKNOWN, DEBATED, PROBABLE, CERTAIN}`:

- `UnifiedRetriever` emits sources only. Using `RetrievalSource.score`
  as a tier basis is the "scoring retrieval relevance / source confidence as
  answer confidence" category error rejected by `EXP1_PREREGISTRATION.md`
  Section 5 (`PROGRAM_A_ADAPTER_AUDIT.md` F-3, F-7).
- `AnswerSynthesizer` emits a 5-grade label that does not match the
  canonical 4-tier set; mapping 5->4 inside the binding is "post-hoc tier
  remapping" (`EXP1_PREREGISTRATION.md` Section 4 kill criterion #5) and
  "scientific logic" the brief forbids. Binning its `confidence` float is
  "post-hoc calibration" (Section 6, prohibited). It also depends on
  `[REJECTED]` mechanisms (`PROGRAM_D_CANONICAL.md` Section 5 line 90),
  so binding it into the live EXP-1 path realizes the TD-08 risk
  (`PROGRAM_A_ADAPTER_AUDIT.md` F-4, F-5, F-7).
- `program_a/` is empty; binding it requires inventing Program A
  architecture, which is out of scope and requires its own preregistration
  + ScientificAuditor sign-off (`PROGRAM_A_ADAPTER_AUDIT.md` Section 6
  item 6).

### Step 3 - Construct the binding - BLOCKED (depends on Step 2)
Given a canonical Program A answer+tier emission surface, the binding is a
~20-line function (Form A) or class (Form B) that:
1. calls the surface with `query.query` and `seed`,
2. reads back the answer text and the canonical tier,
3. returns `AnswerRecord(query_id=query.query_id, answer=..., tier=...,
   seed=seed, raw_numeric_confidence=..., metadata=...)`.

This step introduces no scientific logic - it is pure field transport - and
could be implemented by the Builder **as soon as Step 2 is unblocked**.

### Step 4 - Choose the lawful location - PENDING ARCHITECT
Per `architecture.md` Section 4 rule 2, `experiments/` must not import
`backend/` except via the documented `research/` composition layer.
Therefore the binding cannot live in `experiments/EXP1/`. Candidate
locations (Architect to adjudicate):
- `research/` composition layer (side-effect-free harness; can compose
  backend surfaces behind research abstractions per `architecture.md`
  Section 4 evidence block 4).
- `program_a/` (currently empty; would require Program A architecture).
- A new `scripts/` entry that constructs the runner arguments.

### Feasibility verdict
**Implementation is infeasible as scoped without inventing scientific
behavior.** Step 2 is blocked by the absence of a canonical Program A
answer+tier emission surface. Any binding constructed against the existing
`UnifiedRetriever` or `AnswerSynthesizer` surfaces would either embed
scientific tier logic (forbidden), perform post-hoc tier remapping / post-hoc
calibration (kill criteria), or bind `[REJECTED]` mechanisms (canonical
violation). Per the brief: **stop after the specification; do not implement.**

---

## 6. Required files (for the eventual binding, once Step 2 is unblocked)

| File | Role | Status |
|---|---|---|
| `experiments/EXP1/program_a_adapter.py` | `ProgramAAdapter` Protocol, `CallableProgramAAdapter`, `coerce_program_a_adapter`, `callable_identity` | exists, fully tested, unchanged |
| `experiments/EXP1/dataset.py` | `AnswerRecord`, `QueryRecord`, `CONFIDENCE_TIERS` | exists, unchanged |
| `experiments/EXP1/run.py` | `run_seed`/`run_experiment` injection points, `_coerce_answer_record` | exists, unchanged |
| `experiments/EXP1/manifest.py` | `ExecutionManifest.program_a_adapter_id` | exists, unchanged |
| `backend/retrieval/unified_retriever.py` | retriever (sources-only) | exists; **insufficient** (no answer, no canonical tier) |
| `backend/cognition/answer_synthesizer.py` | synthesizer (5-grade, `[REJECTED]` deps) | exists; **unusable** (taxonomy mismatch + canonical violation) |
| `program_a/retrieval/__init__.py`, `program_a/nlp/__init__.py` | empty stubs | exist; **empty** |
| **NEW**: canonical Program A answer+tier emission component | emits `answer: str` + `tier in {UNKNOWN, DEBATED, PROBABLE, CERTAIN}` from a real surface | **does not exist - requires its own preregistration + ScientificAuditor sign-off** |
| **NEW**: the binding (Form A or B) in the lawful location | transports fields into `AnswerRecord` | blocked on the above + Architect location decision |
| **NEW**: `tests/EXP1/test_program_a_binding.py` (or under `research/tests/`) | exercises the binding end-to-end through `run_seed_sync` | blocked on the binding |

---

## 7. Required interfaces (all already exist; the binding reuses them)

```python
# experiments/EXP1/program_a_adapter.py:18-27
class ProgramAAdapter(Protocol):
    @property
    def adapter_id(self) -> str: ...
    def answer(self, query: QueryRecord, seed: int) -> ProgramAAnswer: ...

# experiments/EXP1/program_a_adapter.py:30-44
@dataclass(frozen=True)
class CallableProgramAAdapter:
    adapter_id: str
    answer_fn: Any
    def answer(self, query: QueryRecord, seed: int) -> ProgramAAnswer: ...

# experiments/EXP1/program_a_adapter.py:55-76
def coerce_program_a_adapter(*, adapter=None, answer_fn=None,
                             adapter_id=None) -> ProgramAAdapter: ...

# experiments/EXP1/dataset.py:101-151
@dataclass(frozen=True)
class AnswerRecord:
    query_id: str; answer: str; tier: str
    seed: int | None = None
    raw_numeric_confidence: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    @classmethod
    def from_mapping(cls, row: Mapping) -> "AnswerRecord": ...

# experiments/EXP1/run.py:39
AnswerFunction = Callable[[QueryRecord, int], AnswerRecord | Mapping | Awaitable]
# experiments/EXP1/run.py:50-111, 114-221  run_seed / run_experiment (injection points)
```

The binding consumes these interfaces; it does **not** modify any of them.

---

## 8. Dependency graph

```
                        [MISSING: canonical Program A answer+tier surface]
                                      |
                                      v
[MISSING: concrete binding (Form A or B, lawful location)]
   implements ProgramAAdapter OR is an answer_fn
                                      |
                                      v  (injected by caller)
   experiments/EXP1/run.py  run_seed / run_experiment
        |
        +-> coerce_program_a_adapter        (program_a_adapter.py:55-76)
        |       |
        |       +-> ProgramAAdapter Protocol     (program_a_adapter.py:18-27)
        |       +-> CallableProgramAAdapter       (program_a_adapter.py:30-44)
        |
        +-> adapter.answer(query, seed)            (run.py:84,181)
        +-> _coerce_answer_record -> AnswerRecord  (run.py:242-258; dataset.py:101-151)
        +-> _maybe_await                            (run.py:236-239)
        +-> ExecutionManifest.program_a_adapter_id  (manifest.py:29)
        |
        v
   [Adjudicator] (MISSING - link 3, separate spec)
        |
        v
   EvaluatedRecord -> calibration.compute_ece -> decision.decide_seed/decide_experiment
```

Upward edges that **must not** exist (boundary rule,
`architecture.md` Section 4 rule 2):
`experiments/EXP1/` -> `backend/*` (forbidden except via `research/`).
`experiments/EXP1/` -> `program_a/*` (`program_a/` is empty; binding
there is inventing architecture).

---

## 9. Risks

| # | Risk | Citation / status |
|---|---|---|
| R1 | **Category error** - using `RetrievalSource.score` as the answer-confidence tier. | `EXP1_PREREGISTRATION.md` Section 5; `PROGRAM_A_ADAPTER_AUDIT.md` F-3, F-7. Preregistered kill. |
| R2 | **Post-hoc tier remapping** - mapping the synthesizer's 5-grade label to the canonical 4-tier set inside the binding. | `EXP1_PREREGISTRATION.md` Section 4 #5 (kill criterion); Section 5. Forbidden by the brief ("no scientific logic"). |
| R3 | **Post-hoc calibration** - binning the synthesizer's raw `confidence` float into canonical tiers. | `EXP1_PREREGISTRATION.md` Section 6 ("Use of post-hoc calibration: Prohibited"). |
| R4 | **Canonical violation (TD-08)** - binding `AnswerSynthesizer` into the live EXP-1 path realizes a `[REJECTED]`-mechanism dependency (ReasoningTrace, thermodynamic_state, kg). | `PROGRAM_D_CANONICAL.md` Section 5 line 90; `architecture.md` Section 6 item 6; `PROGRAM_A_ADAPTER_AUDIT.md` F-5. |
| R5 | **Dependency-boundary violation** - placing a `backend/`-importing binding inside `experiments/EXP1/`. | `architecture.md` Section 4 rule 2. |
| R6 | **Inventing Program A architecture** - building the canonical answer+tier surface inside `program_a/` is out of scope for an adapter/binding task and requires its own preregistration + ScientificAuditor sign-off. | `PROGRAM_A_ADAPTER_AUDIT.md` Section 6 item 6. |
| R7 | **Direct-construction tier bypass (F-10)** - an injected `answer_fn` returning an `AnswerRecord` *instance* with a non-canonical tier bypasses `from_mapping` validation; `_coerce_answer_record` (`run.py:242-258`) accepts an `AnswerRecord` instance without re-validating its tier. The non-canonical tier then propagates until `calibration.confidence_for_tier` raises `KeyError`. | `PROGRAM_A_ADAPTER_AUDIT.md` F-10 (observed, documented, NOT fixed). A real binding must construct via `from_mapping` or guarantee a canonical tier; the underlying guard gap is a separate production-code fix requiring Reviewer + ScientificAuditor sign-off. |
| R8 | **Specialist unavailability** - Architect, Builder, Reviewer, ScientificAuditor returned no output this session. This specification has no formal Architect location decision and no formal ScientificAuditor tier-source lawfulness verdict. | matches `EXP1_TRACE.md` and `PROGRAM_A_ADAPTER_AUDIT.md` recorded specialist-runtime failure. |

---

## 10. Open items requiring specialist sign-off

1. **Architect** - adjudicate the lawful binding location (`research/`
   composition layer vs `program_a/` vs `scripts/`) given the
   dependency boundary (`architecture.md` Section 4 rule 2) and the
   empty-`program_a/` state.
2. **ScientificAuditor** - PASS/FAIL on tier-source lawfulness: confirm
   that no existing Program A surface lawfully emits a canonical 4-tier
   confidence, and that any future surface must emit the canonical tiers
   itself (not be remapped inside the binding). This is the primary
   question this specification could only answer provisionally.
3. **Architect + ScientificAuditor** - decide whether a canonical Program A
   answer+tier emission component should be built (separate task; requires
   preregistration + ScientificAuditor sign-off). Until this exists, the
   binding is blocked at Step 2.
4. **Reviewer** - PASS on the eventual binding code (once Steps 2-3 are
   unblocked) and on the F-10 guard-gap fix if undertaken.
5. **Documentation** - correct the `program_a/` "LIVE" inaccuracy in
   `ARCHITECTURE_MAP.md` Section 1 row 6 (TD-13 pattern).

---

## 11. Verdict

**Implementation feasibility:** **INFEASIBLE as scoped.** No concrete
Program A binding can be implemented against the existing surfaces without
(a) inventing Program A architecture, (b) embedding scientific tier logic
in the adapter, or (c) binding `[REJECTED]` mechanisms - each of which is
forbidden by the brief, the preregistration, or the canon.

**Per the brief:** *"If implementation is feasible without inventing
scientific behavior, implement only the binding. Otherwise stop after the
specification."* -> **Stopped after the specification.** No production code
written. No production code changes to `experiments/`, `core/`,
`backend/`, or `program_a/`. No canonical-document edits. No parameter
changes. No tier computation, no calibration, no ECE, no rubric, no
decision logic.

**Return value:** **FAIL** - the binding cannot be implemented as scoped.
The specification is delivered; the implementation is blocked pending the
canonical Program A answer+tier emission component (Open item 3) and the
Architect location decision (Open item 1).

**Routing (handoff chain, no stage skipped):**
- This specification -> **Architect** (lawful location adjudication, Open
  item 1) -> **ScientificAuditor** (tier-source lawfulness PASS/FAIL, Open
  item 2) -> [canonical Program A answer+tier surface built as a separate
  preregistered task, Open item 3] -> **Builder** (implement the binding,
  Step 3) -> **Reviewer** (PASS on binding + F-10 guard-gap fix, Open item 4)
  -> **Documentation** (`ARCHITECTURE_MAP.md` correction, Open item 5) ->
  **ReleaseManager**.
- The Director does not override this FAIL. The work returns to the
  responsible agents with the exact reasons above.
