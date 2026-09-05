# Full library accounting — de novo EX8 screen

Generated 2026-09-05 on the local Mac by
`scripts/v2_full_accounting.py`. Every number below was recomputed from the
primary artefact named in the `source` column of
`FULL_LIBRARY_ACCOUNTING.csv`; none was carried over from an earlier report.
The machine-readable table has 101 rows: 98 `COMPUTED`, 1 `DISCREPANCY`,
1 `REPORTED_NOT_RECOMPUTABLE`, 1 `UNKNOWN`.

Reproduce with:

```
.venv-v2/bin/python YONSEI_FINAL10_V2/scripts/v2_full_accounting.py \
  --recovery ../PAR2_WORKER_RECOVERY_2026-09-05 \
  --universe YONSEI_FINAL10_V2/10_FINAL/COMPLETE_RECOVERED_EX8_UNIVERSE.csv \
  --stereo-audit YONSEI_FINAL10_V2/10_FINAL/STEREOCHEMISTRY_AUDIT.csv \
  --out YONSEI_FINAL10_V2/10_FINAL/FULL_LIBRARY_ACCOUNTING.csv \
  --verify-shard-hashes
```

Docking scores and fingerprint recoveries are ranking evidence only. Nothing
here is a claim of biological activity.

---

## 1. Generation

| Quantity | Value | How it was obtained |
|---|---:|---|
| Raw structures enumerated | 182,734 | `GENERATION_MANIFEST.json`: 120,331 in the initial pass plus 62,403 across three refill rounds. **Reported, not recomputable** — the raw molecules were never retained. |
| Scored candidate pool, rows | 17,074 | row count of `SCORED_CANDIDATES.csv` |
| Scored candidate pool, unique SMILES | 17,011 | **DISCREPANCY**: 63 rows of that file repeat a SMILES already present. It is a pre-selection scoring pool, and the 15,000 selected designs are unique, so nothing downstream inherits the repeat; the file itself is nevertheless not a set. |
| **Original generated structures (the library)** | **15,000** | row count of `DENOVO_15000.csv`; matches `requested_total` in the generation manifest |
| Unique `denovo_rank` values | 15,000 | one rank per design, 1–15,000 |
| Unique raw SMILES strings | 15,000 | no literal string repeats |

### Unique parent molecules

"Unique parent molecules" depends entirely on which identity you use, so all
four are given rather than one:

| Notion of identity | Distinct structures |
|---|---:|
| `STEREO_ID` — canonical isomeric SMILES | 15,000 |
| Stereo-aware InChIKey | 15,000 |
| `CONNECTIVITY_ID` — canonical SMILES, `isomericSmiles=False` | 14,081 |
| Flat InChIKey (stereo layer removed) | 14,081 |
| `TAUTOMER_PARENT_ID` — canonical SMILES of the tautomer-canonical parent | 14,975 |

The library therefore holds **919 designs that are additional stereoisomers of a
skeleton it already contains** (15,000 − 14,081), and tautomer canonicalisation
alone merges 25 designs onto 14,975 parents. Every design is distinct as a
stereochemical entity; none is distinct once stereochemistry is discarded and
another design shares its skeleton.

## 2. Queue split

| Quantity | Value |
|---|---:|
| Batch-1 docking queue (`DENOVO_TOP3000_FOR_DOCKING_TAUTOMER_CORRECTED.csv`) | 3,000 |
| Batch-2 remainder (`DENOVO_BATCH2_REMAINING12000_TAUTOMER_CORRECTED.csv`) | 12,000 |
| Sum | 15,000 |
| Designs appearing in both queues (by original SMILES) | 0 |
| Library designs in neither queue | 0 |
| Tautomer-corrected inputs, batch 1 / batch 2 | 394 / 1,737 |

The two queues partition the library exactly.

### Verified landmines

* **`denovo_rank` is the queue rank, not the library rank.** In batch 1 the
  queue's `dock_priority_rank` equals the library `denovo_rank` in exactly
  **52 of 3,000** queue rows, and in **52 of the 2,988** rows that survived
  preparation — `v2_prepare_ligands.py` writes `denovo_rank = dock_priority_rank`
  into `V2_LIGAND_TABLE.csv`. In batch 2 `denovo_rank`, `library_rank` and
  `dock_priority_rank` are all identical (12,000 of 12,000 rows), which is why
  the defect is invisible there and dangerous when the two batches are pooled.
* **`dock_priority_rank` collides across batches.** 487 rank values occur in
  both prepared batches, and all 487 name different molecules (`smiles_input`
  differs in every case). `cand_id` never collides: 0 shared ids between the
  `DN` and `DL` prefixes. Join on `cand_id` or InChIKey only.

## 3. Preparation

| Quantity | Batch 1 | Batch 2 | Total |
|---|---:|---:|---:|
| Queue rows in | 3,000 | 12,000 | 15,000 |
| Prepared successfully | 2,995 | 11,854 | 14,849 |
| Failed at preparation | 5 | 146 | 151 |
| Collapsed as duplicate InChIKey | 7 | 17 | 24 |
| Unique ligands shipped to docking | 2,988 | 11,837 | 14,825 |

`15,000 − 151 − 24 = 14,825`. Both preparation manifests agree with these
recomputed values on every line.

**Failure reasons.** All 151 failures are `EMBED_FAILED` — ETKDGv3 produced no
conformer, including after the `useRandomCoords` retry. There are no
`SMILES_PARSE_FAILED`, `UNSUPPORTED_ELEMENT`, or heavy-atom-bound failures.
No row in either shipped ligand table has `prep_ok = False`.

**Duplicate-InChIKey collapses.** All 24 are analysed in
`STEREOCHEMISTRY_AUDIT.md`. None is a true duplicate.

**One structure was docked twice.** De-duplication ran inside each batch
independently, so `DN00314` and `DL03110` — an R/S epimer pair that both lost
their stereocentre during preparation — became the same prepared structure
(`YUIAMUUFZPWUAJ-UHFFFAOYSA-N`) and were both docked. 1 structure, 2 cand_ids.

## 4. Docking jobs queued

Ligands route to one or both pockets, so jobs exceed ligands.

| Pocket | Batch 1 | Batch 2 | Total |
|---|---:|---:|---:|
| 5NDD orthosteric | 2,317 | 9,049 | 11,366 |
| 5NDZ allosteric | 1,125 | 3,823 | 4,948 |
| **All** | **3,442** | **12,872** | **16,314** |

Recomputed by expanding the `pockets` column of both ligand tables; both
preparation manifests agree.

## 5. Docked and analysed on 2026-09-04

| Quantity | Value |
|---|---:|
| Batch-1 ligand–pocket results | 3,442 |
| Batch-1 molecules | 2,988 |
| Batch-2 ligand–pocket results | 8,899 |
| Batch-2 molecules | 8,497 |
| **Total ligand–pocket results** | **12,341** |
| **Total unique molecules** | **11,485** |
| Batch-1 jobs with no result | 0 |
| Batch-2 jobs with no result at that point | 3,973 |

Batch 1 was complete. The 11,485 figure is the universe described by commit
`f342a8d`.

## 6. Newly recovered from the workers

| Quantity | Value |
|---|---:|
| Recovered pose shards | 282 |
| Sentinels recorded | 282 |
| Sentinels with a non-zero GNINA return code | 0 |
| Shards whose SHA-256 matches its sentinel (re-hashed here) | 282 |
| Shards failing that check | 0 |
| Ligand–pocket results parsed from the recovered shards | 7,049 |
| **Of those, duplicating the 2026-09-04 analysis** | **5,799** |
| **Of those, new** | **1,250** |
| New results carried into `EVIDENCE_recovered.csv` | 1,250 |
| New molecules | 1,250 |
| New molecules with no prior result in either pocket | 1,059 |
| New molecules that already had the other pocket | 191 |

The 1,250 new results fall inside exactly 50 shards, and those 50 shards contain
no result that was already known — the new and previously-analysed shard sets do
not interleave. The 5,799 overlapping results were re-derived independently and
compared against `EVIDENCE_batch2.csv`: `n_poses`, top-pose affinity, best
affinity, acceptable-pose count and clash flag agree to the last digit on all
5,799 (maximum absolute difference 0.0). No PIGNet2 rescoring exists for
batch-2 or recovered poses, so `pignet2_*` stays missing in those rows rather
than being filled with a placeholder.

## 7. The complete universe

`10_FINAL/COMPLETE_RECOVERED_EX8_UNIVERSE.csv`

| Quantity | Value |
|---|---:|
| Ligand–pocket rows | 13,591 |
| Duplicate `(cand_id, pocket)` keys across the three inputs | 0 |
| Rows from `EVIDENCE_batch1.csv` / `batch2` / `recovered` | 3,442 / 8,899 / 1,250 |
| 5NDD orthosteric rows | 9,641 |
| 5NDZ allosteric rows | 3,950 |
| Unique `cand_id` | 12,544 |
| Unique prepared structures | 12,543 |
| Rows where every GNINA pose clashes (`minimizedAffinity ≥ 0`) | 1,690 |
| **Unique cand_ids with usable evidence** | **10,919** |
| **Unique structures with usable evidence** | **10,918** |

"Usable evidence" means at least one pose in at least one pocket survived the
clash filter. The structure counts are one lower than the cand_id counts because
of the `DN00314` / `DL03110` pair.

Composition by design family (unique molecules): orthosteric 8,350,
allosteric 2,757, exploratory 1,437.

## 8. Never docked, or docked and lost

| Quantity | Value |
|---|---:|
| Jobs queued | 16,314 |
| Jobs with a surviving result | 13,591 |
| **Jobs with no surviving result** | **2,723** |
| — 5NDD orthosteric | 1,725 |
| — 5NDZ allosteric | 998 |
| Prepared molecules with no result in any pocket | 2,281 |
| — from batch 1 | 0 |
| — from batch 2 | 2,281 |

Batch-2 docking was dispatched as 25-ligand `shardNNNN_pM` partitions of the
100-ligand screen-set shards. Partition membership was reconstructed from the
shard SDFs preserved on the recovered workers (verified against a recovered
pose file: the four partitions of `5NDD_orthosteric_shard0055` reproduce
records 1–25, 26–50, 51–75 and 76–100 exactly).

| Quantity | Value |
|---|---:|
| Batch-2 dispatch partitions | 515 |
| Partitions with a result for every ligand | 406 |
| Partitions with no result for any ligand | 109 |
| Partitions with a partial result | **0** |
| Ligand–pocket jobs inside the 109 empty partitions | 2,723 |

Every missing job lies inside a partition that produced nothing at all; not one
partition is half-finished. The 109 empty partitions span 31 screen-set shards
and are listed in `MISSING_BATCH2_PARTITIONS.csv`.

**Independent corroboration.** `10_FINAL/EX8_TRUE_MISSING_JOBS.csv`, produced
separately in this sprint, lists 2,723 missing jobs; its `(cand_id, pocket)` set
is *identical* to the one computed here — 0 rows in one and not the other — and
its per-pocket split is the same 1,725 / 998. Its companion
`EX8_MISSING_JOBS.csv` lists 3,973 rows, matching the pre-recovery figure above.
That file attributes the gap to 17 of the 250-ligand preparation shards; this
one attributes it to 109 of the 25-ligand dispatch partitions. The two are
different granularities of the same gap, not a disagreement.

### Irrecoverably lost

**UNKNOWN, and it must stay unknown.** `pw-n2b` was deleted together with its
auto-delete boot disk before the 2026-09-05 export, and its output after 14:45
on 2026-09-04 is gone. No surviving artefact records which partitions `pw-n2b`
was assigned or which it finished: the workers each received all 130 shards and
partitioned locally, the sentinels only exist for shards that were exported, and
no dispatcher log survives. The 2,723 jobs above are therefore a **joint** total
of "never dispatched" and "dispatched to `pw-n2b` after 14:45 and lost with the
disk". The split between those two cannot be computed, and no split is asserted.

What *can* be said: the loss is confined to whole 25-ligand dispatch units, so
no partially written or truncated result entered the universe.

## 9. End-to-end reconciliation

```
15,000  designs generated and selected
   -151  failed at preparation (all EMBED_FAILED)
    -24  collapsed as "duplicate InChIKey" (see the stereochemistry audit)
 ------
 14,825  unique prepared ligands
     ->  16,314 ligand-pocket docking jobs queued (some ligands route to both pockets)

 16,314  jobs queued
-13,591  jobs with a surviving result
 ------
  2,723  jobs with no surviving result (never dispatched OR lost with pw-n2b; split UNKNOWN)

 13,591  ligand-pocket rows in the complete universe
        = 3,442 batch 1 + 8,899 batch 2 + 1,250 newly recovered
 12,544  unique cand_ids  (12,543 unique structures)
 -1,625  cand_ids whose every pose clashes in every pocket they were docked in
 ------
 10,919  cand_ids with usable evidence  (10,918 unique structures)
```

(14,825 prepared − 12,544 with a result = 2,281 prepared molecules never
returned a result; 12,544 − 10,919 = 1,625 returned only clashing poses.)
