"""Controls that isolate the mechanisms under test.

Responsibility: provide the comparison conditions the M0 scientific review
listed as missing, so that a replay or gating claim can be attributed to
something narrower than "the whole intervention bundle".

Each component below maps to a specific control in the review:

    matched_random gate     control 1  — equal replay budget, timing chosen
                                         independently of loss. Without it,
                                         "surprise gating works" is unfalsifiable.
    boundary gate           control 15 — matched frequency near known task
                                         switches; diagnoses surprise acting only
                                         as an implicit change detector.
    current_sample replay   control 3  — same number of learning updates, drawn
                                         from the current observation. Separates
                                         historical replay from generic extra
                                         optimisation and extra decay.
    historical_only replay  control 6  — excludes current-task items, so
                                         protection must come from older evidence.
    task_balanced replay    control 7  — equal draws per prior task; estimates the
                                         best retention attainable at a budget and
                                         exposes reservoir-composition limits.
    none replay             control 5  — storage with no replay, combined with a
                                         non-null memory.

These are controls, not new mechanism proposals: the review permits (and
requires) them while forbidding further mechanism proliferation.
"""

from __future__ import annotations

import random
from collections import defaultdict
from typing import Any, Dict, List, Sequence

from core.protocols import Memory, ReplayItem
from core.types import Observation
from science.registries import GATES, REPLAYS

# --------------------------------------------------------------------------- #
# Gates — replay timing and budget
# --------------------------------------------------------------------------- #


class MatchedRandomGate:
    """Fires at times independent of the loss, with a controllable budget.

    Two modes, and the difference matters scientifically:

    exact   `n_fires` steps are drawn without replacement from `horizon` at
            construction time. The realised replay count then equals that of the
            reference run exactly, which is what "equal budget" requires. Obtain
            `n_fires` from the reference run's `gate.fired_steps` and pin it in
            the config; the two-pass wiring is deliberate and visible.

    rate    each step fires with probability `rate`. Budget matches only in
            expectation, so it is adequate for pilots and not for a confirmatory
            equal-budget contrast.
    """

    def __init__(
        self,
        k: int = 4,
        n_fires: int | None = None,
        horizon: int | None = None,
        rate: float | None = None,
        *,
        seed: int,
    ) -> None:
        if (n_fires is None) == (rate is None):
            raise ValueError(
                "matched_random needs exactly one of 'n_fires' (with 'horizon') or 'rate'"
            )
        if n_fires is not None and horizon is None:
            raise ValueError("matched_random 'n_fires' requires 'horizon' (total steps)")
        if rate is not None and not 0.0 <= rate <= 1.0:
            raise ValueError("matched_random 'rate' must be in [0, 1]")
        if n_fires is not None and horizon is not None and n_fires > horizon:
            raise ValueError("matched_random 'n_fires' cannot exceed 'horizon'")

        self.k = k
        self.rate = rate
        self.n_fires = n_fires
        self.horizon = horizon
        self.n_fired = 0
        self.n_replays = 0
        self._rng = random.Random(seed + 7919)
        self._schedule: frozenset[int] = frozenset()
        if n_fires is not None and horizon is not None:
            self._schedule = frozenset(self._rng.sample(range(horizon), n_fires))

    def replay_count(self, loss: float, t: int) -> int:
        if self.rate is not None:
            fire = self._rng.random() < self.rate
        else:
            fire = t in self._schedule
        if not fire:
            return 0
        self.n_fired += 1
        self.n_replays += self.k
        return self.k


class BoundaryGate:
    """Fires in a fixed window after each task switch. Diagnostic control.

    Task-switch positions come from config (`period`), not from the environment:
    a gate that could read the environment would be able to cheat in ways a
    deployed mechanism cannot, and would stop being a fair comparator.
    """

    def __init__(self, period: int, window: int = 50, k: int = 4) -> None:
        if period < 1:
            raise ValueError("boundary gate 'period' must be >= 1")
        if not 0 <= window <= period:
            raise ValueError("boundary gate 'window' must be in [0, period]")
        self.period = period
        self.window = window
        self.k = k
        self.n_fired = 0
        self.n_replays = 0

    def replay_count(self, loss: float, t: int) -> int:
        if (t % self.period) >= self.window:
            return 0
        self.n_fired += 1
        self.n_replays += self.k
        return self.k


@GATES.register("matched_random")
def _matched_random(
    k: int = 4,
    n_fires: int | None = None,
    rate: float | None = None,
    *,
    seed: int,
    total_steps: int,
) -> MatchedRandomGate:
    """Control 1: equal-budget replay at loss-independent times.

    `horizon` is injected from the environment, never configured: a schedule drawn
    over the wrong horizon would silently under- or over-spend the budget it is
    supposed to match.
    """
    return MatchedRandomGate(k=k, n_fires=n_fires, horizon=total_steps, rate=rate, seed=seed)


@GATES.register("boundary")
def _boundary(window: int = 50, k: int = 4, *, steps_per_task: int) -> BoundaryGate:
    """Control 15: replay only just after task switches.

    `period` is injected as the environment's block length, so it cannot disagree
    with where the switches actually are.
    """
    return BoundaryGate(period=steps_per_task, window=window, k=k)


# --------------------------------------------------------------------------- #
# Replay policies — replay content
# --------------------------------------------------------------------------- #


class NoReplay:
    """Control 5: spend no budget, whatever the gate asks for.

    Combined with a non-null memory this isolates storage from rehearsal: if
    storage alone has an effect, this condition will show it.
    """

    def select(self, memory: Memory, k: int, latest: Observation) -> List[ReplayItem]:
        return []


class BufferSample:
    """M0 behaviour: uniform draws from the buffer, current task included.

    Delegates to the memory's own sampler so the frozen reservoir performs the
    draws, keeping bit-level equivalence with the reviewed artifact.
    """

    def __init__(self, weight: float = 1.0) -> None:
        self.weight = weight

    def select(self, memory: Memory, k: int, latest: Observation) -> List[ReplayItem]:
        if k <= 0:
            return []
        return [(obs.context, obs.target, self.weight) for obs in memory.sample(k)]


class CurrentSample:
    """Control 3: update-count-matched, non-historical.

    Replays the just-observed item `k` times. Consumes exactly the same number of
    learning updates (and, for `count_model`, the same number of row decays) as
    historical replay, while carrying no information about earlier tasks. If this
    condition matches historical replay, the M0 effect is generic extra
    optimisation rather than memory.
    """

    def __init__(self, weight: float = 1.0) -> None:
        self.weight = weight

    def select(self, memory: Memory, k: int, latest: Observation) -> List[ReplayItem]:
        if k <= 0:
            return []
        return [(latest.context, latest.target, self.weight)] * k


class HistoricalOnly:
    """Control 6: draws only from tasks other than the current one.

    Returns fewer than `k` items when no prior-task item is stored (early in the
    first block). The engine records that shortfall, because a budget-matched
    control that silently under-spends is not matched.
    """

    def __init__(self, weight: float = 1.0, *, seed: int) -> None:
        self.weight = weight
        self._rng = random.Random(seed + 104729)

    def select(self, memory: Memory, k: int, latest: Observation) -> List[ReplayItem]:
        if k <= 0:
            return []
        pool = [obs for obs in memory.snapshot() if obs.task != latest.task]
        if not pool:
            return []
        picks = [pool[self._rng.randrange(len(pool))] for _ in range(k)]
        return [(obs.context, obs.target, self.weight) for obs in picks]


class TaskBalanced:
    """Control 7: equal budget per prior task seen so far.

    Uses task labels, which a deployed mechanism would not have. It is an oracle
    reference for the best retention attainable at a given budget, not a
    candidate mechanism.
    """

    def __init__(self, weight: float = 1.0, *, seed: int) -> None:
        self.weight = weight
        self._rng = random.Random(seed + 15485863)

    def select(self, memory: Memory, k: int, latest: Observation) -> List[ReplayItem]:
        if k <= 0:
            return []
        by_task: Dict[int, List[Observation]] = defaultdict(list)
        for obs in memory.snapshot():
            if obs.task != latest.task:
                by_task[obs.task].append(obs)
        if not by_task:
            return []
        tasks = sorted(by_task)
        out: List[ReplayItem] = []
        for i in range(k):
            pool = by_task[tasks[i % len(tasks)]]
            obs = pool[self._rng.randrange(len(pool))]
            out.append((obs.context, obs.target, self.weight))
        return out


@REPLAYS.register("none")
def _no_replay() -> NoReplay:
    """Control 5: storage without rehearsal."""
    return NoReplay()


@REPLAYS.register("buffer_sample")
def _buffer_sample(weight: float = 1.0) -> BufferSample:
    """M0 replay content: uniform over the reservoir."""
    return BufferSample(weight=weight)


@REPLAYS.register("current_sample")
def _current_sample(weight: float = 1.0) -> CurrentSample:
    """Control 3: update-matched, non-historical."""
    return CurrentSample(weight=weight)


@REPLAYS.register("historical_only")
def _historical_only(weight: float = 1.0, *, seed: int) -> HistoricalOnly:
    """Control 6: prior-task items only."""
    return HistoricalOnly(weight=weight, seed=seed)


@REPLAYS.register("task_balanced")
def _task_balanced(weight: float = 1.0, *, seed: int) -> TaskBalanced:
    """Control 7: equal draws per prior task (oracle reference)."""
    return TaskBalanced(weight=weight, seed=seed)


def total_selected(items: Sequence[ReplayItem]) -> int:
    """Number of learning updates a selection will consume."""
    return len(items)
