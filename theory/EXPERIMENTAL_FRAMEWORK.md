# P1 Experimental Framework — Master Reference & Self-Review

**Status:** Canonical reference for Project P1's experimental program, version 1.0
**Date:** 2026-07-20
**Author role:** Principal Experimental Methodologist
**Scope:** Ties together the four deliverables into one instrument and subjects the whole to adversarial self-review.

---

## 0. What this framework is (and is not)

**It is** the minimum experimental apparatus that lets P1 determine whether competing computational hypotheses make *genuinely different* predictions, built on the primitives already in `framework/core` and continuous with the existing Program D kill criteria.

**It is not** a benchmark, a theory, or a measure of intelligence. Per the theory phase (`THEORY_NOTEBOOK_v3.md` §12), no new universal principle is registered, and this framework registers none. It is a **scientific instrument**: its job is to *discriminate and to reject impostors*, not to score.

### 0.1 The four deliverables

| # | Document | Function |
|---|---|---|
| 1 | `PHENOMENON_REGISTRY.md` | Five null-anchored phenomena (PH-1…PH-5) mapped one-to-one onto the adaptive-agency obligations A1–A4 plus the emergence/irreducibility measurement problem. |
| 2 | `HYPOTHESIS_DISCRIMINATION_MATRIX.md` | What separates T-01's memory reading from ALT-0/L/S/C; explicit statement that T-01 and T-02 are **not** mutually distinguishable as written. |
| 3 | `preregistrations/EXPERIMENT_ZERO_PREREGISTRATION.md` | EXP-Z0: minimal complete pipeline-validation run with positive+negative controls, leakage rejection, two-hypothesis discrimination, bootstrap uncertainty, pre-committed decision rule. |
| 4 | `MEASUREMENT_VALIDITY.md` | Per-metric construct-validity audit; the rule that no raw magnitude may gate a claim. |

### 0.2 The single organizing idea

> Every evidential quantity in this framework is a **difference between a treatment and a matched control whose null has a computed expectation.** Raw performance never carries weight. This is the operational form of the brief's "no task performance as a proxy for intelligence."

This one rule generates the phenomenon nulls (PH-1 ceiling, PH-5 shuffle), the discrimination interventions (carrier ablation), and the measurement-validity table. It is what makes the apparatus an instrument rather than a leaderboard.

---

## 1. How a hypothesis flows through the instrument

```text
Claim (e.g. memory-carrying T-01)
  → Phenomenon that operationalizes it            (PH-1)
    → Intervention that separates it from impostors (carrier ablation)
      → Metric as a DIFFERENCE vs null-expectation control (Δ vs ceiling, C vs ablation)
        → Uncertainty (22 seeds, 10k bootstrap, α=0.01)
          → Pre-committed decision rule (four-way (Δ,C) readout)
            → Verdict scoped to the tested environment only
```

Any claim that cannot be pushed through all seven stages is not yet testable by this instrument, and the framework says so rather than inventing a proxy.

---

## 2. Self-Review — attempting to invalidate the framework

The brief mandates an adversarial pass. Each subsection tries to *break* the framework; the response is either a defense or an accepted limitation carried into the revision log.

### 2.1 "Could trivial systems succeed?"

**Attack.** A finite-state machine, a counter, or a lookup table satisfies "history-dependence" and could pass PH-1.

**Response.** This is exactly why PH-1 uses a **memoryless ceiling** as the null and a **carrier-ablation** co-requirement. A counter unrelated to the alias schedule produces `Δ≈0`. A lookup table that memorizes the stream fails the held-out split and fails DV-3 localization. The four impostors (ALT-0/L/S/C) are named and each has a dedicated control (`HYPOTHESIS_DISCRIMINATION_MATRIX.md` §1.1). **Residual risk accepted:** a trivial system *specifically engineered* to carry the cue would pass — and it *should*, because PH-1 tests carrier-use, not intelligence. The framework never claims a PH-1 pass implies intelligence; that over-claim is blocked in `MEASUREMENT_VALIDITY.md` M1. So trivial success is either excluded by a control or is a correct (scoped) result, not a false positive.

### 2.2 "Are the hypotheses genuinely distinguishable?"

**Attack.** The brief's own two hypotheses might be indistinguishable, making the whole exercise vacuous.

**Response.** They *are* indistinguishable, and the framework **states so explicitly** (`HYPOTHESIS_DISCRIMINATION_MATRIX.md` §4): T-02 subsumes T-01, so no experiment separates them as written. Rather than hide this, the framework re-poses the real contrast — memory-carrying T-01 vs ALT-0/L/S/C — which *is* distinguishable via the `(Δ,C)` four-way readout (§6 of the preregistration). Four further non-distinguishability statements (internal vs external memory; Bayesian vs gradient vs selection retention; reward-max vs active-inference; T-02 unfalsifiability) bound what may be concluded. **This is a strength, not a gap:** the instrument reports the limits of its own discriminative power.

### 2.3 "Are the metrics measuring the intended construct?"

**Attack.** LL, accuracy, and task score are classic proxies that drift from the construct.

**Response.** `MEASUREMENT_VALIDITY.md` gives every metric an explicit "does NOT measure" column and admits each **only as a difference** against a null-expectation control. Absolute LL is declared invalid for any intelligence claim; only T−C1/C2 differences gate H\*. ECE is declared a measurement property, not a principle. Task score is admitted only as framed−unframed on a third-party set with a circularity guard. **Residual limitation accepted:** the "true latent" granularity in M4 and the partition-metric choice retain researcher degrees of freedom that the shuffle-null does not remove; this is flagged (`THEORY_GAPS.md` §14) and is a reason M4 cannot support a general emergence claim.

### 2.4 "Could benchmark optimization invalidate the conclusions?"

**Attack.** If someone tunes to the instrument, a pass becomes meaningless (Goodhart).

**Response.** Three structural defenses: (i) **no-tuning / frozen-code rule** during runs (`EXPERIMENT_INTERFACE_SPEC.md` §6); (ii) **derived, not fitted, thresholds** — the MDL `λ` is a derivation, ECE bins are locked equal-width, the EXP-Z0 margin mirrors the pre-existing `M=0.05` scale; (iii) the decisive metrics are **differences against controls that share the treatment's capacity and compute**, so optimizing raw score raises the control equally and cancels. **Residual risk accepted:** a sufficiently determined actor could design an environment-specific carrier exploit; the defense is that EXP-Z0's leakage guard (`C>0`) and localization (DV-3) would flag a non-generalizing exploit, and every verdict is scoped to the tested environment, so a gamed pass cannot be laundered into a general claim.

### 2.5 "Is any unnecessary complexity present?"

**Attack.** Five phenomena, six metrics, five controls — is this minimal?

**Response.** Pressure-tested each element:
- **PH-1–PH-4** are one-to-one with the four obligations A1–A4; dropping any leaves an obligation axis untestable. **Kept.**
- **PH-5** overlaps PH-3 (both touch A3). **Kept anyway**, but justified narrowly: PH-5 is the *irreducibility* measurement (clause iii / I2) that PH-3 (retention) does not cover, and it anchors the instrument to the existing E0. Removing it would sever continuity with the protected canon. This is the one deliberate redundancy, and it is argued, not accidental.
- **EXP-Z0 controls:** each of N1, N2, P1, P2 rejects a *distinct* impostor or checks a *distinct* pipeline property (ceiling, leakage, solvability, structure-necessity). Dropping any one un-guards a named confound. **All kept.**
- **Excluded on purpose:** open-endedness, general emergence, self-model, composition, causality (`PHENOMENON_REGISTRY.md` §6) — each fails a selection criterion today; adding them now would be the unnecessary complexity. **Excluded.**

**Verdict:** the set is at the minimum that still covers every obligation axis and stays continuous with Program D. One redundancy (PH-5) is retained with an explicit argument.

### 2.6 Additional self-attacks

- **"The environment is synthetic — does anything transfer?"** Accepted limitation: every verdict is explicitly scoped to its environment (`MEASUREMENT_VALIDITY.md` M1 limitations). The instrument validates *the pipeline* and *scoped contrasts*, never general competence. Synthetic-but-known is a deliberate choice so ground truth exists for calibration (EXP-Z0 §0).
- **"22 seeds is arbitrary."** It is derived from the miss-probability rule `(1−0.10)^22 < 0.10` used across P1 (`EXP1_PREREGISTRATION.md` §7), not chosen for convenience.
- **"Behavior underdetermines mechanism — so what do you actually learn?"** You learn *that* a distinction is carried and *that* it lives in the history (via ablation), never *where* or *how*. This is stated as the framework's hard ceiling (`HYPOTHESIS_DISCRIMINATION_MATRIX.md` §4.2), consistent with `THEORY_LANDSCAPE.md` §2.4.

---

## 3. Revisions made as a result of this review

The review did not merely defend; it forced these choices, now baked into the deliverables:

1. **T-01/T-02 demoted from "two hypotheses" to "one mechanism-claim + one measurement schema"** after §2.2 confirmed non-distinguishability. The matrix is rebuilt around T-01-vs-impostors instead.
2. **Leakage elevated to the primary rejected explanation** in EXP-Z0 (§2.1) — the `C>0` co-requirement was added specifically so leakage produces a *detectable* `(Δ>0, C≈0)` signature rather than a silent false positive.
3. **PH-5 redundancy made explicit and argued** (§2.5) rather than dropped, to preserve continuity with E0.
4. **Every metric re-expressed as a difference** (§2.3) — the "no raw magnitude gates a claim" rule in `MEASUREMENT_VALIDITY.md` §8 is the direct output of this review.

---

## 4. Standing limitations (carried, not resolved)

| Limitation | Consequence | Where honored |
|---|---|---|
| Behavior underdetermines mechanism | Cannot locate/identify internal memory or update rule | Matrix §4; Validity §8 rule 5 |
| Synthetic environments | No general-competence transfer claim | Validity M1; Registry §6 |
| M4 residual researcher DOF | No universal emergence claim | Gaps §14; Validity M4 |
| T-02 unfalsifiable as schema | Used as design constraint, not tested | Matrix §2 |
| A2/A4 phenomena (PH-2,PH-4) not yet in an executable preregistration | Interactive-agency obligations specified but not yet calibrated | Registry PH-2/PH-4; future EXP-Z1 |

**Next instrument step (not part of this deliverable):** an EXP-Z1 calibration for PH-2 (consequence-coupled regulation), since H\*/E0 currently has no action loop and A2 is therefore untested (`THEORY_NOTEBOOK_v3.md` §7.1). It should mirror EXP-Z0: known-answer environment, open-loop replay as the null, pre-committed decision rule.

---

## 5. Bottom line

The framework delivers exactly one genuinely discriminative, fully-controlled test today — **PH-1 via carrier-ablation, calibrated by EXP-Z0** — and is honest that this is what it delivers. It states where hypotheses cannot be separated, admits no metric as an intelligence proxy, rejects four named impostors by construction, quantifies its uncertainty, and scopes every verdict to its environment. That is the minimum viable scientific instrument for P1, and it is continuous with the protected Program D canon rather than a parallel benchmark.
