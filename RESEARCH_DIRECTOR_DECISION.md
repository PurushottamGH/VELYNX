# Research Director Decision — Program D, Sprint 1

**Role:** Research Director (final scientific authority for Program D).
**Authority ordering (canonical §1.4):** scientific correctness > experiment reproducibility > code simplicity > performance > features.
**Reference of record:** `PROGRAM_D_CANONICAL.md` (immutable); Sprint 1 = E0 (H\*) implementation + n=20 run.
**Date:** 2026-07-04.

---

## FINAL DECISION — GO (2026-07-04)

**GO.** Accept Sprint 1 as a **feasibility pilot that surfaced a load-bearing engineering defect (F-A, the unit-incommensurate MDL growth trigger) before it reached publication.** That is exactly what a pilot is for; the pilot succeeded.

- **Disposition:** ACCEPT (as a pilot) WITH LIMITATIONS. The engineering deliverables, controls, and honesty framework are retained.
- **Characterization of record:** **H\* untested; growth-trigger unit defect (F-A) precluded firing; attempts-toward-kill = 0.** Sprint 1 is **not** a "double-negative result" and must not be described as one. DV-b shows no trustworthy positive emergence (the original PASS was a C3-null artifact; the self-null value is negative but confounded by the K′=2 bottleneck and disconnected from H\* since capacity never grew — direction verified robust to the 2-seed self-null gap, `evidence/12_m_recomputation.md`).
- **Tag authorized:** `v1.0.0-Sprint1-Complete` may be applied to mark the pilot and its (corrected) evidence package as certified-with-limitations. The tag certifies the *engineering deliverable and the corrected record*, **not** an H\* result.
- **Sprint 1.3 prerequisite (binding):** Sprint 1.3 must fix the trigger-unit mismatch (grow iff `N·ΔH > model-cost-of-one-state`; re-specify `hypothetical_entropy_after_growth`, F-E) **before** C2f runs. Running C2f on top of the current broken trigger would reproduce F-A in a new arm and test nothing. The M self-null implementation gap (2/20 seeds) is a secondary Sprint 1.3 prerequisite (validate the null construction generally).
- **External publication of Sprint 1:** still blocked on corrections C-1…C-4 (§7). This GO certifies the pilot internally and authorizes the tag — not a venue submission.

The detailed findings (F-A…F-G), required corrections, and Sprint 2 authorization below are unchanged and remain in force.

---

## 0. Decision (read this first)

| Question | Ruling |
|---|---|
| Is Sprint 1 scientifically complete? | **No.** The engineering is complete and clean; the *science* is not — E0 did not yet produce a valid test of H\*, for two independent reasons (F-A, F-C below). |
| Contribution | A **feasibility pilot that did its job**: it surfaced a load-bearing defect in the MDL trigger before publication. That is real value — but it is not the "rigorous negative result on H\*" the publication docs imply. |
| Overall verdict | **ACCEPT WITH LIMITATIONS.** Accept the engineering deliverables and the pilot; **reject the current publication framing**; downgrade the scientific claim to "trigger-scaling defect found; H\* untested." |
| External publication of Sprint 1 now? | **No.** Blocked on corrections C-1…C-4 (§7). |
| Sprint 2 | **AUTHORIZED, conditionally** — as **EXP-1 (calibration)**, whose preregistration is strong. Gated on C-1 (integrity fix) landing first, and on E0-v2 + EXP-0 being tracked (§8). |

**One-line summary:** The pilot is worth keeping and the team's honesty discipline (`LIMITATIONS.md`, `FINAL_PUBLICATION_CLAIM.md`) is commendable, but the headline result — "growth never fired" — is **confounded by a unit-incommensurate MDL trigger** and therefore cannot be attributed to the environment or the hypothesis. Fix the trigger, correct the fabricated architecture claims, re-run, then re-submit.

---

## 1. Inputs reviewed

- `PROGRAM_D_CANONICAL.md` (§1, §4, §5, §6, §7, §8, §11).
- Full `evidence/` package (n=20): `01_manifest.json`, `05_metrics.json`, `06_statistical_results.md`, `09…`, `10…`, `11_power_analysis.md`, `growth_diagnostics.md`.
- Integration reviews (Sonnet): `INTEGRATION_LEDGER.md` Review #001 (FAIL→F1) and #002 (PASS).
- `DOCUMENTATION_RECONCILIATION.md`.
- Nemotron publication pass: `FINAL_PUBLICATION_CLAIM.md`, `ABSTRACT_LANGUAGE.md`, `LIMITATIONS.md`.
- Sprint 2 candidate: `EXP1_PREREGISTRATION.md`.
- Source: `core/mdl/mdl_growth.py`, `core/predictors/dirichlet_markov.py`, `experiments/E0/run.py`, `experiments/E0/config.json`.
- **MiniMax "independent cold read": NOT PRESENT in the repository** (no matching file under any tracked path; see F-G). This decision proceeds without it and must be revisited if it is delivered.

---

## 2. What Sprint 1 delivered (credit where due)

The engineering meets the canonical process bar and should be retained:

- **Canonical 5-primitive mapping** implemented: log score (§5.3), MDL trigger with derived `λ_model` (§5.4), null-referenced `M = NMI(learned,true) − NMI(learned,shuffled)` (§5.5). No banned `free_energy`/`E=λH+μS+νA` symbols in the live E0 path (`INTEGRATION_LEDGER.md:32`).
- **Four conditions** T/C1/C2/C3 with C2 capacity-matched and C3 shuffled (`config.json:22`).
- **F1 remediated** — the DV-a category error (scoring a length-`k` internal distribution against a `[0,K_env)` latent) was correctly caught in Review #001 and fixed to `predictor.log_predictive_probability(obs_list, context)` at all four sites; floor-hit rate now 0% (`05_metrics.json` `floor_hit_rate: 0.0`).
- **C2 held-out leakage fixed** and verified (`test_n=1999` matches T, all seeds).
- **Reproducibility hardening** (W1: `hash()`→`hashlib.sha256`), dead-code removal (W2/W4), held-out env, Holm-Bonferroni FWER.
- **Honest limitations discipline.** `FINAL_PUBLICATION_CLAIM.md` §"What CANNOT Be Claimed" and `LIMITATIONS.md` correctly refuse to claim falsification, refuse "true rate = 0", and flag the DV-a/DV-b dissociation. This is exactly the posture the canon demands.

Test suite: 100 passed / 1 skipped (verified in Review #001, `INTEGRATION_LEDGER.md:16`).

**This is good engineering.** The findings below are about the *science the engineering was pointed at*, not the code quality.

---

## 3. Contribution assessment

Per canonical §8, H\* is **definitely not novel** (Oudeyer & Kaplan 2007, Weng 2001, Rao–Ballard 1999, ICM/RND, MDL structure learning), and the sanctioned publishable output is a **negative result + the I2 discrimination methodology**, not "a mind." Measured against that:

- The **null-referenced `M`** and the **E0 discrimination design** (T/C1/C2/C3 with a shuffled null so `E[M|H₀]=0`) are the genuine methodological contribution and are sound in construction.
- The **actual empirical result is not yet a contribution**, because (F-A) the trigger cannot fire by construction and (F-C) the treatment never differed from control — so no statement about H\* has been earned.

Net contribution of Sprint 1: **a working, honest experimental harness + a caught defect**. That justifies continuing, not publishing.

---

## 4. Correctness findings (severity-ranked, evidence-cited)

### F-A — CRITICAL (scientific correctness). The MDL growth trigger is unit-incommensurate; growth cannot fire by construction.

- `core/predictors/dirichlet_markov.py:125` `entropy()` returns a **per-symbol conditional entropy in bits**, `H = −Σ P(i)P(j|i)log₂P(j|i)`, bounded by `log₂k` (≤1 bit for k=2). Diagnostics confirm `H_before ≈ 0.72–0.90` (`growth_diagnostics.md`).
- `experiments/E0/run.py:215-231` computes `entropy_before/entropy_after` from that per-symbol method, then calls `should_grow(..., n=k, N=predictor.n_observations)`.
- `core/mdl/mdl_growth.py compute_lambda_model` returns `k·b + n·log₂N`. With `n=k=2` and `N` = observations seen (1000→9500), `λ_model = 2 + 2·log₂(N) ≈ 21.9 → 28.4` bits — matching `growth_diagnostics.md` exactly.
- The trigger therefore evaluates `G = (H_before − H_after)[≈ per-symbol, ~0.01 bits] − λ_model[≈ 22–28 bits]`. **The two operands are different quantities** (a per-symbol entropy delta vs. a total-data-code-length penalty). This is precisely the canonical §1-rule-5 prohibited construct: *"unit-incommensurate mathematics."*
- Consequence: `G ≈ −22 to −28` at **every one of 720 checks**, off by ~3 orders of magnitude. Growth is impossible **independent of the environment or the hypothesis**.
- Correct two-part MDL for a growth step compares **total** description-length deltas: `ΔL = Δ[L(model)] + Δ[L(data|model)]`, i.e. grow iff `N·(H_before − H_after) > (model-cost of one new state ≈ k·b)`. The current code (a) fails to scale the data-fit term by `N`, and (b) loads the data-code term `N·log₂N` onto the *model* penalty, where it does not belong. Note the penalty also grows with data — backwards from correct MDL, where more data makes added complexity *easier* to justify.
- **This is the top-priority defect.** It invalidates the headline claim in `06_statistical_results.md`, `FINAL_PUBLICATION_CLAIM.md`, `ABSTRACT_LANGUAGE.md`: "growth never fired" is not a property of the environment; it is an artifact of the trigger scaling.

### F-B — CRITICAL (research integrity). Publication docs describe an architecture that was never run.

- Actual experiment (`config.json:13-16`, `01_manifest.json:23-26`): a **Dirichlet–Markov conjugate predictor**, `initial_capacity=2`, `alpha=1.0`, on a **10-latent-state, obs_dim=16 synthetic stream**. No neural network exists in the E0 path.
- `ABSTRACT_LANGUAGE.md:4` — *"a structured sequence task (Parity-Lite, Transformer, 20M params)."*
- `FINAL_PUBLICATION_CLAIM.md:37` — *"single architecture (20M Transformer)"*; `:15,:37` invoke a "Parity-Lite" task and `λ_base/λ_budget` schedule.
- `LIMITATIONS.md:27` — *"single MDL configuration (λ_base=20.0, λ_budget=0.5)."* No `λ_base`/`λ_budget` exists in `mdl_growth.py`; `λ_model` is `k·b + n·log₂N`.
- These are **fabricated method details**. An abstract that misstates the model class and parameter count is disqualifying for any venue and violates the prime directive (§1: truth over survival). This is not a wording nit; it is a fabricated experimental record that must be purged before any external claim.

### F-C — MAJOR. DV-a "FAIL" is a manipulation-check failure, not an H\* result.

- The H\* kill criterion (§6) presumes T actually *differs* (grows) and still fails to beat C1/C2. Here `T_growth=0` and `T==C1==C2` identically (`05_metrics.json` per_seed) — the independent variable ("growth ON") **never activated**, so paired differences are exactly 0 and p=NaN.
- Therefore this run **must not count as one of the "two honest attempts"** to falsify H\* (§6). Labeling the verdict "FAIL (DV-a)" and wiring it to the kill decision conflates *"the manipulation did not occur"* with *"the hypothesis failed."* `FINAL_PUBLICATION_CLAIM.md:25` gets the interpretation right ("untested, not falsified") but the machine verdict and several summaries still read as an H\* FAIL. The decision record must state: **H\* remains untested; attempts-toward-kill = 0.**

### F-D — MAJOR. DV-b "PASS" uses a data-derived margin, contradicting the pre-registered gate.

- Canonical §7 requires *"`M` exceeds **pre-registered** margin."*
- `05_metrics.json` `dv_b.margin_source: "data_derived"` (`= 2·std(M)/√n` from the same 20 seeds). A margin computed from the realized run is **not pre-registered** and reintroduces researcher DOF — the exact failure mode (§5.5, F3) the null-referencing was meant to close.
- Compounding: with growth never firing, capacity is frozen at k=2, so `M` measures the structure a **static 2-state** predictor shares with a 10-state latent — it says nothing about *error-gated growth*. DV-b "PASS" is therefore both procedurally non-conforming (F-D) and, per the docs' own caveat, disconnected from H\* (`FINAL_PUBLICATION_CLAIM.md:39`). **Do not report DV-b as a pass** without a pre-registered margin.

### F-E — MINOR (method). The growth-benefit proxy adds an untrained uniform state, guaranteeing `entropy_after ≥ entropy_before`.

- `hypothetical_entropy_after_growth()` estimates the post-growth model by appending a fresh Dirichlet state (α=1 smoothing) that has seen no data; its high-entropy row **raises** conditional entropy. Every `gain` in `growth_diagnostics.md` is negative even *before* `λ_model`. So even with F-A fixed, the proxy measures "entropy of a model with an unfitted extra state," not "entropy the model would reach after also assigning data to that state." The benefit-of-growth estimator needs re-specification alongside F-A.

### F-F — DOCUMENTATION. Citation drift after `06_statistical_results.md` was rewritten n=5→n=20.

- Confirmed in the prior integration-review pass: `DOCUMENTATION_RECONCILIATION.md:13,29` and `INTEGRATION_LEDGER.md:102,108` cite line ranges in `evidence/06_statistical_results.md` that no longer contain the quoted text (the file was overwritten from the 5-seed to the 20-seed version, shifting content and changing 90→720 checks, −21.95→−21.89). Numbers-of-record are inconsistent across the package (`05_metrics.json` still n=5; `01_manifest.json`/`06`/`11` n=20).

### F-G — PROCESS. Named review input absent.

- The "MiniMax independent cold read" listed as a Sprint-1 input is not in the repo. Either it was not delivered or lives outside the tree. An independent cold read is exactly what should have caught F-B; its absence is a process gap, not just a missing file.

---

## 5. Limitations & publication-readiness verdict

`LIMITATIONS.md` and `FINAL_PUBLICATION_CLAIM.md` are, in structure and caution, the strongest documents in the package — **except** that they (a) inherit the fabricated architecture (F-B) and (b) present the result as a bounded null on H\* when it is actually a **trigger-scaling artifact** (F-A). The correct top-line limitation, currently missing, is:

> *The MDL growth trigger as implemented compares a per-symbol entropy difference against a total-data-code-length penalty (`λ_model = k·b + n·log₂N`, ≈22–28 bits). Growth is mathematically precluded regardless of environment. The observation "0/720 growth events" is a property of the trigger's units, not evidence about error-gated growth. H\* is untested.*

Publication readiness: **not ready.** The negative-result/methodology paper (canonical §8 path 1) is still the right target — but its empirical core must be a **corrected** E0-v2 run, and its method section must describe the Dirichlet–Markov organism truthfully.

---

## 6. Verdict

**ACCEPT WITH LIMITATIONS.**

- **Accept:** the E0 harness, controls, F1/C2/held-out/FWER remediations, reproducibility work, and the honesty framework — as a feasibility pilot.
- **Limitations (binding):** (1) H\* is untested (F-A, F-C); (2) publication docs carry a fabricated architecture and must be corrected before any external use (F-B); (3) DV-b is not a conforming pass (F-D); (4) evidence package has internal numbering drift (F-F).
- **Reject:** any statement that Sprint 1 tested, supported, or falsified H\*, or that "growth never fired" is a finding about the environment/hypothesis.

---

## 7. Required corrections before Sprint 1 can be cited externally

| ID | Owner | Correction | Blocks publication? |
|---|---|---|---|
| **C-1** | Nemotron (publication) | Purge "Parity-Lite / Transformer / 20M params / λ_base/λ_budget" from `ABSTRACT_LANGUAGE.md`, `FINAL_PUBLICATION_CLAIM.md`, `LIMITATIONS.md`. Describe the actual Dirichlet–Markov k=2 organism (F-B). **[RESOLVED 2026-07-04: fabricated terms purged from all three docs; pickaxe confirmed no lineage in any `.py`/`.json`/`.yaml` across history — fabricated boilerplate, not W3-style drift. Docs now describe the Dirichlet–Markov k=2 organism.]** | **Yes** |
| **C-2** | Core/E0 eng | Fix the MDL trigger units (F-A): make the data-fit term and `λ_model` commensurate (grow iff `N·ΔH > model-cost-of-one-state`), and re-specify `hypothetical_entropy_after_growth` (F-E). Re-derive against §5.4 and `literature/program_d_mathematical_provenance.md`. | **Yes** |
| **C-3** | Analysis | Pre-register the DV-b `M` margin **before** the E0-v2 run; stop reporting the data-derived margin as a gate (F-D). | **Yes** |
| **C-4** | Integration (Sonnet) | Re-run `DOCUMENTATION_RECONCILIATION.md`/`INTEGRATION_LEDGER.md` citations against current `evidence/` line numbers; reconcile `05_metrics.json` (n=5) to n=20; single numbers-of-record (F-F). | **Yes** |
| C-5 | Research Director | Restate the E0 verdict as **"H\* untested; attempts-toward-kill = 0; trigger defect found"** wherever "FAIL (DV-a)" implies an H\* result (F-C). | Yes |

---

## 8. Sprint 2 authorization

**AUTHORIZED — conditionally — with Sprint 2 = EXP-1 (Program A calibration gate).**

Rationale: `EXP1_PREREGISTRATION.md` is a strong, canon-derived preregistration. It sets the single ECE<0.10 gate (§6-H1, no dead zone), 22 seeds by the correct binomial power rule (`(1−0.10)^22=0.0985`), a locked tier→probability mapping, and — critically — §5 explicitly internalizes E0's F1 lesson (do not score one label space against another). EXP-1 is an **independent deliverable** (Program A product gate) and does not depend on the E0 defect, so it may proceed in parallel with the E0 fix.

Conditions on the authorization:

1. **C-1 must land before Sprint 2 opens.** A publication program cannot be built on documents that misdescribe what was run. (Integrity gate.)
2. **E0-v2 is a tracked scientific-correctness blocker (C-2/C-3/F-E), not abandoned.** It is surviving deliverable #3 (canonical §3) and outranks features by §1.4. E0 is not "done" until the trigger can fire and H\* gets an honest first attempt.
3. **EXP-0 (paraphrase precondition) must be scheduled.** Canonical §11 names EXP-0 — not E0 — as the immediate next step and a precondition to stop the deployed system claiming its 100/100 headline. `experiments/EXP0/` protocol exists; it is ~1 day and must run before or alongside EXP-1, and before any external Program-A honesty claim.
4. **EXP-1 freezes code and its rubric/bins/mapping before execution** (its own §4 kill-condition on post-hoc relabeling); the Research Director will spot-check that the frozen rubric is committed prior to the run.

**Not authorized:** external publication of Sprint 1; any Sprint-2 scope that reintroduces the 32 soul concepts or a dense-embedding control into EXP-2 (canonical §10 Issue-6), should EXP-2 be brought forward.

---

## 9. Standing instruction

The pilot succeeded at the one thing pilots are for: it exposed a load-bearing defect (F-A) and a fabrication (F-B) **before** they reached a venue. That is the system working. Fix the trigger, tell the truth about the architecture, re-run, and E0 becomes what the canon always expected it to be — an honest negative-or-null result plus a real discrimination method. Proceed.

— Research Director, Program D
