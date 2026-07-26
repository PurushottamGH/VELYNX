"""
VELYNX Capability Benchmark -- V2 Pipeline
Runs all 10 benchmark queries against the actual V2 system.
"""

import json, sys, traceback
from pathlib import Path

_backend = str(Path(__file__).parent / "backend")
if _backend not in sys.path:
    sys.path.insert(0, _backend)

from cognition.scenario_engine import parse_scenario
from soul.soul_graph import synthesize

BENCHMARK_QUERIES = [
    {
        "id": "Q1",
        "query": "I feel empty after losing someone",
        "expect_concepts": {"grief", "loss"},
        "threshold": 0.6,
        "check": "basic_retrieval",
    },
    {
        "id": "Q2",
        "query": "She trusted him completely and he lied",
        "expect_concepts": {"trust", "betrayal"},
        "check": "tension_source",
    },
    {
        "id": "Q3",
        "query": "I keep pushing forward even when it hurts",
        "expect_concepts": {"resilience", "pain", "courage"},
        "min_match": 2,
        "check": "partial_match",
    },
    {
        "id": "Q4",
        "query": "He plans everything but life keeps falling apart",
        "expect_concepts": {"planning", "grief", "loss"},
        "check": "bfs_edge",
    },
    {
        "id": "Q5",
        "query": "Loving someone means risking everything",
        "expect_concepts": {"love", "betrayal", "sacrifice"},
        "check": "tension_label",
    },
    {
        "id": "Q6",
        "query": "Grief eventually turns into something else",
        "expect_concepts": {"grief", "hope"},
        "check": "catalyzes_edge",
    },
    {
        "id": "Q7",
        "query": "A man loses his job, doubts himself, but slowly rebuilds",
        "expect_type": "scenario",
        "min_hops": 2,
        "check": "scenario_arc",
    },
    {
        "id": "Q8",
        "query": "She sacrificed her happiness for people who never noticed",
        "expect_concepts": {"sacrifice", "pain"},
        "check": "emotional_synthesis",
    },
    {
        "id": "Q9",
        "query": "Forgiveness doesn't mean forgetting",
        "expect_concepts": {"forgiveness", "grief", "trust"},
        "check": "concept_edge_link",
    },
    {
        "id": "Q10",
        "query": "He planned his whole life around her. When she left, everything collapsed. Slowly, painfully, he learned to carry the grief. And one day he woke up without the weight.",
        "expect_concepts": {"planning", "love", "grief", "loss", "resilience", "hope"},
        "min_concepts": 5,
        "min_hops": 3,
        "check": "full_pipeline",
    },
]

RESULTS = []


def score_q1(r):
    concepts = set(r.get("concepts", []))
    scores = r.get("scores", {})
    has_grief = "grief" in concepts
    has_loss = "loss" in concepts
    grief_ok = scores.get("grief", 0) > 0.6
    loss_ok = scores.get("loss", 0) > 0.6
    pass_ = all([has_grief, has_loss, grief_ok, loss_ok])
    return pass_


def score_q2(r):
    concepts = set(r.get("concepts", []))
    return "trust" in concepts and "betrayal" in concepts


def score_q3(r):
    concepts = set(r.get("concepts", []))
    expected = {"resilience", "pain", "courage"}
    found = expected & concepts
    return len(found) >= 2


def score_q4(r):
    concepts = set(r.get("concepts", []))
    return "planning" in concepts and "grief" in concepts and "loss" in concepts


def score_q5(r):
    concepts = set(r.get("concepts", []))
    return "love" in concepts and "betrayal" in concepts and "sacrifice" in concepts


def score_q6(r):
    concepts = set(r.get("concepts", []))
    return "grief" in concepts and "hope" in concepts


def score_q7(r):
    qtype = r.get("query_type", "")
    return qtype == "scenario"


def score_q8(r):
    concepts = set(r.get("concepts", []))
    return "sacrifice" in concepts and "pain" in concepts


def score_q9(r):
    concepts = set(r.get("concepts", []))
    return "forgiveness" in concepts or "grief" in concepts or "trust" in concepts


def score_q10(r):
    concepts = set(r.get("concepts", []))
    expected = {"planning", "love", "grief", "loss", "resilience", "hope"}
    found = expected & concepts
    return len(found) >= 5


SCORERS = {
    "basic_retrieval": score_q1,
    "tension_source": score_q2,
    "partial_match": score_q3,
    "bfs_edge": score_q4,
    "tension_label": score_q5,
    "catalyzes_edge": score_q6,
    "scenario_arc": score_q7,
    "emotional_synthesis": score_q8,
    "concept_edge_link": score_q9,
    "full_pipeline": score_q10,
}

NOTES_TEMPLATES = {
    "basic_retrieval": lambda r: f"grief={r['scores'].get('grief',0):.3f}, loss={r['scores'].get('loss',0):.3f}",
    "tension_source": lambda r: f"trust={'OK' if 'trust' in r['concepts'] else 'NO'}, betrayal={'OK' if 'betrayal' in r['concepts'] else 'NO'}",
    "partial_match": lambda r: f"concepts found: {r['concepts']}",
    "bfs_edge": lambda r: f"concepts: {r['concepts']}, arc: {r['arc'][:80]}",
    "tension_label": lambda r: f"concepts: {r['concepts']}, arc: {r['arc'][:80]}",
    "catalyzes_edge": lambda r: f"concepts: {r['concepts']}, arc: {r['arc'][:80]}",
    "scenario_arc": lambda r: f"type={r['query_type']}, concepts={r['concepts']}, arc={r['arc'][:80]}",
    "emotional_synthesis": lambda r: f"concepts: {r['concepts']}, arc: {r['arc'][:80]}",
    "concept_edge_link": lambda r: f"concepts: {r['concepts']}, arc: {r['arc'][:80]}",
    "full_pipeline": lambda r: f"concepts: {r['concepts']}, arc: {r['arc'][:80]}",
}


def run_benchmark():
    total = 0
    max_score = 10

    for q in BENCHMARK_QUERIES:
        qid = q["id"]
        query = q["query"]
        check = q["check"]
        scorer = SCORERS[check]
        note_fn = NOTES_TEMPLATES[check]

        print()
        print("=" * 60)
        disp = query[:80] + ("..." if len(query) > 80 else "")
        print(f'{qid}: "{disp}"')
        print("=" * 60)

        result = None
        error = None
        try:
            result = parse_scenario(query)
            concepts = result.get("concepts", [])
            if len(concepts) >= 2:
                try:
                    synth = synthesize(concepts[:3])
                    if synth:
                        result["_synth"] = synth
                except Exception:
                    pass
            pass_ = scorer(result)
        except Exception as e:
            error = traceback.format_exc()
            pass_ = False

        score = 1 if pass_ else 0
        total += score

        label = "PASS" if pass_ else "FAIL"
        notes = note_fn(result) if result else "NO RESULT"

        print(f"  Concepts: {result.get('concepts', []) if result else 'N/A'}")
        print(
            f"  Scores:  {json.dumps(result.get('scores', {}), default=str) if result else 'N/A'}"
        )
        print(f"  Type:    {result.get('query_type', 'N/A') if result else 'N/A'}")
        print(f"  Arc:     {result.get('arc', 'N/A')[:120] if result else 'N/A'}")
        if result and result.get("_synth"):
            print(f"  Synth:   {result['_synth'][:120]}")
        print(f"  >>> {qid}: {label} ({score}/1)")
        print(f"  Notes: {notes}")
        if error:
            print(f"  TRACEBACK:")
            print(error)

        RESULTS.append(
            {
                "id": qid,
                "pass": pass_,
                "score": score,
                "concepts": result.get("concepts", []) if result else [],
                "scores": result.get("scores", {}),
                "query_type": result.get("query_type", "") if result else "",
                "arc": result.get("arc", "") if result else "",
                "synth": result.get("_synth", "") if result else "",
                "error": error,
            }
        )

    print()
    print("=" * 60)
    print(f"TOTAL SCORE: {total}/{max_score}")
    print("=" * 60)

    gaps = [r for r in RESULTS if not r["pass"]]
    if gaps:
        print(f"\nGAPS IDENTIFIED ({len(gaps)} FAILS):")
        for g in gaps:
            print(f"  - {g['id']}: concepts={g['concepts']}, type={g['query_type']}")
            if g.get("error"):
                print(f"    ERROR: {g['error'][:200]}")
    else:
        print("\nGAPS IDENTIFIED: None")

    if total < max_score:
        print("\nNEXT ACTION: Fix failures before claiming 10/10 readiness.")
    else:
        print("\nNEXT ACTION: Ready for Step 3: pipeline patch + teach auto-link.")

    out_path = Path(__file__).parent / "benchmark_v2_results.json"
    out_path.write_text(json.dumps(RESULTS, indent=2), encoding="utf-8")
    print(f"\nResults saved to: {out_path}")


if __name__ == "__main__":
    run_benchmark()
