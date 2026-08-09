"""Determinism and structural-separation tests for the P1-LN-DEC grammar.

These enforce the properties claimed by ``experiments/DEC/grammar.py``: master
seed determinism, call-order invariance, disjoint abstraction block, hold-out
templates never trained, and the memorization slice being an exact training
reproduction.
"""

import pytest

from experiments.DEC import GrammarConfig, P1Grammar


def _grammar(seed: int = 7) -> P1Grammar:
    return P1Grammar(GrammarConfig(master_seed=seed))


def test_same_seed_identity() -> None:
    a, b = _grammar(7), _grammar(7)
    assert a.training_observations() == b.training_observations()
    fa, fb = a.probe_families(), b.probe_families()
    assert set(fa) == set(fb)
    for name in fa:
        assert fa[name].items == fb[name].items


def test_different_seeds_differ() -> None:
    a, b = _grammar(1), _grammar(2)
    assert a.training_observations() != b.training_observations()


def test_call_order_invariance() -> None:
    probe_first = _grammar(42)
    fa = probe_first.probe_families()
    train_first = _grammar(42)
    _ = train_first.training_observations()
    fb = train_first.probe_families()
    for name in fa:
        assert fa[name].items == fb[name].items, name


def test_abstraction_block_disjoint_from_training() -> None:
    g = _grammar(7)
    trained: set[int] = {t for ctx, tgt in g.training_observations() for t in ctx}
    trained |= {t for _, tgt in g.training_observations() for t in [tgt]}
    assert trained.isdisjoint(range(g.cfg.abst_lo, g.cfg.abst_hi))


def test_abstraction_probe_pairs_not_in_training() -> None:
    g = _grammar(7)
    train = set(g.training_observations())
    abs_items = set(g.probe_families()["abstraction"].items)
    assert not (abs_items & train)


def test_hold_compositions_never_trained_as_program() -> None:
    g = _grammar(7)
    cfg = g.cfg
    from experiments.DEC.grammar import TRAIN_COMPOSITIONS, TRAIN_TEMPLATES

    trained_templates = list(TRAIN_TEMPLATES) + list(TRAIN_COMPOSITIONS)
    max_trained_body = max(len(t) for t in trained_templates) * cfg.atom_length
    train_body_lens = {len(ctx) - 1 for ctx, _ in g.training_observations()}
    assert max(train_body_lens) == max_trained_body
    # A 3-atom hold program (a,b,c) needs a 9-token body stream: strictly
    # longer than training can ever emit, so no hold *program* is reproduceable
    # from training alone.
    comp_ctx_lens = {len(ctx) - 1 for ctx, _ in g.probe_families()["composition"].items}
    assert max(comp_ctx_lens) > max(train_body_lens)


def test_memorization_is_exact_training_slice() -> None:
    g = _grammar(7)
    mem = g.probe_families()["memorization"]
    train = g.training_observations()
    # The memorization family must be the *ordered* head of the training
    # stream: byte-identical reproductions, so B0/B2 can be near-perfect.
    assert mem.items == tuple(train[: len(mem)])


def test_training_contexts_use_only_body_block() -> None:
    g = _grammar(7)
    cfg = g.cfg
    for ctx, _ in g.training_observations():
        assert all(t == cfg.start or t == cfg.eos or t < cfg.base for t in ctx)


def test_config_rejects_overlap_alphabet() -> None:
    with pytest.raises(ValueError):
        GrammarConfig(master_seed=1, alphabet=5, rule_count=3, band_size=3)
    with pytest.raises(ValueError):
        GrammarConfig(master_seed=1, atom_length=1)


def test_describe_roundtrip() -> None:
    g = _grammar(3)
    d = g.describe()
    assert d["kind"] == "p1arc_grammar_minimal"
    assert d["master_seed"] == 3
