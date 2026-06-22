"""Reflex layer — instant, graph-bypassing responses for trivial inputs."""
from __future__ import annotations

import ast
import operator
import re

from backend.models.answer import AnswerResponse

# ── Constants ──────────────────────────────────────────────────────────────────

_GREETING_WORDS = {
    "hello", "hi", "hey", "yo", "hiya", "heya", "howdy", "greetings", "sup",
}
_GREETING_PHRASES = {
    "good morning", "good afternoon", "good evening", "good day",
}
_GREETING_RESPONSE = (
    "Hello! I'm VELYNX. Ask me a question and I'll reason it out for you."
)

# Allowed arithmetic operators for the safe evaluator (no pow — avoids
# exponentiation blow-ups; no names, calls, or attribute access).
_ARITH_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}
_ARITH_UNARY = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}
_ARITH_CHARS = re.compile(r"^[0-9\.\s\+\-\*\/\%\(\)]+$")

_INTERROGATIVE_LEADS = {
    "who", "what", "where", "when", "why", "how",
    "is", "are", "was", "were", "am",
    "can", "could", "do", "does", "did",
    "will", "would", "should", "may", "might", "shall",
    "whom", "whose", "which", "has", "have", "had",
}

# ── Greeting detection ────────────────────────────────────────────────────────


def reflex_greeting(text: str) -> str | None:
    """Return a friendly response if ``text`` is a basic greeting, else None."""
    cleaned = re.sub(r"[!.?,]+$", "", text.strip().lower()).strip()
    if not cleaned:
        return None
    if cleaned in _GREETING_WORDS or cleaned in _GREETING_PHRASES:
        return _GREETING_RESPONSE
    # Short opener like "hi there", "hello velynx" (<= 3 tokens, starts with a
    # greeting word).
    tokens = cleaned.split()
    if tokens and tokens[0] in _GREETING_WORDS and len(tokens) <= 3:
        return _GREETING_RESPONSE
    return None


# ── Safe arithmetic evaluation ────────────────────────────────────────────────


def _eval_arith_node(node: ast.AST) -> float:
    """Recursively evaluate a whitelisted arithmetic AST node."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise ValueError("non-numeric constant")
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ARITH_BINOPS:
        return _ARITH_BINOPS[type(node.op)](
            _eval_arith_node(node.left), _eval_arith_node(node.right)
        )
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ARITH_UNARY:
        return _ARITH_UNARY[type(node.op)](_eval_arith_node(node.operand))
    raise ValueError("disallowed arithmetic expression")


def reflex_arithmetic(text: str) -> str | None:
    """
    If ``text`` is a pure arithmetic expression, evaluate it with a safe,
    AST-based parser (no ``eval``) and return a formatted result string.
    Returns None for anything that isn't a self-contained calculation.
    """
    expr = text.strip().rstrip("=?").strip()
    if not expr or not _ARITH_CHARS.match(expr):
        return None
    # Require at least one operator so bare numbers fall through to reasoning.
    if not any(op in expr for op in "+-*/%"):
        return None
    try:
        tree = ast.parse(expr, mode="eval")
        result = _eval_arith_node(tree.body)
    except (ValueError, SyntaxError, ZeroDivisionError, TypeError):
        return None
    # Present integers without a trailing ".0".
    if isinstance(result, float) and result.is_integer():
        result = int(result)
    return f"{expr} = {result}"


# ── Reflex response ───────────────────────────────────────────────────────────


def reflex_response(text: str) -> AnswerResponse | None:
    """
    Lightweight reflex check run BEFORE the ReasoningEngine. Returns a fully
    formed AnswerResponse for greetings / pure arithmetic, or None to let the
    full cognitive pipeline handle the query.
    """
    greeting = reflex_greeting(text)
    if greeting is not None:
        return AnswerResponse(
            query=text,
            answer=greeting,
            confidence="CERTAIN",
            source="reflex",
            sources=[],
            contradictions=[],
            gaps=[],
            citations=[],
            tone="friendly",
            debug={"reflex": "greeting"},
        )

    arithmetic = reflex_arithmetic(text)
    if arithmetic is not None:
        return AnswerResponse(
            query=text,
            answer=arithmetic,
            confidence="CERTAIN",
            source="reflex",
            sources=[],
            contradictions=[],
            gaps=[],
            citations=[],
            tone="direct",
            debug={"reflex": "arithmetic"},
        )
    return None


# ── Declarative statement detection (Phase 53 knowledge acquisition gate) ─────


def is_declarative_statement(text: str) -> bool:
    """
    Fast heuristic: return True when ``text`` looks like a declarative statement
    (a fact to learn) rather than a question.

    A statement is declarative when it does NOT end in a question mark and does
    NOT start with a typical interrogative word (Who, What, Where, When, Why,
    How, Is, Can, Do, ...).
    """
    if not text:
        return False
    stripped = text.strip()
    if not stripped:
        return False
    # Questions explicitly end with '?'.
    if stripped.endswith("?"):
        return False
    # Must contain at least one alphabetic character (skip pure numbers/symbols).
    if not any(ch.isalpha() for ch in stripped):
        return False
    first_word = stripped.split()[0].lower().strip(",.!;:'\"()[]{}")
    if first_word in _INTERROGATIVE_LEADS:
        return False
    return True
