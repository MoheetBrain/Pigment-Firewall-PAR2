# PAR2 Pigment Firewall — live pipeline status

Updated: 2026-09-04 · branch `yonsei-final10-v2`

Mechanistic priority: **5NDD / AZ8838 orthosteric is the primary lane** (complete
monophasic trypsin blockade); 5NDZ / AZ3451 is retained as a hedge, not as an
equal. No quota is forced on the final selection.

## CURRENT STATE

| Track | Status |
|---|---|
| Reference IFP repair | **DONE** — repaired, verified, 5NDD now shows 2 H-bonds |
| Batch-1 EX8 screen (2,988 designs) | **DONE** — 3,442 jobs, 30,978 poses, 0 failures |
| Batch-1 ProLIF over all 30,978 poses | **DONE** — 0 failures |
| Batch-1 evidence table | **DONE** — `SCREEN_REAL/EVIDENCE_batch1.csv` |
| Full 15k library audit | **DONE** — `02_DENOVO_CPU/DENOVO_FULL_LIBRARY_AUDIT.md` |
| Batch-2 preparation (12,000 designs) | **DONE** — 11,837 unique, 12,872 jobs, 130 shards |
| Batch-2 EX8 screen | **RUNNING** on h3 |
| A100 / PIGNet2 | **RUNNING** — install + control validation |
| Boltz-2 | not started (deliberate — controls only, after PIGNet2) |

## ACTIVE H3 JOB

`screen_ex8_batch2` — 12,872 jobs, 130 shards, 22 workers x 4 CPU, EX8, 9 modes,
CPU-only. Started ~13:35 UTC. Projected ~3 h from the measured batch-1 rate of
18.5 s per 4-CPU job. Output: `SCREEN_REAL/screen_ex8_batch2/`.

## ACTIVE A100 JOB

PIGNet2 install and control validation on `a100-40` (us-central1-b). Controls:
crystallographic 5NDD+AZ8838, 5NDZ+AZ3451, and the nine redock poses of each.
Output: `YONSEI_FINAL10_V2/A100_TRACK/`.

## COMPLETED, WITH NUMBERS

**Reference IFP repair.** Receptors protonated with Open Babel at pH 7.4 (4,599 H
added to 5NDD, 4,533 to 5NDZ); ligands rebuilt from the wwPDB template SMILES
with bond orders reassigned onto the crystal coordinates (max heavy-atom shift
0.000000 Å) and hydrogens added. 5NDD corrected InChIKey
`IDFPQEHZYBXIFO-LBPRGKRZSA-N` matches wwPDB; aromatic bonds 6 → 11.

Four-condition control, which separates the two defects cleanly:

| Condition | 5NDD interactions / H-bonds | 5NDZ interactions / H-bonds |
|---|---|---|
| A as committed | 8 / 0 | 8 / 0 |
| B ligand H, stored tautomer | 10 / 0 | 10 / 0 |
| C ligand H, corrected tautomer | 15 / **2** | 11 / 0 |
| D repaired ligand + receptor H | 16 / **2** | 12 / 0 |

5NDD hydrogen bonds recovered: TYR:82 (2.475 Å, DHA 153.9°) and HIS:135
(2.63 Å, DHA 138.9°), both ligand-as-donor. These are the two contacts the
verification report flagged as being missed, and both are literature-consistent
anchors for AZ8838.

**5NDZ genuinely forms no hydrogen bond**, and this is a finding rather than a
detection failure: the ligand carries 7 polar atoms and 1 polar hydrogen, the
receptor 1,541 polar atoms and 4,533 hydrogens, yet only one polar pair lies
within 3.5 Å (TYR:210 OH ··· ligand N at 3.393 Å). The identical code path fires
twice in 5NDD, which proves the detector works. Consistent with the allosteric
site being a lipid-facing hydrophobic pocket. No interaction was forced.

**Batch-1 IFP.** 30,978 poses fingerprinted, 0 failures. Best-pose recovery:
5NDD median 0.75, p90 0.875, max 1.00, with 968 of 2,317 ligands making at least
one hydrogen bond; 5NDZ median 0.417, max 0.833.

**Pose disagreement — why all 9 modes are kept.** Of 3,442 ligand-pocket pairs,
the CNN-ranked pose (pose 1, because `--cnn_scoring rescore` sorts by CNNscore)
is the best-Vina pose in only 672, and the best-IFP pose in only 441. Best-Vina
and best-IFP coincide in 684. Collapsing to one pose would discard most of the
evidence.

## FAILED / FIXED

Three defects found and fixed before the batch-1 screen: the wrong AZ8838
tautomer (394 designs rebuilt), AppleDouble `._*` files entering shard globs, and
a temp filename that made GNINA emit nothing while exiting 0.

Two further defects found in my own pre-flight while gating batch 2:
1. the output-separation gate treated the *completed* batch-1 results as
   contamination. It now checks only the directory the new run will write into,
   and separately proves no dry-run file sits inside the real root.
2. **a silent no-op**: the preparation before/after comparison built ids with a
   hard-coded `DN` prefix, so for batch 2 (`DL` prefix) it compared **zero**
   molecules and still reported PASS. It now derives the prefix from the table
   and fails if fewer than 20 molecules were actually compared. Re-verified:
   batch 1 25 compared (prefix `DN`), batch 2 25 compared (prefix `DL`).

## KNOWN ISSUES CARRIED FORWARD

- `V2_LIGAND_TABLE.csv`'s `denovo_rank` holds the batch-1 *queue* rank, not the
  library rank; the two agree in only 52 of 2,988 rows. Never join screening
  results back to the library on that column — join on `cand_id` or InChIKey.
- `dock_priority_rank` values collide across batches while naming different
  molecules. Batch ids are disjoint by prefix (`DN` vs `DL`), so use those.
- 7 batch-1 and 17 batch-2 "duplicate InChIKey" collapses arise because
  `TautomerEnumerator().Canonicalize()` strips stereo before the key is computed;
  at least two batch-1 pairs are genuine R/S epimers, not duplicates. The
  arithmetic holds but the label is misleading, and stereochemistry matters for
  the target profile.
- CNNscore and CNNaffinity are uncalibrated ranking features, never probabilities
  of antagonism. Static docking cannot separate an antagonist from a biased
  agonist — that requires the functional assays.

## NEXT DEPENDENCY

Merged full-library EX8 universe needs batch-2 docking + ProLIF. Consensus
ranking additionally needs PIGNet2 from the A100.

## GIT

Branch `yonsei-final10-v2`, last commit `ca2f4a9` (batch-1 EX8 results).
