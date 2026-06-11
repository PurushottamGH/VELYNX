# VELYNX Capability Benchmark — DeepSeek Prompt
**Version:** Post-Phase-36 | **Target Score:** 10/10

---

## YOUR TASK

You are running a capability benchmark on VELYNX — a self-contained cognitive AI system.
VELYNX has three active layers:
- **Layer 1** — `embed_index.py` (GPU embeddings, semantic lookup, edge weight scoring)
- **Layer 2** — `soul_graph.py` (BFS traversal, tension detection, relational synthesis)
- **Layer 3** — `scenario_engine.py` (narrative arc builder, query classifier, emotional arc)

Run the benchmark below. For each query, call VELYNX's full pipeline and record the output.
Score each response honestly. At the end, calculate the total and identify any remaining gaps.

---

## BENCHMARK QUERIES (10 Tests)

Run each query through VELYNX's `parse_scenario()` or equivalent entry point.

### Layer 1 — Semantic Retrieval (Tests 1–3)
These test whether VELYNX finds the right soul concept from raw input.

**Q1:** `"I feel empty after losing someone"`
- Expected concepts: `grief`, `loss`
- Pass if: both concepts returned, confidence > 0.6

**Q2:** `"She trusted him completely and he lied"`
- Expected concepts: `trust`, `betrayal`
- Pass if: both returned, betrayal flagged as tension source

**Q3:** `"I keep pushing forward even when it hurts"`
- Expected concepts: `resilience`, `pain`, `courage`
- Pass if: at least 2 of 3 returned

---

### Layer 2 — Relational Soul Traversal (Tests 4–6)
These test BFS edge traversal and tension detection.

**Q4:** `"He plans everything but life keeps falling apart"`
- Expected concepts: `planning`, `grief`, `loss`
- Expected edge: `planning → diminishes → grief`
- Pass if: edge is present in arc output

**Q5:** `"Loving someone means risking everything"`
- Expected concepts: `love`, `betrayal`, `sacrifice`
- Expected tension: `love ↔ betrayal risk`
- Pass if: tension detected and labeled

**Q6:** `"Grief eventually turns into something else"`
- Expected concepts: `grief`, `hope`
- Expected edge: `grief → catalyzes → hope`
- Pass if: catalyzes edge traversed and appears in arc

---

### Layer 3 — Scenario Engine (Tests 7–9)
These test narrative arc construction and emotional synthesis.

**Q7:** `"A man loses his job, doubts himself, but slowly rebuilds"`
- Expected arc: loss → resilience (multi-hop)
- Expected type: `scenario`
- Pass if: arc has ≥ 2 hops and type is `scenario`

**Q8:** `"She sacrificed her happiness for people who never noticed"`
- Expected concepts: `sacrifice`, `pain`, `gratitude` (or absence of)
- Expected tension: sacrifice without return
- Pass if: tension present, arc explains emotional direction

**Q9:** `"Forgiveness doesn't mean forgetting"`
- Expected concepts: `forgiveness`, `grief`, `trust`
- Expected arc: forgiveness as distinct from resolution
- Pass if: forgiveness concept linked to ≥ 1 relational edge in output

---

### Full Pipeline Stress Test (Test 10)
**Q10:** `"He planned his whole life around her. When she left, everything collapsed. Slowly, painfully, he learned to carry the grief. And one day he woke up without the weight."`
- Expected concepts: `planning`, `love`, `grief`, `loss`, `resilience`, `hope`
- Expected: multi-hop arc, ≥ 1 tension, scenario type
- Pass if: ≥ 5 concepts returned, arc has ≥ 3 hops, tension detected

---

## SCORING RUBRIC

| Test | Max Points | What You're Measuring |
|------|-----------|----------------------|
| Q1 | 1 | Basic concept retrieval |
| Q2 | 1 | Tension source detection |
| Q3 | 1 | Partial match / fuzzy retrieval |
| Q4 | 1 | BFS edge traversal |
| Q5 | 1 | Tension labeling |
| Q6 | 1 | Multi-hop catalyzes edge |
| Q7 | 1 | Scenario type + multi-hop arc |
| Q8 | 1 | Emotional synthesis under ambiguity |
| Q9 | 1 | Concept-to-edge linking |
| Q10 | 1 | Full pipeline stress test |
| **Total** | **10** | |

---

## OUTPUT FORMAT

For each query, report:
```
Q[N]: PASS / FAIL
  Concepts returned: [...]
  Arc: ...
  Tension: ...
  Notes: (what was wrong if FAIL)
```

At the end, report:
```
TOTAL SCORE: X/10
GAPS IDENTIFIED: [list any FAIL reasons]
NEXT ACTION: [what to fix if score < 10]
```

---

## IMPORTANT RULES

- Do NOT fake a pass. If VELYNX returns wrong concepts or no arc, mark FAIL.
- Do NOT modify VELYNX during the benchmark. Run it as-is.
- If a query crashes VELYNX, mark FAIL and log the traceback.
- Partial outputs (some concepts correct, arc missing) = FAIL unless rubric says otherwise.

---

*This benchmark was designed to validate VELYNX post-Phase-36 across all three cognitive layers.*
*A score of 10/10 confirms readiness for Step 3: pipeline patch + teach auto-link.*
