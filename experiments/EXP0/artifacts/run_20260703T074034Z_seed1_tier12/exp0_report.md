# EXP-0 Report

Seed: 1  |  Tiers run: [1, 2]

### tier2_legacy

- N (paired items): 32
- Hit rate, original:   1.000 (32/32)
- Hit rate, paraphrase: 0.000 (0/32)
- McNemar exact test: n01=32, n10=0, discordant=32, p=0.00000 (collapse (paraphrase worse than original))
- Bootstrap 95% CI on rate difference (original - paraphrase): [1.000, 1.000] (point=1.000, 10000 iters, seed=0)
- Significant at alpha=0.01: True

- Concepts that collapsed (hit on original, miss on paraphrase): anger, betrayal, courage, curiosity, death, depression, empathy, forgiveness, gratitude, grief, guilt, hate, hope, identity, jealousy, loneliness, loss, love, market collapse, obsolescence, pain, patience, planning, pride, regret, resilience, sacrifice, shame, stagnation, trust, uncontrollable forces, understanding

### tier1_v2

- N (paired items): 32
- Hit rate, original:   0.000 (0/32)
- Hit rate, paraphrase: 0.000 (0/32)
- McNemar exact test: n01=0, n10=0, discordant=0, p=1.00000 (no asymmetry)
- Bootstrap 95% CI on rate difference (original - paraphrase): [0.000, 0.000] (point=0.000, 10000 iters, seed=0)
- Significant at alpha=0.01: False

### Holm-Bonferroni correction across primary tiers (1, 2)
- tier2_legacy: p=0.00000, threshold=0.00500, significant after correction: True
- tier1_v2: p=1.00000, threshold=0.01000, significant after correction: False
