# Theory Notebook v3

**Status:** Scientific decision record  
**Date:** 2026-07-20  
**Input:** `THEORY_LANDSCAPE.md` and `THEORY_GAPS.md`  
**Decision:** No new universal principle is supported; no hypothesis is registered

## 1. Purpose

This notebook records whether the reduced landscape warrants a new computational principle of intelligence. It is intentionally shorter than the landscape and gap analysis. Its function is to preserve decisions, rejected formulations, and the evidence required to reopen them.

This document does not modify `PROGRAM_D_CANONICAL.md`, `theory/HYPOTHESIS_REGISTER.md`, or any preregistration. The Program D rule prohibiting new hypotheses remains binding for that program.

## 2. Decision rule

A proposed universal principle should satisfy all of the following. A narrower comparative, probabilistic, causal, or scaling hypothesis may be legitimate without claiming necessary and sufficient conditions:

1. a reproducible observation not adequately predicted by sampled existing theories;
2. evidence that the residual is not an omitted objective, prior, interface, task distribution, or resource constraint;
3. separation from known principles and behaviorally equivalent implementations;
4. a minimal, operational definition;
5. predictions that differ from existing theories;
6. necessary or sufficient conditions wherever the claim makes either kind of assertion;
7. a feasible falsification experiment with appropriate nulls; and
8. an explicit account of explanatory gain and added assumptions.

No reviewed candidate currently passes this standard as a universal principle. This does not prohibit narrower hypotheses. Program D governance separately prohibits registering new hypotheses in its protected canon.

## 3. Findings carried forward

### 3.1 The measurement frame is prior to mechanism

An empirical intelligence claim should declare its boundary/interface, target problem or domain, success relation, and system behavior. Resource/prior accounting is additionally required for adaptation-efficiency and fair-comparison claims. Evidence may be formal, exhaustive, online, intervention-based, held out, or independently replicated. This is a claim-specification checklist, not a mechanism from which intelligent behavior emerges.

### 3.2 Mechanistic necessities are conditional

- Memory is required when relevant histories are aliased at decision time.
- Feedback is required when outputs must regulate future conditions.
- Learning is required only when evidence-accessible change is needed to cross the performance standard and is worth its cost.
- Exploration is required only when feasible action-selected information has positive value and is needed to cross the performance standard.
- Compression and composition are candidate responses when finite resources make enumeration infeasible; task-specific lower bounds are needed for necessity claims.
- Causal semantics are a candidate response when observationally equivalent environments demand different interventions; an explicit causal model is not uniquely required if another policy realization succeeds within the same budget.

### 3.3 No reviewed mechanism is sufficient

Prediction, Bayesian inference, reward maximization, active inference, compression, symbol manipulation, embodiment, self-organization, evolution, global broadcasting, and collective aggregation each require additional boundary conditions. Combining all of them would not establish minimality or sufficiency.

## 4. Disposition of provisional P1 propositions

The labels below originate in the current research brief and were not found in the repository hypothesis register.

### T-01: History-Dependent State

**Disposition:** Do not register as a fundamental principle.

**Classification:** Derived and conditionally necessary.

**Reason:** For a fixed information set and loss, a memoryless policy cannot be conditionally optimal in two aliased histories with disjoint loss-minimizing outputs. This does not require retention if aggregate competence allows compromise, information is inaccessible, or its value is below its cost. State may be internal, embodied, environmental, social, or represented directly by the accessible history.

**Retained result:** Retained history is required only when it contains feasible information whose use is necessary to cross a declared performance standard.

**Failure as an intelligence theory:** Arbitrary counters and finite automata satisfy T-01 without competence, learning, breadth, or generalization.

### T-02: Stateful Conditional Transduction

**Disposition:** Retain only as descriptive vocabulary, not a causal or explanatory hypothesis.

**Classification:** Extensional schema; stateful component conditionally derived.

**Reason:** Conditional transduction describes input-output behavior. Stateful transduction already subsumes T-01, making the pair non-independent. Thermostats and protocol machines are counterexamples to sufficiency. For interactive competence, a policy kernel is incomplete without environment dynamics, causal ordering, intervention semantics, and, for efficiency claims, realization costs.

**Retained result:** Evaluate a non-anticipating causal policy together with its environment process over a declared target domain and success relation; add resource and prior accounting when the claim concerns efficiency or adaptation.

**Failure as an intelligence theory:** It predicts no distinction between competent and arbitrary transducers until an evaluation frame is added.

## 5. Candidate universal principles considered and rejected

### Candidate A: Relevant State Preservation

**Possible claim:** Intelligent systems preserve exactly the distinctions needed for future competent action.

**Why rejected:** As written, this is a consequence of task definition and successful performance. "Needed" is defined by the outcome, making the claim close to tautological. Stronger claims about minimal sufficient states are already covered by automata minimization, sufficient statistics, predictive state representations, and rate-distortion.

**Evidence that could reopen it:** A characterization of relevance over a clearly broad environment class that predicts which distinctions transfer across changes not used to construct it.

### Candidate B: Endogenous Objective Formation

**Possible claim:** Intelligence necessarily generates its own objectives.

**Why rejected:** Instrumental objectives derive from higher-level criteria. Terminal objectives cannot be selected as better or worse without inherited viability, preference, social, or selection conditions. Removing all criteria makes the claim ill-posed; retaining one makes objective formation derived.

**Evidence that could reopen it:** A system with only explicitly declared viability constraints repeatedly develops novel, transferable intermediate objectives, together with a theory predicting which objectives arise better than control, compression, and selection accounts.

### Candidate C: Open-Ended Capability Expansion

**Possible claim:** Intelligence requires a process that continually expands the space of attainable capabilities.

**Why rejected:** Sustained open-endedness is not yet a stable measured phenomenon in artificial systems. Current results can reflect expanding generators, archives, noise, novelty metrics, or finite curricula. The claim also excludes competent finite systems by definition without justification.

**Evidence that could reopen it:** Independent replications of sustained adaptive growth across multiple non-equivalent metrics, under fixed generators and matched nulls, with a mechanism predicting saturation versus continued expansion.

### Candidate D: Causal Counterfactual Competence

**Possible claim:** Intelligence requires representations supporting interventions and counterfactuals.

**Why rejected:** Reactive policies are sufficient in many task classes. Causal distinctions become necessary only where observationally equivalent situations demand different interventions. Structural causal modeling already supplies the relevant principle.

**Evidence that could reopen it:** A broad, precisely bounded task class for which causal representation has a formal resource advantage that no compiled reactive policy can match under the same budget.

### Candidate E: Multi-Scale Adaptive Closure

**Possible claim:** Intelligence requires mutually supporting regulation, learning, and self-modification across timescales.

**Why rejected:** This bundles feedback, differential retention, and hierarchical control without demonstrating an independent residual. It risks renaming a conjunction as a principle.

**Evidence that could reopen it:** A cross-scale phenomenon with predictions not obtainable by composing existing control, learning, and selection models.

## 6. Current dependency model

```text
Empirical intelligence claim
  should specify
    boundary/interface
    target problem/class/sequence/distribution
    success predicate/constraint/loss/utility
    behavior or process
    resources and priors when efficiency is claimed
    claim-matched evidence

Task conditions may then force
  valuable accessible history needed for threshold  -> distinction retention
  responsive feedback needed for threshold           -> closed-loop regulation
  valuable evidence-based change needed for threshold-> learning
  feasible positive-value action-selected evidence   -> exploration
  combinatorial structure under a precise lower bound -> candidate composition
  novel interventions under a precise lower bound     -> candidate causal model
  binding resource limits                              -> candidate allocation method
  population-scale demands                             -> candidate social retention
```

Learning normally entails retained distinction; active information acquisition normally entails consequential feedback and retention or immediate use. No arrow establishes sufficiency for intelligence. Each states a conditional obligation, not an independent axiom.

## 7. Relationship to existing Program D hypotheses

### H*: Error-Gated Structure Acquisition

H* remains a narrow, testable acquisition hypothesis. It instantiates differential retention through prediction-error-coupled capacity growth and uses MDL as a complexity control. It does not establish prediction error as the sole general learning signal, and it does not test interactive agency because the reduced experiment lacks an action-consequence loop.

**Notebook verdict:** retain its current canonical status; do not elevate it to a universal principle. Interpret any positive E0 result only for the tested environment class and controls.

### H1: Retrieval Uncertainty Calibration

H1 tests whether reported uncertainty corresponds to empirical correctness. Calibration is an important measurement property and can support metacognitive control, but it is not a minimal principle of intelligence.

**Notebook verdict:** retain as a product-scoped hypothesis, not theory foundation.

### H2: Affective Indexing

H2 tests whether affective framing retrieves useful problem-solving schemas. Even if supported, it would establish one indexing mechanism under a defined task distribution, not a universal principle.

**Notebook verdict:** retain as an empirical mechanism hypothesis with its existing circularity guards; no theoretical promotion before evidence.

## 8. Falsification priorities before new theory

1. **Measurement validity:** use claim-matched evidence; empirical generalization and adaptation claims need prospective or held-out, contamination-resistant evaluation, with resource accounting when efficiency is claimed.
2. **Mechanism discrimination:** use interventions to distinguish proposed internal mechanisms from behaviorally equivalent alternatives.
3. **Emergence controls:** specify system boundary, scale, macrovariable, designer contribution, and null model.
4. **Open-endedness operationalization:** establish sustained adaptive growth across several metrics before theorizing its mechanism.
5. **Population-level tests:** determine whether cumulative culture requires conditions beyond known transmission, selection, and coordination.

## 9. Reopening protocol

Any future proposal for a new principle should use this template. Fields not asserted by a scoped hypothesis may be marked `not claimed` rather than invented:

```text
Hypothesis ID:
Name:
Scope:
Definition:
Observation requiring it:
Motivation:
Derivation or independence proof:
Assumptions:
Predictions distinct from existing theories:
Necessary conditions:
Sufficient conditions:
Observable consequences:
Failure conditions:
Falsification experiments:
Null and matched-resource controls:
Relationship to the claim checklist, adaptive obligations, and prior theories:
Expected weaknesses:
Confidence assessment:
Registration authority:
```

The `Registration authority` field is mandatory because scientific support and governance permission are separate: Program D's protected canon prohibits new registrations without an explicit governance change.

## 10. Self-critique

### Hidden assumptions

- The operational definition privileges measurable task performance and may omit intrinsic or phenomenological properties.
- The system boundary is treated as selectable, but different boundaries can change whether memory, computation, or objectives appear internal.
- Target domains are treated as specifiable even though real ecological conditions drift and may be unknown.
- The synthesis favors extensional comparison and may underweight mechanistic explanations that matter despite identical observed behavior.
- "Resource" combines unlike quantities; time, energy, memory, data, and hardware may not admit one ordering.

### Missing or underrepresented literature

- Formal learning theory, online learning, PAC-Bayes, and algorithmic statistics deserve deeper treatment.
- Ecological psychology, autopoiesis, basal cognition, origin-of-life work, formal control, and evolutionary theory require deeper systematic treatment.
- Neuroscience evidence is sampled rather than systematically reviewed because the target is implementation-independent.
- Economic mechanism design and distributed computation could deepen collective-intelligence analysis.
- Philosophy of computation and consciousness are deliberately excluded except where they constrain operational claims.

### Alternative explanations

- A richer definition of intelligence centered on autonomous viability would make feedback and self-maintenance foundational rather than conditional. That would exclude passive but broadly competent systems and must be stated as a scope choice.
- A skill-acquisition definition would make learning central, while a competence definition permits frozen policies. The present documents distinguish these instead of choosing silently.
- An ecological or enactive definition may treat agent and environment as one coupled system and may reject, rather than merely relocate, a computational description.

### Simpler formulation

The entire result can be compressed to:

> There is no demonstrated assumption-free intelligence mechanism. Specify the target, information, success relation, and relevant resources; then test which distinctions and adaptations that scope forces.

The longer landscape remains necessary to show that this statement is a reduction of existing theories rather than an unsupported assertion.

## 11. Confidence assessment

| Conclusion | Confidence | Main uncertainty |
|---|---:|---|
| Comparative intelligence measurement depends on target, interface, prior knowledge, and relevant resources. | High | Pure correctness claims do not require all resource accounting. |
| T-01 is conditionally derived rather than universal. | High | Definitions that restrict intelligence to temporally adaptive systems. |
| T-02 is descriptive and insufficient. | High | None substantial; counterexamples are direct. |
| Prediction, compression, embodiment, symbols, and self-models are not universal necessities. | Moderate-high | Broader task scopes may make some practically unavoidable. |
| A1-A4 are overlapping dimensions of adaptive online agency. | High | Their exact dependencies vary with boundary and timing. |
| Open-endedness is a genuine residual gap. | Moderate | The phenomenon may dissolve under better measurement. |
| This selective review supports no new universal principle. | Moderate | The review is not systematic and major adjacent literatures remain underrepresented. |

## 12. Final decision

**No T-03 or other new hypothesis is registered.**

T-01 is reduced to a conditional information-sufficiency result under a declared loss, accessible information set, cost, and performance standard. T-02 is reduced to a behavioral description that requires an environment process and explicit claim specification to evaluate interactive competence. The remaining gaps are real research questions, but this review supports none as a new universal computational principle.

Scoped hypotheses about open-endedness, cumulative culture, causal abstraction, or preference development remain scientifically available outside the protected Program D register. Universal novelty is deferred until stronger measurement, broader review, and discriminating experiments exist.
