"""Execution loop.

Responsibility: perform one step -- predict, score, learn, store, replay --
and yield a record of it. Performs no aggregation and no IO, so the same loop
serves interactive debugging and batch runs.

Step order is fixed and must not change between variants, or losses become
incomparable:
    1. predict from context (model has NOT seen this observation)
    2. score the prediction          -> the reported online loss
    3. learn from the observation
    4. store the observation
    5. ask the gate, replay that many samples from memory
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from p1v0.gate import Gate
from p1v0.memory import ReplayBuffer
from p1v0.model import CountModel, scoring_loss
from p1v0.stream import Event, TaskStream


@dataclass(frozen=True)
class StepRecord:
    t: int
    task: int
    loss: float
    replays: int
    buffer_size: int


def run(
    stream: TaskStream,
    model: CountModel,
    memory: ReplayBuffer,
    gate: Gate,
    replay_weight: float = 1.0,
) -> Iterator[StepRecord]:
    """Drive the stream through the mechanism set, yielding one record per step."""
    for ev in stream:
        loss = step(ev, model, memory, gate, replay_weight)
        yield StepRecord(
            t=ev.t,
            task=ev.task,
            loss=loss,
            replays=gate.n_replays,
            buffer_size=len(memory),
        )


def step(
    ev: Event,
    model: CountModel,
    memory: ReplayBuffer,
    gate: Gate,
    replay_weight: float = 1.0,
) -> float:
    """One step. Returns the online scoring loss for this observation."""
    probs = model.predict(ev.prev)
    loss = scoring_loss(probs, ev.sym)

    model.learn(ev.prev, ev.sym)
    memory.append((ev.prev, ev.sym))

    for prev, sym in memory.sample(gate.replay_count(loss)):
        model.learn(prev, sym, weight=replay_weight)

    return loss
