# Project P1 — M1 Scientific Impact and Readiness Assessment

- **Assessment date:** 2026-07-28
- **Scientific phase:** Discovery
- **Evidence target:** Claude Opus engineering review of the M1 platform
- **Scientific decision:** `DEC-2026-0010`
- **Canonical evidence:** `OBS-2026-0015..0019`, `EVD-2026-0009`
- **Verdict:** **Discovery Cycle 001 remains scientifically approved in purpose, but execution is delayed pending minimum apparatus-admissibility gates. The platform is not ready for confirmatory experiments.**

## 1. Executive ruling

Claude's central claim is substantially corroborated, but its scope must be precise.

The current working tree contains a substantial M1 apparatus that passes strong local engineering-conformance checks. Independent verification completed 202 M1/v0-rig tests with 88.5% line coverage, passed the configured Black scope, and completed the config-to-artifact smoke path. This is positive evidence that the local apparatus is coherent enough to preserve for further testing.

It is not confirmatory evidence readiness. The apparatus, v0 configs, tests, and scientific-state files are absent from the committed revision. The assessed smoke manifest records `code_state=dirty`, `untracked_rig=true`, and 39 dirty entries. The committed CI revision does not run the M1 tests, frozen-rig equivalence suite, or config-driven M1 execution. The artifact-integrity and reproducibility jobs inspect legacy surfaces rather than the live M1 run layout and configs. Finally, non-clean run ineligibility is stated and recorded but not machine-enforced.

Therefore:

- no scientific hypothesis, mechanism, negative result, or theory changes status;
- local M1 conformance is accepted as engineering evidence only;
- Discovery Cycle 001's scientific objective remains approved;
- Cycle 001 execution is delayed until the minimum gates in Section 10 pass;
- `EXP-2026-0007` is `Blocked_Confirmatory`;
- the platform cannot currently produce confirmatory evidence.

## 2. Independent evaluation of Claude's claims

| Claim | Assessment | Basis |
|---|---|---|
| Smoke manifest is dirty and flags an untracked rig | **Verified** | Manifest records `dirty`, `untracked_rig=true`, 39 dirty entries. |
| The M1 platform is not in git | **Verified** | `git ls-files` returns none of the M1 platform/config/test paths; repository status lists them as untracked. |
| CI checks out a revision without M1 | **Verified** | Consequence follows directly from untracked apparatus. |
| Existing CI omitted the 202-test M1 suite | **Verified** | Committed workflow runs legacy unit/research suites only. |
| Current artifact-integrity gate does not assess M1 | **Verified** | It inspects `artifacts/experiments`; M1 writes `artifacts/runs`; absence exits success. |
| Current reproducibility gate assesses legacy stubs/configs | **Verified** | It checks legacy experiment directories and `configs/*.json`, not `configs/v0` or M1 execution. |
| `code_state` is recorded but not enforced | **Verified** | Repository search found recording and an enum-membership test, but no rejection path. |
| Local formatting is clean | **Verified** | Black reports 246 scoped files unchanged. |
| 202 tests pass with approximately 88% coverage | **Verified with execution caveat** | All 202 tests completed; coverage XML reports 88.5%. Process exit was changed only by host safe-delete policy during pytest temporary cleanup, not by a test failure. |
| Config-driven smoke works locally | **Verified** | `scripts/p1.py run configs/v0/smoke.yaml` completed. |
| Byte-identical run N versus run N+1 is entirely absent | **Partly overstated** | `tests/m1/test_engine.py` already compares same-config metrics across two local executions, and frozen-equivalence tests compare platform to v0 across seeds. What remains unproven is isolated clean-checkout identity of the complete decision-relevant evidence package, including artifact hashes under an explicit normalization policy. |

## 3. Does the Scientific State change?

### Changed

The scientific state changes at the **evidence-admissibility layer**:

1. The previous phrase “reproducible exploratory assay” is narrowed to **locally reproducible but immutable-provenance-limited exploratory assay**.
2. `EXP-2026-0007` changes from `Designed` to `Blocked_Confirmatory`.
3. The M0 provenance debt expands to include the uncommitted successor platform.
4. New assumptions, an unknown, debt records, audit evidence, and a Decision are added for apparatus reconstruction and gate validity.
5. The immediate roadmap now begins with a short platform-admissibility gate before Cycle 001 execution.

### Unchanged

The report contains no outcome evidence about replay, surprise, retention, emergence, calibration, affective indexing, or historical-carrier dependence. Therefore:

- no hypothesis confidence changes;
- no mechanism advances or regresses;
- no negative-result record changes;
- no theory candidate is admitted;
- forgetting construct validity remains the highest-priority scientific unknown after readiness.

## 4. Affected scientific objects

### Assumptions

- **`ASM-2026-0003` — seed/inference-unit assumption:** not contradicted, but V0-4 cannot estimate it credibly until repeatability of the apparatus is established.
- **`ASM-2026-0010` — clean committed reconstruction:** new, active-unvalidated.
- **`ASM-2026-0011` — automation measures the live apparatus:** new and contradicted in the assessed revision.

### Unknowns

- **`UNK-2026-0010` — M1 fresh-checkout reconstruction and repeatability:** new, blocking readiness unknown.
- **`UNK-2026-0003` — forgetting construct validity:** remains the top scientific unknown once the readiness gate is cleared.
- **`UNK-2026-0001/0002`:** unchanged; not answerable by this report.

### Scientific debt

- **`SDEBT-2026-0010`:** expanded from M0 artifact identity to M0/M1 immutable evidence identity; severity becomes Critical, B3.
- **`SDEBT-2026-0011`:** new; non-clean confirmatory exclusion is unenforced; Critical, B3.
- **`SDEBT-2026-0012`:** new; CI and verification gates do not measure the live apparatus; Critical, B3.
- Existing `SDEBT-2026-0001/0002/0003/0006` remain confirmatory blockers after the new readiness gate.

### Decisions

- **`DEC-2026-0006` remains valid but is narrowed:** M0 is locally deterministic and scientifically provisional; “reproducible” must not imply immutable reconstructability.
- **`DEC-2026-0007` remains valid:** matched controls, valid measurement, paired inference, and untouched confirmation seeds are still required.
- **`DEC-2026-0010` is created:** retain the scientific program; delay Cycle 001 execution; block confirmation pending explicit readiness evidence.

## 5. Experiment blocking assessment

| Experiment / activity | Status after assessment | Reason |
|---|---|---|
| Discovery Cycle 001 exploratory pilot | **Scientifically approved, execution delayed** | The question remains valuable, but a run now would add non-reconstructable evidence. |
| `EXP-2026-0007` confirmatory V0 family | **Blocked** | Provenance, gate validity, and enforcement fail before pre-existing protocol/measurement/control blockers are even considered. |
| M0 historical interpretation | **Unchanged** | Remains valid-indeterminate and locally reproduced; exact immutable reconstruction remains open. |
| E0/H* repetition | **Still blocked independently** | Treatment non-operability remains B4; unrelated to M1 readiness. |
| Low-cost engineering smoke/tests | **Permitted** | They are apparatus checks, not scientific experiments, and must not be labeled evidence for a mechanism. |

## 6. Issue classification

Issues can carry more than one consequence, but each has one primary classification.

| Issue | Primary classification | Secondary consequence | Scientific impact |
|---|---|---|---|
| M1 platform absent from committed revision | **Provenance issue** | Reproducibility issue | No immutable code identity; blocks all confirmatory use. |
| Smoke manifest is dirty/untracked | **Provenance issue** | Confirmatory evidence blocker | Assessed run is explicitly ineligible for confirmation. |
| Committed CI omits M1/v0-rig suites and smoke path | **Reproducibility issue** | Confirmatory evidence blocker | Green CI provides no evidence about the apparatus. |
| Artifact-integrity gate targets legacy path and passes on absence | **Measurement issue** | Scientific validity issue | Gate lacks sensitivity to the object it claims to measure. |
| Reproducibility gate checks legacy stubs/configs | **Measurement issue** | Reproducibility issue | “ALL CHECKS PASSED” is not evidence of M1 reproducibility. |
| `code_state` rule is unenforced | **Confirmatory evidence blocker** | Provenance issue | Dirty/untracked outputs can be silently consumed. |
| No isolated repeated-run evidence-package identity gate | **Reproducibility issue** | Confirmatory evidence blocker | Determinism of full evidence output is not established. |
| Local 202 tests, coverage, formatting, and smoke success | **Engineering issue** | Positive conformance evidence | Supports preserving and freezing M1; does not validate scientific constructs. |
| Existing replay resource matching, metric validity, and random timing gaps | **Scientific validity issue** | Confirmatory evidence blocker | Unchanged and still prohibit causal claims after platform readiness. |

## 7. Discovery Cycle 001 decision

**Decision: retain approval, delay execution, require minimum engineering gates.**

This is not a rejection of Cycle 001. The target unknowns and pilot logic remain high value. It is not scientifically efficient to run them now because the results would enter the SKB with avoidable provenance and repeatability defects. The gate is small relative to the cost of generating an unusable pilot and then repeating it.

### Experiment-justification test

1. **Which unknown is reduced?** Whether the M1 apparatus can create reconstructable evidence from a clean committed state.
2. **Why highest priority?** Every Cycle 001 result depends on it; failure contaminates all downstream inference and variance estimates.
3. **Competing explanations?** Local success may reflect stable committed behavior, or unrecorded working-tree state/environment artifacts.
4. **What changes belief?** Clean isolated reruns yield identical decision-relevant metrics/artifact hashes and all live-surface gates pass and fail when deliberately challenged.
5. **What does not?** More local tests on the same dirty tree, higher coverage, or another successful smoke run without clean provenance.
6. **What decision is enabled?** Permit Cycle 001 exploratory execution and preserve its outputs as reconstructable evidence.
7. **Cheaper alternative?** No. Committing without an isolated rerun does not test reconstruction; rerunning without committing preserves the same defect.

## 8. Updated scientific-debt priority

### Immediate readiness gate

1. `SDEBT-2026-0010` — immutable M0/M1 evidence identity.
2. `SDEBT-2026-0012` — live-apparatus CI and verification validity.
3. `SDEBT-2026-0011` — machine-enforced confirmatory provenance exclusion.

### Scientific priorities after readiness

4. `SDEBT-2026-0003` — forgetting construct validity.
5. `SDEBT-2026-0002` — equal-budget random timing.
6. `SDEBT-2026-0001` — replay resource/decay matching.
7. `SDEBT-2026-0009` — H* trigger operability, still the H* line's B4 stop.
8. `SDEBT-2026-0006` — validate load-bearing measurements.
9. `SDEBT-2026-0007` — learned-versus-injected identifiability.
10. Legacy migration and theory debt remain deferred or decision-triggered.

## 9. Living Scientific Model revisions

Required revisions were made:

- “reproducible assay” is narrowed to **local reproducibility under a provenance limitation**;
- the 202-test/88.5% result is recorded as engineering conformance, not mechanism evidence;
- an immediate apparatus-admissibility gate precedes the scientific priority queue;
- confirmatory blockers now include uncommitted apparatus, unenforced clean-state exclusion, mis-targeted gates, and absent isolated evidence-package identity;
- no hypothesis, mechanism, or theory statement changes.

## 10. Minimum engineering changes before Cycle 001 may begin

These are stated as scientific acceptance conditions, not implementation architecture.

1. **Immutable apparatus identity**
   - Commit the M1 scientific apparatus, v0 configs, tests, and required execution entrypoints.
   - Separate unrelated planning documents and secrets from the scientific revision.
   - Produce a smoke manifest from an isolated checkout with `code_state=clean` and `untracked_rig=false`.

2. **Required clean-checkout verification**
   - Required CI must execute M1 tests, v0-rig/frozen-equivalence tests, and the config-to-artifact smoke path from the committed revision.
   - A real required-job pass must exist; local workflow edits are insufficient.

3. **Live-surface gate validity**
   - Artifact integrity must inspect `artifacts/runs` or the actual declared evidence package and fail when required artifacts are absent, corrupted, or incomplete.
   - Reproducibility verification must inspect substantive `configs/v0` and executable M1 requirements rather than legacy path existence.
   - Each gate must have at least one known-failure test demonstrating sensitivity; a gate that cannot fail is not a measurement.

4. **Machine-enforced evidence eligibility**
   - A non-clean run must be rejected at the confirmatory execution or evidence-admission boundary.
   - A negative test must prove that a deliberately dirty/untracked manifest cannot enter a confirmatory decision.

5. **Isolated repeated-run identity**
   - Execute one frozen minimal deterministic config twice from isolated clean checkouts.
   - Require identical decision-relevant metrics and artifact hashes after explicitly excluding or normalizing declared nondeterministic metadata such as timestamps, duration, hostname, and path.
   - Any unexplained difference blocks Cycle 001 and must be diagnosed before pilot evidence is collected.

### Additional requirements before confirmation, but not before exploratory Cycle 001 pilots

- content-hashed preregistration;
- SESOI/equivalence and guardrail margins;
- prospective seed-count justification;
- untouched confirmation seeds;
- exact resource and replay-budget matching;
- validated retention construct and controls;
- multiplicity and stopping rules.

This distinction preserves progressive rigor: the minimum gate prevents disposable or irreproducible Discovery evidence; the additional conditions prevent exploratory choices from masquerading as confirmation.

## 11. Final Scientific Readiness Assessment

| Dimension | Status | Basis |
|---|---|---|
| Local engineering conformance | **Pass with caveat** | 202 tests completed, 88.5% coverage, formatting and smoke pass; host cleanup policy affected process exit only. |
| Immutable provenance | **Fail** | Apparatus/configs/tests absent from committed revision; dirty manifest. |
| CI relevance | **Fail** | Committed CI omits the live platform; modifications are uncommitted. |
| Artifact-integrity measurement | **Fail** | Legacy target, absence can pass, live M1 path unassessed. |
| Reproducibility measurement | **Fail** | Legacy stubs/configs checked; no clean isolated reconstruction. |
| Confirmatory evidence admission | **Fail** | Non-clean ineligibility unenforced. |
| Scientific construct validity | **Not ready** | Existing metric and causal-control debts remain open. |
| Discovery Cycle 001 scientific rationale | **Approved** | Target unknowns and pilot designs remain decision-relevant. |
| Discovery Cycle 001 execution | **Delayed** | Minimum apparatus gates not yet met. |
| Confirmatory experiments | **Not ready / blocked** | Platform-readiness and pre-existing scientific-validity conditions both fail. |

## 12. Bottom line

The report does not weaken or strengthen any computational principle. It changes whether future results could count as durable evidence.

The correct response is neither to discard M1 nor to proceed because local tests are green. Preserve and freeze the working apparatus, prove that the committed system and its gates reconstruct and measure the live evidence path, then begin Cycle 001 as explicitly exploratory. Confirmatory work remains blocked until both platform admissibility and the already-registered causal, measurement, statistical, and preregistration requirements are satisfied.
