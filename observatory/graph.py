"""Graph projection: engine state -> node/edge deltas, and back.

Responsibility: express the model's learned state as a weighted directed graph, as
a stream of changes, and reconstruct that state exactly from the stream.

Why this module exists at all is the central finding of the architecture review:
the active P1 engine has no neurons. Its only registered model, `p1v0.model.CountModel`,
holds an `alphabet x alphabet` matrix of transition counts. That matrix *is* a
weighted directed graph, so it can be observed honestly:

    node i   a context/target state of the model
    edge i->j  counts[i][j], the learned weight of that transition

Node liveness is derived, not invented: a node is live when it has any incident
weight above `epsilon`. Node birth is the inactive->active transition; node death is
active->inactive. Under `CountModel`'s row decay, weights shrink toward zero on every
touch, so decay-to-death is a real observable rather than a visual effect.

Two rules keep this faithful:

  * **Absolute weights.** Every event carries the new weight, never only a delta.
    That is what makes a lossy live stream safe to coalesce and safe to resume: a
    later event fully supersedes an earlier one for the same edge.
  * **`epsilon` defaults to exact.** With `epsilon = 0.0` an edge exists iff its
    weight is not zero, so folding the stream reproduces the matrix bit-for-bit.
    Pruning small weights is a *view* policy; if the projector pruned by default,
    reconstruction would silently disagree with the engine.

The projector is read-only with respect to the model. It consumes the mapping
returned by `state_dict()`, which `CountModel` already builds from copied rows, so
it cannot alias or mutate live engine state.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Sequence, Set, Tuple

from observatory.schema import ObsEvent

#: A projected change, ready to be wrapped in an `ObsEvent` by the tap.
Delta = Tuple[str, Dict[str, Any]]


def _incident(counts: Sequence[Sequence[float]], node: int, epsilon: float) -> bool:
    """True if `node` has any incident weight above `epsilon` (out or in)."""
    row = counts[node]
    for w in row:
        if w > epsilon:
            return True
    for other in counts:
        if other[node] > epsilon:
            return True
    return False


class GraphProjector:
    """Diffs successive model states into graph deltas.

    Stateful by necessity: a delta is only meaningful against the previous state.
    One projector instance belongs to one run.
    """

    __slots__ = ("epsilon", "_prev", "_live", "_alphabet", "_initialised")

    def __init__(self, epsilon: float = 0.0) -> None:
        if epsilon < 0.0:
            raise ValueError("epsilon must be >= 0")
        self.epsilon = float(epsilon)
        self._prev: List[List[float]] | None = None
        self._live: Set[int] = set()
        self._alphabet = 0
        self._initialised = False

    def project(self, state: Mapping[str, Any], t: int | None = None) -> List[Delta]:
        """Return the deltas between the last projected state and `state`.

        `state` is a `CountModel.state_dict()`-shaped mapping: it must carry
        `alphabet` and `counts`. The first call emits the full topology, so a client
        that joins at any point can be brought up to date from one projection.
        """
        counts = state.get("counts")
        if counts is None:
            raise ValueError("state has no 'counts'; not a projectable model state")
        alphabet = int(state.get("alphabet", len(counts)))
        eps = self.epsilon

        if not self._initialised:
            return self._initial(counts, alphabet, state, t)

        if alphabet != self._alphabet:
            # Capacity growth is exactly what a future structural-plasticity
            # mechanism will do. Re-initialising is correct and honest: the client
            # receives a fresh topology rather than a partial diff across a resize.
            return self._initial(counts, alphabet, state, t)

        deltas: List[Delta] = []
        prev = self._prev or []
        for i in range(alphabet):
            prev_row = prev[i]
            new_row = counts[i]
            for j in range(alphabet):
                old = prev_row[j]
                new = new_row[j]
                if new == old:
                    continue
                old_live = old > eps
                new_live = new > eps
                if not old_live and new_live:
                    deltas.append(("edge_add", {"src": i, "dst": j, "w": new, "t": t}))
                elif old_live and not new_live:
                    deltas.append(("edge_remove", {"src": i, "dst": j, "t": t}))
                elif new_live:
                    deltas.append(
                        ("edge_update", {"src": i, "dst": j, "w": new, "dw": new - old, "t": t})
                    )

        # Node liveness is recomputed after edge deltas so that a node's birth is
        # reported alongside the edge that caused it.
        live_now = {n for n in range(alphabet) if _incident(counts, n, eps)}
        for node in sorted(live_now - self._live):
            deltas.append(("node_add", {"id": node, "t": t}))
        for node in sorted(self._live - live_now):
            deltas.append(("node_remove", {"id": node, "t": t}))

        self._live = live_now
        self._prev = [list(row) for row in counts]
        return deltas

    def _initial(
        self,
        counts: Sequence[Sequence[float]],
        alphabet: int,
        state: Mapping[str, Any],
        t: int | None,
    ) -> List[Delta]:
        eps = self.epsilon
        edges = [
            {"src": i, "dst": j, "w": counts[i][j]}
            for i in range(alphabet)
            for j in range(alphabet)
            if counts[i][j] > eps
        ]
        live = {n for n in range(alphabet) if _incident(counts, n, eps)}
        deltas: List[Delta] = [
            (
                "topology_init",
                {
                    "n_nodes": alphabet,
                    "alphabet": alphabet,
                    "epsilon": eps,
                    "nodes": sorted(live),
                    "edges": edges,
                    "alpha": state.get("alpha"),
                    "decay": state.get("decay"),
                    "n_updates": state.get("n_updates"),
                    "t": t,
                },
            )
        ]
        self._live = live
        self._alphabet = alphabet
        self._prev = [list(row) for row in counts]
        self._initialised = True
        return deltas


class GraphView:
    """Reconstructed graph state, built by folding deltas.

    This is the client-side reducer in its simplest form, and the reference the
    fidelity tests compare against. If folding the stream does not reproduce the
    engine's matrix, the stream is lossy and the instrument is wrong.
    """

    __slots__ = ("alphabet", "nodes", "edges", "epsilon", "last_t", "_applied")

    def __init__(self) -> None:
        self.alphabet = 0
        self.nodes: Set[int] = set()
        self.edges: Dict[Tuple[int, int], float] = {}
        self.epsilon = 0.0
        self.last_t: int | None = None
        self._applied = 0

    def apply(self, kind: str, payload: Mapping[str, Any]) -> None:
        """Apply one delta. Unknown structural combinations raise, by design."""
        t = payload.get("t")
        if t is not None:
            self.last_t = int(t)
        self._applied += 1

        if kind == "topology_init":
            self.alphabet = int(payload["n_nodes"])
            self.epsilon = float(payload.get("epsilon", 0.0))
            self.nodes = set(payload.get("nodes") or [])
            self.edges = {
                (int(e["src"]), int(e["dst"])): float(e["w"])
                for e in payload.get("edges") or []
            }
            return
        if kind == "edge_add":
            self.edges[(int(payload["src"]), int(payload["dst"]))] = float(payload["w"])
            return
        if kind == "edge_update":
            key = (int(payload["src"]), int(payload["dst"]))
            if key not in self.edges:
                # Per the data-model invariant: an update for an unknown edge means a
                # structural event was lost. Failing loudly is the point -- silently
                # inserting would let the view diverge from the engine undetected.
                raise KeyError(f"edge_update for unknown edge {key}; structural event lost")
            self.edges[key] = float(payload["w"])
            return
        if kind == "edge_remove":
            self.edges.pop((int(payload["src"]), int(payload["dst"])), None)
            return
        if kind == "node_add":
            self.nodes.add(int(payload["id"]))
            return
        if kind == "node_remove":
            self.nodes.discard(int(payload["id"]))
            return
        # Non-structural kinds carry no graph state; ignoring them is correct.

    def apply_event(self, event: ObsEvent) -> None:
        self.apply(event.kind, event.p)

    def apply_all(self, deltas: Iterable[Delta]) -> None:
        for kind, payload in deltas:
            self.apply(kind, payload)

    def to_matrix(self) -> List[List[float]]:
        """Dense matrix, for exact comparison against `CountModel.counts`."""
        size = self.alphabet
        matrix = [[0.0] * size for _ in range(size)]
        for (i, j), w in self.edges.items():
            matrix[i][j] = w
        return matrix

    def stats(self) -> Dict[str, Any]:
        return {
            "alphabet": self.alphabet,
            "n_nodes": len(self.nodes),
            "n_edges": len(self.edges),
            "last_t": self.last_t,
            "applied": self._applied,
        }
