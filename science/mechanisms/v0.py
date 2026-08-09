"""Protocol adapters over the frozen M0 rig.

Responsibility: expose `p1v0`'s components through the `core.protocols`
contracts without changing a line of `p1v0`.

`p1v0` is the version-pinned artifact the M0 scientific review assessed. Editing
it would destroy the evidence identity the review requires, so every adaptation
here is additive: a subclass that supplies a missing method, or a wrapper that
translates a record type. All numerical behaviour, including every random draw,
is still executed by the frozen code.

That is what makes `tests/m1/test_frozen_v0_equivalence.py` meaningful: the
platform reproduces M0 exactly, so any later difference is attributable to a
declared configuration change rather than to a rewrite.
"""

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Sequence, Tuple

from core.protocols import ReplayItem
from core.seeds import SeedSet
from core.types import Observation
from p1v0.gate import AlwaysGate, NeverGate, SurpriseGate
from p1v0.memory import NullBuffer, ReplayBuffer
from p1v0.model import CountModel, scoring_loss
from p1v0.stream import TaskStream
from science.registries import ENVIRONMENTS, GATES, MEMORIES, MODELS

# --------------------------------------------------------------------------- #
# Model
# --------------------------------------------------------------------------- #


class CountModelPlugin(CountModel):
    """`p1v0.CountModel` plus the `score` method the protocol requires.

    The loss belongs to the model because it must match the predictive form the
    model emits; see `core.protocols.Model`.
    """

    def score(self, prediction: Sequence[float], target: int) -> float:
        return scoring_loss(list(prediction), target)


@MODELS.register("count_model")
def _count_model(alpha: float = 0.5, decay: float = 1.0, *, alphabet: int) -> CountModelPlugin:
    """Order-1 count table with additive smoothing and row-wise recency decay.

    `alphabet` is injected from the environment's hints, never set in config, so
    a model and its environment cannot silently disagree about symbol count.
    """
    return CountModelPlugin(alphabet=alphabet, alpha=alpha, decay=decay)


# --------------------------------------------------------------------------- #
# Memory
# --------------------------------------------------------------------------- #


class ReservoirMemory:
    """Uniform reservoir over the entire stream, holding `Observation` records.

    Composition, not subclassing: `p1v0.ReplayBuffer` exposes `items` as a list
    attribute, which would collide with the protocol's `snapshot()`. Every random
    draw is still executed by the frozen buffer, so behaviour is identical to M0
    given the same seed.

    Full `Observation`s are stored rather than bare `(context, target)` tuples
    because the task-stratified replay controls the M0 review requires
    (`historical_only`, `task_balanced`) need task labels. The frozen buffer never
    inspects its items, so this changes no draw.
    """

    def __init__(self, capacity: int = 1000, seed: int = 0) -> None:
        self._buffer = ReplayBuffer(capacity=capacity, seed=seed)

    def append(self, obs: Observation) -> None:
        self._buffer.append(obs)  # type: ignore[arg-type]

    def sample(self, k: int) -> List[Observation]:
        return list(self._buffer.sample(k))  # type: ignore[arg-type]

    def snapshot(self) -> Tuple[Observation, ...]:
        return tuple(self._buffer.items)  # type: ignore[arg-type]

    @property
    def n_seen(self) -> int:
        return self._buffer.n_seen

    @property
    def capacity(self) -> int:
        return self._buffer.capacity

    def __len__(self) -> int:
        return len(self._buffer)


class NullMemory:
    """Control: stores nothing, returns nothing. Isolates storage from replay."""

    def __init__(self, seed: int = 0) -> None:
        self._buffer = NullBuffer(seed=seed)

    def append(self, obs: Observation) -> None:
        self._buffer.append(obs)  # type: ignore[arg-type]

    def sample(self, k: int) -> List[Observation]:
        return []

    def snapshot(self) -> Tuple[Observation, ...]:
        return ()

    @property
    def n_seen(self) -> int:
        return self._buffer.n_seen

    def __len__(self) -> int:
        return 0


@MEMORIES.register("reservoir")
def _reservoir(capacity: int = 1000, *, seed: int) -> ReservoirMemory:
    """Uniform reservoir over the whole stream seen so far.

    Reservoir rather than FIFO because a FIFO buffer is biased toward the current
    task, which would confound every replay ablation.
    """
    return ReservoirMemory(capacity=capacity, seed=seed)


@MEMORIES.register("null")
def _null_memory(*, seed: int) -> NullMemory:
    """Control: no storage at all."""
    return NullMemory(seed=seed)


# --------------------------------------------------------------------------- #
# Gates (timing / budget)
# --------------------------------------------------------------------------- #


class NeverGatePlugin(NeverGate):
    def replay_count(self, loss: float, t: int = 0) -> int:  # type: ignore[override]
        return super().replay_count(loss)


class AlwaysGatePlugin(AlwaysGate):
    def replay_count(self, loss: float, t: int = 0) -> int:  # type: ignore[override]
        return super().replay_count(loss)


class SurpriseGatePlugin(SurpriseGate):
    def replay_count(self, loss: float, t: int = 0) -> int:  # type: ignore[override]
        return super().replay_count(loss)


@GATES.register("never")
def _never() -> NeverGatePlugin:
    """Control: never replay."""
    return NeverGatePlugin()


@GATES.register("always")
def _always(k: int = 4) -> AlwaysGatePlugin:
    """Control: constant budget every step, independent of surprise."""
    return AlwaysGatePlugin(k=k)


@GATES.register("surprise")
def _surprise(threshold: float = 1.5, k: int = 4) -> SurpriseGatePlugin:
    """Hypothesis under test: replay when step loss exceeds `threshold` nats."""
    return SurpriseGatePlugin(threshold=threshold, k=k)


# --------------------------------------------------------------------------- #
# Environment
# --------------------------------------------------------------------------- #


class MarkovBlocksV0:
    """The frozen `p1v0.TaskStream`, wrapped to emit `Observation`s.

    Task generation and stream trajectory share one seed here, exactly as in M0.
    Use `markov_blocks_split` when variance sources must be separated (V0-4).
    """

    def __init__(
        self,
        n_tasks: int = 4,
        alphabet: int = 8,
        steps_per_task: int = 2000,
        cycles: int = 1,
        fanout: int = 2,
        *,
        seed: int,
    ) -> None:
        self.stream = TaskStream(
            n_tasks=n_tasks,
            alphabet=alphabet,
            steps_per_task=steps_per_task,
            seed=seed,
            cycles=cycles,
            fanout=fanout,
        )
        self.n_tasks = n_tasks
        self.alphabet = alphabet
        self.steps_per_task = steps_per_task
        self.cycles = cycles

    @property
    def hints(self) -> Dict[str, Any]:
        """Facts other components must not restate in config."""
        return {"alphabet": self.alphabet, "steps_per_task": self.steps_per_task}

    @property
    def total_steps(self) -> int:
        return self.stream.total_steps

    def checkpoints(self) -> Sequence[Tuple[int, int]]:
        return self.stream.blocks()

    def tasks(self) -> Sequence[Any]:
        """True generators, for oracle construction. Read-only."""
        return self.stream.tasks

    def describe(self) -> Dict[str, Any]:
        return {
            "kind": "markov_blocks_v0",
            "n_tasks": self.n_tasks,
            "alphabet": self.alphabet,
            "steps_per_task": self.steps_per_task,
            "cycles": self.cycles,
            "task_order": list(range(self.n_tasks)) * self.cycles,
            "seed_coupling": "task generation and trajectory share one seed (M0 behaviour)",
        }

    def __iter__(self) -> Iterator[Observation]:
        for ev in self.stream:
            yield Observation(t=ev.t, task=ev.task, context=ev.prev, target=ev.sym)


@ENVIRONMENTS.register("markov_blocks_v0")
def _markov_blocks_v0(
    n_tasks: int = 4,
    alphabet: int = 8,
    steps_per_task: int = 2000,
    cycles: int = 1,
    fanout: int = 2,
    *,
    seeds: SeedSet,
) -> MarkovBlocksV0:
    """M0 environment, bit-for-bit. Single composite seed by design.

    Only the `environment` substream is consumed: task generation and trajectory
    are coupled inside the frozen stream and cannot be separated without editing
    it. `markov_blocks_split` exists for that purpose.
    """
    return MarkovBlocksV0(
        n_tasks=n_tasks,
        alphabet=alphabet,
        steps_per_task=steps_per_task,
        cycles=cycles,
        fanout=fanout,
        seed=seeds["environment"],
    )


def replay_items(observations: Sequence[Observation], weight: float) -> List[ReplayItem]:
    """Shared helper: turn stored observations into weighted learn arguments."""
    return [(obs.context, obs.target, weight) for obs in observations]
