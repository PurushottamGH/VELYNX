"""Probe builders: renaming, permutation, composition, anti-memorisation.

Three families of held-out instrument (per architecture §2.2 and the
P1-LN-DEC decisive experiment):

1. **relabel / symbol-renaming** — apply a deterministic bijection of the
   alphabet to a train plot. If the image alphabet is *disjoint* from the
   training alphabet, an exact string/n-gram lookup over the training corpus
   cannot match it: none of its tokens ever appears in training. If the
   relabel is *within-alphabet* (a non-trivial permutation), the probe tests
   whether a model learns roles rather than raw symbols.

2. **composition** — the held-out pair continuation (from
   :class:`CompositionWorld`); a two-step ``(a,b)->c`` probe also tests
   multi-rule composition end-to-end.

3. **anti-memorisation** — a "hard-positive" control: a probe that an exact
   lookup *can* answer (it shares a full context with a training plot), used
   to show the exact-lookup baseline is not vacuous while the true holdouts
   are unsolvable.
"""

from __future__ import annotations

from typing import List, Sequence, Tuple

from p1.live.neural.playgarden.alphabet import Permutation
from p1.live.neural.playgarden.worlds import CompositionWorld, Probe


def renaming_probes(
    world: CompositionWorld,
    sigma: Permutation,
) -> List[Probe]:
    """Relabel every held-out composition probe of ``world`` under ``sigma``.

    Returns one probe per held-out pair, mapping both the context and the
    expected continuation by ``sigma``. The relabeled context's token set and
    the world's training token set are disjoint *when* the probe is built with
    a sigma whose image lies in a disjoint ``alpha_target`` (asserted by the
    leakage tests in :mod:`verification`).
    """
    out: List[Probe] = []
    for p in world.probes:
        ctx = sigma.apply(p.context)
        exp = sigma.apply(p.expected)
        out.append(
            Probe(
                "relabel",
                ctx,
                exp,
                train_out_of_corpus=True,
                metadata={
                    "base_kind": p.kind,
                    "pair": p.metadata.get("pair"),
                    "sigma_seed": sigma.seed,
                },
            )
        )
    return out


def disjoint_relabel_probes(world: CompositionWorld, seed: int) -> List[Probe]:
    """Relabel every held-out probe onto a *disjoint* alphabet.

    A fresh target alphabet (kind ``rl``, seeded ``seed``) is generated that
    is disjoint from the world's training tokens, and a deterministic
    bijection from the probe token set onto it is applied. Every relabeled
    token is out-of-vocabulary, so an exact n-gram lookup has literally no
    memory of any symbol used — the strongest possible symbol-renaming probe.
    """
    from p1.live.neural.playgarden.alphabet import disjoint_alpha

    src_tokens = sorted({t for p in world.probes for t in p.context + p.expected})
    target = disjoint_alpha(seed, "rel", len(src_tokens), avoid=tuple(world.train_tokens))
    mapping = dict(zip(src_tokens, target))
    out: List[Probe] = []
    for p in world.probes:
        ctx = tuple(mapping[t] for t in p.context)
        exp = tuple(mapping[t] for t in p.expected)
        out.append(
            Probe(
                "relabel",
                ctx,
                exp,
                train_out_of_corpus=True,
                metadata={
                    "base_kind": p.kind,
                    "pair": p.metadata.get("pair"),
                    "disjoint": True,
                    "relabel_seed": seed,
                },
            )
        )
    return out


def within_alphabet_permutation_probes(
    world: CompositionWorld,
    sigma: Permutation,
) -> List[Probe]:
    """Permutation probe within the *training alphabet*.

    Same map as :func:`renaming_probes` but the target pool is the training
    alphabet itself, using a provably non-identity permutation (the caller
    guarantees it via ``Permutation.non_identity``). These probes are
    retrievable only if a model has abstracted the rule rather than the raw
    symbol; a lookup keyed on raw symbols fails because role tokens were
    scrambled.
    """
    out: List[Probe] = []
    for p in world.probes:
        ctx = sigma.apply(p.context)
        exp = sigma.apply(p.expected)
        out.append(
            Probe(
                "permute",
                ctx,
                exp,
                train_out_of_corpus=True,
                metadata={
                    "pair": p.metadata.get("pair"),
                    "sigma_seed": sigma.seed,
                },
            )
        )
    return out


def two_step_composition_probe(
    world: CompositionWorld, i: int, j: int, k: int
) -> Probe:
    """A two-step composition probe: plot(i) then plot(j) then plot(k).

    Context is ``plot_a(i) + plot_b(j)``; the expected continuation is
    ``plot_b(k)``. The caller is responsible for choosing a triple that the
    training stream never emitted (holdout by construction).
    """
    # Both rule selectors are observable query components.  The final selector
    # identifies the intended continuation, so the context remains one-target.
    query_j = f"query_{world.seed}_{j}"
    query_k = f"query_{world.seed}_{k}"
    ctx = world.query_context(i, j) + world.plot_b(j).tokens + (query_k,)
    exp = world.plot_b(k).tokens
    return Probe(
        "composition",
        ctx,
        exp,
        train_out_of_corpus=True,
        metadata={"triple": (i, j, k)},
    )


def anti_memorisation_control(world: CompositionWorld) -> List[Probe]:
    """Hard-positive control: a probe the exact-lookup baseline *can* answer.

    Re-uses the first *train* pair of the world: the repaired observable query
    context and expected continuation appear verbatim in the training stream
    (followed by SEP). The exact-lookup baseline must retrieve it (its top
    candidate must equal the expected first token), which proves the baseline
    is not vacuous while the true composition holdouts remain unsolvable.
    """
    (i, j) = world.train_pairs[0]
    ctx = world.query_context(i, j)
    exp = world.plot_b(j).tokens
    return [
        Probe(
            "anti_memorisation_control",
            ctx,
            exp,
            train_out_of_corpus=False,  # intentionally present in the corpus
            metadata={"pair": (i, j), "control": True},
        )
    ]


def rename_pool(world: CompositionWorld, seed: int) -> Permutation:
    """Build a permutation over the *full* train+probe alphabet of a world.

    Deterministic from ``seed``; guaranteed non-identity. The image alphabet
    is the world's own tokens, which is what a within-alphabet role scramble
    needs.
    """
    tokens: List[str] = []
    seen: set = set()
    for p in world.probes:
        for t in p.context + p.expected:
            if t not in seen:
                seen.add(t)
                tokens.append(t)
    for t in world.train_tokens:
        if t not in seen and t != "SEP":
            seen.add(t)
            tokens.append(t)
    if len(tokens) < 2:
        raise ValueError("rename_pool needs >= 2 distinct tokens")
    return Permutation(seed ^ 0xABCD, tuple(tokens))


def two_step_probe(
    world: CompositionWorld, i: int, j: int, k: int
) -> Probe:
    """Alias of :func:`two_step_composition_probe`."""
    return two_step_composition_probe(world, i, j, k)


__all__ = [
    "anti_memorisation_control",
    "disjoint_relabel_probes",
    "rename_pool",
    "renaming_probes",
    "two_step_composition_probe",
    "two_step_probe",
    "within_alphabet_permutation_probes",
]
