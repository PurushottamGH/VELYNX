# P1 Assumption Registry — SKB v1.0

- **State date:** 2026-07-28
- **Rule:** `Active-Unvalidated` means load-bearing and insufficiently supported, not provisionally true.

| ID | Assumption | Category | Status | Load-bearing for | Consequence if false | Smallest test |
|---|---|---|---|---|---|---|
| `ASM-2026-0001` | Decay-induced v0 degradation is informative about continual interference, not only artificial erasure. | model | Active-Unvalidated | replay/surprise hypotheses | Findings collapse to correction of a constructed erasure rule | decay 0.99 vs 1.0 with oracle excess loss |
| `ASM-2026-0002` | Change from post-learning loss validly measures forgetting when mastery and plasticity are joint. | measurement | Active-Unvalidated | replay/surprise outcomes | Low forgetting may reward weak initial learning | compare final excess loss, BWT, mastery, joint guardrails |
| `ASM-2026-0003` | Environment seed is the primary independent unit for v0 inference. | statistical | Active-Unvalidated | v0 validation | Variance and inference target may be wrong | factorial seed variance decomposition |
| `ASM-2026-0004` | Prediction error is sufficient to drive E0 structure growth. | causal | Active-Unvalidated | H* | No viable developmental signal | operable trigger plus decoupled-growth comparison |
| `ASM-2026-0005` | Learned structure can be distinguished from injected/trivial structure. | measurement | Contradicted in legacy instantiation | H* | Emergence becomes non-identifiable | shuffled/injection-matched null-referenced test |
| `ASM-2026-0006` | A feasible environment can require nontrivial structure without being seeded or linearly trivial. | world | Active-Unvalidated | H* | E0 becomes vacuous or infeasible | offline oracle and fixed/linear challenge |
| `ASM-2026-0007` | Calibration evaluation data represent intended Program A use. | data | Active-Unvalidated | calibration | ECE will not transfer | predefine deployment strata and test heterogeneity |
| `ASM-2026-0008` | Affective indexing can be tested without task-authoring circularity. | human judgment | Active-Unvalidated | affective indexing | Performance may reflect designer alignment | independently frozen third-party task set |
| `ASM-2026-0009` | PH-1 has no current-input leakage and the cue is feasible to retain. | world | Active-Unvalidated | carrier dependence | Experiment cannot identify memory use | analytic ceiling, oracle, ablation, shuffle |
| `ASM-2026-0010` | A clean committed run is reconstructable from recorded code, config, runtime, seeds, and artifacts without hidden local state. | reproducibility | Active-Unvalidated | v0 confirmatory family | Nominally clean evidence may still be irreproducible | isolated repeated clean-checkout run identity |
| `ASM-2026-0011` | CI and verification gates exercise the same platform and artifact surfaces that produce evidence and fail when those surfaces are absent or invalid. | measurement | Contradicted | v0 confirmatory family | Green automation gives false assurance | fresh-checkout gate run plus known-failure sensitivity tests |

## Innate-bias interpretation

The designer-injection audit is incorporated as evidence against silently treating built-in structure as learned structure. Not every fixed constant is scientifically problematic: numerical epsilons and declared experimental settings may be legitimate. The critical question is whether a built-in choice determines the target phenomenon or conclusion.

The following bias classes remain material:

1. **Objective bias:** hand-set proxy weights define what the legacy system optimizes.
2. **Perceptual bias:** authored regimes, sensor mappings, and cluster limits determine available structure.
3. **Ontological bias:** seed concepts, curricula, and thresholds determine what can appear as a concept.
4. **Temporal bias:** decay and replay semantics construct the forgetting process.
5. **Measurement bias:** metrics can be aligned with the mechanism's own objective or reward weak learning.
6. **Selection bias:** thresholds and displayed seeds may have been chosen after outcome access.

## Assumption interaction map

- If `ASM-2026-0002` fails, both replay hypotheses become uninterpretable even if the observed scalar improves.
- If `ASM-2026-0005` fails, H* cannot become science because “emergence” is not identifiable.
- If `ASM-2026-0006` fails, a positive E0 may merely recover an easy authored generator.
- If `ASM-2026-0007` fails, a low aggregate ECE may hide deployment-stratum failure.
- If `ASM-2026-0008` fails, affective-indexing success is circular.
- If `ASM-2026-0009` fails, Experiment Zero can generate either false memory evidence or false rejection.
- Until `ASM-2026-0010` is tested, confirmatory reconstruction and V0-4 variance attribution remain unsafe.
- `ASM-2026-0011` is contradicted in the assessed revision: required automation omitted the live M1 surfaces or targeted legacy paths.

## Retirement policy

An assumption is retired only if it is directly tested, bounded by scope, eliminated from the claim/design, or replaced by a better-supported proposition. Adding code or documenting a rationale does not retire it.
