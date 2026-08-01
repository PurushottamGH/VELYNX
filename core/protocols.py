"""The eight replaceable component contracts.

Responsibility: state the minimum surface each component must expose so that
the experiment loop (`experiments/engine/engine.py`) can be written once and
never edited again when a component is added or swapped.

The loop calls these methods in exactly this order, every step:

    1. prediction = model.predict(observation.context)
    2. loss       = model.score(prediction, observation.target)   <- prequential
    3. model.learn(observation.context, observation.target)
    4. memory.append(observation)
    5. k          = gate.replay_count(loss, t)                    <- WHEN / HOW MANY
    6. batch      = replay.select(memory, k, observation)         <- WHAT
    7. model.learn(...) for each item in batch

Steps 5 and 6 are separate contracts on purpose. Replay *timing* and replay
*content* were confounded in v0, and the M0 review requires them to be varied
independently (equal-budget random timing; update-count-matched non-historical
content). One protocol per confound is the abstraction that removes that
future complexity.

These are `typing.Protocol`s: implementations need not inherit from anything,
which keeps the frozen `p1v0` package unmodified and still conformant through
thin adapters in `science/mechanisms/`.
"""

from __future__ import annotations

from typing import (
    Any,
    Dict,
    Iterator,
    Mapping,
    Protocol,
    Sequence,
    Tuple,
    runtime_checkable,
)

from core.types import Observation, ProbeRecord, StepRecord

#: (context, target, weight) triple consumed by ``Model.learn``.
ReplayItem = Tuple[Any, Any, float]


@runtime_checkable
class Environment(Protocol):
    """Source of observations. Owns the data-generating process only.

    Must be deterministic given its seeds and re-iterable: iterating twice
    yields identical observation sequences, which the determinism tests assert.
    """

    n_tasks: int

    @property
    def total_steps(self) -> int:
        """Number of observations a full iteration yields."""
        ...

    def checkpoints(self) -> Sequence[Tuple[int, int]]:
        """`[(task_id, last_step_index)]` — where the engine takes probes."""
        ...

    def __iter__(self) -> Iterator[Observation]: ...


@runtime_checkable
class Model(Protocol):
    """Predictor. Owns the hypothesis about the data and its own loss form.

    `score` lives here, not in the metrics layer, because the loss must match
    the predictive form the model emits. Metrics aggregate losses; they do not
    define them.
    """

    def predict(self, context: Any) -> Any:
        """Return a prediction for `context` without observing the target."""
        ...

    def score(self, prediction: Any, target: Any) -> float:
        """Proper scoring loss of `prediction` against `target`. Lower better."""
        ...

    def learn(self, context: Any, target: Any, weight: float = 1.0) -> None:
        """Absorb one observation. `weight` scales the update (replay uses it)."""
        ...

    def state_dict(self) -> Dict[str, Any]: ...

    def load_state_dict(self, state: Mapping[str, Any]) -> None: ...


@runtime_checkable
class Memory(Protocol):
    """Bounded store of past observations. Does not learn, score, or decide."""

    def append(self, obs: Observation) -> None: ...

    def sample(self, k: int) -> Sequence[Observation]:
        """Draw `k` items. Returns fewer (or none) if unavailable."""
        ...

    def snapshot(self) -> Sequence[Observation]:
        """Read-only view of stored items, for replay policies that filter.

        Named `snapshot` rather than `items` because concrete buffers commonly
        expose `items` as a mutable list attribute, and a method of the same name
        would shadow it.
        """
        ...

    def __len__(self) -> int: ...


@runtime_checkable
class Gate(Protocol):
    """Replay *timing and budget*: how many replay updates to spend now.

    Receives only the current loss and step index. A gate that needed the model
    or the memory would be making a content decision, which belongs to `Replay`.
    """

    n_fired: int
    n_replays: int

    def replay_count(self, loss: float, t: int) -> int: ...


@runtime_checkable
class Replay(Protocol):
    """Replay *content*: which items to learn from, given a budget of `k`.

    Returning fewer than `k` items is legal but must be reported, because a
    budget-matched control that silently under-spends is not matched.
    """

    def select(self, memory: Memory, k: int, latest: Observation) -> Sequence[ReplayItem]: ...


@runtime_checkable
class Metric(Protocol):
    """Streaming accumulator over engine events.

    Metrics are write-only observers: they may not touch the model, the memory
    or the environment, so adding one can never change a run's trajectory.
    Determinism tests rely on that.

    `requires_oracle` is validated once before a run starts, so a metric that
    needs ground truth fails loudly at configuration time rather than emitting
    a silently wrong number.
    """

    name: str
    requires_oracle: bool

    def on_step(self, rec: StepRecord) -> None: ...

    def on_probe(self, rec: ProbeRecord) -> None: ...

    def result(self) -> Dict[str, Any]:
        """Final values. Called once, after the last event."""
        ...


@runtime_checkable
class Benchmark(Protocol):
    """Evaluation harness: environment + held-out probes + ground truth.

    All benchmark-specific knowledge lives behind this contract, which is why
    the engine contains no benchmark branching. Swapping a benchmark swaps the
    environment, the probe data and the oracle together — they are one
    scientific unit and must stay consistent.
    """

    name: str

    def build_environment(self) -> Environment: ...

    def evaluate(self, model: Model, block: int, t: int, trained_task: int) -> ProbeRecord:
        """Frozen-model evaluation. Must not call `model.learn`."""
        ...

    def describe(self) -> Dict[str, Any]:
        """Benchmark identity and parameters, recorded in the run manifest."""
        ...


@runtime_checkable
class Logger(Protocol):
    """Structured sink for engine events. The only component allowed to be
    side-effecting without affecting results."""

    def event(self, kind: str, payload: Mapping[str, Any]) -> None: ...

    def close(self) -> None: ...
