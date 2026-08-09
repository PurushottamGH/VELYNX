"""Environments with separable randomness.

Responsibility: generate observation streams whose variance sources can be varied
one at a time.

`markov_blocks_split` exists because experiment V0-4 requires task generation,
stream trajectory and task presentation order to be varied independently, and the
frozen `markov_blocks_v0` couples all three to one seed. The chain construction
itself reuses `p1v0.stream.MarkovTask`, so the task family is identical to M0 and
the only change is which random source drives which decision.
"""

from __future__ import annotations

import random
from typing import Any, Dict, Iterator, List, Sequence, Tuple

from core.seeds import SeedSet
from core.types import Observation
from p1v0.stream import MarkovTask
from science.registries import ENVIRONMENTS

ORDER_MODES: Tuple[str, ...] = ("sequential", "shuffled", "reversed")


class MarkovBlocksSplit:
    """Piecewise-stationary Markov blocks with independent random sources.

    generation  -> the transition matrices (which tasks exist)
    trajectory  -> the symbol draws given those matrices
    order       -> the presentation order of tasks within each cycle

    Presentation order is drawn per cycle so that a two-cycle run does not repeat
    the same order twice, which would reintroduce the serial-position confound the
    order stream is meant to break (review control 10).
    """

    def __init__(
        self,
        n_tasks: int = 4,
        alphabet: int = 8,
        steps_per_task: int = 2000,
        cycles: int = 1,
        fanout: int = 2,
        order: str = "sequential",
        *,
        seeds: SeedSet,
    ) -> None:
        if n_tasks < 1:
            raise ValueError("n_tasks must be >= 1")
        if steps_per_task < 1:
            raise ValueError("steps_per_task must be >= 1")
        if cycles < 1:
            raise ValueError("cycles must be >= 1")
        if order not in ORDER_MODES:
            raise ValueError(f"unknown order {order!r}; expected one of {ORDER_MODES}")

        self.n_tasks = n_tasks
        self.alphabet = alphabet
        self.steps_per_task = steps_per_task
        self.cycles = cycles
        self.order = order
        self._generation_seed = seeds["environment"]
        self._trajectory_seed = seeds["trajectory"]
        self._order_seed = seeds["order"]

        # Same generator as M0, one independent generation seed per task.
        self._tasks: List[MarkovTask] = [
            MarkovTask(i, alphabet, self._generation_seed * 10_000 + 7 * i + 1, fanout)
            for i in range(n_tasks)
        ]
        self._schedule: List[int] = self._build_schedule()

    def _build_schedule(self) -> List[int]:
        rng = random.Random(self._order_seed + 613)
        schedule: List[int] = []
        for _ in range(self.cycles):
            ids = list(range(self.n_tasks))
            if self.order == "shuffled":
                rng.shuffle(ids)
            elif self.order == "reversed":
                ids.reverse()
            schedule.extend(ids)
        return schedule

    @property
    def hints(self) -> Dict[str, Any]:
        return {"alphabet": self.alphabet, "steps_per_task": self.steps_per_task}

    @property
    def total_steps(self) -> int:
        return len(self._schedule) * self.steps_per_task

    def checkpoints(self) -> Sequence[Tuple[int, int]]:
        return [
            (task_id, (block + 1) * self.steps_per_task - 1)
            for block, task_id in enumerate(self._schedule)
        ]

    def tasks(self) -> Sequence[MarkovTask]:
        """True generators, in task-id order. Used only to build the oracle."""
        return self._tasks

    def describe(self) -> Dict[str, Any]:
        return {
            "kind": "markov_blocks_split",
            "n_tasks": self.n_tasks,
            "alphabet": self.alphabet,
            "steps_per_task": self.steps_per_task,
            "cycles": self.cycles,
            "order": self.order,
            "task_order": list(self._schedule),
            "seed_coupling": "generation, trajectory and order are independent",
        }

    def __iter__(self) -> Iterator[Observation]:
        rng = random.Random(self._trajectory_seed + 991)
        prev = 0
        t = 0
        for task_id in self._schedule:
            task = self._tasks[task_id]
            for _ in range(self.steps_per_task):
                sym = task.next_symbol(prev, rng)
                yield Observation(t=t, task=task_id, context=prev, target=sym)
                prev = sym
                t += 1


@ENVIRONMENTS.register("markov_blocks_split")
def _markov_blocks_split(
    n_tasks: int = 4,
    alphabet: int = 8,
    steps_per_task: int = 2000,
    cycles: int = 1,
    fanout: int = 2,
    order: str = "sequential",
    *,
    seeds: SeedSet,
) -> MarkovBlocksSplit:
    """V0-4 environment: independent generation, trajectory and order seeds."""
    return MarkovBlocksSplit(
        n_tasks=n_tasks,
        alphabet=alphabet,
        steps_per_task=steps_per_task,
        cycles=cycles,
        fanout=fanout,
        order=order,
        seeds=seeds,
    )
