# Project P1-v2 — Constitution Lock

- **Document type:** Constitutional reconciliation and primitive freeze
- **Version:** 1.0.0
- **Date:** 2026-07-28
- **Produced by:** P1 Architecture Review Board (reconciliation of three independent inputs)
- **Status:** Proposed. **Unregistered.** Per `REPOSITORY_CONSTITUTION.md`, this document has
  no normative authority until it is entered in `GOVERNANCE_REGISTRY.yaml` with a status,
  jurisdiction and authority assignment. A root location grants none.
- **Scope:** P1-v2 primitive ontology, lifecycle/event vocabulary, evidence boundary, and
  experiment-gated implementation sequence.
- **Responsibility:** Reconcile computational existence, scientific necessity, experimental
  observability, and removal criteria into the smallest pre-implementation architecture.
- **Authority source:** Pending explicit Architecture Review Board adoption and Governance
  Registry activation; this draft does not confer authority on itself.
- **Authority jurisdiction:** P1-v2 primitive admission, removal, reclassification, and generation
  gates. It does not establish scientific truth or supersede repository-wide governance.
- **Implementation state at freeze:** no `v2/` package exists in the repository. The primitive
  set is frozen *before* implementation, which is the only point at which a freeze is cheap.

## Reconciled inputs

| Input | Path | Authority claimed | Authority granted here |
|---|---|---|---|
| Computational architecture | `docs/architecture/P1V2_COMPUTATIONAL_ARCHITECTURE.md` | Engineering design | Defines **computational existence** |
| Scientific constitution | `P1_V2_SCIENTIFIC_CONSTITUTION.md` v0.1.0 | Scientific blueprint | Defines **scientific necessity** |
| Observatory specification | `P1_OBSERVATORY_SCIENTIFIC_SPECIFICATION.md` | Scientific requirements | Defines **experimental observability** |

Where the three disagree, this document decides, and records why. Where they agree, this
document deletes whatever the agreement made redundant.

---

## Part 0 — Reconciliation verdict

### 0.1 The admission rule applied

An object survives only if it satisfies all four tests. This is the intersection of the three
inputs' own rules (Architecture §2.17 "a state exists only where the scheduler treats it
differently"; Constitution Art. 4 admissibility; Observatory §2.1 admissible mark classes).

| Test | Question | Source of the test |
|---|---|---|
| **T1 Computational necessity** | Does removing it change what the engine computes, or make a required guarantee untestable? | Architecture |
| **T2 Scientific necessity** | Does a live hypothesis or law candidate need it, and is deletion its own null? | Constitution Art. 3, §68 |
| **T3 Observability** | Can its state be emitted, folded, and rendered without invention? | Observatory §2.1, §20.1 |
| **T4 Experimental necessity** | Does at least one registered experiment become runnable *because* it exists? | Constitution §54 |

An object failing **T1** is a measurement. Failing **T2** is decoration. Failing **T3** is hidden
state. Failing **T4** is speculation. All four failures were found in the inputs.

### 0.2 Result

| Quantity | Architecture | Constitution | Observatory | **Locked v1.0** |
|---|---|---|---|---|
| Object/primitive types | 20 catalogued (+11 declined) | 19 object cards over 9 layers | 9 zoom objects | **19** (14 runtime + 5 evidence) |
| Lifecycle states | 8 (neuron) + 4 (edge) + 4 (candidate) | 12 stages | — | **5**, one machine, declared subsets |
| Event kinds | 44 | — | — | **16** |
| Overlays | — | — | 18 | **8** |
| Visualization plates | 16 view rows | — | 36 | **30** |
| Registered experiments | 5 generation gates | 24 | — | **22** |
| Public interfaces | 5 | — | — | **4** |
| Candidate laws | — | 15 | — | **11** |

Deleted outright: 9 named objects. Reclassified as measurements: 8. Merged: 7. Added: 3 primitives plus mandatory guardrails and control-policy instances.

### 0.3 The four decisions that carry the freeze

1. **`Candidate` is not an object.** It is the lifecycle state `CANDIDATE` on a `Neuron` or
   `Edge`. Both already had that state. Keeping a separate class was two representations of one
   claim — the exact defect Architecture §2.17 was written to prevent.
2. **`Intervention` is a primitive, and was missing from all three ontologies as an object.**
   Without it, 8 of 24 registered experiments and every causal claim in the Constitution are
   unrunnable, and Observatory V27/V32 have no source records. This is the single largest gap
   found.
3. **Structural decisions require *exact* ΔL, which the log-linear readout supplies only for
   readout-incident contributions.** Therefore v1.0 forbids promoting any object whose ΔL is
   not exactly computable. Depth beyond that is a G4 question, not a substrate assumption.
4. **Detected organization is a measurement, not an object.** Community, hierarchy, circuit,
   attention, plasticity, surprise, expertise and cooperation all reduce to statistics over the
   14 runtime primitives. `Module` alone retains a path back to primitive status, and only on
   G4/G5 evidence.

---

## Part 1 — Reconciliation matrix

Two tiers. **Tier R (runtime)** is what the engine is; every entry is state or occurrence inside
a run. **Tier E (evidence)** is what the science is; every entry is a record about runs. The
split exists because Constitution §6's "Scientific" layer (hypothesis, law, decision) has no
runtime state and would otherwise fail T1 and be deleted, taking the falsification programme
with it.

Notation: `E##` = Constitution §54 experiment. `V##` = Observatory §15 plate. `G#` = Architecture
§12 generation.

### Tier R — runtime primitives

#### R1 `Run`

| Facet | Reconciled definition |
|---|---|
| **Scientific definition** | The organism/run of Constitution §6 System layer: one bounded adaptive process whose provenance determines whether anything observed in it is admissible evidence. |
| **Computational implementation** | Immutable manifest allocated before tick 0: `run_id`, config hash, code commit + clean/dirty, full seed decomposition (7 substreams), environment identity, determinism tier D0/D1/D2, policy roster, status, completeness/truncation, artifact inventory + digests. Root of every run-addressed `ObjId`. |
| **Observable state** | Direct. Emitted as `run` at open and close. Every other event is scoped by it. |
| **Validation experiment** | Not a mechanism. Validated by the apparatus workflow: isolated repeated-run identity of decision-relevant outputs under a clean checkout. |
| **Failure modes** | Dirty/untracked code; unrecorded seed; truncation reported as completion; tier claimed but not enforced; artifact digest drift; manifest written after the fact. |
| **Acceptance criteria** | V01 renders from the manifest alone; a D2 run is mechanically refused by the confirmatory decision path; incomplete runs cannot reach `confirmatory-admissible`. |
| **Removal criteria** | Never. Removing it makes every other primitive unattributable. |

#### R2 `Environment`

| Facet | Reconciled definition |
|---|---|
| **Scientific definition** | Constitution §6 World layer: supplies observations, targets, regimes/tasks, switch boundaries, and — where defined — the oracle against which excess loss is measured. |
| **Computational implementation** | M1 `core.protocols.Environment` / `Benchmark`, inherited unchanged. Registered, seeded from the `environment` substream, identity in the manifest. |
| **Observable state** | Direct: observation, target, regime id, boundary, oracle value per step, recorded in `predict`. |
| **Validation experiment** | Environment non-triviality is a precondition of E11/E22: a generating process the order-1 baseline cannot represent, with a computable oracle. G2 cannot start without it. |
| **Failure modes** | Trivial environment (no structure to find, producing a true null that says nothing); leakage of target into observation; no valid oracle while excess loss is reported; undeclared regime boundaries; distance between regimes not prespecified. |
| **Acceptance criteria** | Oracle validated; boundaries declared before runs; a positive and a negative control environment exist for every growth claim. |
| **Removal criteria** | Never. Without it there is no prediction, no regime switch, and no adaptation to measure. |

#### R3 `Tick`

| Facet | Reconciled definition |
|---|---|
| **Scientific definition** | The logical time basis (Constitution §6.3 Temporal) and the unit that separates online learning from replay learning from frozen probing — the separation whose absence produced the M0 update-count confound. |
| **Computational implementation** | `(index, mode ∈ {ONLINE, REPLAY, PROBE}, graph_generation)`. Fixed 11-phase order, predict-before-learn. `PROBE` mechanically cannot produce a parameter delta. Replay is issued as `mode=REPLAY` sub-ticks, recursion depth capped at 1. |
| **Observable state** | Direct: one `tick` event per tick; closed by that tick's `ledger` settle. |
| **Validation experiment** | Underlies all. Directly required by E06 (replay content × timing at identical *realized* budgets) and every resource-matching check. |
| **Failure modes** | Phase executed out of order; replay updates counted as online; probe that trains; unbounded replay recursion turning consolidation into the whole computation; wall-clock used as an ordering key. |
| **Acceptance criteria** | Phase-order assertion; `test_probe_no_delta`; realized replay dose reconstructible per tick from events alone (V06/V20). |
| **Removal criteria** | Never. |

#### R4 `Event`

| Facet | Reconciled definition |
|---|---|
| **Scientific definition** | Constitution §58 universal event record: the immutable occurrence from which all histories, all provenance, and all traceability (§69) are built. Observatory class **D**. |
| **Computational implementation** | `obs/2` envelope: `seq, kind, tick, phase, subject, cause, payload, v, wall`. 16 kinds (Appendix C), 6 tiers; FAULT and STRUCTURAL undroppable. `cause` records computational parentage; it must not be rendered as an identified causal relation unless an `Intervention` and declared estimand support that interpretation. The log is the system of record: state at T is *defined* as the fold of events 0..T. |
| **Observable state** | It *is* the observable. `stream_meta` carries the drop ledger, sampling rule and omitted mass. |
| **Validation experiment** | Enables all 22. Directly gates V1 exact reconstruction and `test_no_engine_import`. |
| **Failure modes** | Silent loss (loss is legal, silence is not); dropped fault producing a run that looks clean; renumbered kind ids breaking old logs; unrecorded `cause` making birth look spontaneous; blocking or formatting on the tick path. |
| **Acceptance criteria** | V1 reconstruction bit-exact from structural + checkpoint streams; every Observatory mark names a real `(run_id, seq, tick)`; `test_no_engine_import` passes with `v2.*` unimportable. |
| **Removal criteria** | Never. Its removal is the definition of hidden state. |

#### R5 `Snapshot`

| Facet | Reconciled definition |
|---|---|
| **Scientific definition** | Constitution §57's checkpoint alternative to complete history, and §6.3 Reliability: reconstruction completeness at a scale where the dynamic stream is admittedly lossy. |
| **Computational implementation** | Content-addressed (BLAKE2b over canonical bytes) complete state: neurons, edges, delay line, ledger, episodic memory contents, **per-substream RNG states**. Sorted, canonical, versioned. |
| **Observable state** | Direct: `checkpoint` event carries the digest; the payload is the addressed artifact. |
| **Validation experiment** | `test_snapshot_roundtrip`, `test_rollback_equivalence`. Prerequisite for every intervention experiment that must branch from a common pre-intervention history (E13, E23, V03, V14). |
| **Failure modes** | Resume that re-seeds (a new run with borrowed parameters); digest that depends on history rather than state; omitted field discovered only as a hash mismatch; snapshot trusted rather than verified. |
| **Acceptance criteria** | Load-then-tick reproduces the live state hash; rollback from T reproduces the original hash at T'. |
| **Removal criteria** | If the complete event stream is affordable at target scale, snapshots become an optimisation, not a primitive. Not the case at 10⁵. |

#### R6 `Neuron`

| Facet | Reconciled definition |
|---|---|
| **Scientific definition** | Constitution §7: the smallest persistent, individually identifiable adaptive unit — a locally addressable conditional transformation with memory. Its scientific content is not a semantic label. |
| **Computational implementation** | `(id, kind, kind_version, params, in/out arity from kind, stats, lifecycle, birth_tick, birth_cause, shard)`. `id` allocated once, never reused. Params initialised from a seed derived from the neuron's **own id**, so initialisation is independent of creation order. `stats` contains **only accumulators read by an active Policy** (Art. L-6). |
| **Observable state** | Direct: `lifecycle`, `param_update` (delta norm + contribution_nats), `signal` (in/out at declared resolution and coverage), `evidence`. Full params only in snapshots. |
| **Validation experiment** | **E02 persistent-unit necessity** — persistent identifiable units vs the anonymous shared-state model, capacity- and compute-matched, on switching tasks. `count_model` is that control and is already registered. E01 for its update rule; E03 for specialisation. |
| **Failure modes** | Identity aliasing / index reuse; state not causally relevant despite apparent selectivity; dead, saturated or perpetually active units; global updates misrepresented as local; designer-assigned semantics mistaken for learned specialisation; deletion by a defective importance metric; single-unit stories that ignore distributed redundancy; non-finite params. |
| **Acceptance criteria** | G1 count-equivalence (the degenerate static case reproduces `p1v0.CountModel` bit-for-bit); then **E02 must show a discriminating advantage before any growth claim is attempted**. |
| **Removal criteria** | **E02 null.** If persistent identity adds no predictive, adaptive, or causal-localisation value over anonymous matched state, `Neuron` collapses to `Kind` + a parameter block and this lock is amended by evidence (Constitution §56, §74). |

#### R7 `Kind`

| Facet | Reconciled definition |
|---|---|
| **Scientific definition** | Constitution §6.2 "version/type identity", and the only place a mechanism declares its own description length — the arithmetic on which every existence decision rests. |
| **Computational implementation** | Registered, never subclassed, keyed `(name, version)`: `init`, pure `forward`, `update` → delta, `cost_nats`, declared arity and output width. G1 ships exactly four: `encode_onehot`, `count_expert`, `linear_readout`, `constant_bias`. `residual_expert` at G2, `gate_sigmoid` at G3. Nothing arrives before the experiment that needs it. |
| **Observable state** | Direct: `(name, version)` on every `lifecycle` birth; the registry roster in the manifest. |
| **Validation experiment** | E01 (does the update rule beat frozen / random / shuffled-target?). Each new kind is a treatment requiring its own falsifier before it ships. |
| **Failure modes** | Unregistered name; arity disagreement with wiring; `forward` impurity (breaks determinism, snapshot, replay); numerically changed `forward` without a version bump, silently invalidating old evidence; a kind whose `cost_nats` is unstated or gamed. |
| **Acceptance criteria** | Old logs replayable because resolution is by `(name, version)`; golden-file test per registry entry; purity caught by the worker-count differential. |
| **Removal criteria** | Merging behaviour into `Neuron` would delete shared versioned identity and the cost declaration. Not removable. Merger with `Policy` was considered and declined (Part 4.3). |

#### R8 `Edge`

| Facet | Reconciled definition |
|---|---|
| **Scientific definition** | Constitution §8: an individually identifiable directed relation that transforms and transmits state and may itself adapt. Not a decorative graph line. |
| **Computational implementation** | `(id, src=(neuron,index), dst=(neuron,index), weight, delay ∈ {INSTANT, DELAYED}, conductance, lifecycle, birth_tick, birth_cause, stats)`. The INSTANT subgraph must be acyclic; a cycle-closing proposal is **retyped DELAYED**, not discarded. `weight` has exactly one writer (the receiver's `kind.update`). `conductance` is the per-tick routing multiplier, kept separate so a learned association and a momentary routing decision are never confused. |
| **Observable state** | Direct: `lifecycle`, `edge_state` (**absolute** weight and conductance, never deltas only, so a lossy stream stays safe to coalesce and resume). |
| **Validation experiment** | **E04 connection causality** — edge/path perturbation against random, magnitude-matched, activity-matched and path-redundancy-matched controls. Requires `Intervention` (R14). |
| **Failure modes** | Weight magnitude mistaken for importance; stale endpoint identity; silent disconnection; runaway amplification; hidden broadcast bypass; dense redundancy defeating localisation; two writers to one weight making attribution impossible. |
| **Acceptance criteria** | Deletion effects exceed matched-random edge interventions conditional on alternate paths; absolute-value emission verified by a fold-under-loss test. |
| **Removal criteria** | If all measured effects are explained by unit state or alternate paths, the edge is a bookkeeping device and the ontology narrows to a shared transform. |

#### R9 `Graph`

| Facet | Reconciled definition |
|---|---|
| **Scientific definition** | Constitution §6.1 relationship ontology made concrete, plus §9 structural observability: the topology whose history *is* structural memory. |
| **Computational implementation** | The only object permitted to mutate structure, and only in phase STRUCTURE, and only as an atomically validated batch. Holds `generation`; derives (never stores as a separate primitive) the topological order and wavefront level sets, recomputed once per generation. |
| **Observable state** | Reconstructed: the fold of `lifecycle` + `edge_state`. Depth, wavefront membership and connectivity are **derived**, never stored — a stored layer index is a second representation of the edge set. |
| **Validation experiment** | E19/E20 operate on its derived organisation. V3 (tick-constant topology) is its own test. |
| **Failure modes** | Mutation outside phase STRUCTURE; partially applied batch (unreconstructible, so V1-fatal); accepted cycle; generation/schedule mismatch; validation that reports success on a rejected batch. |
| **Acceptance criteria** | `test_structure_phase_only`; atomic rejection emits `structure_reject` naming the failed invariant; caches keyed by generation. |
| **Removal criteria** | Never while structure is dynamic. |

#### R10 `DelayLine`

| Facet | Reconciled definition |
|---|---|
| **Scientific definition** | Activation memory: one of exactly two historical carriers whose intervention can satisfy Constitution §43 (Causal Historical Carrier Law) on a one-tick timescale. |
| **Computational implementation** | Latched previous-tick outputs, indexed by `(neuron_id, out_index)` so re-indexing after a structural commit preserves values by identity, not by ordinal. Written only in phase COMMIT. Sole channel that may cross a shard boundary. |
| **Observable state** | Direct via `signal`; complete in snapshots. `fault(delay_default)` when a neuron created this tick is read. |
| **Validation experiment** | **E05 historical-carrier assay** on temporally aliased tasks: intact / removed / shuffled / irrelevant carrier vs current-input-only control. |
| **Failure modes** | Invisible dependence on creation order (defaults left implicit); generation mismatch losing values; recurrence reintroduced into the current tick, restoring the fixed-point problem the delay class exists to remove. |
| **Acceptance criteria** | DELAYED reads provably independent of evaluation order within a tick; carrier intervention changes later behaviour that current input cannot explain. |
| **Removal criteria** | Delete only if recurrence is deleted. Per-edge latching was considered and rejected (O(E) storage, duplicated values, two writers). |

#### R11 `EpisodicMemory`

| Facet | Reconciled definition |
|---|---|
| **Scientific definition** | Constitution §9/§10: the bounded population of identifiable historical carriers whose write, residence, selection, transformation and causal use are observable. The substrate of the repository's live replay programme. |
| **Computational implementation** | M1 `core.protocols.Memory`, contract unchanged (`append` / `sample` / `snapshot` / `__len__`), so every existing replay policy, gate and matched-budget control applies without modification. Read in REPLAY, written in INTAKE. |
| **Observable state** | Direct via `memory` events, which v1.0 **extends beyond M1** to carry admit, evict *and selection* with item id, source tick, source regime, age and weight. Without selection records, V18 is unsupportable and replay content cannot be attributed. |
| **Validation experiment** | **E06 replay content × timing factorial** at identical realized budgets; E05 carrier assay. |
| **Failure modes** | Current-sample rehearsal counted as replay; extra updates masquerading as replay benefit; biased or empty buffer; duplicate items; premature eviction; requested-vs-realized dose divergence; item provenance fabricated from buffer contents. |
| **Acceptance criteria** | V20 budget equivalence from *realized* not intended dose; selected item ids present in the log; historical content separable from timing. |
| **Removal criteria** | E06 null under matched controls terminates replay as a mechanism, but the carrier remains required by E05. Deletion requires both to fail. |

#### R12 `Ledger`

| Facet | Reconciled definition |
|---|---|
| **Scientific definition** | Constitution §15 and §40: a **measured resource**, never a metaphor. It is the named scarcity without which "competition" has no referent, and the accounting that makes outcome-per-resource comparisons fair. |
| **Computational implementation** | Per-tick evaluation capacity, per-object charges, candidate quota, exploration reserve, settle record. Renamed from `EnergyLedger`: the word *energy* is banned from v1.0 state, events and results (Art. L-4). Charges are **counts of evaluations**; the nats↔compute exchange rate is a Policy parameter recorded in the manifest, never a ledger field — mixing units inside the accounting object is Constitution §15's named failure mode. |
| **Observable state** | Direct: `ledger` settle per tick (capacity, spent, per-object charges at declared resolution, unmet demand); starvation as `fault(starved)` with the skipped set, because a silently degraded prediction is a fabricated measurement. |
| **Validation experiment** | **E09 resource-budget response** (does the proxy track real cost, and does the allocation law beat uniform/random/oracle at equal budget?) and **E15 competition under scarcity**. |
| **Failure modes** | Weighted score mislabelled as a resource; incommensurate terms summed; hidden resources; double counting; capacity below the readout's transitive closure (must fail at build, not at tick); **starvation→pruning collapse** — see the mandatory guardrail below. |
| **Acceptance criteria** | Ledger totals reconcile against an independent compute counter; the G2 result survives a declared range of exchange rates (sensitivity analysis is a gate, not an appendix). |
| **Removal criteria** | E09 shows the proxy diverges from real cost, or direct counters make the allocation layer decision-irrelevant. Then the ledger degrades to a counter and competition is deleted with it. |

> **Mandatory guardrail (new; resolves Contradiction 12).** Architecture §3.6 makes competition and
> dormancy pressure the same mechanism, so an object that repeatedly loses allocation stops
> accumulating contribution and is then tombstoned *for having been starved*. That is
> Constitution §22's winner lock-in, imported as a feature. v1.0 requires: (a)
> `contribution_nats` is accumulated only over ticks in which the object was actually evaluated,
> with `n_forward` as its denominator; (b) the ledger reserves a declared exploration quota for
> low-priority objects; (c) a tombstone decision taken on an object whose evaluated-tick count is
> below a declared floor is a `fault`, not a decision.

#### R13 `Policy`

| Facet | Reconciled definition |
|---|---|
| **Scientific definition** | The mechanism under study, made addressable. Constitution Part V's law candidates are claims *about policies*; §54's controls (frozen, random, matched, oracle, decoupled, seeded) are themselves policies. A mechanism that cannot be named, versioned and ablated cannot be evidence. |
| **Computational implementation** | One registered primitive replacing the architecture's three controller classes. Declared domain ∈ {`parametric`, `structural`}; interface `propose(...) → Proposals` and `decide(subject, evidence, ledger) → Decision`. Reads only the subject's own statistics and feedback arriving on its own edges — locality is what lets a shard decide without consensus. Growth and pruning are **the two signs of one criterion**, not two objects (Architecture §4.1); representing them as separate classes contradicted that claim. Every proposal and decision is attributed to a policy name so yields are separately measurable. |
| **Observable state** | Direct: `lifecycle` transitions carry the deciding policy in `cause`; `evidence` carries ΔL, cost and evaluated-tick count; the roster and parameters are in the manifest. |
| **Validation experiment** | E01 (parametric), E07 plasticity frontier, **E10 growth operability before E11 growth necessity**, E12 dormancy, E13 pruning safety, E15 competition, E18 allocation. Required matched arms, all as policy instances: `random_matched`, `error_decoupled`, `designer_seeded`, `frozen`, `oracle`. |
| **Failure modes** | A mechanism shipped without its matched control; retuned margins after a null (forbidden — the null is registered instead); promote/prune thrash; plasticity concentrated in already dominant units; unreported clipping, which is an undocumented change to the mechanism under study; learned/meta-learned policies, which make yields unattributable and are excluded. |
| **Acceptance criteria** | Hysteresis `promote_margin > prune_margin` and `min_tenure_ticks` enforced; `structural_churn` reported; **V5′ (below)**; every claim decided by `science/stats.py` against a preregistered protocol. |
| **Removal criteria** | Per instance, by its own falsifier. Deleting the last policy leaves a static substrate — which is exactly G1, a legitimate configuration. |

> **V5′ — Justified existence, tightened (resolves Contradiction 11).** Architecture V5 requires a
> recorded nats justification exceeding recorded cost. The closed-form ΔL that makes this exact
> exists only for **readout-incident** contributions. v1.0 therefore forbids promoting any object
> whose ΔL is not exactly computable. Interior structure (depth > 1) may be *proposed* and
> *measured*, but its promotion is deferred to G4, where multi-hop credit assignment has its own
> falsifier. Without this rule, V5 silently degrades from a test to an estimate at the first
> promoted second layer.

#### R14 `Intervention` — **added by this reconciliation**

| Facet | Reconciled definition |
|---|---|
| **Scientific definition** | Constitution §6 World layer, §6.1 (`causes` "only when backed by an identified intervention"), §6.3 Causal, and Observatory §14: a declared, scheduled, recorded forcing of system state, distinct from the mechanism under study. |
| **Computational implementation** | A registered record applied at declared ticks to declared target ids: `silence`, `reset`, `freeze`, `perturb`, `mask` (conductance), `lesion` (edge/neuron removal), `replace`, `shuffle`. Applied in a declared phase, with realized effect and compliance recorded. Deliberately **not** a `Policy`: conflating the instrument with the mechanism is how an ablation becomes unattributable. |
| **Observable state** | Direct: `intervention` events (declaration, application, target set, realized separation, compliance, non-compliance reason). |
| **Validation experiment** | It is the enabling object for **E03, E04, E12, E13, E14, E17→(deleted), E18, E19, E21, E23** and for every `causes` relation in the ontology. Its own validation is a positive/negative control pair: a known-necessary target must show loss, a known-redundant target must not. |
| **Failure modes** | Retrospective path selection (target chosen after seeing the outcome); intervention leakage; compensatory paths unmeasured; unmatched ablation presented as causal; non-compliance unrecorded; permanent damage before sufficient probes. |
| **Acceptance criteria** | Every causal plate (V27, V32) renders from `intervention` events alone; targets preregistered in the protocol; matched control interventions (random, activity-matched, contribution-matched) declared in the same protocol. |
| **Removal criteria** | Never, while any causal claim is live. Its absence, not its presence, is what the three input documents got wrong. |

### Tier E — evidence primitives

These fail T1 by construction (they are not runtime state) and are admitted under an explicit
exemption: they are the objects that make T2 and T4 decidable. Nothing in Tier E may be an input
to a runtime computation.

#### E1 `Protocol`

| Facet | Reconciled definition |
|---|---|
| **Scientific definition** | Constitution §37/§53–54 and Observatory §5.1: the preregistered design — hypothesis, conditions, controls and what each removes, estimand, unit of inference, pairing, SESOI/equivalence margin, guardrails, seed generation and tuning/confirmation split, stopping rule, exclusion rule, multiplicity family. |
| **Computational implementation** | Versioned, hashed record in `protocols/`, referenced by `Run`. Frozen before execution; deviations recorded, never edited away. |
| **Observable state** | Class **D** metadata. Renders V04, V05, V31. |
| **Validation experiment** | Its own integrity check: post hoc choices cannot appear preregistered; confirmation seeds are separated. |
| **Failure modes** | Retuned margins; unregistered exclusions; stopping rule altered after inspection; controls declared without stating which confound they remove. |
| **Acceptance criteria** | No result advances past `exploratory-admissible` without a hash-matched protocol frozen before the first run. |
| **Removal criteria** | Never. |

#### E2 `Measurement`

| Facet | Reconciled definition |
|---|---|
| **Scientific definition** | Constitution §6.3 quantity families and Observatory class **V**: a derived statistic with an operational definition, units, direction, formula, estimator version, aggregation rule, coverage, uncertainty and validity status. |
| **Computational implementation** | Registered metric definitions (M1's `science/metrics/` pattern) plus emitted `measurement` events. **All reclassified objects live here:** selectivity/expertise, partition (community detection), depth/hierarchy, synergy/cooperation, allocation entropy/attention, plasticity, novelty-if-ever, modularity Q, structural churn, calibration. |
| **Observable state** | Derived, with mandatory disclosure of inputs, membership rule, weighting, window, included/excluded mass, sampling rule and seed, and distribution — not only a mean. |
| **Validation experiment** | Positive and negative controls per metric (a metric that cannot detect known success and known failure is not a metric). Nulls are named per statistic: shuffled labels for selectivity, degree-preserving rewiring for Q, common-input conditioning for coordination. |
| **Failure modes** | Aggregate concealing sign reversal or subgroup collapse; oracle-dependent metric reported without a valid oracle; known-defective metric (the legacy retention scalar) used for primary inference; threshold or resolution tuning; label switching across detection runs presented as continuity. |
| **Acceptance criteria** | Every decision-bearing metric has direction, units, validity state, known failure modes and a declared null before it appears in a decision. |
| **Removal criteria** | Per metric, when no live claim reads it. |

#### E3 `Claim`

| Facet | Reconciled definition |
|---|---|
| **Scientific definition** | One primitive absorbing Constitution §6's *hypothesis, law, theory* and *Unknown*, plus Observatory's annotation class **A**. They differ only in status level and scope breadth — which §64 already formalises as Levels 0–5. |
| **Computational implementation** | Record with: statement, scope, objects referenced, predicted observations, adverse outcomes, named alternatives, dependencies, status level 0–5, and ten separate confidence dimensions (§63) — existence, measurement validity, effect existence, magnitude, mechanism, robustness, generalisation, necessity over simpler alternatives, resource efficiency, observability completeness. A human annotation enters as a Level-0 Claim with an author. An Unknown is a Claim with no evidence relation. |
| **Observable state** | Class **A**/registry. Renders V08, V33/V36, V35. |
| **Validation experiment** | E24 cross-instance replication is the only route to Level 4; Level 5 additionally requires integration with an independent principle and a novel risky prediction. |
| **Failure modes** | Status advanced because engineering adopted the object; law called supported outside validated scope; conflicting results averaged instead of splitting the claim by scope; ad hoc rescue; annotation cited as fact (structurally impossible: evidence relations accept only Measurements). |
| **Acceptance criteria** | No level advance without the required evidence relations; negative and null results permanent; heterogeneity modelled as a moderator, never averaged away. |
| **Removal criteria** | Never removed; superseded, with lineage retained. |

#### E4 `Evidence`

| Facet | Reconciled definition |
|---|---|
| **Scientific definition** | The typed relation between a `Measurement` (from an admissible `Run` under a `Protocol`) and a `Claim`: supports, opposes, null/indeterminate, invalid, requires-assumption, depends-on. |
| **Computational implementation** | Directed record with source measurement ids, run ids, eligibility state, assumptions relied upon, and the alternatives it fails to exclude. |
| **Observable state** | Class **A**/registry. Renders V07, V08, V31. |
| **Validation experiment** | Evidence-graph completeness is itself checked: orphan evidence, circular support and shared-evidence dependence are detectable defects. |
| **Failure modes** | Correlational evidence typed as causal; evidence from an ineligible run; shared assumption counted as independent replication; broken references. |
| **Acceptance criteria** | Every completed or abandoned experiment produces evidence relations before the run is closed (§66). |
| **Removal criteria** | Never. |

#### E5 `Decision`

| Facet | Reconciled definition |
|---|---|
| **Scientific definition** | Constitution §65–66's Scientific Decision: the recorded consequence — accept within scope, reject, revise, narrow, split, merge, archive, or explicitly no change. The Observatory's terminal state; the unit of value is a decision changed, not a chart. |
| **Computational implementation** | Record linking claim, evidence set, scope, reversibility, blockers, author, time, and supersession lineage. Includes deletion decisions, which §68 defines as scientific successes. |
| **Observable state** | Class **A**/registry. Renders V07 and the Decision overlay. |
| **Validation experiment** | Not applicable; it is what experiments produce. |
| **Failure modes** | Result closed without a decision; decision without linked evidence; silent reversal without lineage; deletion recorded as failure rather than as a result. |
| **Acceptance criteria** | No experiment is complete until validity, observations, evidence, decision, dependency propagation, debt and Living Scientific Model updates are resolved. |
| **Removal criteria** | Never. |


---

## Part 2 — Contradictions and their resolutions

Twenty-two conflicts were found. Each is classified by type, resolved, and given a status:
**Blocking** (must be resolved before the next generation ships), **Locked** (resolved by this
document), or **Constraint** (no contradiction, but a limit that must be recorded).

### 2.1 Architecture requires an object that science or observability rejects

| # | Contradiction | Resolution | Status |
|---|---|---|---|
| **1** | Architecture defines a `Candidate` object **and** a `CANDIDATE` lifecycle state on both `Neuron` and `Edge`. Two representations of one claim, with its own id type, its own state machine and its own snapshot section. | **Delete the object.** A candidate is a `Neuron` or `Edge` in state `CANDIDATE`, with `evidence_nats` and `contribution_nats` as one accumulator read in different lifecycle states. Removes one primitive, one id type, one state machine, one snapshot section, and the "evidence computed against a stale generation" invalidation path. | Locked |
| **2** | `Port` is presented as an object with identity, justified by canonical fan-in order and delay-line re-indexing. But its identity is exactly `(neuron_id, index)`, and width/role are declarations of the `Kind`. | **Delete as a primitive**; retain as a typed address alias. The canonical reduction order `(dst.index, src.neuron)` becomes an invariant, not an object. Delay-line values are preserved by `(neuron_id, out_index)`, which is already stable. | Locked |
| **3** | `Feedback` is an object, while `Signal` — its exact mirror — was explicitly declined as an object for allocation reasons. Its `source` field is derivable from `Tick.mode` and the emitting subject. | **Delete.** Both directions are transient array slots, observable as `signal` events with a direction. Symmetry restored; one event kind instead of two objects. | Locked |
| **4** | `Schedule` (§5.2) duplicates `Graph.instant_order` / `Graph.wavefronts` (§2.5). Two caches of one derivation, each keyed by generation. | **Delete.** Derived state of `Graph`, keyed by `generation`. | Locked |
| **5** | Three controller classes (`Plasticity`, `Growth`, `Pruning`) contradict §4.1's own central claim that all four structural decisions are **one criterion in one unit, sign reversed**. A second interface would need its own unit, justification and null. | **Merge into `Policy`** with a declared domain. Growth and pruning are the two signs of one criterion; `random_matched`, `error_decoupled`, `designer_seeded`, `frozen` and `oracle` become policy instances rather than special cases. | Locked |
| **6** | `Community` and `Module` are two object types for what §8.3–8.4 describes as one thing at two stages, and neither influences computation before G4/G5. | **Community becomes a `Measurement`** (a partition is a derived statistic with an algorithm version — precisely class V). **`Module` is deferred**: a conditional primitive admitted only on G4 evidence (Q above the rewiring null, partitions persisting) *and* G5 necessity (shard boundary contract). The shard constraint itself needs only `Neuron.shard` plus the placement invariant, both of which survive. | Locked |
| **7** | `EnergyLedger` converts compute to nats at a config exchange rate. Constitution §15 names exactly this — "incommensurate terms added; arbitrary coefficients" — as an energy failure mode, and Architecture A4 concedes the risk. | **Rename to `Ledger`; ban the word *energy*** from v1.0 state, events and results. Charges are evaluation counts. The exchange rate is a `Policy` parameter in the manifest, and **exchange-rate sensitivity analysis becomes a G2 acceptance gate**, not an appendix: a finding that does not survive a declared rate range is a finding about a tuned constant. | Locked |
| **8** | Architecture stores `selectivity` in `NeuronStats`, but no policy in G1–G3 reads it, and §3.5 explicitly says a policy *would* be the mechanism if it were ever needed. State with no computational consequence is the decorative architecture the design forbids. | **Move to `Measurement`.** General rule (Art. L-6): `stats` contains exactly the accumulators read by an active `Policy`; everything else is a Measurement. This bounds per-object state growth permanently. | Locked |

### 2.2 Science requires an object that has no computational existence or cannot be measured

| # | Contradiction | Resolution | Status |
|---|---|---|---|
| **9** | **Novelty** (§13) is a full object card with experiment E08, but has no computational existence anywhere in the architecture and no live hypothesis requires it. | **Delete from v1.0.** Restorable only by amendment, when a live claim requires a density/reference model that `loss` cannot supply. E08 is withdrawn with it. | Locked |
| **10** | **Surprise** (§14) is defined as `-log P(outcome | information before t)`. That is bit-for-bit the readout's scoring loss, which already exists, is already emitted, and already drives the existing replay gate. | **Merge.** Surprise is a declared alias of the per-step loss, not an object. Every surprise-timed mechanism is a `Policy` reading that value. | Locked |
| **11** | **Synchronization** (§24) requires phase/lag statistics beyond common drive. The substrate is a globally clocked discrete tick: every neuron in a wavefront is trivially simultaneous, and DELAYED edges give exactly lag 1. There is no free temporal parameter, so no coordination statistic is identifiable beyond common input — and Architecture §13 excludes continuous time for independent reasons. | **Delete the object and E17.** Not implementable, not identifiable, not observable. Restorable only if per-object update periods or continuous time are ever introduced, which would itself require an amendment. | Locked |
| **12** | **Reproduction** (§35) requires parentage and inherited state. Architecture has exactly two birth paths (seeded, proposed), no parent field, and derives initialisation from the object's **own id** — which is what makes initialisation order-independent and shard-local. Parent-conditioned initialisation would break that property. | **Delete from v1.0.** Lineage is `birth_cause` (an event pointer), which answers "why do I exist?" without a parentage graph. Inheritance, if ever justified, arrives as declared `hints` on a proposal — a field, not a primitive, and E11's reproduction arm is withdrawn until then. | Locked |
| **13** | **Hierarchy** (§18) and **Circuit** (§20) are object cards; the architecture derives depth from the INSTANT DAG and treats pathways as queries, because materialising either creates state that can drift from the graph. | **Reclassify both as `Measurement` + query.** E20 (depth, cross-level fraction, directional intervention) and E21 (sequence reliability under stage-specific perturbation) remain runnable over derived state plus `Intervention`. | Locked |
| **14** | **Attention** (§21) is an object card; the architecture deletes it (its whole state is `Edge.conductance`); the Observatory currently must render "construct not present". Three positions, three vocabularies. | **One position:** attention is a `Measurement` (allocation entropy, concentration, coverage) over `Edge.conductance`, produced by a gate `Kind`, intervened on by `mask`. Observatory V26/V27 are **renamed Allocation / Allocation Intervention** and become admissible at G3 — not before, and never by relabelling gate activity. | Locked |
| **15** | **Competition** (§22) and **Cooperation** (§23) are object cards with no computational counterpart. | Competition **is** the `Ledger` operating at capacity (one mechanism producing allocation, competition and the pruning signal). Cooperation is a `Measurement`: the log-linear readout makes exact synergy and redundancy over subsets closed-form, so E16 needs no new object and no re-runs. | Locked |
| **16** | **Memory** (§9) is one object; the architecture keeps three mechanisms and states that conflating them was a real historical defect. | **Memory is a role, never an object.** Two carrier primitives (`DelayLine`, `EpisodicMemory`) plus `Neuron.params`. E05 is run separately per carrier. | Locked |
| **17** | Six lifecycle stages — Nascent, Developing, Expert, Generalist, Reactivated, Reproducing (§26) — have no scheduler consequence. `PROPOSED`, `REJECTED` and `EXPIRED` are likewise indistinguishable to the scheduler from "does not exist" and "deleted". | **Lifecycle frozen at five states**: `CANDIDATE → ACTIVE ⇄ DORMANT → TOMBSTONED → DELETED`, plus `TOMBSTONED → ACTIVE` (revive) and `CANDIDATE → DELETED` (reject/expire/evict, distinguished by cause on the transition event). Expert/Generalist/Developing become Measurements. Edges use the subset without `TOMBSTONED`. Down from 12 stages and 3 machines to 5 states and 1 machine. | Locked |

### 2.3 Implementation or measurement is impossible as specified

| # | Contradiction | Resolution | Status |
|---|---|---|---|
| **18** | **The exactness claim does not survive depth.** §1.3/§4.1 make ΔL exact *because* the readout is log-linear — true only for readout-incident contributions. §8.1 and A2 simultaneously want arbitrary depth. At the first promoted second layer, V5 silently degrades from a test to an estimate, and growth/pruning lose their single unit. | **V5′:** no promotion of an object whose ΔL is not exactly computable. Depth may be proposed and measured; promotion beyond readout-incident contributions is deferred to G4 where multi-hop credit has its own falsifier. | **Blocking** for G2 design |
| **19** | **Starvation causes pruning.** §3.6 makes competition and dormancy pressure the same mechanism; a neuron that loses allocation stops accumulating contribution and is then tombstoned for it. Constitution §22/§41 require guardrails against exactly this collapse. | Three-part guardrail under R12: contribution accumulated only over evaluated ticks; a declared exploration reserve in the ledger; tombstoning below an evaluated-tick floor is a `fault`, not a decision. | **Blocking** for G2 |
| **20** | **Calibration is unmeasurable as specified.** Observatory §4.1.8 and V12, and Constitution §12, require calibration; the architecture emits `loss` but not the predictive distribution, so no calibration statistic is computable from the log. | The `predict` event must carry the distribution or declared sufficient statistics at a declared resolution. An emission fix, not a new primitive. | **Blocking** for G1 |
| **21** | **Replay content is unattributable as specified.** Observatory V18 requires selected item ids, source regime, age and weight; M1 records only realized counts, and the architecture inherits the `Memory` contract unchanged. Buffer contents must not be used to reconstruct selections. | `memory` events extend to admit / evict / **select**, carrying item id and provenance. Contract unchanged; emission extended. | **Blocking** for the live replay programme |
| **22** | **Sequencing inversion.** Constitution §74 designates E01 and E02 as the smallest next scientific step and says explicitly: run them *before* investing in growth, reproduction, hierarchy or communities. Architecture G2 opens with a growth claim and never runs E02 as a claim — although it already ships the required control, since `count_model` **is** the anonymous shared-state condition. | **G1's acceptance gate is extended:** count-equivalence (a null by construction) **plus E01 plus E02** as registered claims. G2 does not begin until E02 shows a discriminating advantage for persistent identity. If E02 is null, the `Neuron` primitive is amended, not defended. | **Blocking** for G2 |

### 2.4 Constraints recorded (not contradictions)

| # | Constraint | Consequence |
|---|---|---|
| **C-a** | The dynamic stream is admittedly lossy at 10⁵+ (§6.5), while Observatory §20.7 blocks claims outside the observed subset and Constitution §70 requires disclosed omitted mass. | Unit- and edge-level claims require D0/D1 runs with the relevant stream complete. Population claims require `stream_meta` coverage disclosure and one prespecified sampling-sensitivity check. No exceptions at 10⁶. |
| **C-b** | Observatory acceptance 20.2.5 (identical outputs with collection enabled and disabled) is only definable under bit-exactness. | The non-interference test is defined for **D0 only**; D1 runs assert it within a fixed layout; D2 runs may never be offered as confirmatory evidence. |
| **C-c** | G4's emergence claim (modularity Q above a rewiring null, partitions persistent) names two of the six clauses Constitution §52 requires. | G4 acceptance must additionally carry: absent-at-initialisation, treatment operability, designer-injection audit, and independent seed replication. The missing arms are policy instances (`error_decoupled`, `designer_seeded`), not new objects. |
| **C-d** | Constitution §61 versions ontology types; the architecture versions kinds and records. | A material change to any primitive's identity, state boundary or transition set creates a successor ontology version with an explicit cross-version mapping and a loss-of-meaning statement. Old records retain their original semantics. |

---

## Part 3 — Missing objects

### 3.1 Required by science, missing from the architecture

| Missing | Required by | Verdict |
|---|---|---|
| **`Intervention`** | §6.1 (`causes` requires an identified intervention), §6.3 Causal, §33 (pruning is an experiment before it is a transition), §34 (staged disablement with rollback), and 9 of the 22 retained experiments. Observatory §14, V27, V32. | **Added as R14.** The largest gap in all three documents. `PROBE` mode disables plasticity but cannot silence, mask, lesion, perturb or replace, and records no compliance. Without this primitive the entire causal programme is aspiration. |
| **`Run` / manifest as an object** | §57 provenance and artifact identity; Part X.1; Observatory V01, which is **Priority 0** — the gate on whether any Observatory output may enter durable Discovery records. | **Added as R1.** The architecture references manifest *fields* (determinism tier is "a required manifest field") but never catalogues the object that holds them. |
| **`Protocol`** | §37 law format, §53–54 experiment matrix, Observatory §5.1, V04/V05/V31. | **Added as E1.** The architecture defers to "a preregistered protocol in the M2 `protocols/` form" without giving it object status, so nothing in the runtime can be checked against it. |
| **Starvation guardrail and exploration reserve** | §22 (starvation, diversity collapse), §41 (scarcity-conditioned allocation must not harm guardrails). | **Added to R12.** A mechanism, not an object. |
| **`error_decoupled` and `designer_seeded` control arms** | §52 emergence clauses, E11, E22. | **Added as `Policy` instances.** `random_matched` alone matches capacity and rate but not error-coupling, and audits no injection. |

### 3.2 Implemented (or specified) but scientifically unnecessary

| Object | Judgement |
|---|---|
| `Candidate`, `Port`, `Feedback`, `Schedule`, three controller classes, `Community`+`Module` as objects | Deleted or merged — Part 2.1. None is required by a live claim; each duplicated a representation that already existed. |
| `Signal` as an object | Already declined by the architecture. Confirmed: transient slot, observable as an event. |
| `selectivity` as state | Reclassified as a Measurement. No policy reads it in v1.0. |
| Six lifecycle stages, `PROPOSED`/`REJECTED`/`EXPIRED` | Deleted. No scheduler consequence; causes recorded on transition events instead. |
| Nats↔compute conversion inside the ledger | Removed from the object; retained as a manifest-recorded policy parameter under mandatory sensitivity analysis. |

### 3.3 Observable, or scientifically named, but with no computational existence

| Named object | Verdict |
|---|---|
| Novelty, Synchronization, Reproduction | **Deleted.** No implementation, and for synchronization no identifiability in a clocked substrate. Amendment paths recorded. |
| Attention, Competition, Cooperation, Hierarchy, Circuit, Plasticity, Expertise, Emergence, Prediction, Identity, Memory | **Reclassified**, not deleted: each becomes a Measurement, a role, an Event, a facet, or a Claim over the 14 runtime primitives. Every associated law candidate and experiment survives; only the object entries disappear. |
| Observatory V13/V16/V18/V21–V27 ("not currently supportable") | **Reclassified as gated, not impossible.** Their blocker was the substrate having no units, edges, candidates or item-level records — which G1/G2 supply. The gap register becomes a generation gate: each plate turns on when its events exist, and not by inference. |
| Predictive distribution, replay selections | **Missing emissions, not missing objects** — Contradictions 20 and 21. |


---

## Part 4 — Simplification ledger

### 4.1 What was removed, and what it cost

| Reduction | Before | After | Explanatory power lost |
|---|---|---|---|
| Primitives | 20 architecture objects + 19 science object cards | **19** (14 runtime, 5 evidence) | None. Every deleted object's claims are carried by a Measurement, an Event, a lifecycle state, or a Claim. |
| Id types | `NeuronId`, `EdgeId`, `CandidateId`, `ObjId` | `NeuronId`, `EdgeId` (+ content addresses) | None. Candidates are neurons and edges. |
| Lifecycle | 8 + 4 + 4 states across 3 machines; 12 science stages | **5 states, 1 machine, declared subsets** | None. Every deleted state had no scheduler consequence; its information survives as a transition cause. |
| Event kinds | 44 | **16** | None. Lifecycle transitions collapse to one kind with `(from, to, cause)`; six fault kinds to one typed kind; `probe` becomes `tick(mode=PROBE)`; `replay_batch` becomes `tick(mode=REPLAY)` + `memory(select)`; `community_snapshot` becomes `measurement`. |
| Overlays | 18 | **8** | None. Construct validity became a field of `Measurement`; provenance, rigor stage and eligibility are one admissibility overlay because they are all fields of one manifest. |
| Plates | 36 | **30** | None. Six merges, each between plates that fold the same events at different zoom or scope — which the Observatory's own semantic-zoom principle says is one plate. |
| Interfaces | 5 | **4** | None. §10.1's pure kernel and §9.2's permanent reference implementation are the same oracle under two names. |
| Experiments | 24 | **22** | E08 and E17 fall with novelty and synchronization. |
| Law candidates | 15 | **11** | Novelty/surprise dissociation, synchronization, reproduction and the metaphorical-energy law disappear; competition and attention laws survive as laws about the `Ledger` and about conductance. |
| Controllers | 3 protocols | 1 `Policy` protocol, 2 domains | None. §4.1 already claimed one criterion; three interfaces contradicted it. |
| Memory objects | 1 science object vs 3 mechanisms | 2 carrier primitives + `params` | Nothing, and the historical conflation defect stays structurally impossible. |

### 4.2 Merges performed

| Merged into | From |
|---|---|
| `Neuron` / `Edge` lifecycle state `CANDIDATE` | `Candidate` object, `CandidateId`, candidate state machine, snapshot `candidates` section |
| `Edge` address fields + `Kind` arity | `Port` |
| `signal` event | `Signal` slot, `Feedback` object, `activation` and `feedback` kinds |
| `Graph` (derived, keyed by generation) | `Schedule`, `instant_order`, `wavefronts`, layer/depth indices |
| `Policy` | `PlasticityController`, `GrowthController`, `PruningController`, and all matched-control special cases |
| `Measurement` | Community, hierarchy, circuit, attention, cooperation, plasticity, expertise, selectivity, modularity Q, allocation entropy, depth |
| `Claim` | hypothesis, law, theory, Unknown, annotation |
| per-step loss | surprise |
| `contribution_nats` | `evidence_nats` (one accumulator, two lifecycle states) |
| `fault` event with a type | `neuron_fault`, `edge_fault`, `feedback_fault`, `energy_starved`, `delay_default`, `plasticity_clip` |

### 4.3 Merges considered and declined

| Proposed merge | Declined because |
|---|---|
| `Kind` + `Policy` → one "Rule" primitive | Different necessity proofs and different failure modes. Only `Kind` declares `cost_nats`, on which V5′ depends; only `Policy` is a per-run singleton whose yield must be attributable. Merging would blur the mechanism under study with the transformation being studied. |
| `Snapshot` → an `Event` payload | Snapshot is state, not occurrence, and is content-addressed rather than run-addressed. Rollback exactness depends on per-substream RNG states that a decimated stream cannot supply. |
| `DelayLine` + `EpisodicMemory` → one "Carrier" primitive | The Constitution's own finding: conflating activation and episodic memory was a real defect. Different timescales, write phases, indexing and eviction, and E05 must distinguish them. |
| `DelayLine` → per-edge latched value | O(E) instead of O(V) storage, duplicated values per fan-out, and a second writer to edge state. |
| `Intervention` → a `Policy` instance | Mechanically possible, scientifically fatal: the instrument would become indistinguishable from the mechanism under study, and no ablation could be attributed. |
| `Tick` → `Event(kind=tick)` only | `mode` must be an addressable property of the unit that events, budgets and snapshots are keyed on, not a payload field of one event. |
| `Ledger` → a field of `Graph` | Different write phase, different lifetime (per-tick flow vs per-generation structure), and its own settle record. |
| `Community` → keep as a primitive for G5 sharding | The shard constraint needs only `Neuron.shard` plus the placement invariant. The object is not required until promotion has evidence. |

### 4.4 Ontology-growth bound

Two rules keep the ontology from re-inflating without anyone deciding to inflate it:

- **Art. L-6 (state bound):** an object's `stats` contains exactly the accumulators read by an
  active `Policy`. Anything else is a `Measurement`.
- **Art. L-7 (state bound):** a lifecycle state exists only where the scheduler treats the object
  differently. Anything else is a transition cause or a Measurement.

Both are mechanically checkable, which is why they are in the lock rather than in a review
checklist.

---

## Part 5 — The frozen primitive set

### 5.1 Canonical list

**Tier R — runtime (14):**
`Run`, `Environment`, `Tick`, `Event`, `Snapshot`, `Neuron`, `Kind`, `Edge`, `Graph`,
`DelayLine`, `EpisodicMemory`, `Ledger`, `Policy`, `Intervention`.

**Tier E — evidence (5):**
`Protocol`, `Measurement`, `Claim`, `Evidence`, `Decision`.

**Conditional (1, not yet admitted):**
`Module` — admissible only on G4 evidence (modularity above a degree-preserving rewiring null,
partitions persistent across detection runs) **and** demonstrated G5 necessity (a boundary
contract required for sharding that `Neuron.shard` cannot satisfy). Until then, promoted
organization does not exist.

### 5.2 Admission test for any future primitive

A candidate primitive is admitted only by satisfying all four tests **with evidence**, recorded
in a `Decision` that cites `Measurement`s from admissible `Run`s:

1. **Computational necessity.** Removing it changes what the engine computes, or makes a named
   invariant (V1–V5′, I1–I3) untestable. A convenience, a cache, or a second representation of
   existing state fails this test.
2. **Scientific necessity.** A live `Claim` requires it, its deletion is a runnable null, and no
   existing primitive can state its scientific role.
3. **Observability necessity.** Its full decision-relevant state can be emitted, folded and
   rendered without invention, with declared missingness and coverage.
4. **Experimental necessity.** At least one registered experiment becomes runnable *because* it
   exists, and that experiment can produce adverse evidence against the primitive itself.

Failing test 1 makes it a `Measurement`. Failing test 2 makes it decoration. Failing test 3 makes
it hidden state. Failing test 4 makes it speculation. There is no fifth outcome and no
provisional admission.

### 5.3 What may still be added without amendment

Only instances of existing primitives, and only with a falsifier:

- new `Kind` registrations (each is a treatment; ships with its own null);
- new `Policy` registrations (each ships with its matched control);
- new `Measurement` definitions (each ships with its declared null and validity state);
- new `Environment` registrations (each ships with an oracle or an explicit absence);
- new `Intervention` types drawn from the declared set;
- new `Protocol`, `Claim`, `Evidence`, `Decision` records.

This is where all future growth belongs. A decade of work fits inside it.

---

## Part 6 — P1-v2 Core Primitive Table

`M` = Measurement. Events are from the 16-kind set (Appendix C). Plates are the reconciled
30 (Appendix B).

| Primitive | Purpose | State | Events | Measurements | Validation experiment | Observatory view | Acceptance gate |
|---|---|---|---|---|---|---|---|
| **Run** | Makes a run's evidence admissible or not | manifest: config/commit/seeds/tier/status/artifacts | `run` | admissibility, coverage, overhead | apparatus repeat-identity | V01 | D2 refused for confirmatory; V01 renders from manifest alone |
| **Environment** | Supplies observation, target, regime, oracle | registered identity, seed, regime schedule | `predict` | excess loss, regime distance | non-triviality precondition (E11/E22) | V09 | valid oracle; boundaries prespecified |
| **Tick** | Logical time; separates online/replay/probe | index, mode, graph_generation | `tick`, `ledger` | realized dose, update counts | E06 | V02, V17 | phase order; probe produces no delta |
| **Event** | Immutable record; the system of record | seq, kind, tick, phase, subject, cause, payload | all 16 | drop rate, coverage, omitted mass | enables all 22 | V02, all | V1 fold is bit-exact; `test_no_engine_import` |
| **Snapshot** | Exact state for rollback and reconstruction | full state + per-substream RNG + memory | `checkpoint` | reconstruction completeness | prerequisite of E13/E23 | V03, V14 | load-and-tick equals live hash |
| **Neuron** | Persistent identifiable adaptive unit | id, kind, params, policy-read accumulators, lifecycle, shard | `lifecycle`, `param_update`, `signal`, `evidence` | contribution, selectivity (M), tenure, turnover | **E01, E02**, E03 | V21, V24 | G1 count-equivalence, then **E02 discriminating advantage** |
| **Kind** | Declares behaviour, arity and own cost in nats | name, version, arity, cost function | `lifecycle` (birth payload) | cost, yield per kind | E01 | V21 | `(name, version)` resolution of old logs; purity |
| **Edge** | Transform-and-transmit relation; the only value channel | endpoints, weight, delay class, conductance, lifecycle | `lifecycle`, `edge_state` | transmission, conditional contribution, redundancy | **E04** | V25, V26 | effect exceeds matched-random edge lesions |
| **Graph** | Sole structural mutator; topology of record | generation; derived order and wavefronts | `lifecycle`, `structure_reject` | depth (M), churn, modularity Q (M) | E19, E20 | V21, V22, V23 | V3; atomic batch rejection |
| **DelayLine** | Activation memory; the only recurrence path | latched outputs by (neuron, out index) | `signal`, `fault` | carrier effect, lag-1 dependence | **E05** | V24 | DELAYED reads order-independent |
| **EpisodicMemory** | Bounded historical carriers | items with provenance, occupancy, eviction | `memory` | coverage, age/task composition, realized dose | **E05, E06** | V15, V16+V18 | selection ids logged; realized-dose equivalence |
| **Ledger** | Named scarcity and resource truth | capacity, spent, per-object charges, reserve | `ledger`, `fault` | outcome per resource, starvation, concentration | **E09, E15** | V06, V34 | reconciles with an independent counter; exchange-rate sensitivity |
| **Policy** | The mechanism under study, addressable and ablatable | name, version, domain, parameters | `lifecycle` cause, `evidence` | operability, dose, yield, churn | **E07, E10, E11, E12, E13, E18** | V05, V22 | matched control ships with it; **V5′**; hysteresis |
| **Intervention** | Makes causal claims possible | type, targets, schedule, realized separation, compliance | `intervention` | effect, compliance, compensation | **E03, E04, E13, E14, E19, E21, E23** | V27, V32 | positive/negative control pair; targets preregistered |
| **Protocol** | Preregistered design | conditions, estimand, SESOI, guardrails, stopping rule | — (referenced by `Run`) | protocol integrity | own integrity check | V04, V05, V31 | frozen and hashed before first run |
| **Measurement** | Every derived statistic, with its null | definition, units, direction, version, validity, coverage | `measurement` | itself | positive/negative controls per metric | V09–V14, V23, V28 | direction, units, validity and null declared before use |
| **Claim** | Hypothesis, law, theory, Unknown, annotation | statement, scope, level 0–5, 10 confidence dimensions | — | confidence dimensions | **E24** for level 4 | V08, V33/V36, V35 | no level advance without required evidence |
| **Evidence** | Typed relation from measurement to claim | type, sources, eligibility, assumptions, unexcluded alternatives | — | graph completeness | evidence-graph audit | V07, V08, V31 | produced before a run is closed |
| **Decision** | Recorded scientific consequence | claim, evidence set, scope, reversibility, lineage | — | decision latency, reversal rate | — | V07 | no experiment complete without one |

---

## Part 7 — The Constitution Lock

**This is Version 1.0. Everything after this point is implementation.**

### Article L-1 — Frozen ontology

The primitive set of Part 5.1 is closed: 14 runtime primitives, 5 evidence primitives, and one
conditional primitive (`Module`) that does not yet exist. No other object type may be created,
and no deleted object may return, except by amendment under Art. L-9.

### Article L-2 — Frozen lifecycle

One state machine: `CANDIDATE → ACTIVE ⇄ DORMANT → TOMBSTONED → DELETED`, with
`TOMBSTONED → ACTIVE` and `CANDIDATE → DELETED`. Edges use the subset without `TOMBSTONED`.
Every transition emits `lifecycle` with `from`, `to` and `cause`. A state reached without an
event does not exist. No sixth state may be added without demonstrating that the scheduler
treats it differently.

### Article L-3 — Frozen event set

Sixteen kinds (Appendix C), six tiers. Kind ids are append-only and never renumbered; `obs/1`
streams remain decodable. FAULT and STRUCTURAL tiers are undroppable — a suppressed fault is a
fabricated healthy run. Loss is legal; silence is not.

### Article L-4 — Frozen vocabulary

The words *energy*, *attention*, *thought*, *understanding*, *belief*, *curiosity*, *dream*,
*emotion*, *intention*, *consciousness* may not name state, events, fields or results. Measured
resources are named by what they measure (evaluations, operations, bytes, seconds). Allocation is
named allocation. Any anthropomorphic term appearing in a result is a defect, reportable as such.

### Article L-5 — One criterion

All four structural decisions (add neuron, add edge, remove edge, remove neuron) are decided by
`ΔL = contribution_nats − cost_nats − maintenance_nats`, with hysteresis
`promote_margin > prune_margin`. A second structural criterion may not be introduced. **V5′:** no
object is promoted whose ΔL is not exactly computable. The nats-per-evaluation exchange rate is
the single free parameter, lives in config, is recorded in every manifest, and every claim that
depends on it must survive a declared sensitivity range.

### Article L-6 — State bound

An object's `stats` contains exactly the accumulators read by an active `Policy`. Every other
quantity is a `Measurement`. Adding a field to an object requires naming the policy that reads it.

### Article L-7 — Derivation preference

Anything computable from the primitives is computed, not stored: depth, wavefront membership,
pathways, partitions, hierarchy, selectivity, synergy, allocation concentration. A stored copy of
derivable structure is hidden state by definition, because the two can disagree.

### Article L-8 — Evidence separation

Tier E records may never be inputs to a runtime computation. `Claim`s at level 0 (including human
annotations) may never appear as computational facts. `Evidence` relations accept only
`Measurement`s from `Run`s whose eligibility permits the intended rigor stage. The Observatory
may prepare and annotate; it may never write model state, memory, thresholds, seeds, treatment
assignment or active run configuration.

### Article L-9 — Amendment by evidence only

The Constitution changes only through a `Decision` citing `Measurement`s from admissible `Run`s.
Specifically:

| Change | Required evidence |
|---|---|
| Add a primitive | All four tests of Part 5.2, each cited, plus a registered experiment capable of adverse evidence against the new primitive |
| Restore a deleted object | The evidence that its deletion criterion is now false — recorded per object in Part 2 |
| Delete a primitive | Its removal criterion in Part 1 is met |
| Promote `Module` | G4 organization evidence **and** demonstrated G5 necessity |
| Amend `Neuron` | An **E02 null**: persistent identity adds no predictive, adaptive or causal-localisation value over anonymous matched state |

Arguments from elegance, biological precedent, engineering convenience, visual appeal or
implementation momentum are not evidence. Deletion by evidence is a scientific success and is
recorded as one.

### Article L-10 — Order of work

No generation begins until the previous generation's falsifier has been run and its result
registered — including registration of nulls in the negative-results registry, which may not be
retried with new margins.

```
G1 substrate + count-equivalence + E01 + E02   ← gate: persistent identity must earn its place
  └─▶ G2 structural plasticity (E10 then E11)  ← needs a non-trivial environment with an oracle
        └─▶ G3 routing and allocation (E18, E03)
              └─▶ G4 organization and depth (E19, E20, E22)
                    └─▶ G5 scale and longevity (E23, E24)
```

### Article L-11 — Registration

This document has no normative authority until it is registered in `GOVERNANCE_REGISTRY.yaml`
with a status, jurisdiction and authority assignment, as `REPOSITORY_CONSTITUTION.md` requires.
The same obligation binds the three input documents, none of which is currently registered.
Implementation may proceed against an unregistered lock only as engineering-only work producing
no admissible evidence.

### Article L-12 — Closure

The three input documents remain the reasoning behind this lock and are superseded only as to
ontology. Where they name an object this document deleted, reclassified or merged, this document
governs. Where they describe mechanism, measurement or method, they remain the reference.

---

## Appendix A — Reconciled experiment set (22)

| ID | Target | Primitives exercised | Gate |
|---|---|---|---|
| E01 | Local learning calibration | Policy(parametric), Kind, Neuron | G1 |
| **E02** | **Persistent-unit necessity** | Neuron vs `count_model` anonymous state | **G1 — blocks G2** |
| E03 | Specialisation discrimination | Measurement(selectivity), Intervention | G3 |
| E04 | Connection causality | Edge, Intervention | G2 |
| E05 | Historical-carrier assay | DelayLine, EpisodicMemory, Intervention | G2 |
| E06 | Replay content × timing factorial | EpisodicMemory, Tick(REPLAY), Policy | live programme |
| E07 | Plasticity frontier | Policy(parametric), Environment | G2 |
| E09 | Resource-budget response | Ledger | G2 |
| E10 | Growth operability | Policy(structural), lifecycle events | G2 precondition |
| E11 | Growth necessity | Policy(structural) vs `random_matched`, `error_decoupled` | G2 claim |
| E12 | Dormancy and reactivation | lifecycle, Ledger | G2 |
| E13 | Pruning safety and value | Intervention, lifecycle | G2 |
| E14 | Replacement equivalence | lifecycle, Intervention | G2 |
| E15 | Competition under scarcity | Ledger | G3 |
| E16 | Cooperative synergy | Measurement(synergy), Intervention | G3 |
| E18 | Allocation advantage | Kind(gate), Edge.conductance, Intervention | G3 |
| E19 | Partition validity | Measurement(partition), Intervention | G4 — gates `Module` |
| E20 | Depth necessity | Measurement(depth), Intervention | G4 |
| E21 | Circuit causality | Graph query, Intervention | G4 |
| E22 | Emergence discriminator | Claim + all six §52 clauses | G4 |
| E23 | Damage and recovery | Intervention, Snapshot | G5 |
| E24 | Cross-instance replication | Claim level 4 | G5 |

Withdrawn: **E08** (novelty–surprise dissociation) with `Novelty`; **E17** (synchronization
causality) with `Synchronization`. Both restorable only with their objects.

## Appendix B — Reconciled Observatory set

**Plates: 30.** Unchanged: V01–V05, V07–V12, V14, V15, V17, V19, V23, V28–V32, V34, V35.
Merged: V06+V20 → resource matching including replay dose; V16+V18 → carrier lineage and
selection; V21+V22 → structural inventory and change history; V24+V25+V13 → object and population
state history (one plate, parameterised by `subject`, at three zooms); V33+V36 → alternative
explanation and theory discrimination.
Renamed: V26 → Allocation, V27 → Allocation Intervention (sourced from `edge_state.conductance`;
never from relabelled gate activity).

**Overlays: 8.** Admissibility (provenance + rigor stage + eligibility), Directness (D/R/V/A),
Design (treatment, control identity, intervention type, compliance), Resource (realized budgets),
Coverage (total/rendered/sampled/omitted/dropped/missingness), Uncertainty, Blinding, Decision
(including supersession, debt, negative knowledge, surviving alternatives). Construct validity
ceased to be an overlay: it is a field of `Measurement`.

**Zoom levels: 8**, each mapping to exactly one primitive: Run → subsystem (`Graph`,
`EpisodicMemory`, `Ledger`, `Policy`) → population (`Measurement` partition) → object
(`Neuron` | `Edge`) → `Event` → history (`Tick` range) → `Protocol` → `Claim`. The former
"Theory" level is `Claim` at level 5.

## Appendix C — Frozen event kinds (16)

| Tier | Kinds | Droppable |
|---|---|---|
| **STRUCTURAL** | `run`, `lifecycle`, `structure_reject` | no |
| **DYNAMIC** | `tick`, `predict`, `param_update`, `edge_state`, `signal`, `evidence`, `ledger` | yes (absolute values only) |
| **MEMORY** | `memory` (admit / evict / **select**) | no |
| **MEASUREMENT** | `measurement`, `checkpoint`, `stream_meta` | no |
| **INTERVENTION** | `intervention` | no |
| **FAULT** | `fault` (typed: neuron, edge, feedback, starved, delay_default, clip, tick, run) | no |

Required payload additions relative to the input architecture: `predict` carries the predictive
distribution or declared sufficient statistics (Contradiction 20); `memory` carries selection with
item provenance (Contradiction 21); `evidence` carries evaluated-tick count alongside ΔL
(Contradiction 19); `lifecycle` carries the deciding policy name in `cause` (attribution of yield).

---

## Closing test

Nineteen primitives remain. For each, deletion has a named consequence: an invariant becomes
untestable, an experiment becomes unrunnable, a view becomes an invention, or a claim becomes
unattributable. Nine named objects were deleted, eight reclassified as measurements, seven merged,
three primitives plus mandatory guardrails and control-policy instances were added. Twenty-two contradictions are resolved; five of them block work that was about to
begin.

The one primitive whose necessity is still unproven is `Neuron` itself — and the experiment that
could remove it, E02, is now the first gate rather than an afterthought. That is the correct
state for a constitution whose subject is a hypothesis.
