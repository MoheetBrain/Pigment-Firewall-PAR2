#!/usr/bin/env python3
"""Merge the benchmark docking evidence into PAR2_ACTIVE_DECOY_BENCHMARK.csv.

CRYSTAL_IFP_RECOVERY and DESIGN_HOTSPOT_SCORE are computed by importing
`v2_anchor_metrics.score_pose` from the campaign scripts, so they carry the
campaign's residue definitions, hotspot weights and crystal reference key sets
exactly. consensus_score comes from `v2_consensus_rank.py`, also unmodified.

One convention differs from the campaign, deliberately, and is recorded in the
output: the campaign collapses duplicate prepared InChIKeys, whereas a benchmark
must keep every input molecule. Duplicates are therefore flagged
(`qc_duplicate_prepared_structure`) rather than dropped.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from v2_anchor_metrics import score_pose  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--consensus", type=Path, required=True,
                    help="DENOVO_EX8_CONSENSUS_ALL.csv from v2_consensus_rank.py")
    ap.add_argument("--anchors", type=Path, required=True,
                    help="ROBUST_ANCHORS_*_BEST.csv from v2_robust_anchors.py")
    ap.add_argument("--input", type=Path, nargs="+", required=True,
                    help="BENCH_DOCKING_INPUT*.csv (class labels and provenance)")
    ap.add_argument("--ligand-table", type=Path, required=True)
    ap.add_argument("--actives", type=Path, required=True)
    ap.add_argument("--decoys", type=Path, required=True)
    ap.add_argument("--ex32", type=Path, default=None,
                    help="optional EX32 consensus table for the EX8-vs-EX32 check")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    e = pd.read_csv(args.consensus, low_memory=False)
    print(f"[merge] consensus rows {len(e)}, molecules {e.cand_id.nunique()}")

    # --- campaign anchor metrics, computed from the stored ifp_keys ---
    metrics = pd.DataFrame([score_pose(k, p, per_residue=False)
                            for k, p in zip(e.ifp_keys.fillna(""), e.pocket)])
    metrics = metrics.rename(columns={
        "crystal_ifp_recovery": "CRYSTAL_IFP_RECOVERY",
        "design_hotspot_score": "DESIGN_HOTSPOT_SCORE",
        "design_hotspot_hbond_score": "DESIGN_HOTSPOT_HBOND_SCORE",
    })
    e = pd.concat([e.reset_index(drop=True), metrics.reset_index(drop=True)], axis=1)

    # cross-check: the campaign's own max_ifp_recovery must reproduce
    if "max_ifp_recovery" in e:
        d = (e.CRYSTAL_IFP_RECOVERY - e.max_ifp_recovery).abs().max()
        print(f"[crosscheck] CRYSTAL_IFP_RECOVERY vs max_ifp_recovery, "
              f"max |delta| = {d:.3e} "
              f"({'AGREE' if pd.isna(d) or d < 1e-9 else 'DISAGREE'})")

    anchors = pd.read_csv(args.anchors)
    keep = ["cand_id", "pocket", "polar_anchor_count", "polar_anchor_fraction",
            "min_receptor_contact_A", "n_receptor_atoms_within_4_5A",
            "n_ligand_polar_atoms"] + [c for c in anchors.columns
                                       if c.startswith(("dist_", "anchor_"))]
    e = e.merge(anchors[[c for c in keep if c in anchors.columns]],
                on=["cand_id", "pocket"], how="left")

    inp = pd.concat([pd.read_csv(p) for p in args.input], ignore_index=True)
    take = ["cand_id", "mol_class", "label_name", "source_ref", "activity_nM", "notes"]
    # v2_pose_evidence.py already merged the ligand table, which carries some of
    # these names. Drop the copies so the join cannot produce _x/_y columns whose
    # meaning then depends on merge order.
    e = e.drop(columns=[c for c in take if c != "cand_id" and c in e.columns])
    e = e.merge(inp[take], on="cand_id", how="left")

    # The class label is RE-DERIVED from the current curated actives table rather
    # than trusted from the frozen docking-input CSV. The actives curation was
    # revised after docking started (censored ">" measurements removed, three
    # GtoPdb-verified compounds added), and a stale label would silently put a
    # compound known to be INACTIVE at PAR2 into the actives set.
    A_now = pd.read_csv(args.actives)
    inc_ids = set(A_now.loc[A_now.include_in_enrichment == True, "chembl_id"].dropna())  # noqa: E712
    exc = A_now[A_now.include_in_enrichment != True]  # noqa: E712
    censored_ids = set(exc.loc[exc.get("censored_inactive", False) == True, "chembl_id"].dropna())  # noqa: E712
    reason_by_id = dict(zip(exc.chembl_id, exc.exclusion_reason))
    supp_names = set(A_now.loc[A_now.supplementary_source.notna()
                               & (A_now.include_in_enrichment == True),  # noqa: E712
                               "name_canonical"].dropna())

    def reclass(row):
        if row.mol_class == "DECOY":
            return "DECOY"
        if row.label_name in supp_names:
            return "ACTIVE"
        cid = row.source_ref
        if cid in inc_ids:
            return "ACTIVE"
        if cid in censored_ids:
            return "CENSORED_INACTIVE"
        if cid in reason_by_id:
            r = str(reason_by_id[cid])
            if "peptide" in r or "frequent hitter" in r or "agonist" in r or "distal" in r:
                return "COUNTER_CONTROL"
            return "WEAK_ACTIVE"
        return row.mol_class

    before = e.mol_class.value_counts().to_dict()
    e["mol_class_as_docked"] = e.mol_class
    e["mol_class"] = e.apply(reclass, axis=1)
    print(f"[reclass] before {before}")
    print(f"[reclass] after  {e.mol_class.value_counts().to_dict()}")

    lig = pd.read_csv(args.ligand_table)
    qc = lig[["cand_id", "inchikey", "constitution_changed", "stereo_changed",
              "n_stereocentres_in", "n_assigned_in", "n_assigned_out",
              "duplicate_prepared_inchikey", "smiles"]].rename(columns={
                  "constitution_changed": "qc_prep_constitution_changed",
                  "stereo_changed": "qc_prep_stereo_changed",
                  "duplicate_prepared_inchikey": "qc_duplicate_prepared_structure",
                  "smiles": "smiles_input"})
    e = e.merge(qc, on="cand_id", how="left", suffixes=("", "_lt"))

    # provenance columns from the curated source tables
    A = pd.read_csv(args.actives)
    # Supplementary and UNVERIFIED rows carry no ChEMBL id, so the column has
    # repeated NaNs and cannot index directly.
    amap = A[A.chembl_id.notna()].drop_duplicates("chembl_id").set_index("chembl_id")
    for col, new in (("activity_type", "active_activity_type"),
                     ("activity_nM_normalised", "active_potency_nM"),
                     ("assay", "active_assay"),
                     ("reference", "active_reference"),
                     ("confidence", "active_confidence"),
                     ("readout_class", "active_readout_class"),
                     ("murcko_scaffold", "active_murcko_scaffold")):
        e[new] = e.source_ref.map(amap[col]) if col in amap else None
    D = pd.read_csv(args.decoys)
    dmap = D[D.cand_id.notna()].drop_duplicates("cand_id").set_index("cand_id")
    for col, new in (("matched_active", "decoy_matched_active"),
                     ("match_tier", "decoy_match_tier"),
                     ("tier_window", "decoy_tier_window"),
                     ("max_tanimoto_to_any_active", "decoy_max_tanimoto_to_any_active"),
                     ("pool_library", "decoy_source_library"),
                     ("pool_id", "decoy_source_id"),
                     ("pool_lane", "decoy_source_lane")):
        e[new] = e.cand_id.map(dmap[col]) if col in dmap else None

    # QC: a decoy that shares a prepared structure with any non-decoy is not a
    # decoy. Flagged, and excluded from the enrichment universe downstream.
    nondecoy_keys = set(e.loc[e.mol_class != "DECOY", "inchikey"].dropna())
    e["qc_decoy_collides_with_active"] = (
        (e.mol_class == "DECOY") & e.inchikey.isin(nondecoy_keys))
    e["qc_exclude_from_enrichment"] = e.qc_decoy_collides_with_active
    n_bad = int(e.qc_decoy_collides_with_active.sum())
    print(f"[qc] decoys colliding with a non-decoy prepared structure: {n_bad}")
    e.loc[e.qc_decoy_collides_with_active, "mol_class"] = "DECOY_DISQUALIFIED"

    if args.ex32 and args.ex32.exists():
        x = pd.read_csv(args.ex32, low_memory=False)
        xm = pd.DataFrame([score_pose(k, p, per_residue=False)
                           for k, p in zip(x.ifp_keys.fillna(""), x.pocket)])
        x = pd.concat([x.reset_index(drop=True), xm.reset_index(drop=True)], axis=1)
        cols = {"best_vina_affinity": "ex32_best_vina_affinity",
                "best_CNNscore": "ex32_best_CNNscore",
                "best_CNNaffinity": "ex32_best_CNNaffinity",
                "crystal_ifp_recovery": "ex32_CRYSTAL_IFP_RECOVERY",
                "design_hotspot_score": "ex32_DESIGN_HOTSPOT_SCORE",
                "all_poses_clashing": "ex32_all_poses_clashing"}
        sub = x[["cand_id", "pocket"] + [c for c in cols if c in x]].rename(columns=cols)
        e = e.merge(sub, on=["cand_id", "pocket"], how="left")
        print(f"[merge] EX32 rows joined: {int(sub.shape[0])}")

    front = ["cand_id", "mol_class", "label_name", "pocket", "source_ref",
             "activity_nM", "smiles_input", "smiles_prepared", "inchikey"]
    e = e[[c for c in front if c in e] + [c for c in e.columns if c not in front]]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    e.to_csv(args.out, index=False)

    summary = dict(
        generated_utc=datetime.now(timezone.utc).isoformat(),
        rows=int(len(e)), molecules=int(e.cand_id.nunique()),
        by_class=e.groupby(["mol_class", "pocket"]).size().unstack(fill_value=0).to_dict(),
        decoys_disqualified=n_bad,
        clash_rate_by_pocket={p: float(s.all_poses_clashing.astype(bool).mean())
                              for p, s in e.groupby("pocket")}
        if "all_poses_clashing" in e else {},
    )
    args.out.with_suffix(".summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
