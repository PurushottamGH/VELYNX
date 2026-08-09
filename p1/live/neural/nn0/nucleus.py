"""NN-0 minimal predictive recurrent core (experimental substrate).

Implements the exact NN-0 contract from
``outputs/P1_LIVE_NN_NEURAL_ARCHITECTURE.md``:

    e   = Embedding(x_t, V, 32)
    r   = KStore.read(proj(h_{t-1}))
    h   = GRU(cat(e, r), h_{t-1}, 128)
    P   = Softmax(Readout(h))
    L   = CE(P, x_{t+1})                    # the SOLE learning signal

Managed facilities:
    * deterministic seeding (torch CPU/CUDA, numpy, python random)
    * checkpoint / restart (7-file bundle: model/optim/rng/episodic/replay/
      meta/lineage)
    * online single-experience updates (next-token CE only)
    * bounded replay reservoir with error-prioritized sampling
    * host-resident episodic key/value store (non-parametric: keys and values
      are detached; memory interacts with the loss only through reads)

Everything here is an experimental substrate, not a capability claim. Nothing
in this module talks to LSKE, governance, the ros Store, proposal adapters,
contradiction detection, vector indexing, chat, or generation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import copy
import hashlib
import json
import random
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

CHECKPOINT_VERSION = 2
NN0_ARCH = "nn0-tiny-gru"


def set_global_seed(seed: int) -> None:
    """Seed every RNG stream used downstream."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


@dataclass
class NN0Config:
    vocab_size: int = 128
    d_embed: int = 32
    d_hidden: int = 128
    d_read: int = 32
    kv_capacity: int = 65536
    kv_top_k: int = 4
    replay_capacity: int = 65536
    replay_alpha: float = 0.6
    replay_batch_size: int = 64
    replay_every: int = 1
    lr: float = 1e-3
    weight_decay: float = 5e-4
    store_threshold: float = 0.0
    # ``transition`` is the legacy online mode: one gradient step per token with
    # the hidden state detached between tokens (BPTT window of exactly 1) and a
    # replay buffer of isolated bigrams.  ``sequence`` back-propagates over a
    # frozen ``bptt_window`` and replays whole experience sequences from the
    # episode boundary; both are recorded in the protocol.
    training_mode: str = "transition"
    bptt_window: int = 1
    seed: int = 0
    device: str = "auto"
    experiment_id: str = "nn0-dev"
    run_id: int = 0
    protocol_id: str = ""
    vocabulary_id: str = ""
    replay_seed: Optional[int] = None
    checkpoint_dir: Optional[str] = None

    def __post_init__(self) -> None:
        if self.device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        if self.replay_seed is None:
            self.replay_seed = int(self.seed)
        if self.training_mode not in ("transition", "sequence"):
            raise ValueError(f"unknown training_mode: {self.training_mode}")
        if self.bptt_window < 1:
            raise ValueError("bptt_window must be >= 1")
        if self.training_mode == "transition" and self.bptt_window != 1:
            raise ValueError("transition mode has a fixed BPTT window of 1")


def _hash_state(state: Dict[str, torch.Tensor]) -> str:
    blobs: List[bytes] = []
    for _, t in sorted(state.items()):
        blobs.append(t.detach().cpu().contiguous().numpy().tobytes())
    return hashlib.sha256(b"".join(blobs)).hexdigest()


class TinyGRUCore(nn.Module):
    """``Embedding(d_embed) -> GRU(d_embed + d_read, d_hidden) -> readout``."""

    def __init__(self, cfg: NN0Config) -> None:
        super().__init__()
        self.embedding = nn.Embedding(cfg.vocab_size, cfg.d_embed)
        self.key_head = nn.Linear(cfg.d_hidden, cfg.d_read, bias=True)
        self.gru = nn.GRU(cfg.d_embed + cfg.d_read, cfg.d_hidden, batch_first=True)
        self.readout = nn.Linear(cfg.d_hidden, cfg.vocab_size, bias=True)
        self.d_hidden = cfg.d_hidden
        self.reset_parameters()
        # Frozen random address projection for ``project_key_token``. Drawn from
        # its own generator so it is identical at every ``d_hidden`` and cannot
        # shift the global RNG stream the parameter init above consumes.
        # ``persistent=False`` keeps it out of ``state_dict``, so pre-patch
        # checkpoints load unchanged and it is never a trainable surface.
        gen = torch.Generator(device="cpu").manual_seed(int(cfg.seed))
        self.register_buffer(
            "key_token_proj",
            torch.empty(cfg.d_embed, cfg.d_read).normal_(0.0, 1.0, generator=gen)
            / float(cfg.d_embed) ** 0.5,
            persistent=False,
        )

    def reset_parameters(self) -> None:
        for mod in self.modules():
            if isinstance(mod, nn.Linear):
                nn.init.xavier_uniform_(mod.weight)
                if mod.bias is not None:
                    nn.init.zeros_(mod.bias)
            elif isinstance(mod, nn.Embedding):
                nn.init.normal_(mod.weight, 0.0, 1.0)
            elif isinstance(mod, nn.GRU):
                for name, p in mod.named_parameters():
                    if "weight_ih" in name:
                        nn.init.xavier_uniform_(p)
                    elif "weight_hh" in name:
                        nn.init.orthogonal_(p)
                    elif "bias" in name:
                        nn.init.zeros_(p)

    def forward(
        self,
        x: torch.Tensor,
        h: torch.Tensor,
        read: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """``(B, T) -> ((B, T, V), (B, T, H))``.

        ``read``: ``(B, d_read)`` pre-computed memory read aligned to ``h``;
        may be ``None`` to run on the embedding alone.

        ``h_out`` is the per-timestep GRU output; because GRU output at step
        ``t`` is exactly the hidden state ``h_t``, ``h_out[:, t]`` is the
        state summary that ``Readout`` consumes (the last step ``h_out[:, -1]``
        seeds the next single-experience recurrence).
        """
        emb = self.embedding(x)  # (B, T, d_embed)
        if read is None:
            read = torch.zeros(emb.size(0), self.key_head.out_features, device=emb.device)
        read = read.unsqueeze(1)  # (B, 1, d_read)
        emb = torch.cat([emb, read.expand(-1, emb.size(1), -1)], dim=-1)
        h_out, _ = self.gru(emb, h)
        logits = self.readout(h_out)
        return logits, h_out

    def forward_memory(
        self,
        x: torch.Tensor,
        h: torch.Tensor,
        reader: Optional[Callable[[torch.Tensor], Optional[torch.Tensor]]] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor, List[torch.Tensor]]:
        """``forward`` with a per-timestep memory read instead of one broadcast.

        ``reader(h_prev)`` is called once per timestep with the ``(1, B, H)``
        incoming state and returns a ``(B, d_read)`` read (or ``None``).  This
        honours the documented contract ``r_t = KV.read(project_key(h_{t-1}))``,
        which ``forward`` violates by computing a single read outside the
        recurrence and broadcasting it over every ``T``.

        Returns ``((B, T, V), (B, T, H), [h_0 .. h_{T-1}])``; the third element
        is the list of *incoming* states, i.e. exactly the states whose
        projections were used as read queries, so a caller can write KV keys
        that match the query it will later issue.
        """
        b, t = x.shape
        logits: List[torch.Tensor] = []
        states: List[torch.Tensor] = []
        queried: List[torch.Tensor] = []
        for i in range(t):
            queried.append(h)
            read = None if reader is None else reader(h)
            emb = self.embedding(x[:, i : i + 1])
            if read is None:
                read = torch.zeros(b, self.key_head.out_features, device=emb.device)
            emb = torch.cat([emb, read.unsqueeze(1)], dim=-1)
            step_out, h = self.gru(emb, h)
            logits.append(self.readout(step_out))
            states.append(step_out)
        return torch.cat(logits, dim=1), torch.cat(states, dim=1), queried

    def project_key(self, h: torch.Tensor) -> torch.Tensor:
        """Key for the episodic store (detached; no gradient path).

        ``h`` is ``(1, B, H)`` or ``(B, H)``; returns ``(B, d_read)``.

        ``key_head`` is deliberately a *frozen random projection*: the detach
        means it never receives gradient, so its weights stay at their seeded
        initialisation for the whole run. That keeps the store non-parametric.
        The consequence to remember is ``project_key(0) == key_head.bias == 0``,
        so a query issued from an un-evolved hidden state is the zero vector and
        carries no context; queries must be issued from ``h_{t-1}`` after at
        least one token (see ``forward_memory``).
        """
        h = h.detach()
        if h.dim() == 3:
            h = h.squeeze(0)
        return self.key_head(h)

    def project_key_token(self, x: torch.Tensor) -> torch.Tensor:
        """Token-conditioned address: ``(B,) token ids -> (B, d_read)``.

        ``project_key`` reads the *hidden* state, so under the causal
        intervention ``do(h=0)`` it collapses to ``key_head.bias`` and every
        query becomes the same vector -- a key-blind read. This address depends
        only on the key token identity, so it survives ``h=0`` unchanged.

        ``key_token_proj`` is a frozen random projection held as a
        non-persistent buffer: it is re-derived deterministically from
        ``cfg.seed`` at construction, adds no parameters, never receives
        gradient, and is not written into ``state_dict`` (so checkpoints written
        before this patch still load).
        """
        if x.dim() == 2:
            x = x.reshape(-1)
        if x.dim() != 1:
            raise ValueError("project_key_token expects (B,) token ids")
        emb = self.embedding(x).detach()  # (B, d_embed)
        return emb @ self.key_token_proj


class KVMemory:
    """Host-resident append-only episodic key/value store (non-parametric).

    ``write(key, value, outcome, err)`` appends until ``capacity``.
    ``read(query, k)`` returns a top-``k`` cosine-weighted mixture of stored
    value vectors. Nothing here carries a gradient and nothing is trainable.
    """

    def __init__(self, capacity: int, d_key: int, d_value: int) -> None:
        self.capacity = capacity
        self.d_key = d_key
        self.d_value = d_value
        self.keys: List[torch.Tensor] = []
        self.values: List[torch.Tensor] = []
        self.outcomes: List[int] = []
        self.errors: List[float] = []
        self.source_ids: List[str] = []
        self.dropped: int = 0
        # ponytail: the store is append-only, so re-stacking every key on every
        # read is pure waste -- and reads happen once per timestep plus once per
        # replay position, which is where the runtime actually goes. Invalidated
        # by write/clear/load_state_dict; numerically identical either way.
        self._stack_cache: Optional[Tuple[str, torch.Tensor, torch.Tensor]] = None

    def __len__(self) -> int:
        return len(self.keys)

    def write(
        self,
        key: torch.Tensor,
        value: torch.Tensor,
        outcome: int,
        err: float,
        source_id: str = "legacy:unknown",
        forbidden_source_ids: Optional[set[str]] = None,
    ) -> bool:
        """Append one row per key, up to ``capacity`` (row-level batch aware).

        A single-experience write passes a ``(1, d)`` key/value pair and stores
        exactly one entry; a ``(B, d)`` pair stores ``B`` entries under the
        same ``outcome`` / ``err`` metadata.
        """
        if forbidden_source_ids and source_id in forbidden_source_ids:
            raise AssertionError(f"probe source cannot enter KV memory: {source_id}")
        keys = key.detach().cpu()
        values = value.detach().cpu()
        if keys.dim() == 1:
            keys = keys.unsqueeze(0)
            values = values.unsqueeze(0)
        wrote_any = False
        for r in range(keys.shape[0]):
            if len(self.keys) >= self.capacity:
                self.dropped += 1
                continue
            self.keys.append(keys[r].clone())
            self.values.append(values[r].clone())
            self.outcomes.append(int(outcome))
            self.errors.append(float(err))
            self.source_ids.append(str(source_id))
            wrote_any = True
        if wrote_any:
            self._stack_cache = None
        return wrote_any

    def read(self, query: torch.Tensor, k: int, device: str = "cpu") -> Optional[torch.Tensor]:
        """Top-k memory read -> ``(B, d_value)`` mixture, detached."""
        if not self.keys:
            return None
        k = min(k, len(self.keys))
        if self._stack_cache is None or self._stack_cache[0] != device:
            K = torch.stack(self.keys).to(device)  # (K, d_key)
            V = torch.stack(self.values).to(device)  # (K, d_value)
            self._stack_cache = (device, F.normalize(K, dim=-1), V)
        _, kn, V = self._stack_cache
        q = F.normalize(query.detach(), dim=-1)
        sim = q @ kn.T  # (B, K)
        top = torch.topk(sim, k, dim=-1)
        w = torch.softmax(top.values, dim=-1)  # (B, k)
        read = (w.unsqueeze(-1) * V[top.indices]).sum(dim=-2)
        return read.detach()

    def state_dict(self) -> Dict[str, Any]:
        return {
            "capacity": self.capacity,
            "keys": self.keys,
            "values": self.values,
            "outcomes": self.outcomes,
            "errors": self.errors,
            "source_ids": self.source_ids,
            "dropped": self.dropped,
        }

    def load_state_dict(self, sd: Dict[str, Any]) -> None:
        self.capacity = sd["capacity"]
        self.keys = sd["keys"]
        self.values = sd["values"]
        self.outcomes = sd["outcomes"]
        self.errors = sd["errors"]
        self.source_ids = list(sd.get("source_ids", ["legacy:unknown"] * len(self.keys)))
        self.dropped = sd["dropped"]
        self._stack_cache = None

    def clear(self) -> None:
        """Clear external episodic memory without touching model weights."""
        self.keys.clear()
        self.values.clear()
        self.outcomes.clear()
        self.errors.clear()
        self.source_ids.clear()
        self.dropped = 0
        self._stack_cache = None


@dataclass(frozen=True)
class ReplayEntry:
    """Replay row with provenance while preserving legacy tuple unpacking."""

    x: int
    y: int
    err: float
    source_id: str = "legacy:unknown"

    def __iter__(self):
        # Existing nucleus callers unpack (x, y, err); provenance is exposed
        # through the named attribute and checkpoint state.
        yield self.x
        yield self.y
        yield self.err

    def __getitem__(self, index: int):
        return (self.x, self.y, self.err)[index]


class ReplayReservoir:
    """Bounded reservoir replay buffer with error-prioritized sampling."""

    def __init__(self, capacity: int, alpha: float = 0.6, seed: int = 0) -> None:
        self.capacity = capacity
        self.alpha = alpha
        self._rng = np.random.default_rng(seed)
        self.items: List[ReplayEntry] = []

    def __len__(self) -> int:
        return len(self.items)

    def push(
        self,
        x: int,
        y: int,
        err: float,
        source_id: str = "legacy:unknown",
        forbidden_source_ids: Optional[set[str]] = None,
    ) -> None:
        if forbidden_source_ids and source_id in forbidden_source_ids:
            raise AssertionError(f"probe source cannot enter replay: {source_id}")
        entry = ReplayEntry(int(x), int(y), float(err), str(source_id))
        if len(self.items) < self.capacity:
            self.items.append(entry)
            return
        j = int(self._rng.integers(0, self.capacity))
        self.items[j] = entry

    def sample(self, n: int) -> List[ReplayEntry]:
        """Error-ranked priority sampling without replacement."""
        if not self.items:
            return []
        n = min(n, len(self.items))
        arr: np.ndarray = np.array([i[2] for i in self.items], dtype=float)
        rank = np.argsort(np.argsort(arr)).astype(float)
        p = (1.0 + rank) ** self.alpha
        p = p / p.sum()
        idx = self._rng.choice(len(self.items), size=n, replace=False, p=p)
        return [self.items[i] for i in idx]

    def state_dict(self) -> Dict[str, Any]:
        return {
            "capacity": self.capacity,
            "alpha": self.alpha,
            "items": [
                {
                    "x": it.x,
                    "y": it.y,
                    "err": it.err,
                    "source_id": it.source_id,
                }
                for it in self.items
            ],
            "rng": self._rng.bit_generator.state,
        }

    def load_state_dict(self, sd: Dict[str, Any]) -> None:
        self.capacity = sd["capacity"]
        self.alpha = sd["alpha"]
        self.items = [
            ReplayEntry(
                int(it["x"]) if isinstance(it, dict) else int(it[0]),
                int(it["y"]) if isinstance(it, dict) else int(it[1]),
                float(it["err"]) if isinstance(it, dict) else float(it[2]),
                (
                    str(it.get("source_id", "legacy:unknown"))
                    if isinstance(it, dict)
                    else "legacy:unknown"
                ),
            )
            for it in sd["items"]
        ]
        rng = np.random.default_rng(0)
        rng.bit_generator.state = sd["rng"]
        self._rng = rng

    def clear(self) -> None:
        """Clear replay rows without touching learned model weights."""
        self.items.clear()

    def digest_rows(self) -> List[Tuple[Any, ...]]:
        """Order-preserving rows for an external state digest."""
        return [(it.x, it.y, it.err, it.source_id) for it in self.items]


@dataclass(frozen=True)
class SequenceReplayEntry:
    """Replay row whose unit is a whole experience sequence."""

    tokens: Tuple[int, ...]
    err: float
    source_id: str = "legacy:unknown"


class SequenceReplay:
    """Replay whose unit is one full experience sequence, not one transition.

    ``ReplayReservoir`` stores isolated ``(x, y)`` bigrams that are later
    replayed from a zero hidden state, so the replay objective is a strictly
    context-free next-token model even when the online objective is not.  This
    buffer stores the whole ``Experience.sequence()`` and replays it from the
    same episode-start state the online pass used, so the replay objective is
    the online objective evaluated on an earlier experience -- nothing more.
    """

    def __init__(self, capacity: int, alpha: float = 0.6, seed: int = 0) -> None:
        self.capacity = capacity
        self.alpha = alpha
        self._rng = np.random.default_rng(seed)
        self.items: List[SequenceReplayEntry] = []

    def __len__(self) -> int:
        return len(self.items)

    def push_sequence(
        self,
        tokens: Sequence[int],
        err: float,
        source_id: str = "legacy:unknown",
        forbidden_source_ids: Optional[set[str]] = None,
    ) -> None:
        if forbidden_source_ids and source_id in forbidden_source_ids:
            raise AssertionError(f"probe source cannot enter replay: {source_id}")
        entry = SequenceReplayEntry(tuple(int(t) for t in tokens), float(err), str(source_id))
        if len(self.items) < self.capacity:
            self.items.append(entry)
            return
        j = int(self._rng.integers(0, self.capacity))
        self.items[j] = entry

    def sample(self, n: int) -> List[SequenceReplayEntry]:
        """Error-ranked priority sampling without replacement (as reservoir)."""
        if not self.items:
            return []
        n = min(n, len(self.items))
        arr: np.ndarray = np.array([it.err for it in self.items], dtype=float)
        rank = np.argsort(np.argsort(arr)).astype(float)
        p = (1.0 + rank) ** self.alpha
        p = p / p.sum()
        idx = self._rng.choice(len(self.items), size=n, replace=False, p=p)
        return [self.items[i] for i in idx]

    def state_dict(self) -> Dict[str, Any]:
        return {
            "capacity": self.capacity,
            "alpha": self.alpha,
            "items": [
                {"tokens": list(it.tokens), "err": it.err, "source_id": it.source_id}
                for it in self.items
            ],
            "rng": self._rng.bit_generator.state,
        }

    def load_state_dict(self, sd: Dict[str, Any]) -> None:
        self.capacity = sd["capacity"]
        self.alpha = sd["alpha"]
        self.items = [
            SequenceReplayEntry(
                tuple(int(t) for t in it["tokens"]),
                float(it["err"]),
                str(it.get("source_id", "legacy:unknown")),
            )
            for it in sd["items"]
        ]
        rng = np.random.default_rng(0)
        rng.bit_generator.state = sd["rng"]
        self._rng = rng

    def clear(self) -> None:
        self.items.clear()

    def digest_rows(self) -> List[Tuple[Any, ...]]:
        return [(it.tokens, it.err, it.source_id) for it in self.items]


class NN0Trainer:
    """Online single-experience trainer plus persistence envelope."""

    def __init__(self, config: NN0Config) -> None:
        self.cfg = config
        set_global_seed(config.seed)
        self.device = torch.device(config.device)
        self.model = TinyGRUCore(config).to(self.device)
        self.optim = torch.optim.AdamW(
            self.model.parameters(),
            lr=self.cfg.lr,
            weight_decay=self.cfg.weight_decay,
        )
        self.memory = KVMemory(
            capacity=config.kv_capacity,
            d_key=config.d_read,
            d_value=config.d_embed,
        )
        self.replay = (
            SequenceReplay(
                capacity=config.replay_capacity,
                alpha=config.replay_alpha,
                seed=int(config.replay_seed),
            )
            if config.training_mode == "sequence"
            else ReplayReservoir(
                capacity=config.replay_capacity,
                alpha=config.replay_alpha,
                seed=int(config.replay_seed),
            )
        )
        self.step_count = 0
        self.last_h: Optional[torch.Tensor] = None
        self.history: Dict[str, List[float]] = {"loss": [], "err": []}
        self.source_blacklist: frozenset[str] = frozenset()
        self.evaluation_active = False
        self._frozen = False

    def _zero_h(self, b: int = 1) -> torch.Tensor:
        return torch.zeros(1, b, self.cfg.d_hidden, device=self.device)

    def reset_state(self) -> None:
        """Clear recurrent hidden state only."""
        self.last_h = None

    def reset_episode(self) -> None:
        """Clear the recurrent episode state without touching learned weights."""
        self.reset_state()

    def clear_external_memory(self) -> None:
        """Clear only external KV memory."""
        self.memory.clear()

    def clear_replay(self) -> None:
        """Clear only replay entries."""
        self.replay.clear()

    # ---- causal-isolation controls ---------------------------------------

    def reset_optimizer(self) -> None:
        """Discard all optimizer state; leave θ, memory, and replay untouched.

        Blocks the AdamW-momentum path: ``exp_avg``, ``exp_avg_sq`` and the
        per-parameter ``step`` counters carry history across an evaluation
        boundary and make an update depend on tokens seen before the
        intervention. A fresh optimizer is the only way to clear ``step``, since
        AdamW's bias correction reads it. This is *not* a parameter reset --
        ``parameter_hash()`` is unchanged by this call.
        """
        self.optim = torch.optim.AdamW(
            self.model.parameters(),
            lr=self.cfg.lr,
            weight_decay=self.cfg.weight_decay,
        )
        for p in self.model.parameters():
            p.grad = None

    def optimizer_state_is_empty(self) -> bool:
        """True when no optimizer moment or step state exists (audit seam)."""
        return not any(self.optim.state_dict()["state"].values())

    def freeze_parameters(self) -> None:
        """Make θ immutable: no grad accumulation, no optimizer update.

        Sets ``requires_grad=False`` on every parameter, drops any pending
        ``.grad``, and latches ``_frozen`` so ``step``/``step_sequence`` refuse
        rather than silently no-op. ``model.eval()`` alone does not block
        updates, and ``requires_grad=False`` alone still lets a stale ``.grad``
        plus ``optim.step()`` move weights -- both are needed.
        """
        self._frozen = True
        for p in self.model.parameters():
            p.requires_grad_(False)
            p.grad = None

    def unfreeze_parameters(self) -> None:
        """Restore trainability after :meth:`freeze_parameters`."""
        self._frozen = False
        for p in self.model.parameters():
            p.requires_grad_(True)

    @property
    def parameters_frozen(self) -> bool:
        """Auditable freeze state: latch plus the actual ``requires_grad`` flags."""
        return self._frozen and not any(p.requires_grad for p in self.model.parameters())

    def parameter_hash(self) -> str:
        """SHA-256 over θ; the protocol's θ-immutability witness."""
        return _hash_state(self.model.state_dict())

    def set_source_blacklist(self, source_ids: List[str] | set[str] | frozenset[str]) -> None:
        """Freeze source IDs that cannot reach training, KV, or replay writes."""
        self.source_blacklist = frozenset(str(source_id) for source_id in source_ids)

    def _assert_trainable_source(self, source_id: str) -> None:
        if self._frozen:
            raise AssertionError("parameters are frozen; call unfreeze_parameters() first")
        if self.evaluation_active:
            raise AssertionError("evaluation cannot update NN-0 parameters or memories")
        if source_id in self.source_blacklist or source_id.startswith("probe:"):
            raise AssertionError(f"probe source cannot enter NN-0 training: {source_id}")

    def _forward(self, x: torch.Tensor, h: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        read = None
        if len(self.memory) > 0:
            query = self.model.project_key(h)
            read = self.memory.read(query, self.cfg.kv_top_k, self.device)
        logits, h_out = self.model(x, h, read)
        return logits, h_out

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Model forward over a batch; updates ``last_h`` with a detached copy."""
        b = x.size(0)
        h = self._zero_h(b) if self.last_h is None else self.last_h.clone()
        logits, h_out = self._forward(x, h)
        self.last_h = h_out.detach()
        return logits

    def predict_context(
        self, context: List[int] | Tuple[int, ...], *, use_external_memory: bool = True
    ) -> torch.Tensor:
        """Pure frozen-parameter prediction for one complete context.

        This seam never changes ``last_h`` and never writes KV or replay state;
        it is the only prediction path used by the canonical adapter.
        """
        if not context:
            raise ValueError("context must not be empty")
        was_training = self.model.training
        self.model.eval()
        try:
            with torch.no_grad():
                x = torch.tensor([list(context)], dtype=torch.long, device=self.device)
                h = self._zero_h(1)
                if use_external_memory and len(self.memory) > 0:
                    # Query per timestep from the state the context has actually
                    # produced. The legacy path issued one query from h_0, which
                    # is the zero vector at evaluation and therefore identical
                    # for every probe.
                    logits, _, _ = self.model.forward_memory(x, h, self._reader)
                else:
                    logits, _ = self.model(x, h, None)
                return torch.softmax(logits[:, -1, :], dim=-1).squeeze(0).cpu()
        finally:
            self.model.train(was_training)

    def _loss_batch(self, xs: torch.Tensor, ys: torch.Tensor) -> torch.Tensor:
        h = self._zero_h(xs.size(0))
        logits, _ = self.model(xs, h, None)
        return F.cross_entropy(logits.squeeze(1), ys)

    def _reader(self, h: torch.Tensor) -> Optional[torch.Tensor]:
        """``r_t = KV.read(project_key(h_{t-1}))``, or ``None`` on empty memory."""
        if len(self.memory) == 0:
            return None
        return self.memory.read(self.model.project_key(h), self.cfg.kv_top_k, self.device)

    def _replay_sequence_loss(self, batch: List[SequenceReplayEntry]) -> torch.Tensor:
        """Replay whole sequences through the *online* forward path.

        Right-padded with ``ignore_index=-100`` so a mixed-length batch scores
        exactly the positions the online pass scored. Because this uses
        ``forward_memory`` from the episode-start state, the replay objective is
        the online objective on an earlier experience -- it cannot pull the GRU
        towards a context-free bigram model the way isolated-transition replay
        does.
        """
        width = max(len(entry.tokens) for entry in batch) - 1
        xs = torch.zeros(len(batch), width, dtype=torch.long, device=self.device)
        ys = torch.full((len(batch), width), -100, dtype=torch.long, device=self.device)
        for row, entry in enumerate(batch):
            tokens = entry.tokens
            n = len(tokens) - 1
            xs[row, :n] = torch.tensor(tokens[:-1], device=self.device)
            ys[row, :n] = torch.tensor(tokens[1:], device=self.device)
        logits, _, _ = self.model.forward_memory(xs, self._zero_h(len(batch)), self._reader)
        return F.cross_entropy(
            logits.reshape(-1, logits.size(-1)), ys.reshape(-1), ignore_index=-100
        )

    def step_sequence(
        self,
        tokens: Sequence[int],
        *,
        source_id: str = "legacy:unknown",
        weight: float = 1.0,
        reset: bool = True,
    ) -> Dict[str, float]:
        """One online update over a whole experience with truncated BPTT.

        The sequence is cut into ``cfg.bptt_window``-length chunks; gradient
        flows across every timestep inside a chunk and the state is detached
        only at the chunk boundary, so the credit-assignment horizon is exactly
        ``bptt_window`` rather than the single timestep ``step`` allows. The
        window is a frozen protocol field, not a free runtime knob.
        """
        self._assert_trainable_source(source_id)
        if weight <= 0.0:
            raise ValueError("weight must be > 0")
        if len(tokens) < 2:
            raise ValueError("a sequence experience needs at least 2 tokens")
        if reset:
            self.reset_state()
        window = int(self.cfg.bptt_window)
        xs = list(int(t) for t in tokens[:-1])
        ys = list(int(t) for t in tokens[1:])
        errs: List[float] = []
        losses: List[float] = []

        for start in range(0, len(xs), window):
            cx, cy = xs[start : start + window], ys[start : start + window]
            self.optim.zero_grad(set_to_none=True)
            h = self._zero_h(1) if self.last_h is None else self.last_h.clone()
            x = torch.tensor([cx], device=self.device)
            y = torch.tensor([cy], device=self.device)
            logits, h_out, queried = self.model.forward_memory(x, h, self._reader)
            per_pos = F.cross_entropy(logits.squeeze(0), y.squeeze(0), reduction="none")
            loss = per_pos.mean()
            chunk_errs = [float(v) for v in per_pos.detach().cpu()]

            total = loss
            if self.step_count % self.cfg.replay_every == 0 and len(self.replay) > 0:
                total = total + self._replay_sequence_loss(
                    self.replay.sample(self.cfg.replay_batch_size)
                )
            (total * weight).backward()
            self.optim.step()
            self.last_h = h_out[:, -1, :].unsqueeze(0).detach()

            for i, err in enumerate(chunk_errs):
                if err < self.cfg.store_threshold:
                    continue
                self.memory.write(
                    self.model.project_key(queried[i]),
                    self.model.embedding(y[:, i]),
                    cy[i],
                    err,
                    source_id=source_id,
                    forbidden_source_ids=set(self.source_blacklist),
                )
            self.step_count += 1
            errs.extend(chunk_errs)
            losses.append(float(total.detach().item()))

        mean_err = sum(errs) / len(errs)
        self.replay.push_sequence(
            tokens,
            mean_err,
            source_id=source_id,
            forbidden_source_ids=set(self.source_blacklist),
        )
        self.history["err"].append(mean_err)
        return {
            "err": mean_err,
            "loss": sum(losses) / len(losses),
            "step": self.step_count,
            "chunks": float(len(losses)),
        }

    def step(
        self,
        x_val: int,
        y_val: int,
        *,
        source_id: str = "legacy:unknown",
        weight: float = 1.0,
    ) -> Dict[str, float]:
        """One online single-experience update (pure next-token CE)."""
        self._assert_trainable_source(source_id)
        if weight <= 0.0:
            raise ValueError("weight must be > 0")
        self.optim.zero_grad(set_to_none=True)
        x = torch.tensor([[x_val]], device=self.device)
        y = torch.tensor([y_val], device=self.device)
        logits = self.forward(x)
        loss = F.cross_entropy(logits.squeeze(1), y)
        err = float(loss.detach().item())

        if self.step_count % self.cfg.replay_every == 0 and len(self.replay) > 0:
            batch = self.replay.sample(self.cfg.replay_batch_size)
            rb_x = torch.tensor([[entry.x] for entry in batch], device=self.device)
            rb_y = torch.tensor([entry.y for entry in batch], device=self.device)
            loss = loss + self._loss_batch(rb_x, rb_y)

        (loss * weight).backward()
        self.optim.step()

        if err >= self.cfg.store_threshold:
            key = self.model.project_key(self.last_h)
            value = self.model.embedding(y)
            self.memory.write(
                key,
                value,
                y_val,
                err,
                source_id=source_id,
                forbidden_source_ids=set(self.source_blacklist),
            )
        self.replay.push(
            x_val,
            y_val,
            err,
            source_id=source_id,
            forbidden_source_ids=set(self.source_blacklist),
        )

        self.step_count += 1
        self.history["err"].append(err)
        return {"err": err, "loss": float(loss.item()), "step": self.step_count}

    def state_dict(self) -> Dict[str, Any]:
        """Export the four distinct memory/state surfaces without aliases."""
        return {
            "cfg": asdict(self.cfg),
            "model": {
                key: value.detach().cpu().clone() for key, value in self.model.state_dict().items()
            },
            "optim": self.optim.state_dict(),
            "memory": self.memory.state_dict(),
            "replay": self.replay.state_dict(),
            "step_count": self.step_count,
            "last_h": self.last_h.detach().cpu().clone() if self.last_h is not None else None,
            "history": {key: list(value) for key, value in self.history.items()},
        }

    def load_state_dict(self, state: Dict[str, Any]) -> None:
        """Restore state while preserving the current source blacklist."""
        self.model.load_state_dict(state["model"])
        self.optim.load_state_dict(state["optim"])
        self.memory.load_state_dict(state["memory"])
        self.replay.load_state_dict(state["replay"])
        self.step_count = int(state["step_count"])
        self.last_h = state["last_h"].to(self.device) if state.get("last_h") is not None else None
        self.history = {key: list(value) for key, value in state.get("history", {}).items()}

    def snapshot(self) -> Dict[str, Any]:
        """Deep, self-contained capture of every causally relevant surface.

        Distinct from :meth:`state_dict`, which aliases the live KV/replay lists
        and RNG dicts: mutating the trainer after ``state_dict()`` would mutate
        the "snapshot" too, so it cannot express "State A and State B differ only
        in M". Everything here is cloned or deep-copied, and RNG state is
        included because it is already part of the checkpoint contract.
        """
        return {
            "cfg": asdict(self.cfg),
            "model": {k: v.detach().cpu().clone() for k, v in self.model.state_dict().items()},
            "optim": copy.deepcopy(self.optim.state_dict()),
            "memory": copy.deepcopy(self.memory.state_dict()),
            "replay": copy.deepcopy(self.replay.state_dict()),
            "step_count": self.step_count,
            "last_h": self.last_h.detach().cpu().clone() if self.last_h is not None else None,
            "history": {k: list(v) for k, v in self.history.items()},
            "frozen": self._frozen,
            "evaluation_active": self.evaluation_active,
            "rng": {
                "torch_cpu": torch.get_rng_state().clone(),
                "random": random.getstate(),
                "numpy": np.random.get_state(),
            },
        }

    def restore(self, snap: Dict[str, Any]) -> None:
        """Restore a :meth:`snapshot` exactly, including RNG and freeze state."""
        if int(snap["cfg"]["d_hidden"]) != self.cfg.d_hidden:
            raise ValueError(f"snapshot d_hidden {snap['cfg']['d_hidden']} != {self.cfg.d_hidden}")
        self.model.load_state_dict({k: v.to(self.device) for k, v in snap["model"].items()})
        self.optim.load_state_dict(copy.deepcopy(snap["optim"]))
        self.memory.load_state_dict(copy.deepcopy(snap["memory"]))
        self.replay.load_state_dict(copy.deepcopy(snap["replay"]))
        self.step_count = int(snap["step_count"])
        self.last_h = snap["last_h"].to(self.device) if snap["last_h"] is not None else None
        self.history = {k: list(v) for k, v in snap["history"].items()}
        self.evaluation_active = bool(snap["evaluation_active"])
        if bool(snap["frozen"]):
            self.freeze_parameters()
        else:
            self.unfreeze_parameters()
        rng = snap["rng"]
        torch.set_rng_state(rng["torch_cpu"].clone())
        random.setstate(rng["random"])
        np.random.set_state(rng["numpy"])

    def probe(self, xs: List[int], ys: List[int]) -> Dict[str, float]:
        """Frozen-θ mean next-token CE over a held-out pair list."""
        was_training = self.model.training
        self.model.eval()
        try:
            with torch.no_grad():
                x = torch.tensor([xs], device=self.device)
                y = torch.tensor(ys, device=self.device)
                h = self._zero_h(1)
                logits, _ = self._forward(x, h)
                nll = float(F.cross_entropy(logits.squeeze(0), y).item())
        finally:
            self.model.train(was_training)
        return {"nll_eval": nll}

    # ---- persistence / restart -------------------------------------------

    def save_checkpoint(self, path: str | Path) -> Path:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        state = self.model.state_dict()
        torch.save(
            {
                "model": state,
                "last_h": self.last_h.detach().cpu() if self.last_h is not None else None,
            },
            path / "model.pt",
        )
        torch.save(self.optim.state_dict(), path / "optim.pt")
        rng = {
            "torch_cpu": torch.get_rng_state(),
            "random": random.getstate(),
            "numpy": np.random.get_state(),
        }
        if torch.cuda.is_available():
            rng["torch_cuda"] = torch.cuda.get_rng_state()
        torch.save(rng, path / "rng.pt")
        torch.save(self.memory.state_dict(), path / "episodic.pt")
        torch.save(self.replay.state_dict(), path / "replay.pt")
        meta = {
            "arch": NN0_ARCH,
            "architecture_identity": NN0_ARCH,
            "version": CHECKPOINT_VERSION,
            "seed": self.cfg.seed,
            "params_hash": _hash_state(state),
            "cfg": asdict(self.cfg),
            "vocabulary_id": self.cfg.vocabulary_id,
            "protocol_id": self.cfg.protocol_id,
            "parameter_count": self.parameter_count(),
            "d_hidden": self.cfg.d_hidden,
            "step": self.step_count,
        }
        (path / "meta.json").write_text(json.dumps(meta, indent=2))
        lineage_path = path / "lineage.json"
        if lineage_path.exists():
            lineage = json.loads(lineage_path.read_text())
        else:
            lineage = {
                "prev": None,
                "experiment": self.cfg.experiment_id,
                "run": self.cfg.run_id,
            }
        lineage["last_step"] = self.step_count
        (path / "lineage.json").write_text(json.dumps(lineage, indent=2))
        return path

    @classmethod
    def from_checkpoint(
        cls,
        path: str | Path,
        *,
        expected_protocol_id: Optional[str] = None,
        expected_vocabulary_id: Optional[str] = None,
    ) -> "NN0Trainer":
        path = Path(path)
        meta = json.loads((path / "meta.json").read_text())
        if meta.get("arch") != NN0_ARCH or meta.get("architecture_identity", NN0_ARCH) != NN0_ARCH:
            raise ValueError("checkpoint architecture identity mismatch")
        if int(meta.get("version", -1)) != CHECKPOINT_VERSION:
            raise ValueError("checkpoint version mismatch")
        cfg = NN0Config(**meta["cfg"])
        if meta.get("vocabulary_id", cfg.vocabulary_id) != cfg.vocabulary_id:
            raise ValueError("checkpoint vocabulary identity is inconsistent")
        if meta.get("protocol_id", cfg.protocol_id) != cfg.protocol_id:
            raise ValueError("checkpoint protocol identity is inconsistent")
        if expected_protocol_id is not None and cfg.protocol_id != expected_protocol_id:
            raise ValueError("checkpoint protocol identity mismatch")
        if expected_vocabulary_id is not None and cfg.vocabulary_id != expected_vocabulary_id:
            raise ValueError("checkpoint vocabulary identity mismatch")
        if int(meta.get("d_hidden", cfg.d_hidden)) != cfg.d_hidden:
            raise ValueError("checkpoint d_hidden is inconsistent")
        trainer = cls(cfg)
        bundle = torch.load(path / "model.pt", map_location=trainer.device, weights_only=False)
        if not isinstance(bundle, dict) or "model" not in bundle:
            raise ValueError("checkpoint model bundle is malformed")
        actual_hash = _hash_state(bundle["model"])
        if actual_hash != meta.get("params_hash"):
            raise ValueError(
                f"checkpoint parameter hash mismatch: expected {meta.get('params_hash')}, got {actual_hash}"
            )
        trainer.model.load_state_dict(bundle["model"])
        if bundle.get("last_h") is not None:
            trainer.last_h = bundle["last_h"].to(trainer.device)
        trainer.optim.load_state_dict(torch.load(path / "optim.pt", map_location=trainer.device))
        rngd = torch.load(path / "rng.pt", map_location="cpu", weights_only=False)
        torch.set_rng_state(rngd["torch_cpu"])
        random.setstate(rngd["random"])
        np.random.set_state(rngd["numpy"])
        if "torch_cuda" in rngd and torch.cuda.is_available():
            torch.cuda.set_rng_state(rngd["torch_cuda"])
        trainer.memory.load_state_dict(torch.load(path / "episodic.pt", weights_only=False))
        trainer.replay.load_state_dict(torch.load(path / "replay.pt", weights_only=False))
        trainer.step_count = int(meta["step"])
        lineage_path = path / "lineage.json"
        if not lineage_path.exists():
            raise ValueError("checkpoint lineage is missing")
        lineage = json.loads(lineage_path.read_text())
        if int(lineage.get("last_step", -1)) != trainer.step_count:
            raise ValueError("checkpoint lineage step mismatch")
        if (
            lineage.get("experiment") != cfg.experiment_id
            or int(lineage.get("run", -1)) != cfg.run_id
        ):
            raise ValueError("checkpoint lineage identity mismatch")
        return trainer

    def parameter_count(self) -> int:
        return sum(p.numel() for p in self.model.parameters())
