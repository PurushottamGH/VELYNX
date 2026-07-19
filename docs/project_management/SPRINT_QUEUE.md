# Sprint Queue - EXP-1 Before Sprint 1.3 C2f

**Decision:** Run **EXP-1 Calibration** first in Sprint 2, then run **Sprint 1.3 C2f forced-growth sensitivity** after EXP-1 artifacts are frozen.

EXP-1 is already preregistered as the Program A calibration gate and now requires 22 independent seed replicates over the frozen mixed-query set. Sprint 1.3 C2f should be treated as the second preregistered experiment in the queue: important, but downstream of EXP-1 for engineering order. C2f may receive doc-only preregistration review while EXP-1 is running, but no C2f implementation or scored run should begin until EXP-1 has emitted its run logs, analysis artifacts, and decision record.

## Sprint 1 Result Characterization (of record)

Sprint 1's result is **"H\* untested; growth-trigger unit defect (F-A) precluded firing; attempts-toward-kill = 0"** — **not** a "double-negative result." The 0/720 growth events are an artifact of a unit-incommensurate MDL trigger (per-symbol entropy delta vs. total-data-code penalty ≈ 22–28 bits), not a tested-and-failed hypothesis. Any C2f / Sprint 1.3 scheduling text that describes Sprint 1 as an H\* pass/fail must use this characterization. See `RESEARCH_DIRECTOR_DECISION.md` and `LIMITATIONS.md` (F-A section).

**Hard prerequisite for C2f:** Sprint 1.3 must fix the trigger-unit mismatch (grow iff `N·ΔH > model-cost-of-one-state`) **before** C2f runs. Running C2f on top of the current broken trigger would reproduce the same F-A defect in a new arm and test nothing.

## Queue Order

| Order | Work item | Status | Start condition | Stop condition |
|---:|---|---|---|---|
| 1 | **EXP-1: Calibration, 22 seeds** | Preregistered | Sprint 1 certification complete; EXP-1 query/rubric freeze complete; experiment runner/provenance ready | 22 seed replicates completed; ECE/reliability/tier-independence/hard hallucination gates reported |
| 2 | **Sprint 1.3: C2f forced growth** | Queued behind EXP-1 | C2f preregistration locked; EXP-1 artifacts frozen; shared run/seed/provenance conventions reused | Forced-growth sensitivity verdict reported without changing Sprint 1 historical claims |

## Why EXP-1 Runs First

1. **EXP-1 is the canonical product-honesty gate.** The current canonical queue gives EXP-1 deliverable priority because Program A cannot claim honest uncertainty until calibration is measured. C2f clarifies the growth-mechanism limitation from Sprint 1, but it does not unblock the Program A calibration claim.

2. **EXP-1 is lower-risk infrastructure hardening.** EXP-1 mainly exercises shared experiment plumbing: seed replication, config/provenance stamps, result tables, metric computation, reliability figures, decision records, and preregistration discipline. It does not require modifying the E0 growth mechanism. That makes it the safer first user of the Sprint 2 experiment-run infrastructure.

3. **C2f touches the higher-risk E0/growth path.** Forced growth will intentionally alter the inactive-growth regime that produced Sprint 1's T=C1=C2 identity. That work risks entangling capacity schedules, PRNG handling, growth-event logging, and DV-a/DV-b interpretation. It should not run while EXP-1 still needs a stable shared harness.

4. **Shared seed/provenance conventions should be set once.** EXP-1's 22-seed requirement is an immediate pressure test for seed registries, deterministic replay, artifact naming, per-seed failure handling, and pooled-vs-seed-level reporting. C2f should inherit those conventions instead of inventing a second format.

5. **Avoid cross-experiment contamination.** Once EXP-1 starts scored execution, the shared experiment utilities it consumes should be frozen except for run-blocking defects. Starting C2f implementation first would increase the chance that E0/growth changes, runner changes, or metrics changes leak into EXP-1's execution window.

## Shared Infrastructure To Stabilize In EXP-1

EXP-1 should leave behind reusable conventions for C2f:

- Per-seed output directories and manifest format.
- Commit/config hash recording before every scored run.
- Canonical result CSV shape: seed, condition or query family, primary metric, auxiliary checks, decision inputs.
- Machine-readable decision file plus human-readable report.
- Failure semantics: a seed-level preregistered failure cannot be rescued by pooled results.
- Run-freeze rule: after scored execution begins, only reproducibility or correctness blockers may change shared experiment utilities.

## C2f Entry Criteria

C2f should start only after all of the following are true:

- The F-A trigger-unit mismatch is fixed and verified (the trigger can fire in principle); C2f must not run on the broken trigger.
- EXP-1 has completed all 22 seeds or has hit a preregistered stop/fail condition.
- EXP-1 artifacts are written and immutable enough for review.
- C2f preregistration locks the forced-growth intervention, growth schedule, seed count, primary outcome, correction policy, and decision rule before outputs are observed.
- C2f explicitly preserves Sprint 1's corrected characterization: Sprint 1's 0/720 growth events are an artifact of the F-A trigger-unit defect (H\* untested; attempts-toward-kill = 0), **not** a tested-and-failed hypothesis. C2f tests a different forced-growth sensitivity question and must run only after the F-A trigger-unit fix has landed.

## Practical Scheduling Rule

Use a two-lane queue: **Lane A runs EXP-1**, while **Lane B may only prepare C2f preregistration text, review checklists, and non-executing analysis templates**. Lane B must not merge C2f growth-path code, alter shared experiment utilities, or begin scored C2f runs until EXP-1 is frozen.

**Bottom line:** EXP-1 first, C2f second. EXP-1 stabilizes the shared experiment infrastructure under a lower-risk, already-preregistered calibration workload; C2f then reuses that infrastructure for the higher-risk forced-growth sensitivity experiment without contaminating EXP-1 or rewriting Sprint 1's result.
