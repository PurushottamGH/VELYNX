# Assumption and Uncertainty Registry Standards

- **Version:** 1.0.0
- **Assumption prefix:** `ASM-`
- **Uncertainty prefix:** `UNK-`

## Part A — Assumption Registry

### A1. Purpose

The Assumption Registry exposes every proposition P1 temporarily relies on without adequate direct support. Hidden assumptions are scientific defects; registered assumptions are testable research objects.

### A2. Assumption schema

Each assumption records:

- permanent ID and version;
- statement and operational meaning;
- category: `world`, `measurement`, `causal`, `statistical`, `model`, `data`, `human_judgment`, or `scope`;
- scope and conditions;
- why it is needed;
- dependents: hypotheses, theories, experiments, metrics, decisions, mechanisms;
- expected consequence if false;
- current evidence for, against, and unresolved;
- confidence and confidence history;
- validation method and required experiment;
- sensitivity/robustness analysis;
- status and decision history;
- replacement/supersession links;
- owner and review date.

### A3. Lifecycle

```text
Proposed → Active-Unvalidated → Under Test
  → Supported | Contradicted | Retired | Replaced
Supported → Under Test (challenge)
Contradicted → Replaced | Retired
Any state → Superseded
```

- **Active-Unvalidated:** relied upon but not adequately tested.
- **Supported:** evidence supports use within scope; still revisable.
- **Contradicted:** credible evidence shows it fails within scope.
- **Retired:** no longer load-bearing; no replacement required.
- **Replaced:** successor assumption exists.

### A4. Confidence updates

Confidence changes only through a Decision. Record separate confidence in truth and sensitivity of conclusions to the assumption. An assumption may be low-confidence but low-risk if conclusions are insensitive; a moderate-confidence load-bearing assumption may be high priority.

### A5. Validation and retirement

An assumption can be:

- **directly tested** by a discriminating experiment;
- **stress-tested** across plausible values or environments;
- **eliminated** by reformulating the claim or experiment so it is no longer required;
- **bounded** by narrowing scope;
- **replaced** by a better-supported assumption.

Retirement never deletes history. Any dependent validated claim must be reassessed if a load-bearing assumption becomes contradicted.

### A6. Innate biases

Every built-in scientific bias is an assumption and, where instantiated as a mechanism, also links to the Mechanism Registry. Record expected effect, affected behavior, ablation strategy, and evidence. No hidden inductive bias is permitted in a scientific interpretation.

## Part B — Uncertainty Registry

### B1. Purpose

The Uncertainty Registry tracks material unanswered questions, contradictions, anomalies, failed replications, measurement gaps, and missing information.

### B2. Uncertainty schema

Each uncertainty records:

- permanent ID, title, statement, and type;
- scope and materiality;
- originating observation, experiment, assumption, hypothesis, theory, or decision;
- affected scientific records;
- candidate answers and current probability ranges, when defensible;
- what would resolve or materially reduce it;
- smallest discriminating experiment;
- feasible actions and expected information gain;
- cost, time, feasibility, and downstream decision value;
- priority score and rationale;
- status, owner, and review date;
- resolving evidence and decision when closed.

Types include `open_question`, `contradiction`, `anomaly`, `measurement_gap`, `failed_replication`, `missing_provenance`, `nonidentifiability`, and `scope_unknown`.

### B3. Lifecycle

```text
Open → Prioritized → Under Investigation → Reduced | Resolved
Resolved → Reopened
Open/Prioritized → Deferred | Archived
```

Resolution criteria are fixed when the uncertainty is opened. They may be revised only by a Decision that preserves the prior criterion and explains why it was defective.

### B4. Expected information gain prioritization

Priority is based on decision value, not curiosity alone. Use an ordinal 0–4 score for:

- `D`: probability the answer changes a major scientific decision;
- `U`: current uncertainty/entropy;
- `B`: downstream breadth—how many claims depend on it;
- `R`: risk of continuing while unresolved;
- `F`: feasibility of a discriminating experiment;
- `C`: normalized scientific cost.

Recommended priority index:

`Priority = (D × U × B × R × F) / (1 + C)`

The formula ranks attention; it does not authorize conclusions. Scores require written rationale and sensitivity review. Where numeric probabilities are unjustified, use pairwise ranking with the same dimensions.

### B5. Mandatory intake triggers

Open or update an uncertainty when there is:

- a load-bearing untested assumption;
- conflicting valid evidence;
- an unexplained anomaly;
- a failed replication;
- a measurement construct that may not identify the target;
- missing provenance material to a conclusion;
- hypotheses that predict identical observables;
- an experiment that failed to reduce the intended uncertainty.

### B6. Closure

`Resolved` means the recorded resolution criterion was met within scope. `Reduced` means uncertainty decreased but remains decision-relevant. Closure by authority, elapsed time, implementation completion, or absence of investigation is prohibited.
