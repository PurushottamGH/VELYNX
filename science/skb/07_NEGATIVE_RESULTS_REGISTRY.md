# P1 Negative Results Registry — SKB v1.0

- **State date:** 2026-07-28
- **Policy:** A negative result is preserved with scope and validity. “No significant effect” is not automatically equivalence.

| ID | Result | Source | Validity | What it rules against | What it does not rule out |
|---|---|---|---|---|---|
| `NEG-2026-0001` | R1 found no measurable free-energy PredictionRMSE advantage over null (`+0.0040`, `p=0.8660`, CI spans zero). | `EXP-2026-0001` | valid negative | advantage of the tested legacy policy in R1 | small effects, other environments, other formulations, formal equivalence |
| `NEG-2026-0002` | Tier-2 legacy detector fell from 32/32 originals to 0/32 paraphrases. | `EXP-2026-0002` | valid negative | inference that the exact-keyword benchmark establishes robust semantics | all semantic systems or all possible detector revisions |
| `NEG-2026-0003` | Tier-1 v2 detected 0/32 originals and 0/32 paraphrases. | `EXP-2026-0002` | valid negative | adequacy of that path for the tested detection task | paraphrase sensitivity conditional on successful original detection |
| `NEG-2026-0004` | Legacy Q6 emitted `CERTAIN` on a fabricated irrelevant response. | `EXP-2026-0008` | valid negative failure case | claim that the historical emitter was uniformly honest/calibrated | population ECE, calibration of a revised system |
| `NEG-2026-0005` | E0 recorded zero growth events. | `EXP-2026-0004` | valid methodological failure; invalid H* test | operability of that execution's treatment | H* itself |

## Interpretation notes

### R1

The scientifically correct wording is “no measurable advantage was detected in the tested design.” The wide confidence interval prevents a small-effect equivalence claim. R1 still has high value because it blocks an unearned positive mechanism claim and exposes measurement gaps.

### EXP-0

The complete paired collapse is strong for the tested concept set. The causal explanation “exact lexical lookup” is supported by the frozen intervention, but broad claims about understanding remain outside scope.

### Tier-1 v2

Zero performance in both arms is not evidence of robustness. It is an assay floor for that path and should not be combined with Tier-2 as if both tested the same conditional hypothesis successfully.

### Calibration failure

A single hard failure can refute a zero-tolerance honesty claim for the historical instance. It cannot estimate how often the failure occurs. That requires EXP-1.

### E0

The E0 record is included because failed treatment activation is permanent scientific knowledge. Its negative content is about the experimental mechanism's operability, not the target hypothesis.

## Preservation rule

None of these records may be deleted because a mechanism is later revised. A later positive result must coexist with, scope, and explain the earlier negative record; it does not erase it.
