"""
Finding-3 correction reference model.

Extends the auditor's own scratch reference (es1_finding2_audit_reference.py)
with the F3-corrected anchoring rule: the ONLY change is that the `Comp` set
gains the §A4 condition-3 (cross-origin independence) filter -- i.e. `Comp`
becomes exactly "the claims that form an S1-FIRING pair WITH selected_claim",
using the frozen §A4 predicate verbatim. No new predicate, no new constant.

Not part of program_a/ (standing prohibition). Scratch verification only.
"""

from es1_finding2_audit_reference import (
    Claim, Oracle, argmax, ios, supp, TieError,
    s1_pair_fires, s1_firing_pairs, classify_post_finding2,
)


def classify_post_finding3(oracle, claims, seed=None):
    """
    F3-corrected anchoring. Identical to classify_post_finding2 EXCEPT the
    `comp` list adds the frozen §A4 cross-origin condition on the pair
    {selected_claim, c}. `s1_pair_fires` IS the frozen §A4 conds 1-3 predicate
    (contradicts ∧ is_material ∧ cross-origin independence) -- reused verbatim.
    """
    sigma = [c for c in claims if ios(c) >= 1]
    if not sigma:
        return dict(state="S0", selected_claim=None, support_doc_ids=(),
                    contradiction_doc_ids=(), independent_origin_count=0, branch=None)

    firing_pairs = s1_firing_pairs(oracle, sigma)
    if firing_pairs:
        selected_claim = argmax(sigma)
        # F3: Comp = { c : {selected_claim, c} is an S1-FIRING pair } (adds §A4 cond 3)
        comp = [c for c in sigma if c is not selected_claim
                and s1_pair_fires(oracle, selected_claim, c)]
        if comp:
            competing = argmax(comp)
            branch = "Comp"
        else:
            part = set()
            for a, b in firing_pairs:
                part.add(a); part.add(b)
            competing = argmax(part)
            branch = "Part"

        selected_is_true_s1_participant = any(
            (selected_claim is a or selected_claim is b) for a, b in firing_pairs
        )
        return dict(state="S1", selected_claim=selected_claim.name,
                    support_doc_ids=tuple(sorted(supp(selected_claim))),
                    contradiction_doc_ids=tuple(sorted(supp(competing))),
                    competing_claim=competing.name,
                    independent_origin_count=ios(selected_claim),
                    branch=branch, comp_nonempty=bool(comp),
                    selected_is_true_s1_participant=selected_is_true_s1_participant,
                    firing_pairs=sorted(tuple(sorted((a.name, b.name))) for a, b in firing_pairs))

    selected_claim = argmax(sigma)
    n = ios(selected_claim)
    return dict(state=("S3" if n >= 2 else "S2"), selected_claim=selected_claim.name,
                support_doc_ids=tuple(sorted(supp(selected_claim))),
                contradiction_doc_ids=(), independent_origin_count=n, branch=None)


def competing_is_true_s1_participant(oracle, claims):
    """The F3 correctness property: the emitted competing claim is a member of
    some S1-firing pair (a genuine participant in the S1-triggering contradiction)."""
    sigma = [c for c in claims if ios(c) >= 1]
    fp = s1_firing_pairs(oracle, sigma)
    if not fp:
        return None
    participants = set()
    for a, b in fp:
        participants.add(a.name); participants.add(b.name)
    r = classify_post_finding3(oracle, claims)
    return r["competing_claim"] in participants
