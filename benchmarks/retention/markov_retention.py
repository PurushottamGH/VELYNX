"""Retention under non-stationarity, for Markov-block environments.

Responsibility: hold together the three things that must agree for a retention
measurement to be valid — the environment, the held-out probe data, and the
oracle — and expose them through `core.protocols.Benchmark`.

They are one unit on purpose. Probe pairs drawn from a different generator than
the training stream, or an oracle computed from different transition matrices,
would produce numbers that look fine and mean nothing. Binding them behind one
contract is what allows the engine to contain no benchmark-specific branching.

Probe construction reproduces `p1v0.probe.ProbeSuite` exactly (same per-task seed
formula), so with `seeds.mode = legacy_v0` the probe data is identical to M0.
Probe Monte-Carlo error is estimated by re-running with the `probe` seed stream
overridden, which the split-seed design supports; there is deliberately no
in-run replication parameter.
"""

from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

from core.protocols import Environment, Model
from core.seeds import SeedSet
from core.types import ProbeRecord
from science.oracle import MarkovOracle
from science.registries import BENCHMARKS, ENVIRONMENTS

Pair = Tuple[int, int]

#: Offsets reproducing `p1v0.probe.ProbeSuite`'s per-task probe seeding, so probe
#: data is bit-identical to M0 under `seeds.mode = legacy_v0`.
_PROBE_SCALE = 10_000
_PROBE_OFFSET = 5_000


class MarkovRetention:
    """Environment + per-task held-out probes + exact oracle."""

    name = "markov_retention"

    def __init__(
        self,
        environment: Any,
        probe_pairs: int = 500,
        *,
        seeds: SeedSet,
    ) -> None:
        if probe_pairs < 1:
            raise ValueError("probe_pairs must be >= 1")
        self.probe_pairs = probe_pairs
        self._seeds = seeds
        self._environment_spec = environment
        self._env = ENVIRONMENTS.create(environment, seeds=seeds)
        if not hasattr(self._env, "tasks"):
            raise TypeError(
                f"environment {getattr(self._env, 'name', type(self._env).__name__)!r} does not "
                "expose tasks(); markov_retention needs the true generators to build an oracle"
            )
        tasks = list(self._env.tasks())
        probe_seed = seeds["probe"]
        self._pairs: List[List[Pair]] = [
            list(task.sample_pairs(probe_pairs, seed=probe_seed * _PROBE_SCALE + _PROBE_OFFSET + i))
            for i, task in enumerate(tasks)
        ]
        self._oracle = MarkovOracle([task.rows for task in tasks])
        self._oracle_losses: Tuple[float, ...] = tuple(self._oracle.losses(self._pairs))

    @property
    def has_oracle(self) -> bool:
        return True

    @property
    def predictions_per_probe(self) -> int:
        """Model calls one full probe costs. Recorded in the compute budget."""
        return sum(len(pairs) for pairs in self._pairs)

    def build_environment(self) -> Environment:
        return self._env

    def evaluate(self, model: Model, block: int, t: int, trained_task: int) -> ProbeRecord:
        """Frozen-model evaluation. Calls `predict`/`score` only, never `learn`."""
        losses: List[float] = []
        for pairs in self._pairs:
            if not pairs:
                losses.append(float("nan"))
                continue
            total = 0.0
            for context, target in pairs:
                total += model.score(model.predict(context), target)
            losses.append(total / len(pairs))
        return ProbeRecord(
            t=t,
            block=block,
            trained_task=trained_task,
            losses=tuple(losses),
            oracle=self._oracle_losses,
        )

    def describe(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "probe_pairs": self.probe_pairs,
            "probe_seed": self._seeds["probe"],
            "oracle": self._oracle.describe(),
            "oracle_losses": list(self._oracle_losses),
            "environment": self._env.describe(),
        }


@BENCHMARKS.register("markov_retention")
def _markov_retention(
    environment: Any,
    probe_pairs: int = 500,
    *,
    seeds: SeedSet,
) -> MarkovRetention:
    """Retention benchmark for any Markov-block environment exposing `tasks()`."""
    return MarkovRetention(environment=environment, probe_pairs=probe_pairs, seeds=seeds)


def oracle_losses(benchmark: MarkovRetention) -> Sequence[float]:
    """Convenience accessor used by reporting scripts."""
    return benchmark._oracle_losses  # noqa: SLF001  (deliberate, read-only)
