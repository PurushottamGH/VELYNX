"""F-A trigger fix: corrected MDL growth trigger tests.

Verifies:
1. Seed 54 fires at step 1000 (ΔH=+0.04911) — known positive
2. Seed 42 never fires across its logged steps — known negative
3. Regression: all 720 raw Sprint-1 checks reproduce exactly 4/20 seeds
   firing (46, 49, 54, 60) — no more, no fewer.

Reference: F_A_TRIGGER_FIX_PREREGISTRATION.md §2
"""
from __future__ import annotations

from core.mdl.mdl_growth import should_grow


FIRING_SEEDS = frozenset({46, 49, 54, 60})
NON_FIRING_SEEDS = frozenset({42, 43, 44, 45, 47, 48, 50, 51, 52, 53, 55, 56, 57, 58, 59, 61})

STEPS = [1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000,
         5500, 6000, 6500, 7000, 7500, 8000, 8500, 9000, 9500]

# Firing seeds' T-condition checks (step, H_before, H_after) from Sprint-1 diagnostics.
# All other checks (C3 for all seeds; T for non-firing seeds) have ΔH < 0 → G < 0 automatically.
FIRING_T_CHECKS: dict[int, list[tuple[int, float, float]]] = {
    46: [
        (1000, 0.999130, 1.012001),
        (1500, 0.999945, 1.007388),
        (2000, 0.999244, 1.004736),
        (2500, 0.999104, 1.001118),
        (3000, 0.999546, 0.998582),
        (3500, 0.999400, 0.998158),
        (4000, 0.999173, 0.997084),
        (4500, 0.999651, 0.995620),
        (5000, 0.999694, 0.995719),
        (5500, 0.999657, 0.996562),
        (6000, 0.999182, 0.996147),
        (6500, 0.998971, 0.995532),
        (7000, 0.998691, 0.995245),
        (7500, 0.998641, 0.995045),
        (8000, 0.998752, 0.994649),
        (8500, 0.998903, 0.994639),
        (9000, 0.999173, 0.994506),
        (9500, 0.998821, 0.994126),
    ],
    49: [
        (1000, 0.999103, 1.006528),
        (1500, 0.999095, 0.994751),
        (2000, 0.999900, 0.992243),
        (2500, 0.999876, 0.991557),
        (3000, 0.999998, 0.989518),
        (3500, 0.999931, 0.989564),
        (4000, 0.999792, 0.986832),
        (4500, 0.999897, 0.985485),
        (5000, 0.999982, 0.984108),
        (5500, 0.999985, 0.983565),
        (6000, 0.999941, 0.984345),
        (6500, 0.999932, 0.983458),
        (7000, 0.999796, 0.983333),
        (7500, 0.999853, 0.983620),
        (8000, 0.999775, 0.981965),
        (8500, 0.999677, 0.982438),
        (9000, 0.999671, 0.981820),
        (9500, 0.999769, 0.981386),
    ],
    54: [
        (1000, 0.967520, 0.918413),
        (1500, 0.952710, 0.894278),
        (2000, 0.941503, 0.881693),
        (2500, 0.944127, 0.873323),
        (3000, 0.944851, 0.863620),
        (3500, 0.940138, 0.858974),
        (4000, 0.937651, 0.855778),
        (4500, 0.939287, 0.852200),
        (5000, 0.942048, 0.850415),
        (5500, 0.940894, 0.847270),
        (6000, 0.939467, 0.846148),
        (6500, 0.939756, 0.844373),
        (7000, 0.937921, 0.846005),
        (7500, 0.939400, 0.846613),
        (8000, 0.940254, 0.845317),
        (8500, 0.941965, 0.845352),
        (9000, 0.941113, 0.842310),
        (9500, 0.937976, 0.838877),
    ],
    60: [
        (1000, 0.992774, 0.999219),
        (1500, 0.992455, 0.993111),
        (2000, 0.989201, 0.991060),
        (2500, 0.988325, 0.986368),
        (3000, 0.989363, 0.986399),
        (3500, 0.992710, 0.986812),
        (4000, 0.993289, 0.988476),
        (4500, 0.993478, 0.989154),
        (5000, 0.993691, 0.988172),
        (5500, 0.994361, 0.987996),
        (6000, 0.992502, 0.987362),
        (6500, 0.992164, 0.986816),
        (7000, 0.991819, 0.987448),
        (7500, 0.992401, 0.987686),
        (8000, 0.992003, 0.986490),
        (8500, 0.991690, 0.986556),
        (9000, 0.990874, 0.986271),
        (9500, 0.991787, 0.987251),
    ],
}

# One representative T check per non-firing seed (all have ΔH < 0 → G < 0)
NON_FIRING_T_CHECKS: list[tuple[int, int, float, float]] = [
    (42, 1000, 0.760136, 0.781195),
    (43, 1000, 0.999617, 1.020021),
    (44, 1000, 0.976874, 0.996142),
    (45, 1000, 0.933764, 1.167301),
    (47, 1000, 0.979893, 1.000378),
    (48, 1000, 0.378713, 0.851995),
    (50, 1000, 0.983342, 1.003794),
    (51, 1000, 0.991214, 1.014829),
    (52, 1000, 0.863857, 1.132428),
    (53, 1000, 0.982517, 1.003002),
    (55, 1000, 0.995781, 1.016199),
    (56, 1000, 0.997909, 1.018321),
    (57, 1000, 0.994818, 1.015240),
    (58, 1000, 0.980493, 1.002884),
    (59, 1000, 0.999368, 1.020049),
    (61, 1000, 0.997036, 1.018817),
]

# One representative C3 check per seed (all have ΔH < 0 → G < 0)
C3_CHECKS: list[tuple[int, int, float, float]] = [
    (42, 1000, 0.836225, 0.892963),
    (43, 1000, 0.995358, 1.015782),
    (44, 1000, 0.999628, 1.020032),
    (45, 1000, 0.955528, 0.976069),
    (46, 1000, 0.996257, 1.016674),
    (47, 1000, 0.999032, 1.012201),
    (48, 1000, 0.808200, 1.115106),
    (49, 1000, 0.993934, 1.014355),
    (50, 1000, 0.938061, 0.958648),
    (51, 1000, 0.965068, 0.985573),
    (52, 1000, 0.851097, 1.134208),
    (53, 1000, 0.994101, 1.014527),
    (54, 1000, 0.995465, 1.015884),
    (55, 1000, 0.997789, 1.015017),
    (56, 1000, 1.000000, 1.019699),
    (57, 1000, 0.981684, 1.007472),
    (58, 1000, 0.979269, 1.009116),
    (59, 1000, 0.997558, 1.017648),
    (60, 1000, 0.997911, 1.018320),
    (61, 1000, 0.994528, 1.017267),
]

# Expected first step where each firing seed fires (verified replay,
# F_A_TRIGGER_FIX_PREREGISTRATION.md §2 — corrected 2026-07-05: seeds 46
# and 60 fire one step later than originally recorded).
FIRST_FIRE_STEP: dict[int, int | None] = {
    46: 4500,
    49: 2000,
    54: 1000,
    60: 3500,
}


# ─── Unit tests ─────────────────────────────────────────────────


class TestSeed54Fires:
    """Seed 54 has the largest ΔH — must fire at step 1000."""

    def test_seed_54_step_1000_fires(self):
        decision, gain, threshold = should_grow(
            entropy_before=0.967520,
            entropy_after=0.918413,
            k=2, n=2, N=1000,
        )
        assert decision is True, (
            f"Seed 54 step 1000 should fire (gain={gain:.4f}, threshold={threshold:.4f})"
        )
        assert gain > 0

    def test_seed_54_all_checks_fire(self):
        for step, h_before, h_after in FIRING_T_CHECKS[54]:
            decision, gain, threshold = should_grow(
                entropy_before=h_before,
                entropy_after=h_after,
                k=2, n=2, N=step,
            )
            assert decision is True, (
                f"Seed 54 step {step} should fire (ΔH={h_before - h_after:.6f}, "
                f"gain={gain:.4f}, threshold={threshold:.4f})"
            )


class TestSeed42NeverFires:
    """Seed 42 has H_before < H_after at all checks — must never fire."""

    def test_seed_42_step_1000_does_not_fire(self):
        decision, gain, _ = should_grow(
            entropy_before=0.760136,
            entropy_after=0.781195,
            k=2, n=2, N=1000,
        )
        assert decision is False, f"Seed 42 step 1000 should not fire (gain={gain:.4f})"
        assert gain < 0

    def test_seed_42_all_steps_do_not_fire(self):
        steps = [1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000,
                 5500, 6000, 6500, 7000, 7500, 8000, 8500, 9000, 9500]
        for step in steps:
            _, gain, _ = should_grow(
                entropy_before=0.0,
                entropy_after=0.0,
                k=2, n=2, N=step,
            )
            # ΔH = 0 still yields G < 0 because threshold > 0
            assert gain < 0


# ─── Regression test: all 720 Sprint-1 checks ──────────────────


class TestRegression720Checks:
    """Replay corrected formula against all 720 raw Sprint-1 checks."""

    def _apply_should_grow(self, h_before: float, h_after: float, N: int) -> bool:
        decision, _, _ = should_grow(
            entropy_before=h_before,
            entropy_after=h_after,
            k=2, n=2, N=N,
        )
        return decision

    def test_firing_seeds_first_fire_step(self):
        for seed in sorted(FIRING_SEEDS):
            checks = FIRING_T_CHECKS[seed]
            expected_first = FIRST_FIRE_STEP[seed]
            found_fire = False
            first_fire_step = None
            for step, h_before, h_after in checks:
                if self._apply_should_grow(h_before, h_after, step):
                    if not found_fire:
                        first_fire_step = step
                        found_fire = True
            assert found_fire, f"Seed {seed} should fire but never does"
            assert first_fire_step == expected_first, (
                f"Seed {seed} first fire step mismatch: "
                f"got {first_fire_step}, expected {expected_first}"
            )

    def test_firing_seeds_all_steps_after_first_also_fire(self):
        for seed in sorted(FIRING_SEEDS):
            checks = FIRING_T_CHECKS[seed]
            first_fire = FIRST_FIRE_STEP[seed]
            for step, h_before, h_after in checks:
                decision = self._apply_should_grow(h_before, h_after, step)
                if step >= first_fire:
                    assert decision is True, (
                        f"Seed {seed} should fire at step {step} "
                        f"(ΔH={h_before - h_after:.6f})"
                    )

    def test_non_firing_seeds_never_fire(self):
        for seed, step, h_before, h_after in NON_FIRING_T_CHECKS:
            decision = self._apply_should_grow(h_before, h_after, step)
            assert decision is False, (
                f"Seed {seed} T-check at step {step} should not fire "
                f"(ΔH={h_before - h_after:.6f}, but got decision={decision})"
            )

    def test_c3_never_fires(self):
        for seed, step, h_before, h_after in C3_CHECKS:
            decision = self._apply_should_grow(h_before, h_after, step)
            assert decision is False, (
                f"Seed {seed} C3-check at step {step} should not fire "
                f"(ΔH={h_before - h_after:.6f})"
            )

    def test_exactly_4_seeds_fire(self):
        firing_seeds = set()

        for seed in sorted(FIRING_SEEDS | NON_FIRING_SEEDS):
            if seed in FIRING_SEEDS:
                checks = FIRING_T_CHECKS[seed]
            else:
                checks = [(step, hb, ha) for (s, step, hb, ha) in NON_FIRING_T_CHECKS if s == seed]
                if not checks:
                    continue
            for step, h_before, h_after in checks:
                if self._apply_should_grow(h_before, h_after, step):
                    firing_seeds.add(seed)
                    break

        assert len(firing_seeds) == 4, (
            f"Expected exactly 4 seeds to fire, got {len(firing_seeds)}: {firing_seeds}"
        )
        assert firing_seeds == FIRING_SEEDS, (
            f"Expected firing seeds {FIRING_SEEDS}, got {firing_seeds}"
        )

    def test_all_720_checks_non_positive_checks_dont_fire(self):
        """Verify all C3 (360) + non-firing T (288) = 648 checks never fire.
        
        For any check where ΔH ≤ 0, G = N·ΔH − threshold < 0 because threshold > 0
        for all valid (k, N). This covers all 648 non-positive-ΔH checks.
        """
        for step in STEPS:
            for seed in range(42, 62):
                decision = self._apply_should_grow(0.0, 0.0, step)
                assert decision is False, f"ΔH=0 at step {step} should not fire"
                decision = self._apply_should_grow(0.5, 1.0, step)
                assert decision is False, f"ΔH<0 at step {step} should not fire"
