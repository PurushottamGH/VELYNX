# PROGRAM A — BUILD CHECKLIST

**Authority:** Lead Systems Architect, 2026-07-08.
**Function:** the single executable checklist for building Program A, from
today's state to hand-off at G5 review. Every box cites its owner; no box may
be checked by the author of the work it verifies, and no specialist box may be
checked on a specialist's behalf (MASTER_SPEC §16; R-08). This checklist
*encodes* — it does not replace — `ES1_IMPLEMENTATION_GATE.md`,
`ES1_CORRECTION_PLAN.md`, and `PROGRAM_A_IMPLEMENTATION_ROADMAP.md`.
Execution (T9–T11) has its own gates and is out of scope here.

---

## Phase 0 — Already true on disk (verify, don't build)

- [ ] **V1.** Confirm F-10 fix present: `AnswerRecord.__post_init__` calls
      `validate()` (`experiments/EXP1/dataset.py:112-122`) and the rejection
      test passes. *(Gate box C2 — verify + record; stale docs to be corrected,
      not code.)* — Reviewer
- [ ] **V2.** Confirm sentinel-substitution test exists and is green against
      the stub adapter (`tests/EXP1/test_cheat_channel_guard.py`). *(Gate box
      C1, first half.)* — Reviewer
- [ ] **V3.** Confirm EXP-1 framework suite green (the 64 EXP-1 tests). —
      Reviewer
- [ ] **V4.** Confirm `program_a/` still empty and unpackaged (pre-build
      baseline recorded). — Builder

## Phase 1 — Governance to GO (no code; ES-1 gate Sections A/B)

- [ ] **G-1.** Architect ratifies the location ruling:
      `program_a/` package + R-16 packaging line
      (`PROGRAM_A_FINAL_ARCHITECTURE.md` §2). *(Gate A1.)* — Architect
- [ ] **G-2.** ScientificAuditor ratifies tier-source lawfulness. *(Gate A2.)*
      — ScientificAuditor
- [ ] **G-3.** Retrieval-mode decision recorded: frozen snapshot, with the
      snapshot leakage-review procedure named. *(Gate A3 / Q2.)* — Architect +
      ScientificAuditor
- [ ] **G-4.** Seed-variance disposition recorded; prereg §7 power amendment
      for the fully-deterministic case drafted and submitted (adjudication
      complete before G6). *(Gate A4 / Q3 — forced, CF-R5.)* — Builder draft +
      ScientificAuditor
- [ ] **G-5.** `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` committed,
      assembled per `ES1_CORRECTION_PLAN.md` Wave 2 (ES-1 states/coupling/
      tier map/precedence; per-tier semantic argument; free-constant register
      **including** this architecture's additions: PA-1 ordering rule, PA-2
      extraction parameters, PA-4 answer templates; Q2/Q3 resolutions; L11 +
      Q7 read-scope clause; identity clause; L8-scope and dev-corpus rulings
      requested). *(Gate B1.)* — Builder (assembly) + ScientificAuditor
- [ ] **G-6.** ScientificAuditor sign-off on T1 — named, dated. *(Gate B2.)*
- [ ] **G-7.** Release Manager freezes T1 — pinned commit recorded, before any
      frozen-row output is observed. *(Gate B3 / G4-freeze.)*
- [ ] **G-8. GO declared:** A1–A4 ∧ B1–B3 ∧ C1–C3 all checked
      (C-boxes may complete in parallel below but must be green at gate time).
      — Release Manager

## Phase 2 — Gate-independent engineering (may run parallel with Phase 1)

- [ ] **E-1.** Packaging: add `program_a*` to `pyproject.toml` packages.find;
      create real package dirs per `PROGRAM_A_MODULE_SPEC.md` §0. (Merge after
      G-1.) — Builder; Reviewer sign-off
- [ ] **E-2.** Import-guard test landed: deny-list per
      `PROGRAM_A_FINAL_ARCHITECTURE.md` §7 over `program_a/**` transitive
      closure; allow-list exception for `snapshot_builder.py` →
      `backend.retrieval.unified_retriever` only; planted-import self-test.
      *(Gate C3 / roadmap T7 / TD-08.)* — Builder; Reviewer sign-off
- [ ] **E-3.** Stale-doc corrections queued (not blocking): F-10 now fixed;
      `ARCHITECTURE_MAP.md:54` row 6 to become true at E-4. — Documentation;
      Reviewer

## Phase 3 — Build (after GO; order per `PROGRAM_A_IMPLEMENTATION_ORDER.md` §2)

- [ ] **B-1.** `types.py` + structural-guard test (no score/timestamp/rubric
      fields representable). — Builder
- [ ] **B-2.** `constants.py` — contents transcribed from the frozen T1
      register; `SPEC_VERSION` = T1 version; digest pinned to the G-7 commit;
      test asserting no evaluation-side numbers (0.125/0.375/0.625/0.875,
      bin boundaries). — Builder; ScientificAuditor spot-check that constants
      ≡ T1 register
- [ ] **B-3.** `evidence/snapshot_format.py` + `evidence/snapshot_store.py` +
      tests (integrity-failure rejection; determinism; no-network socket
      guard; ordering stability; no score/timestamp in output). — Builder
- [ ] **B-4.** `evidence/snapshot_builder.py` (offline; the only
      `backend.retrieval` importer) + stubbed-retriever smoke test. — Builder
- [ ] **B-5.** **Frozen execution snapshot built**, content-hashed, and passed
      through the G-3 leakage-review procedure; review recorded in the
      snapshot manifest. — Experiment Engineer builds; ScientificAuditor
      reviews leakage
- [ ] **B-6.** `extraction/claim_extraction.py` + tests (determinism; empty
      evidence → no claims; nonexistent-entity/topic-only evidence → no claim).
      — Builder
- [ ] **B-7.** `mechanism/support_tests.py` + `mechanism/evidence_states.py` +
      tests (one case per state S0–S3; exhaustiveness/mutual-exclusion
      property; precedence S0→S1→(S2|S3); mirror-domain independence;
      materiality; fabrication-pressure negatives; constants-digest pin).
      — Builder
- [ ] **B-8.** `mechanism/emission.py` + `__init__.py` exports + tests
      (determinism + purity per the
      `test_answer_is_deterministic_and_side_effect_free` pattern; CR-9
      answer-form invariants — assertion text never with UNKNOWN/DEBATED,
      CERTAIN only from S3; tier ∈ CONFIDENCE_TIERS; ≥2 tiers reachable on a
      synthetic three-family corpus; `mechanism_id()` =
      `program-a-public-v1+es1-{SPEC_VERSION}+const-{frozen_constants_digest[:8]}+snap-{snapshot_aggregate_hash[:8]}` stable). — Builder
- [ ] **B-9.** `binding/exp1_binding.py` + `test_binding.py`
      (transport fidelity — nothing computed; seed echo; returns Mapping so
      `from_mapping` validates; reads only `query.query`/`query.query_id`).
      — Builder
- [ ] **B-10.** Sentinel-substitution test extended to the real
      `program_a_answer_fn`: rubric/family sentinels ⇒ byte-identical output.
      *(Gate C1, second half / CR-3.)* — Builder; Reviewer
- [ ] **B-11.** `test_replay.py`: end-to-end `run_seed_sync` on a synthetic
      non-frozen corpus; byte-identical re-run including artifacts. — Builder

## Phase 4 — Pre-freeze verification and hand-off

- [ ] **P-1.** Full dry run (T10 mechanics, W4.2) on a synthetic corpus with
      fabrication pressure: (a) zero `CERTAIN` on fabricated-claim probes
      (CF-R2/FM-1); (b) ≥2 tiers emitted (CF-R6); (c) byte-identical replay;
      (d) full artifact set present. **Scope limit (B-11):** any adverse
      finding routes to redesign + T1 re-freeze (back to G-5), never to
      in-place tuning. — Experiment Engineer
- [ ] **P-2.** Import-guard, sentinel, and full `tests/program_a/` +
      `tests/EXP1/` suites green in CI. — Reviewer
- [ ] **P-3.** Reviewer PASS on all Phase 2–3 code. *(Roadmap G5.)* — Reviewer
- [ ] **P-4.** Manifest sanity: a trial `build_execution_manifest` records
      `program_a_adapter_id == mechanism_id()`; identity-equality replay check
      exercised. — Reviewer
- [ ] **P-5.** Hand-off recorded: Program A build complete; execution remains
      gated on the external items — frozen dataset (T2), adjudicator (T3),
      report wiring (T5), EXP-0 run-state (T9), prereg §7 amendment
      adjudicated, pre-run lock (G6). *(None of these is a Program A
      subsystem.)* — Release Manager

## Standing prohibitions (in force throughout)

1. No frozen-row output observed by anyone, in any capacity, before G6
   (prereg §4 #5; gate standing prohibition).
2. No constant, template, threshold, or snapshot edited in response to any
   observed output — dry-run findings included — except via T1 revision +
   re-freeze **before** frozen-row exposure (CR-6/CR-7; B-11 scope limit).
3. No import from the deny-list, ever (`PROGRAM_A_FINAL_ARCHITECTURE.md` §7).
4. No test or fixture may read the frozen dataset (dataset-spec §12.3).
5. No self-issued approvals; every specialist box carries a real name and
   date (MASTER_SPEC §16; R-08; CF-R12).
6. A kill at EXP-1 is a reportable scientific outcome, not a build defect;
   the only unacceptable outcome is an invalid run (FAILURE_ANALYSIS §4).
