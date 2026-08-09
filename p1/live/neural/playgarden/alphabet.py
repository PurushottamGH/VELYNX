"""Deterministic anonymous symbols for the playgarden.

Symbols are plain strings drawn from a seeded generator. Per the architecture
spec (§2.2) "symbols are anonymous and syntactically re-drawn per seed — no
preloaded semantics, no symbol shortcut". Every pool is a pure function of its
seed, so any two runs with the same seed produce byte-identical symbols.

A permutation/renaming is a bijection ``sigma`` over a token pool. Applying it
to a *train* plot produces a *relabelled* plot whose tokens may (by design of
the probe) be either:

- **disjoint** from the training alphabet (a true out-of-vocabulary relabel
  that no memorised exact string can match), or
- a non-trivial permutation *within* the training alphabet (role-scramble).

Both are used as anti-memorisation probes in :mod:`probes`.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple


def _stream(seed: int) -> str:
    return f"p1-arc:{seed}"


def token(seed: int, index: int, kind: str = "t") -> str:
    """A single deterministic token.

    ``kind`` names the role (e.g. ``a``/``b``/``p``) and ``seed`` isolates
    pools; two different pools never collide even for the same index.
    """
    return f"{kind}_{'%03d' % index}_" + hashlib.sha256(_stream(seed).encode()).hexdigest()[:8]


@dataclass(frozen=True)
class Alphabet:
    """An ordered token pool for one world/seed.

    The pool is the deterministic objects: token(kind, seed, i) for i in a
    bounded range. ``size`` can be left open (infinite iterable) for
    generators that need arbitrarily many tokens.
    """

    seed: int
    kinds: Tuple[str, ...] = ("a", "b")
    sizes: Tuple[int, ...] = (0, 0)  # per-kind counts; 0 => unbounded
    memo: Dict[str, str] = field(default_factory=dict, compare=False)

    def symbol(self, kind: str, index: int) -> str:
        """Deterministic symbol for (kind, index). Cached for fast tests."""
        key = f"{kind}:{index}"
        hit = self.memo.get(key)
        if hit is None:
            hit = token(self.seed, index, kind)
            self.memo[key] = hit
        return hit

    def pool(self, kind: str, count: int) -> Tuple[str, ...]:
        return tuple(self.symbol(kind, i) for i in range(count))


@dataclass(frozen=True)
class Permutation:
    """A deterministic bijection over a pool. Pure and reproducible.

    ``forward`` maps each symbol to its image; ``inverse`` is derived so the
    permutation is exact. Generation uses the seed via a fixed LCG so no RNG
    module state is involved.
    """

    seed: int
    pool: Tuple[str, ...]
    forward: Dict[str, str] = field(default_factory=dict)
    inverse: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # An explicitly supplied map (e.g. a transposition) is used as-is;
        # otherwise the map is generated from the seed via a fixed LCG-based
        # Fisher-Yates shuffle, so no RNG module state is involved.
        if self.forward:
            if not self.inverse:
                object.__setattr__(self, "inverse", {v: k for k, v in self.forward.items()})
            return
        pool = self.pool
        n = len(pool)
        if n == 0:
            return
        # Deterministic shuffle of the index list
        idx = list(range(n))
        x = self.seed + (n << 16)
        for i in range(n - 1, 0, -1):
            x = (1103515245 * x + 12345) % (2**31)
            j = x % (i + 1)
            idx[i], idx[j] = idx[j], idx[i]
        fwd: Dict[str, str] = {}
        inv: Dict[str, str] = {}
        for i, j in enumerate(idx):
            fwd[pool[i]] = pool[j]
            inv[pool[j]] = pool[i]
        object.__setattr__(self, "forward", fwd)
        object.__setattr__(self, "inverse", inv)

    def apply(self, seq: Sequence[str]) -> Tuple[str, ...]:
        return tuple(self.forward.get(s, s) for s in seq)

    def is_identity(self) -> bool:
        return all(k == v for k, v in self.forward.items())

    def non_identity(self) -> "Permutation":
        """Return a provably non-identity sibling permutation.

        Always builds the adjacent transposition of the first two pool
        elements (never conditioned on the seeded map), so ``is_identity()``
        is False for any pool of size >= 2, it is an involution, and it is
        deterministic for a fixed pool. Used so a "rename" probe is never
        vacuously the identity.
        """
        pool = list(self.pool)
        if len(pool) < 2:
            # Degenerate pool: identity only — caller must not use a rename
            # probe on it. Raising here keeps the invariant explicit.
            return self
        fwd = {t: t for t in pool}
        fwd[pool[0]], fwd[pool[1]] = pool[1], pool[0]
        inv = {v: k for k, v in fwd.items()}
        return Permutation(self.seed ^ 0xA11C, tuple(pool), fwd, inv)


def disjoint_alpha(seed: int, kind: str, size: int, avoid: Sequence[str]) -> Tuple[str, ...]:
    """A pool of ``size`` tokens that are disjoint from ``avoid``.

    Guaranteed by construction: ``kind`` is namespaced per probe (a fresh
    kind string such as ``rw``/``x``/``h``), and no member equals any token in
    ``avoid``. This gives voice to a relabel whose alphabet shares *no*
    memory with training tokens, so looked-up strings cannot coincide.
    """
    out: List[str] = []
    i = 0
    seen: set = set(avoid)
    while len(out) < size:
        t = f"{kind}_{'%08x' % i}_" + hashlib.sha256(str(seed).encode()).hexdigest()[:8]
        if t not in seen:
            out.append(t)
            seen.add(t)
        i += 1
    return tuple(out)  # type: ignore[return-value]


__all__ = ["Alphabet", "Permutation", "disjoint_alpha", "token"]