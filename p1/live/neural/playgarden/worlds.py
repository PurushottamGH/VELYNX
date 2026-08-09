"""Deterministic symbolic world generators with by-construction holdout.

Each world is a data generator object with three surfaces:

- ``alphabet``   the seeded token pool (women anonymised per seed);
- ``train_stream`` a tuple of plots emitted during the *train* condition
  (never the probe items);
- ``probes``  a tuple of probe items that reference plots the train stream
  never emitted (composition pairs held out by construction, or held-out
  lengths).

By *construction* we mean: the holdout is not a random split of one big
sample. The worlds here partition a structural parameter space (pair set,
length bound, relation distance, alphabet) *before* generating, so no random
pick ever selects a test item into the train slice. This is the property the
leakage tests in :mod:`verification` assert.

Separators
----------
Streams are concatenations of plots with a reserved ``SEP`` token (kind
``sep``). The separator is part of the emitted token stream, so an n-gram
model trained on the train locale can in principle *predict* SEP after any
plot end — it can never predict a composition- continuation that the train
stream never showed. Both properties are what the probes rely on.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from p1.live.neural.playgarden import rules
from p1.live.neural.playgarden.alphabet import Alphabet, Permutation

SEP = "SEP"


def _query_token(seed: int, index: int) -> str:
    """Observable target-selector token used by identifiable compositions."""
    return f"query_{seed}_{index}"


@dataclass(frozen=True)
class Probe:
    """One held-out item.

    ``kind``: ``composition`` | ``length`` | ``relation`` | ``relabel`` |
    ``permute`` | ``memory_zero``
    ``context``: the token p-you see before the gap.
    ``expected``: the ideal continuation (a tuple or a token).
    ``train_out_of_corpus``: whether the item depends on structure never
    present in the train stream (set by the world generator).
    """

    kind: str
    context: Tuple[str, ...]
    expected: Tuple[str, ...]
    train_out_of_corpus: bool
    metadata: Dict[str, object] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "kind": self.kind,
            "context": list(self.context),
            "expected": list(self.expected),
            "train_out_of_corpus": self.train_out_of_corpus,
            "metadata": self.metadata,
        }


class SequenceWorld:
    """Sequence/pattern world (S0–S3): repetition, mirror, bounce.

    Train: for each symbol in the pool, repeat/mirror/bounce at lengths
    ``len_train``. Probe: the *same rule and symbol* at a length never
    emitted in training — an exact-string lookup cannot retrieve it because
    the specific long pattern is not present, yet the rule is reusable.
    """

    def __init__(
        self,
        seed: int,
        n_symbols: int = 6,
        len_train: Tuple[int, int] = (2, 4),
        len_probe: Tuple[int, int] = (10, 16),
        rule: str = "bounce",
    ) -> None:
        self.seed = seed
        self.rule = rule
        self.n_symbols = n_symbols
        self.len_train = len_train
        self.len_probe = len_probe
        self.alpha = Alphabet(seed)
        self.a_len_train_min, self.a_len_train_max = len_train
        self.p_len_min, self.p_len_max = len_probe
        self._build()

    def _build(self) -> None:
        lo, hi = self.len_train
        rng_seed = self.seed
        train_tokens: List[str] = []
        self.probes: List[Probe] = []
        for i in range(self.n_symbols):
            a = self.alpha.symbol("a", i)
            b = self.alpha.symbol("b", i)
            for n in range(lo, hi + 1):
                # deterministic lengths: emit each train length once
                if self.rule == "bounce":
                    plot = rules.bounce(self.seed, self.alpha, a, b, n)
                elif self.rule == "repeat":
                    plot = rules.repeat(self.seed, self.alpha, n, a)
                elif self.rule == "mirror":
                    w = tuple(self.alpha.pool("m", n))
                    plot = rules.mirror(self.seed, self.alpha, w)
                else:
                    raise ValueError(f"unknown rule {self.rule}")
                train_tokens.extend(plot.tokens)
                train_tokens.append(SEP)
        for i in range(self.n_symbols):
            a = self.alpha.symbol("a", i)
            b = self.alpha.symbol("b", i)
            for n in range(self.p_len_min, self.p_len_max + 1):
                if self.rule == "bounce":
                    plot = self.bounce(self.seed, self.alpha, a, b, n)
                else:
                    plot = rules.repeat(self.seed, self.alpha, n, a)
                self.probes.append(
                    Probe(
                        "length",
                        plot.tokens[:-1],
                        plot.tokens[-1:],
                        train_out_of_corpus=True,
                        metadata={"symbol": i, "length": n, "rule": self.rule},
                    )
                )
        self.train_tokens: Tuple[str, ...] = tuple(train_tokens)

    # -- stateless helpers (exposed for tests to recompute plots) -----------
    @staticmethod
    def bounce(seed: int, alpha: Alphabet, a: str, b: str, n: int) -> rules.Plot:
        return rules.bounce(seed, alpha, a, b, n)


class CompositionWorld:
    """Composition world: single A/B plots in train; held-out A∘B pairs probe.

    Structure:
      - ``n_a`` A-side symbols, ``n_b`` B-side symbols
      - each symbol emits a per-ruleplot (repeat block) at a fixed length
      - *train* streams emit every single plot, plus compositions for all
        pairs in ``train_pairs``;
      - the probe contains every pair in ``holdout_pairs``, exactly the pairs
        never emitted in train. For each held-out pair ``(a*,b*)`` the probe
        context is the observable query context for ``(a*,b*)`` and the
        expected continuation is plate(b*).

    Airtight property (asserted by leaking tests): the continuation string
    plate(b*) (and in particular its first token) *never* follows plate(a*)
    in the train stream, because plate(a*)+SEP is the only training emission
    ending at plate(a*). An exact-context lookup trained on the corpus
    predicts SEP (or a different symbol) and therefore cannot answer it.
    """

    def __init__(
        self,
        seed: int,
        n_a: int = 4,
        n_b: int = 4,
        block_len: int = 3,
        holdout_pairs: Optional[Sequence[Tuple[int, int]]] = None,
        holdout_frac: float = 0.4,
        rule_a: str = "repeat",
        rule_b: str = "repeat",
    ) -> None:
        self.seed = seed
        self.n_a = n_a
        self.n_b = n_b
        self.block_len = block_len
        self.alpha = Alphabet(seed=seed, kinds=("a", "b"), sizes=(n_a, n_b))
        self.rule_a, self.rule_b = rule_a, rule_b
        self._pairs = [(i, j) for i in range(n_a) for j in range(n_b)]
        if holdout_pairs is not None:
            self.holdout_pairs: Tuple[Tuple[int, int], ...] = tuple(holdout_pairs)
            train_pairs = [p for p in self._pairs if p not in self.holdout_pairs]
            if len(train_pairs) < 1:
                raise ValueError("holdout_pairs must leave at least one train pair")
        else:
            # by construction: deterministic holdout subset, never a random split
            n_hold = max(1, int(len(self._pairs) * holdout_frac))
            h = self._pairs[:: (len(self._pairs) // n_hold) or 1]
            self.holdout_pairs = tuple(h[:n_hold])
            train_pairs = [p for p in self._pairs if p not in self.holdout_pairs]
        self.train_pairs: Tuple[Tuple[int, int], ...] = tuple(train_pairs)
        self._build()

    def plot_a(self, i: int) -> rules.Plot:
        a = self.alpha.symbol("a", i)
        if self.rule_a == "repeat":
            return rules.repeat(self.seed, self.alpha, self.block_len, a)
        if self.rule_a == "bounce":
            b = self.alpha.symbol("b", 0)
            return rules.bounce(self.seed, self.alpha, a, b, self.block_len)
        raise ValueError(self.rule_a)

    def plot_b(self, j: int) -> rules.Plot:
        b = self.alpha.symbol("b", j)
        return rules.repeat(self.seed, self.alpha, self.block_len, b)

    def query_context(self, i: int, j: int) -> Tuple[str, ...]:
        """Observable selector followed by an ``i``-specific query tail.

        The selector identifies ``j`` but is separated from the prediction
        point by three ``i``-specific bridge tokens.  This keeps the target
        identifiable while ensuring the cheap order-1..3 lookup controls do
        not receive the answer as their final local transition.
        """
        bridge = f"bridge_{self.seed}_{i}"
        return self.plot_a(i).tokens + (_query_token(self.seed, j),) + (bridge,) * 3

    def _build(self) -> None:
        train_tokens: List[str] = []
        for i in range(self.n_a):
            train_tokens.extend(self.plot_a(i).tokens)
            train_tokens.append(SEP)
        for j in range(self.n_b):
            train_tokens.extend(self.plot_b(j).tokens)
            train_tokens.append(SEP)
        # Each composition is emitted twice so that, for any train pair, the
        # corpus continuation distribution of plot(i) is *dominated* by
        # first-token-of-plot(j). This is what makes the anti-memorisation
        # control retrievable deterministically by the exact-lookup baseline,
        # while held-out pairs remain unretrievable (they are never emitted).
        for _ in range(2):
            for (i, j) in self.train_pairs:
                train_tokens.extend(self.query_context(i, j))
                train_tokens.extend(self.plot_b(j).tokens)
                train_tokens.append(SEP)
        self.train_tokens = tuple(train_tokens)

        self.probes: List[Probe] = []
        for (i, j) in self.holdout_pairs:
            ctx = self.query_context(i, j)
            exp = self.plot_b(j).tokens
            self.probes.append(
                Probe(
                    "composition",
                    ctx,
                    exp,
                    train_out_of_corpus=True,
                    metadata={"pair": (i, j), "first_of_b": exp[0]},
                )
            )

    @property
    def alpha(self) -> Alphabet:
        return self._alpha

    @alpha.setter
    def alpha(self, value: Alphabet) -> None:
        self._alpha = value


class RelationWorld:
    """Relation/transitivity world.

    Defines a total order on symbol pairs: ``rank()`` per symbol (a pure
    function of seed). Training emits all pairs ``(x,y)`` with
    ``rank(y) == rank(x)+1`` (adjacent) plus, sometimes, distance d=2 —
    but *never* the distance actually used for probes. Probes are pairs with
    ``rank(y) == rank(x)+d_probe`` where ``d_probe > d_train``; the exact
    string ``(x,y)`` never appears in the training relation-emitting stream,
    so an exact-lookup model cannot answer; answering requires composing
    the order across two relation links (transitivity).
    """

    def __init__(
        self,
        seed: int,
        n_nodes: int = 8,
        d_train: int = 1,
        d_probe: int = 2,
    ) -> None:
        self.seed = seed
        self.n_nodes = n_nodes
        self.d_train = d_train
        self.d_probe = d_probe
        self.alpha = Alphabet(seed=seed, kinds=("r",))
        self._build()

    def rank(self, i: int) -> int:
        """Deterministic seeded order for node i (a total order)."""
        return (self.seed + i * 17) % self.n_nodes

    def _build(self) -> None:
        # Nodes are tokens, ordered by rank.
        ordered = sorted(range(self.n_nodes), key=self.rank)
        self.ordered = ordered
        train_tokens: List[str] = []
        edges: List[Tuple[str, str]] = []
        for k in range(len(ordered) - self.d_train):
            lo, hi = ordered[k], ordered[k + self.d_train]
            x, y = self.alpha.symbol("r", lo), self.alpha.symbol("r", hi)
            edges.append((x, y))
            train_tokens.extend((x, y))
            train_tokens.append(SEP)
        self.train_edges = tuple(edges)
        self.train_tokens = tuple(train_tokens)

        self.probes: List[Probe] = []
        for k in range(len(ordered) - self.d_probe):
            lo, hi = ordered[k], ordered[k + self.d_probe]
            if (lo, hi) in self.train_pairs_src() or (hi, lo) in self.train_pairs_src():
                continue  # never probe an edge already trained
            x, y = self.alpha.symbol("r", lo), self.alpha.symbol("r", hi)
            self.probes.append(
                Probe(
                    "relation",
                    (x,),
                    (y,),
                    train_out_of_corpus=True,
                    metadata={"distance": self.d_probe, "rank_lo": self.rank(lo), "rank_hi": self.rank(hi), "raw_lo": lo, "raw_hi": hi},
                )
            )

    def train_pairs_src(self) -> set:
        return {(a, b) for a, b in self._train_src_plains()}

    def _train_src_plains(self):
        out = []
        for k in range(len(self.ordered) - self.d_train):
            out.append((self.ordered[k], self.ordered[k + self.d_train]))
        return out


__all__ = ["CompositionWorld", "Probe", "RelationWorld", "SEP", "SequenceWorld"]
