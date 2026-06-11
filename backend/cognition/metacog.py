import json
import re
from datetime import datetime, timezone
from pathlib import Path

EMOTION_WORDS = {
    "grief","loss","hope","love","hate","anger","fear","pain","trust",
    "betrayal","shame","guilt","pride","joy","sadness","loneliness",
    "courage","sacrifice","forgiveness","resilience","regret","gratitude",
    "empathy","patience","curiosity","jealousy","depression","planning",
    "understanding","death","acceptance","anxiety","confusion","wonder"
}

STOPWORDS = {
    "the","a","an","is","was","are","were","be","been","being","have","has","had",
    "do","does","did","will","would","shall","should","may","might","must","can","could",
    "i","me","my","we","us","our","you","your","he","him","his","she","her","it","its",
    "they","them","their","this","that","these","those","what","which","who","whom",
    "and","but","or","nor","not","so","if","then","else","when","where","why","how",
    "all","each","every","both","few","more","most","some","any","no","none",
    "to","of","in","for","on","with","at","by","from","up","about","into","through",
    "during","before","after","above","below","between","out","off","over","under",
    "again","once","here","there","only","own","same","too","very","just","now",
    "am","don","t","re","m","ve","ll","s","d","feel","felt","know","going","thing",
    "like","want","need","get","got","make","one","even","still","really","always",
    "never","back","away","much","many","also","think","someone","something","everything",
    "nothing","anything","myself","anymore","who","how"
}

GAP_LOG_PATH = Path(__file__).parent.parent.parent / "data" / "gap_log.jsonl"
SOUL_PATH = Path(__file__).parent.parent / "soul" / "concepts.json"


def _load_soul_concepts() -> set:
    if not SOUL_PATH.exists():
        return set()
    return set(json.loads(SOUL_PATH.read_text(encoding="utf-8")).keys())


def evaluate_output(result: dict) -> dict:
    concept_count = len(result.get("concepts", []))
    arc = result.get("arc", "")

    hops = 0
    has_tension = "tension" in arc.lower()
    if arc:
        if "leads through" in arc and "arrives at" in arc:
            hops = 3
        elif "are in tension" in arc:
            hops = 1
        elif arc:
            hops = 1

    if concept_count >= 3 and hops >= 2 and has_tension:
        confidence = 0.85 + min(concept_count - 3, 4) * 0.03
    elif concept_count >= 3 and hops >= 2:
        confidence = 0.80
    elif concept_count >= 3:
        confidence = 0.65
    elif concept_count == 2 and hops >= 1:
        confidence = 0.55 + min(hops, 2) * 0.10
    elif concept_count == 2:
        confidence = 0.50
    elif concept_count == 1:
        confidence = 0.35
    else:
        confidence = 0.0

    confidence = round(min(confidence, 1.0), 2)

    if confidence >= 0.75:
        status = "strong"
    elif confidence >= 0.45:
        status = "partial"
    else:
        status = "gap"

    scores = result.get("scores", {})
    weak_concepts = [c for c, s in scores.items() if s < 0.55]

    all_soul = _load_soul_concepts()
    activated = set(result.get("concepts", []))
    missing_signals = [c for c in all_soul if c in EMOTION_WORDS and c not in activated]

    result["meta"] = {
        "confidence": confidence,
        "status": status,
        "weak_concepts": weak_concepts[:5],
        "missing_signals": missing_signals[:5],
    }
    return result


def detect_gaps(query: str, result: dict) -> list:
    q_lower = query.lower()
    words = re.findall(r'\b[a-z]+\b', q_lower)

    soul_concepts = _load_soul_concepts()
    activated = set(result.get("concepts", []))

    gaps = []
    seen = set()

    for word in words:
        if word in STOPWORDS or len(word) < 3:
            continue
        if word in seen:
            continue
        seen.add(word)

        if word in soul_concepts and word not in activated:
            gaps.append({
                "type": "missing_concept",
                "concept": word,
                "reason": "no signal match — query used indirect language",
            })
        elif word not in soul_concepts and word in EMOTION_WORDS:
            gaps.append({
                "type": "unknown_concept",
                "raw_term": word,
                "reason": "not in soul graph — candidate for teaching",
            })

    return gaps


def log_gap(gap: dict, query: str) -> None:
    GAP_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "type": gap.get("type", ""),
        "term": gap.get("concept") or gap.get("raw_term", ""),
        "reason": gap.get("reason", ""),
        "status": "unresolved",
    }
    with open(GAP_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def reflect(query: str, parsed_result: dict | None = None) -> dict:
    if parsed_result is not None:
        result = parsed_result
    else:
        from cognition.scenario_engine import parse_scenario
        result = parse_scenario(query)

    result = evaluate_output(result)

    gaps = []
    if result["meta"]["status"] != "strong":
        gaps = detect_gaps(query, result)
        for gap in gaps:
            log_gap(gap, query)

    result["gaps"] = gaps
    return result
