"""Seed-clustered paired statistics for P1-LN-DEC."""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple


MASTER_SEEDS: Tuple[int, ...] = (1, 7, 42, 99, 1234, 2027, 31415, 65537, 100003, 424242)

# Two-sided Student-t critical values for a 95% interval, df 1..30.  The
# protocol uses ten seeds; keeping the small table local avoids a scipy runtime
# dependency in the isolated runner.
_T95 = {
    1: 12.706,
    2: 4.303,
    3: 3.182,
    4: 2.776,
    5: 2.571,
    6: 2.447,
    7: 2.365,
    8: 2.306,
    9: 2.262,
    10: 2.228,
    11: 2.201,
    12: 2.179,
    13: 2.160,
    14: 2.145,
    15: 2.131,
    16: 2.120,
    17: 2.110,
    18: 2.101,
    19: 2.093,
    20: 2.086,
    21: 2.080,
    22: 2.074,
    23: 2.069,
    24: 2.064,
    25: 2.060,
    26: 2.056,
    27: 2.052,
    28: 2.048,
    29: 2.045,
    30: 2.042,
}


@dataclass(frozen=True)
class SeedContrast:
    """One seed-level paired contrast; positive means candidate is better."""

    seed: int
    family: str
    baseline: str
    candidate_nll: float | None
    baseline_nll: float | None
    failed: bool = False
    failure_reason: str | None = None

    @property
    def difference(self) -> float | None:
        if self.failed or self.candidate_nll is None or self.baseline_nll is None:
            return None
        return self.baseline_nll - self.candidate_nll


@dataclass(frozen=True)
class PairedStatistics:
    """Complete seed-clustered summary, including failed seeds."""

    expected_seeds: Tuple[int, ...]
    observed_seeds: Tuple[int, ...]
    failed_seeds: Tuple[int, ...]
    differences: Tuple[float, ...]
    mean_paired_nll_difference: float | None
    relative_nll_reduction: float | None
    ci95: Tuple[float, float] | None
    sign_permutation_p: float | None
    complete: bool
    failure_policy: str


def compute_paired_statistics(
    contrasts: Sequence[SeedContrast],
    *,
    expected_seeds: Sequence[int] = MASTER_SEEDS,
) -> PairedStatistics:
    """Compute the primary estimand at the seed cluster, never item count."""
    expected = tuple(int(seed) for seed in expected_seeds)
    by_seed = {contrast.seed: contrast for contrast in contrasts}
    observed = tuple(sorted(by_seed))
    failed = tuple(
        seed
        for seed in expected
        if seed not in by_seed or by_seed[seed].failed or by_seed[seed].difference is None
    )
    differences = tuple(
        float(by_seed[seed].difference)
        for seed in expected
        if seed in by_seed and by_seed[seed].difference is not None
    )
    complete = not failed and set(observed) == set(expected)
    if not differences:
        return PairedStatistics(
            expected_seeds=expected,
            observed_seeds=observed,
            failed_seeds=failed,
            differences=(),
            mean_paired_nll_difference=None,
            relative_nll_reduction=None,
            ci95=None,
            sign_permutation_p=None,
            complete=False,
            failure_policy="failed_or_diverged_seeds_are retained and block the gate",
        )

    mean = sum(differences) / len(differences)
    baseline_values = [
        float(by_seed[seed].baseline_nll)
        for seed in expected
        if seed in by_seed and by_seed[seed].baseline_nll is not None
    ]
    baseline_mean = sum(baseline_values) / len(baseline_values) if baseline_values else 0.0
    relative = mean / baseline_mean if baseline_mean > 0.0 else None
    ci = _mean_ci(differences) if complete else None
    permutation = _sign_permutation_p(differences) if complete else None
    return PairedStatistics(
        expected_seeds=expected,
        observed_seeds=observed,
        failed_seeds=failed,
        differences=differences,
        mean_paired_nll_difference=mean if complete else None,
        relative_nll_reduction=relative if complete else None,
        ci95=ci,
        sign_permutation_p=permutation,
        complete=complete,
        failure_policy="failed_or_diverged_seeds_are retained and block the gate",
    )


def _mean_ci(values: Sequence[float]) -> Tuple[float, float]:
    mean = sum(values) / len(values)
    if len(values) < 2:
        return (mean, mean)
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    standard_error = math.sqrt(variance / len(values))
    critical = _T95.get(len(values) - 1, 1.96)
    margin = critical * standard_error
    return (mean - margin, mean + margin)


def _sign_permutation_p(values: Sequence[float]) -> float:
    """Exact two-sided sign-permutation sensitivity check."""
    if not values:
        return 1.0
    observed = abs(sum(values))
    extreme = 0
    total = 2 ** len(values)
    for signs in itertools.product((-1.0, 1.0), repeat=len(values)):
        if abs(sum(sign * value for sign, value in zip(signs, values))) >= observed - 1e-12:
            extreme += 1
    return extreme / total


__all__ = [
    "MASTER_SEEDS",
    "PairedStatistics",
    "SeedContrast",
    "compute_paired_statistics",
]

