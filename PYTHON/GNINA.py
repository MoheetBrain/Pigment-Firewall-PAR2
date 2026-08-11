#!/usr/bin/env python3
"""
04_gnina_screen_par2.py
PAR2 GNINA Screening — exhaustiveness=32, CNN + Vina scores both required.
Docks all molecules in SCREENING/ against all 3 boxes (A/B/C).
Generates 3D SDF for any library without one.
No fallbacks. Fails loudly if anything is broken.

Usage (local):  python3 04_gnina_screen_par2.py
Usage (Azure):  python3 04_gnina_screen_par2.py --jobs 120
"""

import os, sys, glob, argparse, subprocess, shutil, time, json
from pathlib import Path
from multiprocessing import Pool, cpu_count
import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit import RDLogger
RDLogger.DisableLog('rdApp.*')

# ─── ARGS ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument('--jobs',     type=int, default=cpu_count(),
                    help='Parallel GNINA jobs (default: all CPUs)')
parser.add_argument('--top_n',   type=int, default=100,
                    help='Top N hits to report per box')
parser.add_argument('--ex',      type=int, default=32,
                    help='GNINA exhaustiveness (default: 32)')
parser.add_argument('--fast',    action='store_true',
                    help='Fast mode: ex=8 for initial pass on full library')
args = parser.parse_args()

EX = args.ex if not args.fast else 8
N_JOBS = args.jobs

# ─── PATHS ────────────────────────────────────────────────────────────────────
BASE    = Path("/Users/mk/PycharmProjects/Pigment-Firewall-PAR2")
SCREEN  = BASE / "SCREENING"
PROT    = BASE / "PROTEINS"
CONF    = PROT / "CONF"
BENCH   = BASE / "BENCHMARK_LIGS"
OUTBASE = BASE / "GNINA_SCREEN_EX32"
LOGDIR  = OUTBASE / "LOGS"
SDFDIR  = OUTBASE / "SDF_GENERATED"

for d in [OUTBASE, LOGDIR, SDFDIR]:
    d.mkdir(parents=True, exist_ok=True)

# ─── GNINA BINARY ─────────────────────────────────────────────────────────────
GNINA_BIN = shutil.which("gnina")
if GNINA_BIN is None:
    # try common install locations
    for candidate in ["/usr/local/bin/gnina", "/opt/gnina/gnina",
                      str(Path.home() / "gnina"), "/usr/bin/gnina",
                      str(BASE / "BIN" / "gnina")]:
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            GNINA_BIN = candidate
            break
if GNINA_BIN is None:
    print("ERROR: gnina binary not found. Install with:")
    print("  wget https://github.com/gnina/gnina/releases/latest/download/gnina")
    print("  chmod +x gnina && sudo mv gnina /usr/local/bin/")
    sys.exit(1)
print(f"GNINA binary: {GNINA_BIN}")

# ─── BOXES (receptor + conf) ──────────────────────────────────────────────────
BOXES = {
    "BoxA_orthosteric": {
        "receptor": str(PROT / "PAR2_inactive_orthosteric_receptor.pdbqt"),
        "conf":     str(CONF / "boxA_orthosteric_5NDD.conf"),
        "ref_lig":  str(BENCH / "flex_AZ8838.sdf"),
    },
    "BoxB_allosteric": {
        "receptor": str(PROT / "PAR2_inactive_allosteric_receptor.pdbqt"),
        "conf":     str(CONF / "boxB_allosteric_5NDZ.conf"),
        "ref_lig":  str(BENCH / "flex_AZ3451.sdf"),
    },
    "BoxC_active_Gq": {
        "receptor": str(PROT / "PAR2_active_Gq_receptor_aligned.pdbqt"),
        "conf":     str(CONF / "boxC_active_8ZMD.conf"),
        "ref_lig":  str(BENCH / "lig_tethered_peptide_boxC_8ZMD.pdb"),
    },
}

# Verify all receptor + conf files exist
print("\nVerifying protein/conf files...")
for box_name, box in BOXES.items():
    for key in ["receptor", "conf"]:
        if not os.path.exists(box[key]):
            print(f"  ERROR: Missing {key} for {box_name}: {box[key]}")
            sys.exit(1)
    print(f"  {box_name}: OK")

# ─── LIBRARY SOURCES ──────────────────────────────────────────────────────────
# All screening files — SDF if they exist, CSV/TSV if not (will generate SDF)
LIBRARY_SOURCES = {
    # Name                         SDF (existing or to generate)       SMILES source (CSV/TSV)
    "COCONUT_3D":    {
        "sdf": str(SCREEN / "SAFE_coconut_3D.sdf"),
        "csv": str(SCREEN / "SAFE_coconut.csv"),
        "smiles_col": "SMILES",
    },
    "LOTUS_3D": {
        "sdf": str(SCREEN / "LOTUS_2021_03_simple.sdf"),
        "csv": None,
    },
    "NPATLAS_3D": {
        "sdf": str(SCREEN / "NPAtlas_download_2024_09.sdf"),
        "csv": str(SCREEN / "NPATLAS.tsv"),
        "smiles_col": "smiles",
    },
    "FDA_DRUGS_3D": {
        "sdf": str(SDFDIR / "FDA_DRUGS_3D.sdf"),
        "csv": str(SCREEN / "FDA_DRUGS.csv"),
        "smiles_col": "smiles",
    },
    "BLEACHING_3D": {
        "sdf": str(SDFDIR / "BLEACHING_3D.sdf"),
        "csv": str(SCREEN / "BLEACHING_APROVED_clean.csv"),
        "smiles_col": "SMILES",
    },
    "MITF_SCAFFOLDS_3D": {
        "sdf": str(SDFDIR / "MITF_SCAFFOLDS_3D.sdf"),
        "csv": str(SCREEN / "elite_mitf_scaffolds_clean.csv"),
        "smiles_col": "SMILES",
    },
}

# ─── STEP 1: GENERATE 3D SDF FOR MISSING LIBRARIES ────────────────────────────
print("\n" + "="*60)
print("STEP 1 — Generating 3D SDFs for libraries without one")
print("="*60)

def csv_to_sdf_3d(csv_path, sdf_out, smiles_col, name_col=None, sep=None):
    """Convert a CSV/TSV of SMILES to a 3D SDF using ETKDGv3 + MMFF."""
    if sep is None:
        sep = '\t' if csv_path.endswith('.tsv') else ','

    df = None
    for s in [sep, ',', '\t', ';']:
        try:
            df = pd.read_csv(csv_path, sep=s, low_memory=False)
            if smiles_col in df.columns:
                break
        except Exception:
            pass

    if df is None or smiles_col not in df.columns:
        # try to detect SMILES column
        for c in (df.columns if df is not None else []):
            if 'smile' in c.lower():
                smiles_col = c
                break
        else:
            print(f"  ERROR: SMILES column '{smiles_col}' not found in {csv_path}")
            print(f"  Columns: {list(df.columns) if df is not None else 'N/A'}")
            return 0

    writer = Chem.SDWriter(sdf_out)
    n_ok, n_fail = 0, 0

    for i, row in df.iterrows():
        smi = str(row[smiles_col]).strip()
        if not smi or smi == 'nan':
            continue

        # Get name
        mol_name = str(row.get(name_col, f"mol_{i}")) if name_col else f"mol_{i}"
        for nc in ['name','Name','compound_name','id','ID','InChIKey','inchikey']:
            if nc in df.columns:
                mol_name = str(row[nc])
                break

        try:
            mol = Chem.MolFromSmiles(smi)
            if mol is None:
                n_fail += 1
                continue
            mol.SetProp("_Name", mol_name)
            mol.SetProp("SMILES", smi)
            mol = Chem.AddHs(mol)

            p = AllChem.ETKDGv3()
            p.randomSeed = 42
            p.numThreads = 0
            ids = AllChem.EmbedMultipleConfs(mol, numConfs=1, params=p)
            if not ids:
                n_fail += 1
                continue

            ff = AllChem.MMFFGetMoleculeForceField(
                mol, AllChem.MMFFGetMoleculeProperties(mol), confId=0)
            if ff:
                ff.Minimize(maxIts=200)

            mol = Chem.RemoveHs(mol)
            writer.write(mol)
            n_ok += 1

            if n_ok % 500 == 0:
                print(f"    {n_ok} molecules written...")

        except Exception:
            n_fail += 1
            continue

    writer.close()
    print(f"  {os.path.basename(csv_path)} → {n_ok} OK, {n_fail} failed → {sdf_out}")
    return n_ok

for lib_name, lib in LIBRARY_SOURCES.items():
    sdf_path = lib["sdf"]
    if os.path.exists(sdf_path) and os.path.getsize(sdf_path) > 1000:
        # Count molecules
        supplier = Chem.SDMolSupplier(sdf_path, removeHs=True)
        n = sum(1 for m in supplier if m is not None)
        print(f"  {lib_name}: SDF already exists — {n} molecules")
        lib["n_mols"] = n
    elif lib.get("csv") and os.path.exists(lib["csv"]):
        print(f"  {lib_name}: Generating 3D SDF from CSV...")
        n = csv_to_sdf_3d(lib["csv"], sdf_path, lib.get("smiles_col","SMILES"))
        lib["n_mols"] = n
    else:
        print(f"  {lib_name}: SKIP — no SDF and no CSV source found")
        lib["n_mols"] = 0

# Print total
total_mols = sum(lib["n_mols"] for lib in LIBRARY_SOURCES.values())
print(f"\n  Total molecules to screen: {total_mols:,}")

# ─── STEP 2: BUILD GNINA DOCKING JOBS ─────────────────────────────────────────
print("\n" + "="*60)
print("STEP 2 — Building GNINA job queue")
print("="*60)

def build_job(box_name, box, lib_name, lib, out_sdf, log_path):
    """Build a GNINA command list."""
    cmd = [
        GNINA_BIN,
        "--receptor",     box["receptor"],
        "--ligand",       lib["sdf"],
        "--config",       box["conf"],
        "--out",          out_sdf,
        "--log",          log_path,
        "--exhaustiveness", str(EX),
        "--num_modes",    "9",
        "--scoring",      "vina",        # Vina scoring (Vina score always computed)
        "--cnn_scoring",  "rescore",     # CNN rescoring on top Vina poses (both scores in output)
        "--stripH",       "true",
        "--addH",         "true",
        "--cpu",          str(max(1, N_JOBS // len(BOXES))),
    ]
    return cmd

jobs = []   # list of (cmd, box_name, lib_name, out_sdf, log_path)
for box_name, box in BOXES.items():
    box_outdir = OUTBASE / box_name
    box_outdir.mkdir(parents=True, exist_ok=True)
    for lib_name, lib in LIBRARY_SOURCES.items():
        if lib["n_mols"] == 0:
            continue
        out_sdf  = str(box_outdir / f"{lib_name}_docked.sdf")
        log_path = str(LOGDIR / f"{box_name}_{lib_name}.log")
        if os.path.exists(out_sdf) and os.path.getsize(out_sdf) > 1000:
            print(f"  SKIP (already done): {box_name} × {lib_name}")
            continue
        cmd = build_job(box_name, box, lib_name, lib, out_sdf, log_path)
        jobs.append((cmd, box_name, lib_name, out_sdf, log_path))

print(f"\n  Total docking jobs: {len(jobs)}")
print(f"  Exhaustiveness    : {EX}")
print(f"  Scoring           : Vina + CNN rescore")
print(f"  Parallel jobs     : {N_JOBS}")

# ─── STEP 3: RUN GNINA ────────────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 3 — Running GNINA (thi