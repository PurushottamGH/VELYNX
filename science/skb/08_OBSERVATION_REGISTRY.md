# P1 Observation Registry — SKB v1.0

- **State date:** 2026-07-28
- **Rule:** Observations state what was recorded. Causal and evaluative meaning belongs in Evidence and Decision records.

| ID | Observation | Source | Primary limitation |
|---|---|---|---|
| `OBS-2026-0001` | R1 free_energy PredictionRMSE `0.2991 ± 0.0976`; null `0.2951 ± 0.0975`; effect `+0.0040`; `p=0.8660`; CI `[-0.1163, 0.1251]`. | R1 ablation report | wide interval; three seeds/cell |
| `OBS-2026-0002` | Five of R1's six declared primary metrics were unavailable. | R1 ablation report | substrate-specific availability |
| `OBS-2026-0003` | EXP-0 Tier-2: originals 32/32, paraphrases 0/32; exact `p=4.656612873077393e-10`; bootstrap CI `[1,1]`. | EXP-0 summary | one 32-concept set |
| `OBS-2026-0004` | EXP-0 Tier-1 v2: originals 0/32, paraphrases 0/32; `p=1.0`; CI `[0,0]`. | EXP-0 summary | original-condition floor |
| `OBS-2026-0005` | Inspected E0 execution recorded zero growth events in every condition for three seeds. | E0 aggregate | execution-specific |
| `OBS-2026-0006` | E0 diagnostic recorded a per-symbol entropy-delta versus total-data-code penalty mismatch. | E0 aggregate | diagnosis scoped to implementation/protocol |
| `OBS-2026-0007` | E0 aggregate recorded three seeds available and five required. | E0 aggregate | secondary to absent treatment |
| `OBS-2026-0008` | Reproduced M0 seed-0 outputs: online `0.6849/+2.4516/0`; always `1.1819/+0.6405/32000`; surprise `0.7593/+1.4761/4292`. | M0 scientific review | one seed, bundled variants |
| `OBS-2026-0009` | Nine v0 rig tests passed. | M0 scientific review | conformance only |
| `OBS-2026-0010` | Reviewed v0 code was uncommitted; stored summary used 300 rather than reported 2000 steps/task. | M0 scientific review | provenance observation |
| `OBS-2026-0011` | Legacy Q6 produced an irrelevant fabricated response and emitted `CERTAIN`. | soul test report | one manually assessed query |
| `OBS-2026-0012` | Injection audit listed 48 injection classes, about 150 governing constants, and zero data-derived/systematically searched values. | designer-injection report | static audit; percentage impacts estimated |
| `OBS-2026-0013` | Old certification text says EXP-0 was unavailable/unrun; current repository contains paraphrases and two result directories. | migration audit | transition history missing |
| `OBS-2026-0014` | Legacy labels `FACT`, `ACCEPTED`, `KEEP`, `canonical`, and `rejected` have non-equivalent meanings across records. | terminology audit | documentary observation |
| `OBS-2026-0015` | Smoke manifest recorded `code_state=dirty`, `untracked_rig=true`, and 39 dirty entries; the live M1 apparatus is absent from `git ls-files`. | manifest + git provenance audit | revision-state observation; may change after commit |
| `OBS-2026-0016` | Committed CI did not run M1/v0-rig tests or the v0 smoke config; those steps exist only in uncommitted workflow changes. | working-tree versus `HEAD` workflow comparison | modified workflow has not run remotely |
| `OBS-2026-0017` | Artifact-integrity targets legacy `artifacts/experiments`; reproducibility checks legacy configs and path existence rather than the M1 apparatus. | script audit + direct execution | legacy failures are distinct from M1 integrity |
| `OBS-2026-0018` | Local working-tree checks completed 202 M1/v0-rig tests at 88.5% line coverage; Black and config smoke passed. | local verification commands | conformance only; not clean-checkout or remote-CI evidence |
| `OBS-2026-0019` | `code_state` is recorded, but no assessed path rejects a dirty/untracked run from confirmatory evidence. | static enforcement audit | future code may add enforcement |

## Source paths

- R1: `evidence/research_artifacts/research_artifacts/run_20260627T022109/ablation_report.md`
- EXP-0: `experiments/EXP0/artifacts/run_20260703T074034Z_seed1_tier12/exp0_summary.json`
- E0: `artifacts/experiments/E0/run_20260726T095330Z_s42_n3/aggregated_results.json`
- M0: `P1_V0_M0_SCIENTIFIC_REVIEW.md`
- Calibration probe: `archive/data/soul_test_report.md`
- Injection audit: `research/designer_injection_report.md`
- M1 readiness audit: `artifacts/runs/smoke/smoke__seed0__57055578123a/manifest.json`, `.github/workflows/ci.yml`, `scripts/verify_artifact_integrity.py`, `scripts/verify_reproducibility.py`, `m1-coverage.xml`

## Observation discipline examples

Permitted:

> “Replay_always had lower seed-0 mean forgetting than online and used 32,000 replay updates.”

Not an observation:

> “Replay caused retention.”

Permitted:

> “E0 recorded zero growth events and a units-mismatch diagnostic.”

Not an observation:

> “Error-gated growth does not work.”

Permitted:

> “The detector scored 32/32 originals and 0/32 keyword-free paraphrases.”

Interpretation belongs elsewhere:

> “The tested benchmark did not establish paraphrase-robust semantic understanding.”
