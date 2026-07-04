"""
R3F.2 Preregistered Analysis — Replay Fidelity vs Predictive Validity.
Executes the LOCKED preregistration exactly. No redesign.
"""
import json
import numpy as np
from scipy import stats

PATH = r"C:\Users\Purushottam\Documents\VELYNX\research_artifacts\attribution_20260628T234455\evaluation_log.jsonl"
SEED = 42
N_BOOT = 10000

# ----------------------------------------------------------------------
# STEP 1-2: Load + JOIN -> one flat row per proposal
# ----------------------------------------------------------------------
rows = []  # each: dict with proposal_id, window_index, replay_error, delta_prediction, counterfactual_rank, + extras
n_windows = 0
join_mismatch = 0

with open(PATH, "r", encoding="utf-8") as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        w = json.loads(line)
        n_windows += 1
        window_index = w.get("window_index")
        cf_rank_ids = w.get("counterfactual_ranking_ids", [])
        rank_pos = {pid: i + 1 for i, pid in enumerate(cf_rank_ids)}  # 1-indexed
        replay_map = w.get("replay_errors_per_proposal", {})
        is_topk = w.get("is_top_k_correct")
        pareto = w.get("winner_is_pareto_optimal")
        rankings = w.get("evaluator_result", {}).get("rankings", [])
        for r in rankings:
            pid = r.get("proposal_id")
            if pid not in replay_map or pid not in rank_pos:
                join_mismatch += 1
                continue
            rows.append({
                "proposal_id": pid,
                "window_index": window_index,
                "replay_error": float(replay_map[pid]),
                "delta_prediction": float(r.get("delta_prediction")),   # ΔS
                "counterfactual_rank": int(rank_pos[pid]),
                "accepted": bool(r.get("accepted")),
                "delta_energy": r.get("delta_energy"),
                "delta_entropy": r.get("delta_entropy"),
                "delta_load": r.get("delta_load"),
                "margin": r.get("margin"),
                "is_top_k_correct": is_topk,
                "winner_is_pareto_optimal": pareto,
            })

print(f"# windows loaded            : {n_windows}")
print(f"# proposals (flat rows)     : {len(rows)}")
print(f"# join mismatches           : {join_mismatch}")

replay = np.array([r["replay_error"] for r in rows])
dS = np.array([r["delta_prediction"] for r in rows])
cf_rank = np.array([r["counterfactual_rank"] for r in rows], dtype=float)

# ----------------------------------------------------------------------
# STEP 3: Equal-frequency quartiles (qcut), stable-rank tie handling
#   rank with method='first' (stable, ties by order of appearance),
#   then split into 4 exactly-equal-frequency bins.
# ----------------------------------------------------------------------
order = np.argsort(replay, kind="stable")     # stable -> "first" tie handling
ranks = np.empty(len(replay), dtype=int)
ranks[order] = np.arange(len(replay))          # 0-indexed stable rank
n = len(replay)
quartile = np.floor(4.0 * ranks / n).astype(int)
quartile = np.clip(quartile, 0, 3)             # labels 0..3 == Q1..Q4

# ----------------------------------------------------------------------
# Pearson r (SIGNED) between ΔS and counterfactual_rank, per stratum,
# with BCa 95% CI (10,000 resamples, seed=42).
# ----------------------------------------------------------------------
def pearson_stat(x, y):
    return stats.pearsonr(x, y)[0]

print("\n=== QUARTILE STATISTICS (ΔS vs counterfactual_rank) ===")
strat_r = []
strat_mean_re = []
strat_n = []
for q in range(4):
    m = quartile == q
    x = dS[m]                      # ΔS
    y = cf_rank[m]                 # rank
    nq = int(m.sum())
    mean_re = float(replay[m].mean())
    pr, pp = stats.pearsonr(x, y)
    sr, sp = stats.spearmanr(x, y)
    rng = np.random.default_rng(SEED)
    boot = stats.bootstrap(
        (x, y), pearson_stat, method="BCa", n_resamples=N_BOOT,
        paired=True, vectorized=False, random_state=rng, confidence_level=0.95,
    )
    lo, hi = boot.confidence_interval
    strat_r.append(pr)
    strat_mean_re.append(mean_re)
    strat_n.append(nq)
    print(f"Q{q+1}: n={nq:4d}  mean_replay_error={mean_re:.6f}  "
          f"Pearson r={pr:+.4f} (p={pp:.4f})  Spearman rho={sr:+.4f} (p={sp:.4f})  "
          f"BCa95%=[{lo:+.4f}, {hi:+.4f}]")

strat_r = np.array(strat_r)
strat_mean_re = np.array(strat_mean_re)

# ----------------------------------------------------------------------
# STEP 4: Authoritative trend test — two-tailed linear regression
#   DV = stratum-level Pearson r ; IV = mean replay_error per stratum
# ----------------------------------------------------------------------
print("\n=== REGRESSION (DV = stratum Pearson r, IV = mean replay_error) ===")
lr = stats.linregress(strat_mean_re, strat_r)
slope, intercept, rval, pval, stderr = lr.slope, lr.intercept, lr.rvalue, lr.pvalue, lr.stderr
r2 = rval ** 2
df = len(strat_r) - 2
tcrit = stats.t.ppf(0.975, df)
slope_lo = slope - tcrit * stderr
slope_hi = slope + tcrit * stderr
int_stderr = getattr(lr, "intercept_stderr", float("nan"))
print(f"slope     = {slope:+.6f}")
print(f"intercept = {intercept:+.6f}")
print(f"R^2       = {r2:.6f}")
print(f"p-value   = {pval:.6f} (two-tailed)")
print(f"slope 95% CI = [{slope_lo:+.6f}, {slope_hi:+.6f}]  (t_crit={tcrit:.4f}, df={df})")

# ----------------------------------------------------------------------
# STEP 6 support: window-level is_top_k_correct by quartile
#   (window-level table, not per-proposal, to respect non-independence)
# ----------------------------------------------------------------------
print("\n=== STEP 6 PREP: window-level is_top_k_correct by replay_error quartile ===")
# Build window-level mean replay_error, then quartile windows by their mean replay error.
win_ids = sorted(set(r["window_index"] for r in rows))
win_re = {}
win_topk = {}
for wid in win_ids:
    vals = [r["replay_error"] for r in rows if r["window_index"] == wid]
    win_re[wid] = float(np.mean(vals))
    tk = [r["is_top_k_correct"] for r in rows if r["window_index"] == wid]
    win_topk[wid] = bool(tk[0]) if tk else None

wids = np.array(win_ids)
wre = np.array([win_re[w] for w in win_ids])
wtk = np.array([1 if win_topk[w] else 0 for w in win_ids])
worder = np.argsort(wre, kind="stable")
wr = np.empty(len(wre), dtype=int)
wr[worder] = np.arange(len(wre))
wq = np.clip(np.floor(4.0 * wr / len(wre)).astype(int), 0, 3)

table = np.zeros((4, 2), dtype=int)  # [quartile][topk 0/1]
for q in range(4):
    mm = wq == q
    table[q, 1] = int(wtk[mm].sum())
    table[q, 0] = int((mm.sum()) - wtk[mm].sum())
    print(f"Q{q+1}: windows={int(mm.sum()):3d}  topk_TRUE={table[q,1]:3d}  "
          f"topk_FALSE={table[q,0]:3d}  rate={table[q,1]/max(mm.sum(),1):.3f}")

chi2, chi_p, dof, _ = stats.chi2_contingency(table)
print(f"chi-square (4x2, window-level): chi2={chi2:.4f}  p={chi_p:.4f}  dof={dof}")
print(f"total windows topk_TRUE = {int(wtk.sum())}/{len(wtk)} ({wtk.mean():.3f})")

# Also: acceptance rate & pareto by quartile (per-proposal descriptive)
print("\n=== STEP 6 PREP: acceptance rate by proposal quartile ===")
acc = np.array([1 if r["accepted"] else 0 for r in rows])
for q in range(4):
    m = quartile == q
    print(f"Q{q+1}: acceptance_rate={acc[m].mean():.4f}  n={int(m.sum())}")

# Pooled correlations for reference
pr_all, pp_all = stats.pearsonr(dS, cf_rank)
sr_all, sp_all = stats.spearmanr(dS, cf_rank)
print(f"\nPOOLED (all 656): Pearson r={pr_all:+.4f} (p={pp_all:.4g})  "
      f"Spearman rho={sr_all:+.4f} (p={sp_all:.4g})")
