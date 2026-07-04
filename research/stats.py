"""
research/stats.py
=================

Distribution summaries and an *extensible* hypothesis-test framework
(Sprint R1, Task 4).

Two layers, deliberately separated:

1. :class:`SummaryStatistics` — the descriptive six-number summary the sprint
   requires for every metric: mean, median, standard deviation, 95% confidence
   interval, minimum, maximum (plus the sample count). Pure ``statistics`` /
   ``math``; no third-party dependency.

2. :class:`HypothesisTest` — an abstract base for *inferential* tests, plus a
   registry. This is the "structure the code so future tests can be added
   without redesign" requirement: a t-test, permutation test, or different
   bootstrap variant is added by subclassing and registering, with no change to
   any caller. A non-parametric :class:`BootstrapMeanDifferenceTest` ships as
   the reference implementation precisely because it makes the *fewest*
   distributional assumptions ("do not hard-code statistical assumptions").

Honesty note on the confidence interval
----------------------------------------
The 95% CI on the mean is computed with the Student-t critical value for the
sample's degrees of freedom (small embedded table; falls back to the normal
z=1.96 for large samples or unknown df). This is a parametric approximation that
assumes the sampling distribution of the mean is approximately normal. With the
small seed counts typical here (n=5) that assumption is *not* guaranteed; the
ablation report's "Threats to Validity" states this explicitly, and the
bootstrap test is provided for assumption-light inference.
"""

from __future__ import annotations

import math
import random
import statistics
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Sequence, Type

# ---------------------------------------------------------------------------
# Student-t two-sided 95% critical values by degrees of freedom.
# ---------------------------------------------------------------------------
# A compact table so the CI is honest for small n without pulling in scipy.
# Missing df interpolate to the nearest tabulated lower df (conservative), and
# anything beyond the table falls back to the normal approximation z=1.96.
_T_CRIT_95: Dict[int, float] = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
    6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
    11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131,
    16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
    25: 2.060, 30: 2.042, 40: 2.021, 60: 2.000, 120: 1.980,
}
_Z_CRIT_95 = 1.96


def t_critical_95(df: int) -> float:
    """Two-sided 95% Student-t critical value for ``df`` degrees of freedom.

    Uses the embedded table where possible; for an untabulated ``df`` it picks
    the largest tabulated df not exceeding ``df`` (a conservative, slightly
    wider interval), and falls back to the normal ``z=1.96`` once ``df`` is
    large enough that the difference is negligible.
    """
    if df <= 0:
        return float("nan")
    if df in _T_CRIT_95:
        return _T_CRIT_95[df]
    candidates = [k for k in _T_CRIT_95 if k <= df]
    if not candidates:
        return _T_CRIT_95[1]
    nearest = max(candidates)
    if nearest >= 120:
        return _Z_CRIT_95
    return _T_CRIT_95[nearest]


@dataclass(frozen=True)
class SummaryStatistics:
    """The six-number descriptive summary of a sample, plus its size and CI.

    Every field is ``Optional[float]`` so an *empty* sample (e.g. a metric that
    was unavailable on every run) summarises cleanly to ``None`` rather than
    raising — the honest representation of "we have no data here".
    """

    n: int
    mean: Optional[float]
    median: Optional[float]
    std: Optional[float]
    minimum: Optional[float]
    maximum: Optional[float]
    ci95_low: Optional[float]
    ci95_high: Optional[float]
    #: Standard error of the mean (kept for downstream inferential tests).
    sem: Optional[float] = None

    @classmethod
    def from_samples(cls, samples: Sequence[float]) -> "SummaryStatistics":
        """Summarise a sequence of numbers (``None`` entries are dropped)."""
        data: List[float] = [float(x) for x in samples if x is not None]
        n = len(data)
        if n == 0:
            return cls(
                n=0, mean=None, median=None, std=None,
                minimum=None, maximum=None, ci95_low=None, ci95_high=None,
                sem=None,
            )
        mean = statistics.fmean(data)
        median = statistics.median(data)
        minimum = min(data)
        maximum = max(data)
        if n == 1:
            # A single observation has no spread and no interval.
            return cls(
                n=1, mean=mean, median=median, std=0.0,
                minimum=minimum, maximum=maximum,
                ci95_low=mean, ci95_high=mean, sem=0.0,
            )
        std = statistics.stdev(data)  # sample (n-1) standard deviation
        sem = std / math.sqrt(n)
        half = t_critical_95(n - 1) * sem
        return cls(
            n=n, mean=mean, median=median, std=std,
            minimum=minimum, maximum=maximum,
            ci95_low=mean - half, ci95_high=mean + half, sem=sem,
        )

    def as_dict(self) -> Dict[str, Optional[float]]:
        """JSON-safe mapping, e.g. for ``metrics.json`` / ``summary.json``."""
        return asdict(self)


# ---------------------------------------------------------------------------
# Inferential layer — pluggable hypothesis tests
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TestResult:
    """The outcome of a two-sample hypothesis test.

    ``effect`` is the point estimate of the difference (treatment − baseline)
    in the metric's own units; ``p_value`` is two-sided. ``details`` carries
    test-specific extras (e.g. CI of the difference) without bloating the core.
    """

    name: str
    effect: Optional[float]
    p_value: Optional[float]
    n_baseline: int
    n_treatment: int
    details: Dict[str, float]


class HypothesisTest(ABC):
    """Abstract two-sample test: is *treatment* different from *baseline*?

    Concrete tests implement :meth:`compare`. They must be pure functions of
    their inputs (plus an optional seeded RNG for resampling tests) so a result
    is reproducible. New tests are added by subclassing and calling
    :func:`register_test`; nothing else in the codebase needs to change.
    """

    name: str = "abstract"

    @abstractmethod
    def compare(
        self,
        baseline: Sequence[float],
        treatment: Sequence[float],
    ) -> TestResult:
        raise NotImplementedError


class BootstrapMeanDifferenceTest(HypothesisTest):
    """Non-parametric bootstrap test for a difference in means.

    Makes no distributional assumption: it estimates the sampling distribution
    of the mean difference by resampling each group with replacement, and
    derives a two-sided p-value from a permutation-style sign of the bootstrap
    distribution around zero. Deterministic given its seed.

    This is intentionally the reference test: with the small samples this sprint
    produces, an assumption-light resampling method is more defensible than a
    parametric t-test. A t-test can be added later as a sibling subclass without
    touching this class or any caller.
    """

    name = "bootstrap_mean_difference"

    def __init__(self, iterations: int = 10_000, seed: int = 0) -> None:
        self.iterations = int(iterations)
        self.seed = int(seed)

    def compare(
        self,
        baseline: Sequence[float],
        treatment: Sequence[float],
    ) -> TestResult:
        b = [float(x) for x in baseline if x is not None]
        t = [float(x) for x in treatment if x is not None]
        if not b or not t:
            return TestResult(
                name=self.name, effect=None, p_value=None,
                n_baseline=len(b), n_treatment=len(t), details={},
            )

        observed = statistics.fmean(t) - statistics.fmean(b)
        rng = random.Random(self.seed)

        # Bootstrap the difference of means.
        diffs: List[float] = []
        nb, nt = len(b), len(t)
        for _ in range(self.iterations):
            rb = statistics.fmean(rng.choices(b, k=nb))
            rt = statistics.fmean(rng.choices(t, k=nt))
            diffs.append(rt - rb)

        diffs.sort()
        # Two-sided p-value: fraction of bootstrap diffs on the opposite side of
        # zero from the observed effect (the resampled distribution straddling
        # zero is evidence against a real difference).
        if observed >= 0:
            tail = sum(1 for d in diffs if d <= 0)
        else:
            tail = sum(1 for d in diffs if d >= 0)
        p_value = min(1.0, 2.0 * tail / len(diffs))

        lo = diffs[int(0.025 * len(diffs))]
        hi = diffs[min(len(diffs) - 1, int(0.975 * len(diffs)))]
        return TestResult(
            name=self.name,
            effect=observed,
            p_value=p_value,
            n_baseline=nb,
            n_treatment=nt,
            details={"diff_ci95_low": lo, "diff_ci95_high": hi},
        )


#: Registry of inferential tests, mirroring the policy registry pattern.
TEST_REGISTRY: Dict[str, Type[HypothesisTest]] = {
    BootstrapMeanDifferenceTest.name: BootstrapMeanDifferenceTest,
}


def register_test(cls: Type[HypothesisTest]) -> Type[HypothesisTest]:
    """Register a :class:`HypothesisTest` subclass (usable as a decorator).

    The extension seam for future tests (t-test, permutation, Mann-Whitney):
    define the subclass, decorate it, and it becomes selectable by name with no
    other code change.
    """
    TEST_REGISTRY[cls.name] = cls
    return cls


def build_test(name: str, **params) -> HypothesisTest:
    """Construct a registered hypothesis test by name."""
    try:
        cls = TEST_REGISTRY[name]
    except KeyError:
        valid = ", ".join(sorted(TEST_REGISTRY)) or "(none registered)"
        raise KeyError(
            f"Unknown hypothesis test {name!r}. Registered: {valid}."
        ) from None
    return cls(**params)


__all__ = [
    "SummaryStatistics",
    "t_critical_95",
    "TestResult",
    "HypothesisTest",
    "BootstrapMeanDifferenceTest",
    "TEST_REGISTRY",
    "register_test",
    "build_test",
]
