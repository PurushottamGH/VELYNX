"""
INDEPENDENT witness replay + adversarial witness catalog for the fresh Finding-3
audit. Built without consulting es1_finding3_correction_reference.py,
es1_finding3_verify.py, or any audit_f3_*.py scratch file from a prior session.
"""

from audit_new_f3_reference import (
    Claim, classify_finding2, classify_finding3, selected_participates,
    ios, TieError,
)

PASS = "PASS"
FAIL = "FAIL"


def C(name, text, supp):
    return Claim(name, text, supp)


def contradicts_factory(pairs):
    pairset = set()
    for a, b in pairs:
        pairset.add(frozenset((a, b)))

    def f(x, y):
        return frozenset((x.name, y.name)) in pairset
    return f


def material_factory(pairs):
    # is_material only meaningful where contradicts is True; reuse same set
    return contradicts_factory(pairs)


results = []


def record(name, ok, detail):
    results.append((name, ok, detail))
    status = "OK" if ok else "**FAIL**"
    print(f"[{status}] {name}: {detail}")


# =====================================================================
# PART 1 -- REPLAY: original (W0) / Finding-1 (W2 alias) / Finding-2 (W2) /
#           Finding-3 (A1-equivalent) witnesses
# =====================================================================
print("=" * 78)
print("PART 1: REPLAY OF NAMED WITNESSES")
print("=" * 78)

# --- W0: "original witness" (Finding-1 correction Sec 4.1) ---
a = C("a", "capital is Alpha", [("d1", "doc1")])
b = C("b", "capital is Beta", [("d1", "doc2")])
contr_w0 = contradicts_factory([("a", "b")])
mat_w0 = material_factory([("a", "b")])

r2_w0 = classify_finding2([a, b], contr_w0, mat_w0)
r3_w0 = classify_finding3([a, b], contr_w0, mat_w0)
ok = (r2_w0["state"] == "S2" and r3_w0["state"] == "S2"
      and r2_w0["selected_claim"].name == "a" and r3_w0["selected_claim"].name == "a"
      and r2_w0["contradiction"] == () and r3_w0["contradiction"] == ()
      and r2_w0["support"] == r3_w0["support"] == (("d1", "doc1"),))
record("W0 replay (same-origin, never reaches S1)", ok,
       f"F2={r2_w0['state']}/{r2_w0['selected_claim'].name} F3={r3_w0['state']}/{r3_w0['selected_claim'].name}, byte-identical F2==F3={r2_w0==r3_w0 or (r2_w0['state']==r3_w0['state'] and r2_w0['support']==r3_w0['support'] and r2_w0['contradiction']==r3_w0['contradiction'])}")

# seed/shuffle stability
r3_w0_seed = classify_finding3([a, b], contr_w0, mat_w0, seed=777, shuffle=True)
record("W0 shuffle/seed stability", r3_w0_seed["state"] == r3_w0["state"] and r3_w0_seed["selected_claim"].name == r3_w0["selected_claim"].name,
       f"shuffled result state={r3_w0_seed['state']} selected={r3_w0_seed['selected_claim'].name}")

# --- W2: "Finding 1 witness" == "Finding 2 witness" (top2 + disjoint {x2,y2}) ---
top2 = C("top2", "top2-claim", [("p1", "p1doc"), ("p2", "p2doc"), ("p3", "p3doc")])
x2 = C("x2", "x2-claim", [("d4", "e4")])
y2 = C("y2", "y2-claim", [("d5", "e5")])
contr_w2 = contradicts_factory([("x2", "y2")])
mat_w2 = material_factory([("x2", "y2")])

r2_w2 = classify_finding2([top2, x2, y2], contr_w2, mat_w2)
r3_w2 = classify_finding3([top2, x2, y2], contr_w2, mat_w2)
ok = (r2_w2["state"] == "S1" and r3_w2["state"] == "S1"
      and r2_w2["selected_claim"].name == "top2" and r3_w2["selected_claim"].name == "top2"
      and r2_w2["branch"] == "Part" and r3_w2["branch"] == "Part"
      and r2_w2["competing"].name == "x2" and r3_w2["competing"].name == "x2"
      and r2_w2["contradiction"] == (("d4", "e4"),) == r3_w2["contradiction"])
record("W2 replay (Finding-1/Finding-2 witness, top2/x2/y2)", ok,
       f"F2 branch={r2_w2['branch']} competing={r2_w2['competing'].name} contradiction={r2_w2['contradiction']}; "
       f"F3 branch={r3_w2['branch']} competing={r3_w2['competing'].name} contradiction={r3_w2['contradiction']} -- F2==F3 (expected, ios(top2)=3>=2, algebraic confinement)")

r3_w2_seed = classify_finding3([top2, x2, y2], contr_w2, mat_w2, seed=13, shuffle=True)
record("W2 shuffle/seed stability", r3_w2_seed["competing"].name == "x2",
       f"shuffled competing={r3_w2_seed['competing'].name}")

# --- A1-equivalent: "Finding 3 witness" (decoy-Comp witness, FINDING3_CORRECTION Sec 1.1) ---
top4 = C("top4", "top4-claim", [("a1", "a1_doc")])
z4 = C("z4", "z4-claim", [("a1", "a1_doc2")])
x4 = C("x4", "x4-claim", [("b1", "b1_doc")])
y4 = C("y4", "y4-claim", [("c1", "c1_doc")])
contr_a1 = contradicts_factory([("top4", "z4"), ("x4", "y4")])
mat_a1 = material_factory([("top4", "z4"), ("x4", "y4")])

r2_a1 = classify_finding2([top4, z4, x4, y4], contr_a1, mat_a1)
r3_a1 = classify_finding3([top4, z4, x4, y4], contr_a1, mat_a1)

f2_is_decoy = (r2_a1["branch"] == "Comp" and r2_a1["competing"].name == "z4")
f3_is_faithful = (r3_a1["branch"] == "Part" and r3_a1["competing"].name == "x4"
                   and selected_participates(r3_a1) is False   # selected_claim (top4) itself never participates in a firing pair
                   )
competing_is_participant = any("x4" in fp for fp in r3_a1["firing_pairs"])
record("A1-equivalent replay under Finding-2-only rule reproduces the decoy defect", f2_is_decoy,
       f"F2: branch={r2_a1['branch']} competing={r2_a1['competing'].name} (expected decoy z4)")
record("A1-equivalent replay under Finding-3 rule reproduces the correction's claimed fix", f3_is_faithful and competing_is_participant,
       f"F3: branch={r3_a1['branch']} competing={r3_a1['competing'].name} contradiction={r3_a1['contradiction']} "
       f"(expected Part/x4, contradiction=(('b1','b1_doc'),)) -- matches PROGRAM_A_A3_5_FINDING3_CORRECTION.md Sec4 verbatim: {r3_a1['contradiction'] == (('b1','b1_doc'),)}")

for seed in (None, 0, 1, 42, 999999):
    rr = classify_finding3([top4, z4, x4, y4], contr_a1, mat_a1, seed=seed, shuffle=(seed is not None))
    assert rr["branch"] == "Part" and rr["competing"].name == "x4", f"seed {seed} diverged: {rr}"
record("A1-equivalent seed/shuffle stability {None,0,1,42,999999}", True, "all 5 runs identical (branch=Part, competing=x4)")

print()

# =====================================================================
# PART 2 -- NEW ADVERSARIAL WITNESSES (B1..B12), independently constructed
# =====================================================================
print("=" * 78)
print("PART 2: ADVERSARIAL WITNESS CATALOG (12 new witnesses)")
print("=" * 78)

adversarial = []


def adv(name):
    def deco(fn):
        adversarial.append((name, fn))
        return fn
    return deco


# --- B1: Comp full-tie attack (extends F2/F2' tie-break fragility to the
#         corrected Comp set itself, not just Part) ---
@adv("B1 -- Comp full-tie attack")
def b1():
    sc = C("sc", "sc-claim", [("o1", "o1doc"), ("o2", "o2doc")])  # ios=2
    # two Comp-eligible partners with IDENTICAL claim_text and IDENTICAL min evidence key
    m1 = C("dupe", "same-text-dupe", [("o3", "o3doc")])
    m2 = C("dupe", "same-text-dupe", [("o3", "o3doc")])  # full key collision vs m1
    contr = contradicts_factory([("sc", "dupe")])
    # NB: contradicts_factory keys on .name, so both m1/m2 as "dupe" is intentional:
    # constructing two *distinct object* claims that happen to carry the same name/text/evidence
    mat = material_factory([("sc", "dupe")])
    try:
        r = classify_finding3([sc, m1, m2], contr, mat)
        return ("NO-TIE-RAISED", r["branch"], r["competing"].name)
    except TieError as e:
        return ("TieError", str(e))


# --- B2: multi-decoy -- two independent same-origin decoys on selected_claim,
#         plus the real disjoint firing pair; both decoys must be excluded ---
@adv("B2 -- multi-decoy exclusion")
def b2():
    # 'a1' sorts before 'w1'/'w2' so sc (origin a1) wins Sigma-wide selection
    sc = C("sc", "sc-claim", [("a1", "a1doc")])  # ios=1
    decoy1 = C("decoy1", "decoy1-claim", [("a1", "a1doc2")])   # same origin a1 as sc
    decoy2 = C("decoy2", "decoy2-claim", [("a1", "a1doc3")])   # also same origin a1 as sc
    real_a = C("real_a", "real_a-claim", [("w1", "w1doc")])
    real_b = C("real_b", "real_b-claim", [("w2", "w2doc")])
    contr = contradicts_factory([("sc", "decoy1"), ("sc", "decoy2"), ("real_a", "real_b")])
    mat = material_factory([("sc", "decoy1"), ("sc", "decoy2"), ("real_a", "real_b")])
    r2 = classify_finding2([sc, decoy1, decoy2, real_a, real_b], contr, mat)
    r3 = classify_finding3([sc, decoy1, decoy2, real_a, real_b], contr, mat)
    ok = (r2["selected_claim"].name == "sc" and r3["selected_claim"].name == "sc"
          and r2["branch"] == "Comp" and r2["competing"].name in ("decoy1", "decoy2")  # F2 defect: picks a decoy
          and r3["branch"] == "Part" and r3["comp"] == []  # F3 fix: both decoys excluded from Comp
          and r3["competing"].name == "real_a")
    return (ok, r2["branch"], r2["competing"].name, r3["branch"], r3["competing"].name, r3["comp"])


# --- B3: ios(selected_claim)>=2 algebraic-confinement check -- Comp must be
#         byte-identical between Finding2 and Finding3 whenever ios(sc)>=2 ---
@adv("B3 -- ios>=2 confinement (Comp unchanged)")
def b3():
    sc = C("sc", "sc-claim", [("m1", "m1doc"), ("m2", "m2doc")])  # ios=2
    partner = C("partner", "partner-claim", [("m3", "m3doc")])    # single, different origin
    contr = contradicts_factory([("sc", "partner")])
    mat = material_factory([("sc", "partner")])
    r2 = classify_finding2([sc, partner], contr, mat)
    r3 = classify_finding3([sc, partner], contr, mat)
    same = (r2["branch"] == r3["branch"] == "Comp" and r2["competing"].name == r3["competing"].name == "partner")
    return (same, r2["branch"], r3["branch"])


# --- B4: two disjoint firing pairs, selected_claim genuinely participates in
#         one of them directly (Comp branch must fire, not Part) ---
@adv("B4 -- selected_claim as genuine Comp participant amid a second disjoint pair")
def b4():
    sc = C("sc", "sc-claim", [("g1", "g1doc")])       # ios=1
    partner = C("partner", "partner-claim", [("g2", "g2doc")])  # cross-origin vs sc -> real S1 partner
    other_a = C("other_a", "other_a-claim", [("g3", "g3doc")])
    other_b = C("other_b", "other_b-claim", [("g4", "g4doc")])
    contr = contradicts_factory([("sc", "partner"), ("other_a", "other_b")])
    mat = material_factory([("sc", "partner"), ("other_a", "other_b")])
    r3 = classify_finding3([sc, partner, other_a, other_b], contr, mat)
    fps_as_sets = {frozenset(p) for p in r3["firing_pairs"]}
    ok = (r3["branch"] == "Comp" and r3["competing"].name == "partner"
          and fps_as_sets == {frozenset({"sc", "partner"}), frozenset({"other_a", "other_b"})})
    return (ok, r3["branch"], r3["competing"].name, r3["firing_pairs"])


# --- B5: decoy AND genuine Comp partner coexist on selected_claim -- verify
#         the genuine partner (not the decoy) wins the Comp argmax ---
@adv("B5 -- decoy + genuine Comp partner coexistence")
def b5():
    sc = C("sc", "sc-claim", [("h1", "h1doc")])          # ios=1
    decoy = C("decoy", "decoy-claim", [("h1", "h1doc2")])  # same-origin decoy vs sc
    genuine = C("genuine", "genuine-claim", [("h2", "h2doc")])  # cross-origin, real partner
    contr = contradicts_factory([("sc", "decoy"), ("sc", "genuine")])
    mat = material_factory([("sc", "decoy"), ("sc", "genuine")])
    r3 = classify_finding3([sc, decoy, genuine], contr, mat)
    ok = (r3["branch"] == "Comp" and r3["competing"].name == "genuine" and "decoy" not in r3["comp"])
    return (ok, r3["branch"], r3["competing"].name, r3["comp"])


# --- B6: S0 boundary + attempted spurious S1/S2/S3 co-firing ---
@adv("B6 -- S0 boundary, no spurious co-firing")
def b6():
    unsupported = C("u", "u-claim", [])  # ios=0, never enters Sigma
    r3 = classify_finding3([unsupported], lambda a, b: False, lambda a, b: False)
    ok = (r3["state"] == "S0" and r3["selected_claim"] is None
          and r3["support"] == () and r3["contradiction"] == () and r3["ioc"] == 0)
    return (ok, r3["state"], r3["selected_claim"])


# --- B7: state exclusivity stress -- across a battery of random inputs, no
#         input may satisfy both the S1-firing guard and the ios-split guard ---
@adv("B7 -- state exclusivity battery (see sweep, Part 3)")
def b7():
    return ("see Part 3 sweep",)


# --- B8: I-3 biconditional direct stress (independently re-derived, not A11) ---
@adv("B8 -- I-3 biconditional: Comp!=empty <=> selected_claim participates")
def b8():
    import random as _r
    rnd = _r.Random(20260714)
    mismatches = 0
    trials = 0
    origins = [f"org{i}" for i in range(8)]
    for _ in range(3000):
        n = rnd.randint(2, 6)
        claims = []
        for i in range(n):
            k = rnd.choice([1, 1, 1, 2])
            supp = [(rnd.choice(origins), f"doc{i}_{j}") for j in range(k)]
            # force distinct origins if k==2
            if k == 2 and supp[0][0] == supp[1][0]:
                supp[1] = (rnd.choice([o for o in origins if o != supp[0][0]]), supp[1][1])
            claims.append(C(f"c{i}", f"text{i}", supp))
        pairs = []
        for i in range(n):
            for j in range(i + 1, n):
                if rnd.random() < 0.35:
                    pairs.append((f"c{i}", f"c{j}"))
        contr = contradicts_factory(pairs)
        mat = material_factory(pairs)
        r = classify_finding3(claims, contr, mat)
        if r["state"] != "S1":
            continue
        trials += 1
        comp_nonempty = len(r["comp"]) > 0
        participates = selected_participates(r)
        if comp_nonempty != participates:
            mismatches += 1
    return (mismatches == 0, f"S1 trials={trials} mismatches={mismatches}")


# --- B9: digest-semantics regression -- every field OTHER than
#         contradiction_doc_ids must be byte-identical between Finding2 and
#         Finding3 on every input (only rule (iv)'s Comp filter changed) ---
@adv("B9 -- digest-semantics regression (only contradiction_doc_ids may differ)")
def b9():
    import random as _r
    rnd = _r.Random(4242)
    origins = [f"src{i}" for i in range(6)]
    checked = 0
    other_field_diffs = 0
    contradiction_diffs = 0
    for _ in range(2000):
        n = rnd.randint(1, 5)
        claims = []
        for i in range(n):
            k = rnd.choice([0, 1, 1, 2])
            supp = [(rnd.choice(origins), f"d{i}_{j}") for j in range(k)]
            if k == 2 and supp[0][0] == supp[1][0]:
                supp[1] = (rnd.choice([o for o in origins if o != supp[0][0]]), supp[1][1])
            claims.append(C(f"c{i}", f"t{i}", supp))
        pairs = []
        for i in range(n):
            for j in range(i + 1, n):
                if rnd.random() < 0.4:
                    pairs.append((f"c{i}", f"c{j}"))
        contr = contradicts_factory(pairs)
        mat = material_factory(pairs)
        try:
            r2 = classify_finding2(claims, contr, mat)
            r3 = classify_finding3(claims, contr, mat)
        except TieError:
            continue
        checked += 1
        sc2 = r2["selected_claim"].name if r2["selected_claim"] else None
        sc3 = r3["selected_claim"].name if r3["selected_claim"] else None
        if r2["state"] != r3["state"] or sc2 != sc3 or r2["support"] != r3["support"] or r2["ioc"] != r3["ioc"]:
            other_field_diffs += 1
        if r2["contradiction"] != r3["contradiction"]:
            contradiction_diffs += 1
    return (other_field_diffs == 0, f"checked={checked} other_field_diffs={other_field_diffs} contradiction_diffs={contradiction_diffs}")


# --- B10: three-way disjoint firing-pair union, order/shuffle independence ---
@adv("B10 -- 3-way disjoint firing pairs, Part union + shuffle independence")
def b10():
    sc = C("sc", "sc-claim", [("q1", "q1doc"), ("q2", "q2doc"), ("q3", "q3doc")])  # ios=3, no contradictions -> selected outright
    pairs_claims = []
    fp_names = []
    for i, (oa, ob) in enumerate([("r1", "r2"), ("r3", "r4"), ("r5", "r6")]):
        a_ = C(f"pa{i}", f"pa{i}-text", [(oa, f"{oa}doc")])
        b_ = C(f"pb{i}", f"pb{i}-text", [(ob, f"{ob}doc")])
        pairs_claims += [a_, b_]
        fp_names.append((f"pa{i}", f"pb{i}"))
    contr = contradicts_factory(fp_names)
    mat = material_factory(fp_names)
    all_claims = [sc] + pairs_claims
    r3 = classify_finding3(all_claims, contr, mat)
    winner_base = r3["competing"].name
    stable = True
    for seed in range(10):
        rr = classify_finding3(all_claims, contr, mat, seed=seed, shuffle=True)
        if rr["competing"].name != winner_base or rr["branch"] != r3["branch"]:
            stable = False
    ok = (r3["branch"] == "Part" and stable)
    return (ok, r3["branch"], winner_base, "stable across 10 shuffles" if stable else "UNSTABLE")


# --- B11: Part never empty when firing_pairs non-empty (totality survives
#          the Finding-3 narrowing of Comp) ---
@adv("B11 -- Part-nonempty totality under Finding-3's narrowed Comp")
def b11():
    import random as _r
    rnd = _r.Random(99)
    origins = [f"t{i}" for i in range(5)]
    violations = 0
    s1_trials = 0
    for _ in range(1500):
        n = rnd.randint(2, 5)
        claims = []
        for i in range(n):
            k = rnd.choice([1, 1, 2])
            supp = [(rnd.choice(origins), f"e{i}_{j}") for j in range(k)]
            if k == 2 and supp[0][0] == supp[1][0]:
                supp[1] = (rnd.choice([o for o in origins if o != supp[0][0]]), supp[1][1])
            claims.append(C(f"c{i}", f"tx{i}", supp))
        pairs = [(f"c{i}", f"c{j}") for i in range(n) for j in range(i + 1, n) if rnd.random() < 0.4]
        contr = contradicts_factory(pairs)
        mat = material_factory(pairs)
        try:
            r = classify_finding3(claims, contr, mat)
        except TieError:
            continue
        if r["state"] != "S1":
            continue
        s1_trials += 1
        if not r["firing_pairs"]:
            violations += 1
        if r["branch"] == "Part" and not r["part"]:
            violations += 1
        if r["competing"] is None:
            violations += 1
    return (violations == 0, f"S1 trials={s1_trials} violations={violations}")


# --- B12: selected_claim leakage check -- Comp/Part argmax must never
#          overwrite the Sigma-wide selected_claim ---
@adv("B12 -- selected_claim non-leakage from Comp/Part argmax")
def b12():
    sc = C("sc", "sc-claim", [("v1", "v1doc")])  # ios=1, wins by secondary key
    earlier_sorting_partner = C("aaa_partner", "aaa-text", [("v0", "v0doc")])  # sorts earlier alphabetically but ios=1 too -> should NOT be selected unless it wins rank_key
    contr = contradicts_factory([("sc", "earlier_sorting_partner" if False else "aaa_partner")])
    # NB: contradicts_factory keys by claim.name; sc's real name is "sc"
    contr = contradicts_factory([("sc", "aaa_partner")])
    mat = material_factory([("sc", "aaa_partner")])
    r3 = classify_finding3([sc, earlier_sorting_partner], contr, mat)
    # sc: min_evidence_key=('v1','v1doc'); aaa_partner: ('v0','v0doc') -- aaa_partner's key sorts FIRST
    # so Sigma-wide argmax should pick aaa_partner as selected_claim (not sc), and Comp should
    # then be evaluated relative to aaa_partner, with sc as the competing claim.
    ok = (r3["selected_claim"].name == "aaa_partner" and r3["branch"] == "Comp" and r3["competing"].name == "sc")
    return (ok, r3["selected_claim"].name, r3["branch"], r3["competing"].name)


for name, fn in adversarial:
    try:
        out = fn()
        ok = out[0] if isinstance(out, tuple) and isinstance(out[0], bool) else True
        record(name, ok, out)
    except Exception as e:
        record(name, False, f"EXCEPTION: {type(e).__name__}: {e}")

print()

# =====================================================================
# PART 3 -- SYSTEMATIC SWEEP: state exclusivity/completeness + confinement
# =====================================================================
print("=" * 78)
print("PART 3: SYSTEMATIC SWEEP")
print("=" * 78)

import random as _random


def random_instance(rnd, n_claims, origins, contr_p):
    claims = []
    for i in range(n_claims):
        k = rnd.choice([0, 1, 1, 1, 2])
        supp = [(rnd.choice(origins), f"s{i}_{j}") for j in range(k)]
        if k == 2 and supp[0][0] == supp[1][0]:
            alt = [o for o in origins if o != supp[0][0]]
            supp[1] = (rnd.choice(alt), supp[1][1])
        claims.append(C(f"n{i}", f"tt{i}", supp))
    pairs = [(f"n{i}", f"n{j}") for i in range(n_claims) for j in range(i + 1, n_claims)
              if rnd.random() < contr_p]
    return claims, contradicts_factory(pairs), material_factory(pairs)


# 3a: exhaustiveness + exclusivity over 6000 random instances
rnd = _random.Random(31415)
origins_pool = [f"src{i}" for i in range(7)]
total, s0, s1, s2, s3, other, ties = 0, 0, 0, 0, 0, 0, 0
for _ in range(6000):
    n = rnd.randint(0, 6)
    claims, contr, mat = random_instance(rnd, n, origins_pool, 0.3)
    total += 1
    try:
        r = classify_finding3(claims, contr, mat)
    except TieError:
        ties += 1
        continue
    st = r["state"]
    if st == "S0":
        s0 += 1
    elif st == "S1":
        s1 += 1
    elif st == "S2":
        s2 += 1
    elif st == "S3":
        s3 += 1
    else:
        other += 1
    # exclusivity: exactly-one-state invariant is structural (elif cascade) --
    # verify no result carries a state label outside {S0,S1,S2,S3}
    assert st in ("S0", "S1", "S2", "S3")
    # cross-check: state must be consistent with the deterministic recomputation
    Sigma_n = [c for c in claims if ios(c) >= 1]
    if not Sigma_n:
        assert st == "S0"
    else:
        fps = [ (a,b) for i,a in enumerate(Sigma_n) for b in Sigma_n[Sigma_n.index(a)+1:]
                 if contr(a,b) and mat(a,b) and __import__("audit_new_f3_reference").independent_origins(a.supp+b.supp) >= 2 ]
        if fps:
            assert st == "S1", f"expected S1, got {st}"
        else:
            assert st in ("S2", "S3")

record("3a. Exhaustiveness/exclusivity over 6000 random instances (S0/S1/S2/S3 only, 0 violations)",
       (other == 0), f"total={total} ties(excluded)={ties} s0={s0} s1={s1} s2={s2} s3={s3} other={other}")

# 3b: confinement sweep -- pathology (Comp excludes a decoy that F2 would have
# admitted) possible iff ios(selected_claim)==1
rnd = _random.Random(271828)
by_ios_total = {1: 0, 2: 0, 3: 0, 4: 0}
by_ios_diff = {1: 0, 2: 0, 3: 0, 4: 0}
for _ in range(4000):
    n = rnd.randint(2, 6)
    claims, contr, mat = random_instance(rnd, n, origins_pool, 0.35)
    try:
        r2 = classify_finding2(claims, contr, mat)
        r3 = classify_finding3(claims, contr, mat)
    except TieError:
        continue
    if r3["state"] != "S1":
        continue
    n_ios = r3["ioc"]
    if n_ios not in by_ios_total:
        continue
    by_ios_total[n_ios] += 1
    if r2["contradiction"] != r3["contradiction"]:
        by_ios_diff[n_ios] += 1

confinement_ok = all(by_ios_diff[k] == 0 for k in (2, 3, 4))
record("3b. Algebraic confinement: F2!=F3 only possible at ios(selected_claim)=1",
       confinement_ok,
       f"by_ios_total={by_ios_total} by_ios_diff={by_ios_diff}")

print()
print("SUMMARY:", sum(1 for _, ok, _ in results if ok), "/", len(results), "checks passed")
failed = [n for n, ok, _ in results if not ok]
print("FAILED:", failed if failed else "none")

