"""A fully deterministic benchmark with no randomness at all.

Responsibility: let the engine be verified without depending on any scientific
component.

Every number here is fixed by construction: the stream cycles through a known
pattern, and the "oracle" is a declared constant. If an engine test fails against
this benchmark, the fault is in the engine — not in a model, a sampler or a task
generator. That separation is why the engine tests are trustworthy, and why this
module must stay trivial.

It is not a scientific instrument and no result obtained from it may be reported
as evidence about a mechanism.
"""

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Sequence, Tuple

from core.protocols import Environment, Model
from core.seeds import SeedSet
from core.types import Observation, ProbeRecord
from science.registries import BENCHMARKS, ENVIRONMENTS


class CyclicEnvironment:
    """Emits `context = t % alphabet`, `target = (context + 1 + task) % alphabet`.

    Deterministic, re-iterable, and learnable: each task is a different shift, so a
    model that adapts to task 1 is measurably wrong on task 0.
    """

    def __init__(
        self,
        n_tasks: int = 2,
        alphabet: int = 4,
        steps_per_task: int = 20,
        cycles: int = 1,
    ) -> None:
        self.n_tasks = n_tasks
        self.alphabet = alphabet
        self.steps_per_task = steps_per_task
        self.cycles = cycles

    @property
    def hints(self) -> Dict[str, Any]:
        return {"alphabet": self.alphabet, "steps_per_task": self.steps_per_task}

    @property
    def total_steps(self) -> int:
        return self.n_tasks * self.steps_per_task * self.cycles

    def checkpoints(self) -> Sequence[Tuple[int, int]]:
        out: List[Tuple[int, int]] = []
        block = 0
        for _ in range(self.cycles):
            for task in range(self.n_tasks):
                block += 1
                out.append((task, block * self.steps_per_task - 1))
        return out

    def describe(self) -> Dict[str, Any]:
        return {
            "kind": "cyclic_deterministic",
            "n_tasks": self.n_tasks,
            "alphabet": self.alphabet,
            "steps_per_task": self.steps_per_task,
            "cycles": self.cycles,
        }

    def __iter__(self) -> Iterator[Observation]:
        t = 0
        for _ in range(self.cycles):
            for task in range(self.n_tasks):
                for _ in range(self.steps_per_task):
                    context = t % self.alphabet
                    yield Observation(
                        t=t,
                        task=task,
                        context=context,
                        target=(context + 1 + task) % self.alphabet,
                    )
                    t += 1


class DeterministicBenchmark:
    """Cyclic environment, exhaustive probes, constant zero oracle."""

    name = "deterministic"

    def __init__(self, environment: Any, *, seeds: SeedSet) -> None:
        self._env = ENVIRONMENTS.create(environment, seeds=seeds)
        self._alphabet = self._env.alphabet
        self._n_tasks = self._env.n_tasks
        # Exhaustive: every context appears exactly once, so probe estimates carry
        # no Monte-Carlo error whatsoever.
        self._pairs = [
            [(c, (c + 1 + task) % self._alphabet) for c in range(self._alphabet)]
            for task in range(self._n_tasks)
        ]

    @property
    def has_oracle(self) -> bool:
        return True

    @property
    def predictions_per_probe(self) -> int:
        return sum(len(p) for p in self._pairs)

    def build_environment(self) -> Environment:
        return self._env

    def evaluate(self, model: Model, block: int, t: int, trained_task: int) -> ProbeRecord:
        losses: List[float] = []
        for pairs in self._pairs:
            total = sum(model.score(model.predict(c), y) for c, y in pairs)
            losses.append(total / len(pairs))
        return ProbeRecord(
            t=t,
            block=block,
            trained_task=trained_task,
            losses=tuple(losses),
            oracle=tuple(0.0 for _ in losses),
        )

    def describe(self) -> Dict[str, Any]:
        return {"name": self.name, "environment": self._env.describe(), "oracle": "constant_zero"}


@ENVIRONMENTS.register("cyclic")
def _cyclic(
    n_tasks: int = 2,
    alphabet: int = 4,
    steps_per_task: int = 20,
    cycles: int = 1,
) -> CyclicEnvironment:
    """Deterministic shift-cycle environment. Consumes no seeds."""
    return CyclicEnvironment(
        n_tasks=n_tasks, alphabet=alphabet, steps_per_task=steps_per_task, cycles=cycles
    )


@BENCHMARKS.register("deterministic")
def _deterministic(environment: Any, *, seeds: SeedSet) -> DeterministicBenchmark:
    """Engine test double. Not a scientific instrument."""
    return DeterministicBenchmark(environment=environment, seeds=seeds)
