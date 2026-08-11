#!/usr/bin/env python3
"""Run corrected GNINA reference redocking when a compatible binary exists.

This script intentionally refuses to substitute historical redock outputs and
does not run candidate docking.  It writes only small reference-pose outputs.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


SYSTEMS = {
    "5NDD_AZ8838": {
        "ligand": "01_REFERENCE_POCKETS/ligands/5NDD_AZ8838_crystallographic_clean.sdf",
        "receptor": "01_REFERENCE_POCKETS/receptors/5NDD_inactive_orthosteric_receptor_clean.pdbqt",
        "config": "01_REFERENCE_POCKETS/configs/BoxA_orthosteric_5NDD_ligand_centered.conf",
        "output": "02_REFERENCE_VALIDATION/corrected_redock/5NDD_AZ8838_corrected_gnina_redock.sdf",
        "log": "02_REFERENCE_VALIDATION/corrected_redock/5NDD_AZ8838_corrected_gnina_redock.log",
    },
    "5NDZ_AZ3451": {
        "ligand": "01_REFERENCE_POCKETS/ligands/5NDZ_AZ3451_crystallographic_clean.sdf",
        "receptor": "01_REFERENCE_POCKETS/receptors/5NDZ_inactive_allosteric_receptor_clean.pdbqt",
        "config": "01_REFERENCE_POCKETS/configs/BoxB_allosteric_5NDZ_ligand_centered.conf",
        "output": "02_REFERENCE_VALIDATION/corrected_redock/5NDZ_AZ3451_corrected_gnina_redock.sdf",
        "log": "02_REFERENCE_VALIDATION/corrected_redock/5NDZ_AZ3451_corrected_gnina_redock.log",
    },
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("system", choices=sorted(SYSTEMS))
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--gnina", default=shutil.which("gnina"))
    parser.add_argument("--cpu", type=int, default=1)
    args = parser.parse_args()
    root = args.root.resolve()
    if not args.gnina:
        raise SystemExit("GNINA executable not found; corrected reference redocking is blocked and candidate docking must not run.")
    system = SYSTEMS[args.system]
    output = root / "YONSEI_FINAL10_V2" / system["output"]
    log = root / "YONSEI_FINAL10_V2" / system["log"]
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        args.gnina,
        "--receptor", str(root / "YONSEI_FINAL10_V2" / system["receptor"]),
        "--ligand", str(root / "YONSEI_FINAL10_V2" / system["ligand"]),
        "--config", str(root / "YONSEI_FINAL10_V2" / system["config"]),
        "--out", str(output),
        "--log", str(log),
        "--exhaustiveness", "32",
        "--num_modes", "9",
        "--cnn_scoring", "rescore",
        "--min_rmsd_filter", "2.0",
        "--addH", "true",
        "--cpu", str(max(1, args.cpu)),
    ]
    print("Running:", " ".join(command))
    result = subprocess.run(command, cwd=str(root), text=True)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
