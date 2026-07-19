"""Verify Comp_F3 subset Comp_F2 claim (doc SS3.1, SS5.3, SS5.8) directly, and check the
'Comp_F3 == Comp_F2 whenever Comp_F2 already held only genuine participants' claim (SS3.3/SS5.4)."""
import itertools, random
from audit_f3_independent import Claim, Oracle, ios, supp, firing_pairs

def comp_f2(oracle, sigma, sel):
    return set(c.name for c in sigma if c is not sel
               and oracle.contradicts(sel, c) and oracle.is_material(sel, c))

def comp_f3(oracle, sigma, sel):
    from audit_f3_independent import s1pair
    return set(c.name for c in sigma if c is not sel and s1pair(oracle, sel, c))

def prec_max_name(oracle, sigma):
    from audit_f3_independent import prec_max
    m = prec_max(sigma)
    return m

random.seed(555)
violations_subset = 0
violations_equal_when_f2_pure = 0
trials = 0
for _ in range(3000):
    n = random.randint(1, 6)
    cs = []
    for i in range(n):
        k = random.randint(1, 3)
        cs.append(Claim("C%d"%i, "C%d"%i, [("O%d_%d"%(i,j), "D%d_%d"%(i,j)) for j in range(k)]))
    names = [c.name for c in cs]
    contra = [(a,b) for a,b in itertools.combinations(names,2) if random.random() < 0.35]
    o = Oracle(contra=contra)
    sigma = [c for c in cs if ios(c) >= 1]
    if not sigma:
        continue
    try:
        sel = prec_max_name(o, sigma)
    except Exception:
        continue
    trials += 1
    c2 = comp_f2(o, sigma, sel)
    c3 = comp_f3(o, sigma, sel)
    if not c3.issubset(c2):
        violations_subset += 1
    # "F2 was already pure" means every member of c2 is a genuine S1 co-participant with sel
    fp = firing_pairs(o, sigma)
    def is_participant_with_sel(name):
        return any((sel.name==a.name and name==b.name) or (sel.name==b.name and name==a.name) for a,b in fp)
    f2_pure = all(is_participant_with_sel(n) for n in c2) if c2 else True
    if f2_pure and c2 != c3:
        violations_equal_when_f2_pure += 1

print("trials=%d" % trials)
print("Comp_F3 subset Comp_F2 violations = %d (must be 0)" % violations_subset)
print("Comp_F3 == Comp_F2 violations, when Comp_F2 already pure = %d (must be 0)" % violations_equal_when_f2_pure)
assert violations_subset == 0
assert violations_equal_when_f2_pure == 0
print("SUBSET/BYTE-IDENTITY CLAIMS VERIFIED")
