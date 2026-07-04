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
from validation.runner import BenchmarkRunner

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
