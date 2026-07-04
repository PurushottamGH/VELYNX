"""E0: Emergence-vs-injection discrimination.

Central experiment that decides H* — emergence vs injection
on a nonlinear-latent stream.

Submodules:
    dataset.py   — Synthetic nonlinear latent environment generator
    leakage_check.py — Offline nonlinearity verification
    run.py       — Full experiment runner (T, C1, C2, C3 conditions)
    analysis.py  — DV-a (held-out LL) and DV-b (M statistic) computation
    decision.py  — Pass/kill criteria with two-attempt falsification protocol

Reference: PROGRAM_D_CANONICAL.md §7 (E0)
           SCIENTIFIC_EXECUTION_SPEC.md §E0
"""
