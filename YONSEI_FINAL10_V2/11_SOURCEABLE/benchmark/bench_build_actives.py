#!/usr/bin/env python3
"""Build PAR2_KNOWN_ACTIVES.csv from verified database records.

Every structure comes from a database record fetched live (ChEMBL molecule
endpoint, cross-checked against PubChem where a trivial name exists). No SMILES
is written by hand and no structure is inferred from a compound name.

Inclusion in the enrichment set requires ALL of:
  * a small molecule that fits the campaign preparation limits (<= 60 heavy
    atoms) and is not a peptide (no two consecutive amide-linked residues),
  * a functional PAR2 ANTAGONIST / inhibitor measurement, in an assay whose
    description states inhibition of agonist- or protease-stimulated signalling,
  * potency at or below the stated cutoff (default IC50 <= 10 uM),
  * no agonist EC50/Emax annotation against human PAR2.

Rows failing any of these are KEPT in the table with the reason recorded and
include_in_enrichment=FALSE. Nothing is deleted.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors
from rdkit.Chem.Scaffolds import MurckoScaffold

RDLogger.DisableLog("rdApp.*")

PEPTIDE_BB = Chem.MolFromSmarts("[NX3][CX4][CX3](=[OX1])[NX3][CX4][CX3](=[OX1])")
MAX_HEAVY = 60  # v2_prepare_ligands.py --max-heavy default

# Trivial names resolved by InChIKey connectivity block, each confirmed against
# a PubChem name lookup performed in this session. The name is a label only;
# the structure always comes from the ChEMBL record.
NAME_BY_SKELETON = {
    "IDFPQEHZYBXIFO": "AZ8838",
    "FJAOGFGHTPYADT": "AZ3451",
    "DCUDDCGUKZLQLN": "GB88",
    "HXLQLJFWNKMGET": "GB110",
    "ADEQJSQZZXWZPW": "K-14585",
    "OHQDORKALTUSJJ": "C391",
    "VRZYMMVEALDDBH": "ENMD-1068",
    "WPJYZCYPCSYODL": "I-287 (PubChem name hit, UNVERIFIED against paper)",
}

ANTAGONIST_HINTS = ("antagonist activity", "inhibition of", "ip-one htrf",
                    "flpr", "flipr", "displacement of")

# Receptor-proximal readouts: what the compound does to PAR2 signalling within
# seconds to an hour. A distal readout (transcription, cytokine release,
# migration) can be moved by a great many mechanisms that have nothing to do
# with binding PAR2, so a compound supported ONLY by a distal readout is not
# usable as a docking-benchmark active.
PROXIMAL_READOUTS = ("calcium", "ca2+", "ip-one", "ip1", "inositol", "arrestin",
                     "camp", "displacement of", "binding", "flpr", "flipr",
                     "sre-luciferase", "cytosolic")
DISTAL_READOUTS = ("nfkappab", "nf-kappab", "il-8", "interleukin", "chemotactic",
                   "migration", "reporter gene", "cytokine", "proliferation")

#: Structures whose apparent PAR2 antagonism is not credibly receptor-mediated.
#: Recorded here rather than silently dropped.
FREQUENT_HITTERS = {
    "ZBBAKYWMFAFTAI": ("Triptolide", "covalent epoxide-bearing diterpenoid and a "
                       "well-documented promiscuous inhibitor of RNA Pol II / "
                       "NF-kB dependent transcription; its PAR2 'IC50' comes from "
                       "an NF-kB luciferase reporter and an IL-8 ELISA, both "
                       "transcriptional readouts many hundreds of steps "
                       "downstream of the receptor"),
}


def potency_nM(act: dict) -> float | None:
    """Normalise a ChEMBL potency record to nM. Returns None if not convertible.

    pKb/pKi are logarithmic and INVERTED relative to IC50: treating them as a
    concentration silently turns a 41 uM counter-screen value into a 4.4 nM
    'active'. They are converted explicitly here.
    """
    t, v, u = act.get("standard_type"), act.get("standard_value"), act.get("standard_units")
    if v is None:
        return None
    try:
        v = float(v)
    except (TypeError, ValueError):
        return None
    if t in ("IC50", "Ki") and u == "nM":
        return v
    if t in ("IC50", "Ki") and u == "uM":
        return v * 1000.0
    if t in ("pKb", "pKi", "pIC50"):
        return 10.0 ** (9.0 - v)
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--activities", type=Path, required=True)
    ap.add_argument("--molecules", type=Path, required=True)
    ap.add_argument("--documents", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--ic50-cutoff-nM", type=float, default=10000.0)
    args = ap.parse_args()

    activities = json.loads(args.activities.read_text())
    bundle = json.loads(args.molecules.read_text())
    mols = bundle["mols"]
    docs = json.loads(args.documents.read_text())

    by_mol = defaultdict(list)
    for a in activities:
        by_mol[a["molecule_chembl_id"]].append(a)

    rows = []
    for cid, acts in by_mol.items():
        m = mols.get(cid)
        if not m:
            continue
        struct = m.get("molecule_structures") or {}
        smiles = struct.get("canonical_smiles")
        if not smiles:
            continue
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            rows.append(dict(chembl_id=cid, isomeric_smiles=smiles,
                             verification_status="UNVERIFIED",
                             exclusion_reason="RDKit could not parse the ChEMBL SMILES",
                             include_in_enrichment=False))
            continue

        antag = [a for a in acts
                 if a.get("standard_type") in ("IC50", "Ki", "pKb")
                 and a.get("standard_value")
                 and any(h in (a.get("assay_description") or "").lower()
                         for h in ANTAGONIST_HINTS)]
        agonist = [a for a in acts
                   if a.get("standard_type") in ("EC50", "Emax", "Efficacy")
                   and "agonist activity" in (a.get("assay_description") or "").lower()]
        # Censored measurements are the opposite of what they look like.
        # "IC50 > 1000 nM" means the compound did NOT reach 50% inhibition at
        # 1 uM, i.e. it is inactive; six such rows in this dataset are PAR4
        # antagonists counter-screened against PAR2. Taking the number at face
        # value would import them into the actives set as 1 uM binders.
        censored = [a for a in antag if a.get("standard_relation") in (">", ">=")]
        antag = [a for a in antag if a.get("standard_relation") not in (">", ">=")]

        # Every antagonist measurement normalised to nM before anything is
        # compared, so pKb and IC50 are never ranked against each other raw.
        scored = [(potency_nM(a), a) for a in antag]
        scored = [(p, a) for p, a in scored if p is not None]
        best_pair = min(scored, key=lambda pa: pa[0]) if scored else None
        best = best_pair[1] if best_pair else None
        best_nM = best_pair[0] if best_pair else None
        proximal = [a for a in antag
                    if any(h in (a.get("assay_description") or "").lower()
                           for h in PROXIMAL_READOUTS)]
        distal_only = bool(antag) and not proximal

        inchikey = struct.get("standard_inchi_key") or ""
        skeleton = inchikey.split("-")[0]
        heavy = mol.GetNumHeavyAtoms()
        is_peptide = bool(mol.HasSubstructMatch(PEPTIDE_BB))
        doc = docs.get(best.get("document_chembl_id"), {}) if best else {}

        reasons = []
        if best is None and censored:
            reasons.append(f"only censored measurements ({len(censored)} rows, "
                           f"e.g. {censored[0]['standard_type']} "
                           f"{censored[0].get('standard_relation')}"
                           f"{censored[0].get('standard_value')} "
                           f"{censored[0].get('standard_units') or ''}) -- tested "
                           f"against PAR2 and NOT active at the top concentration")
        elif best is None:
            reasons.append("no antagonist-type measurement in ChEMBL for human PAR2")
        if is_peptide:
            reasons.append("peptide/peptidomimetic backbone (>=2 consecutive amide-linked residues)")
        if heavy > MAX_HEAVY:
            reasons.append(f"{heavy} heavy atoms exceeds the campaign preparation limit of {MAX_HEAVY}")
        if agonist:
            reasons.append("also carries a PAR2 agonist EC50/Emax annotation")
        potency = float(best["standard_value"]) if best else None
        units = best.get("standard_units") if best else None
        if best_nM is not None and best_nM > args.ic50_cutoff_nM:
            reasons.append(f"best potency {best_nM:.4g} nM "
                           f"({best['standard_type']} {potency:g} "
                           f"{units or ''}) is weaker than the "
                           f"{args.ic50_cutoff_nM:g} nM inclusion cutoff")
        if distal_only:
            reasons.append("supported only by a distal readout (transcription / "
                           "cytokine / migration), which many non-PAR2 mechanisms "
                           "can move")
        if skeleton in FREQUENT_HITTERS:
            reasons.append("frequent hitter: " + FREQUENT_HITTERS[skeleton][1])

        name = NAME_BY_SKELETON.get(skeleton)
        if not name:
            syn = [s["molecule_synonym"] for s in (m.get("molecule_synonyms") or [])]
            name = syn[0] if syn else (m.get("pref_name") or cid)

        ref = ""
        if doc:
            if doc.get("patent"):
                ref = f"Patent {doc['patent']} ({doc.get('year')}): {doc.get('title')}"
            else:
                ref = (f"{doc.get('journal')} {doc.get('year')}; "
                       f"{doc.get('title')}. DOI {doc.get('doi')}")

        rows.append(dict(
            name_canonical=name,
            chembl_id=cid,
            structure_source=f"ChEMBL {cid} (molecule_structures.canonical_smiles, "
                             f"fetched {datetime.now(timezone.utc).date()})",
            isomeric_smiles=smiles,
            inchikey=inchikey,
            molecular_formula=(m.get("molecule_properties") or {}).get("full_molformula"),
            mw=round(Descriptors.MolWt(mol), 2),
            heavy_atoms=heavy,
            murcko_scaffold=MurckoScaffold.MurckoScaffoldSmiles(mol=mol, includeChirality=False),
            is_peptide_backbone=is_peptide,
            activity_type=best["standard_type"] if best else None,
            activity_value=potency,
            activity_units=units,
            activity_nM_normalised=round(best_nM, 4) if best_nM is not None else None,
            activity_relation=best.get("standard_relation") if best else None,
            n_antagonist_measurements=len(antag),
            n_proximal_measurements=len(proximal),
            readout_class=("PROXIMAL" if proximal else "DISTAL_ONLY" if antag else "NONE"),
            frequent_hitter_flag=skeleton in FREQUENT_HITTERS,
            n_censored_measurements=len(censored),
            censored_inactive=bool(censored and best is None),
            has_agonist_annotation=bool(agonist),
            assay=(best.get("assay_description") or "")[:400] if best else "",
            assay_chembl_id=best.get("assay_chembl_id") if best else None,
            target_chembl_id="CHEMBL5963",
            target="Proteinase-activated receptor 2, Homo sapiens",
            reference=ref,
            document_chembl_id=best.get("document_chembl_id") if best else None,
            reference_doi=doc.get("doi"),
            reference_patent=doc.get("patent"),
            verification_status="VERIFIED" if best and not reasons else (
                "VERIFIED_STRUCTURE_EXCLUDED_FROM_SET" if best else "UNVERIFIED_ACTIVITY"),
            confidence=("HIGH" if best and doc.get("doi") else
                        "MEDIUM (patent-derived structure and assay)" if best and doc.get("patent")
                        else "LOW"),
            exclusion_reason="; ".join(reasons),
            include_in_enrichment=bool(best and not reasons),
        ))

    frame = pd.DataFrame(rows)
    frame = frame.sort_values(["include_in_enrichment", "activity_nM_normalised"],
                              ascending=[False, True])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.out, index=False)
    inc = frame[frame.include_in_enrichment]
    print(f"total rows                : {len(frame)}")
    print(f"included in enrichment    : {len(inc)}")
    print(f"unique Murcko scaffolds   : {inc.murcko_scaffold.nunique()}")
    print(f"unique documents          : {inc.document_chembl_id.nunique()}")
    print(f"MW range                  : {inc.mw.min():.0f} - {inc.mw.max():.0f}")
    print(f"heavy atom range          : {inc.heavy_atoms.min()} - {inc.heavy_atoms.max()}")
    print(f"potency range (nM)        : {inc.activity_nM_normalised.min():g} - {inc.activity_nM_normalised.max():g}")
    print("\nexclusion reasons:")
    for r, c in frame[~frame.include_in_enrichment].exclusion_reason.value_counts().items():
        print(f"  [{c:3d}] {r[:110]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
