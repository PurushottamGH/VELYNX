"""P1-ARC playgarden: isolated environment for the NN-0 line.

Experimental, isolated surface. This package is deliberately **stdlib-only**
(no numpy, no torch, no import of ``core``/``experiments``/``ros``) so that
the environment and its probes are independently executable and deterministic
across machines. It implements only *generators and probes*:

- deterministic symbolic generators for sequence, composition and relation
  tasks, where the held-out split is **by construction** (different seed-time
  rule draws, never a random split of one pool);
- held-out probes with the property that an exact string/n-gram lookup over
  the training corpus cannot answer them (proven by tests);
- symbol-renaming / permutation probes, compositional-generalization probes,
  an anti-memorization control, and a memory-zero evaluation harness.

The user-facing entry point is ``python -m p1.live.neural.playgarden``.

References
----------
- ``outputs/P1_LIVE_NN_NEURAL_ARCHITECTURE.md`` section 2 (P1-ARC playgarden,
  held-out split by construction, symbol-anonymity, three protocols).
- ``outputs/P1_LIVE_NN_HOSTILE_ROADMAP.md`` P1-LN-DEC / P1-LN-DEC-2: the
  composition + relabeled holdout; memory-zero ablation N1.

Boundary rule
-------------
Nothing in this package writes a canonical record, trains a network, or imports
any production scientific module. Registering mechanisms, changing schemas and
/training NN-0 are explicit non-goals of this package.
"""

from p1.live.neural.playgarden import alphabet, memory, probes, rules, verification, worlds

__all__ = ["alphabet", "probes", "rules", "verification", "worlds", "memory"]