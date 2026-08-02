# PCA Remediation Ledger — bounded working record

**GOVERNANCE: DRAFT — NO ADMISSIBLE EVIDENCE**

**Status vocabulary:** `OPEN` · `HUMAN_ACTION_REQUIRED` · `FIXED` · `VERIFIED` · `BLOCKED` only.

**Scope.** This ledger reconciles available PCA remediation state with the P1-v2 Stage-1 engineering candidate on 2026-08-02. It is not a replacement for the missing immutable PCA register. It does not invent a finding title, definition, closure condition, human decision, provider action, or governance act.

**Engineering candidate.** Recovered baseline `0ab225176b10f98fa763b3914b27a2162b550205`; implementation checkpoint `3ac369910e66fda72edc67a6ae7de21c3e71c5b8`; evidence-record commit `7ed5d40feca227018a7e2abb44a0c5ba4f368430`; final verification commit to be recorded after clean-clone evidence is added.

## Root causes

| Root cause | Recorded meaning | Current implication |
|---|---|---|
| `R1` | Governance activation was never executed. | Human adoption, steward assignment, attestations, and registry activation remain required. |
| `R2` | Required repository corpus / ROS materials were not consistently tracked in the earlier baseline. | The Stage-1 candidate now commits its bounded implementation and records, but broader authority-corpus completeness remains a repository-owner decision. |
| `R3` | GCP service-account credential was exposed in repository history. | Provider revocation and human-authorized coordinated history remediation remain mandatory. |
| `R4` | Stale v1.1.0-era implementation and document residue existed. | Bounded mechanical corrections and explicit status records are used; no broad rewriting. |

## Finding ledger

| Finding | Root cause | Remediation / current result | Responsible actor | Verification | Status |
|---|---|---|---|---|---|
| `PCA-01` | `R1` | Section 13 adoption remains a human act; Stage-1 engineering does not activate it. | Constitutional steward, adopter, independent reviewer | `P1_V2_HUMAN_GATE_CHECKLIST.md` leaves all adoption fields blank. | `HUMAN_ACTION_REQUIRED` |
| `PCA-02` | `R2` | The exact immutable finding definition and closure condition remain unavailable. The bounded Stage-1 candidate commits its own implementation/evidence paths, but no broader closure is inferred. | Audit owner, repository owner | No immutable register recovered; human checklist requires restoration. | `OPEN` |
| `PCA-03` | `R3` | No provider-side revocation proof exists in the available corpus; no history remediation was performed. | GCP IAM owner, repository owner | Credential contents were not inspected; provider and authorization fields remain blank. | `HUMAN_ACTION_REQUIRED` |
| `PCA-04` | `R4` | `SchemaViolation` materializes once, keeps the first equal occurrence, de-duplicates, sorts by the frozen key, preserves `args == (message,)`, and derives nothing in the exception constructor. | Engineering | Exact-pin focused suite: `109 passed, 1 skipped`; installed-wheel behavioral subset: `101 passed, 1 skipped`. | `VERIFIED` |
| `PCA-05` | `R4` | `v2.lske` defines and exports only its package version; ontology version is owned only by `v2.lske.schema`. | Engineering | Package ownership test and external wheel probe passed. | `VERIFIED` |
| `PCA-06` | `R1` / `R4` | Any correction to constitutional-lock implementation state remains a human governance act. | Constitutional steward | No governance file was activated or silently rewritten in Stage 1. | `HUMAN_ACTION_REQUIRED` |
| `PCA-07` | `R1` | Scientific Constitution placement in precedence remains an unissued ruling. | Constitutional steward | No ruling was fabricated. | `HUMAN_ACTION_REQUIRED` |
| `PCA-08` | `R1` | Authoritative Observatory specification remains an unissued frozen-input decision. | Constitutional steward | No supersession was fabricated. | `HUMAN_ACTION_REQUIRED` |
| `PCA-09` | `R4` | Earlier mechanically derived predecessor notices are preserved outside this bounded Stage-1 transaction. | Engineering / independent reviewer | Stage-1 candidate does not alter predecessor specifications. | `FIXED` |
| `PCA-10` | `R1` | A missing Final Implementation Authority Review cannot be recreated or attributed by engineering. | Constitutional steward | Human review fields remain blank. | `HUMAN_ACTION_REQUIRED` |
| `PCA-11` | — | Immutable finding definition and closure condition are unavailable. | Audit owner | No status was inferred beyond preserving it open. | `OPEN` |
| `PCA-12` | — | Immutable finding definition and closure condition are unavailable. | Audit owner | No status was inferred beyond preserving it open. | `OPEN` |
| `PCA-13` | `R1` / `R4` | Planning-material status and withdrawal/scope decisions remain human governance matters. | Constitutional steward | Stage-1 engineering records claim no authority for that corpus. | `HUMAN_ACTION_REQUIRED` |
| `PCA-14` | `R4` | Prior bounded erratum work is not expanded by this Stage-1 transaction; full retirement remains unissued. | Engineering; constitutional steward for retirement | No retirement claim was made. | `HUMAN_ACTION_REQUIRED` |
| `PCA-15` | — | Immutable finding definition and closure condition are unavailable. | Audit owner | No status was inferred beyond preserving it open. | `OPEN` |
| `PCA-16` | `R2` | Earlier committed baseline `0ab2251...` could not represent the uncommitted Stage-1 implementation. The bounded candidate is now checkpointed and its final exact commit must still pass fresh clean-clone reproduction. | Engineering for proof; repository owner for corpus authority | Development and installed-wheel checks passed; final exact-commit clean-clone evidence is pending. | `BLOCKED` |
| `PCA-17` | `R4` | Dated baseline documents remain historical records; current Stage-1 state is reported additively in the acceptance record. | Engineering | `outputs/P1_V2_PHASE1_STAGE1_ACCEPTANCE_RECORD.md` distinguishes baseline, checkpoint, and pending final proof. | `FIXED` |
| `PCA-18` | `R4` | Package version `1.1.0` and ontology version `1.1.2` are distinct; the exact evaluator pin and all 23 schemas now exist in the candidate. | Engineering | Exact-pin suite, 23-schema compilation, external wheel probe, and ownership tests passed. | `VERIFIED` |

## Stage-1 engineering evidence — 2026-08-02

- Recovered failed edit: `tests/lske/test_schema_generation.py`, classified `PARTIAL_CHANGE`, repaired within the frozen closure audit.
- Safe implementation checkpoint: `3ac369910e66fda72edc67a6ae7de21c3e71c5b8`.
- Focused Stage-1 result: `109 passed, 1 skipped`.
- Exact evaluator result: `jsonschema==4.25.1`; `109 passed, 1 skipped`.
- Schema set: exactly 23; all Draft 2020-12 schemas compile; offline references pass.
- Behaviour catalogue: all N-01…N-32 positive payloads pass; every LSKE-owned object rejects one undeclared key; N-31 is explicitly exempt because its interior is Observatory-owned.
- Determinism: two consecutive generations produced 23 schemas with clean schema diffs; generation suite `8 passed`.
- Packaging defect found and repaired: the first wheel omitted inherited `ros` imports. `pyproject.toml` now packages `ros*` without changing any `ros/*.py` file.
- External installed-wheel result: import resolved from `site-packages`; exact evaluator, 23 schemas, offline references, deterministic access, public surface, and append-only writer passed; behavioral subset `101 passed, 1 skipped`.
- Stage boundary: no `ros/*` source diff; `len(ros.model.COLLECTIONS) == 11`; the 11-to-20 expansion remains Stage 2.
- Research CI scope: `168 passed`.
- Unit CI scope: `194 passed, 1 skipped, 1 failed`; sole failure is the unrelated absent candidate document `docs/architecture/OBSERVATORY_ARCHITECTURE.md`.

## Verification limits

1. **No re-certification is authorized by this ledger.** `PCA-03` and governance findings remain `HUMAN_ACTION_REQUIRED`.
2. **PCA-02, PCA-11, PCA-12, and PCA-15 remain `OPEN`.** Their immutable definitions and closure conditions are unavailable.
3. **PCA-16 remains `BLOCKED` until the final exact documentation commit passes a fresh clean clone, exact declared dependency verification, wheel build, external installation, and clean-status checks.**
4. **The unrelated Observatory document failure is not silently repaired.** The file exists only outside the candidate and is not imported without repository authority.
5. **No Git history was rewritten, no credential contents were inspected, and no human identity, decision, signature, provider action, or attestation was invented.**

## Next admissible actions

1. Commit this bounded documentation/evidence update and record the exact final candidate SHA.
2. Reproduce that exact SHA in a fresh clean clone; run focused and CI-equivalent Stage-1 checks; build and externally install its wheel.
3. Update this ledger and the acceptance record with exact clean-clone evidence; change `PCA-16` only if its stated engineering proof condition is met, without claiming broader authority-corpus closure.
4. Obtain non-secret proof of provider-side credential revocation and explicit human authorization before any history remediation.
5. Recover the immutable PCA register before changing PCA-02, PCA-11, PCA-12, or PCA-15.
