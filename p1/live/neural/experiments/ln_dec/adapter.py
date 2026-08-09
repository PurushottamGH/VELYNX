"""Typed NN-0 adapter for the canonical benchmark."""

from __future__ import annotations

import hashlib
import json
import math
from contextlib import contextmanager
from typing import Any, Dict, Iterator, Mapping, Sequence, Tuple

import torch

from p1.live.neural.experiments.ln_dec.provenance import (
    EvaluationMutationError,
    ProvenanceViolation,
    SourceBlacklist,
)
from p1.live.neural.experiments.ln_dec.types import Experience, Probe, TokenVocabulary
from p1.live.neural.nn0.nucleus import NN0Config, NN0Trainer, _hash_state


class NN0Adapter:
    """Expose explicit train/eval and memory semantics around :class:`NN0Trainer`.

    Contract:

    * ``predict(context)`` is pure and returns a shared-vocabulary distribution.
    * ``score(prediction, target)`` is proper categorical NLL.
    * ``learn(experience)`` is the only parameter-update boundary.
    * ``reset_episode`` clears recurrent hidden state only.
    * ``clear_external_memory`` and ``clear_replay`` are independent operations.
    """

    ADAPTER_VERSION = 1

    def __init__(
        self,
        config: NN0Config,
        vocabulary: TokenVocabulary,
        *,
        probe_ids: Sequence[str] = (),
        training_ids: Sequence[str] = (),
    ) -> None:
        if config.vocab_size != vocabulary.size:
            raise ValueError(
                f"NN-0 vocab_size {config.vocab_size} does not match {vocabulary.size}"
            )
        self.vocabulary = vocabulary
        self.trainer = NN0Trainer(config)
        self.blacklist = SourceBlacklist.from_ids(probe_ids, training_ids)
        self.trainer.set_source_blacklist(set(self.blacklist.probe_ids))
        self._evaluating = False

    @property
    def device(self) -> torch.device:
        return self.trainer.device

    @property
    def model(self) -> torch.nn.Module:
        return self.trainer.model

    @property
    def memory_size(self) -> int:
        return len(self.trainer.memory)

    @property
    def replay_size(self) -> int:
        return len(self.trainer.replay)

    def predict(self, context: Tuple[int, ...]) -> list[float]:
        """Predict without changing hidden state, weights, KV, or replay."""
        self.vocabulary.validate(tuple(context))
        probs = self.trainer.predict_context(
            tuple(context), use_external_memory=self.trainer.memory is not None
        )
        return [float(value) for value in probs.tolist()]

    def score(self, prediction: Sequence[float] | torch.Tensor, target: int) -> float:
        """Proper categorical NLL over the adapter's shared vocabulary."""
        if target < 0 or target >= self.vocabulary.size:
            raise ValueError(f"target {target} outside vocabulary")
        if isinstance(prediction, torch.Tensor):
            probability = float(prediction.detach().cpu()[target].item())
        else:
            if len(prediction) != self.vocabulary.size:
                raise ValueError("prediction length does not match vocabulary")
            probability = float(prediction[target])
        return -math.log(max(probability, 1e-15))

    def learn(
        self,
        experience_or_context: Experience | Tuple[int, ...],
        target: int | None = None,
        weight: float = 1.0,
    ) -> None:
        """Learn one provenance-bearing experience or a legacy explicit pair."""
        if self._evaluating:
            raise EvaluationMutationError("evaluation cannot call learn()")
        if isinstance(experience_or_context, Experience):
            experience = experience_or_context
        else:
            if target is None:
                raise TypeError("target is required for a raw context")
            experience = Experience(
                experience_id="legacy-adapter-experience",
                source_id="legacy:adapter",
                episode_id="legacy-adapter-episode",
                context=tuple(experience_or_context),
                target=int(target),
                family="legacy",
            )
        self.vocabulary.validate(experience.context)
        self.vocabulary.validate((experience.target,))
        self.blacklist.assert_training(experience.source_id)
        if experience.episode_start:
            self.reset_episode()
        sequence = experience.sequence()
        if self.trainer.cfg.training_mode == "sequence":
            # One update over the whole experience, back-propagating across the
            # frozen BPTT window instead of one detached step per token.
            self.trainer.step_sequence(
                sequence,
                source_id=experience.source_id,
                weight=weight,
                reset=False,
            )
        else:
            for index in range(len(sequence) - 1):
                self.trainer.step(
                    sequence[index],
                    sequence[index + 1],
                    source_id=experience.source_id,
                    weight=weight,
                )
        self.blacklist.record_update(experience.source_id)
        # This assertion is deliberately executed after every update so a
        # future memory implementation cannot silently bypass the blacklist.
        self.blacklist.assert_no_probe_writes()

    def score_probe(self, probe: Probe) -> float:
        """Score one frozen probe without exposing its target to prediction."""
        self.blacklist.assert_probe(probe.source_id)
        prediction = self.predict(probe.context)
        return self.score(prediction, probe.target)

    def evaluate(self, probes: Sequence[Probe]) -> Dict[str, float]:
        """Frozen evaluation with a hard mutation guard."""
        before = self.state_digest()
        with self.evaluation_mode():
            result = {probe.probe_id: self.score_probe(probe) for probe in probes}
        after = self.state_digest()
        if before != after:
            raise EvaluationMutationError("evaluation mutated NN-0 state")
        return result

    @contextmanager
    def evaluation_mode(self) -> Iterator[None]:
        """Mark a scope in which any learning attempt is an error."""
        if self._evaluating:
            raise EvaluationMutationError("nested evaluation mode")
        self._evaluating = True
        self.trainer.evaluation_active = True
        try:
            yield
        finally:
            self.trainer.evaluation_active = False
            self._evaluating = False

    def reset_episode(self) -> None:
        """Reset recurrent hidden state; learned weights and stores survive."""
        self.trainer.reset_episode()

    def clear_external_memory(self) -> None:
        """N1 operation: wipe KV only, leaving weights, hidden state, and replay."""
        self.trainer.clear_external_memory()

    def clear_replay(self) -> None:
        """Clear replay only; learned weights and KV survive."""
        self.trainer.clear_replay()

    def state_dict(self) -> Dict[str, Any]:
        """Export adapter identity plus trainer state."""
        return {
            "adapter_version": self.ADAPTER_VERSION,
            "vocabulary_id": self.vocabulary.vocabulary_id,
            "protocol_id": self.trainer.cfg.protocol_id,
            "trainer": self.trainer.state_dict(),
        }

    def load_state_dict(self, state: Mapping[str, Any]) -> None:
        """Restore only a matching adapter identity."""
        if int(state.get("adapter_version", -1)) != self.ADAPTER_VERSION:
            raise ValueError("adapter version mismatch")
        if state.get("vocabulary_id") != self.vocabulary.vocabulary_id:
            raise ValueError("adapter vocabulary identity mismatch")
        if state.get("protocol_id", "") != self.trainer.cfg.protocol_id:
            raise ValueError("adapter protocol identity mismatch")
        self.trainer.load_state_dict(dict(state["trainer"]))

    def state_digest(self) -> str:
        """Digest weights, recurrent state, KV, and replay for immutability tests."""
        digest = hashlib.sha256()

        def add(label: str, value: bytes) -> None:
            digest.update(label.encode("utf-8"))
            digest.update(len(value).to_bytes(8, "big"))
            digest.update(value)

        for name, tensor in sorted(self.trainer.model.state_dict().items()):
            add(name, tensor.detach().cpu().contiguous().numpy().tobytes())
        if self.trainer.last_h is None:
            add("last_h", b"none")
        else:
            add("last_h", self.trainer.last_h.detach().cpu().contiguous().numpy().tobytes())
        for index, (key, value) in enumerate(zip(self.trainer.memory.keys, self.trainer.memory.values)):
            add(f"kv-key-{index}", key.contiguous().numpy().tobytes())
            add(f"kv-value-{index}", value.contiguous().numpy().tobytes())
        add("kv-outcomes", json.dumps(self.trainer.memory.outcomes).encode("utf-8"))
        add("kv-errors", json.dumps(self.trainer.memory.errors).encode("utf-8"))
        add("kv-sources", json.dumps(self.trainer.memory.source_ids).encode("utf-8"))
        add(
            "replay-items",
            json.dumps(
                [list(row) for row in self.trainer.replay.digest_rows()],
                sort_keys=True,
            ).encode("utf-8"),
        )
        add("replay-rng", repr(self.trainer.replay._rng.bit_generator.state).encode("utf-8"))
        return digest.hexdigest()

    def parameter_hash(self) -> str:
        return _hash_state(self.trainer.model.state_dict())


__all__ = ["EvaluationMutationError", "NN0Adapter", "ProvenanceViolation"]
