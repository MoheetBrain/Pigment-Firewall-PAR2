#!/usr/bin/env python3
"""Append literature compounds that ChEMBL's PAR2 target record does not cover.

Two kinds of row are added.

1. VERIFIED-but-not-in-ChEMBL antagonists/NAMs. Each structure was fetched from
   PubChem by CID in this session and independently confirmed against the IUPHAR
   Guide to Pharmacology ligand record (same InChIKey), so two independent
   curators agree on the structure behind the name. These enter the enrichment
   set. They have NO dedicated property-matched decoys, because the decoy
   selection ran before they were added; that is recorded per row.

2. UNVERIFIED compounds. Named PAR2 antagonists for which no public structure
   record exists. They are written down so the gap is visible, and they are
   excluded from everything downstream. No structure is guessed for them.

The AZ8838 enantiomer conflict is also recorded here: ChEMBL curates the two
Vertex/AZ patents inconsistently, assigning activity to (R) in US-10550089-B2
and to (S) in US-10995072-B2. PDB 5NDD and the Nature 2017 paper support (S).
"""

from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors
from rdkit.Chem.Scaffolds import MurckoScaffold

RDLogger.DisableLog("rdApp.*")

# name, PubChem CID, GtoPdb ligand id, class, potency, assay, reference, notes
VERIFIED = [
    dict(name="I-191", cid=117977934, gtopdb=10268,
         cls="NAM (noncompetitive, unbiased)",
         activity_type="pIC50", activity_value=7.1,
         assay="Ca2+ mobilisation in HT29 cells against trypsin, 2f-LIGRLO-NH2 and "
               "non-peptide agonists; also blocks ERK1/2, RhoA and cAMP responses",
         reference="Jiang Y, Yau MK, Lim J, Wu KC, Xu W, Suen JY, Fairlie DP. "
                   "J Pharmacol Exp Ther 2018;364(2):246-257. "
                   "DOI 10.1124/jpet.117.245027, PMID 29263243",
         note="Not present in ChEMBL's PAR2 target record. Best-characterised "
              "drug-like PAR2 NAM with an unbiased mechanistic profile."),
    dict(name="I-287", cid=134296695, gtopdb=12491,
         cls="NAM (pathway-biased: blocks Gq and G12/13, spares Gi/o and beta-arrestin2)",
         activity_type="pIC50", activity_value=7.1,
         assay="Gq and G13 BRET biosensors in HEK293 stimulated with trypsin or "
               "SLIGKV-NH2; DAG / PKC / Ca2+ IC50 10-500 nM",
         reference="Avet C et al. Commun Biol 2020;3:719. "
                   "DOI 10.1038/s42003-020-01453-8, PMID 33247181",
         note="Not in ChEMBL's PAR2 record. Insurmountable inhibition, so a NAM "
              "rather than an orthosteric competitor. A PubChem name search for "
              "'I-287' returns this same CID, and the GtoPdb record confirms the "
              "InChIKey, so the name is not a collision."),
    dict(name="AZ7188", cid=129320516, gtopdb=9586,
         cls="ANTAGONIST",
         activity_type="pIC50", activity_value=5.2,
         assay="IUPHAR-curated PAR2 antagonist potency",
         reference="Cheng RKY et al. Nature 2017;545:112-115. "
                   "DOI 10.1038/nature22309, PMID 28445455",
         note="Ligand of PDB 5NJ6 (PAR2 + Fab3949 + AZ7188, 4.0 A) but NOT "
              "modelled in those coordinates, so there is no crystallographic "
              "cross-check of the pose. The indoline C2 stereocentre is "
              "undefined in both PubChem and GtoPdb."),
]

UNVERIFIED = [
    dict(name="P2L-003", reason="No PubChem, ChEMBL or GtoPdb record. Reported as "
         "an sp3-rich tetrahydropyrazolopyridine, 35-fold more potent and 11.6-fold "
         "more soluble than S757-0124, selective over PAR1/PAR4/ATP signalling.",
         reference="Park J, Lim H, Lee Y, Kim T, Song H, Lee S, Heo Y, Kim J, "
                   "Namkung W, Han G. Bioorg Chem 2025;167:109285. "
                   "DOI 10.1016/j.bioorg.2025.109285, PMID 41308341 (closed access)"),
    dict(name="S757-0124", reason="No PubChem compound or substance record, no "
         "ChEMBL entry, no ChemDiv product page located. Reported as an indazole "
         "virtual-screening hit; the identifier is ChemDiv catalogue format.",
         reference="Park J et al. Bioorg Chem 2025;167:109285, PMID 41308341"),
    dict(name="C781", reason="No PubChem, ChEMBL or GtoPdb record. Structure is "
         "patent-protected and undisclosed; the authors are founders of "
         "PARMedics Inc., which licenses it.",
         reference="Schiff HV et al. Br J Pharmacol 2023;180(5):667-680. "
                   "DOI 10.1111/bph.15903, PMID 35735078"),
    dict(name="K-12940", reason="Not in PubChem, ChEMBL or GtoPdb; structure "
         "appears only in the paper body/SI. Peptide-mimetic, Ki 1.94 uM against "
         "[3H]-2-furoyl-LIGRL-NH2 at human PAR2.",
         reference="Kanke T et al. Br J Pharmacol 2009;158(1):361-371. "
                   "DOI 10.1111/j.1476-5381.2009.00342.x, PMID 19719785"),
    dict(name="C376", reason="Could not be substantiated as a PAR2 compound at "
         "all: no PubMed hit pairing this identifier with PAR2 or "
         "protease-activated receptor, and no PubChem/ChEMBL/GtoPdb record.",
         reference="none located"),
    dict(name="PZ-235", reason="A lipidated cell-penetrating PEPDUCIN, not a small "
         "molecule; outside the scope of a small-molecule docking benchmark.",
         reference="Shearer AM et al. J Biol Chem 2016;291(44):23188-23198. "
                   "DOI 10.1074/jbc.M116.732743, PMID 27613872"),
]


def pubchem(cid: int) -> dict:
    url = (f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/"
           f"SMILES,MolecularFormula,MolecularWeight,InChIKey,Title/JSON")
    with urllib.request.urlopen(url, timeout=60) as f:
        return json.load(f)["PropertyTable"]["Properties"][0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--actives", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    base = pd.read_csv(args.actives)
    known = set(base.inchikey.dropna())
    rows = []

    for spec in VERIFIED:
        p = pubchem(spec["cid"])
        smiles, ik = p["SMILES"], p["InChIKey"]
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            print(f"  SKIP {spec['name']}: unparsable PubChem SMILES")
            continue
        if ik in known:
            print(f"  SKIP {spec['name']}: already present as {ik}")
            continue
        potency = 10.0 ** (9.0 - spec["activity_value"])
        rows.append(dict(
            name_canonical=spec["name"], chembl_id=None,
            structure_source=f"PubChem CID {spec['cid']} (SMILES field) cross-confirmed "
                             f"against IUPHAR Guide to Pharmacology ligand "
                             f"{spec['gtopdb']} by identical InChIKey",
            isomeric_smiles=smiles, inchikey=ik,
            molecular_formula=p["MolecularFormula"],
            mw=round(Descriptors.MolWt(mol), 2),
            heavy_atoms=mol.GetNumHeavyAtoms(),
            murcko_scaffold=MurckoScaffold.MurckoScaffoldSmiles(mol=mol, includeChirality=False),
            is_peptide_backbone=False,
            activity_type=spec["activity_type"], activity_value=spec["activity_value"],
            activity_units=None, activity_nM_normalised=round(potency, 4),
            activity_relation="=", n_antagonist_measurements=1,
            n_proximal_measurements=1, readout_class="PROXIMAL",
            frequent_hitter_flag=False, n_censored_measurements=0,
            censored_inactive=False, has_agonist_annotation=False,
            assay=spec["assay"], assay_chembl_id=None,
            target_chembl_id="CHEMBL5963",
            target="Proteinase-activated receptor 2, Homo sapiens",
            reference=spec["reference"], document_chembl_id=None,
            reference_doi=None, reference_patent=None,
            verification_status="VERIFIED",
            confidence="HIGH (two independent curators agree on the structure: "
                       "PubChem and IUPHAR/GtoPdb, identical InChIKey)",
            exclusion_reason="",
            include_in_enrichment=True,
            supplementary_source="PubChem+GtoPdb, not in the ChEMBL PAR2 target record",
            mechanism_class=spec["cls"],
            curation_note=spec["note"] + " NO dedicated property-matched decoys were "
                          "generated for this compound: decoy selection ran before it "
                          "was added.",
        ))
        print(f"  + {spec['name']}: {ik}  MW {Descriptors.MolWt(mol):.1f}")

    for spec in UNVERIFIED:
        rows.append(dict(
            name_canonical=spec["name"], chembl_id=None,
            structure_source="NO STRUCTURE FOUND", isomeric_smiles=None, inchikey=None,
            verification_status="UNVERIFIED",
            confidence="UNVERIFIED - no public structure record",
            reference=spec["reference"],
            exclusion_reason="NO STRUCTURE FOUND: " + spec["reason"],
            include_in_enrichment=False,
            supplementary_source="literature only",
            curation_note="Recorded so the gap is visible. No structure was "
                          "guessed or substituted.",
        ))
        print(f"  ? {spec['name']}: UNVERIFIED")

    out = pd.concat([base, pd.DataFrame(rows)], ignore_index=True)

    # Record the AZ8838 enantiomer curation conflict on the affected rows.
    az = out.inchikey.fillna("").str.startswith("IDFPQEHZYBXIFO")
    out.loc[az, "curation_note"] = (
        "AZ8838 enantiomer conflict: ChEMBL curates the two source patents "
        "inconsistently, assigning the activity to (R) in US-10550089-B2 and to "
        "(S) in US-10995072-B2. PDB 5NDD and Cheng et al. Nature 2017 support "
        "(S), InChIKey IDFPQEHZYBXIFO-LBPRGKRZSA-N (PubChem CID 126961334). "
        "Both enantiomers are docked here and reported separately.")

    out.to_csv(args.out, index=False)
    inc = out[out.include_in_enrichment == True]  # noqa: E712
    print(f"\ntotal rows              : {len(out)}")
    print(f"included in enrichment  : {len(inc)}")
    print(f"unique Murcko scaffolds : {inc.murcko_scaffold.nunique()}")
    print(f"UNVERIFIED rows kept    : {int((out.verification_status == 'UNVERIFIED').sum())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
