"""P1 v0 — minimal continual-learning measurement rig.

Version-pinned package. v0 is frozen once its milestones pass; v1 is added
alongside it so successive designs can be benchmarked against each other
without migration.

Modules have exactly one responsibility each:
    stream  -- generate a non-stationary task stream (deterministic)
    model   -- predict / learn
    memory  -- store / sample past events
    gate    -- decide how much replay to perform this step
    loop    -- wire the above into one step
    probe   -- frozen-model evaluation on held-out per-task data
    metrics -- aggregate losses into retention / forgetting
    runner  -- config -> run -> artifacts (only module doing IO)
"""

__version__ = "0.0.1"
