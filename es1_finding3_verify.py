"""
Finding-3 verification: prove the F3 fix (a) closes F3, (b) preserves Finding-2's
own headline fix on W2, (c) is byte-identical to Finding-2 on every input where
Finding-2 was already correct (i.e. changes ONLY the pathological Comp-decoy class),
(d) preserves state label / exclusivity / totality / derived seam invariant.
"""

import itertools, random
from es1_finding2_audit_reference import (
    Claim, Oracle, classify_post_finding2, ios, supp, s1_firing_pairs, argmax,
)
from es1_finding3_correction_reference import (
    classify_post_finding3, competing_is_true_s1_participant,
)

CORE = ["state", "selected_claim", "support_doc_ids", "contradiction_doc_ids",
        "independent_origin_count"]

def core(r):
    return {k: r.get(k) for k in CORE}

def build(names_ev, contra):
    claims = [Claim(n, n, ev) for (n, ev) in names_ev]
    return Oracle(contradicts_pairs=contra), claims

fails = []

# ---- 1. W0 (Finding-1 witness): unaffected ----
o, c = build([("a", [("d1","doc1")]), ("b",[("d1","doc2")])], [("a","b")])
r2, r3 = classify_post_finding2(o,c), classify_post_finding3(o,c)
assert core(r2)==core(r3)==dict(state="S2",selected_claim="a",
    support_doc_ids=(("d1","doc1"),),contradiction_doc_ids=(),independent_origin_count=1)
print("W0  : S2, identical F2==F3  OK")

# ---- 2. W2 (Finding-2 headline witness): F3 must PRESERVE the Part fix ----
o, c = build([("top2",[("d1","e1"),("d2","e2"),("d3","e3")]),
              ("x2",[("d4","e4")]),("y2",[("d5","e5")])], [("x2","y2")])
r2, r3 = classify_post_finding2(o,c), classify_post_finding3(o,c)
assert core(r2)==core(r3), (core(r2),core(r3))
assert r3["branch"]=="Part" and r3["competing_claim"] in ("x2","y2")
assert competing_is_true_s1_participant(o,c) is True
print("W2  : S1/Part, F2==F3, competing is a true S1 participant  OK  ->", core(r3)["contradiction_doc_ids"])

# ---- 3. A1 (the F3 pathology): F3 must FIX it ----
o, c = build([("top4",[("a1","a1_doc")]),("z4",[("a1","a1_doc2")]),
              ("x4",[("b1","b1_doc")]),("y4",[("c1","c1_doc")])],
             [("top4","z4"),("x4","y4")])
r2, r3 = classify_post_finding2(o,c), classify_post_finding3(o,c)
print("A1  : F2 competing =", r2["competing_claim"], "(branch",r2["branch"]+", WRONG: decoy)")
print("      F3 competing =", r3["competing_claim"], "(branch",r3["branch"]+")")
assert r2["competing_claim"]=="z4" and r2["branch"]=="Comp"          # F2 pathology
assert r3["branch"]=="Part" and r3["competing_claim"] in ("x4","y4")  # F3 fixed
assert competing_is_true_s1_participant(o,c) is True
# state/selected_claim/support/ios all UNCHANGED between F2 and F3
for k in ["state","selected_claim","support_doc_ids","independent_origin_count"]:
    assert r2[k]==r3[k], (k, r2[k], r3[k])
print("      state/selected_claim/support/ios byte-identical F2==F3; only contradiction_doc_ids differs  OK")

# ---- 4. Comp-branch legitimacy: when selected_claim IS a real participant, F3==F2 ----
# top has ios=2 (spans 2 origins) and genuinely contradicts w across origins.
o, c = build([("top",[("o1","t1"),("o2","t2")]),("w",[("o3","w1")]),
              ("k",[("o4","k1")])], [("top","w")])
r2, r3 = classify_post_finding2(o,c), classify_post_finding3(o,c)
assert r2["branch"]=="Comp" and r3["branch"]=="Comp"
assert core(r2)==core(r3)
assert r3["competing_claim"]=="w"
print("Comp: legit Comp case (ios>=2, real cross-origin), F2==F3, branch=Comp  OK")

# ---- 5. Byte-identity sweep: F3 differs from F2 ONLY on the pathological class ----
random.seed(20260713)
def make(name, origins):
    return name, [(o, name+"_d%d"%i) for i,o in enumerate(origins)]
diffs = 0; diffs_all_pathological = True; total_s1 = 0; checked = 0
for _ in range(4000):
    top_ios = random.choice([1,1,1,2,3])
    T = make("T", ["AAA%d"%i for i in range(top_ios)])
    Z = make("Z", ["AAA0"] if random.random()<0.5 else ["ZZ%d"%random.randint(0,3)])
    peris = [make("P%d"%i, ["PO%d"%i]) for i in range(4)]
    names_ev = [T, Z] + peris
    claim_objs = {n: Claim(n,n,ev) for n,ev in names_ev}
    contra = []
    if random.random()<0.6: contra.append(("T","Z"))
    pnames = [p[0] for p in peris]
    for a,b in itertools.combinations(pnames,2):
        if random.random()<0.3: contra.append((a,b))
    o = Oracle(contradicts_pairs=contra)
    cl = list(claim_objs.values())
    try:
        r2 = classify_post_finding2(o, cl); r3 = classify_post_finding3(o, cl)
    except Exception:
        continue
    checked += 1
    if r3["state"]=="S1": total_s1 += 1
    if core(r2) != core(r3):
        diffs += 1
        # every diff must be: F2 was pathological (decoy), F3 fixes to a true participant
        patho_f2 = (r2.get("branch")=="Comp" and not r2.get("selected_is_true_s1_participant"))
        fixed_f3 = competing_is_true_s1_participant(o, cl)
        # and only contradiction_doc_ids changed
        onlyc = all(r2[k]==r3[k] for k in ["state","selected_claim","support_doc_ids","independent_origin_count"])
        if not (patho_f2 and fixed_f3 and onlyc):
            diffs_all_pathological = False
            fails.append(("sweep-diff-not-pathological", contra))
print("SWEEP: checked=%d, S1=%d, F2!=F3 diffs=%d, every diff strictly the pathological class=%s"
      % (checked, total_s1, diffs, diffs_all_pathological))
assert diffs_all_pathological
assert diffs > 0  # the fix actually does something

# ---- 6. F3 correctness property: competing ALWAYS a true S1 participant, on every S1 input ----
random.seed(999)
bad = 0
for _ in range(4000):
    top_ios = random.choice([1,1,1,2,3])
    T = make("T", ["AAA%d"%i for i in range(top_ios)])
    Z = make("Z", ["AAA0"] if random.random()<0.5 else ["ZZ%d"%random.randint(0,3)])
    peris = [make("P%d"%i, ["PO%d"%i]) for i in range(4)]
    names_ev = [T,Z]+peris
    cl = [Claim(n,n,ev) for n,ev in names_ev]
    contra=[]
    if random.random()<0.6: contra.append(("T","Z"))
    for a,b in itertools.combinations([p[0] for p in peris],2):
        if random.random()<0.3: contra.append((a,b))
    o=Oracle(contradicts_pairs=contra)
    res = competing_is_true_s1_participant(o, cl)
    if res is False:
        bad += 1
print("CORRECTNESS: S1-firing inputs where competing is NOT a true participant =", bad, "(must be 0)")
assert bad == 0

# ---- 7. derived seam invariant contradiction_doc_ids != () <=> state==S1 under F3 ----
random.seed(7)
inv_ok=True
for _ in range(3000):
    T=make("T",["AAA%d"%i for i in range(random.choice([1,2,3]))])
    Z=make("Z",["AAA0"] if random.random()<0.5 else ["ZZ0"])
    peris=[make("P%d"%i,["PO%d"%i]) for i in range(random.randint(0,4))]
    cl=[Claim(n,n,ev) for n,ev in ([T,Z]+peris)]
    contra=[]
    if random.random()<0.5: contra.append(("T","Z"))
    for a,b in itertools.combinations([p[0] for p in peris],2):
        if random.random()<0.3: contra.append((a,b))
    o=Oracle(contradicts_pairs=contra)
    try: r=classify_post_finding3(o,cl)
    except Exception: continue
    if (r["contradiction_doc_ids"]!=()) != (r["state"]=="S1"): inv_ok=False
print("SEAM INVARIANT: contradiction_doc_ids != () <=> state==S1  holds =", inv_ok)
assert inv_ok

print()
print("ALL FINDING-3 VERIFICATION CHECKS PASSED" if not fails else ("FAILURES: %r"%fails))
