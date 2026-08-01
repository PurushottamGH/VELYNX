"""M0 retention, reproduced exactly.

Responsibility: report `p1v0`'s change-from-learned forgetting scalar, unchanged,
so M1 results remain comparable with the reviewed M0 artifact.

The computation is delegated to `p1v0.metrics.forgetting` rather than reimplemented:
a reimplementation could drift, and the point of this metric is continuity.

Known defect, stated here because the number is easy to misread. The M0 review
(risk 5, hidden assumption 14) found that `retention = mean(final - learned)`:

  * rewards poor initial learning — a model that never learned a task cannot lose
    it, so weak learners score well;
  * carries a sign convention where *lower is better*, despite the name;
  * conflates initial mastery with final performance and hides per-task spread.

`excess_loss` is the metric intended to carry inferential weight. This one is
retained for comparability only, and should not be used as a primary outcome.
"""

from __future__ import annotations

from typing import Any, Dict, List

from core.types import ProbeRecord
from p1v0 import metrics as v0_metrics
from science.metrics.base import BaseMetric
from science.registries import METRICS


class Retention(BaseMetric):
    name = "retention"

    def __init__(self) -> None:
        self._matrix: List[List[float]] = []
        self._block_tasks: List[int] = []

    def on_probe(self, rec: ProbeRecord) -> None:
        self._matrix.append(list(rec.losses))
        self._block_tasks.append(rec.trained_task)

    def result(self) -> Dict[str, Any]:
        out = dict(v0_metrics.forgetting(self._matrix, self._block_tasks))
        out["probe_matrix"] = [list(row) for row in self._matrix]
        out["block_tasks"] = list(self._block_tasks)
        out["definition"] = (
            "mean(final - learned) over tasks except the last trained; lower is better"
        )
        out["primary_outcome_eligible"] = False
        return out


@METRICS.register("retention")
def _retention() -> Retention:
    return Retention()
