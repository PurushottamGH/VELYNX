# P1 Evidence Graph — SKB v1.0

- **State date:** 2026-07-28
- **Canonical edges:** `science/SKB_RECORDS_v1.0.yaml`
- **Rule:** Evidence is a claim-relative relation, not a free-standing synonym for a result.

## Evidence records

| ID | Admitted observations | Target | Direction | Strength / validity | Bounded interpretation |
|---|---|---|---|---|---|
| `EVD-2026-0001` | `OBS-0001` | `HYP-0005` free-energy advantage | opposes | moderate / valid negative | no measured R1 advantage; not equivalence |
| `EVD-2026-0002` | `OBS-0003` | `HYP-0006` semantic benchmark inference | opposes | strong / valid negative | complete Tier-2 collapse in tested set |
| `EVD-2026-0003` | `OBS-0004` | `EXP-0002` Tier-1 interpretation | limits | moderate / valid negative | original-condition floor prevents robustness inference |
| `EVD-2026-0004` | `OBS-0011` | `HYP-0002` calibration | opposes | moderate / valid negative | hard historical failure; not population ECE |
| `EVD-2026-0005` | `OBS-0005..0007` | `HYP-0001` and E0 validity | uninformative on H*, opposes protocol validity | strong methodological / invalid H* test | treatment absent |
| `EVD-2026-0006` | `OBS-0008` | `HYP-0007` replay effect | weakly supports | weak / valid indeterminate | seed-0 bundled association only |
| `EVD-2026-0007` | `OBS-0008,0010` | `HYP-0007,0008` | limits | strong methodological / valid indeterminate | confounding prohibits causal attribution |
| `EVD-2026-0008` | `OBS-0012` | `ASM-0005` learned-vs-injected identifiability | opposes | moderate / audit evidence | pervasive injection blocks legacy emergence inference |
| `EVD-2026-0009` | `OBS-0015..0019` | M1 confirmatory readiness, `ASM-0010/0011`, `SDEBT-0010..0012` | blocks confirmatory readiness; supports local conformance | strong methodological / audit evidence | substantial local checks pass, but apparatus provenance and validity gates are not yet admissible |

## Graph

```text
OBS-0001 ─admitted by─> EVD-0001 ─opposes─> HYP-0005
                                             └─DEC-0003─> Rejected in R1 scope

OBS-0003 ─admitted by─> EVD-0002 ─opposes─> HYP-0006
                                             └─DEC-0002─> Rejected benchmark inference
OBS-0004 ─admitted by─> EVD-0003 ─limits──> EXP-0002 Tier-1 interpretation

OBS-0011 ─admitted by─> EVD-0004 ─opposes─> HYP-0002
                                             └─DEC-0005─> No verdict on achievable calibration

OBS-0005 ─┐
OBS-0006 ─┼─admitted by─> EVD-0005 ─invalidates test─> EXP-0004
OBS-0007 ─┘                                      └─uninformative─> HYP-0001
                                                        └─DEC-0004─> H* remains Exploratory

OBS-0008 ─admitted by─> EVD-0006 ─weak support─> HYP-0007
OBS-0008 ─┐
OBS-0010 ─┴─admitted by─> EVD-0007 ─limits─> HYP-0007 and HYP-0008
                                              └─DEC-0007─> matched validation required

OBS-0012 ─admitted by─> EVD-0008 ─opposes─> ASM-0005
                                             └─limits─> HYP-0001 emergence interpretation

OBS-0015..0019 ─admitted by─> EVD-0009 ─blocks─> EXP-0007 confirmatory execution
                                           ├─opposes─> ASM-0011 gate alignment
                                           ├─expands─> SDEBT-0010 provenance
                                           └─creates─> SDEBT-0011/0012 readiness debt
                                                        └─DEC-0010─> delay Cycle 001 execution
```

## Evidence-strength reasoning

### Strong scoped negative evidence

`EVD-2026-0002` is strong because the intervention directly removes the feature suspected of carrying the result, uses paired items, and yields complete collapse. Its scope remains the detector and item set.

### Moderate negative evidence

`EVD-2026-0001` is moderate rather than strong because the point estimate does not favor treatment, but uncertainty is wide and only one primary metric was available.

`EVD-2026-0004` is moderate because a hard failure directly contradicts zero-tolerance honesty for the historical instance, yet a single query cannot characterize calibration over a distribution.

### Invalid scientific test, valid methodological evidence

`EVD-2026-0005` must not be entered as evidence against H*. The execution is highly informative about trigger and protocol failure. This separation prevents false rejection caused by an absent treatment.

### Weak exploratory support plus strong limitation

M0 contributes both `EVD-2026-0006` and `EVD-2026-0007`. The observed direction weakly motivates further testing; the design defects strongly prohibit mechanism acceptance. These are not contradictory relations because they answer different questions.

### Strong readiness limitation without hypothesis update

`EVD-2026-0009` concerns whether future outputs can be admitted as evidence, not whether replay, surprise, or any other mechanism works. Passing 202 local tests supports engineering conformance. Uncommitted code, vacuous or mis-targeted gates, and unenforced provenance independently block confirmatory admissibility. No hypothesis edge is created.

## Missing edges are meaningful

There are no evidence-support edges for affective indexing, historical-carrier dependence, or a supported P1 theory. Their absence is explicit scientific state, not missing documentation.
