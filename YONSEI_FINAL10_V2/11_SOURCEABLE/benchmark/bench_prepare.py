#!/usr/bin/env python3
"""Prepare the actives/decoys benchmark set for docking.

This is a THIN DRIVER, not a parallel implementation. Structure standardisation,
the approximate pH 7.4 ionisation model, conformer embedding and MMFF
optimisation are all performed by `prepare_one` imported verbatim from
`v2_prepare_ligands.py`, and the shard record format is byte-identical to the
one the campaign screen consumes. Only the input source differs: a benchmark CSV
instead of the de novo queue plus sourceable universe.

Two preparation modes are written so the effect of Defect 7 (the
`TautomerEnumerator().Canonicalize()` call that destroyed stereochemistry in
2,534 campaign designs) can be measured rather than assumed:

  campaign  -- exactly what the campaign ran, Canonicalize included.
  stereo    -- identical except the Canonicalize call is skipped.

Both are audited against the input structure and reported. Nothing is silently
repaired.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, Descriptors, QED, rdMolDescriptors
from rdkit.Chem.MolStandardize import rdMolStandardize

RDLogger.DisableLog("rdApp.*")

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

# Reuse the campaign preparation verbatim.
from v2_prepare_ligands import (  # noqa: E402
    POCKET_5NDD,
    POCKET_5NDZ,
    PrepResult,
    prepare_one,
    protonate_ph74,
    sha256,
)


def prepare_one_stereo(task: tuple) -> PrepResult:
    """`prepare_one` with the stereo-destroying Canonicalize call removed.

    Every other step is copied from v2_prepare_ligands.prepare_one so the two
    modes differ in exactly one call.
    """
    cand_id, smiles, seed, n_confs, max_heavy = task
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return PrepResult(cand_id, False, "SMILES_PARSE_FAILED")
    try:
        mol = rdMolStandardize.Cleanup(mol)
        mol = rdMolStandardize.FragmentParent(mol)
        # NOTE: TautomerEnumerator().Canonicalize(mol) deliberately NOT called.
    except Exception as exc:  # noqa: BLE001
        return PrepResult(cand_id, False, f"STANDARDISE_FAILED:{type(exc).__name__}")
    if mol is None or mol.GetNumAtoms() == 0:
        return PrepResult(cand_id, False, "EMPTY_AFTER_STANDARDISE")
    heavy = mol.GetNumHeavyAtoms()
    if heavy < 8:
        return PrepResult(cand_id, False, "TOO_FEW_HEAVY_ATOMS")
    if heavy > max_heavy:
        return PrepResult(cand_id, False, "TOO_MANY_HEAVY_ATOMS")
    if any(a.GetSymbol() not in {"C", "N", "O", "S", "P", "F", "Cl", "Br", "I",
                                 "H", "B", "Se"} for a in mol.GetAtoms()):
        return PrepResult(cand_id, False, "UNSUPPORTED_ELEMENT")
    try:
        mol = protonate_ph74(mol)
    except Exception:  # noqa: BLE001
        pass
    inchikey = ""
    try:
        inchikey = Chem.MolToInchiKey(mol)
    except Exception:  # noqa: BLE001
        pass
    props = dict(
        mw=float(Descriptors.MolWt(mol)),
        clogp=float(Descriptors.MolLogP(mol)),
        tpsa=float(rdMolDescriptors.CalcTPSA(mol)),
        hba=int(rdMolDescriptors.CalcNumHBA(mol)),
        hbd=int(rdMolDescriptors.CalcNumHBD(mol)),
        rotb=int(rdMolDescriptors.CalcNumRotatableBonds(mol)),
        fsp3=float(rdMolDescriptors.CalcFractionCSP3(mol)),
    )
    try:
        props["qed"] = float(QED.qed(mol))
    except Exception:  # noqa: BLE001
        props["qed"] = float("nan")
    from rdkit.Chem.Scaffolds import MurckoScaffold
    try:
        murcko = MurckoScaffold.MurckoScaffoldSmiles(mol=mol, includeChirality=False)
    except Exception:  # noqa: BLE001
        murcko = ""
    molh = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = seed
    params.useSmallRingTorsions = True
    params.pruneRmsThresh = 0.5
    cids = AllChem.EmbedMultipleConfs(molh, numConfs=n_confs, params=params)
    if len(cids) == 0:
        params.useRandomCoords = True
        cids = AllChem.EmbedMultipleConfs(molh, numConfs=n_confs, params=params)
    if len(cids) == 0:
        return PrepResult(cand_id, False, "EMBED_FAILED")
    best_cid, best_energy = int(cids[0]), None
    try:
        results = AllChem.MMFFOptimizeMoleculeConfs(molh, maxIters=800, mmffVariant="MMFF94s")
        for cid, (_conv, energy) in zip(cids, results):
            if best_energy is None or energy < best_energy:
                best_energy, best_cid = energy, int(cid)
    except Exception:  # noqa: BLE001
        pass
    conf_mol = Chem.Mol(molh)
    conf_mol.RemoveAllConformers()
    conf_mol.AddConformer(molh.GetConformer(best_cid), assignId=True)
    conf_mol.SetProp("_Name", cand_id)
    return PrepResult(cand_id=cand_id, ok=True, reason="OK", inchikey=inchikey,
                      smiles_prepared=Chem.MolToSmiles(mol),
                      formal_charge=int(Chem.GetFormalCharge(mol)),
                      heavy_atoms=int(heavy),
                      molblock=Chem.MolToMolBlock(conf_mol), murcko=murcko, **props)


def stereo_audit(smiles_in: str, smiles_prep: str) -> dict:
    """Did preparation change constitution or stereochemistry?"""
    a = Chem.MolFromSmiles(smiles_in) if isinstance(smiles_in, str) else None
    b = Chem.MolFromSmiles(smiles_prep) if isinstance(smiles_prep, str) else None
    if a is None or b is None:
        return dict(constitution_changed=None, stereo_changed=None,
                    n_stereocentres_in=None, n_stereocentres_out=None,
                    inchikey_in="", inchikey_skeleton_match=None)
    ka, kb = Chem.MolToInchiKey(a), Chem.MolToInchiKey(b)
    sa = Chem.FindMolChiralCenters(a, includeUnassigned=True, useLegacyImplementation=False)
    sb = Chem.FindMolChiralCenters(b, includeUnassigned=True, useLegacyImplementation=False)
    assigned_a = {i for i, c in sa if c != "?"}
    assigned_b = {i for i, c in sb if c != "?"}
    return dict(
        constitution_changed=bool(ka.split("-")[0] != kb.split("-")[0]),
        stereo_changed=bool(ka != kb),
        n_stereocentres_in=len(sa), n_stereocentres_out=len(sb),
        n_assigned_in=len(assigned_a), n_assigned_out=len(assigned_b),
        inchikey_in=ka, inchikey_skeleton_match=bool(ka.split("-")[0] == kb.split("-")[0]),
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True,
                    help="CSV with cand_id, smiles, pockets (';'-joined), class")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--mode", choices=["campaign", "stereo"], default="campaign")
    ap.add_argument("--seed", type=int, default=20260904)
    ap.add_argument("--n-confs", type=int, default=8)
    ap.add_argument("--max-heavy", type=int, default=60)
    ap.add_argument("--shard-size", type=int, default=25)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    table = pd.read_csv(args.input)
    for col in ("cand_id", "smiles", "pockets"):
        if col not in table.columns:
            raise SystemExit(f"input must carry a '{col}' column")
    out = args.out.resolve()
    shard_dir = out / "shards"
    shard_dir.mkdir(parents=True, exist_ok=True)

    fn = prepare_one if args.mode == "campaign" else prepare_one_stereo
    tasks = [(r.cand_id, r.smiles, args.seed, args.n_confs, args.max_heavy)
             for r in table.itertuples()]
    results: dict[str, PrepResult] = {}
    with mp.Pool(args.workers) as pool:
        for n, res in enumerate(pool.imap_unordered(fn, tasks, chunksize=4), 1):
            results[res.cand_id] = res
            if n % 100 == 0:
                print(f"[prep:{args.mode}] {n}/{len(tasks)}", flush=True)

    table["prep_ok"] = table.cand_id.map(lambda c: results[c].ok)
    table["prep_reason"] = table.cand_id.map(lambda c: results[c].reason)
    for field in ("inchikey", "smiles_prepared", "formal_charge", "heavy_atoms", "mw",
                  "clogp", "tpsa", "hba", "hbd", "rotb", "fsp3", "qed", "murcko"):
        table[field] = table.cand_id.map(lambda c, f=field: getattr(results[c], f))

    audit = pd.DataFrame([stereo_audit(r.smiles, r.smiles_prepared)
                          for r in table.itertuples()])
    table = pd.concat([table.reset_index(drop=True), audit], axis=1)

    good = table[table.prep_ok].copy()
    # NB: the campaign collapses duplicate prepared InChIKeys. A benchmark must
    # keep every distinct input molecule, so duplicates are FLAGGED, not dropped.
    good["duplicate_prepared_inchikey"] = good.inchikey.duplicated(keep=False)

    manifest_rows, shard_index = [], {POCKET_5NDD: 0, POCKET_5NDZ: 0}
    buffers: dict[str, list[str]] = {POCKET_5NDD: [], POCKET_5NDZ: []}
    shard_files: dict[str, list[Path]] = {POCKET_5NDD: [], POCKET_5NDZ: []}

    def flush(pocket: str) -> None:
        if not buffers[pocket]:
            return
        path = shard_dir / f"{pocket}_shard{shard_index[pocket]:04d}.sdf"
        path.write_text("".join(buffers[pocket]))
        shard_files[pocket].append(path)
        buffers[pocket] = []
        shard_index[pocket] += 1

    for r in good.itertuples():
        res = results[r.cand_id]
        block = res.molblock.rstrip("\n")
        record = (f"{block}\n"
                  f">  <cand_id>\n{r.cand_id}\n\n"
                  f">  <source>\n{getattr(r, 'mol_class', 'BENCH')}\n\n"
                  f">  <inchikey>\n{res.inchikey}\n\n"
                  f">  <smiles_prepared>\n{res.smiles_prepared}\n\n"
                  f"$$$$\n")
        for pocket in str(r.pockets).split(";"):
            pocket = pocket.strip()
            if pocket not in buffers:
                continue
            buffers[pocket].append(record)
            manifest_rows.append(dict(cand_id=r.cand_id, pocket=pocket,
                                      shard=f"{pocket}_shard{shard_index[pocket]:04d}.sdf"))
            if len(buffers[pocket]) >= args.shard_size:
                flush(pocket)
    for pocket in (POCKET_5NDD, POCKET_5NDZ):
        flush(pocket)

    good.to_csv(out / "BENCH_LIGAND_TABLE.csv", index=False)
    table[~table.prep_ok][["cand_id", "smiles", "prep_reason"]].to_csv(
        out / "BENCH_PREP_FAILURES.csv", index=False)
    pd.DataFrame(manifest_rows).to_csv(out / "BENCH_DOCKING_ROUTING.csv", index=False)

    manifest = dict(
        generated_utc=datetime.now(timezone.utc).isoformat(),
        mode=args.mode, seed=args.seed, n_confs=args.n_confs,
        max_heavy=args.max_heavy, shard_size=args.shard_size,
        rdkit_version=Chem.rdBase.rdkitVersion,
        input_rows=int(len(table)), prepared=int(len(good)),
        failed=int((~table.prep_ok).sum()),
        failure_reasons=table[~table.prep_ok].prep_reason.value_counts().to_dict(),
        constitution_changed=int(good.constitution_changed.fillna(False).sum()),
        stereo_changed=int(good.stereo_changed.fillna(False).sum()),
        duplicate_prepared_inchikeys=int(good.duplicate_prepared_inchikey.sum()),
        docking_jobs=int(len(manifest_rows)),
        jobs_by_pocket=pd.DataFrame(manifest_rows).pocket.value_counts().to_dict()
        if manifest_rows else {},
        shard_sha256={f.name: sha256(f) for p in shard_files for f in shard_files[p]},
    )
    (out / f"BENCH_PREP_MANIFEST_{args.mode}.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps({k: v for k, v in manifest.items() if k != "shard_sha256"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
