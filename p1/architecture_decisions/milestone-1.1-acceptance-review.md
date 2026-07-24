# Milestone 1.1 — Acceptance Review

Status: Complete, awaiting explicit human approval before Milestone 2.
Scope executed: exactly the seven authorized Milestone 1.1 work items.
No CLI, no dashboards, no schema/ontology redesign, no new object types,
no parser redesign, no scientific content, no Milestone 2 work.

## 1. Files changed

### Modified

| File | Reason |
|---|---|
| `p1/tooling/p1_os/frontmatter.py` | (a) `_StrictSafeDumper.increase_indent` now forces block-sequence items to indent under their parent key, matching every hand-authored fixture/template, instead of PyYAML's default flush-left style. (b) New `_format_datetime` helper: UTC instants now serialize with a trailing `Z` instead of `+00:00`; non-UTC offsets keep an explicit `±HH:MM`; fractional seconds pass through `isoformat()` unchanged; values remain quoted via the existing `_Quoted` mechanism. |
| `p1/tooling/p1_os/schemas/results.py` | Added an `@model_validator(mode="after")` rejecting `ended_at < started_at`; equal timestamps are accepted. |
| `tests/p1_os/conftest.py` | Removed the `sys.path.insert(0, tooling_dir)` hack now that `p1_os` is pip-installed (editable) from `p1/tooling/pyproject.toml`. The `tests/p1_os` local-helpers path insertion (for `helpers.py`/`payloads.py`, which are not part of the installable package) is unchanged. The `tooling_dir` fixture is retained; `test_isolation.py` still uses it to simulate a pre-installation sys.path-only import. |
| `tests/p1_os/test_frontmatter.py` | Corrected `test_serialization_quotes_datetimes`, which had asserted the old, non-canonical `+00:00` output — it now asserts the canonical `Z` output. Added 8 new regression tests (sequence indentation ×3, datetime serialization ×5). |
| `tests/p1_os/schemas/test_results.py` | Added 4 new regression tests for the `ended_at >= started_at` rule. |

### Created

| File | Reason |
|---|---|
| `p1/methodology/STATUS_LIFECYCLE.md` | Task 4: documents representable schema `status`/`maturity` states (from `enums.py`) versus which transitions the specification authorizes only a `Decision` to make (PI-003, PI-004). Explicitly documentation-only — no enforcement code was added. |
| `p1/tooling/pyproject.toml` | Task 5: makes `p1_os` an installable distribution (`p1-os`, pinned to the same `pydantic==2.13.4` / `PyYAML==6.0.3` already declared in `p1/requirements.txt`), isolated from the root VELYNX `pyproject.toml` (not modified, not read). |
| `tests/p1_os/test_installation.py` | Task 6: 5 new regression tests — installed-distribution metadata, declared dependencies, `pyproject.toml` structure, import with no sys.path insertion from a non-repo cwd, and forbidden-module isolation for the installed package. |
| `p1/architecture_decisions/milestone-1.1-acceptance-review.md` | Task 7: this document. |

### Not modified (confirmed via `git status`)

Root `pyproject.toml`, root/backend `requirements*.txt`, `p1/requirements.txt`, `p1/requirements-dev.txt`, `.gitignore`, all VELYNX/backend/frontend source, all 12 Milestone 1 schema files other than `results.py`, all 12 templates, all `tests/fixtures/p1_os/*` fixtures, and the 8 pre-existing untracked `theory/*` files.

## 2. Environment changes (not repository files)

`pip install --no-deps -e p1/tooling` was run against `.venv`, registering
`p1-os==1.0.0` as an editable distribution. `--no-deps` was used
deliberately so pip would not attempt to re-resolve `pydantic`/`PyYAML`
(their pinned versions in `p1/tooling/pyproject.toml` already match what
`p1/requirements.txt` had already installed). This is an environment
mutation, not a file change, and is reversible with
`pip uninstall p1-os`. `python -m build --outdir <tmp> p1/tooling` was
also run once to confirm sdist/wheel construction; its output was
directed outside the repository and nothing was left behind except the
already-`.gitignore`d `p1_os.egg-info/` from the editable install.

## 3. Tests executed

```
.venv/Scripts/python.exe -m pytest tests/p1_os --collect-only -q
.venv/Scripts/python.exe -m pytest tests/p1_os -q
```

- Baseline (before Milestone 1.1 changes): **365 passed**.
- After Milestone 1.1 changes: **382 passed**, 0 failed, 0 skipped.
  - 365 original tests, all still passing (1 assertion corrected — see
    `test_serialization_quotes_datetimes` above — not removed or
    weakened; it now checks the *fixed* behavior that task 2 required).
  - 17 new regression tests: 8 sequence-indentation/datetime tests in
    `test_frontmatter.py`, 4 ordering tests in
    `schemas/test_results.py`, 5 installation/import tests in
    `test_installation.py`.
- Separately verified: all 12 `p1/templates/*.md` files parse, validate,
  and remain serialization-stable (`serialize(parse(x)) ==
  serialize(parse(serialize(parse(x)))))` after both fixes.
- Separately verified: `pip show p1-os` reports the editable location as
  `p1/tooling`; `python -c "import p1_os"` succeeds from a temp directory
  outside the repository with no sys.path modification; `python -m
  build` produces a wheel and sdist containing only the `p1_os` package.

## 4. Coverage of Milestone 1.1 authorized work

| # | Item | Status |
|---|---|---|
| 1 | Canonical YAML sequence indentation | Done — indented style, verified at top level and nested under a sequence of mappings (`Experiment.prospective_update_rules[].proposed_actions`). |
| 2 | Canonical UTC datetime serialization | Done — UTC → `Z`, non-UTC → explicit `±HH:MM`, fractional seconds preserved, always quoted. |
| 3 | Result validation (`ended_at >= started_at`) | Done — equal timestamps accepted, `ended_at < started_at` rejected, including cross-offset comparison. |
| 4 | Status lifecycle documentation | Done — `p1/methodology/STATUS_LIFECYCLE.md`; no enforcement code added. |
| 5 | Package installation | Done — `p1/tooling/pyproject.toml`; editable install, wheel/sdist build, import outside pytest, and import isolation from VELYNX/backend/frontend/infra all verified. `conftest.py`'s pytest-only path dependency removed. |
| 6 | Regression tests | Done — 17 new tests across the three categories above plus installation/import. |
| 7 | Preserve acceptance review | Done — this document, stored under `p1/architecture_decisions/`. |

## 5. Remaining technical debt / deferred items

These are pre-existing and intentionally out of scope for Milestone 1.1
(unchanged from the Milestone 1 specification, section 10):

- No lifecycle/maturity **transition enforcement** in code — only
  documented (task 4 was documentation-only by design).
- No CLI, ID allocation/retirement, repository scans, relationship
  existence/cycle checks, derived reverse indexes, transaction
  manifests, pilot validation profiles, or Decision-application
  workflow. All remain Milestone 2+ scope, per the `LOCKED` status of
  Milestone 2 and this brief's stop condition.
- `p1/requirements-dev.txt` was deliberately **not** changed to add a
  `-e ./tooling` line: testing showed pip resolves a relative editable
  path in a requirements file relative to the *current working
  directory*, not the requirements file's own directory, which would
  make `pip install -r p1/requirements-dev.txt` silently fail unless
  invoked from `p1/`. Rather than encode that footgun, installation is
  documented here as two explicit steps: `pip install -r
  p1/requirements-dev.txt` (pinned deps) then `pip install -e
  p1/tooling` (the package itself).
- `serialize_metadata` still emits plain (unquoted) scalars for
  free-text fields that some hand-authored fixtures/templates happen to
  have quoted (e.g. `scope: "..."` in the source file becomes
  `scope: ...` on re-serialization). This is unchanged pre-existing
  behavior, out of Milestone 1.1's authorized scope (only sequence
  indentation and datetime formatting were authorized), and does not
  violate the existing round-trip-determinism tests, which check
  `serialize(parse(x)) == serialize(parse(serialize(parse(x))))`, not
  byte-equality against the original hand-authored file.

## 6. Stop condition

Milestone 1.1 work is complete. No Milestone 2 work (CLI, ID allocation,
lifecycle enforcement, transactions, etc.) was started. Awaiting explicit
human approval before any further milestone begins.
