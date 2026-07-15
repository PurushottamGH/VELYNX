"""
INDEPENDENT replay of the three named witnesses (original / F1 / F2 / F3) plus a
freshly-constructed adversarial witness catalog, run against audit_f3_independent.py
(a from-scratch reference model, NOT the correction author's own scratch files).

Mission targets: contradiction_doc_ids correctness, selected_claim correctness,
determinism, replay, invariant I-3, state exclusivity, state completeness.
"""

import itertools, random
from audit_f3_independent import (
    Claim, Oracle, classify_f2, classify_f3, core, competing_is_participant,
    firing_pairs, ios, prec_max, TieError,
)

FAILS = []

def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print("[%s] %s %s" % (status, name, ("- " + detail) if detail and not cond else ""))
    if not cond:
        FAILS.append((name, detail))

print("="*100)
print("PART 1: REPLAY OF NAMED WITNESSES (independent reference)")
print("="*100)

# --- W0: original witness (Finding-1 correction sec4.1 style) ---
o = Oracle(contra=[("a","b")])
a = Claim("a","a",[("d1","doc1")]); b = Claim("b","b",[("d1","doc2")])
r2, r3 = classify_f2(o,[a,b]), classify_f3(o,[a,b])
print("W0 :", core(r2), core(r3))
check("W0 state=S2 both", r2["state"]=="S2"=="S2" and r3["state"]=="S2")
check("W0 F2==F3", core(r2)==core(r3))

# --- W2: Finding-1/Finding-2 witness (top2 ios=3, contradicts nothing; disjoint x2/y2 cross-origin) ---
top2 = Claim("top2","top2",[("d1","e1"),("d2","e2"),("d3","e3")])
x2 = Claim("x2","x2",[("d4","e4")]); y2 = Claim("y2","y2",[("d5","e5")])
o = Oracle(contra=[("x2","y2")])
claims = [top2,x2,y2]
r2, r3 = classify_f2(o,claims), classify_f3(o,claims)
print("W2 :", core(r2), core(r3))
check("W2 state=S1", r2["state"]==r3["state"]=="S1")
check("W2 selected=top2", r2["selected_claim"]==r3["selected_claim"]=="top2")
check("W2 branch=Part both", r2["branch"]==r3["branch"]=="Part")
check("W2 F2==F3 (unaffected)", core(r2)==core(r3))
check("W2 competing is true participant (F3)", competing_is_participant(o,claims,r3))

# --- A1: Finding-3 witness (decoy same-origin z4 on top4, disjoint real cross-origin x4/y4) ---
top4 = Claim("top4","top4",[("a1","a1_doc")])
z4 = Claim("z4","z4",[("a1","a1_doc2")])
x4 = Claim("x4","x4",[("b1","b1_doc")])
y4 = Claim("y4","y4",[("c1","c1_doc")])
o = Oracle(contra=[("top4","z4"),("x4","y4")])
claims = [top4,z4,x4,y4]
r2, r3 = classify_f2(o,claims), classify_f3(o,claims)
print("A1 : F2=", core(r2), "branch", r2["branch"], "competing", r2["competing"])
print("A1 : F3=", core(r3), "branch", r3["branch"], "competing", r3["competing"])
check("A1 F2 exhibits the decoy pathology", r2["branch"]=="Comp" and r2["competing"]=="z4")
check("A1 F3 takes Part fallback", r3["branch"]=="Part")
check("A1 F3 competing is true participant", competing_is_participant(o,claims,r3))
check("A1 F3 competing in {x4,y4}", r3["competing"] in ("x4","y4"))
check("A1 state/selected/support/ioc unchanged F2 vs F3",
      all(r2[k]==r3[k] for k in ["state","selected_claim","support","ioc"]))

print()
print("="*100)
print("PART 2: FRESH ADVERSARIAL WITNESSES (independently constructed, not from the author's suite)")
print("="*100)

# B1: TWO same-origin decoys on selected_claim (decoys share sel's OWN origin K0, so cond-3
# fails for {sel,dec1} and {sel,dec2} individually) + one disjoint genuine cross-origin pair.
sel = Claim("sel","sel",[("K0","a")])
dec1 = Claim("dec1","dec1",[("K0","b")])
dec2 = Claim("dec2","dec2",[("K0","c")])
gx = Claim("gx","gx",[("K2","a")])
gy = Claim("gy","gy",[("K3","a")])
o = Oracle(contra=[("sel","dec1"),("sel","dec2"),("gx","gy")])
claims = [sel,dec1,dec2,gx,gy]
r2, r3 = classify_f2(o,claims), classify_f3(o,claims)
print("B1 : F2=", core(r2), r2["branch"], r2["competing"], " F3=", core(r3), r3["branch"], r3["competing"])
check("B1 F2 pathological (Comp branch, non-participant decoy)",
      r2["branch"]=="Comp" and r2["competing"] in ("dec1","dec2"))
check("B1 F3 excludes both decoys -> Part fallback", r3["branch"]=="Part")
check("B1 F3 competing is true participant", competing_is_participant(o,claims,r3))

# B2: MIXED Comp -- selected_claim (the Sigma-wide winner) has BOTH a same-origin decoy AND a
# genuine cross-origin co-participant, both landing in F2's unfiltered Comp. This tests whether,
# even when selected_claim DOES truly participate in the S1-firing contradiction (so the I-3
# biconditional's TRUTH VALUE is correct under F2), the SPECIFIC emitted evidence can still be
# unfaithful because the decoy -- not the genuine partner -- wins the tie-break inside Comp.
# Keys: hub must have the globally-smallest evidence key (wins Sigma-wide selection); decoy
# shares hub's origin (H0) with a slightly larger key; genuine is cross-origin with the largest key.
hub = Claim("hub","hub",[("H0","a")])
decoy = Claim("decoy","decoy",[("H0","b")])          # same origin H0 as hub -> cond-3 fails
genuine = Claim("genuine","genuine",[("Z9","a")])     # cross-origin -> {hub,genuine} genuinely fires S1
o = Oracle(contra=[("hub","decoy"),("hub","genuine")])
claims = [hub, decoy, genuine]
r2, r3 = classify_f2(o,claims), classify_f3(o,claims)
print("B2 : F2=", core(r2), r2["branch"], r2["competing"], "sel_participates(F2 sense)=",
      any(("hub" in pair) for pair in r2["firing_pairs"]))
print("B2 : F3=", core(r3), r3["branch"], r3["competing"], "sel_participates=", r3["sel_participates"])
check("B2 selected_claim is hub (globally smallest key)", r2["selected_claim"]==r3["selected_claim"]=="hub")
check("B2 F2 Comp = {decoy, genuine}, tie-break picks decoy (smaller key H0<Z9) despite a genuine partner existing",
      r2["branch"]=="Comp" and r2["competing"]=="decoy")
check("B2 hub DOES truly participate (via genuine) even under F2's firing_pairs",
      any("hub" in pair for pair in r2["firing_pairs"]))
check("B2 F3 Comp correctly EXCLUDES decoy (cond-3 fails) and KEEPS genuine",
      r3["branch"]=="Comp" and r3["competing"]=="genuine")
check("B2 F3 competing is true participant", competing_is_participant(o,claims,r3))
check("B2 F2 emitted contradiction_doc_ids WAS unfaithful even though sel participates (subtler than A1)",
      r2["contradiction"] != r3["contradiction"])

# B3: algebraic-confinement stress -- ios(selected_claim) >= 2, attempt to construct a decoy
# that STILL sneaks into Comp without being a genuine participant. Per the doc's own proof
# (SS2 "Algebraic confinement"), this should be IMPOSSIBLE. Try to break it anyway.
selH = Claim("selH","selH",[("h1","e1"),("h2","e2")])  # ios=2, origins h1,h2
tryDecoy = Claim("tryDecoy","tryDecoy",[("h1","e3")])   # subset-overlaps origin h1 only
o = Oracle(contra=[("selH","tryDecoy")])
claims = [selH, tryDecoy]
r2, r3 = classify_f2(o,claims), classify_f3(o,claims)
print("B3 : F2=", core(r2), r2["branch"], " F3=", core(r3), r3.get("branch"))
# independent_origins(supp(selH) U supp(tryDecoy)) = |{h1,h2} U {h1}| = 2 >= 2 -> genuinely qualifies (not a decoy at all)
check("B3 confirms algebraic confinement: ios>=2 selected_claim cannot admit a non-qualifying Comp member",
      r3["branch"]=="Comp" and r3["competing"]=="tryDecoy" and competing_is_participant(o,claims,r3))

# B4: THREE disjoint firing pairs plus a decoy on selected_claim; Part must union ALL of them
# and pick the true SSA2-minimal winner, not just the first pair found. Origins prefixed A/B
# so selD's key ("A0",..) is unambiguously the Sigma-wide global minimum (guaranteeing selD IS
# selected_claim), and B1<B2<...<B6 fixes the Part-internal ordering unambiguously.
selD = Claim("selD","selD",[("A0","d0")])
decoyD = Claim("decoyD","decoyD",[("A0","d1")])   # same origin A0 as selD -> cond-3 fails, not S1-qualifying
p1a=Claim("p1a","p1a",[("B1","x")]); p1b=Claim("p1b","p1b",[("B2","x")])
p2a=Claim("p2a","p2a",[("B3","x")]); p2b=Claim("p2b","p2b",[("B4","x")])
p3a=Claim("p3a","p3a",[("B5","x")]); p3b=Claim("p3b","p3b",[("B6","x")])
o = Oracle(contra=[("selD","decoyD"),("p1a","p1b"),("p2a","p2b"),("p3a","p3b")])
claims=[selD,decoyD,p1a,p1b,p2a,p2b,p3a,p3b]
r2, r3 = classify_f2(o,claims), classify_f3(o,claims)
print("B4 : F2=", core(r2), r2["branch"], r2["competing"])
print("B4 : F3=", core(r3), r3["branch"], r3["competing"], "firing_pairs=", r3["firing_pairs"])
check("B4 selected_claim is selD (global minimal key)", r2["selected_claim"]==r3["selected_claim"]=="selD")
check("B4 F2 pathological: Comp={decoyD}, picks the non-participant decoy",
      r2["branch"]=="Comp" and r2["competing"]=="decoyD")
check("B4 F3 excludes decoyD, falls to Part, aggregates across all 3 disjoint pairs (winner=p1a, global min of Part)",
      r3["branch"]=="Part" and r3["competing"]=="p1a")
check("B4 competing is true participant", competing_is_participant(o,claims,r3))

# B5: order/seed independence (shuffle input list) on B2 (the subtler mixed-Comp witness) and B4.
random.seed(4242)
for trial in range(8):
    shuffled = claims[:]
    random.shuffle(shuffled)
    r3s = classify_f3(o, shuffled)
    check("B4 shuffle-stable trial %d" % trial, core(r3s)==core(r3) and r3s["branch"]==r3["branch"] and r3s["competing"]==r3["competing"])

claimsB2 = [hub, decoy, genuine]
oB2 = Oracle(contra=[("hub","decoy"),("hub","genuine")])
for trial in range(8):
    shuffled = claimsB2[:]
    random.shuffle(shuffled)
    r3s = classify_f3(oB2, shuffled)
    check("B2 shuffle-stable trial %d" % trial, r3s["branch"]=="Comp" and r3s["competing"]=="genuine")

# B6: I-3 biconditional direct attack -- construct a witness where selected_claim participates
# DIRECTLY (is one of the two claims in the actual S1-firing pair), confirm Comp reflects that
# and the biconditional (Comp!=empty <=> sel participates) holds both directions.
sd = Claim("sd","sd",[("n1","n1doc")])
partner = Claim("partner","partner",[("n2","n2doc")])
bystander = Claim("bystander","bystander",[("n3","n3doc")])  # contradicts nothing
o = Oracle(contra=[("sd","partner")])
claims=[sd,partner,bystander]
r3 = classify_f3(o,claims)
print("B6 :", core(r3), r3["branch"], r3["sel_participates"])
check("B6 selected_claim is sd (ios tie broken alphabetically: sd/partner/bystander all ios=1, n1<n2<n3)",
      r3["selected_claim"]=="sd")
check("B6 Comp nonempty and equals sel-participates=True (forward direction of I-3 biconditional)",
      r3["branch"]=="Comp" and r3["sel_participates"]==True and r3["competing"]=="partner")

# B7: reverse-direction I-3 attack -- construct MANY random witnesses and check the corrected
# biconditional Comp!=empty <=> sel_participates holds with ZERO exceptions (not just spot checks).
random.seed(13)
mismatches = 0
trials = 0
for _ in range(3000):
    n_peripherals = random.randint(0,4)
    sel_ios = random.choice([1,1,1,2,3])
    selc = Claim("SEL","SEL",[("SO%d"%i,"SD%d"%i) for i in range(sel_ios)])
    has_decoy = random.random() < 0.5
    decoyc = Claim("DEC","DEC", [("SO0","decdoc")] if has_decoy else [("DECORIGIN","decdoc")])
    peris = [Claim("PR%d"%i,"PR%d"%i,[("PO%d"%i,"PD%d"%i)]) for i in range(n_peripherals)]
    allc = [selc, decoyc] + peris
    contra = []
    if random.random() < 0.7:
        contra.append(("SEL","DEC"))
    names = [p.name for p in peris]
    for a,b in itertools.combinations(names,2):
        if random.random() < 0.3:
            contra.append((a,b))
    # also sometimes let SEL genuinely contradict a peripheral (cross-origin), to test the forward direction too
    if peris and random.random() < 0.3:
        contra.append(("SEL", peris[0].name))
    o = Oracle(contra=contra)
    try:
        r3 = classify_f3(o, allc)
    except TieError:
        continue
    trials += 1
    if r3["state"] != "S1":
        continue
    comp_nonempty = (r3["branch"] == "Comp")
    if comp_nonempty != r3["sel_participates"]:
        mismatches += 1
print("B7 : trials=%d, I-3 biconditional mismatches under F3 = %d (must be 0)" % (trials, mismatches))
check("B7 I-3 biconditional holds with zero mismatches over 3000 random trials", mismatches==0)

# B8: state exclusivity/completeness stress -- boundary cases: empty claims, all-zero-ios claims,
# ios=1/ios=2 boundary co-occurring with a Comp decoy, verify state always exactly one of S0..S3
# and Comp/Part edits never move an input across a state boundary vs F2.
def rand_witness(seed):
    random.seed(seed)
    n = random.randint(0,6)
    cs = []
    for i in range(n):
        # sometimes give zero evidence (excluded from Sigma) to stress the S0/Sigma boundary
        if random.random() < 0.15:
            cs.append(Claim("Z%d"%i,"Z%d"%i, []))
        else:
            k = random.randint(1,3)
            cs.append(Claim("C%d"%i,"C%d"%i, [("OR%d_%d"%(i,j),"D%d_%d"%(i,j)) for j in range(k)]))
    names = [c.name for c in cs]
    contra = []
    for a,b in itertools.combinations(names,2):
        if random.random() < 0.25:
            contra.append((a,b))
    return Oracle(contra=contra), cs

state_mismatches = 0
exclusivity_violations = 0
boundary_trials = 0
for s in range(2000):
    o, cs = rand_witness(s)
    try:
        r2 = classify_f2(o, cs); r3 = classify_f3(o, cs)
    except TieError:
        continue
    boundary_trials += 1
    if r2["state"] != r3["state"]:
        state_mismatches += 1
    if r3["state"] not in ("S0","S1","S2","S3"):
        exclusivity_violations += 1
print("B8 : boundary_trials=%d, F2 vs F3 state-label mismatches=%d (must be 0), invalid state labels=%d (must be 0)"
      % (boundary_trials, state_mismatches, exclusivity_violations))
check("B8 state boundary identical between F2 and F3 across 2000 random inputs", state_mismatches==0)
check("B8 every input lands in exactly one of S0/S1/S2/S3", exclusivity_violations==0)

# B9: selected_claim correctness -- confirm selected_claim is NEVER altered by the F3 edit,
# across the same 2000-trial sweep (Finding 3 must only ever touch contradiction_doc_ids).
sel_mismatches = 0
support_mismatches = 0
ioc_mismatches = 0
for s in range(2000):
    o, cs = rand_witness(s)
    try:
        r2 = classify_f2(o, cs); r3 = classify_f3(o, cs)
    except TieError:
        continue
    if r2["selected_claim"] != r3["selected_claim"]:
        sel_mismatches += 1
    if r2["support"] != r3["support"]:
        support_mismatches += 1
    if r2["ioc"] != r3["ioc"]:
        ioc_mismatches += 1
print("B9 : selected_claim mismatches=%d, support mismatches=%d, ioc mismatches=%d (all must be 0)"
      % (sel_mismatches, support_mismatches, ioc_mismatches))
check("B9 selected_claim never altered by F3", sel_mismatches==0)
check("B9 support_doc_ids never altered by F3", support_mismatches==0)
check("B9 independent_origin_count never altered by F3", ioc_mismatches==0)

# B10: determinism/replay -- re-run the FULL 2000-trial sweep with different "seed" values
# threaded through classify (there is no seed parameter in this from-scratch model by design --
# frozen contract says seed must be UNUSED -- so instead we verify by re-shuffling each witness's
# claim list and re-running; any divergence would indicate hidden order-dependence).
divergences = 0
redo_trials = 0
for s in range(500):
    o, cs = rand_witness(s)
    try:
        r3a = classify_f3(o, cs)
    except TieError:
        continue
    shuffled = cs[:]
    random.Random(s+99999).shuffle(shuffled)
    try:
        r3b = classify_f3(o, shuffled)
    except TieError:
        continue
    redo_trials += 1
    if core(r3a) != core(r3b):
        divergences += 1
print("B10: redo_trials=%d, shuffle-order divergences=%d (must be 0)" % (redo_trials, divergences))
check("B10 determinism/order-independence holds under F3", divergences==0)

print()
print("="*100)
if FAILS:
    print("OVERALL: %d CHECK(S) FAILED:" % len(FAILS))
    for f in FAILS:
        print("  -", f)
else:
    print("OVERALL: ALL INDEPENDENT CHECKS PASSED")
print("="*100)
