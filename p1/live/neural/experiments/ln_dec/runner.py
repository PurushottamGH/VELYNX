"""Minimum isolated P1-LN-DEC runner.

The runner intentionally treats ``--decisive`` as a guarded operation.  With
the current protocol SESOI is OPEN, so that mode refuses before corpus
construction or training.  ``--dry-run`` is a tiny, explicitly non-decisive
path for exercising interfaces and artifact sealing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Dict, Mapping, Sequence

from p1.live.neural.experiments.ln_dec.adapter import NN0Adapter
from p1.live.neural.experiments.ln_dec.benchmark import BenchmarkCorpus, build_corpus
from p1.live.neural.experiments.ln_dec.baselines import train_baselines
from p1.live.neural.experiments.ln_dec.oracle import ReferenceOracle, audit_candidate_information
from p1.live.neural.experiments.ln_dec.protocol import (
    PROTOCOL_HASH_PATH,
    PROTOCOL_PATH,
    ProtocolRefusal,
    build_protocol,
    canonical_json,
    load_and_verify_protocol,
    protected_surface_manifest,
    protocol_hash,
    require_decisive_allowed,
    store_content_hash,
    write_protocol,
)
from p1.live.neural.experiments.ln_dec.rng import SeedStreams
from p1.live.neural.nn0.nucleus import NN0Config, NN0Trainer


def _config_for(corpus: BenchmarkCorpus, protocol: Mapping[str, object], *, tiny: bool, seed: int) -> NN0Config:
    streams = SeedStreams.build(seed)
    if tiny:
        hidden, embed, read = 32, 16, 16
        capacity, batch = 128, 8
    else:
        hidden, embed, read = 128, 32, 32
        capacity, batch = 65536, 64
    return NN0Config(
        vocab_size=corpus.vocabulary.size,
        d_embed=embed,
        d_hidden=hidden,
        d_read=read,
        kv_capacity=capacity,
        kv_top_k=4,
        replay_capacity=capacity,
        replay_alpha=0.6,
        replay_batch_size=batch,
        replay_every=1,
        lr=1e-3,
        weight_decay=5e-4,
        store_threshold=0.0,
        seed=streams.seeds["model_init"],
        replay_seed=streams.seeds["replay"],
        device="cpu",
        experiment_id="p1-ln-dec",
        run_id=seed,
        protocol_id=protocol_hash(protocol),
        vocabulary_id=corpus.vocabulary.vocabulary_id,
    )


def initialize_protocol(root: Path) -> str:
    """Create the isolated protocol after all implementation files exist."""
    corpus = build_corpus(master_seed=0, tiny=False)
    config = _config_for(corpus, {"placeholder": True}, tiny=False, seed=0)
    # The placeholder protocol ID above is not used for training; it only lets
    # us instantiate the nucleus to record its exact parameter count.
    trainer = NN0Trainer(config)
    protected = protected_surface_manifest(root)
    protocol = build_protocol(
        root,
        vocabulary=corpus.vocabulary.as_dict(),
        parameter_count=trainer.parameter_count(),
        nn_config={
            "vocab_size": corpus.vocabulary.size,
            "d_embed": config.d_embed,
            "d_hidden": config.d_hidden,
            "d_read": config.d_read,
            "kv_capacity": config.kv_capacity,
            "kv_top_k": config.kv_top_k,
            "replay_capacity": config.replay_capacity,
            "replay_alpha": config.replay_alpha,
            "replay_batch_size": config.replay_batch_size,
            "replay_every": config.replay_every,
            "lr": config.lr,
            "weight_decay": config.weight_decay,
            "training_mode": config.training_mode,
            "bptt_window": config.bptt_window,
        },
        corpus_manifest=corpus.manifest.as_dict(),
        protected_manifest=protected,
        store_hash=store_content_hash(root),
    )
    return write_protocol(root, protocol)


def verify_corpus(corpus: BenchmarkCorpus) -> None:
    """Run the corpus invariants and blacklist-ready source checks."""
    corpus.validate()
    if set(corpus.training_ids) & set(corpus.probe_ids):
        raise AssertionError("training/probe source overlap")
    if any(not source.startswith("probe:") for source in corpus.probe_ids):
        raise AssertionError("probe source IDs are not namespaced")
    if any(not source.startswith("train:") for source in corpus.training_ids):
        raise AssertionError("training source IDs are not namespaced")


def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else float("nan")


def _family_means(scores: Mapping[str, float], corpus: BenchmarkCorpus) -> Dict[str, float]:
    return {
        family: _mean([scores[probe.probe_id] for probe in corpus.probes_for(family)])
        for family in sorted({probe.family for probe in corpus.probes})
    }


def run_dry_run(root: Path, *, seed: int = 0, output_dir: Path | None = None) -> Dict[str, object]:
    """Run a tiny non-decisive corpus through candidate and controls."""
    protocol = load_and_verify_protocol(root)
    corpus = build_corpus(master_seed=seed, tiny=True)
    verify_corpus(corpus)
    info_audit = audit_candidate_information(corpus)

    config = _config_for(corpus, protocol, tiny=True, seed=seed)
    candidate = NN0Adapter(
        config,
        corpus.vocabulary,
        probe_ids=corpus.probe_ids,
        training_ids=corpus.training_ids,
    )
    for experience in corpus.training:
        candidate.learn(experience)

    baselines = train_baselines(corpus.vocabulary, corpus.training)
    candidate_scores = candidate.evaluate(corpus.probes)
    baseline_scores = {baseline.name: baseline.score_items(corpus.probes) for baseline in baselines}
    oracle_scores = ReferenceOracle(corpus).score_items(corpus.probes)

    params_before_n1 = candidate.parameter_hash()
    replay_before_n1 = candidate.replay_size
    candidate.clear_external_memory()
    n1_scores = candidate.evaluate(corpus.probes)
    if candidate.parameter_hash() != params_before_n1:
        raise AssertionError("N1 changed learned weights")
    if candidate.replay_size != replay_before_n1:
        raise AssertionError("N1 changed replay state")

    payload: Dict[str, object] = {
        "run_mode": "NON_DECISIVE_DRY_RUN",
        "decisive_experiment_executed": False,
        "master_seed": seed,
        "benchmark_fingerprint": corpus.fingerprint(),
        "benchmark_manifest": corpus.manifest.as_dict(),
        "candidate_information_audit": info_audit,
        "candidate": {
            "parameter_count": candidate.trainer.parameter_count(),
            "parameter_hash": candidate.parameter_hash(),
            "nll_by_item": candidate_scores,
            "family_means": _family_means(candidate_scores, corpus),
        },
        "baselines": {
            name: {"nll_by_item": scores, "family_means": _family_means(scores, corpus)}
            for name, scores in sorted(baseline_scores.items())
        },
        "reference_ceiling": {
            "name": "Bref_reference_ceiling",
            "nll_by_item": oracle_scores,
            "family_means": _family_means(oracle_scores, corpus),
        },
        "N1": {
            "semantics": "external KV cleared only",
            "nll_by_item": n1_scores,
            "family_means": _family_means(n1_scores, corpus),
            "delta_by_item": {
                probe_id: n1_scores[probe_id] - candidate_scores[probe_id]
                for probe_id in candidate_scores
            },
        },
        "protocol_sha256": protocol_hash(protocol),
        "protected_surface_aggregate_sha256": protocol["protected_surface"]["aggregate_sha256"],
        "store_content_hash": protocol["store_content_hash"],
    }
    sealed = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    payload["artifact_sha256"] = sealed
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "run.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (output_dir / "SHA256SUM").write_text(sealed + "  run.json\n", encoding="utf-8")
    return payload


def run_cli(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="P1-LN-DEC isolated runner")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--init-protocol", action="store_true")
    mode.add_argument("--verify", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--decisive", action="store_true")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    root = Path.cwd()

    try:
        if args.init_protocol:
            digest = initialize_protocol(root)
            print(f"protocol initialized: {digest}")
            return 0
        if args.verify:
            protocol = load_and_verify_protocol(root)
            print(f"protocol verified: {protocol_hash(protocol)}")
            return 0
        if args.decisive:
            protocol = load_and_verify_protocol(root)
            require_decisive_allowed(protocol, root)
            raise ProtocolRefusal("decisive execution is intentionally disabled in this transaction")
        output = args.out or (root / "artifacts/p1-ln-dec/dry-run")
        payload = run_dry_run(root, seed=args.seed, output_dir=output)
        print(json.dumps({"run_mode": payload["run_mode"], "artifact_sha256": payload["artifact_sha256"]}, sort_keys=True))
        return 0
    except ProtocolRefusal as exc:
        print(f"REFUSED: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(run_cli())


__all__ = ["initialize_protocol", "run_cli", "run_dry_run", "verify_corpus"]
