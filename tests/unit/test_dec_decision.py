"""P1-LN-DEC decision-layer tests.

The adjudication must be conservative: an oracle-level candidate that passes
every measured gate is still INCONCLUSIVE until the N1 ablation is provided;
a lookup-level candidate that cannot beat B0/B2 on the decisive probe is FAIL.
"""

from experiments.DEC import GrammarConfig, P1Grammar
from experiments.DEC.baselines import train_baselines
from experiments.DEC.metrics import mean_loss
from experiments.DEC.oracle import RefOracle
from experiments.DEC import decision as D

SEEDS = (1, 7, 42, 99, 1234)


def family_tables(seed: int):
    """mean-loss[family][model] for one seed (all probe-free models)."""
    g = P1Grammar(GrammarConfig(master_seed=seed))
    fam = g.probe_families()
    preds = {b.name: b.predict for b in train_baselines(g)}
    preds["uniform"] = lambda c: [1.0 / g.cfg.vocab] * g.cfg.vocab
    plain = RefOracle(g, relabel=False)
    absref = RefOracle(g, relabel=True)
    out = {}
    for name, pf in fam.items():
        items = pf.items
        oracle = absref if name == "abstraction" else plain
        row = {k: mean_loss(p, items) for k, p in preds.items()}
        row[D.BREF_KEY] = mean_loss(oracle.predict, items)
        out[name] = row
    return out


def seeds(candidate_for_family):
    out = []
    for seed in SEEDS:
        table = family_tables(seed)
        loss = {name: dict(row) for name, row in table.items()}
        for name, value in candidate_for_family(seed).items():
            loss[name][D.CAND_KEY] = value
        out.append(D.Seed(seed=seed, loss=loss))
    return tuple(out)


def oracle_candidate(seed):
    table = family_tables(seed)
    return {name: row[D.BREF_KEY] for name, row in table.items()}


def lookup_candidate(seed):
    table = family_tables(seed)
    out = {}
    for name, row in table.items():
        out[name] = row[D.B0_KEY] if name in D.DECISIVE_FAMILIES else row[D.BREF_KEY]
    return out


def test_oracle_level_candidate_is_inconclusive_without_n1() -> None:
    v = D.evaluate(seeds(oracle_candidate))
    assert v.status == D.INCONCLUSIVE, v.summary()
    assert v.decisive_seeds == 5
    for k in ("K1", "K2", "K3", "K4", "K5", "K7"):
        assert v.gates[k].ok, k


def test_oracle_level_candidate_passes_with_n1_ablation() -> None:
    seeds = []
    for seed in SEEDS:
        table = family_tables(seed)
        loss = {name: dict(row) for name, row in table.items()}
        for name in table:
            loss[name][D.CAND_KEY] = oracle_candidate(seed)[name]
        # N1 ablation far worse (loss inflated): memory doing the work.
        n1 = {name: loss[name][D.CAND_KEY] * 1.5 for name in table}
        seeds.append(D.Seed(seed=seed, loss=loss, loss_n1=n1))
    verdict = D.evaluate(tuple(seeds))
    assert verdict.status == D.PASS, verdict.summary()


def test_lookup_candidate_fails() -> None:
    verdict = D.evaluate(seeds(lookup_candidate))
    assert verdict.status == D.FAIL
    assert verdict.decisive_seeds == 0


def test_n1_without_drop_fails() -> None:
    seeds = []
    for seed in SEEDS:
        loss = {name: dict(row) for name, row in family_tables(seed).items()}
        for name in loss:
            loss[name][D.CAND_KEY] = oracle_candidate(seed)[name]
        n1_no_drop = {name: loss[name][D.CAND_KEY] for name in loss}
        seeds.append(D.Seed(seed=seed, loss=loss, loss_n1=n1_no_drop))
    verdict = D.evaluate(tuple(seeds))
    assert verdict.status == D.FAIL
