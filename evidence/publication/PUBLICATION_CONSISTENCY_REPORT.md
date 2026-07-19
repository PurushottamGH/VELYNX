# Publication Consistency Report — Sprint 1 Documentation Audit

**Scope:** All Sprint 1 documentation in VELYNX repository as of 2026-07-05
**Focus:** Consistency, terminology, references, citation integrity, contradictory wording

---

## Remaining Inconsistencies

### 1. n=5 vs n=20 Evidence Package Drift (Critical)
**Files:** `evidence/05_metrics.json` vs `evidence/01_manifest.json`, `evidence/06_statistical_results.md`, `evidence/11_power_analysis.md`, `evidence/12_m_recomputation.md`
- `05_metrics.json` reports Sprint 1.1.1 (5 seeds): `num_seeds: 5`, `total_mdl_checks: 90`, `verdict: "FAIL (DV-a)"`, `dv_b_pass: true`
- `01_manifest.json` reports Sprint 1.2 (20 seeds): `num_seeds: 20`, `t_per_step_log_count: 360`, `c3_per_step_log_count: 360`, `verdict: "H* UNTESTED"`, `dv_b_self_null_pass: false`
- `06_statistical_results.md` and `12_m_recomputation.md` describe n=20 results with self-null M = -0.6055 (FAIL)
- `11_power_analysis.md` retains n=5 table "for historical reference" but n=20 is "definitive"
- **Manifest notes:** "config.json's num_seeds field shows 5 due to a known parsing quirk"

### 2. DV-a Verdict Terminology Contradiction (Critical)
**Files:** `evidence/05_metrics.json` vs `evidence/06_statistical_results.md`, `FINAL_PUBLICATION_CLAIM.md`, `LIMITATIONS.md`, `RESEARCH_DIRECTOR_DECISION.md`
- `05_metrics.json`: `"verdict": "FAIL (DV-a)"` — implies H* was tested and failed
- `06_statistical_results.md`: `"DV-a verdict: UNTESTED (not FAIL)"`
- `FINAL_PUBLICATION_CLAIM.md`: "Sprint 1 did not test H*. The result is 'H* untested,' not a hypothesis that was tested and failed."
- `LIMITATIONS.md`: "DV-a (primary outcome) is untested, not failed"
- `RESEARCH_DIRECTOR_DECISION.md`: "Reject any statement that Sprint 1 tested, supported, or falsified H*"
- `SPRINT1_FINAL_REPORT.md`: "All four Sprint 1 blockers are resolved. Sprint 1 engineering: COMPLETE" — no mention of H* untested

### 3. DV-b Verdict Terminology Contradiction (Critical)
**Files:** `evidence/05_metrics.json` vs `evidence/06_statistical_results.md`, `evidence/12_m_recomputation.md`, `LIMITATIONS.md`, `FINAL_PUBLICATION_CLAIM.md`
- `05_metrics.json`: `"dv_b_pass": true`, `"margin_source": "data_derived"` (0.0511 margin)
- `06_statistical_results.md`: "DV-b verdict: NO TRUSTWORTHY POSITIVE EMERGENCE", margin 0.0440 (C3 null)
- `12_m_recomputation.md`: Self-null M = -0.6055 (FAIL, margin 0.0896); C3-null PASS is "methodological artifact"
- `LIMITATIONS.md`: "M = 0.2949 PASS is sensitive to null reference... under self-null M = -0.6055... FAIL by wide margin"
- `FINAL_PUBLICATION_CLAIM.md`: "DV-b shows no trustworthy positive emergence... original PASS was C3-shuffle artifact"

### 4. C2 Control Independence Misrepresentation
**Files:** `SPRINT1_FINAL_REPORT.md` vs `LIMITATIONS.md`, `SPRINT_1.3_PREREGISTRATION.md`, `evidence/06_statistical_results.md`
- `SPRINT1_FINAL_REPORT.md`: "C2 capacity-matched to T (same growth count, random timing)" — frames as successful control
- `LIMITATIONS.md`: "C2 did not function as an independent random-growth control. Its growth count was derived from Treatment's observed growth events... C2's growth count was structurally forced to zero by construction"
- `SPRINT_1.3_PREREGISTRATION.md`: Confirms C2 receives `t_growth_count` from T; "C2f must NOT do this"
- `06_statistical_results.md`: "T == C1 == C2 for ALL 20 seeds... growth=0 across every seed"

### 5. Sprint Numbering Inconsistency
**Files:** Multiple
- `SPRINT1_FINAL_REPORT.md`: "Sprint 1" (no sub-version)
- `evidence/10_sprint_report.md`: "Sprint 1.1.1 — Final Reconciliation Report"
- `evidence/02_git_diff_summary.md`: "Sprint 1.1.1 — C2 Data Leakage Fix (Post-Audit)"
- `evidence/06_statistical_results.md`: "Sprint 1.2 20-Seed Extension"
- `SPRINT_1.3_PREREGISTRATION.md`: "SPRINT 1.3 — Preregistration: Forced-Growth Condition (C2f)"
- `SPRINT1_RETROSPECTIVE.md`: References "Sprint 1.1", "Sprint 1.2", "Sprint 1.3" interchangeably
- `RESEARCH_DIRECTOR_DECISION.md`: "Sprint 1 = E0 (H*) implementation + n=20 run" (no sub-versions)

### 6. Architecture/Experiment Description Fabrication (F-B — Claimed Resolved)
**Files:** `RESEARCH_DIRECTOR_DECISION.md` (F-B finding) vs `ABSTRACT_LANGUAGE.md`, `FINAL_PUBLICATION_CLAIM.md`, `LIMITATIONS.md`
- `RESEARCH_DIRECTOR_DECISION.md` documents F-B: "Publication docs describe an architecture that was never run... ABSTRACT_LANGUAGE.md: 'Parity-Lite, Transformer, 20M params'... FINAL_PUBLICATION_CLAIM.md: 'single architecture (20M Transformer)'... LIMITATIONS.md: 'λ_base=20.0, λ_budget=0.5'"
- `RESEARCH_DIRECTOR_DECISION.md` claims "[RESOLVED 2026-07-04: fabricated terms purged from all three docs]"
- Current `ABSTRACT_LANGUAGE.md` describes "Dirichlet–Markov conjugate predictor (initial capacity k=2)" — appears corrected
- Current `FINAL_PUBLICATION_CLAIM.md` references F-A trigger defect but no Transformer mention — appears corrected
- Current `LIMITATIONS.md` describes "Dirichlet–Markov, k=2" and "λ_model = k·b + n·log₂N" — appears corrected
- **Status:** Appears resolved but no git verification provided in docs

### 7. MiniMax Cold Read Provenance Contradiction
**Files:** `SPRINT1_RETROSPECTIVE.md` vs `RESEARCH_DIRECTOR_DECISION.md`
- `SPRINT1_RETROSPECTIVE.md` items 7, 37-38: "C2 coupling artifact found (MiniMax cold-read)... MiniMax's C2 cold-read caught a coupling that context-familiar reviewers had missed"
- `RESEARCH_DIRECTOR_DECISION.md` §48: "MiniMax 'independent cold read': NOT PRESENT in the repository (no matching file under any tracked path; see F-G). This decision proceeds without it and must be revisited if it is delivered."
- Direct contradiction: Retrospective claims it happened; Research Director says it's not in repo

### 8. Decision.py C-5 Fix Status Ambiguity
**Files:** `SPRINT1_RETROSPECTIVE.md` vs `RESEARCH_DIRECTOR_DECISION.md`
- `SPRINT1_RETROSPECTIVE.md` items 12, 62-67: "decision.py C-5 fix — two commits... fd7aabf... 2b5644a... closure commit... before the closure tag was cut"
- `RESEARCH_DIRECTOR_DECISION.md` C-5: "Restate the E0 verdict as 'H* untested; attempts-toward-kill = 0; trigger defect found' wherever 'FAIL (DV-a)' implies an H* result (F-C)" — listed as required correction
- Retrospective says fixed; Research Director says still required

### 9. Seed Count Terminology Drift
**Files:** `SPRINT1_FINAL_REPORT.md`, `SPRINT_QUEUE.md`, `SPRINT_1.3_PREREGISTRATION.md`, `evidence/11_power_analysis.md`
- `SPRINT1_FINAL_REPORT.md`: "Default Seeds >= 5", "DEFAULT_CONFIG.num_seeds = 5", "experiment_registry.yaml updated with num_seeds: 5"
- `SPRINT_QUEUE.md`: "Sprint 1's lesson: defaulting to n=5 gives 44% chance of missing a 15% effect rate"
- `SPRINT_1.3_PREREGISTRATION.md`: Same n=5 lesson, then "Preregistered n = 22 seeds"
- `11_power_analysis.md`: "current result is 0/20 growth events (extended from 0/5 in Sprint 1.1.1)"
- `01_manifest.json`: `num_seeds: 20` (actual run)
- Ambiguity: "default vs actual run size not clearly distinguished in final report

### 10. Growth Event Count / MDL Check Count Inconsistency
**Files:** `SPRINT1_FINAL_REPORT.md`, `evidence/05_metrics.json`, `evidence/01_manifest.json`, `evidence/06_statistical_results.md`, `evidence/growth_diagnostics.md`
- `SPRINT1_FINAL_REPORT.md`: "C2 capacity-matched to T (same growth count, random timing)" — no absolute numbers
- `05_metrics.json` (n=5): `total_mdl_checks: 90`, `growth_events: 0`
- `01_manifest.json` (n=20): `t_per_step_log_count: 360`, `c3_per_step_log_count: 360`, `growth_events: 0`
- `06_statistical_results.md`: "Total MDL checks: 720 (360 from T, 360 from C3)"
- `growth_diagnostics.md`: 720 rows (20 seeds × 18 checks × 2 conditions)
- Final report doesn't specify absolute check counts

### 11. DV-b Margin Values Drift (n=5 vs n=20)
**Files:** `evidence/05_metrics.json` vs `evidence/06_statistical_results.md`, `evidence/12_m_recomputation.md`
- `05_metrics.json` (n=5): `margin: 0.051140693004735976`, `margin_source: "data_derived"`
- `06_statistical_results.md` (n=20): "Margin (data-derived) | 0.0440"
- `12_m_recomputation.md` (n=20): C3 null margin 0.0440, self-null margin 0.0896
- Different margins reported without clear version labeling

### 12. M Statistic Precision Inconsistency
**Files:** `FINAL_PUBLICATION_CLAIM.md`, `ABSTRACT_LANGUAGE.md`, `evidence/06_statistical_results.md`, `evidence/12_m_recomputation.md`, `LIMITATIONS.md`
- `FINAL_PUBLICATION_CLAIM.md` table: -0.6055, 0.2949
- `ABSTRACT_LANGUAGE.md`: -0.606, 0.295 (rounded to 3 decimals)
- `06_statistical_results.md`: 0.2949, -0.6055
- `12_m_recomputation.md`: -0.6055, 0.2949
- `LIMITATIONS.md`: -0.6055, 0.2949
- Minor but inconsistent rounding in abstract language

### 13. H* "Double-Negative" Framing Drift
**Files:** `SPRINT1_RETROSPECTIVE.md`, `SPRINT_QUEUE.md`, `RESEARCH_DIRECTOR_DECISION.md`, `LIMITATIONS.md`, `FINAL_PUBLICATION_CLAIM.md`
- `SPRINT1_RETROSPECTIVE.md` item 10: "H* reframed from FAIL → UNTESTED" — documents the correction
- `SPRINT_QUEUE.md`: "Sprint 1's result is 'H* untested... NOT a 'double-negative result.'"
- `RESEARCH_DIRECTOR_DECISION.md`: "Sprint 1 is NOT a 'double-negative result' and must not be described as one"
- `LIMITATIONS.md`: "Sprint 1 must NOT be described as a 'double-negative result.'"
- `FINAL_PUBLICATION_CLAIM.md`: "Sprint 1 did not test H*. The result is 'H* untested,' not a hypothesis that was tested and failed."
- **Consistent now** but retrospective documents prior inconsistent framing

### 14. Review Log Provenance (Historical)
**Files:** `SPRINT1_RETROSPECTIVE.md` item 3, `INTEGRATION_LEDGER.md`, `DOCUMENTATION_RECONCILIATION.md`
- `SPRINT1_RETROSPECTIVE.md`: "REVIEW_LOG.md claimed 'Review #002' as completed review, but no matching committed artifact existed at the cited commit"
- `INTEGRATION_LEDGER.md`: "Review #002 — 2026-07-04 — Sprint 1.1.1 Remediation Verification (committed fd7aabf)" — now exists
- `DOCUMENTATION_RECONCILIATION.md`: Cites Review #002 evidence
- Documented as resolved in retrospective but shows historical drift

### 15. C3 Instrumentation Timing Ambiguity
**Files:** `SPRINT1_RETROSPECTIVE.md` item 6, `evidence/05_metrics.json`, `evidence/01_manifest.json`
- `SPRINT1_RETROSPECTIVE.md`: "C3 instrumentation gap found → fixed... Instrumentation added to the trigger site before C3 was re-run"
- `05_metrics.json` (n=5): No C3 per_step_log mentioned
- `01_manifest.json` (n=20): `c3_per_step_log_count: 360`, `c3_instrumentation_verified: true`
- Unclear if n=5 run had C3 instrumentation; n=20 run did

### 16. Power Analysis Target vs Actual (n=22 vs n=20)
**Files:** `evidence/11_power_analysis.md`, `SPRINT_1.3_PREREGISTRATION.md`, `LIMITATIONS.md`, `RESEARCH_DIRECTOR_DECISION.md`
- `11_power_analysis.md`: "Recommendation: use at least n=22 total seeds... n=20 is close but not sufficient for the stricter 10% target"
- `SPRINT_1.3_PREREGISTRATION.md`: "Preregistered n = 22 seeds"
- `LIMITATIONS.md`: "The planned n=22 for 10% detection was not reached"
- `RESEARCH_DIRECTOR_DECISION.md`: "22 seeds by the correct binomial power rule ((1−0.10)^22=0.0985)"
- Consistent acknowledgment but actual run was n=20

### 17. "Attempts-toward-kill" Terminology Consistency Check
**Files:** Multiple
- `RESEARCH_DIRECTOR_DECISION.md`: "attempts-toward-kill = 0"
- `FINAL_PUBLICATION_CLAIM.md`: "attempts-toward-kill = 0"
- `LIMITATIONS.md`: "Attempts-toward-kill = 0"
- `SPRINT_QUEUE.md`: "attempts-toward-kill = 0"
- `evidence/12_m_recomputation.md`: "attempts-toward-kill = 0"
- `evidence/06_statistical_results.md`: "attempts-toward-kill = 0"
- `ABSTRACT_LANGUAGE.md`: "attempts-toward-kill = 0"
- `SPRINT1_RETROSPECTIVE.md`: Does not use this term
- `SPRINT1_FINAL_REPORT.md`: Does not use this term
- **Consistent where used** but absent from engineering-facing docs

---

## Summary Count

| Category | Count |
|----------|-------|
| Critical (verdict contradictions) | 3 |
| High (control misrepresentation, provenance) | 4 |
| Medium (numbering, margins, precision) | 7 |
| Low (historical drift, resolved items) | 3 |
| **Total** | **17** |

---

## Files Requiring Alignment (Priority Order)

1. `evidence/05_metrics.json` — stale n=5 data contradicts n=20 package
2. `SPRINT1_FINAL_REPORT.md` — omits H* untested status, misrepresents C2
3. `evidence/06_statistical_results.md` — primary n=20 narrative but margins differ from 12_m_recomputation
4. `SPRINT1_RETROSPECTIVE.md` — MiniMax cold read claim contradicted by Research Director
5. `RESEARCH_DIRECTOR_DECISION.md` C-5 — decision.py fix status ambiguous vs retrospective