import os
import subprocess
import sys
import time

# Ensure clean output encoding for all platforms
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def run_suite():
    suites = [
        ("Phase 53.1: Knowledge Consolidation", "backend/tests/test_cognition.py"),
        ("Phase 54: Semantic Grounding", "backend/tests/test_semantic_grounding.py"),
        ("Phase 55: Working Memory", "backend/tests/test_working_memory.py"),
        ("Phase 56: Belief Revision", "backend/tests/test_belief_revision.py"),
        ("Phase 57: Agency & Planning", "backend/tests/test_agency.py"),
        ("Phase 58: Symbolic Dynamic Agency", "backend/tests/test_dynamic_agency.py"),
        ("Phase 59: Curiosity & Goal Formation", "backend/tests/test_curiosity.py"),
        ("Phase 60.1: Epistemic State & Routing", "backend/tests/test_self_model.py"),
        ("Phase 61: Episodic Narrative Memory", "backend/tests/test_episodic_memory.py")
    ]

    total = len(suites)
    passed = 0
    failed = []

    print("=" * 72)
    print("                    VELYNX Master Cognitive Test Suite                    ")
    print("=" * 72)
    print(f"Executing {total} foundational cognitive gates...\n")

    start_time = time.time()

    # Enforce isolated test mode to prevent background loops from locking the DB
    child_env = {**os.environ, "VELYNX_TEST_MODE": "1", "PYTHONIOENCODING": "utf-8"}

    for name, script_path in suites:
        print(f"▶ Running {name}...")

        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=child_env
        )

        if result.returncode == 0:
            print(f"  [PASS] {name} cleared.\n")
            passed += 1
        else:
            print(f"  [FAIL] {name} failed!")
            print("  --- Output Tail ---")
            lines = result.stdout.strip().split('\n')
            # Output the last 20 lines to capture the failure context
            print("  " + "\n  ".join(lines[-20:]))
            print("  -------------------\n")
            failed.append(name)

    elapsed = time.time() - start_time
    print("=" * 72)
    print("                        MASTER COGNITIVE REPORT                         ")
    print("=" * 72)
    print(f"Time: {elapsed:.2f} seconds")
    print(f"Score: {passed}/{total} Suites Passed\n")

    if failed:
        print("[FAILURE] The following cognitive gates failed:")
        for f in failed:
            print(f"  - {f}")
    else:
        print("[SUCCESS] The cognitive architecture is fully stable.")
        print("          You are cleared to proceed.")

if __name__ == "__main__":
    run_suite()
