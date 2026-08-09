"""The twelve scientific requirements for the repaired P1-LN-DEC experiment.

Each test maps to exactly one numbered requirement from the repair transaction,
so a failure names the scientific property that broke rather than the line that
raised.  Nothing here runs the decisive experiment: the learner tests use tiny
synthetic token sequences, and the benchmark tests use the corpus generator plus
the non-neural ladder.  NN-0 is never trained on the DEC-2 stream in this file.

R1  BPTT spans more than one timestep
R2  recurrent weights receive gradient from a multi-step path
R3  replay preserves sequence context and the online objective
R4  the KV query depends on the evaluation context
R5  candidate and baseline exposure are equal
R6  the symbolic baseline cannot exploit answer metadata
R7  train/test compositional separation
R8  symbol relabelling does not change difficulty
R9  no probe leakage
R10 the protocol is deterministic and provenance is honest
R11 checkpoint continuation is exact
R12 evaluation does not mutate state
"""

from __future__ import annotations

import dataclasses
import math
from pathlib import Path

import pytest
import torch
import torch.nn.functional as F

from p1.live.neural.experiments.ln_dec.baselines2 import (
    DECISION_COMPARATORS,
    SOLVED_NLL,
    exposure_units,
    fit_ladder,
    ladder_accuracy,
    ladder_report,
)
from p1.live.neural.experiments.ln_dec.benchmark2 import (
    CONTROL_FAMILIES2,
    DECISIVE_FAMILIES2,
    DIAGNOSTIC_FAMILIES2,
    N_BODY,
    build_chain_corpus,
    relabel_body,
    uniform_nll,
)
from p1.live.neural.experiments.ln_dec.protocol import (
    ProtocolRefusal,
    load_and_verify_protocol,
    protocol_hash,
    require_decisive_allowed,
    source_state,
)
from p1.live.neural.nn0.nucleus import (
    NN0Config,
    NN0Trainer,
    SequenceReplay,
    SequenceReplayEntry,
)

ROOT = Path(__file__).resolve().parents[2]
SEEDS = (0, 1, 2, 3, 4)

# Four distinct input tokens plus a distinct target, so "which token received
# gradient" has an unambiguous answer.
SYNTHETIC = (9, 6, 7, 2, 4)
WARM_EPISODES = ((9, 6, 7, 2, 4), (9, 7, 6, 3, 1), (9, 8, 6, 5, 0))


def sequence_trainer(*, window: int = 4, seed: int = 0) -> NN0Trainer:
    return NN0Trainer(
        NN0Config(
            vocab_size=10,
            d_embed=16,
            d_hidden=32,
            d_read=16,
            kv_capacity=128,
            kv_top_k=4,
            replay_capacity=128,
            replay_batch_size=4,
            replay_every=1,
            seed=seed,
            replay_seed=seed + 1000,
            device="cpu",
            protocol_id="test-repair1",
            vocabulary_id="test-vocab",
            training_mode="sequence",
            bptt_window=window,
        )
    )


def warm(trainer: NN0Trainer) -> NN0Trainer:
    """Populate KV and replay from three synthetic episodes."""
    for tokens in WARM_EPISODES:
        trainer.step_sequence(tokens, source_id=f"warm:{tokens}", reset=True)
    return trainer


@pytest.fixture(scope="module")
def corpora():
    return {seed: build_chain_corpus(seed) for seed in SEEDS}


@pytest.fixture(scope="module")
def protocol():
    return load_and_verify_protocol(ROOT)


# --------------------------------------------------------------------------- R1


@pytest.mark.parametrize("window", [1, 2, 3, 4])
def test_r1_credit_assignment_horizon_is_exactly_the_window(window):
    """The final prediction's gradient reaches exactly the last ``window`` inputs.

    This states the BPTT claim as an equality rather than an inequality: at
    ``window == 1`` only the immediately preceding token is reachable, which is
    the legacy horizon the repair replaced.
    """
    trainer = sequence_trainer(window=window)
    inputs, target = SYNTHETIC[:-1], SYNTHETIC[-1]
    chunk = inputs[-window:] + (target,)

    trainer.optim.zero_grad(set_to_none=True)
    xs = torch.tensor([chunk[:-1]], dtype=torch.long)
    ys = torch.tensor([chunk[1:]], dtype=torch.long)
    logits, _, _ = trainer.model.forward_memory(xs, trainer._zero_h(1), None)
    F.cross_entropy(logits[0, -1:], ys[0, -1:]).backward()

    grad = trainer.model.embedding.weight.grad
    reached = {token for token in inputs if float(grad[token].norm()) > 0.0}
    assert reached == set(inputs[-window:]), (window, sorted(reached))


def test_r1_truncation_boundary_is_explicit():
    """Chunk count is exactly ``ceil(transitions / window)``, not an accident."""
    for window, expected in ((1, 4), (2, 2), (3, 2), (4, 1)):
        trainer = sequence_trainer(window=window)
        stats = trainer.step_sequence(SYNTHETIC, source_id="r1b", reset=True)
        assert expected == math.ceil((len(SYNTHETIC) - 1) / window)
        assert int(stats["chunks"]) == expected, (window, stats["chunks"])


def test_r1_transition_mode_cannot_widen_its_window():
    with pytest.raises(ValueError):
        NN0Config(training_mode="transition", bptt_window=4)


# --------------------------------------------------------------------------- R2


def test_r2_recurrent_weights_receive_multistep_gradient():
    """``weight_hh`` is only reachable when the loss looks back past one token."""
    trainer = sequence_trainer(window=4)
    xs = torch.tensor([SYNTHETIC[:-1]], dtype=torch.long)
    ys = torch.tensor([SYNTHETIC[1:]], dtype=torch.long)
    trainer.optim.zero_grad(set_to_none=True)
    logits, _, _ = trainer.model.forward_memory(xs, trainer._zero_h(1), None)
    F.cross_entropy(logits[0, -1:], ys[0, -1:]).backward()
    assert float(trainer.model.gru.weight_hh_l0.grad.norm()) > 0.0


def test_r2_single_timestep_leaves_the_recurrent_weights_dead():
    trainer = sequence_trainer(window=1)
    trainer.optim.zero_grad(set_to_none=True)
    logits, _, _ = trainer.model.forward_memory(torch.tensor([[2]]), trainer._zero_h(1), None)
    F.cross_entropy(logits[0], torch.tensor([4])).backward()
    assert float(trainer.model.gru.weight_hh_l0.grad.norm()) == 0.0


def test_r2_step_sequence_actually_moves_the_recurrent_weights():
    trainer = sequence_trainer(window=4)
    before = trainer.model.gru.weight_hh_l0.detach().clone()
    trainer.step_sequence(SYNTHETIC, source_id="r2c", reset=True)
    assert float((trainer.model.gru.weight_hh_l0.detach() - before).abs().max()) > 0.0


def test_r2_hidden_state_is_detached_only_at_the_boundary():
    trainer = sequence_trainer(window=4)
    trainer.step_sequence(SYNTHETIC, source_id="r2d", reset=True)
    assert trainer.last_h is not None
    assert trainer.last_h.is_leaf and not trainer.last_h.requires_grad


# --------------------------------------------------------------------------- R3


def test_r3_replay_unit_is_a_sequence_not_a_transition():
    trainer = warm(sequence_trainer(window=4))
    assert isinstance(trainer.replay, SequenceReplay)
    assert len(trainer.replay) == len(WARM_EPISODES)
    assert {row[0] for row in trainer.replay.digest_rows()} == set(WARM_EPISODES)


def test_r3_replay_objective_equals_the_online_objective():
    """Replaying one sequence reproduces the online loss on that sequence."""
    trainer = sequence_trainer(window=4)
    trainer.step_sequence(SYNTHETIC, source_id="r3b", reset=True)
    entry = trainer.replay.items[0]

    with torch.no_grad():
        replayed = float(trainer._replay_sequence_loss([entry]))
        xs = torch.tensor([SYNTHETIC[:-1]], dtype=torch.long)
        ys = torch.tensor([SYNTHETIC[1:]], dtype=torch.long)
        logits, _, _ = trainer.model.forward_memory(xs, trainer._zero_h(1), trainer._reader)
        online = float(F.cross_entropy(logits.squeeze(0), ys.squeeze(0)))
    assert replayed == pytest.approx(online, abs=1e-6)


def test_r3_replay_is_not_a_bigram_objective():
    """Permuting a replayed sequence changes its loss, so order is scored."""
    trainer = sequence_trainer(window=4)
    trainer.step_sequence(SYNTHETIC, source_id="r3c", reset=True)
    entry = trainer.replay.items[0]
    shuffled = SequenceReplayEntry((9, 7, 6, 2, 4), entry.err, "r3c-shuffled")
    with torch.no_grad():
        ordered = float(trainer._replay_sequence_loss([entry]))
        permuted = float(trainer._replay_sequence_loss([shuffled]))
    assert ordered != pytest.approx(permuted, abs=1e-9)


def test_r3_mixed_length_replay_masks_its_padding():
    """A short row must be scored on its own positions only, never on padding."""
    trainer = sequence_trainer(window=4)
    trainer.step_sequence((9, 6, 7, 2, 4), source_id="r3d:long", reset=True)
    trainer.step_sequence((9, 6, 3), source_id="r3d:short", reset=True)
    rows = trainer.replay.items
    assert len(rows) == 2

    with torch.no_grad():
        batched = float(trainer._replay_sequence_loss(rows))
        alone = [float(trainer._replay_sequence_loss([row])) for row in rows]
    widths = [len(row.tokens) - 1 for row in rows]
    expected = sum(w * v for w, v in zip(widths, alone)) / sum(widths)
    assert batched == pytest.approx(expected, abs=1e-6)


# --------------------------------------------------------------------------- R4


def test_r4_kv_query_depends_on_the_evaluation_context():
    trainer = warm(sequence_trainer(window=4))
    assert len(trainer.memory) > 0

    contexts = [(9, 6, 7, 2), (9, 7, 6, 3), (9, 8, 6, 5), (9, 6, 8, 1)]
    queries, reads = [], []
    with torch.no_grad():
        for context in contexts:
            xs = torch.tensor([context], dtype=torch.long)
            _, _, queried = trainer.model.forward_memory(xs, trainer._zero_h(1), trainer._reader)
            query = trainer.model.project_key(queried[-1])
            read = trainer.memory.read(query, trainer.cfg.kv_top_k, trainer.device)
            queries.append(tuple(round(v, 9) for v in query.flatten().tolist()))
            reads.append(tuple(round(v, 9) for v in read.flatten().tolist()))

    assert len(set(queries)) == len(contexts), "distinct contexts collapsed to one query"
    assert len(set(reads)) == len(contexts), "distinct queries collapsed to one read"
    assert all(any(v != 0.0 for v in q) for q in queries), "query is the zero vector"


def test_r4_external_memory_is_not_inert():
    """Toggling the store changes the prediction, so the read is actually used."""
    trainer = warm(sequence_trainer(window=4))
    context = (9, 6, 7, 2)
    with_memory = trainer.predict_context(context, use_external_memory=True).tolist()
    without = trainer.predict_context(context, use_external_memory=False).tolist()
    assert max(abs(a - b) for a, b in zip(with_memory, without)) > 1e-6


def test_r4_key_and_query_are_the_same_projection_of_the_same_state():
    """The store is keyed by ``project_key(h_{t-1})``, which is what is queried."""
    trainer = sequence_trainer(window=4)
    trainer.step_sequence(SYNTHETIC, source_id="r4c", reset=True)
    with torch.no_grad():
        xs = torch.tensor([SYNTHETIC[:-1]], dtype=torch.long)
        _, _, queried = trainer.model.forward_memory(xs, trainer._zero_h(1), None)
        first_key = trainer.model.project_key(queried[0]).flatten()
    assert torch.allclose(trainer.memory.keys[0], first_key, atol=1e-6)


def test_r4_read_reflects_writes_that_land_after_an_earlier_read():
    """The store caches its stacked keys; a later write must invalidate it.

    A stale cache would silently make the memory read ignore everything written
    after the first read -- the store would look context-dependent while being
    frozen at its first few rows.
    """
    trainer = sequence_trainer(window=4)
    memory, query = trainer.memory, torch.ones(1, trainer.cfg.d_read)

    memory.write(torch.randn(1, trainer.cfg.d_read), torch.zeros(1, trainer.cfg.d_embed), 0, 1.0)
    before = memory.read(query, trainer.cfg.kv_top_k, trainer.device).clone()

    memory.write(query.clone(), torch.full((1, trainer.cfg.d_embed), 7.0), 1, 1.0)
    after = memory.read(query, trainer.cfg.kv_top_k, trainer.device)

    assert not torch.allclose(before, after), "write after read did not reach the reader"
    assert float(after.max()) > 0.0

    memory.clear()
    assert memory.read(query, trainer.cfg.kv_top_k, trainer.device) is None


# --------------------------------------------------------------------------- R5


def test_r5_candidate_and_baseline_exposure_are_equal(corpora):
    """Both are fitted from the identical ordered stream of transitions."""
    for seed, corpus in corpora.items():
        stream = corpus.stream()
        units = exposure_units(stream)
        assert units == corpus.exposure(), seed
        assert units["episodes"] == len(corpus.training), seed
        # One NN-0 gradient position per transition; one fitted transition per
        # transition.  The unit is the same object on both sides.
        assert units["transitions"] == sum(len(seq) - 1 for seq in stream), seed

        models = fit_ladder(corpus.vocabulary.size, stream, N_BODY)
        assert len(models) == 9, seed
        # Every member really consumed this stream: halving it moves the ladder.
        half = fit_ladder(corpus.vocabulary.size, stream[: len(stream) // 2], N_BODY)
        items = [(p.context, p.target) for p in corpus.heldout_probes()]
        full, part = ladder_report(models, items), ladder_report(half, items)
        assert any(full[name] != part[name] for name in DECISION_COMPARATORS), seed


def test_r5_exposure_unit_is_recorded_in_the_protocol(protocol):
    assert protocol["training_exposure"]["exposure_unit"] == (
        "one token transition in the ordered training stream"
    )
    learner = protocol["dec2_preregistration"]["learner"]
    assert learner["training_mode"] == "sequence"
    assert learner["bptt_window"] == 4
    assert learner["frozen"] is True


def test_r5_the_frozen_window_spans_a_whole_dec2_episode(corpora):
    """A window of 4 never truncates inside a DEC-2 episode."""
    for seed, corpus in corpora.items():
        transitions = {len(seq) - 1 for seq in corpus.stream()}
        assert max(transitions) <= 4, (seed, sorted(transitions))


# --------------------------------------------------------------------------- R6


def test_r6_the_vocabulary_carries_no_answer_bearing_metadata(corpora):
    """No mode, rule-identifier, separator, or metadata token exists to parse."""
    expected = {"body_tokens", "rule_tokens", "start", "size", "vocabulary_id"}
    for seed, corpus in corpora.items():
        fields = {f.name for f in dataclasses.fields(corpus.vocabulary)}
        assert fields == expected, (seed, sorted(fields))
        assert corpus.vocabulary.size == 10, seed
        assert {t for seq in corpus.stream() for t in seq} <= set(range(10)), seed
        for probe in corpus.probes:
            assert probe.target not in probe.context, (seed, probe.probe_id)


def test_r6_shortcut_parses_are_wrong_and_the_ladder_fails(corpora):
    """B5b must fail; every decision comparator must stay above the threshold."""
    for seed, corpus in corpora.items():
        models = fit_ladder(corpus.vocabulary.size, corpus.stream(), N_BODY)
        items = [(p.context, p.target) for p in corpus.decisive_probes()]
        report = ladder_report(models, items)

        assert ladder_accuracy(models, items)["B5b"] == 0.0, seed
        for name in DECISION_COMPARATORS:
            assert report[name] > SOLVED_NLL, (seed, name, report[name])
        # B6 cannot fall below ln(3): closure is vacuous on an unseen marker run
        # and at most three of six body symbols are excludable.
        assert report["B6"] >= math.log(3.0) - 1e-9, (seed, report["B6"])
        assert corpus.assert_cheap_baselines_fail() == report, seed


def test_r6_the_symbolic_ceiling_is_reported_not_compared(corpora):
    """B5a solves it, which is the point: the task is achievable, not magic."""
    assert "B5a" not in DECISION_COMPARATORS
    assert "B5b" not in DECISION_COMPARATORS
    for seed, corpus in corpora.items():
        models = fit_ladder(corpus.vocabulary.size, corpus.stream(), N_BODY)
        items = [(p.context, p.target) for p in corpus.decisive_probes()]
        assert ladder_accuracy(models, items)["B5a"] == 1.0, seed


def test_r6_composition_order_is_identifiable_from_the_stream(corpora):
    """A reversed-order learner is falsified by training, not merely by probes."""
    for seed, corpus in corpora.items():
        falsifying = sum(
            1
            for e in corpus.training
            if e.family == "composition"
            and corpus.reference.chain(tuple(e.metadata["pair"]), int(e.context[-1]))
            != corpus.reference.chain(tuple(reversed(e.metadata["pair"])), int(e.context[-1]))
        )
        assert falsifying > 0, seed
        assert corpus.order_insensitive_fraction() < 1.0, seed


# --------------------------------------------------------------------------- R7


def test_r7_no_decisive_pair_or_marker_run_was_ever_trained(corpora):
    for seed, corpus in corpora.items():
        seen_pairs = {
            tuple(e.metadata["pair"]) for e in corpus.training if e.family == "composition"
        }
        seen_runs = {e.context[1:-1] for e in corpus.training}
        for probe in corpus.probes_for("pair_holdout"):
            assert tuple(probe.metadata["pair"]) not in seen_pairs, (seed, probe.probe_id)
            assert probe.context[1:-1] not in seen_runs, (seed, probe.probe_id)


def test_r7_every_marker_is_still_learnable_in_both_positions(corpora):
    """Separation must withhold the composition, not starve a marker."""
    for seed, corpus in corpora.items():
        pairs = [tuple(e.metadata["pair"]) for e in corpus.training if e.family == "composition"]
        markers = {int(e.metadata["marker"]) for e in corpus.training if e.family == "component"}
        assert {p[0] for p in pairs} == markers, seed
        assert {p[1] for p in pairs} == markers, seed


def test_r7_decisive_and_diagnostic_families_are_separated(protocol):
    assert DECISIVE_FAMILIES2 == ("pair_holdout",)
    assert DIAGNOSTIC_FAMILIES2 == ("value_holdout",)
    assert not set(DECISIVE_FAMILIES2) & set(CONTROL_FAMILIES2)
    prereg = protocol["dec2_preregistration"]
    assert prereg["decisive_families"] == list(DECISIVE_FAMILIES2)
    assert prereg["diagnostic_families"] == list(DIAGNOSTIC_FAMILIES2)
    assert prereg["comparator"]["members"] == list(DECISION_COMPARATORS)


def test_r7_value_holdout_is_demoted_because_closure_alone_solves_it(corpora):
    """The stated reason for the demotion is measured, not asserted."""
    for seed, corpus in corpora.items():
        models = fit_ladder(corpus.vocabulary.size, corpus.stream(), N_BODY)
        diagnostic = ladder_report(
            models, [(p.context, p.target) for p in corpus.probes_for("value_holdout")]
        )["B6"]
        decisive = ladder_report(models, [(p.context, p.target) for p in corpus.decisive_probes()])[
            "B6"
        ]
        assert diagnostic < SOLVED_NLL, (seed, diagnostic)
        assert decisive > SOLVED_NLL, (seed, decisive)


# --------------------------------------------------------------------------- R8


def _body_shift(corpus):
    body = list(corpus.vocabulary.body_tokens)
    return {t: body[(i + 1) % len(body)] for i, t in enumerate(body)}


def test_r8_symbol_relabelling_leaves_the_ladder_invariant(corpora):
    """Difficulty is a property of the structure, not of the symbol names."""
    for seed, corpus in corpora.items():
        stream, probes = relabel_body(corpus, _body_shift(corpus))
        before = ladder_report(
            fit_ladder(corpus.vocabulary.size, corpus.stream(), N_BODY),
            [(p.context, p.target) for p in corpus.decisive_probes()],
        )
        after = ladder_report(fit_ladder(corpus.vocabulary.size, stream, N_BODY), list(probes))
        for name in before:
            assert before[name] == pytest.approx(after[name], abs=1e-9), (seed, name)


def test_r8_relabelling_really_changes_the_symbols(corpora):
    corpus = corpora[0]
    stream, probes = relabel_body(corpus, _body_shift(corpus))
    assert stream != corpus.stream()
    assert list(probes) != [(p.context, p.target) for p in corpus.decisive_probes()]
    # Markers and START are untouched: only the body alphabet is permuted.
    assert {t for seq in stream for t in seq if t >= N_BODY} == {
        t for seq in corpus.stream() for t in seq if t >= N_BODY
    }


def test_r8_relabelling_must_be_a_bijection_on_the_body(corpora):
    with pytest.raises(ValueError):
        relabel_body(corpora[0], {0: 1, 1: 0})


# --------------------------------------------------------------------------- R9


def test_r9_no_heldout_answer_or_context_appears_in_training(corpora):
    for seed, corpus in corpora.items():
        sequences = [e.sequence() for e in corpus.training]
        prefixes = {seq[:i] for seq in sequences for i in range(1, len(seq) + 1)}
        for probe in corpus.heldout_probes():
            needle = probe.sequence()
            width = len(needle)
            for seq in sequences:
                windows = [seq[i : i + width] for i in range(len(seq) - width + 1)]
                assert needle not in windows, (seed, probe.probe_id)
            assert probe.context not in prefixes, (seed, probe.probe_id)


def test_r9_the_candidate_view_carries_no_probe_content(corpora):
    for seed, corpus in corpora.items():
        view = corpus.candidate_view()
        assert {f.name for f in dataclasses.fields(view)} == {
            "vocabulary",
            "training",
            "manifest",
        }, seed
        # The manifest names probe *sources* so they can be blacklisted; it must
        # never carry a context or a target.
        assert all(isinstance(pid, str) for pid in view.manifest.probe_ids), seed
        assert not set(corpus.training_ids) & set(corpus.probe_ids), seed


def test_r9_controls_are_memorisable_by_construction(corpora):
    """The positive controls sit outside the decisive gate on purpose."""
    for seed, corpus in corpora.items():
        models = fit_ladder(corpus.vocabulary.size, corpus.stream(), N_BODY)
        items = [(p.context, p.target) for p in corpus.probes if p.family in CONTROL_FAMILIES2]
        assert ladder_accuracy(models, items)["B0"] == 1.0, seed


# -------------------------------------------------------------------------- R10


def test_r10_the_corpus_is_reproducible(corpora):
    for seed, corpus in corpora.items():
        rebuilt = build_chain_corpus(seed)
        assert rebuilt.fingerprint() == corpus.fingerprint(), seed
        assert rebuilt.stream() == corpus.stream(), seed


def test_r10_corpus_content_does_not_depend_on_non_corpus_substreams():
    """Changing the replay or model-init seed must not move the data."""
    base = build_chain_corpus(3)
    shifted = build_chain_corpus(3, seed_overrides={"replay": 1, "model_init": 2})
    assert shifted.stream() == base.stream()
    assert [p.as_dict() for p in shifted.probes] == [p.as_dict() for p in base.probes]
    # The fingerprint still moves, because it commits the whole seed record.
    assert shifted.fingerprint() != base.fingerprint()


def test_r10_protocol_hash_is_stable(protocol):
    assert protocol_hash(protocol) == protocol_hash(load_and_verify_protocol(ROOT))


def test_r10_decisive_execution_is_still_refused(protocol):
    """SESOI is now CLOSED, so provenance is the only thing still refusing."""
    assert protocol["SESOI"]["status"] == "CLOSED"
    assert protocol["SESOI"]["value"] == pytest.approx(math.log(3.0) - math.log(2.0))
    with pytest.raises(ProtocolRefusal, match="source state"):
        require_decisive_allowed(protocol, ROOT)


def test_r10_decisive_gate_cannot_be_bypassed_by_omitting_root():
    """``require_decisive_allowed(protocol)`` must not authorise on its own.

    While SESOI was OPEN the rootless call refused on SESOI before it ever
    reached provenance. Closing SESOI removed that backstop, so the rootless
    path has to check the source state itself or it becomes a way to authorise
    a decisive run against unverified code.
    """
    protocol = load_and_verify_protocol(ROOT)
    with pytest.raises(ProtocolRefusal, match="source state"):
        require_decisive_allowed(protocol)


def test_r10_sesoi_is_closed_with_a_derivation_and_a_consumed_seed_range(protocol):
    """A frozen SESOI has to carry its provenance, not just a number."""
    sesoi = protocol["SESOI"]
    assert sesoi["status"] == "CLOSED" and sesoi["value"] is not None
    assert sesoi["structural_floor"]["expression"] == "log(3) - log(2)"

    null = sesoi["empirical_null"]
    assert null["n"] == 20 and null["positive_seeds"] == 0
    assert null["seeds"] == "100-119"
    assert null["binding"] is False, "a negative null p95 must not be sold as binding"
    assert null["effect_p95"] < 0.0
    assert sesoi["value"] == pytest.approx(math.log(3.0) - math.log(2.0))

    partition = sesoi["seed_partition"]
    assert "200-209" in partition and "untouched" in partition["200-209"]
    assert set(partition) == {"0-4", "100-119", "200-209"}, "seed ranges must not overlap"


def test_r10_provenance_reports_the_actual_source_state():
    state = source_state(ROOT)
    assert set(state) >= {"head", "clean", "files", "divergent_files"}
    assert state["head_describes_implementation"] is (not state["divergent_files"])
    assert state["clean"] is (not state["divergent_files"])
    for path, entry in state["files"].items():
        assert entry["status"] in {"clean", "modified", "untracked_at_head", "missing"}
        if entry["status"] == "clean":
            assert entry["head_blob"] == entry["worktree_blob"], path
        assert (path in state["divergent_files"]) == (entry["status"] != "clean"), path


# -------------------------------------------------------------------------- R11


def test_r11_checkpoint_continuation_is_exact():
    """Resuming from a snapshot reproduces the uninterrupted run bit for bit."""
    reference = sequence_trainer(window=4, seed=5)
    for tokens in WARM_EPISODES:
        reference.step_sequence(tokens, source_id=f"r11:{tokens}", reset=True)
    expected = reference.predict_context((9, 6, 7, 2)).tolist()

    early = sequence_trainer(window=4, seed=5)
    early.step_sequence(WARM_EPISODES[0], source_id=f"r11:{WARM_EPISODES[0]}", reset=True)
    snapshot = early.state_dict()

    resumed = sequence_trainer(window=4, seed=99)
    resumed.load_state_dict(snapshot)
    for tokens in WARM_EPISODES[1:]:
        resumed.step_sequence(tokens, source_id=f"r11:{tokens}", reset=True)

    assert resumed.step_count == reference.step_count
    assert len(resumed.memory) == len(reference.memory)
    assert resumed.replay.digest_rows() == reference.replay.digest_rows()
    assert resumed.predict_context((9, 6, 7, 2)).tolist() == pytest.approx(expected, abs=1e-9)


# -------------------------------------------------------------------------- R12


def test_r12_evaluation_does_not_mutate_state():
    trainer = warm(sequence_trainer(window=4))
    memory, replay = len(trainer.memory), len(trainer.replay)
    steps, mode = trainer.step_count, trainer.model.training
    last_h = trainer.last_h.clone()
    params = [p.detach().clone() for p in trainer.model.parameters()]

    for context in ((9, 6, 7, 2), (9, 8, 6, 5), (9, 7, 8, 0)):
        trainer.predict_context(context, use_external_memory=True)
        trainer.predict_context(context, use_external_memory=False)

    assert len(trainer.memory) == memory
    assert len(trainer.replay) == replay
    assert trainer.step_count == steps
    assert trainer.model.training is mode
    assert torch.equal(trainer.last_h, last_h)
    for old, new in zip(params, trainer.model.parameters()):
        assert torch.equal(old, new.detach())


def test_r12_a_blacklisted_probe_source_can_never_be_trained_on():
    trainer = sequence_trainer(window=4)
    trainer.set_source_blacklist({"probe:blocked"})
    with pytest.raises(AssertionError):
        trainer.step_sequence(SYNTHETIC, source_id="probe:blocked", reset=True)
    assert len(trainer.memory) == 0
    assert len(trainer.replay) == 0


def test_r12_uniform_reference_is_the_declared_chance_rate(corpora):
    for seed, corpus in corpora.items():
        assert uniform_nll(corpus) == pytest.approx(
            math.log(corpus.vocabulary.size), abs=1e-12
        ), seed
