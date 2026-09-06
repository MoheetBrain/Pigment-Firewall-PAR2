#!/usr/bin/env python3
"""Select property-matched, topologically dissimilar decoys for the PAR2 benchmark.

Decoy pool: the project's own already-prepared real-compound library
(`10_FINAL/REAL_COMPOUND_DOCKING_QUEUE.csv`) -- 6,492 real catalogue/database
molecules (FDA approved drugs, LOTUS / NPAtlas / COCONUT natural products, and
PubChem similarity analogues). Nothing is enumerated or invented.

Matching, DUD-E style, is on MW, cLogP, TPSA, formal charge, HBD, HBA and
rotatable bonds. Properties are computed with the same RDKit descriptors and the
same approximate pH 7.4 ionisation model the campaign ligand preparation uses,
so a decoy's formal charge means the same thing as an active's.

Topological dissimilarity is enforced with ECFP4 (Morgan radius 2, 2048 bits)
Tanimoto against EVERY active, not just the one being matched. The threshold is
a parameter and is recorded in the output.

Windows are widened in documented tiers only until the per-active quota is met;
the tier each decoy was drawn at is recorded so a reader can see how hard the
match had to work.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import Descriptors, rdFingerprintGenerator, rdMolDescriptors
from rdkit.Chem.MolStandardize import rdMolStandardize

RDLogger.DisableLog("rdApp.*")

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from v2_prepare_ligands import protonate_ph74  # noqa: E402

MORGAN = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)

# (dMW, dclogP, dTPSA, dHBD, dHBA, drotB). Formal charge must always match exactly.
TIERS = [
    (20.0, 0.5, 15.0, 0, 0, 0),
    (40.0, 1.0, 25.0, 1, 1, 1),
    (60.0, 1.5, 35.0, 1, 2, 2),
    (80.0, 2.0, 45.0, 2, 3, 3),
    (100.0, 2.5, 60.0, 2, 4, 4),
]


def descriptors(smiles: str) -> dict | None:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    try:
        mol = rdMolStandardize.Cleanup(mol)
        mol = rdMolStandardize.FragmentParent(mol)
    except Exception:  # noqa: BLE001
        return None
    if mol is None or mol.GetNumHeavyAtoms() < 8:
        return None
    try:
        mol = protonate_ph74(mol)
        # protonate_ph74 can hand back a molecule whose ring info was cleared by
        # the atom edits; descriptors need it re-derived.
        Chem.SanitizeMol(mol)
    except Exception:  # noqa: BLE001
        try:
            Chem.SanitizeMol(mol)
        except Exception:  # noqa: BLE001
            return None
    return dict(
        mw=float(Descriptors.MolWt(mol)),
        clogp=float(Descriptors.MolLogP(mol)),
        tpsa=float(rdMolDescriptors.CalcTPSA(mol)),
        hba=int(rdMolDescriptors.CalcNumHBA(mol)),
        hbd=int(rdMolDescriptors.CalcNumHBD(mol)),
        rotb=int(rdMolDescriptors.CalcNumRotatableBonds(mol)),
        formal_charge=int(Chem.GetFormalCharge(mol)),
        heavy_atoms=int(mol.GetNumHeavyAtoms()),
        fp=MORGAN.GetFingerprint(mol),
        std_smiles=Chem.MolToSmiles(mol),
        inchikey=Chem.MolToInchiKey(mol),
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--actives", type=Path, required=True)
    ap.add_argument("--pool", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--per-active", type=int, default=50)
    ap.add_argument("--max-tanimoto", type=float, default=0.35)
    ap.add_argument("--seed", type=int, default=20260906)
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    actives = pd.read_csv(args.actives)
    actives = actives[actives.include_in_enrichment.astype(str).str.upper() == "TRUE"].copy()
    if actives.empty:
        raise SystemExit("no actives flagged include_in_enrichment=TRUE")
    print(f"[decoys] actives in enrichment set: {len(actives)}")

    act = []
    for r in actives.itertuples():
        d = descriptors(r.isomeric_smiles)
        if d is None:
            raise SystemExit(f"active {r.name_canonical} failed descriptor computation")
        d["name"] = r.name_canonical
        act.append(d)
    active_fps = [a["fp"] for a in act]
    active_keys = {a["inchikey"].split("-")[0] for a in act}

    pool = pd.read_csv(args.pool)
    print(f"[decoys] pool rows: {len(pool)}")
    pool_rec = []
    for r in pool.itertuples():
        d = descriptors(r.smiles)
        if d is None:
            continue
        if d["inchikey"].split("-")[0] in active_keys:
            continue  # never let an active leak into its own decoy set
        d["pool_id"] = r.source_id
        d["pool_name"] = r.compound_name
        d["pool_library"] = r.origin_library
        d["pool_lane"] = r.source_lane
        d["pool_smiles"] = r.smiles
        pool_rec.append(d)
    print(f"[decoys] pool usable: {len(pool_rec)}")

    # Max Tanimoto to ANY active -- computed once, reused for every quota.
    maxtan = np.array([max(DataStructs.BulkTanimotoSimilarity(p["fp"], active_fps))
                       for p in pool_rec])
    eligible = maxtan <= args.max_tanimoto
    print(f"[decoys] pool passing Tanimoto <= {args.max_tanimoto} to all actives: "
          f"{int(eligible.sum())} / {len(pool_rec)}")

    P = pd.DataFrame([{k: v for k, v in p.items() if k != "fp"} for p in pool_rec])
    P["max_tanimoto_to_any_active"] = maxtan
    P["eligible"] = eligible

    taken: set[int] = set()
    rows = []
    for a in act:
        need = args.per_active
        for tier_idx, (dmw, dlp, dtp, dhbd, dhba, drot) in enumerate(TIERS):
            if need <= 0:
                break
            m = (P.eligible
                 & ~P.index.isin(taken)
                 & (P.formal_charge == a["formal_charge"])
                 & ((P.mw - a["mw"]).abs() <= dmw)
                 & ((P.clogp - a["clogp"]).abs() <= dlp)
                 & ((P.tpsa - a["tpsa"]).abs() <= dtp)
                 & ((P.hbd - a["hbd"]).abs() <= dhbd)
                 & ((P.hba - a["hba"]).abs() <= dhba)
                 & ((P.rotb - a["rotb"]).abs() <= drot))
            cand = np.array(P.index[m].to_numpy(), copy=True)
            if len(cand) == 0:
                continue
            rng.shuffle(cand)
            pick = cand[:need]
            for i in pick:
                taken.add(int(i))
                rows.append(dict(pool_index=int(i), matched_active=a["name"],
                                 match_tier=tier_idx,
                                 tier_window=f"MW+-{dmw} clogP+-{dlp} TPSA+-{dtp} "
                                             f"HBD+-{dhbd} HBA+-{dhba} rotB+-{drot} charge=exact"))
            need -= len(pick)
        if need > 0:
            print(f"[decoys] WARNING {a['name']}: only "
                  f"{args.per_active - need}/{args.per_active} decoys found even at "
                  f"the widest tier")

    sel = pd.DataFrame(rows).merge(P.reset_index().rename(columns={"index": "pool_index"}),
                                   on="pool_index", how="left")
    sel = sel.drop(columns=["eligible"])
    sel.insert(0, "cand_id", [f"BD{i:05d}" for i in range(1, len(sel) + 1)])
    sel["mol_class"] = "DECOY"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    sel.to_csv(args.out, index=False)

    summary = dict(
        generated_utc=datetime.now(timezone.utc).isoformat(),
        pool_file=str(args.pool), pool_rows=int(len(pool)),
        pool_usable=int(len(pool_rec)),
        actives_used=int(len(act)),
        per_active_target=args.per_active,
        max_tanimoto_threshold=args.max_tanimoto,
        fingerprint="ECFP4 / Morgan radius 2, 2048 bits, RDKit rdFingerprintGenerator",
        pool_passing_tanimoto=int(eligible.sum()),
        decoys_selected=int(len(sel)),
        decoys_per_active=sel.matched_active.value_counts().to_dict(),
        tier_counts=sel.match_tier.value_counts().sort_index().to_dict(),
        tier_definitions={str(i): dict(zip(
            ["dMW", "dclogP", "dTPSA", "dHBD", "dHBA", "drotB"], t))
            for i, t in enumerate(TIERS)},
        decoy_max_tanimoto_observed=float(sel.max_tanimoto_to_any_active.max()),
        decoy_library_counts=sel.pool_library.value_counts().to_dict(),
        seed=args.seed,
        note=("Decoys are real catalogue/database molecules, not enumerated. "
              "They are presumed inactive because no PAR2 activity is recorded "
              "for them, which is an assumption, not a measurement."),
    )
    args.out.with_suffix(".summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(json.dumps({k: v for k, v in summary.items() if k != "decoys_per_active"}, indent=2,
                     default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
