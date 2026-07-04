"""
research/evaluation/split.py
============================

Deterministic seed partitioning for held-out evaluation.

To measure *generalization* honestly, the held-out probe stream must share no
random-number lineage with the training stream — otherwise we are scoring the
model on data it effectively saw. This module derives a reproducible
**evaluation seed** from a training seed and provides a guard,
:func:`assert_disjoint`, that fails loudly if a training partition and an
evaluation partition would ever overlap.

The substrate's seed lineage
----------------------------
:class:`validation.datasets.EnvironmentDataset` seeds the *world* with ``seed``
and the *sensor bank* with ``seed + 1`` (see its ``reset``). A single run with
seed ``S`` therefore consumes the seed pair ``{S, S + 1}``. Disjointness is only
meaningful at the granularity of that pair, so :func:`seed_lineage` expands a
seed into exactly that set and :func:`assert_disjoint` compares lineages.

The partition
-------------
Evaluation seeds live in a high, well-separated band::

    probe_seed(train_seed, index) = EVAL_SEED_BASE
                                    + train_seed * EVAL_SEED_STRIDE
                                    + index

With :data:`EVAL_SEED_BASE` = 1,000,000 and :data:`EVAL_SEED_STRIDE` = 1,000,
every realistic training seed (and its ``+1`` sensor seed) maps to its own
1,000-wide block of evaluation seeds far above the training range, so training
and evaluation lineages cannot collide.

Standard library only.
"""

from __future__ import annotations

from typing import Iterable

#: Base offset of the held-out evaluation seed band. Training seeds are small
#: (typically ``1..N``); evaluation seeds start a million above them.
EVAL_SEED_BASE: int = 1_000_000

#: Width of the per-train-seed evaluation block. Each training seed owns
#: ``[BASE + seed*STRIDE, BASE + seed*STRIDE + STRIDE)`` so distinct training
#: seeds never share an evaluation seed (for ``index < STRIDE``).
EVAL_SEED_STRIDE: int = 1_000


def probe_seed(train_seed: int, index: int = 0) -> int:
    """Derive the held-out evaluation seed for a training seed.

    Parameters
    ----------
    train_seed :
        The seed the model was trained under.
    index :
        Optional offset within this training seed's evaluation block, for
        drawing multiple distinct held-out streams. Must satisfy
        ``0 <= index < EVAL_SEED_STRIDE`` so blocks never overlap.

    Returns
    -------
    int
        A reproducible evaluation seed in this training seed's dedicated block.

    Raises
    ------
    ValueError
        If ``train_seed`` is negative or ``index`` is outside
        ``[0, EVAL_SEED_STRIDE)``.
    """
    if train_seed < 0:
        raise ValueError(f"train_seed must be non-negative, got {train_seed}.")
    if not 0 <= index < EVAL_SEED_STRIDE:
        raise ValueError(
            f"index must be in [0, {EVAL_SEED_STRIDE}), got {index}."
        )
    return EVAL_SEED_BASE + train_seed * EVAL_SEED_STRIDE + index


def seed_lineage(seed: int) -> frozenset[int]:
    """Return every RNG seed a single run with ``seed`` consumes.

    Mirrors :class:`validation.datasets.EnvironmentDataset`, which seeds the
    world with ``seed`` and the sensor bank with ``seed + 1``.
    """
    return frozenset({seed, seed + 1})


def assert_disjoint(
    train_seeds: Iterable[int],
    eval_seeds: Iterable[int],
) -> None:
    """Assert that no training and evaluation seed lineages overlap.

    Each seed is expanded via :func:`seed_lineage` (``{seed, seed + 1}``) before
    comparison, matching the substrate's world/sensor seeding.

    Raises
    ------
    ValueError
        If any training lineage intersects any evaluation lineage, naming the
        offending raw seeds.
    """
    train_lineage: set[int] = set()
    for s in train_seeds:
        train_lineage |= seed_lineage(s)

    eval_lineage: set[int] = set()
    for s in eval_seeds:
        eval_lineage |= seed_lineage(s)

    overlap = train_lineage & eval_lineage
    if overlap:
        raise ValueError(
            "Training and evaluation seed lineages overlap on "
            f"{sorted(overlap)}; held-out evaluation would not be independent."
        )


__all__ = [
    "EVAL_SEED_BASE",
    "EVAL_SEED_STRIDE",
    "probe_seed",
    "seed_lineage",
    "assert_disjoint",
]
