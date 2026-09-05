# Stereochemistry audit — de novo EX8 library

Generated 2026-09-05 by `scripts/v2_stereo_audit.py`, RDKit 2026.03.6.
Full table: `STEREOCHEMISTRY_AUDIT.csv` (15,000 rows, 62 columns).
Machine-readable summary and every collapse group: `STEREOCHEMISTRY_AUDIT.summary.json`.
Work list: `STEREO_REDOCK_LIST.csv`.

Reproduce with:

```
.venv-v2/bin/python YONSEI_FINAL10_V2/scripts/v2_stereo_audit.py \
  --out YONSEI_FINAL10_V2/10_FINAL/STEREOCHEMISTRY_AUDIT.csv \
  --out-redock YONSEI_FINAL10_V2/10_FINAL/STEREO_REDOCK_LIST.csv \
  --ranking YONSEI_FINAL10_V2/07_CONSENSUS/DENOVO_EX8_CONSENSUS_TOP1000.csv \
            YONSEI_FINAL10_V2/07_CONSENSUS/CONSENSUS_TOP500_5NDD_orthosteric.csv \
            YONSEI_FINAL10_V2/07_CONSENSUS/CONSENSUS_TOP500_5NDZ_allosteric.csv \
            YONSEI_FINAL10_V2/08_CLUSTERS/SIMILARITY_SEARCH_SEEDS.csv \
  --top-n 1000 --redock-scope ranked
```

## The defect

`v2_prepare_ligands.prepare_one` standardises every design with

```python
mol = rdMolStandardize.Cleanup(mol)
mol = rdMolStandardize.FragmentParent(mol)
mol = rdMolStandardize.TautomerEnumerator().Canonicalize(mol)   # <-- here
...
inchikey = Chem.MolToInchiKey(mol)                               # computed after
```

The tautomer canonicaliser moves protons, and a stereocentre or double-bond
geometry that depended on the original proton placement is erased. Because the
InChIKey is computed afterwards, two designs that differ only in that
stereochemistry produce the same key and one is discarded as a duplicate.

## Method and self-check

The audit re-runs that exact standardisation on all 15,000 queue SMILES
(the tautomer-corrected structures actually handed to preparation), applies the
same `protonate_ph74` function imported from the production script, and records
the stereochemistry at every step.

**Replication check: for all 14,825 designs that reached the shards, the
recomputed prepared InChIKey and the recomputed prepared SMILES match the
shipped `V2_LIGAND_TABLE.csv` values exactly (14,825 / 14,825 on both).** The
audit is therefore describing the real pipeline, not an approximation of it.

Definitions used throughout, all computed per design:

* stereocentres from `Chem.FindMolChiralCenters(mol, includeUnassigned=True,
  useLegacyImplementation=False)`, split into assigned (`R`/`S`) and unassigned (`?`)
* a double bond counts as defined stereochemistry only when its
  `GetStereo()` is `STEREOE/Z/CIS/TRANS`. `STEREOANY` is *not* counted —
  that is precisely the state the tautomer canonicaliser leaves a defined
  double bond in, and counting it would have hidden 30 losses
* `CONNECTIVITY_ID` = `MolToSmiles(mol, isomericSmiles=False)`
* `STEREO_ID` = `MolToSmiles(mol, isomericSmiles=True)`
* `TAUTOMER_PARENT_ID` = canonical SMILES of the tautomer-canonical parent
* stereo-aware InChIKey and flat InChIKey (after `RemoveStereochemistry`) are
  recorded for the input, the tautomer parent and the prepared structure

## Headline counts

| Quantity | All 15,000 designs | The 14,825 that were docked |
|---|---:|---:|
| Declared stereochemistry in the input | 11,090 | — |
| **Stereochemistry LOST during preparation** | **2,534** | **2,511** |
| PRESERVED | 8,556 | 8,410 |
| NEVER_PRESENT (input declared none) | 3,910 | 3,904 |
| ALTERED (inverted rather than dropped) | 0 | 0 |

Supporting detail:

| Quantity | Value |
|---|---:|
| Stereocentres destroyed, total | 3,042 |
| Defined double bonds destroyed, total | 36 |
| Designs that lost *only* double-bond geometry | 30 |
| Designs whose constitution was changed by standardisation | 1,199 |
| Designs given a **new** unassigned stereocentre by standardisation | 2,241 |
| Designs carrying an unassigned stereocentre already in the design | 4,901 |

**Every one of the 2,534 losses is attributable to
`TautomerEnumerator().Canonicalize()`.** The audit measured the assigned-centre
plus defined-bond count after each individual step; `Cleanup`,
`FragmentParent` and `protonate_ph74` destroyed stereochemistry in zero designs.

The 1,199 constitution changes are mostly enol → keto canonicalisation, which is
also where most of the 2,241 new unassigned centres come from: the canonical
keto form opens an sp3 centre that the enol form did not have, and nothing then
specifies its configuration.

## The 24 collapsed "duplicate InChIKey" pairs

All 24 groups are pairs; 7 in batch 1 and 17 in batch 2, matching both
preparation manifests. **None of the 24 is a true duplicate.**

| Classification | Groups | Meaning |
|---|---:|---|
| `EPIMERIC_PAIR` | **6** (2 batch-1, 4 batch-2) | both designs fully specify the same centres, with opposite descriptors — genuinely different molecules |
| `SPECIFIED_VS_UNSPECIFIED` | 17 (5 batch-1, 12 batch-2) | one design pins a centre the other leaves open; the docked structure specifies neither |
| `TAUTOMER_MERGE` | 1 (batch-2) | different constitutions made identical only by tautomer canonicalisation |
| `TRUE_DUPLICATE` | **0** | — |

### Genuine R/S epimers discarded

| Kept | Discarded | Batch | Design SMILES (kept) | Design SMILES (discarded) |
|---|---|---|---|---|
| DN01351 | DN01352 | 1 | `COc1cc([C@@H](C)C2CCC(=O)O2)nc2ccccc12` | `COc1cc([C@H](C)C2CCC(=O)O2)nc2ccccc12` |
| DN01866 | DN01867 | 1 | `COc1ccc2c(c1)[nH]c1c([C@@H](C)C3CCC(=O)O3)nccc12` | `COc1ccc2c(c1)[nH]c1c([C@H](C)C3CCC(=O)O3)nccc12` |
| DL06912 | DL06913 | 2 | `COc1cc(O)c2c(=O)cc([C@@H](C)C3CCC(=O)O3)oc2c1` | `COc1cc(O)c2c(=O)cc([C@H](C)C3CCC(=O)O3)oc2c1` |
| DL09180 | DL09181 | 2 | `C[C@H](c1occ2c1C(=O)c1c(O)cccc1[C@@H]2O)C1CCC(=O)O1` | `C[C@@H](c1occ2c1C(=O)c1c(O)cccc1[C@@H]2O)C1CCC(=O)O1` |
| DL10372 | DL10373 | 2 | `C[C@H](c1cc(=O)c2c(O)cc(O)cc2o1)C1CCC(=O)O1` | `C[C@@H](c1cc(=O)c2c(O)cc(O)cc2o1)C1CCC(=O)O1` |
| DL10523 | DL10525 | 2 | `COc1c(O)cc([C@@H](C)C2CCC(=O)O2)cc1O` | `COc1c(O)cc([C@H](C)C2CCC(=O)O2)cc1O` |

All six invert the same motif: a `CH(CH3)` centre bridging an aromatic system
and a γ-butyrolactone. That chemotype recurs throughout this library, so the
defect is concentrated rather than scattered.

### Tautomer merge

`DL09345` (kept) and `DL11010` (discarded) are different constitutional isomers —
input flat InChIKeys `HFABUMLFIALQFC` and `IDMDXDLSOXHCPH` — that tautomer
canonicalisation drove to one structure. This is not a stereochemistry problem
but it was counted as a duplicate collapse.

### The 17 specified-vs-unspecified pairs

In each of these one design assigns a stereocentre that its partner leaves
unassigned, e.g. `DN02599` `CC[C@H](C)c1cc2occ(...)` against `DN02600`
`CCC(C)c1cc2occ(...)`. Merging them is arithmetically defensible, but the
molecule that was actually docked has the centre unassigned, so it stands for
neither design specifically. All 17 pairs are listed in
`STEREOCHEMISTRY_AUDIT.summary.json` under `groups`.

## One structure was docked twice

De-duplication ran **within** each batch. `DN00314` (`R`) and `DL03110` (`S`)
are an R/S epimer pair split across the two batches. Both lost the stereocentre
in preparation, both became `COc1c(O)cc(C(C)C2CCCCC2)cc1O`
(`YUIAMUUFZPWUAJ-UHFFFAOYSA-N`), and both were docked — `DN00314` into both
pockets, `DL03110` into 5NDZ. `DN00314` sits at consensus rank **240**. Its
score and `DL03110`'s 5NDZ score describe the same physical structure.

## Affected finalists

`STEREO_REDOCK_LIST.csv` — **646 cand_ids**, drawn from the 1,492 distinct
molecules named across the four current ranking artefacts (consensus top-1000,
both per-pocket top-500 lists, and the 34 similarity-search seeds).

| Severity | Count | Meaning |
|---|---:|---|
| `WRONG_STEREOISOMER_DOCKED` | **207** | the docked structure is not the declared design: stereo was lost, a new unassigned centre was opened, the molecule stands in for a collapsed partner, or the same structure was docked under a second cand_id |
| `AMBIGUOUS_STEREOCHEMISTRY` | **439** | the design itself never fixed the configuration; docking silently used one arbitrary embedding |

The four ranking files do **not** share a rank scale — the pooled consensus
table is ranked 1–1000 over the whole universe, the 5NDD file restarts at 1 for
that pocket, and the 5NDZ file carries pooled ranks 1281–5976. `ranking_position`
is therefore taken from the first file that lists a molecule, never minimised
across files, and `ranking_source` names that file. Reach into the ranking,
measured against the pooled `DENOVO_EX8_CONSENSUS_TOP1000.csv` rank:

| Ranking window | Affected |
|---|---|
| Top 10 | **7** — ranks 1–7 (`DN00464`, `DN00361`, `DN00375`, `DN01387`, `DN00626`, `DN00613`, `DN00332`), all `AMBIGUOUS_STEREOCHEMISTRY` |
| Top 50 | 27 |
| Top 100 | 48 |
| Top 500 | 254 |
| Top 1000 | 500 |

A further 146 affected molecules come from the 5NDZ per-pocket top-500 and were
outside the pooled top-1000, giving the 646 total. Every affected molecule in
the 5NDD per-pocket list and among the similarity-search seeds was already in
the pooled top-1000.

Also affected:

* **15 of the 34** similarity-search seeds
* **23 of the 56** cand_ids named in `FINAL_CANDIDATES.md`
  (20 `AMBIGUOUS_STEREOCHEMISTRY`, 3 `WRONG_STEREOISOMER_DOCKED`); across all
  56, `stereo_status` is PRESERVED 35, NEVER_PRESENT 17, LOST 4
* by batch: 298 batch-1, 348 batch-2

Across the whole library 6,692 designs are affected on the same criteria; the
list is restricted to ranked finalists so the redocking effort is bounded.
Rerun with `--redock-scope all` for the complete set.

## What this does and does not mean

* Nothing here changes any docking score. No docking was rerun.
* A `LOST` verdict says the structure that GNINA saw is flatter than the design.
  It does not say which stereoisomer binds — that requires the redock.
* An `AMBIGUOUS` verdict is a property of the generator's output, not of the
  preparation code: those designs never carried a configuration to preserve.
* The clean fix in `v2_prepare_ligands.py` is to compute the InChIKey used for
  de-duplication **before** `TautomerEnumerator().Canonicalize()`, or to keep the
  pre-canonicalisation stereo-aware key alongside it, and to run de-duplication
  once over the whole library instead of once per batch.
