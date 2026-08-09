"""Memory-zero evaluation harness (N1 ablation protocol).

The harness pins the environment-side protocol of the memory-zero ablation: a
frozen predictor is measured with memory cleared *before* every probe item.
It asserts:

- ``reset()`` is called once per item under ``memory_zero=True`` and not at
  all under ``memory_zero=False``;
- the harness **never** calls ``learn``;
- the exact-lookup baseline solves the in-corpus control and cannot solve any
  held-out composite, so the boundary is measurable in both modes (the
  baseline is stateless, hence mode-invariant).
"""

from p1.live.neural.playgarden import verification
from p1.live.neural.playgarden.memory import MemoryZeroEvaluator, NGramLookupModel
from p1.live.neural.playgarden.probes import anti_memorisation_control, disjoint_relabel_probes
from p1.live.neural.playgarden.worlds import CompositionWorld


class _GuardedModel:
    """A model with `learn` that raises and a counting `reset`."""

    learn_calls = 0
    reset_calls = 0

    def __init__(self, model):
        self._model = model

    def learn(self, *a, **k):
        self.learn_calls += 1
        raise AssertionError("harness must never call learn()")

    def reset(self):
        self.reset_calls += 1
        self._model.reset()

    def predict(self, context):
        return self._model.predict(context)


def test_reset_called_before_every_item_in_memory_zero_mode():
    cw = CompositionWorld(seed=0)
    guarded = _GuardedModel(NGramLookupModel(cw.train_tokens))
    ev = MemoryZeroEvaluator(guarded)
    items = list(cw.probes) + anti_memorisation_control(cw) + disjoint_relabel_probes(cw, seed=1)
    ev.evaluate(items, memory_zero=True)
    assert guarded.reset_calls == len(items)


def test_no_reset_outside_memory_zero_mode():
    cw = CompositionWorld(seed=0)
    guarded = _GuardedModel(NGramLookupModel(cw.train_tokens))
    ev = MemoryZeroEvaluator(guarded)
    ev.evaluate(cw.probes, memory_zero=False)
    assert guarded.reset_calls == 0


def test_learn_never_called_by_harness():
    cw = CompositionWorld(seed=0)
    guarded = _GuardedModel(NGramLookupModel(cw.train_tokens))
    ev = MemoryZeroEvaluator(guarded)
    ev.evaluate(cw.probes, memory_zero=True)
    ev.evaluate(cw.probes, memory_zero=False)
    assert guarded.learn_calls == 0  # the guard would have raised


def test_baseline_solves_control_not_holdouts():
    cw = CompositionWorld(seed=0)
    ev = MemoryZeroEvaluator(NGramLookupModel(cw.train_tokens))
    items = list(cw.probes) + anti_memorisation_control(cw)
    report = ev.evaluate(items, memory_zero=True)

    assert report.by_kind["composition"] == 0.0
    assert report.by_kind["anti_memorisation_control"] == 1.0

    # stateless baseline: the boundary holds in both memory modes
    kept = ev.evaluate(items, memory_zero=False)
    assert kept.accuracy == report.accuracy


def test_report_fields_sane_and_control_drives_n_solved():
    cw = CompositionWorld(seed=0)
    ev = MemoryZeroEvaluator(NGramLookupModel(cw.train_tokens))
    items = list(cw.probes) + anti_memorisation_control(cw)

    report = ev.evaluate(items, memory_zero=True)
    assert report.n_items == len(items)
    assert 0.0 <= report.accuracy <= 1.0
    assert set(report.by_kind) == {"composition", "anti_memorisation_control"}
    assert report.n_solved == 1  # only the control is solvable
    assert report.memory_zero is True


def test_proof_reports_consistent_with_construction():
    cw = CompositionWorld(seed=0)
    verdict = verification.prove_lookup_unsolvable(cw.train_tokens, cw.probes)
    assert all(v.out_of_corpus for v in verdict)
    assert all(v.unsolvable_by_lookup for v in verdict)
