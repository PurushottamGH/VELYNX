# DV-b Recomputation with Stricter Methodology

**[FACT]** Per `M_STATISTIC_SPECIFICATION.md` (Sprint 1.3 companion), the M statistic
from the n=20 production run was recomputed under (a) Hungarian-alignment,
(b) ARI as a K'≠K fallback, and (c) a block-shuffled self-null replacing the
C3 reference.

Source data: `evidence/experiment_logs/run_20260704_n20/aggregated_results.json`
(raw per-step dump, ~94 MB — **kept out of git**; sha256 recorded in the
provenance table below. Committed summaries + configs + the recompute script
reproduce every statistic here.)
Script: `recompute_m_hungarian.py`

## Per-Seed Results

K (ground truth) = 10, K' (learned) = 2 in all 20 seeds. C3 also has K' = 2.
K' = K in 0/20 seeds, so the Hungarian alignment falls back to the
"pad smaller side" path (matches 2 of 10 true clusters).

| seed | legacy M (C3 null) | aligned M (C3 null) | aligned M (self-null) | ARI-diff (C3) | ARI-diff (self-null) |
|------|--------------------|---------------------|------------------------|---------------|----------------------|
| 42 | 0.2837 | 0.2837 | -0.7163 | 0.0883 | -0.9146 |
| 43 | 0.2199 | 0.2199 | -0.7800 | 0.1180 | -0.8821 |
| 44 | 0.3668 | 0.3668 | -0.6330 | 0.1761 | -0.8237 |
| 45 | 0.2925 | 0.2925 | -0.3868 | 0.1400 | -0.6539 |
| 46 | 0.3435 | 0.3435 | -0.6564 | 0.1505 | -0.8492 |
| 47 | 0.3981 | 0.3981 | -0.2763 | 0.1956 | -0.5850 |
| 48 | 0.1300 | 0.1300 | -0.8692 | 0.0432 | -0.9738 |
| 49 | 0.3529 | 0.3529 | -0.6470 | 0.1513 | -0.8488 |
| 50 | 0.3180 | 0.3180 | -0.3246 | 0.1639 | -0.5929 |
| 51 | 0.3192 | 0.3192 | -0.3219 | 0.1439 | -0.6039 |
| 52 | 0.2740 | 0.2740 | -0.4460 | 0.1045 | -0.7269 |
| 53 | 0.4242 | 0.4242 | -0.5758 | 0.2125 | -0.7875 |
| 54 | 0.3728 | 0.3728 | -0.6272 | 0.1494 | -0.8510 |
| 55 | 0.1492 | 0.1492 | -0.8508 | 0.0877 | -0.9122 |
| 56 | 0.3383 | 0.3383 | -0.6617 | 0.1756 | -0.8244 |
| 57 | 0.3078 | 0.3078 | -0.6922 | 0.1421 | -0.8580 |
| 58 | 0.0410 | 0.0410 | -0.9589 | 0.0230 | -0.9765 |
| 59 | 0.2310 | 0.2310 | -0.7689 | 0.1410 | -0.8590 |
| 60 | 0.4051 | 0.4051 | -0.5949 | 0.1863 | -0.8139 |
| 61 | 0.3296 | 0.3296 | -0.3223 | 0.1601 | -0.5962 |

## Aggregate

| Method | Mean | Std | SE | Margin (2·SE, floor 0.02) | DV-b vs margin | DV-b vs 0.044 |
|--------|------|-----|----|---------------------------|----------------|---------------|
| Legacy (unaligned, C3 null) | 0.2949 | 0.0984 | 0.0220 | 0.0440 | **PASS** | **PASS** |
| Hungarian-aligned, C3 null | 0.2949 | 0.0984 | 0.0220 | 0.0440 | **PASS** | **PASS** |
| Hungarian-aligned, block-shuffled self-null | -0.6055 | 0.2003 | 0.0448 | 0.0896 | **FAIL** | **FAIL** |
| ARI, C3 null | 0.1376 | 0.0484 | 0.0108 | 0.0216 | **PASS** | **PASS** |
| ARI, block-shuffled self-null | -0.7967 | 0.1267 | 0.0283 | 0.0567 | **FAIL** | **FAIL** |

## Interpretation

1. **Hungarian alignment is a no-op for K'=2 vs K=10.** With 2 learned
   clusters, the alignment permutes both sides trivially, and NMI is
   permutation-invariant. The aligned and unaligned values are identical
   to 4 decimal places across all 20 seeds. Alignment matters when K'≈K
   and the matching is genuinely ambiguous; here, it is not.

2. **The block-shuffled self-null inverts the M sign.** This is the
   critical finding. Both T and C3 produce 2-cluster sequences that are
   smoothings of the 10-state true generator. The shared low-frequency
   structure inflates `NMI(learned, C3)`, which inflates M. Once the
   self-null strips the predictor's own marginals and short-range runs
   (the smoothing signal both T and C3 share), the residual temporal
   signal is *negative*: the predictor's specific temporal ordering
   correlates **less** with truth than a temporally-scrambled version of
   itself does, because the 2-state model cannot distinguish 10 true
   states and its ordering is dominated by smoothing artifacts.

3. **ARI agrees with NMI on the sign.** ARI is alignment-free and
   confirmatory: positive under C3 null, negative under self-null.

## Consequence for the n=20 verdict

The original DV-b verdict (PASS, M=0.2949) holds only under the C3 null
as specified in the pre-registered design. Under the stricter self-null
prescribed in `M_STATISTIC_SPECIFICATION.md` §3, DV-b shows no
trustworthy positive emergence (self-null M=−0.6055, ~6.8× past the
0.0896 self-null margin). The corrected reading of the two DVs:
- DV-a: **untested, not failed.** T=C1=C2 because growth never fired —
  and growth could not fire: the MDL trigger is unit-incommensurate
  (F-A). "0/720" is a trigger-unit artifact, not an H\* result;
  attempts-toward-kill = 0.
- DV-b: **no trustworthy positive emergence.** Negative under the
  self-null, but confounded by the K'=2 bottleneck and disconnected from
  H\* since capacity never grew. The original PASS was a C3-null artifact.

The previously-reported M>0 result must be characterized as
*null-reference-dependent* in any publication. The 0.044 margin is
**not** the right bar — the self-null margin of 0.0896 is, and it is
**not** met.

## Self-null robustness to the implementation gap (verified)

**[FACT]** For 2 of 20 seeds (42, 58) the block-shuffled self-null was
found identical to the learned sequence (the predictor's inferred
sequence had too few distinct runs for the block-shuffle to reorder
anything). When `null == learned`, `NMI(learned, null) = 1`, which drives
`M = NMI(learned, true) − 1` toward its **most negative possible bound** —
consistent with seeds 42 and 58 sitting among the most negative self-null
values in the per-seed table (−0.7163 and −0.9589).

The mechanism therefore inflates the *magnitude* of the negative aggregate
but **cannot flip its sign.** Direction is robust to the gap:

| Set | n | Mean M (self-null) | vs 0.0896 margin |
|-----|---|--------------------|------------------|
| All seeds | 20 | −0.6055 | ~6.8× (FAIL) |
| Drop seeds 42, 58 | 18 | −0.5797 | ~6.5× (FAIL) |

Removing both degenerate seeds moves the aggregate from −0.6055 to
−0.5797 — still a wide FAIL, ~6.5× past the 0.0896 self-null margin. The
DV-b FAIL direction does not depend on the 2 affected seeds. The
implementation gap is queued as a Sprint 1.3 prerequisite (validate the
block-shuffle null construction generally, not just patch 2 seeds), but it
does not change the Sprint 1 disposition.

## Recommendation for Sprint 1.3 / publication

1. Report M under **both** the C3 null and the block-shuffled self-null
   in the main text or supplementary. Do not present the M=0.2949 result
   without the self-null companion.
2. Treat the negative self-null result as a substantive finding about
   the predictor's 2-state bottleneck, not a methodological nit. With
   K'=2 and K=10, the predictor cannot in principle recover 10 latent
   states, so any positive M under any null is at best a partial-credit
   signal.
3. The forced-growth experiment in Sprint 1.3 is the right next step:
   forcing capacity to k=1,2,4,8 will let us see whether M (under both
   nulls) tracks final capacity, which is the falsifiable prediction
   the current data cannot test.

## Reproducibility

- Script: `recompute_m_hungarian.py`
- Block-shuffle seed: 20260107 (preregistered)
- Self-null block length: median run length of the predictor's own
  inferred sequence, recomputed per seed
- All other parameters match the preregistration in
  `M_STATISTIC_SPECIFICATION.md`

## Raw source-data provenance (not committed to git)

The raw per-step `aggregated_results.json` dumps are large (~205 MB total)
and are intentionally excluded from git (`.gitignore`) to keep the repository
lean. The committed summaries (`06_statistical_results.md`,
`growth_diagnostics.md`, this file's per-seed table), configs, and
`recompute_m_hungarian.py` reproduce every reported statistic. For provenance,
the sha256 of each raw file is recorded here (verify with
`sha256sum <file>`):

| Raw file | sha256 |
|----------|--------|
| `run_20260704_n20/aggregated_results.json` (n=20, primary source) | `1207462a59fef9fb1ebfd2c772f1ebbf11d68d05c28683614b51c26d30e17921` |
| `run_20260704T125008Z_s42_n5/aggregated_results.json` | `27870808f26e7b9b9d32d5981b0559a034ca0926b4186e005e370136ad03f1bc` |
| `run_20260704T125108Z_s42_n5/aggregated_results.json` | `911b894ace85687efb4a5a4bda0aff0d917bca2b56421ecf7e67551119e1e56e` |
| `run_seed50/aggregated_results.json` | `57f5213a0ce867ae0fad98e61531ea613a12cf2b81df308a1ee35e60130b5619` |
| `seed_51/aggregated_results.json` | `3a6b57a799c5c9434351ef6d76ca18c896fa07da74c565d9e41e421905c8c6ca` |
| `seed_52/aggregated_results.json` | `26c525cb349ef537c6742865fde34005404fb0a9de93bb7fbf597951bd31e4f1` |
| `seed_53/aggregated_results.json` | `8148b2cb17703f309db8cd7bf80a98300e6270c8024a2369ecde2184772ecd61` |
| `seed_54/aggregated_results.json` | `123d69bc4c291ceb563dc1ce49bd4070fcdaa2daf9f50c9c22843fec14157382` |
| `seed_55/aggregated_results.json` | `2f976fa27bf60cb111609b4d63087a4305095594ba6663b716ed8e0755cd7332` |
| `seed_56/aggregated_results.json` | `cfa72dd9f46bf249f44348e6deeff31b3a249922413b7e2ed78309e7f5caf49c` |
| `seed_57/aggregated_results.json` | `8c6ed3956b21d2515ab301320805c5031c4b70254355b87c92755fe681d35cd9` |
| `seed_58/aggregated_results.json` | `a7c4337abe2f3fda12a483207056dfe8eed3c199129feabed4c334659685e35a` |
| `seed_59/aggregated_results.json` | `1dfd01ee7c71ea530190bdcb5cd230b74bb9b1976028b7595f260eb2992bb1a6` |
| `seed_60/aggregated_results.json` | `89527d26bb082796b1b36a65f113285911396950dd1a318ed5126c09a57e4c54` |
| `seed_61/aggregated_results.json` | `80943760426d0211eb6639ad26df8b406b2f1cf0b28b47b4b7f12e5e21bdba4d` |

## Files

- `recompute_m_hungarian.py` — full analysis script
- `M_STATISTIC_SPECIFICATION.md` — the preregistered methodology
- `evidence/12_m_recomputation.md` — this report
- `LIMITATIONS.md` — updated with the new finding (Limitations §3,
  Mandatory Limitation #11)
