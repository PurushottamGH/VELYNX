"""
VELYNX — Top-Down Attention Modulator.

Wraps Euclidean distance with a LatentCause-driven weight vector,
physically warping cluster space so the attended dimension dominates
proximity.  Proves "Understanding changes Perception."

Standard library only.  Drop-in compatible with vector_prediction_core.
"""

import math
from typing import Callable, Optional


# ── Latent Cause ──────────────────────────────────────────────────────

class LatentCause:
    """A discovered invariant — one dimension flagged as the critical driver.

    Attributes
    ----------
    index : int
        Which vector dimension (0-based) this cause controls.
    importance : float
        How predictive this dimension is relative to others.
        Higher → stronger attention pull during clustering.
    label : str, optional
        Human-readable name (e.g. "Sensor 2 / Temperature").
    """

    __slots__ = ("index", "importance", "label")

    def __init__(self, index: int, importance: float = 1.0,
                 label: Optional[str] = None):
        if index < 0:
            raise ValueError(f"index must be ≥ 0, got {index}")
        if importance <= 0:
            raise ValueError(f"importance must be > 0, got {importance}")
        self.index = index
        self.importance = importance
        self.label = label

    def __repr__(self) -> str:
        tag = f" [{self.label}]" if self.label else ""
        return (
            f"LatentCause(index={self.index}, "
            f"importance={self.importance:.2f}){tag}"
        )


# ── Weight Vector Construction ───────────────────────────────────────

def attention_weights(
    dim: int,
    cause: LatentCause,
    *,
    focus_mult: float = 10.0,
    suppress_floor: float = 0.05,
) -> list[float]:
    """Build a weight vector that amplifies the attended dimension.

    Parameters
    ----------
    dim : int
        Total number of dimensions (vector length).
    cause : LatentCause
        Which dimension to attend to.
    focus_mult : float
        How much to multiply the attended dimension's weight.
        Default 10.0 — a massive factor that warps cluster space.
    suppress_floor : float
        Residual weight for all *other* dimensions so they don't
        vanish entirely.  Default 0.05 (barely counts).

    Returns
    -------
    list[float]
        Weight vector of length *dim*, ready for weighted Euclidean.
    """
    w = [suppress_floor] * dim
    w[cause.index] = focus_mult * cause.importance
    return w


# ── Weighted Distance (the core warp) ─────────────────────────────────

def weighted_euclidean_distance(
    a: list[float],
    b: list[float],
    weights: list[float],
) -> float:
    """Weighted Euclidean distance where each dimension counts differently.

    ``sqrt(sum(w_i * (a_i - b_i)^2))``

    When one weight is 10× the others, that single dimension
    dominates the distance, forcing clusters to form around it.
    """
    s = 0.0
    for ai, bi, wi in zip(a, b, weights):
        d = ai - bi
        s += wi * d * d
    return math.sqrt(s)


# ── Attention Modulator (stateful wrapper) ────────────────────────────

class AttentionModulator:
    """Wraps a distance function with top-down attention from a LatentCause.

    Once ``focus()`` is called with a LatentCause, every distance
    calculation becomes attention-weighted — the engine sees a
    *warped* space where the discovered cause dominates.

    Call ``unfocus()`` to restore the raw metric.
    """

    def __init__(
        self,
        dim: int,
        base_distance: Callable[[list[float], list[float]], float],
        *,
        focus_mult: float = 10.0,
        suppress_floor: float = 0.05,
    ):
        """
        Parameters
        ----------
        dim : int
            Dimensionality of the vectors this modulator will process.
        base_distance : callable
            The raw distance function to wrap (typically
            ``vector_prediction_core.euclidean_distance``).
        focus_mult : float
            Amplification factor for the attended dimension.
        suppress_floor : float
            Residual weight for non-attended dimensions.
        """
        self.dim = dim
        self._base = base_distance
        self.focus_mult = focus_mult
        self.suppress_floor = suppress_floor
        self._active_cause: Optional[LatentCause] = None
        self._weights: Optional[list[float]] = None

    def focus(self, cause: LatentCause) -> None:
        """Lock attention onto a LatentCause.

        After this call, ``self.distance(a, b)`` returns the
        *weighted* Euclidean distance.
        """
        self._active_cause = cause
        self._weights = attention_weights(
            self.dim, cause,
            focus_mult=self.focus_mult,
            suppress_floor=self.suppress_floor,
        )

    def unfocus(self) -> None:
        """Release attention — restore raw distance."""
        self._active_cause = None
        self._weights = None

    def distance(self, a: list[float], b: list[float]) -> float:
        """Compute distance, applying active attention if set.

        Drop-in replacement for ``euclidean_distance(a, b)``.
        """
        if self._weights is not None:
            return weighted_euclidean_distance(a, b, self._weights)
        return self._base(a, b)

    def __call__(self, a: list[float], b: list[float]) -> float:
        """Alias so the modulator is itself a callable distance function."""
        return self.distance(a, b)

    @property
    def is_focused(self) -> bool:
        return self._active_cause is not None

    @property
    def active_cause(self) -> Optional[LatentCause]:
        return self._active_cause

    @property
    def weights(self) -> Optional[list[float]]:
        """Current weight vector, or None if unfocused."""
        if self._weights is None:
            return None
        return self._weights[:]

    def weight_profile(self) -> str:
        """Human-readable bar showing which dimension dominates."""
        if self._weights is None:
            return "(unfocused -- all dimensions equal)"
        bars = []
        for i, w in enumerate(self._weights):
            n = min(round(w * 4), 40)
            bar = "#" * n
            marker = " <<-- FOCUS" if (
                self._active_cause and i == self._active_cause.index
            ) else ""
            bars.append(f"  [{i}] w={w:<8.4f} {bar}{marker}")
        return "\n".join(bars)

    def __repr__(self) -> str:
        state = "FOCUSED" if self.is_focused else "unfocused"
        cause = f" on {self._active_cause}" if self._active_cause else ""
        return f"AttentionModulator(dim={self.dim}, {state}{cause})"


# ── Convenience Factory ───────────────────────────────────────────────

def make_modulator(
    dim: int,
    base_distance: Callable[[list[float], list[float]], float],
    cause: Optional[LatentCause] = None,
    *,
    focus_mult: float = 10.0,
    suppress_floor: float = 0.05,
) -> AttentionModulator:
    """Build and optionally pre-focus an AttentionModulator.

    Parameters
    ----------
    dim : int
        Vector dimensionality.
    base_distance : callable
        Raw distance function.
    cause : LatentCause, optional
        If provided, the modulator starts **focused** on this cause.
    focus_mult, suppress_floor
        Forwarded to :meth:`AttentionModulator.focus`.

    Returns
    -------
    AttentionModulator
    """
    mod = AttentionModulator(
        dim, base_distance,
        focus_mult=focus_mult,
        suppress_floor=suppress_floor,
    )
    if cause is not None:
        mod.focus(cause)
    return mod


# ── Integration: Patch Cluster.distance_to with the modulator ─────────

def patch_engine(engine, modulator: AttentionModulator) -> None:
    """Monkey-patch ``Cluster.distance_to`` so all clusters use the modulator.

    After this call, every proximity comparison in the engine runs
    through the modulator's weighted metric.  To restore, call
    :func:`unpatch_engine`.
    """
    from cognition.vector_prediction_core import Cluster as _Cluster

    if not hasattr(_Cluster, '_orig_distance_to'):
        _Cluster._orig_distance_to = _Cluster.distance_to

    def _attended(self, vector):
        return modulator.distance(self.centroid, vector)

    _Cluster.distance_to = _attended


def unpatch_engine(engine) -> None:
    """Restore the original ``Cluster.distance_to``."""
    from cognition.vector_prediction_core import Cluster as _Cluster

    if hasattr(_Cluster, '_orig_distance_to'):
        _Cluster.distance_to = _Cluster._orig_distance_to
        del _Cluster._orig_distance_to


# ── Demo ──────────────────────────────────────────────────────────────

def demo():
    """Compare cluster assignments with and without top-down attention.

    Same sensory stream, same proximity threshold.
    Attention warps the metric — the engine perceives different structure.
    """
    from cognition.vector_prediction_core import (
        VectorPredictionCore,
        euclidean_distance,
    )

    print("=" * 68)
    print("  VELYNX -- Attention Modulator Demo")
    print("  Top-Down Attention: Understanding changes Perception.")
    print("=" * 68)

    # ── Synthetic 4-D stream where only dim 2 carries signal ──────
    import random as _random
    rng = _random.Random(1)
    stream = []
    for t in range(40):
        vec = [
            0.5 + rng.gauss(0, 0.12),         # dim 0: noise
            0.5 + rng.gauss(0, 0.12),         # dim 1: noise
            0.5 + 0.40 * math.sin(t * 0.5),   # dim 2: THE signal
            0.5 + rng.gauss(0, 0.12),         # dim 3: noise
        ]
        stream.append([round(v, 4) for v in vec])

    dim = len(stream[0])

    # ── Phase 1: Run WITHOUT attention ─────────────────────────────
    print("\n─── Phase 1: Unmodulated (no attention) ───────────────────")
    core1 = VectorPredictionCore(
        proximity_threshold=0.20,
        auto_seed=True, max_clusters=20, history_depth=5,
    )
    for obs in stream:
        core1.ingest(obs)

    s1 = core1.summary
    print(f"  Clusters:  {s1['clusters']}")
    print(f"  Anomalies: {s1['anomalies']}")
    for cl in core1.cluster_engine.clusters:
        c = [round(x, 4) for x in cl.centroid]
        print(f"    Cluster({cl.id}, centroid={c}, count={cl.count})")

    # ── Phase 2: Inject the modulator, focused on Index 2 ──────────
    print("\n─── Phase 2: Modulated (attention on Index 2, 10×) ──────")
    cause = LatentCause(index=2, importance=1.0,
                        label="Sensor 2 / Signal")
    modulator = make_modulator(
        dim=dim,
        base_distance=euclidean_distance,
        cause=cause,
        focus_mult=10.0,
        suppress_floor=0.05,
    )
    print(f"  {cause}")
    print(f"  Weight vector: {[round(w, 4) for w in modulator.weights]}")
    print(f"  Weight profile:\n{modulator.weight_profile()}")

    # Patch and re-run
    patch_engine(None, modulator)

    core2 = VectorPredictionCore(
        proximity_threshold=0.20,
        auto_seed=True, max_clusters=20, history_depth=5,
    )
    for obs in stream:
        core2.ingest(obs)

    s2 = core2.summary
    print(f"\n  Clusters:  {s2['clusters']}")
    print(f"  Anomalies: {s2['anomalies']}")
    for cl in core2.cluster_engine.clusters:
        c = [round(x, 4) for x in cl.centroid]
        print(f"    Cluster({cl.id}, centroid={c}, count={cl.count})")

    # ── Compare ────────────────────────────────────────────────────
    print("\n─── Comparison ───────────────────────────────────────────")
    print(f"  Without attention: {s1['clusters']} clusters, "
          f"{s1['anomalies']} anomalies")
    print(f"  With attention:    {s2['clusters']} clusters, "
          f"{s2['anomalies']} anomalies")
    print()
    print("  Same sensory stream. Different cluster geometry.")
    print("  Understanding changes Perception.")

    unpatch_engine(None)
    print("\n  [OK] Demo complete.")


if __name__ == "__main__":
    demo()
