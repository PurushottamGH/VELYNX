"""Reference-ceiling and candidate-achievability audits."""

from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

from p1.live.neural.experiments.ln_dec.benchmark import BenchmarkCorpus, DECISIVE_FAMILIES
from p1.live.neural.experiments.ln_dec.types import Probe


class ReferenceOracle:
    """Generator-aware reference ceiling, never passed to the candidate."""

    name = "Bref_reference_ceiling"

    def __init__(self, corpus: BenchmarkCorpus) -> None:
        self.corpus = corpus
        self.vocab_size = corpus.vocabulary.size
        self._answers = {probe.context: probe.target for probe in corpus.probes}

    def predict(self, context: Tuple[int, ...]) -> List[float]:
        target = self._answers.get(tuple(context))
        if target is None:
            return [1.0 / self.vocab_size] * self.vocab_size
        result = [0.0] * self.vocab_size
        result[target] = 1.0
        return result

    def score_items(self, probes: Sequence[Probe]) -> Dict[str, float]:
        # The proper-score floor is represented by a small numerical epsilon.
        import math

        return {
            probe.probe_id: -math.log(max(self.predict(probe.context)[probe.target], 1e-15))
            for probe in probes
        }


def audit_candidate_information(corpus: BenchmarkCorpus) -> Dict[str, object]:
    """Prove that decisive target information is observable in principle.

    The audit checks grounding and calibration without handing the generator's
    private mapping or atom table to the candidate.  It is deliberately a
    structural audit, not an observed NN result.
    """
    corpus.validate()
    observed_targets = {token for item in corpus.training for token in item.sequence()[1:]}
    decisive = [probe for probe in corpus.probes if probe.family in DECISIVE_FAMILIES]
    grounded = all(probe.target in observed_targets for probe in decisive)
    calibration_sources = {
        item.context[-1]: item.target
        for item in corpus.training
        if item.family == "calibration"
    }
    transfer_grounded = all(
        calibration_sources.get(int(probe.metadata["source_body_token"])) == probe.target
        for probe in corpus.probes_for("symbol_transfer")
    )
    return {
        "candidate_has_sufficient_observable_information": grounded and transfer_grounded,
        "all_decisive_targets_seen_in_training": grounded,
        "symbol_mapping_calibrated": transfer_grounded,
        "reference_is_private": True,
        "reference_semantics": "reference_ceiling_only",
    }


__all__ = ["ReferenceOracle", "audit_candidate_information"]

