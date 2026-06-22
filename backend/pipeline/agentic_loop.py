"""
VELYNX Phase 57 — Agentic Loop
==============================

Until now the pipeline was single-pass: one question in, one retrieval/reasoning
sweep, one answer out. That cannot answer a *multi-hop* goal whose answer depends
on the result of an intermediate lookup, e.g.::

    "What is the population of the city where my favorite coffee shop is located?"

No single retrieval resolves this. It must be DECOMPOSED:

    Step 1 — RETRIEVE_KG : ask our own Knowledge Graph for the favorite coffee
                            shop and the city it is in (Third Wave -> Bengaluru).
    Step 2 — WEB_SEARCH  : use an external tool to look up that city's population.

:class:`AgenticController` makes this explicit. It emits an inspectable
:class:`Plan` (a small dependency DAG of :class:`PlanStep`) BEFORE execution, then
runs the steps in dependency order, threading results through ``Plan.context`` so
a later step can consume what an earlier step resolved.

Design notes
------------
* **Deterministic planning.** ``should_plan`` and ``formulate_plan`` are pure
  heuristics — no LLM, no randomness — so the plan for a given query is stable
  and testable.
* **Conservative gating.** ``should_plan`` only fires for genuine multi-hop /
  comparison goals (a nested "where/located" clause over an indirect referent, or
  an explicit comparison). Plain single-hop questions ("what is my favorite
  color?") are left to the normal pipeline.
* **Robust execution.** Each action is best-effort and never raises out of the
  loop: a failed step is recorded and the plan halts gracefully with whatever was
  resolved. External calls (web search) degrade to a clearly-labelled stub when
  the retrieval mesh is unavailable.
* **No import cycle.** Heavy pipeline/memory modules are imported lazily inside
  methods, since ``app.pipeline`` imports this module.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger("velynx.agentic")


def _coref(phrase: str) -> str:
    """Normalise first-person pronouns in a referent the SAME way the TEACH path does.

    The agentic planner extracts referents verbatim from the question ("my
    favorite software"), but the knowledge-acquisition pipeline stores
    user-asserted facts with first-person pronouns rewritten ("User's favorite
    software"). Searching memory with the literal phrase therefore misses. We
    delegate to the single shared mapper in
    :func:`backend.knowledge.fact_extractor.resolve_first_person_coref` so the
    two paths can never drift apart. Best-effort: a normalisation failure returns
    the original phrase rather than breaking the plan.
    """
    if not phrase:
        return phrase
    try:
        from backend.knowledge.fact_extractor import resolve_first_person_coref

        return resolve_first_person_coref(phrase)
    except Exception as exc:  # pragma: no cover - never break planning on coref
        logger.debug("Phase58 coref normalisation failed for %r: %s", phrase, exc)
        return phrase


# ── spaCy access ──────────────────────────────────────────────────────────────
# VELYNX already loads ``en_core_web_sm`` for declarative fact extraction. We
# reuse that *same cached* pipeline object here (Phase 58) instead of loading a
# second copy, so symbolic decomposition shares the one model the system has in
# memory. We fall back to loading/caching locally only if the shared handle is
# unavailable, and never raise out of the planner — a parse failure degrades to
# a single-hop plan with a full observability trail (see ``formulate_plan``).
_NLP = None


def _get_nlp():
    """Return VELYNX's shared, cached spaCy English pipeline.

    Resolution order:
      1. Reuse the model already loaded by :mod:`backend.knowledge.fact_extractor`
         (the object "VELYNX already has loaded").
      2. Otherwise lazily load and cache ``en_core_web_sm`` here.

    Returns ``None`` (never raises) if spaCy or the model is unavailable, so the
    planner can degrade gracefully rather than crash the request pipeline.
    """
    global _NLP
    if _NLP is not None:
        return _NLP
    # 1) Reuse the already-loaded pipeline from the fact extractor.
    try:
        from backend.knowledge import fact_extractor

        _NLP = fact_extractor._get_nlp()
        if _NLP is not None:
            return _NLP
    except Exception as exc:  # import error / model missing — try local load
        logger.debug("Shared spaCy handle unavailable (%s); loading locally", exc)
    # 2) Local lazy load as a last resort.
    try:
        import spacy

        _NLP = spacy.load("en_core_web_sm")
    except Exception as exc:
        logger.warning(
            "spaCy model 'en_core_web_sm' unavailable (%s); agentic planner will "
            "fall back to a single-hop plan", exc
        )
        _NLP = None
    return _NLP


# ── Schemas ──────────────────────────────────────────────────────────────────
class PlanAction(str, Enum):
    """The pipeline primitives a plan step may invoke."""

    RETRIEVE_KG = "retrieve_kg"        # internal Knowledge-Graph / memory lookup
    WEB_SEARCH = "web_search"          # external tool: retrieval mesh / web search
    SYNTHESIZE = "synthesize"          # combine resolved context into an answer


class PlanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


@dataclass
class PlanStep:
    """One node in the plan DAG."""

    id: int
    action: PlanAction
    description: str
    dependencies: list[int] = field(default_factory=list)
    params: dict[str, Any] = field(default_factory=dict)
    status: PlanStatus = PlanStatus.PENDING
    result: Any = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "action": self.action.value,
            "description": self.description,
            "dependencies": list(self.dependencies),
            "params": self.params,
            "status": self.status.value,
            "result": self.result,
        }


@dataclass
class Plan:
    """An ordered, dependency-aware collection of steps for one goal."""

    query: str
    steps: list[PlanStep] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    status: PlanStatus = PlanStatus.PENDING

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "status": self.status.value,
            "steps": [s.to_dict() for s in self.steps],
            "context": self.context,
        }


# ── Fallback heuristic vocabulary ─────────────────────────────────────────────
# Phase 58.1: gating is now grammatical (spaCy). These string markers are only a
# best-effort FALLBACK used when the spaCy pipeline is unavailable, so routing
# still degrades sensibly offline rather than silently disabling planning.
_COMPARISON_MARKERS = (
    "compare", "comparison", "versus", " vs ", " vs.", "difference between",
    "compared to", "bigger than", "smaller than", "larger than", "taller than",
    "older than", "more populous", "richer than", "which is more",
)
# A subordinate clause that defers the real subject to an inner lookup.
_NESTING_MARKERS = (
    " where ", " in which ", " whose ", " is located", " located in",
    " located at", " that is in ", " situated in",
)
# An indirect referent the inner clause must first resolve.
_INDIRECT_REFERENTS = (
    "my ", "the city", "the place", "the town", "the country", "the company",
    "the person", "the author", "the creator", "the owner", "his ", "her ",
    "their ", " its ",
)


class AgenticController:
    """Intercepts multi-hop goals, plans a DAG, and executes it step by step."""

    # Tunables.
    WEB_SEARCH_TIMEOUT = 8.0

    # ── Gating (Phase 58.1 — grammatical router) ──────────────────────────
    def should_plan(self, query: str) -> bool:
        """Decide *grammatically* whether ``query`` needs a multi-hop plan.

        Uses the same shared spaCy pipeline as :meth:`formulate_plan` rather than
        Phase 57's hardcoded string markers. Returns ``True`` when the query is:

          * a **comparison** goal — comparative morphology (``JJR`` / ``RBR``),
            an explicit ``than`` / ``versus`` / ``compare`` / "difference
            between"; or
          * a **nested-bridge** goal — the dependency parse yields a chain of two
            or more referent noun chunks (``_collect_bridges``) whose innermost
            referent is *indirect*: it carries a ``poss`` modifier nested inside a
            ``prep``/``pobj`` chain (e.g. "the creator **of my** favorite
            software"), or the chain is introduced by a **relative clause**
            (``relcl`` / ``acl`` / ``advcl``, e.g. "the city **where** my shop is
            located").

        A plain single prep relation between concrete entities ("the capital of
        France") is NOT multi-hop — it has no possessive/relative indirection, so
        it is left to the single-hop graph lookup. Likewise simple direct
        questions ("What is my favorite color?", "Who created VELYNX?") return
        ``False``.

        Falls back to the legacy string markers only if spaCy is unavailable.
        """
        if not query or not query.strip():
            return False

        doc = self._parse(query)
        if doc is None:
            return self._legacy_should_plan(query)

        # 1) Comparison goals.
        if self._is_comparison(doc):
            logger.debug("should_plan(%r) -> True (comparison)", query[:60])
            return True

        # 2) Nested-bridge goals: a genuine referent chain with indirection.
        chunks = list(doc.noun_chunks)
        if not chunks:
            return False

        deepest = self._find_deepest_chunk(chunks)
        bridges = self._collect_bridges(deepest, chunks)
        has_chain = len(bridges) >= 2
        # The chain must be driven by an *indirect* referent — a possessive
        # nested under the prep/pobj chain, or a relative-clause subject — not a
        # plain prep relation between two concrete named entities.
        indirect = self._chunk_has_poss(deepest) or any(
            t.dep_ in ("relcl", "acl", "advcl") for t in doc
        )
        decision = has_chain and indirect
        logger.debug(
            "should_plan(%r) -> %s (bridges=%d, indirect=%s)",
            query[:60], decision, len(bridges), indirect,
        )
        return decision

    @staticmethod
    def _is_comparison(doc) -> bool:
        """Detect a comparison goal purely from grammar / lemmas.

        Triggers on explicit comparison lemmas ("compare", "versus") and the
        "difference between" frame, on a comparative preposition ("than"), or on
        comparative morphology (``JJR`` / ``RBR``: "bigger", "more populous")
        when there are at least two comparable referents (a coordinating
        conjunction or two+ noun chunks).
        """
        if "difference between" in doc.text.lower():
            return True
        has_comparative = False
        for tok in doc:
            if tok.lemma_ in ("compare", "comparison", "versus"):
                return True
            if tok.lower_ in ("vs", "vs.", "than"):
                return True
            if tok.tag_ in ("JJR", "RBR"):
                has_comparative = True
        if has_comparative:
            if any(t.pos_ == "CCONJ" for t in doc) or len(list(doc.noun_chunks)) >= 2:
                return True
        return False

    def _legacy_should_plan(self, query: str) -> bool:
        """String-marker gate used only when spaCy is unavailable (offline)."""
        q = f" {query.strip().lower()} "
        if any(m in q for m in _COMPARISON_MARKERS):
            return True
        has_nesting = any(m in q for m in _NESTING_MARKERS)
        has_indirect = any(m in q for m in _INDIRECT_REFERENTS)
        return has_nesting and has_indirect

    # ── Planning (Phase 58 — Symbolic Query Decomposer) ───────────────────
    def formulate_plan(self, query: str) -> Plan:
        """Dynamically generate a dependency-DAG by parsing ``query``'s grammar.

        This is a *purely symbolic* decomposer: no LLM, no generative model. It
        runs VELYNX's shared spaCy pipeline over the query and walks the
        dependency tree of its ``noun_chunks`` to discover the multi-hop chain
        the question implicitly encodes. The heuristic relies ONLY on dependency
        labels (``poss``, ``prep``, ``pobj``, ``nsubj``, ``ROOT``) and never on
        specific nouns, verbs or domains.

        Decomposition (recursive, deepest-first):

          * **DEEPEST BRIDGE** — the most deeply nested noun chunk, preferring one
            that carries a ``poss`` dependency (e.g. *"my favorite 3D software"*).
            This becomes ``Step 1`` (``RETRIEVE_KG``): resolve that referent
            against our own Knowledge Graph / memory.
          * **PARENT BRIDGE(S)** — walk *up* the dependency tree from the deepest
            chunk. Every ancestor that is itself the head of a noun chunk, reached
            through a ``prep``/``pobj`` link (e.g. following *"of"* to *"original
            creator"*), becomes a further ``RETRIEVE_KG`` step that depends on the
            step below it.
          * **ROOT ACTION** — the sentence ``ROOT`` verb together with the
            question focus (the wh-word and the attribute noun chunk it governs,
            e.g. *"What year was [X] born?"*) becomes the final step, depending on
            the outermost bridge.

        The full dependency tree is logged (observability trail). If spaCy is
        unavailable or the parse yields no usable chunks, the planner degrades to
        a single best-effort step rather than raising.
        """
        q = query.strip()
        plan = Plan(query=q)
        plan.context["goal"] = q

        doc = self._parse(q)
        if doc is None:
            return self._degenerate_plan(plan, reason="spaCy pipeline unavailable")

        # Observability: emit the full dependency tree + noun-chunk inventory.
        trace = self._format_dependency_tree(doc)
        plan.context["dep_trace"] = trace
        logger.info("Phase58 decomposing %r\n%s", q[:80], trace)

        chunks = list(doc.noun_chunks)
        if not chunks:
            logger.warning("Phase58: no noun_chunks parsed from %r — degrading", q)
            return self._degenerate_plan(plan, reason="no noun chunks")

        # 1) DEEPEST BRIDGE — most nested chunk, preferring a possessive referent.
        deepest = self._find_deepest_chunk(chunks)
        # 2) PARENT BRIDGE(S) — ordered deepest -> outermost, with the linking
        #    preposition (relation) that connects each to the one below it.
        bridges = self._collect_bridges(deepest, chunks)
        # 3) ROOT ACTION — root verb + question focus (the answerable attribute).
        root = self._sentence_root(doc)
        wh = self._question_word(doc)
        bridge_root_ids = {c.root.i for c, _ in bridges}
        attribute_chunk = self._question_focus(chunks, bridge_root_ids)
        attribute = (
            attribute_chunk.text if attribute_chunk is not None
            else (root.lemma_ if root is not None else "answer")
        )

        logger.debug(
            "Phase58 bridges=%s | root=%r focus=%r attribute=%r",
            [(c.text, rel) for c, rel in bridges],
            root.text if root is not None else None,
            wh.text if wh is not None else None,
            attribute,
        )

        # ── Construct the DAG ─────────────────────────────────────────────
        steps: list[PlanStep] = []
        sid = 0
        prev_id: Optional[int] = None

        for idx, (chunk, relation) in enumerate(bridges):
            sid += 1
            deps = [prev_id] if prev_id is not None else []
            if idx == 0:
                description = (
                    f"DEEPEST BRIDGE — internal Knowledge Graph / memory lookup: "
                    f"resolve the most-nested referent '{chunk.text}' "
                    f"(deepest noun chunk"
                    f"{', carries a possessive `poss` dependency' if self._chunk_has_poss(chunk) else ''})."
                )
            else:
                description = (
                    f"PARENT BRIDGE — Knowledge Graph traversal: from the entity "
                    f"resolved in step {prev_id}, follow the "
                    f"'{relation or 'related'}' relation (dependency `prep`/`pobj`) "
                    f"to resolve '{chunk.text}'."
                )
            steps.append(
                PlanStep(
                    id=sid,
                    action=PlanAction.RETRIEVE_KG,
                    description=description,
                    dependencies=deps,
                    params={
                        "referent": _coref(chunk.text),
                        "referent_raw": chunk.text,
                        "relation": relation,
                        "depth": self._token_depth(chunk.root),
                        "poss": self._chunk_has_poss(chunk),
                    },
                )
            )
            prev_id = sid

        # ROOT ACTION — answer the outer attribute about the outermost resolved
        # entity. Uses the external tool (WEB_SEARCH) since it is an attribute of
        # a now-resolved entity, consistent with the executor's context threading.
        sid += 1
        deps = [prev_id] if prev_id is not None else []
        root_desc = (
            f"ROOT ACTION — answer the question focus '{attribute}'"
            + (f" (wh-word '{wh.text}')" if wh is not None else "")
            + (f", governed by ROOT verb '{root.lemma_}'" if root is not None else "")
            + (f", about the entity resolved in step {prev_id}." if prev_id is not None
               else " from the goal directly.")
        )
        steps.append(
            PlanStep(
                id=sid,
                action=PlanAction.WEB_SEARCH,
                description=root_desc,
                dependencies=deps,
                params={
                    "attribute": attribute,
                    "root": root.lemma_ if root is not None else None,
                    "focus": wh.text if wh is not None else None,
                },
            )
        )

        plan.steps = steps
        # Thread the symbolic findings into context for the executor / synthesis.
        # Referents are coreference-normalised ("my favorite software" ->
        # "User's favorite software") so KG/memory lookups match the form the
        # TEACH pipeline stored facts under. Keep the raw text for logging/UX.
        plan.context["referent"] = _coref(deepest.text)
        plan.context["referent_raw"] = deepest.text
        plan.context["attribute"] = attribute
        plan.context["bridges"] = [_coref(c.text) for c, _ in bridges]
        return plan

    # ── spaCy parsing + dependency-tree heuristics ────────────────────────
    @staticmethod
    def _parse(query: str):
        """Run the shared spaCy pipeline over ``query``; ``None`` on failure."""
        if not query:
            return None
        nlp = _get_nlp()
        if nlp is None:
            return None
        try:
            return nlp(query)
        except Exception as exc:
            logger.warning("Phase58 spaCy parse failed for %r: %s", query[:80], exc)
            return None

    @staticmethod
    def _format_dependency_tree(doc) -> str:
        """Render the full dependency tree + noun-chunk inventory for logging.

        This is the observability trail: if a decomposition looks wrong, the log
        shows every token's (text, lemma, POS, dep, head) plus the chunks and
        their depth from ROOT, so the parse can be audited offline.
        """
        lines = ["  token        lemma        pos    dep         head"]
        for tok in doc:
            lines.append(
                f"  {tok.text[:11]:<11}  {tok.lemma_[:11]:<11}  "
                f"{tok.pos_:<5}  {tok.dep_:<10}  {tok.head.text}"
            )
        lines.append("  noun_chunks (text | root | root.dep | depth | poss):")
        for ch in doc.noun_chunks:
            depth = AgenticController._token_depth(ch.root)
            poss = any(t.dep_ == "poss" for t in ch)
            lines.append(
                f"    - '{ch.text}' | root={ch.root.text} | "
                f"dep={ch.root.dep_} | depth={depth} | poss={poss}"
            )
        return "\n".join(lines)

    @staticmethod
    def _token_depth(token) -> int:
        """Distance (in head-hops) from ``token`` to its sentence ROOT."""
        depth = 0
        cur = token
        # The ROOT is its own head; compare by index since spaCy returns a fresh
        # Token wrapper on each ``.head`` access (so ``is`` identity won't work).
        while cur.head.i != cur.i and depth < 64:
            depth += 1
            cur = cur.head
        return depth

    @staticmethod
    def _chunk_has_poss(chunk) -> bool:
        """True if the noun chunk contains a possessive (``poss``) dependency."""
        return any(t.dep_ == "poss" for t in chunk)

    @classmethod
    def _find_deepest_chunk(cls, chunks):
        """The most deeply nested noun chunk, preferring a possessive referent.

        Possessive chunks ("my favorite 3D software") are the canonical innermost
        referent in a multi-hop goal, so they win ties / are preferred outright.
        Among the preferred pool we pick the chunk whose root sits deepest in the
        dependency tree.
        """
        poss_chunks = [c for c in chunks if cls._chunk_has_poss(c)]
        pool = poss_chunks or list(chunks)
        return max(pool, key=lambda c: cls._token_depth(c.root))

    @classmethod
    def _collect_bridges(cls, deepest, chunks):
        """Walk UP the dependency tree from ``deepest`` collecting noun bridges.

        Returns an ordered list of ``(chunk, relation)`` tuples, deepest-first.
        ``relation`` is the dependency link (the lemma of the connecting ``prep``
        such as "of", or the lemma of a relative-clause verb such as "locate")
        that ties a bridge to the one nested below it (``None`` for the deepest
        chunk). We climb through *subordinate-clause* verbs (``relcl`` / ``acl`` /
        ``advcl`` …) so a noun modified by a relative clause ("the city where my
        shop is located") is still captured, and stop only at the matrix ROOT
        verb, beyond which we are into the question's action rather than its
        referent chain.
        """
        subordinate_clause_deps = {
            "relcl", "acl", "advcl", "pcomp", "ccomp", "xcomp",
        }
        chunk_by_root = {c.root.i: c for c in chunks}
        bridges = [(deepest, None)]
        seen = {deepest.root.i}
        pending_rel: Optional[str] = None

        for anc in deepest.root.ancestors:
            # A preposition (prep) is the relation linking the next outer noun.
            if anc.dep_ == "prep":
                pending_rel = anc.lemma_
                continue
            if anc.pos_ in ("VERB", "AUX"):
                # A subordinate-clause verb just links a noun to its modifier —
                # keep climbing (record it as the relation if none seen yet).
                if anc.dep_ in subordinate_clause_deps:
                    if pending_rel is None:
                        pending_rel = anc.lemma_
                    continue
                # The matrix ROOT verb — stop the referent chain here.
                break
            # An ancestor that heads its own noun chunk is a parent bridge.
            if anc.i in chunk_by_root and anc.i not in seen:
                bridges.append((chunk_by_root[anc.i], pending_rel))
                seen.add(anc.i)
                pending_rel = None
        return bridges

    @staticmethod
    def _sentence_root(doc):
        """The sentence ROOT token (the main verb / head), or ``None``."""
        for tok in doc:
            if tok.dep_ == "ROOT":
                return tok
        return None

    @staticmethod
    def _question_word(doc):
        """The interrogative token (what/which/who/whose/where/when), if any."""
        for tok in doc:
            if tok.tag_ in ("WDT", "WP", "WP$", "WRB"):
                return tok
        return None

    @classmethod
    def _question_focus(cls, chunks, bridge_root_ids):
        """The noun chunk naming the asked-for attribute.

        It is the chunk NOT already consumed as a referent bridge that sits
        closest to the ROOT (smallest dependency depth) — e.g. "year" in "what
        year was X born", or "the population" in "the population of the city ...".
        """
        others = [c for c in chunks if c.root.i not in bridge_root_ids]
        if not others:
            return None
        return min(others, key=lambda c: cls._token_depth(c.root))

    def _degenerate_plan(self, plan: Plan, *, reason: str) -> Plan:
        """Single best-effort step when grammatical decomposition isn't possible.

        Keeps the public contract intact (a runnable :class:`Plan`) so the
        executor still completes deterministically. The reason is recorded for
        the observability trail.
        """
        logger.warning("Phase58 degrading to single-hop plan (%s)", reason)
        plan.context["decomposition"] = f"degraded: {reason}"
        plan.context.setdefault("attribute", "answer")
        plan.context.setdefault("referent", plan.query)
        plan.steps = [
            PlanStep(
                id=1,
                action=PlanAction.WEB_SEARCH,
                description=(
                    f"ROOT ACTION (fallback) — could not decompose grammatically "
                    f"({reason}); resolve the whole goal as a single lookup."
                ),
                dependencies=[],
                params={"attribute": "answer", "referent": plan.query},
            )
        ]
        return plan

    # ── Execution ─────────────────────────────────────────────────────────
    async def execute_plan(self, plan: Plan) -> dict:
        """Execute the plan in dependency order, threading ``plan.context``.

        A simple scheduler loop: repeatedly pick the next PENDING step whose
        dependencies are all DONE, run it, and store its result both on the step
        and in ``plan.context``. Halts when every step is resolved (DONE) or when
        a step FAILS (no ready step can make progress).

        Returns a synthesis dict: ``{answer, confidence, citations, context}``.
        Never raises — execution failures are captured on the step/plan status.
        """
        plan.status = PlanStatus.RUNNING
        guard = 0
        max_iterations = len(plan.steps) * 2 + 4

        while guard < max_iterations:
            guard += 1
            step = self._next_ready_step(plan)
            if step is None:
                break  # nothing ready: either all done, or blocked/failed
            step.status = PlanStatus.RUNNING
            try:
                step.result = await self._run_step(step, plan.context)
                step.status = PlanStatus.DONE
            except Exception as exc:
                step.status = PlanStatus.FAILED
                plan.context.setdefault("errors", []).append(
                    f"step {step.id} ({step.action.value}): {exc}"
                )
                logger.warning("Agentic step %d failed: %s", step.id, exc)
                plan.status = PlanStatus.FAILED
                break

        if plan.status != PlanStatus.FAILED:
            if all(s.status == PlanStatus.DONE for s in plan.steps):
                plan.status = PlanStatus.DONE
            else:
                plan.status = PlanStatus.FAILED

        return self._synthesize(plan)

    @staticmethod
    def _next_ready_step(plan: Plan) -> Optional[PlanStep]:
        done_ids = {s.id for s in plan.steps if s.status == PlanStatus.DONE}
        for step in plan.steps:
            if step.status != PlanStatus.PENDING:
                continue
            if all(dep in done_ids for dep in step.dependencies):
                return step
        return None

    async def _run_step(self, step: PlanStep, context: dict) -> Any:
        if step.action == PlanAction.RETRIEVE_KG:
            return await self._do_retrieve_kg(step, context)
        if step.action == PlanAction.WEB_SEARCH:
            return await self._do_web_search(step, context)
        if step.action == PlanAction.SYNTHESIZE:
            return self._synthesize(  # pragma: no cover - not used in the DAG
                context.get("_plan")  # type: ignore[arg-type]
            )
        raise ValueError(f"Unknown plan action: {step.action!r}")

    # ── Action implementations ────────────────────────────────────────────
    @staticmethod
    def _kg_resolve_entity(graph, seed: str) -> tuple[Optional[str], list[str]]:
        """Resolve *seed* to a concrete entity by following its strongest edge.

        Returns ``(entity, evidence)``. We look at *seed*'s outgoing relations and
        prefer an identity/definition edge ("be") — e.g. "user's favorite software
        -be-> blender" resolves the referent to "blender". If the seed is already
        a concrete node with no identity edge, the seed itself is returned so a
        downstream relation hop can still proceed. ``None`` when nothing is known.
        """
        seed_norm = (seed or "").strip().lower()
        if not seed_norm:
            return None, []
        evidence: list[str] = []
        try:
            rels = list(graph.get_related(seed_norm))
        except Exception:
            rels = []
        if not rels:
            return None, []
        # Prefer an identity edge where the seed is the SOURCE ("X be Y" -> Y).
        for rel in rels:
            relation = (rel.get("relation") or "").lower()
            src = (rel.get("source") or "").lower()
            target = rel.get("target") or ""
            if src == seed_norm and relation in ("be", "is", "equals") and target:
                evidence.append(f"{rel.get('source')} {relation} {target}")
                return target, evidence
        # Otherwise the seed is itself a resolved entity (it has edges).
        return seed_norm, evidence

    @staticmethod
    def _kg_follow_relation(graph, entity: str, relation_hint: Optional[str]) -> tuple[Optional[str], list[str]]:
        """From *entity*, follow an edge matching *relation_hint* to its target.

        ``relation_hint`` is the dependency connector captured by the planner
        (e.g. "of" for "the creator of X"); we also key off the step's bridge noun
        when present. Matching is loose (substring) against the edge relation, and
        a small synonym map bridges connector words to KG predicates
        ("creator"->"create", "country"/"location"->"live_in"/"locate"). Returns
        ``(target, evidence)`` or ``(None, [])``.
        """
        ent = (entity or "").strip().lower()
        if not ent:
            return None, []
        hint = (relation_hint or "").strip().lower()
        synonyms = {
            "creator": ("create", "creator", "author", "found", "design", "develop"),
            "create": ("create", "creator"),
            "country": ("live_in", "locate", "country", "in"),
            "location": ("live_in", "locate", "in"),
            "of": (),  # generic possessive connector — match any non-identity edge
        }
        wanted = synonyms.get(hint, (hint,) if hint else ())
        try:
            rels = list(graph.get_related(ent))
        except Exception:
            rels = []
        # First pass: honour the relation hint.
        for rel in rels:
            relation = (rel.get("relation") or "").lower()
            src = (rel.get("source") or "").lower()
            target = rel.get("target") or ""
            if src != ent or not target:
                continue
            if relation in ("be", "is", "equals"):
                continue  # identity edge already consumed during resolution
            if wanted and any(k in relation for k in wanted):
                return target, [f"{rel.get('source')} {relation} {target}"]
        # Second pass (generic connector like "of"): take the first non-identity edge.
        if hint in ("", "of"):
            for rel in rels:
                relation = (rel.get("relation") or "").lower()
                src = (rel.get("source") or "").lower()
                target = rel.get("target") or ""
                if src == ent and target and relation not in ("be", "is", "equals"):
                    return target, [f"{rel.get('source')} {relation} {target}"]
        return None, []

    async def _do_retrieve_kg(self, step: PlanStep, context: dict) -> dict:
        """Resolve the inner referent against the KG / semantic memory.

        Generic, chained traversal: the deepest step resolves the referent to a
        concrete entity (e.g. "User's favorite software" -> "blender"); each
        parent step hops from the entity resolved by its dependency along the
        step's relation (e.g. follow "create" to "ton roosendaal"). The running
        entity is threaded through ``context['resolved_entity']`` and the
        human-readable hop chain through ``context['chain']``. The original
        city/location behaviour is preserved as a fallback so the coffee-shop
        demo still works.
        """
        referent = step.params.get("referent") or context.get("referent") or ""
        # Defensive: ensure first-person coreference is resolved even if a caller
        # threaded a raw referent (the planner already normalises at formulation,
        # but this keeps the search robust to other entry points).
        referent = _coref(referent)
        relation_hint = step.params.get("relation") or step.params.get("referent")
        prior_entity = context.get("resolved_entity")
        found_city: Optional[str] = None
        resolved_entity: Optional[str] = None
        evidence: list[str] = []

        # 1. Semantic memory recall (Graph-RAG facts written by the consolidator).
        try:
            from backend.memory.memory_manager import memory_manager

            hits = await memory_manager.recall(
                f"{referent}", limit=5, kinds=["semantic", "episodic"]
            )
            for h in hits or []:
                txt = getattr(h.entry, "text", "") or ""
                if txt:
                    evidence.append(txt)
        except Exception as exc:
            logger.debug("KG semantic recall failed: %s", exc)

        # 2. Generic symbolic KG traversal (chained entity resolution).
        try:
            from backend.knowledge.knowledge_graph import KnowledgeGraph

            graph = KnowledgeGraph()
            if prior_entity:
                # Parent hop: from the entity resolved below, follow this step's
                # relation (e.g. "of"/"creator") to the next entity.
                resolved_entity, ev = self._kg_follow_relation(
                    graph, prior_entity, relation_hint
                )
                evidence.extend(ev)
            if resolved_entity is None:
                # Deepest hop (or parent fallback): resolve the referent itself.
                resolved_entity, ev = self._kg_resolve_entity(graph, referent)
                evidence.extend(ev)

            # Location/ city detection retained for the coffee-shop demo path.
            scan_seed = (resolved_entity or referent or "").lower()
            if scan_seed:
                for rel in graph.get_related(scan_seed):
                    relation = (rel.get("relation") or "").lower()
                    target = rel.get("target") or ""
                    if target and any(k in relation for k in ("locate", "in", "city", "live")):
                        found_city = target
                        evidence.append(f"{rel.get('source')} {relation} {target}")
                        break
        except Exception as exc:
            logger.debug("KG traversal failed: %s", exc)

        # 3. Fallback: mine a city from the evidence text.
        if not found_city:
            found_city = self._guess_city_from_text(" ".join(evidence))

        if resolved_entity:
            context["resolved_entity"] = resolved_entity
            chain = context.setdefault("chain", [])
            chain.append(resolved_entity)
        if found_city:
            context["city"] = found_city
        context["kg_evidence"] = evidence[:8]
        return {
            "resolved_entity": resolved_entity,
            "city": found_city,
            "evidence": evidence[:8],
        }

    async def _do_web_search(self, step: PlanStep, context: dict) -> dict:
        """External lookup of the outer attribute for the resolved entity.

        Uses the retrieval mesh when available; otherwise returns a clearly
        labelled stub so the loop completes deterministically offline.
        """
        attribute = step.params.get("attribute") or context.get("attribute") or "answer"
        city = context.get("city")
        target = city or context.get("resolved_entity") or context.get("referent") or context.get("goal") or ""
        query = f"{attribute} of {target}".strip()

        snippet = None
        source_url = None
        try:
            import asyncio

            from backend.pipeline import retrieval_mesh

            sources = await asyncio.wait_for(
                retrieval_mesh.retrieve_all(query), timeout=self.WEB_SEARCH_TIMEOUT
            )
            if sources:
                top = sources[0]
                snippet = (top.get("snippet") or top.get("title") or "") if isinstance(top, dict) else str(top)
                source_url = top.get("url") if isinstance(top, dict) else None
        except Exception as exc:
            logger.debug("Web search unavailable (%s); using stub result", exc)

        if not snippet:
            snippet = (
                f"[web_search stub] Could not retrieve the {attribute} of "
                f"{target or 'the resolved entity'} (no external result available)."
            )

        context["web_result"] = snippet
        context["web_query"] = query
        return {"query": query, "snippet": snippet, "url": source_url}

    # ── Synthesis ─────────────────────────────────────────────────────────
    def _synthesize(self, plan: Plan) -> dict:
        ctx = plan.context
        attribute = ctx.get("attribute", "answer")
        city = ctx.get("city")
        web = ctx.get("web_result")
        resolved = ctx.get("resolved_entity")
        chain = ctx.get("chain") or []
        referent_label = ctx.get("referent_raw") or ctx.get("referent", "entity")

        def _title(s: str) -> str:
            return " ".join(w.capitalize() if w.islower() else w for w in str(s).split())

        # A location/country edge resolved entirely inside the KG is an answer in
        # its own right — surface it without needing an external source.
        if city:
            chain_str = " -> ".join(_title(c) for c in chain) if chain else ""
            trail = f" (resolved chain: {referent_label} -> {chain_str})" if chain_str else ""
            answer = (
                f"Resolved via a {len(plan.steps)}-step plan: {referent_label} "
                f"leads to {_title(city)}{trail}."
            )
            confidence = "PROBABLE"
        elif resolved and chain and len(chain) >= 1:
            # Multi-hop resolved a final entity through the KG (e.g. referent ->
            # creator) even without a location edge. Report the chain.
            chain_str = " -> ".join(_title(c) for c in chain)
            answer = (
                f"Resolved via a {len(plan.steps)}-step plan: {referent_label} -> "
                f"{chain_str}."
            )
            if web and "stub" not in (web or "").lower():
                answer += f" {attribute}: {web}"
            confidence = "PROBABLE" if web and "stub" not in (web or "").lower() else "LOW"
        else:
            answer = (
                f"I planned a {len(plan.steps)}-step lookup for this multi-hop goal but "
                f"could not resolve the {referent_label} from memory."
            )
            confidence = "LOW"

        citations = []
        if city or resolved:
            citations.append("[KG] internal lookup")
        if web and "stub" not in (web or "").lower():
            citations.append("[web] external search")

        return {
            "answer": answer,
            "confidence": confidence,
            "citations": citations,
            "context": ctx,
        }

    @staticmethod
    def _guess_city_from_text(text: str) -> Optional[str]:
        """Pull a known/likely city token out of free text (best-effort)."""
        if not text:
            return None
        lc = text.lower()
        for city in ("bengaluru", "bangalore", "mumbai", "delhi", "chennai",
                     "kolkata", "hyderabad", "pune", "london", "new york", "paris"):
            if city in lc:
                return city
        return None


# Process-wide singleton.
agentic_controller = AgenticController()


__all__ = [
    "PlanAction",
    "PlanStatus",
    "PlanStep",
    "Plan",
    "AgenticController",
    "agentic_controller",
]
