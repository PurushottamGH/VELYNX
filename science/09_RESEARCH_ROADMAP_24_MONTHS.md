# P1 Scientific Research Roadmap — 24 Months

- **Roadmap period:** August 2026–July 2028
- **Version:** 1.0.0
- **Scientific phase at start:** Discovery
- **Principle:** Milestones represent reductions in uncertainty or justified changes in scientific belief, never software completion.

## 1. Roadmap rules

1. Dates are planning windows, not evidence deadlines.
2. A milestone exits only when its scientific decision is recorded.
3. A negative or null result can complete a milestone successfully if it resolves the question.
4. Discovery may proceed around unresolved validation debt when results remain exploratory.
5. Later milestones are conditional; failed assumptions can cancel entire branches.
6. The roadmap is re-ranked after every material Scientific Decision.
7. No experiment is retained solely because engineering has already implemented it.

## 2. Program questions

The roadmap addresses five nested questions:

- **Q1 — Measurement:** Can P1 validly measure retention, adaptation, efficiency, robustness, transfer, and learned structure?
- **Q2 — Minimal mechanisms:** Which mechanisms provide effects beyond matched simpler controls?
- **Q3 — Interaction:** Do independently supported mechanisms combine constructively, redundantly, or destructively?
- **Q4 — Scope:** Across which environment and task classes do supported effects persist?
- **Q5 — Theory:** Can multiple validated effects be explained by a compact model that predicts new outcomes?

## 3. Milestones

### Months 1–2 — M1: Scientific state initialization

**Question:** What does P1 actually know, and which legacy claims are reusable?

**Work:** Migrate active hypotheses, experiments, assumptions, negative results, and open questions into the new schemas; classify provenance and phase; expose contradictions.

**Evidence gained:** A traceable baseline scientific state and confidence inventory.

**Exit decision:** Every currently active line is classified as fact, evidence, hypothesis, theory candidate, speculation, unknown, or debt. Conflicting authority labels are no longer treated as scientific status.

**Failure condition:** Material claims remain untraceable or silently duplicated.

### Months 2–4 — M2: Measurement calibration

**Question:** Do P1’s metrics identify the constructs they name?

**Minimal experiments:** Positive and negative controls for forgetting/retention, adaptation speed, calibration, and replay cost; compare current forgetting scalar with final excess loss and joint stability–plasticity measures.

**Evidence gained:** Construct-validity map and prohibited interpretations for each metric.

**Exit decision:** At least retention and adaptation have calibrated measures with known failure modes; invalid metrics are retired or renamed.

**Kill/pivot:** If no metric discriminates known positive and negative controls, mechanism experiments pause and measurement remains the research target.

### Months 3–6 — M3: Replay effect isolation

**Question:** Does historical replay cause a decision-relevant retention benefit beyond generic extra updates and decay refresh?

**Minimal experiments:** Update-count/decay-matched historical replay versus current-sample or sham controls; multiple exploratory environments; report initial mastery and final excess loss.

**Evidence gained:** Effect existence and magnitude separated from obvious resource confounds.

**Exit decision:** Replay hypothesis advances to Validation, is revised to a narrower condition, or is rejected within tested scope.

**Failure condition:** Benefit disappears under matched resources or violates a prespecified adaptation guardrail.

### Months 4–7 — M4: Replay allocation discrimination

**Question:** Does surprise contain useful allocation information?

**Minimal experiment:** Surprise-triggered versus equal-budget random timing, with boundary-triggered diagnostic if needed.

**Evidence gained:** Whether timing signal—not budget—changes outcomes.

**Exit decision:** Surprise gating advances, is merged with generic sparse replay, or is rejected.

**Stop condition:** If matched random is equivalent, do not proliferate surprise-specific architecture.

### Months 6–9 — M5: Robustness of minimal replay findings

**Question:** Which moderators determine the replay effect?

**Scaling study:** Vary task overlap, change rate, recurrence, memory budget, decay/interference strength, and task order using factorial screening rather than exhaustive architecture search.

**Evidence gained:** Boundary conditions and variance components.

**Exit decision:** Produce a scoped replay principle candidate or retain an environment-specific effect only.

**Failure condition:** Effect direction is unstable without a predictive moderator.

### Months 8–11 — M6: Calibration and uncertainty reporting

**Question:** Can P1 report uncertainty that tracks empirical correctness?

**Experiments:** Discovery calibration curves, strong constant/base-rate baselines, then held-out validation if signal exists; examine distribution shift and abstention.

**Evidence gained:** Calibration effect, robustness, and failure under shift.

**Exit decision:** Validate a scoped uncertainty-reporting hypothesis, revise it, or reject the claim.

**Stop condition:** Do not retain semantic confidence labels if they do not beat simple calibrated baselines.

### Months 10–13 — M7: Learned structure versus injected structure

**Question:** Can any P1 process acquire useful structure not reducible to initialization, environment encoding, or evaluator choice?

**Experiments:** Fixed-capacity, capacity-matched random growth, shuffled-input, designer-information, and metric-researcher-DOF controls. Audit every built-in bias.

**Evidence gained:** Whether an effect survives injection and capacity confounds.

**Exit decision:** Advance a narrowly scoped structure-acquisition hypothesis or reject/revise emergence language.

**Failure condition:** Learned structure is predicted by injected priors or disappears under matched controls.

### Months 12–15 — M8: Transfer and recombination

**Question:** Does any supported mechanism improve outcomes outside the training/task regime that selected it?

**Experiments:** Held-out generators, reordered tasks, unseen compositions, and transfer with frozen mechanism choices.

**Evidence gained:** Transfer boundary and distinction between interpolation, retention, and reusable structure.

**Exit decision:** Generalize scope only where transfer evidence permits; otherwise preserve narrow claims.

### Months 14–17 — M9: Mechanism interaction matrix

**Question:** Do validated mechanisms combine additively, synergistically, redundantly, or antagonistically?

**Experiments:** Minimal factorial combinations of only mechanisms that survived prior milestones; interaction effects against matched single-mechanism baselines.

**Evidence gained:** Causal interaction structure and redundancy.

**Exit decision:** Retain the simplest non-redundant set. Remove combinations whose complexity has no measurable contribution.

**Precondition:** At least two mechanisms possess validation-grade support. Otherwise defer M9.

### Months 16–19 — M10: Candidate theory formation

**Question:** Can supported effects be explained by a compact computational model?

**Work:** Form Candidate theories only from independently supported hypotheses; specify relationships, alternatives, boundary conditions, and novel risky predictions.

**Evidence gained:** Competing explanatory models and discriminating predictions.

**Exit decision:** Select one or more Provisional theories for testing, or record that synthesis is premature.

### Months 18–22 — M11: Theory discrimination

**Question:** Which candidate theory best predicts untouched conditions?

**Experiments:** Theory-derived predictions selected to maximize disagreement among candidates; frozen predictions and untouched environment conditions.

**Evidence gained:** Predictive discrimination beyond retrospective fit.

**Exit decision:** Support, revise, reject, or preserve plural theories due to nonidentifiability.

**Failure condition:** Candidates make indistinguishable predictions; open a nonidentifiability Unknown rather than choosing by simplicity alone.

### Months 21–24 — M12: Independent replication and model consolidation

**Question:** Which findings survive independent reproduction and cumulative synthesis?

**Work:** Replicate the most consequential validated effects with independent execution or materially independent environment construction; synthesize all positive, negative, and heterogeneous evidence.

**Evidence gained:** Reproducibility, generalization limits, and final 24-month confidence state.

**Exit decision:** Publish only if desired; scientifically, update supported principles, rejected branches, surviving theories, and the next uncertainty frontier.

**Success condition:** P1 ends the period with fewer mechanisms and stronger scoped knowledge, not merely more experiments.

## 4. Cross-cutting scaling studies

Scaling is scientific only when it tests a hypothesis about behavior. Candidate axes:

- number of tasks and recurrence interval;
- task overlap/interference geometry;
- environment stationarity and change rate;
- memory and compute budget;
- observation noise and partial observability;
- learner capacity;
- duration and delayed evaluation;
- distribution shift severity.

For every scaling study specify the predicted functional form or transition. Plotting performance against size without a discriminating prediction is characterization, not mechanism validation.

## 5. Decision checkpoints

At months 3, 6, 9, 12, 15, 18, 21, and 24, the SOS re-evaluates:

- confidence changes;
- hypotheses to reject/revise/merge;
- scientific debt and blockers;
- information-gain ranking;
- mechanisms that have not repaid complexity debt;
- whether any theory construction is justified.

## 6. Expected scientific outcomes

The roadmap is successful if it produces any combination of:

- well-calibrated measurements;
- clean rejection of ineffective mechanisms;
- validated narrow effects with boundary conditions;
- demonstrations that apparently different mechanisms are equivalent;
- identification of irreducible unknowns;
- a predictive theory that survives a novel test;
- a defensible conclusion that no current mechanism supports a broader intelligence principle.

A truthful negative program is preferable to a complex positive narrative unsupported by evidence.
