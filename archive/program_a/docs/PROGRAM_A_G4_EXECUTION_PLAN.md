# PROGRAM A — G4 EXECUTION PLAN

## 1. Executive Summary

This is the master execution checklist for converting the current ES-1 working
tree into the legitimate G4 Freeze Package.  It executes the already-frozen
mechanism and PA-3 addendum; it makes no architectural, scientific, or
governance decision.

The package is complete only when a single G4 commit contains the complete
freeze payload, `CONSTANTS_HASH` is a real pinned digest of the completed
register, the B2 and B3 records are genuine, and post-freeze repository
verification passes against that exact commit.  No emission or binding
implementation is part of this plan.

## 2. Current State

- ES-1, the T1 mechanism specification, and the PA-3 addendum are frozen in
  substance; the addendum remains marked DRAFT until it is co-frozen.
- The prior commit `0674b8d` is not the G4 commit.  It does not contain the
  complete freeze payload and does not constitute B2 or B3 completion.
- `program_a/constants.py` has four deliberately empty register entries:
  `SUPPORT_TEST_PARAMS`, `CONTRADICTION_MATERIALITY_PARAMS`,
  `EXTRACTION_PARAMS`, and `ANSWER_TEMPLATES`.  Consequently
  `CONSTANTS_HASH` is `None` and no final digest exists.
- The T1 document, PA-3 addendum, gate, Program A package, Program A tests,
  and EXP-1 support files are present as working-tree material and must be
  deliberately classified and staged.  Unrelated pre-existing working-tree
  changes must remain outside the G4 payload.
- B2 and B3 records are not yet legitimate.  B2 must be a direct
  ScientificAuditor signature; B3 must pin the created G4 commit.

## 3. Remaining Execution Tasks

### E1 — Classify and clean the repository for the G4 payload

- **Objective:** Produce a clean, intentional index containing only the G4
  freeze payload; preserve every unrelated tracked modification and untracked
  file outside that payload.
- **Exact files involved:**
  `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md`,
  `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md`, `ES1_IMPLEMENTATION_GATE.md`,
  `PROGRAM_A_REGISTER_AUDIT.md`, `program_a/__init__.py`,
  `program_a/constants.py`, `program_a/types.py`,
  `program_a/evidence/__init__.py`, `program_a/evidence/snapshot_builder.py`,
  `program_a/evidence/snapshot_store.py`,
  `program_a/extraction/__init__.py`, `program_a/extraction/claim_extraction.py`,
  `program_a/mechanism/__init__.py`, `program_a/mechanism/support_tests.py`,
  `program_a/mechanism/evidence_states.py`,
  `tests/program_a/conftest.py`, `tests/program_a/test_claim_extraction.py`,
  `tests/program_a/test_constants_freeze.py`,
  `tests/program_a/test_hidden_state_guard.py`,
  `tests/program_a/test_import_guard.py`,
  `tests/program_a/test_pa2_doc_consistency.py`,
  `tests/program_a/test_snapshot_store.py`,
  `tests/program_a/test_stub_contracts.py`,
  `tests/program_a/test_tier_set_triplication_regression.py`,
  `tests/program_a/test_types.py`, `experiments/EXP1/__init__.py`,
  `experiments/EXP1/artifact_specs.py`, `experiments/EXP1/calibration.py`,
  `experiments/EXP1/config.json`, `experiments/EXP1/dataset.py`,
  `experiments/EXP1/decision.py`, `experiments/EXP1/manifest.py`,
  `experiments/EXP1/program_a_adapter.py`, `experiments/EXP1/report.py`,
  `experiments/EXP1/rubric.py`, `experiments/EXP1/run.py`, and the frozen
  Program A specification set:
  `PROGRAM_A_API_REFERENCE.md`, `PROGRAM_A_ARCHITECTURE.md`,
  `PROGRAM_A_BINDING_SPEC.md`, `PROGRAM_A_BUILD_CHECKLIST.md`,
  `PROGRAM_A_CONFIDENCE_DECISION_TREE.md`, `PROGRAM_A_CONFIDENCE_MECHANISM.md`,
  `PROGRAM_A_CONFIDENCE_REQUIREMENTS.md`, `PROGRAM_A_CONFIDENCE_RISKS.md`,
  `PROGRAM_A_DATAFLOW.md`, `PROGRAM_A_DEPENDENCY_GRAPH.md`,
  `PROGRAM_A_FINAL_ARCHITECTURE.md`, `PROGRAM_A_IMPLEMENTATION_ORDER.md`,
  `PROGRAM_A_IMPLEMENTATION_ROADMAP.md`, `PROGRAM_A_MASTER_SPECIFICATION.md`,
  `PROGRAM_A_MODULE_SPEC.md`, `PROGRAM_A_PUBLIC_API.md`,
  `PROGRAM_A_RISK_REGISTER.md`, `PROGRAM_A_SEQUENCE_DIAGRAM.md`, and
  `PROGRAM_A_TEST_STRATEGY.md`.
- **Preconditions:** None.
- **Responsible role:** ReleaseManager.
- **Inputs:** Current working tree; current `HEAD`; the frozen-object inventory
  in T1 §1.
- **Expected output:** A written staging manifest in the ReleaseManager’s
  execution record and an index containing exactly the listed payload, minus
  files explicitly determined not to be part of the frozen-object inventory.
- **Completion criteria:** `git diff --cached --name-only` matches the approved
  manifest; `git diff --name-only` retains all unrelated changes unstaged; no
  relocated emission or binding source is introduced.
- **Blocks G4:** Yes.

### E2 — Prepare genuine B2 sign-off materials

- **Objective:** Prepare the exact, complete freeze object for direct B2
  disposition without proxy approval or backdated attribution.
- **Exact files involved:** `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md`,
  `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md`, `PROGRAM_A_REGISTER_AUDIT.md`, and
  `program_a/constants.py`.
- **Preconditions:** E1 complete; the register-audit record identifies the four
  values still requiring authorship.
- **Responsible role:** ReleaseManager.
- **Inputs:** Staged frozen-object inventory, the closed PA-3 addendum, and the
  four named pending fields in `constants.py`.
- **Expected output:** A B2 review packet with immutable staged file contents,
  file list, and a blank direct-signature block for the ScientificAuditor.
- **Completion criteria:** The packet identifies the exact staged revision and
  contains no claim that B2 has already occurred.
- **Blocks G4:** Yes.

### E3 — Obtain and record the genuine B2 sign-off

- **Objective:** Obtain the ScientificAuditor’s direct, named, dated approval
  of the frozen T1 object and co-frozen PA-3 addendum.
- **Exact files involved:** `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` §12 and
  `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` §D.
- **Preconditions:** E2 complete; no unstaged change to the B2 packet.
- **Responsible role:** ScientificAuditor.
- **Inputs:** E2 B2 review packet.
- **Expected output:** Direct B2 sign-off records in both files, with signer
  identity and date.
- **Completion criteria:** Both records are completed by the ScientificAuditor,
  refer to the same freeze object, and are staged.  Neither role is supplied
  by the ReleaseManager or another proxy.
- **Blocks G4:** Yes.

### E4 — Author the remaining register values

- **Objective:** Author the four previously pending values exactly as required
  by the frozen register, with no inferred defaults.
- **Exact files involved:** `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` §5,
  `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` §C, and
  `program_a/constants.py`.
- **Preconditions:** E3 complete.
- **Responsible role:** ScientificAuditor for the frozen value text;
  ReleaseManager for its faithful execution record.
- **Inputs:** The closed T1 register and PA-3 addendum.
- **Expected output:** Non-empty values for `SUPPORT_TEST_PARAMS`,
  `CONTRADICTION_MATERIALITY_PARAMS`, `EXTRACTION_PARAMS`, and
  `ANSWER_TEMPLATES`, authored in the register and ready for verbatim
  transcription.
- **Completion criteria:** Each field has one explicit value and no field is
  `{}`; all values are signed/dated as B2-authorized register content.
- **Blocks G4:** Yes.

### E5 — Transcribe the authored register into `constants.py`

- **Objective:** Faithfully transcribe the four authored values into the sole
  runtime constants home and replace G4-preparation assertions with frozen
  assertions.
- **Exact files involved:** `program_a/constants.py` and
  `tests/program_a/test_constants_freeze.py`.
- **Preconditions:** E4 complete.
- **Responsible role:** ReleaseManager.
- **Inputs:** E4’s signed register values.
- **Expected output:** Four non-empty runtime constants; no pending-entry list,
  placeholder-specific behavior, or assertion that `CONSTANTS_HASH is None`.
- **Completion criteria:** The runtime values are byte-for-byte faithful to the
  approved register serialization; affected test expectations describe the
  frozen state only.
- **Blocks G4:** Yes.

### E6 — Generate the frozen constants digest

- **Objective:** Generate the deterministic SHA-256 digest only after all
  eleven ordered inputs are final.
- **Exact files involved:** `program_a/constants.py` and
  `tests/program_a/test_constants_freeze.py`.
- **Preconditions:** E5 complete.
- **Responsible role:** ReleaseManager.
- **Inputs:** The E5 runtime constants and the canonical serialization already
  defined in `frozen_constants_digest()`.
- **Expected output:** One reproducibly generated hexadecimal digest and a test
  expectation that recomputes it from the frozen constants.
- **Completion criteria:** Two clean invocations of
  `frozen_constants_digest()` return the same 64-character SHA-256 value; no
  pending placeholder remains.
- **Blocks G4:** Yes.

### E7 — Pin `CONSTANTS_HASH` and prove the pin

- **Objective:** Place the E6 digest in the source and make any future drift
  fail mechanically.
- **Exact files involved:** `program_a/constants.py` and
  `tests/program_a/test_constants_freeze.py`.
- **Preconditions:** E6 complete.
- **Responsible role:** ReleaseManager.
- **Inputs:** E6 generated digest.
- **Expected output:** `CONSTANTS_HASH` set to the generated digest and a green
  equality test between `CONSTANTS_HASH` and `frozen_constants_digest()`.
- **Completion criteria:** The constants test verifies exact equality, rejects
  a changed digest input, and retains the CR-8/L8 firewall check.
- **Blocks G4:** Yes.

### E8 — Assemble and create the genuine G4 freeze commit

- **Objective:** Create one coherent commit containing the full, completed G4
  payload and no unrelated repository work.
- **Exact files involved:** The E1 payload; the E3 B2 records; and the E5–E7
  `constants.py` and constants-test changes.
- **Preconditions:** E1, E3, E4, E5, E6, and E7 complete; all staged checks
  pass.
- **Responsible role:** ReleaseManager.
- **Inputs:** Approved staged index and green staged test evidence.
- **Expected output:** One new commit whose tree contains the complete T1
  object, co-frozen addendum, constants transcription, digest pin, enforcement
  tests, gate record, and supporting frozen Program A materials.
- **Completion criteria:** `git show --name-status <freeze-commit>` matches the
  approved E1 manifest; no required freeze artifact is untracked or omitted;
  no emission/binding implementation is included.
- **Blocks G4:** Yes.

### E9 — Record genuine B3 pinning

- **Objective:** Have the ReleaseManager pin the exact E8 commit and complete
  the co-freeze record without attempting to place a self-referential commit
  hash inside that commit.
- **Exact files involved:** E8 commit object; the B3 blocks in
  `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` §12,
  `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` §D, and
  `ES1_IMPLEMENTATION_GATE.md` §B3.
- **Preconditions:** E8 complete and its commit ID known.
- **Responsible role:** ReleaseManager.
- **Inputs:** E8 commit ID, B2 record, and the approved payload manifest.
- **Expected output:** A signed annotated Git tag named for the ES-1 G4 freeze,
  targeting E8 and recording the ReleaseManager identity, date, and target
  commit ID.  The B3 document blocks must refer to that immutable tag as the
  pin record.
- **Completion criteria:** The tag resolves only to E8; its message names the
  same commit ID; B3 is direct, named, and dated; no file is amended after the
  G4 commit to manufacture a self-hash.
- **Blocks G4:** Yes.

### E10 — Verify the frozen repository state

- **Objective:** Run the prescribed repository verification against the exact
  tagged E8 commit and record PASS/FAIL without changing the frozen payload.
- **Exact files involved:** E8 commit tree, the signed G4 tag, and
  `PROGRAM_A_REPOSITORY_VERIFICATION.md`.
- **Preconditions:** E9 complete.
- **Responsible role:** RepositoryVerifier.
- **Inputs:** G4 tag, E1 manifest, E8 commit, B2 record, B3 tag record, and
  green constants-test evidence.
- **Expected output:** A post-freeze verification result referencing the tag
  and commit ID.
- **Completion criteria:** PASS confirms one coherent commit, complete payload
  presence, genuine B2/B3 records, pinned non-`None` `CONSTANTS_HASH`, and no
  prohibited emission/binding source.  A FAIL returns only the identified
  execution defect to its owner; the tag and frozen mechanism are not revised
  silently.
- **Blocks G4:** Yes.

### E11 — Unlock implementation

- **Objective:** Make the implementation gate accurately reflect the passed,
  tagged G4 freeze and communicate the bounded authorization to begin ES-1
  implementation.
- **Exact files involved:** `ES1_IMPLEMENTATION_GATE.md`.
- **Preconditions:** E10 PASS and all pre-existing non-G4 gate criteria already
  have their real records.
- **Responsible role:** ReleaseManager.
- **Inputs:** E10 PASS, signed G4 tag, B2 record, B3 tag record, and the
  pre-existing gate evidence.
- **Expected output:** A dated GO entry identifying the G4 tag and commit,
  with only genuinely satisfied boxes checked.
- **Completion criteria:** The gate is GO under its stated conjunction; the
  authorization is limited to the implementation work it names and does not
  authorize EXP-1 execution or claims.
- **Blocks G4:** No; it blocks ES-1 implementation start.

## 4. Dependency Graph

```text
E1 Repository cleanup
 └─> E2 B2 packet preparation
      └─> E3 Genuine B2 record
           └─> E4 Author four register values
                └─> E5 constants.py transcription
                     └─> E6 Digest generation
                          └─> E7 CONSTANTS_HASH pinning
                               └─> E8 Single G4 freeze commit
                                    └─> E9 Genuine B3 tagged pin
                                         └─> E10 Post-freeze verification PASS
                                              └─> E11 Implementation unlock
```

## 5. Critical Path

`E1 → E2 → E3 → E4 → E5 → E6 → E7 → E8 → E9 → E10 → E11` is the critical
path.  No step may be moved ahead of its predecessor because each consumes the
exact artifact produced by the previous step.

## 6. Blocking Tasks

G4 is blocked by E1 through E10.  The immediate blocking conditions are:

- unclassified or unintentionally staged repository material;
- absence of a direct B2 record;
- any one of the four register entries still empty;
- inability to generate and pin a non-`None` constants digest;
- absence of the single complete G4 commit;
- absence of the direct B3 tag pin; or
- a post-freeze RepositoryVerifier FAIL.

E11 is not a G4 blocker; it is the separate authorization boundary for
implementation.

## 7. Files Changed Per Task

| Task | Files changed |
|---|---|
| E1 | Git index only; the exact candidate payload listed in E1 is classified, with unrelated files left unstaged. |
| E2 | No frozen-content edit required; B2 packet is prepared from the E1 staged versions. |
| E3 | `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md`; `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md`. |
| E4 | `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md`; `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md`; `program_a/constants.py`. |
| E5 | `program_a/constants.py`; `tests/program_a/test_constants_freeze.py`. |
| E6 | `tests/program_a/test_constants_freeze.py` if the generated-value assertion is added there; no other file. |
| E7 | `program_a/constants.py`; `tests/program_a/test_constants_freeze.py`. |
| E8 | All and only the approved E1 manifest files. |
| E9 | Git annotated tag; B3 blocks are already included in the E8 committed files and refer to the tag record. |
| E10 | `PROGRAM_A_REPOSITORY_VERIFICATION.md` only if the verifier’s result is retained in-repository; it is never amended into E8. |
| E11 | `ES1_IMPLEMENTATION_GATE.md`, in a post-verification gate-record commit if a repository record is required. |

## 8. Required Reviews

| Review | Responsible role | Required artifact | Required result |
|---|---|---|---|
| B2 frozen-object sign-off | ScientificAuditor | T1 preregistration and PA-3 addendum at the E2 staged revision | Direct named, dated approval. |
| G4 pin authorization | ReleaseManager | E8 complete commit | Direct named, dated signed annotated tag targeting E8. |
| Post-freeze repository verification | RepositoryVerifier | E8 tag and commit tree | PASS. |
| Implementation-gate record check | ReleaseManager | E10 PASS plus pre-existing gate evidence | Accurate GO record. |

## 9. Git Operations

1. Inspect `git status --short` and `git diff --cached --name-only`; classify
   the E1 manifest and stage only those files.
2. Recheck the staged content after E3–E7 and run the constants-freeze test
   against the staged worktree.
3. Create exactly one commit for the G4 payload, using a G4 freeze message that
   identifies ES-1 and the T1/PA-3 co-freeze.
4. Capture the resulting commit ID and create one signed annotated tag for the
   B3 G4 pin, with the target commit ID, ReleaseManager identity, and date in
   the tag annotation.
5. Verify the tag target and commit tree before E10.  Do not amend E8 after
   B3 pinning; any later verification or gate-record change is a separate,
   explicitly labelled post-freeze record.

## 10. Expected Final Repository State

- One G4 freeze commit contains the complete, reviewable ES-1 freeze payload.
- The T1 preregistration and PA-3 addendum are co-frozen and have authentic B2
  records.
- All four register values are concrete and faithfully transcribed into
  `program_a/constants.py`.
- `frozen_constants_digest()` returns the pinned SHA-256 value and
  `CONSTANTS_HASH` equals it.
- The G4 commit has an authentic B3 signed annotated tag.
- All unrelated pre-existing work remains outside the G4 commit.
- No emission or binding implementation is added before implementation unlock.
- Post-freeze repository verification reports PASS for the tagged commit.

## 11. Definition of G4 Complete

G4 is complete if and only if E1–E10 are complete, the RepositoryVerifier
returns PASS for the signed B3 tag target, and that target is the single commit
containing the complete G4 payload.  A prior narrative commit, a working-tree
only artifact, a blank/proxy sign-off, a `None` hash, or an untagged commit is
not G4 complete.

## 12. Definition of "Ready for ES-1 Implementation"

ES-1 is ready for implementation only when G4 is complete and E11 has recorded
GO using real evidence for every gate criterion.  This authorizes only the
implementation scope named by `ES1_IMPLEMENTATION_GATE.md`; it does not
authorize experiment execution, scientific claims, or any change to the
frozen mechanism.
