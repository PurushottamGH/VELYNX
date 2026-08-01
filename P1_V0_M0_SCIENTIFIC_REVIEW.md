# Project P1 v0 / M0 Scientific Review

- **Reviewer role:** Principal Scientist
- **Review date:** 2026-07-28
- **Scope:** Scientific evidence produced by the P1 v0 M0 rig
- **Reviewed revision:** Working tree based on Git `3deb076`; `p1v0/` and `tests/v0_rig/` were uncommitted at review time
- **Decision:** **APPROVE WITH REQUIRED EXPERIMENTS**

## Review basis

The reviewer inspected the current `p1v0/` source, `tests/v0_rig/test_p1v0_rig.py`, available run artifacts, and reproduced the reported default run. The command equivalent to `python -m p1v0.runner --variant all --seed 0 --no-artifacts` reproduced:

| Variant | Tail online log loss | Mean forgetting (“retention” field) | Replay updates |
|---|---:|---:|---:|
| online | 0.6849 | +2.4516 | 0 |
| replay_always | 1.1819 | +0.6405 | 32,000 |
| replay_surprise | 0.7593 | +1.4761 | 4,292 |

The nine rig tests also passed. This establishes computational reproducibility in the reviewed environment, not scientific generality.

# 1. Milestone Assessment

## Demonstrated results

1. **The rig executes deterministically for a fixed configuration and seed.** A repeated in-process execution is bit-identical under the tested environment. This is an engineering and measurement precondition.
2. **The reported seed-0 values are reproducible.** The three aggregate values and replay counts match the report.
3. **The count predictor learns the current synthetic Markov task.** Tail loss is below the uniform predictor’s `ln(8) = 2.079` nats for the tested task stream.
4. **The deliberately decaying shared count table loses predictive performance on earlier task probes after later blocks.** Under the implemented forgetting metric, online training has positive mean degradation on the first three tasks.
5. **Unconditional reservoir replay reduces measured seed-0 forgetting relative to no replay in this rig.** The observed difference is 1.811 nats in mean forgetting, accompanied by 32,000 additional replay updates.
6. **The surprise-triggered condition produces an intermediate seed-0 point.** It uses 4,292 replay updates, with lower forgetting than online and higher forgetting than unconditional replay.
7. **Probe evaluation is read-only and generated from task distributions using a separate random draw.** This reduces direct train/probe sample reuse, although the generator parameters are shared.

## Inferred conclusions

These are plausible descriptions of the seed-0 trace, but not yet established scientific findings:

1. There is a **stability–plasticity pattern** in the reported outcomes: replay is associated with less earlier-task degradation and worse final-block online loss. One environment realization is illustrative, not evidence of a stable trade-off law.
2. Replay may protect prior-task performance in this deliberately interference-prone model.
3. Sparse surprise-triggered replay may provide a different replay-budget/performance operating point.
4. The rig may be suitable for later causal experiments if its measurement and controls survive validation.

## Unsupported claims

1. **“Catastrophic forgetting” is not yet established.** The rig was constructed with decay expressly to induce recency bias. Large forgetting in this setting shows that the rig can manufacture and measure degradation; it does not establish catastrophic forgetting as a general P1 property.
2. **“Unconditional replay cuts forgetting 4×” is descriptive only and numerically imprecise.** Seed 0 gives `2.4516 / 0.6405 = 3.83`, not a population effect or stable factor.
3. **“Costs 0.5 nats of current-task accuracy” is not a clean causal estimate.** The conditions differ in total model updates and effective decay applications; the online-tail metric covers only the last 500 stream observations, while replay updates occur between those observations.
4. **No claim about the efficacy of surprise gating is justified.** It has no equal-budget random-timing control, and its threshold was not shown to be preregistered or independent of the displayed run.
5. **Replay efficiency is not demonstrated.** “One-seventh the replay budget” describes resource use, not performance per unit resource. There is no replay-budget response curve or equal-budget comparator.
6. **The variant ranking is not demonstrated beyond seed 0.** Tests use selected seeds as invariants and cannot substitute for an unbiased multi-seed study.
7. **The rig does not demonstrate a general continual-learning capability.** It studies one shared count table on one family of sparse first-order Markov chains in one fixed task order.
8. **Passing nine tests provides no evidence for a scientific mechanism.** The tests verify intended behavior, including an expected replay benefit on a hand-selected setting.

**Assessment:** M0 genuinely demonstrates a deterministic experimental scaffold that can exhibit measurable, replay-sensitive forgetting. It does not yet demonstrate a validated scientific capability or establish surprise gating as a mechanism.

# 2. Experimental Validity

## Experimental design

The basic design has useful elements: sequential tasks, prequential log loss, frozen held-out probes after each block, a no-replay comparator, an unconditional-replay comparator, and explicit replay counts. However, it is presently a demonstration rather than a controlled experiment.

## Controls and baselines

- The **uniform baseline** is only a weak learning sanity check. It is not a continual-learning baseline and does not control for task entropy or Bayes-optimal achievable loss.
- The **online condition** is a valid no-replay comparator for the combined memory-plus-replay intervention, but it does not isolate storage, replay timing, replay budget, or added optimization.
- The **always-replay condition** establishes an upper-budget replay comparator, but it is not fair to surprise replay because replay counts differ by 7.46×.
- There is no **budget-matched random gate**, no **compute/update-matched control**, and no **oracle or task-balanced replay control**.

## Fairness

Comparisons are not resource-matched. Each replay invokes `model.learn`, which both adds a count and applies row-wise decay. Thus variants differ simultaneously in:

1. number of training updates;
2. number and timing of decay operations;
3. historical-data mixture;
4. memory sampling trajectory;
5. wall-clock/computational cost.

Consequently, the intervention is not simply “replay versus no replay” or “surprise timing versus always timing.” It is a bundle of causal changes.

## Threats to internal validity

1. **Single stochastic realization.** Seed 0 jointly determines task transition matrices, stream draws, probe draws, reservoir replacement, and replay sampling. There is no independent replication.
2. **Paired randomness is only partial.** Variants share the task stream for a seed, which is good, but replay conditions consume a buffer RNG differently. There is no separate factorial treatment of environment and agent randomness.
3. **Replay budget confound.** Always and surprise conditions spend different numbers of replay updates.
4. **Optimization/update-count confound.** Replay variants receive more learning operations than online.
5. **Decay-operation confound.** Each replay update applies decay to a touched row before incrementing it. Replay can protect or damage information through changed decay frequency, independent of rehearsal content.
6. **Memory-content confound.** Replay samples from a reservoir that includes the current observation before replay. Benefits may reflect extra immediate rehearsal, historical rehearsal, or both.
7. **Threshold-selection bias.** `1.5` nats, replay batch `k=4`, decay `0.99`, capacity `1000`, fanout `2`, four tasks, and 2,000 steps per task are not accompanied by preregistered rationales or tuning provenance.
8. **Construct validity of “retention.”** The field named `retention` is mean forgetting, where lower is better. This naming inversion invites interpretation errors.
9. **Reference-score confound.** Forgetting is `final loss − loss immediately after the task’s training block`. Variants can appear to forget less if they learn a task less well initially. Always replay already has worse post-block learned losses for later tasks than online, so forgetting alone cannot represent retained capability.
10. **Last-task exclusion.** Averaging only earlier tasks is defensible for backward transfer, but it omits plasticity from the same scalar and can hide severe current-task impairment.
11. **Task-order confound.** Only order 0→1→2→3 is used. Task identity is inseparable from serial position.
12. **Task-overlap heterogeneity.** Randomly generated chains can differ in pair overlap and interference. The observed effect may be peculiar to seed-0 task geometry.
13. **Boundary carry-over.** The `prev` symbol is not reset at task boundaries. The first transition of a new task uses a context generated under the preceding task. The probe generator starts independently. This mismatch is small per block but systematic.
14. **Probe Monte Carlo error.** Each task uses 500 correlated transitions from one Markov-chain path. Treating them as independent would understate uncertainty; no effective sample size or multiple probe-set sensitivity is reported.
15. **Generator knowledge in evaluation.** Probe data are independent draws but come from the exact known generator family and parameters. This is valid for in-distribution estimation, not generalization.
16. **No Bayes/reference model.** Without task entropy or an oracle task-specific predictor, absolute loss and excess loss are hard to interpret across tasks and seeds.
17. **Synthetic design embeds distinguishability.** Tasks are explicitly constructed to be sparse and mutually distinguishable. External validity to overlapping, gradual, recurrent, higher-order, or nonstationary tasks is unknown.
18. **Designed-to-forget model.** Decay is identified in the source as the tunable mechanism under study. This supports assay sensitivity but risks circularity if the result is phrased as discovery rather than positive-control validation.
19. **Tests encode expected outcomes.** The replay-benefit and decay-forgetting tests were created on selected seeds/settings. They are not blinded confirmatory evidence and may reflect test-case selection.
20. **Unversioned evidence.** At review time, `p1v0/` and `tests/v0_rig/` were uncommitted. The result therefore lacks a permanent code identity; the available stored summary also used 300 rather than the reported 2,000 steps per task. The report was reproducible interactively, but the exact claimed artifact was not preserved.
21. **No preregistration.** Primary outcome, seed set, exclusions, threshold provenance, analysis rules, and failure criteria were not demonstrably frozen before outcome access.
22. **No blinding or held-out confirmation.** If parameters or assertions were adjusted after seeing seed 0, the displayed result is exploratory.
23. **Sequential loss dependence.** Online losses and probe pairs are autocorrelated. Naive sample-level inference would be invalid.
24. **Potential metric aggregation bias.** An unweighted mean over tasks gives equal weight to task-level estimates but reports no task-specific uncertainty or worst-case behavior.

# 3. Statistical Review

## Sufficiency

The reported evidence is insufficient for any population-level or mechanism-level claim.

- **Sample size:** one environment seed and one run per variant.
- **Seed count:** one. The stated future target `n ≥ 20` is a planning choice, not a power justification.
- **Confidence intervals:** none.
- **Variance:** unknown across task generation, stream trajectories, probes, reservoir sampling, and replay draws.
- **Repeatability:** exact repeatability under the same seed is shown; stochastic replication across independent seeds is not.
- **Statistical power:** not estimated. No smallest effect size of interest (SESOI), variance pilot, or prospective power/simulation analysis exists.
- **Multiplicity:** several variants and outcomes are inspected, with no declared primary contrast or correction procedure.

## Problems with the proposed M1 criterion

“Variant ranking stable across seeds with non-overlapping CIs” should **not** be adopted as the acceptance rule:

1. Non-overlap of separate 95% CIs is not the correct paired hypothesis test.
2. Ranking stability is not an effect-size criterion and can accept scientifically trivial differences.
3. Seed outcomes should be paired by shared environment realization and analyzed as paired contrasts.
4. Bootstrap validity depends on resampling the correct independent unit. Steps and probe pairs are not independent units; environment seeds should be the primary unit.
5. `n ≥ 20` is not automatically adequate. Required `n` must follow a prospective power or precision calculation for a preregistered SESOI.
6. The criterion ignores multiplicity and the plasticity cost.

## Currently justified scientific claims

Only narrowly scoped descriptive claims are justified:

- For the exact default configuration and seed 0, the three reported values occurred and are reproducible.
- The rig is sensitive to deliberately induced forgetting and to a large replay intervention in selected test settings.

No inferential claim about expected replay benefit, surprise-gating benefit, replay efficiency, stable stability–plasticity trade-offs, or general continual learning is currently justified.

# 4. Mechanism Review

## What can be attributed

At most, the seed-0 contrast between `online` and `replay_always` can be attributed to the **entire intervention bundle**: reservoir storage, sampled replay, 32,000 additional updates, changed row-wise decay schedule, and changed empirical training distribution.

## What cannot be attributed

1. The benefit cannot be attributed specifically to **memory storage**; storage without replay is not tested.
2. It cannot be attributed specifically to **rehearsal of older tasks**; the buffer contains current-task and just-observed samples.
3. It cannot be attributed to **surprise gating**; no equal-budget random-timing gate exists.
4. It cannot be attributed to **surprise as an informative signal**; threshold crossing is correlated with task switches, model underfit, rare transitions, and high-loss outliers.
5. It cannot be described as **efficiency**; compute-normalized and budget-response analyses are absent.
6. The apparent current-task cost cannot be attributed to a fundamental stability–plasticity law; it may arise from excessive replay ratio, reservoir mixture, decay semantics, or chosen task schedule.

## Alternative explanations

- Any replay, regardless of timing, could yield the same result at 4,292 updates.
- Equal numbers of extra updates on current-task samples could alter losses similarly.
- Replays may counteract decay simply by refreshing rows, rather than preserve task-specific knowledge through a meaningful memory mechanism.
- Surprise events may cluster near task boundaries; a boundary-triggered or early-block schedule might match performance.
- Reservoir sampling may create a near-uniform historical mixture that alone explains protection.
- The always condition may impair current-task loss because its replay ratio is four historical updates per new observation, not because stability necessarily costs plasticity.
- Differences in initial task mastery can mechanically change the forgetting score.

**Causal attribution is not justified beyond the bundled variant definitions.**

# 5. Missing Controls

Prioritized by scientific importance:

1. **Equal-budget random replay timing.** Same realized replay count and batch-size distribution as SurpriseGate, but times selected independently of loss. Necessary to test whether surprise carries information beyond budget.
2. **Replay-budget dose–response controls.** Always/random replay at several fixed expected budgets spanning 0 to 32,000. Necessary to distinguish gating quality from merely spending more updates and to estimate a Pareto frontier.
3. **Update-count/compute-matched nonhistorical control.** Add the same number of learning operations using current samples or a declared sham operation. Necessary to isolate historical replay from generic extra optimization and decay applications.
4. **No-decay control (`decay = 1`).** Necessary to determine whether the phenomenon is solely an artifact of the explicitly injected decay mechanism and whether replay has any effect when model state is not deliberately erased.
5. **Storage-without-replay control.** ReplayBuffer plus NeverGate. Necessary to verify that storage itself has no behavioral effect and to isolate replay from memory maintenance.
6. **Historical-only replay control.** Exclude the just-observed/current-task item or stratify replay by task age. Necessary to show protection comes from older evidence rather than repeated current-step learning.
7. **Oracle/task-balanced replay control.** Equal samples from prior tasks, using task labels only for the control. Necessary to estimate the best attainable retention at a budget and diagnose reservoir-composition limitations.
8. **Task-specific oracle predictor/Bayes entropy baseline.** Necessary to report excess log loss and compare tasks with different intrinsic entropy.
9. **No-learning/frozen-model baseline.** Necessary to verify metric behavior and bound apparent changes caused by stream/probe construction.
10. **Multiple task orders.** Counterbalance or randomize order independently of task generation. Necessary to separate task identity from serial-position effects.
11. **Independent environment, trajectory, replay, and probe seeds.** Necessary to estimate distinct variance components and prevent one composite seed from hiding sensitivity.
12. **Multiple probe sets or exact stationary-distribution evaluation.** Necessary to quantify or remove evaluation Monte Carlo error and autocorrelation.
13. **Alternative forgetting metrics.** Report final prior-task loss/excess loss, average accuracy/loss over time, backward transfer, area under the retention curve, and worst-task degradation. Necessary because change-from-learned can reward poor initial learning.
14. **Threshold-free or threshold-sweep control on held-out seeds.** Necessary to detect cherry-picking and establish sensitivity to the 1.5-nat threshold.
15. **Boundary-triggered control.** Replay at matched frequency near known task boundaries. Necessary because surprise may act only as an implicit change detector.
16. **Capacity and task-overlap stress controls.** Necessary later for scope and robustness, though not required for the minimal M0 assay validation.

# 6. Hidden Assumptions

1. **First-order Markov sufficiency:** a shared order-1 count table is assumed to be an informative substrate for P1. Effects may not transfer to richer learners.
2. **Abrupt, labeled block tasks are representative:** gradual drift, revisitation, and unlabeled mixtures may behave differently.
3. **Random sparse chains are sufficiently distinct:** the level of overlap controls interference and may predetermine the observed effect.
4. **Decay is a legitimate forgetting proxy:** replay may be correcting an artificial erasure rule rather than a naturally arising learning conflict.
5. **Row-wise decay represents model plasticity:** update frequency by context changes forgetting unevenly.
6. **Replay samples with replacement are appropriate:** duplicate samples within a replay batch can alter effective budget and variance.
7. **A replay update has unit cost equal to an online update:** actual compute/memory costs and access patterns may differ.
8. **One replay has equal scientific value across time:** sample age, task, context frequency, and model state likely matter.
9. **Loss > 1.5 nats operationalizes surprise:** this threshold may reflect uncertainty, rare events, task switches, or miscalibration; it is not validated as a construct.
10. **Absolute loss is comparable across tasks:** task entropy may differ.
11. **Uniform loss is the relevant baseline:** a useful predictor can beat uniform while remaining far from oracle performance.
12. **Probe pairs are held out enough:** they are new draws, but their generating transition matrices are exactly those seen during training.
13. **500 probe transitions provide precise estimates:** autocorrelation reduces effective sample size.
14. **Mean forgetting captures retention:** it conflates initial mastery and final performance and suppresses task heterogeneity.
15. **Excluding the final task is adequate:** it separates backward retention but not the joint stability–plasticity objective.
16. **Tail online loss captures plasticity:** it measures only the last block’s last 500 observations, not adaptation speed after every switch.
17. **Replay counts are the relevant budget:** memory operations, prediction calls, and decay side effects are not included.
18. **Same numeric seed means fair pairing:** it also fixes a single task geometry and multiple coupled random processes.
19. **Determinism implies reproducibility:** cross-platform/runtime and immutable artifact reproduction remain untested.
20. **The chosen configuration was not outcome-tuned:** no provenance establishes this.
21. **A stable rank is sufficient evidence:** magnitude, uncertainty, practical relevance, and joint costs also matter.
22. **Twenty seeds will be adequate:** adequacy depends on effect variance and SESOI.
23. **Failure to beat a comparator indicates mechanism failure:** it could instead reflect an unsuitable environment, threshold, budget, or insensitive metric; scope must be predefined.

# 7. Scientific Risks

| Rank | Risk | Why it is high risk |
|---:|---|---|
| 1 | **Premature causal claim for surprise gating** | Budget, timing, update count, memory content, and decay operations are confounded. A false mechanism discovery is likely without a matched random gate. |
| 2 | **Circular validation in a designed-to-forget rig** | The model deliberately decays; replay refreshes the same counts. The assay may validate its construction rather than reveal a general phenomenon. |
| 3 | **Unpreregistered, single-seed inference** | Effect direction, variance, robustness, and tuning bias are unknown. |
| 4 | **Invalid or misleading acceptance rule for M1** | Non-overlapping CIs and arbitrary `n ≥ 20` can produce false acceptance or rejection. |
| 5 | **Retention metric construct failure** | Lower forgetting can result from worse initial learning; the metric name also reverses directionality. |
| 6 | **Resource unfairness** | Additional replay updates and decay events can explain both retention and plasticity changes. |
| 7 | **No immutable evidence identity** | The reviewed rig is uncommitted, and the available stored artifact does not match the reported run length. |
| 8 | **Narrow environment overgeneralization** | One synthetic task family and one order cannot support claims about P1 generally. |
| 9 | **Coupled randomness and unmeasured variance components** | A single seed obscures which source drives the result. |
| 10 | **Goodhart risk on replay threshold and aggregate ranking** | Optimizing a threshold against the same seed set can create apparent efficiency without held-out confirmation. |

# 8. Required Experiments

These are the minimum experiments required to validate M0 as a scientific assay. They are not a redesign of P1.

## Experiment V0-1: Assay sensitivity and specificity

- **Hypothesis (H1):** Under a prespecified decay setting, the rig detects degradation of prior-task predictive performance after later-task training, while it does not report material degradation in a prespecified non-forgetting positive control (`decay = 1`) beyond the SESOI.
- **Null hypothesis (H01):** The measured degradation under decay is no greater than the prespecified minimum detectable effect, or similar degradation appears without decay.
- **Independent variables:** decay condition (`0.99` versus `1.0`); sequential-task exposure.
- **Dependent variables:** primary: paired change in prior-task excess log loss; secondary: final prior-task excess loss and per-task degradation.
- **Controlled variables:** task generators, order, stream trajectories, probe sets, model hyperparameters, and update counts; pair conditions by environment seed.
- **Controls:** no-decay model; frozen/no-learning sanity baseline; task-specific oracle entropy baseline.
- **Metrics:** excess log loss relative to oracle; mean and worst-task change; paired effect with 95% CI.
- **Acceptance criteria:** preregister a positive SESOI `δ_forget` and equivalence margin `ε`; decayed condition’s paired mean degradation must exceed `δ_forget`, while no-decay degradation must fall within `[-ε, +ε]`, with familywise error controlled. Also require the result on a held-out confirmation seed set.
- **Rejection criteria:** decayed degradation does not exceed `δ_forget`; no-decay is not equivalent to zero within `ε`; effect depends on a small set of anomalous tasks; or conclusions fail on confirmation seeds.

## Experiment V0-2: Replay causal effect under fair resource accounting

- **Hypothesis (H2):** Historical replay reduces final prior-task excess log loss compared with no historical replay when total learning-update count and decay applications are matched.
- **Null hypothesis (H02):** At matched update count, historical replay improves prior-task excess log loss by less than the prespecified SESOI or does not improve it.
- **Independent variable:** content of matched extra updates: historical replay versus current-sample/sham matched updates versus no-extra-update descriptive reference.
- **Dependent variables:** primary: final prior-task excess log loss; co-primary guardrail: current-task excess log loss or adaptation area-under-curve.
- **Controlled variables:** exact number/timing of extra updates, decay applications, task stream, order, random seeds, memory capacity, probe data, and compute accounting.
- **Controls:** online no-extra-update condition; update-count-matched current-sample or scientifically valid sham condition; storage-without-replay condition.
- **Metrics:** paired historical-replay contrasts; joint stability–plasticity vector; replay/update count and compute; 95% simultaneous CIs.
- **Acceptance criteria:** historical replay improves prior-task loss by at least preregistered `δ_replay`, its CI excludes zero in the beneficial direction, and the plasticity guardrail remains within preregistered `ε_plasticity`; effect replicates on held-out seeds.
- **Rejection criteria:** improvement disappears under matched updates/decay, is below `δ_replay`, violates the plasticity guardrail, or is driven by immediate/current-task samples.

## Experiment V0-3: Surprise-information ablation

- **Hypothesis (H3):** At an identical replay budget and batch-size profile, loss-triggered replay outperforms replay times selected uniformly at random on a preregistered joint retention–plasticity criterion.
- **Null hypothesis (H03):** Surprise-triggered allocation is no better than equal-budget random allocation by the prespecified SESOI.
- **Independent variable:** replay timing policy: surprise-triggered versus matched random; optional diagnostic boundary-matched policy.
- **Dependent variables:** primary: paired difference in final prior-task excess log loss; guardrails: adaptation area-under-curve and final current-task loss.
- **Controlled variables:** realized replay count per run, replay batch sizes, replay content sampler, model, decay, task stream, task order, memory capacity, and compute.
- **Controls:** equal-budget random gate; no-replay reference; boundary-timing diagnostic if surprise firing clusters around switches.
- **Metrics:** paired effect sizes across independent environment seeds; simultaneous CIs; fraction of seeds improved; budget-normalized effect; task-level heterogeneity.
- **Acceptance criteria:** on a held-out confirmation set, surprise timing improves the primary metric over matched random by at least preregistered `δ_gate`, with a corrected CI excluding zero, without violating plasticity guardrails. The threshold must be frozen before confirmation data are accessed.
- **Rejection criteria:** matched random is equivalent or superior; benefit is below `δ_gate`; threshold sensitivity is severe; benefit vanishes after boundary matching; or guardrails fail.

## Experiment V0-4: Measurement reliability and seed design

- **Hypothesis (H4):** Variant contrasts are robust to independent task-generation, trajectory, replay, probe, and task-order randomness, and probe estimates meet a preregistered precision target.
- **Null hypothesis (H04):** Estimated contrasts are unstable across variance sources or probe uncertainty exceeds the precision target.
- **Independent variables:** independently varied environment seed, trajectory seed, replay seed, probe seed, and randomized/counterbalanced task order.
- **Dependent variables:** variance components and paired variant contrasts.
- **Controlled variables:** frozen experimental configurations and analysis plan.
- **Controls:** repeated probe sets for identical trained states; where feasible, exact or high-precision oracle evaluation.
- **Metrics:** variance decomposition; intraclass or repeatability measures; CI width; sensitivity to order; worst-case task effects.
- **Acceptance criteria:** prospective simulation or pilot-based analysis determines sample size; final CI width is within a declared precision target; conclusions retain direction and SESOI across held-out orders and probe replications.
- **Rejection criteria:** one randomness source dominates unpredictably; order reverses the conclusion; probe error is material; or the prespecified precision target is not met.

## Required statistical protocol for all four experiments

1. Freeze hypotheses, primary contrasts, SESOIs, equivalence margins, seed-generation procedure, sample size/stopping rule, exclusions, and multiplicity correction before confirmatory runs.
2. Use paired analyses at the independent environment-seed level; do not treat steps or probe transitions as independent replicates.
3. Determine sample size by prospective power/precision simulation using pilot variance. `n = 20` is a minimum only if justified by that analysis.
4. Report effect sizes and uncertainty, not only p-values or rank order.
5. Separate exploratory tuning seeds from untouched confirmation seeds.
6. Preserve every valid negative result and all run manifests.
7. Report per-task outcomes and worst-case behavior alongside means.

# 9. Milestone Decision

## APPROVE WITH REQUIRED EXPERIMENTS

M0 is approved **only as an engineering-complete, scientifically provisional experimental scaffold**. Evidence establishes deterministic execution, a functioning prequential/probe measurement path, deliberate forgetting sensitivity, and a reproducible seed-0 replay-associated contrast. That is enough to preserve the rig and proceed directly into validation work.

M0 is **not approved as evidence** for a general stability–plasticity principle, replay efficacy, surprise-gating efficacy, replay efficiency, or a P1 learning capability. Those conclusions remain hypotheses.

The required next work is not a v0 redesign and not the proposed “ranking with non-overlapping CIs.” It is the four minimal validation experiments above, beginning with assay validity and resource-matched causal controls. M1 may be defined as that statistical and measurement-validation program, but no mechanism slots or further mechanism proliferation should proceed until V0-1 through V0-3 have preregistered protocols and the exact M0 code/results are version-pinned.

# 10. Recommendations to Claude

**To: Principal Architect (Claude Opus)**

Do not revise the v0 architecture yet. Freeze and commit the exact M0 code, configuration, runtime identity, and seed-0 artifacts first. Treat the current numbers as exploratory.

Before proceeding beyond M1 validation:

1. preregister primary outcomes, SESOIs, equivalence margins, seed generation, stopping rule, and multiplicity handling;
2. replace the proposed “non-overlapping CIs” gate with paired effect-size inference at the environment-seed level and a power/precision-justified sample size;
3. validate the forgetting assay against no-decay and oracle/frozen controls;
4. isolate replay from extra updates and extra decay operations using matched controls;
5. add an equal-budget random-timing gate before making any claim about surprise;
6. split environment, stream, replay, probe, and task-order randomness and preserve per-run manifests;
7. report final prior-task loss, initial mastery, adaptation cost, per-task effects, and compute budget—not the current `retention` scalar alone;
8. reserve untouched seeds for confirmation after thresholds are frozen.

No M0 result currently warrants a mechanism claim. The next milestone should produce discriminating evidence, not additional mechanism options.
