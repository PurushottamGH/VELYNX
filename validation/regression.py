"""
validation/regression.py
=========================

The **RegressionGate** -- the enforcement point for the project's *Freeze Rule*.

This module is the validation harness's "security guard". Given the metric
scores of a *baseline* run and a *candidate* run, it decides whether the
candidate is allowed to ship. If any **critical** metric (e.g. ``PredictionError``
or ``FalsePositives``) has degraded by more than a fixed tolerance versus the
baseline, the gate fails -- and :func:`assert_no_regression` turns that failure
into a hard :class:`AssertionError`, so a CI step, pre-commit hook, or PR check
can block any change that makes the brain measurably "dumber".

Directionality
--------------
By convention in this codebase every metric in :mod:`validation.metrics`
(Entropy, Surprise, Active Load, Cognitive Energy, and the error/false-positive
style metrics referenced by the Freeze Rule) is **lower-is-better**. The gate
therefore treats a metric as *degraded* when its value goes **up** relative to
the baseline. Metrics that are genuinely higher-is-better (accuracy, recall,
...) can be registered via ``higher_is_better`` so the gate flips the sign for
them.

Contract
--------
``RegressionGate`` implements :class:`validation.interfaces.Regression`, so its
:meth:`~RegressionGate.is_improvement` returns a plain ``bool`` as the ABC
requires. The richer, fully-itemised verdict -- which metrics improved, which
regressed, and a human-readable summary -- is available via
:meth:`~RegressionGate.evaluate`, which returns a :class:`RegressionResult`.

Pure standard library (``math`` + ``dataclasses`` + ``typing``), consistent
with the rest of the ``validation`` subsystem.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Iterable, Mapping, Optional

from validation.interfaces import Regression

# Default noise margin: a critical metric must degrade by MORE than this
# fraction of its baseline value before the gate trips. 0.05 == 5%.
DEFAULT_TOLERANCE = 0.05


# ---------------------------------------------------------------------------
# Result data structure
# ---------------------------------------------------------------------------


@dataclass
class RegressionResult:
    """The itemised verdict of a single :class:`RegressionGate` evaluation.

    Attributes
    ----------
    passed : bool
        ``True`` iff no *critical* metric degraded beyond the gate's
        tolerance (and every critical metric was actually measurable in the
        candidate run). This is the bit the Freeze Rule keys off.
    improvements : dict
        Mapping ``metric_name -> fractional_change`` for every metric that got
        **better**. The value is the magnitude of the improvement as a fraction
        of the baseline (``0.07`` == a 7% improvement).
    regressions : dict
        Mapping ``metric_name -> fractional_change`` for every metric that got
        **worse**. The value is the magnitude of the degradation as a fraction
        of the baseline (``0.07`` == a 7% degradation). Includes both
        tolerated (sub-threshold) and breaching regressions; the ``summary``
        and ``passed`` flag distinguish them.
    summary : str
        A human-readable, multi-line explanation suitable for printing in CI
        logs or attaching to a failed assertion.
    """

    passed: bool
    improvements: Dict[str, float] = field(default_factory=dict)
    regressions: Dict[str, float] = field(default_factory=dict)
    summary: str = ""


# ---------------------------------------------------------------------------
# The gate
# ---------------------------------------------------------------------------


class RegressionGate(Regression):
    """Compare candidate metrics against a baseline and enforce the Freeze Rule.

    Parameters
    ----------
    tolerance : float
        The fractional noise margin. A critical metric may drift by up to
        ``tolerance`` (inclusive) before it counts as a breaching regression.
        Defaults to :data:`DEFAULT_TOLERANCE` (5%).
    critical_metrics : Iterable[str] or None
        The names of the metrics whose degradation can fail the gate. If
        ``None`` (the default), **every** metric present in both runs is
        treated as critical -- the safest posture for a security guard: nothing
        is allowed to silently get worse.
    higher_is_better : Iterable[str] or None
        Names of metrics for which a *larger* value is an improvement (e.g.
        accuracy). Everything not listed here is treated as lower-is-better,
        matching the :mod:`validation.metrics` convention.

    Notes
    -----
    Directionality of comparison is computed per metric so that
    ``regressions`` always holds *worsening* changes and ``improvements``
    always holds *bettering* changes, regardless of whether the underlying
    metric is lower- or higher-is-better.
    """

    def __init__(
        self,
        tolerance: float = DEFAULT_TOLERANCE,
        critical_metrics: Optional[Iterable[str]] = None,
        higher_is_better: Optional[Iterable[str]] = None,
    ) -> None:
        if tolerance < 0:
            raise ValueError(f"tolerance must be non-negative, got {tolerance!r}")
        self.tolerance = float(tolerance)
        # ``None`` means "treat all shared metrics as critical".
        self.critical_metrics: Optional[set] = (
            set(critical_metrics) if critical_metrics is not None else None
        )
        self.higher_is_better: set = set(higher_is_better or ())

    # -- public API --------------------------------------------------------

    def is_improvement(
        self,
        current_metrics: Mapping[str, float],
        baseline_metrics: Mapping[str, float],
    ) -> bool:
        """Return ``True`` iff the candidate passes the Freeze Rule.

        Implements the :class:`~validation.interfaces.Regression` contract.
        This is a thin, side-effect-free wrapper around :meth:`evaluate`; call
        :meth:`evaluate` directly when you need the itemised
        :class:`RegressionResult` (improvements, regressions, summary).
        """
        return self.evaluate(current_metrics, baseline_metrics).passed

    def evaluate(
        self,
        current_metrics: Mapping[str, float],
        baseline_metrics: Mapping[str, float],
    ) -> RegressionResult:
        """Compute per-metric deltas and decide whether the candidate passes.

        For every metric present in *both* ``baseline_metrics`` and
        ``current_metrics`` the gate computes a signed fractional *degradation*
        relative to the baseline. A positive degradation means the candidate is
        worse; a negative one means it is better. A *critical* metric whose
        degradation exceeds :attr:`tolerance` trips the gate.

        Parameters
        ----------
        current_metrics : Mapping[str, float]
            ``metric_name -> score`` for the candidate run.
        baseline_metrics : Mapping[str, float]
            ``metric_name -> score`` for the frozen baseline run.

        Returns
        -------
        RegressionResult
            The full verdict.
        """
        improvements: Dict[str, float] = {}
        regressions: Dict[str, float] = {}
        breaches: Dict[str, float] = {}

        shared = [m for m in baseline_metrics if m in current_metrics]

        for name in shared:
            baseline = float(baseline_metrics[name])
            current = float(current_metrics[name])
            degradation = self._degradation_fraction(name, baseline, current)

            if degradation > 0:
                regressions[name] = degradation
                if self._is_critical(name) and degradation > self.tolerance:
                    breaches[name] = degradation
            elif degradation < 0:
                improvements[name] = -degradation
            # degradation == 0 -> unchanged; recorded in neither bucket.

        # A critical metric that the candidate failed to report at all is a
        # failure: absence of evidence is not evidence of no regression.
        missing_critical = self._missing_critical(baseline_metrics, current_metrics)

        passed = not breaches and not missing_critical
        summary = self._build_summary(
            passed=passed,
            improvements=improvements,
            regressions=regressions,
            breaches=breaches,
            missing_critical=missing_critical,
        )

        return RegressionResult(
            passed=passed,
            improvements=improvements,
            regressions=regressions,
            summary=summary,
        )

    # -- internals ---------------------------------------------------------

    def _is_critical(self, name: str) -> bool:
        """Whether ``name`` can fail the gate. ``None`` set == all critical."""
        if self.critical_metrics is None:
            return True
        return name in self.critical_metrics

    def _missing_critical(
        self,
        baseline_metrics: Mapping[str, float],
        current_metrics: Mapping[str, float],
    ) -> list:
        """Critical metrics present in the baseline but absent from candidate."""
        missing = []
        for name in baseline_metrics:
            if name in current_metrics:
                continue
            if self._is_critical(name):
                missing.append(name)
        return sorted(missing)

    def _degradation_fraction(
        self,
        name: str,
        baseline: float,
        current: float,
    ) -> float:
        """Signed fractional degradation of ``current`` vs ``baseline``.

        Positive => worse, negative => better, normalised by the baseline
        magnitude. Direction is flipped for higher-is-better metrics so that
        "worse" always maps to a positive number.

        The zero-baseline case is handled explicitly to avoid division by
        zero: any move away from a zero baseline is treated as an unbounded
        (``inf``) change in the corresponding direction, while no change at all
        is ``0.0``.
        """
        raw = current - baseline
        if name in self.higher_is_better:
            # Higher is better: a drop (raw < 0) is a degradation.
            raw = -raw

        if baseline == 0:
            if raw == 0:
                return 0.0
            return math.inf if raw > 0 else -math.inf

        return raw / abs(baseline)

    def _build_summary(
        self,
        passed: bool,
        improvements: Mapping[str, float],
        regressions: Mapping[str, float],
        breaches: Mapping[str, float],
        missing_critical: Iterable[str],
    ) -> str:
        """Render the human-readable verdict for logs and assertions."""
        pct = self.tolerance * 100.0
        lines = []

        if passed:
            lines.append(f"REGRESSION GATE: PASS (tolerance {pct:.1f}%)")
        else:
            lines.append(f"REGRESSION GATE: FAIL (tolerance {pct:.1f}%)")

        breach_set = set(breaches)
        missing_list = list(missing_critical)

        if breach_set:
            lines.append("  Critical regressions exceeding tolerance:")
            for name in sorted(breach_set):
                lines.append(f"    - {name}: {self._fmt_pct(breaches[name])} worse")

        if missing_list:
            lines.append("  Critical metrics missing from candidate run:")
            for name in missing_list:
                lines.append(f"    - {name}: not reported (cannot prove no regression)")

        tolerated = {name: val for name, val in regressions.items() if name not in breach_set}
        if tolerated:
            lines.append("  Tolerated regressions (within margin):")
            for name in sorted(tolerated):
                lines.append(f"    - {name}: {self._fmt_pct(tolerated[name])} worse")

        if improvements:
            lines.append("  Improvements:")
            for name in sorted(improvements):
                lines.append(f"    - {name}: {self._fmt_pct(improvements[name])} better")

        if not breach_set and not missing_list and not tolerated and not improvements:
            lines.append("  No measured change across shared metrics.")

        return "\n".join(lines)

    @staticmethod
    def _fmt_pct(fraction: float) -> str:
        """Format a fractional change as a percentage string."""
        if math.isinf(fraction):
            return "inf%"
        return f"{fraction * 100.0:.2f}%"


# ---------------------------------------------------------------------------
# The Enforcer
# ---------------------------------------------------------------------------


def assert_no_regression(result: RegressionResult) -> None:
    """Hard-fail the Freeze Rule if ``result`` did not pass.

    This is the function a CI step, pre-commit hook, or PR check calls to turn
    a :class:`RegressionResult` into a build-breaking error. If
    ``result.passed`` is ``False`` it raises :class:`AssertionError` carrying
    the result's ``summary`` so the failure is self-explanatory in the logs.

    Parameters
    ----------
    result : RegressionResult
        The verdict produced by :meth:`RegressionGate.evaluate`.

    Raises
    ------
    AssertionError
        If ``result.passed`` is ``False``.
    """
    if not result.passed:
        raise AssertionError(result.summary)


__all__ = [
    "DEFAULT_TOLERANCE",
    "RegressionResult",
    "RegressionGate",
    "assert_no_regression",
]
