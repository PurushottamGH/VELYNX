# Project P1-v2 — Scientific Constitution for an Observable Adaptive Artificial Nervous System

- **Document type:** Scientific blueprint and hypothesis constitution; not software architecture
- **Owner:** P1 Scientific Operating System / Chief Scientist
- **Status:** Proposed scientific constitution for P1-v2 architecture families
- **Scientific phase:** Pre-Discovery model formation
- **Version:** 0.1.0
- **Date:** 2026-07-28
- **Epistemic warning:** Every mechanism and law in this document is a candidate hypothesis until validated within a declared scope
- **Engineering boundary:** This document specifies scientific meaning, required state, measurements, falsification tests, and decisions. It does not prescribe data structures, services, algorithms, interfaces, deployment, or implementation technique.

---

## Preamble

P1-v2 is not scientifically defined by having nodes called neurons. It earns the description **adaptive artificial nervous system** only if it contains persistent adaptive computational units whose local states, interactions, resource use, lifecycles, population organization, and contributions to system behavior are operationally defined, observable, manipulable, and experimentally distinguishable from simpler alternatives.

“Neuron,” “memory,” “energy,” “attention,” “community,” and “emergence” are not permissions to imitate biology or use biological language. Each is a proposed scientific object. Each must justify its existence by enabling a measurable capability or explanation that a simpler object cannot provide.

The constitution therefore adopts five commitments:

1. **No object without an operational identity.** Every object has a stable or explicitly ephemeral identity, state, boundary, provenance, and observable transitions.
2. **No mechanism without a falsifier.** Implementation does not validate a mechanism.
3. **No biological analogy as evidence.** Biological precedent may suggest a hypothesis, never authorize it.
4. **No hidden cognition.** A claimed internal process must correspond to recorded computational state and intervention-supported consequences.
5. **No complexity without earned necessity.** The null model for every new object is deletion, freezing, randomization, or replacement by a simpler alternative.

The scientific objective is not to build the most brain-like system. It is to discover the smallest set of computational principles sufficient for persistent, efficient, recoverable, and generalizable adaptation.

---

# Part I — Constitutional principles

## Article 1 — Scientific mission

P1-v2 exists to test whether a population of locally adaptive, resource-bounded computational units can self-organize into persistent functional structure that improves prediction and adaptation across changing environments without relying on hidden designer injection.

The mission decomposes into five questions:

1. Can local units acquire useful specialization?
2. Can populations retain and reuse information without preventing new learning?
3. Can structure grow, reorganize, become dormant, and be removed under observable laws?
4. Can local interactions produce system-level functions that survive controlled disruption and transfer?
5. Can every accepted explanation be traced from behavior through experiment to actual unit, connection, event, and history state?

## Article 2 — Scientific status of this blueprint

This blueprint defines:

- a **reference ontology** for forming hypotheses;
- a set of **candidate computational laws**;
- required observables and measurements;
- a falsification program;
- lifecycle and knowledge-evolution rules.

It does **not** assert that neuron-level representation, reproduction, hierarchy, modularity, replay, energy constraints, synchronization, or attention are necessary. Necessity must be demonstrated experimentally. Objects may be deleted from future P1 models if a simpler ontology explains and predicts the same evidence.

## Article 3 — Minimum scientific criteria for any P1-v2 object

Every object type must have:

1. **Scientific definition:** what role the object claims to play.
2. **Operational definition:** how an independent observer determines whether it exists.
3. **Identity rule:** what makes it the same object over time.
4. **State boundary:** which variables belong to it.
5. **Transition set:** which changes it can undergo.
6. **Observable state:** what is emitted directly and what is derived.
7. **Measurement model:** quantities, units, time basis, aggregation, and validity.
8. **Failure modes:** how it can be malformed, ineffective, unstable, or misinterpreted.
9. **Validation experiment:** an intervention capable of adverse evidence.
10. **Controls:** simpler, random, frozen, shuffled, deleted, or resource-matched alternatives.
11. **Alternative explanations:** credible accounts producing the same observations.
12. **Retention decision:** keep, revise, narrow, split, merge, or delete.

## Article 4 — Object admissibility

A proposed object enters the live scientific ontology only if all conditions hold:

- its state is real computational state, not a display reconstruction presented as fact;
- it is distinguishable from neighboring objects;
- its identity survives or explicitly records replacement;
- it supports at least one discriminating experiment;
- its measurement has positive and negative controls;
- its scientific role cannot be stated equally well using a simpler already-existing object.

## Article 5 — Non-anthropomorphism

The following words have no privileged status: thought, belief, desire, pain, curiosity, self, consciousness, dream, emotion, understanding, intention. They may be used only after operationalization into measurable computational variables and must not imply human subjective experience.

---

# Part II — Reference ontology

## 6. Ontological layers

P1-v2 scientific objects occupy nine layers. Layers express scientific containment and dependence, not software boundaries.

| Layer | Objects | Scientific role |
|---|---|---|
| **World** | environment, task/regime, observation, outcome, intervention | Supplies conditions against which adaptation is tested |
| **Event** | prediction, error, update, message, replay, birth, death, checkpoint | Immutable occurrences from which histories are built |
| **Primitive adaptive** | neuron, connection | Smallest persistent adaptive state and interaction objects |
| **Resource** | energy budget, compute, memory capacity, communication budget | Constrains possible activity and supports fair comparisons |
| **Population** | community, hierarchy, module, circuit | Measured organizations of primitives at different stability and function levels |
| **Control** | attention, competition, cooperation, synchronization | Allocation and coordination processes, only if explicitly computed |
| **Learning** | memory, replay, plasticity, novelty, surprise | State-change and historical-use processes |
| **System** | organism/run, subsystem, behavioral capability, recovery state | Whole adaptive process and measured outcomes |
| **Scientific** | observation, evidence, hypothesis, law, theory, Unknown, Decision | Governs what is known about the computational system |

## 6.1 Relationship ontology

Permitted computational relationships include:

- `contains` / `member_of`;
- `connected_to` with direction and type;
- `sends_to` / `receives_from`;
- `inhibits`, `excites`, `modulates`, or neutral `transforms`, only when mathematically defined;
- `predicts` a target variable;
- `updates` a state;
- `stores` / `retrieves` / `replays` a historical carrier;
- `competes_with` for a named resource or opportunity;
- `cooperates_with` under a defined joint objective;
- `synchronizes_with` under a defined temporal statistic;
- `controls` an allocation or transition;
- `born_from`, `replaces`, `descends_from`, `pruned_by`;
- `specializes_for` an empirically defined context class;
- `generalizes_to` a held-out context class;
- `causes` only when backed by an identified intervention;
- `correlates_with` when no causal identification exists.

Relationship semantics must never be inferred from screen proximity or visual edge direction.

## 6.2 Identity ontology

Every persistent object has:

- a permanent identity;
- birth event and initial state;
- version/type identity;
- parentage if reproduced or split;
- membership history;
- state checkpoints or a complete reconstructable history;
- terminal event if it dies;
- replacement/successor link if functionality transfers.

A reused numeric index is not identity. A changed object retaining a name is not necessarily the same object. Identity continuity requires a declared rule and lineage record.

## 6.3 Core measurable quantities

The following quantity families form the shared measurement vocabulary:

1. **Predictive:** proper loss, excess loss versus oracle/reference, calibration, discrimination.
2. **Adaptive:** update magnitude, adaptation cost, learning progress, retained competence, recovery time.
3. **Structural:** unit/connection count, parameter count, topology, capacity, turnover, lineage.
4. **Functional:** intervention effect, selectivity, invariance, synergy, redundancy, unique contribution.
5. **Resource:** compute operations, update count, storage, communication, latency, wall/process time, explicitly defined energy proxy.
6. **Temporal:** event time, logical step, age, dormancy duration, onset, persistence, lag.
7. **Population:** distribution, heterogeneity, concentration, diversity, participation, coverage, omitted mass.
8. **Information:** predictive information, conditional information, compression/description length under a declared code, never metaphorical “knowledge.”
9. **Reliability:** variance across seeds/environments, failure probability, artifact integrity, reconstruction completeness.
10. **Causal:** estimand, compliance, paired contrast, mediation under assumptions, robustness to intervention.

---

# Part III — Computational objects

The entries below are scientific object cards. The proposed validation experiments are Discovery-stage minimal discriminators unless explicitly escalated.

## 7. Neuron

### Scientific definition

A **P1 neuron** is the smallest persistent, individually identifiable adaptive computational unit that integrates a bounded set of incoming signals and local state, emits a measurable output, and can change its future input–output transformation through learning.

A neuron is not defined by biological shape, spiking, scalar activation, or use of a neural-network library. A table entry, rule, token, or process is not a neuron unless it satisfies the full identity, state, communication, and adaptive-unit criteria.

### What it scientifically represents

A neuron represents a **locally addressable conditional transformation with memory**. Its scientific content is not a semantic label. It encodes whatever regularity in its input history is identifiable from its state and behavior: a predictive feature, context discriminator, temporal carrier, controller state, or combination. Semantic interpretations are hypotheses requiring decoding and intervention tests.

### Why it should exist

Neuronhood is justified only if persistent local units enable better adaptation, retention, causal localization, or resource allocation than a functionally matched architecture without individually persistent adaptive units.

### Operational definition

An independent observer can identify:

- unit ID, type, birth time, and lineage;
- incoming and outgoing connection IDs;
- local dynamic state;
- parameters controlling its transformation;
- input at an event and output produced;
- learning/update events affecting it;
- resource use and lifecycle state;
- interventions that silence, reset, perturb, duplicate, or replace it.

### Observable state

Direct state should include identity, lifecycle state, age, type, input summary, output, local parameters, update/delta, eligibility/plasticity state, incoming/outgoing messages, resource use, memberships, and parent/successor IDs. State not emitted is unobserved.

### Measurement

- predictive contribution under intervention;
- update rate and magnitude;
- selectivity and invariance across prespecified contexts;
- reliability across repeated contexts;
- mutual/predictive information with targets, conditional on alternatives;
- unique, redundant, and synergistic contribution at population level;
- resource cost per attributable outcome change;
- lifespan, dormancy, turnover, and replacement success;
- generalization to held-out contexts.

### How it should learn — candidate principle

A neuron should change only from locally available signals plus explicitly defined modulatory variables. Any global signal must be observable and experimentally separable. Useful learning means the update improves a prespecified future prediction or control outcome relative to frozen, random-update, and resource-matched alternatives.

### How it should specialize

Specialization is an empirical state in which a neuron’s interventionally relevant contribution is concentrated in a reproducible context class while preserving adequate response outside it. Labels are assigned after validation, never injected as identity.

### How it should forget

Forgetting is a measurable loss of previously demonstrated neuron- or system-level function. It may arise through parameter drift, connection loss, interference, resource reallocation, or deletion. A neuron should forget only under a candidate law shown to improve system adaptation, capacity, or recovery relative to no-forgetting and random-forgetting controls.

### How it should die

Death is an irreversible terminal transition removing the unit from future computation, except through a distinct replacement identity. It is scientifically justified only if removal preserves outcomes within a prespecified margin or improves resource-adjusted performance, and if recovery from mistaken death is understood.

### How it should reproduce

Reproduction is creation of a new neuron with explicit parentage and some inherited state. It is not ordinary initialization. It is justified only if parent-conditioned initialization improves adaptation or specialization over de novo, random-parent, and capacity-matched growth controls.

### How it should communicate

A neuron communicates only through recorded messages over actual connections. Each message has sender, receiver, time, content type, magnitude, and cost. Communication semantics are defined by measurable transformation, not by anthropomorphic labels.

### Failure modes

- identity aliasing or index reuse;
- unit state not causally relevant despite apparent selectivity;
- dead, saturated, unstable, or perpetually active units;
- global hidden updates misrepresented as local learning;
- designer-assigned semantics mistaken for learned specialization;
- duplication without functional diversity;
- deletion based on a defective importance metric;
- unbounded activity or resource use;
- single-unit stories that ignore distributed redundancy.

### Validation experiment

Train persistent-unit and no-persistent-unit conditions under matched capacity, updates, and compute on switching predictive tasks. Measure adaptation, retained competence, intervention-localizable contribution, and transfer. Then silence or reset units selected by preregistered criteria and compare with random, activity-matched, and resource-matched silencing.

### Controls

Frozen neurons; nonadaptive units; anonymous shared-state model; random local updates; shuffled unit identities; random silencing; activity-matched silencing; parameter-count and compute-matched simpler predictor.

### Alternative explanations

Performance may arise from total capacity, optimizer behavior, data order, designer initialization, connection structure, or population redundancy rather than neuron identity or specialization.

---

## 8. Connection

### Scientific definition

A **connection** is an individually identifiable, directed or explicitly undirected relation that transforms and transmits state from one computational object to another and may itself adapt.

### Operational definition

It has a stable connection ID, endpoint IDs, type, transformation/parameter state, delay if any, enablement state, update rule, creation/deletion history, and transmitted-message records.

### Observable state

Endpoints, direction, value/parameters, message history, delay, update/delta, plasticity state, age, utilization, resource cost, structural status, and lineage.

### Measurement

Effective transmission; intervention effect of deletion/perturbation; update magnitude; stability; redundancy; path participation; signal-to-noise; delay; cost; contribution conditional on alternate paths.

### Failure modes

Decorative graph edges; weight magnitude mistaken for importance; stale endpoint identity; silent disconnection; runaway amplification; frozen connection; hidden broadcast bypass; label leakage; dense redundancy that defeats localization.

### Validation experiment

Perturb or delete preregistered connection sets while measuring predicted target changes; compare against random, magnitude-matched, activity-matched, and path-redundancy-matched edge interventions.

### Controls

Fixed connections; random topology; shuffled endpoints; equal-parameter dense/sparse baselines; connection-free shared transform; lesion controls.

### Alternative explanations

Unit state, alternate paths, normalization, global updates, or topology density—not the connection—may cause the measured effect.

---

## 9. Memory

### Scientific definition

**Memory** is persistent computational state whose presence changes future behavior as a function of prior experience after that experience is no longer available in the current input.

### Operational definition

A memory claim requires a carrier, write event, persistence interval, read/use event or intervention, and an outcome difference attributable to the retained state.

### Observable state

Carrier ID, content representation or declared summary, source event, write/update time, age, accessibility, strength, retrieval eligibility, read events, mutation, eviction, owner/location, and resource cost.

### Measurement

Retention interval; retrieval accuracy; behavioral effect of carrier removal/replacement; interference; capacity; compression fidelity; task coverage; age distribution; reacquisition; recovery; false-memory or contamination rate.

### Failure modes

Current-input leakage; static designer state called memory; storage without causal use; retrieval without provenance; contamination; overwrite; stale harmful persistence; duplicated carriers; retention metric rewarding failure to learn.

### Validation experiment

Create temporally aliased tasks whose correct later response depends on a prior event unavailable at decision time. Intervene on the candidate carrier before the decision. Compare intact, removed, shuffled, irrelevant-carrier, and capacity-matched history-free controls.

### Controls

No-memory; current-input-only; randomized carrier; delayed irrelevant state; oracle memory; equal-capacity nonhistorical state.

### Alternative explanations

Current cues, task order, leakage, recurrent state not tied to the declared carrier, or memorized designer structure may explain success.

---

## 10. Replay

### Scientific definition

**Replay** is a later learning or state-transition event that intentionally reuses an identifiable historical carrier or reconstruction in the absence of the original event.

### Operational definition

Replay requires source provenance, selection event, requested and realized dose, timing, transformed content, receiving object, update consequence, and cost.

### Observable state

Eligibility set, selected item IDs, source task/time, age, gate request, realized batch, weights, receiver updates, shortfall, compute, and post-replay state.

### Measurement

Effect on retained competence, adaptation, transfer, calibration, and recovery; budget fidelity; historical specificity; timing specificity; item diversity; cost-adjusted benefit.

### Failure modes

Extra updates masquerading as replay benefit; current-sample rehearsal; unmatched timing or dose; biased buffer; replaying corrupted state; shortfall; catastrophic interference; no causal link between selected content and outcome.

### Validation experiment

Factorially separate historical content and timing under identical realized update budgets: historical versus nonhistorical content, and surprise versus matched-random timing. Pair by environment seed and report mastery, final oracle-relative loss, plasticity, and compute.

### Controls

No replay; update-matched current/nonhistorical rehearsal; shuffled historical content; equal-budget random timing; boundary timing; oracle selection.

### Alternative explanations

More compute, additional decay applications, immediate rehearsal, boundary detection, or task balancing can explain apparent replay effects.

---

## 11. Plasticity

### Scientific definition

**Plasticity** is the conditional capacity of a computational object to change its future transformation in response to experience.

### Operational definition

Plasticity is the measured response of state and behavior to a standardized learning opportunity, conditional on prior state and resource budget.

### Observable state

Eligibility, update sensitivity, actual deltas, learning rate or equivalent, constraints, local/global modulators, saturation, and history.

### Measurement

Adaptation AUC; samples/updates to criterion; state change per exposure; retained old competence; response across ages/contexts; reversibility; cost.

### Failure modes

Zero learning; uncontrolled drift; instability; hidden freezing; plasticity concentrated in already dominant units; retention achieved by refusing adaptation; measure confounded by task difficulty.

### Validation experiment

Expose matched systems to a controlled regime switch and compare adaptive, frozen, random-update, and constrained-plasticity conditions on adaptation and retention.

### Controls

Frozen state; random direction updates; replay/update matched baselines; task-difficulty calibration; oracle learner.

### Alternative explanations

Initial capacity, task similarity, optimizer state, or data order may explain apparent plasticity.

---

## 12. Prediction

### Scientific definition

A **prediction** is a probability distribution, score, or action-contingent forecast emitted before the target outcome is observed.

### Operational definition

Prediction time precedes target revelation; predictive object, target, horizon, condition, and scoring rule are fixed.

### Observable state

Prediction value/distribution, timestamp, source objects, target definition, horizon, confidence, context, and subsequent outcome.

### Measurement

Strictly proper score where applicable; oracle-relative excess; calibration; discrimination; regret; horizon-specific error; transfer.

### Failure modes

Target leakage; postdiction; improper score; changing target; uncalibrated confidence; aggregate masking; trivial environment.

### Validation experiment

Prequential held-out prediction against fixed-capacity, history-free, and oracle/reference baselines across prespecified environment classes.

### Controls

Constant predictor; empirical-frequency predictor; shuffled targets; oracle; capacity-matched simpler model.

### Alternative explanations

Leakage, persistence, task imbalance, or memorization may produce low error without learned structure.

---

## 13. Novelty

### Scientific definition

**Novelty** is the degree to which an observation is dissimilar or improbable relative to an explicitly defined reference set or density model, irrespective of whether the current predictor is accurate.

### Operational definition

A novelty score names the representation, reference distribution/window, distance or density rule, and update policy.

### Observable state

Score, reference identity, representation, nearest/reference items, age/window, threshold if any, and decision consequence.

### Measurement

Detection of held-out distributional changes; false-positive rate under stationary data; calibration to density or rank; robustness to scale and representation.

### Failure modes

Novelty equals raw prediction error; feature-scale artifact; reference drift; all rare events treated as useful; high-dimensional distance collapse; threshold tuning.

### Validation experiment

Cross novelty and predictive surprise independently: novel-predictable, novel-unpredictable, familiar-predictable, familiar-unpredictable events. Test whether the score discriminates the intended axis.

### Controls

Random score; raw loss; simple distance; frozen versus adaptive reference; shuffled representation.

### Alternative explanations

Prediction error, rarity, task boundary, magnitude, or encoder drift may produce the score.

---

## 14. Surprise

### Scientific definition

**Surprise** is the negative log probability or another preregistered proper unexpectedness measure assigned by the system’s predictive model to an observed outcome.

### Operational definition

For probabilistic prediction, `surprise_t = -log P(outcome_t | information available before t)`, with model and information set recorded.

### Observable state

Pre-event predictive distribution, outcome, score, units, source model, calibration state, and downstream allocation decisions.

### Measurement

Proper score behavior; calibration; sensitivity to genuine prediction violations; independence from arbitrary scaling; incremental value over boundary and novelty signals.

### Failure modes

Unit mismatch; uncalibrated probabilities; surprise conflated with novelty, salience, or task switch; threshold creates designer injection; degenerate overconfidence.

### Validation experiment

Manipulate outcome probability while independently controlling novelty and task boundaries. Test score ordering and whether surprise-based allocation outperforms matched random/boundary allocation.

### Controls

Random timing; boundary detector; novelty score; constant threshold; calibrated oracle surprise.

### Alternative explanations

Boundary timing, model miscalibration, rarity, or magnitude may explain both surprise and downstream effect.

---

## 15. Energy

### Scientific definition

**Energy** is permitted only as a conserved or budgeted measurable resource consumed by computation, communication, storage, or state change. It is not a metaphor for importance, uncertainty, affect, motivation, or free energy.

### Operational definition

Every energy variable names its unit or proxy, accounting boundary, conservation/budget rule, measurement method, and relation to actual resource use. If only operations, latency, or joules are measured, call the quantity by that name.

### Observable state

Allocated budget, consumption by object/event, residual budget, replenishment, unmet demand, accounting error, and external resource measurements.

### Measurement

Joules where available; otherwise explicit operation/communication/storage cost; outcome per resource; budget violations; allocation efficiency; starvation and waste.

### Failure modes

Weighted score mislabeled energy; incommensurate terms added; arbitrary coefficients; hidden resources; double counting; “energy” used to justify behavior without causal evidence.

### Validation experiment

Hold task and capacity constant, vary a real resource budget, and test prespecified performance/degradation curves. Compare the proposed allocation law against uniform, random, and oracle allocation under identical total budgets.

### Controls

No energy abstraction; direct compute counter; random/uniform allocation; shuffled costs; wall-power measurement where feasible.

### Alternative explanations

Compute count, latency, memory bandwidth, or scheduler priority—not the proposed energy law—may explain outcomes.

---

## 16. Identity

### Scientific definition

**Identity** is the continuity relation that determines whether state at two times belongs to the same computational object despite allowed changes.

### Operational definition

Identity is defined by permanent ID, birth/terminal events, lineage, permissible state transitions, and replacement rules.

### Observable state

ID, type/version, parentage, birth, state history, memberships, terminal status, successor, and integrity checks.

### Measurement

Continuity violations; alias/reuse rate; lineage completeness; reconstruction success; state attribution accuracy.

### Failure modes

Index reuse; hidden replacement; clone conflation; split/merge without lineage; stale references; identity based only on similarity.

### Validation experiment

Induce reorder, serialization, migration, reproduction, replacement, and deletion while testing whether histories and causal interventions remain correctly attributed.

### Controls

Index-based identity; randomized IDs; stateless reconstruction; deliberately aliased identities.

### Alternative explanations

State similarity or position may mimic continuity without persistent identity.

---

## 17. Community

### Scientific definition

A **community** is a reproducibly detected population of objects with stronger or more functionally coherent interaction internally than expected under a specified null, without presuming a single task function.

### Operational definition

Membership rule, interaction statistic, null model, resolution, alignment across time, coverage, and stability are declared.

### Observable state

Member IDs, boundary, internal/external interaction, derivation version, stability, split/merge history, and functional measurements.

### Measurement

Modularity relative to null; stability; communication concentration; intervention effect; synergy/redundancy; task/context association; cost.

### Failure modes

Layout-created clusters; algorithm sensitivity; resolution hacking; label switching; dense-degree artifact; communities with no functional consequence.

### Validation experiment

Detect communities on one data partition; preregister predictions; test on held-out histories and community-level interventions against size/degree/activity-matched random groups.

### Controls

Random partitions; degree-preserving graph null; activity-matched groups; alternate clustering algorithms.

### Alternative explanations

Topology density, common input, shared age, or clustering algorithm may produce apparent communities.

---

## 18. Hierarchy

### Scientific definition

A **hierarchy** is a directed relation among representational or control scales in which higher-level states integrate, constrain, predict, or coordinate lower-level states over broader temporal, spatial, or task scope.

### Operational definition

Levels, direction, scale, information flow, intervention targets, and cross-level predictions are explicit.

### Observable state

Level membership, parent/child relationships, update timescales, messages, predictions, control actions, and lineage.

### Measurement

Incremental predictive value across scales; timescale separation; top-down/bottom-up intervention effects; compression with fidelity; transfer; resource cost.

### Failure modes

Arbitrary layering; depth mistaken for hierarchy; circular level definitions; no cross-level causal effect; bottleneck without benefit; designer labels.

### Validation experiment

Compare proposed hierarchy with flat capacity/compute-matched controls and shuffled level assignments; intervene separately on bottom-up and top-down paths.

### Controls

Flat model; same-depth unstructured model; randomized hierarchy; disconnected higher level.

### Alternative explanations

Additional capacity, depth, receptive field, or training schedule may cause benefit.

---

## 19. Module

### Scientific definition

A **module** is a stable, bounded set of objects that performs a reproducible transformation or control function and is more independently replaceable than arbitrary equal-size sets.

### Operational definition

Boundary, inputs, outputs, state, function test, replacement interface at the scientific level, and stability interval are declared.

### Observable state

Members, boundary interactions, state, inputs/outputs, performance, resource use, replacement history, and dependencies.

### Measurement

Functional sufficiency/necessity under replacement; boundary strength; transfer; interference isolation; resource cost; robustness.

### Failure modes

Software package mistaken for scientific module; post hoc functional labeling; hidden cross-boundary dependencies; no replaceability; redundant module proliferation.

### Validation experiment

Replace, freeze, or swap the candidate module between trained systems and compare with random-group and equal-capacity replacements.

### Controls

Random equal-size group; monolithic matched model; boundary-shuffled population; no-module condition.

### Alternative explanations

Shared training, topology, or capacity—not modular function—may explain localization.

---

## 20. Circuit

### Scientific definition

A **circuit** is a recurring, temporally ordered causal interaction among identified objects that implements a bounded transformation or control process.

### Operational definition

Participants, event ordering, entry condition, state transition sequence, output condition, and interventionally necessary relations are specified.

### Observable state

Ordered events/messages, object states, latencies, repetitions, failures, and causal intervention results.

### Measurement

Sequence reliability; latency; causal necessity/sufficiency; outcome effect; recurrence; robustness; cost.

### Failure modes

Correlated activation presented as circuit; retrospective path selection; omitted alternate routes; sequence caused by common input; no repeatability.

### Validation experiment

Perturb specific participants or timing at preregistered circuit stages; compare predicted versus unpredicted outcome changes and alternate-path controls.

### Controls

Time-shuffled path; participant-matched random path; common-input control; endpoint-only model.

### Alternative explanations

Common drive, global state, or alternate paths may create the observed sequence.

---

## 21. Attention

### Scientific definition

**Attention** is an explicit, resource-bounded allocation process that changes which inputs, memories, units, messages, or updates receive computational access or weight.

### Operational definition

Eligible set, allocation scores, normalization, budget, selected objects, timing, and downstream consequence are recorded.

### Observable state

Raw and normalized allocation, masks, eligible objects, budget, controller state, selected targets, and outcome.

### Measurement

Concentration/entropy; coverage; switching; cost; intervention effect; benefit over uniform/random allocation; robustness.

### Failure modes

Weight equals explanation; saliency mislabeled attention; hidden eligibility; normalization error; collapsed allocation; high score without causal importance.

### Validation experiment

Compare learned allocation with uniform, random, fixed, and oracle allocation under equal budgets; mask/replace selected and nonselected content.

### Controls

Uniform/random allocation; score-shuffled targets; equal-compute full processing; oracle relevance.

### Alternative explanations

Scale, masking, positional bias, or extra compute may explain performance.

---

## 22. Competition

### Scientific definition

**Competition** is a process in which objects’ access to a named limited resource or opportunity is negatively coupled.

### Operational definition

Competitors, resource, allocation rule, coupling, winner/loser consequences, and total budget are explicit.

### Observable state

Bids/scores, eligibility, allocation, unmet demand, inhibition or exclusion, costs, winners, and downstream outcomes.

### Measurement

Allocation efficiency; diversity; concentration; starvation; specialization; adaptation; resource-adjusted performance.

### Failure modes

Winner lock-in; rich-get-richer collapse; arbitrary score; lost useful diversity; oscillation; competition with no real scarcity.

### Validation experiment

Vary scarcity and compare the candidate competition law with no competition, random, equal-share, soft allocation, and oracle allocation.

### Controls

Unlimited resource; uniform allocation; random winner; matched regularization; fixed specialists.

### Alternative explanations

Regularization, sparsity, or capacity limits—not competition dynamics—may produce specialization.

---

## 23. Cooperation

### Scientific definition

**Cooperation** is a measurable interaction in which joint contribution exceeds what the participating objects achieve independently under matched resources.

### Operational definition

Participants, joint task, independent baselines, combination rule, and synergy estimand are declared.

### Observable state

Messages, joint activation/state, shared resources, individual and combined outputs, and interventions.

### Measurement

Synergy versus additive baseline; redundancy; complementarity; robustness to member loss; cost; transfer.

### Failure modes

Mere coactivation; double-counted capacity; common input; one dominant object; unverifiable synergy metric.

### Validation experiment

Compare joint, isolated, shuffled-partner, and capacity-matched single-object conditions; intervene on each partner and their communication.

### Controls

Additive ensemble; random partners; no communication; duplicated strongest member; oracle grouping.

### Alternative explanations

Ensembling, extra capacity, or shared input may explain the apparent benefit.

---

## 24. Synchronization

### Scientific definition

**Synchronization** is reproducible temporal coordination among object events or states beyond that expected from shared inputs and base rates.

### Operational definition

Time basis, event/state variable, window, phase/lag statistic, null model, and relevant task interval are specified.

### Observable state

Timestamped states/events, phase or lag, common inputs, messages, and intervention records.

### Measurement

Phase-locking/cross-correlation conditional on common input; lag stability; information transfer; outcome effect; resource cost.

### Failure modes

Common-drive artifact; clock alignment artifact; arbitrary window; zero-lag correlation interpreted causally; synchrony without function.

### Validation experiment

Perturb timing while preserving rates and inputs; compare with time-shuffled, common-drive, and independently clocked controls.

### Controls

Jittered timing; shared-input-only; rate-matched independent streams; disconnected communication.

### Alternative explanations

Common input, global clock, task boundaries, or slow trends may produce synchrony.

---

## 25. Emergence

### Scientific definition

**Emergence** is the acquisition of a preregistered system property that was absent at initialization, results from learning or interaction, exceeds specified simpler/null/injection controls, and persists sufficiently to have measurable consequences.

### Operational definition

Property, baseline, onset, persistence, treatment, null, designer-injection audit, effect measure, and boundary conditions are preregistered.

### Observable state

Initialization state, learning history, structural/functional onset, persistence, intervention, controls, and outcome.

### Measurement

Null-referenced statistic; effect versus fixed-capacity and capacity-matched decoupled controls; injection audit; seed replication; threshold sensitivity; transfer.

### Failure modes

Post hoc property; treatment absent; designer injection; threshold hacking; capacity alone; shuffled control invalid; transient fluctuation; one-seed story.

### Validation experiment

Use a verified nontrivial environment and compare learning condition against fixed-capacity, capacity-matched error-decoupled, shuffled-input, and designer-seeded controls. Require treatment activation, absent-at-init state, held-out benefit, null-referenced structure, persistence, and independent replication.

### Controls

Fixed capacity; random-timed capacity; shuffled input; seeded target structure; equivalent extra capacity; no-learning.

### Alternative explanations

Capacity, optimization, data leakage, analysis flexibility, initialization, or designer-provided representation may explain the property.

---

# Part IV — Neuron lifecycle

## 26. Lifecycle state model

The lifecycle is a set of measurable states, not an analogy to organismal development.

```text
Proposed birth → Nascent → Developing → Active
                                  ├→ Expert
                                  ├→ Generalist
                                  ├→ Dormant → Reactivated
                                  ├→ Reproducing → Active + descendant
                                  ├→ Pruning candidate → Active | Dormant | Dead
                                  └→ Dead → Replaced (new identity) | terminal
```

Transitions require recorded events and decision variables. Age alone does not determine stage.

## 27. Birth

**Definition:** creation of a new persistent neuron identity and initial state.

**Birth eligibility hypothesis:** a neuron should be born only when residual predictive/adaptive error cannot be reduced adequately by existing capacity under a validated resource-aware criterion.

**Required observables:** trigger inputs, alternatives attempted, parentage, initial parameters, available capacity, predicted benefit, cost, and assigned resources.

**Failure:** runaway growth, births at arbitrary thresholds, duplicates, birth caused by scale mismatch, or no subsequent use.

**Minimal test:** compare error-linked birth with no growth, random-timed growth, and equal-count oracle-informed growth under matched capacity.

## 28. Development

**Definition:** period after birth during which state and connections change sufficiently that function is not yet stable.

**Operational criterion:** high but bounded update rate plus improving held-out predictive contribution over prespecified windows.

**Failure:** perpetual instability, no learning, takeover before evidence, or protected resources without benefit.

**Test:** track newborn learning curves against de novo random units, parent-initialized units, and equivalent updates to existing units.

## 29. Learning

**Definition:** experience-dependent change that improves a preregistered future outcome or intermediate predictive quantity.

A state change without future benefit is adaptation attempt, not successful learning.

**Test:** withheld future outcomes, frozen controls, shuffled targets, and intervention attribution.

## 30. Expertise

**Definition:** reproducible, interventionally relevant superior contribution in a bounded context class relative to peer and simpler baselines.

**Criterion:** high within-scope contribution, reliability, and cost efficiency; scope and failures explicitly recorded.

**Failure:** semantic label from correlation, train-set specificity, or dominance caused only by allocation bias.

**Test:** held-out within-scope tasks, out-of-scope tasks, matched-unit interventions, and allocation-controlled comparisons.

## 31. Generalization

**Definition:** preservation of attributable function under prespecified changes not used to define the specialization.

**Measurement:** transfer effect, invariance, calibration, and degradation across environment distance.

**Failure:** leakage, near-duplicate data, undefined scope, or average success hiding subgroup collapse.

**Test:** untouched contexts and environment classes with distance/shift specified prospectively.

## 32. Dormancy

**Definition:** reversible low-participation state in which identity and recoverable functional state persist while routine resource use is reduced.

**Operational criterion:** activity/resource use below threshold defined before outcomes, plus successful reactivation when prior context returns.

**Failure:** dead unit mislabeled dormant, unrecoverable state, hidden ongoing cost, or useful unit starved.

**Test:** context recurrence after controlled dormancy; compare deletion, always-active, random-dormant, and oracle dormancy.

## 33. Pruning

**Definition:** tested removal or disabling of a neuron or connection judged nonessential under a declared objective and scope.

**Pruning is an experiment before it is a permanent transition.**

**Required observables:** selection rule, predicted impact, lesion outcome, recovery, resource saving, and scope.

**Failure:** importance metric invalid, distributed redundancy masks immediate loss, delayed failure, subgroup harm, or irreproducible regrowth.

**Test:** prospective lesion with random, activity-matched, and contribution-matched controls; delayed and transfer probes.

## 34. Death

**Definition:** irreversible termination of an identity’s participation in future computation.

**Acceptance condition:** either the object is demonstrably dispensable within scope or removal yields a validated resource/adaptation advantage; lineage remains permanent.

**Failure:** irreversible loss before sufficient probes, identity reuse, hidden orphan connections, or post-death evidence erasure.

**Test:** staged disablement before permanent death, with rollback and delayed evaluation.

## 35. Reproduction

**Definition:** creation of a descendant identity inheriting a declared subset/transformation of parent state.

**Candidate scientific purpose:** accelerate capacity expansion while preserving useful priors and enabling divergence.

**Failure:** clone redundancy, inherited bias, population monoculture, identity confusion, or benefit due only to extra capacity.

**Test:** parent-derived versus de novo, random-parent, shuffled-inheritance, and equal-capacity existing-unit expansion.

## 36. Replacement

**Definition:** substitution of a new identity intended to preserve a specified function of a removed or failed object.

**Measurement:** functional equivalence margins, adaptation cost, recovery time, new-scope behavior, and resource change.

**Failure:** assuming identity continuity, hidden state transfer, loss of rare capability, or replacement evaluated only on common cases.

**Test:** blinded functional probes before/after replacement, rare-case and transfer tests, plus no-replacement and restored-original controls.

---

# Part V — Candidate computational laws

These are **law candidates**, not constitutional truths. A “law” is retained only after independent validation across at least two materially distinct architecture instances and environment classes, with a defined domain and documented exceptions. Before then it is a `HYP` family.

## 37. Law format

Each law records:

- scope and objects;
- mathematical/operational statement;
- predicted observations;
- adverse outcomes;
- dependencies;
- simpler alternatives;
- validation history;
- known boundaries;
- current status: Proposed, Exploratory, Under Validation, Supported in Scope, Rejected, or Superseded.

## 38. Learning law candidate — Predictive Improvement Law

**Statement:** Within a stationary-enough local interval, adaptive changes are retained only when they improve a prespecified future proper score or downstream outcome beyond frozen and random-update controls after resource adjustment.

**Implication:** update magnitude or loss reduction on the same sample is insufficient.

**Adverse outcome:** updates persist without future benefit, or a simpler frozen/random method matches them.

## 39. Growth law candidate — Residual-Need Growth Law

**Statement:** Additional neuron/connection capacity is justified only when existing capacity shows persistent, validated residual error and growth yields out-of-sample benefit beyond equal-capacity random-timed and error-decoupled controls after a complexity/resource cost.

**Adverse outcome:** growth does not activate, activates under trivial noise, or benefit is explained by capacity alone.

## 40. Energy law candidate — Explicit Resource Accounting Law

**Statement:** Under bounded resources, every state transition and communication event has an explicit measurable cost, and allocation policies are evaluated by outcome per resource against uniform/random/simple controls.

**Adverse outcome:** the energy variable is not aligned with actual resource use or does not improve decisions beyond direct resource counters.

## 41. Competition law candidate — Scarcity-Conditioned Allocation Law

**Statement:** Competition is useful only when a real constrained resource exists and competitive allocation improves resource-adjusted adaptation or specialization without unacceptable starvation or diversity collapse.

**Adverse outcome:** no-scarcity condition performs equally, or benefit is explained by sparsity/regularization.

## 42. Communication law candidate — Marginal Information Value Law

**Statement:** A communication channel is retained only when its messages improve receiver prediction/control conditional on receiver-local information and matched channel cost.

**Adverse outcome:** shuffled, delayed, or no-message controls perform equivalently.

## 43. Memory law candidate — Causal Historical Carrier Law

**Statement:** A state qualifies as functional memory only if removing or altering its historical carrier changes a later behavior that depends on past information unavailable in the current input.

**Adverse outcome:** performance survives carrier intervention or current cues fully explain it.

## 44. Plasticity law candidate — Bounded Adaptability Law

**Statement:** Useful plasticity reduces adaptation cost on changed conditions while retaining prior competence above a prespecified guardrail; neither maximum change nor minimum change is intrinsically optimal.

**Adverse outcome:** apparent retention arises from non-learning, or rapid adaptation destroys bounded prior capability.

## 45. Replay law candidate — Matched Historical Reuse Law

**Statement:** Replay is useful as a mechanism only if historical-content reuse improves a declared retention/adaptation/recovery outcome over update-, compute-, decay-, exposure-, and timing-matched nonhistorical controls.

**Adverse outcome:** matched controls eliminate the benefit.

## 46. Adaptation law candidate — Error-Conditional Reconfiguration Law

**Statement:** Reconfiguration should track persistent predictive inadequacy or changing task demands rather than raw activity, age, or arbitrary schedules, and must improve future outcomes relative to equal-budget random reconfiguration.

**Adverse outcome:** random or fixed schedules match it, or reconfiguration follows noise.

## 47. Recovery law candidate — Functional Redundancy and Relearning Law

**Statement:** After bounded damage or state loss, recovery arises through identifiable redundant pathways, reactivation, replacement, or relearning, each with distinct signatures and costs.

**Adverse outcome:** apparent recovery is task leakage, hidden restoration, easier post-damage data, or metric insensitivity.

## 48. Cooperation law candidate — Superadditive Joint Contribution Law

**Statement:** Cooperation exists only when a group’s interventionally measured contribution exceeds an additive/resource-matched combination of members acting independently.

**Adverse outcome:** additive ensemble or duplicated best member matches the group.

## 49. Synchronization law candidate — Functionally Consequential Coordination Law

**Statement:** Synchronization is scientifically retained only when coordination exceeds shared-input nulls and controlled timing perturbation changes a declared outcome.

**Adverse outcome:** synchrony disappears after conditioning on common drive or timing perturbation has no consequence.

## 50. Attention law candidate — Budgeted Allocation Advantage Law

**Statement:** An attention process is useful only if, under equal total processing budget, its allocations improve future outcomes over uniform, random, and simple fixed allocation and selected content has causal consequence.

**Adverse outcome:** equal-compute full processing or random allocation matches it.

## 51. Organization law candidate — Intervention-Stable Functional Organization Law

**Statement:** communities, modules, circuits, and hierarchies deserve ontological status only when their organization is reproducible, predicts held-out behavior, and supports stronger intervention predictions than size/activity/topology-matched arbitrary groupings.

**Adverse outcome:** organization depends on analysis choices or has no differential intervention effect.

## 52. Emergence law candidate — Null-Referenced Acquisition Law

**Statement:** A property may be called emergent only when absent at initialization, acquired under an operable learning treatment, beneficial out of sample, persistent, and above fixed, capacity-matched decoupled, shuffled, and designer-injection controls.

**Adverse outcome:** any necessary clause fails.

---

# Part VI — Falsification program for the law candidates

## 53. Experimental doctrine

The program does not attempt to validate all laws simultaneously. Each experiment targets one highest-priority uncertainty and uses the smallest design that distinguishes the candidate law from credible alternatives.

Every law moves through:

1. **Construct calibration:** can the intended variable be measured and manipulated?
2. **Treatment operability:** does the mechanism actually activate and separate conditions?
3. **Discovery discrimination:** does a cheap control make the law unnecessary?
4. **Validation:** do fit-for-claim controls, independent replication, uncertainty, and untouched conditions support the scoped claim?
5. **Cross-instance replication:** does the relation hold in another architecture and environment class?
6. **Law admission:** only then may the relation be called supported in scope.

## 54. Required experiment matrix

| Experiment | Target law/object | Minimal treatment and key controls | Primary measures | Falsifying outcome | Decision enabled |
|---|---|---|---|---|---|
| **V2-E01 Local learning calibration** | Neuron; Learning Law | Adaptive local update vs frozen, random-update, target-shuffled, matched simpler predictor | Future proper loss, update cost, held-out contexts | No advantage or benefit vanishes under target-shuffle control | Retain/revise/delete local neuron learning rule |
| **V2-E02 Persistent-unit necessity** | Neuron identity | Persistent identifiable units vs anonymous/shared-state matched model | Adaptation, retention, intervention localization, compute | Shared-state model matches all outcomes | Neuron ontology not yet necessary |
| **V2-E03 Specialization discrimination** | Expertise/community | Learned candidate specialists; random/activity/allocation-matched units | Held-out selectivity, causal effect, transfer | Correlation without differential intervention effect | Accept or reject specialization label |
| **V2-E04 Connection causality** | Connection; Communication Law | Edge/path perturbation with random/magnitude/activity/redundancy matched controls | Receiver outcome, conditional information, cost | Shuffled/no-channel matches or alternate paths explain effect | Retain/delete channel or narrow role |
| **V2-E05 Historical-carrier assay** | Memory Law | Temporally aliased task; carrier intact/removed/shuffled/irrelevant | Later decision accuracy, carrier intervention effect | Current cues suffice or carrier intervention irrelevant | Admit functional memory object |
| **V2-E06 Replay content × timing factorial** | Replay Law | Historical/nonhistorical × surprise/random timing with identical realized budgets | Mastery, final excess, plasticity, compute | Matched controls eliminate benefit | Advance or terminate replay line |
| **V2-E07 Plasticity frontier** | Plasticity/Adaptation Laws | Vary plasticity under controlled switches | Adaptation AUC, retained competence, worst-task result | No condition improves frontier over simple baseline | Reject proposed plasticity regulation |
| **V2-E08 Novelty–surprise dissociation** | Novelty; Surprise | Orthogonal manipulation of rarity and predictive probability | Score discrimination, calibration, allocation consequence | Scores fail intended axis or collapse to same signal | Merge constructs or retain distinction |
| **V2-E09 Resource-budget response** | Energy Law | Vary measured resource and allocation rule | Outcome/resource, starvation, accounting error | Energy proxy diverges from real cost or direct counters suffice | Delete metaphorical energy layer |
| **V2-E10 Growth operability** | Birth/Growth Law | Known positive and negative residual-need cases | Trigger opportunities, births, dose, false birth rate | Trigger absent in positive or fires in negative control | Recalibrate; do not test growth benefit yet |
| **V2-E11 Growth necessity** | Growth Law; reproduction | Need-gated birth vs no growth, random timing, capacity-matched decoupled, de novo vs inherited | Held-out gain, complexity cost, specialization, diversity | Capacity alone or random timing explains gain | Retain growth/reproduction or delete |
| **V2-E12 Dormancy and reactivation** | Dormancy | Candidate dormancy vs always-active, deletion, random dormancy, oracle | Resource saving, reactivation time, retained function | No saving or failed recovery | Retain/revise/delete dormancy |
| **V2-E13 Pruning safety and value** | Pruning/death | Staged lesion selected by criterion; random/activity/contribution matched | Immediate/delayed/transfer loss, resource saving, recovery | Selection no better than random or delayed harm exceeds margin | Authorize or prohibit permanent death law |
| **V2-E14 Replacement equivalence** | Replacement/identity | Replace failed unit/module vs restore original/no replacement | Equivalence, recovery, rare-case performance, cost | Functional scope not preserved | Reject replacement criterion |
| **V2-E15 Competition under scarcity** | Competition Law | Scarcity varied; candidate vs uniform/random/no competition/oracle | Efficiency, diversity, starvation, specialization | No benefit under scarcity or collapse harms guardrail | Retain/revise competition |
| **V2-E16 Cooperative synergy** | Cooperation Law | Joint vs isolated/additive/random partner/duplicated best | Synergy, intervention effects, cost | Additive or capacity explanation suffices | Accept/reject cooperation object |
| **V2-E17 Synchronization causality** | Synchronization Law | Timing perturbation preserving rate/input | Conditional synchrony, behavior, communication | Common-input null explains synchrony or perturbation irrelevant | Retain as mechanism or descriptive statistic only |
| **V2-E18 Attention allocation** | Attention Law | Learned vs uniform/random/fixed/oracle at equal budget; masking | Outcome, allocation entropy, causal selected-content effect | Equal-compute/random matches it | Delete or narrow attention mechanism |
| **V2-E19 Community/module validity** | Community/module | Held-out cluster derivation and group interventions vs matched random groups | Stability, prediction, necessity/sufficiency, replaceability | Analysis-sensitive or no stronger intervention prediction | Admit/reject population object |
| **V2-E20 Hierarchy necessity** | Hierarchy | Hierarchical vs flat/depth/capacity/compute matched; directional path interventions | Multi-timescale prediction, transfer, cost | Flat model matches or direction has no effect | Retain/delete hierarchy |
| **V2-E21 Circuit causality** | Circuit | Stage-specific timing/member perturbations vs shuffled/common-input controls | Sequence reliability, bounded output effect | Correlation explained by common drive/alternate path | Admit causal circuit or remain descriptive |
| **V2-E22 Emergence discriminator** | Emergence Law | Operable learning treatment vs fixed, random-timed capacity, shuffled input, designer-seeded | Absent-at-init, held-out gain, null-referenced structure, persistence | Any necessary emergence clause fails | Support scoped emergence or reject claim |
| **V2-E23 Damage and recovery decomposition** | Recovery Law | Standardized lesions; redundancy blocked, reactivation blocked, replacement blocked, relearning controlled | Recovery curve, pathway signatures, cost | Recovery cannot be attributed or is hidden restoration/leakage | Identify recovery mechanism or reject claim |
| **V2-E24 Cross-instance law replication** | Law status | Reimplement only scientific relation in a materially distinct architecture/environment | Same scoped estimand, heterogeneity, boundary conditions | Direction/relationship fails without explained moderator | Admit supported-in-scope law or challenge it |

## 55. Controls required across the program

Where applicable, every mechanism test considers:

- deletion/no-mechanism;
- frozen mechanism;
- random mechanism;
- shuffled inputs/targets/timing/identity;
- resource- and capacity-matched simpler baseline;
- positive and negative treatment-operability controls;
- oracle upper reference when defensible;
- current-input leakage control;
- designer-injection audit;
- common-input control;
- delayed and transfer probes;
- independent seed substreams;
- untouched confirmation conditions for Validation.

## 56. What would cause the entire neuron ontology to be revised

The reference neuron ontology should be narrowed, split, or abandoned if:

1. persistent unit identity adds no explanatory or predictive value over anonymous state;
2. local state cannot be interventionally linked to function because contributions are irreducibly nonlocal at all useful resolutions;
3. neuron lifecycle concepts do not improve prediction of adaptation/resource behavior;
4. simpler parameter/process ontologies support equal scientific discrimination;
5. observability required for neuron claims changes computation unacceptably;
6. unit definitions vary so radically across architectures that “neuron” has no stable cross-instance content.

In that case, P1 should retain the scientifically smaller ontology—adaptive state variables, transformations, and events—rather than defend the neuron metaphor.

---

# Part VII — Complete ontology schema

## 57. Universal computational object record

Every instantiated object must be representable scientifically by:

- object ID and ontology type;
- scientific-definition version;
- architecture-instance scope;
- birth/creation event;
- terminal state and successor if any;
- parent/child and containment relations;
- state schema and units;
- allowed transitions;
- incoming/outgoing relations;
- resource account;
- event history or checkpoint/reconstruction policy;
- observability class: direct, reconstructed, derived, annotation;
- measurement validity state;
- linked hypotheses/laws/experiments;
- known failure modes and anomalies;
- provenance and artifact identity.

## 58. Universal event record

Every decision-bearing event requires:

- event ID and type;
- logical time and, if relevant, wall time;
- actor object IDs;
- input state references;
- output state references;
- message/content references;
- resource consumption;
- causal parents only if recorded/identified;
- experiment/run/condition/config/seed provenance;
- completeness and dropped-state flags.

## 59. Hierarchy of scientific dependence

```text
World and task conditions
  → observations and interventions
    → predictions and errors
      → neuron/connection events
        → learning, communication, memory, replay, allocation
          → lifecycle and structural transitions
            → communities/modules/circuits/hierarchies
              → system behavior and recovery
                → measurements and results
                  → evidence relations
                    → hypotheses and candidate laws
                      → theories, only when earned
```

Arrows describe dependence, not automatic causation. Each causal arrow must be separately identified by intervention.

## 60. Dependency classes

- **Existential:** object A cannot exist without B.
- **Measurement:** claim A cannot be assessed without valid measure B.
- **Resource:** process A consumes or competes for B.
- **Temporal:** event A precedes or enables B.
- **Structural:** A contains/connects/controls B.
- **Functional:** A contributes to outcome B.
- **Causal:** intervention on A changes B under stated assumptions.
- **Epistemic:** hypothesis/law A depends on assumption or evidence B.

## 61. Ontology versioning

Ontology types are versioned hypotheses. A material change in definition, identity, measurement, or transition rules creates a successor ontology version. Old execution records retain their original semantics. Cross-version comparisons require an explicit mapping and loss-of-meaning statement.

---

# Part VIII — Living Scientific Model for P1-v2

## 62. Purpose

The P1-v2 Living Scientific Model is the current evidence-linked account of:

- which computational objects demonstrably exist;
- what functions they perform;
- which candidate laws survive;
- where relations hold or fail;
- which explanations compete;
- what architecture-independent principles, if any, have been earned.

It is a projection of canonical records, not a narrative source of truth.

## 63. Required state dimensions

For every object and law maintain separate confidence in:

1. **existence/operability**;
2. **measurement validity**;
3. **effect existence**;
4. **effect magnitude**;
5. **causal mechanism**;
6. **robustness**;
7. **generalization**;
8. **necessity over simpler alternatives**;
9. **resource efficiency**;
10. **observability completeness**.

## 64. Scientific model levels

### Level 0 — Proposed ontology

Definitions and possible experiments exist. No implementation or evidence is required.

### Level 1 — Operable object

Object state is emitted, identity is stable, positive/negative controls work, and observation is non-interfering.

### Level 2 — Functional association

Object state predicts a future outcome on held-out data, but causal role is unresolved.

### Level 3 — Scoped causal mechanism

Intervention distinguishes the object/mechanism from credible alternatives within one architecture/environment scope.

### Level 4 — Replicated computational principle

The relation replicates independently across seeds, instances, and at least two materially different architecture/environment classes, with boundaries known.

### Level 5 — Candidate theory component

The principle integrates with at least one independent principle and generates a novel risky prediction.

No object advances automatically because engineering adopts it.

## 65. Architecture growth transaction

Whenever Claude introduces or changes an architecture object, the scientific state must record:

1. ontology mapping or declaration that the object is scientifically new;
2. operational state and identity schema;
3. target hypothesis/law and why the object is needed;
4. cheaper or simpler alternatives considered;
5. treatment-operability and measurement tests;
6. expected adverse outcome and deletion criterion;
7. observability/non-interference evidence;
8. experiments enabled or invalidated;
9. effects on existing claims and comparability;
10. Scientific Decision after evidence.

Architecture growth does not update law confidence until experiments produce admissible evidence.

## 66. Post-experiment transaction

Every completed or abandoned P1-v2 experiment must update:

- execution validity;
- object/treatment operability;
- raw observations;
- measurement validity;
- evidence relations per claim;
- alternatives and confounders;
- object status and law status;
- confidence dimensions;
- ontology dependencies;
- negative results;
- Unknowns and scientific debt;
- experimental priority queue;
- Living Scientific Model change log;
- a Scientific Decision.

## 67. Conflict and heterogeneity

If a law holds in one architecture but fails in another:

- preserve both results;
- test measurement and treatment equivalence;
- model architecture/environment as moderators;
- narrow or split the law rather than average away conflict;
- prefer the smallest separating experiment;
- demote architecture-independence until replicated.

## 68. Deletion doctrine

A computational object becomes a deletion candidate when:

- no live high-priority hypothesis requires it;
- its state cannot be validly observed;
- its effect disappears under matched controls;
- a simpler object predicts/explains the same evidence;
- its resource or scientific debt exceeds its decision value;
- repeated attempts fail treatment operability;
- it survives only through post hoc relabeling.

Deletion is a scientific success when it removes a false principle.

---

# Part IX — Observatory obligations for P1-v2

## 69. Required traceability

The Observatory must permit the path:

```text
Theory or candidate law
→ hypothesis
→ evidence
→ experiment
→ condition
→ run
→ history
→ event
→ object
→ state and relationship
```

and the reverse path from an object event to the scientific decision it can affect.

## 70. Minimum neuron observability

No object may be called a neuron in scientific results unless the Observatory can expose:

- identity and lineage;
- lifecycle state;
- local state and parameters;
- actual inputs and outputs at a declared resolution;
- update events;
- connections and messages;
- resource use;
- memberships;
- interventions;
- missingness and sampling coverage.

At million-neuron scale, aggregation/sampling must disclose total count, observed count, omitted mass, sampling rule/seed, and stable drill-down identity.

## 71. No simulated internal narratives

The Observatory must never invent:

- thoughts or semantic labels;
- unrecorded neuron activation;
- causal influence from weight magnitude;
- cluster continuity without alignment;
- attention where no allocation operator exists;
- replay items from buffer summaries;
- emergence from growth animation;
- energy from arbitrary combined scores.

---

# Part X — Scientific acceptance criteria for future P1 architectures

A future architecture is scientifically admissible under this constitution only if:

1. Every claimed object maps to an ontology version and actual observable state.
2. Neuron and connection identities are stable and lineage-preserving.
3. Observability is proven non-interfering for decision-relevant behavior.
4. Prediction is prequential and measured by valid outcomes/scores.
5. Learning is separated from mere state change.
6. Memory is demonstrated by historical-carrier intervention.
7. Replay separates storage, timing, requested/realized budget, content, and effect.
8. Plasticity is evaluated jointly with retention and current-task adaptation.
9. Growth passes treatment-operability and capacity-matched controls.
10. Reproduction beats de novo and random-parent growth after resource matching.
11. Dormancy demonstrates reversible function plus resource savings.
12. Pruning/death uses prospective lesions and delayed/transfer probes.
13. Replacement never implies identity continuity and meets functional equivalence criteria.
14. Energy names real measured resource or an explicitly validated proxy.
15. Attention names actual budgeted allocation and survives causal masking controls.
16. Competition names a real scarcity and preserves guardrails against starvation/collapse.
17. Cooperation demonstrates superadditive joint contribution.
18. Synchronization exceeds common-input nulls and has interventionally measured consequence.
19. Communities/modules/circuits/hierarchies beat matched arbitrary organizations in held-out intervention prediction.
20. Emergence satisfies absence-at-init, treatment operability, null/reference, injection audit, persistence, and replication.
21. Every causal claim names an estimand, intervention, unit of inference, controls, assumptions, and uncertainty.
22. Every aggregate exposes heterogeneity, coverage, and omitted mass.
23. Negative, null, invalid, and abandoned outcomes remain permanent.
24. No candidate law is called supported outside its validated scope.
25. No architecture is retained merely because it resembles biology.

---

# Part XI — Ten-year scientific architecture

## 72. What would deserve the name “observable artificial nervous system”

Ten years from now, P1 would deserve that name only if the phrase makes precise, testable commitments.

Such a system would contain a large population of persistent adaptive units, but scale would not be the achievement. The achievement would be that every unit and relation belongs to a coherent scientific ontology and every important system-level claim can be traced to recorded state and tested interventions.

### 72.1 Its primitive units

Its neurons would be heterogeneous only where heterogeneity has earned explanatory value. Each would have stable identity, lineage, local adaptive state, bounded communication, resource accounting, and a measurable lifecycle. Some would become specialists, some generalists, some dormant, some reproducibly replaced, and many would never justify survival. None would receive human semantic labels merely from high activation.

### 72.2 Its structure

Connections would be real transform-and-transmit relations with observed messages and intervention histories. Communities, modules, circuits, and hierarchies would not be drawn because a graph looks clustered. They would exist scientifically because preregistered organization measures predict held-out behavior and group-level interventions outperform matched arbitrary partitions.

### 72.3 Its adaptation

Learning would be judged by future proper prediction and objective task outcomes. Plasticity would be a measured frontier between new adaptation and preserved old competence. Growth would occur only when residual need is demonstrated. Pruning and death would be reversible experiments before permanent transitions. Reproduction would survive only if inherited state helps beyond extra capacity.

### 72.4 Its memory

Memory would be a population of identifiable historical carriers whose write, persistence, access, transformation, and causal use are observable. Replay would reveal exactly what history was reused, when, at what dose and cost, and against what matched alternative. Recovery after damage would be decomposable into redundancy, reactivation, replacement, and relearning rather than celebrated as an opaque resilience score.

### 72.5 Its control and resources

Attention would be an actual constrained allocation process, not a visualization of salience. Competition would occur only over named scarce resources; cooperation would require superadditive contribution; synchronization would require functional timing dependence beyond common drive. Energy would mean measured resource—not metaphysics.

### 72.6 Its emergence

The system might exhibit emergent organization, but the scientific bar would remain severe: the property was absent at initialization, the learning treatment operated, matched controls failed to reproduce it, designer injection was excluded, the result persisted, transferred within declared bounds, and replicated independently. Most attractive patterns would not meet this standard. That is a strength.

### 72.7 Its observability

Scientists could navigate from system outcome to experiment, history, event, community, neuron, connection, message, and state transition, then back to the evidence and law affected. At millions of neurons the instrument would disclose aggregation and sampling rather than simulate omniscience. Unknown state would remain visibly unknown.

### 72.8 Its scientific maturity

The mature P1 would not possess a single sacred architecture. It would possess a small set of replicated computational principles with known domains and failures. Architectures would be replaceable experimental realizations of those principles. Unsupported objects would disappear. Contradictory evidence would split laws by scope. The Living Scientific Model would show what is observed, causally supported, rejected, unresolved, and worth testing next.

### 72.9 Final criterion

P1 becomes an observable artificial nervous system when:

> persistent adaptive units and their relations form experimentally validated, resource-bounded, recoverable organizations whose behavior can be explained and falsified across scales without hidden state, biological mysticism, or decorative inference.

Until then, “artificial nervous system” remains a hypothesis about what P1 may become—not a title the project grants itself.

---

# Part XII — Immediate scientific decision

## 73. What this constitution authorizes now

It authorizes:

- vocabulary and object hypotheses for P1-v2;
- observability requirements;
- candidate law registration;
- minimal construct-calibration experiments;
- deletion of terms or mechanisms that cannot pass operational definition.

It does not authorize building the complete ontology at once.

## 74. Smallest next scientific step

The highest-value first question is not how millions of neurons should organize. It is:

> Does persistent, individually identifiable local adaptive state provide measurable predictive, adaptive, or causal-localization value beyond an anonymous, capacity- and resource-matched adaptive baseline?

Run **V2-E01 Local learning calibration** and **V2-E02 Persistent-unit necessity** before investing in reproduction, hierarchy, communities, synchronization, or complex lifecycle control.

If persistent units add no discriminating value, revise the neuron ontology immediately. If they do, proceed next to memory-carrier, plasticity-frontier, and growth-operability assays. This sequencing maximizes scientific understanding per unit of engineering effort.

---

## Constitutional doctrine

P1-v2 must not begin with the proposition that intelligence requires neurons. It begins with a falsifiable question:

> Under what conditions do persistent local adaptive units become the smallest useful scientific explanation for continual adaptive behavior?

Every future P1 architecture is an experiment on that question.
