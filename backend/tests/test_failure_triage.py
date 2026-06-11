"""Smoke test for the failure-context triage refactor in scenario_engine."""
import sys
sys.path.insert(0, r"backend")
from unittest.mock import patch

# Match the test fixture from test_scenario_engine.py to prevent real embed calls.
patch("cognition.embed_index.semantic_lookup", return_value=[]).start()

from cognition.scenario_engine import parse_scenario


def test_personal_triage_doubt_myself():
    r = parse_scenario("I am failing at everything and I doubt myself")
    assert r["domain_route"] == "personal", f"got {r['domain_route']}"
    assert r["scores"].get("shame", 0) >= 1.5, f"shame={r['scores'].get('shame')}"
    assert r["scores"].get("identity", 0) >= 1.0, f"identity={r['scores'].get('identity')}"
    assert "shame" in r["concepts"][:3], r["concepts"]


def test_personal_triage_feel_like_a_failure():
    r = parse_scenario("I feel like a failure and I do not know who I am anymore")
    assert r["domain_route"] == "personal"
    assert r["scores"].get("shame", 0) >= 1.5
    assert r["scores"].get("identity", 0) >= 1.0


def test_personal_triage_self_worth():
    r = parse_scenario("I am useless, a total disappointment, and I lost faith in myself")
    assert r["domain_route"] == "personal"
    assert r["scores"].get("shame", 0) >= 1.5
    assert r["scores"].get("identity", 0) >= 1.0


def test_structural_triage_deployment_failed():
    r = parse_scenario("the deployment failed and the server is down")
    assert r["domain_route"] == "structural", f"got {r['domain_route']}"
    assert "failure" in r["domain_hits"]
    assert "shame" not in r["scores"], "shame must be stripped for structural"
    assert "identity" not in r["scores"], "identity must be stripped for structural"
    assert r["arc"] == ""


def test_structural_triage_pipeline_crash():
    r = parse_scenario("the pipeline crashed and the api is broken")
    assert r["domain_route"] == "structural"
    assert "failure" in r["domain_hits"]


def test_structural_triage_server_failure():
    r = parse_scenario("server failure on the primary node")
    assert r["domain_route"] == "structural"
    assert "failure" in r["domain_hits"]


def test_structural_triage_bottleneck():
    r = parse_scenario("the database is the bottleneck")
    assert r["domain_route"] == "structural"
    assert "bottleneck" in r["domain_hits"]


def test_no_triage_grief():
    r = parse_scenario("I lost everything and felt nothing")
    assert r["domain_route"] == "none"
    assert "grief" in r["concepts"]


def test_mixed_collision_prefers_personal():
    """When both regex sets fire, personal wins because the soul graph is the
    canonical home for lived experience."""
    r = parse_scenario("I failed at my deployment and I feel like a failure")
    assert r["domain_route"] == "personal", f"got {r['domain_route']}"


def test_return_shape_includes_new_fields():
    r = parse_scenario("I doubt myself")
    for k in ("triage", "domain_route", "domain_hits"):
        assert k in r, f"missing key {k}"


if __name__ == "__main__":
    tests = [
        test_personal_triage_doubt_myself,
        test_personal_triage_feel_like_a_failure,
        test_personal_triage_self_worth,
        test_structural_triage_deployment_failed,
        test_structural_triage_pipeline_crash,
        test_structural_triage_server_failure,
        test_structural_triage_bottleneck,
        test_no_triage_grief,
        test_mixed_collision_prefers_personal,
        test_return_shape_includes_new_fields,
    ]

    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
        except AssertionError as e:
            print(f"  FAIL  {t.__name__}: {e}")
            failed += 1

    print()
    print(f"{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
