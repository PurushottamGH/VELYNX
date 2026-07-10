# PROGRAM A — CONFIDENCE-EMISSION RISKS

**Authority:** Chief Scientific Architect review, 2026-07-07. Risks specific
to the confidence-emission mechanism (recommended ES-1,
`PROGRAM_A_CONFIDENCE_MECHANISM.md` §7) and to the decision process around
it. Complements — does not duplicate — `PROGRAM_A_RISK_REGISTER.md` (R-01…
R-17) and `PROGRAM_A_FAILURE_ANALYSIS.md` (FM-1…FM-12); cross-references
given. Severity: CRITICAL (invalidates EXP-1 or violates canon) > HIGH
(a preregistered kill fires or the verdict is uninterpretable) > MEDIUM >
LOW. Tags: `[FACT]`, `[INFERENCE]`, `[RISK]`, `[OPEN QUESTION]`.

---

| ID | Sev | Risk | Basis | Mitigation / disposition |
|---|---|---|---|---|
| CF-R1 | CRITICAL | **Rubric/family visibility at answer time.** The runner hands the surface the full `QueryRecord` including `gold_rubric` and `query_family` (`dataset.py:33-41`; `run.py:84,181`). A mechanism (or a later "improvement") that reads them fakes calibration undetectably in the ECE number. **[FACT]** the channel exists; **[RISK]** no document or test currently guards it. | new finding (CR-3) | Required: sentinel-substitution test (CR-3 verification); consider passing a redacted view to the adapter as a production fix (needs Reviewer + ScientificAuditor sign-off, F-10-style). |
| CF-R2 | CRITICAL | **Claim-support test false-positives on fabricated claims.** The never-fail retriever always returns *something* (`unified_retriever.py:61-67`); on nonexistent-entity/false-premise rows, topically related snippets may lexically match a fabricated candidate claim → S3 → asserted answer + `CERTAIN` → the zero-tolerance FM-1 kill (prereg §4; `decision.py:20`). **[INFERENCE]** This is the single most likely path to recreating the historical Q6 failure (canon `:146`) inside a lawful-looking mechanism. | MECHANISM §7.4 | The support test — not the state table — is where design effort belongs: require entity-level match, not topic-level; treat "retrieved but non-supporting" as S0. Dry-run on a synthetic non-frozen corpus with fabrication pressure (roadmap T10) before freeze. |
| CF-R3 | HIGH | **DEBATED-bin over-accuracy (family-echo tension).** Under the pinned semantics (CR-2), a well-constructed qualified answer on an ambiguous row is often rubric-correct; if S1 answers succeed ≫ 37.5% of the time, the DEBATED bin contributes heavily to ECE and can breach 0.10 on its own. Symmetrically, S0 refusals may be rubric-correct ≫ 12.5% on hallucination rows. **[INFERENCE]** ES-1's ordinal map is a-priori honest but its bin accuracies are untested — this is H1 itself. | MECHANISM §3, §7.2 | None lawful post-freeze. A kill here is a valid scientific outcome (FM-4). Pre-freeze: the only lawful sanity check is a disjoint dev corpus, itself an **[OPEN QUESTION]** (M13) requiring ScientificAuditor ruling. Do not resolve by tuning. |
| CF-R4 | HIGH | **Q2 unresolved: live retrieval vs frozen snapshot.** Live → wall-clock and env-keyed sources (`unified_retriever.py:31,156,346,362`) break per-(query,seed) determinism and byte-identical replay (CR-4); drift can kill one seed of 22 with no flake exemption (FM-6). Snapshot → snapshot construction after seeing the frozen queries is leakage-adjacent and must itself pass review. | OPEN_QUESTIONS Q2; R-06 | Architect + ScientificAuditor decision (T0) before freeze; recommended: frozen snapshot constructed under documented leakage review. |
| CF-R5 | HIGH | **Q3 forced amendment: full determinism vs 22-seed power design.** ES-1 + snapshot ⇒ all 22 replicates byte-identical ⇒ the preregistration's own clause fires: "this preregistration is underpowered and must be amended before outputs are observed" (prereg §7). Running 22 identical replicates *without* amendment is a protocol defect; amending *after* outputs is a kill. | R-13; CR-15 | Invoke the amendment before execution, or introduce a declared, justified seed-variance source. This is forced, not optional. **[FACT]** |
| CF-R6 | HIGH | **Degenerate tier distribution without unlawful recourse.** If the support test is strict, S0 may dominate all 210 rows (< 2 tiers ⇒ kill, `decision.py:19`); if lax, S3 dominates and CF-R2 bites. The lawful response window is *before* freeze only (redesign + refreeze); after outputs, nothing may be adjusted. | FM-3; R-10; CR-14 | Dry-run tier-distribution check on non-frozen synthetic corpus (T10) before G4 freeze. |
| CF-R7 | MEDIUM | **Evidence-universe mismatch with the rubric's allowed source set.** Rubric correctness is adjudicated against each row's `allowed_source_set` (`EXP1_DATASET_SPEC.md` §7); ES-1 corroborates against whatever the retriever returns. A claim well-corroborated in Program A's evidence but outside the allowed set (or vice versa) decouples the tier from the adjudicated event. **[INFERENCE]** This is a calibration-noise floor built into the design, not a protocol violation. | dataset spec §7, §20 | Quantify in the dry run; if dominant, the Q2 snapshot should be constructed to cover the allowed source universes (with leakage review). |
| CF-R8 | MEDIUM | **Hand-set structural constants (I2-analogue).** "≥2 independent origins", the independence relation, and the materiality rule are designer choices; unjustified, they reproduce the uncited-constant pattern (canon §8: ~150 constants, zero data-derived) inside the one surviving product. | CR-11; MASTER_SPEC §17 | Free-constant register in T1 with a-priori justifications; ScientificAuditor review; never tuned. |
| CF-R9 | MEDIUM | **Fallback-path ambiguity (L8 scope).** If ES-1 is rejected at T1 and the M12 fallback is taken, the unresolved "mirror" reading of MASTER_SPEC §7 item 3 (may an a-priori probability be discretized at the locked boundaries?) becomes load-bearing, and M12's ε constants have no lawful provenance today. | MECHANISM §7.3, §4 M12 | Obtain the L8-scope ruling *at* T1 even if ES-1 is adopted, so the fallback is adjudicated before it is ever needed. **[OPEN QUESTION]** |
| CF-R10 | MEDIUM | **Dev-corpus Goodhart channel (M13).** If pre-freeze dev-set sanity checks are permitted, iterating the state→tier map against dev results until it "looks calibrated" is calibration-by-another-name; the Goodhart guard (canon §6-H1) applies in spirit even off the frozen set. | MECHANISM §4 M13 | If permitted at all: single pre-registered dev evaluation, documented, with change budget declared in advance; ScientificAuditor ruling required. **[OPEN QUESTION]** |
| CF-R11 | LOW | **Identity drift.** A mechanism-spec change without an `adapter_id` change makes replay silently compare different mechanisms (Q8). | CR-12; OPEN_QUESTIONS Q8 | Encode T1 spec version in the id string until the Architect/Release-Manager ruling. |
| CF-R12 | HIGH | **Process risk: this analysis being treated as authorization.** This document set recommends ES-1 but cannot authorize it; Q1's decider is the ScientificAuditor (ADAPTER_AUDIT §6 item 6), and every specialist channel was unavailable this session (R-08). Building from this analysis without T1/G4 sign-off would itself be the fabricated-approvals threat named in MASTER_SPEC §16. | R-08; roadmap Tree 3 | Hard rule: no emission-surface code before G2 + T1 + G4 are discharged by real specialists. **[FACT]** |

---

## Open questions consolidated (deciders unchanged from `PROGRAM_A_OPEN_QUESTIONS.md`)

1. **[OPEN QUESTION — Q1]** Adopt ES-1 as the T1 mechanism? — ScientificAuditor.
2. **[OPEN QUESTION — Q2]** Snapshot vs live retrieval — Architect + ScientificAuditor (CF-R4).
3. **[OPEN QUESTION — Q3]** Seed-variance source / prereg §7 amendment — ScientificAuditor (CF-R5).
4. **[OPEN QUESTION — new]** Is the L11/CR-3 input restriction to be enforced by test only, or by redacting the `QueryRecord` view handed to adapters (production change)? — Architect + Reviewer + ScientificAuditor (CF-R1).
5. **[OPEN QUESTION — new]** Are pre-freeze disjoint-dev-corpus checks (M13) lawful, and under what documentation duty? — ScientificAuditor (CF-R3, CF-R10).
6. **[OPEN QUESTION — new]** L8 scope: does boundary-discretization of an a-priori probability constitute forbidden "mirroring"? — ScientificAuditor (CF-R9).

## Honest-outcome statement

**[FACT]** Canon §8 budgets for negative results; `PROGRAM_A_FAILURE_
ANALYSIS.md` §4 pre-agrees that a killed EXP-1 is a reportable outcome. The
risks above are therefore split deliberately: CF-R1/CF-R4/CF-R5/CF-R12 (and
CF-R10 if mishandled) threaten the run's **validity** and must be closed
before execution; CF-R2/CF-R3/CF-R6/CF-R7 threaten only the **pass**, and the
correct response to them is measurement, not mitigation-by-tuning.
