"""Focused interface, leakage, and non-decisive-run tests for P1-LN-DEC."""

from __future__ import annotations

import json
import math
from dataclasses import replace
from pathlib import Path

import pytest
import torch

from core.protocols import Model
from p1.live.neural.experiments.ln_dec.adapter import (
    EvaluationMutationError,
    NN0Adapter,
)
from p1.live.neural.experiments.ln_dec.benchmark import DECISIVE_FAMILIES, build_corpus
from p1.live.neural.experiments.ln_dec.baselines import train_baselines
from p1.live.neural.experiments.ln_dec.claims import ClaimClass, validate_claim_class
from p1.live.neural.experiments.ln_dec.oracle import audit_candidate_information
from p1.live.neural.experiments.ln_dec.protocol import (
    ProtocolRefusal,
    PROTOCOL_PATH,
    load_and_verify_protocol,
    protocol_hash,
    require_decisive_allowed,
    verify_protected_surface,
    verify_protocol_digest,
    verify_master_seed_set,
)
from p1.live.neural.experiments.ln_dec.runner import _config_for, run_dry_run
from p1.live.neural.experiments.ln_dec.stats import (
    SeedContrast,
    compute_paired_statistics,
)
from p1.live.neural.experiments.ln_dec.types import Experience
from p1.live.neural.nn0.nucleus import NN0Config, NN0Trainer
from p1.live.neural.playgarden import verification as playgarden_verification
from p1.live.neural.playgarden.worlds import CompositionWorld


@pytest.fixture(scope="module")
def corpus():
    return build_corpus(0, tiny=True)


def make_adapter(corpus, *, seed: int = 0, device: str = "cpu") -> NN0Adapter:
    return NN0Adapter(
        NN0Config(
            vocab_size=corpus.vocabulary.size,
            d_embed=16,
            d_hidden=32,
            d_read=16,
            kv_capacity=128,
            kv_top_k=4,
            replay_capacity=128,
            replay_batch_size=8,
            replay_every=1,
            seed=seed,
            replay_seed=seed + 1000,
            device=device,
            protocol_id="test-protocol",
            vocabulary_id=corpus.vocabulary.vocabulary_id,
        ),
        corpus.vocabulary,
        probe_ids=corpus.probe_ids,
        training_ids=corpus.training_ids,
    )


def train_adapter(adapter: NN0Adapter, corpus) -> None:
    for experience in corpus.training:
        adapter.learn(experience)


def test_canonical_benchmark_determinism_and_rng_isolation():
    a = build_corpus(7, tiny=True, seed_overrides={"replay": 1})
    b = build_corpus(7, tiny=True, seed_overrides={"replay": 2})
    assert [item.as_dict() for item in a.training] == [item.as_dict() for item in b.training]
    assert [item.as_dict() for item in a.probes] == [item.as_dict() for item in b.probes]
    c = build_corpus(7, tiny=True, seed_overrides={"model_init": 999})
    assert [item.as_dict() for item in a.probes] == [item.as_dict() for item in c.probes]


def test_composition_target_identifiability_and_calibration(corpus):
    corpus.validate()
    audit = audit_candidate_information(corpus)
    assert audit["candidate_has_sufficient_observable_information"] is True
    assert audit["symbol_mapping_calibrated"] is True
    assert set(p.family for p in corpus.probes) >= set(DECISIVE_FAMILIES)


def test_candidate_view_excludes_private_reference_semantics(corpus):
    view = corpus.candidate_view()
    public = corpus.as_public_dict()
    assert not hasattr(view, "reference")
    assert "reference" not in public
    assert "mapping" not in public


def test_playgarden_composition_selector_repairs_old_ambiguity():
    world = CompositionWorld(seed=0)
    assert playgarden_verification.assert_target_identifiability(world.probes) is True


def test_held_out_composition_and_no_direct_answer_leakage(corpus):
    training_sequences = {item.sequence() for item in corpus.training}
    for probe in corpus.probes:
        if probe.family in DECISIVE_FAMILIES:
            assert probe.sequence() not in training_sequences
            assert probe.context not in {item.context for item in corpus.training}


def test_probe_change_after_freeze_is_rejected(corpus):
    changed = replace(
        corpus.probes[0], target=(corpus.probes[0].target + 1) % corpus.vocabulary.size
    )
    with pytest.raises(AssertionError):
        replace(corpus, probes=(changed,) + corpus.probes[1:]).validate()


def test_adapter_is_core_model_and_learns(corpus):
    adapter = make_adapter(corpus)
    assert isinstance(adapter, Model)
    item = corpus.training[0]
    before = adapter.parameter_hash()
    prediction = adapter.predict(item.context)
    assert len(prediction) == corpus.vocabulary.size
    assert math.isfinite(adapter.score(prediction, item.target))
    adapter.learn(item)
    assert adapter.parameter_hash() != before
    assert adapter.memory_size > 0
    assert adapter.replay_size > 0


def test_adapter_state_roundtrip_and_episode_reset(corpus):
    adapter = make_adapter(corpus)
    train_adapter(adapter, corpus)
    params = adapter.parameter_hash()
    memory = adapter.memory_size
    replay = adapter.replay_size
    state = adapter.state_dict()
    restored = make_adapter(corpus)
    restored.load_state_dict(state)
    assert restored.parameter_hash() == params
    assert restored.memory_size == memory
    assert restored.replay_size == replay
    adapter.reset_episode()
    assert adapter.trainer.last_h is None
    assert adapter.parameter_hash() == params
    assert adapter.memory_size == memory
    assert adapter.replay_size == replay


def test_external_memory_and_replay_clear_are_independent(corpus):
    adapter = make_adapter(corpus)
    train_adapter(adapter, corpus)
    params = adapter.parameter_hash()
    replay = adapter.replay_size
    adapter.clear_external_memory()
    assert adapter.memory_size == 0
    assert adapter.replay_size == replay
    assert adapter.parameter_hash() == params
    adapter.clear_replay()
    assert adapter.replay_size == 0
    assert adapter.parameter_hash() == params


def test_provenance_blacklist_rejects_training_replay_and_kv(corpus):
    probe = corpus.probes[0]
    bad = replace(
        corpus.training[0],
        source_id=probe.source_id,
        experience_id="bad-experience",
    )
    with pytest.raises(AssertionError):
        replace(corpus, training=corpus.training + (bad,)).validate()

    adapter = make_adapter(corpus)
    with pytest.raises(AssertionError):
        adapter.learn(bad)
    with pytest.raises(AssertionError):
        adapter.trainer.replay.push(
            0,
            1,
            1.0,
            source_id=probe.source_id,
            forbidden_source_ids={probe.source_id},
        )
    key = torch.zeros(1, adapter.trainer.cfg.d_read)
    value = torch.zeros(1, adapter.trainer.cfg.d_embed)
    with pytest.raises(AssertionError):
        adapter.trainer.memory.write(
            key,
            value,
            0,
            1.0,
            source_id=probe.source_id,
            forbidden_source_ids={probe.source_id},
        )


def test_evaluation_is_immutable_and_learn_is_forbidden(corpus):
    adapter = make_adapter(corpus)
    train_adapter(adapter, corpus)
    params = adapter.parameter_hash()
    digest = adapter.state_digest()
    memory = adapter.memory_size
    replay = adapter.replay_size
    scores = adapter.evaluate(corpus.probes)
    assert set(scores) == set(corpus.probe_ids)
    assert adapter.parameter_hash() == params
    assert adapter.state_digest() == digest
    assert adapter.memory_size == memory
    assert adapter.replay_size == replay
    with pytest.raises(EvaluationMutationError):
        with adapter.evaluation_mode():
            adapter.learn(corpus.training[0])


def test_checkpoint_tensor_corruption_is_rejected(tmp_path: Path):
    trainer = NN0Trainer(
        NN0Config(
            vocab_size=8,
            d_embed=8,
            d_hidden=16,
            d_read=8,
            kv_capacity=8,
            replay_capacity=8,
            replay_batch_size=2,
            seed=3,
            replay_seed=4,
            device="cpu",
            protocol_id="checkpoint-test",
            vocabulary_id="v8",
        )
    )
    trainer.step(0, 1, source_id="train:checkpoint")
    checkpoint = trainer.save_checkpoint(tmp_path / "checkpoint")
    bundle = torch.load(checkpoint / "model.pt", weights_only=False)
    bundle["model"]["embedding.weight"][0, 0] += 1.0
    torch.save(bundle, checkpoint / "model.pt")
    with pytest.raises(ValueError, match="parameter hash mismatch"):
        NN0Trainer.from_checkpoint(
            checkpoint, expected_protocol_id="checkpoint-test", expected_vocabulary_id="v8"
        )


def test_baseline_parity_on_identical_probe_items(corpus):
    baselines = train_baselines(corpus.vocabulary, corpus.training)
    assert {baseline.name for baseline in baselines} == {
        "uniform",
        "B0",
        "B1",
        "B2",
        "B3",
        "B4",
        "context_retrieval",
    }
    for baseline in baselines:
        assert set(baseline.score_items(corpus.probes)) == set(corpus.probe_ids)


def test_paired_statistics_and_failed_seed_policy():
    expected = tuple(range(1, 11))
    complete = [
        SeedContrast(seed, "composition", "B0", candidate_nll=1.0, baseline_nll=2.0)
        for seed in expected
    ]
    stats = compute_paired_statistics(complete, expected_seeds=expected)
    assert stats.complete is True
    assert stats.mean_paired_nll_difference == pytest.approx(1.0)
    assert stats.relative_nll_reduction == pytest.approx(0.5)
    assert stats.ci95 is not None
    assert stats.sign_permutation_p is not None
    incomplete = complete[:-1] + [
        SeedContrast(10, "composition", "B0", None, None, failed=True, failure_reason="diverged")
    ]
    blocked = compute_paired_statistics(incomplete, expected_seeds=expected)
    assert blocked.complete is False
    assert blocked.failed_seeds == (10,)
    assert blocked.mean_paired_nll_difference is None


def test_claim_firewall():
    assert validate_claim_class(ClaimClass.R4.value) is ClaimClass.R4
    with pytest.raises(ValueError):
        validate_claim_class("A1")


def test_protocol_hash_seed_store_and_seoi_detectors():
    root = Path.cwd()
    protocol = load_and_verify_protocol(root)
    digest = protocol_hash(protocol)
    tampered = dict(protocol)
    tampered["master_seeds"] = [1]
    with pytest.raises(ProtocolRefusal):
        verify_protocol_digest(tampered, digest)
    with pytest.raises(ProtocolRefusal):
        verify_master_seed_set(tampered)
    with pytest.raises(ProtocolRefusal):
        verify_protected_surface(root, "0" * 64)
    with pytest.raises(ProtocolRefusal):
        require_decisive_allowed(protocol)
    assert PROTOCOL_PATH.exists()


def test_dry_run_is_reproducible_without_decisive_execution():
    root = Path.cwd()
    a = run_dry_run(root, seed=0)
    b = run_dry_run(root, seed=0)
    assert a["run_mode"] == "NON_DECISIVE_DRY_RUN"
    assert a["decisive_experiment_executed"] is False
    assert a["artifact_sha256"] == b["artifact_sha256"]


def test_cuda_adapter_execution_when_available(corpus):
    if not torch.cuda.is_available():
        pytest.skip("CUDA not available")
    adapter = make_adapter(corpus, seed=4, device="cuda")
    adapter.learn(corpus.training[0])
    scores = adapter.evaluate(corpus.probes[:1])
    assert all(math.isfinite(value) for value in scores.values())
    assert adapter.device.type == "cuda"
