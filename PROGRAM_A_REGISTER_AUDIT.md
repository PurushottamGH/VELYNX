# PROGRAM A REGISTER AUDIT

**Auditor:** ScientificAuditor (ES-1)
**Date:** 2026-07-10
**Scope:** Every frozen register entry of the Program A free-constant register
classified during A1 — `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` §5.1–§5.9,
plus the two co-frozen structural constants of §3.2 (`STATE_TIER_MAP`,
`CONFIDENCE_TIERS`) that share the register's change-control rule and are
serialized into `frozen_constants_digest()` (T1 §6.1).
**Mandate:** Binary scientific-admissibility audit only. Architecture treated as
frozen. No redesign, no implementation, no architecture discussion.

---

## Criterion polarity (binding on every table below)

`PASS` = admissible on that axis. `FAIL` = violation on that axis. For the
negatively-phrased criteria this means:

| Criterion | PASS means |
|---|---|
| 1. Deterministic? | Deterministic |
| 2. Contains any probability? | Contains **no** probability |
| 3. Introduces calibration leakage? | Introduces **none** |
| 4. Introduces EXP-1 leakage? | Introduces **none** |
| 5. Hidden tuning freedom? | **No** hidden tuning freedom |
| 6. A priori justification present? | Present (for the **frozen value**, not only the role) |
| 7. Amendment rule defined? | Defined |
| 8. Scientifically admissible? | Admissible as it stands in the frozen register |

**Shared amendment rule (applies to all 11 entries).** A change to any entry is
a mechanism change requiring *T1 revision + re-freeze + new `SPEC_VERSION` + new
`mechanism_id()`* before any frozen-row output, and is prohibited after
(T1 §5 preamble; `program_a/constants.py` module docstring; CR-6/CR-11/CR-12).
Enforcement is mechanical: `frozen_constants_digest()` (SHA-256 over the ordered
serialization) is pinned as `CONSTANTS_HASH` and asserted by
`tests/program_a/test_constants_freeze.py`; drift fails CI (T1 §6.1). Criterion 7
is therefore `PASS` for every entry and is not re-argued per row.

**Global reproduction datapoint.** `python -m pytest
tests/program_a/test_constants_freeze.py tests/program_a/test_import_guard.py
tests/program_a/test_tier_set_triplication_regression.py -q` → **82 passed**.
`test_constants_contain_no_exp1_probability_or_bin_value` (constants carry none
of `{0.125, 0.375, 0.625, 0.875}`, bin boundaries, or ECE thresholds) is green.

---

## Summary verdict

| # | Entry | State | Admissible? | Severity |
|---|---|---|---|---|
| 5.1 | `MIN_INDEPENDENT_ORIGINS_FOR_S3` | transcribed (`=2`) | **PASS** | residual (LOW) |
| 5.2 | `INDEPENDENCE_RELATION` | transcribed | **PASS** | — |
| 5.3 | `SUPPORT_TEST_PARAMS` | **placeholder `{}`** | **FAIL (deferred)** | **BLOCKER** |
| 5.4 | `CONTRADICTION_MATERIALITY_PARAMS` | **placeholder `{}`** | **FAIL (deferred)** | **BLOCKER** |
| 5.5 | `EVIDENCE_ORDERING_KEY` | transcribed | **PASS** | — |
| 5.6 | `EXTRACTION_PARAMS` | **placeholder `{}`** | **FAIL (deferred)** | HIGH |
| 5.7 | `ANSWER_TEMPLATES` | **placeholder `{}`** | **FAIL (deferred)** | MEDIUM |
| 5.8 | `SPEC_VERSION` | transcribed (draft id) | **PASS** | — |
| 5.9 | `PA3_RULESET_VERSION` | transcribed | **PASS** | — |
| §3.2 | `STATE_TIER_MAP` | transcribed | **PASS** | — |
| §3.2 | `CONFIDENCE_TIERS` | transcribed | **PASS** | residual (LOW, EXP-1 coupling) |

**7 of 11 admissible now. 4 of 11 (5.3, 5.4, 5.6, 5.7) are un-transcribed
placeholders whose scientific admissibility cannot be certified because the
frozen value does not yet exist.** These four are the G4 transcription duty
(addendum §C condition 4); the digest is unpinnable and `CONSTANTS_HASH` is
`None` until they are supplied. An admissible G4 freeze is **not dischargeable**
while any of the four remains a placeholder or is transcribed without a recorded
a-priori justification for its concrete value.

---

## Entry 5.1 — `MIN_INDEPENDENT_ORIGINS_FOR_S3`

**Origin:** T1 §5.1; §3.3 (S2|S3 split); `program_a/constants.py:` `MIN_INDEPENDENT_ORIGINS_FOR_S3: int = 2`.

| Criterion | Verdict |
|---|---|
| 1. Deterministic? | PASS |
| 2. Contains any probability? | PASS (integer origin count, not a probability) |
| 3. Calibration leakage? | PASS |
| 4. EXP-1 leakage? | PASS |
| 5. Hidden tuning freedom? | PASS |
| 6. A priori justification present? | PASS |
| 7. Amendment rule defined? | PASS |
| 8. Scientifically admissible? | PASS |

**Repository evidence:** value `2` transcribed at `program_a/constants.py`;
justification T1 §5.1 — "2 is the smallest count that is corroboration *at
all* — one origin is not corroboration, two is."

**Scientific verdict:** PASS. The a-priori argument is a structural-necessity
argument (the definitional minimum of corroboration), not an outcome fit.

**Remaining scientific risk (LOW, non-blocking):** T1 §5.1 self-describes the
constant as "**Hand-set in the F2 sense**." The admissibility rests *entirely* on
the structural-minimum argument, which licenses the value `2` and **no other
value**. Any future value ≥3 would be an empirical/tuned dial with no a-priori
warrant and would be inadmissible without an EXP-independent justification. Does
not block G4.

---

## Entry 5.2 — `INDEPENDENCE_RELATION`

**Origin:** T1 §5.2; ARCHITECTURE PA-1; `program_a/constants.py` (transcribed string).

| Criterion | Verdict |
|---|---|
| 1. Deterministic? | PASS |
| 2. Contains any probability? | PASS |
| 3. Calibration leakage? | PASS |
| 4. EXP-1 leakage? | PASS |
| 5. Hidden tuning freedom? | PASS |
| 6. A priori justification present? | PASS |
| 7. Amendment rule defined? | PASS |
| 8. Scientifically admissible? | PASS |

**Repository evidence:** frozen relation text transcribed at
`program_a/constants.py` ("distinct `origin_domain` provenance, mirror/
syndication counted once"); justification T1 §5.2 (corroboration counts
independent origins, not mirror copies).

**Scientific verdict:** PASS. Deterministic structural de-duplication rule; the
anti-inflation guard on S3.

**Remaining scientific risk:** None material. Correctness of mirror/syndication
detection is an implementation-conformance question for the Reviewer, not a
register-admissibility defect.

---

## Entry 5.3 — `SUPPORT_TEST_PARAMS`  ❌ BLOCKER

**Origin:** T1 §5.3; MECHANISM §7.4; CF-R2. `program_a/constants.py`:
`SUPPORT_TEST_PARAMS: dict[str, Any] = {}` (in `_FREEZE_PENDING_ENTRIES`).

| Criterion | Verdict |
|---|---|
| 1. Deterministic? | PASS (design mandate: entity-level, no model calls, no randomness) |
| 2. Contains any probability? | PASS ("No probability numbers", T1 §5.3) |
| 3. Calibration leakage? | PASS |
| 4. EXP-1 leakage? | PASS |
| 5. Hidden tuning freedom? | **FAIL** |
| 6. A priori justification present? | **FAIL (value-level)** |
| 7. Amendment rule defined? | PASS |
| 8. Scientifically admissible? | **FAIL (deferred)** |

**Repository evidence:** the register supplies only the **structural form**
("exact parameters fixed at G4 from this register"); the concrete value is the
empty-dict placeholder `{}`. `frozen_constants_digest()` raises
`FrozenConstantsIncomplete` and `CONSTANTS_HASH is None` while this remains
pending (asserted by `test_frozen_constants_digest_pending_until_register_complete`).

**Scientific verdict:** FAIL (deferred). This is the **load-bearing**
claim-support test whose failure modes dominate the risk register (CF-R2 — the
dominant residual risk). Its concrete parameters do not exist in the frozen
register, so (a) there is real latitude in the parameter values between spec and
G4 (criterion 5), and (b) no a-priori justification for the *specific values*
can be certified because there are no values (criterion 6). The no-fabrication
placeholder correctly refuses to invent a default, but that converts the defect
from "silent wrong value" into "specification hole," not into admissibility.

**Blocks G4:** **YES.** This is the G4 transcription duty (addendum §C condition
4). An admissible freeze requires the parameters transcribed **with a recorded
a-priori justification for each** (entity-level matching rationale), not merely
filled in. Freezing an empty or unjustified value here would place the dominant
CF-R2 risk surface outside a-priori control.

**Remaining scientific risk (BLOCKER):** until transcribed-with-justification, a
`CERTAIN`/`PROBABLE` assertion can be produced by whatever support rule is later
chosen, unaudited. The FM-1 / CF-R2 fabrication-pressure guard is only as sound
as these parameters, which are currently unspecified.

---

## Entry 5.4 — `CONTRADICTION_MATERIALITY_PARAMS`  ❌ BLOCKER

**Origin:** T1 §5.4; MECHANISM §7.4; addendum §A4 (S1 composition).
`program_a/constants.py`: `CONTRADICTION_MATERIALITY_PARAMS = {}` (pending).

| Criterion | Verdict |
|---|---|
| 1. Deterministic? | PASS (design mandate) |
| 2. Contains any probability? | PASS ("No probability numbers", T1 §5.4) |
| 3. Calibration leakage? | PASS |
| 4. EXP-1 leakage? | PASS |
| 5. Hidden tuning freedom? | **FAIL** |
| 6. A priori justification present? | **FAIL (value-level)** |
| 7. Amendment rule defined? | PASS |
| 8. Scientifically admissible? | **FAIL (deferred)** |

**Repository evidence:** placeholder `{}`; structural form only in T1 §5.4;
composed by addendum §A4 to decide S1 (material contradiction) vs noise; digest
gated pending.

**Scientific verdict:** FAIL (deferred). This constant is the S1-vs-noise
frozen boundary. With the value unspecified, the threshold that separates a
material contradiction from a trivial phrasing variation is an open dial —
exactly the "runtime judgment" the register exists to eliminate.

**Blocks G4:** **YES** — same status as 5.3 (G4 transcription duty; must carry a
recorded a-priori materiality rationale, not a fitted threshold).

**Remaining scientific risk (BLOCKER):** an unjustified materiality value can
silently move the S1 (`DEBATED`) boundary, changing which queries are
represented as contested vs asserted. Must be pinned with a-priori justification
at G4.

---

## Entry 5.5 — `EVIDENCE_ORDERING_KEY`

**Origin:** T1 §5.5; ARCHITECTURE PA-1; L6 (replay). `program_a/constants.py`:
`"lexicographic on (origin_domain, doc_id)"`.

| Criterion | Verdict |
|---|---|
| 1. Deterministic? | PASS |
| 2. Contains any probability? | PASS |
| 3. Calibration leakage? | PASS |
| 4. EXP-1 leakage? | PASS |
| 5. Hidden tuning freedom? | PASS |
| 6. A priori justification present? | PASS |
| 7. Amendment rule defined? | PASS |
| 8. Scientifically admissible? | PASS |

**Repository evidence:** frozen total-order key transcribed; justification T1
§5.5 (a frozen total order removes wall-clock/score-order as a determinism leak,
required for L6 replay).

**Scientific verdict:** PASS. A determinism-preserving structural key; supports
reproducibility rather than threatening it.

**Remaining scientific risk:** None material.

---

## Entry 5.6 — `EXTRACTION_PARAMS`  ⚠ HIGH

**Origin:** T1 §5.6; ARCHITECTURE PA-2; MECHANISM §7.1; CF-R2 (first line).
`program_a/constants.py`: `EXTRACTION_PARAMS = {}` (pending).

| Criterion | Verdict |
|---|---|
| 1. Deterministic? | PASS (design mandate: no model calls — M8 unlawful) |
| 2. Contains any probability? | PASS ("No probability numbers, no model calls") |
| 3. Calibration leakage? | PASS |
| 4. EXP-1 leakage? | PASS |
| 5. Hidden tuning freedom? | **FAIL** |
| 6. A priori justification present? | **FAIL (value-level)** |
| 7. Amendment rule defined? | PASS |
| 8. Scientifically admissible? | **FAIL (deferred)** |

**Repository evidence:** placeholder `{}`; structural form only; feeds PA-3, so
its parameters upstream-condition every state. `claim_extraction.py` structural
defaults govern meanwhile (constants.py comment) — i.e., the frozen value is not
yet the operative one.

**Scientific verdict:** FAIL (deferred). PA-2 extraction is the first CF-R2 line
(fabricated-entity probes must yield no claim). Concrete parameters unspecified →
tuning latitude + no value-level a-priori justification.

**Blocks G4:** **YES** (G4 transcription duty). Severity HIGH rather than
BLOCKER only because a documented structural default exists in
`claim_extraction.py`; nonetheless the *frozen* value is unrecorded and must be
transcribed-with-justification at G4.

**Remaining scientific risk (HIGH):** divergence between the interim
`claim_extraction.py` defaults and the eventual frozen value is unaudited until
G4; the frozen extraction contract is not yet under a-priori control.

---

## Entry 5.7 — `ANSWER_TEMPLATES`  ⚠ MEDIUM

**Origin:** T1 §5.7; ARCHITECTURE PA-4; MECHANISM §7.2; CR-9.
`program_a/constants.py`: `ANSWER_TEMPLATES = {}` (pending).

| Criterion | Verdict |
|---|---|
| 1. Deterministic? | PASS |
| 2. Contains any probability? | PASS (forms assert no probability; UNKNOWN/DEBATED assert no fact; PROBABLE/CERTAIN source-attributed) |
| 3. Calibration leakage? | PASS |
| 4. EXP-1 leakage? | PASS |
| 5. Hidden tuning freedom? | PASS (qualitative surface text; no numeric dial fittable to outcomes) |
| 6. A priori justification present? | **FAIL (value-level: exact template text not yet fixed)** |
| 7. Amendment rule defined? | PASS |
| 8. Scientifically admissible? | **FAIL (deferred)** |

**Repository evidence:** placeholder `{}`; T1 §5.7 fixes the *form* per state
`{S0,S1,S2,S3}` but not the text; digest gated pending.

**Scientific verdict:** FAIL (deferred), but qualitatively different from
5.3/5.4/5.6: templates carry no numeric/tuning surface, so criterion 5 is PASS.
The defect is that the exact frozen wording is unrecorded, so criterion 6 (and
therefore 8) cannot be certified.

**Blocks G4:** **YES** (G4 transcription duty), MEDIUM severity.

**Remaining scientific risk (MEDIUM):** at transcription the template text must
be screened for embedded probability/quantifier language (e.g. "90% likely")
that would smuggle a calibration claim onto the answer surface and breach the
CR-8/L8 firewall. The register form forbids this; the check is owed at G4.

---

## Entry 5.8 — `SPEC_VERSION`

**Origin:** T1 §5.8; CR-6/CR-12. `program_a/constants.py`:
`SPEC_VERSION: str = "es1-t1-2026-07-09"` (draft; ratified at G4).

| Criterion | Verdict |
|---|---|
| 1. Deterministic? | PASS |
| 2. Contains any probability? | PASS (identity string) |
| 3. Calibration leakage? | PASS |
| 4. EXP-1 leakage? | PASS |
| 5. Hidden tuning freedom? | PASS |
| 6. A priori justification present? | PASS (structural identity anchor) |
| 7. Amendment rule defined? | PASS |
| 8. Scientifically admissible? | PASS |

**Repository evidence:** transcribed string; T1 §5.8 (version anchor tying
frozen code to frozen spec).

**Scientific verdict:** PASS. Pure identity tag; carries no scientific value.
The "final value set at G4" note is ratification of an identifier, not an open
scientific quantity.

**Remaining scientific risk:** None scientific. Non-blocking clerical: the final
identity string must be the pinned value at the G4 commit.

---

## Entry 5.9 — `PA3_RULESET_VERSION`

**Origin:** addendum §A6-DIGEST; T1 §5.9. `program_a/constants.py`:
`PA3_RULESET_VERSION: str = "pa3-ruleset-2026-07-09"`.

| Criterion | Verdict |
|---|---|
| 1. Deterministic? | PASS |
| 2. Contains any probability? | PASS ("no probability, no numeric evaluation constant" — addendum §A6-DIGEST) |
| 3. Calibration leakage? | PASS |
| 4. EXP-1 leakage? | PASS |
| 5. Hidden tuning freedom? | PASS |
| 6. A priori justification present? | PASS |
| 7. Amendment rule defined? | PASS |
| 8. Scientifically admissible? | PASS |

**Repository evidence:** transcribed identity tag folded into the digest inputs
(`_frozen_constants_items()`); justification addendum §A6-DIGEST (binds the PA-3
prose rules (i)–(v) to the runtime tripwire, closing the digest coverage gap).

**Scientific verdict:** PASS. Strengthens change-control (makes rule-text drift
mechanically un-landable); pure identity string in the `SPEC_VERSION` class.

**Remaining scientific risk:** None material.

---

## Entry §3.2a — `STATE_TIER_MAP`

**Origin:** T1 §3.1–§3.2; `program_a/constants.py`
`{"S0":"UNKNOWN","S1":"DEBATED","S2":"PROBABLE","S3":"CERTAIN"}`.

| Criterion | Verdict |
|---|---|
| 1. Deterministic? | PASS |
| 2. Contains any probability? | PASS (labels one tier per state; "labels a corroboration state, does not assign a probability", T1 §3.2) |
| 3. Calibration leakage? | PASS |
| 4. EXP-1 leakage? | PASS (no probability mirrored) |
| 5. Hidden tuning freedom? | PASS (fixed bijection state→tier; not fittable) |
| 6. A priori justification present? | PASS |
| 7. Amendment rule defined? | PASS |
| 8. Scientifically admissible? | PASS |

**Repository evidence:** transcribed verbatim; `test_constants_state_tier_map_and_confidence_tiers_frozen` green; one-tier-per-state exclusivity (CR-9) argued in T1 §3.2.

**Scientific verdict:** PASS. Ordinal structural map; the ordinality-by-
construction backbone. No probability, no fit.

**Remaining scientific risk:** None material.

---

## Entry §3.2b — `CONFIDENCE_TIERS`

**Origin:** T1 §3.2; `program_a/constants.py`
`("UNKNOWN","DEBATED","PROBABLE","CERTAIN")`; declared equal to
`experiments.EXP1.dataset.CONFIDENCE_TIERS`.

| Criterion | Verdict |
|---|---|
| 1. Deterministic? | PASS |
| 2. Contains any probability? | PASS (label tuple only) |
| 3. Calibration leakage? | PASS |
| 4. EXP-1 leakage? | PASS (labels shared, probabilities not) |
| 5. Hidden tuning freedom? | PASS |
| 6. A priori justification present? | PASS |
| 7. Amendment rule defined? | PASS |
| 8. Scientifically admissible? | PASS |

**Repository evidence:** the EXP-1 tier→probability values `{0.125, 0.375,
0.625, 0.875}` live **only** in `experiments/EXP1/calibration.py:15–18` and
`experiments/EXP1/config.json`; they appear **nowhere** in `program_a/`
(verified by grep and by `test_constants_contain_no_exp1_probability_or_bin_value`,
green). The only shared object is the label tuple; T1 §3.2 frames the equality
as "lawful conformance (same labels, no probability mirroring — G2/A2)."
`test_import_guard.py` (green) enforces the `experiments.EXP1.calibration`
deny-list per `PROGRAM_A_MODULE_SPEC.md` §2.

**Scientific verdict:** PASS. This is the single entry with a *direct* EXP-1
coupling, and it is the CR-8/L8 firewall's focal point. Admissible because the
coupling is confined to the ordinal **label set**; no calibration probability,
bin boundary, or ECE threshold crosses into the mechanism.

**Remaining scientific risk (LOW, non-blocking):** admissibility rests wholly on
the labels-only argument plus two enforcement facts — the no-probability
constants test and the import deny-list — both currently green, and on gate item
**C1** (sentinel-substitution / byte-identical output) which is a gate box, not
yet checked at G-time. If a future edit introduced the EXP-1 probabilities
alongside the shared labels, admissibility would flip; the firewall test is what
holds this at PASS and must remain green through freeze.

---

## Aggregate scientific risk & G4 disposition

1. **Admissible now (7):** 5.1, 5.2, 5.5, 5.8, 5.9, `STATE_TIER_MAP`,
   `CONFIDENCE_TIERS`. No probability, no calibration/EXP-1 leakage, a-priori
   justified at the value level, amendment-controlled.

2. **Deferred / not certifiable (4):** 5.3, 5.4, 5.6, 5.7 are un-transcribed
   placeholders. On the pure-determinism / no-probability / no-leakage axes they
   are clean **by design mandate**, but their **concrete frozen values do not
   exist**, so criterion 6 (value-level a-priori justification) and criterion 8
   (admissibility) are `FAIL (deferred)`, and criterion 5 is `FAIL` for the three
   parameter entries (5.3, 5.4, 5.6). The repository handles this correctly and
   honestly: no fabricated default; digest refuses to pin; `CONSTANTS_HASH` is
   `None`.

3. **G4 impact.** The four deferred entries **are** the G4 transcription duty
   (addendum §C condition 4). An admissible G4 freeze (gate item B3) is **not
   dischargeable** until each is transcribed **with a recorded a-priori
   justification for its concrete value** and the digest is pinned. 5.3 and 5.4
   are BLOCKER (they gate the dominant CF-R2 / FM-1 fabrication risk and the
   S1-vs-noise boundary); 5.6 is HIGH; 5.7 is MEDIUM (plus a mandatory screen for
   embedded probability/quantifier language in the template text).

4. **Non-blocking residuals.** 5.1 carries a self-admitted "hand-set in the F2
   sense" value whose sole warrant is the structural-minimum argument (licenses
   `2`, nothing else). `CONFIDENCE_TIERS` carries the only live EXP-1 coupling,
   held admissible solely by the labels-only firewall (green tests + gate item
   C1).

**Register-level verdict:** `SCIENTIFIC: FAIL — 4 of 11 register entries
(5.3 SUPPORT_TEST_PARAMS, 5.4 CONTRADICTION_MATERIALITY_PARAMS, 5.6
EXTRACTION_PARAMS, 5.7 ANSWER_TEMPLATES) are un-transcribed placeholders whose
scientific admissibility cannot be certified. The 7 transcribed entries PASS.
No probability, calibration leakage, or EXP-1 leakage was found in any entry.
G4 freeze is inadmissible until the four owed values are transcribed with
value-level a-priori justification and the digest is pinned.`
