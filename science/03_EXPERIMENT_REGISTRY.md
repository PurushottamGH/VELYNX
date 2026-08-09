# Experiment Registry Standard

- **Version:** 1.0.0
- **Record prefix:** `EXP-`
- **Purpose:** Make every scientific execution permanently traceable from question through result, interpretation, and decision.

## 1. Experiment identity

An experiment is a bounded attempt to reduce uncertainty. A protocol version and each execution are distinct:

- Experiment family: `EXP-YYYY-NNNN`
- Protocol version: `EXP-YYYY-NNNN-PvX.Y.Z`
- Execution: `EXP-YYYY-NNNN-RNNNN`

IDs are permanent and never reused.

## 2. Core schema

Every experiment family records:

- ID, title, phase (`Discovery` or `Validation`);
- question and expected decision impact;
- linked hypotheses, assumptions, unknowns, theory, and debt items;
- null hypothesis and credible alternatives;
- motivation and expected information gain;
- environment/dataset/world scope;
- independent, dependent, controlled, nuisance, and confounding variables;
- treatment conditions, controls, and baselines;
- metrics and measurement-validity links;
- acceptance, rejection, revision, and invalidity criteria;
- compute/data/time budget as an experimental constraint;
- protocol versions and execution IDs;
- observed outcomes, validity status, lessons learned, future work;
- resulting Evidence, Interpretation, and Decision IDs.

Every execution records:

- exact protocol version;
- code/architecture version identifier supplied by engineering;
- environment/runtime version;
- dataset/world version and custody reference;
- complete parameter configuration;
- random generators and seeds by variance source;
- compute budget actually consumed;
- start/end time;
- raw-output manifest and digests;
- deviations and unplanned events;
- validity determination independent of favorability;
- outcome summary without interpretation.

## 3. Phase-scaled completeness

### Discovery record

Required before execution:

1. question or hypothesis;
2. smallest decision the result could change;
3. meaningful baseline or null;
4. primary measurement;
5. rough failure/adverse outcome;
6. configuration and seed sufficient for local repetition.

Allowed: adaptive iteration, convenience samples, small seed counts, exploratory metrics, post hoc analysis—provided they are labeled.

### Validation record

Required before confirmatory access:

1. fixed scope and hypotheses;
2. primary outcomes and estimands;
3. sampling frame and independent unit;
4. sample size or stopping rule;
5. assignment and controls;
6. exclusions and invalidity criteria;
7. statistical/logical decision rule;
8. multiplicity handling;
9. randomness plan;
10. effect-size threshold or equivalence margin where applicable;
11. reproducibility and deviation policy.

Publication packaging is not part of experiment validity.

## 4. Lifecycle

```text
Proposed → Designed → Ready → Running → Completed
              └──────> Withdrawn
Running → Abandoned
Completed → Interpreted → Closed
Any state → Superseded (with successor)
```

- **Proposed:** question and decision impact exist.
- **Designed:** variables, baseline, and metric are specified.
- **Ready:** phase-appropriate readiness criteria are met.
- **Running:** at least one governed execution began.
- **Completed:** execution disposition and immutable outputs exist.
- **Interpreted:** scoped inference and alternatives are recorded.
- **Closed:** scientific state was updated by Decision.
- **Abandoned:** execution stopped; reason and partial outputs retained.
- **Withdrawn:** no execution began and the plan was retired.

## 5. Traceability chain

```text
Question/Unknown
  → Hypothesis/Assumption
    → Experiment protocol
      → Execution
        → Observation/Result
          → Evidence relation
            → Interpretation
              → Scientific Decision
                → Updated Living Scientific Model/Roadmap
```

A completed experiment is not closed until the chain reaches a Decision or explicitly states why no scientific update was possible. An experiment that reduced no uncertainty becomes evidence about method or measurement and must create or update a debt/unknown record.

## 6. Validity and outcome

Validity is independent of favorability:

- `valid_positive`
- `valid_negative`
- `valid_indeterminate`
- `invalid`
- `abandoned`

Invalid and abandoned executions remain traceable. They may update methodological knowledge but cannot support the target scientific conclusion unless a later decision establishes a different relevance.

## 7. Comparison fairness

Every claimed treatment comparison must state whether conditions are matched on data, opportunity, compute, updates, memory, parameter search, and information access. Unmatched dimensions are confounders or explicit scope limitations.

## 8. Evidence-preserving revision

A protocol change after outcome access creates a new protocol version and exploratory execution lineage. Previous records remain unchanged. No later preregistration can retroactively make an exploratory run confirmatory.
