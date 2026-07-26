"""
VELYNX ``validation`` subsystem.

Interface-First architecture. Every concrete dataset, metric, regression gate,
and runner in the validation harness MUST inherit from the abstract base
classes defined in :mod:`validation.interfaces`. This enforces a single,
consistent contract across all future cognitive-research modules.

See :mod:`validation.interfaces` for the binding contracts:

    - :class:`~validation.interfaces.Dataset`
    - :class:`~validation.interfaces.Metric`
    - :class:`~validation.interfaces.Regression`

See :mod:`validation.runner` for the experiment execution harness:

    - :class:`~validation.runner.BenchmarkRunner`
"""

from validation.artifact import ResultSerializer
from validation.interfaces import Dataset, Metric, Regression, Vector
from validation.regression import (
    DEFAULT_TOLERANCE,
    RegressionGate,
    RegressionResult,
    assert_no_regression,
)


# `validation.runner` drives concrete `backend.cognition` components, which are not part
# of the shipped `velynx` distribution (`pyproject.toml` excludes `backend*`). Importing
# it eagerly here made the entire `validation` package — and therefore
# `framework.core.cognitive_health`, which needs only `validation.metrics` and
# `validation.report` — unimportable from an installed wheel. Resolving it on first
# attribute access keeps the harness working wherever `backend/` is on the path, without
# poisoning the package for consumers that never touch the runner.
# The underlying boundary breach is CRITICAL_PATH.md Priority 2 (W-056).
def __getattr__(name: str):
    if name == "BenchmarkRunner":
        from validation.runner import BenchmarkRunner

        return BenchmarkRunner
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "Dataset",
    "Metric",
    "Regression",
    "Vector",
    "BenchmarkRunner",
    "RegressionGate",
    "RegressionResult",
    "assert_no_regression",
    "DEFAULT_TOLERANCE",
    "ResultSerializer",
]
