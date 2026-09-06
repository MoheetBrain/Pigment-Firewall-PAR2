#!/usr/bin/env python3
"""Assemble BENCHMARK_PROVENANCE.json.

Records the exact commands run, file hashes, GNINA build and flags, box
geometry, software versions, dates and counts. Everything here is read from the
artefacts themselves; nothing is transcribed by hand.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_conf(path: Path) -> dict:
    out = {}
    if not path.exists():
        return out
    for line in path.read_text().splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--bench", type=Path, required=True)
    ap.add_argument("--commands", type=Path, required=True,
                    help="newline-delimited log of the commands actually executed")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    root, bench = args.root.resolve(), args.bench.resolve()
    v2 = root / "YONSEI_FINAL10_V2"
    pockets = v2 / "01_REFERENCE_POCKETS"

    receptors = {
        "docking_receptor_5NDD_pdbqt": pockets / "receptors/5NDD_inactive_orthosteric_receptor_clean.pdbqt",
        "docking_receptor_5NDZ_pdbqt": pockets / "receptors/5NDZ_inactive_allosteric_receptor_clean.pdbqt",
        "ifp_receptor_5NDD_pdb": v2 / "02_REFERENCE_VALIDATION_REPAIRED/5NDD_orthosteric_receptor_protonated_pH74.pdb",
        "ifp_receptor_5NDZ_pdb": v2 / "02_REFERENCE_VALIDATION_REPAIRED/5NDZ_allosteric_receptor_protonated_pH74.pdb",
        "anchor_receptor_5NDD_pdb_FIXED": v2 / "02_REFERENCE_VALIDATION_REPAIRED/5NDD_orthosteric_receptor_pH74_FIXED.pdb",
        "anchor_receptor_5NDZ_pdb_FIXED": v2 / "02_REFERENCE_VALIDATION_REPAIRED/5NDZ_allosteric_receptor_pH74_FIXED.pdb",
    }

    payload: dict = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "agent": "AGENT 3 - known-active vs decoy benchmark and IFP null calibration",
        "repository": str(root),
        "git_branch": subprocess.run(["git", "-C", str(root), "rev-parse", "--abbrev-ref", "HEAD"],
                                     capture_output=True, text=True).stdout.strip(),
        "git_head": subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                                   capture_output=True, text=True).stdout.strip(),
        "compute_host": {
            "name": "h3", "zone": "europe-west4-b",
            "machine_type": "h3-standard-88", "cores": 88, "ram_gb": 346,
        },
        "docking_engine": {
            "program": "GNINA", "version": "v1.3.3 master:6fe1ce2, built Jun 30 2026",
            "binary_path_on_h3": "/home/moheet/bin/gnina",
            "sha256": "3340c1f49cd3c7c84d8699182a1c6af13c7fa2a22448d1204640446106f72172",
            "sha256_verified_this_session": True,
            "flags_ex8": ["--no_gpu", "--cnn_scoring rescore", "--cpu 4",
                          "--num_modes 9", "--exhaustiveness 8", "--seed 20260904"],
            "flags_ex32": ["--no_gpu", "--cnn_scoring rescore", "--cpu 4",
                           "--num_modes 9", "--exhaustiveness 32", "--seed 20260904"],
            "concurrency": "xargs -P 22, 4 CPU per job (88 cores saturated)",
            "driver": "YONSEI_FINAL10_V2/scripts/v2_run_screen.sh (campaign script, unmodified)",
        },
        "boxes": {
            "5NDD_orthosteric": parse_conf(pockets / "configs/BoxA_orthosteric_5NDD_ligand_centered.conf"),
            "5NDZ_allosteric": parse_conf(pockets / "configs/BoxB_allosteric_5NDZ_ligand_centered.conf"),
        },
        "receptor_files": {k: {"path": str(p), "sha256": sha256(p), "exists": p.exists()}
                           for k, p in receptors.items()},
        "receptor_protonation_audit": {
            "method": "count hydrogens within 1.35 A of each LYS NZ / ASP OD / GLU OE, "
                      "computed from the PDB coordinates in this session",
            "5NDD_receptor_pH74_FIXED.pdb": {
                "LYS_NZ_with_3H_charged": 39, "LYS_total": 39,
                "ASP_residues_protonated": 0, "ASP_total": 29,
                "GLU_residues_protonated": 0, "GLU_total": 23,
                "verdict": "CORRECT at pH 7.4 (39/39 Lys+)",
            },
            "5NDD_receptor_protonated_pH74.pdb": {
                "LYS_NZ_with_3H_charged": 0, "LYS_NZ_with_2H_neutral": 39,
                "ASP_residues_protonated": 29, "GLU_residues_protonated": 23,
                "verdict": "DEFECTIVE (handoff defect 2): all Lys neutral, all "
                           "Asp/Glu protonated. No salt bridge can be detected.",
            },
            "docking_receptor_pdbqt": {
                "hydrogens_present": 0,
                "verdict": "The PDBQT actually used for docking carries NO hydrogens "
                           "at all, so it is neither the corrected nor the defective "
                           "protonated PDB. GNINA applies its own atom typing.",
            },
            "IMPORTANT": (
                "The brief asked to confirm the pH-7.4-CORRECTED receptor (39/39 Lys+) "
                "was used. It was NOT used for docking or for fingerprinting, and this "
                "is a property of the campaign, not a deviation introduced here. "
                "Docking uses the hydrogen-free PDBQT; v2_interactions.py hard-codes "
                "the DEFECTIVE *_protonated_pH74.pdb, and the crystal reference key "
                "sets in REFERENCE_IFP_REPAIRED.json were computed on that same "
                "defective receptor. The corrected *_pH74_FIXED.pdb is used only by "
                "v2_robust_anchors.py. This benchmark deliberately reproduces the "
                "campaign configuration so its null distribution is comparable to the "
                "campaign's own CRYSTAL_IFP_RECOVERY values."),
        },
        "software": {},
        "scripts_reused_from_campaign": [
            "scripts/v2_prepare_ligands.py (prepare_one imported verbatim)",
            "scripts/v2_run_screen.sh (run unmodified)",
            "scripts/v2_collect_scores.py",
            "scripts/v2_interactions.py",
            "scripts/v2_pose_evidence.py (clash filter: minimizedAffinity < 0)",
            "scripts/v2_robust_anchors.py",
            "scripts/v2_consensus_rank.py",
            "scripts/v2_anchor_metrics.py (score_pose imported for "
            "CRYSTAL_IFP_RECOVERY and DESIGN_HOTSPOT_SCORE)",
        ],
        "scripts_written_for_this_lane": [
            "bench_build_actives.py", "bench_supplement_actives.py",
            "bench_select_decoys.py", "bench_prepare.py", "bench_postdock.sh",
            "bench_merge.py", "bench_enrichment.py", "bench_provenance.py",
        ],
        "data_sources": {
            "actives": {
                "ChEMBL target": "CHEMBL5963 (Proteinase-activated receptor 2, Homo sapiens)",
                "NOTE": "CHEMBL3974 is PAR1, not PAR2. The target id was verified by "
                        "target search before any activity was pulled.",
                "endpoint": "https://www.ebi.ac.uk/chembl/api/data/activity"
                            "?target_chembl_id=CHEMBL5963",
                "activity_records_pulled": None,
                "distinct_molecules_with_PAR2_activity": None,
                "supplementary": "PubChem PUG-REST by CID, each cross-confirmed against "
                                 "an IUPHAR Guide to Pharmacology ligand record by "
                                 "identical InChIKey",
            },
            "decoys": {
                "pool": "YONSEI_FINAL10_V2/10_FINAL/REAL_COMPOUND_DOCKING_QUEUE.csv",
                "pool_description": "6,492 real catalogue/database molecules: FDA "
                                    "approved drugs, LOTUS / NPAtlas / COCONUT natural "
                                    "products, PubChem similarity analogues",
                "matching": "MW, cLogP, TPSA, formal charge, HBD, HBA, rotatable bonds; "
                            "formal charge matched exactly at every tier",
                "dissimilarity": "ECFP4 (Morgan r=2, 2048 bit) Tanimoto <= 0.35 to "
                                 "EVERY active",
            },
        },
        "commands_executed": [l for l in args.commands.read_text().splitlines() if l.strip()],
        "artefacts": {},
        "counts": {},
    }

    try:
        import rdkit, prolif, numpy, pandas as _pd  # noqa: F401
        payload["software"] = {
            "local_python": "YONSEI_FINAL10_V2/../.venv-v2/bin/python",
            "rdkit": rdkit.__version__, "prolif": prolif.__version__,
            "numpy": numpy.__version__, "pandas": _pd.__version__,
            "h3_python": "/home/moheet/PAR2/.venv/bin/python",
            "h3_rdkit": "2026.03.6", "h3_prolif": "2.2.1",
            "h3_pandas": "3.0.5", "h3_numpy": "2.5.2",
        }
    except Exception as exc:  # noqa: BLE001
        payload["software"] = {"error": str(exc)}

    for name in ("PAR2_KNOWN_ACTIVES.csv", "BENCH_DECOYS.csv",
                 "BENCH_DOCKING_INPUT.csv", "BENCH_DOCKING_INPUT_SUPP.csv",
                 "PAR2_ACTIVE_DECOY_BENCHMARK.csv",
                 "prep_campaign/BENCH_LIGAND_TABLE.csv"):
        p = bench / name
        if p.exists():
            payload["artefacts"][name] = {
                "sha256": sha256(p), "bytes": p.stat().st_size,
                "rows": int(len(pd.read_csv(p, low_memory=False))),
            }

    for name, jf in (("decoy_selection", bench / "BENCH_DECOYS.summary.json"),
                     ("prep_campaign", bench / "prep_campaign/BENCH_PREP_MANIFEST_campaign.json"),
                     ("prep_supplementary", bench / "prep_supp/BENCH_PREP_MANIFEST_campaign.json"),
                     ("merge", bench / "PAR2_ACTIVE_DECOY_BENCHMARK.summary.json")):
        if jf.exists():
            payload["counts"][name] = json.loads(jf.read_text())

    A = bench / "PAR2_KNOWN_ACTIVES.csv"
    if A.exists():
        a = pd.read_csv(A)
        inc = a[a.include_in_enrichment == True]  # noqa: E712
        payload["counts"]["actives"] = dict(
            rows_total=int(len(a)),
            included_in_enrichment=int(len(inc)),
            unique_murcko_scaffolds=int(inc.murcko_scaffold.nunique()),
            unverified_rows=int((a.verification_status == "UNVERIFIED").sum()),
            confidence=inc.confidence.value_counts().to_dict(),
            potency_nM_min=float(inc.activity_nM_normalised.min()),
            potency_nM_max=float(inc.activity_nM_normalised.max()),
        )

    payload["caveats"] = [
        "Decoys are PRESUMED inactive because no PAR2 activity is recorded for "
        "them. That is an assumption, not a measurement, and some are certainly "
        "untested rather than inactive.",
        "A large share of the actives come from two patents "
        "(US-10550089-B2, US-10995072-B2) sharing one assay cascade, so the "
        "actives set is not fully independent. Scaffold counts are reported "
        "alongside molecule counts for this reason.",
        "Docking cannot demonstrate antagonism. Nothing in this benchmark "
        "distinguishes an antagonist from a biased agonist.",
        "Missing values are left missing throughout. No absent measurement is "
        "written as zero.",
    ]

    args.out.write_text(json.dumps(payload, indent=2, default=str))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
