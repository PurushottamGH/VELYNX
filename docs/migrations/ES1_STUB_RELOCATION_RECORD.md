# ES-1 STUB RELOCATION RECORD

**Authority:** VELYNX Director (agent), executing user-directed remediation of a Reviewer FAIL.
**Date:** 2026-07-09
**Gate state:** ES1_IMPLEMENTATION_GATE.md = NO-GO (2026-07-07).

## 1. Reason

The Reviewer pre-adjudication (2026-07-09) returned FAIL: the emission-surface stub
`program_a/mechanism/emission.py` and the binding stub `program_a/binding/exp1_binding.py`
violated the gate standing prohibition (ES1_IMPLEMENTATION_GATE.md:91-93) -- "no
emission-surface or binding code may be written, merged, or prototyped-in-place" before GO.
This is reinforced by PA2_ACCEPTANCE_DECISION.md Sec.3, which explicitly excludes those
modules and restates the prohibition. The Director cannot override a Reviewer FAIL.

## 2. Files relocated (contents preserved byte-for-byte; SHA-256 verified)

| Original path (REMOVED from program_a/) | Sandbox path (PRESERVED) | SHA-256 |
|---|---|---|
| program_a/mechanism/emission.py | C:\Users\PURUSH~1\AppData\Local\Temp\opencode\program_a_stubs_relocated_2026-07-09\program_a\mechanism\emission.py | 5D80A8175A613D6B92C48FFB500FDEE15866B2A66CFBA58AABCC95C258AFF3D1 |
| program_a/binding/exp1_binding.py | C:\Users\PURUSH~1\AppData\Local\Temp\opencode\program_a_stubs_relocated_2026-07-09\program_a\binding\exp1_binding.py | A31A6E9870C77EE65D8E6E68474C142975EF2325611984971EEBD10D758BF37D |

## 3. What was NOT touched (left in place, unchanged)

program_a/__init__.py, program_a/types.py, program_a/mechanism/{__init__.py, support_tests.py,
evidence_states.py}, program_a/extraction/{__init__.py, claim_extraction.py},
program_a/evidence/{__init__.py, snapshot_store.py, snapshot_format.py, snapshot_builder.py},
program_a/constants.py, program_a/binding/__init__.py. Package directories preserved
(Phase-2 E-1 sanctioned after G-1; G-1 ruling produced 2026-07-09).

## 4. Restore procedure (post-GO ONLY)

After ES1_IMPLEMENTATION_GATE.md flips to GO (A1-A4 AND B1-B3 AND C1-C3 all signed/green),
copy the two sandbox files back to their original paths, verify SHA-256 matches the values
in Sec.2, then proceed with lawful T4/T8 implementation. Do NOT restore before GO.

## 5. Status of other program_a/ stubs (Reviewer ruling)

support_tests.py, evidence_states.py, snapshot_builder.py, snapshot_store.py, constants.py,
types.py are NOT a standing-prohibition violation, but pre-empt PROGRAM_A_IMPLEMENTATION_ORDER.md
Sec.2 steps (gated behind GO / T1-at-G4). Conditions: remain untracked, must not be merged
before GO, no stub may be filled with real logic before GO, constants.py may not be filled
before T1 frozen at G4 (CR-6).

## 6. Sign-off

Relocation executed by: VELYNX Director (agent), 2026-07-09, per user directive.
Reviewer FAIL respected; no override. No production code written; no implementation begun.
