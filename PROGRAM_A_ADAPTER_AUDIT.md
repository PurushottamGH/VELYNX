# Program A Adapter Audit

**Status:** Director-implemented due to specialist runtime failure.

**Reason:** The Architect, ScientificAuditor, and Builder specialist agents
returned no output across all invocation attempts in this session (matching the
documented ScientificAuditor failure in `EXP1_TRACE.md`). This document is a
factual audit produced by the Director under explicit, one-time user
authorization (2026-07-07). It is NOT a formal Architect spec and NOT a formal
ScientificAuditor verdict. No specialist approvals are claimed or implied.

**Authority:** Director prerequisite verification, 2026-07-07. Every claim
verified against the file on disk this session and cited to file:line.

**Scope:** (1) inventory and assess the EXISTING Program A adapter framework at
`experiments/EXP1/program_a_adapter.py`; (2) document the prerequisite findings
that block a concrete retriever/synthesizer binding; (3) record the
user-approved re-scope to adapter-framework tests.

**Out of scope:** scientific lawfulness adjudication (ScientificAuditor
unavailable), architecture redesign (Architect unavailable), production code
changes, canonical-document edits, tier mapping, calibration, binding to
`backend/` or `[REJECTED]` mechanisms.

---

## 1. The adapter framework already exists (verified)

The brief requested "the complete Program A Adapter required for EXP-1 ...
responsible ONLY for converting Program A retrieval outputs into EXP-1
AnswerRecord objects ... deterministic, replay compatible, seed aware,
testable, dependency injected, side-effect free." The framework satisfying
these engineering properties already exists and is wired into the runner:

| Interface | File:line | Contract | Reuse |
|---|---|---|---|
| `ProgramAAdapter` Protocol | `experiments/EXP1/program_a_adapter.py:18-27` | `@runtime_checkable`; `adapter_id: str` property + `answer(query, seed) -> ProgramAAnswer` | unchanged |
| `ProgramAAnswer` alias | `program_a_adapter.py:15` | `AnswerRecord \| Mapping \| Awaitable` | unchanged |
| `CallableProgramAAdapter` | `program_a_adapter.py:30-44` | frozen dataclass; wraps any `answer_fn`; validates `adapter_id` non-empty + `answer_fn` callable | unchanged |
| `callable_identity` | `program_a_adapter.py:47-52` | deterministic `"{module}.{qualname}"` for manifest identity | unchanged |
| `coerce_program_a_adapter` | `program_a_adapter.py:55-76` | normalizes explicit adapter vs legacy `answer_fn`; all error branches | unchanged |
| `AnswerRecord` | `experiments/EXP1/dataset.py:101-151` | requires `tier in CONFIDENCE_TIERS` (line 17); optional `seed`, `raw_numeric_confidence`, `metadata` | unchanged |
| `QueryRecord` | `dataset.py:33-81` | frozen query + gold rubric; `query_family in QUERY_FAMILIES` | unchanged |
| `_coerce_answer_record` | `experiments/EXP1/run.py:242-258` | coerces `AnswerRecord`/`Mapping` to `AnswerRecord`; validates query_id + seed match | unchanged |
| `_maybe_await` | `run.py:236-239` | awaits awaitable adapter/adjudicator returns | unchanged |
| Runner injection points | `run.py:50-70, 114-134` | `answer_fn` / `program_a_adapter` injected by caller | unchanged |

`CallableProgramAAdapter` already IS a thin, dependency-injected concrete
binding around an externally-injected answer function. It is deterministic
(frozen dataclass, no hidden state), seed-aware (`answer(query, seed)`), and
side-effect free (delegates verbatim to `answer_fn`). **No new adapter class is
required.**

---

## 2. Prerequisite findings (verified against disk)

| # | Finding | Citation |
|---|---|---|
| F-1 | `program_a/retrieval/` is an EMPTY stub (0-byte `__init__.py`). `program_a/` contains only `retrieval/` + `nlp/`, both empty. | glob `program_a/**/*.py`; `program_a/retrieval/__init__.py` (0 bytes) |
| F-2 | `ARCHITECTURE_MAP.md` row 6 claims `program_a/` is "LIVE" with "Unified retriever (Arxiv, Brave, DuckDuckGo, etc.)" — INACCURATE (TD-13-style parallel skeleton). | `ARCHITECTURE_MAP.md:54` |
| F-3 | The real retriever `UnifiedRetriever.retrieve() -> RetrievalReport` emits ONLY `query`, `sources` (url/title/snippet/source/score), `attempts`, `elapsed`. **No answer text. No confidence tier.** `RetrievalSource.score` is heuristic retrieval relevance, not answer confidence. | `backend/retrieval/unified_retriever.py:154,43-58` |
| F-4 | `AnswerSynthesizer.synthesize() -> SynthesisResult` emits `confidence_label` from a 5-grade enum `{CERTAIN, PROBABLE, UNCERTAIN, SPECULATIVE, INSUFFICIENT}` (bands 0.90/0.70/0.50/0.25/0.00). This does NOT match the EXP-1 canonical 4-tier set `{UNKNOWN, DEBATED, PROBABLE, CERTAIN}`. | `backend/cognition/answer_synthesizer.py:32-47,106` |
| F-5 | `AnswerSynthesizer` depends on a `ReasoningTrace` (reasoning engine), `thermodynamic_state`, and a knowledge graph `kg` — all marked `[REJECTED]` by the canon. Binding it into the live EXP-1 path would realize the TD-08 risk. | `answer_synthesizer.py:106-133`; `PROGRAM_D_CANONICAL.md:90` |
| F-6 | Dependency boundary rule: `experiments/` MUST NOT import `backend/` except via the `research/` composition layer. A concrete retriever/synthesizer binding therefore cannot live in `experiments/EXP1/`. | `.agents/skills/velynx-core/architecture.md` Section 4 rule 2 |
| F-7 | Preregistration rejects: "scoring retrieval relevance as answer correctness"; "source confidence as answer confidence"; "post-hoc tier remapping"; "post-hoc calibration: Prohibited". | `EXP1_PREREGISTRATION.md` Sections 4, 5, 6 |
| F-8 | The missing concrete adapter binding is already documented as ML-1 / TD-06. | `EXP1_TRACE.md` Link 1; `TECHNICAL_DEBT.md` TD-06 |
| F-9 | Existing EXP-1 test coverage exercises the adapter only THROUGH the runner (`test_exp1_run.py`) plus one identity test (`test_exp1_readiness.py:174`). No dedicated unit suite for `program_a_adapter.py` itself. | `tests/EXP1/test_exp1_run.py`, `tests/EXP1/test_exp1_readiness.py` |

---

## 3. Contract gap - no lawful canonical tier source

The brief asks the adapter to "convert Program A retrieval outputs into EXP-1
`AnswerRecord` objects." An `AnswerRecord` requires `answer: str` and
`tier in {UNKNOWN, DEBATED, PROBABLE, CERTAIN}`. No existing Program A surface
lawfully emits both:

- `UnifiedRetriever` emits sources only — no answer, no tier. Using
  `RetrievalSource.score` as a tier basis is the "scoring retrieval relevance
  / source confidence as answer confidence" category error rejected by
  `EXP1_PREREGISTRATION.md` Section 5.
- `AnswerSynthesizer` emits a 5-grade label that does not match the canonical
  4-tier set; mapping 5-grade -> 4-tier inside the adapter is "post-hoc tier
  remapping" (a Section 4 kill criterion) and "scientific logic" the brief
  forbids. Binning its `confidence` float is "post-hoc calibration"
  (Section 6, prohibited).
- `AnswerSynthesizer` sits on `[REJECTED]` science (canon Section 5 line 90);
  binding it into the live EXP-1 path is a canonical violation (TD-08).

**Director's provisional conclusion (NOT a ScientificAuditor verdict):** a
concrete adapter binding against existing Program A surfaces is infeasible as
scoped without (a) inventing Program A architecture, (b) embedding scientific
tier logic in the adapter, or (c) binding `[REJECTED]` mechanisms. The adapter
the brief describes already exists as `CallableProgramAAdapter`. The true
missing piece is a Program A answer+tier emission surface that emits canonical
tiers — a separate Program A / scientific-path concern requiring its own
preregistration and ScientificAuditor sign-off, not an adapter task.

---

## 4. Re-scope decision (user-approved, 2026-07-07)

Because the adapter framework already satisfies the brief's engineering
properties and a concrete retriever/synthesizer binding is infeasible without
violating the brief or the canon, the task is re-scoped to:

- **Tests only** for the existing `CallableProgramAAdapter` /
  `ProgramAAdapter` / `coerce_program_a_adapter` / `callable_identity`
  framework.
- No production code changes. No new adapter class. No retriever/synthesizer
  binding. No tier computation. No canonical-document edits. No parameter
  changes. No architecture changes.
- All tiers come from an externally-injected canonical `answer_fn`; the
  adapter only passes them through.

Deliverables for the re-scope: this audit, `PROGRAM_A_ADAPTER_TEST_PLAN.md`,
and the test files under `tests/EXP1/`.

---

## 5. What this audit does NOT do

- No production-code changes to `experiments/`, `core/`, `backend/`, or
  `program_a/`.
- No scientific lawfulness adjudication (ScientificAuditor unavailable).
- No architecture redesign (Architect unavailable).
- No tier mapping, calibration, ECE, rubric, scoring, decision, or replay
  logic.
- No edits to `PROGRAM_D_CANONICAL.md`, `EXP1_PREREGISTRATION.md`,
  `HYPOTHESIS_REGISTER.md`, or any preregistration.
- No binding to `backend/` or `[REJECTED]` mechanisms.
- No fabricated specialist approvals.

---

## 6. Open items requiring specialist sign-off when agents are available

1. Formal Architect `PROGRAM_A_ADAPTER_SPEC.md` adjudicating the seam and the
   concrete-binding location (given the dependency boundary).
2. Formal ScientificAuditor PASS/FAIL on tier-source lawfulness (the primary
   question this audit could only answer provisionally).
3. Formal Reviewer PASS on the test code in this re-scope.
4. Discharge of the PROVISIONAL Goodhart-guard categorization in
   `EXP1_TRACE.md` (active detector required vs. passive locked-bins + flag).
5. Documentation correction of the `program_a/` "LIVE" inaccuracy in
   `ARCHITECTURE_MAP.md` Section 1 row 6 (and the parallel TD-13 pattern).
6. Decision on whether a canonical Program A answer+tier emission component
   should be built (separate task; requires preregistration + ScientificAuditor
   sign-off).

---

## 7. Observation discovered during testing (2026-07-07)

**F-10 (observed):** The `AnswerRecord` dataclass
(`experiments/EXP1/dataset.py:101-151`) does NOT call `validate()` in its
generated `__init__`. Tier validation is enforced only at the `from_mapping`
boundary (`dataset.py:134`). Consequently:

- `AnswerRecord.from_mapping({"tier": "INSUFFICIENT"})` raises `ValueError`
  (the guard that protects the runner's Mapping coercion path).
- `AnswerRecord(query_id=..., answer=..., tier="INSUFFICIENT")` direct
  construction does NOT raise.

Implication for the adapter: an injected `answer_fn` that returns an
`AnswerRecord` *instance* with a non-canonical tier bypasses the
non-canonical-tier guard, because `_coerce_answer_record`
(`experiments/EXP1/run.py:242-258`) accepts an `AnswerRecord` instance without
re-validating its tier. The non-canonical tier would propagate until
`calibration.confidence_for_tier` raises a `KeyError` downstream.

This is documented as observed behavior (test
`test_direct_construction_does_not_validate_tier`), NOT fixed. Fixing it
(adding `validate()` to `AnswerRecord.__post_init__`, or re-validating in
`_coerce_answer_record`) is a production-code change that is out of scope for
this test-only re-scope and would require Reviewer + ScientificAuditor
sign-off. It is added to Section 6 for specialist attention.
