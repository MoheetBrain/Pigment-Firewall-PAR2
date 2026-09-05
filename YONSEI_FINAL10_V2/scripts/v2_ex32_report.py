#!/usr/bin/env python3
"""Assemble the EX32 precision-redocking deliverables.

Joins the EX32 clash-filtered evidence to the EX8 evidence for the same
ligand-pocket pairs and to the diversity axis each molecule was selected on,
so that the EX32 result can be read against the EX8 result that motivated it.

DENOVO_EX32_ALL.csv    every EX32 job, with its EX8 counterpart alongside
DENOVO_EX32_TOP500.csv the same rows ranked, capped at 500

The ranking is a transparent mean of within-pocket percentile ranks over the
evidence axes; it is a presentation order, not a probability of activity, and
missing inputs stay missing rather than being imputed.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

# Higher percentile = better. False means "lower raw value is better".
RANK_AXES = {
    "max_ifp_recovery": True,
    "best_vina_affinity": False,
    "ligand_efficiency": True,
    "best_CNN_VS": True,
    "anchor_hbond_fraction_repaired": True,
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ex32-evidence", type=Path, required=True)
    ap.add_argument("--ex8-universe", type=Path, required=True)
    ap.add_argument("--selection", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--top", type=int, default=500)
    args = ap.parse_args()

    ex32 = pd.read_csv(args.ex32_evidence, low_memory=False)
    ex8 = pd.read_csv(args.ex8_universe, low_memory=False)
    sel = pd.read_csv(args.selection, low_memory=False)

    keep8 = [c for c in ["cand_id", "pocket", "best_vina_affinity", "max_ifp_recovery",
                         "ligand_efficiency", "best_CNN_VS", "best_CNNscore",
                         "n_poses_acceptable", "all_poses_clashing", "ifp_hbonds",
                         "ifp_keys", "pignet2_best"] if c in ex8.columns]
    ex8s = ex8[keep8].add_prefix("ex8_").rename(
        columns={"ex8_cand_id": "cand_id", "ex8_pocket": "pocket"})

    keepsel = [c for c in ["cand_id", "pocket", "ex32_axis", "murcko", "smiles_prepared",
                           "inchikey", "mw", "clogp", "tpsa", "hba", "hbd", "rotb", "fsp3",
                           "qed", "heavy_atoms", "aromatic_rings", "in_envelope",
                           "design_score", "ref_tanimoto", "denovo_family", "batch",
                           "dual_anchor_repaired", "anchor_any_two_repaired",
                           "anchor_hbond_fraction_repaired"] if c in sel.columns]
    sels = sel[keepsel].rename(columns={
        "dual_anchor_repaired": "ex8_dual_anchor_repaired",
        "anchor_any_two_repaired": "ex8_anchor_any_two_repaired",
        "anchor_hbond_fraction_repaired": "ex8_anchor_hbond_fraction_repaired"})

    df = ex32.merge(sels, on=["cand_id", "pocket"], how="left", suffixes=("", "_sel"))
    df = df.merge(ex8s, on=["cand_id", "pocket"], how="left")
    df["ex32_minus_ex8_vina"] = df.best_vina_affinity - df.ex8_best_vina_affinity
    df["ex32_minus_ex8_ifp"] = df.max_ifp_recovery - df.ex8_max_ifp_recovery

    # Within-pocket percentile blend over whichever axes are actually present.
    used = [c for c in RANK_AXES if c in df.columns and df[c].notna().any()]
    for col in used:
        pct = df.groupby("pocket")[col].rank(pct=True, ascending=RANK_AXES[col])
        df[f"pct_{col}"] = pct
    df["ex32_rank_score"] = df[[f"pct_{c}" for c in used]].mean(axis=1, skipna=True)
    df = df.sort_values(["ex32_rank_score"], ascending=False).reset_index(drop=True)
    df.insert(0, "ex32_rank", np.arange(1, len(df) + 1))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out_dir / "DENOVO_EX32_ALL.csv", index=False)
    df.head(args.top).to_csv(args.out_dir / "DENOVO_EX32_TOP500.csv", index=False)

    summary = dict(
        generated_utc=datetime.now(timezone.utc).isoformat(),
        ex32_jobs=int(len(df)),
        ex32_molecules=int(df.cand_id.nunique()),
        by_pocket=df.pocket.value_counts().to_dict(),
        by_selection_axis=df.ex32_axis.value_counts(dropna=False).to_dict(),
        unique_murcko=int(df.murcko.nunique()),
        rank_axes_used=used,
        all_poses_clashing_at_ex32=int(df.all_poses_clashing.sum())
        if "all_poses_clashing" in df else None,
        median_ex32_minus_ex8_vina=float(df.ex32_minus_ex8_vina.median())
        if df.ex32_minus_ex8_vina.notna().any() else None,
        median_ex32_minus_ex8_ifp=float(df.ex32_minus_ex8_ifp.median())
        if df.ex32_minus_ex8_ifp.notna().any() else None,
        top_written=int(min(args.top, len(df))),
        note=("EX32 = exhaustiveness 32, --cnn_scoring rescore, --num_modes 9, CPU. "
              "Ranking evidence only; no activity claim. Missing values are missing."),
    )
    (args.out_dir / "DENOVO_EX32_SUMMARY.json").write_text(json.dumps(summary, indent=2, default=str))
    print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
