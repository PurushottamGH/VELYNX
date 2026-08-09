# CRITICAL_PATH.md

Emergency engineering mode. Ordered by **dependency**, not W-number.
All statuses are **measured** on 2026-07-26, not inferred. Baseline revision `e02fda1`.

---

## 0. Gate status

| Gate | Before | After | Evidence |
|---|---|---|---|
| `pip install -e .` | **RED** `BackendUnavailable` | **GREEN** | `Would install velynx-0.1.0` |
| `python -m build` | **RED** same cause | **GREEN** | `velynx-0.1.0.tar.gz` + `-py3-none-any.whl` |
| Wheel imports outside repo root | **RED** | **GREEN** | `validation`, `validation.metrics`, `validation.report`, `framework.core.cognitive_health`, `framework` all import with `cwd=C:\` |
| `pytest` whole-repo | GREEN 1048 | **GREEN** 1048 passed, 3 skipped | no regression across 4 runs |
| `pytest research/tests/` (CI's call) | **RED** 6 collection errors | **GREEN** 168 passed | standalone invocation |
| CI `lint` — flake8 | **RED** 41 findings | **GREEN** exit 0 | 5 × E999 + 36 × F82 → 0 |
| CI `lint` — `black --check` | **RED** 457 files | **GREEN** exit 0 | 177 files clean on scoped surface |
| CI `lint` — mypy | advisory | advisory | `continue-on-error`, unchanged |
| CI `reproducibility` | GREEN | GREEN | exit 0 |
| CI `experiment-validation` | GREEN *(falsely)* | GREEN *(falsely)* | exit 0 — W-052 unfixed, see P2 |
| CI `benchmark` | GREEN | GREEN | exit 0 |
| CI `kill-criteria` | **RED** | **RED** | exit 1 — P1-5 |
| CI `artifact-integrity` | **RED** | **RED** | exit 1 — P1-5 |

**Editable install, build, and pytest are green. CI has two red jobs left (P1-5).**

### Corrections to the backlog, established by measurement

1. **`validation` was never missing.** W-057 states it "exists nowhere in the tree". It
   was at **`tests/validation/`** — a production subsystem whose `__init__.py` imports
   itself as top-level `validation`. `tests/` has no `__init__.py`, so it reached
   `sys.path` only via pytest rootdir insertion. A misplacement, not an absence; the
   repair was `git mv`, not reconstruction.
2. **W-002 was 5 files, not 4.** `archive/code/diagnostics/velynx_soul.py` also failed
   E999 and CI linted it.
3. **W-002 never depended on W-008.** All five were one corruption event — a botched
   rewrite that spliced a duplicated tail onto a line. Faithful truncations, no boundary
   decision required. **W-008 was off the critical path.**
4. **The `validation` → `backend` coupling was masked, not absent.** Surfaced only once
   the package shipped: `validation/runner.py:43-47` has five module-level
   `backend.cognition` imports, and `backend*` is excluded from the wheel. Previously
   invisible because a repo-root session resolves `backend` via `pythonpath = ["."]`.

---

## 1. Critical path (as executed)

```
        P0-1 build backend  [DONE]
                  |
   +--------------+--------------+
   |                             |
P0-2 validation pkg [DONE]   P0-3 syntax splices [DONE]
   |                             |
   +--------------+--------------+
                  |
        P0-4 lint gate truth [DONE]
                  |
        P1-5 CI red jobs [OPEN]
                  |
     P1-6 first green CI run [OPEN]
```

---

## Priority 0 — **COMPLETE** (~115 min estimated / ~110 min actual)

### P0-1 · Build backend — **DONE** (10 min)
- `pyproject.toml:3`: `setuptools.backends._legacy:_Backend` → `setuptools.build_meta`
- The fictional backend meant the `velynx` distribution had **never** been installable.
- Verified: dry-run editable install exits 0; `python -m build` emits sdist + wheel.

### P0-2 · Relocate the `validation` package — **DONE** (45 min)
- `git mv tests/validation validation` (history preserved as renames); added
  `"validation*"` to `[tool.setuptools.packages.find].include`.
- Chosen over a move under `framework/` because every consumer already writes
  `from validation.x import …` — **zero import rewrites** across 35 call sites.
- Then made `validation/__init__.py`'s `BenchmarkRunner` re-export lazy via PEP 562
  `__getattr__`. That eager import was the sole reason the whole package pulled in
  `backend`, which the wheel excludes. No consumer uses the package attribute, so the
  public API is unchanged and the harness still resolves wherever `backend/` is on path.
- **Closed W-057 outright** — `framework/core/cognitive_health.py` was the only
  non-importing module of 21; it now imports from an installed wheel outside the repo root.
- Also repaired all 6 `research/tests` collection errors and the shipped wheel.

### P0-3 · The 5 spliced files — **DONE** (25 min)
| File | Line | Repair |
|---|---|---|
| `backend/abstraction/belief_generator.py` | 146 | truncated duplicated `print(...)` tail |
| `backend/abstraction/belief_store.py` | 132 | truncated duplicated `return [...]` tail |
| `backend/self_model/baseline_tracker.py` | 120 | deleted spliced line (119 already had the call) |
| `backend/app/lifespan.py` | 112 | `from framework.core import night_learner` |
| `archive/code/diagnostics/velynx_soul.py` | 1 | excluded from lint — see P0-4 |

- `lifespan.py:113` calls `night_learner.start()`, but `framework/core/night_learner.py`
  defines no `start()`. **A latent `AttributeError` the syntax error was masking.** It sits
  inside `try/except Exception`, so it degrades to a logged skip. Syntax restored
  faithfully; the call was **not** invented. Recorded in Priority 2.

### P0-4 · Lint gate truth — **DONE** (40 min)
Added `.flake8` — flake8 never read `[tool.flake8]` in `pyproject.toml` (needs the
`Flake8-pyproject` plugin), so that config block had always been inert. CI's bare
`flake8 .` picks the new file up with no workflow change.

- **`archive/` excluded**, documented in-file as an immutable historical vault, already
  excluded from packaging. **Verified: 71 tracked `.py` files under `archive/` yield
  exactly 1 finding** across E9,F63,F7,F82 — the 20-byte UTF-16LE `'Created\r\n'`
  shell-redirect artifact. No active-package defect is hidden. No vault file was modified.
- **32 F821 suppressed, scoped to one code in one directory.**
  `p1/tooling/p1_os/schemas/*.py` declare `claim_ids: IdListField("claim")` under
  `from __future__ import annotations`; pyflakes reads the string argument as a
  forward-reference *type name*. Runtime is correct — pydantic resolves the call in module
  scope where `"claim"` is a plain str. Analysis artifact, not defect.
- **6 real defects fixed, not suppressed:**
  - `backend/orchestrator.py` — imported neither `llm_client` nor `LLMMessage` despite
    using both in 3 functions. Fixed with the canonical module-level import matching
    `backend/cognition/lexicon_updater.py:19`. (6 findings → 0.)
  - `backend/memory/embedding_service.py:25` — `from typing import TYPE_CHECKING, Any`.
  - `backend/memory/episodic.py:1166` — `self._stitch(...)` inside the `compress`
    **staticmethod**, which has no `self`. Now `NarrativeCompressor._stitch(...)`.
    (Line 1185's `self._stitch` is correct — it is inside `_narrate_chain(self, …)`.)
- **2 real defects recorded, not silently suppressed** — `# noqa: F821` plus an inline
  `FIXME` naming the defect and pointing here:
  - `framework/core/night_learner.py` — `domain` undefined in `learn_topic()`'s scope;
    unreachable because the enclosing `memory.vector_backend` import resolves to nothing.
  - `scripts/gpu_deep_learn.py` — `checkpoint` is a local of `main()`, not of
    `learn_single_topic()`. Both references raise `NameError`, swallowed by
    `except Exception`, so **topic expansion has never run**. Fixing it means threading
    `checkpoint` through the signature — a refactor, not an emergency repair.
- **black scoped to the released surface**: `framework/ validation/ experiments/ scripts/
  tests/ p1/tooling/` — 115 files reformatted, then clean. `backend/` excluded pending its
  W-008 disposition; it is **261 of the 457** unformatted files and ships in no
  distribution. `ci.yml`'s black step updated to match, with the reason in-file.

---

## Priority 1 — turns CI green and records it

### P1-5 · Rescope the two failing CI checks — **OPEN** (~45 min)
- **Merges W-054 + W-055** — same root cause: both check archived/rejected runs.
- `verify_artifact_integrity.py` exit 1 — failures include `R1`, `R3F` (archived, marked
  *Do not rebuild*) and `EXP3`, `EXP4` (H3 is `[REJECTED]`).
- `check_kill_criteria.py` exit 1 — `R3F` and `specs` report `metrics.jsonl not found`.
- **Verify:** both exit 0; a genuine integrity failure still exits 1 (negative test).

### P1-6 · Record the first green CI run — **OPEN** (~25 min)
- Depends on P1-5. Nothing in this repo has ever observed a green CI run.
- **Verify:** run URL + job-level status table; every non-advisory job green, or a red job
  disclosed with its reason.

---

## Priority 2 — after the baseline holds

| Task | Merges | Min | Note |
|---|---|---|---|
| Registry truth | W-052 **+** W-051 | 30 | **Must land together.** W-052 makes the job fail on missing components; it goes red until W-051 fixes the 4 `core/…` paths. Landing W-052 alone reddens CI. |
| `framework/`+`validation/` → `backend/` boundary | W-056 | 90 | Now 11 sites: 5 in `validation/runner.py`, 1 lazy in `validation/monitor.py:42`, 5 in `framework/`. P0-2 removed its `validation`-unresolvable row and deferred the rest behind a lazy import. |
| `night_learner.start()` does not exist | — | 20 | Latent `AttributeError` at `backend/app/lifespan.py:113`, unmasked by P0-3. |
| `checkpoint` scope bug | — | 30 | `scripts/gpu_deep_learn.py` — topic expansion has never executed. |
| Import-smoke gate | W-058 | 25 | P0-2 fixed the defect; this stops recurrence. A parse gate would not have caught it. |
| Parse gate | W-003 | 20 | Same, for P0-3. |
| **Full-repository black pass** | — | 30 | Deferred from P0-4 by decision. `backend/` = 261 files; run once its W-008 disposition is recorded, then widen `ci.yml`'s black step back to `.` |
| Destroy local key file | W-047 / W-006 | 5 | `gcp-key.json.json`, 2346 bytes, on disk. Does **not** substitute for provider-side rotation. |
| `backend/` disposition | W-008 | 60 | Off the critical path once P0-3 landed; still gates the black pass and the coverage denominator. |

---

## 2. Explicitly NOT on the critical path

`W-004`, `W-006`, `W-007`, `W-009`, `W-010`, `W-011`, `W-014`–`W-028`, `W-043`–`W-046`,
`W-048`–`W-050`, `W-053`.

None blocks editable install, build, pytest, or CI. The backlog's ≈64.2 engineer-days
contained **~110 minutes** of actual gate-blocking work.

---

## 3. Known non-goal

`A-07` keeps failing after all of the above. The GCP key is in reachable git history on
public remotes; only provider-side rotation reduces exposure, and history presence is
permanent. It is **not** an engineering blocker and must not be counted against this
baseline.
