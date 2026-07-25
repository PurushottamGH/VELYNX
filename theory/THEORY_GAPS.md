# Theory Gaps: What Remains Unexplained

**Status:** Gap analysis derived from `THEORY_LANDSCAPE.md`  
**Date:** 2026-07-20  
**Epistemic status:** Open questions and experiment proposals, not registered hypotheses

## Executive conclusion

Most alleged "missing principles" are not principle gaps. They are one of four things:

1. a difficult approximation to a known normative computation;
2. an identifiability problem caused by insufficient data or interventions;
3. an omitted boundary condition such as objective, prior, task distribution, or resource budget; or
4. an ill-posed demand for assumption-free generality.

The strongest genuine scientific gaps concern **conditions for sustained open-ended adaptive growth**, **cumulative cultural competence**, **development of viability and preferences from inherited constraints**, and **valid measurement across unequal priors and resources**. Current evidence does not justify a new universal computational principle for any of them.

## 1. Gap qualification test

A question qualifies as a candidate principle gap only if all conditions hold:

1. A repeatable phenomenon is operationally defined.
2. Existing principles make distinguishable predictions about it.
3. Matched-resource and null controls reject simpler explanations.
4. The residual is not due to inaccessible information or computational infeasibility.
5. A proposed principle makes a risky prediction beyond redescribing the result.
6. The prediction is implementation-independent or the implementation scope is explicit.

Without these conditions, P1 should record an open problem rather than invent a principle.

## 2. Generalization and transfer

**Observation.** High performance under one distribution often fails under changed composition, surface statistics, causal mechanism, goals, or sensor mappings. Shortcut learning and failures on controlled compositional splits are well documented [G1, G2].

**Existing formalization.** Bayesian inference, MDL, representation learning, program induction, and causal modeling predict transfer only after a hypothesis class and environmental invariances are supplied. They formalize why task-matched structure can transfer; they do not explain where the correct structure comes from. No Free Lunch rules out unrestricted superiority under its averaging assumptions.

**Residual.** Which invariances and reusable factors characterize a declared family of shifts, and how can a bounded learner identify them from available evidence?

**Classification.** Predominantly inductive-bias selection, identifiability, and engineering.

**Decisive experiments.** Use procedurally generated task families with separately manipulated recombination, new entities, changed mechanisms, sensor remapping, and goal transfer. Freeze training data and computation. Compare correct-invariance models against equal-capacity models with deliberately wrong invariances.

**New principle warranted?** No. Failure is predicted by existing theory unless an unexplained regularity remains after priors, data, and resources are matched.

## 3. Relevance and the open-world frame problem

**Observation.** Bounded systems must select facts, memories, consequences, and computations from an effectively unbounded set. Unexpected dependencies can invalidate the selection.

**Existing formalization.** Value of information, sparse causal structure, attention, retrieval, and rational metareasoning define relevance relative to a task and budget. Situation calculus and circumscription address important forms of the narrow logical frame problem, but do not solve open-world relevance selection [G3, G16].

**Residual.** Efficiently revise a relevance model after surprise without searching all possible dependencies. Prediction error signals failure but does not identify the omitted cause.

**Classification.** Engineering under bounded rationality. Guaranteed relevance in arbitrary open worlds is impossible or ill-posed.

**Decisive experiments.** Environments with many distractors, delayed side effects, hidden context changes, and rare decisive variables. Measure omitted-consequence rate, computation, calibration, and recovery after surprise.

**New principle warranted?** No. A better retrieval or attention mechanism would be useful but is not automatically a new principle.

## 4. Abstraction and compositionality

**Observation.** Some systems discover reusable concepts, programs, objects, or options; others memorize surface regularities and fail novel combinations. Program-induction systems show strong transfer when supplied suitable languages [G4, G5].

**Existing candidate accounts.** MDL favors reusable components that shorten total description. Bayesian latent-variable models infer shared causes. Program induction and hierarchical control encode composition directly. Each requires a representation language, prior, or search procedure and therefore does not by itself predict which abstraction will be found.

**Residual.** Tractable discovery of abstractions that remain useful under future interventions not known during training. Multiple equally compressive factorizations may support different transfers.

**Classification.** Search, prior selection, and identifiability.

**Decisive experiments.** Hold out combinations and interventions, not random samples. Require discovered components to transfer across independently generated task families. Compare flat, compositional, and wrong-factorization controls at matched capacity.

**New principle warranted?** No. Existing principles explain why reuse helps; they do not promise that bounded search finds the correct factorization.

## 5. Causal model acquisition

**Observation.** Observationally correct predictors can fail interventions. Causal structure is not generally identifiable from observation alone [G6].

**Existing formalization.** Structural causal models add intervention semantics and invariance assumptions to probabilistic inference. Active learning and information gain formalize experiment selection after candidate variables, models, and costs are specified.

**Residual.** Learn transportable mechanisms under latent confounding, partial observability, changing selection, expensive intervention, and safety constraints.

**Classification.** Identifiability science plus engineering.

**Decisive experiments.** Train on observationally equivalent environments with different intervention structure, then test unseen interventions, mechanism changes, and transport. A purely associational model should be an explicit control.

**New principle warranted?** No. Causal semantics are important, but already formulated. Some cases are impossible, not unexplained.

## 6. Exploration under deception, noise, and risk

**Observation.** Random exploration and local novelty fail in sparse, deceptive, stochastic, irreversible, or very large environments. Memory-based return-and-explore methods solve some previously difficult cases [G7].

**Existing formalization.** Bayes-adaptive control, information gain, optimism, novelty, and empowerment formalize why selected information can have instrumental value under a specified model and objective.

**Residual.** Compute which uncertainty matters to future outcomes when beliefs are approximate and information gathering can cause irreversible harm.

**Classification.** Algorithmic and objective-specification problem.

**Decisive experiments.** Cross sparse reward, stochastic distraction, deceptive local optima, irreversible traps, and hidden changes. Report downstream value, information gained, safety violations, and computation rather than state coverage alone.

**New principle warranted?** No universal principle. Existing theory states the tradeoff; scalable safe approximations remain unsolved.

## 7. Credit assignment across timescales and structural change

**Observation.** Known methods degrade with long delays, partial observability, modular interactions, many agents, and changes to representation or objective.

**Existing candidate mechanisms.** Gradients, temporal differences, eligibility traces, counterfactual baselines, and causal intervention estimate contribution to later loss or value. Sutton [G8] supports temporal-difference prediction specifically, not the entire family.

**Residual.** Low-bias, low-variance, local, online credit for events that alter the future hypothesis space rather than only the current state.

**Classification.** Engineering for artificial systems; mechanism science for biological systems.

**Decisive experiments.** Generate tasks with known causal contribution graphs and controlled dependency lengths. Compare estimated attribution with intervention ground truth while measuring sample, memory, and latency costs.

**New principle warranted?** No. The abstract requirement is clear; efficient estimators are incomplete.

## 8. Autonomous objective formation

**Observation.** Organisms and artificial agents acquire subgoals, skills, social preferences, and state-dependent motivations. Demonstrations always retain inherited viability variables, reward channels, novelty criteria, preference priors, or selection processes [G9].

**Existing candidate accounts.** Optimization derives instrumental subgoals from higher-level criteria. Homeostatic control derives changing value from deficits. Evolutionary and cultural models can account for inherited or transmitted preferences but require specific population, developmental, and environmental mechanisms.

**Residual.** How biological development and social processes establish and revise the variables that later function as objectives.

**Classification.** Scientific when inherited constraints and developmental processes are specified. "Choose terminal values from no prior criterion" is ill-posed: without a criterion, no choice is better.

**Decisive experiments.** Supply only fixed viability variables and broad action spaces; test whether transferable intermediate objectives arise and improve lifetime viability over fixed shaping, novelty, and random intrinsic controls.

**New principle warranted?** No. Evidence currently supports combinations of selection, regulation, learning, and transmission.

## 9. Self-maintenance and system boundaries

**Observation.** Biological systems regulate energy, integrity, temperature, and other viability variables; engineered systems can regulate analogous quantities.

**Existing formalization.** Feedback, viability theory, constrained optimization, predictive control, and homeostatic reinforcement learning formalize maintenance once boundary, viable region, dynamics, and failure costs are given.

**Residual.** How boundaries and viable variables originate, persist through component replacement, and change during development.

**Classification.** Boundary specification plus biological mechanism. Intrinsic self-preservation for an unspecified system is ill-posed.

**Decisive experiments.** Perturb resources and components; distinguish preservation of task function from preservation of current material; compare reactive and anticipatory control.

**New principle warranted?** No. Viability is an important condition, not an unexplained computational force.

## 10. Bounded rationality and metareasoning

**Observation.** More computation has uncertain value and consumes time, memory, and energy. Performance rankings can reverse under different budgets.

**Existing formalization.** Computational rationality models outcome quality jointly with an assumed computation-cost model [G10]. Related bounded-optimality, rate-distortion, and rational-metareasoning traditions require their own assumptions and deeper review.

**Residual.** Estimate the value of computation when metareasoning is itself costly and hardware or deadlines change.

**Classification.** Engineering and empirical resource-model selection.

**Decisive experiments.** Change budgets after training and test whether computation is concentrated on cases with high marginal value. Report Pareto frontiers over score, latency, memory, energy, and samples.

**New principle warranted?** No. Resource-sensitive optimization is already the principle.

## 11. Open-ended adaptive growth

**Observation.** Evolutionary and multi-agent systems can generate finite sequences of new environments and behaviors. Existing demonstrations depend on designer-chosen generators, mutation operators, novelty measures, archives, and viability filters [G11, G12]. Sustained unbounded innovation has not been established.

**Why current explanations are incomplete.** Variation, selection, novelty pressure, ecological interaction, curriculum generation, and transfer explain finite innovation. They do not yet predict when growth will persist rather than saturate, cycle, drift, or exploit a metric.

**Genuine residual.** Identify sufficient ecological and computational conditions for sustained increases in adaptive capability and future innovation potential, while separating them from noise, archive growth, and designer expansion.

**Classification.** Genuine scientific and measurement gap.

**Required operational work.** Predefine several non-equivalent measures:

- adaptive value in newly generated niches;
- behavioral and structural diversity;
- compressible functional complexity rather than raw entropy;
- cross-domain transfer;
- rate of capability-enabling innovations; and
- robustness to replacing the novelty metric.

**Decisive experiments.** Long-horizon scaling over time, population, and resources with random-mutation, fixed-curriculum, novelty-only, objective-only, archive-only, and generator-expansion controls. Replication must show continuing growth across multiple measures.

**New principle warranted?** **Not yet.** This is the strongest candidate domain, but the explanandum itself is not stable enough to justify a new law.

## 12. Cumulative cultural competence

**Observation.** Human groups preserve and improve capabilities beyond individual lifetime discovery; cultural-evolution research studies the required transmission and selection processes [G17]. Artificial multi-agent systems show coordination and autocurricula but often overfit partners and conventions [G13].

**Existing candidate accounts.** Social learning, communication, population selection, institutions, external memory, and division of labor provide candidate components. Their conjunction does not yet predict when cumulative culture will occur.

**Residual.** Determine which combinations of transmission fidelity, innovation, teaching, reputation, norms, population structure, and turnover cause robust accumulation rather than conformity or cascade.

**Classification.** Scientific mechanism gap at the population level.

**Decisive experiments.** Iterated transmission with population replacement, newcomer integration, novel partners, convention changes, adversarial messages, and tasks exceeding individual learning budgets. Include solitary, imitation-only, static-population, and communication-disabled controls.

**New principle warranted?** No, currently. A new principle becomes plausible only if robust scaling laws remain unexplained by known transmission, selection, and coordination mechanisms.

## 13. Measurement of intelligence

**Observation.** Scores conflate prior knowledge, training data, task fit, tools, compute, and adaptation. Universal measures require environment weighting and are generally incomputable; benchmark measures encode human-selected priors [G14, G15].

**Existing formalization.** Decision theory evaluates expected competence once target domains, scores, priors, and relevant resources are fixed. Psychometrics estimates latent factors relative to task populations.

**Residual.** Compare adaptation fairly across unequal priors and compute, detect contamination, and predict performance under genuinely new task generators.

**Classification.** Measurement science. A context-free scalar ordering of all intelligence is ill-posed.

**Decisive work.** Hidden procedural generators, contamination audits, explicit experience/compute accounting, learning curves, reliability and construct validation, and capability profiles or Pareto surfaces instead of one score.

**New principle warranted?** No cognitive principle. Better standards and instruments are required.

## 14. Emergence as an unresolved measurement problem

**Observation.** "Emergence" is applied to self-organization, learned latent variables, unprogrammed behavior, phase transitions, and observer surprise. These uses do not share a single operational criterion.

**Existing formalisms.** Dynamical systems define macrovariables and bifurcations; statistics defines null models; learning theory measures generalization; information theory measures dependence and complexity. None supplies a unique domain-general emergence criterion.

**Residual.** A domain-general emergence claim must specify:

1. system boundary and scale;
2. macrovariable;
3. comparison class and null;
4. what was supplied by design, data, selection, or evaluator;
5. nontriviality criterion;
6. robustness across measurements; and
7. novel prediction made by the macrodescription.

Without these, emergence is an interpretation, not an observation.

**Relationship to Program D.** H*'s shuffled-input NMI difference addresses one confound for a synthetic latent-recovery task. It does not provide a universal emergence measure: the true latent, partition metric, generator, and scale are investigator-specified.

**New principle warranted?** No. Better null-referenced methodology is warranted before theorizing.

## 15. Priority research program

| Priority | Question | Why it outranks alternatives | Entry criterion |
|---|---|---|---|
| 1 | Valid measurement of adaptation and emergence | Empirical adaptation and emergence claims depend on non-gameable observables. | Prospective task generation, resource accounting where efficiency is claimed, and explicit nulls. |
| 2 | Open-ended adaptive growth | Strongest plausible residual not reduced to a known finite optimization task. | Replicated sustained growth across several non-equivalent metrics. |
| 3 | Cumulative cultural competence | Real capability growth beyond individual lifetime suggests population-level conditions worth isolating. | Tasks exceeding individual budgets and controlled population turnover. |
| 4 | Development of preferences from viability and social constraints | Clarifies objective origins without asking for criterion-free values. | Fixed inherited constraints and held-out developmental environments. |
| 5 | Causal abstraction under mechanism change | Central to transfer, but existing theory already defines much of the target. | Observationally equivalent/interventionally different controls. |

P1 should not prioritize a new universal mechanism before Priority 1 produces validated observables.

## 16. Questions rejected as presently ill-posed

- Which algorithm generalizes to every possible future task?
- How can a system derive terminal values from no preference, viability condition, or selection history?
- How can a bounded system guarantee consideration of every relevant consequence in an unrestricted world?
- Which system is more intelligent without specifying tasks, prior knowledge, interfaces, and resources?
- Is novelty objectively interesting without an observer-independent adaptive criterion?
- Did intelligence "emerge" without specifying a scale, null model, and designer contribution?

These should be reformulated, not answered with new principles.

## 17. Final gap verdict

This selective review supports no convincing new **universal** computational principle. Scoped comparative, probabilistic, causal, and scaling hypotheses remain scientifically available. The defensible research posture is:

- preserve the conditional claim schema and overlapping adaptive obligations in `THEORY_LANDSCAPE.md`;
- treat T-01 as a derived temporal-aliasing requirement;
- treat T-02 as descriptive measurement syntax;
- investigate open-endedness and cumulative culture only after stronger operationalization;
- distinguish scientific unknowns from implementation difficulty; and
- require preregistered nulls and matched-resource controls before elevating a gap to a universal-principle claim.

## 18. References

- **[G1]** Lake, B. M., & Baroni, M. (2018). Generalization without systematicity. https://proceedings.mlr.press/v80/lake18a.html
- **[G2]** Geirhos, R. et al. (2020). Shortcut learning in deep neural networks. *Nature Machine Intelligence*. https://doi.org/10.1038/s42256-020-00257-z
- **[G3]** McCarthy, J., & Hayes, P. J. (1969). Some philosophical problems from the standpoint of artificial intelligence. https://www-formal.stanford.edu/jmc/mcchay69/mcchay69.html
- **[G4]** Lake, B. M., Salakhutdinov, R., & Tenenbaum, J. B. (2015). Human-level concept learning through probabilistic program induction. *Science*. https://doi.org/10.1126/science.aab3050
- **[G5]** Ellis, K. et al. (2020). DreamCoder. https://arxiv.org/abs/2006.08381
- **[G6]** Pearl, J. (2009). Causal inference in statistics: an overview. *Statistics Surveys*. https://doi.org/10.1214/09-SS057
- **[G7]** Ecoffet, A. et al. (2021). First return, then explore. *Nature*. https://doi.org/10.1038/s41586-020-03157-9
- **[G8]** Sutton, R. S. (1988). Learning to predict by the methods of temporal differences. https://doi.org/10.1007/BF00115009
- **[G9]** Keramati, M., & Gutkin, B. (2014). Homeostatic reinforcement learning for integrating reward collection and physiological stability. *eLife*. https://doi.org/10.7554/eLife.04811
- **[G10]** Gershman, S. J., Horvitz, E. J., & Tenenbaum, J. B. (2015). Computational rationality. *Science*. https://doi.org/10.1126/science.aac6076
- **[G11]** Lehman, J., & Stanley, K. O. (2011). Abandoning objectives. *Evolutionary Computation*. https://doi.org/10.1162/EVCO_a_00025
- **[G12]** Wang, R. et al. (2019). Paired Open-Ended Trailblazer. https://arxiv.org/abs/1901.01753
- **[G13]** Leibo, J. Z. et al. (2021). Scalable evaluation of multi-agent reinforcement learning with Melting Pot. https://arxiv.org/abs/2107.06857
- **[G14]** Legg, S., & Hutter, M. (2007). Universal intelligence. https://arxiv.org/abs/0712.3329
- **[G15]** Chollet, F. (2019). On the measure of intelligence. https://arxiv.org/abs/1911.01547
- **[G16]** McCarthy, J. (1980). Circumscription: a form of non-monotonic reasoning. *Artificial Intelligence*. https://doi.org/10.1016/0004-3702(80)90011-9
- **[G17]** Mesoudi, A., Whiten, A., & Laland, K. N. (2006). Towards a unified science of cultural evolution. *Behavioral and Brain Sciences*. https://doi.org/10.1017/S0140525X06009083
