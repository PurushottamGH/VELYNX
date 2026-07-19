# PA-2 ACCEPTANCE DECISION -- Claim-Extraction Closure Sprint

**Authority:** VELYNX Director, acting on the latest PA-2 Engineering Decision as the approving integration review (per directive 2026-07-09).
**Status:** Approved for execution. Scope: PA-2 (Claim Extraction) closure only.
**Created:** 2026-07-09.

## 1. Scope and authority

This decision records the approved engineering action list for closing PA-2 (Program A, Stage 2 -- Claim Extraction) as a documentation/implementation milestone. It is the single authorizing record for this sprint; no action outside this list is in scope.

PA-2 = `program_a/extraction/claim_extraction.py` + the `CandidateClaim`/`CandidateClaims` value types in `program_a/types.py`.

Canonical implemented contract (source of truth):
- `CandidateClaim(claim_text: str, supporting_doc_ids: tuple[str, ...])` -- exactly two fields; no `claim_id`.
- `CandidateClaims(claims: tuple[CandidateClaim, ...])`.
- `extract_claims(query_text: str, evidence: EvidenceSet) -> CandidateClaims`.

## 2. Approved actions (in scope)

### A. Documentation reconciliation -- PA-2 contract drift
- **A1.** `PROGRAM_A_FINAL_ARCHITECTURE.md` PA-2 section (~lines 194-196): remove the spurious `claim_id: str` from the documented PA-2 output. Documented output becomes exactly `CandidateClaims` of claims each carrying `claim_text: str` and `supporting_doc_ids: tuple[str, ...]` (refs into `EvidenceSet` by `doc_id`).
- **A2.** `PROGRAM_A_CONSISTENCY_AUDIT.md` (AUD-05, ~lines 108-117; and the PA-2 standardize bullet at ~line 203): update AUD-05 to RESOLVED -- the `supporting_evidence_refs -> supporting_doc_ids` rename is already applied and the residual corrected item is the spurious `claim_id` field (removed by A1). Remove the stale `supporting_evidence_refs` assertions and the ambiguous "or `supporting_evidence_refs`" alternative. Do NOT touch AUD-04 / line 202 (PA-3) -- out of scope.
- **A3.** `PROGRAM_A_RECONCILIATION_PLAN.md` DRF-05 (table row ~line 30; finding body ~lines 112-124): update the conflict description to the accurate residual (spurious `claim_id` field; the `supporting_evidence_refs -> supporting_doc_ids` rename already applied) and set Status from Open -> Resolved by PA-2 closure sprint (2026-07-09), with a dated resolution note.

### B. Architecture/module documentation -- verify match to implemented contract
- **B1.** `PROGRAM_A_MODULE_SPEC.md` Section 6/types: verified already matches code (no edit).
- **B2.** `PROGRAM_A_API_REFERENCE.md` Section 7 / `CandidateClaim` (~lines 114-126): verified already matches code (no edit).
- **B3.** `PROGRAM_A_DATAFLOW.md`, `PROGRAM_A_DEPENDENCY_GRAPH.md`, `PROGRAM_A_SEQUENCE_DIAGRAM.md`, `ARCHITECTURE_MAP.md`: verified contain no PA-2 output-field text (no edit).

### C. Non-ES-1 guard tests (executed by the Builder agent)
- **C1.** Extend `tests/program_a/test_types.py` regression section: assert `CandidateClaim` has exactly the field set `{claim_text, supporting_doc_ids}` and explicitly does NOT have `claim_id`.
- **C2.** New `tests/program_a/test_pa2_doc_consistency.py`: documentation-consistency guard parsing the PA-2 section of `PROGRAM_A_FINAL_ARCHITECTURE.md`, asserting it documents `supporting_doc_ids` and does NOT document `claim_id`, matching the implemented `CandidateClaim` type.

## 3. Explicit exclusions (NOT in scope -- ES-1 NO-GO boundary)

Excluded; must not be touched in this sprint:
- Frozen constants / parameter-freeze plumbing (`program_a/constants.py` frozen values, `frozen_constants_digest`).
- `mechanism_id`, replay digest, emission (`program_a/mechanism/emission.py`), binding (`program_a/binding/`).
- ES-1 core (PA-3 `support_tests`/`evidence_states`), the ES-1 implementation gate, and EXP-1 plumbing.
- H1 engineering hardening depending on frozen constants or the T1/G4 process.
- Any DRF/AUD other than DRF-05/AUD-05: DRF-04/AUD-04 (PA-3), DRF-06 (seed-variance), DRF-07 (binding boundary), DRF-08 (stubs), DRF-09/10 -- left for their respective phases / ES-1 governance.

Reference: `ES1_IMPLEMENTATION_GATE.md` is NO-GO (2026-07-07); no emission-surface or binding code may be written, merged, or prototyped-in-place.

## 4. Closure criteria

PA-2 is closed when all of: A1-A3 applied; B1-B3 verified; C1-C2 added and green; PA-2 test subset green; Reviewer returns PASS. (ScientificAuditor not required -- PA-2 is pure text mechanics, not the ES-1 frozen core or H1 calibration.) No ES-1 / emission-surface code introduced.

## 5. Evidence index

- Implemented contract: `program_a/types.py` (lines 66-87), `program_a/extraction/claim_extraction.py` (lines 164-224).
- Drift site: `PROGRAM_A_FINAL_ARCHITECTURE.md` (lines 194-196) -- spurious `claim_id`.
- Already-consistent: `PROGRAM_A_MODULE_SPEC.md` (line 69), `PROGRAM_A_API_REFERENCE.md` (lines 120-121).
- Tracking docs: `PROGRAM_A_CONSISTENCY_AUDIT.md` (AUD-05, lines 108-117; line 203); `PROGRAM_A_RECONCILIATION_PLAN.md` DRF-05 (lines 30, 112-124).
- Existing PA-2 tests: `tests/program_a/test_claim_extraction.py`; `tests/program_a/test_types.py` (lines 299-303 -- partial field guard, no `claim_id` assertion yet).