"""VELYNX 6-query soul test harness (v2 - post fixes)."""
import sys, json, time, asyncio
sys.path.insert(0, "backend")

import httpx
from app.main import app

QUERIES = [
    "What is grief?",
    "What is betrayal?",
    "How does grief relate to hope?",
    "Can someone feel love and betrayal at the same time?",
    "A man forgave someone who never apologized. What is he feeling?",
    "Someone plans carefully for years then loses everything. Walk me through their inner state.",
]

SOUL_CONCEPT_NAMES = [
    "hate","understanding","pain","loneliness","hope","love","sacrifice",
    "death","depression","planning","anger","forgiveness","grief","trust",
    "betrayal","courage","jealousy","pride","regret","gratitude"
]

def classify_soul_concepts(text):
    tl = text.lower()
    return sorted(c for c in SOUL_CONCEPT_NAMES if c in tl)

async def main():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # warm
        try:
            await client.post("/query", json={"text": "ping"}, timeout=45)
        except Exception:
            pass

        results = []
        for i, q in enumerate(QUERIES):
            print(f"\n{'='*60}")
            print(f"QUERY {i+1}: {q}")
            print(f"{'='*60}")
            start = time.time()
            try:
                resp = await client.post("/query", json={"text": q}, timeout=60)
                elapsed = time.time() - start
                data = resp.json()

                answer = data.get("answer", "")
                confidence = data.get("confidence", "UNKNOWN")
                debug = data.get("debug", {})
                path = debug.get("path", "")
                soul_concepts = debug.get("soul_concepts", [])
                clamped = debug.get("confidence_clamped", False)
                soul_count = debug.get("soul_count", 0)
                soul_used = path == "soul_lookup"
                token_match = classify_soul_concepts(q)

                entry = {
                    "query": q,
                    "answer": answer,
                    "answer_preview": answer[:300] + ("..." if len(answer) > 300 else ""),
                    "confidence": confidence,
                    "path": path,
                    "soul_concepts_debug": soul_concepts,
                    "soul_count": soul_count,
                    "soul_used": soul_used,
                    "confidence_clamped": clamped,
                    "elapsed_s": round(elapsed, 2),
                    "token_matches": token_match,
                }
                results.append(entry)

                print(f"  Path:          {path}")
                print(f"  Confidence:    {confidence}")
                print(f"  Soul Used:     {soul_used}")
                print(f"  Soul Concepts: {soul_concepts}")
                print(f"  Clamped:       {clamped}")
                print(f"  Elapsed:       {elapsed:.2f}s")
                print(f"  Answer:        {entry['answer_preview']}")
                print(f"  Gaps:          {data.get('gaps', [])}")
                if data.get("citations"):
                    print(f"  Citations:     {data['citations'][:2]}")

            except Exception as e:
                elapsed = time.time() - start
                print(f"  ERROR: {e}")
                results.append({
                    "query": q, "answer": "", "answer_preview": f"ERROR: {e}",
                    "confidence": "ERROR", "path": "error",
                    "soul_concepts_debug": [], "soul_count": 0,
                    "soul_used": False, "confidence_clamped": False,
                    "elapsed_s": round(elapsed, 2),
                    "token_matches": [],
                })

        # ── Final Report ──
        print("\n\n")
        print("=" * 60)
        print("         VELYNX SOUL TEST v2 — FINAL REPORT")
        print("=" * 60)

        soul_hits = sum(1 for r in results if r["soul_used"])
        print(f"\nSoul routed: {soul_hits}/6   Soul missed: {6 - soul_hits}/6")

        for idx, r in enumerate(results, 1):
            flag = " <-- MISS (no soul)" if not r["soul_used"] else ""
            print(f"\n  [{r['confidence']:8s}] Q{idx}: {r['query'][:65]}{flag}")
            print(f"         path={r['path']}, concepts={r['soul_concepts_debug']}, "
                  f"count={r['soul_count']}, clamped={r['confidence_clamped']}, "
                  f"elapsed={r['elapsed_s']}s")

        # Level analysis
        print("\n" + "-" * 44)
        print("LEVEL ANALYSIS")
        print("-" * 44)

        # L1: Retrieval
        l1_pass = results[0]["soul_used"] and results[1]["soul_used"]
        print(f"  L1 Retrieval (keyword->soul):     {'PASS' if l1_pass else 'FAIL'}")
        for idx in [0, 1]:
            r = results[idx]
            print(f"    Q{idx+1} soul_used={r['soul_used']} concepts={r['soul_concepts_debug']}")

        # L2: Relation
        l2_queries = results[2:4]
        any_synth = any(r["soul_count"] >= 2 for r in l2_queries)
        both_hit = all(r["soul_used"] for r in l2_queries)
        l2_pass = both_hit and True  # both have >1 concept
        print(f"  L2 Relation (multi-concept):     {'PASS' if l2_pass else 'FAIL'}")
        for i, r in enumerate(l2_queries, 3):
            print(f"    Q{i} soul_used={r['soul_used']} concepts={r['soul_concepts_debug']} count={r['soul_count']}")

        # L3: Reasoning
        l3_queries = results[4:]
        l3_pass = all(r["soul_used"] for r in l3_queries)
        print(f"  L3 Reasoning (implicit/synth):  {'PASS' if l3_pass else 'FAIL'}")
        for i, r in enumerate(l3_queries, 5):
            print(f"    Q{i} soul_used={r['soul_used']} concepts={r['soul_concepts_debug']} clamped={r['confidence_clamped']}")

        # Score
        soul_score = soul_hits / 6
        syn_score = 1.0 if any_synth else 0.0
        clamp_bonus = 0.5 if any(r["confidence_clamped"] for r in results) else 0.0
        base = 2.0
        score = round(base + (soul_score * 4) + (syn_score * 2) + clamp_bonus, 1)

        print(f"\n{'='*60}")
        print(f"  OVERALL MIND CAPABILITY:  {score}/10")
        print(f"  Base capability:         {base:.1f}")
        print(f"  Soul hit rate ({int(soul_hits)}/6):      +{soul_score * 4:.1f}")
        print(f"  Multi-concept synthesis: +{syn_score * 2:.1f}")
        print(f"  Confidence calibration:  +{clamp_bonus:.1f}")
        print(f"{'='*60}")

        with open("soul_test_results_v2.json", "w") as f:
            json.dump(results, f, indent=2)
        print("\nResults saved to soul_test_results_v2.json")

asyncio.run(main())
