"""
INDEPENDENT auditor reference model for the ES-1 / PA-3 Finding-3 correction.

Written from scratch, from the FROZEN TEXT ONLY:
  - PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md  (SS A1, A2, A3, A4, A7)
  - PROGRAM_A_A3_5_FINDING2_CORRECTION.md SS3.1 (the Comp/Part split under audit)
  - PROGRAM_A_A3_5_FINDING3_CORRECTION.md SS3.1 (the cond-3-on-Comp amendment under audit)

Deliberately does NOT import or reuse any of the correction author's own scratch
files (es1_finding2_audit_reference.py, es1_finding3_correction_reference.py,
es1_finding3_verify.py). This is an independent re-derivation so the audit does
not simply replay the author's own test harness back at them.

Not part of program_a/ (standing prohibition, ES1_IMPLEMENTATION_GATE.md:91-93).
Scratch auditor artifact only.
"""

from itertools import combinations

class Claim:
    __slots__ = ("name", "claim_text", "evidence")
    def __init__(self, name, claim_text, evidence):
        self.name = name
        self.claim_text = claim_text
        self.evidence = tuple(evidence)  # tuple of (origin_domain, doc_id)
    def __repr__(self):
        return "Claim(%s)" % self.name

def supp(c):
    return set(c.evidence)

def independent_origins(evidence_items):
    return len(set(o for (o, d) in evidence_items))

def ios(c):
    return independent_origins(supp(c))

def min_evidence_key(c):
    return min(c.evidence)  # (origin_domain, doc_id) lexicographic, already EVIDENCE_ORDERING_KEY

def rank_key(c):
    # SSA2: primary ios desc, secondary min-evidence-key asc, tertiary claim_text asc
    return (-ios(c), min_evidence_key(c), c.claim_text)

class TieError(Exception):
    pass

def prec_max(claims):
    """the -max under SS A2's strict total order. Raises on a genuine full-key tie
    (the pre-existing, out-of-scope F2 dependency -- not this audit's target)."""
    claims = list(claims)
    if not claims:
        return None
    keys = sorted(((rank_key(c), c) for c in claims), key=lambda t: t[0])
    if len(claims) > 1 and keys[0][0] == keys[1][0]:
        raise TieError("full rank_key tie: %r" % ([c for _, c in keys if _ == keys[0][0]],))
    return keys[0][1]


class Oracle:
    """contradicts/is_material supplied per-witness (frozen SSA5/A6 contract:
    is_material(a,b) is only meaningful, and only ever invoked, when contradicts(a,b))."""
    def __init__(self, contra=(), non_material=()):
        self._contra = set(frozenset(p) for p in contra)
        self._non_material = set(frozenset(p) for p in non_material)  # contradicts but NOT material
    def contradicts(self, a, b):
        return frozenset((a.name, b.name)) in self._contra
    def is_material(self, a, b):
        if not self.contradicts(a, b):
            return False
        return frozenset((a.name, b.name)) not in self._non_material


def s1pair(oracle, a, b):
    """The frozen SSA4 firing predicate, conditions 1-3, verbatim."""
    if not oracle.contradicts(a, b):
        return False
    if not oracle.is_material(a, b):
        return False
    if independent_origins(supp(a) | supp(b)) < 2:
        return False
    return True

def firing_pairs(oracle, sigma):
    return [(a, b) for a, b in combinations(sigma, 2) if s1pair(oracle, a, b)]


def classify_f2(oracle, claims):
    """SS A1-A4 + Finding-2's Comp/Part anchoring (Comp has NO cond-3 filter)."""
    sigma = [c for c in claims if ios(c) >= 1]
    if not sigma:
        return dict(state="S0", selected_claim=None, support=(), contradiction=(), ioc=0, branch=None)
    fp = firing_pairs(oracle, sigma)
    if fp:
        sel = prec_max(sigma)
        comp = [c for c in sigma if c is not sel
                and oracle.contradicts(sel, c) and oracle.is_material(sel, c)]
        if comp:
            competing = prec_max(comp); branch = "Comp"
        else:
            part = set(x for pair in fp for x in pair)
            competing = prec_max(part); branch = "Part"
        return dict(state="S1", selected_claim=sel.name,
                    support=tuple(sorted(supp(sel))),
                    contradiction=tuple(sorted(supp(competing))),
                    competing=competing.name, ioc=ios(sel), branch=branch,
                    firing_pairs=sorted(tuple(sorted((a.name, b.name))) for a, b in fp))
    sel = prec_max(sigma)
    n = ios(sel)
    return dict(state=("S3" if n >= 2 else "S2"), selected_claim=sel.name,
                support=tuple(sorted(supp(sel))), contradiction=(), ioc=n, branch=None)


def classify_f3(oracle, claims):
    """SS A1-A4 + Finding-3's corrected Comp (adds cond-3 to the {selected_claim,c} pair)."""
    sigma = [c for c in claims if ios(c) >= 1]
    if not sigma:
        return dict(state="S0", selected_claim=None, support=(), contradiction=(), ioc=0, branch=None)
    fp = firing_pairs(oracle, sigma)
    if fp:
        sel = prec_max(sigma)
        comp = [c for c in sigma if c is not sel and s1pair(oracle, sel, c)]
        if comp:
            competing = prec_max(comp); branch = "Comp"
        else:
            part = set(x for pair in fp for x in pair)
            competing = prec_max(part); branch = "Part"
        sel_participates = any(sel is a or sel is b for a, b in fp)
        return dict(state="S1", selected_claim=sel.name,
                    support=tuple(sorted(supp(sel))),
                    contradiction=tuple(sorted(supp(competing))),
                    competing=competing.name, ioc=ios(sel), branch=branch,
                    sel_participates=sel_participates,
                    firing_pairs=sorted(tuple(sorted((a.name, b.name))) for a, b in fp))
    sel = prec_max(sigma)
    n = ios(sel)
    return dict(state=("S3" if n >= 2 else "S2"), selected_claim=sel.name,
                support=tuple(sorted(supp(sel))), contradiction=(), ioc=n, branch=None)


def competing_is_participant(oracle, claims, res):
    """genuine correctness predicate: is res['competing'] a member of SOME firing pair?"""
    sigma = [c for c in claims if ios(c) >= 1]
    fp = firing_pairs(oracle, sigma)
    participants = set(x.name for pair in fp for x in pair)
    return res.get("competing") in participants


CORE = ["state", "selected_claim", "support", "contradiction", "ioc"]
def core(r):
    return {k: r.get(k) for k in CORE}


if __name__ == "__main__":
    import json
    print("Independent F3 reference model loaded OK.")
