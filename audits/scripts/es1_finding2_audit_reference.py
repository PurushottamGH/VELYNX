"""
Independent reference model for the ES-1 / PA-3 Finding-2 correction audit.
Built ONLY from:
  - PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md (T1, frozen)
  - PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md (addendum, frozen)
  - PROGRAM_A_A3_5_FINDING2_CORRECTION.md (the corrected D1 anchoring rule, section 3.1)
Not part of program_a/ (that package remains NotImplementedError stubs under the
standing prohibition). Scratch auditor reference implementation only.
"""

from itertools import combinations

# ---------- Claim / evidence model ----------

class Claim:
    def __init__(self, name, claim_text, evidence):
        # evidence: list of (origin_domain, doc_id)
        self.name = name
        self.claim_text = claim_text
        self.evidence = list(evidence)
    def __repr__(self):
        return "Claim(%s)" % self.name
    def __eq__(self, other):
        return isinstance(other, Claim) and self.name == other.name
    def __hash__(self):
        return hash(self.name)

def independent_origins(evidence_items):
    return len(set(o for (o, d) in evidence_items))

def supp(c):
    return set(c.evidence)

def ios(c):
    return independent_origins(supp(c))

def evidence_ordering_key(item):
    return item  # already (origin_domain, doc_id) lexicographic tuple

def min_evidence_key(c):
    return min(c.evidence, key=evidence_ordering_key)

def rank_key(c):
    # primary: -ios (descending ios => ascending -ios), secondary: min evidence key asc,
    # tertiary: claim_text asc
    return (-ios(c), min_evidence_key(c), c.claim_text)

class TieError(Exception):
    pass

def argmax(claim_set, allow_tie_report=False):
    """
    strict-order maximum under rank_key (lower rank_key wins, i.e. higher ios first).
    Raises TieError if two elements collide on the full key (F2-class attack),
    unless allow_tie_report, in which case it returns (winner_or_None, is_tied_bool).
    """
    claims = list(claim_set)
    if not claims:
        return None
    keys = [(rank_key(c), c) for c in claims]
    keys.sort(key=lambda t: t[0])
    best_key = keys[0][0]
    tied = [c for k, c in keys if k == best_key]
    if len(tied) > 1:
        if allow_tie_report:
            return None, True
        raise TieError("Non-unique argmax: %r all share rank_key %r" % (tied, best_key))
    if allow_tie_report:
        return tied[0], False
    return tied[0]


class Oracle:
    """contradicts/is_material as explicit frozen 'oracle' tables (matches the
    Finding-1-audit's methodology: these are supplied per witness, not invented)."""
    def __init__(self, contradicts_pairs=(), material_pairs=None):
        self._contra = set()
        for a, b in contradicts_pairs:
            self._contra.add(frozenset((a, b)))
        # materiality only meaningful (and only ever invoked) on a contradicting pair (A5 precondition)
        self._material = set()
        mp = material_pairs if material_pairs is not None else contradicts_pairs
        for a, b in mp:
            self._material.add(frozenset((a, b)))

    def contradicts(self, a, b):
        return frozenset((a.name, b.name)) in self._contra

    def is_material(self, a, b):
        # frozen precondition A5: only meaningful / only invoked when contradicts is True
        if not self.contradicts(a, b):
            return False
        return frozenset((a.name, b.name)) in self._material


# ---------- Classifier (T1 + addendum, PRE Finding-2 correction) ----------

def s1_pair_fires(oracle, a, b):
    """A4 conditions 1-3 on unordered pair {a,b}."""
    if not oracle.contradicts(a, b):
        return False
    if not oracle.is_material(a, b):
        return False
    if independent_origins(supp(a) | supp(b)) < 2:
        return False
    return True

def fires_s1(oracle, sigma):
    for a, b in combinations(sigma, 2):
        if s1_pair_fires(oracle, a, b):
            return True
    return False

def s1_firing_pairs(oracle, sigma):
    return [(a, b) for a, b in combinations(sigma, 2) if s1_pair_fires(oracle, a, b)]

def classify_pre_finding2(oracle, claims):
    """Frozen T1 + addendum, D1 = ORIGINAL (pre-Finding-2) anchoring rule.
    contradiction_doc_ids is UNDEFINED if the scoped Comp set is empty."""
    sigma = [c for c in claims if ios(c) >= 1]
    if not sigma:
        return dict(state="S0", selected_claim=None, support_doc_ids=(),
                     contradiction_doc_ids=(), independent_origin_count=0)

    if fires_s1(oracle, sigma):
        selected_claim = argmax(sigma)
        comp = [c for c in sigma if c is not selected_claim
                and oracle.contradicts(selected_claim, c)
                and oracle.is_material(selected_claim, c)]
        if not comp:
            return dict(state="S1", selected_claim=selected_claim.name,
                         support_doc_ids=tuple(sorted(supp(selected_claim))),
                         contradiction_doc_ids="UNDEFINED (argmax over empty Comp)",
                         independent_origin_count=ios(selected_claim),
                         UNDEFINED=True)
        competing = argmax(comp)
        return dict(state="S1", selected_claim=selected_claim.name,
                     support_doc_ids=tuple(sorted(supp(selected_claim))),
                     contradiction_doc_ids=tuple(sorted(supp(competing))),
                     independent_origin_count=ios(selected_claim),
                     UNDEFINED=False)

    selected_claim = argmax(sigma)
    n = ios(selected_claim)
    state = "S3" if n >= 2 else "S2"
    return dict(state=state, selected_claim=selected_claim.name,
                support_doc_ids=tuple(sorted(supp(selected_claim))),
                contradiction_doc_ids=(), independent_origin_count=n)


# ---------- Classifier, POST Finding-2 correction (the fallback under audit) ----------

def classify_post_finding2(oracle, claims, seed=None):
    """
    Same as above but D1 is the Finding-2-corrected anchoring rule (correction doc
    section 3.1): if Comp (contradicting selected_claim) is empty, fall back to
    Part = the union of all claims participating in some S1-firing pair.
    `seed` is accepted-and-unused, exactly as the frozen contract requires (T1 sec 7.2),
    included here only to mechanically test seed-independence.
    """
    sigma = [c for c in claims if ios(c) >= 1]
    if not sigma:
        return dict(state="S0", selected_claim=None, support_doc_ids=(),
                     contradiction_doc_ids=(), independent_origin_count=0,
                     branch=None)

    firing_pairs = s1_firing_pairs(oracle, sigma)
    if firing_pairs:
        selected_claim = argmax(sigma)
        comp = [c for c in sigma if c is not selected_claim
                and oracle.contradicts(selected_claim, c)
                and oracle.is_material(selected_claim, c)]
        if comp:
            competing = argmax(comp)
            branch = "Comp"
        else:
            part = set()
            for a, b in firing_pairs:
                part.add(a)
                part.add(b)
            competing = argmax(part)
            branch = "Part"

        # independent check of the correction's own textual claim:
        # "Comp != empty => selected_claim participates in the S1-triggering contradiction"
        selected_is_true_s1_participant = any(
            (selected_claim is a or selected_claim is b) for a, b in firing_pairs
        )

        return dict(state="S1", selected_claim=selected_claim.name,
                     support_doc_ids=tuple(sorted(supp(selected_claim))),
                     contradiction_doc_ids=tuple(sorted(supp(competing))),
                     competing_claim=competing.name,
                     independent_origin_count=ios(selected_claim),
                     branch=branch,
                     comp_nonempty=bool(comp),
                     selected_is_true_s1_participant=selected_is_true_s1_participant,
                     firing_pairs=sorted(tuple(sorted((a.name, b.name))) for a, b in firing_pairs))

    selected_claim = argmax(sigma)
    n = ios(selected_claim)
    state = "S3" if n >= 2 else "S2"
    return dict(state=state, selected_claim=selected_claim.name,
                support_doc_ids=tuple(sorted(supp(selected_claim))),
                contradiction_doc_ids=(), independent_origin_count=n, branch=None)
