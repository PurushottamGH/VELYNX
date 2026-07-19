import json
import random
from es1_finding2_audit_reference import (
    Claim, Oracle, classify_pre_finding2, classify_post_finding2,
    argmax, ios, TieError, s1_firing_pairs
)

def line(s="-"):
    print(s * 90)

def show(label, result):
    print("  %-8s -> %s" % (label, result))

results_log = {}

def record(name, result):
    results_log[name] = result

# =====================================================================
# REPLAY 1: "original witness" -- Finding-1 correction's own witness
#   (same-origin material contradiction; capital Alpha/Beta). Not affected
#   by Finding 2 (no S1 fires here) -- replayed under BOTH pre- and
#   post-Finding-2 classifiers to confirm Finding-2 changes nothing here.
# =====================================================================
line("=")
print("REPLAY 1 -- ORIGINAL WITNESS (Finding-1 correction Sec 4.1: same-origin contradiction)")
line("=")
a = Claim("a", "the capital is Alpha", [("d1", "doc1")])
b = Claim("b", "the capital is Beta", [("d1", "doc2")])
oracle_w0 = Oracle(contradicts_pairs=[("a", "b")])
claims_w0 = [a, b]

r_pre = classify_pre_finding2(oracle_w0, claims_w0)
r_post = classify_post_finding2(oracle_w0, claims_w0)
r_post_seed = classify_post_finding2(oracle_w0, claims_w0, seed=999)
r_post_shuffled = classify_post_finding2(oracle_w0, list(reversed(claims_w0)))
show("pre-F2", r_pre)
show("post-F2", r_post)
show("post-F2(seed=999)", r_post_seed)
show("post-F2(shuffled)", r_post_shuffled)
assert r_pre["state"] == "S2" and r_pre["selected_claim"] == "a"
assert r_post == r_post_seed
assert r_post["state"] == "S2" and r_post["selected_claim"] == "a"
assert r_post["support_doc_ids"] == (("d1", "doc1"),)
assert r_post["contradiction_doc_ids"] == ()
record("R1_original_witness", r_post)
print("VERDICT: unaffected by Finding 2 (S1 never fires here) -- survives, as claimed (correction Sec 3.3/5.2).")

# =====================================================================
# REPLAY 2: "Finding 1 witness" / "Finding 2 witness" -- audit's W2 / F1
#   (the anchoring-gap witness). Replay PRE-Finding-2 (must reproduce the
#   UNDEFINED result / the falsification) and POST-Finding-2 (must reproduce
#   the correction doc's claimed fix).
# =====================================================================
line("=")
print("REPLAY 2 -- W2 / FINDING F1 WITNESS (anchoring gap: S1 pair disjoint from selected_claim)")
line("=")
top2 = Claim("top2", "top2", [("d1", "e1"), ("d2", "e2"), ("d3", "e3")])
x2 = Claim("x2", "x2", [("d4", "e4")])
y2 = Claim("y2", "y2", [("d5", "e5")])
oracle_w2 = Oracle(contradicts_pairs=[("x2", "y2")])
claims_w2 = [top2, x2, y2]

r_pre_w2 = classify_pre_finding2(oracle_w2, claims_w2)
r_post_w2 = classify_post_finding2(oracle_w2, claims_w2)
r_post_w2_seed = classify_post_finding2(oracle_w2, claims_w2, seed=42)
r_post_w2_shuffled = classify_post_finding2(oracle_w2, [y2, top2, x2])
show("pre-F2 (should be UNDEFINED)", r_pre_w2)
show("post-F2", r_post_w2)
show("post-F2(seed=42)", r_post_w2_seed)
show("post-F2(shuffled)", r_post_w2_shuffled)
assert r_pre_w2["UNDEFINED"] is True
assert r_post_w2["state"] == "S1"
assert r_post_w2["selected_claim"] == "top2"
assert r_post_w2["branch"] == "Part"
assert r_post_w2["comp_nonempty"] is False
assert r_post_w2["competing_claim"] in ("x2", "y2")
CORE_FIELDS = ["state", "selected_claim", "support_doc_ids", "contradiction_doc_ids",
               "independent_origin_count", "branch", "competing_claim", "comp_nonempty"]
def core(r):
    return {k: r[k] for k in CORE_FIELDS if k in r}
assert core(r_post_w2) == core(r_post_w2_seed) == core(r_post_w2_shuffled), \
    (core(r_post_w2), core(r_post_w2_seed), core(r_post_w2_shuffled))
record("R2_W2_F1_witness", r_post_w2)
print("VERDICT: replay CONFIRMS the correction's own claimed fix -- Comp empty, Part fallback fires,")
print("         deterministic and order/seed independent. Matches correction doc Sec 4 exactly.")

# =====================================================================
# ADVERSARIAL WITNESS SUITE (targeting the Finding-2 correction specifically)
# =====================================================================
line("=")
print("ADVERSARIAL WITNESSES (>=10), targeting: determinism, replay, state completeness,")
print("state exclusivity, selected_claim, contradiction_doc_ids, invariant I-3")
line("=")

# ---- A1: THE HEADLINE ATTACK -----------------------------------------
# selected_claim has an *unrelated*, same-origin (non-S1-qualifying) material
# contradiction against a decoy claim z4, while the REAL S1-firing pair is a
# totally separate, disjoint, cross-origin pair {x4,y4}. Comp is populated by
# the decoy alone (Comp's definition has NO independence/cross-origin filter),
# so the corrected rule takes the Comp branch and returns contradiction_doc_ids
# pointing at the decoy z4 -- NOT the actual S1 debate.
print("\n[A1] Decoy-Comp witness: same-origin decoy contradiction on selected_claim")
print("     co-occurring with a disjoint, unrelated, genuinely S1-firing pair.")
top4 = Claim("top4", "top4", [("a1", "a1_doc")])
z4 = Claim("z4", "z4", [("a1", "a1_doc2")])          # SAME origin a1 as top4
x4 = Claim("x4", "x4", [("b1", "b1_doc")])
y4 = Claim("y4", "y4", [("c1", "c1_doc")])
oracle_a1 = Oracle(contradicts_pairs=[("top4", "z4"), ("x4", "y4")])
claims_a1 = [top4, z4, x4, y4]

r_a1 = classify_post_finding2(oracle_a1, claims_a1)
show("A1", r_a1)
assert r_a1["state"] == "S1"
assert r_a1["selected_claim"] == "top4"
assert r_a1["branch"] == "Comp"
assert r_a1["comp_nonempty"] is True
assert r_a1["competing_claim"] == "z4"
assert r_a1["firing_pairs"] == [("x4", "y4")]
assert r_a1["selected_is_true_s1_participant"] is False
print("  firing_pairs (the actual S1 trigger):", r_a1["firing_pairs"])
print("  competing_claim returned            :", r_a1["competing_claim"], " (the DECOY, not the trigger pair)")
print("  selected_claim is a true S1 participant in ANY firing pair:",
      r_a1["selected_is_true_s1_participant"])
print("  ==> FALSIFIES the correction's own textual claim (Sec 3.1 / Sec 3.2 preamble):")
print("      'if Comp != empty (the S1-triggering contradiction involves selected_claim)'")
print("      Comp is non-empty here, but selected_claim (top4) participates in NO S1-firing pair.")
record("A1_decoy_comp", r_a1)

# ---- A2: Part tie-break with >=3 participants requiring tertiary key ----
print("\n[A2] Part tie-break: 4 S1-participants across two firing pairs, full")
print("     primary+secondary tie among two of them, tertiary claim_text decides.")
topB = Claim("topB", "topB", [("z9", "z9doc"), ("z8", "z8doc")])  # ios=2, wins selection outright
p1 = Claim("p1", "aaa_text", [("m1", "shared_doc")])
p2 = Claim("p2", "zzz_text", [("m1", "shared_doc")])  # identical evidence key AND ios to p1's *pair partner*? see below
q1 = Claim("q1", "q1", [("n1", "n1doc")])
q2 = Claim("q2", "q2", [("n2", "n2doc")])
# Note: p1/p2 cannot literally share the SAME evidence tuple across two distinct claims in this
# toy model without breaking ios() bookkeeping cleanliness, so instead give them distinct docs
# at the SAME (origin,doc) prefix collision point deliberately -- see A3 for the true full-tie
# (F2-class) attack. Here we construct a genuine, resolvable tie needing only the tertiary key.
p1 = Claim("p1", "aaa_text", [("m1", "shared_doc")])
p2 = Claim("p2", "zzz_text", [("m1", "shared_doc2")])
oracle_a2 = Oracle(contradicts_pairs=[("p1", "q1"), ("p2", "q2")])
claims_a2 = [topB, p1, q1, p2, q2]
r_a2 = classify_post_finding2(oracle_a2, claims_a2)
show("A2", r_a2)
assert r_a2["state"] == "S1"
assert r_a2["selected_claim"] == "topB"
assert r_a2["branch"] == "Part"
# Part = {p1,q1,p2,q2}; all ios=1; ranking: primary tie (all ios=1); secondary = min evidence key:
#   p1=(m1,shared_doc) p2=(m1,shared_doc2) q1=(n1,n1doc) q2=(n2,n2doc)
# p1's key < p2's key < q1's key < q2's key lexicographically -> p1 wins, no tertiary needed here.
assert r_a2["competing_claim"] == "p1"
record("A2_part_tiebreak", r_a2)
print("  Part =", sorted(x for pr in r_a2['firing_pairs'] for x in pr), " winner:", r_a2["competing_claim"])
print("  VERDICT: survives -- Part argmax resolves via the frozen A2 total order, same as Sigma-wide argmax.")

# ---- A3: Part inherits F2 (duplicate claim_text + duplicate minimal evidence key -> true tie) ----
print("\n[A3] Part full-tie (F2-class) attack: two S1-participants share IDENTICAL")
print("     claim_text AND identical minimal-evidence key -> argmax(Part) undefined.")
topC = Claim("topC", "topC", [("y9", "y9doc"), ("y8", "y8doc")])  # ios=2, wins selection
r1 = Claim("r1", "duplicate_text", [("k1", "same_doc_id")])
r2 = Claim("r2", "duplicate_text", [("k1", "same_doc_id")])  # identical text AND identical evidence key
s1c = Claim("s1c", "s1c", [("k2", "k2doc")])
oracle_a3 = Oracle(contradicts_pairs=[("r1", "s1c"), ("r2", "s1c")])
claims_a3 = [topC, r1, r2, s1c]
try:
    r_a3 = classify_post_finding2(oracle_a3, claims_a3)
    show("A3", r_a3)
    a3_status = "NO TIE DETECTED (unexpected)"
except TieError as e:
    a3_status = "TieError: %s" % e
    print("  A3 -> %s" % a3_status)
record("A3_part_full_tie", a3_status)
print("  VERDICT: CONDITIONAL FALSIFICATION -- extends the audit's pre-existing F2 (Sigma-wide")
print("  argmax non-uniqueness) to the NEW Part construct introduced by Finding 2. Same root cause")
print("  (unverified PA-2 claim_text-uniqueness assumption, addendum Sec A2), new attack surface.")

# ---- A4: Multiple disjoint firing pairs -- Part aggregates across ALL of them ----
print("\n[A4] Multiple disjoint firing pairs: verify Part is the union across ALL")
print("     S1-firing pairs, and argmax(Part) can pick a participant from any of them.")
topD = Claim("topD", "topD", [("w1", "w1doc"), ("w2", "w2doc"), ("w3", "w3doc")])  # ios=3
u1 = Claim("u1", "u1", [("f1", "f1doc")])
u2 = Claim("u2", "u2", [("f2", "f2doc")])
v1 = Claim("v1", "v1", [("g1", "g1doc")])
v2 = Claim("v2", "v2", [("g2", "g2doc")])
# make the SECOND pair {v1,v2} the strongest (best evidence key) even though it is NOT
# textually "first" -- verifies Part isn't accidentally scoped to only one firing pair.
oracle_a4 = Oracle(contradicts_pairs=[("u1", "u2"), ("v1", "v2")])
claims_a4 = [topD, u1, u2, v1, v2]
r_a4 = classify_post_finding2(oracle_a4, claims_a4)
show("A4", r_a4)
assert r_a4["state"] == "S1" and r_a4["branch"] == "Part"
assert set(r_a4["firing_pairs"]) == {("u1", "u2"), ("v1", "v2")}
# lexicographically: f1 < f2 < g1 < g2 -> u1 wins (lowest evidence key among all Part members)
assert r_a4["competing_claim"] == "u1"
record("A4_multi_pair_part", r_a4)
print("  firing_pairs:", r_a4["firing_pairs"], " Part winner:", r_a4["competing_claim"])
print("  VERDICT: survives -- Part correctly unions participants from ALL firing pairs, not just one.")

# ---- A5: Order-independence / shuffle test on the W2/A1 classes ----
print("\n[A5] Shuffle / claim-list-order independence, on W2 and on A1 (decoy) witnesses.")
random.seed(1234567)  # local determinism of the *test harness* only, not the classifier
perms_w2 = [claims_w2[:], list(reversed(claims_w2)), [x2, y2, top2]]
perms_a1 = [claims_a1[:], list(reversed(claims_a1)), [z4, x4, top4, y4], [y4, z4, x4, top4]]
w2_results = [classify_post_finding2(oracle_w2, p) for p in perms_w2]
a1_results = [classify_post_finding2(oracle_a1, p) for p in perms_a1]
assert all(r == w2_results[0] for r in w2_results)
assert all(r == a1_results[0] for r in a1_results)
record("A5_order_independence_w2", w2_results[0])
record("A5_order_independence_a1", a1_results[0])
print("  VERDICT: survives on both -- order-independent (as required by A1/A2 being pure")
print("  functions of Sigma content, not list position).")

# ---- A6: Seed replay specifically on the A1 decoy witness -----------
print("\n[A6] Seed-independence replay on the A1 decoy witness (is the WRONG answer at least")
print("     deterministic/replay-safe, or does it also break byte-identity across seeds?)")
seeds = [None, 0, 1, 42, 999999]
a1_seeded = [classify_post_finding2(oracle_a1, claims_a1, seed=s) for s in seeds]
assert all(r == a1_seeded[0] for r in a1_seeded)
record("A6_seed_replay_a1", a1_seeded[0])
print("  VERDICT: survives (replay-safe) -- the decoy result (z4) is WRONG relative to the")
print("  correction's own stated intent, but it is deterministically, reproducibly wrong.")
print("  This confirms A1 is a SEMANTIC/textual-claim defect, not a determinism/replay defect.")

# ---- A7: State exclusivity under the new Comp/Part machinery --------
print("\n[A7] State exclusivity attack: try to force S1 AND make the (S2|S3) ios-split")
print("     condition ALSO look satisfiable on the same input, now that Comp/Part exist.")
# Reuse A1's witness: does the presence of Comp/Part machinery open any path where the
# classifier could ALSO reach the (S2|S3) branch for the same input? Structurally impossible
# (elif cascade; Part/Comp are only ever computed INSIDE the already-fired S1 branch), verified
# by construction: classify_post_finding2 never evaluates the ios-split when firing_pairs is
# non-empty. Confirm empirically across every witness constructed so far.
all_witnesses = [
    (oracle_w0, claims_w0), (oracle_w2, claims_w2), (oracle_a1, claims_a1),
    (oracle_a2, claims_a2), (oracle_a4, claims_a4),
]
exclusivity_ok = True
for orc, cls in all_witnesses:
    r = classify_post_finding2(orc, cls)
    fp = s1_firing_pairs(orc, [c for c in cls if ios(c) >= 1])
    if fp and r["state"] != "S1":
        exclusivity_ok = False
    if (not fp) and r["state"] == "S1":
        exclusivity_ok = False
record("A7_state_exclusivity", exclusivity_ok)
print("  VERDICT:", "survives" if exclusivity_ok else "FALSIFIED", "-- elif-cascade structurally",
      "prevents any input from satisfying both S1's firing predicate and reaching the (S2|S3) branch.")

# ---- A8: selected_claim is NOT overwritten by the Part fallback -----
print("\n[A8] selected_claim integrity: confirm Part's argmax (a DIFFERENT total order")
print("     evaluation, scoped to Part not Sigma) never leaks into / replaces selected_claim.")
r_a1_check = classify_post_finding2(oracle_a1, claims_a1)
sigma_a1 = [c for c in claims_a1 if ios(c) >= 1]
true_sigma_argmax = argmax(sigma_a1).name
assert r_a1_check["selected_claim"] == true_sigma_argmax == "top4"
r_a4_check = classify_post_finding2(oracle_a4, claims_a4)
sigma_a4 = [c for c in claims_a4 if ios(c) >= 1]
assert r_a4_check["selected_claim"] == argmax(sigma_a4).name == "topD"
record("A8_selected_claim_integrity", True)
print("  VERDICT: survives -- selected_claim strictly equals Sigma-wide argmax in every witness;")
print("  Part's separate argmax computation (over a different, smaller set) never contaminates it.")

# ---- A9: Empty-Part impossibility attempt (attack the Sec 5.1 proof) ----
print("\n[A9] Attempt to construct an S1-firing input with an EMPTY Part (attacking the")
print("     correction's own Sec 5.1 totality proof: 'S1 fires ==> Part != empty').")
# By construction Part := union of all firing-pair members; if firing_pairs is non-empty,
# Part contains at least the 2 members of any one firing pair. Try adversarial constructions:
# (i) a firing pair where a==b (degenerate) -- forbidden by A4's own text ("distinct claims").
# (ii) a firing pair whose members happen to also be filtered out of Sigma -- impossible,
#      s1_pair_fires already operates only over Sigma members (ios>=1 required to be considered).
# Exhaustively confirmed over every witness above: Part is always non-empty whenever fires.
part_never_empty = True
for orc, cls in all_witnesses + [(oracle_a2, claims_a2), (oracle_a3, [topC, r1, s1c])]:
    sigma = [c for c in cls if ios(c) >= 1]
    fp = s1_firing_pairs(orc, sigma)
    if fp:
        part = set()
        for a, b in fp:
            part.add(a); part.add(b)
        if not part:
            part_never_empty = False
record("A9_part_never_empty", part_never_empty)
print("  VERDICT:", "survives" if part_never_empty else "FALSIFIED",
      "-- could not construct a firing input with empty Part; matches Sec 5.1's algebraic proof")
print("  (any pair satisfying A4 cond 1-3 is by definition 2 distinct Sigma members).")

# ---- A10: Derived invariant contradiction_doc_ids != () <=> state=S1, stress test ----
print("\n[A10] Derived invariant stress test: contradiction_doc_ids != () iff state == S1,")
print("      across every witness constructed (including decoy/Part/tie classes).")
inv_ok = True
for orc, cls in all_witnesses + [(oracle_a2, claims_a2)]:
    r = classify_post_finding2(orc, cls)
    has_contra = r["contradiction_doc_ids"] != ()
    is_s1 = (r["state"] == "S1")
    if has_contra != is_s1:
        inv_ok = False
record("A10_derived_invariant", inv_ok)
print("  VERDICT:", "survives" if inv_ok else "FALSIFIED",
      "-- derived invariant holds across all constructed witnesses, including the A1 decoy.")

# ---- A11: F0-lineage sanity: I-3 preamble literal biconditional check ----
print("\n[A11] I-3 restated preamble (Finding-2 correction Sec 3.2) literal biconditional check:")
print("      'contradiction_doc_ids computed wrt selected_claim WHEN selected_claim participates")
print("      in the S1-triggering contradiction (Comp != empty)' -- test Comp!=empty as a proxy")
print("      for true participation across ALL constructed S1 witnesses.")
mismatch_witnesses = []
for label, (orc, cls) in {
    "W2": (oracle_w2, claims_w2), "A1": (oracle_a1, claims_a1),
    "A2": (oracle_a2, claims_a2), "A4": (oracle_a4, claims_a4),
}.items():
    r = classify_post_finding2(orc, cls)
    if r["state"] != "S1":
        continue
    comp_nonempty = r["comp_nonempty"]
    true_participant = r["selected_is_true_s1_participant"]
    if comp_nonempty != true_participant:
        mismatch_witnesses.append((label, comp_nonempty, true_participant))
record("A11_i3_preamble_biconditional_mismatches", mismatch_witnesses)
print("  Mismatches (Comp!=empty  vs  selected_claim actually in a firing pair):", mismatch_witnesses)
print("  VERDICT:", "FALSIFIED" if mismatch_witnesses else "survives",
      "-- Comp!=empty does NOT imply selected_claim participates in the S1-triggering contradiction.")

line("=")
print("SUMMARY OF ALL RECORDED RESULTS")
line("=")
for k, v in results_log.items():
    print("%-40s %r" % (k, v))
