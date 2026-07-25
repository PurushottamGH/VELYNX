# Hypothesis Discrimination Matrix (Deliverable 2)

**Status:** Canonical experimental-instrument reference, version 1.0
**Date:** 2026-07-20
**Author role:** Principal Experimental Methodologist
**Input:** `PHENOMENON_REGISTRY.md`, `THEORY_LANDSCAPE.md` §7, `THEORY_NOTEBOOK_v3.md` §4–5, `HYPOTHESIS_REGISTER.md`
**Epistemic status:** Discrimination analysis. Registers no hypothesis; classifies existing ones by what would separate them.

---

## 0. Scope and a required up-front admission

The brief names two current hypotheses, **T-01** and **T-02**, plus "any serious alternative supported by existing literature." Before the matrix, two facts must be stated plainly because they determine what the instrument can and cannot do:

- **[FACT]** T-01 and T-02 **do not appear in the repository register** (`THEORY_LANDSCAPE.md` §7). They originate in the research brief. This document evaluates them as *provisional propositions*; it does not register them and does not touch the protected Program D canon (H\*, H1, H2).
- **[FACT — the load-bearing admission]** The theory phase found that **T-02 subsumes T-01**: if T-02's "stateful conditional transduction" includes a state-update, it already contains T-01's history dependence, "making the pair non-independent" (`THEORY_NOTEBOOK_v3.md` §4.2). Therefore **T-01 and T-02 are not, as written, mutually distinguishable by experiment.** No observation can support T-02-with-state over T-01, because any such observation supports both. This is reported in full in §4 rather than hidden.

Consequently the useful discrimination is **not** T-01 vs T-02. It is:

> **the memory-carrying reading of T-01/T-02 (a system that retains a task-relevant distinction) versus its serious rivals: memoryless-sufficient policies, leakage, spurious surface correlates, and pure capacity.**

The matrix below is built around that real contrast, using phenomenon **PH-1** as the primary discriminator and PH-3/PH-5 for the retention-and-irreducibility alternatives.

### 0.1 Hypotheses and alternatives under discrimination

| Label | Statement (as tested) | Source |
|---|---|---|
| **T-01** | Competent behavior on temporally-aliased decisions requires retaining a task-relevant distinction across time (obligation A1). | Brief; reduced in `THEORY_LANDSCAPE.md` §7 |
| **T-02** | Interactive competence is a non-anticipating causal policy kernel evaluated with an environment process; a *stateful* kernel is one realization. | Brief; reduced to descriptive schema, `THEORY_NOTEBOOK_v3.md` §4.2 |
| **ALT-0** | **Memoryless sufficiency**: the task's current input is (or can be made) sufficient; no retained distinction is needed. | `THEORY_LANDSCAPE.md` §2.2, §7 counterexamples |
| **ALT-L** | **Leakage**: apparent memory is the disambiguating bit surviving in the current input. | `PHENOMENON_REGISTRY.md` PH-1 trivial expl. (a) |
| **ALT-S** | **Spurious correlate**: a surface feature correlated with the target, not the historical cause, drives success. | PH-1 trivial expl. (c) |
| **ALT-C** | **Capacity-not-coupling**: gains come from added parameters, not from evidence-coupled retention. | `HYPOTHESIS_REGISTER.md` control C1/C2 |
| **ALT-I** | **Injection**: learned "structure" re-reads designer-injected statistics (the H\* clause-iii rival). | `METRIC_SPECIFICATION.md` §5 (shuffled reference) |

ALT-0, ALT-L, ALT-S, ALT-C, ALT-I are the "serious alternatives" — each is a documented way a naive experiment would wrongly credit memory/structure. Discrimination = beating all of them under one intervention.

---

## 1. Matrix — T-01 (memory-carrying reading) vs its rivals

**Primary phenomenon:** PH-1 (temporal aliasing resolution). **Instrument:** the aliasing battery of matched-input / mismatched-target pairs, with a memoryless policy of matched compute as the reference ceiling.

| Field | Content |
|---|---|
| **Predicted outcome (T-01)** | Loss on the aliased set strictly below the best memoryless policy: `E[loss\|A, sys] < E[loss\|A, memoryless]`, by a pre-registered margin, at matched memory budget. |
| **Distinguishing intervention** | **Erase the historical carrier.** Two matched runs: (i) full stream; (ii) stream with the disambiguating past observation ablated/permuted so the bit is absent. T-01 predicts a large loss increase on the aliased set in (ii); ALT-0/ALT-L/ALT-S predict little change. |
| **Observations that SUPPORT** | Aliased-set loss below memoryless ceiling in (i); collapse to memoryless ceiling in (ii); the collapse localized to timesteps whose disambiguator was ablated; effect stable across ≥5 seeds. |
| **Observations that WEAKEN** | Sub-ceiling loss in (i) but only small degradation in (ii) → the information was partly present currently (points toward ALT-L); benefit present but not localized to ablated steps (points to ALT-S). |
| **Observations that FALSIFY (the memory reading)** | Full-stream aliased loss **not** below the memoryless ceiling across seeds → no retained distinction is being used; the memory-carrying reading of T-01 is false for this instrument. |
| **Observations that are UNINFORMATIVE** | Any result where the memoryless control was *not* compute-matched (confounds capacity with memory); any result on non-aliased timesteps (T-01 makes no claim there); absence of PH-1 when the disambiguator was not feasibly carryable within budget (`THEORY_LANDSCAPE.md` §7 residue — absence is expected, not falsifying). |

### 1.1 Separating the rivals within PH-1

| Rival | Its distinct signature under the ablation intervention | Control that isolates it |
|---|---|---|
| ALT-0 | No sub-ceiling gain even in the full stream. | The memoryless ceiling itself. |
| ALT-L | Gain in full stream, *survives* ablation of the past carrier. | Current-input-only probe: train/evaluate a memoryless policy on run (i)'s current inputs; if it matches the system, leakage. |
| ALT-S | Gain survives replacing the true past cause with a decorrelated surrogate that preserves the surface feature. | Surrogate-cause swap control. |
| ALT-C | Gain scales with capacity, not with presence of the carrier. | Capacity-matched memoryless model. |

Only if the gain **appears in (i), disappears in (ii), and none of ALT-L/S/C reproduce it** is the memory-carrying reading supported. This is the discriminative core of the instrument.

---

## 2. Matrix — T-02 as descriptive schema

T-02 as reduced is a *measurement ontology* ("evaluate a non-anticipating causal policy together with its environment process"), not a mechanism (`THEORY_NOTEBOOK_v3.md` §4.2). It makes **no risky prediction** on its own.

| Field | Content |
|---|---|
| **Predicted outcome** | None that differs from "an evaluation frame exists." T-02 predicts that competence claims are *ill-posed* without an environment process + success relation. |
| **Distinguishing intervention** | The only test of T-02 *qua schema* is a **specification audit**: can two policies that agree on observational data be separated by adding an intervention/shift? If yes, T-02's insistence on the environment process is vindicated; if no environment ever separates them, the schema added nothing here. |
| **Observations that SUPPORT** | Two systems with identical observational `pi(y\|h)` diverge under an intervention or distribution shift (T-02's environment-process term is doing work). |
| **Observations that WEAKEN** | No environment in the tractable class ever separates observationally-equal policies → the extra schema machinery is idle for this domain. |
| **Observations that FALSIFY** | **None.** A descriptive schema is not falsifiable. This is stated as a limitation, not a strength. |
| **Observations that are UNINFORMATIVE** | Any single-environment result — T-02's content is precisely about cross-environment/intervention comparison. |

**Verdict carried into the instrument:** T-02 is used as a *design constraint* (always specify environment process + success relation + resource budget), not as a hypothesis the instrument tests. It earns its place by disciplining the other tests, per `THEORY_LANDSCAPE.md` §4.

---

## 3. Matrix — retention and irreducibility alternatives (continuity with H\*)

Because the memory-carrying T-01 shares content with H\*'s A3/PH-3 and PH-5, the same rivals recur. This row set keeps the new instrument commensurable with the existing E0 kill criteria.

| Contrast | Phenomenon | Distinguishing intervention | Supports the retention/irreducibility claim | Falsifies it |
|---|---|---|---|---|
| Coupled retention vs ALT-C (capacity) | PH-3 | Capacity-matched frozen control C1. | Treatment > C1 on held-out LL, p<0.01, ≥5 seeds. | Treatment ≤ C1. |
| Coupled retention vs decoupled change | PH-3 | Change-times decoupled from evidence (C2). | Treatment > C2 on held-out LL, p<0.01. | Treatment ≤ C2. |
| Emergent vs injected structure | PH-5 | Shuffled-input reference (C3). | `M = NMI(learned,true) − NMI(learned,shuffled)` > margin, `E[M\|H0]=0`. | `M` within noise of C3. |

These three are **already the E0 kill criteria** (`SCIENTIFIC_EXECUTION_SPEC.md` E0); reproducing them here shows the discrimination matrix is consistent with the protected canon, not competing with it.

---

## 4. Explicit non-distinguishability statements (required by the brief)

The brief requires: *"If two hypotheses cannot currently be distinguished experimentally, state that explicitly."* The following pairs cannot:

1. **T-01 vs T-02-with-state.** Non-distinguishable **in principle as written**. T-02's stateful kernel *contains* T-01's history dependence (`THEORY_NOTEBOOK_v3.md` §4.2). Any observation supporting a stateful T-02 supports T-01 identically. Resolution: they are not competing hypotheses; T-01 is the mechanism-conditional claim, T-02 is the measurement frame around it. The instrument tests T-01's memory reading against ALT-0/L/S/C, not against T-02.

2. **Internal-memory vs external/embodied-memory realizations of T-01.** Non-distinguishable **by any behavior-only measure** (`THEORY_LANDSCAPE.md` §2.4 — behavior underdetermines mechanism). PH-1's ablation intervention shows *that* a carrier exists and *that* it lives in the history; it cannot show *where* the carrier is stored without process-level lesions. Reported as a scope limit, not a defect.

3. **Bayesian-update vs gradient vs selection realizations of PH-3 retention.** Non-distinguishable on held-out LL alone. Separating them requires interventions on the update rule (freeze/perturb) that the minimal instrument does not include. Deferred, not claimed.

4. **Reward-maximization vs active-inference policies on PH-2/PH-4** (where present). The equivalence map (`THEORY_LANDSCAPE.md` §4) shows these coincide after matching preferences, models, and horizons. The minimal instrument does not attempt to separate them; doing so needs the epistemic-value manipulations noted there.

Stating these prevents the instrument from over-claiming mechanism identification from behavioral discrimination — the single most common error the theory phase warns against.

---

## 5. What the matrix buys

- The one **genuinely discriminative** test the instrument delivers is **PH-1 with the historical-carrier ablation**, separating the memory-carrying reading of T-01 from ALT-0/L/S/C. This is Experiment Zero's core (`EXPERIMENT_ZERO_PREREGISTRATION.md`).
- T-02 is demoted to a design constraint; this is a *result*, not a gap — the theory phase already established it.
- Retention/irreducibility contrasts (PH-3, PH-5) reuse the existing E0 kill criteria, so the new instrument and the protected canon give the same verdicts on the same data.
- Four non-distinguishability statements bound what the instrument may conclude, keeping mechanism claims out of behavior-only evidence.
