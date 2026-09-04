# Reference-model defects found during independent V2 verification

**Status: two defects confirmed in the corrected reference models. Both are
upstream of the de novo campaign and of the planned candidate docking.**

This report was produced by an independent verification pass over the
`yonsei-final10-v2` branch at commit `3a80c0b`. It does not replace, delete, or
modify any committed artifact. Every claim below is reproducible with the
scripts named in each section.

The de novo production artifacts themselves are internally consistent: all six
SHA-256 checksums in `HANDOFF_TO_CLAUDE.md` section 15.3 match, and a full
row-by-row recomputation of both design tables passes (see
`DENOVO_VERIFICATION.md`). The defects below are in the **reference models**
that the campaign was built on, not in the generator's bookkeeping.

---

## Defect 1 — the orthosteric reference ligand is the wrong tautomer

`01_REFERENCE_POCKETS/ligands/5NDD_AZ8838_crystallographic_clean.sdf` does not
contain AZ8838. It contains a non-aromatic **4H-imidazole** tautomer in which the
implicit hydrogen sits on the ring carbon C2 instead of a ring nitrogen.

Verified against the authoritative wwPDB chemical-component definition
(`https://data.rcsb.org/rest/v1/core/chemcomp/8TZ`):

| | wwPDB 8TZ (ground truth) | Stored in repository |
|---|---|---|
| Name | (S)-(4-fluoranyl-2-propyl-phenyl)-(1H-imidazol-2-yl)methanol | — |
| SMILES | `CCCc1cc(F)ccc1[C@H](O)c2[nH]ccn2` | `CCCc1cc(F)ccc1[C@H](O)C1N=CC=N1` |
| InChIKey | `IDFPQEHZYBXIFO-LBPRGKRZSA-N` | `BBGRVUDFEGKPGW-LBPRGKRZSA-N` |
| Aromatic bonds | 11 | **6** |
| Aromatic rings | 2 | **1** |
| HBD / HBA | 2 / 2 | **1 / 3** |

The molecular formula (`C13H15FN2O`) and mass (234.274) are **identical** in both
forms, which is why the existing integrity checks did not catch it: this is a
hydrogen-placement/tautomer error, not an atom-count error. Stereochemistry is
preserved — both are (S), and the InChIKey stereo layer `LBPRGKRZSA` is common
to both. Only the connectivity layer differs.

**Root cause.** Ligands extracted from PDB HETATM records carry no hydrogens.
When bond orders are perceived from heavy-atom coordinates alone, an azole can
be assigned a localised `N=C-C=N` pattern with the hydrogen placed on carbon.
The giveaway in the stored file is that C2 is sp3 and bears *both* the exocyclic
substituent and a hydrogen, which is not a chemically reasonable form for a
2-substituted imidazole in a crystal structure.

RDKit's `TautomerEnumerator` does **not** enumerate this C→N 1,3-shift, so a
generic tautomer-canonicalisation step would not have caught it either.

Reproduce with:

```bash
python YONSEI_FINAL10_V2/scripts/check_reference_tautomers.py --impact --scan-designs
```

The allosteric reference (`8UN` / AZ3451) was checked the same way and is
**clean**: InChIKey `FJAOGFGHTPYADT-SFHVURJKSA-N` and 22 aromatic bonds, both
matching wwPDB exactly.

### 1a. Consequence for scoring — moderate, repairable by rescoring

`ref_tanimoto` for the orthosteric family was computed against the wrong
reference fingerprint. The two reference forms are only **0.5102** Tanimoto
apart (Morgan radius 2, 2048 bits).

| Quantity (orthosteric family, n=10,000) | Stored | With corrected reference |
|---|---:|---:|
| `ref_tanimoto` max | 0.8462 | 0.4340 |
| `ref_tanimoto` median | 0.1558 | 0.1290 |
| `ref_tanimoto` mean | 0.1602 | 0.1335 |

Because `ref_tanimoto` enters `design_score` only through the novelty term
(weight 0.20), the ranking is broadly robust but not stable at the margin:

- mean |Δ design_score| = 0.01729, max = 0.17963
- 6,840 of 10,000 designs shift by more than 0.01; 231 shift by more than 0.05
- Spearman(old, new) = 0.98816; mean rank shift 300 positions
- **358 of the 1,867 orthosteric slots in the docking queue (19.2%) would change
  membership** (score-only comparison, ignoring the scaffold-cap-12 reselection,
  so this is an upper bound)

### 1b. Consequence for the generated structures — serious, NOT repairable by rescoring

The defect also propagated into generation. BRICS decomposition of the reference
seed yields four fragments, and exactly one of them — the imidazole head group,
the pharmacophorically important part — is wrong:

| Stored seed fragments | Correct seed fragments |
|---|---|
| `[13*]C1N=CC=N1` ← **wrong** | `[14*]c1ncc[nH]1` |
| `[16*]c1ccc(F)cc1[16*]` | `[16*]c1ccc(F)cc1[16*]` |
| `[8*]C([8*])O` | `[8*]C([8*])O` |
| `[8*]CCC` | `[8*]CCC` |

Note the BRICS attachment label also changes (`[13*]` → `[14*]`), so the fragment
participates in different reverse-BRICS reactions.

Scanning the committed design tables for the same motif:

| Table | Designs carrying the wrong tautomer | Share |
|---|---:|---:|
| `DENOVO_15000.csv` | 2,131 / 15,000 | **14.21%** |
| `DENOVO_TOP3000_FOR_DOCKING.csv` | 394 / 3,000 | **13.13%** |

By family in the full set: 2,100 orthosteric, 25 allosteric, 6 exploratory.

These molecules are not merely mis-scored — **the stored structures themselves
are chemically wrong**, carrying an sp3 C2 with a spurious stereocentre where an
aromatic imidazole belongs. Rescoring cannot fix them. If they were carried
forward into 3D conformer generation, docking, or vendor/synthesis triage as
written, the wrong chemistry would be propagated.

The affected rows, each with its corrected SMILES, are written to
`04_VERIFICATION/affected_designs_wrong_tautomer.csv`.

---

## Defect 2 — the reference interaction fingerprints contain no hydrogen bonds

`scripts/reference_interactions.py` loads the ligand SDF and receptor PDB with
`removeHs=False` and never calls `Chem.AddHs`. Neither input carries explicit
hydrogens. ProLIF's `HBDonor`/`HBAcceptor` detectors require explicit hydrogens,
so **no hydrogen bond can be detected at all**.

Both committed reference fingerprints consist only of `VdWContact` and
`Hydrophobic` terms — despite polar contacts well inside hydrogen-bonding
distance, including TYR:82 at 2.47 Å and HIS:135 at 2.63 Å in the 5NDD system.

Reproduce with:

```bash
python YONSEI_FINAL10_V2/scripts/diagnose_reference_ifp.py
```

Controlled result (ProLIF 2.2.1, the same version used on the production VM).
Condition A is the control and reproduces the committed CSVs exactly:

| System | Condition | Interactions | H-bonds |
|---|---|---:|---:|
| 5NDD / AZ8838 | A — as committed | 10 (matches committed CSV) | **0** |
| 5NDD / AZ8838 | B — stored tautomer + ligand H | 14 | 1 |
| 5NDD / AZ8838 | C — corrected tautomer + ligand H | 15 | **2** |
| 5NDZ / AZ3451 | A — as committed | 9 (matches committed CSV) | **0** |
| 5NDZ / AZ3451 | B — stored tautomer + ligand H | 11 | 0 |

This separates the two defects cleanly. Adding hydrogens alone recovers the
hydroxyl donor (B); the second donor in condition C is the imidazole N-H, which
exists only in the correct tautomer.

**A further limitation applies to both systems:** the receptor was never
protonated either, so receptor-as-donor hydrogen bonds remain undetectable under
*every* condition above. A complete repair requires protonating the receptor at
the intended pH as well, not just the ligand.

### Consequence for the reported benchmark

The handoff reports these gate values in section 7.4:

| System | Best RMSD | Top-ranked IFP recovery | Best IFP recovery |
|---|---:|---:|---:|
| 5NDD / AZ8838 | 0.674658 Å | 0.500 | 0.700 |
| 5NDZ / AZ3451 | 0.867183 Å | 0.889 | 0.889 |

- **The RMSD gate is unaffected.** Symmetry-corrected heavy-atom RMSD is purely
  geometric; aromaticity and hydrogen placement do not move heavy atoms. Both
  systems still pass the primary ≤2.0 Å best-pose criterion, and the section 7.4
  nuance about the 5NDZ top-ranked pose still stands as written.
- **The IFP recovery figures are measured against an incomplete reference.**
  They quantify recovery of a fingerprint that structurally cannot contain
  hydrogen bonds — the most discriminating interaction class for a polar
  antagonist pocket. They should not be quoted as interaction-level validation
  in their current form.

This matters most downstream: handoff section 17 lists "recovery/similarity to
the correct crystallographic antagonist fingerprint" as a core ranking criterion
for the final candidate selection. That criterion needs a repaired reference
fingerprint before it can carry weight.

---

## What is *not* affected

- The de novo generator's bookkeeping. All 15,000 rows recompute exactly; family
  allocation, deduplication, scaffold caps, and the TOP3000 subset relation all
  verify. See `DENOVO_VERIFICATION.md`.
- All six production checksums in handoff section 15.3.
- The allosteric reference ligand identity (8UN / AZ3451), confirmed against wwPDB.
- The corrected box geometry in handoff section 6.2. Box centres and sizes derive
  from heavy-atom coordinates, which are unchanged.
- The RMSD half of the benchmark gate, as set out above.
- The V1 audit conclusions in `00_AUDIT/`.
- Hard property filters, PAINS/reactive screening, and QED. These are computed
  per design and do not reference the crystallographic ligand.

---

## Recommended sequencing

Handoff section 20 guardrail 9 applies throughout: use a new output directory and
do not overwrite the canonical production CSVs.

1. **Repair the orthosteric reference ligand.** Rebuild
   `5NDD_AZ8838_crystallographic_clean.sdf` from the wwPDB 8TZ definition,
   keeping the deposited coordinates, and gate on InChIKey
   `IDFPQEHZYBXIFO-LBPRGKRZSA-N`. `check_reference_tautomers.py` already encodes
   this as a regression test and exits non-zero on failure.
2. **Protonate both ligand and receptor before fingerprinting**, then regenerate
   both reference IFPs and recompute the section 7.4 recovery values. Re-running
   the redock is not required for the RMSD gate, which stands.
3. **Decide how to handle the 2,131 contaminated designs.** Two options, and this
   is a chemistry judgement rather than a mechanical one:
   - correct the motif in place (the corrected SMILES are already provided) and
     rescore against the repaired reference; or
   - regenerate the orthosteric family from the corrected seed fragment, which is
     cleaner in provenance terms but discards the current orthosteric set.
4. **Rebuild the docking queue after 1–3, before spending GNINA CPU time.** Roughly
   a fifth of the orthosteric queue membership is expected to change, and ~13% of
   the current queue carries the wrong motif outright. Docking the queue as it
   stands would spend the campaign's compute budget on partly wrong chemistry.

The sourceable V1/FDA universe route recommended in handoff section 17 is
**not** blocked by either defect, since those are real catalogued structures
rather than reference-seeded designs. If near-term wet-lab throughput is the
priority, that campaign can proceed in parallel with this repair.

---

## Interpretation limits

Nothing in this report establishes PAR2 activity, or the absence of it, for any
molecule. It concerns the internal correctness of the reference models and the
generated design set. `design_score`, `ref_tanimoto`, QED and ProLIF recovery
remain prioritisation features, not calibrated probabilities of inhibition.
