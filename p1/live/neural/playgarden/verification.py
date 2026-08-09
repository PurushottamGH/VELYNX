"""Proofs: no train/test leakage and exact-lookup unsolvability.

Two independent proof instruments over a world's *train token stream*:

* ``prove_no_leakage`` — a probe leaks iff the exact token sequence
  ``context + (expected[0],)`` occurs as a contiguous n-gram anywhere in the
  training stream. For every constructed holdout this is impossible (held-out
  pair / beyond-max length / never-adjacent relation pair / out-of-vocabulary
  relabel), while the anti-memorisation control *does* occur in the corpus,
  proving the check can fire on both sides.

* ``prove_lookup_unsolvable`` — score every probe against the strongest naive
  exact retriever: an n-gram table (orders 1..``order_n``) over the whole
  training stream, answering with the most frequent continuation of the
  longest supported suffix of the context (ties broken by lexicographic
  order, fully deterministic). A probe is **unsolvable by exact lookup**
  exactly when this baseline does not emit the expected first token. If even
  this baseline fails, no substring/n-gram memorizer can solve the probe.

``relabel_token_disjoint`` additionally proves that relabel probes' token
sets are disjoint from the training vocabulary.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from p1.live.neural.playgarden.worlds import Probe


# --------------------------------------------------------------------------
# Exact n-gram lookup baseline (deterministic)
# --------------------------------------------------------------------------


@dataclass
class NGramLookup:
    """Exact context-continuation lookup over a corpus.

    Builds ``continuation_counts[context][token]`` for every context of
    length 1..``order_n`` appearing in the corpus (sliding windows over the
    raw token stream, SEP included). Prediction for a probe context uses the
    longest suffix of the context present in the table, then the most
    frequent continuation; ties are resolved by lexicographically smallest
    token, so the baseline is fully deterministic.
    """

    order_n: int = 3
    corpus: Tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        from collections import defaultdict

        c = self.corpus
        table: Dict[Tuple[str, ...], Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for l in range(1, self.order_n + 1):
            for i in range(len(c) - l):
                ctx = c[i : i + l]
                nxt = c[i + l]
                table[ctx][nxt] += 1
        self._table: Dict[Tuple[str, ...], Dict[str, int]] = dict(table)

    def score(self, context: Sequence[str], expected: Sequence[str] = ()) -> Dict[str, object]:
        """Score a context; return dict with coverage/top/correct_first/matched_len."""
        ctx = tuple(context)
        best_len = 0
        best_key: Optional[Tuple[str, ...]] = None
        for l in range(min(len(ctx), self.order_n), 0, -1):
            key = ctx[-l:]
            if key in self._table:
                best_len = l
                best_key = key
                break
        if best_key is None:
            return {
                "coverage": 0,
                "top": None,
                "correct_first": False,
                "matched_len": 0,
                "context_len": len(ctx),
            }
        counts = self._table[best_key]
        total = sum(counts.values())
        top = max(sorted(counts), key=counts.get)
        expected_first = expected[0] if expected else None
        return {
            "coverage": total,
            "top": top,
            "correct_first": expected_first is not None and top == expected_first,
            "matched_len": best_len,
            "context_len": len(ctx),
        }


# --------------------------------------------------------------------------
# Verdicts and reports
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ProbeVerdict:
    """One probe's results on both proofs."""

    probe: Probe
    out_of_corpus: bool
    unsolvable_by_lookup: bool
    coverage: float
    top: Optional[str]
    expected_first: Optional[str]
    disjoint: bool = False  # relabel probes only
    detail: str = ""


@dataclass(frozen=True)
class ProofReport:
    """Aggregate of both proofs for one world."""

    world_name: str
    seed: int
    n_train_tokens: int
    n_probes: int
    verdicts: Tuple[ProbeVerdict, ...] = field(default_factory=tuple)

    @property
    def all_out_of_corpus(self) -> bool:
        return all(v.out_of_corpus for v in self.verdicts)

    @property
    def all_unsolvable(self) -> bool:
        return all(v.unsolvable_by_lookup for v in self.verdicts)

    def summary(self) -> Dict[str, object]:
        return {
            "world_name": self.world_name,
            "seed": self.seed,
            "n_train_tokens": self.n_train_tokens,
            "n_probes": self.n_probes,
            "all_out_of_corpus": self.all_out_of_corpus,
            "all_unsolvable": self.all_unsolvable,
            "per_probe": [v.probe.as_dict() for v in self.verdicts],
        }


# --------------------------------------------------------------------------
# Proof helpers
# --------------------------------------------------------------------------


def contains(corpus: Sequence[str], seq: Sequence[str]) -> bool:
    """Exact contiguous occurrence of ``seq`` in ``corpus`` (empty seq: True)."""
    n = len(seq)
    if n == 0:
        return True
    c = tuple(corpus)
    s = tuple(seq)
    return any(c[i : i + n] == s for i in range(len(c) - n + 1))


def token_set(probe: Probe) -> set:
    return set(probe.context) | set(probe.expected)


def prove_no_leakage(corpus: Sequence[str], probe: Probe) -> bool:
    """True iff the probe is out of corpus (no train/test leakage).

    A probe leaks iff ``context + (expected[0],)`` occurs as a contiguous
    n-gram in the training stream — the exact key-value pair a memorizer
    would retrieve. The anti-memorisation control is the *positive* control:
    it occurs in the corpus and is therefore reported as ``False`` here.
    """
    seq = probe.context + ((probe.expected[0],) if probe.expected else ())
    return not contains(corpus, seq)


def assert_target_identifiability(
    probes: Sequence[Probe], *, stochastic: bool = False
) -> bool:
    """Executable invariant: one observable context has one target.

    A stochastic benchmark may opt in only if it supplies a complete target
    distribution; Playgarden's repaired deterministic probes do not opt in.
    """
    targets: Dict[Tuple[str, ...], set[Tuple[str, ...]]] = {}
    for probe in probes:
        targets.setdefault(probe.context, set()).add(probe.expected)
    ambiguous = {context: values for context, values in targets.items() if len(values) != 1}
    if ambiguous and not stochastic:
        raise AssertionError(f"ambiguous deterministic probe context(s): {ambiguous!r}")
    return not ambiguous


def relabel_token_disjoint(probes: Sequence[Probe], train_tokens: Sequence[str]) -> List[bool]:
    """Per-probe proof that relabel tokens are disjoint from the train vocabulary."""
    vocab = set(train_tokens)
    return [token_set(p).isdisjoint(vocab) for p in probes]


def prove_lookup_unsolvable(
    corpus: Sequence[str],
    probes: Sequence[Probe],
    order_n: int = 3,
) -> List[ProbeVerdict]:
    """Score each probe against the exact n-gram lookup baseline."""
    lookup = NGramLookup(order_n=order_n, corpus=tuple(corpus))
    verdicts: List[ProbeVerdict] = []
    for p in probes:
        res = lookup.score(p.context, p.expected)
        verdicts.append(
            ProbeVerdict(
                probe=p,
                out_of_corpus=prove_no_leakage(corpus, p),
                unsolvable_by_lookup=not bool(res["correct_first"]),
                coverage=float(res["coverage"]),
                top=res["top"],  # type: ignore[arg-type]
                expected_first=p.expected[0] if p.expected else None,
                disjoint=bool(p.metadata.get("disjoint", False)),
                detail=f"matched_len={res['matched_len']} coverage={res['coverage']}",
            )
        )
    return verdicts


def build_report(
    world_name: str,
    seed: int,
    train_tokens: Sequence[str],
    verdicts: Sequence[ProbeVerdict],
) -> ProofReport:
    return ProofReport(world_name, seed, len(train_tokens), len(verdicts), tuple(verdicts))


__all__ = [
    "NGramLookup",
    "ProbeVerdict",
    "ProofReport",
    "build_report",
    "assert_target_identifiability",
    "contains",
    "prove_lookup_unsolvable",
    "prove_no_leakage",
    "relabel_token_disjoint",
    "token_set",
]
