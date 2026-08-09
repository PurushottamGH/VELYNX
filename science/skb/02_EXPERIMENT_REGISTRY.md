# P1 Experiment Registry — SKB v1.0

- **State date:** 2026-07-28
- **Canonical machine record:** `science/SKB_RECORDS_v1.0.yaml`
- **Distinction:** `Closed` means interpretation is recorded, not that the tested claim was supported.

## Experiment families

| ID | Legacy | Question | Phase | Status | Result validity | Scientific outcome |
|---|---|---|---|---|---|---|
| `EXP-2026-0001` | R1 | Does FreeEnergyPolicy improve measurable outcomes over simpler policies? | Discovery | Closed | valid negative | No measurable PredictionRMSE advantage over null; five of six primary metrics unavailable |
| `EXP-2026-0002` | EXP-0 | Does concept detection survive keyword-free paraphrase? | Discovery | Closed | valid negative | Tier-2 collapsed 32/32 to 0/32; Tier-1 v2 was 0/32 in both conditions |
| `EXP-2026-0003` | M0 | Can v0 produce reproducible forgetting and replay-associated contrasts? | Discovery | Interpreted | valid indeterminate | Assay usable for Discovery; causal replay and surprise claims blocked |
| `EXP-2026-0004` | E0 | Does error-gated growth beat fixed, decoupled, and shuffled controls? | Discovery | Interpreted | invalid | Growth never activated; H* untested |
| `EXP-2026-0005` | EXP-1 | Are retrieval confidence tiers calibrated? | Discovery | Designed | not run | Awaiting representative frozen query set and adjudication |
| `EXP-2026-0006` | EXP-2 | Does affective framing improve objective task outcomes? | Discovery | Designed | not run | Awaiting independent third-party tasks |
| `EXP-2026-0007` | V0-1..V0-4 | Can v0 assay validity and replay mechanisms survive matched validation? | Validation | Blocked—confirmatory | not run | Pilot questions remain approved; no confirmatory execution until DEC-2026-0010 readiness gates pass |
| `EXP-2026-0008` | six-query soul probe | How does the legacy path behave on direct, relational, and implicit queries? | Discovery | Closed | valid negative | Recorded a hard `CERTAIN` fabrication failure; not a population calibration study |
| `EXP-2026-0009` | EXP-Z0 | Can the pipeline detect a known historical-carrier effect and reject impostors? | Discovery | Designed | not run | Instrument-calibration experiment; licenses no intelligence claim |

## Completed evidence

### `EXP-2026-0001` — R1

- **Design:** 6 policies × 2 replay horizons × 2 noise levels × 3 seeds = 72 runs, 700 ticks each.
- **Primary observable:** PredictionRMSE.
- **Treatment versus null:** `0.2991 ± 0.0976` versus `0.2951 ± 0.0975`; difference `+0.0040`; `p=0.8660`; 95% CI `[-0.1163, 0.1251]`.
- **Valid conclusion:** no measurable advantage in this test.
- **Not established:** equivalence, universal ineffectiveness, or validity of the proxy objective.

### `EXP-2026-0002` — EXP-0

- **Dataset:** 32 paired original and keyword-free paraphrase items.
- **Tier-2 legacy:** original `1.0`, paraphrase `0.0`; McNemar exact `p=4.656612873077393e-10`; bootstrap difference CI `[1.0, 1.0]`.
- **Tier-1 v2:** original `0.0`, paraphrase `0.0`; `p=1.0`.
- **Valid conclusion:** the legacy Tier-2 exact-keyword benchmark did not establish paraphrase-robust semantic detection.

### `EXP-2026-0003` — M0

| Variant | Tail online log loss | Mean forgetting field | Replay updates |
|---|---:|---:|---:|
| online | 0.6849 | +2.4516 | 0 |
| replay_always | 1.1819 | +0.6405 | 32,000 |
| replay_surprise | 0.7593 | +1.4761 | 4,292 |

Nine implementation tests passed. This establishes deterministic behavior and assay sensitivity for the reviewed setting. The conditions simultaneously changed historical exposure, update count, decay applications, replay budget, and compute; hence the result is indeterminate for causal mechanism claims.

### `EXP-2026-0004` — E0

- Three seeds were present where five were required.
- More importantly, all recorded conditions had zero growth events.
- The artifact diagnosed a per-symbol entropy-delta versus total-data-code penalty mismatch.
- **Validity ruling:** invalid for H*. The treatment was absent.

### `EXP-2026-0008` — Legacy six-query probe

Q6 routed through irrelevant retrieval, produced a fabricated answer, and emitted `CERTAIN`. This is a valid failure observation for the historical system. It is too small and manually selected to estimate ECE or prevalence.

## Designed experiments and prerequisites

### `EXP-2026-0005` — Calibration

Must freeze query strata, adjudication, tier-to-probability mapping, ECE/Brier metrics, constant-confidence and retrieval baselines, and a zero-tolerance hard-fabrication criterion before execution.

### `EXP-2026-0006` — Affective indexing

Must use identical tasks under framed and neutral prompts, objective scoring, no tasks authored around the affect map, and no per-task schema rewriting.

### `EXP-2026-0007` — v0 validation family

**Readiness ruling:** The scientific design remains approved, but confirmatory execution is blocked. Discovery Cycle 001 exploratory pilots may begin only after the minimum apparatus gates in `DEC-2026-0010` pass; pilot results remain non-confirmatory. Confirmatory execution additionally requires the pre-existing preregistration, construct-validity, causal-control, seed, and resource-matching requirements.

Minimum causal sequence:

1. validate degradation against no-decay and oracle/frozen controls;
2. match update count and decay applications for historical replay;
3. compare surprise timing with equal-budget random timing;
4. separate environment, trajectory, replay, probe, and task-order randomness;
5. reserve untouched confirmation seeds.

### `EXP-2026-0009` — Pipeline calibration

The instrument must show that an oracle wins, a memoryless system stays at its analytic ceiling, treatment beats that ceiling, carrier ablation destroys the treatment advantage, and temporal shuffling removes the effect. A pass validates the measurement pipeline only.

## Execution records

| Execution ID | Experiment | Recoverable source | Classification |
|---|---|---|---|
| `EXP-2026-0001-R0001` | R1 | `evidence/research_artifacts/research_artifacts/run_20260627T022109/ablation_report.md` | completed, valid negative |
| `EXP-2026-0002-R0001` | EXP-0 | `run_20260703T070728Z_seed1_tier12` | completed; summary duplicates later run |
| `EXP-2026-0002-R0002` | EXP-0 | `run_20260703T074034Z_seed1_tier12` | completed, canonical migrated artifact |
| `EXP-2026-0003-R0001` | M0 | independently reproduced review command | completed, valid indeterminate |
| `EXP-2026-0004-R0001` | E0 | `run_20260726T095330Z_s42_n3` | completed execution, invalid hypothesis test |
| `EXP-2026-0008-R0001` | six-query probe | `archive/data/soul_test_report.md` | completed qualitative probe |

## Unresolved registry issues

1. The historical `experiment_registry.yaml` labels E0 `running`; the recovered aggregate is completed but invalid. SKB state governs scientific interpretation.
2. Older certification documents reported EXP-0 unavailable or unrun; current artifact directories demonstrate that it was later run. The transition history is missing.
3. M0's exact default-run immutable artifact was not preserved under a matching committed revision.
4. The E1–E13 coverage matrix establishes mapped engineering tests, not completed scientific experiments; those rows were not promoted into canonical experiment records without result artifacts and claim-relative interpretations.
