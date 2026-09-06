#!/usr/bin/env python3
"""Supporting analyses that the headline enrichment table cannot carry.

  * EX8 vs EX32 -- does four-fold more sampling change the conclusion?
  * sensitivity summaries -- scaffold-deduplicated actives, potent-only actives,
    and measured-inactive negatives, each compared with the primary result.
  * reference redock -- what CRYSTAL_IFP_RECOVERY do AZ8838 and AZ3451 themselves
    get when redocked, and where do they sit in the decoy null?
  * the AZ8838 enantiomer conflict, reported per enantiomer.
  * determinism check -- two cand_ids carrying the identical prepared structure
    must produce identical scores.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

KEY = ["ROC_AUC", "EF1pct", "EF5pct", "BEDROC_a20"]
SCORES = ["best_vina_affinity", "best_CNNscore", "best_CNNaffinity", "best_CNN_VS",
          "CRYSTAL_IFP_RECOVERY", "DESIGN_HOTSPOT_SCORE", "consensus_score",
          "ligand_efficiency", "heavy_atoms"]


def summarise(pack: dict) -> dict:
    out = {}
    for s in SCORES:
        r = pack["enrichment"].get(s)
        if r and r.get("status") != "INSUFFICIENT_DATA":
            out[s] = {k: round(r[k]["value"], 4) for k in KEY if k in r}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--benchmark", type=Path, required=True)
    ap.add_argument("--primary", type=Path, required=True)
    ap.add_argument("--sensitivity", type=Path, nargs="*", default=[])
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    df = pd.read_csv(args.benchmark, low_memory=False)
    d5 = df[df.pocket == "5NDD_orthosteric"]
    primary = json.loads(args.primary.read_text())
    extra: dict = {}

    # ---- sensitivity comparison ----
    comp = {"PRIMARY (all actives, clash-filtered, DECOY negatives)": summarise(primary)}
    for p in args.sensitivity:
        pack = json.loads(p.read_text())
        tag = (f"{p.stem}: n_act={pack['n_actives']} n_neg={pack['n_decoys']} "
               f"neg={pack.get('negative_class', 'DECOY')} "
               f"clash={pack.get('clash_filtered')} "
               f"scafdedup={pack.get('one_active_per_scaffold')} "
               f"potency<={pack.get('potency_cutoff_nM')}")
        comp[tag] = summarise(pack)
    extra["sensitivity_analyses"] = comp

    # ---- EX8 vs EX32 ----
    if "ex32_best_vina_affinity" in d5.columns:
        m = d5[d5.ex32_best_vina_affinity.notna()]
        pairs = {}
        for a, b in (("best_vina_affinity", "ex32_best_vina_affinity"),
                     ("best_CNNscore", "ex32_best_CNNscore"),
                     ("best_CNNaffinity", "ex32_best_CNNaffinity"),
                     ("CRYSTAL_IFP_RECOVERY", "ex32_CRYSTAL_IFP_RECOVERY"),
                     ("DESIGN_HOTSPOT_SCORE", "ex32_DESIGN_HOTSPOT_SCORE")):
            if b not in m.columns:
                continue
            x = pd.to_numeric(m[a], errors="coerce")
            y = pd.to_numeric(m[b], errors="coerce")
            ok = x.notna() & y.notna()
            if ok.sum() < 10:
                continue
            d = (y[ok] - x[ok])
            pairs[a] = dict(
                n=int(ok.sum()),
                spearman=round(float(x[ok].rank().corr(y[ok].rank())), 4),
                pearson=round(float(np.corrcoef(x[ok], y[ok])[0, 1]), 4),
                median_change=round(float(d.median()), 4),
                mean_change=round(float(d.mean()), 4),
                improved=int((d < 0).sum()) if a == "best_vina_affinity" else int((d > 0).sum()),
                worsened=int((d > 0).sum()) if a == "best_vina_affinity" else int((d < 0).sum()),
                unchanged=int((d == 0).sum()),
            )
        extra["ex8_vs_ex32"] = dict(
            molecules_compared=int(len(m)),
            note=("'improved' is signed for the metric: lower Vina is better, "
                  "higher is better for everything else."),
            per_score=pairs)

    # ---- reference ligand redock ----
    refs = df[df.mol_class == "REFERENCE"]
    if len(refs):
        rows = []
        for r in refs.itertuples():
            pool = df[(df.pocket == r.pocket) & (df.mol_class == "DECOY")]
            v = pd.to_numeric(pool.CRYSTAL_IFP_RECOVERY, errors="coerce").dropna()
            rec = getattr(r, "CRYSTAL_IFP_RECOVERY", np.nan)
            rows.append(dict(
                name=r.label_name, pocket=r.pocket,
                CRYSTAL_IFP_RECOVERY=None if pd.isna(rec) else float(rec),
                best_vina_affinity=float(r.best_vina_affinity)
                if pd.notna(r.best_vina_affinity) else None,
                all_poses_clashing=bool(r.all_poses_clashing),
                percentile_among_decoys=(round(float((v < rec).mean() * 100), 2)
                                         if len(v) and pd.notna(rec) else None),
                decoys_matching_or_beating=(int((v >= rec).sum())
                                            if len(v) and pd.notna(rec) else None),
                n_decoys=int(len(v)),
            ))
        extra["reference_ligand_redock"] = rows

    # ---- AZ8838 enantiomers ----
    az = df[df.label_name.fillna("").str.startswith("AZ8838")
            & (df.pocket == "5NDD_orthosteric")]
    if len(az):
        extra["AZ8838_enantiomers"] = [
            dict(cand_id=r.cand_id, inchikey=r.inchikey, mol_class=r.mol_class,
                 source=r.source_ref,
                 CRYSTAL_IFP_RECOVERY=None if pd.isna(r.CRYSTAL_IFP_RECOVERY)
                 else float(r.CRYSTAL_IFP_RECOVERY),
                 best_vina_affinity=None if pd.isna(r.best_vina_affinity)
                 else float(r.best_vina_affinity),
                 polar_anchor_count=None if pd.isna(getattr(r, "polar_anchor_count", np.nan))
                 else float(r.polar_anchor_count))
            for r in az.itertuples()]
        extra["AZ8838_enantiomer_note"] = (
            "ChEMBL curates the two source patents inconsistently: the (R) "
            "enantiomer is the active one in US-10550089-B2 and (S) in "
            "US-10995072-B2. PDB 5NDD and Cheng et al. Nature 2017 support (S) "
            "(IDFPQEHZYBXIFO-LBPRGKRZSA-N). All forms present in ChEMBL were "
            "docked and are reported separately rather than being merged.")

    # ---- determinism: identical prepared structure, different cand_id ----
    dup = d5[d5.inchikey.duplicated(keep=False)].sort_values(["inchikey", "cand_id"])
    checks = []
    for ik, g in dup.groupby("inchikey"):
        if len(g) < 2:
            continue
        v = pd.to_numeric(g.best_vina_affinity, errors="coerce").dropna()
        if len(v) < 2:
            continue
        checks.append(dict(inchikey=ik, n=len(g),
                           cand_ids=list(g.cand_id)[:4],
                           vina_spread=round(float(v.max() - v.min()), 6),
                           classes=sorted(set(g.mol_class))))
    if checks:
        spreads = [c["vina_spread"] for c in checks]
        extra["determinism_identical_structures"] = dict(
            n_groups=len(checks),
            max_vina_spread=round(float(max(spreads)), 6),
            median_vina_spread=round(float(np.median(spreads)), 6),
            groups_with_zero_spread=int(sum(1 for s in spreads if s == 0)),
            interpretation=("Identical prepared structures docked under different "
                            "cand_ids must give identical scores. A non-zero spread "
                            "means the docking is not reproducible at fixed seed."),
            examples=checks[:8])

    # ---- clash rates ----
    extra["clash_rates"] = {
        p: {c: round(float(s.all_poses_clashing.astype(bool).mean()), 4)
            for c, s in sub.groupby("mol_class")}
        for p, sub in df.groupby("pocket")}

    args.out.write_text(json.dumps(extra, indent=2, default=str))
    print(f"wrote {args.out}")
    for k in extra:
        print(f"  - {k}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
