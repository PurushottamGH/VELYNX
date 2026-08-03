# P1-v2 Phase 1 Stage-1 Engineering Acceptance Record

**GOVERNANCE: DRAFT — NO ADMISSIBLE EVIDENCE**

- **Record date:** 2026-08-02
- **Candidate branch:** `p1-v2-stage1-candidate-rebuild2-20260802`
- **Recovered baseline:** `0ab225176b10f98fa763b3914b27a2162b550205`
- **Implementation checkpoint:** `3ac369910e66fda72edc67a6ae7de21c3e71c5b8`
- **Evidence-record commit:** `7ed5d40feca227018a7e2abb44a0c5ba4f368430`
- **Clean-clone implementation commit:** `78d3f4ff2c0dc4f0eab504b317398a535ef3a9a0`
- **Verified evidence-closure commit:** `b38c32c189c1d9f7e5fa5a053947af51b83edf68`
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
| Formatting | Black reported `8 files would be left unchanged` in the final implementation verification surface |
| Fresh clean clone at `78d3f4ff2c0dc4f0eab504b317398a535ef3a9a0` | `109 passed, 1 skipped`; exact `jsonschema==4.25.1`; 23/23 schemas compiled; offline references passed |
| Clean-clone deterministic generation | Two consecutive 23-schema generations; `GIT_SCHEMA_DIFF=CLEAN` after repository LF normalization through `.gitattributes` |
| Clean-clone wheel build | PASS; `velynx-0.1.0-py3-none-any.whl` built from the exact clean clone |
| Exact clean-clone wheel external probe | Module resolved from the fresh environment's `site-packages`; exact evaluator, 23 schemas, Draft compilation, offline references, deterministic accessors, public surface, and append-only writer passed |
| Exact clean-clone installed-wheel behavioral subset | `101 passed, 1 skipped` from outside the repository with isolated Python and repository `pythonpath` disabled; schema-file byte test excluded because generated JSON files are repository artifacts, not wheel package data |
| Research CI scope | `168 passed` |
| Unit CI scope | `194 passed, 1 skipped, 1 failed`; the sole failure is a pre-existing non-Stage-1 missing document, `docs/architecture/OBSERVATORY_ARCHITECTURE.md`, absent from the candidate commit |
| Broad whole-tree pytest | Not an acceptance command: it collected archived/manual/environment-dependent scripts and failed during collection for unrelated legacy conditions |
| Candidate and clean-clone Git status | Clean after verification; transient `build/` and `*.egg-info/` paths remained ignored |

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

A complete dependency-resolving wheel installation was also attempted. It reached the distribution's unrelated heavy dependency chain through `sentence-transformers` and `torch`, then failed on Windows with `WinError 206` for a deeply nested Torch license path. The bounded LSKE installation therefore used `--no-deps`, followed by exact installation of `jsonschema==4.25.1`, `PyYAML==6.0.3`, and `pytest==8.4.1`. This proves the installed LSKE surface and its inherited runtime imports; it does **not** claim successful installation or verification of every unrelated dependency declared by the broader `velynx` distribution.

## 7. Known non-Stage-1 condition

The repository's configured unit scope has one failure because `tests/unit/test_observatory.py` requires `docs/architecture/OBSERVATORY_ARCHITECTURE.md`, which is absent from this candidate commit. A copy exists only in another working directory. It was not imported into the candidate because Stage-1 recovery must not mix unrelated, uncommitted corpus without repository authority. This condition must be handled by the repository owner independently of LSKE Stage 1; it is not evidence against the 27 LSKE acceptance criteria.

## 8. Exact-commit reproduction disposition

Commit `78d3f4ff2c0dc4f0eab504b317398a535ef3a9a0` independently reproduced the complete Stage-1 implementation surface in a fresh clean clone. The focused suite, exact evaluator, 23-schema Draft compilation, offline registry, two-pass byte-deterministic generation, wheel build, external installed-wheel probe, behavioral subset, and clean Git status all passed. The only changes after that commit are these documentation evidence updates; their exact evidence-closure commit must receive a final minimal clean-clone focused-suite and clean-status check before the terminal engineering verdict.

## 9. Human and governance boundary

This record does not constitute independent human code review, dependency approval, merge approval, release approval, governance adoption, credential revocation proof, history-rewrite authorization, or scientific validation. Those acts remain in `P1_V2_HUMAN_GATE_CHECKLIST.md`; identity and approval fields remain blank.

---

# Part II — Stage-1 Red-Team Remediation Correction

**GOVERNANCE: DRAFT — NO ADMISSIBLE EVIDENCE**

- **Correction date:** 2026-08-03
- **Remediation branch:** `p1-v2-stage1-remediation-20260802`
- **Remediation commit:** `647fe7739a205a081d91acfb98f87aa4c088bf2c`
- **Pre-remediation tip corrected by this part:** `2f1c7b397573315923f87fb80eadd07517a3ba9f`
- **Clean-clone verification commit:** `647fe7739a205a081d91acfb98f87aa4c088bf2c`
- **Standing:** Engineering verification record only. Unchanged from Part I: it does not register the specification, activate governance, raise Scientific Readiness, or create admissible scientific evidence.

## 12. Why this correction exists

An adversarial red team found six defects (D-01…D-06) in the Stage-1 surface that
Part I certified. Part I's claims were accurate reports of the commands actually
run; they were nonetheless **insufficient**, because the suite they cite could not
fail on the defect vectors. This part corrects the record. It does not delete
Part I: Part I remains a true account of the artifact as it stood at `2f1c7b3`,
and the gap between "the tests passed" and "the contract holds" is precisely what
D-01 exposed.

Two Part I statements are **superseded** rather than merely extended:

| Part I statement | Status | Correction |
|---|---|---|
| §5 `Focused Stage-1 suite in development environment` — `109 passed, 1 skipped` | SUPERSEDED | `1138 passed, 7 skipped`. The prior suite could not fail on D-01…D-04, so the counts are not comparable. |
| §5 `Exact clean-clone installed-wheel behavioral subset` — `101 passed, 1 skipped … schema-file byte test excluded` | SUPERSEDED | `1137 passed, 8 skipped`. The exclusion is now an in-band `pytest.mark.skipif` with a printed reason rather than an off-record omission, and the delta from the source-tree run is accounted for by collection-set differencing in §12.4 instead of left to inference. |

Part I §4's AC-P1-01…27 dispositions are **not** restated as PASS by this part.
They were derived from the superseded suite. AC-P1-04, AC-P1-12, AC-P1-14, and
AC-P1-27 were each directly implicated by a defect below and are re-evidenced here
against the corrected surface; the remaining criteria are unchanged in mechanism
but were never exercised against the defect vectors, so their standing is
engineering-verified, not independently certified.

## 12.1 D-01…D-06 closure

| ID | Defect | Fix | New observable | Regression evidence |
|---|---|---|---|---|
| D-01 | `_leaf_assertion_errors` returned `[]` for an applicator error with empty `context`, so the failure vanished and `validate` returned success. A null `direction` on any of the four evidential relation types was silently accepted, violating RB-02 cl. 2. | Every `{"not": {"type": "null"}}` presence-encoding reachable inside a `then` replaced with a positive assertion via `_present(...)`; `_leaf_assertion_errors` now raises `OntologyError` rather than returning `[]`. | `direction: null` on `supports`/`refutes`/`contradicts`/`validated_by` is REJECTED with `/direction` `enum` and `type`, both `derived=False`. | `test_null_direction_on_every_evidential_relation_type_is_reported`, `test_applicator_with_no_reportable_leaf_fails_closed`, `test_oneof_with_two_matches_also_fails_closed`, `test_raw_and_public_validators_agree_on_every_mutation`; self-attack A-01, A-05 |
| D-02 | `absolute_schema_path` omits `$ref`/`$defs` splice points, so emitted schema pointers did not resolve against the schema graph, violating RF-01 cl. 3 item 2. | `_schema_pointer_for` walks the registered graph tracking resource boundaries, emitting the clause-3 form `{$id}#{RFC6901 from resource root}`; `_follow_ref` handles the splice. | Every emitted pointer resolves to the exact keyword it names. | `test_every_emitted_pointer_resolves_and_names_its_keyword` over the full mutation corpus; self-attack A-03 |
| D-03 | `_cross_value_failures` emitted `ascending`, `creation`, `transitionState` — names outside the RF-01 cl. 3 item 3 value space — and over-rejected a coverage-undercount payload that raw jsonschema accepts. | Function and its call site deleted in full. | No emitted keyword lies outside the frozen vocabulary; no applicator is ever reported. | `test_no_emitted_keyword_is_outside_the_frozen_vocabulary`; self-attack A-02, A-06 |
| D-04 | `type(value) in {str, bool, int, float}` rejected the scalar subclasses the schemas admit, so `from_payload` could build a payload that the `LskeRecord` constructor then rejected as unfrozen. | `isinstance(value, (str, bool, int, float))`, per RF-05 cl. 2.1. | `str`/`int`/`float` subclasses survive the freeze audit and the full round trip. | `test_frozen_leaf_predicate_admits_every_scalar_instance`, `test_frozen_leaf_predicate_still_rejects_non_scalars`, `test_subclass_leaves_survive_the_full_from_payload_roundtrip`; self-attack A-07 |
| D-05 | PyYAML undeclared in `requirements.txt` — the authoritative site given `dynamic = ["dependencies"]` — while `ros.governance`, `ros.protocol`, and `ros.store` import it. | `PyYAML==6.0.3` declared. | Wheel `Requires-Dist` carries PyYAML; `import ros.store` succeeds in an environment built only from wheel metadata. | Installed-surface probe (§12.3); self-attack A-09 |
| D-06 | `tests*` shipped in the wheel, putting a second copy of `tests.lske` on the installed surface, so an installed run could import repository-shaped modules and pass for the wrong reason; separately, the schema byte-match test was excluded from the installed run without an in-band record. | `tests*` moved from `include` to `exclude` with the reason recorded in `pyproject.toml`; the byte-match test guarded by `skipif` with an explicit printed reason. | Wheel contains 0 `tests/` entries; the skip is reported by `pytest -rs` rather than silently dropped. | `test_exactly_23_generated_schema_files_are_byte_identical_to_canonical_state` (guarded); self-attack A-08 |

**Closure is differential, not merely assertional.** A passing suite on the fixed
code does not by itself prove a defect existed. Each defect was therefore
demonstrated *present* on the pre-remediation tip `2f1c7b3` (checked out into a
separate worktree, nothing stashed) and *absent* on `647fe77`:

| Probe on `2f1c7b3` | Observed |
|---|---|
| D-01 | `direction: null` SILENTLY ACCEPTED on all four evidential types (`supports`, `refutes`, `contradicts`, `validated_by`) |
| D-02 | The remediation harness cannot even import against the defective source — `_SCHEMA_BY_ID` does not exist, because resource-aware pointer emission was absent |
| D-03 | `ascending`, `creation`, `transitionState` present in `schema.py`; `_cross_value_failures` still defined |
| D-04 | Frozen-leaf predicate uses `type(value) in {...}`, not `isinstance` |
| D-05 | PyYAML absent from `requirements.txt` |
| D-06 | `tests*` present in the wheel `include` list |

On `647fe77` the same probe reports zero defects present, and the D-04 closure was
additionally confirmed *behaviourally* rather than by source pattern: `str`, `int`,
and `float` subclasses pass the leaf predicate and survive the full
`from_payload` → `LskeRecord` round trip, while a raw `dict` leaf is still rejected
at pointer `/k`. (A source-text probe initially flagged D-04 as still present on
the remediated file; that was a false positive matching the explanatory comment at
`v2/lske/schema.py:1467`, not the predicate at line 1470.)

**SPEC-CONFLICT-01** (raised, not resolved): §9.2.4 N-18 requires
`uncertainty.interval` to be ascending. Draft 2020-12 has no keyword comparing
`interval[0]` to `interval[1]`, and RF-01 cl. 3 item 3 admits no keyword that
could name such a comparison. The rule is therefore **unrepresentable at the
schema layer**. D-03's fix removes the invented encoding; it does not implement
the rule, and no ascending check is enforced anywhere in Stage 1 today.
Enforcement belongs to the store-level layer owning MEM-01…MEM-06 (§9.4.2). This
is a specification-versus-mechanism conflict for the specification owner, recorded
here rather than silently amended.

## 12.2 Corrected engineering evidence

| Check | Result |
|---|---|
| Focused Stage-1 suite, development environment | `1138 passed, 7 skipped` |
| Focused Stage-1 suite, exact evaluator `jsonschema==4.25.1` | `1138 passed, 7 skipped` |
| Adversarial mutation corpus | 238 mutation cases across all 23 entry surfaces, 12 mutation families; `test_differential.py` collects 1035 tests in total (each case is asserted through several independent invariants) |
| Differential invariant `RAW == PUBLIC` | Holds on every case; the only two accepted mutations are pinned by `_EXPECTED_ACCEPTED` and explained in §12.5 |
| Independent self-attack | 10 probes A-01…A-10, including an exhaustive `not`-under-`then` sweep, a nested-interior mutation sweep, and a null-injection sweep over every property of every surface; **all held** in both the worktree and the clean clone |
| Schema count | 23/23 |
| Two-pass deterministic regeneration | `regenerated 0 of 23` on both passes; `GIT_SCHEMA_DIFF=CLEAN` after each |
| Clean clone at `647fe77` | `1138 passed, 7 skipped` under exact `jsonschema==4.25.1` |
| Cross-version check | Identical counts under `jsonschema==4.26.0`; the result is not pin-fragile |
| Wheel build | `velynx-0.1.0-py3-none-any.whl`, 131 entries, **0** `tests/` entries, **0** `schemas/` entries |
| Wheel `Requires-Dist` | includes `jsonschema==4.25.1` and `PyYAML==6.0.3` |
| Installed-surface probe | `v2.lske` and `ros` resolve from `site-packages` with the repository off `sys.path`; 23 schemas compiled; D-01 vector rejected with resolvable pointers |
| Installed-wheel bounded subset | `1137 passed, 8 skipped` from outside the repository |
| Whole-repository suite | `29 failed, 2634 passed, 10 skipped` — see §12.6 |
| Worktree Git status | Clean at the evidence-closure commit recorded in §12.8 (`git status --porcelain` empty) |
| Diff `2f1c7b3..647fe77` | 12 files changed, 1193 insertions(+), 155 deletions(-) — code, tests, schemas, packaging. This Part II text lands in the separate evidence-closure commit of §12.8. |

## 12.3 Installed-surface probe

Run with the repository absent from `sys.path` (`python -P`, `PYTHONPATH=`) and
CWD outside the repository:

- `v2.lske.schema` resolves to `wheel_env\Lib\site-packages\v2\lske\schema.py`; `inside repo? False`
- `import yaml` succeeds at 6.0.3 from wheel metadata alone; `import ros.store` succeeds (D-05)
- 23 schemas compile without the repository `schemas/` directory
- The D-01 vector is REJECTED with 2 failures, `/direction` `enum` and `type`, both `derived=False`

## 12.4 The installed-wheel delta, stated rather than inferred

Source tree `1138 passed, 7 skipped`; installed wheel `1137 passed, 8 skipped`.
Both runs **collect the identical 1145 test IDs** — verified by differencing the
two `--collect-only` sets, which is empty in both directions. The delta is
therefore exactly one test changing outcome from passed to skipped, and nothing
else: `test_exactly_23_generated_schema_files_are_byte_identical_to_canonical_state`,
under the D-06 guard.

`schemas/lske/` is a repository artifact and deliberately not wheel package data,
so that assertion is *source-tree build evidence*; under an installed run there is
nothing to compare against and it would be vacuous rather than true. It is now
skipped with a printed reason instead of dropped without one.

**Recorded honestly:** an earlier draft of this section attributed the delta to
three companion cases "not collected against an installed distribution." That was
wrong. The external test directory held a stale copy of `test_differential.py`
predating this remediation's last three tests, so those three were genuinely
uncollected — an artifact of the harness, not a property of the wheel. The copy
was refreshed to byte-identity with the committed clean clone and the run repeated;
the numbers above are from that run. The original 4-test claim is withdrawn.

This is a **bounded** claim. It proves the installed LSKE surface and its declared
runtime imports. It does **not** claim that every unrelated dependency of the
broader `velynx` distribution installs or verifies; the Part I §6
`sentence-transformers`/`torch` `WinError 206` condition is unchanged and remains
outside Stage 1.

## 12.5 Two accepted mutations, and why they are correct

The corpus accepts exactly two mutations, both on the `record` fragment — the
shared envelope, not an entry surface any caller writes to:

- `record::add-unknown` — `record` carries neither `additionalProperties` nor
  `unevaluatedProperties`; closure is the composing collection's obligation
  (§9.13.1). All 22 collection surfaces reject the same undeclared key, asserted
  by `test_the_record_fragment_delegates_closure_to_its_collections`.
- `record::break-allof-branch:id-prefix` — `#/$defs/record_id` is the generic
  `^[A-Z]{3,5}-[0-9]{4}-[0-9]{4}$`, which `ZZZ-9999-9999` satisfies. Every
  collection narrows it (e.g. `^HYP-…`), asserted by
  `test_the_generic_record_id_pattern_is_narrowed_by_every_collection`.

Both are frozen by `_EXPECTED_ACCEPTED`, so any *new* silent accept fails the
suite rather than passing unnoticed.

## 12.6 Whole-repository failures are pre-existing and non-Stage-1

The whole-repository suite reports `29 failed`. All 29 are outside `tests/lske/`:
24 in `tests/p1_os/test_templates.py` (`LineEndingError: Mixed line endings are
not allowed` — 12 `test_round_trips_deterministically` and 12 `test_uses_lf_only`),
4 in `tests/p1_os/test_installation.py`, and 1 in `tests/unit/test_observatory.py`
(the missing `docs/architecture/OBSERVATORY_ARCHITECTURE.md` already recorded in
Part I §7).

**Verified pre-existing by set identity, not by count.** The pre-remediation tip
`2f1c7b3` was checked out into a separate worktree and the same three files run
with the same interpreter: `29 failed, 82 passed`. Differencing the two sorted
`FAILED` node-ID lists is **empty in both directions** — the failure sets are
identical, not merely the same size. The remediation neither introduced nor
repaired any of them. Part I §7 disclosed only
the single observatory failure; the other 28 were not disclosed, and this section
corrects that omission. They remain the repository owner's to handle and are not
evidence for or against the LSKE criteria.

## 12.7 Boundaries held

- **Stage 2 not entered.** `git diff 2f1c7b3 647fe77 -- ros/` is empty;
  `len(ros.model.COLLECTIONS) == 11`; `v2/lske/` still contains exactly
  `__init__.py`, `errors.py`, `events.py`, `schema.py`. No reader, transaction
  layer, CLI, server, or network client was introduced.
- **No governance change.** No status was raised, no gate opened, no
  specification amended. SPEC-CONFLICT-01 is raised for the owner, not resolved.
- **No scientific claim.** Nothing in this part creates, promotes, or admits
  evidence, and no hypothesis, result, or interpretation is asserted.
- **No test weakened to obtain green.** The D-03 test correction removes an
  assertion on an *invented* keyword and replaces it with the positive assertion
  that no such keyword is emitted. No expected result was edited to match
  defective behavior; every count in §12.2 rose.
- **Security posture unchanged.** No credential was exposed, rotated, or acted
  on; no provider action was taken; no human identity or approval was fabricated.
  The unrotated GCP key in Git history remains HUMAN_ACTION_REQUIRED and A-07 of
  the original PCA audit still FAILs by design.

## 12.8 Commit topology of this remediation

| Commit | Contents | Standing |
|---|---|---|
| `2f1c7b397573315923f87fb80eadd07517a3ba9f` | Pre-remediation tip. The artifact Part I certified, with D-01…D-06 present. | Superseded |
| `647fe7739a205a081d91acfb98f87aa4c088bf2c` | The remediation: `v2/lske/schema.py`, 4 regenerated schema JSON files, 4 test files, `pyproject.toml`, `requirements.txt`, `regen_schemas.py`. All engineering evidence in §12.2 was measured at this tree. | Verification subject |
| Evidence-closure commit (this Part II text) | Documentation only. Touches exactly `outputs/P1_V2_PHASE1_STAGE1_ACCEPTANCE_RECORD.md`. No code, test, schema, or packaging file. | Record of the above |

The separation is deliberate: every executable claim in §12.2 is reproducible from
`647fe77` alone, without depending on the commit that describes it. An independent
certifier should verify against `647fe77` and read this text as commentary, not as
input.

## 12.9 Standing of this correction

This part is engineering verification only. It does not constitute independent
human code review, dependency approval, merge approval, release approval,
governance adoption, credential revocation proof, history-rewrite authorization,
or scientific validation. Those remain in `P1_V2_HUMAN_GATE_CHECKLIST.md` with
identity and approval fields blank.


---

# Part III — N-18 Amendment Closure (SPEC-CONFLICT-01)

**GOVERNANCE: DRAFT — NO ADMISSIBLE EVIDENCE. THE GOVERNING AMENDMENT IS PROPOSED AND UNREGISTERED.**

- **Closure date:** 2026-08-03
- **Branch:** `p1-v2-stage1-remediation-20260802`
- **Parent commit:** `aa7f751475525c25153c5db362f19350cb10e252`
- **Governing amendment:** `P1_V2_LSKE_SPECIFICATION_v1.1.3.md` — **Proposed / Unregistered**
- **Standing:** Engineering closure only. This part does **not** certify Stage 1, does not register v1.1.3, and does not open any gate.

## 13. What this part does and does not overturn

Parts I and II stand. Nothing below rewrites them.

- The independent Stage-1 certification of `aa7f751`
  (`outputs/P1_V2_STAGE1_INDEPENDENT_CERTIFICATION_AA7F751.md`) **FAILED**, and it
  was **correct to fail**. Measured against the then-governing contract
  `v1.1.2`, `N-18` was enforced only in part — `interval` type, arity and
  conditional nullability were schema-enforced, the ascending requirement was
  not — and `AC-P1-08` forbids a partial catalogue entry. `N-18: FAIL —
  PARTIAL` and `AC-P1-08: FAIL` were true statements about that artifact under
  that contract.
- That verdict is **not** reversed by this part and is **not** reversed by
  `v1.1.3`. It remains the terminal disposition of `aa7f751` against `v1.1.2`.
- What changed is the **contract**, not the artifact's conformance to the old
  one. `v1.1.3` `RG-02` splits `N-18` into a structural half owned by the Stage-1
  schema layer and a semantic half owned by `MEM-11` in
  `ros.store._check_memory` at Stage 4. Under `v1.1.3` the Stage-1 schema layer
  is no longer the owner of the ascending sentence, so its absence there ceases
  to be partiality (`RG-04`).
- Recertification against `v1.1.3` has **not** been performed and cannot be
  performed while `v1.1.3` is unregistered. No `AC-P1-08` PASS is claimed here.

## 13.1 Two stale references in the prior record, corrected

The following appear in earlier engineering commentary and are wrong on the
normative facts. They are corrected here rather than edited out of Part II.

| Stale statement | Correct statement | Authority |
|---|---|---|
| The ascending check is deferred to **Stage 2**. | It is owned at **Stage 4**. Stage 2 is `ros.model` 11 → 20 collections and nothing else. | `v1.1.2` §9.8 build order; `v1.1.3` `RG-01` cl. 2, `RG-03` |
| The relevant store-integrity register is **`MEM-01`…`MEM-06`**. | The canonical register is **`MEM-01`…`MEM-10`**, and `v1.1.3` `RG-03` appends **`MEM-11`** as the eleventh. | `v1.1.0` §3.6 as ruled by `RC-03`; `v1.1.3` `RG-03` |

## 13.2 The authorized test correction

Exactly one code path changed: `tests/lske/test_envelope.py`. No production
module, generated schema, packaging file, or `ros/` module was touched.

- The stale commentary in
  `test_cross_value_and_collection_specific_normative_conditions` — which cited
  `SPEC-CONFLICT-01` as an open conflict and `MEM-01`…`MEM-06` as the register —
  was replaced with the authoritative citation chain `RG-01` cl. 2 / `RG-02` /
  `RG-03` / Stage 4 / `AC-P1-28`. The assertion itself
  (`"/uncertainty/interval" not in pointers`) is unchanged; only its
  justification is now correct.
- Four parametrized tests were added, pinning the ruled Stage-1 boundary:
  every ordering of two numbers — `[1.0, 2.0]`, `[1.0, 1.0]`, `[2.0, 1.0]` — is
  a structural **PASS** for both `ci95` and `iqr`; malformed structure is
  **REJECTED**; a non-`ci95`/`iqr` `kind` requires `null`; a `ci95`/`iqr` `kind`
  forbids it. `[1.0, 1.0]` is admissible on `RG-02` cl. 3 grounds: the ascending
  relation is non-strict, and a zero-width `ci95`/`iqr` is a real empirical
  outcome.
- **No other test was weakened.** The suite count rose from `1138 passed, 7
  skipped` at `aa7f751` to `1161 passed, 7 skipped`; the delta is exactly the 23
  new N-18 node IDs. No expected result was edited to match observed behavior.

## 13.3 A pre-existing defect raised, not disposed of

`RG-05` cl. 1 makes raising mandatory and disposing the defect. Accordingly:

**Finding N18-E1.** An `uncertainty.interval` of three or more numbers, with
`kind ∈ {ci95, iqr}`, is rejected — but with `OntologyError`, not the
`SchemaViolation` that `RF-01` contracts for a reportable structural failure.
The childless `items: false` applicator reaches the `_leaf_assertion_errors`
raise in `v2/lske/schema.py` before the co-located and perfectly reportable
`maxItems: 2` can be collected.

- **Pre-existing.** `git diff --stat v2/lske/schema.py` against `aa7f751` is
  empty. Not caused by `RG-02` and not caused by this transaction.
- **Fails closed.** The record never validates either way, so D-01's
  no-silent-acceptance property is intact. The defect is in the failure
  *class*, not in the accept/reject decision.
- **Blast radius.** `"items": false` occurs in exactly one generated schema,
  `schemas/lske/observations.schema.json`, twice.
- **Not repaired here.** Repair requires editing `v2/lske/schema.py`, which this
  transaction is forbidden to do. The three-item vector is therefore held out of
  the ordinary `SchemaViolation` parametrization and pinned by
  `test_n18_stage1_rejects_an_over_long_interval`, which asserts the invariant
  that must hold both now and after repair.
- **Disposition.** Open. Requires a separate authorized transaction. It is not
  an `N-18` defect and does not affect `RG-01`…`RG-05`.

## 13.4 Boundaries held

- `git diff aa7f751 -- v2/ ros/ schemas/` is **empty**. All 23 LSKE schemas are
  byte-identical to the parent commit.
- `len(ros.model.COLLECTIONS) == 11`. **Stage 2 not entered.**
- `grep -rn "MEM-11" ros/ v2/` returns **0**. **Stage 4 not entered.** `MEM-11`
  exists as a normative sentence and a recorded obligation only.
- No governance status was raised, no gate opened, no human approval recorded.
