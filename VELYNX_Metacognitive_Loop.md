# VELYNX — Metacognitive Loop (Phase 37)
**Prompt for DeepSeek V4 Pro | Token-optimized | Maximum output**

---

## CONTEXT (read once, don't repeat back)

VELYNX is a local cognitive AI. Three layers already working:
- `embed_index.py` — GPU embeddings, semantic lookup
- `soul_graph.py` — BFS traversal, tension detection, arc synthesis  
- `scenario_engine.py` — narrative parser, query classifier, emotional arc builder

Current state: 10/10 benchmark. 20 soul concepts. SQLite graph. GTX 1070 local.

---

## YOUR TASK

Build `metacog.py` — a single new file that gives VELYNX self-awareness of its own gaps.

**One rule: touch nothing in existing files except one import line in `scenario_engine.py`.**

---

## WHAT IT MUST DO

```
Query → parse_scenario() runs → metacog wraps the output → evaluates it → returns enriched result
```

Three jobs in one file:

### Job 1: Confidence Monitor
After `parse_scenario()` returns, score the result quality:

```python
def evaluate_output(result: dict) -> dict:
    """
    Input:  parse_scenario() output dict
    Output: same dict + 'meta' key added

    meta = {
        'confidence':  float,   # 0.0–1.0
        'status':      str,     # 'strong' | 'partial' | 'gap'
        'weak_concepts': list,  # concepts that matched below threshold
        'missing_signals': list # concepts expected but absent
    }
    """
```

**Confidence scoring rules:**
- concept count ≥ 3 AND arc has ≥ 2 hops AND tension detected → 0.85+
- concept count == 2 AND arc has 1 hop → 0.55–0.75
- concept count == 1 OR no arc → 0.0–0.45
- status = 'strong' if ≥ 0.75, 'partial' if 0.45–0.74, 'gap' if < 0.45

### Job 2: Gap Detector
When status is 'partial' or 'gap', identify what's missing:

```python
def detect_gaps(query: str, result: dict) -> list:
    """
    Returns list of gap dicts:
    [
      {
        'type': 'missing_concept',   # concept exists in soul but wasn't triggered
        'concept': 'resilience',
        'reason': 'no signal match — query used indirect language'
      },
      {
        'type': 'unknown_concept',   # concept doesn't exist in soul at all
        'raw_term': 'acceptance',
        'reason': 'not in soul graph — candidate for teaching'
      }
    ]
    """
```

**Gap detection logic:**
1. Extract nouns/emotion words from query using simple word list (no NLTK)
2. For each word, check if it's in soul graph → if yes but not returned = `missing_concept`
3. If not in soul graph and not a stopword → `unknown_concept` (teach candidate)

### Job 3: Gap Logger
Persist gaps so VELYNX builds a running list of what it needs to learn:

```python
def log_gap(gap: dict, query: str) -> None:
    """
    Appends to data/gap_log.jsonl — one JSON object per line.
    Fields: timestamp, query, gap_type, concept/term, reason, status='unresolved'
    Creates file if not exists. Never overwrites.
    """
```

---

## MAIN ENTRY POINT

```python
def reflect(query: str) -> dict:
    """
    Single public function. Replaces bare parse_scenario() calls.
    
    1. Calls parse_scenario(query)
    2. Calls evaluate_output(result)
    3. If status != 'strong': calls detect_gaps(query, result)
    4. Logs each gap via log_gap()
    5. Returns enriched result with meta + gaps attached
    
    Returns:
    {
        ...original parse_scenario() output...,
        'meta': {
            'confidence': float,
            'status': str,
            'weak_concepts': list,
            'missing_signals': list
        },
        'gaps': [ ...gap dicts... ]  # empty list if status == 'strong'
    }
    """
```

---

## DATA CONTRACT

`gap_log.jsonl` format (one line per gap):
```json
{"ts": "2026-06-09T10:30:00", "query": "...", "type": "unknown_concept", "term": "acceptance", "reason": "not in soul graph", "status": "unresolved"}
```

---

## CONSTRAINTS

- **Zero new dependencies.** Use only: `json`, `datetime`, `pathlib`, `re`, `collections` — all stdlib.
- **No NLTK, no spaCy, no transformers.** Simple string ops only for gap detection.
- **One file only:** `metacog.py` in the same directory as `scenario_engine.py`.
- **One import addition** in `scenario_engine.py`: nothing else changes in existing files.
- Emotion word list for gap detection — hardcode this exact list (extend later):
  ```python
  EMOTION_WORDS = {
      "grief","loss","hope","love","hate","anger","fear","pain","trust",
      "betrayal","shame","guilt","pride","joy","sadness","loneliness",
      "courage","sacrifice","forgiveness","resilience","regret","gratitude",
      "empathy","patience","curiosity","jealousy","depression","planning",
      "understanding","death","acceptance","anxiety","confusion","wonder"
  }
  ```

---

## OUTPUT FORMAT

Deliver in this exact order, nothing else:

1. **`metacog.py`** — complete, runnable file
2. **One-line addition** for `scenario_engine.py` — exact line + where to insert it
3. **Test block** — 3 test calls using `reflect()` showing strong / partial / gap outputs
4. **Gap log sample** — what `data/gap_log.jsonl` looks like after those 3 tests

No explanations outside code comments. No preamble. No summary at the end.
Code comments should be minimal — only where logic is non-obvious.

---

## QUALITY BAR

The output should pass this mental test:
> If I paste `metacog.py` into VELYNX right now and call `reflect("I feel lost and don't know who I am anymore")`, it should return a result with `status: 'gap'`, flag `identity` or `confusion` as unknown concepts, and write a line to `gap_log.jsonl`.

That's the bar. Build to it.
