"""AFFINE-MSAT(ℤ₁₇) Benchmark Generator & C3/C2 Experimental Infrastructure.

Implements the deterministic AFFINE-MSAT over ℤ₁₇ benchmark layer strictly within
the Architect domain, as specified in P1_LIVE_NN_AFFINE_MSAT_FINAL_PREREGISTRATION_AUDIT.md.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

# Modulus and Algebraic Constants
MODULUS = 17
UNITS = tuple(range(1, MODULUS))      # 1..16
TRANSLATIONS = tuple(range(MODULUS))  # 0..16
NUM_AFFINE_OPS = len(UNITS) * len(TRANSLATIONS)  # 16 * 17 = 272

# Token Space Layout
TOKEN_WRITE = 17
TOKEN_QUERY = 18
HEADER_VOCAB_SIZE = 19


@dataclass(frozen=True)
class AffineOp:
    """Affine operation f_{a,b}(x) = (a*x + b) mod 17."""
    op_id: int
    a: int
    b: int

    def apply(self, x: int) -> int:
        return (self.a * x + self.b) % MODULUS


def build_affine_op_table() -> Tuple[AffineOp, ...]:
    """Construct the canonical table of 272 Affine operations over Z_17."""
    ops: List[AffineOp] = []
    op_id = 0
    for a in UNITS:
        for b in TRANSLATIONS:
            ops.append(AffineOp(op_id=op_id, a=a, b=b))
            op_id += 1
    return tuple(ops)


AFFINE_OPS_TABLE = build_affine_op_table()


@dataclass(frozen=True)
class AffineEpisode:
    """Single write episode in an AFFINE-MSAT stream."""
    key: int
    op_id: int
    a: int
    b: int

    def to_tokens(self, key_offset: int, op_offset: int) -> Tuple[int, int, int]:
        return (TOKEN_WRITE, key_offset + self.key, op_offset + self.op_id)


@dataclass(frozen=True)
class AffineProbe:
    """Probe asking for final state S_T(key_q)."""
    key_q: int
    target: int
    query_context: Tuple[int, int]  # (TOKEN_QUERY, key_offset + key_q)


@dataclass
class AffineMSATInstance:
    """Single self-contained AFFINE-MSAT session instance."""
    instance_id: str
    num_keys: int
    initial_state: Dict[int, int]
    episodes: List[AffineEpisode]
    probes: List[AffineProbe]
    distractor_episodes: List[AffineEpisode]
    
    def render_tokens(self, num_keys: int) -> List[int]:
        key_offset = HEADER_VOCAB_SIZE
        op_offset = HEADER_VOCAB_SIZE + num_keys
        tokens: List[int] = []
        for ep in self.episodes:
            tokens.extend(ep.to_tokens(key_offset, op_offset))
        return tokens


@dataclass
class OrderSwapPair:
    """Paired H1 and H2 streams with order-swap applied to non-commutative operations."""
    pair_id: str
    h1_instance: AffineMSATInstance
    h2_instance: AffineMSATInstance
    swapped_key: int
    op_i: AffineOp
    op_ip1: AffineOp
    y_h1: int
    y_h2: int
    
    def verify_invariants(self) -> bool:
        """Verify that H1 and H2 have identical multiset, length, and marginals but different target."""
        t1 = self.h1_instance.render_tokens(self.h1_instance.num_keys)
        t2 = self.h2_instance.render_tokens(self.h2_instance.num_keys)
        if len(t1) != len(t2):
            return False
        if sorted(t1) != sorted(t2):
            return False
        if self.y_h1 == self.y_h2:
            return False
        if self.h1_instance.probes[0].query_context != self.h2_instance.probes[0].query_context:
            return False
        return True


@dataclass
class AffineMSATCorpus:
    """Complete AFFINE-MSAT corpus with metadata and seed isolation."""
    seed: int
    num_keys: int
    num_episodes: int
    instances: List[AffineMSATInstance]
    order_swap_pairs: List[OrderSwapPair]
    vocab_size: int
    fingerprint: str


def compute_task_state_bits(num_keys: int) -> float:
    return num_keys * math.log2(MODULUS)


def compute_task_state_nats(num_keys: int) -> float:
    return num_keys * math.log(MODULUS)


def generate_instance(
    rng: random.Random,
    instance_id: str,
    num_keys: int,
    num_episodes: int,
) -> AffineMSATInstance:
    """Generate one deterministic AFFINE-MSAT session instance."""
    # Random initial state per key S_0(k) ~ U(Z_17)
    s0: Dict[int, int] = {k: rng.randrange(MODULUS) for k in range(num_keys)}
    state: Dict[int, int] = dict(s0)
    episodes: List[AffineEpisode] = []
    key_write_counts: Dict[int, int] = {k: 0 for k in range(num_keys)}

    for _ in range(num_episodes):
        k = rng.randrange(num_keys)
        op = rng.choice(AFFINE_OPS_TABLE)
        state[k] = op.apply(state[k])
        key_write_counts[k] += 1
        episodes.append(AffineEpisode(key=k, op_id=op.op_id, a=op.a, b=op.b))

    # Generate distractor episodes (for C2 matched exposure)
    distractor_episodes: List[AffineEpisode] = []
    for _ in range(num_episodes):
        k = rng.randrange(num_keys)
        op = rng.choice(AFFINE_OPS_TABLE)
        distractor_episodes.append(AffineEpisode(key=k, op_id=op.op_id, a=op.a, b=op.b))

    active_keys = [k for k, count in key_write_counts.items() if count > 0]
    if not active_keys:
        active_keys = list(range(num_keys))
        
    key_q = rng.choice(active_keys)
    target = state[key_q]

    key_offset = HEADER_VOCAB_SIZE
    probe = AffineProbe(
        key_q=key_q,
        target=target,
        query_context=(TOKEN_QUERY, key_offset + key_q),
    )

    return AffineMSATInstance(
        instance_id=instance_id,
        num_keys=num_keys,
        initial_state=s0,
        episodes=episodes,
        probes=[probe],
        distractor_episodes=distractor_episodes,
    )


def generate_order_swap_pair(
    rng: random.Random,
    pair_id: str,
    num_keys: int,
    num_episodes: int,
) -> OrderSwapPair:
    """Generate an explicit order-swap pair (H1, H2) with identical query and token multiset."""
    while True:
        inst1 = generate_instance(rng, f"{pair_id}_h1", num_keys, num_episodes)
        key_q = inst1.probes[0].key_q
        
        q_writes = [i for i, ep in enumerate(inst1.episodes) if ep.key == key_q]
        if len(q_writes) < 2:
            continue
            
        swap_idx = -1
        for idx in range(len(q_writes) - 1):
            i1, i2 = q_writes[idx], q_writes[idx + 1]
            if i2 == i1 + 1:
                ep1, ep2 = inst1.episodes[i1], inst1.episodes[i2]
                if ((ep2.a - 1) * ep1.b) % MODULUS != ((ep1.a - 1) * ep2.b) % MODULUS:
                    swap_idx = i1
                    break
        
        if swap_idx == -1:
            continue
            
        episodes_h2 = list(inst1.episodes)
        episodes_h2[swap_idx], episodes_h2[swap_idx + 1] = (
            episodes_h2[swap_idx + 1],
            episodes_h2[swap_idx],
        )
        
        state_h2 = dict(inst1.initial_state)
        for ep in episodes_h2:
            state_h2[ep.key] = (ep.a * state_h2[ep.key] + ep.b) % MODULUS
                
        target_h2 = state_h2[key_q]
        if target_h2 == inst1.probes[0].target:
            continue
            
        key_offset = HEADER_VOCAB_SIZE
        inst2 = AffineMSATInstance(
            instance_id=f"{pair_id}_h2",
            num_keys=num_keys,
            initial_state=dict(inst1.initial_state),
            episodes=episodes_h2,
            probes=[AffineProbe(key_q=key_q, target=target_h2, query_context=(TOKEN_QUERY, key_offset + key_q))],
            distractor_episodes=list(inst1.distractor_episodes),
        )
        
        op1 = AFFINE_OPS_TABLE[inst1.episodes[swap_idx].op_id]
        op2 = AFFINE_OPS_TABLE[inst1.episodes[swap_idx + 1].op_id]
        
        pair = OrderSwapPair(
            pair_id=pair_id,
            h1_instance=inst1,
            h2_instance=inst2,
            swapped_key=key_q,
            op_i=op1,
            op_ip1=op2,
            y_h1=inst1.probes[0].target,
            y_h2=target_h2,
        )
        assert pair.verify_invariants(), "OrderSwapPair failed invariant check!"
        return pair


def build_affine_msat_corpus(
    seed: int = 42,
    num_instances: int = 100,
    num_keys: int = 8,
    num_episodes: Optional[int] = None,
) -> AffineMSATCorpus:
    """Build a complete deterministic AFFINE-MSAT corpus with Defect Repair scaling."""
    if num_episodes is None:
        num_episodes = max(64, num_keys * 6)

    rng = random.Random(seed)
    instances: List[AffineMSATInstance] = []
    order_swap_pairs: List[OrderSwapPair] = []

    for idx in range(num_instances):
        inst = generate_instance(rng, f"inst_{idx}", num_keys, num_episodes)
        instances.append(inst)

    for idx in range(min(num_instances // 2, 20)):
        pair = generate_order_swap_pair(rng, f"pair_{idx}", num_keys, num_episodes)
        order_swap_pairs.append(pair)

    vocab_size = HEADER_VOCAB_SIZE + num_keys + NUM_AFFINE_OPS

    fingerprint_data = {
        "seed": seed,
        "num_keys": num_keys,
        "num_episodes": num_episodes,
        "num_instances": len(instances),
        "vocab_size": vocab_size,
        "sample_targets": [inst.probes[0].target for inst in instances[:10]],
    }
    fingerprint = hashlib.sha256(json.dumps(fingerprint_data, sort_keys=True).encode("utf-8")).hexdigest()

    return AffineMSATCorpus(
        seed=seed,
        num_keys=num_keys,
        num_episodes=num_episodes,
        instances=instances,
        order_swap_pairs=order_swap_pairs,
        vocab_size=vocab_size,
        fingerprint=fingerprint,
    )
