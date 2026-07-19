"""
INDEPENDENT, FROM-SCRATCH reference model for the ES-1/PA-3 mechanism, built
solely from:
  - PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md (T1)
  - PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md (the addendum, sections A0-A7, A6-DIGEST)
  - PROGRAM_A_A3_5_FINDING3_CORRECTION.md (the document under audit)
  - docs/audits/A3_5_FINDING2_SONNET_AUDIT.md (cited authority only, for the A1
    witness construction verbatim)

This file is written independently of:
  - es1_finding2_audit_reference.py / _witnesses.py / _sweep.py (the F2 auditor's own files)
  - es1_finding3_correction_reference.py / es1_finding3_verify.py (the correction author's own files)
  - audit_f3_independent.py / audit_f3_replay.py / audit_f3_subset_check.py (prior-session scratch,
    NOT read or consulted while writing this file, per the "fresh audit" mission constraint)

No numeric constant is invented; predicates (contradicts/is_material) are
supplied per-witness as explicit fixtures, exactly as the frozen
support_tests.py is unimplemented (NotImplementedError stubs) at this
pre-G4 DRAFT stage -- this is the same posture the F1/F2 audits took.
"""

from itertools import combinations, permutations
import random


class Claim:
    __slots__ = ("name", "claim_text", "supp")

    def __init__(self, name, claim_text, supp):
        # supp: tuple of (origin_domain, doc_id) pairs
        self.name = name
        self.claim_text = claim_text
        self.supp = tuple(supp)

    def __repr__(self):
        return f"Claim({self.name!r})"

    def __eq__(self, other):
        return isinstance(other, Claim) and self.name == other.name

    def __hash__(self):
        return hash(self.name)


def independent_origins(doc_ids):
    """T1 Sec 5.2 INDEPENDENCE_RELATION: distinct origin_domain count (no
    mirror/syndication collapsing needed in these synthetic fixtures -- each
    origin string already denotes a distinct origin)."""
    return len(set(o for (o, _d) in doc_ids))


def ios(claim):
    return independent_origins(claim.supp)


def evidence_key(doc_id):
    # T1 Sec 5.5 EVIDENCE_ORDERING_KEY: lexicographic on (origin_domain, doc_id)
    return doc_id  # already an (origin, doc) tuple -> lexicographic by construction


def min_evidence_key(claim):
    return min(evidence_key(d) for d in claim.supp)


def rank_key(claim):
    # A2: primary ios desc, secondary min EVIDENCE_ORDERING_KEY asc, tertiary claim_text asc
    return (-ios(claim), min_evidence_key(claim), claim.claim_text)


class TieError(Exception):
    pass


def argmax(claim_set):
    """A2: unique ~-maximum (= minimum of rank_key). Raises TieError if the
    full 3-key tuple collides between two distinct claims (undefined per the
    addendum's unproven injectivity assumption -- same posture as prior audits'
    F2)."""
    claims = list(claim_set)
    if not claims:
        raise ValueError("argmax over empty set")
    keys = [(rank_key(c), c) for c in claims]
    keys.sort(key=lambda t: t[0])
    best_key = keys[0][0]
    winners = [c for k, c in keys if k == best_key]
    if len(winners) > 1:
        raise TieError(f"full rank_key tie among {[c.name for c in winners]}")
    return keys[0][1]


def firing_pairs(Sigma, contradicts, is_material):
    """A4 conds 1-3: the S1-firing predicate over unordered pairs."""
    out = []
    for a, b in combinations(sorted(Sigma, key=lambda c: c.name), 2):
        if not contradicts(a, b):
            continue
        if not is_material(a, b):
            continue
        if independent_origins(a.supp + b.supp) >= 2:
            out.append((a, b))
    return out


def s1pair(a, b, contradicts, is_material):
    if not contradicts(a, b):
        return False
    if not is_material(a, b):
        return False
    return independent_origins(a.supp + b.supp) >= 2


def classify_finding2(claims, contradicts, is_material, seed=None, shuffle=False):
    """Finding-2-only rule: Comp has NO cond-3 filter (D1 unchanged), Part
    fallback present. Used as a differential baseline against the Finding-3
    corrected rule below -- NOT the object under audit by itself."""
    claim_list = list(claims)
    if shuffle:
        rnd = random.Random(seed)
        rnd.shuffle(claim_list)
    Sigma = [c for c in claim_list if ios(c) >= 1]
    if not Sigma:
        return dict(state="S0", selected_claim=None, support=(), contradiction=(),
                    ioc=0, branch=None, competing=None, firing_pairs=[])

    fps = firing_pairs(Sigma, contradicts, is_material)
    if fps:
        sc = argmax(Sigma)
        Comp = [c for c in Sigma if c != sc and contradicts(sc, c) and is_material(sc, c)]
        if Comp:
            competing = argmax(Comp)
            branch = "Comp"
        else:
            Part = sorted(set(x for pair in fps for x in pair), key=lambda c: c.name)
            competing = argmax(Part)
            branch = "Part"
        return dict(
            state="S1", selected_claim=sc,
            support=tuple(sorted(sc.supp)),
            contradiction=tuple(sorted(competing.supp)),
            ioc=ios(sc), branch=branch, competing=competing,
            firing_pairs=[(a.name, b.name) for a, b in fps],
        )

    sc = argmax(Sigma)
    n = ios(sc)
    return dict(
        state=("S3" if n >= 2 else "S2"), selected_claim=sc,
        support=tuple(sorted(sc.supp)), contradiction=(), ioc=n,
        branch=None, competing=None, firing_pairs=[],
    )


def classify_finding3(claims, contradicts, is_material, seed=None, shuffle=False):
    """The corrected rule under audit: Finding 2's Comp/Part split, with
    Finding 3's cond-3 conjunct added to Comp membership (addendum Sec A4, as
    merged; PROGRAM_A_A3_5_FINDING3_CORRECTION.md Sec 3.1)."""
    claim_list = list(claims)
    if shuffle:
        rnd = random.Random(seed)
        rnd.shuffle(claim_list)
    Sigma = [c for c in claim_list if ios(c) >= 1]
    if not Sigma:
        return dict(state="S0", selected_claim=None, support=(), contradiction=(),
                    ioc=0, branch=None, competing=None, firing_pairs=[], comp=[], part=[])

    fps = firing_pairs(Sigma, contradicts, is_material)
    if fps:
        sc = argmax(Sigma)
        Comp = [c for c in Sigma
                if c != sc and s1pair(sc, c, contradicts, is_material)]
        if Comp:
            competing = argmax(Comp)
            branch = "Comp"
        else:
            Part = sorted(set(x for pair in fps for x in pair), key=lambda c: c.name)
            competing = argmax(Part)
            branch = "Part"
        Part_full = sorted(set(x for pair in fps for x in pair), key=lambda c: c.name)
        return dict(
            state="S1", selected_claim=sc,
            support=tuple(sorted(sc.supp)),
            contradiction=tuple(sorted(competing.supp)),
            ioc=ios(sc), branch=branch, competing=competing,
            firing_pairs=[(a.name, b.name) for a, b in fps],
            comp=[c.name for c in Comp], part=[c.name for c in Part_full],
        )

    sc = argmax(Sigma)
    n = ios(sc)
    return dict(
        state=("S3" if n >= 2 else "S2"), selected_claim=sc,
        support=tuple(sorted(sc.supp)), contradiction=(), ioc=n,
        branch=None, competing=None, firing_pairs=[], comp=[], part=[],
    )


def selected_participates(result):
    """True iff selected_claim is a member of some firing pair (the actual
    property I-3's biconditional claims 'Comp != empty' to mean)."""
    if result["state"] != "S1":
        return None
    sc_name = result["selected_claim"].name
    return any(sc_name in pair for pair in result["firing_pairs"])
