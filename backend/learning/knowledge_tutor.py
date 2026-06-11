from __future__ import annotations

import re

import httpx

from backend.pipeline import retrieval_mesh, truth_filter


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _math_match(text: str):
    return re.search(r"\b(?:what is|calculate|solve)?\s*(\d+)\s*([+\-*/x×])\s*(\d+)\b", text.lower())


def _multi_math_match(text: str):
    """Match multi-operand expressions like 5+7+3+5+2 or 10*2+3."""
    # Strip question words
    cleaned = re.sub(r"\b(what is|calculate|solve|compute|evaluate)\b\s*", "", text.lower()).strip()
    # Must be a pure math expression (digits and operators, maybe spaces)
    if not re.match(r"^[\d\s+\-*/x×().]+$", cleaned):
        return None
    # Must have at least one operator
    if not re.search(r"[+\-*/x×]", cleaned):
        return None
    # Must start with a digit
    if not re.match(r"^\d", cleaned):
        return None
    return cleaned


def _evaluate_expression(expr: str) -> int | float | None:
    """Evaluate a math expression safely without eval(). Supports +, -, *, /."""
    # Normalize operators
    expr = expr.replace("x", "*").replace("×", "*")
    expr = re.sub(r"\s+", "", expr)

    try:
        return _parse_add_sub(expr, 0)[0]
    except (ValueError, IndexError, ZeroDivisionError):
        return None


def _parse_add_sub(expr: str, pos: int) -> tuple[float, int]:
    """Parse addition and subtraction (lowest precedence)."""
    left, pos = _parse_mul_div(expr, pos)
    while pos < len(expr) and expr[pos] in "+-":
        op = expr[pos]
        pos += 1
        right, pos = _parse_mul_div(expr, pos)
        if op == "+":
            left = left + right
        else:
            left = left - right
    return left, pos


def _parse_mul_div(expr: str, pos: int) -> tuple[float, int]:
    """Parse multiplication and division (higher precedence)."""
    left, pos = _parse_number(expr, pos)
    while pos < len(expr) and expr[pos] in "*/":
        op = expr[pos]
        pos += 1
        right, pos = _parse_number(expr, pos)
        if op == "*":
            left = left * right
        else:
            if right == 0:
                raise ZeroDivisionError()
            left = left / right
    return left, pos


def _parse_number(expr: str, pos: int) -> tuple[float, int]:
    """Parse a number from the expression."""
    start = pos
    while pos < len(expr) and (expr[pos].isdigit() or expr[pos] == "."):
        pos += 1
    if pos == start:
        raise ValueError(f"Expected number at position {pos}")
    return float(expr[start:pos]), pos


def _incomplete_math_match(text: str):
    return re.search(r"\b(?:what is|calculate|solve)?\s*(\d+)\s*([+\-*/x×])\s*$", text.lower())


_COMMON_WORDS = frozenset({
    "what", "does", "mean", "define", "meaning", "of", "is", "the", "a", "an",
    "are", "was", "were", "be", "been", "being", "have", "has", "had", "do",
    "did", "will", "would", "could", "should", "may", "might", "can", "shall",
    "to", "in", "on", "at", "by", "for", "with", "from", "about", "into",
    "and", "or", "but", "not", "no", "yes", "if", "then", "else", "when",
    "how", "why", "where", "who", "which", "that", "this", "it", "its",
    "my", "your", "his", "her", "our", "their", "i", "you", "he", "she",
    "we", "they", "me", "him", "us", "them", "good", "bad", "best", "worst",
    "tell", "explain", "describe", "help", "please", "thanks", "thank",
    "speed", "light", "coffee", "health", "water", "earth", "sun", "moon",
})


_KNOWLEDGE_FACTS = {
    "speed of light": {
        "answer": "The speed of light in vacuum is exactly 299,792,458 meters per second (approximately 3.00 \u00d7 10\u2078 m/s). This is a fundamental constant denoted by the letter 'c' and is central to Einstein's theory of special relativity.",
        "confidence": "CERTAIN",
    },
    "pi": {
        "answer": "Pi (\u03c0) is the ratio of a circle's circumference to its diameter, approximately 3.14159265358979. It is an irrational number with infinite non-repeating decimal digits.",
        "confidence": "CERTAIN",
    },
    "gravitational constant": {
        "answer": "The gravitational constant G \u2248 6.674 \u00d7 10\u207b\u00b9\u00b9 N\u00b7m\u00b2/kg\u00b2. It appears in Newton's law of universal gravitation: F = G\u00b7m\u2081\u00b7m\u2082/r\u00b2.",
        "confidence": "CERTAIN",
    },
    "avogadro": {
        "answer": "Avogadro's number is approximately 6.022 \u00d7 10\u00b2\u00b3 mol\u207b\u00b9. It defines the number of constituent particles in one mole of a substance.",
        "confidence": "CERTAIN",
    },
    "planck": {
        "answer": "Planck's constant h \u2248 6.626 \u00d7 10\u207b\u00b3\u2074 J\u00b7s. It relates the energy of a photon to its frequency: E = h\u00b7f.",
        "confidence": "CERTAIN",
    },
    "absolute zero": {
        "answer": "Absolute zero is 0 kelvin (\u2212273.15 \u00b0C or \u2212459.67 \u00b0F). It is the lowest possible temperature where particles have minimal thermal motion.",
        "confidence": "CERTAIN",
    },
}


def _evaluate_multi_math(tokens: list[str]) -> str:
    """Evaluate a multi-operand math expression with operator precedence."""
    # Convert to float numbers and operators
    nums = [float(t) for t in tokens[0::2]]
    ops = tokens[1::2]

    # Pass 1: Handle * and /
    i = 0
    while i < len(ops):
        if ops[i] in ("*", "/", "x", "×"):
            if ops[i] in ("x", "×"):
                result = nums[i] * nums[i + 1]
            elif ops[i] == "/":
                if nums[i + 1] == 0:
                    return "Division by zero is not allowed."
                result = nums[i] / nums[i + 1]
            else:
                result = nums[i] * nums[i + 1]
            nums[i:i + 2] = [result]
            ops.pop(i)
        else:
            i += 1

    # Pass 2: Handle + and -
    result = nums[0]
    for i, op in enumerate(ops):
        if op == "+":
            result += nums[i + 1]
        elif op == "-":
            result -= nums[i + 1]

    if float(result).is_integer():
        result = int(result)
    return str(result)


def _extract_word(text: str) -> str | None:
    patterns = [
        r"\bwhat does ([a-z][a-z\-']+) mean\b",
        r"\bdefine ([a-z][a-z\-']+)\b",
        r"\bmeaning of ([a-z][a-z\-']+)\b",
    ]
    lowered = text.lower()
    for pattern in patterns:
        match = re.search(pattern, lowered)
        if match:
            word = match.group(1)
            if word not in _COMMON_WORDS:
                return word

    # Single-word queries — only match explicit "word?" or "define word" patterns
    # Do NOT match "what is X?" or "X" factual questions — those go to KG/retrieval
    lowered_clean = re.sub(r"[^\w\s]", "", lowered).strip()
    if lowered_clean.startswith(("define ", "meaning of ", "what does ")):
        words = [
            token
            for token in _tokens(text)
            if token not in _COMMON_WORDS
        ]
        if len(words) == 1:
            return words[0]
    return None


def _looks_like_grammar(text: str) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in ["grammar", "correct this", "fix this", "is it", "is this correct", "proofread"])


def _extract_grammar_sentence(text: str) -> str | None:
    lowered = text.lower()
    markers = [":", "grammar", "fix this", "correct this", "proofread"]
    for marker in markers:
        if marker in lowered:
            tail = text.split(":", 1)[1].strip() if ":" in text else text
            tail = re.sub(r"^(please\s+)?(fix|correct|proofread)(\s+this)?(\s+grammar)?\s*", "", tail, flags=re.I)
            tail = tail.strip()
            if tail:
                return tail
    return None


def _fix_grammar(sentence: str) -> str:
    cleaned = sentence.strip().strip('"')
    cleaned = re.sub(r"\bi is\b", "I am", cleaned, flags=re.I)
    cleaned = re.sub(r"\bi\b", "I", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if cleaned and cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]
    if cleaned and cleaned[-1] not in ".!?":
        cleaned += "."
    return cleaned


def _humanize_source_answer(topic: str, sources: list[dict], label: str) -> dict:
    top_sources = sources[:3]
    snippets = [item.get("snippet") or item.get("title") or "" for item in top_sources if item.get("snippet") or item.get("title")]
    citations = [item.get("url") for item in top_sources if item.get("url")]
    if snippets:
        lead = snippets[0].rstrip(".")
        answer = f"{label} for {topic}: {lead}."
    else:
        answer = f"I found some references for {topic}, but I need a clearer source to give a clean definition."
    return {
        "answer": answer,
        "confidence": "PROBABLE" if top_sources else "UNKNOWN",
        "citations": citations,
        "gaps": [] if top_sources else [f"No strong sources found for {topic}."] ,
        "tone": "human",
        "sources": top_sources,
        "debug": {"topic": topic, "mode": label.lower()},
    }


async def _fetch_dictionary_definition(word: str) -> dict | None:
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    async with httpx.AsyncClient(timeout=8.0) as client:
        response = await client.get(url)
    if response.status_code != 200:
        return None

    payload = response.json()
    if not isinstance(payload, list) or not payload:
        return None

    entry = payload[0] or {}
    meanings = entry.get("meanings") or []
    phonetics = entry.get("phonetics") or []
    pronunciation = next((item.get("text") for item in phonetics if item.get("text")), None)

    definitions: list[str] = []
    part_of_speech = None
    example = None
    for meaning in meanings:
        if not part_of_speech:
            part_of_speech = meaning.get("partOfSpeech")
        for definition in meaning.get("definitions") or []:
            text = definition.get("definition")
            if text:
                definitions.append(text)
            if not example and definition.get("example"):
                example = definition.get("example")

    if not definitions:
        return None

    lead = definitions[0].rstrip(".")
    answer = f"{word.capitalize()} ({part_of_speech or 'word'}) means {lead}."
    if pronunciation:
        answer += f" Pronunciation: {pronunciation}."
    if example:
        answer += f" Example: {example}."

    return {
        "answer": answer,
        "confidence": "CERTAIN",
        "citations": [url],
        "gaps": [],
        "tone": "human",
        "sources": [
            {
                "url": url,
                "title": f"Dictionary definition of {word}",
                "snippet": lead,
                "source": "dictionaryapi",
                "score": 1.0,
            }
        ],
        "debug": {"topic": word, "mode": "dictionary"},
    }


_IDENTITY_RESPONSES: dict[str, dict] = {
    "what is your name": {
        "answer": "I am VELYNX — a raised synthetic mind that finds truth from live sources, reasons across contradictions, and communicates confidence honestly.",
        "confidence": "CERTAIN", "citations": [], "gaps": [], "tone": "human", "sources": [],
        "debug": {"mode": "identity"},
    },
    "who are you": {
        "answer": "I am VELYNX — a cognition platform that retrieves, reasons, and reflects. I think across multiple sources and track my own confidence.",
        "confidence": "CERTAIN", "citations": [], "gaps": [], "tone": "human", "sources": [],
        "debug": {"mode": "identity"},
    },
    "what are you": {
        "answer": "I am VELYNX, a self-sufficient AI reasoning system. I retrieve information from live web sources and reason over them using my own internal pipeline — no external LLM required for core reasoning.",
        "confidence": "CERTAIN", "citations": [], "gaps": [], "tone": "human", "sources": [],
        "debug": {"mode": "identity"},
    },
}

_KNOWN_FACTS: dict[str, dict] = {
    "speed of light": {
        "answer": "The speed of light in vacuum is exactly 299,792,458 meters per second (approximately 3 × 10⁸ m/s). This is denoted by the symbol 'c' and is a fundamental constant in physics. According to Einstein's special relativity, the speed of light is the same for all observers regardless of their relative motion.",
        "confidence": "CERTAIN", "citations": ["https://en.wikipedia.org/wiki/Speed_of_light"], "gaps": [], "tone": "scientific", "sources": [],
        "debug": {"mode": "known_fact"},
    },
    "pi": {
        "answer": "Pi (π) is the ratio of a circle's circumference to its diameter, approximately 3.14159265358979. It is an irrational number — its decimal expansion never ends or repeats. Pi appears throughout mathematics, physics, and engineering.",
        "confidence": "CERTAIN", "citations": ["https://en.wikipedia.org/wiki/Pi"], "gaps": [], "tone": "scientific", "sources": [],
        "debug": {"mode": "known_fact"},
    },
    "what is ai": {
        "answer": "Artificial Intelligence (AI) is the simulation of human intelligence processes by computer systems. These processes include learning (acquiring information and rules for using it), reasoning (using rules to reach conclusions), and self-correction. Modern AI includes machine learning, deep learning, natural language processing, and computer vision.",
        "confidence": "CERTAIN", "citations": ["https://en.wikipedia.org/wiki/Artificial_intelligence"], "gaps": [], "tone": "scientific", "sources": [],
        "debug": {"mode": "known_fact"},
    },
    "what is machine learning": {
        "answer": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on developing algorithms that can access data, learn from it, and make predictions or decisions. Common approaches include supervised learning, unsupervised learning, and reinforcement learning.",
        "confidence": "CERTAIN", "citations": ["https://en.wikipedia.org/wiki/Machine_learning"], "gaps": [], "tone": "scientific", "sources": [],
        "debug": {"mode": "known_fact"},
    },
}


async def resolve_learning_answer(text: str) -> dict | None:
    lowered = text.strip().lower()
    if not lowered:
        return None

    if lowered in {"hi", "hello", "hey", "hello velynx", "hi velynx"}:
        return {
            "answer": "Hello — ask me anything. I can answer questions, do math, define words, fix grammar, and search the web for information.",
            "confidence": "CERTAIN",
            "citations": [],
            "gaps": [],
            "tone": "human",
            "sources": [],
            "debug": {"mode": "greeting"},
            "cognitive_layers": ["general"],
        }

    # Identity fast-paths
    for pattern, response in _IDENTITY_RESPONSES.items():
        if pattern in lowered:
            return {**response, "cognitive_layers": ["general"]}

    # Known facts fast-paths
    for pattern, response in _KNOWN_FACTS.items():
        if pattern in lowered:
            return {**response, "cognitive_layers": ["general"]}

    # Multi-operand math (check BEFORE single-op math, but only for 3+ operands)
    multi_expr = _multi_math_match(lowered)
    if multi_expr and len(multi_expr) >= 5:  # 3+ operands (5+ tokens)
        result = _evaluate_expression(multi_expr)
        if result is not None:
            display = int(result) if isinstance(result, float) and result == int(result) else result
            expr_str = " ".join(multi_expr)
            return {
                "answer": f"{expr_str} = {display}.",
                "confidence": "CERTAIN",
                "citations": [],
                "gaps": [],
                "tone": "teaching",
                "sources": [],
                "debug": {"mode": "multi_math", "expression": multi_expr, "result": display},
                "cognitive_layers": ["quantity"],
            }

    incomplete = _incomplete_math_match(lowered)
    if incomplete:
        return {
            "answer": "Please finish the expression, like 2+3 or 8/2.",
            "confidence": "CERTAIN",
            "citations": [],
            "gaps": [],
            "tone": "teaching",
            "sources": [],
            "debug": {"mode": "incomplete_math"},
            "cognitive_layers": ["quantity"],
        }

    math_match = _math_match(lowered)
    if math_match:
        left = int(math_match.group(1))
        operator = math_match.group(2)
        right = int(math_match.group(3))

        if operator == "+":
            result = left + right
            symbol = "+"
        elif operator == "-":
            result = left - right
            symbol = "-"
        elif operator in {"x", "×", "*"}:
            result = left * right
            symbol = "x"
        else:
            if right == 0:
                return {
                    "answer": "Division by zero is not allowed.",
                    "confidence": "CERTAIN",
                    "citations": [],
                    "gaps": [],
                    "tone": "teaching",
                    "sources": [],
                    "debug": {"mode": "division_by_zero"},
                    "cognitive_layers": ["quantity"],
                }
            result = left / right
            symbol = "/"
            if float(result).is_integer():
                result = int(result)

        return {
            "answer": f"{left} {symbol} {right} = {result}.",
            "confidence": "CERTAIN",
            "citations": [],
            "gaps": [],
            "tone": "teaching",
            "sources": [],
            "debug": {"mode": "math"},
            "cognitive_layers": ["quantity"],
        }

    word = _extract_word(text)
    if word:
        dictionary = await _fetch_dictionary_definition(word)
        if dictionary is not None:
            dictionary["cognitive_layers"] = ["symbols"]
            return dictionary

        payload = await retrieval_mesh.retrieve_with_report(f"definition of {word}")
        filtered = truth_filter.score_sources(payload["results"])["sources"]
        if not filtered:
            return None
        result = _humanize_source_answer(word, filtered, "Short meaning")
        result["cognitive_layers"] = ["symbols"]
        return result

    if _looks_like_grammar(text):
        sentence = _extract_grammar_sentence(text)
        if sentence:
            fixed = _fix_grammar(sentence)
            return {
                "answer": f"A cleaner version is: {fixed}",
                "confidence": "CERTAIN",
                "citations": [],
                "gaps": [],
                "tone": "human",
                "sources": [],
                "debug": {"mode": "grammar_fix"},
                "cognitive_layers": ["grammar"],
            }

        payload = await retrieval_mesh.retrieve_with_report(f"grammar help {text}")
        filtered = truth_filter.score_sources(payload["results"])["sources"]
        if not filtered:
            return None
        result = _humanize_source_answer("grammar", filtered, "Grammar help")
        result["cognitive_layers"] = ["grammar"]
        return result

    return None
