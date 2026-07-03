"""
VELYNX Cognitive Architecture
Module: velynx/graph/curiosity_engine_v2.py
Milestone: C5 — Curiosity Engine v2 (Information Gain)

Philosophy
----------
A database-driven agent asks "Tell me about X" because a field is NULL.
A *cognitive* agent asks a question because a prediction FAILED, producing a
spike in Surprise (self-information). It then seeks the single missing piece of
structural knowledge that maximally collapses the uncertainty (Shannon entropy)
in its world model.

Worked example (the canonical one):
    Model believes:   Bird --flies--> True   (p ~ 0.97)
    Observation:      Penguin IS-A Bird, Penguin --flies--> False

    A null-field agent asks:  "What is a penguin?"            (uninformative)
    VELYNX asks:              "Is flight ESSENTIAL to the concept 'Bird',
                               or merely a TYPICAL (default) trait?"

The second question is chosen not by heuristic but because it carries the
highest Expected Information Gain over the space of structural hypotheses that
could explain the contradiction.

This module contains NO LLM calls in its core. All decisions are derived from
Shannon information theory over an explicit cognitive graph.

Hardware target: local processing (no network, no GPU required).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Sequence, Tuple

# A trait attached to a concept is modelled probabilistically: the fraction of
# observed instances for which the trait holds. This lets us reason about
# "default" traits (high-but-not-1.0) vs "essential" traits (1.0 by definition).
Probability = float

# Numerical floor to keep logarithms finite.
_EPS: float = 1e-12


# ---------------------------------------------------------------------------
# Section 1: Information-theoretic primitives (pure functions, no state)
# ---------------------------------------------------------------------------

def shannon_entropy(distribution: Sequence[Probability]) -> float:
    """Shannon entropy H(X) = -Sum p_i * log2(p_i), in bits.

    The distribution is normalised defensively; zero-probability outcomes
    contribute nothing (0 * log 0 := 0).
    """
    total = sum(distribution)
    if total <= _EPS:
        return 0.0
    entropy = 0.0
    for p in distribution:
        if p <= _EPS:
            continue
        norm = p / total
        entropy -= norm * math.log2(norm)
    return entropy


def self_information(probability: Probability) -> float:
    """Self-information (surprisal) of a single outcome: -log2(p), in bits.

    This is the formal measure of "surprise": an outcome the model rated as
    near-certain-to-NOT-happen (small p) yields a large surprisal when it does.
    """
    return -math.log2(max(probability, _EPS))


def normalise(weights: Sequence[float]) -> List[Probability]:
    """Normalise non-negative weights into a probability distribution."""
    total = sum(weights)
    if total <= _EPS:
        # Uniform fallback so downstream entropy maths stays well-defined.
        n = len(weights)
        return [1.0 / n] * n if n else []
    return [w / total for w in weights]


def expected_information_gain(
    prior: Sequence[Probability],
    likelihoods: Sequence[Sequence[Probability]],
) -> float:
    """Expected Information Gain of an inquiry == mutual information I(H; A).

    Parameters
    ----------
    prior:
        P(H) over the structural hypotheses, length H.
    likelihoods:
        Row-major matrix L[h][a] = P(answer = a | hypothesis = h).
        Each row is a conditional distribution over the inquiry's answers.

    Returns
    -------
    EIG = H(H) - E_a[ H(H | A = a) ]  in bits.

    Derivation
    ----------
        P(a)      = Sum_h P(h) * P(a | h)
        P(h | a)  = P(a | h) * P(h) / P(a)            (Bayes)
        EIG       = H(H) - Sum_a P(a) * H( P(.|a) )

    An inquiry whose answer is statistically independent of H yields EIG = 0:
    asking it teaches the system nothing about the structure of its world model.
    """
    prior = normalise(prior)
    n_hyp = len(prior)
    if n_hyp == 0:
        return 0.0
    n_ans = len(likelihoods[0]) if likelihoods else 0

    h_prior = shannon_entropy(prior)

    expected_posterior_entropy = 0.0
    for a in range(n_ans):
        # Marginal probability of observing answer a.
        p_a = sum(prior[h] * likelihoods[h][a] for h in range(n_hyp))
        if p_a <= _EPS:
            continue
        # Posterior over hypotheses given answer a.
        posterior = [prior[h] * likelihoods[h][a] / p_a for h in range(n_hyp)]
        expected_posterior_entropy += p_a * shannon_entropy(posterior)

    return h_prior - expected_posterior_entropy


# ---------------------------------------------------------------------------
# Section 2: Cognitive graph model
# ---------------------------------------------------------------------------

@dataclass
class TraitBelief:
    """The model's belief that a concept possesses a trait.

    probability:  P(trait holds | instance of concept), in [0, 1].
    support:      number of observed instances backing this estimate.
    essential:    True iff the trait is held to be *definitional* (analytic),
                  i.e. removing it would make the instance not-a-member.
                  None means the system has not yet committed either way -- the
                  very gap curiosity exists to close.
    """

    probability: Probability
    support: int = 1
    essential: Optional[bool] = None


@dataclass
class Concept:
    """A node in the cognitive graph."""

    name: str
    parents: List[str] = field(default_factory=list)          # IS-A edges
    traits: Dict[str, TraitBelief] = field(default_factory=dict)


class CognitiveGraph:
    """A minimal inheritance graph with probabilistic traits.

    Mirrors the semantics of the production `living_edges` table (IS-A edges +
    weighted property edges) but kept in-memory and dependency-free so the
    information-gain logic can be reasoned about and tested in isolation.
    """

    def __init__(self) -> None:
        self._concepts: Dict[str, Concept] = {}

    def add_concept(self, name: str, parents: Optional[Sequence[str]] = None) -> Concept:
        concept = self._concepts.get(name)
        if concept is None:
            concept = Concept(name=name, parents=list(parents or []))
            self._concepts[name] = concept
        elif parents:
            for p in parents:
                if p not in concept.parents:
                    concept.parents.append(p)
        return concept

    def assert_trait(
        self,
        concept: str,
        trait: str,
        probability: Probability,
        support: int = 1,
        essential: Optional[bool] = None,
    ) -> None:
        node = self.add_concept(concept)
        node.traits[trait] = TraitBelief(probability, support, essential)

    def get(self, name: str) -> Optional[Concept]:
        return self._concepts.get(name)

    def ancestors(self, name: str) -> List[str]:
        """Return all IS-A ancestors (breadth-first, no cycles)."""
        seen: List[str] = []
        frontier = list(self._concepts.get(name, Concept(name)).parents)
        while frontier:
            current = frontier.pop(0)
            if current in seen:
                continue
            seen.append(current)
            node = self._concepts.get(current)
            if node:
                frontier.extend(node.parents)
        return seen

    def inherited_trait(self, name: str, trait: str) -> Optional[Tuple[str, TraitBelief]]:
        """Find the nearest ancestor that asserts `trait`. Returns (owner, belief)."""
        for ancestor in self.ancestors(name):
            node = self._concepts.get(ancestor)
            if node and trait in node.traits:
                return ancestor, node.traits[trait]
        return None

    def siblings(self, name: str) -> List[str]:
        """Concepts sharing at least one direct parent with `name`."""
        node = self._concepts.get(name)
        if not node:
            return []
        parents = set(node.parents)
        out = []
        for other_name, other in self._concepts.items():
            if other_name == name:
                continue
            if parents.intersection(other.parents):
                out.append(other_name)
        return out

    def exception_ratio(self, parent: str, trait: str) -> Tuple[int, int]:
        """Among known direct children of `parent` that have an opinion on
        `trait`, count how many CONTRADICT the parent's trait value.

        Returns (n_exceptions, n_children_with_opinion). This statistic is the
        empirical evidence that shapes the *prior* over structural hypotheses:
        many exceptions -> the parent trait is probably a soft default or
        actually belongs to a subclass; zero exceptions -> likely essential.
        """
        owner = self._concepts.get(parent)
        if not owner or trait not in owner.traits:
            return 0, 0
        parent_holds = owner.traits[trait].probability >= 0.5

        n_children = 0
        n_exceptions = 0
        for child_name, child in self._concepts.items():
            if parent not in child.parents:
                continue
            if trait not in child.traits:
                continue
            n_children += 1
            child_holds = child.traits[trait].probability >= 0.5
            if child_holds != parent_holds:
                n_exceptions += 1
        return n_exceptions, n_children


# ---------------------------------------------------------------------------
# Section 3: Domain objects (experience, surprise, hypotheses, inquiry)
# ---------------------------------------------------------------------------

@dataclass
class Experience:
    """A single predict-then-observe episode involving an inherited trait.

    subject:          the concept actually observed (e.g. "penguin").
    trait:            the trait under prediction (e.g. "can_fly").
    predicted_value:  what the model expected (bool).
    predicted_prob:   model confidence in `predicted_value`, in [0, 1].
    observed_value:   what reality showed (bool).
    """

    subject: str
    trait: str
    predicted_value: bool
    predicted_prob: Probability
    observed_value: bool

    @property
    def is_failure(self) -> bool:
        return self.predicted_value != self.observed_value


class StructuralHypothesis(str, Enum):
    """The competing structural explanations for an inherited-trait conflict."""

    ESSENTIAL = "trait_is_essential_to_parent"
    DEFAULT_WITH_EXCEPTION = "trait_is_default_subject_is_exception"
    BELONGS_TO_SUBCLASS = "trait_belongs_to_intermediate_subclass"
    MISCLASSIFIED = "subject_is_misclassified_under_parent"


@dataclass
class SurpriseReport:
    """Output of the uncertainty trigger."""

    experience: Experience
    surprise_bits: float
    triggered: bool
    parent: Optional[str] = None
    inherited_belief: Optional[TraitBelief] = None

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        status = "TRIGGERED" if self.triggered else "below-threshold"
        return (
            f"Surprise[{status}] {self.surprise_bits:.2f} bits :: "
            f"{self.experience.subject}.{self.experience.trait} "
            f"predicted={self.experience.predicted_value} "
            f"observed={self.experience.observed_value}"
        )


@dataclass
class TargetedInquiry:
    """A structural question the engine needs answered to resolve dissonance.

    This is NOT a natural-language afterthought -- the `resolves` /
    `answer_space` / `hypothesis_priors` fields define, in machine-actionable
    terms, exactly which structural relationship is in question and how each
    possible answer would re-wire the graph.
    """

    question: str
    relation_in_question: str               # e.g. "Bird --can_fly--> ?"
    answer_space: List[str]
    expected_information_gain: float        # bits
    prior_entropy: float                    # bits of structural uncertainty
    hypothesis_priors: Dict[str, Probability]
    resolves: List[StructuralHypothesis]
    rationale: str

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return (
            f"TargetedInquiry(EIG={self.expected_information_gain:.3f} bits | "
            f"H_prior={self.prior_entropy:.3f} bits)\n"
            f"  Q: {self.question}\n"
            f"  relation: {self.relation_in_question}\n"
            f"  answers : {self.answer_space}"
        )


# ---------------------------------------------------------------------------
# Section 4: The Curiosity Engine
# ---------------------------------------------------------------------------

class CuriosityEngine:
    """Information-gain-driven curiosity over an inheritance graph."""

    def __init__(self, graph: CognitiveGraph, surprise_threshold_bits: float = 2.0) -> None:
        self.graph = graph
        # 2 bits ~ the model assigned <= 25% to the outcome that occurred.
        self.surprise_threshold_bits = surprise_threshold_bits

    # -- Requirement 1: The Uncertainty Trigger ---------------------------
    def evaluate_surprise(self, experience: Experience) -> SurpriseReport:
        """Quantify the surprise of a prediction failure as self-information.

        Surprise is the surprisal of the *observed* value under the model's
        own predictive distribution. Confident-and-wrong => large surprise.
        """
        # P(observed) under the model. If the model predicted `predicted_value`
        # with `predicted_prob`, then the complementary outcome carried the
        # residual mass (1 - predicted_prob).
        if experience.observed_value == experience.predicted_value:
            p_observed = experience.predicted_prob
        else:
            p_observed = 1.0 - experience.predicted_prob

        surprise = self_information(p_observed)
        triggered = experience.is_failure and surprise >= self.surprise_threshold_bits

        parent_info = self.graph.inherited_trait(experience.subject, experience.trait)
        parent = parent_info[0] if parent_info else None
        belief = parent_info[1] if parent_info else None

        return SurpriseReport(
            experience=experience,
            surprise_bits=surprise,
            triggered=triggered,
            parent=parent,
            inherited_belief=belief,
        )

    # -- Prior over structural hypotheses --------------------------------
    def _derive_hypothesis_prior(
        self, report: SurpriseReport
    ) -> Dict[StructuralHypothesis, Probability]:
        """Turn graph evidence into a prior P(H) over structural explanations.

        The empirical exception ratio among the parent's children is the key
        signal:
          * zero exceptions among many children  -> trait looks ESSENTIAL.
          * a sizeable minority of exceptions     -> trait is a DEFAULT and the
            subject is an exception, or the exceptions form a SUBCLASS.
          * the parent trait was itself near-certain (high p, high support) ->
            mild evidence the subject is simply MISCLASSIFIED.
        """
        exp = report.experience
        parent = report.parent
        belief = report.inherited_belief

        # Weights (unnormalised) for each hypothesis; start from a weak uniform
        # prior so no explanation is ever assigned probability zero.
        w = {
            StructuralHypothesis.ESSENTIAL: 1.0,
            StructuralHypothesis.DEFAULT_WITH_EXCEPTION: 1.0,
            StructuralHypothesis.BELONGS_TO_SUBCLASS: 1.0,
            StructuralHypothesis.MISCLASSIFIED: 1.0,
        }

        if parent is not None:
            n_exc, n_children = self.graph.exception_ratio(parent, exp.trait)
            ratio = (n_exc / n_children) if n_children else 0.0

            # More exceptions -> default / subclass become more credible.
            w[StructuralHypothesis.DEFAULT_WITH_EXCEPTION] += 4.0 * ratio + 0.5 * n_exc
            w[StructuralHypothesis.BELONGS_TO_SUBCLASS] += 3.0 * ratio
            # No exceptions at all among real children -> trait looks definitional.
            if n_children > 0 and n_exc == 0:
                w[StructuralHypothesis.ESSENTIAL] += 3.0

        if belief is not None:
            # A trait the parent holds with overwhelming, well-supported
            # probability is more plausibly essential; if it is already flagged
            # essential, a contradiction implies the subject is misclassified.
            if belief.essential is True:
                w[StructuralHypothesis.MISCLASSIFIED] += 3.0
                w[StructuralHypothesis.ESSENTIAL] += 1.0
            else:
                confidence_mass = belief.probability * math.log2(belief.support + 1)
                w[StructuralHypothesis.ESSENTIAL] += confidence_mass
                # High-but-imperfect probability is the signature of a default.
                if 0.6 <= belief.probability < 0.99:
                    w[StructuralHypothesis.DEFAULT_WITH_EXCEPTION] += 2.0

        keys = list(w.keys())
        probs = normalise([w[k] for k in keys])
        return {k: p for k, p in zip(keys, probs)}


    # Canonical hypothesis ordering used by every likelihood matrix below.
    _HYPOTHESIS_ORDER: Tuple[StructuralHypothesis, ...] = (
        StructuralHypothesis.ESSENTIAL,
        StructuralHypothesis.DEFAULT_WITH_EXCEPTION,
        StructuralHypothesis.BELONGS_TO_SUBCLASS,
        StructuralHypothesis.MISCLASSIFIED,
    )

    def _candidate_inquiries(self, report: SurpriseReport) -> List[dict]:
        """Enumerate candidate inquiries.

        Each candidate ships with a likelihood matrix P(answer | hypothesis),
        rows ordered by `_HYPOTHESIS_ORDER`. These likelihoods encode how
        diagnostic each answer is: the more sharply a question separates the
        hypotheses, the more information its answer carries.

        Note the deliberately-included NAIVE question ("What is a penguin?"):
        its answer is independent of the structural hypotheses, so its rows are
        identical and its Expected Information Gain provably collapses to ~0.
        """
        subject = report.experience.subject
        trait = report.experience.trait
        parent = report.parent or "<root>"

        return [
            {
                "key": "essential_vs_typical",
                "question": (
                    f"Is '{trait}' ESSENTIAL to the concept of '{parent}', "
                    f"or merely a TYPICAL (default) trait that most '{parent}' "
                    f"instances happen to share?"
                ),
                "relation": f"{parent} --{trait}--> ? [essential | typical]",
                "answers": ["essential", "typical"],
                # rows: ESSENTIAL, DEFAULT, SUBCLASS, MISCLASSIFIED
                "likelihoods": [
                    [0.92, 0.08],
                    [0.08, 0.92],
                    [0.20, 0.80],
                    [0.85, 0.15],
                ],
                "resolves": [
                    StructuralHypothesis.ESSENTIAL,
                    StructuralHypothesis.DEFAULT_WITH_EXCEPTION,
                ],
                "rationale": (
                    "Directly probes the analytic-vs-statistical status of the "
                    "trait, which is the root of the inheritance conflict."
                ),
            },
            {
                "key": "subgroup_vs_isolated",
                "question": (
                    f"Do the '{parent}' instances lacking '{trait}' form a "
                    f"coherent subgroup (an intermediate subclass), or is "
                    f"'{subject}' an isolated exception?"
                ),
                "relation": f"{parent} --has_subclass--> ?(not {trait})",
                "answers": ["coherent_subgroup", "isolated_exception"],
                "likelihoods": [
                    [0.30, 0.70],
                    [0.25, 0.75],
                    [0.90, 0.10],
                    [0.40, 0.60],
                ],
                "resolves": [StructuralHypothesis.BELONGS_TO_SUBCLASS],
                "rationale": (
                    "Tests whether the taxonomy needs an intermediate node "
                    "rather than a per-instance override."
                ),
            },
            {
                "key": "membership_validity",
                "question": (
                    f"Given that '{subject}' lacks '{trait}', is '{subject}' "
                    f"genuinely a member of '{parent}'?"
                ),
                "relation": f"{subject} --is_a--> {parent} ? [valid | invalid]",
                "answers": ["valid_member", "invalid_member"],
                "likelihoods": [
                    [0.15, 0.85],
                    [0.95, 0.05],
                    [0.90, 0.10],
                    [0.10, 0.90],
                ],
                "resolves": [StructuralHypothesis.MISCLASSIFIED],
                "rationale": (
                    "Distinguishes a real exception from a classification error "
                    "in the IS-A edge itself."
                ),
            },
            {
                "key": "naive_definition",
                "question": f"What is a '{subject}'?",
                "relation": f"{subject} --definition--> ?",
                "answers": ["a_description", "another_description"],
                # Identical rows: the answer tells us nothing about WHICH
                # structural hypothesis is true. EIG -> 0 by construction.
                "likelihoods": [
                    [0.5, 0.5],
                    [0.5, 0.5],
                    [0.5, 0.5],
                    [0.5, 0.5],
                ],
                "resolves": [],
                "rationale": (
                    "Null-field-style question. Included as a control: its "
                    "information gain is ~0, so the engine rejects it."
                ),
            },
        ]

    # -- Requirements 2 & 3: Information gain + inquiry generation --------
    def rank_inquiries(
        self, report: SurpriseReport
    ) -> List[TargetedInquiry]:
        """Score every candidate inquiry by Expected Information Gain (desc)."""
        prior_map = self._derive_hypothesis_prior(report)
        prior_vec = [prior_map[h] for h in self._HYPOTHESIS_ORDER]
        prior_entropy = shannon_entropy(prior_vec)
        prior_named = {h.value: round(p, 4) for h, p in prior_map.items()}

        ranked: List[TargetedInquiry] = []
        for cand in self._candidate_inquiries(report):
            eig = expected_information_gain(prior_vec, cand["likelihoods"])
            ranked.append(
                TargetedInquiry(
                    question=cand["question"],
                    relation_in_question=cand["relation"],
                    answer_space=cand["answers"],
                    expected_information_gain=eig,
                    prior_entropy=prior_entropy,
                    hypothesis_priors=prior_named,
                    resolves=cand["resolves"],
                    rationale=cand["rationale"],
                )
            )

        ranked.sort(key=lambda i: i.expected_information_gain, reverse=True)
        return ranked

    def generate_inquiry(self, report: SurpriseReport) -> Optional[TargetedInquiry]:
        """Return the single highest-information-gain structural inquiry.

        Returns None when surprise did not trip the trigger -- a calm,
        well-predicted observation warrants no curiosity.
        """
        if not report.triggered:
            return None
        ranked = self.rank_inquiries(report)
        return ranked[0] if ranked else None


# ---------------------------------------------------------------------------
# Section 5: Mock simulation (Requirement 4)
# ---------------------------------------------------------------------------

def _build_demo_graph() -> CognitiveGraph:
    """A small avian world model with a single buried contradiction."""
    g = CognitiveGraph()
    g.add_concept("animal")
    g.add_concept("bird", parents=["animal"])

    # The model believes birds fly: high probability, decent support, NOT marked
    # essential -- the system has never had to decide if flight is definitional.
    g.assert_trait("bird", "can_fly", probability=0.97, support=40, essential=None)

    # Known birds that DO fly (reinforce the default).
    for flyer in ("sparrow", "eagle", "robin", "pigeon"):
        g.add_concept(flyer, parents=["bird"])
        g.assert_trait(flyer, "can_fly", probability=0.99, support=10)

    # The exception that creates the dissonance.
    g.add_concept("penguin", parents=["bird"])
    g.assert_trait("penguin", "can_fly", probability=0.02, support=8)
    return g


def _run_demo() -> TargetedInquiry:
    print("=" * 72)
    print("VELYNX C5 — Curiosity Engine v2 (Information Gain)  ::  DEMO")
    print("=" * 72)

    graph = _build_demo_graph()
    engine = CuriosityEngine(graph, surprise_threshold_bits=2.0)

    # The model predicts penguin can fly (inherited from Bird @ 0.97).
    # Reality: it cannot. A confident, wrong prediction.
    experience = Experience(
        subject="penguin",
        trait="can_fly",
        predicted_value=True,
        predicted_prob=0.97,
        observed_value=False,
    )

    # --- Step 1: Uncertainty trigger -----------------------------------
    report = engine.evaluate_surprise(experience)
    print("\n[1] UNCERTAINTY TRIGGER")
    print(f"    {report}")
    print(f"    inherited from : {report.parent} "
          f"(p={report.inherited_belief.probability if report.inherited_belief else 'n/a'})")
    print(f"    threshold      : {engine.surprise_threshold_bits:.2f} bits")

    if not report.triggered:
        print("    -> No curiosity warranted.")
        raise SystemExit(0)

    # --- Step 2/3: rank candidate inquiries by information gain ---------
    ranked = engine.rank_inquiries(report)
    print("\n[2] STRUCTURAL HYPOTHESIS PRIOR  P(H)")
    for name, p in ranked[0].hypothesis_priors.items():
        print(f"    {p:6.3f}  {name}")
    print(f"    prior structural entropy H(H) = {ranked[0].prior_entropy:.3f} bits")

    print("\n[3] EXPECTED INFORMATION GAIN  (mutual information I(H;A))")
    for inq in ranked:
        print(f"    {inq.expected_information_gain:6.3f} bits  |  {inq.question}")

    # --- Step 4: the chosen targeted inquiry ---------------------------
    chosen = engine.generate_inquiry(report)
    print("\n[4] TARGETED INQUIRY  (max information gain)")
    print("    " + str(chosen).replace("\n", "\n    "))
    print(f"    resolves: {[h.value for h in chosen.resolves]}")
    print(f"    why     : {chosen.rationale}")
    print("=" * 72)
    return chosen


if __name__ == "__main__":
    _run_demo()
