"""Metric definitions, checked against hand-computed values.

Metrics are tested from synthetic records rather than from runs, so a metric's
arithmetic is verified independently of any mechanism. That matters most for
`excess_loss`: it is the primary outcome family, and an error in it would be
invisible in an end-to-end test that only checks the run completed.
"""

from __future__ import annotations

import math

import pytest

from core.types import ProbeRecord, StepRecord
from science.metrics.compute import Compute
from science.metrics.excess_loss import ExcessLoss
from science.metrics.gate_activity import GateActivity
from science.metrics.online_loss import OnlineLoss
from science.metrics.plasticity import Plasticity
from science.metrics.retention import Retention


def step(t: int, task: int, loss: float, replays: int = 0) -> StepRecord:
    return StepRecord(
        t=t,
        task=task,
        loss=loss,
        replays=replays,
        gate_fired=replays > 0,
        buffer_size=0,
        updates=1 + replays,
    )


def probe(block: int, trained: int, losses, oracle=None) -> ProbeRecord:
    return ProbeRecord(
        t=block * 10,
        block=block,
        trained_task=trained,
        losses=tuple(losses),
        oracle=tuple(oracle) if oracle else (),
    )


class TestOnlineLoss:
    def test_mean_tail_and_per_task(self):
        metric = OnlineLoss(tail=2)
        for t, (task, loss) in enumerate([(0, 1.0), (0, 3.0), (1, 5.0), (1, 7.0)]):
            metric.on_step(step(t, task, loss))
        out = metric.result()
        assert out["online_loss_mean"] == pytest.approx(4.0)
        assert out["online_loss_tail"] == pytest.approx(6.0)
        assert out["steps"] == 4
        assert out["online_loss_by_task"] == {"0": pytest.approx(2.0), "1": pytest.approx(6.0)}

    def test_rejects_invalid_window(self):
        with pytest.raises(ValueError, match="tail"):
            OnlineLoss(tail=0)


class TestExcessLoss:
    """Two tasks, two blocks. Task 0 is trained first, then task 1.

        block 0 (trained task 0): losses (1.0, 4.0), oracle (0.5, 0.5)
                                  excess         (0.5, 3.5)
        block 1 (trained task 1): losses (2.0, 1.0), oracle (0.5, 0.5)
                                  excess         (1.5, 0.5)

    learned[0] = 0.5 (block 0), learned[1] = 0.5 (block 1)
    final      = (1.5, 0.5)
    degradation[0] = 1.5 - 0.5 = 1.0; degradation[1] = 0.0
    prior tasks (excluding last trained, task 1) = {0}
    """

    @pytest.fixture
    def result(self):
        metric = ExcessLoss()
        metric.on_probe(probe(0, 0, (1.0, 4.0), (0.5, 0.5)))
        metric.on_probe(probe(1, 1, (2.0, 1.0), (0.5, 0.5)))
        return metric.result()

    def test_learned_and_final(self, result):
        assert result["learned_excess"] == pytest.approx([0.5, 0.5])
        assert result["final_excess"] == pytest.approx([1.5, 0.5])

    def test_degradation_is_paired_per_task(self, result):
        assert result["degradation"] == pytest.approx([1.0, 0.0])
        assert result["degradation_prior_mean"] == pytest.approx(1.0)
        assert result["backward_transfer"] == pytest.approx(-1.0)

    def test_prior_task_summary_excludes_the_task_just_trained(self, result):
        assert result["final_prior_excess_mean"] == pytest.approx(1.5)
        assert result["final_prior_excess_worst"] == pytest.approx(1.5)

    def test_retention_curve_tracks_prior_tasks_only(self, result):
        # Block 0: no prior task exists yet -> nan. Block 1: task 0's excess = 1.5.
        curve = result["retention_curve"]
        assert math.isnan(curve[0])
        assert curve[1] == pytest.approx(1.5)
        assert result["retention_auc"] == pytest.approx(1.5)

    def test_declares_itself_primary_eligible(self, result):
        assert result["primary_outcome_eligible"] is True

    def test_requires_an_oracle(self):
        assert ExcessLoss.requires_oracle is True

    def test_reports_unavailable_without_probes(self):
        assert ExcessLoss().result()["available"] is False

    def test_last_training_block_is_the_reference_under_cycles(self):
        """With repeated tasks, the *last* block that trained a task is its
        reference — the conservative choice, matching p1v0."""
        metric = ExcessLoss()
        metric.on_probe(probe(0, 0, (1.0, 9.0), (0.0, 0.0)))
        metric.on_probe(probe(1, 1, (5.0, 1.0), (0.0, 0.0)))
        metric.on_probe(probe(2, 0, (1.0, 6.0), (0.0, 0.0)))
        metric.on_probe(probe(3, 1, (4.0, 1.0), (0.0, 0.0)))
        out = metric.result()
        assert out["learned_excess"][0] == pytest.approx(1.0)  # from block 2, not block 0
        assert out["degradation"][0] == pytest.approx(3.0)  # 4.0 - 1.0


class TestRetention:
    def test_matches_frozen_implementation(self):
        """Delegation to `p1v0.metrics.forgetting` must be exact."""
        from p1v0 import metrics as v0_metrics

        matrix = [[1.0, 4.0], [2.0, 1.0]]
        tasks = [0, 1]
        metric = Retention()
        metric.on_probe(probe(0, 0, matrix[0]))
        metric.on_probe(probe(1, 1, matrix[1]))
        out = metric.result()
        expected = v0_metrics.forgetting(matrix, tasks)
        assert out["retention"] == pytest.approx(expected["retention"])
        assert out["forgetting"] == pytest.approx(expected["forgetting"])

    def test_declares_itself_ineligible_as_a_primary_outcome(self):
        """The M0 review found this metric rewards poor initial learning."""
        metric = Retention()
        metric.on_probe(probe(0, 0, (1.0, 2.0)))
        assert metric.result()["primary_outcome_eligible"] is False


class TestPlasticity:
    def test_adaptation_excludes_the_first_block(self):
        """The run's start is not a task switch, so it is reported separately."""
        metric = Plasticity(window=2)
        for t, (task, loss) in enumerate(
            [(0, 1.0), (0, 1.0), (0, 9.0), (1, 4.0), (1, 6.0), (1, 9.0)]
        ):
            metric.on_step(step(t, task, loss))
        out = metric.result()
        assert out["first_block_mean"] == pytest.approx(1.0)  # window truncates the 9.0
        assert out["adaptation_auc"] == pytest.approx(5.0)  # (4+6)/2
        assert out["n_blocks"] == 2

    def test_tail_tracks_the_final_window(self):
        metric = Plasticity(window=2)
        for t, loss in enumerate([5.0, 5.0, 1.0, 3.0]):
            metric.on_step(step(t, 0, loss))
        assert metric.result()["current_task_tail"] == pytest.approx(2.0)


class TestCompute:
    def test_accounting_identity(self):
        metric = Compute()
        metric.on_step(step(0, 0, 1.0, replays=0))
        metric.on_step(step(1, 0, 1.0, replays=4))
        metric.on_step(step(2, 0, 1.0, replays=4))
        out = metric.result()
        assert out["steps"] == 3
        assert out["online_updates"] == 3
        assert out["replay_updates"] == 8
        assert out["updates_total"] == 11
        assert out["replay_batches"] == 2
        assert out["update_multiplier"] == pytest.approx(11 / 3)


class TestGateActivity:
    def test_boundary_clustering_is_measured(self):
        """The diagnostic for the review's top-ranked alternative explanation:
        surprise firing may simply track task switches."""
        metric = GateActivity(boundary_window=2)
        # Task 0: fires late (not near a switch). Task 1: fires immediately after.
        records = [
            step(0, 0, 1.0),
            step(1, 0, 1.0),
            step(2, 0, 1.0, replays=4),  # far from a switch
            step(3, 1, 1.0, replays=4),  # 0 steps after the switch
            step(4, 1, 1.0, replays=4),  # 1 step after the switch
            step(5, 1, 1.0),
        ]
        for rec in records:
            metric.on_step(rec)
        out = metric.result()
        assert out["fired_steps"] == 3
        assert out["total_replays"] == 12
        assert out["boundary_fires"] == 2
        assert out["boundary_fire_fraction"] == pytest.approx(2 / 3)
        assert out["fires_by_task"] == {"0": 1, "1": 2}
        assert out["mean_batch_size"] == pytest.approx(4.0)

    def test_no_fires_reports_zeroes_not_errors(self):
        metric = GateActivity()
        metric.on_step(step(0, 0, 1.0))
        out = metric.result()
        assert out["fired_steps"] == 0
        assert out["boundary_fire_fraction"] == 0.0
        assert out["first_fire_step"] is None


class TestMetricIsolation:
    def test_metrics_cannot_touch_the_model(self):
        """Structural guarantee: no metric may accept anything but records."""
        import inspect

        from science.registries import METRICS

        for name in METRICS.available():
            metric = METRICS.create(name)
            for hook in ("on_step", "on_probe"):
                params = list(inspect.signature(getattr(metric, hook)).parameters)
                assert params == ["rec"], f"{name}.{hook} takes {params}"
