# Project P1 Observatory — Scientific Instrument Specification

- **Document type:** Scientific requirements, not software architecture
- **Owner:** P1 Scientific Operating System / Chief Scientist
- **Scientific phase:** Discovery
- **Specification status:** Proposed baseline for engineering translation
- **State date:** 2026-07-28
- **Canonical scientific state:** `science/SKB_RECORDS_v1.0.yaml` (SKB v1.1.0)
- **Current Living Scientific Model:** `science/11_LIVING_SCIENTIFIC_MODEL.md` v1.2.0
- **Governing question:** What is the smallest observation or experiment that would most reduce uncertainty?

---

## Executive scientific ruling

The P1 Observatory must be an **epistemic instrument**: a read-only, provenance-preserving means of connecting computational events to measurements, experiments, evidence, hypotheses, and—only when earned—theories.

Its scientific purpose is not to make P1 look understandable. Its purpose is to reveal where P1 is understood, where it is not understood, and which observation or intervention would discriminate among competing explanations.

The Observatory must maintain five hard separations:

1. **recorded state vs reconstructed state**;
2. **direct measurement vs derived statistic**;
3. **exploratory pattern vs validated finding**;
4. **correlation vs intervention-supported causal evidence**;
5. **implementation activity vs scientific evidence**.

A visual object is admissible only when it has:

- an actual source record or declared derivation;
- a stable identity or explicit ephemeral identity;
- units, scope, and time basis;
- provenance to a run, configuration, code state, seeds, and experiment condition;
- a missingness state when unavailable;
- a declared epistemic status;
- a route back to the raw evidence from which it was rendered.

If P1 does not emit a scientific state needed by a view, the correct visualization is **“not observed”**, not an inferred animation.

The current M1 apparatus supports real run, step, probe, metric, compute, manifest, and scientific-record observables. It does **not** yet supply general neuron, connection, attention, replay-item, memory-content-history, or causal-trace records. Those views are therefore scientifically specified here but must remain unavailable until their corresponding records exist and pass non-interference and validity tests.

---

# 1. Scientific objectives

## 1.1 Primary objectives

The Observatory shall enable scientists to:

1. **Locate the computational origin of a measured outcome.** Move from an experiment-level effect to the conditions, runs, events, subsystems, and state transitions that produced it.
2. **Test mechanistic explanations.** Determine whether a proposed mechanism occurred, whether it preceded the outcome, whether matched controls isolate it, and whether alternatives remain viable.
3. **Expose treatment operability.** Verify that an intended intervention actually activated and produced separation before interpreting outcomes. E0’s zero-growth execution is the canonical warning.
4. **Separate competence, retention, and adaptation.** Prevent weak initial learning from appearing as good retention and prevent non-adaptation from appearing as stability.
5. **Audit replay as three distinct objects:** storage, timing/budget, and selected content.
6. **Observe learning at multiple scales.** Trace changes from individual updates through units/clusters/subsystems to experiment-level outcomes without presuming that scale aggregation preserves meaning.
7. **Detect emergent organization without mistaking injection for emergence.** Compare learned organization with initialization, designer structure, shuffled references, and capacity-matched controls.
8. **Measure uncertainty honestly.** Display empirical calibration, missing evidence, and competing explanations rather than converting confidence labels into truth.
9. **Diagnose scientific and engineering failure.** Distinguish invalid experiment, absent treatment, corrupted artifact, resource mismatch, numerical failure, model failure, and hypothesis failure.
10. **Make evidence cumulative.** Connect every completed experiment to observations, evidence relations, Decisions, hypothesis/mechanism updates, assumptions, Unknowns, debt, roadmap priority, and the Living Scientific Model.
11. **Support scale without surrendering traceability.** Permit scientific navigation from millions of units to exact events while disclosing aggregation, sampling, and omitted mass.
12. **Protect computation from observation.** Establish that enabling Observatory collection does not alter trajectory, randomness, update order, resource allocation, or decision-relevant outputs.

## 1.2 Non-objectives

The Observatory shall not:

- anthropomorphize internal activity;
- label activity as “thought,” “understanding,” “attention,” “memory,” or “emergence” without an operational definition;
- infer causation from salience, sequence, correlation, or visual proximity;
- use layout, color, motion, or density as evidence;
- present aggregate smoothness as unit-level stability;
- hide negative, null, invalid, or missing outcomes;
- rank runs by a single “intelligence score”;
- authorize theory claims from exploratory observations;
- modify model state, replay decisions, seeds, timing, or experiment conditions;
- substitute visual plausibility for registered scientific state.

## 1.3 Success condition

A scientist using the Observatory should be able to answer, with evidence links:

> What changed, when did it change, where did it change, under which condition, relative to which control, with what uncertainty, and what scientific decision follows?

---

# 2. Observability principles

## 2.1 Scientific fidelity

Every displayed mark must correspond to one of four admissible classes:

| Class | Meaning | Display rule |
|---|---|---|
| **D — Direct** | Value emitted as immutable computational or experimental state | Show source field, object ID, time, and units |
| **R — Reconstructed** | Deterministically reconstructed from complete recorded state | Show reconstruction method/version and completeness test |
| **V — Derived** | Statistic computed from D/R records | Show formula, inputs, aggregation, uncertainty, and version |
| **A — Annotation** | Human scientific interpretation or registered metadata | Visually separate from computation; link author/time/status |

Anything outside these classes is not displayable as scientific state.

## 2.2 Non-interference

Observation must be scientifically passive:

- observers cannot access mutable model, memory, environment, or gate state except through declared read-only records;
- collection must not consume random numbers;
- collection must not reorder events or updates;
- collection must not change control flow or compute budgets;
- disabled and enabled collection must produce identical decision-relevant outputs under a frozen deterministic config;
- overhead must be measured; timing-sensitive experiments must declare whether observation overhead is admissible;
- dropped records must be explicit and quantified.

P1 already establishes a useful precedent: metrics are write-only observers over immutable `StepRecord` and `ProbeRecord` objects. Observatory state collection must meet at least this standard.

## 2.3 Provenance before interpretation

Every view must expose:

- run ID and config hash;
- code commit and clean/dirty state;
- frozen-rig or model version;
- full seed decomposition;
- component identities;
- benchmark/environment identity;
- artifact inventory/hash status;
- execution completeness/truncation/failure;
- experiment, condition, and control assignment;
- Discovery/Validation/Publication stage;
- eligibility for exploratory or confirmatory use.

A visually compelling result from a dirty, untracked, truncated, corrupted, or unmatched run remains ineligible evidence.

## 2.4 Measurement before visualization

No visualization may be accepted until its underlying construct has:

1. an operational definition;
2. units and directionality;
3. a source schema;
4. positive and negative controls where applicable;
5. known failure modes;
6. missingness semantics;
7. a validity status;
8. an explicit claim scope.

## 2.5 Multiscale truth preservation

Aggregation is a scientific transformation, not a display convenience. Every aggregate must declare:

- membership rule;
- aggregation function;
- weighting;
- time window;
- included and excluded mass;
- sampling method and seed if sampled;
- variance or distribution, not only mean;
- whether drill-down can recover constituents;
- whether the aggregate can conceal sign reversals or subpopulation failure.

## 2.6 Stable identity and lineage

Objects that persist through time require stable IDs. Objects that split, merge, are created, or are deleted require lineage events. Index position alone is not identity. Cluster labels generated independently at each checkpoint must not be shown as the same cluster unless alignment evidence supports continuity.

## 2.7 Honest absence

Unavailable state must be rendered as one of:

- not emitted;
- not recorded;
- recording incomplete;
- not reconstructable;
- construct undefined;
- construct invalid;
- insufficient resolution;
- access intentionally blinded;
- run ineligible;
- not applicable.

Zero, null, absence, and missingness must never be conflated.

## 2.8 Progressive rigor

- **Discovery views** optimize rapid discrimination and display exploratory labels prominently.
- **Validation views** require prespecified outcomes, controls, uncertainty, adequate independent replication, and confirmatory separation when material.
- **Publication views** preserve validated results and complete communication; they do not retroactively validate discovery.

## 2.9 Scale discipline

For thousands to millions of units, the Observatory must use scientifically declared levels of detail. It must not imply that all objects were rendered when only a subset was sampled. Density views must retain counts and omitted mass; drill-down must follow stable identities; population summaries must show heterogeneity and outliers.

## 2.10 Counterfactual discipline

Counterfactuals are displayable only when generated by an actual intervention, valid replay from a checkpoint under a changed registered condition, or a named model-based estimator with assumptions. A hypothetical path drawn by the interface is not a causal observable.

---

# 3. Zoom levels and object ontology

The zoom ladder is semantic, not merely geometric.

| Level | Scientific object | Minimum actual state | Questions enabled | Prohibited substitution |
|---|---|---|---|---|
| **System** | Complete P1 run or synchronized population of runs | run status, manifests, global compute, benchmark, component set | Is the system operating, admissible, stable, and within scope? | A decorative “brain” overview |
| **Subsystem** | Model, memory, gate, replay selector, environment, benchmark, metric | component identity, inputs/outputs, state summaries, event counts | Which functional component changed or failed? | Arbitrary screen regions called modules |
| **Cluster** | Recorded or reproducibly derived group of units/connections/items/events | members, rule/version, stability, coverage | Is behavior localized to a population? | Layout-based proximity or unlabeled clustering |
| **Neuron** | Actual computational unit in a model that defines such units | stable unit ID, state/activation/update records, type | Which unit participates, changes, saturates, or fails? | Treating table cells or features as neurons without declaration |
| **Connection** | Actual parameterized relation between units | source/target IDs, parameter, update, status | Which interaction changed and with what consequence? | Decorative edges or inferred influence |
| **Event** | Immutable occurrence at a specific logical time | event ID, time, kind, actor, inputs/outputs, causal parents if recorded | What exactly happened? | Interpolated animation frames |
| **History** | Ordered state/event trajectory | checkpoint lineage, completeness, time basis | How did the state evolve and when did divergence begin? | Smoothed curve without raw support |
| **Experiment** | Registered protocol, conditions, executions, outcomes, evidence | experiment ID, protocol version, conditions, seeds, controls, analysis | Does a contrast change belief? | Side-by-side runs without matched design |
| **Theory** | Registered explanatory model and evidence graph | theory/hypothesis records, relations, alternatives, decisions | Which explanations survive and what test separates them? | A mechanism illustration presented as theory |

### 3.1 Cross-level navigation rule

Any aggregate claim must support a trace path:

**Theory → hypothesis → evidence relation → experiment → condition → run → history → event → subsystem → unit/connection**, stopping honestly wherever lower-resolution state does not exist.

The reverse path must also work:

**Event/unit change → run outcome → condition contrast → evidence relation → affected hypothesis/Unknown/Decision**.

---

# 4. Cognitive observables

“Cognitive” is used only for operationally defined performance and internal process variables, not anthropomorphic interpretation.

## 4.1 Required observables

1. **Prequential predictive loss** by time, task/regime, condition, and seed.
2. **Oracle-relative excess loss** where a valid oracle exists.
3. **Initial mastery** immediately after learning each task.
4. **Final retained competence** for each prior task.
5. **Degradation/backward transfer** relative to each task’s own learned state.
6. **Adaptation cost/plasticity** after regime changes.
7. **Current-task performance** alongside retention.
8. **Prediction/confidence calibration** only where predictions and adjudicated outcomes exist.
9. **Error composition** by task, context class, and prespecified strata.
10. **Behavioral invariance/transfer** across prespecified perturbations or environment classes.

## 4.2 Current availability

- `StepRecord.loss`, task, and time are directly available.
- `ProbeRecord.losses`, oracle values, and derived excess are directly/derivatively available.
- `online_loss`, `excess_loss`, and `plasticity` metrics already implement several required summaries.
- The legacy `retention` scalar is present for comparability but is scientifically ineligible as a primary outcome because it can reward weak initial learning.
- General confidence calibration records are not yet part of the M1 step/probe schema.

---

# 5. Experimental observables

## 5.1 Protocol identity

Display the registered experiment ID, protocol version/hash, hypothesis target, phase, condition definitions, control logic, outcome hierarchy, stopping rule, exclusion rule, and preregistration status.

## 5.2 Execution identity

For every execution display:

- seed and independent seed substreams;
- code/config/data/benchmark identity;
- run status and completeness;
- treatment assignment;
- treatment-operability status;
- compute and resource use;
- exclusions with reasons;
- deviations from protocol;
- artifact integrity;
- analysis version;
- evidence eligibility.

## 5.3 Contrast state

For every scientific comparison display:

- estimand;
- unit of inference;
- pairing or blocking structure;
- sample size and independent replication count;
- condition means/distributions and paired contrasts;
- uncertainty interval/effect size;
- SESOI/equivalence margin when prespecified;
- multiplicity family;
- guardrails;
- missing/excluded runs;
- sensitivity analyses;
- conclusion scope and Decision status.

## 5.4 Treatment-operability state

An experiment cannot answer its hypothesis if the intervention did not occur. Operability views must show trigger opportunities, activations, magnitude of treatment separation, dose distribution, and whether positive/negative controls behaved as required.

---

# 6. Memory observables

Memory must be separated into **stored content**, **retention behavior**, and **use of stored content**.

## 6.1 Storage observables

- capacity, occupancy, and `n_seen`;
- item identity and provenance where privacy/scope permit;
- item age and insertion time;
- task/regime/source distribution;
- replacement/eviction events and reasons;
- sampling eligibility and selection probability if known;
- duplication rate;
- coverage of historical tasks/contexts;
- compression or abstraction state only when explicitly represented;
- memory lineage across checkpoints.

## 6.2 Retention observables

- learned performance per task;
- final oracle-relative performance per task;
- degradation per task;
- worst-case retained competence;
- retention trajectory across checkpoints;
- reacquisition/adaptation after return;
- uncertainty and seed variation.

## 6.3 Current availability

Current M1 emits buffer size per step and allows a read-only memory snapshot at runtime, but standard artifacts do not record item-level memory history, eviction events, selection probabilities, or snapshots. Therefore only occupancy history is presently displayable from standard run artifacts. Item-level memory views remain unavailable until actual records exist.

---

# 7. Replay observables

Replay is not one mechanism. The Observatory must separately expose:

1. **availability:** what historical items were eligible;
2. **timing:** when the gate requested replay;
3. **requested budget:** how many replay updates were requested;
4. **realized budget:** how many were actually performed;
5. **shortfall:** requested minus realized;
6. **content:** which stored observations were selected;
7. **weight/dose:** update weight per replay item;
8. **provenance:** source task, event, age, and memory location;
9. **immediate-sample reuse:** whether the latest observation entered replay;
10. **outcome association:** subsequent loss/adaptation/retention changes, labeled correlational unless intervened;
11. **matched-control equivalence:** equality of counts, batch profiles, update totals, and compute;
12. **boundary concentration:** replay timing relative to task switches.

## 7.1 Current availability

Directly available now: gate fired, realized replay count, buffer size, updates, aggregate gate activity, boundary-fire fraction, total replay updates, update multiplier, and manifest-level replay shortfall.

Not currently recorded in standard step artifacts: requested `k`, identity of selected replay items, their source task/age, item weights, or causal effect of individual replay events. These must not be fabricated from the memory contents.

---

# 8. Learning observables

Learning observables describe actual update processes and performance consequences.

## 8.1 Required observables

- prediction before learning;
- target and prequential loss;
- online update event;
- replay update events and weights;
- parameter/state change magnitude by unit, connection, cluster, and subsystem where exposed;
- gradient/update norm or equivalent model-specific learning quantity where it exists;
- saturation, dead-unit, exploding, vanishing, and numerical-instability indicators;
- learning-rate or plasticity state if computationally represented;
- cumulative online and replay updates;
- adaptation curves after switches;
- learning-versus-forgetting trade-off by task and seed;
- divergence point between conditions.

## 8.2 Interpretation constraint

A parameter change is not evidence of useful learning. It becomes scientifically meaningful only when linked to a preregistered behavioral outcome or a validated intermediate construct.

## 8.3 Current availability

Current M1 directly records prequential loss and counts of updates. The model exposes `state_dict`, but standard execution does not emit per-update deltas. General unit/connection learning views are therefore not currently available.

---

# 9. Structural observables

“Structure” must refer to actual topology, parameter organization, capacity, or reproducibly defined grouping.

## 9.1 Required observables

- unit and connection inventories by type;
- stable IDs and birth/death times;
- topology and parameter values;
- capacity allocated and used;
- growth/pruning/split/merge events;
- connectivity distribution and isolated components;
- reproducibly derived clusters with membership and algorithm version;
- cluster persistence, split, merge, and turnover;
- specialization by task/context measured against controls;
- initialization structure versus learned change;
- injected/design-imposed constraints;
- shuffled and capacity-matched references;
- structure-performance relation across interventions.

## 9.2 Current availability

The current count-model assay has an actual count-table state and an E0 line concerning capacity growth, but the standard Observatory source records do not yet define universal neuron/connection IDs or structural events. It would be scientifically false to render a neural graph for the current model. For count models, valid structural objects would be declared table entries, contexts, targets, and their parameters—not invented neurons.

---

# 10. Attention observables

Attention is displayable only for a model that computes and records an attention-like allocation.

## 10.1 Required observables

- source and destination object IDs;
- raw score, normalization rule, and normalized weight;
- mask/eligibility set;
- head/channel/layer identity where applicable;
- time, context, and query identity;
- entropy/concentration and mass by prespecified group;
- stability across perturbations and seeds;
- relation to output changes under intervention;
- competing explanation from saliency, scale, or masking artifacts.

## 10.2 Scientific distinction

Attention weight is not automatically causal importance, explanation, or human-like focus. Causal claims require interventions such as masking, replacement, or controlled perturbation with outcome measurement.

## 10.3 Current availability

No general attention state exists in the current M1/v0 scientific record. The attention view must display **construct not present / not observed**. Gate activity must not be relabeled as attention.

---

# 11. Emergence observables

Emergence requires evidence that a capability or structure was absent at initialization, arose through learning, and exceeds appropriate references without designer injection.

## 11.1 Required observables

- preregistered emergent property and measurement;
- baseline at initialization;
- time of onset with uncertainty;
- persistence after onset;
- treatment activation and dose;
- fixed-capacity control;
- capacity-matched error-decoupled control;
- shuffled-input/null reference;
- designer-injection audit;
- performance gain and structural change jointly;
- replication across independent seeds;
- robustness to analysis thresholds;
- boundary conditions and failures;
- generalization only across prespecified environment classes.

## 11.2 Current state

E0 recorded zero growth events; therefore H* was not tested. The current Observatory must show **treatment non-operability**, not an emergence curve. The registered emergence statistic `M = NMI(learned,true) - NMI(learned,shuffled)` is displayable only when its inputs, alignment, null construction, and treatment activation are validly recorded.

---

# 12. Failure observables

Failures must be classified before they are visualized.

## 12.1 Failure taxonomy

1. **Apparatus failure:** crash, incomplete run, corrupted artifact, missing required field.
2. **Provenance failure:** dirty/untracked code, unknown data/config identity, hash mismatch.
3. **Measurement failure:** invalid construct, unavailable metric, insensitive gate, missing oracle.
4. **Treatment failure:** intended intervention absent, insufficient dose, control contamination.
5. **Design failure:** unmatched resources, seed confounding, leakage, invalid unit of inference.
6. **Numerical failure:** NaN/Inf, overflow, underflow, exploding or frozen state.
7. **Scale failure:** dropped events, incomplete coverage, sampling bias, aggregation overflow.
8. **Behavioral failure:** poor outcome under a valid measurement.
9. **Mechanism failure:** valid intervention fails within scope.
10. **Hypothesis failure:** valid evidence contradicts a falsifiable prediction within scope.
11. **Theory failure:** discriminating prediction fails or an alternative explains evidence better.
12. **Human-interpretation failure:** exploratory or correlational pattern is mislabeled as causal/validated.

## 12.2 First-divergence requirement

For matched deterministic or paired runs, the instrument should identify the earliest recorded divergence in input, component state, event, resource use, or output. If resolution is insufficient, it must report a divergence interval rather than invent an exact cause.

---

# 13. Validation observables

Validation views determine whether an observation is fit for a claim.

## 13.1 Required validation dimensions

- schema validity and completeness;
- source and artifact integrity;
- deterministic repeatability where expected;
- observer non-interference;
- construct validity;
- metric direction, units, and eligibility;
- positive/negative-control sensitivity;
- treatment operability;
- control fidelity and resource matching;
- randomization/pairing integrity;
- independent seed count and uncertainty;
- preregistration integrity;
- exclusion and stopping-rule adherence;
- confirmation-seed separation;
- robustness/sensitivity analysis;
- transfer scope;
- evidence-graph completeness;
- post-experiment state propagation completeness.

## 13.2 Evidence eligibility states

Every result must have one explicit state:

- engineering-only;
- exploratory-admissible;
- validation-admissible;
- confirmatory-admissible;
- publication-ready;
- invalid;
- indeterminate;
- superseded.

The current M1 working apparatus is engineering-conformant locally but not confirmatory-admissible because immutable provenance, live-surface gates, and clean repeated-output identity are not established.

---

# 14. Causal observables

## 14.1 Causal object

A causal view must begin with a declared estimand, for example:

> Effect of surprise-timed replay versus equal-budget random-timed replay on final prior-task oracle-relative excess loss, paired by environment seed.

## 14.2 Required causal state

- treatment and control definitions;
- intervention assignment and compliance;
- causal unit and unit of inference;
- temporal ordering;
- treatment dose and realized separation;
- matched resources and exposure;
- confound register;
- outcome and guardrails;
- paired contrasts and uncertainty;
- alternative mechanisms;
- mediation quantities only when interventionally identified;
- scope and transport assumptions;
- Decision linked to the causal result.

## 14.3 Prohibitions

Do not draw causal arrows from:

- temporal precedence alone;
- correlation between activation and outcome;
- high attention weight;
- replay followed by lower loss in the same run;
- cluster membership;
- a single seed;
- an unmatched ablation;
- a retrospective path chosen after seeing the outcome.

---

# 15. Canonical scientific visualizations

Each visualization below is a **scientific plate**. A plate is allowed only when its required source state exists. The five mandated questions are answered for every plate.

## 15.1 System, experiment, and history plates

| ID and visualization | Why should it exist? | Scientific question answered | Hypothesis it can validate | Engineering problem diagnosed | Decision made easier |
|---|---|---|---|---|---|
| **V01 — Run Provenance & Eligibility Plate**: manifest, config hash, commit state, seeds, artifact integrity, status, truncation, eligibility | Prevents inadmissible execution from being interpreted as evidence | Can this run count as evidence at the intended rigor stage? | No mechanism hypothesis directly; validates the apparatus/reproducibility assumption | Dirty/untracked code, wrong config, missing artifacts, truncation, seed mismatch | Admit, quarantine, rerun, or reject the run |
| **V02 — System Event Chronology**: exact event sequence with regime boundaries, probes, gates, failures, structural events | Establishes what happened and in what order | When did behavior or state change, and what recorded event preceded it? | Any hypothesis with a temporal prediction, subject to controls | Ordering bugs, missing events, stalled components, incorrect boundaries | Choose the interval/object for deeper diagnosis |
| **V03 — First-Divergence Comparator**: two aligned histories with earliest differing record and divergence interval | Converts reproducibility or condition differences into a localized question | Where do nominally identical or matched runs first cease to agree? | Deterministic-repeatability hypothesis; some intervention hypotheses when pre-intervention identity is required | Seed leakage, nondeterminism, config drift, update-order divergence | Block evidence, isolate defect, or accept treatment separation |
| **V04 — Experiment Contrast Plate**: condition distributions, paired contrasts, uncertainty, SESOI, guardrails, exclusions | Makes the experimental estimand and uncertainty primary | Does the prespecified treatment change the outcome relative to the correct control? | The experiment’s registered hypothesis within scope | Missing seeds, imbalance, failed runs, analysis mismatch | Accept/reject/revise hypothesis, continue/stop line |
| **V05 — Treatment Operability Plate**: opportunities, activation count, dose, separation, positive/negative controls | Prevents absent treatment from masquerading as null evidence | Did the intervention occur with sufficient and interpretable separation? | Operability subhypothesis required by any mechanism test | Trigger unit mismatch, threshold error, dead code, control contamination | Run the main test, recalibrate treatment, or stop |
| **V06 — Resource-Matching Plate**: online/replay updates, requested/realized replay, compute, exposure, decay applications | Reveals whether an ablation isolates mechanism or merely gives more work/resources | Were compared conditions equal on all resources outside the intended intervention? | Replay-content or replay-timing hypotheses | Under-spent controls, extra updates, budget shortfall, compute drift | Permit causal interpretation or redesign the control |
| **V07 — Scientific State Transaction Plate**: result → observations → evidence → Decision → affected records | Ensures a completed run changes scientific memory consistently | What did this experiment change in P1’s knowledge, and what remains unchanged? | Validates no computational hypothesis; validates evidence propagation completeness | Orphan evidence, stale statuses, missing decision links | Close the experiment, reopen it, or repair the scientific record |
| **V08 — Evidence–Hypothesis–Theory Graph**: typed evidence relations, assumptions, Unknowns, alternatives, Decisions | Reveals support, contradiction, dependence, and gaps without narrative authority | Which claims depend on which evidence and shared assumptions? | Theory or hypothesis integration only after required evidence exists | Broken references, circular support, shared-evidence dependence | Prioritize separating experiment; admit/challenge/reject theory |

## 15.2 Cognitive and learning plates

| ID and visualization | Why should it exist? | Scientific question answered | Hypothesis it can validate | Engineering problem diagnosed | Decision made easier |
|---|---|---|---|---|---|
| **V09 — Prequential Loss History**: raw/aggregated loss by task, regime, seed, condition, with boundaries | Shows actual predictive performance before learning each target | When and under which regimes does predictive error rise, fall, or diverge? | Learning/adaptation hypotheses; not mechanism causality alone | Incorrect task order, non-learning, loss spikes, numerical instability | Select failure interval; assess whether learning occurred |
| **V10 — Mastery–Retention Matrix**: learned excess, final excess, degradation, worst task, uncertainty | Separates learning a task from retaining it | Was a task learned initially, and how much competence remained later? | Resource-matched replay benefit hypothesis | Probe/oracle mismatch, indexing error, catastrophic per-task loss hidden by means | Continue replay line, revise outcome, investigate specific task |
| **V11 — Plasticity–Retention Frontier**: adaptation cost versus retained competence per condition/seed | Prevents “retention by refusing to learn” | Does improved retention preserve acceptable adaptation to current tasks? | Stability–plasticity mechanism hypotheses | Frozen learning, excessive regularization/replay, task-specific collapse | Accept mechanism, reject trade-off, set guardrail |
| **V12 — Calibration/Reliability Plate**: predicted confidence versus empirical correctness by prespecified stratum | Tests whether uncertainty labels mean what they claim | Are confidence outputs calibrated and honest on the target distribution? | Retrieval uncertainty calibration H1/HYP-2026-0002 | Confidence inversion, overconfidence, stratum failure, missing abstention | Deploy, recalibrate, restrict scope, or reject calibration claim |
| **V13 — Learning Update Field**: actual state deltas by time/unit/connection/cluster with outcome linkage | Locates where computational learning occurred | Which model states changed during successful or failed adaptation? | Model-specific update/localization hypotheses after controls | Dead units, exploding updates, frozen parameters, unintended update paths | Target ablation or instrumentation; revise mechanism model |
| **V14 — Condition Divergence Trajectory**: paired outcome/state distance from common pre-intervention history | Shows when an intervention begins to matter | When does treatment separation emerge, persist, or reverse? | Time-resolved predictions of registered interventions | Intervention not applied, delayed effect, state desynchronization | Choose probe schedule; retain or simplify mechanism |

## 15.3 Memory and replay plates

| ID and visualization | Why should it exist? | Scientific question answered | Hypothesis it can validate | Engineering problem diagnosed | Decision made easier |
|---|---|---|---|---|---|
| **V15 — Memory Occupancy & Composition History**: capacity, occupancy, age/task/source distributions, turnover | Makes the available historical substrate explicit | What information was available to replay at each time? | Storage/coverage prerequisites for replay hypotheses | Empty/biased buffer, capacity saturation, task starvation, faulty eviction | Change experimental interpretation or memory condition |
| **V16 — Memory Item Lineage Plate**: actual item insertion, residence, eviction, selection, source event | Traces whether claimed historical information persisted and was used | Did a specific historical carrier survive and participate later? | Historical-carrier dependence HYP-2026-0009; replay-content hypotheses | Identity loss, duplicate items, wrong provenance, premature eviction | Accept carrier test, inspect leak, revise memory policy experiment |
| **V17 — Replay Timing Raster**: gate opportunities/fires, requested and realized dose, switches, loss | Separates timing from content and exposes boundary concentration | Is replay allocated by surprise, by boundary proximity, or effectively always/never? | Surprise-triggered replay allocation HYP-2026-0008 | Threshold misconfiguration, boundary proxy, replay shortfall | Compare against matched random/boundary control or stop timing claim |
| **V18 — Replay Content Provenance Plate**: selected item IDs, source task/age/context, weights, eligibility set | Determines what the replay intervention actually contained | Does historical content, rather than extra updates or current-sample rehearsal, drive the outcome? | Resource-matched historical replay HYP-2026-0007 | Current-item leakage, task imbalance, duplicate selection, wrong filter | Permit content-specific inference or redesign selector/control |
| **V19 — Replay Event Outcome Window**: prespecified before/after outcomes around events, with matched non-events | Supports exploratory localization while guarding against causal overclaim | Are replay events followed by changes beyond matched control windows? | Generates/refines replay hypotheses; validates causality only under randomized event timing | Misaligned timestamps, probe scarcity, event duplication | Decide whether a causal replay experiment is worth running |
| **V20 — Replay Budget Equivalence Plate**: requested/realized distributions and cumulative totals across paired runs | Makes equal-budget control fidelity visible | Did timing/content conditions spend the same replay dose? | Required validity condition for HYP-2026-0007/0008 | Silent under-spend, differing batch sizes, early memory shortage | Accept comparison or invalidate it before outcome analysis |

## 15.4 Structure, neuron, connection, and attention plates

| ID and visualization | Why should it exist? | Scientific question answered | Hypothesis it can validate | Engineering problem diagnosed | Decision made easier |
|---|---|---|---|---|---|
| **V21 — Structural Inventory Plate**: actual unit/connection types, counts, capacity, topology, unobserved regions | Establishes what computational structure truly exists | What are the model’s represented structural objects at this checkpoint? | Structural-capacity hypotheses; no emergence claim alone | Missing units, disconnected components, wrong capacity, serialization loss | Select valid zoom targets; verify intervention target |
| **V22 — Structural Change History**: births, deaths, growth, pruning, splits, merges with lineage | Tests whether structure changed and treatment activated | When, where, and how did capacity/topology change? | Error-gated structure acquisition HYP-2026-0001 after valid controls | Growth never fires, runaway growth, unstable IDs, prune/grow oscillation | Proceed with H* test, recalibrate trigger, or stop |
| **V23 — Cluster Composition & Stability Plate**: membership, derivation version, alignment, turnover, task selectivity | Allows population organization to be studied without treating layout as structure | Are reproducible functional/structural populations forming and persisting? | Cluster-specialization or organization hypotheses | Cluster instability, algorithm sensitivity, label switching, hidden outliers | Define unit-level follow-up or reject cluster interpretation |
| **V24 — Neuron State History**: stable unit’s actual activation/state/update distribution across contexts | Enables precise unit-level diagnosis when the model has neurons | Does a unit acquire selective, stable, or pathological behavior? | Unit-specialization hypotheses with perturbation controls | Dead/saturated/noisy units, state discontinuity, update anomaly | Ablate/perturb in an experiment or deprioritize the unit |
| **V25 — Connection State History**: actual edge parameter, updates, source/target activity, birth/death | Reveals interaction dynamics at the smallest structural relation | Does a specific connection mediate a registered behavior under intervention? | Connection-specific causal hypotheses after edge intervention | Frozen/exploding weights, wrong connectivity, update leakage | Choose edge ablation, verify learning path, revise mechanism |
| **V26 — Attention Allocation Plate**: actual weights/scores/masks by source/destination/head/context | Makes real allocation state inspectable without calling it explanation | Where did the implemented attention operator allocate mass? | Attention-allocation predictions; not causal importance alone | Mask error, normalization failure, collapsed heads, diffuse/saturated weights | Design masking intervention; diagnose operator |
| **V27 — Attention Intervention Plate**: outcome under prespecified mask/replace/permute interventions | Separates attention correlation from causal contribution | Does changing attended content change the outcome as predicted? | Causal attention hypotheses | Intervention leakage, invalid mask, compensatory path | Accept/reject causal role; simplify model |

## 15.5 Emergence, failure, validation, and causal plates

| ID and visualization | Why should it exist? | Scientific question answered | Hypothesis it can validate | Engineering problem diagnosed | Decision made easier |
|---|---|---|---|---|---|
| **V28 — Emergence Onset & Null Reference Plate**: baseline, onset, persistence, shuffled/null, controls, seed uncertainty | Prevents post hoc “emergence” labels based on attractive trajectories | Did a preregistered property arise through learning beyond null and injected structure? | HYP-2026-0001 or future emergence hypotheses | Misaligned NMI, threshold artifact, absent treatment, seed collapse | Support/reject/revise emergence claim; repeat or terminate line |
| **V29 — Designer Injection Audit Plate**: initial constraints, encoded labels/rules, information available at initialization | Exposes whether the claimed learned structure was supplied by design | Could the observed capability be explained by injected structure? | Identifiability assumption behind emergence hypotheses | Leakage, seeded semantics, hard-coded mapping, benchmark contamination | Reject emergence interpretation or redesign experiment |
| **V30 — Failure Localization Plate**: typed failure, first occurrence, affected objects, propagation, eligibility consequence | Distinguishes apparatus, measurement, treatment, mechanism, and hypothesis failure | What failed, at which level, and what claims are invalidated? | Negative tests of apparatus/controls; hypothesis failure only for valid experiments | Crash, NaN, corrupt artifact, missing event, dead treatment | Repair, rerun, preserve negative result, or stop research line |
| **V31 — Validation Matrix Plate**: rows=claims/metrics/conditions; columns=provenance, construct, controls, inference, replication | Makes claim readiness auditable instead of rhetorical | Which exact requirement blocks this claim from advancing? | Validates evidence admissibility, not a cognitive mechanism | Missing gate, stale check, unavailable metric, confirmation leakage | Promote, hold, or block claim; prioritize minimum missing test |
| **V32 — Causal Contrast Plate**: estimand, DAG/assumptions, intervention compliance, paired effects, guardrails | Makes causal identification conditions explicit | What effect is identified, under which assumptions, relative to which alternative? | Registered causal mechanism hypothesis | Confounding, noncompliance, imbalance, post-treatment conditioning | Accept scoped causal interpretation or demand a separating control |
| **V33 — Alternative Explanations Plate**: prediction table for competing mechanisms against observed outcomes | Forces evidence to discriminate, not merely fit one story | Which explanations are ruled out, survive, or make the same prediction? | Any mechanism/theory hypothesis with named alternatives | Missing control, nonidentifiability, circular analysis | Choose the smallest discriminating experiment |
| **V34 — Scale Coverage & Sampling Plate**: total objects, rendered/aggregated/sampled counts, omitted mass, sampling rule | Prevents million-unit views from implying complete inspection | Is the displayed pattern representative of the actual system state? | Population-level hypotheses subject to sampling validity | Dropped telemetry, biased sampling, incomplete shards, aggregation overflow | Trust, resample, narrow scope, or block population claim |
| **V35 — Negative Results & Boundary Conditions Plate**: failed predictions, nulls, invalid runs, scope, preserved evidence | Keeps scientific memory from selecting only successes | Where does a mechanism not work, and was the test capable of detecting it? | Rejects or bounds hypotheses within tested scope | Repeated known failure, insensitive test, accidental rerun | Terminate, narrow, revise, or archive a research line |
| **V36 — Theory Discrimination Plate**: theory predictions across existing and proposed tests, evidence independence | Makes theory status depend on risky predictions and alternatives | Which theory best explains evidence and what untouched outcome separates them? | Candidate/provisional theory predictions | Shared evidence, ad hoc rescue, untestable clauses | Admit candidate, challenge, revise, supersede, or reject theory |

### 15.6 Current-state admissibility of plates

| Availability | Plates |
|---|---|
| **Currently supportable from standard M1/SKB artifacts** | V01, V02 at milestone resolution, V04 when multi-run analyses exist, V05 for gate/growth counts if emitted, V06, V07, V08, V09, V10, V11, V17 at current step resolution, V20, V30, V31, V33, V35, V36 |
| **Partially supportable; missing state must be explicit** | V03, V12, V14, V15, V19, V28, V29, V32, V34 |
| **Not currently supportable from standard artifacts** | V13, V16, V18 item-level detail, V21–V27 general unit/connection/attention views |

This table is not permission to infer missing fields. It is a scientific instrumentation gap register.

---

# 16. Scientific overlays

Overlays modify interpretation, never underlying state.

1. **Provenance overlay:** clean/dirty, commit, config hash, seeds, inventory integrity.
2. **Rigor-stage overlay:** Discovery, Validation, Publication.
3. **Evidence-eligibility overlay:** engineering-only through confirmatory-admissible.
4. **Directness overlay:** D, R, V, or A class for every mark.
5. **Construct-validity overlay:** validated, provisional, known-defective, unavailable.
6. **Treatment overlay:** assignment, opportunity, activation, realized dose, compliance.
7. **Control overlay:** control identity and which confound it removes.
8. **Resource overlay:** updates, compute, replay dose, exposure, decay, wall/process time.
9. **Uncertainty overlay:** interval/distribution, independent n, pairing, missingness.
10. **Alternative-explanation overlay:** named surviving explanations and required discriminators.
11. **Intervention overlay:** observed, randomized, ablated, masked, perturbed, or merely correlated.
12. **Temporal overlay:** logical step, checkpoint, regime boundary, wall time; never silently mixed.
13. **Scale overlay:** total population, aggregation level, sample count, omitted mass.
14. **Data-quality overlay:** dropped/incomplete/late/corrupt records and affected time ranges.
15. **Blinding overlay:** condition labels hidden/revealed and reveal time.
16. **Decision overlay:** current Decision, reversibility, blockers, supersession lineage.
17. **Negative-knowledge overlay:** known failures and boundaries relevant to the selected object.
18. **Scientific-debt overlay:** debt IDs, severity, blocked claims, discharge evidence needed.

No overlay may recolor a result as “good” or “bad” without a prespecified direction and threshold. Color must encode registered state, not emotional salience.

---

# 17. Experiment workflow

The Observatory shall support the following scientific workflow without becoming the experiment controller.

## 17.1 Before execution

1. Select a registered target Unknown or hypothesis.
2. Display priority, competing explanations, and existing evidence.
3. State the belief-changing outcome and non-informative outcome.
4. Specify the estimand and unit of inference.
5. Attach protocol/preregistration, conditions, controls, metrics, guardrails, exclusions, and stopping rules.
6. Run an **observability readiness check**: every decision-bearing variable must have an actual source and validity state.
7. Run an **apparatus admissibility check**: clean identity, live-surface verification, deterministic expectations, evidence eligibility.
8. Where applicable, verify treatment operability with positive/negative controls before the main contrast.

## 17.2 During execution

9. Show execution status, provenance, completeness, resource use, and failure events.
10. Do not display outcome-derived treatment labels in blinded confirmatory work.
11. Do not permit live exploratory inspection to alter a preregistered confirmatory stopping rule.
12. Record deviations and missingness immediately.
13. Preserve raw immutable records before derived views.

## 17.3 After execution

14. Validate integrity and eligibility before outcome interpretation.
15. Verify treatment operability and control/resource fidelity.
16. Compute prespecified metrics and uncertainty.
17. Compare alternatives and conduct declared sensitivity analyses.
18. Classify the result: valid support, valid opposition, valid null/indeterminate, or invalid.
19. Create observations and typed evidence relations.
20. Record a Scientific Decision: accept within scope, reject, revise, split, merge, archive, or no status change.
21. Update dependent hypotheses, mechanisms, assumptions, Unknowns, debt, roadmap, and Living Scientific Model.
22. Preserve negative and ambiguous results.
23. Expose the complete state transaction in V07.

A result is not complete until steps 14–23 are resolved.

---

# 18. Research workflows

## 18.1 Apparatus and reproducibility workflow

- Start at V01.
- Compare isolated repeats with V03.
- Inspect failures through V30.
- Use V31 to identify the minimum missing gate.
- Decision: permit Discovery evidence collection, continue blocking, or quarantine apparatus.

This is the immediate M1 readiness workflow.

## 18.2 Retention and continual-learning workflow

- Establish initial mastery and final excess with V10.
- Check adaptation guardrail with V11.
- Inspect task/regime history with V09.
- Inspect memory substrate with V15.
- Verify replay/resource control with V06 and V20.
- Compare the causal contrast with V04/V32.
- Decision: retain replay line, revise construct, or terminate unsupported mechanism.

## 18.3 Replay timing workflow

- Use V17 to characterize actual timing.
- Test boundary concentration.
- Verify equal realized dose with V20.
- Compare surprise against matched-random and boundary-timed controls in V04/V32.
- Use V33 to distinguish surprise sensitivity from change detection or extra compute.
- Decision: advance timing mechanism to Validation, revise it, or stop.

## 18.4 Replay content workflow

- Verify stored historical availability with V15/V16.
- Trace selected items with V18.
- Exclude current-item rehearsal and resource differences via V06/V20.
- Compare historical, non-historical update-matched, and no-history controls.
- Decision: attribute a scoped effect to historical content or retain only bundled-variant evidence.

## 18.5 Structure acquisition workflow

- Verify growth treatment operability with V05/V22.
- Establish initialization and injection state with V21/V29.
- Compare fixed-capacity, capacity-matched error-decoupled, and shuffled controls.
- Examine onset/persistence with V28.
- Replicate across untouched seeds before any emergence claim.
- Decision: test H*, revise trigger units, or preserve another non-operability result.

## 18.6 Unit/connection mechanism workflow

- Select a population through V23 only if cluster validity is adequate.
- Inspect exact units and edges in V24/V25.
- Form a falsifiable unit/edge hypothesis before intervention.
- Ablate, perturb, or replace the registered object.
- Evaluate behavioral consequences with V04/V32.
- Decision: accept a scoped causal role or reject the localization.

## 18.7 Attention workflow

- Confirm an implemented attention operator exists.
- Inspect allocation with V26 without calling it explanation.
- Test robustness across perturbations/seeds.
- Intervene with V27.
- Compare against masking and scale artifacts.
- Decision: accept a scoped causal contribution, describe allocation only, or reject attention interpretation.

## 18.8 Failure investigation workflow

- Classify the failure in V30.
- Find first divergence with V03.
- Trace to V02 and the relevant subsystem/unit plate.
- Determine eligibility consequences in V01/V31.
- Preserve the result in V35 if scientifically informative.
- Decision: repair/rerun, accept scoped negative result, revise, or terminate.

## 18.9 Theory formation and discrimination workflow

- Begin only after at least two independently supported hypotheses concern related phenomena.
- Use V08 to inspect evidence independence.
- Use V33 to name alternatives.
- Use V36 to compare risky novel predictions.
- Select the smallest untouched discriminating experiment.
- Decision: admit Candidate/Provisional theory, keep pluralism, revise, challenge, reject, or supersede.

## 18.10 Scale workflow

- Start from System/Subsystem summaries.
- Apply V34 before interpreting cluster or unit patterns.
- Compare aggregates with stratified distributions and outliers.
- Drill through stable IDs, not screen position.
- Recompute key findings under alternate valid aggregation/sampling rules.
- Decision: accept population inference, narrow scope, increase coverage, or block the claim.

---

# 19. Human interaction model

## 19.1 Interaction stance

The human is not a spectator watching intelligence. The human is an investigator interrogating evidence.

The primary interaction loop is:

**Question → object → comparison → provenance → alternative explanation → evidence → decision**.

## 19.2 Required interactions

1. **Question-first entry:** begin from a hypothesis, Unknown, failure, experiment, or selected computational object—not a default spectacle.
2. **Semantic zoom:** moving between levels changes the scientific object and declares the aggregation transformation.
3. **Brushing with provenance:** selecting any mark reveals source records, derivation, units, completeness, and eligibility.
4. **Matched comparison:** compare only scientifically compatible runs by default; mismatches are shown before outcomes.
5. **Time alignment:** align by logical step, event, regime boundary, intervention, or checkpoint with the chosen basis visible.
6. **Raw-to-derived trace:** every statistic can reveal constituent records or report why that is impossible.
7. **Alternative-explanation prompt:** a selected pattern shows competing explanations and the control needed to distinguish them.
8. **Annotation as annotation:** scientist notes never appear as computational facts; they carry author, time, status, and links.
9. **Blinding protection:** condition identity and confirmatory outcomes can remain hidden until the registered reveal criterion is met.
10. **Missingness interaction:** unavailable views explain precisely which record or validation is absent.
11. **Failure-first navigation:** errors and invalidity cannot be hidden by filtering to successful runs.
12. **Decision capture:** interpretation culminates in a registered Scientific Decision or explicit “no decision.”

## 19.3 Guardrails against human bias

- default to showing all registered conditions and exclusions;
- distinguish exploratory filters from preregistered strata;
- record post hoc thresholds and selections;
- show effect distributions before ranked highlights;
- show worst-case task/unit/seed alongside means;
- display negative results in the same ontology as positive findings;
- prevent annotations from changing raw data;
- retain prior Decisions and supersession lineage;
- disclose when a view was inspected before confirmatory analysis was frozen.

## 19.4 No control-plane coupling

The Observatory may support preparation and annotation, but it must not silently write to model state, memory, gate thresholds, seeds, treatment assignment, or active run configuration. Any transition from observation to a new experiment must create a new declared protocol/config identity outside the observed run.

---

# 20. Scientific acceptance criteria

The Observatory is scientifically acceptable only when all applicable criteria below pass.

## 20.1 Object fidelity

1. Every displayed object maps to an actual D/R/V/A record class.
2. Every object exposes source, identity, units, time basis, and scope.
3. Missing state is explicit; no interpolation is presented as observation.
4. Neuron, connection, cluster, attention, memory-item, and theory labels are used only when their scientific object definitions are satisfied.

## 20.2 Non-interference

5. Under a frozen deterministic config, Observatory-disabled and Observatory-enabled runs produce identical decision-relevant metrics and normalized artifact hashes.
6. Observation consumes no model/environment/replay random draws.
7. Event collection does not change update order or treatment allocation.
8. Collection overhead and dropped records are measured and disclosed.
9. Timing-sensitive claims are blocked unless observation overhead is demonstrated irrelevant or included in all matched conditions.

## 20.3 Provenance and reproducibility

10. Every run view exposes commit/config/seed/component/benchmark/artifact identity.
11. Dirty/untracked or corrupted runs cannot appear confirmatory-admissible.
12. Reconstructed views identify method/version and pass reconstruction completeness checks.
13. Derived views identify exact inputs, formula, version, aggregation, and missingness.
14. Repeated clean-checkout identity is demonstrated for deterministic Observatory records under an explicit normalization policy.

## 20.4 Measurement validity

15. Each decision-bearing metric has an operational definition, direction, units, scope, validity status, and known failure modes.
16. Metrics requiring an oracle fail visibly when no valid oracle exists.
17. Known-defective metrics such as the legacy retention scalar are marked ineligible for primary inference.
18. Positive and negative controls demonstrate that treatment and validation views can detect known success and known failure.
19. No aggregate is accepted without distribution/heterogeneity and membership/coverage disclosure.

## 20.5 Experimental validity

20. Treatment operability is shown before hypothesis interpretation.
21. Control conditions state which confound they remove.
22. Resource matching is measured from realized—not intended—budgets.
23. Unit of inference, pairing, replication count, uncertainty, exclusions, and guardrails are visible.
24. Exploratory and confirmatory results are visually and semantically distinct.
25. Post hoc choices are recorded and cannot appear preregistered.
26. Non-informative outcomes are distinguished from evidence against a hypothesis.

## 20.6 Causal validity

27. Causal plates require a declared estimand and actual intervention/control records.
28. Correlational paths and attention weights cannot render as causal arrows.
29. Mediation claims require identified intervention logic and assumptions.
30. Alternative explanations and unresolved confounders remain visible.

## 20.7 Scale validity

31. Every large-scale view reports total, rendered, aggregated, sampled, and omitted counts.
32. Sampling rules and seeds are reproducible.
33. Stable IDs preserve drill-down and history across scale levels.
34. Cluster identity changes are represented as split/merge/unaligned events rather than continuity by label.
35. Key population claims survive at least one prespecified aggregation/sampling sensitivity check.
36. Telemetry loss or partial coverage blocks claims outside the observed subset.

## 20.8 Scientific workflow validity

37. Every completed experiment traces through validity, observations, evidence, interpretation, Decision, dependencies, debt, roadmap, and Living Scientific Model.
38. Negative, null, ambiguous, and invalid outcomes remain discoverable.
39. Theory views cannot show “supported” without the Theory Registry’s admission and risky-prediction requirements.
40. Every visualization plate passes a review answering the five questions in Section 15 and is removed if it does not change a scientific or engineering decision.

## 20.9 Current acceptance gate for beginning Observatory-backed science

Before Observatory output can support even durable Discovery evidence, P1 must first satisfy the existing M1 apparatus-admissibility conditions:

- immutable committed apparatus identity;
- clean-checkout verification of the live M1 path;
- valid live-surface artifact/reproducibility gates with known-failure tests;
- machine-enforced exclusion of non-clean confirmatory input;
- isolated repeated-run identity of decision-relevant outputs.

The Observatory must expose these conditions; it cannot compensate for their absence.

---

# 21. Initial scientific priority queue for Observatory instrumentation

This is a scientific priority order, not an implementation plan.

## Priority 0 — Admissibility foundation

1. V01 Run Provenance & Eligibility.
2. V03 First-Divergence Comparator for clean isolated repeats.
3. V30 Failure Localization.
4. V31 Validation Matrix.
5. Non-interference and dropped-record validation.

**Decision enabled:** whether Observatory-backed outputs can enter durable Discovery records.

## Priority 1 — Current highest-value P1 questions

6. V09 Prequential Loss History.
7. V10 Mastery–Retention Matrix.
8. V11 Plasticity–Retention Frontier.
9. V17 Replay Timing Raster, extended to requested budget when recorded.
10. V20 Replay Budget Equivalence.
11. V06 Resource Matching.
12. V04/V32 paired experiment and causal contrasts.

**Decision enabled:** whether surprise timing or historical replay deserves a Validation program.

## Priority 2 — Missing state required for mechanism identification

13. Actual replay-item provenance for V18.
14. Actual memory item lineage for V16.
15. Treatment-operability records for V05/V22.
16. Designer-injection state for V29.
17. Scale coverage records for V34.

**Decision enabled:** whether replay content, carrier dependence, or growth can be causally isolated.

## Priority 3 — Model-dependent deep observability

18. Structural inventories and stable unit/connection IDs.
19. Unit/connection update histories.
20. Attention allocation and intervention state, if future models actually implement attention.
21. Reproducible cluster derivations and lineage.

**Decision enabled:** whether a localized internal mechanism warrants intervention testing.

Do not build Priority 3 merely because it is visually impressive. It becomes necessary only when a registered high-priority hypothesis requires that resolution and no cheaper similarly informative observable exists.

---

# 22. Final scientific doctrine

The Observatory shall not claim to reveal P1’s mind. It shall reveal P1’s **recorded computation, measured behavior, experimental contrasts, evidential limits, and evolving scientific model**.

The central unit of value is not a chart, node, animation, or trace. It is a reduction in uncertainty that changes a scientific decision.

A visualization earns its place only if it lets a scientist do at least one of the following better:

- falsify a hypothesis;
- distinguish mechanisms;
- detect an invalid experiment;
- localize a computational failure;
- verify treatment and control fidelity;
- identify a missing measurement;
- preserve a negative result;
- select the smallest next experiment;
- revise the Living Scientific Model.

Anything else is decoration and does not belong in the P1 Observatory.
