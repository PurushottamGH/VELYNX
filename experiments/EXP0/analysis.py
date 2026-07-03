"""EXP-0 statistical analysis.

Implements exactly the tests pre-registered in EXP0_PREREGISTRATION.md /
EXP0_STATISTICAL_ANALYSIS.md:

  * McNemar's exact test on paired binary (hit/miss) outcomes -- the primary
    test for DV-1 (Tier 2) and DV-2 (Tier 1).
  * A paired bootstrap 95% CI on the hit-rate difference, in the same style
    as research/stats.py's BootstrapMeanDifferenceTest, so EXP-0's output is
    directly comparable in format to the R1 ablation's reporting.
  * Holm-Bonferroni correction across the two pre-registered primary tests.

Standard-library only (matches research/stats.py's no-scipy convention).
Deterministic given a seed: uses random.Random(seed), never the global
random module or time-based seeding.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class McNemarResult:
    n01: int          # original hit, paraphrase miss  (the "collapse" direction)
    n10: int          # original miss, paraphrase hit
    n_concordant: int
    n_discordant: int
    p_value: float

    @property
    def direction(self) -> str:
        if self.n01 > self.n10:
            return "collapse (paraphrase worse than original)"
        if self.n10 > self.n01:
            return "inverted (paraphrase better than original)"
        return "no asymmetry"


def mcnemar_exact(hits_original: list[bool], hits_paraphrase: list[bool]) -> McNemarResult:
    """Exact two-sided McNemar test via the binomial distribution on
    discordant pairs. No continuity correction (exact test is preferred at
    this sample size, N=32, per EXP0_STATISTICAL_ANALYSIS.md)."""
    if len(hits_original) != len(hits_paraphrase):
        raise ValueError("hits_original and hits_paraphrase must be the same length")

    n01 = sum(1 for o, p in zip(hits_original, hits_paraphrase) if o and not p)
    n10 = sum(1 for o, p in zip(hits_original, hits_paraphrase) if (not o) and p)
    n_discordant = n01 + n10
    n_concordant = len(hits_original) - n_discordant

    if n_discordant == 0:
        p_value = 1.0
    else:
        k = min(n01, n10)
        tail = sum(math.comb(n_discordant, i) for i in range(0, k + 1))
        p_value = min(1.0, 2 * tail * (0.5 ** n_discordant))

    return McNemarResult(n01=n01, n10=n10, n_concordant=n_concordant,
                          n_discordant=n_discordant, p_value=p_value)


def paired_bootstrap_ci(hits_original: list[bool], hits_paraphrase: list[bool],
                         *, iterations: int = 10_000, seed: int = 0,
                         ci: float = 0.95) -> dict:
    """Bootstrap CI for (rate_original - rate_paraphrase), resampling PAIRS
    (item indices) with replacement -- correct for paired/within-subject
    data, unlike resampling the two groups independently."""
    n = len(hits_original)
    if n != len(hits_paraphrase):
        raise ValueError("hits_original and hits_paraphrase must be the same length")
    rng = random.Random(seed)
    diffs = []
    for _ in range(iterations):
        idx = [rng.randrange(n) for _ in range(n)]
        ro = sum(hits_original[i] for i in idx) / n
        rp = sum(hits_paraphrase[i] for i in idx) / n
        diffs.append(ro - rp)
    diffs.sort()
    lo_pct = (1 - ci) / 2
    hi_pct = 1 - lo_pct
    lo = diffs[int(lo_pct * iterations)]
    hi = diffs[min(iterations - 1, int(hi_pct * iterations))]
    point = sum(hits_original) / n - sum(hits_paraphrase) / n
    return {"point_estimate": point, "ci_low": lo, "ci_high": hi,
            "iterations": iterations, "seed": seed}


def holm_bonferroni(named_p_values: dict[str, float], alpha: float = 0.05) -> dict[str, dict]:
    """Holm-Bonferroni step-down correction. Returns, per test name, the
    adjusted alpha threshold it was compared against and whether it survives."""
    ordered = sorted(named_p_values.items(), key=lambda kv: kv[1])
    m = len(ordered)
    results: dict[str, dict] = {}
    still_significant = True
    for rank, (name, p) in enumerate(ordered):  # rank is 0-indexed
        threshold = alpha / (m - rank)
        significant = still_significant and (p <= threshold)
        if not significant:
            still_significant = False  # step-down: once one fails, all remaining fail
        results[name] = {"p_value": p, "threshold": threshold,
                          "rank": rank + 1, "significant_after_correction": significant}
    return results


def hit_rate(hits: list[bool]) -> float:
    return sum(hits) / len(hits) if hits else float("nan")


def render_report(*, tier_name: str, concepts: list[str],
                   hits_original: list[bool], hits_paraphrase: list[bool],
                   mcnemar: McNemarResult, bootstrap: dict,
                   alpha_used: float) -> str:
    lines = [
        f"### {tier_name}",
        "",
        f"- N (paired items): {len(concepts)}",
        f"- Hit rate, original:   {hit_rate(hits_original):.3f} "
        f"({sum(hits_original)}/{len(hits_original)})",
        f"- Hit rate, paraphrase: {hit_rate(hits_paraphrase):.3f} "
        f"({sum(hits_paraphrase)}/{len(hits_paraphrase)})",
        f"- McNemar exact test: n01={mcnemar.n01}, n10={mcnemar.n10}, "
        f"discordant={mcnemar.n_discordant}, p={mcnemar.p_value:.5f} "
        f"({mcnemar.direction})",
        f"- Bootstrap 95% CI on rate difference (original - paraphrase): "
        f"[{bootstrap['ci_low']:.3f}, {bootstrap['ci_high']:.3f}] "
        f"(point={bootstrap['point_estimate']:.3f}, "
        f"{bootstrap['iterations']} iters, seed={bootstrap['seed']})",
        f"- Significant at alpha={alpha_used}: {mcnemar.p_value <= alpha_used}",
        "",
    ]
    misses = [c for c, o, p in zip(concepts, hits_original, hits_paraphrase) if o and not p]
    if misses:
        lines.append(f"- Concepts that collapsed (hit on original, miss on paraphrase): "
                      f"{', '.join(sorted(misses))}")
        lines.append("")
    return "\n".join(lines)
