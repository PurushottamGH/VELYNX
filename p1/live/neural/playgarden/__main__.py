"""``python -m p1.live.neural.playgarden`` — generate the environment and run proofs.

This package is **read-only for the repository**: it trains nothing, writes no
scientific records, and only optionally writes a JSON summary to ``--out``.

Example::

    python -m p1.live.neural.playgarden --seed 0
    python -m p1.live.neural.playgarden --seed 0 --out reports/playgarden.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

from p1.live.neural.playgarden import verification
from p1.live.neural.playgarden.memory import MemoryZeroEvaluator, NGramLookupModel
from p1.live.neural.playgarden.probes import (
    anti_memorisation_control,
    disjoint_relabel_probes,
    rename_pool,
    two_step_composition_probe,
    within_alphabet_permutation_probes,
)
from p1.live.neural.playgarden.worlds import CompositionWorld, Probe, RelationWorld, SequenceWorld


def build_environment(seed: int) -> Dict[str, object]:
    """Deterministic build of worlds, probes, and proofs for one seed."""
    cw = CompositionWorld(seed=seed)
    rw = RelationWorld(seed=seed)
    sw = SequenceWorld(seed=seed)

    control = anti_memorisation_control(cw)
    relabel = disjoint_relabel_probes(cw, seed=seed + 1)
    sigma = rename_pool(cw, seed=seed + 2).non_identity()
    permute = within_alphabet_permutation_probes(cw, sigma)
    two_step = two_step_composition_probe(
        cw, cw.holdout_pairs[0][0], cw.holdout_pairs[0][1], (cw.holdout_pairs[0][1] + 1) % cw.n_b
    )

    reports: Dict[str, object] = {}
    for name, world in (("composition", cw), ("relation", rw), ("sequence", sw)):
        verdicts = verification.prove_lookup_unsolvable(world.train_tokens, world.probes)
        reports[name] = verification.build_report(name, seed, world.train_tokens, verdicts)

    relabel_verdicts = verification.prove_lookup_unsolvable(cw.train_tokens, relabel)
    reports["relabel"] = verification.build_report("relabel", seed, cw.train_tokens, relabel_verdicts)
    control_verdicts = verification.prove_lookup_unsolvable(cw.train_tokens, control)
    permute_verdicts = verification.prove_lookup_unsolvable(cw.train_tokens, permute)

    mem_eval = MemoryZeroEvaluator(NGramLookupModel(cw.train_tokens))
    all_items: List[Probe] = list(cw.probes) + relabel + control
    mem_zero = mem_eval.evaluate(all_items, memory_zero=True)
    mem_kept = mem_eval.evaluate(all_items, memory_zero=False)

    return {
        "seed": seed,
        "worlds": {
            "composition": {
                "n_train_tokens": len(cw.train_tokens),
                "n_train_pairs": len(cw.train_pairs),
                "n_holdout_pairs": len(cw.holdout_pairs),
                "n_probes": len(cw.probes),
            },
            "relation": {"n_train_tokens": len(rw.train_tokens), "n_probes": len(rw.probes)},
            "sequence": {"n_train_tokens": len(sw.train_tokens), "n_probes": len(sw.probes)},
        },
        "proofs": {
            "composition_no_leak": reports["composition"].all_out_of_corpus,
            "composition_unsolvable": reports["composition"].all_unsolvable,
            "relation_no_leak": reports["relation"].all_out_of_corpus,
            "relation_unsolvable": reports["relation"].all_unsolvable,
            "sequence_no_leak": reports["sequence"].all_out_of_corpus,
            "sequence_unsolvable": reports["sequence"].all_unsolvable,
            "relabel_no_leak": reports["relabel"].all_out_of_corpus,
            "relabel_unsolvable": reports["relabel"].all_unsolvable,
            "relabel_disjoint": all(
                verification.relabel_token_disjoint(relabel, cw.train_tokens)
            ),
            "permute_sigma_non_identity": not sigma.is_identity(),
            "control_retrievable": all(v.unsolvable_by_lookup is False for v in control_verdicts),
        },
        "memory_zero": {
            "n_items": mem_zero.n_items,
            "accuracy": mem_zero.accuracy,
            "by_kind": mem_zero.by_kind,
            "identical_to_kept": mem_zero.accuracy == mem_kept.accuracy,
        },
        "two_step_probe": two_step.as_dict(),
    }


def render(env: Dict[str, object]) -> str:
    lines = [
        f"P1-ARC playgarden environment (seed={env['seed']})",
        "  worlds:",
        f"    composition:  {env['worlds']['composition']['n_train_pairs']} train pairs, "
        f"{env['worlds']['composition']['n_holdout_pairs']} held out, "
        f"{env['worlds']['composition']['n_probes']} probes, "
        f"{env['worlds']['composition']['n_train_tokens']} train tokens",
        f"    relation:     {env['worlds']['relation']['n_probes']} probes, "
        f"{env['worlds']['relation']['n_train_tokens']} train tokens",
        f"    sequence:     {env['worlds']['sequence']['n_probes']} probes, "
        f"{env['worlds']['sequence']['n_train_tokens']} train tokens",
        "  proofs:",
    ]
    for k, v in env["proofs"].items():
        lines.append(f"    {k:<28} {'PASS' if v else 'FAIL'}")
    mz = env["memory_zero"]
    lines.append(
        "  memory-zero harness: "
        f"accuracy={mz['accuracy']:.2f} over {mz['n_items']} items, "
        f"same-as-memory-kept={mz['identical_to_kept']}"
    )
    return "\n".join(lines)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate P1-ARC playgarden environment + proofs.")
    parser.add_argument("--seed", type=int, default=0, help="deterministic seed")
    parser.add_argument("--out", type=Path, default=None, help="write JSON summary to this path")
    args = parser.parse_args(argv)

    env = build_environment(args.seed)
    print(render(env))

    passed = all(env["proofs"].values())
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(env, indent=2, default=str), encoding="utf-8")
        print(f"\nwrote {args.out}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
