"""P1 Research Operating System.

The operating system *around* the frozen P1-v2 architecture. It does not
implement, redesign, or depend on the engine: `ros` must never import `v2`,
`experiments.engine`, `core`, or `observatory` runtime code, because Article L-8
of the Constitution Lock forbids evidence-tier records from entering a runtime
computation and the cleanest enforcement of that is a package boundary.
"""

__version__ = "1.0.0"
