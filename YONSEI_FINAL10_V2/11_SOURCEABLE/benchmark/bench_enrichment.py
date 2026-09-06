#!/usr/bin/env python3
"""Enrichment metrics and the interaction-fingerprint null distribution.

Computes, for every candidate score, ROC-AUC, PR-AUC, EF1%, EF5%, BEDROC at
alpha = 20 and alpha = 80.5, each with a bootstrap confidence interval and a
label-permutation null. Metrics are implemented directly on numpy so nothing
depends on a package the docking host does not carry, and so the tie-handling is
explicit rather than inherited.

Ties matter here. Docking scores tie rarely, but a metric such as
CRYSTAL_IFP_RECOVERY takes only 17 distinct values in 5NDD (k/16), so a naive
"sort and count" enrichment silently rewards whichever class happens to sort
first inside a tied block. Every metric below therefore averages over the tied
block instead of trusting the sort order.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


# --------------------------------------------------------------------------- #
# metrics
# --------------------------------------------------------------------------- #

def roc_auc(y: np.ndarray, s: np.ndarray) -> float:
    """Rank-based ROC-AUC with proper mid-rank handling of ties."""
    order = np.argsort(s, kind="mergesort")
    ranks = np.empty(len(s), dtype=float)
    sorted_s = s[order]
    i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and sorted_s[j + 1] == sorted_s[i]:
            j += 1
        ranks[order[i:j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    n_pos, n_neg = int(y.sum()), int(len(y) - y.sum())
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    return float((ranks[y == 1].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def pr_auc(y: np.ndarray, s: np.ndarray) -> float:
    """Average precision. Tied scores are collapsed into a single threshold."""
    order = np.argsort(-s, kind="mergesort")
    ys, ss = y[order], s[order]
    n_pos = int(y.sum())
    if n_pos == 0:
        return float("nan")
    tp = fp = 0
    prev_recall = 0.0
    ap = 0.0
    i = 0
    while i < len(ys):
        j = i
        while j + 1 < len(ys) and ss[j + 1] == ss[i]:
            j += 1
        block = ys[i:j + 1]
        tp += int(block.sum())
        fp += int(len(block) - block.sum())
        recall = tp / n_pos
        precision = tp / (tp + fp)
        ap += (recall - prev_recall) * precision
        prev_recall = recall
        i = j + 1
    return float(ap)


def enrichment_factor(y: np.ndarray, s: np.ndarray, frac: float) -> float:
    """EF at a top fraction, averaging actives across the tied block at the cut.

    A tie spanning the cut contributes its actives in proportion to how much of
    the block falls inside the cut, so the value does not depend on sort order.
    """
    n = len(y)
    k = max(1, int(round(frac * n)))
    order = np.argsort(-s, kind="mergesort")
    ys, ss = y[order], s[order]
    n_pos = int(y.sum())
    if n_pos == 0:
        return float("nan")
    captured = 0.0
    i = 0
    while i < n:
        j = i
        while j + 1 < n and ss[j + 1] == ss[i]:
            j += 1
        size = j - i + 1
        inside = min(j + 1, k) - i
        if inside <= 0:
            break
        captured += ys[i:j + 1].sum() * (inside / size)
        i = j + 1
    return float((captured / k) / (n_pos / n))


def bedroc(y: np.ndarray, s: np.ndarray, alpha: float) -> float:
    """BEDROC exactly as defined by Truchon & Bayly, J Chem Inf Model 2007, 47, 488.

        RIE   = (1/n) sum_i exp(-alpha * r_i / N)
                / [ (1/N) (1 - exp(-alpha)) / (exp(alpha/N) - 1) ]

        BEDROC = RIE * Ra sinh(alpha/2)
                       / (cosh(alpha/2) - cosh(alpha/2 - alpha Ra))
                 + 1 / (1 - exp(alpha (1 - Ra)))

    with N the total, n the number of actives and Ra = n/N. Tied scores receive
    their mid-rank so the result cannot depend on the sort order inside a tie.
    """
    N = len(y)
    n = int(y.sum())
    if n == 0 or n == N:
        return float("nan")
    order = np.argsort(-s, kind="mergesort")
    ss, ys = s[order], y[order]
    ranks = np.empty(N, dtype=float)
    i = 0
    while i < N:
        j = i
        while j + 1 < N and ss[j + 1] == ss[i]:
            j += 1
        ranks[i:j + 1] = 0.5 * (i + j) + 1.0
        i = j + 1
    ra = n / N
    r = ranks[ys == 1]
    rie_num = float(np.exp(-alpha * r / N).sum()) / n
    rie_den = (1.0 / N) * (1.0 - np.exp(-alpha)) / (np.exp(alpha / N) - 1.0)
    rie = rie_num / rie_den
    scale_den = np.cosh(alpha / 2.0) - np.cosh(alpha / 2.0 - alpha * ra)
    if scale_den == 0:
        return float("nan")
    return float(rie * ra * np.sinh(alpha / 2.0) / scale_den
                 + 1.0 / (1.0 - np.exp(alpha * (1.0 - ra))))


METRICS = {
    "ROC_AUC": lambda y, s: roc_auc(y, s),
    "PR_AUC": lambda y, s: pr_auc(y, s),
    "EF1pct": lambda y, s: enrichment_factor(y, s, 0.01),
    "EF5pct": lambda y, s: enrichment_factor(y, s, 0.05),
    "BEDROC_a20": lambda y, s: bedroc(y, s, 20.0),
    "BEDROC_a80.5": lambda y, s: bedroc(y, s, 80.5),
}


def evaluate(y: np.ndarray, s: np.ndarray, n_boot: int, n_perm: int,
             rng: np.random.Generator) -> dict:
    """Point estimates, stratified bootstrap CIs and a label-permutation null."""
    point = {k: f(y, s) for k, f in METRICS.items()}
    pos_idx = np.flatnonzero(y == 1)
    neg_idx = np.flatnonzero(y == 0)
    boot = {k: [] for k in METRICS}
    for _ in range(n_boot):
        pick = np.concatenate([rng.choice(pos_idx, len(pos_idx), replace=True),
                               rng.choice(neg_idx, len(neg_idx), replace=True)])
        yb, sb = y[pick], s[pick]
        for k, f in METRICS.items():
            boot[k].append(f(yb, sb))
    perm = {k: [] for k in METRICS}
    for _ in range(n_perm):
        yp = rng.permutation(y)
        for k, f in METRICS.items():
            perm[k].append(f(yp, s))
    out = {}
    for k in METRICS:
        b = np.asarray(boot[k], dtype=float)
        b = b[np.isfinite(b)]
        p = np.asarray(perm[k], dtype=float)
        p = p[np.isfinite(p)]
        pv = float((np.sum(p >= point[k]) + 1) / (len(p) + 1)) if len(p) else float("nan")
        out[k] = dict(
            value=point[k],
            ci95_low=float(np.percentile(b, 2.5)) if len(b) else float("nan"),
            ci95_high=float(np.percentile(b, 97.5)) if len(b) else float("nan"),
            null_median=float(np.median(p)) if len(p) else float("nan"),
            null_p95=float(np.percentile(p, 95)) if len(p) else float("nan"),
            permutation_p=pv,
        )
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--benchmark", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--pocket", default="5NDD_orthosteric")
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--n-perm", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20260906)
    ap.add_argument("--clash-filter", action="store_true",
                    help="drop molecules whose every pose clashed")
    ap.add_argument("--one-active-per-scaffold", action="store_true",
                    help="keep only the most potent active per Murcko scaffold. "
                         "Guards against analogue bias: most of the actives come "
                         "from two patents, and a congeneric series can inflate "
                         "enrichment without the score generalising at all.")
    ap.add_argument("--negatives", default="DECOY",
                    help="class used as the negative set. DECOY is the default "
                         "property-matched set; CENSORED_INACTIVE is the small "
                         "set of molecules actually TESTED against PAR2 and found "
                         "inactive, which is the only measured-negative "
                         "comparison available.")
    ap.add_argument("--potency-cutoff-nM", type=float, default=None,
                    help="restrict actives to those at or below this potency")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    df = pd.read_csv(args.benchmark, low_memory=False)
    df = df[df.pocket == args.pocket].copy()

    scores = ["best_vina_affinity", "best_CNNscore", "best_CNNaffinity",
              "CRYSTAL_IFP_RECOVERY", "DESIGN_HOTSPOT_SCORE", "consensus_score",
              "ligand_efficiency", "best_CNN_VS", "polar_anchor_count",
              "crystal_hbond_recovery",
              # Negative controls. These carry NO docking information. A docking
              # score that cannot beat them is not measuring binding, it is
              # re-reading a molecular property. hbd and hba are here because the
              # decoy set is significantly mismatched to the actives on both
              # (Mann-Whitney p < 1e-4), so any score correlated with them
              # inherits that separation for free.
              "heavy_atoms", "hbd", "hba", "mw", "clogp", "tpsa"]
    # Lower is better for Vina; every other score here is higher-is-better.
    sign = {s: (-1.0 if s == "best_vina_affinity" else 1.0) for s in scores}

    neg = args.negatives
    universe = df[df.mol_class.isin(["ACTIVE", neg])].copy()
    if "qc_exclude_from_enrichment" in universe:
        universe = universe[~universe.qc_exclude_from_enrichment.astype(bool)]
    if args.clash_filter and "all_poses_clashing" in universe:
        before = len(universe)
        universe = universe[~universe.all_poses_clashing.astype(bool)]
        print(f"[enrich] clash filter: {before} -> {len(universe)}")
    if args.potency_cutoff_nM is not None:
        act = universe[universe.mol_class == "ACTIVE"]
        drop = act[pd.to_numeric(act.activity_nM, errors="coerce")
                   > args.potency_cutoff_nM].index
        universe = universe.drop(drop)
        print(f"[enrich] potency cutoff {args.potency_cutoff_nM} nM dropped "
              f"{len(drop)} actives")
    if args.one_active_per_scaffold:
        scaf_col = "murcko" if "murcko" in universe.columns else "active_murcko_scaffold"
        act = universe[universe.mol_class == "ACTIVE"].copy()
        act["_p"] = pd.to_numeric(act.activity_nM, errors="coerce").fillna(9e18)
        keep = (act.sort_values("_p").drop_duplicates(scaf_col, keep="first").index)
        universe = universe.drop(act.index.difference(keep))
        print(f"[enrich] one active per scaffold ({scaf_col}): "
              f"{len(act)} -> {len(keep)} actives")
    y = (universe.mol_class == "ACTIVE").astype(int).to_numpy()
    print(f"[enrich] {args.pocket}: {int(y.sum())} actives, {int(len(y) - y.sum())} decoys")

    results = {}
    for sc in scores:
        if sc not in universe.columns:
            continue
        v = pd.to_numeric(universe[sc], errors="coerce")
        ok = v.notna().to_numpy()
        if ok.sum() < 20 or y[ok].sum() < 3:
            results[sc] = dict(status="INSUFFICIENT_DATA",
                               n_with_value=int(ok.sum()),
                               n_actives_with_value=int(y[ok].sum()))
            continue
        r = evaluate(y[ok], sign[sc] * v[ok].to_numpy(float), args.n_boot, args.n_perm, rng)
        r["n_evaluated"] = int(ok.sum())
        r["n_actives"] = int(y[ok].sum())
        r["n_missing"] = int((~ok).sum())
        r["direction"] = "lower_is_better" if sign[sc] < 0 else "higher_is_better"
        # A control that separates the classes in EITHER direction is equally
        # informative about how much free signal a correlated score inherits.
        r["auc_abs_deviation_from_chance"] = abs(r["ROC_AUC"]["value"] - 0.5)
        results[sc] = r
        print(f"  {sc:26s} ROC-AUC {r['ROC_AUC']['value']:.3f} "
              f"[{r['ROC_AUC']['ci95_low']:.3f},{r['ROC_AUC']['ci95_high']:.3f}] "
              f"p={r['ROC_AUC']['permutation_p']:.4f}  "
              f"EF1% {r['EF1pct']['value']:.2f}  "
              f"BEDROC20 {r['BEDROC_a20']['value']:.3f}")

    # ---------------- IFP null distribution over decoys ---------------- #
    dec = df[df.mol_class == neg].copy()
    ifp = pd.to_numeric(dec.get("CRYSTAL_IFP_RECOVERY"), errors="coerce").dropna()
    null = {}
    if len(ifp):
        null = dict(
            n_decoys_with_ifp=int(len(ifp)),
            n_decoys_total=int(len(dec)),
            mean=float(ifp.mean()), median=float(ifp.median()),
            std=float(ifp.std()), min=float(ifp.min()), max=float(ifp.max()),
            deciles={f"p{p}": float(np.percentile(ifp, p))
                     for p in range(0, 101, 10)},
            exceedance={
                "P_ge_0.800": float((ifp >= 0.800).mean()),
                "P_ge_0.875": float((ifp >= 0.875).mean()),
                "P_ge_0.938": float((ifp >= 0.938).mean()),
                "P_eq_1.000": float((ifp >= 0.99999).mean()),
            },
            exceedance_counts={
                "n_ge_0.800": int((ifp >= 0.800).sum()),
                "n_ge_0.875": int((ifp >= 0.875).sum()),
                "n_ge_0.938": int((ifp >= 0.938).sum()),
                "n_eq_1.000": int((ifp >= 0.99999).sum()),
            },
        )
        # Does IFP recovery just track ligand size?
        ha = pd.to_numeric(dec.get("heavy_atoms"), errors="coerce")
        both = ifp.index.intersection(ha.dropna().index)
        if len(both) > 30:
            x, z = ha.loc[both].to_numpy(float), ifp.loc[both].to_numpy(float)
            pear = float(np.corrcoef(x, z)[0, 1])
            rx = pd.Series(x).rank().to_numpy()
            rz = pd.Series(z).rank().to_numpy()
            spear = float(np.corrcoef(rx, rz)[0, 1])
            bins = pd.cut(pd.Series(x, index=both), [0, 20, 25, 30, 35, 40, 100])
            by_size = (pd.DataFrame({"ifp": z, "bin": bins.to_numpy()})
                       .groupby("bin", observed=True)
                       .ifp.agg(["count", "median", "mean", "max",
                                 lambda v: float((v >= 0.875).mean()),
                                 lambda v: float((v >= 0.938).mean())]))
            by_size.columns = ["n", "median", "mean", "max", "P_ge_0.875", "P_ge_0.938"]
            null["heavy_atom_correlation"] = dict(
                pearson_r=pear, spearman_rho=spear,
                n=len(both),
                interpretation=("IFP recovery tracks ligand size"
                                if abs(spear) >= 0.5 else
                                "IFP recovery is only weakly related to ligand size"),
            )
            null["by_heavy_atom_bin"] = json.loads(by_size.reset_index().to_json(orient="records"))

    # per-class IFP summary, actives vs decoys vs controls
    per_class = {}
    for cls, sub in df.groupby("mol_class"):
        v = pd.to_numeric(sub.get("CRYSTAL_IFP_RECOVERY"), errors="coerce").dropna()
        if len(v):
            per_class[cls] = dict(n=int(len(v)), median=float(v.median()),
                                  mean=float(v.mean()), max=float(v.max()),
                                  P_ge_0_875=float((v >= 0.875).mean()))

    # How much of each docking score is simply a molecular property? Measured
    # WITHIN the decoys only, so the active/decoy label cannot create the
    # correlation.
    contamination = {}
    props = ["heavy_atoms", "hbd", "hba", "mw", "clogp", "tpsa"]
    dock_scores = ["best_vina_affinity", "best_CNNscore", "best_CNNaffinity",
                   "CRYSTAL_IFP_RECOVERY", "DESIGN_HOTSPOT_SCORE",
                   "consensus_score", "ligand_efficiency", "best_CNN_VS"]
    for sc in dock_scores:
        if sc not in dec.columns:
            continue
        a = pd.to_numeric(dec[sc], errors="coerce")
        row = {}
        for pr in props:
            if pr not in dec.columns:
                continue
            b = pd.to_numeric(dec[pr], errors="coerce")
            m = a.notna() & b.notna()
            if m.sum() > 30:
                row[pr] = round(float(a[m].rank().corr(b[m].rank())), 4)
        if row:
            contamination[sc] = row

    payload = dict(
        generated_utc=datetime.now(timezone.utc).isoformat(),
        pocket=args.pocket,
        negative_class=neg,
        clash_filtered=bool(args.clash_filter),
        one_active_per_scaffold=bool(args.one_active_per_scaffold),
        potency_cutoff_nM=args.potency_cutoff_nM,
        n_actives=int(y.sum()), n_decoys=int(len(y) - y.sum()),
        n_bootstrap=args.n_boot, n_permutation=args.n_perm, seed=args.seed,
        enrichment=results,
        score_property_spearman_within_decoys=contamination,
        ifp_null_distribution=null,
        ifp_by_class=per_class,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, default=str))
    print(f"\n[enrich] wrote {args.out}")
    if null:
        print("IFP null over decoys: " + ", ".join(
            f"{k}={v:.4f}" for k, v in null["exceedance"].items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
