# SPRINT1 RETROSPECTIVE

## Timeline of Major Discoveries

Chronological, with dates / commit refs where available.

1. **F1 measurement defect found → fixed.**
   `E0` was initialized against an index-collision metric rather than a
   prediction-quality metric. Sonnet diagnosed the defect in the first
   review pass; the metric was re-pointed before any sprint number was
   stamped on it.
2. **C2 held-out leakage found → fixed.**
   The C2 evaluation set was reachable from the training partition via
   a shared upstream index. Caught during the same review pass as F1;
   the held-out boundary was re-cut before C2 was run for publication.
3. **Commit provenance discrepancy found → resolved.**
   `REVIEW_LOG.md` claimed "Review #002" as a completed review, but
   no matching committed artifact existed at the cited commit. The
   review was either re-run or the log entry was corrected so every
   numbered review maps to a real commit.
4. **Repo size anomaly (`research_artifacts/`) found → resolved.**
   A `git add -A` had staged ~2.2M lines of generated artifacts under
   `research_artifacts/`. The directory was gitignored and the staged
   entries were dropped before they entered history.
5. **n=5 → n=20 power extension.**
   Initial eval runs used n=5 seeds. Power analysis showed this was
   insufficient to distinguish the effect from noise; the cohort was
   extended to n=20 before any "zero events" claim was entertained.
6. **C3 instrumentation gap found → fixed.**
   C3's trigger path was not being logged, so zero-event counts were
   ambiguous between "no effect" and "no opportunity." Instrumentation
   added to the trigger site before C3 was re-run.
7. **C2 coupling artifact found (MiniMax cold-read).**
   A cold, context-free MiniMax review identified a coupling in the C2
   harness (`MiniMax cold-read`) that reviewers who had seen the full
   sprint context had missed.
8. **M-statistic weakness found → stronger self-null spec written.**
   The M-statistic used to reject the null had a known degenerate mode.
   A stronger self-null specification was written to close the gap.
9. **Self-null implementation gap found (2/20 seeds) → verified
   non-reversing.**
   The stronger self-null spec failed on 2 of 20 seeds during
   implementation. The failures were traced and verified to be
   non-reversing (i.e. the spec was correct; the implementation had a
   path that didn't reverse sign under the null) before the spec was
   trusted.
10. **Opus F-A discovery: growth trigger units mismatch; H\* reframed
    from FAIL → UNTESTED.**
    Opus's review found that the growth trigger in F-A was being compared
    in inconsistent units (fractional vs. absolute scale), so the null
    result could not be interpreted as "hypothesis false." H\* was
    reframed from `FAIL` to `UNTESTED` pending a units-consistent
    re-run.
11. **F-B fabrication found and purged.**
    A block of text in F-B asserted results that had no matching run
    artifact. The fabricated block was purged and the section was
    rewritten against the actual run logs.
12. **`decision.py` C-5 fix.**
    The C-5 branch in `decision.py` was corrected to match the reviewed
    specification before the tag was cut.
13. **Tag cut.**
    Sprint 1 tag was cut only after all of the above were resolved and
    reconciled.

## What Each Catch Actually Prevented

One line per major finding — what would have happened if it had NOT
been caught.

- **F1 uncaught** → `E0` would have measured index collisions and called
  it prediction quality.
- **C2 leakage uncaught** → C2 would have reported held-out performance
  that was actually reachable from training, inflating the claim.
- **Provenance discrepancy uncaught** → "Review #002" would have been
  cited as evidence of a review that never existed as a committed
  artifact; provenance would be undecidable later.
- **`research_artifacts/` uncaught** → ~2.2M generated lines would have
  entered history, bloating the repo and making every future clone
  carry the pollution.
- **n=5 uncaught** → a "zero events" claim would have been published
  on a cohort too small to distinguish zero from noise.
- **C3 instrumentation uncaught** → C3's zero-event count would have
  been published as "no effect" when the trigger may never have fired.
- **C2 coupling uncaught (MiniMax)** → the C2 result would have been
  published with a harness coupling that context-familiar reviewers
  had consistently missed.
- **M-statistic weakness uncaught** → the null rejection would have
  relied on a statistic with a known degenerate mode.
- **Self-null implementation gap uncaught** → the "stronger" statistic
  would have been trusted over the thing it replaced while still
  failing its own null on 2/20 seeds.
- **F-A units mismatch uncaught (Opus)** → H\* would have been
  published as `FAIL` when the correct status was `UNTESTED`; a true
  hypothesis would have been killed by a units bug.
- **F-B fabrication uncaught** → fabricated results would have entered
  the publication record with no backing run artifact.
- **`decision.py` C-5 uncaught** → the shipped decision logic would
  have diverged from the reviewed specification at the tagged commit.
- **Tag cut before fixes uncaught** → the sprint tag would have pointed
  at a commit with known-defective metrics, leakage, fabrication, and
  a broken decision branch.

## Lessons Learned, by Category

### Engineering
- Generated artifacts must be gitignored from day one. A single
  `git add -A` nearly polluted history with ~2.2M lines under
  `research_artifacts/`.
- Review infrastructure (numbered reviews, REVIEW_LOG entries) is
  itself a system that can lie. Claimed reviews must point at real
  commits.

### Scientific
- Zero events across many seeds can mean "hypothesis false" OR
  "manipulation never had a chance to occur" — always check the
  trigger's units and instrumentation before interpreting a null.
- A null result is only as strong as the power analysis behind it; n=5
  was insufficient and was extended to n=20 before any zero-events
  claim was entertainable.

### Review process
- Cold, context-free reviews (MiniMax, later Opus) found defects that
  reviewers who had seen the whole conversation had missed.
  Familiarity is a blind spot, not just an efficiency gain.
- A cold read should be treated as a first-class review artifact, not
  a sanity check; the MiniMax C2 cold-read caught a coupling that
  context-familiar reviewers had repeatedly passed.

### Statistics
- An unverified "stronger" statistic can itself need its own
  verification before being trusted over the thing it replaced. The
  stronger self-null spec failed on 2/20 seeds during implementation
  and had to be verified non-reversing before adoption.
- Reframing a result (H\* `FAIL` → `UNTESTED`) is a legitimate
  statistical outcome, not a downgrade; the alternative was
  publishing a false negative.

### Documentation
- Claimed reviews (e.g. Review #002) must correspond to committed
  artifacts, or provenance becomes undecidable later.
- Status labels (`FAIL`, `UNTESTED`, `PASS`) must be reconciled
  against run artifacts, not asserted in prose. F-B had asserted
  results with no backing run.

## What Specifically Prevented a False Publication

- **Sonnet's F1 diagnosis** — re-pointed `E0` from index collisions to
  prediction quality before any sprint number was stamped.
- **The citation-drift / provenance catch** — reconciled Review #002's
  claimed review to a committed artifact so later citations could not
  point at a review that never existed.
- **MiniMax's C2 cold-read** — caught a harness coupling that
  context-familiar reviewers had missed.
- **MiniMax's self-null critique** — exposed the M-statistic's
  degenerate mode and forced a stronger self-null spec.
- **Opus's F-A reframe** — reframed H\* from `FAIL` to `UNTESTED` on
  growth-trigger units mismatch, preventing a true hypothesis from
  being killed by a units bug.
- **The F-B fabrication purge** — removed an asserted-results block
  with no backing run artifact before it could enter the publication
  record.
- **The `decision.py` C-5 fix** — brought the shipped decision logic
  back in line with the reviewed specification before the tag was cut.

## Pipeline Improvements for Every Future Sprint

- **Documentation reconciliation as a standing step, not an ad hoc
  fix.** Every claimed review, status label, and citation must map
  to a committed artifact at the time it is written.
- **Power analysis required before any "zero events" claim.** No
  zero-events result is publishable without a prior power analysis
  justifying the cohort size.
- **At least one cold, context-free review per major finding.** A
  reviewer who has not seen the sprint conversation must review each
  major finding before it is tagged.
- **Publication review specifically hunting for units/scale
  mismatches, not just statistical validity.** Units and scale checks
  are a distinct pass from statistical validity; the F-A catch was a
  units mismatch, not a stats failure.
- **Research Director review as the final, single-use gate — never
  spent on intermediate debugging.** The Director review is the last
  gate before the tag, not a debugging resource to be consumed
  mid-sprint.
