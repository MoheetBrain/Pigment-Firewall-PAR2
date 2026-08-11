# V1 audit

Generated: `2026-08-11T09:40:47.149165+00:00`

This audit reads historical files only and writes new files below `YONSEI_FINAL10_V2/00_AUDIT`. It does not overwrite V1 results.

## Confirmed findings

- Pass-1 contains 2,487 result rows and 1,255 unique row keys.
- Pass-1 result rows by box: BoxA_orthosteric=1256, BoxB_allosteric=1231.
- Pass-1 result rows by source library: COCONUT_3D=317, FDA_DRUGS_3D=8, LOTUS_3D=1798, MITF_SCAFFOLDS_3D=36, NPATLAS_3D=328.
- The final V1 ranking contains COCONUT_3D=32, LOTUS_3D=389, MITF_SCAFFOLDS_3D=2, NPATLAS_3D=77.
- The final V1 ranking contains BoxA_orthosteric=396, BoxB_allosteric=104.
- Final V1 rows not linked by exact InChIKey/SMILES to Pass-1: 32.
- Historical Pass-2 input files: 35; nonempty: 35; output files: 105; nonempty outputs: 0.
- The clean historical 35-candidate Pass-2 shortlist exists: False.
- 5NDD benchmark contains non-ligand residues: {"HOH": 10, "NA": 1, "PO4": 5}.
- 5NDZ benchmark contains non-ligand residues: {"HOH": 2, "NA": 1}.
- Historical Box A configured receptor exists: False; Box B configured receptor exists: False.
- The historical GNINA driver hard-codes `/Users/mk/PycharmProjects/Pigment-Firewall-PAR2` rather than the checked-out repository path.
- Historical GNINA driver referenced paths missing from this checkout: /Users/moheet/Documents/ChatGPT/PAR2/SCREENING/SAFE_coconut_3D.sdf, /Users/moheet/Documents/ChatGPT/PAR2/SCREENING/SAFE_coconut.csv, /Users/moheet/Documents/ChatGPT/PAR2/SCREENING/LOTUS_2021_03_simple.sdf, /Users/moheet/Documents/ChatGPT/PAR2/SCREENING/NPAtlas_download_2024_09.sdf, /Users/moheet/Documents/ChatGPT/PAR2/GNINA_SCREEN_EX32/SDF_GENERATED/BLEACHING_3D.sdf.
- GNINA log command stages/modes: {"P1": 208, "P2": 105} / {"none": 521, "rescore": 105}.

## Current V1 ranking composition

| Prefix | Rows | Source libraries | Binding sites |
|---:|---:|---|---|
| 10 | 10 | `{"COCONUT_3D": 1, "LOTUS_3D": 9}` | `{"BoxB_allosteric": 10}` |
| 50 | 50 | `{"COCONUT_3D": 5, "LOTUS_3D": 42, "NPATLAS_3D": 3}` | `{"BoxA_orthosteric": 9, "BoxB_allosteric": 41}` |
| 100 | 100 | `{"COCONUT_3D": 10, "LOTUS_3D": 82, "MITF_SCAFFOLDS_3D": 2, "NPATLAS_3D": 6}` | `{"BoxA_orthosteric": 32, "BoxB_allosteric": 68}` |
| 500 | 500 | `{"COCONUT_3D": 32, "LOTUS_3D": 389, "MITF_SCAFFOLDS_3D": 2, "NPATLAS_3D": 77}` | `{"BoxA_orthosteric": 396, "BoxB_allosteric": 104}` |

## Current V1 top 10

| Rank | Molecule | Library | Site | Vina affinity | CNN score | InChIKey |
|---:|---|---|---|---:|---:|---|
| 1 | 1-[5-(2,5-dihydroxyphenyl)furan-3-yl]-4-methylpent-3-en-1-yl 3-methylbut-2-enoate | LOTUS_3D | BoxB_allosteric | -9.66864 | 0.93605 | MIIXCJKPPPUPOJ-UHFFFAOYSA-N |
| 2 | (6e)-2,6,11,15-tetramethylhexadeca-2,6,9,14-tetraene-4,11-diol | LOTUS_3D | BoxB_allosteric | -8.80146 | 0.92072 | FQDHGEYWNHWGJN-YHCYYBMYSA-N |
| 3 | (4r,6e,8s,10s)-4,6,8,10-tetramethylpentadec-6-ene-3,5-dione | LOTUS_3D | BoxB_allosteric | -6.32071 | 0.91104 | IABHSIINLYLXJN-NOSCTQNOSA-N |
| 4 | (2s,3z)-1-(furan-2-yl)-4,8-dimethylnona-3,7-dien-2-yl acetate | LOTUS_3D | BoxB_allosteric | -8.61959 | 0.89891 | BPWCJTWCEBVEOB-VWILAXROSA-N |
| 5 | mol_276266 | COCONUT_3D | BoxB_allosteric | -9.34429 | 0.88579 |  |
| 6 | (4s,6e,10r)-10-hydroxy-2,6,10-trimethyl-8-oxododeca-2,6,11-trien-4-yl acetate | LOTUS_3D | BoxB_allosteric | -8.49806 | 0.86416 | IPTYHUPNHDORPF-FIRJTHROSA-N |
| 7 | (2z,5e)-2-[(4z)-4-[(acetyloxy)methyl]-6-hydroxyhex-4-en-1-ylidene]-6-methyl-7-oxohept-5-en-1-yl acetate | LOTUS_3D | BoxB_allosteric | -8.06068 | 0.84698 | NYCFYGOJSIWKPN-BVNZSQIGSA-N |
| 8 | 4-[(1e,3s,5e)-3-ethenyl-7-hydroxy-3,7-dimethylocta-1,5-dien-1-yl]phenol | LOTUS_3D | BoxB_allosteric | -8.35753 | 0.83904 | KGYDEXUROYEYFL-CEAFDCLWSA-N |
| 9 | (2r,4r,5r,8r)-2-[(3z)-1-chlorohex-3-en-5-yn-1-yl]-8-ethyl-4-hydroxy-3,4,5,8-tetrahydro-2h-oxocin-5-yl acetate | LOTUS_3D | BoxB_allosteric | -8.90216 | 0.81642 | HDYZHQCPGQNLNH-YEXOBJAXSA-N |
| 10 | (4e,6s)-6-hydroxy-1,7-diphenylhept-4-en-3-one | LOTUS_3D | BoxB_allosteric | -7.41728 | 0.81117 | TYZZLIGGENRWEF-JKIKYLSZSA-N |

## Benchmark/configuration audit

The reference ligand geometry is calculated from the heavy atoms in the crystallographic ligand residue only. Non-ligand HETATM records are reported rather than silently retained.

- **5NDD_AZ8838**: 17 heavy atoms; centroid `(16.974, 5.926, 55.826)`; spans `(7.332, 7.672, 3.644) Å`; non-ligand species `{"HOH": 10, "NA": 1, "PO4": 5}`; configured receptor exists: `False`; config/centroid distance: `13.889114483096737` Å.
- **5NDZ_AZ3451**: 38 heavy atoms; centroid `(1.356, 12.419, 48.400)`; spans `(10.702, 7.885, 15.525) Å`; non-ligand species `{"HOH": 2, "NA": 1}`; configured receptor exists: `False`; config/centroid distance: `6.001491802597766` Å.

## Pass-2 status

The repository contains 35 nonempty Pass-2 input structures expected to represent the historical 35-candidate shortlist, but 105 output files are present and 0 contain data. Therefore a clean, completed historical 35-candidate Pass-2 shortlist is **not established**.

## Reproducible files

- `V1_AUDIT_SUMMARY.json` — complete machine-readable audit summary.
- `v1_source_library_counts.csv`, `v1_box_counts.csv` — result and unique-candidate counts.
- `V1_TOP10.csv`, `V1_TOP50.csv`, `V1_TOP100.csv`, `V1_TOP500.csv` — preserved current ranking prefixes.
- `benchmark_config_audit.csv`, `receptor_and_config_inventory.csv`, `screening_source_inventory.csv`, `sdf_output_inventory.csv`, `pass2_audit.json` — detailed inventories.
