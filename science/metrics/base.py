"""Shared metric scaffolding.

Responsibility: give metrics a no-op default for every event hook, so a metric
that cares only about probes does not have to implement `on_step`, and adding a
new hook later does not break existing metrics.

A metric is a write-only observer. It receives records and returns numbers; it
cannot reach the model, the memory or the environment. That is what makes
"add a metric" a zero-risk change: no metric can alter a run's trajectory, so
determinism tests remain valid however many metrics are configured.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

from core.types import ProbeRecord, StepRecord


def mean(values: Sequence[float]) -> float:
    """Mean that drops NaN, matching `p1v0.metrics.mean` semantics.

    NaN appears legitimately (a task never probed, an empty probe set), and a
    single NaN must not silently poison an aggregate.
    """
    vals = [v for v in values if v == v]
    return sum(vals) / len(vals) if vals else float("nan")


class BaseMetric:
    """Default no-op implementation of `core.protocols.Metric`."""

    #: Config name, also the key its results appear under in metrics.json.
    name: str = "base"
    #: When True the engine refuses to start unless the benchmark supplies an
    #: oracle, rather than reporting a silently wrong number.
    requires_oracle: bool = False

    def on_step(self, rec: StepRecord) -> None:
        return None

    def on_probe(self, rec: ProbeRecord) -> None:
        return None

    def result(self) -> Dict[str, Any]:
        raise NotImplementedError(f"metric {self.name!r} must implement result()")
