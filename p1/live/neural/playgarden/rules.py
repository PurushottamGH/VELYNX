"""Primitive rule generators for the playgarden.

A *rule* is a deterministic function ``R(seed, alphabet, params) -> plot``
where a plot is a tuple of symbols. Rules are pure: the same seed, alphabet
and params give the same plot every time, so a rule can be emitted in a train
stream and re-emitted verbatim in a probe. No rule inspects any stored state.

Rules implemented here (architecture §2.2 list):

- ``repeat``     A^n
- ``mirror``     w + reverse(w)
- ``bounce``     ABABA… (alternation around a pivot)
- ``reverse``    transpose x -> f(x) (alphabet permutation)
- ``chaining``   concatenation of two sub-plots (composition seed)
- ``count``      numeric ramp, deterministic

Every rule returns a ``Plot`` (immutable) with a ``rule`` tag used by
composition probes to describe what was composed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Sequence, Tuple

from p1.live.neural.playgarden.alphabet import Alphabet, Permutation


@dataclass(frozen=True)
class Plot:
    """One emitted plot: an ordered tuple of symbols plus a rule tag."""

    rule: str
    tokens: Tuple[str, ...]

    def __len__(self) -> int:
        return len(self.tokens)

    def __getitem__(self, i: int) -> str:
        return self.tokens[i]


def repeat(seed: int, alpha: Alphabet, n: int, symbol: Optional[str] = None) -> Plot:
    s = symbol or alpha.symbol("a", 0)
    return Plot("repeat", (s,) * n)


def mirror(seed: int, alpha: Alphabet, word: Sequence[str]) -> Plot:
    w = tuple(word)
    return Plot("mirror", w + w[::-1])


def bounce(seed: int, alpha: Alphabet, a: str, b: str, n: int) -> Plot:
    """ABABA… with n symbols."""
    toks: Tuple[str, ...] = ()
    for i in range(n):
        toks += ((a if i % 2 == 0 else b),)
    return Plot("bounce", toks)


def reverse(seed: int, alpha: Alphabet, word: Sequence[str]) -> Plot:
    return Plot("reverse", tuple(word)[::-1])


def transpose(seed: int, alpha: Alphabet, word: Sequence[str], perm: Permutation) -> Plot:
    return Plot("transpose", perm.apply(word))


def chaining(seed: int, alpha: Alphabet, parts: Sequence[Plot]) -> Plot:
    toks: Tuple[str, ...] = ()
    tags: Tuple[str, ...] = ()
    for p in parts:
        toks += p.tokens
        tags += (p.rule,)
    return Plot("chaining:" + "+".join(tags), toks)


def count(seed: int, alpha: Alphabet, symbol: str, n: int) -> Plot:
    """Countdown/up ramp: s n times then s-1 … (symbols from alphabet pool)."""
    toks: Tuple[str, ...] = ()
    for k in range(n, 0, -1):
        toks += (alpha.symbol("c", k),)
    return Plot("count", toks)


#: Registry name -> factory, for generator composability and probe metadata.
RULE_FACTORIES: dict = {
    "repeat": repeat,
    "mirror": mirror,
    "bounce": bounce,
    "reverse": reverse,
    "transpose": transpose,
    "chaining": chaining,
    "count": count,
}

__all__ = [
    "Plot",
    "RULE_FACTORIES",
    "bounce",
    "chaining",
    "count",
    "mirror",
    "repeat",
    "reverse",
    "transpose",
]