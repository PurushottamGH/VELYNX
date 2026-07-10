# PROGRAM A — MODULE SPECIFICATION

**Authority:** Lead Systems Architect, 2026-07-08.
**Function:** the file-level production module layout of Program A, one entry
per module: path, responsibility, public names + signatures (contracts, not
code), imports allowed, imports forbidden, and the tests that bind it. Derives
from `PROGRAM_A_FINAL_ARCHITECTURE.md` (subsystems PA-1..PA-6) and the frozen
contracts it cites. **No implementation code appears here** and none may be
written until `ES1_IMPLEMENTATION_GATE.md` flips to GO.
**Location:** all modules live in the `program_a/` package (Architecture §2
ruling, pending G1 ratification), except test modules under `tests/program_a/`
and one packaging edit.

---

## 0. File tree (target)

```
program_a/
  __init__.py                      # exports answer_query, mechanism_id, program_a_answer_fn
  types.py                         # EvidenceItem, EvidenceSet, CandidateClaims, EvidenceStateResult, Emission
  constants.py                     # FROZEN ES-1 constants; hash-asserted; sourced from T1 spec
  evidence/
    __init__.py
    snapshot_store.py              # PA-1 execution-time: load + evidence_for
    snapshot_format.py             # PA-1: on-disk snapshot schema + integrity verify
    snapshot_builder.py            # PA-1 builder-side (offline; MAY use backend.retrieval)
  extraction/
    __init__.py
    claim_extraction.py            # PA-2: extract_claims
  mechanism/
    __init__.py
    support_tests.py               # PA-3: claim-support, contradiction, materiality, independence
    evidence_states.py             # PA-3: classify() → EvidenceStateResult (S0..S3, precedence)
    emission.py                    # PA-4: answer_query(), mechanism_id(), answer templates
  binding/
    __init__.py
    exp1_binding.py                # PA-5: program_a_answer_fn(query, seed) -> Mapping
tests/program_a/
  test_snapshot_store.py
  test_claim_extraction.py
  test_evidence_states.py
  test_emission.py
  test_binding.py
  test_import_guard.py
  test_replay.py
pyproject.toml                     # + "program_a*" in packages.find (R-16)
```

Rationale for the split: the frozen scientific rule (ES-1) is confined to
`program_a/mechanism/` + `program_a/constants.py`; retrieval and text
mechanics are science-free and separately testable; the binding is the only
module importing `experiments.EXP1` types.

---

## 1. `program_a/types.py` — shared value types (PA-1..PA-4)

- **Responsibility:** frozen dataclasses passed between subsystems. No logic,
  no I/O, no constants. Deliberately *below* `QueryRecord`: nothing here has a
  `gold_rubric`, `query_family`, or `score` field — the L11 cheat channel and
  the retrieval-relevance channel are unrepresentable (Architecture §4 PA-1,
  PA-3).
- **Public names (contracts):**
  - `EvidenceItem(doc_id: str, origin_domain: str, title: str, text: str,
    snapshot_hash_ref: str)` — frozen; **no `score`, no timestamp.**
  - `EvidenceSet(items: tuple[EvidenceItem, ...])` — frozen; preserves PA-1's
    frozen total order.
  - `CandidateClaim(claim_text: str, supporting_doc_ids: tuple[str, ...])`;
    `CandidateClaims(claims: tuple[CandidateClaim, ...])` — frozen.
  - `EvidenceStateResult(state: str, selected_claim: CandidateClaim | None,
    support_doc_ids: tuple[str,...], contradiction_doc_ids: tuple[str,...],
    independent_origin_count: int)` — frozen; `state ∈ {"S0","S1","S2","S3"}`.
  - `Emission(answer: str, tier: str, raw_numeric_confidence: None,
    metadata: dict)` — frozen; `tier ∈ CONFIDENCE_TIERS`.
- **Imports allowed:** stdlib (`dataclasses`, `typing`).
- **Imports forbidden:** everything else, including `experiments.*`,
  `backend.*`, `program_a.*` siblings (leaf module).
- **Tests:** exercised transitively; a direct test asserts `EvidenceItem` has
  no `score`/timestamp field (structural-guard regression).

## 2. `program_a/constants.py` — frozen ES-1 constants (PA-3 owns their use)

- **Responsibility:** the single home of every ES-1 free constant named in
  `PROGRAM_A_CONFIDENCE_MECHANISM.md` §7.4 and the T1 free-constant register
  (CR-11): the S3 corroboration threshold (`MIN_INDEPENDENT_ORIGINS_FOR_S3 =
  2`), the source-independence relation definition, the claim-support test
  parameters, the contradiction-materiality rule parameters, the PA-1 frozen
  ordering key, and the PA-2 extraction parameters. Each constant carries an
  a-priori justification comment referencing its T1 register line. Includes
  `SPEC_VERSION: str` (the T1 spec version), the structural identity tag
  `PA3_RULESET_VERSION: str` (addendum §A6-DIGEST, folded into the digest), and
  the `CONSTANTS_HASH` self-check. **G4-prep state:** the concrete frozen values
  for `SPEC_VERSION`, `MIN_INDEPENDENT_ORIGINS_FOR_S3`, `INDEPENDENCE_RELATION`,
  `EVIDENCE_ORDERING_KEY`, `PA3_RULESET_VERSION`, `STATE_TIER_MAP`, and
  `CONFIDENCE_TIERS` are transcribed; `SUPPORT_TEST_PARAMS`,
  `CONTRADICTION_MATERIALITY_PARAMS`, `EXTRACTION_PARAMS`, and
  `ANSWER_TEMPLATES` remain pending (addendum §C condition 4, the pre-existing
  T1 transcription duty) and `CONSTANTS_HASH` is `None` until the G4 freeze step
  transcribes them and pins the digest.
- **Public names:** the named constants above; `SPEC_VERSION`;
  `PA3_RULESET_VERSION`; `CONSTANTS_HASH`; `frozen_constants_digest() -> str`.
- **Determinism/replay:** these constants ARE the mechanism; a change here is
  a mechanism change → new T1 revision, re-freeze, new `SPEC_VERSION`, new
  `mechanism_id()` (Architecture §4 PA-3 replay guarantee; CR-6/CR-12).
- **Imports allowed:** stdlib only.
- **Imports forbidden:** all else. In particular `experiments.EXP1.calibration`
  (must not mirror `TIER_TO_CONFIDENCE`/`BIN_BOUNDARIES` — CR-8/L8); no
  probability numbers appear here at all.
- **Tests:** `tests/program_a/test_constants_freeze.py` asserts the G4-prep
  freeze state (concrete values transcribed; four dict entries pending;
  `frozen_constants_digest()` raises `FrozenConstantsIncomplete` while
  pending; `CONSTANTS_HASH` is `None`) and the CR-8/L8 firewall (no constant
  equals `0.125/0.375/0.625/0.875` or a bin boundary). Post-GO, the
  `frozen_constants_digest()` equality pin (drift tripwire) and the §A7
  seam-invariant assertions land in `test_evidence_states.py` (addendum §B5,
  Wave 4).

## 3. `program_a/evidence/snapshot_format.py` — snapshot schema + integrity (PA-1)

- **Responsibility:** define the frozen retrieval-snapshot on-disk format and
  verify its integrity. A snapshot is a static, content-addressed corpus:
  a manifest (`snapshot_manifest.json`: aggregate SHA-256, per-document
  hashes, build provenance, leakage-review reference) plus documents. Read-only
  at execution (Q7: frozen assets readable).
- **Public names:**
  - `SnapshotManifest` (frozen: `aggregate_hash`, `doc_hashes`,
    `built_from`, `leakage_review_ref`, `created_commit`).
  - `verify_snapshot(path) -> SnapshotManifest` — raises on hash mismatch.
- **Determinism/replay:** integrity failure is a hard pre-run error (drift
  detectable before any output — FM-6 mitigation).
- **Imports allowed:** stdlib (`hashlib`, `json`, `pathlib`).
- **Imports forbidden:** deny-list; `backend.*`; network.
- **Tests:** `test_snapshot_store.py` — tampered doc → verify raises;
  well-formed snapshot → manifest returned.

## 4. `program_a/evidence/snapshot_store.py` — evidence acquisition (PA-1)

- **Responsibility:** load a verified snapshot and answer
  `evidence_for(query_text)` by the frozen lookup + frozen total order, with
  `score`/timestamps stripped. The only execution-path evidence source.
- **Public names:**
  - `SnapshotStore.load(path: str | Path) -> SnapshotStore` (calls
    `verify_snapshot`).
  - `SnapshotStore.evidence_for(query_text: str) -> EvidenceSet`.
  - `SnapshotStore.snapshot_hash -> str` (feeds `mechanism_id()`).
- **Determinism/replay:** identical `(query_text, snapshot)` → identical
  `EvidenceSet` bytes; ordering key from `constants.py`; no network, no
  wall-clock, no env vars in this module.
- **Imports allowed:** stdlib; `program_a.types`; `program_a.constants`;
  `program_a.evidence.snapshot_format`.
- **Imports forbidden:** deny-list; `backend.*`; `experiments.*`; network libs.
- **Tests:** `test_snapshot_store.py` — determinism (two loads → identical
  bytes); no-network (socket guard); ordering stability under permuted file
  order; output type carries no `score`/timestamp.

## 5. `program_a/evidence/snapshot_builder.py` — offline builder (PA-1, builder-side ONLY)

- **Responsibility:** construct a snapshot offline, before freeze, outside the
  execution path. This is the **only** module permitted to import
  `backend.retrieval.unified_retriever`. Its output passes the documented
  leakage review (CF-R4 / gate A3) before any frozen-row exposure.
- **Public names:** `build_snapshot(queries: Iterable[str], out_dir) ->
  SnapshotManifest` (build tool entry; run manually/CI, never at execution).
- **Determinism/replay:** builder output is content-addressed; the built
  snapshot is then frozen and treated exactly like the dataset.
- **Imports allowed:** stdlib; `program_a.types`;
  `program_a.evidence.snapshot_format`; **`backend.retrieval.unified_retriever`
  (this module only)**.
- **Imports forbidden:** the rest of the deny-list; `experiments.*`; any
  `[REJECTED]` backend module.
- **Tests:** a builder smoke test with a stubbed retriever (no live network in
  CI); leakage-review checklist is a human gate, not a unit test.
- **Guard note:** the import-guard test (PA-6) allow-lists
  `backend.retrieval.unified_retriever` **for this module path only** and
  denies it everywhere else in `program_a/`.

## 6. `program_a/extraction/claim_extraction.py` — claim extraction (PA-2)

- **Responsibility:** deterministic candidate-claim construction from evidence
  (ES-1 §7.1). Entity-level matching (not topic-level) — the first line of
  defence against CF-R2/FM-1.
- **Public names:** `extract_claims(query_text: str, evidence: EvidenceSet)
  -> CandidateClaims`.
- **Determinism/replay:** pure; parameters from `constants.py`; no model calls
  (M8 unlawful), no randomness.
- **Imports allowed:** stdlib; `program_a.types`; `program_a.constants`.
- **Imports forbidden:** deny-list; `backend.*`; `experiments.*`; providers.
- **Tests:** `test_claim_extraction.py` — determinism; empty evidence → empty
  claims; nonexistent-entity/topically-related evidence → no claim; every
  claim's `supporting_doc_ids` exist in the evidence.

## 7. `program_a/mechanism/support_tests.py` — the frozen sub-tests (PA-3)

- **Responsibility:** the four load-bearing deterministic predicates of ES-1
  (§7.4 register): `supports(claim, evidence_item)`,
  `contradicts(claim_a, claim_b)`,
  `is_material(claim_a: CandidateClaim, claim_b: CandidateClaim) -> bool`,
  `independent_origins(items) -> int`. The claim-support test is "the
  load-bearing sub-component; its failure modes dominate the risk register"
  (MECHANISM §7.4; CF-R2). `is_material`'s canonical interface is the two-claim
  form (addendum §A5); the single-argument `is_material(contradiction)` form is
  rejected (no `Contradiction` type exists in the frozen `types.py`).
  `contradicts` is package-internal and retained (addendum §A6).
- **Package-internal names:** the four predicates above (exact signatures
  frozen in T1). "Package-internal" means module-level names within `program_a`,
  not part of the two-callable external API (`answer_query`, `mechanism_id`).
- **Determinism/replay:** pure; all thresholds from `constants.py`; no
  probability numbers.
- **Imports allowed:** stdlib; `program_a.types`; `program_a.constants`.
- **Imports forbidden:** deny-list; `experiments.*`; `backend.*`.
- **Tests:** `test_evidence_states.py` — mirror-domain independence counted
  once; trivial variation is not material; entity-level support positive/
  negative cases; fabrication-pressure negatives (the FM-1 guard).

## 8. `program_a/mechanism/evidence_states.py` — state classification (PA-3)

- **Responsibility:** `classify()` — apply the sub-tests and select exactly
  one state with frozen precedence S0 → S1 → (S2|S3) (DECISION_TREE Tree 2).
  Contains the state decision only; delegates predicates to `support_tests.py`
  and thresholds to `constants.py`.
- **Public names:** `classify(query_text: str, evidence: EvidenceSet,
  claims: CandidateClaims) -> EvidenceStateResult`.
- **Determinism/replay:** exactly one state per input; no probability numbers;
  no knowledge of tier→p_i or bins (CR-8/L8).
- **Imports allowed:** stdlib; `program_a.types`; `program_a.constants`;
  `program_a.mechanism.support_tests`.
- **Imports forbidden:** deny-list; `experiments.EXP1.calibration`;
  `experiments.EXP1.decision`; `experiments.*` generally; `backend.*`;
  **`QueryRecord`** (input is a plain string — structural L11).
- **Tests:** `test_evidence_states.py` — one case per state; exhaustiveness +
  mutual exclusion property test; precedence-order test; `constants.py`
  digest pin.

## 9. `program_a/mechanism/emission.py` — the public surface (PA-4)

- **Responsibility:** the answer-construction + tier map (ES-1 §7.2), both
  from one `EvidenceStateResult` (CR-9). Owns `mechanism_id()`. Program A's
  entire public API lives here (re-exported from `program_a/__init__.py`).
  Answer wording per state uses frozen templates listed in the T1 spec.
- **Public names:**
  - `answer_query(query_text: str, seed: int) -> Emission` — drives PA-1→PA-3
    then maps state→(answer form, tier): S0→`UNKNOWN`, S1→`DEBATED`,
    S2→`PROBABLE`, S3→`CERTAIN`.
  - `mechanism_id() -> str` — `"program-a-public-v1+es1-{SPEC_VERSION}+const-{frozen_constants_digest[:8]}+snap-{snapshot_aggregate_hash[:8]}"` (CR-12/Q8 interim).
  - module-level snapshot handle: constructed once from a configured snapshot
    path at import (read-only), or injected — see below.
- **Determinism/purity:** identical `(query_text, seed)` → identical
  `Emission`; stateless across calls; no writes, no telemetry in path, no
  input mutation (CR-4/CR-5); `raw_numeric_confidence` always `None`.
- **Configuration seam:** the snapshot path is provided via an explicit
  constructor/factory (`build_program_a(snapshot_path) -> ProgramA`) so tests
  inject synthetic snapshots and execution injects the frozen one; module-level
  convenience wrappers `answer_query`/`mechanism_id` bind a
  process-configured instance. No mutable global state beyond the one-time
  configured snapshot handle.
- **Imports allowed:** stdlib; `program_a.types`; `program_a.constants`;
  `program_a.evidence.snapshot_store`; `program_a.extraction.claim_extraction`;
  `program_a.mechanism.{support_tests,evidence_states}`.
- **Imports forbidden:** deny-list; `experiments.*` (public surface has zero
  experiment knowledge); `QueryRecord`.
- **Tests:** `test_emission.py` — determinism/purity (CR-4); per-state
  answer-form invariants (CR-9: no assertion text with UNKNOWN/DEBATED;
  CERTAIN only when `state=="S3"`); tier ∈ CONFIDENCE_TIERS; ≥2 tiers on a
  synthetic three-family corpus (CR-14, pre-freeze design check); id stability.

## 10. `program_a/binding/exp1_binding.py` — the EXP-1 seam (PA-5)

- **Responsibility:** Form-A `answer_fn`; pure field transport into the
  `AnswerRecord` mapping. The only module importing `experiments.EXP1` types.
  Reads `query.query` and `query.query_id` **only** (L11/CR-3).
- **Public names:**
  - `program_a_answer_fn(query: QueryRecord, seed: int) -> Mapping[str, Any]`
    → `{"query_id": query.query_id, "answer": e.answer, "tier": e.tier,
    "seed": seed, "raw_numeric_confidence": None, "metadata": e.metadata}`
    where `e = answer_query(query.query, seed)`.
  - re-export `mechanism_id` (callers pass it as `program_a_adapter_id`).
- **Determinism/replay:** inherits PA-4; injected via
  `run_experiment(answer_fn=program_a_answer_fn,
  program_a_adapter_id=mechanism_id(), adjudicator_fn=..., ...)`.
- **Imports allowed:** stdlib; `program_a.mechanism.emission`;
  `experiments.EXP1.dataset` (`QueryRecord` type);
  `experiments.EXP1.program_a_adapter` (types, for caller convenience).
- **Imports forbidden:** deny-list; `experiments.EXP1.{calibration,decision,
  run}`; reads of `query.gold_rubric`/`query.query_family`/`query.metadata`.
- **Tests:** `test_binding.py` — transport fidelity (mapping ≡ Emission,
  nothing computed); seed echo; end-to-end via `run_seed_sync` on synthetic
  corpus; sentinel-substitution (extends
  `tests/EXP1/test_cheat_channel_guard.py`) — rubric/family replaced by
  sentinels ⇒ byte-identical output (CR-3 / gate C1).

## 11. `program_a/__init__.py` — public exports

- **Responsibility:** export exactly `answer_query`, `mechanism_id`,
  `build_program_a` (from `mechanism.emission`) and `program_a_answer_fn`
  (from `binding.exp1_binding`). Nothing from `evidence/`, `extraction/`, or
  `mechanism/support_tests` is public.
- **Imports forbidden:** must not, at import time, pull `backend.*` or
  `experiments.*` beyond what the binding needs; import-guard test asserts the
  transitive closure.

## 12. Test modules (PA-6) — `tests/program_a/`

| Module | Binds | Notes |
|---|---|---|
| `test_snapshot_store.py` | §3, §4 | integrity, determinism, no-network, ordering |
| `test_claim_extraction.py` | §6 | determinism, fabrication negatives |
| `test_evidence_states.py` | §2, §7, §8 | state table, precedence, exclusivity, constants digest |
| `test_emission.py` | §9 | determinism/purity, CR-9 invariants, tier coverage, id |
| `test_binding.py` | §10 | transport, sentinel (CR-3), end-to-end |
| `test_import_guard.py` | §7 deny-list | transitive-closure deny-list + planted-import self-test; allow-lists `backend.retrieval` for `snapshot_builder.py` only |
| `test_replay.py` | whole pipeline | byte-identical re-run + artifacts on synthetic corpus (T10 mechanics) |

All test corpora are synthetic and disjoint from the frozen dataset
(dataset-spec §12.3). No test observes frozen rows.

## 13. `pyproject.toml` — packaging (R-16)

- **Change:** add `program_a*` to `[tool.setuptools.packages.find]` (or
  equivalent) so the populated package ships. One-line reviewed change;
  Reviewer sign-off only (no science).

## 14. Module → contract cross-reference

| Module | Frozen contract it must satisfy | Source |
|---|---|---|
| snapshot_store | determinism, purity, no score-leak | MASTER_SPEC §8; prereg §5 |
| claim_extraction | deterministic, entity-level | MECHANISM §7.1; CF-R2 |
| support_tests + evidence_states | ES-1 states/precedence/constants | MECHANISM §7.2/§7.4; DECISION_TREE Tree 2 |
| emission | answer–tier coupling; tier set; identity | MECHANISM §7.2; dataset.py:17; CR-9/CR-12 |
| exp1_binding | AnswerRecord fields; L11; from_mapping | BINDING_SPEC §4; dataset.py:101-151; CR-3/CR-13 |
| import_guard | deny-list | DEPENDENCY_GRAPH §4; TD-08 |
| all | frozen before outputs; no outcome coupling | prereg §4 #5, §6; CR-6/CR-7 |
