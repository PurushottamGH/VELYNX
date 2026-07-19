# Assumption Ledger

Reduced from `research/program_c_assumption_ledger.md`. Only three irreducible
inductive assumptions (I1, I2, I3) are retained.

## I1: Free Energy Principle Is Computationally Tractable

- **Assumption:** The free energy functional (F = λH + μS + νL) can be computed
  incrementally in an online setting with bounded resources.
- **Risk:** If exact computation grows superlinearly with experience, the
  architecture cannot scale. We mitigate by using ring-buffer approximations
  (BASELINE_CAP = 240).
- **Bound:** Virtual memory ensures O(k) per tick, where k = BASELINE_CAP.

## I2: Prediction-Error Signal Is Sufficient for Structure Discovery

- **Assumption:** Minimizing prediction error at the sensory level is sufficient
  to drive the formation of hierarchically organized internal representations.
- **Risk:** Without a supervisory signal or reward function, the system may
  discover statistically salient but cognitively irrelevant structure.
- **Bound:** Tested empirically by EXP3 — if H3 fails, I2 is falsified.

## I3: Hebbian Plasticity in the Soul Graph Does Not Produce Runaway Dynamics

- **Assumption:** The Hebbian update rule (Δw = η × activation_pre ×
  activation_post × prediction_error) converges to a stable fixed point given
  the active inference damping term.
- **Risk:** Without the damping term, Hebbian updates can produce runaway
  excitation or catastrophic forgetting.
- **Bound:** Projection step after each update enforces ||w||₂ ≤ 1.

## Archived Assumptions

The following secondary assumptions have been archived as they are consequences
of I1-I3 or are empirically testable within single experiments:

- A4 (Surprise is a reliable proxy for learning progress)
- A7 (Discrete concepts emerge at MDL minima)
- A9 (Ring-buffer approximation preserves free energy topology)
- A11 (Null-referenced statistic controls for complexity)
- A14 (Concept birth via MDL is stable under mild noise)
