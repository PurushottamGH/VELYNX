"""Ground-truth predictors, for excess-loss reporting.

Responsibility: state the lowest loss achievable on a task by a predictor that
knows the true generating process.

The M0 review found raw loss incomparable across tasks (hidden assumption 10) and
the uniform baseline too weak to be informative (assumption 11): a model can beat
`log(alphabet)` while remaining far from achievable performance, and two tasks
with different intrinsic entropy produce different losses for identical
competence. Excess loss, `model_loss - oracle_loss`, removes both problems.

The oracle is evaluated on the *same* probe pairs as the model, so the
Monte-Carlo error of the probe sample cancels in the difference rather than
adding to it.
"""

from __future__ import annotations

import math
from typing import Dict, List, Sequence, Tuple

Pair = Tuple[int, int]  # (context, target)
_EPS = 1e-15


class MarkovOracle:
    """Exact conditional predictor for a set of order-1 Markov tasks.

    Holds a reference to each task's true transition rows. Read-only: the oracle
    must never be reachable from a mechanism, only from measurement code.
    """

    def __init__(self, task_rows: Sequence[Sequence[Sequence[float]]]) -> None:
        self._rows = [[list(row) for row in rows] for rows in task_rows]

    @property
    def n_tasks(self) -> int:
        return len(self._rows)

    def mean_loss(self, task_id: int, pairs: Sequence[Pair]) -> float:
        """Mean oracle loss over `pairs`, i.e. the achievable floor on that sample."""
        if not pairs:
            return float("nan")
        rows = self._rows[task_id]
        total = 0.0
        for context, target in pairs:
            p = rows[context][target] if 0 <= target < len(rows[context]) else 0.0
            total += -math.log(min(max(p, _EPS), 1.0))
        return total / len(pairs)

    def losses(self, pair_sets: Sequence[Sequence[Pair]]) -> List[float]:
        """Per-task oracle loss, aligned with the probe suite's task order."""
        return [self.mean_loss(i, pairs) for i, pairs in enumerate(pair_sets)]

    def describe(self) -> Dict[str, object]:
        return {"kind": "markov_exact", "n_tasks": self.n_tasks}
