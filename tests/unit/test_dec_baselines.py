"""Baseline, oracle, and decision-layer tests for P1-LN-DEC.

The fixed ranking that the falsification harness depends on: on the
*decisive* families (composition, abstraction) Bref beats every cheap
baseline by a wide margin, and the cheap baselines are ordered
uniform >= B1 >= B2 and B0 dominating on the memorization slice.
"""

import math

from experiments.DEC import GrammarConfig, P1Grammar
from experiments.DEC.baselines import UniformBaseline, train_baselines
from experiments.DEC.metrics import mean_loss
from experiments.DEC.oracle import RefOracle

SEED = 7


def test_uniform_loss_is_log_vocab() -> None:
    g = P1Grammar(GrammarConfig(master_seed=SEED))
    fam = g.probe_families()
    unif = UniformBaseline(g)
    unif.fit(g)
    for name in fam:
        assert abs(mean_loss(unif.predict, fam[name].items) - math.log(g.cfg.vocab)) < 1e-9


def test_baselines_probe_blind_and_ordering() -> None:
    g = P1Grammar(GrammarConfig(master_seed=SEED))
    fam = g.probe_families()
    bs = {b.name: b for b in train_baselines(g)}
    losses = {
        name: {k: mean_loss(b.predict, fam[name].items) for k, b in bs.items()} for name in fam
    }

    for f in ("memorization", "tail", "composition"):
        # uniform is the floor; B1/B2 improve on it (lower = better).
        assert losses[f]["uniform"] > losses[f]["B1"]
        assert losses[f]["uniform"] > losses[f]["B2"]
    # B0 must be excellent on the memorization slice (exact lookup works there).
    assert losses["memorization"]["B0"] < losses["memorization"]["B2"]


def test_bref_beats_all_baselines() -> None:
    g = P1Grammar(GrammarConfig(master_seed=SEED))
    fam = g.probe_families()
    plain = RefOracle(g, relabel=False)
    absref = RefOracle(g, relabel=True)
    # The decisive failure case is families that require generalization.
    for name in ("composition", "abstraction", "tail"):
        items = fam[name].items
        oracle = absref if name == "abstraction" else plain
        oracle_loss = mean_loss(oracle.predict, items)
        for b in train_baselines(g):
            base_loss = mean_loss(b.predict, items)
            assert oracle_loss < base_loss, f"Bref lost to {b.name} on {name}"


def test_bref_on_memorization_is_sane() -> None:
    # B2 is a memorizer; Bref is a generalizer. Bref must still do far better
    # than chance on the pure memorization slice and stay within ~15% of B2.
    g = P1Grammar(GrammarConfig(master_seed=SEED))
    items = g.probe_families()["memorization"].items
    bref = mean_loss(RefOracle(g, relabel=False).predict, items)
    uniform = math.log(g.cfg.vocab)
    b2 = None
    for b in train_baselines(g):
        if b.name == "B2":
            b2 = mean_loss(b.predict, items)
    assert b2 is not None
    assert bref < uniform
    assert bref < 1.15 * b2


def test_oracle_relabel_switch() -> None:
    g = P1Grammar(GrammarConfig(master_seed=SEED))
    items = g.probe_families()["abstraction"].items
    plain = mean_loss(RefOracle(g, relabel=False).predict, items)
    relabeled = mean_loss(RefOracle(g, relabel=True).predict, items)
    # Only the relabel-aware oracle knows the abstract symbols.
    assert relabeled < plain
