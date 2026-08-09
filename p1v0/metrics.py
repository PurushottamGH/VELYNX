"""Aggregation of probe results into retention measures.

Responsibility: turn a sequence of probe vectors into scalars. No model access,
no IO.

The probe matrix P has one row per checkpoint (one checkpoint per task block,
in presentation order) and one column per task:

    P[b][i] = loss on task i's held-out data after finishing block b

Definitions (all in nats, lower is better):
    learned[i]   = P[b_i][i]        where b_i is the block that trained task i
    final[i]     = P[-1][i]
    forgetting[i]= final[i] - learned[i]      (>= 0 means degradation)
    retention    = mean forgetting over all tasks except the last trained one
"""

from __future__ import annotations

from typing import Dict, List, Sequence


def mean(values: Sequence[float]) -> float:
    vals = [v for v in values if v == v]  # drop NaN
    return sum(vals) / len(vals) if vals else float("nan")


def forgetting(probe_matrix: Sequence[Sequence[float]], block_tasks: Sequence[int]) -> Dict:
    """Compute per-task forgetting from a probe matrix.

    `block_tasks[b]` is the task id trained during block b. With cycles > 1 a
    task appears in several blocks; the last block that trained it is used as
    its reference, which is the conservative choice.
    """
    if not probe_matrix:
        return {"learned": [], "final": [], "forgetting": [], "retention": float("nan")}

    n_tasks = len(probe_matrix[0])
    ref_block: Dict[int, int] = {}
    for b, task in enumerate(block_tasks):
        ref_block[task] = b

    learned = [float("nan")] * n_tasks
    for task, b in ref_block.items():
        if task < n_tasks:
            learned[task] = probe_matrix[b][task]

    final = list(probe_matrix[-1])
    forg = [
        (final[i] - learned[i]) if learned[i] == learned[i] else float("nan")
        for i in range(n_tasks)
    ]

    last_task = block_tasks[-1] if block_tasks else None
    prior = [forg[i] for i in range(n_tasks) if i != last_task]

    return {
        "learned": learned,
        "final": final,
        "forgetting": forg,
        "retention": mean(prior),
    }


def summarise_online(losses: Sequence[float], tail: int = 500) -> Dict:
    """Overall and tail online loss. Tail shows the converged regime."""
    return {
        "online_loss_mean": mean(losses),
        "online_loss_tail": mean(losses[-tail:]) if losses else float("nan"),
        "steps": len(losses),
    }


def uniform_baseline(alphabet: int) -> float:
    """Loss of the uninformed predictor: log(alphabet) nats. Any useful model beats it."""
    import math

    return math.log(alphabet)
