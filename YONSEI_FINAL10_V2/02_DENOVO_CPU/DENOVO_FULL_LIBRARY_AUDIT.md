# Full de novo library audit — DENOVO_15000

Generated 2026-09-04 13:41:10 UTC by `YONSEI_FINAL10_V2/scripts/v2_full_library_audit.py`.
Every number below was computed by that script from the files listed under
Inputs. Nothing is carried over from an earlier report.

Scope: structural bookkeeping only. Nothing here establishes PAR2 activity,
or the absence of it, for any molecule.

## Inputs

- `YONSEI_FINAL10_V2/02_DENOVO_CPU/DENOVO_15000.csv` (full)
- `YONSEI_FINAL10_V2/02_DENOVO_CPU/DENOVO_TOP3000_FOR_DOCKING_TAUTOMER_CORRECTED.csv` (queue_corrected)
- `YONSEI_FINAL10_V2/02_DENOVO_CPU/DENOVO_BATCH2_REMAINING12000_TAUTOMER_CORRECTED.csv` (batch2)
- `YONSEI_FINAL10_V2/04_VERIFICATION/affected_designs_wrong_tautomer.csv` (affected)
- `YONSEI_FINAL10_V2/SCREEN_REAL/library/V2_LIGAND_TABLE.csv` (ligand_table)

## 1. Library size

- Rows in `DENOVO_15000.csv`: **15000**
- `denovo_rank` unique: True; ascending: True; range 1–15000
- Stored SMILES strings distinct: True (15000 unique strings)

## 2. Unique parent structures (after correction)

- Unique InChIKeys: **15000**
- Rows that repeat an InChIKey seen earlier in the file: **0**
- Unique RDKit canonical SMILES: **15000**
- Rows that repeat a canonical SMILES seen earlier: **0**

`is_duplicate_structure` in the audit CSV uses the InChIKey key; `is_duplicate_canonical_smiles` uses the canonical SMILES key.

## 3. Family counts

| set | orthosteric | allosteric | exploratory | total |
|---|---|---|---|---|
| full library | 10000 | 3500 | 1500 | 15000 |
| screened (batch 1 queue) | 1867 | 678 | 455 | 3000 |
| remaining | 8133 | 2822 | 1045 | 12000 |

## 4. Wrong-tautomer designs

Total carrying the wrong tautomer: **2131** of 15000 (14.21%)

| split | orthosteric | allosteric | exploratory | total |
|---|---|---|---|---|
| all affected | 2100 | 25 | 6 | 2131 |
| affected & screened | 388 | 4 | 2 | 394 |
| affected & not screened | 1712 | 21 | 4 | 1737 |

- Screened / not screened: **394** / **1737**
- Committed `tautomer_corrected` flags: queue 394, batch 2 1737, sum 2131

Motif verification (probes are diagnostic only; they never select a correction):

- Corrected rows whose stored structure matches the non-aromatic 4H-imidazole pattern `[CX4;R]1[#7X2]=[#6][#6]=[#7X2]1`: **2131 / 2131**
- Corrected rows whose repaired structure matches the aromatic 1H-imidazole pattern `[nH]1cncc1`: **2131 / 2131**
- Rows NOT in the correction list that nonetheless match the 4H-imidazole pattern: **0**

## 5. Molecular formula preservation across the correction

- Formula preserved: **2131 / 2131**
- Formula changed: **0**
- Heavy-atom count preserved: **2131 / 2131**

## 6. Aromatic bond count across the correction

- Aromatic bond count increased: **2131 / 2131**
- Did not increase: **0**

Distribution of `aromatic_bonds_after - aromatic_bonds_before` over corrected rows:

| delta | rows |
|---|---|
| 5 | 2131 |

- Aromatic ring count increased: **2131 / 2131**

## 7. RDKit parse failures

- Fail to parse BEFORE correction: **0**
- Fail to parse AFTER correction: **0**
- Rows with a blank InChIKey after correction: **0**

## 8. Reconciliation

### 8.1 15,000 = screened + remaining

    3000 screened + 12000 remaining = 15000  (library rows: 15000)

Holds: **True**

- `DENOVO_REMAINING_TO_SCREEN.csv` row count: **12000**
- Remaining ranks identical to `DENOVO_BATCH2_REMAINING12000_TAUTOMER_CORRECTED.csv`: **True**
- Batch-2 rows whose committed corrected SMILES equals this audit's `smiles_corrected`: **12000 / 12000**
- Queue rows whose committed corrected SMILES equals this audit's `smiles_corrected`: **3000 / 3000**

### 8.2 3,000 queued vs 2,988 prepared

    3000 queued - 5 embed failures - 7 duplicate InChIKeys = 2988  (V2_LIGAND_TABLE.csv rows: 2988; manifest unique_ligands: 2988)

Holds: **True**

Independently recomputed from the audit table: of the 3000 screened designs, **2988** have a `cand_id` in `V2_LIGAND_TABLE.csv` and **12** do not.

- Lost cand_ids (12): DN00281, DN00362, DN00563, DN01352, DN01479, DN01867, DN01970, DN02160, DN02319, DN02600, DN02898, DN02899
- Present in `V2_PREP_FAILURES.csv` as EMBED_FAILED (5): DN00362, DN01479, DN02319, DN02898, DN02899
- Not an embed failure, therefore attributable to InChIKey collapse (7): DN00281, DN00563, DN01352, DN01867, DN01970, DN02160, DN02600

Arithmetic check `12 = 5 + 7`: **True** (5 + 7 = 12)

### 8.3 What the 7 collapsed rows actually collided with

The InChIKey used by `v2_prepare_ligands.py` is computed *after* `rdMolStandardize.Cleanup` -> `FragmentParent` -> `TautomerEnumerator().Canonicalize` -> approximate pH 7.4 protonation. That recipe was re-run here and reproduces the committed `inchikey` for **200 / 200** sampled rows of `V2_LIGAND_TABLE.csv`, so the collision partners below are computed, not assumed. `V2_LIGAND_TABLE.csv` itself contains 0 duplicate InChIKeys.

| cand_id | category | collides with | parent InChIKeys differ |
|---|---|---|---|
| DN00281 | INCHIKEY_COLLAPSED | DN00280 | True |
| DN00362 | EMBED_FAILED | — | — |
| DN00563 | INCHIKEY_COLLAPSED | DN00562 | True |
| DN01352 | INCHIKEY_COLLAPSED | DN01351 | True |
| DN01479 | EMBED_FAILED | — | — |
| DN01867 | INCHIKEY_COLLAPSED | DN01866 | True |
| DN01970 | INCHIKEY_COLLAPSED | DN01969 | True |
| DN02160 | INCHIKEY_COLLAPSED | DN02159 | True |
| DN02319 | EMBED_FAILED | — | — |
| DN02600 | INCHIKEY_COLLAPSED | DN02599 | True |
| DN02898 | EMBED_FAILED | — | — |
| DN02899 | EMBED_FAILED | — | — |

- EMBED_FAILED: **5**; InChIKey-collapsed: **7**; unexplained: **0**
- Collapsed rows whose *parent* InChIKey differs from its partner's: **7 / 7**

This qualifies the phrase "duplicate InChIKeys". At the parent level the library holds no duplicates at all (section 2). The 7 rows collapse only because the canonical-tautomer step in the preparation recipe discards the stereo designation, after which each of them becomes indistinguishable from the queue row immediately above it. The arithmetic holds; the label is narrower than it sounds.

## 9. Column-name collisions between committed tables

Reported, not repaired. No existing file was modified by this audit.

**9.1 `V2_LIGAND_TABLE.csv` column `denovo_rank` is not the library `denovo_rank`.** It holds the batch-1 queue's `dock_priority_rank` (`cand_id == "DN%05d" % denovo_rank` for all 2988 rows: True). It coincides with the design's true `DENOVO_15000.csv` rank in only **52 / 2988** rows; the largest discrepancy is **585** positions. Joining screening results back to the library on that column would mis-map almost every row.

**9.2 `DENOVO_BATCH2_REMAINING12000_TAUTOMER_CORRECTED.csv` carries a `dock_priority_rank` column that is a copy of its library rank** (equal to `denovo_rank` for every row: True). These 12,000 designs are by definition the ones *not* in the batch-1 dock queue, yet **490** of those values also occur as real `dock_priority_rank` values in `DENOVO_TOP3000_FOR_DOCKING_TAUTOMER_CORRECTED.csv`, and **0** of those 490 name the same molecule. A join across the two tables on `dock_priority_rank` would silently pair unrelated designs.

