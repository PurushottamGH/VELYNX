"""Time-shift test for MemoryCore temporal decay.

Force-inserts an experience from exactly 24 hours ago and verifies that
``retrieve_recent_state()`` returns it with a properly decayed
``current_intensity``.  Also confirms that a fresh experience stays at or
near its initial confidence.
"""

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from backend.memory.memory_graph import HEALING_THRESHOLD, MemoryCore

TEST_DB = Path("data") / "test_decay_verify.db"


def _force_insert(db_path: Path, timestamp_str: str, soul: str, domain: str, confidence: float) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS experiences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            route_type TEXT NOT NULL,
            primary_soul_concept TEXT,
            primary_domain_concept TEXT,
            confidence_score REAL DEFAULT 0.0
        )
    """)
    conn.execute("""
        INSERT INTO experiences (timestamp, route_type, primary_soul_concept,
                                 primary_domain_concept, confidence_score)
        VALUES (?, ?, ?, ?, ?)
    """, (timestamp_str, "personal", soul, domain, confidence))
    conn.commit()
    conn.close()


def test_24h_decay() -> None:
    # Clean up any previous run
    if TEST_DB.exists():
        TEST_DB.unlink()

    # Force-insert an experience from 24 hours ago
    ancient = datetime.now(timezone.utc) - timedelta(hours=24)
    ancient_str = ancient.isoformat()
    _force_insert(TEST_DB, ancient_str, soul="shame", domain="failure", confidence=0.85)

    mem = MemoryCore(TEST_DB)
    recent = mem.retrieve_recent_state(limit=1)
    assert len(recent) == 1, f"Expected 1 row, got {len(recent)}"

    entry = recent[0]
    initial = entry["confidence_score"]
    current = entry["current_intensity"]
    status = entry.get("status", "")

    print(f"24h-old memory: initial={initial:.4f}, current={current:.4f}, status={status}")

    # After 24 h with a 12 h half-life, weight should be ~0.25 of original
    # 0.85 * exp(-0.693/12 * 24) = 0.85 * exp(-1.386) ≈ 0.85 * 0.25 = 0.2125
    expected_approx = 0.85 * (0.5 ** (24 / 12))  # 0.85 * 0.25 = 0.2125
    assert current < initial, (
        f"Decayed intensity {current:.4f} should be less than initial {initial:.4f}"
    )
    assert abs(current - expected_approx) < 0.02, (
        f"Expected ~{expected_approx:.4f}, got {current:.4f}"
    )
    print(f"  Expected ~{expected_approx:.4f}, got {current:.4f} — OK")

    # With half-life 12h, after 24h intensity should be > threshold
    # since 0.85 * 0.25 = 0.2125 which is > HEALING_THRESHOLD (0.15)
    assert status != "healed", (
        f"24h memory at intensity={current:.4f} should not yet be 'healed' (threshold={HEALING_THRESHOLD})"
    )

    TEST_DB.unlink()


def test_fresh_memory() -> None:
    if TEST_DB.exists():
        TEST_DB.unlink()

    now = datetime.now(timezone.utc).isoformat()
    _force_insert(TEST_DB, now, soul="hope", domain="resilience", confidence=0.91)

    mem = MemoryCore(TEST_DB)
    recent = mem.retrieve_recent_state(limit=1)
    assert len(recent) == 1

    entry = recent[0]
    current = entry["current_intensity"]
    initial = entry["confidence_score"]

    print(f"Fresh memory: initial={initial:.4f}, current={current:.4f}")

    assert current >= 0.99 * initial, (
        f"Fresh memory intensity {current:.4f} should be >= {0.99 * initial:.4f}"
    )
    assert entry.get("status") != "healed"
    print("  Fresh memory retains full intensity — OK")

    TEST_DB.unlink()


def test_fully_healed() -> None:
    if TEST_DB.exists():
        TEST_DB.unlink()

    # 100 hours ago → should be well below HEALING_THRESHOLD
    ancient = datetime.now(timezone.utc) - timedelta(hours=100)
    ancient_str = ancient.isoformat()
    _force_insert(TEST_DB, ancient_str, soul="shame", domain="failure", confidence=0.50)

    mem = MemoryCore(TEST_DB)
    recent = mem.retrieve_recent_state(limit=1)
    assert len(recent) == 1

    entry = recent[0]
    current = entry["current_intensity"]
    status = entry.get("status", "")

    print(f"100h-old memory: initial=0.50, current={current:.6f}, status={status}")

    assert status == "healed", (
        f"100h-old memory should be 'healed', got status='{status}', intensity={current:.6f}"
    )
    assert current < HEALING_THRESHOLD, (
        f"Intensity {current:.6f} should be below HEALING_THRESHOLD {HEALING_THRESHOLD}"
    )
    print("  Correctly marked as healed — OK")

    TEST_DB.unlink()


def test_calculate_decay_direct() -> None:
    mem = MemoryCore(":memory:")
    # Exactly 12h ago → should halve
    ts = (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat()
    result = mem.calculate_decay(1.0, ts, half_life_hours=12.0)
    print(f"12h-old intensity: {result:.4f} (expected ~0.5000)")
    assert 0.49 <= result <= 0.51, f"Expected ~0.50, got {result:.4f}"

    # 24h ago → quarter
    ts = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    result = mem.calculate_decay(1.0, ts, half_life_hours=12.0)
    print(f"24h-old intensity: {result:.4f} (expected ~0.2500)")
    assert 0.24 <= result <= 0.26, f"Expected ~0.25, got {result:.4f}"

    # Edge: zero half-life
    ts = (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat()
    result = mem.calculate_decay(0.8, ts, half_life_hours=0.0)
    assert result == 0.8, f"Zero half-life should return initial, got {result}"
    print("  Direct decay math — all passed")


if __name__ == "__main__":
    print("=" * 60)
    print("Temporal Decay — Time-Shift Tests")
    print("=" * 60)
    print()

    test_calculate_decay_direct()
    print()
    test_fresh_memory()
    print()
    test_24h_decay()
    print()
    test_fully_healed()
    print()

    print("=" * 60)
    print("[PASS] All decay tests passed.")
    print("=" * 60)
