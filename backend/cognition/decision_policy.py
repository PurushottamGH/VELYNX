"""
backend/cognition/decision_policy.py
=====================================

C8 — The Decision Policy.

The principled successor to the C8 *binary acceptance check*. Where the old
rule asked a single yes/no question ("did total prediction error go down?"),
the :class:`DecisionPolicy` judges a proposed memory restructuring against the
brain's full set of native cognitive vitals and decides whether the merge is
beneficial for the system's *global* stability.

The vitals (the "physics" of this cognitive universe)
------------------------------------------------------
Every vital below is **lower-is-better** — the same convention the validation
harness (:mod:`validation.metrics`) and the external :class:`RegressionGate`
already use:

    H -- Entropy        : conditional Shannon entropy of the cluster-transition
                          Markov chain (bits). Unpredictability of the dynamics.
    S -- Prediction Err : spatial surprise — how far observations land from the
                          nearest centroid the model would have predicted.
    A -- Active Load    : structural load — live clusters + the spatial volume
                          of the quarantined anomaly cloud.
    E -- Cognitive Energy (the headline Free-Energy proxy):

            E = (lambda * H) + (mu * S) + (nu * A)
              =        H      +   2 * S    + 0.5 * A      (default coefficients)

The coupling coefficients ``(lambda, mu, nu) = (1.0, 2.0, 0.5)`` are kept in
lock-step with :data:`validation.metrics.LAMBDA/MU/NU` so the merge-time
decision and the CI-time Freeze Rule speak the *same* energy units. They are
mirrored here (rather than imported) to keep this cognition module
standard-library only and free of any dependency on the validation harness —
the same import-light discipline the rest of the C8 pipeline follows.

Two selection strategies
-------------------------
* ``"free_energy"`` (default) — **Free Energy Minimization.** The merge is
  accepted iff the total Cognitive Energy after the replay is *less than or
  equal to* the energy before it. Equivalently, the signed improvement
  ``delta_energy = E_before - E_after`` must be ``>= 0``. A merge that lowers
  (or holds) global free energy is beneficial for the whole system even if it
  trades a little of one vital for a larger gain in another.

* ``"pareto"`` — **Strict Pareto Dominance.** A far more permissive guard: the
  merge is rejected *only* when it is strictly dominated — i.e. it makes **all
  four** vitals (H, S, A, E) worse simultaneously. Any merge that improves or
  holds even a single vital survives. Useful when you want to block only the
  unambiguously bad merges and let the downstream system sort out the rest.

Separation of concerns
-----------------------
This module decides *whether* a simulated restructuring should be committed,
using metric snapshots produced by a sandbox simulator (the
:class:`~backend.cognition.replay_engine.ReplayEngine`). It performs no
simulation and mutates no state. It is deliberately **independent of the
external** :class:`~validation.regression.RegressionGate`, which remains the CI
"compiler" check comparing whole-run baselines; the two never call each other.

Standard-library only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional

# ── Metric keys (the canonical vital names this policy reads) ─────────────────
PREDICTION_ERROR = "prediction_error"   # S — spatial surprise
ENTROPY = "entropy"                      # H — transition entropy (bits)
ACTIVE_LOAD = "active_load"              # A — clusters + anomaly volume
COGNITIVE_ENERGY = "cognitive_energy"    # E — derived free-energy proxy

# ── Coupling coefficients (mirror validation.metrics; lower-is-better) ────────
# E = lam*H + mu*S + nu*A. Kept identical to validation.metrics.{LAMBDA,MU,NU}
# so this merge-time policy and the CI-time RegressionGate measure energy in the
# same units, without importing the validation package.
# ALSO mirrored in cognitive_core.py (imported from cognitive_health→validation.metrics).
# If tuning these, update ALL THREE: validation/metrics.py, cognitive_core.py, and here.
DEFAULT_LAMBDA = 1.0   # weight on Entropy (H)
DEFAULT_MU = 2.0       # weight on Prediction Error / Surprise (S)
DEFAULT_NU = 0.5       # weight on Active Load (A)

# Selection strategies.
STRATEGY_FREE_ENERGY = "free_energy"
STRATEGY_PARETO = "pareto"

# The JSON/config key under which the energy coupling coefficients live, plus
# the per-coefficient sub-keys. Externalising the weights here makes them the
# single tunable knob for ablation studies / parameter sweeps.
CONFIG_KEY = "decision_policy"
CONFIG_LAMBDA = "lambda"
CONFIG_MU = "mu"
CONFIG_NU = "nu"


def resolve_coefficients(section: Optional[Mapping[str, Any]]) -> Dict[str, float]:
    """Resolve ``(lam, mu, nu)`` from a ``decision_policy`` config section.

    The energy coupling coefficients are no longer hard-coded at the call site:
    they are read from the experiment's environment config file under the
    ``decision_policy`` key, e.g.::

        {"decision_policy": {"lambda": 1.0, "mu": 2.0, "nu": 0.5}}

    Any missing coefficient falls back to its module default
    (:data:`DEFAULT_LAMBDA` / :data:`DEFAULT_MU` / :data:`DEFAULT_NU`), so a run
    with no ``decision_policy`` section behaves exactly as the historical
    ``(1.0, 2.0, 0.5)`` baseline.

    Parameters
    ----------
    section : Mapping or None
        The ``decision_policy`` sub-mapping itself (``{"lambda": ..., ...}``),
        **not** the whole config. ``None`` or an empty mapping yields the full
        default triple.

    Returns
    -------
    dict
        ``{"lam": float, "mu": float, "nu": float}`` — keyword-ready for the
        :class:`DecisionPolicy` constructor (``DecisionPolicy(**weights)``).
    """
    section = section or {}
    return {
        "lam": float(section.get(CONFIG_LAMBDA, DEFAULT_LAMBDA)),
        "mu": float(section.get(CONFIG_MU, DEFAULT_MU)),
        "nu": float(section.get(CONFIG_NU, DEFAULT_NU)),
    }


@dataclass
class DecisionScore:
    """A structured snapshot of the brain's vitals *before* and *after* a merge.

    This is the contract the :class:`~backend.cognition.replay_engine.ReplayEngine`
    produces and the :class:`DecisionPolicy` consumes. It carries **only data** —
    the two metric snapshots plus optional proposal metadata for tracing — and
    makes no judgement of its own. The accept/reject verdict is the
    :class:`DecisionPolicy`'s sole responsibility.

    Attributes
    ----------
    metrics_before : dict
        ``{prediction_error, entropy, active_load}`` measured against the live
        brain (the pre-merge world).
    metrics_after : dict
        The same vitals measured against the sandbox (the post-merge world).
    strategy, target_a, target_b, distance :
        Optional proposal metadata, echoed through purely so a trace can record
        *which* structural change these vitals describe.
    """

    metrics_before: Dict[str, float] = field(default_factory=dict)
    metrics_after: Dict[str, float] = field(default_factory=dict)
    strategy: Any = None
    target_a: Any = None
    target_b: Any = None
    distance: Any = None


class DecisionPolicy:
    """Judge a simulated merge against the brain's cognitive vitals.

    Parameters
    ----------
    strategy : str
        ``"free_energy"`` (default) for Free Energy Minimization, or
        ``"pareto"`` for the strict Pareto-dominance guard. See the module
        docstring for the semantics of each.
    lam, mu, nu : float
        The energy coupling coefficients in ``E = lam*H + mu*S + nu*A``.
        Default to ``(1.0, 2.0, 0.5)`` to match :mod:`validation.metrics`.
    tolerance : float
        Optional non-negative slack on the free-energy rule. The merge is
        accepted while ``delta_energy >= -tolerance`` (i.e. a regression no
        larger than ``tolerance`` energy units is still tolerated). Defaults to
        ``0.0`` — strict ``E_after <= E_before``.
    """

    def __init__(
        self,
        strategy: str = STRATEGY_FREE_ENERGY,
        lam: float = DEFAULT_LAMBDA,
        mu: float = DEFAULT_MU,
        nu: float = DEFAULT_NU,
        tolerance: float = 0.0,
    ) -> None:
        if strategy not in (STRATEGY_FREE_ENERGY, STRATEGY_PARETO):
            raise ValueError(
                f"unknown strategy {strategy!r}; expected "
                f"{STRATEGY_FREE_ENERGY!r} or {STRATEGY_PARETO!r}"
            )
        if tolerance < 0:
            raise ValueError(f"tolerance must be non-negative, got {tolerance!r}")
        self.strategy = strategy
        self.lam = float(lam)
        self.mu = float(mu)
        self.nu = float(nu)
        self.tolerance = float(tolerance)

    # -- public API --------------------------------------------------------

    def evaluate_metrics(
        self,
        metrics_before: Mapping[str, float],
        metrics_after: Mapping[str, float],
    ) -> Dict[str, Any]:
        """Score a merge from before/after vital snapshots and decide its fate.

        Computes the signed improvement (``before - after``; positive == the
        vital got *better*, since every vital is lower-is-better) for each of
        the four core metrics, then applies the configured selection strategy.

        Parameters
        ----------
        metrics_before, metrics_after : Mapping[str, float]
            Vital snapshots, each carrying at least ``prediction_error``,
            ``entropy`` and ``active_load``. ``cognitive_energy`` is derived
            from the three primitives if absent (and recomputed for
            consistency even if present).

        Returns
        -------
        dict
            A fully-itemised verdict::

                {
                    "accepted": bool,
                    "strategy": str,
                    "delta_prediction": float,   # ΔS  (before - after)
                    "delta_entropy": float,       # ΔH
                    "delta_load": float,          # ΔA
                    "delta_energy": float,        # ΔE
                    "energy_before": float,
                    "energy_after": float,
                    "prediction_before": float, "prediction_after": float,
                    "entropy_before": float,     "entropy_after": float,
                    "load_before": float,        "load_after": float,
                    "reason": str,                # explicit structural reason
                }
        """
        s_before = self._get(metrics_before, PREDICTION_ERROR)
        s_after = self._get(metrics_after, PREDICTION_ERROR)
        h_before = self._get(metrics_before, ENTROPY)
        h_after = self._get(metrics_after, ENTROPY)
        a_before = self._get(metrics_before, ACTIVE_LOAD)
        a_after = self._get(metrics_after, ACTIVE_LOAD)

        e_before = self._energy(h_before, s_before, a_before)
        e_after = self._energy(h_after, s_after, a_after)

        # Signed improvement: before - after. Positive ⇒ the vital improved
        # (got smaller); negative ⇒ the merge degraded that vital.
        delta_prediction = s_before - s_after
        delta_entropy = h_before - h_after
        delta_load = a_before - a_after
        delta_energy = e_before - e_after

        if self.strategy == STRATEGY_PARETO:
            accepted, reason = self._decide_pareto(
                delta_prediction, delta_entropy, delta_load, delta_energy
            )
        else:
            accepted, reason = self._decide_free_energy(
                delta_energy, e_before, e_after
            )

        return {
            "accepted": accepted,
            "strategy": self.strategy,
            "delta_prediction": delta_prediction,
            "delta_entropy": delta_entropy,
            "delta_load": delta_load,
            "delta_energy": delta_energy,
            "energy_before": e_before,
            "energy_after": e_after,
            "prediction_before": s_before,
            "prediction_after": s_after,
            "entropy_before": h_before,
            "entropy_after": h_after,
            "load_before": a_before,
            "load_after": a_after,
            "reason": reason,
        }

    def decide(self, score: DecisionScore) -> Dict[str, Any]:
        """Convenience: evaluate a :class:`DecisionScore` straight from the engine.

        Thin wrapper around :meth:`evaluate_metrics` that unpacks the score's
        ``metrics_before`` / ``metrics_after`` snapshots.
        """
        return self.evaluate_metrics(score.metrics_before, score.metrics_after)

    # -- strategies --------------------------------------------------------

    def _decide_free_energy(
        self,
        delta_energy: float,
        e_before: float,
        e_after: float,
    ) -> tuple[bool, str]:
        """Free Energy Minimization: accept iff total energy did not increase.

        ``delta_energy = E_before - E_after``. The merge is beneficial for the
        system's global stability when energy falls or holds, i.e.
        ``delta_energy >= -tolerance`` (strictly ``E_after <= E_before`` at the
        default zero tolerance).
        """
        accepted = delta_energy >= -self.tolerance
        if accepted:
            if delta_energy > 0:
                verdict = "free energy minimized"
            else:
                verdict = "free energy preserved (tie accepted)"
        else:
            verdict = "free energy increased"
        reason = (
            f"Free-energy {('accept' if accepted else 'reject')}: "
            f"{verdict}; ΔE={delta_energy:+.4f} "
            f"(E {e_before:.4f} → {e_after:.4f}, tol={self.tolerance:.4f})"
        )
        return accepted, reason

    def _decide_pareto(
        self,
        delta_prediction: float,
        delta_entropy: float,
        delta_load: float,
        delta_energy: float,
    ) -> tuple[bool, str]:
        """Strict Pareto Dominance: reject only if *all four* vitals worsened.

        A vital worsened when its signed improvement is strictly negative
        (its value went up). When every one of H, S, A and E worsened the merge
        is strictly dominated by the status quo and is rejected; otherwise it
        survives.
        """
        worse = {
            "prediction": delta_prediction < 0,
            "entropy": delta_entropy < 0,
            "load": delta_load < 0,
            "energy": delta_energy < 0,
        }
        dominated = all(worse.values())
        accepted = not dominated
        if dominated:
            reason = (
                "Pareto reject: merge strictly dominated — all four vitals "
                f"degraded (ΔS={delta_prediction:+.4f}, ΔH={delta_entropy:+.4f}, "
                f"ΔA={delta_load:+.4f}, ΔE={delta_energy:+.4f})"
            )
        else:
            improved = sorted(k for k, v in worse.items() if not v)
            reason = (
                "Pareto accept: not dominated — improved/held "
                f"{improved} (ΔS={delta_prediction:+.4f}, ΔH={delta_entropy:+.4f}, "
                f"ΔA={delta_load:+.4f}, ΔE={delta_energy:+.4f})"
            )
        return accepted, reason

    # -- internals ---------------------------------------------------------

    def _energy(self, h: float, s: float, a: float) -> float:
        """The Free-Energy proxy E = lam*H + mu*S + nu*A."""
        return (self.lam * h) + (self.mu * s) + (self.nu * a)

    @staticmethod
    def _get(metrics: Mapping[str, float], key: str) -> float:
        """Read a vital, defaulting cleanly to ``0.0`` when absent/None."""
        value = metrics.get(key, 0.0) if metrics else 0.0
        return float(value) if value is not None else 0.0


__all__ = [
    "PREDICTION_ERROR",
    "ENTROPY",
    "ACTIVE_LOAD",
    "COGNITIVE_ENERGY",
    "DEFAULT_LAMBDA",
    "DEFAULT_MU",
    "DEFAULT_NU",
    "CONFIG_KEY",
    "CONFIG_LAMBDA",
    "CONFIG_MU",
    "CONFIG_NU",
    "resolve_coefficients",
    "STRATEGY_FREE_ENERGY",
    "STRATEGY_PARETO",
    "DecisionScore",
    "DecisionPolicy",
]
