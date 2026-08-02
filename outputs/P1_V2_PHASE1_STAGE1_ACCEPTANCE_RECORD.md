# P1-v2 Phase 1 Stage-1 Engineering Acceptance Record

**GOVERNANCE: DRAFT — NO ADMISSIBLE EVIDENCE**

- **Record date:** 2026-08-02
- **Candidate branch:** `p1-v2-stage1-candidate-rebuild2-20260802`
- **Recovered baseline:** `0ab225176b10f98fa763b3914b27a2162b550205`
- **Implementation checkpoint:** `3ac369910e66fda72edc67a6ae7de21c3e71c5b8`
- **Evidence-record commit:** `7ed5d40feca227018a7e2abb44a0c5ba4f368430`
- **Final verification commit:** `<TO BE FILLED AFTER CLEAN-CLONE RESULTS ARE RECORDED>`
- **Governing specification:** `P1_V2_LSKE_SPECIFICATION_v1.1.2.md`
- **Standing:** Engineering verification record only. It does not register the specification, activate governance, raise Scientific Readiness, or create admissible scientific evidence.

## 1. Crash recovery disposition

| Item | Classification | Basis |
|---|---|---|
| Candidate worktree | `VERIFIED_COMPLETE` recovery | Repository health passed; no interrupted Git operation, lock, truncation, or corruption was found. |
| Failed edit | `PARTIAL_CHANGE` | `tests/lske/test_schema_generation.py` contained an incomplete closed-world classifier. |
| Repair | `VERIFIED_COMPLETE` | The classifier was bounded to the frozen closure forms. No source-level schema contract was changed to accommodate the test. |
| Safe checkpoint | `VERIFIED_COMPLETE` | Commit `3ac369910e66fda72edc67a6ae7de21c3e71c5b8` preserved the recovered implementation. |

## 2. Candidate path classification

| Path | Classification | Stage-1 disposition |
|---|---|---|
| `v2/lske/` | Implemented source | Hand-written Stage-1 implementation. |
| `schemas/lske/*.schema.json` | Generated artifacts | Exactly 23 committed, deterministic, reviewable schema files. |
| `tests/lske/` | Test source | Frozen Stage-1 behavioral and schema verification surface. |
| `requirements.txt` | Configuration | Declares exact `jsonschema==4.25.1`. |
| `pyproject.toml` | Configuration/tooling | Packages `v2*` and its inherited runtime dependency `ros*`; includes `v2` in coverage. |
| `.github/workflows/ci.yml` | Configuration/CI | Runs focused LSKE tests and enforces the 23-schema compilation gate. |
| `outputs/P1_V2_PHASE1_STAGE1_ACCEPTANCE_RECORD.md` | Documentation/evidence | This DRAFT engineering record. |
| `P1_V2_HUMAN_GATE_CHECKLIST.md` | Documentation/evidence | Separates verified engineering facts from human-only acts. |
| `audits/PCA_REMEDIATION_LEDGER.md` | Documentation/evidence | Bounded PCA reconciliation; no invented finding definitions. |
| `ros/` | Inherited static source | Read-only in Stage 1. Packaging includes it because `v2.lske.schema` imports frozen ROS symbols. |
| `.ros/lske_events.jsonl` | Runtime | Created only beneath an explicit runtime root; not a repository source artifact. |
| `build/`, `*.egg-info/`, wheel files, temporary environments | Transient | Excluded from the candidate commit and acceptance corpus. |

## 3. Stage boundary

- No `ros/*` source file changed from the recovered baseline.
- `len(ros.model.COLLECTIONS) == 11` at Stage-1 verification.
- Expanding the ROS collection register from 11 to 20 remains Stage 2 and was not performed.
- No reader, transaction layer, CLI, server, network client, or other later-stage feature was introduced into `v2/lske/`.

## 4. Acceptance criteria AC-P1-01 through AC-P1-27

All criteria below are exercised by the focused Stage-1 suite. Evidence references are test functions rather than claims of human review.

| Criterion | Result | Principal executable evidence |
|---|---|---|
| `AC-P1-01` | PASS | `test_collection_composition_and_record_fragment_closure` |
| `AC-P1-02` | PASS | `test_collection_composition_and_record_fragment_closure` |
| `AC-P1-03` | PASS | closure-form audit plus N-01…N-32 undeclared-key cases |
| `AC-P1-04` | PASS | `validate` tests against collection schemas |
| `AC-P1-05` | PASS | 23-file byte-identity test and two regeneration passes |
| `AC-P1-06` | PASS | relation-envelope tests |
| `AC-P1-07` | PASS | derived `DELETED`, `CANDIDATE`, `DORMANT`, and `ACTIVE` cases |
| `AC-P1-08` | PASS | all N-01…N-32 positive catalogue cases |
| `AC-P1-09` | PASS | N-05 `source_path` catalogue case |
| `AC-P1-10` | PASS | exact `Verdict` to admissibility mapping test |
| `AC-P1-11` | PASS | OBS/2 top-level closure and Observatory-owned interior test |
| `AC-P1-12` | PASS | `LskeRecord.from_payload` validation and deep-immutability tests |
| `AC-P1-13` | PASS | pre-seal/post-seal equality and hash test |
| `AC-P1-14` | PASS | normalized, de-duplicated, total failure ordering tests |
| `AC-P1-15` | PASS | record-ID purity, order stability, exhaustion, and unknown-collection cases |
| `AC-P1-16` | PASS | content-addressed event-ID and namespace-disjointness cases |
| `AC-P1-17` | PASS | content-hash Block H exclusion and ROS canonicalization path |
| `AC-P1-18` | PASS | register ownership and import-based ROS register use tests |
| `AC-P1-19` | PASS | exact 20-entry collection register and generated schemas |
| `AC-P1-20` | PASS | append-only event writer, one line per call, prior-byte preservation |
| `AC-P1-21` | PASS | seven-class frozen error taxonomy and raise-site tests |
| `AC-P1-22` | PASS | `v2.lske` package/version ownership and installed import path |
| `AC-P1-23` | PASS | prefix regex, `RQS`, and unchanged `ID_PATTERN` tests |
| `AC-P1-24` | PASS | primitive four-tuple payload, one-shot materialization, first duplicate retained, `args` contract |
| `AC-P1-25` | PASS | immutable 23-entry mapping and fresh deep accessor copies |
| `AC-P1-26` | PASS | sole schema ontology-version ownership and package-level absence |
| `AC-P1-27` | PASS | exact frozen-payload constructor predicate and single failure item |

## 5. Executed engineering evidence

| Check | Result |
|---|---|
| Focused Stage-1 suite in development environment | `109 passed, 1 skipped` |
| Exact evaluator environment | `jsonschema==4.25.1`; `109 passed, 1 skipped` |
| N-01…N-32 catalogue | 32/32 positive cases; every LSKE-owned interior rejects one undeclared key; N-31 explicitly skipped because its interior is Observatory-owned |
| Schema count | 23/23 |
| Draft compilation | 23/23 with `Draft202012Validator.check_schema` |
| Offline references | PASS through complete in-memory `referencing.Registry` |
| Deterministic generation | Two consecutive 23-schema generations; Git diff clean after each; schema-generation suite `8 passed` |
| Formatting | Black reported `9 files would be left unchanged` before documentation completion |
| Installed checkpoint wheel after packaging repair | Module resolved from external `site-packages`; exact evaluator, 23 schemas, offline references, deterministic accessors, public surface, and append-only writer passed |
| Installed-wheel behavioral subset | `101 passed, 1 skipped` from outside the repository; schema-file byte test excluded because generated JSON files are repository artifacts, not wheel package data |
| Research CI scope | `168 passed` |
| Unit CI scope | `194 passed, 1 skipped, 1 failed`; the sole failure is a pre-existing non-Stage-1 missing document, `docs/architecture/OBSERVATORY_ARCHITECTURE.md`, absent from the candidate commit |
| Broad whole-tree pytest | Not an acceptance command: it collected archived/manual/environment-dependent scripts and failed during collection for unrelated legacy conditions |
| Current-candidate wheel build | PASS after adding inherited `ros*` package discovery |

## 6. Packaging finding and bounded repair

The first externally installed checkpoint wheel could not import `v2.lske.schema` because the distribution omitted the inherited `ros` package while `schema.py` imports frozen symbols from `ros.admissibility`, `ros.authority`, `ros.model`, and `ros.protocol`.

Bounded repair:

```toml
[tool.setuptools.packages.find]
include = [
    # existing packages omitted here
    "ros*",
    "v2*",
]
```

No `ros/*.py` file was edited. The rebuilt wheel imported from `site-packages` and passed the external probe and behavioral suite.

## 7. Known non-Stage-1 condition

The repository's configured unit scope has one failure because `tests/unit/test_observatory.py` requires `docs/architecture/OBSERVATORY_ARCHITECTURE.md`, which is absent from this candidate commit. A copy exists only in another working directory. It was not imported into the candidate because Stage-1 recovery must not mix unrelated, uncommitted corpus without repository authority. This condition must be handled by the repository owner independently of LSKE Stage 1; it is not evidence against the 27 LSKE acceptance criteria.

## 8. Evidence still pending at record creation

The following fields are intentionally prospective until performed against the final documentation commit:

- Final candidate commit SHA.
- Fresh clean-clone focused Stage-1 result.
- Fresh clean-clone exact-pin verification.
- Fresh clean-clone wheel build and external installed-wheel result.
- Final clean status of both candidate and verification clone.

These fields must be updated with command output before a terminal engineering verdict is issued.

## 9. Human and governance boundary

This record does not constitute independent human code review, dependency approval, merge approval, release approval, governance adoption, credential revocation proof, history-rewrite authorization, or scientific validation. Those acts remain in `P1_V2_HUMAN_GATE_CHECKLIST.md`; identity and approval fields remain blank.
