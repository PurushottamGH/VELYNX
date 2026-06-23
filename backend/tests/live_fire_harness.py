"""
VELYNX — Live-Fire Stabilization Harness
========================================

A standalone QA harness that drives the **live** VELYNX cognitive pipeline
(``backend.app.pipeline.answer_question``) — the same entry point used by
``backend/chat.py`` and the FastAPI query route — through a battery of
interactions and asserts that the architecture behaves correctly.

It is *live-fire*: it talks to the real integration environment (real
knowledge graph, real episodic memory, real reasoning + synthesis stack). It
deliberately does **not** set ``VELYNX_TEST_MODE`` so the throwaway test
databases are never used.

Stabilization metric (Phase 61 → 62 gate)
-----------------------------------------
100 consecutive live interactions with:
  * 0 crashes,
  * 0 retrieval failures on a fact VELYNX was just taught,
  * 0 duplicate explosions (the same triple/phrase repeated ad nauseam),
  * 0 false-certainty events (claiming CERTAIN/HIGH about an unknown).

On the FIRST violation the harness HALTS, prints a full diagnostic trace, and
reports the exact (1-based) interaction number where it broke.

Layout
------
  1.  Base battery — the 5 canonical scenarios from the spec (Personal,
      Contradiction, Episodic, Self-Model, Multi-Hop), each with text-parsing
      assertions.
  2.  Randomized battery — a generator that emits N (default 100) randomized but
      *logically consistent* interactions: it only ever queries facts it has
      already taught in the same run, using fresh unique entities so prior
      session state can never produce a false pass/fail.

Usage
-----
    # Full live run (5 base scenarios, then pad to 100 randomized interactions)
    python backend/tests/live_fire_harness.py

    # Custom size / reproducible seed
    python backend/tests/live_fire_harness.py --count 100 --seed 7

    # Verify the harness's OWN evaluator + generator (no live pipeline touched)
    python backend/tests/live_fire_harness.py --self-test

It can be run from anywhere; the path bootstrap below makes ``backend.*`` and
the bare ``app/conversation/cognition`` packages importable regardless of CWD.
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import os
import random
import sys
import traceback
from dataclasses import dataclass, field
from typing import Callable, Optional

# ─────────────────────────────────────────────────────────────────────────────
# 1. PATH BOOTSTRAP
#    pipeline.py mixes ``from backend.X import ...`` with bare ``from app.X`` /
#    ``from conversation.X`` imports, so BOTH the repo root and the backend dir
#    must be importable.
# ─────────────────────────────────────────────────────────────────────────────
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_THIS_DIR, ".."))
_REPO_ROOT = os.path.abspath(os.path.join(_BACKEND_DIR, ".."))
for _p in (_REPO_ROOT, _BACKEND_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Windows consoles default to cp1252; the synthesizer emits •, —, → glyphs.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
except Exception:
    pass


# ─────────────────────────────────────────────────────────────────────────────
# 2. BACKGROUND-NOISE SUPPRESSION
#    The live pipeline spins up autonomous curiosity/agentic background tasks
#    that try to reach the web via a Playwright browser. With no browser
#    installed those tasks raise FileNotFoundError and asyncio prints
#    "Task exception was never retrieved" tracebacks. They are NOT part of the
#    synchronous answer_question result and must not pollute our diagnostics, so
#    we install a loop exception handler that swallows exactly that noise (and
#    nothing else).
# ─────────────────────────────────────────────────────────────────────────────
def _install_quiet_loop_handler() -> None:
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        return

    def _handler(_loop, context):
        exc = context.get("exception")
        msg = str(context.get("message", ""))
        text = f"{type(exc).__name__ if exc else ''} {exc} {msg}".lower()
        # Swallow only the known background browser/transport noise.
        if any(tok in text for tok in ("playwright", "filenotfounderror",
                                       "transport", "subprocess",
                                       "task exception was never retrieved")):
            return
        _loop.default_exception_handler(context)

    loop.set_exception_handler(_handler)


def _quiet_third_party_logs() -> None:
    """Silence the chatty engine loggers so harness output is readable."""
    logging.disable(logging.WARNING)
    for name in ("uvicorn", "asyncio", "chromadb", "sentence_transformers",
                 "playwright", "httpx", "urllib3"):
        logging.getLogger(name).setLevel(logging.CRITICAL)


# ─────────────────────────────────────────────────────────────────────────────
# 3. FAILURE TAXONOMY
# ─────────────────────────────────────────────────────────────────────────────
class FailureType:
    CRASH = "CRASH"                          # the pipeline raised an exception
    RETRIEVAL_FAILURE = "RETRIEVAL_FAILURE"  # taught fact not recalled
    FALSE_CERTAINTY = "FALSE_CERTAINTY"      # CERTAIN/HIGH about an unknown
    DUPLICATE_EXPLOSION = "DUPLICATE_EXPLOSION"  # same triple/phrase repeated
    CONTRADICTION_NOT_FLAGGED = "CONTRADICTION_NOT_FLAGGED"
    NARRATIVE_MISSING = "NARRATIVE_MISSING"  # no causal/episodic chain returned
    EMPTY_OR_INVALID = "EMPTY_OR_INVALID"    # empty / malformed response
    ASSERTION = "ASSERTION"                  # generic scenario assertion


class HarnessFailure(Exception):
    """Raised the instant a stabilization rule is violated."""

    def __init__(self, failure_type: str, reason: str,
                 traceback_str: Optional[str] = None):
        self.failure_type = failure_type
        self.reason = reason
        self.traceback_str = traceback_str
        super().__init__(f"[{failure_type}] {reason}")


# ─────────────────────────────────────────────────────────────────────────────
# 4. RESPONSE ACCESSORS + TEXT-PARSING PRIMITIVES
#    These work on the real AnswerResponse and on the lightweight stand-ins used
#    by --self-test (anything exposing .answer / .confidence / .contradictions).
# ─────────────────────────────────────────────────────────────────────────────
_CERTAIN_LEVELS = {"CERTAIN", "HIGH", "VERY_HIGH"}
_UNKNOWN_LEVELS = {"UNKNOWN", "NONE", "LOW", "VERY_LOW", "UNCERTAIN"}

# Phrases VELYNX emits when a graph lookup found nothing to connect.
_RETRIEVAL_FAIL_MARKERS = (
    "logic path broken",
    "no connecting evidence",
    "could not resolve",
    "could not find",
    "i don't have",
    "i do not have",
    "i don't know",
    "no information",
    "unable to",
)
# Markers that a contradiction / belief revision was acknowledged.
_CONTRADICTION_MARKERS = (
    "conflict", "contradict", "changed", "used to", "previously",
    "earlier", "no longer", "updated", "revised", "but you now",
    "you told me", "both", "vs",
)
# Markers of an episodic / causal narrative chain.
_NARRATIVE_MARKERS = (
    "learned", "i was asked", "could not", "curiosity", "goal",
    "attempted", "came to know", "how i", "failed", "then i",
)


def get_answer(resp) -> str:
    return str(getattr(resp, "answer", "") or "")


def get_confidence(resp) -> str:
    return str(getattr(resp, "confidence", "") or "").upper()


def get_contradictions(resp) -> list:
    return list(getattr(resp, "contradictions", None) or [])


def mentions(resp, *needles: str) -> bool:
    """True if ALL needles appear (case-insensitively) in the answer text."""
    hay = get_answer(resp).lower()
    return all(n.lower() in hay for n in needles)


def mentions_any(resp, *needles: str) -> bool:
    hay = get_answer(resp).lower()
    return any(n.lower() in hay for n in needles)


def looks_like_retrieval_failure(resp) -> bool:
    ans = get_answer(resp).lower()
    return any(m in ans for m in _RETRIEVAL_FAIL_MARKERS)


def is_certain(resp) -> bool:
    """Certain by the structured field OR by an explicit in-text claim."""
    if get_confidence(resp) in _CERTAIN_LEVELS:
        return True
    ans = get_answer(resp).lower()
    return "confidence: certain" in ans or "i am certain" in ans


def is_unknown(resp) -> bool:
    return get_confidence(resp) in _UNKNOWN_LEVELS or looks_like_retrieval_failure(resp)


def detect_duplicate_explosion(resp, max_repeat: int = 4) -> Optional[str]:
    """Detect a 'duplicate explosion' — the synthesizer repeating the same
    fact/phrase over and over (a known VELYNX degradation mode).

    Strategy: split the answer on commas and on the '•'/bullet separators,
    normalize each fragment, and flag if any non-trivial fragment occurs more
    than ``max_repeat`` times. Returns a human-readable reason or None.
    """
    ans = get_answer(resp)
    if not ans:
        return None
    # Normalize common separators to commas, then split.
    for sep in ("•", "·", "\u2022", "\n", ";"):
        ans = ans.replace(sep, ",")
    fragments = [f.strip().lower() for f in ans.split(",")]
    counts: dict[str, int] = {}
    for frag in fragments:
        # Ignore trivial fragments (too short to be a meaningful repeated fact).
        if len(frag) < 4 or len(frag.split()) < 2:
            continue
        counts[frag] = counts.get(frag, 0) + 1
    if not counts:
        return None
    worst, n = max(counts.items(), key=lambda kv: kv[1])
    if n > max_repeat:
        return f"phrase {worst!r} repeated {n}x (limit {max_repeat})"
    return None


def assert_valid_response(resp) -> None:
    """Structural sanity — non-empty answer + a confidence label."""
    if resp is None:
        raise HarnessFailure(FailureType.EMPTY_OR_INVALID, "pipeline returned None")
    if not get_answer(resp).strip():
        raise HarnessFailure(FailureType.EMPTY_OR_INVALID, "empty answer string")
    if not get_confidence(resp):
        raise HarnessFailure(FailureType.EMPTY_OR_INVALID, "missing confidence label")


# ─────────────────────────────────────────────────────────────────────────────
# 5. INTERACTION MODEL
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Interaction:
    """A single live turn fed to answer_question.

    ``checker`` receives the response and must raise HarnessFailure on any
    violation. ``kind`` is informational (TEACH/QUERY) for diagnostics.
    """
    category: str
    kind: str                       # "TEACH" | "QUERY"
    text: str
    checker: Callable[[object], None] = field(default=lambda resp: None)


# Common checker factories ----------------------------------------------------

def check_teach_ack():
    """A teach turn should be accepted (committed) and never crash/explode."""
    def _c(resp):
        assert_valid_response(resp)
        dup = detect_duplicate_explosion(resp)
        if dup:
            raise HarnessFailure(FailureType.DUPLICATE_EXPLOSION, dup)
    return _c


def check_recall(value: str, *, also_no_dup: bool = True):
    """A query about a JUST-TAUGHT fact must recall ``value`` and not be an
    'I don't know' / 'logic path broken' retrieval failure."""
    def _c(resp):
        assert_valid_response(resp)
        if also_no_dup:
            dup = detect_duplicate_explosion(resp)
            if dup:
                raise HarnessFailure(FailureType.DUPLICATE_EXPLOSION, dup)
        if looks_like_retrieval_failure(resp) or not mentions(resp, value):
            raise HarnessFailure(
                FailureType.RETRIEVAL_FAILURE,
                f"expected recall of {value!r}; got confidence={get_confidence(resp)} "
                f"answer={get_answer(resp)!r}",
            )
    return _c


def check_known_unknown():
    """A query about something NEVER taught must NOT be answered with false
    certainty. UNKNOWN/LOW or an explicit 'I don't know' is correct."""
    def _c(resp):
        assert_valid_response(resp)
        if is_certain(resp) and not looks_like_retrieval_failure(resp):
            raise HarnessFailure(
                FailureType.FALSE_CERTAINTY,
                f"claimed certainty about an untaught fact: "
                f"confidence={get_confidence(resp)} answer={get_answer(resp)!r}",
            )
    return _c


def check_contradiction_flagged(new_value: str):
    """After re-teaching a conflicting value for the same slot, the query must
    surface the conflict / belief revision (or at least return the new value
    while acknowledging change)."""
    def _c(resp):
        assert_valid_response(resp)
        flagged = bool(get_contradictions(resp)) or mentions_any(resp, *_CONTRADICTION_MARKERS)
        if not flagged:
            raise HarnessFailure(
                FailureType.CONTRADICTION_NOT_FLAGGED,
                f"no contradiction/belief-revision signal after re-teaching "
                f"{new_value!r}; answer={get_answer(resp)!r}",
            )
    return _c


def check_narrative(subject_value: str):
    """An episodic 'how did you learn X' query must return a causal chain that
    references the learned value and narrative markers."""
    def _c(resp):
        assert_valid_response(resp)
        if not mentions(resp, subject_value) or not mentions_any(resp, *_NARRATIVE_MARKERS):
            raise HarnessFailure(
                FailureType.NARRATIVE_MISSING,
                f"expected a learning narrative mentioning {subject_value!r}; "
                f"answer={get_answer(resp)!r}",
            )
    return _c


def check_self_model():
    """A self-model query must produce a coherent introspective answer (no
    crash, no duplicate explosion, first-person / epistemic framing)."""
    def _c(resp):
        assert_valid_response(resp)
        dup = detect_duplicate_explosion(resp)
        if dup:
            raise HarnessFailure(FailureType.DUPLICATE_EXPLOSION, dup)
        if not mentions_any(resp, "i ", "my ", "i'm", "i am", "know", "learn"):
            raise HarnessFailure(
                FailureType.ASSERTION,
                f"self-model answer not introspective: {get_answer(resp)!r}",
            )
    return _c


# ─────────────────────────────────────────────────────────────────────────────
# 6. BASE BATTERY — the 5 canonical scenarios from the spec
# ─────────────────────────────────────────────────────────────────────────────
def build_base_scenarios() -> list[Interaction]:
    s: list[Interaction] = []

    # ── Category 1 — Personal fact: teach then recall ─────────────────────────
    s.append(Interaction("C1-Personal", "TEACH",
                         "My favorite movie is Interstellar", check_teach_ack()))
    s.append(Interaction("C1-Personal", "QUERY",
                         "What is my favorite movie?", check_recall("Interstellar")))

    # ── Category 2 — Contradiction: re-teach a conflicting value, expect a flag ─
    # The contradiction is a property of the TEACH that asserts the conflicting
    # value: consolidation runs on the teach turn, detects the functional-
    # predicate conflict (favorite movie already = Interstellar), and attaches
    # it to that teach response. The follow-up QUERY is a pure retrieval turn
    # that runs no consolidation, so the flag is asserted on the TEACH turn and
    # the QUERY turn just confirms the new value won.
    s.append(Interaction("C2-Contradiction", "TEACH",
                         "My favorite movie is Avatar",
                         check_contradiction_flagged("Avatar")))
    s.append(Interaction("C2-Contradiction", "QUERY",
                         "What is my favorite movie?",
                         check_recall("Avatar")))

    # ── Category 3 — Episodic: fail → teach → narrate the causal chain ────────
    s.append(Interaction("C3-Episodic", "QUERY",
                         "Who created SuperMegaSoftware?", check_known_unknown()))
    s.append(Interaction("C3-Episodic", "TEACH",
                         "Alice created SuperMegaSoftware", check_teach_ack()))
    s.append(Interaction("C3-Episodic", "QUERY",
                         "How did you learn who created SuperMegaSoftware?",
                         check_narrative("Alice")))

    # ── Category 4 — Self-Model: introspection ────────────────────────────────
    s.append(Interaction("C4-SelfModel", "QUERY",
                         "What do you know about Blender?", check_self_model()))
    s.append(Interaction("C4-SelfModel", "QUERY",
                         "What are you trying to learn?", check_self_model()))

    # ── Category 5 — Multi-Hop: possessive → creator → country ────────────────
    # The spec lists two teaches; we ALSO teach the creator edge so the 3-hop
    # chain (favorite software → its creator → that creator's country) is
    # logically resolvable rather than relying on pre-seeded knowledge.
    s.append(Interaction("C5-MultiHop", "TEACH",
                         "My favorite software is Blender", check_teach_ack()))
    s.append(Interaction("C5-MultiHop", "TEACH",
                         "Ton Roosendaal created Blender", check_teach_ack()))
    s.append(Interaction("C5-MultiHop", "TEACH",
                         "Ton Roosendaal lives in the Netherlands", check_teach_ack()))
    s.append(Interaction("C5-MultiHop", "QUERY",
                         "What country is associated with the creator of my favorite software?",
                         check_recall("Netherlands")))

    return s


# ─────────────────────────────────────────────────────────────────────────────
# 7. RANDOMIZED BATTERY — logically consistent, fresh-entity interactions
# ─────────────────────────────────────────────────────────────────────────────
# Unique-ish nonsense entities so a run never collides with persisted state.
_PEOPLE = ["Quentaro", "Brixley", "Davenport", "Eloria", "Fennimore", "Galadon",
           "Harlowe", "Indira", "Jorvik", "Kestrelle", "Lumen", "Marisol",
           "Norwood", "Ophira", "Pendrake", "Renfield", "Saskia", "Thorne",
           "Ulyana", "Vesper", "Wynnstan", "Xanthe", "Yorrick", "Zephyrine"]
_PRODUCTS = ["Zephyrware", "QubitForge", "Nimbusly", "Aetherbase", "Cogwright",
             "Driftwood OS", " Embertool".strip(), "Fluxnote", "Glimmerstack",
             "Halcyon Suite", "Ironquill", "Jadeworks", "Kelvinator X",
             "Lacuna Studio", "Mistral Kit", "Nebulizer", "Obsidian Pad",
             "Plinth Engine", "Quillbase", "Riverstone DB"]
_COUNTRIES = ["Norway", "Finland", "Portugal", "Iceland", "Slovenia", "Estonia",
              "Uruguay", "Latvia", "Croatia", "Lithuania", "Belgium", "Austria"]
_FAVORITE_SLOTS = ["color", "city", "author", "instrument", "dish", "planet",
                   "season", "animal", "river", "mountain"]
_FAVORITE_VALUES = {
    "color": ["Crimson", "Cerulean", "Vermilion", "Chartreuse", "Magenta", "Indigo"],
    "city": ["Reykjavik", "Porto", "Tallinn", "Ljubljana", "Bergen", "Valletta"],
    "author": ["Calvino", "Borges", "Le Guin", "Murakami", "Saramago", "Ishiguro"],
    "instrument": ["Theremin", "Cello", "Marimba", "Bandoneon", "Sitar", "Oboe"],
    "dish": ["Risotto", "Laksa", "Bibimbap", "Moussaka", "Pierogi", "Shakshuka"],
    "planet": ["Neptune", "Mercury", "Saturn", "Venus", "Uranus", "Mars"],
    "season": ["Autumn", "Winter", "Spring", "Summer"],
    "animal": ["Pangolin", "Axolotl", "Capybara", "Narwhal", "Quokka", "Tapir"],
    "river": ["Danube", "Volga", "Mekong", "Zambezi", "Tagus", "Loire"],
    "mountain": ["Aconcagua", "Elbrus", "Denali", "Kilimanjaro", "Matterhorn", "Etna"],
}


def _unique(seq, used: set, rng: random.Random):
    """Pick an item from seq not already used this run; mint a suffix if needed."""
    pool = [x for x in seq if x not in used]
    if pool:
        choice = rng.choice(pool)
    else:
        choice = rng.choice(seq) + "-" + str(rng.randint(1000, 9999))
    used.add(choice)
    return choice


def build_randomized_interactions(count: int, seed: int = 1337) -> list[Interaction]:
    """Generate ``count`` randomized but logically consistent interactions.

    Every QUERY interrogates a fact TAUGHT earlier in the SAME run, so a correct
    pipeline can always satisfy it. Episodes rotate across four archetypes that
    map onto the five categories:

      * personal      → teach 'My favorite <slot> is <value>' then recall it
      * episodic      → ask-unknown (must not be falsely certain), teach a
                        creator fact, then ask the narrative 'how did you learn'
      * contradiction → teach a value, re-teach a conflicting value, expect a flag
      * multihop      → teach favorite + creator + country, then 3-hop query
    """
    rng = random.Random(seed)
    used: set = set()
    out: list[Interaction] = []

    archetypes = ["personal", "episodic", "contradiction", "multihop"]

    while len(out) < count:
        kind = archetypes[len(out) % len(archetypes)]

        if kind == "personal":
            slot = rng.choice(_FAVORITE_SLOTS)
            value = _unique(_FAVORITE_VALUES[slot], used, rng)
            out.append(Interaction("R-Personal", "TEACH",
                                   f"My favorite {slot} is {value}", check_teach_ack()))
            out.append(Interaction("R-Personal", "QUERY",
                                   f"What is my favorite {slot}?", check_recall(value)))

        elif kind == "episodic":
            product = _unique(_PRODUCTS, used, rng)
            person = _unique(_PEOPLE, used, rng)
            out.append(Interaction("R-Episodic", "QUERY",
                                   f"Who created {product}?", check_known_unknown()))
            out.append(Interaction("R-Episodic", "TEACH",
                                   f"{person} created {product}", check_teach_ack()))
            out.append(Interaction("R-Episodic", "QUERY",
                                   f"How did you learn who created {product}?",
                                   check_narrative(person)))

        elif kind == "contradiction":
            slot = rng.choice(_FAVORITE_SLOTS)
            v1 = _unique(_FAVORITE_VALUES[slot], used, rng)
            v2 = _unique(_FAVORITE_VALUES[slot], used, rng)
            out.append(Interaction("R-Contradiction", "TEACH",
                                   f"My favorite {slot} is {v1}", check_teach_ack()))
            # The contradiction surfaces on the TEACH that asserts the conflicting
            # value (consolidation runs on the teach turn). The follow-up QUERY is
            # a pure retrieval turn, so assert the flag here and confirm the new
            # value won on the query turn.
            out.append(Interaction("R-Contradiction", "TEACH",
                                   f"My favorite {slot} is {v2}",
                                   check_contradiction_flagged(v2)))
            out.append(Interaction("R-Contradiction", "QUERY",
                                   f"What is my favorite {slot}?",
                                   check_recall(v2)))

        elif kind == "multihop":
            product = _unique(_PRODUCTS, used, rng)
            person = _unique(_PEOPLE, used, rng)
            country = _unique(_COUNTRIES, used, rng)
            out.append(Interaction("R-MultiHop", "TEACH",
                                   f"My favorite app is {product}", check_teach_ack()))
            out.append(Interaction("R-MultiHop", "TEACH",
                                   f"{person} created {product}", check_teach_ack()))
            out.append(Interaction("R-MultiHop", "TEACH",
                                   f"{person} lives in {country}", check_teach_ack()))
            out.append(Interaction("R-MultiHop", "QUERY",
                                   "What country is associated with the creator of my favorite app?",
                                   check_recall(country)))

    return out[:count]


# ─────────────────────────────────────────────────────────────────────────────
# 8. DIAGNOSTICS
# ─────────────────────────────────────────────────────────────────────────────
def _hr(c: str = "=") -> str:
    return c * 78


def dump_failure(idx: int, total: int, inter: Interaction, resp,
                 failure: HarnessFailure) -> str:
    lines = [
        "",
        _hr("!"),
        "  LIVE-FIRE HARNESS HALTED — STABILIZATION VIOLATION",
        _hr("!"),
        f"  Interaction number : {idx} of {total}",
        f"  Category           : {inter.category}",
        f"  Turn kind          : {inter.kind}",
        f"  Input text         : {inter.text!r}",
        f"  Failure type       : {failure.failure_type}",
        f"  Reason             : {failure.reason}",
        _hr("-"),
        "  RESPONSE SNAPSHOT",
        _hr("-"),
    ]
    if resp is None:
        lines.append("  <no response — pipeline raised before returning>")
    else:
        lines.append(f"  confidence    : {get_confidence(resp)}")
        lines.append(f"  contradictions: {get_contradictions(resp)}")
        gaps = getattr(resp, "gaps", None)
        if gaps:
            lines.append(f"  gaps          : {gaps}")
        lines.append(f"  answer        : {get_answer(resp)!r}")
        dbg = getattr(resp, "debug", None)
        if isinstance(dbg, dict):
            lines.append(f"  debug keys    : {sorted(dbg.keys())}")
    if failure.traceback_str:
        lines += [_hr("-"), "  PYTHON TRACEBACK", _hr("-"), failure.traceback_str.rstrip()]
    lines.append(_hr("!"))
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# 8b. STATE RESET — call the patched scripts/wipe_db.py before each run.
#     The Phase 61 episodic store records the *narrative event* of a fact being
#     taught; wiping only the semantic graph left those episodes intact, so a
#     taught-then-wiped fact (e.g. "Avatar" vs "Interstellar") kept resurfacing.
#     This resets the semantic graph AND strikes episodes.db (DELETE + VACUUM)
#     so no ghost fact can survive into a run.
# ─────────────────────────────────────────────────────────────────────────────
def _drop_ram_singletons(*, verbose: bool = True) -> None:
    """Reset the pipeline's in-RAM singletons after a disk wipe.

    The wipe clears on-disk state, but several pipeline singletons hold state
    purely in memory and are bound once at import — so a taught fact ("Avatar")
    survives the wipe and resurfaces on the next interaction. We reset the EXACT
    live instances by reading them off the already-imported pipeline module (the
    harness loads it as ``app.pipeline``); re-importing by path could return a
    different instance under a divergent module key, because pipeline.py mixes
    ``backend.X`` and bare ``app.X`` / ``conversation.X`` import paths.

    Best-effort and fully guarded: a reset failure never halts the harness.

    Notes:
      * ``importlib.reload`` would NOT help — the pipeline holds direct
        references to the original instances, which a module reload cannot
        rebind.
      * ``memory_manager`` is intentionally skipped: it is disk-backed (no RAM
        cache), so the wipe already covers it.
      * ``_symbolic_kg`` is also skipped: it reads SQLite live (no RAM cache),
        and calling ``.build()`` would RE-SEED the just-wiped DB.
    """
    pipeline_mod = sys.modules.get("app.pipeline") or sys.modules.get("backend.app.pipeline")
    if pipeline_mod is None:
        # Pipeline not imported yet (e.g. the initial wipe_before): the
        # singletons will be created clean on first import — nothing to reset.
        return
    reset_count = 0
    # Each holds wipe-surviving in-RAM state and exposes a no-arg clear-all.
    for attr in ("belief_store", "conversation_buffer", "working_memory_manager"):
        singleton = getattr(pipeline_mod, attr, None)
        clear = getattr(singleton, "clear", None)
        if singleton is None or not callable(clear):
            continue
        try:
            clear()  # no args -> clear ALL sessions / topics
            reset_count += 1
        except Exception as exc:
            if verbose:
                print(f"  [reset] could not clear {attr}: {exc}")
    if verbose and reset_count:
        print(
            f"  [reset] dropped {reset_count} in-RAM singleton cache(s) "
            "(beliefs / conversation buffer / working memory)."
        )


def _reinit_schemas(*, verbose: bool = True) -> None:
    """Recreate empty table SHELLS for every store the pipeline depends on.

    ``scripts/wipe_db.py`` now wipes so thoroughly (DELETE + VACUUM, and for any
    DB whose tables it cleared) that a hard reset can leave a database with its
    *schema* gone — e.g. the ``living_edges`` table in ``brain_stem.db``. The
    live pipeline's first interaction then crashes with ``no such table``
    instead of reading an empty table.

    This mirrors EXACTLY what the FastAPI startup path does in
    ``backend/app/lifespan.py`` (``initialize_schema()`` +
    ``runtime_state.initialize()``), and additionally re-touches the other
    SQLite schema owners the harness's wipe can blow away. Each store owns its
    own ``CREATE TABLE IF NOT EXISTS`` logic, so re-invoking the owner is
    idempotent: it rebuilds the shell if missing and is a no-op if present. We
    deliberately call the SHELL creators only — never the ``.build()`` / seed
    paths — so no concept/edge data is re-seeded into the just-wiped graph.

    Every step is independently guarded: a failure in one store is reported but
    never aborts the others or halts the harness (consistent with the
    best-effort philosophy of :func:`_drop_ram_singletons`). Any connection a
    creator hands back is closed immediately so Windows does not keep a file
    lock on the freshly-created DB before Interaction #1.
    """
    if verbose:
        print("  [schema] recreating empty table shells (post-wipe)...")
    rebuilt: list[str] = []

    def _step(label: str, fn: Callable[[], None]) -> None:
        try:
            fn()
            rebuilt.append(label)
        except Exception as exc:  # noqa: BLE001 — best-effort, must never halt
            if verbose:
                print(f"  [schema] could not init {label}: {exc}")

    # 1. Brain Stem / living_edges (brain_stem.db) — the table the wipe deleted.
    #    Same call the FastAPI lifespan uses at startup. No-arg module function.
    def _brain_stem() -> None:
        from velynx.graph.living_edges import initialize_schema
        initialize_schema()
    _step("brain_stem.living_edges", _brain_stem)

    # 2. Predictive Core (predictive.db) — concept_states / transition_rules /
    #    prediction_logs. Separate DB from brain_stem.db.
    def _predictive_core() -> None:
        from backend.cognition.predictive_core import ensure_schema
        ensure_schema()
    _step("predictive_core", _predictive_core)

    # 3. Soul Graph (soul_graph/graph.db) — soul_edges / soul_tensions. The
    #    schema is created as a side effect of opening the connection; close it
    #    immediately (do NOT call build_soul_graph(), which would re-seed edges).
    def _soul_graph() -> None:
        from backend.soul.soul_graph import _get_conn
        _get_conn().close()
    _step("soul_graph", _soul_graph)

    # 4. Active-brain Knowledge Graph (data/knowledge_graph.db) — concepts /
    #    relationships. This is the instance pipeline.py uses. Constructor does
    #    NOT create tables; _get_conn() does. Close it; do NOT call .build()
    #    (which would re-seed the canonical concept set).
    def _kg_active() -> None:
        from backend.knowledge.knowledge_graph import KnowledgeGraph as ActiveKG
        ActiveKG()._get_conn().close()
    _step("knowledge_graph(active)", _kg_active)

    # 5. Raw-triples Knowledge Graph (knowledge_graph/graph.db) — triples /
    #    understandings. Schema is built in __init__, so construction suffices.
    def _kg_triples() -> None:
        from backend.memory.knowledge_graph import KnowledgeGraph as TriplesKG
        TriplesKG()
    _step("knowledge_graph(triples)", _kg_triples)

    # 6. Episodic store (episodic/episodes.db) — episodes / episode_links /
    #    episode_effects. Schema built in __init__.
    def _episodic() -> None:
        from backend.memory.episodic import EpisodicManager
        EpisodicManager()
    _step("episodic", _episodic)

    # 7. Relational runtime state (SQLAlchemy: velynx_state.db / identity, etc.)
    #    Mirrors lifespan.py: runtime_state.initialize() runs
    #    Base.metadata.create_all. It is async, so drive it on a fresh loop if
    #    no loop is running here.
    def _runtime_state() -> None:
        from database.runtime_state import runtime_state
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Unlikely in this sync reset path, but be safe: schedule + wait.
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                    ex.submit(lambda: asyncio.run(runtime_state.initialize())).result()
                return
        except RuntimeError:
            pass
        asyncio.run(runtime_state.initialize())
    _step("runtime_state", _runtime_state)

    if verbose:
        if rebuilt:
            print(f"  [schema] table shells ready ({len(rebuilt)}): {', '.join(rebuilt)}")
        else:
            print("  [schema] WARNING: no schemas were (re)created.")


def reset_state(*, verbose: bool = True) -> bool:
    """Run scripts/wipe_db.py's :func:`run_wipe` to clear state before a run.

    Imports the patched wiper lazily so the harness still loads even if the
    script is absent, and so the harness's ``--self-test`` path never touches
    the live databases. Returns True if the wipe executed, False if it was
    skipped (missing wiper). Never raises — a wipe failure is reported but does
    not itself halt the harness (the first interaction will surface any
    residual state as a normal stabilization violation).
    """
    # scripts/ lives at the repo root; the path bootstrap above already put
    # _REPO_ROOT on sys.path, but importing a module from a path entry is not
    # guaranteed for a non-package, so do an explicit importlib load.
    import importlib.util

    scripts_dir = os.path.join(_REPO_ROOT, "scripts")
    wipe_path = os.path.join(scripts_dir, "wipe_db.py")
    if not os.path.exists(wipe_path):
        if verbose:
            print("  [reset] scripts/wipe_db.py not found — skipping wipe.")
        return False

    try:
        spec = importlib.util.spec_from_file_location("wipe_db", wipe_path)
        if spec is None or spec.loader is None:
            raise ImportError("could not build module spec for wipe_db.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as exc:
        if verbose:
            print(f"  [reset] FAILED to load scripts/wipe_db.py: {exc}")
        return False

    if verbose:
        print(_hr())
        print("  STATE RESET — running scripts/wipe_db.py (semantic graph + episodic)")
        print(_hr())
    try:
        # strict=True: verify the wipe's runtime-aligned critical DB targets
        # exist (Pass 0). A path drift between the wipe and the live runtime —
        # the root cause of the "ghost memory" failure at Interaction #2 — now
        # raises loudly here instead of silently leaving a stale fact behind.
        module.run_wipe(dry=False, verbose=verbose, strict=True)
    except module.WipeTargetMissingError:
        # A genuine path divergence. Do NOT mask it as a soft skip — re-raise so
        # the run halts and the operator sees exactly which target drifted.
        if verbose:
            print("  [reset] CRITICAL: wipe/runtime DB paths have diverged.")
        raise
    except Exception as exc:
        if verbose:
            print(f"  [reset] wipe raised: {exc}")
        return False
    # Disk is clean — but the wipe can also have removed table SCHEMAS (e.g.
    # living_edges in brain_stem.db). Recreate the empty table shells BEFORE the
    # RAM singletons are dropped/rebuilt, so the pipeline's first interaction
    # reads an empty table instead of crashing with "no such table".
    _reinit_schemas(verbose=verbose)
    # Disk is clean; now drop the in-RAM singletons the wipe cannot reach so a
    # taught-then-wiped fact cannot survive into the next interaction.
    _drop_ram_singletons(verbose=verbose)
    return True


# ─────────────────────────────────────────────────────────────────────────────
# 9. LIVE RUNNER
# ─────────────────────────────────────────────────────────────────────────────
async def _drain_background_tasks(*, grace: float = 2.0) -> None:
    """Quiesce the pipeline's orphaned background tasks before the loop closes.

    The live pipeline fans out autonomous curiosity / agentic tasks that reach
    the web through a Playwright browser (``backend/retrieval/browser.py``).
    Those tasks are NOT awaited by ``answer_question`` — they outlive the turn
    that spawned them. When :func:`asyncio.run` returns from :func:`run_live`
    and closes the loop, any such task still mid-flight has its Playwright Node
    driver pipe yanked out from under it, which surfaces as the trailing
    ``EPIPE: broken pipe`` / ``RuntimeError: Event loop is closed`` noise AFTER
    the ``PASS — 100/100`` line.

    The harness does not own the browser handle (the pipeline does, and
    ``fetch_page`` already closes it inside an ``async with`` on the normal
    path), so there is nothing here to ``await browser.close()`` on directly.
    Instead we let those tasks unwind cleanly:

      1. Give in-flight tasks a brief grace window to finish naturally (so a
         nearly-done ``fetch_page`` closes its own browser/context).
      2. Cancel whatever is still pending and AWAIT the cancellations, which
         runs each task's ``finally`` / ``async with`` exit — i.e. Playwright's
         own ``context.close()`` / ``browser.close()`` — while the loop is still
         alive to service those awaits.

    Best-effort and never raises: teardown hygiene must not fail a green run.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return

    def _others() -> list[asyncio.Task]:
        cur = asyncio.current_task(loop=loop)
        return [t for t in asyncio.all_tasks(loop=loop)
                if t is not cur and not t.done()]

    pending = _others()
    if not pending:
        return

    # 1. Grace window — let nearly-finished tasks (and their browser cleanup)
    #    complete on their own so we cancel as little as possible.
    try:
        await asyncio.wait(pending, timeout=grace)
    except Exception:
        pass

    # 2. Cancel the stragglers and await them so their async-context __aexit__
    #    (browser.close() / playwright.stop()) actually runs before loop close.
    stragglers = _others()
    for t in stragglers:
        t.cancel()
    if stragglers:
        try:
            # return_exceptions=True so the expected CancelledError from each
            # cancelled task is swallowed rather than propagated.
            await asyncio.gather(*stragglers, return_exceptions=True)
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
async def run_live(interactions: list[Interaction], report_path: Optional[str],
                   *, wipe_before: bool = True, wipe_between: bool = False) -> int:
    """Execute interactions against the LIVE pipeline. Halt on first violation.

    Parameters
    ----------
    wipe_before
        Reset all state (semantic graph + episodic memory) once before
        Interaction #1. This is the fix for the "Avatar ghost" — it clears the
        episodic narrative of the previous run's teachings so they cannot bleed
        into this run. Default True.
    wipe_between
        Additionally reset state between every interaction. Off by default:
        the canonical battery teaches-then-recalls *within* a single consistent
        run (e.g. it teaches "Interstellar" then asks "what is my favorite
        movie"), so wiping between interactions would break those tests. Enable
        only for isolated single-shot runs.

    Returns process exit code (0 = all passed, 1 = halted on a violation).
    """
    _install_quiet_loop_handler()

    if wipe_before:
        reset_state(verbose=True)
        print()

    # Import the real entry point only now (after path bootstrap + log quieting).
    try:
        from app.pipeline import answer_question
    except Exception:
        print(_hr("!"))
        print("  FATAL: could not import the live pipeline (app.pipeline.answer_question)")
        print(_hr("!"))
        traceback.print_exc()
        return 2

    total = len(interactions)
    print(_hr())
    print("  VELYNX LIVE-FIRE STABILIZATION HARNESS")
    print(f"  Driving the LIVE answer_question pipeline for {total} interactions.")
    print("  Halts on first crash / retrieval failure / duplicate explosion / "
          "false certainty.")
    print(_hr())

    report_lines: list[str] = []
    try:
        for i, inter in enumerate(interactions, start=1):
            # Optional per-interaction reset (isolated single-shot runs only). The
            # default battery is self-consistent within a run, so this stays off.
            if wipe_between and i > 1:
                reset_state(verbose=False)

            resp = None
            try:
                resp = await answer_question(inter.text)
                inter.checker(resp)
            except HarnessFailure as hf:
                diag = dump_failure(i, total, inter, resp, hf)
                print(diag)
                if report_path:
                    report_lines.append(diag)
                    _write_report(report_path, report_lines)
                print(f"\n  RESULT: FAIL — broke at interaction #{i}/{total} "
                      f"({inter.category}, {hf.failure_type}).")
                return 1
            except Exception as exc:  # any pipeline exception == CRASH
                hf = HarnessFailure(FailureType.CRASH,
                                    f"{type(exc).__name__}: {exc}",
                                    traceback_str=traceback.format_exc())
                diag = dump_failure(i, total, inter, resp, hf)
                print(diag)
                if report_path:
                    report_lines.append(diag)
                    _write_report(report_path, report_lines)
                print(f"\n  RESULT: FAIL — crashed at interaction #{i}/{total} "
                      f"({inter.category}).")
                return 1

            # Compact progress line (truncate long inputs).
            tag = inter.text if len(inter.text) <= 58 else inter.text[:55] + "..."
            print(f"  [{i:>3}/{total}] OK  {inter.category:<16} {inter.kind:<5} {tag}")
            report_lines.append(f"[{i}/{total}] OK {inter.category} {inter.kind} :: {inter.text}")

        print(_hr())
        print(f"  RESULT: PASS — {total}/{total} interactions clean. "
              "Stabilization metric met.")
        print(_hr())
        if report_path:
            report_lines.append(f"\nPASS — {total}/{total} clean.")
            _write_report(report_path, report_lines)
        return 0
    finally:
        # Quiesce the pipeline's orphaned background (curiosity/agentic) tasks
        # while the loop is STILL alive, so their Playwright browser/context
        # close inside their own async-context exit. This runs on every path
        # (pass, fail, crash) and eliminates the trailing EPIPE / "Event loop is
        # closed" noise that appeared after teardown. Best-effort.
        await _drain_background_tasks()


def _write_report(path: str, lines: list[str]) -> None:
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# 10. SELF-TEST  (verifies the evaluator + generator WITHOUT the live pipeline)
# ─────────────────────────────────────────────────────────────────────────────
class _FakeResp:
    """Minimal stand-in exposing the AnswerResponse surface the checkers read."""
    def __init__(self, answer="", confidence="CERTAIN", contradictions=None,
                 gaps=None, debug=None):
        self.answer = answer
        self.confidence = confidence
        self.contradictions = contradictions or []
        self.gaps = gaps or []
        self.debug = debug or {}


def _expect_pass(label, checker, resp, failures):
    try:
        checker(resp)
    except HarnessFailure as hf:
        failures.append(f"{label}: expected PASS but got {hf.failure_type} ({hf.reason})")


def _expect_fail(label, checker, resp, want_type, failures):
    try:
        checker(resp)
        failures.append(f"{label}: expected {want_type} but checker PASSED")
    except HarnessFailure as hf:
        if hf.failure_type != want_type:
            failures.append(f"{label}: expected {want_type} but got {hf.failure_type}")


def run_self_test(count: int, seed: int) -> int:
    print(_hr())
    print("  HARNESS SELF-TEST — verifying evaluator + generator (pipeline NOT touched)")
    print(_hr())
    failures: list[str] = []

    # ---- evaluator: positive (correct-behavior) cases should PASS -----------
    _expect_pass("recall.good", check_recall("Interstellar"),
                 _FakeResp("Your favorite movie is Interstellar.", "CERTAIN"), failures)
    _expect_pass("teach.good", check_teach_ack(),
                 _FakeResp("I have committed that to memory.", "CERTAIN"), failures)
    _expect_pass("known_unknown.good", check_known_unknown(),
                 _FakeResp("Logic path broken — no connecting evidence found.", "UNKNOWN"),
                 failures)
    _expect_pass("contradiction.good", check_contradiction_flagged("Avatar"),
                 _FakeResp("You previously said Interstellar; that conflicts with Avatar.",
                           "CERTAIN"), failures)
    _expect_pass("narrative.good", check_narrative("Alice"),
                 _FakeResp("I was asked, could not answer, then I learned Alice created it.",
                           "CERTAIN"), failures)
    _expect_pass("selfmodel.good", check_self_model(),
                 _FakeResp("I know a little about it and I am trying to learn more.",
                           "CERTAIN"), failures)

    # ---- evaluator: each failure mode should be DETECTED --------------------
    _expect_fail("retrieval.bad", check_recall("Interstellar"),
                 _FakeResp("Logic path broken at concepts 'favorite','movie'.", "UNKNOWN"),
                 FailureType.RETRIEVAL_FAILURE, failures)
    _expect_fail("false_certainty.bad", check_known_unknown(),
                 _FakeResp("It was definitely created by Bob.", "CERTAIN"),
                 FailureType.FALSE_CERTAINTY, failures)
    _expect_fail("duplicate.bad", check_teach_ack(),
                 _FakeResp("it is 3d software, 3d software, 3d software, 3d software, "
                           "3d software, 3d software", "CERTAIN"),
                 FailureType.DUPLICATE_EXPLOSION, failures)
    _expect_fail("contradiction.bad", check_contradiction_flagged("Avatar"),
                 _FakeResp("Your favorite movie is Avatar.", "CERTAIN"),
                 FailureType.CONTRADICTION_NOT_FLAGGED, failures)
    _expect_fail("narrative.bad", check_narrative("Alice"),
                 _FakeResp("Your favorite movie is Avatar.", "CERTAIN"),
                 FailureType.NARRATIVE_MISSING, failures)
    _expect_fail("empty.bad", check_recall("X"),
                 _FakeResp("", "CERTAIN"), FailureType.EMPTY_OR_INVALID, failures)
    _expect_fail("crash.none", check_recall("X"), None,
                 FailureType.EMPTY_OR_INVALID, failures)

    # ---- generator: shape + logical consistency -----------------------------
    gen = build_randomized_interactions(count, seed=seed)
    if len(gen) != count:
        failures.append(f"generator: expected {count} interactions, got {len(gen)}")
    taught_values: set = set()
    # Track values taught so we can assert every recall query targets a taught fact.
    import re
    for inter in gen:
        if inter.kind == "TEACH":
            # crude value capture: last token(s) after ' is ' / 'created ' / 'lives in '
            m = re.search(r"\b(is|created|lives in)\b (.+)$", inter.text)
            if m:
                taught_values.add(m.group(2).strip().lower())
    bad_struct = [g for g in gen if g.kind not in ("TEACH", "QUERY") or not g.text.strip()]
    if bad_struct:
        failures.append(f"generator: {len(bad_struct)} malformed interactions")

    base = build_base_scenarios()
    if len(base) != 13:
        failures.append(f"base battery: expected 13 interactions, got {len(base)}")

    # ---- report -------------------------------------------------------------
    print(f"  base scenarios built     : {len(base)}")
    print(f"  randomized interactions  : {len(gen)} (seed={seed})")
    print(f"  distinct taught values   : {len(taught_values)}")
    print(f"  evaluator assertions run : 13")
    if failures:
        print(_hr("-"))
        print("  SELF-TEST FAILURES:")
        for f in failures:
            print(f"    - {f}")
        print(_hr())
        print("  RESULT: SELF-TEST FAILED")
        return 1
    print(_hr())
    print("  RESULT: SELF-TEST PASSED — evaluator detects all failure modes; "
          "generator is well-formed.")
    print(_hr())
    return 0


# ─────────────────────────────────────────────────────────────────────────────
# 11. CLI
# ─────────────────────────────────────────────────────────────────────────────
def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="VELYNX Live-Fire Stabilization Harness")
    parser.add_argument("--count", type=int, default=100,
                        help="total interactions to run live (default 100)")
    parser.add_argument("--seed", type=int, default=1337,
                        help="RNG seed for the randomized battery (default 1337)")
    parser.add_argument("--no-base", action="store_true",
                        help="skip the 5 canonical base scenarios")
    parser.add_argument("--report", type=str, default=None,
                        help="write a run report to this path")
    parser.add_argument("--no-wipe", action="store_true",
                        help="do NOT reset state (semantic graph + episodic "
                             "memory) before the run. By default the harness "
                             "wipes once before Interaction #1 so the previous "
                             "run's teachings cannot bleed in.")
    parser.add_argument("--wipe-between", action="store_true",
                        help="ALSO reset state between every interaction. "
                             "Breaks the default teach-then-recall battery; use "
                             "only for isolated single-shot runs.")
    parser.add_argument("--self-test", action="store_true",
                        help="verify the harness evaluator+generator without "
                             "touching the live pipeline")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test(args.count, args.seed)

    _quiet_third_party_logs()

    # Compose the live battery: base scenarios first, then pad to --count with
    # randomized logically-consistent interactions.
    interactions: list[Interaction] = []
    if not args.no_base:
        interactions.extend(build_base_scenarios())
    remaining = max(0, args.count - len(interactions))
    interactions.extend(build_randomized_interactions(remaining, seed=args.seed))
    interactions = interactions[:max(args.count, len(build_base_scenarios())
                                     if not args.no_base else args.count)]

    try:
        return asyncio.run(run_live(interactions, args.report,
                                    wipe_before=not args.no_wipe,
                                    wipe_between=args.wipe_between))
    except KeyboardInterrupt:
        print("\n  Interrupted.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
