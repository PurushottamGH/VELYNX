# PROGRAM A — FINAL PRODUCTION ARCHITECTURE

**Authority:** Lead Systems Architect, 2026-07-08.
**Function:** the production architecture of Program A itself — the public-facing
deterministic retrieval system that EXP-1 evaluates. This document *defines
structure*; it invents no science. The confidence mechanism is ES-1 exactly as
designed (`PROGRAM_A_CONFIDENCE_MECHANISM.md` §7); the binding is exactly as
specified (`PROGRAM_A_BINDING_SPEC.md` §4–§7); the dataset is exactly as
specified (`EXP1_DATASET_SPEC.md`); the evaluation contract is exactly as
preregistered (`EXP1_PREREGISTRATION.md`). Nothing here redesigns any of them.
**Derives from:** `PROGRAM_D_CANONICAL.md` (§2, §3, §6-H1, §7, `:90`),
`PROGRAM_A_MASTER_SPECIFICATION.md`, `PROGRAM_A_ARCHITECTURE.md`,
`PROGRAM_A_PUBLIC_API.md`, `PROGRAM_A_CONFIDENCE_MECHANISM.md` (+
REQUIREMENTS/DECISION_TREE/RISKS companions), `PROGRAM_A_BINDING_SPEC.md`,
`PROGRAM_A_DEPENDENCY_GRAPH.md`, `EXP1_DATASET_SPEC.md`,
`EXP1_PREREGISTRATION.md`, and the code on disk (verified 2026-07-08).
**Companion deliverables:** `PROGRAM_A_MODULE_SPEC.md`,
`PROGRAM_A_IMPLEMENTATION_ORDER.md`, `PROGRAM_A_BUILD_CHECKLIST.md`.
**Governance status:** This architecture does not self-authorize
implementation. The ES-1 implementation gate (`ES1_IMPLEMENTATION_GATE.md`)
stands: **NO-GO until A1–A4 ∧ B1–B3 ∧ C1–C3 are discharged by real
specialists.** This document is the Architect-side input those gates consume
(in particular G1/Q4, the location ruling, is resolved here as an
architectural proposal for ratification).

---

## 0. Disk-state corrections carried into this architecture (verified 2026-07-08)

1. **F-10 is FIXED on disk.** `AnswerRecord.__post_init__` now calls
   `validate()` (`experiments/EXP1/dataset.py:112-122`), closing the
   direct-construction tier bypass every prior document lists as open
   (roadmap T6, gate box C2's substance). Documents still describing F-10 as
   open are stale, not this one.
2. **CR-3 sentinel-substitution test exists.** `tests/EXP1/
   test_cheat_channel_guard.py` is on disk and green against a conforming
   stub (`PROGRAM_A_CONFIDENCE_REQUIREMENTS.md` CR-3 verification note) —
   gate box C1's substance, pending re-run against the real surface.
3. **`program_a/` remains empty** (0-byte `retrieval/__init__.py`,
   `nlp/__init__.py`) and is **not** in `pyproject.toml` packages.find (R-16).
4. The EXP-1 framework (`experiments/EXP1/{dataset,run,calibration,decision,
   manifest,program_a_adapter}.py`) is implemented and tested; `report.py`/
   `artifact_specs.py` exist but are unwired (TD-05); the frozen 210-row
   dataset and the rubric adjudicator do not exist (ML-5, ML-4). These are
   EXP-1-side obligations, not Program A subsystems, and are referenced only
   as external contracts.

---

## 1. What Program A is (one paragraph, binding)

Program A is a **stateless, deterministic, evidence-structural
question-answering surface**. Given one query string and one explicit integer
seed, it (1) acquires evidence from a frozen retrieval corpus, (2) extracts
candidate claims deterministically, (3) classifies the evidence into exactly
one of the four ES-1 corroboration states S0–S3, (4) constructs the answer
text in the form that state mandates, and (5) emits the tier that state
mandates (`UNKNOWN`/`DEBATED`/`PROBABLE`/`CERTAIN`). The answer and the tier
come from the *same* state (CR-9). It writes nothing, learns nothing,
remembers nothing across queries, and exposes exactly one public function
plus a stable identity string. EXP-1 consumes it through a ~20-line binding
that performs pure field transport into `AnswerRecord`.

## 2. Location ruling (Q4 / G1 — architectural decision, for Architect ratification)

**Decision: `program_a/` — populate the package that canon §9-DeepSeek
ordered and that already exists as an empty skeleton.**

Rationale (over `research/` and `scripts/`):
- Canon §9-DeepSeek's intended split names `program_a/` as Program A's home;
  populating it completes an ordered migration rather than adding a third
  parallel location (`PROGRAM_A_ARCHITECTURE.md` §2 option 2).
- Program A is the *product deliverable* (canon §3 deliverable 1). `research/`
  is a composition layer for research harnesses; a durable public product
  surface homed there conflates the product with the research center the
  canon explicitly separates (canon `:42`). `scripts/` "leaves the product
  surface homeless" (`PROGRAM_A_ARCHITECTURE.md` §2).
- Boundary-legal: `program_a/` may import `backend.retrieval` (only
  `experiments/` is barred from `backend/`; architecture.md §4 rule 2), and
  the binding's two `experiments.EXP1` imports (`dataset`, `program_a_adapter`)
  are legal from anywhere (`PROGRAM_A_DEPENDENCY_GRAPH.md` §3).
- Also corrects the `ARCHITECTURE_MAP.md:54` "LIVE" fiction by making it true.

Cost accepted: one `pyproject.toml` packaging addition (`program_a*` to
packages.find) — R-16, a one-line reviewed change.

Consequent boundary rule (new, binding): **`program_a/` may import `core/`,
`backend.retrieval`, and stdlib. Nothing else.** (With the sole exemption of the binding subpackage `program_a/binding/` which is permitted to import `experiments.EXP1.{dataset,program_a_adapter}` types to implement the adapter interface). `experiments/` never imports
`program_a/` (runner stays injection-only); `program_a/` never imports
`experiments.EXP1.{calibration,decision}` and never imports any deny-listed
module (§7 below). The binding module is the single sanctioned point where
`program_a/` code touches `experiments.EXP1.{dataset,program_a_adapter}` types.

## 3. Subsystem decomposition

Program A contains exactly **six subsystems** plus one out-of-path product
shell. No seventh subsystem is permitted without a preregistered experiment
that requires it (canon §1 rule 2).

```
                    PROGRAM A  (package: program_a/)
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│  PA-1 Evidence Acquisition (snapshot store + snapshot-backed retriever)│
│        │  EvidenceSet (ordered, provenance-tagged snippets)            │
│        ▼                                                               │
│  PA-2 Claim Extraction (deterministic candidate-claim construction)    │
│        │  CandidateClaims                                              │
│        ▼                                                               │
│  PA-3 Evidence-State Classification (ES-1: support/contradiction/      │
│        independence tests → exactly one state S0–S3)                   │
│        │  EvidenceState + support/contradiction sets                   │
│        ▼                                                               │
│  PA-4 Emission (answer construction + tier, both from the state;       │
│        the public surface — one function, one identity)                │
│        │  Emission(answer: str, tier: str, metadata)                   │
│        ▼                                                               │
│  PA-5 Binding (Form A answer_fn → AnswerRecord mapping; EXP-1 seam)    │
│                                                                        │
│  PA-6 Conformance Guard (import deny-list test, determinism/purity/    │
│        input-restriction tests, replay harness — test-side subsystem)  │
└────────────────────────────────────────────────────────────────────────┘
   PA-7 Product shell (CLI/API presentation; OUT of the EXP-1 path;
        deferred — no experiment requires it; listed only to fence it off)
```

The pipeline is a strict linear dataflow. PA-3 and PA-4 jointly *are* ES-1;
they are separated so that the frozen rule (state definitions, precedence
S0 → S1 → (S2|S3), tier map, answer-form coupling) lives in exactly one
place (PA-3/PA-4) while retrieval mechanics (PA-1) and text mechanics (PA-2)
stay science-free.

---

## 4. Subsystem specifications

Each subsystem: responsibility · inputs · outputs · deterministic guarantees ·
replay guarantees · public API · internal interfaces · forbidden dependencies ·
testing requirements. (Signatures are contracts, not code; exact module/file
layout is in `PROGRAM_A_MODULE_SPEC.md`.)

### PA-1 — Evidence Acquisition

- **Responsibility:** produce the complete, ordered, provenance-tagged
  evidence set for one query from a **frozen retrieval snapshot** (Q2
  resolution recommended by CF-R4 and required for byte-identical replay;
  live mode exists only behind an explicit non-EXP-1 flag in the product
  shell, never in the experimental path). Owns snapshot loading, integrity
  verification (SHA-256 against a snapshot manifest), query→document lookup,
  and deterministic ordering. It is the *only* subsystem that knows where
  evidence comes from.
- **Inputs:** `query_text: str`; snapshot path + snapshot manifest (frozen
  assets, read-only — Q7 read-scope: frozen assets readable, mutable stores
  not); `seed: int` (accepted for interface uniformity; unused unless the T1
  spec declares a seed-variance source per Q3/CR-15).
- **Outputs:** `EvidenceSet` — ordered sequence of evidence items, each
  `{doc_id, origin_domain, title, text, snapshot_hash_ref}`. **The retrieval
  relevance `score` field is deliberately absent from `EvidenceSet`** —
  structurally enforcing the prereg §5 prohibition (retrieval relevance must
  never flow toward the tier; DATAFLOW §3 row 1). No timestamps in the output
  (wall-clock is a determinism leak, MASTER_SPEC §8 RISK).
- **Deterministic guarantees:** identical `(query_text, snapshot)` →
  byte-identical `EvidenceSet`. Ordering is a frozen total order (e.g.
  lexicographic on `(origin_domain, doc_id)` — exact rule frozen in T1's
  free-constant register). No network access, no env-var-gated sources, no
  wall-clock reads in EXP-1 mode.
- **Replay guarantees:** snapshot identity (aggregate SHA-256) is part of the
  mechanism identity string (CR-12/Q8 interim rule); a re-run against the same
  snapshot hash reproduces the same `EvidenceSet` bytes; snapshot mutation is
  detectable before execution (pre-run integrity check).
- **Public API (package-internal):**
  `SnapshotStore.load(path) -> SnapshotStore` (verifies manifest);
  `SnapshotStore.evidence_for(query_text: str) -> EvidenceSet`.
- **Internal interfaces:** consumes the snapshot artifact format (defined in
  MODULE_SPEC §PA-1); optionally *builds* snapshots offline via a separate
  build tool that MAY drive `backend/retrieval/unified_retriever.py` — the
  builder runs before freeze, outside the execution path, and its output
  passes the documented leakage review (CF-R4 disposition, ES-1 gate A3).
- **Forbidden dependencies:** at execution time — `backend.*` entirely
  (the retriever is builder-side only), network, `time`/`datetime` for
  output values, env vars. Always — the §7 deny-list.
- **Testing requirements:** snapshot integrity-failure rejection; determinism
  (two loads → identical `EvidenceSet` bytes); no-network assertion in EXP-1
  mode (socket-guard fixture); ordering stability under permuted snapshot
  file order; absence of `score`/timestamp fields in the output type.

### PA-2 — Claim Extraction

- **Responsibility:** deterministically construct the candidate-claim set
  from the evidence — the "candidate claims extracted deterministically from
  retrieved content answering the query" of ES-1 §7.1. Pure text mechanics:
  no state logic, no tier knowledge.
- **Inputs:** `query_text: str`, `EvidenceSet`.
- **Outputs:** `CandidateClaims` — ordered claims, each
  carrying `claim_text: str` and `supporting_doc_ids: tuple[str, ...]` (refs into the `EvidenceSet` by
  `doc_id`).
- **Deterministic guarantees:** identical inputs → identical output; frozen
  extraction procedure (its parameters go in the T1 free-constant register,
  CR-11); no randomness, no model calls (hosted-LLM extraction is unlawful —
  M8; a frozen local model is not in the repository and is out of scope).
- **Replay guarantees:** follows from determinism + PA-1's replay guarantee;
  extraction-procedure version is folded into the mechanism identity.
- **Public API (package-internal):**
  `extract_claims(query_text: str, evidence: EvidenceSet) -> CandidateClaims`.
- **Internal interfaces:** `EvidenceSet` from PA-1 only.
- **Forbidden dependencies:** the §7 deny-list; any network/model provider;
  `experiments.*`.
- **Testing requirements:** determinism; empty-evidence → empty claims;
  junk/topically-related-but-non-answering evidence yields no claim (the
  CF-R2 pressure case — entity-level rather than topic-level match, the
  design point where FM-1 risk concentrates); property test that every
  claim's refs exist in the evidence set.

### PA-3 — Evidence-State Classification (the frozen ES-1 core, part 1)

- **Responsibility:** implement, verbatim from the frozen T1 preregistration,
  the ES-1 evidence-state partition: the claim-support test, the
  contradiction/materiality test, the source-independence relation, claim
  selection, and the state decision S0–S3 with frozen precedence
  S0 → S1 → (S2|S3) (DECISION_TREE Tree 2). This subsystem contains **all**
  of ES-1's free constants (§7.4 register: ≥2-independent-origins threshold,
  independence relation, support test, materiality rule) and nothing else
  contains any of them.
- **Inputs:** `query_text: str`, `EvidenceSet`, `CandidateClaims`.
- **Outputs:** `EvidenceStateResult` — `{state ∈ {S0,S1,S2,S3},
  selected_claim | None, support_doc_ids, contradiction_doc_ids,
  independent_origin_count}`. `selected_claim` is governed by
  `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` §A1 (selection) and §A2
  (deterministic tie-break): it is `None` iff `state == S0`, otherwise the
  non-`None` §A1/§A2 winner. `support_doc_ids` and
  `contradiction_doc_ids` are computed **with respect to the selected claim**
  from claim support, never from source rank (M10 lawfulness condition), and
  follow the §A7 seam invariant / witness table. In S1, §A4 anchors
  `support_doc_ids` to the supporters of `selected_claim` and
  `contradiction_doc_ids` to the supporters of the material-incompatible
  competing claim; PA-4 represents both alternatives and asserts neither.
- **Addendum pointers:** PA-3 behavior is closed by
  `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` §A1 (claim selection), §A2
  (tie-break), §A4 (S1 contradiction composition and anchoring), and §A7
  (`selected_claim` seam / I-1 through I-3 witness invariants).
- **Deterministic guarantees:** identical inputs → identical state; exactly
  one state fires per query (states partition the corroboration structure —
  Tree 2 invariant); all thresholds frozen a-priori, none data-fitted (CR-11);
  contains **no probability numbers** and no knowledge of
  0.125/0.375/0.625/0.875 or bin boundaries (L8 compliance by construction,
  MECHANISM §7.3).
- **Replay guarantees:** the rule is a one-page frozen table (C6 auditability);
  the implementing module's version = the T1 spec version, encoded in the
  mechanism identity string; any change to this subsystem REQUIRES a new T1
  revision + re-freeze + new `adapter_id` (CR-6, CR-12).
- **Public API (package-internal):**
  `classify(query_text, evidence, claims) -> EvidenceStateResult`.
- **Internal interfaces:** PA-1/PA-2 output types only.
- **Forbidden dependencies:** §7 deny-list; `experiments.EXP1.calibration`
  and `experiments.EXP1.decision` (no tier→p_i knowledge, no gate knowledge —
  DEPENDENCY_GRAPH §4); any input beyond the three listed (in particular:
  never `QueryRecord` — this subsystem must be *typed* below the level at
  which `gold_rubric`/`query_family` exist, making the L11/CR-3 cheat channel
  unreachable by construction, not just by discipline).
- **Testing requirements:** one table-driven test per state with minimal
  synthetic evidence; mutual-exclusion/exhaustiveness property test (every
  input reaches exactly one state); precedence-order test; independence-
  relation tests (mirror domains counted once); materiality test (trivial
  variation ≠ contradiction); fabrication-pressure tests (nonexistent-entity
  probes must land S0, not S2/S3 — CF-R2, the FM-1 guard); frozen-constant
  audit test (constants imported from a single frozen-constants module whose
  hash is asserted).

### PA-4 — Emission (the frozen ES-1 core, part 2; the public surface)

- **Responsibility:** produce the public `(answer, tier)` from the
  `EvidenceStateResult` — the answer-construction rule and tier map of ES-1
  §7.2, one fixed tier per state, answer form coupled to the state (CR-9):
  S0 → explicit unsupported/unknown/false-premise response, asserts no fact,
  `UNKNOWN`; S1 → qualified answer representing the alternatives, asserts no
  single resolution, `DEBATED`; S2 → single hedged source-attributed answer,
  `PROBABLE`; S3 → single asserted source-attributed answer, `CERTAIN`.
  Owns the mechanism identity string. This is Program A's entire public
  surface.
- **Inputs (public):** `query_text: str`, `seed: int`.
- **Outputs (public):** `Emission` — `{answer: str, tier: str ∈
  CONFIDENCE_TIERS, raw_numeric_confidence: None, metadata: {state,
  independent_origin_count, snapshot_hash, mechanism_version}}`.
  `raw_numeric_confidence` is emitted as `None` under ES-1 (the mechanism
  contains no numeric confidence; prereg §1 line 35 makes it exploratory-only
  anyway).
- **Deterministic guarantees:** identical `(query_text, seed)` → identical
  `Emission`; stateless across calls (a fresh classification per call; no
  caches that observe call order); side-effect-free (no DB writes, no
  telemetry in the measured path, no mutation of inputs — CR-5); answer–tier
  consistency is structural: both fields derive from one `EvidenceStateResult`
  and there is no code path that sets them independently (CR-9).
- **Replay guarantees:** `mechanism_id() -> str` returns the stable identity
  `"program-a-public-v1+es1-{SPEC_VERSION}+const-{frozen_constants_digest[:8]}+snap-{snapshot_aggregate_hash[:8]}"`
  (CR-12/Q8 interim: spec version in the id until the Q8 ruling); identical
  id ⇒ identical mechanism ⇒ identical outputs for identical inputs.
- **Public API:**
  `answer_query(query_text: str, seed: int) -> Emission` and
  `mechanism_id() -> str`. **These two callables are Program A's complete
  public API.** Everything in PA-1..PA-3 is package-internal.
- **Internal interfaces:** PA-3's `classify`; answer-text templates (frozen
  wording patterns per state, listed in the T1 spec so the "explicit
  unsupported/unknown" and "represents the alternatives" rubric-facing forms
  are frozen, not improvised at run time).
- **Forbidden dependencies:** §7 deny-list; `experiments.*` (the public
  surface must be importable with zero experiment knowledge); `QueryRecord`
  (input is a plain string — the structural L11 guard).
- **Testing requirements:** determinism + purity
  (`test_answer_is_deterministic_and_side_effect_free` pattern applied to the
  real surface — CR-4 verification); per-state answer-form invariant tests
  (CR-9 verification: assertion-bearing text never co-occurs with
  `UNKNOWN`/`DEBATED`; `CERTAIN` only with `state == S3`); tier ∈
  CONFIDENCE_TIERS for all inputs; ≥2 tiers reachable across a synthetic
  three-family corpus (CR-14 design check, pre-freeze only); identity-string
  stability test.

### PA-5 — Binding (the EXP-1 seam)

- **Responsibility:** pure field transport from PA-4's `Emission` into the
  EXP-1 `AnswerRecord` contract — BINDING_SPEC §4 **Form A** (an `answer_fn`;
  chosen over Form B because `CallableProgramAAdapter` already *is* the
  adapter class and the audit's verdict is "no new adapter class required").
  ~20 lines. Computes nothing: no tier logic, no mapping, no calibration, no
  rubric, no decision logic (BINDING_SPEC out-of-scope list).
- **Inputs:** `query: QueryRecord`, `seed: int` (the runner's call shape,
  `run.py:84,181`).
- **Outputs:** a `Mapping` — `{"query_id": query.query_id, "answer":
  emission.answer, "tier": emission.tier, "seed": seed,
  "raw_numeric_confidence": None, "metadata": emission.metadata}` — returned
  as a mapping so the runner's `_coerce_answer_record` →
  `AnswerRecord.from_mapping` path validates it (CR-13; belt-and-suspenders
  even though F-10 is now fixed on disk).
- **Deterministic guarantees:** inherits PA-4's exactly; adds none; loses
  none. **Reads only `query.query` and `query.query_id`** — the L11/CR-3
  restriction is enforced here (this is the only module that ever sees a
  `QueryRecord`) and verified by the existing sentinel-substitution test
  rebound to this function.
- **Replay guarantees:** injected as
  `run_experiment(answer_fn=program_a_answer_fn,
  program_a_adapter_id=mechanism_id(), ...)`; the manifest records the id
  (`manifest.py:29`); manifest identity-equality checks (`run.py:147-148`)
  then detect mechanism drift across replays.
- **Public API:** `program_a_answer_fn(query: QueryRecord, seed: int) ->
  Mapping[str, Any]` plus re-export of `mechanism_id`.
- **Internal interfaces:** PA-4 public API;
  `experiments.EXP1.dataset.QueryRecord` (type only);
  `experiments.EXP1.program_a_adapter` types (for callers constructing the
  runner arguments).
- **Forbidden dependencies:** §7 deny-list;
  `experiments.EXP1.{calibration,decision,run}` (the binding is injected *by*
  the caller into the runner, never imports the runner);
  `query.gold_rubric` / `query.query_family` / `query.metadata` reads.
- **Testing requirements:** end-to-end through `run_seed_sync` on a synthetic
  non-frozen corpus (existing integration pattern,
  `tests/EXP1/test_program_a_adapter_integration.py`); sentinel-substitution
  test against this function (CR-3; extends the existing
  `test_cheat_channel_guard.py`); field-transport fidelity (output mapping ≡
  Emission fields, nothing added or computed); seed echo.

### PA-6 — Conformance Guard (test-side subsystem; no runtime footprint)

- **Responsibility:** mechanically enforce the boundaries this architecture
  declares, so conformance does not rest on discipline (TD-08's lesson).
  Owns: the import-guard test (deny-list over the transitive import closure
  of `program_a/` — roadmap T7 / gate C3), the determinism/purity/replay
  harness, the input-restriction (sentinel) test, and the fabrication-pressure
  dry-run suite (T10's mechanics, W4.2: no `CERTAIN` on fabricated-claim
  probes, ≥2 tiers reachable, byte-identical replay, full artifact set).
- **Inputs:** the `program_a` package; the §7 deny-list; synthetic non-frozen
  corpora with fabrication pressure.
- **Outputs:** CI pass/fail. No artifacts consumed by the run.
- **Deterministic/replay guarantees:** n/a (it *verifies* them).
- **Public API:** none (pytest modules under `tests/program_a/`).
- **Internal interfaces:** imports `program_a` and walks `sys.modules` /
  import graph; uses the EXP-1 runner for the end-to-end dry run.
- **Forbidden dependencies:** none beyond not touching frozen rows — **all
  Guard corpora are synthetic and disjoint from the frozen dataset**
  (dataset-spec §12.2–12.3; the B-11 scope limit: dry-run results may trigger
  return-to-Wave-2 redesign+refreeze, never in-place tuning).
- **Testing requirements:** self-tests that the import guard actually fails
  on a planted forbidden import (guard-of-the-guard).

### PA-7 — Product shell (fenced off; NOT built now)

- **Responsibility:** eventual user-facing presentation (CLI/HTTP) over PA-4.
  **No preregistered experiment requires it, therefore it is not built**
  (canon §1 rule 2). Recorded solely to pin the rule that any future shell
  sits strictly *above* PA-4's public API, adds no confidence logic, performs
  persistence/telemetry only outside the measured path (MASTER_SPEC §10–§11),
  and may enable live retrieval only outside EXP-1 execution.

---

## 5. Dataflow with guards (end-to-end, EXP-1 mode)

```
query.query ── PA-5 reads .query/.query_id ONLY (L11; sentinel-tested)
   │
   ▼
PA-1  SnapshotStore.evidence_for(query_text)
   │    guard: no score field, no timestamps, no network (structural)
   ▼  EvidenceSet
PA-2  extract_claims(query_text, evidence)
   │    guard: entity-level matching; no model calls
   ▼  CandidateClaims
PA-3  classify(query_text, evidence, claims)
   │    guard: all ES-1 constants live here, frozen; no probability numbers;
   │           no QueryRecord type in scope (structural L11)
   ▼  EvidenceStateResult (exactly one of S0..S3)
PA-4  answer + tier from the SAME state (CR-9 structural)
   │    S0→UNKNOWN · S1→DEBATED · S2→PROBABLE · S3→CERTAIN
   ▼  Emission
PA-5  mapping{query_id, answer, tier, seed, None, metadata}
   │    guard: pure transport; validated via from_mapping downstream
   ▼
experiments/EXP1/run.py  (existing, unchanged: coercion → adjudicator →
                          ECE → decision → manifest)
```

Data that must NOT flow (inherited verbatim from `PROGRAM_A_DATAFLOW.md` §3,
now structurally enforced where marked): retrieval score → tier
(*structural*: field absent); 5-grade labels → tier (*structural*:
`AnswerSynthesizer` never imported); confidence float → binned tier
(*structural*: no float exists); family/rubric → tier (*structural*: types
below `QueryRecord`); frozen rows → tuning (process + Guard corpora
disjointness); EXP-1 outputs → any constant (governance, CR-6/CR-7).

## 6. Determinism & replay model (consolidated)

| Layer | Source of variation eliminated | Mechanism |
|---|---|---|
| Evidence | live web, timeouts, env keys, wall clock | frozen snapshot + integrity hash; no network in EXP-1 mode |
| Extraction/classification | randomness, model calls | pure frozen rules; constants in one hashed module |
| Emission | hidden state, call order | stateless per call; frozen templates |
| Binding | field drift | pure transport; `from_mapping` validation |
| Run identity | mechanism drift across replays | `mechanism_id()` = adapter_id in manifest; equality-checked on replay (`run.py:147-148`) |
| Dataset | row drift | `order_hash` verified per replicate (existing) |

**Forced consequence (Q3/CF-R5, restated as an architectural fact):** this
architecture is fully deterministic per `(query, seed)`; with a frozen
snapshot, all 22 replicates are byte-identical. Prereg §7's own amendment
clause therefore **must be invoked before execution** (gate A4). The
architecture does not manufacture fake seed variance to dodge this — that
would be an undeclared constant of exactly the kind CR-11 forbids.

## 7. Forbidden-dependency deny-list (binding on PA-1..PA-6; enforced by PA-6)

Verbatim from `PROGRAM_A_DEPENDENCY_GRAPH.md` §4, extended with the
structural additions of this architecture:

```
program_a.**  ✗→  backend.cognition.answer_synthesizer
program_a.**  ✗→  backend.cognition.reasoning_engine
program_a.**  ✗→  backend.cognition.dream_state
program_a.**  ✗→  backend.soul.*
program_a.**  ✗→  backend.self_model.*
program_a.**  ✗→  research.policies.free_energy
program_a.**  ✗→  experiments.EXP1.calibration     (no tier→p_i knowledge)
program_a.**  ✗→  experiments.EXP1.decision        (no gate knowledge)
program_a.**  ✗→  experiments.EXP1.run             (injection-only seam)
program_a.{PA-1..PA-4} ✗→ experiments.*            (only PA-5 touches EXP1 types)
program_a.** (EXP-1 mode) ✗→ network, env-keyed sources, wall-clock outputs
experiments.EXP1.*  ✗→  program_a.*                (runner stays injection-only)
experiments.EXP1.*  ✗→  backend.*                  (boundary rule, standing)
```

`backend.retrieval.unified_retriever` is permitted **only** to the offline
snapshot builder (PA-1 builder-side), never to the execution path.

## 8. Testing architecture (consolidated requirements → suites)

| Suite | Verifies | Gate/CR discharged |
|---|---|---|
| `tests/program_a/test_snapshot_store.py` | PA-1 integrity, determinism, no-network, ordering | CR-4/CR-5 (evidence layer) |
| `tests/program_a/test_claim_extraction.py` | PA-2 determinism, fabrication-pressure negatives | CF-R2 (first line) |
| `tests/program_a/test_evidence_states.py` | PA-3 state table, precedence, exclusivity, constants hash | T1 conformance, CR-11 |
| `tests/program_a/test_emission.py` | PA-4 determinism/purity, CR-9 answer-form invariants, tier coverage on synthetic corpus | CR-4/5/9/14 |
| `tests/program_a/test_binding.py` + extended `tests/EXP1/test_cheat_channel_guard.py` | PA-5 transport fidelity, L11 sentinel test, end-to-end `run_seed_sync` | CR-3 (gate C1), CR-13 |
| `tests/program_a/test_import_guard.py` | §7 deny-list over transitive closure + guard-of-the-guard | TD-08 (gate C3) |
| `tests/program_a/test_replay.py` | byte-identical re-run incl. artifacts on synthetic corpus | MASTER_SPEC §9 (T10 mechanics) |
| existing `tests/EXP1/*` (64 tests) | framework unchanged | regression |

All suites run against **synthetic, non-frozen** corpora only. Frozen rows
are never imported by any test (dataset-spec §12.3).

## 9. Explicit non-goals (inherited, restated once)

Program A is not the research center; carries no H\*/H2; owns no ECE, bins,
tier→probability mapping, rubric, adjudication, or decision logic; consumes
no C8 replay engine, soul graph, self-model, reasoning engine, thermodynamic
state, or free-energy policy; modifies no frozen constant, preregistration,
or canonical document (MASTER_SPEC §19). This architecture adds one: Program
A performs **no snapshot construction at execution time** — snapshots are
frozen inputs with the same discipline as the dataset.

## 10. Open items this architecture hands to governance (unchanged deciders)

1. **G1 ratification** of the §2 location ruling (`program_a/` + R-16
   packaging line) — Architect signature.
2. **A3/Q2 ratification** of frozen-snapshot mode + the snapshot leakage-review
   procedure — Architect + ScientificAuditor.
3. **A4/Q3** prereg §7 power amendment for the deterministic case — drafted
   with T1, adjudicated before G6.
4. **T1 content**: ES-1 states/tier map/constants verbatim from
   `PROGRAM_A_CONFIDENCE_MECHANISM.md` §7 + this architecture's PA-1 ordering
   rule, PA-2 extraction parameters, and PA-4 answer templates added to the
   free-constant register — ScientificAuditor sign-off, then G4 freeze.
5. **Q8 interim** id scheme (§ PA-4) stands until the Architect/Release-Manager
   ruling.
6. Stale-document corrections: F-10 status (now fixed), `ARCHITECTURE_MAP.md`
   row 6 (true once `program_a/` is populated).
