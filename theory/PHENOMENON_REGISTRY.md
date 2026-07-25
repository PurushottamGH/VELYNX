# Phenomenon Registry (Deliverable 1)

**Status:** Canonical experimental-instrument reference, version 1.0
**Date:** 2026-07-20
**Author role:** Principal Experimental Methodologist
**Input:** `THEORY_LANDSCAPE.md`, `THEORY_GAPS.md`, `THEORY_NOTEBOOK_v3.md`, `HYPOTHESIS_REGISTER.md`
**Epistemic status:** Instrument specification, not a hypothesis. Registers phenomena to observe, not claims about them.

---

## 0. Purpose and scope

This registry names the **smallest set of experimentally tractable computational phenomena** that lets Project P1 tell whether competing computational hypotheses make genuinely different predictions. It is an instrument, not a benchmark: each phenomenon is chosen because a well-specified intervention on it *separates* hypotheses, not because a system "scoring high" on it is impressive.

Design constraints inherited from the theory phase and honored here:

- **[FACT]** The theory phase (`THEORY_NOTEBOOK_v3.md` §12) registered **no** new universal principle. This registry therefore does not smuggle one in. Every phenomenon is scoped, null-referenced, and resource-accounted.
- **[FACT]** The brief's T-01 was reduced to obligation **A1** (task-relevant distinction retention; `THEORY_LANDSCAPE.md` §7) and T-02 to a descriptive measurement schema that *subsumes* T-01. The registry treats A1–A4 (`THEORY_LANDSCAPE.md` §6.2) as the phenomenon axes, because that is the level at which the reduced propositions actually make or fail to make distinct predictions.
- **[FACT]** Program D governance forbids new hypotheses in its protected canon. Phenomena here are observation targets usable by *both* the protected hypotheses (H\*, H1, H2) and the scoped alternatives in the Discrimination Matrix. No phenomenon requires registering a new principle.

### 0.1 Selection criterion (why these five and not fifty)

A phenomenon is admitted only if it satisfies all of:

1. **Operational**: definable as a function of logged observables with no investigator judgment call at scoring time.
2. **Discriminative**: at least two serious hypotheses predict *different* values of its observable under the same intervention (verified in `HYPOTHESIS_DISCRIMINATION_MATRIX.md`).
3. **Null-anchored**: a trivial/random control has a known, computed expected value on the observable, so "success" is measured as distance from triviality, not raw magnitude.
4. **Resource-bounded**: the observable is reported jointly with the compute/memory/data budget, so no hypothesis wins merely by being handed more capacity.
5. **Cheaply realizable**: implementable on the existing `framework/core` primitives (Environment, Predictor, MDL growth, emergence statistic) or a minimal extension, so the instrument itself is reproducible.

Phenomena failing (2) are benchmarks, not instruments, and are excluded. This is why the set is five, not a catalogue.

### 0.2 The five phenomena at a glance

| ID | Name | Obligation axis | Core question it makes answerable |
|---|---|---|---|
| PH-1 | Temporal aliasing resolution | A1 | Does the system retain a distinction that is *only* recoverable from history? |
| PH-2 | Consequence-coupled regulation | A2 | Does closing the action→observation loop change behavior beyond open-loop? |
| PH-3 | Differential retention of improvement | A3 | Does an evidence-revealed improvement persist, above a decoupled-change control? |
| PH-4 | Value-driven information acquisition | A4 | Does the system sample informative actions only when they have positive net value? |
| PH-5 | Null-referenced structure acquisition | A3 ∩ measurement | Is acquired latent structure irreducible to designer-injected statistics? |

PH-5 is the phenomenon Program D's H\*/E0 already targets; it is included so the new instrument is continuous with the existing falsification machinery rather than a parallel track. PH-1–PH-4 are the minimal decomposition that the theory phase identified as the *actual* content of the reduced T-01/T-02 and the adaptive-agency obligations.

---

## PH-1 — Temporal Aliasing Resolution

- **ID:** PH-1
- **Name:** Temporal aliasing resolution (the operational content of reduced T-01 / obligation A1)
- **Operational definition:** Given an observation stream in which two decision points present **identical currently-accessible inputs** but require **different loss-minimizing outputs**, and where the disambiguating information appeared earlier in the stream, the phenomenon is the system attaining loss on those aliased points that is strictly below the best memoryless policy's loss. Formally: let `A ⊂ timesteps` be the aliased set; PH-1 is present iff `E[loss | A, system] < E[loss | A, best_memoryless]` under matched information and compute.
- **Observable behavior:** Divergent, correct outputs at timesteps whose immediate inputs are indistinguishable; a controlled probe (the "aliasing battery") measures accuracy on matched-input / mismatched-target pairs.
- **Information required:** The full stream (system side); an experimenter-side ground-truth register of which past observation carries the disambiguating bit and which timesteps are aliased. The ground-truth register is never exposed to the system (same discipline as `Environment.ground_truth`).
- **Boundary conditions:** Requires (i) genuine aliasing — the disambiguating distinction must be *absent* from current input by construction; (ii) the distinction must be *feasibly* carried forward within the stated memory budget; (iii) stationary aliasing structure within a trial. Outside these, absence of PH-1 is uninformative (the information may be inaccessible or not worth its cost — `THEORY_LANDSCAPE.md` §7 residue).
- **Plausible trivial explanations:** (a) leakage — the disambiguating bit is still weakly present in the current input; (b) a fixed periodic counter coincidentally aligned with the alias schedule; (c) exploiting a spurious surface correlate of the target rather than the historical cause; (d) memorizing the specific stream rather than the aliasing *rule*.
- **Candidate computational requirements:** Some carrier of state across time (internal memory, external trace, or embodied buffer). The registry is deliberately **agnostic to the carrier** — this is the crux of the T-01 reduction: A1 requires distinguishability, not internal memory specifically.
- **Why scientifically valuable:** It is the one phenomenon that makes the reduced T-01 falsifiable rather than tautological. A memoryless control has a *computable* ceiling; beating it is not "task performance as proxy for intelligence" but a direct test of an information-theoretic necessity. It also exposes leakage confounds that plague informal "the model remembers" claims.

---

## PH-2 — Consequence-Coupled Regulation

- **ID:** PH-2
- **Name:** Consequence-coupled regulation (obligation A2)
- **Operational definition:** In an environment whose future observations depend on the system's outputs, the phenomenon is a strict reduction in a declared controlled-variable deviation (or increase in declared viability/return) under the **closed loop** relative to a matched **open-loop** system whose outputs are replayed but disconnected from the environment. PH-2 present iff `deviation(closed) < deviation(open_loop_replay)` at matched compute and matched output distribution.
- **Observable behavior:** Disturbance rejection; the controlled variable returns to its acceptable region after perturbation faster/more reliably than the open-loop replay.
- **Information required:** Controlled-variable trace, output trace, perturbation schedule, and the open-loop replay's trace generated by feeding the *same* output sequence into a fresh environment instance with no feedback.
- **Boundary conditions:** Environment must be genuinely output-sensitive (a passive stream cannot exhibit A2); perturbations must be within the regulator's response variety (Ashby requisite-variety bound, `THEORY_LANDSCAPE.md` §3.2). If the controlled variable is insensitive to output, PH-2 is undefined.
- **Plausible trivial explanations:** (a) a thermostat — trivial feedback with no broader competence; (b) the environment self-corrects regardless of output (must be excluded by the open-loop replay control); (c) output happens to correlate with disturbance by construction leak.
- **Candidate computational requirements:** A closed sensorimotor loop and a controlled variable with a target region. Explicit world model is *not* required (good-regulator theorem is conditional, not mandatory — `THEORY_LANDSCAPE.md` §3.2).
- **Why scientifically valuable:** H\*/E0 as currently built has **no action-consequence loop** (`THEORY_NOTEBOOK_v3.md` §7.1). PH-2 is the phenomenon that would let P1 test the A2 obligation at all, and is the precondition for any later interactive-agency claim. Without it the program can only ever study passive prediction.

---

## PH-3 — Differential Retention of Improvement

- **ID:** PH-3
- **Name:** Differential retention of evidence-revealed improvement (obligation A3)
- **Operational definition:** After the stream reveals a change that improves the declared success relation, the phenomenon is a **persistent** performance gain that (i) exceeds a fixed-capacity/frozen control and (ii) exceeds a capacity-matched control whose changes occur at times **decoupled** from the improving evidence. PH-3 present iff `gain(error_gated) > max(gain(frozen), gain(decoupled))` at matched capacity and compute.
- **Observable behavior:** A step or ramp in held-out predictive score following the informative evidence, absent in the decoupled control.
- **Information required:** Held-out predictive log-likelihood over time for treatment, frozen control, decoupled-change control; the evidence-arrival schedule.
- **Boundary conditions:** Requires evidence that *is* accessible and *does* imply a beneficial change worth its cost; a stationary or slowly-drifting target so retention is meaningful. If the environment is too easy (frozen control already saturates) PH-3 is unmeasurable — this is failure mode F1 in `HYPOTHESIS_REGISTER.md`.
- **Plausible trivial explanations:** (a) drift — score rises for reasons unrelated to retention (excluded by decoupled control); (b) capacity, not coupling — more parameters alone raise score (excluded by capacity-matching); (c) overfitting the training stream rather than transferring (excluded by held-out evaluation).
- **Candidate computational requirements:** A mechanism that (a) detects an improving change and (b) preserves it — learning/selection/Bayesian update. The *coupling to evidence* is the tested content, not the specific update rule.
- **Why scientifically valuable:** This is exactly the H\* content, generalized off the specific MDL-growth implementation. Making PH-3 a first-class phenomenon lets alternative retention mechanisms (gradient, Bayesian, selection) compete on the same instrument, which is what turns H\* from a single-implementation claim into a discriminative test.

---

## PH-4 — Value-Driven Information Acquisition

- **ID:** PH-4
- **Name:** Value-driven information acquisition (obligation A4)
- **Operational definition:** When some actions yield no immediate reward but reduce decision-relevant uncertainty, the phenomenon is the system taking such actions **only when their expected information value exceeds their cost**, producing lower downstream loss than both a no-exploration control and a random-exploration control at matched action budget. PH-4 present iff downstream loss ordering is `value_driven < random_explore` and `value_driven < no_explore` under an information-gated environment.
- **Observable behavior:** Selective probing — informative actions concentrated where uncertainty is high and cost is low; abstention where information is worthless or risk is irreversible.
- **Information required:** Action trace, per-action cost, downstream loss, and an environment with separable "informative but unrewarding" vs "rewarding" actions plus at least one irreversible trap.
- **Boundary conditions:** Information must be *feasibly* acquirable by action and must have positive net value (`THEORY_LANDSCAPE.md` §3.3). In known, passive, or one-shot tasks A4 is not required and its absence is uninformative. Irreversible-risk regions must exist to distinguish rational abstention from mere inactivity.
- **Plausible trivial explanations:** (a) undirected novelty-seeking that happens to help (excluded by the random-exploration control matched on action count); (b) reward leakage making "informative" actions secretly rewarding; (c) exhaustive enumeration disguised as exploration (excluded by budget accounting).
- **Candidate computational requirements:** A representation of decision-relevant uncertainty and a value-of-information comparison. Specific exploration bonuses are implementations, not the tested content.
- **Why scientifically valuable:** A4 is the obligation most often faked by novelty heuristics. A phenomenon that requires *net-positive-value* selectivity (not coverage) and includes irreversible traps is the sharpest available separation between genuine value-of-information behavior and its trivial mimics.

---

## PH-5 — Null-Referenced Structure Acquisition

- **ID:** PH-5
- **Name:** Null-referenced structure acquisition (H\* clause (iii) / assumption I2; the existing E0 target)
- **Operational definition:** Structure the system learns from a stream with known hidden latents is **irreducible to injected statistics** iff the null-referenced statistic `M = NMI(learned, true) − NMI(learned, shuffled) > margin` with `E[M | H0] = 0` (`METRIC_SPECIFICATION.md` §5). PH-5 present iff `M` exceeds the pre-registered margin *and* held-out LL beats fixed-capacity and error-decoupled controls.
- **Observable behavior:** A learned partition that aligns with the true generative regime far more than with a temporally-shuffled surrogate of the same marginals.
- **Information required:** Learned state sequence, true latent sequence, shuffled-input learned sequence; held-out LL for treatment and both controls.
- **Boundary conditions:** Environment must be non-linear and require structural capacity (linear baseline must fail); MDL threshold must be *derived*, not hand-tuned (else failure mode F2). Single-state degenerate partitions yield undefined NMI and are handled as 0.
- **Plausible trivial explanations:** (a) the "learned" partition just re-reads designer-injected marginal statistics (this is exactly what the shuffled reference subtracts out); (b) graph-isomorphism-style scoring with researcher degrees of freedom (rejected in favor of null-referenced NMI — `PROGRAM_D_SPECIFICATION.md` §2.5); (c) capacity alone.
- **Candidate computational requirements:** Error-coupled capacity growth plus a null-referenced emergence measure. Continuous with H\*.
- **Why scientifically valuable:** It is the phenomenon that operationalizes the single hardest word in the whole program — "emergent" — as a subtraction against a null with known expectation zero. It is already wired into E0, so PH-5 anchors the new instrument to the program's existing lethal test and prevents the registry from drifting into a parallel, uncalibrated track.

---

## 6. What is deliberately excluded

To keep the instrument minimal and honest, the following are **not** phenomena in this registry, with reasons:

- **Raw task performance / benchmark score.** Excluded: conflates prior knowledge, data, compute, and task fit (`THEORY_GAPS.md` §13). Admitted only inside a phenomenon as a *differenced* quantity against a matched control.
- **"Open-ended growth."** Excluded: the explanandum is not yet a stable measured phenomenon (`THEORY_GAPS.md` §11). Registering it now would violate selection criterion (1).
- **"Emergence" in general.** Excluded except as PH-5's null-referenced special case; the general construct lacks a unique operational criterion (`THEORY_GAPS.md` §14).
- **Self-model / metacognition / consciousness.** Excluded: not operationally separable from report and decision at the current instrument resolution (`THEORY_LANDSCAPE.md` §3.12).
- **Compositional generalization, causal abstraction.** Deferred, not rejected: they are legitimate scoped phenomena but require task-family generators beyond the minimal instrument; adding them now fails selection criterion (5). They are candidates for a v2 registry once PH-1–PH-5 are validated.

---

## 7. Dependency and coverage map

```text
Reduced T-01  ── is exactly ──▶ PH-1 (A1)
Reduced T-02  ── subsumes T-01, adds env process ──▶ PH-1 + PH-2 (needs A2 to have content)
Adaptive agency obligations A1–A4 ──▶ PH-1, PH-2, PH-3, PH-4
Program D H*  ── already targets ──▶ PH-3 (retention) + PH-5 (irreducibility)
Program D H1/H2 ── measurement-only, use PH-* observables' null discipline, not new phenomena
```

Coverage claim: PH-1–PH-4 cover the four adaptive-agency obligations one-to-one; PH-5 covers the emergence/irreducibility measurement problem. No obligation axis is uncovered, and no phenomenon duplicates another's discriminative content. This is the minimality argument for the set.

## 8. Revision triggers

Revise this registry if: a phenomenon's null control turns out to have non-zero expectation under H0; two phenomena are shown to be experimentally non-separable (collapse them); a deferred phenomenon (composition, causality) receives a minimal generator meeting selection criterion (5); or a phenomenon is shown to be passable by a trivial system not excluded by its listed controls (add the missing control or retire the phenomenon).
