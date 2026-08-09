"""Exact-lookup unsolvability: the strongest naive retriever cannot answer.

``verification.prove_lookup_unsolvable`` scores every probe against an exact
n-gram lookup baseline over the training stream (the strongest naive
memorizer possible). These tests establish:

- every **held-out** probe is unsolvable by exact lookup;
- the **anti-memorisation control** (a train-pair probe emitted in the
  corpus) *is* solvable, proving the baseline is not vacuous and that the
  boundary between retrievable and unretrievable is measurable.
"""

from p1.live.neural.playgarden import verification
from p1.live.neural.playgarden.probes import anti_memorisation_control, disjoint_relabel_probes
from p1.live.neural.playgarden.worlds import CompositionWorld, RelationWorld, SequenceWorld


def _assert_all_unsolvable(verdicts):
    assert verdicts
    assert all(v.unsolvable_by_lookup for v in verdicts)


def test_composition_holdouts_unsolvable_by_exact_lookup():
    cw = CompositionWorld(seed=0)
    verdict = verification.prove_lookup_unsolvable(cw.train_tokens, cw.probes)
    assert len(verdict) == len(cw.probes)
    _assert_all_unsolvable(verdict)
    for v in verdict:
        assert v.top != v.expected_first


def test_relation_holdouts_unsolvable():
    rw = RelationWorld(seed=0)
    verdict = verification.prove_lookup_unsolvable(rw.train_tokens, rw.probes)
    _assert_all_unsolvable(verdict)


def test_sequence_holdouts_unsolvable():
    sw = SequenceWorld(seed=0)
    verdict = verification.prove_lookup_unsolvable(sw.train_tokens, sw.probes)
    _assert_all_unsolvable(verdict)


def test_disjoint_relabel_unsolvable_with_zero_coverage():
    cw = CompositionWorld(seed=0)
    relabel = disjoint_relabel_probes(cw, seed=1)
    verdict = verification.prove_lookup_unsolvable(cw.train_tokens, relabel)
    _assert_all_unsolvable(verdict)
    for v in verdict:
        assert v.coverage == 0.0  # literally no memory of the symbols
        assert v.top is None


def test_anti_memorisation_control_retrievable():
    cw = CompositionWorld(seed=0)
    control = anti_memorisation_control(cw)
    verdict = verification.prove_lookup_unsolvable(cw.train_tokens, control)
    assert len(verdict) == 1
    v = verdict[0]
    # in-corpus by design: the pair was emitted in training
    assert v.out_of_corpus is False
    assert v.unsolvable_by_lookup is False
    assert v.top == v.expected_first


def test_generated_env_reaches_same_proof_conclusions():
    from p1.live.neural.playgarden.__main__ import build_environment

    env = build_environment(seed=0)
    assert all(env["proofs"].values())
