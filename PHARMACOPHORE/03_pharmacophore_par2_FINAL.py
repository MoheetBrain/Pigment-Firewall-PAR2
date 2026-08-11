#!/usr/bin/env python3
"""
03_pharmacophore_par2.py  — v2
PAR2 Ligand-Based Ensemble Pharmacophore Builder

Core fix vs v1: every conformer is CrippenO3A-aligned to the highest-pIC50
reference before clustering, so all 3D feature points live in one coordinate
frame and the 2Å distance threshold is physically meaningful.

Clustering is done per feature type (Donor with Donor, Acceptor with Acceptor,
etc.) — not across the whole pooled cloud — to prevent cross-type merging.
"""

import os, sys, json, glob, warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from collections import Counter, defaultdict
from scipy.cluster.hierarchy import fcluster, linkage

from rdkit import Chem, RDConfig
from rdkit.Chem import AllChem, rdMolDescriptors, ChemicalFeatures
from rdkit.Chem.SaltRemover import SaltRemover
from rdkit.Chem.MolStandardize import rdMolStandardize
from rdkit.Chem.EnumerateStereoisomers import EnumerateStereoisomers, StereoEnumerationOptions
from rdkit import RDLogger
RDLogger.DisableLog("rdApp.*")

# ── CONFIG ──────────────────────────────────────────────────────────────────────
ACTIVE_PICSO_CUT    = 5.0    # pIC50 >= 5  → active  (≤10 µM)
INACTIVE_PICSO_MAX  = 4.0    # pIC50 < 4   → high-contrast inactive
CONSENSUS_THRESHOLD = 0.60   # cluster must span ≥60 % of actives
EXCLUSION_THRESHOLD = 0.70   # cluster must span ≥70 % of inactives
CLUSTER_DIST        = 4.0    # Å — relaxed for structurally diverse ChEMBL set
#                              Diagnostic: feature spread ~3.5–4 Å std after
#                              CrippenO3A alignment (mean score 0.51). At 2 Å
#                              no cluster clears 60 %; at 4 Å Donor=87 %,
#                              Acceptor=83 %, Hydrophobe=58 % (top-60 actives).
N_CONFORMERS        = 10
MAX_STEREO          = 4
MAX_INACTIVES       = 50

OUTDIR   = "/Users/mk/PycharmProjects/Pigment-Firewall-PAR2/PHARMACOPHORE"
DATA_DIR = "/Users/mk/PycharmProjects/Pigment-Firewall-PAR2/XGBOOST_RANDOM_FORREST"

# Controls verified from ChEMBL dataset
CONTROLS = {
    "AZ3451": "C[C@@H](C1CCCCC1)n1c(-c2cc3c(cc2Br)OCO3)nc2cc(C(=O)Nc3ccc(C#N)cc3)ccc21",
    "AZ8838": "CCCc1cc(F)ccc1[C@H](O)c1ncc[nH]1",
    "GB83":   "CC[C@H](C)[C@H](NC(=O)[C@H](CC1CCCCC1)NC(=O)c1ccno1)C(=O)N1CCC2(CCc3ccccc32)CC1",
}
CONTROL_MIN = {"AZ3451": 4, "AZ8838": 4, "GB83": 3}

FEATURE_TYPES = [
    "Donor", "Acceptor", "Hydrophobe", "LumpedHydrophobe",
    "Aromatic", "PosIonizable", "NegIonizable",
]
FEATURE_COLOUR = {
    "Donor": "blue", "Acceptor": "red",
    "Hydrophobe": "yellow", "LumpedHydrophobe": "yellow",
    "Aromatic": "orange", "PosIonizable": "cyan",
    "NegIonizable": "pink", "Exclusion": "grey",
}

os.makedirs(OUTDIR, exist_ok=True)
failed_log: list[str] = []

# ── FEATURE FACTORY ─────────────────────────────────────────────────────────────
FDEF = os.path.join(RDConfig.RDDataDir, "BaseFeatures.fdef")
if not os.path.exists(FDEF):
    sys.exit(f"ERROR: BaseFeatures.fdef not found at {FDEF}")
FACTORY = ChemicalFeatures.BuildFeatureFactory(FDEF)
print(f"Feature factory: {FDEF}")


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1 — LOAD ALL DATA
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("STEP 1 — Loading ChEMBL PAR2 data (no filters stripped)")
print("="*60)

KEEP_TYPES = {"IC50", "Ki", "Inhibition", "EC50"}
KEEP_UNITS = {"nM", "uM", "M"}


def to_nm(value, units):
    try:
        v = float(value)
    except Exception:
        return np.nan
    u = str(units).strip()
    if u == "uM":  return v * 1_000.0
    if u == "M":   return v * 1e9
    return v  # nM


def load_csv(path):
    for sep in [";", ",", "\t"]:
        try:
            df = pd.read_csv(path, sep=sep, low_memory=False)
            if len(df.columns) > 5:
                return df
        except Exception:
            pass
    return None


def col(df, *candidates):
    """First column whose lower-stripped name is in candidates."""
    for c in df.columns:
        if c.strip().lower() in candidates:
            return c
    return None


patterns = [
    os.path.join(DATA_DIR, "chembl_par2_raw_bioactivities.csv"),
    os.path.join(DATA_DIR, "**", "*par2*.csv"),
    os.path.join(DATA_DIR, "**", "*PAR2*.csv"),
    os.path.join(DATA_DIR, "**", "*chembl*.csv"),
]

frames, seen = [], set()
for pat in patterns:
    for fpath in sorted(glob.glob(pat, recursive=True)):
        if fpath in seen:
            continue
        seen.add(fpath)
        df_raw = load_csv(fpath)
        if df_raw is None:
            continue
        smi_c  = col(df_raw, "smiles", "canonical_smiles", "smi")
        type_c = col(df_raw, "standard type", "standard_type")
        val_c  = col(df_raw, "standard value", "standard_value")
        unit_c = col(df_raw, "standard units", "standard_units")
        rel_c  = col(df_raw, "standard relation", "standard_relation")
        if not (smi_c and type_c and val_c and unit_c):
            print(f"  SKIP (missing cols): {os.path.basename(fpath)}")
            continue
        df_raw = df_raw.rename(columns={smi_c: "Smiles", type_c: "Standard Type",
                                         val_c: "Standard Value", unit_c: "Standard Units"})
        if rel_c:
            df_raw = df_raw.rename(columns={rel_c: "Standard Relation"})
        else:
            df_raw["Standard Relation"] = "="
        frames.append(df_raw)
        print(f"  Loaded {len(df_raw):5d} rows — {os.path.basename(fpath)}")

if not frames:
    sys.exit("ERROR: No valid bioactivity CSV found.")

big = pd.concat(frames, ignore_index=True, sort=False)
big = big[big["Standard Type"].isin(KEEP_TYPES)]
big = big[big["Standard Units"].isin(KEEP_UNITS)]
big["Standard Value"] = pd.to_numeric(big["Standard Value"], errors="coerce")
big = big.dropna(subset=["Standard Value"])
big = big[big["Standard Value"] > 0]
big["value_nM"] = big.apply(lambda r: to_nm(r["Standard Value"], r["Standard Units"]), axis=1)
big = big[big["value_nM"].notna() & (big["value_nM"] > 0)]
big["pIC50"] = (-np.log10(big["value_nM"] * 1e-9)).clip(3.0, 12.0)
big = big[big["Smiles"].notna() & (big["Smiles"].str.strip() != "")]
big["Standard Relation"] = big["Standard Relation"].fillna("=").astype(str).str.strip().str.strip("'\"")
big["Active"] = (big["pIC50"] >= ACTIVE_PICSO_CUT) & (~big["Standard Relation"].str.contains(">", na=False))

print(f"\n  Total rows (typed+units): {len(big)}")
print(f"  Active  (pIC50≥{ACTIVE_PICSO_CUT}): {big['Active'].sum()}")
print(f"  Inactive              : {(~big['Active']).sum()}")


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2 — STANDARDISE SMILES + STEREO ENUMERATION
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("STEP 2 — Standardising SMILES")
print("="*60)

_remover = SaltRemover()


def standardise(smi: str) -> list[str]:
    mol = Chem.MolFromSmiles(str(smi))
    if mol is None:
        return []
    rw = Chem.RWMol(mol)
    for idx in sorted([a.GetIdx() for a in rw.GetAtoms() if a.GetAtomicNum() == 0], reverse=True):
        rw.RemoveAtom(idx)
    mol = _remover.StripMol(rw.GetMol(), dontRemoveEverything=True)
    if mol is None or mol.GetNumAtoms() == 0:
        return []
    mol = Chem.MolFromSmiles(Chem.MolToSmiles(mol, isomericSmiles=True))
    if mol is None:
        return []
    unassigned = sum(1 for _, s in Chem.FindMolChiralCenters(mol, includeUnassigned=True) if s == "?")
    if unassigned > 0:
        opts = StereoEnumerationOptions(unique=True, maxIsomers=MAX_STEREO)
        return [Chem.MolToSmiles(iso, isomericSmiles=True)
                for iso in list(EnumerateStereoisomers(mol, options=opts))[:MAX_STEREO]]
    return [Chem.MolToSmiles(mol, isomericSmiles=True)]


records = []
for _, row in big.iterrows():
    for si, smi in enumerate(standardise(str(row["Smiles"]))):
        r = row.to_dict()
        r["canon_smiles"] = smi
        r["stereo_idx"]   = si
        records.append(r)

df_std = (pd.DataFrame(records)
            .sort_values("pIC50", ascending=False)
            .drop_duplicates(subset=["canon_smiles"])
            .reset_index(drop=True))

print(f"  Unique standardised SMILES: {len(df_std)}")

actives   = df_std[df_std["Active"]].sort_values("pIC50", ascending=False).reset_index(drop=True)
inactives = df_std[~df_std["Active"]].copy()
hi_contrast = inactives[inactives["pIC50"] < INACTIVE_PICSO_MAX]
if len(hi_contrast) < 5:
    hi_contrast = inactives
hi_contrast = (hi_contrast.sort_values("pIC50")
                           .drop_duplicates(subset=["canon_smiles"])
                           .head(MAX_INACTIVES)
                           .reset_index(drop=True))

print(f"  Actives for model      : {len(actives)}")
print(f"  Inactives (neg. model) : {len(hi_contrast)}")


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3 — CONFORMER GENERATION  +  CrippenO3A ALIGNMENT TO REFERENCE
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("STEP 3 — Conformer generation + CrippenO3A alignment to reference")
print("="*60)


def embed_lowest_energy(smi: str, mol_id: str) -> Chem.Mol | None:
    """ETKDGv3 + MMFF, keep lowest-energy conformer, return heavy-atom mol."""
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        failed_log.append(f"{mol_id}\tInvalid SMILES")
        return None
    mol = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.numThreads = 0
    params.enforceChirality = True
    cids = []
    for attempt in range(3):
        params.randomSeed = 42 + attempt * 17
        cids = AllChem.EmbedMultipleConfs(mol, numConfs=N_CONFORMERS, params=params)
        if cids:
            break
    if not cids:
        failed_log.append(f"{mol_id}\tEmbedding failed after 3 attempts")
        return None
    best_e, best_cid = float("inf"), cids[0]
    for cid in cids:
        props = AllChem.MMFFGetMoleculeProperties(mol)
        if props is None:
            continue
        ff = AllChem.MMFFGetMoleculeForceField(mol, props, confId=cid)
        if ff is None:
            continue
        ff.Minimize()
        e = ff.CalcEnergy()
        if e < best_e:
            best_e, best_cid = e, cid
    for cid in cids:
        if cid != best_cid:
            mol.RemoveConformer(cid)
    return Chem.RemoveHs(mol)


def crippen_o3a_align(probe: Chem.Mol, ref: Chem.Mol) -> tuple[Chem.Mol, float]:
    """
    Align probe to ref in-place using CrippenO3A.
    Works on heavy-atom mols (Hs are added/removed internally).
    Returns (aligned_heavy_mol, alignment_score). Score < 0 = failed.
    """
    try:
        probe_h = Chem.AddHs(probe, addCoords=True)
        ref_h   = Chem.AddHs(ref,   addCoords=True)
        p_crip  = rdMolDescriptors._CalcCrippenContribs(probe_h)
        r_crip  = rdMolDescriptors._CalcCrippenContribs(ref_h)
        o3a   = AllChem.GetCrippenO3A(probe_h, ref_h, p_crip, r_crip)
        score = o3a.Align()   # returns float, not tuple
        return Chem.RemoveHs(probe_h), float(score)
    except Exception:
        return probe, -1.0


def build_mol_dict(subset: pd.DataFrame, label: str,
                   ref_mol: Chem.Mol | None = None) -> dict:
    mol_dict, n_fail, n_aligned = {}, 0, 0
    print(f"  [{label}]  n={len(subset)}")
    for i, (_, row) in enumerate(subset.iterrows()):
        mol_id = f"{row['Molecule ChEMBL ID']}_{int(row['stereo_idx'])}"
        mol    = embed_lowest_energy(row["canon_smiles"], mol_id)
        if mol is None:
            n_fail += 1
        else:
            if ref_mol is not None:
                mol, score = crippen_o3a_align(mol, ref_mol)
                if score >= 0:
                    n_aligned += 1
            mol_dict[mol_id] = {"mol": mol, "pIC50": row["pIC50"],
                                 "smiles": row["canon_smiles"]}
        if (i + 1) % 25 == 0:
            print(f"    {i+1}/{len(subset)}  ok={len(mol_dict)}  fail={n_fail}")
    sfx = f"  aligned={n_aligned}" if ref_mol is not None else ""
    print(f"    done — ok={len(mol_dict)}  fail={n_fail}{sfx}")
    return mol_dict


# ── Pass 1: embed actives without alignment to find reference ──────────────────
print("  Pass 1 — embedding actives (finding reference)...")
active_mol_dict = build_mol_dict(actives, "actives pass-1")

# Reference = highest-pIC50 active that embedded
ref_mol = None
for _, row in actives.iterrows():
    cid = f"{row['Molecule ChEMBL ID']}_{int(row['stereo_idx'])}"
    if cid in active_mol_dict:
        ref_mol = active_mol_dict[cid]["mol"]
        print(f"\n  Reference: {cid}  pIC50={row['pIC50']:.2f}")
        print(f"  SMILES   : {row['canon_smiles']}")
        break

if ref_mol is None:
    sys.exit("ERROR: No active molecule embedded successfully.")

# ── Pass 2: re-embed AND align all actives to reference ───────────────────────
print("\n  Pass 2 — embedding + CrippenO3A alignment to reference...")
active_mol_dict = build_mol_dict(actives, "actives pass-2 (aligned)", ref_mol)

# ── Inactives: embed + align to same reference ─────────────────────────────────
inactive_mol_dict = build_mol_dict(hi_contrast, "inactives (aligned)", ref_mol)

n_actives_used  = len(active_mol_dict)
n_inactives_used = len(inactive_mol_dict)


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4 — FEATURE EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("STEP 4 — Pharmacophore feature extraction")
print("="*60)


def extract_features(mol_dict: dict) -> dict:
    feat_dict: dict = {}
    for mol_id, info in mol_dict.items():
        mol = info["mol"]
        if mol.GetNumConformers() == 0:
            continue
        mol_feats = []
        for f in FACTORY.GetFeaturesForMol(mol):
            if f.GetFamily() not in FEATURE_TYPES:
                continue
            pos = f.GetPos()
            mol_feats.append({"type": f.GetFamily(),
                               "x": round(float(pos.x), 4),
                               "y": round(float(pos.y), 4),
                               "z": round(float(pos.z), 4),
                               "atoms": list(f.GetAtomIds())})
        feat_dict[mol_id] = mol_feats
    print(f"  Extracted features from {len(feat_dict)} molecules")
    return feat_dict


active_feat_dict   = extract_features(active_mol_dict)
inactive_feat_dict = extract_features(inactive_mol_dict)


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 5 — CONSENSUS PHARMACOPHORE
# Cluster per feature type in aligned coordinate space, keep ≥60 % clusters.
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("STEP 5 — Consensus pharmacophore (per-type clustering in aligned space)")
print("="*60)


def cluster_by_type(feat_dict: dict, n_total: int,
                    threshold: float, label: str) -> list[dict]:
    by_type: dict = defaultdict(lambda: {"pts": [], "mols": []})
    total_pts = 0
    for mol_id, feats in feat_dict.items():
        for f in feats:
            by_type[f["type"]]["pts"].append([f["x"], f["y"], f["z"]])
            by_type[f["type"]]["mols"].append(mol_id)
            total_pts += 1

    print(f"  [{label}] {total_pts} feature points from {n_total} molecules")

    clusters, cid = [], 0
    for ftype in FEATURE_TYPES:
        d = by_type.get(ftype)
        if d is None or len(d["pts"]) < 2:
            continue
        pts  = np.array(d["pts"])
        mols = np.array(d["mols"])
        Z    = linkage(pts, method="average", metric="euclidean")
        labs = fcluster(Z, t=CLUSTER_DIST, criterion="distance")

        for cl in np.unique(labs):
            mask       = labs == cl
            clust_pts  = pts[mask]
            clust_mols = mols[mask]
            n_uniq     = len(set(clust_mols))
            freq       = n_uniq / n_total
            if freq < threshold:
                continue
            centroid = clust_pts.mean(axis=0)
            clusters.append({
                "cluster_id":   cid,
                "feature_type": ftype,
                "centroid_x":   round(float(centroid[0]), 4),
                "centroid_y":   round(float(centroid[1]), 4),
                "centroid_z":   round(float(centroid[2]), 4),
                "frequency":    round(freq, 4),
                "n_molecules":  n_uniq,
                "type_votes":   {ftype: int(mask.sum())},
            })
            cid += 1

    clusters.sort(key=lambda x: x["frequency"], reverse=True)
    print(f"  [{label}] clusters passing threshold (≥{threshold*100:.0f}%): {len(clusters)}")
    for c in clusters:
        print(f"    [{c['cluster_id']:3d}] {c['feature_type']:20s}"
              f"  freq={c['frequency']:.2f}  n={c['n_molecules']}")
    return clusters


consensus_features = cluster_by_type(
    active_feat_dict, n_actives_used, CONSENSUS_THRESHOLD, "actives"
)


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 6 — NEGATIVE PHARMACOPHORE (exclusion volumes)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("STEP 6 — Exclusion volumes from inactives")
print("="*60)

consensus_xyzs = np.array([[c["centroid_x"], c["centroid_y"], c["centroid_z"]]
                             for c in consensus_features]) if consensus_features else np.empty((0, 3))

raw_exclusion = cluster_by_type(
    inactive_feat_dict, n_inactives_used, EXCLUSION_THRESHOLD, "inactives"
)

exclusion_features = []
for ef in raw_exclusion:
    centroid = np.array([ef["centroid_x"], ef["centroid_y"], ef["centroid_z"]])
    if len(consensus_xyzs) > 0:
        if np.linalg.norm(consensus_xyzs - centroid, axis=1).min() < CLUSTER_DIST:
            continue  # overlaps consensus — skip
    ef["tag"] = "EXCLUSION_VOLUME"
    exclusion_features.append(ef)

print(f"  Exclusion volumes (not overlapping consensus): {len(exclusion_features)}")


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 7 — OUTPUTS
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("STEP 7 — Saving outputs")
print("="*60)


def save_json(obj, fname):
    p = os.path.join(OUTDIR, fname)
    with open(p, "w") as f:
        json.dump(obj, f, indent=2)
    print(f"  Saved: {p}")


save_json(consensus_features, "pharmacophore_consensus.json")
save_json(exclusion_features, "pharmacophore_exclusion.json")

# Feature matrix
matrix_rows = []
for mol_id, feats in active_feat_dict.items():
    row = {"mol_id": mol_id,
           "pIC50":  active_mol_dict[mol_id]["pIC50"],
           "smiles": active_mol_dict[mol_id]["smiles"]}
    counts = Counter(f["type"] for f in feats)
    for ft in FEATURE_TYPES:
        row[ft] = counts.get(ft, 0)
    matrix_rows.append(row)
p = os.path.join(OUTDIR, "pharmacophore_feature_matrix.csv")
pd.DataFrame(matrix_rows).to_csv(p, index=False)
print(f"  Saved: {p}")

# PyMOL script
pml = ["# PAR2 Pharmacophore v2 — aligned ensemble", "from pymol import cmd", ""]
for i, cf in enumerate(consensus_features):
    name   = f"PH_{cf['feature_type']}_{i+1}"
    colour = FEATURE_COLOUR.get(cf["feature_type"], "white")
    x, y, z = cf["centroid_x"], cf["centroid_y"], cf["centroid_z"]
    pml += [f"# {cf['feature_type']}  freq={cf['frequency']:.2f}  n={cf['n_molecules']}",
            f'cmd.pseudoatom("{name}", pos=[{x},{y},{z}], vdw=1.5)',
            f'cmd.show("sphere", "{name}")',
            f'cmd.color("{colour}", "{name}")',
            f'cmd.set("sphere_transparency", 0.3, "{name}")', ""]
for i, ef in enumerate(exclusion_features):
    name = f"EX_{ef['feature_type']}_{i+1}"
    x, y, z = ef["centroid_x"], ef["centroid_y"], ef["centroid_z"]
    pml += [f"# EXCLUSION {ef['feature_type']}  freq={ef['frequency']:.2f}",
            f'cmd.pseudoatom("{name}", pos=[{x},{y},{z}], vdw=1.5)',
            f'cmd.show("sphere", "{name}")',
            f'cmd.color("grey", "{name}")',
            f'cmd.set("sphere_transparency", 0.5, "{name}")', ""]
pml += ['cmd.group("PAR2_Pharmacophore", "PH_* EX_*")', 'cmd.zoom("PAR2_Pharmacophore")']
p = os.path.join(OUTDIR, "pharmacophore_model.pml")
with open(p, "w") as f:
    f.write("\n".join(pml) + "\n")
print(f"  Saved: {p}")

# Consensus match counter
def n_consensus_matches(mol_feats: list, consensus: list) -> int:
    by_type: dict = defaultdict(list)
    for f in mol_feats:
        by_type[f["type"]].append(np.array([f["x"], f["y"], f["z"]]))
    matched = 0
    for cf in consensus:
        pts = by_type.get(cf["feature_type"], [])
        if not pts:
            continue
        c = np.array([cf["centroid_x"], cf["centroid_y"], cf["centroid_z"]])
        if min(np.linalg.norm(pt - c) for pt in pts) <= CLUSTER_DIST:
            matched += 1
    return matched

# Top 3 actives
top3 = []
for mol_id, info in sorted(active_mol_dict.items(),
                            key=lambda kv: kv[1]["pIC50"], reverse=True)[:3]:
    feats   = active_feat_dict.get(mol_id, [])
    n_match = n_consensus_matches(feats, consensus_features)
    top3.append((mol_id, info["pIC50"], n_match))

type_summary = Counter(cf["feature_type"] for cf in consensus_features)
ph_def = " + ".join(f"{v}×{k}" for k, v in type_summary.items())

summary = [
    "=" * 68,
    "PAR2 ENSEMBLE PHARMACOPHORE v2 — SUMMARY",
    "=" * 68,
    f"Actives used for model:   {n_actives_used}",
    f"Inactives (neg. model):   {n_inactives_used}",
    f"Consensus features:       {len(consensus_features)}",
    f"Exclusion volumes:        {len(exclusion_features)}",
    f"Consensus threshold:      {CONSENSUS_THRESHOLD*100:.0f}% of actives",
    f"Cluster distance:         {CLUSTER_DIST} Å",
    f"Alignment:                CrippenO3A to highest-pIC50 active",
    "",
    "CONSENSUS FEATURES (ranked by frequency):",
]
for cf in consensus_features:
    summary.append(
        f"  [{cf['cluster_id']:3d}] {cf['feature_type']:20s}"
        f"  freq={cf['frequency']:.2f}  n={cf['n_molecules']:3d}"
        f"  ({cf['centroid_x']:.2f}, {cf['centroid_y']:.2f}, {cf['centroid_z']:.2f})"
    )
summary += ["", "EXCLUSION VOLUMES:"]
for ef in exclusion_features:
    summary.append(f"  [{ef['cluster_id']:3d}] {ef['feature_type']:20s}"
                   f"  freq={ef['frequency']:.2f}  n={ef['n_molecules']:3d}")
summary += ["", "TOP 3 ACTIVES BY pIC50:"]
for mol_id, pic50, nm in top3:
    summary.append(f"  {mol_id:40s}  pIC50={pic50:.2f}  matches={nm}/{len(consensus_features)}")
summary += ["", "PAR2 PHARMACOPHORE DEFINITION:", f"  {ph_def}", "",
            f"(Active pIC50≥{ACTIVE_PICSO_CUT} | Cluster {CLUSTER_DIST}Å | "
            f"Freq≥{CONSENSUS_THRESHOLD*100:.0f}%)", "=" * 68]

p = os.path.join(OUTDIR, "pharmacophore_summary.txt")
with open(p, "w") as f:
    f.write("\n".join(summary) + "\n")
print(f"  Saved: {p}")

p = os.path.join(OUTDIR, "failed_embed.txt")
with open(p, "w") as f:
    f.write("# mol_id\treason\n")
    for entry in failed_log:
        f.write(entry + "\n")
print(f"  Saved: {p}  ({len(failed_log)} entries)")

print()
print("\n".join(summary))


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 8 — VALIDATION WITH CONTROL COMPOUNDS
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("STEP 8 — Control compound validation")
print("="*60)


def validate_control(name: str, smi: str, consensus: list, min_match: int):
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        print(f"  {name}: invalid SMILES — skip")
        return
    mol_h = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = 2024
    params.numThreads = 0
    cids = AllChem.EmbedMultipleConfs(mol_h, numConfs=10, params=params)
    if not cids:
        print(f"  {name}: embedding failed — skip")
        return
    # pick lowest MMFF energy
    best_e, best_cid = float("inf"), cids[0]
    for cid in cids:
        props = AllChem.MMFFGetMoleculeProperties(mol_h)
        if props is None:
            continue
        ff = AllChem.MMFFGetMoleculeForceField(mol_h, props, confId=cid)
        if ff is None:
            continue
        ff.Minimize()
        e = ff.CalcEnergy()
        if e < best_e:
            best_e, best_cid = e, cid
    for cid in cids:
        if cid != best_cid:
            mol_h.RemoveConformer(cid)
    mol_clean = Chem.RemoveHs(mol_h)

    # Align to same reference as training set
    if ref_mol is not None:
        mol_clean, score = crippen_o3a_align(mol_clean, ref_mol)

    feats = []
    for f in FACTORY.GetFeaturesForMol(mol_clean):
        if f.GetFamily() not in FEATURE_TYPES:
            continue
        pos = f.GetPos()
        feats.append({"type": f.GetFamily(),
                      "x": pos.x, "y": pos.y, "z": pos.z})

    n_match = n_consensus_matches(feats, consensus)
    status  = "PASS" if n_match >= min_match else "FAIL"
    print(f"  {name:10s}  matched {n_match:2d}/{len(consensus):2d}"
          f"  (min={min_match})  [{status}]")
    if status == "FAIL":
        print(f"    NOTE: may reflect scaffold diversity vs reference or "
              f"insufficient active-set representation.")


for ctrl_name, ctrl_smi in CONTROLS.items():
    validate_control(ctrl_name, ctrl_smi, consensus_features, CONTROL_MIN[ctrl_name])

print("\n" + "="*60)
print("DONE — outputs in:", OUTDIR)
print("="*60)
