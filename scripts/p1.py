"""`python scripts/p1.py ...` — thin wrapper around the engine CLI.

Responsibility: make the CLI runnable from a source checkout without installing
the package, and nothing else. All argument handling lives in
`experiments/engine/cli.py`; duplicating any of it here would create two places to
fix a bug.

    python scripts/p1.py run   configs/v0/smoke.yaml
    python scripts/p1.py sweep configs/v0/v0_2_matched_updates.yaml --workers 4
    python scripts/p1.py list
"""

from __future__ import annotations

import sys
from pathlib import Path

# A source checkout has no installed package; put the repository root first so
# `core`, `science`, `benchmarks` and `experiments` resolve.
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from experiments.engine.cli import main  # noqa: E402  (path set above)

if __name__ == "__main__":
    raise SystemExit(main())
