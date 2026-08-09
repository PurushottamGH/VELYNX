"""Determinism and reproducibility of the playgarden generators.

Every generator is a pure function of its seed. The environment must be
byte-identical under repeated construction with the same seed, and different
seeds must produce different anonymous alphabets.
"""

from p1.live.neural.playgarden.alphabet import Alphabet, Permutation, disjoint_alpha, token
from p1.live.neural.playgarden.worlds import CompositionWorld, RelationWorld, SequenceWorld


def test_token_deterministic_and_kind_namespaced():
    a = token(0, 0, "a")
    assert a == token(0, 0, "a")
    assert a.startswith("a_")
    assert a != token(0, 0, "b")
    assert a != token(1, 0, "a")


def test_alphabet_cached_symbols_deterministic():
    alpha = Alphabet(seed=0)
    assert alpha.symbol("a", 3) == token(0, 3, "a")
    assert alpha.symbol("a", 3) == alpha.symbol("a", 3)


def test_worlds_deterministic_across_rebuilds():
    for make in (CompositionWorld, RelationWorld, SequenceWorld):
        w1, w2 = make(seed=7), make(seed=7)
        assert w1.train_tokens == w2.train_tokens
        assert [p.as_dict() for p in w1.probes] == [p.as_dict() for p in w2.probes]


def test_different_seeds_different_alphabet():
    a, b = CompositionWorld(seed=0), CompositionWorld(seed=1)
    tokens_a = {t for t in a.train_tokens if t != "SEP"}
    tokens_b = {t for t in b.train_tokens if t != "SEP"}
    assert tokens_a.isdisjoint(tokens_b)


def test_permutation_deterministic_and_bijective():
    sigma1 = Permutation(seed=5, pool=("x", "y", "z", "w"))
    sigma2 = Permutation(seed=5, pool=("x", "y", "z", "w"))
    assert sigma1.forward == sigma2.forward
    assert sorted(sigma1.apply(sigma1.pool)) == sorted(sigma1.pool)  # bijection over pool
    assert not sigma1.is_identity()


def test_non_identity_is_involution():
    p = Permutation(seed=0, pool=("a", "b", "c", "d"))
    np = p.non_identity()
    assert not np.is_identity()
    # an adjacent transposition is its own inverse
    assert np.apply(np.apply(p.pool)) == p.pool


def test_disjoint_alpha_is_really_disjoint():
    avoid = ("z1", "z2", "z3")
    got = disjoint_alpha(0, "rel", 8, avoid)
    assert set(got).isdisjoint(set(avoid))
    assert len(got) == 8


def test_separator_is_reserved():
    for w in (CompositionWorld(0), RelationWorld(0), SequenceWorld(0)):
        assert "SEP" in set(w.train_tokens)
        for p in w.probes:
            assert "SEP" not in set(p.context)
            assert "SEP" not in set(p.expected)
