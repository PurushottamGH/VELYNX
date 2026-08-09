"""No train/test leakage: the held-out split is constructed.

Three independent structural separations are asserted:

1. **Construction separation** — composition train pairs and holdout pairs are
   disjoint by construction (a deterministic stride subset, never a random
   split of the same corpus).
2. **n-gram proof** — for every held-out probe,
   ``context + (expected[0],)`` does not occur as a contiguous n-gram in the
   training stream (:func:`verification.prove_no_leakage`).
3. **VOC disjointness for relabel probes** — relabeled tokens never appear in
   the training vocabulary at all.
"""

from p1.live.neural.playgarden import verification
from p1.live.neural.playgarden.probes import (
    disjoint_relabel_probes,
    rename_pool,
    two_step_composition_probe,
    within_alphabet_permutation_probes,
)
from p1.live.neural.playgarden.worlds import CompositionWorld, RelationWorld, SEP, SequenceWorld


def test_composition_holdout_pairs_disjoint_by_construction():
    cw = CompositionWorld(seed=0)
    assert set(cw.train_pairs).isdisjoint(cw.holdout_pairs)
    assert len(cw.holdout_pairs) > 0
    assert len(cw.train_pairs) > 0
    # every pair is exactly train or holdout (no pair invented by a probe)
    assert set(cw.train_pairs) | set(cw.holdout_pairs) == set(cw._pairs)


def test_probe_join_never_in_corpus_for_all_worlds():
    for world in (CompositionWorld(0), RelationWorld(0), SequenceWorld(0)):
        for p in world.probes:
            seq = p.context + (p.expected[0],)
            assert verification.contains(world.train_tokens, seq) is False


def test_no_leakage_proof_passes_all_worlds():
    for world in (CompositionWorld(0), RelationWorld(0), SequenceWorld(0)):
        for p in world.probes:
            assert verification.prove_no_leakage(world.train_tokens, p) is True


def test_relabel_tokens_disjoint_from_training_vocabulary():
    cw = CompositionWorld(seed=0)
    relabel = disjoint_relabel_probes(cw, seed=1)
    voc = set(cw.train_tokens) - {SEP}
    for p in relabel:
        assert p.kind == "relabel"
        assert set(p.context).isdisjoint(voc)
        assert set(p.expected).isdisjoint(voc)
    assert all(verification.relabel_token_disjoint(relabel, cw.train_tokens))


def test_relation_probe_pairs_never_trained():
    rw = RelationWorld(seed=0)
    train_edges = set(rw.train_edges)
    for p in rw.probes:
        edge = (p.context[0], p.expected[0])
        assert edge not in train_edges
        assert edge[::-1] not in train_edges


def test_sequence_probe_lengths_beyond_train_plot_length():
    sw = SequenceWorld(seed=0)
    max_run = max_non_sep_run(sw.train_tokens)
    min_probe_context = min(len(p.context) for p in sw.probes)
    assert min_probe_context > max_run  # no probe context fits inside any train plot


def test_two_step_holdout_absent_from_stream():
    cw = CompositionWorld(seed=0)
    i, j = cw.holdout_pairs[0]
    two_step = two_step_composition_probe(cw, i, j, (j + 1) % cw.n_b)
    assert verification.prove_no_leakage(cw.train_tokens, two_step) is True


def test_within_alphabet_permutation_deterministic_and_non_identity():
    cw = CompositionWorld(seed=0)
    sigma1 = rename_pool(cw, seed=2).non_identity()
    sigma2 = rename_pool(cw, seed=2).non_identity()
    a = within_alphabet_permutation_probes(cw, sigma1)
    b = within_alphabet_permutation_probes(cw, sigma2)
    assert [p.as_dict() for p in a] == [p.as_dict() for p in b]
    assert not sigma1.is_identity()


# --- helpers --------------------------------------------------------------


def max_non_sep_run(tokens):
    best = cur = 0
    for t in tokens:
        if t == SEP:
            cur = 0
        else:
            cur += 1
            best = max(best, cur)
    return best
