# Project Ledger

Append-only. One entry per commit, in chronological order.

---

## 2026-09-04 · V2 screen pipeline built; de novo ligand library prepared

**Branch:** `yonsei-final10-v2`
**Project stage:** V2 campaign, stage 4 — ligand preparation complete, GNINA
screen not yet executed.

**Objective of the change**
Turn the finished 15,000-design de novo campaign into an executable, resumable
dual-pocket GNINA screen and the analysis chain that follows it, so that the
best de novo chemotypes can be identified and used as similarity-search queries
for real, purchasable analogue molecules.

Mid-task the user issued a course correction: do not expand this into a mass
screening pipeline, restrict actual GNINA screening to roughly the best 3,000
de novo designs, keep the 15,000-design library intact, and stop short of
nominating a final ten. The work below reflects that corrected scope.

**Files and systems changed**
- Added `YONSEI_FINAL10_V2/scripts/v2_prepare_ligands.py`
- Added `YONSEI_FINAL10_V2/scripts/v2_select_screen_set.py`
- Added `YONSEI_FINAL10_V2/scripts/v2_run_screen.sh`
- Added `YONSEI_FINAL10_V2/scripts/v2_collect_scores.py`
- Added `YONSEI_FINAL10_V2/scripts/v2_interactions.py`
- Added `YONSEI_FINAL10_V2/scripts/v2_postdock_rank.py`
- Added `YONSEI_FINAL10_V2/scripts/v2_cluster_and_seed.py`
- Added `YONSEI_FINAL10_V2/scripts/v2_similarity_search.py`
- Added `YONSEI_FINAL10_V2/scripts/v2_rank_and_select.py` (later gate)
- Added `YONSEI_FINAL10_V2/04_V2_SCREEN/` outputs and `RUNBOOK.md`
- Added `docs/PROJECT_STATUS.md` and `docs/PROJECT_LEDGER.md`
- Updated `.gitignore`

**What was completed**
- 8,973 input rows (3,000 de novo + 5,973 sourceable) standardised, protonated
  at approximate pH 7.4, embedded in 3D and deduplicated to 7,324 unique
  ligands (2,985 de novo, 4,339 sourceable).
- De novo screen set built: 2,985 designs, 3,436 ligand-pocket jobs
  (5NDD 2,314 · 5NDZ 1,122), 15 shards, coordinates copied verbatim from the
  prepared library.
- Complete downstream chain implemented and rehearsed end to end.
- Runbook written for `h3` (88 cores, 22 GNINA processes × 4 CPU).

**Decisions made and why**
- Screen scope narrowed to the de novo designs, per the user's course
  correction. The sourceable universe remains prepared but unscreened.
- Single-stage screening at the validated benchmark settings (exhaustiveness
  32, 9 poses) instead of a reduced-exhaustiveness pre-pass: on 88 cores the
  full de novo screen is roughly 1.5–2 hours, so a pre-pass saves nothing and
  would produce scores not comparable to the reference benchmark.
- All poses retained rather than pose 1, because the benchmark showed the 5NDZ
  top-ranked pose at 2.23 Å against a best pose of 0.87 Å.
- Ranking z-scores computed within each pocket; 5NDD and 5NDZ never pooled.
- Novelty implemented as a capped one-sided bonus, never a penalty.
- Seed selection uses a 25% per-pocket floor plus rank-driven fill, rather than
  a fixed 50/50 quota, so both mechanisms appear without overriding evidence.
- The 51 MB full prepared shard library is gitignored as deterministically
  reproducible; the 14 MB de novo screen set is committed because the VM needs
  it.

**Tests and verification actually executed**
- `ast.parse` on all eight new Python scripts: passed.
- `bash -n YONSEI_FINAL10_V2/scripts/v2_run_screen.sh`: passed.
- Protonation rule set on 20 hand-picked structures: all expected. This found a
  real defect — the first implementation used reaction SMARTS without atom maps
  and silently reduced molecules to their matched fragment (a 18-heavy-atom
  acid became formate). Replaced with direct atom edits and re-verified.
- `v2_prepare_ligands.py --limit 40` smoke test: 150 SDF records, 0 unparsable,
  exactly 1 conformer per record.
- Full preparation on 8,973 rows: 8,469 prepared, 504 failed (188 too few heavy
  atoms, 293 too many, 16 embed failures, 7 unsupported elements), 1,145
  duplicate InChIKeys collapsed, 7,324 unique ligands.
- `v2_select_screen_set.py`: 2,985 ligands, 3,436 jobs, 15 shards.
- `v2_run_screen.sh --dry-run`: GNINA command lines carried the exact validated
  box centres and sizes for both pockets.
- Synthetic-score rehearsal at production scale: `v2_collect_scores.py` (288
  poses on the small set; 3,436 synthetic rows on the full set),
  `v2_interactions.py` (ProLIF 2.2.1, 96 pairs, 0 failures),
  `v2_postdock_rank.py` (2,985 designs, 451 dual-pocket),
  `v2_cluster_and_seed.py` (400 designs; 259/326/381 clusters at
  0.55/0.65/0.75; 30 seeds across 30 clusters and 30 scaffolds).

**Results**
The pipeline runs end to end and the de novo ligand library is ready to screen.

**Failures or unresolved uncertainty**
- **No GNINA docking has been run.** Every score in the rehearsal is randomly
  generated and scientifically meaningless. The rehearsal proves plumbing only.
- `v2_similarity_search.py` has never contacted the live PubChem or ChEMBL
  endpoints; those calls are unverified.
- The reference benchmark has not been re-run on `h3`.
- Blocker: the authenticated gcloud account `cloud@hamiltonianlabs.co` cannot
  see project `project-08679972-d14a-4025-94f`. Both `moheetc4` and `h3` return
  `Required 'compute.instances.get' permission`. A `gcloud auth login` flow is
  open and waiting for a verification code.

**Effect on the overall project**
The campaign moves from "15,000 designs on disk" to "3,436 docking jobs queued
and every downstream analysis stage written and rehearsed". The only thing
between here and a ranked chemotype map is compute access.

**Next intended step**
Authenticate, SSH to `h3`, install pinned GNINA, re-pass the reference gate on
that machine, then run the 3,436-job de novo screen.

---

## 2026-09-04 · Pre-flight passed on `h3`; real de novo EX8 screen launched

**Branch:** `yonsei-final10-v2`
**Project stage:** V2 campaign, stage 5 — real GNINA screen running.

**Objective of the change**
Reach the execution gate: prove on the target machine that the engine docks into
the real PAR2 pockets with both Vina and CNN scoring working, then use all 88
cores. The user required a strict fail-closed pre-flight, CPU-only execution,
and no fallback of any kind.

**Files and systems changed**
- Merged `origin/yonsei-final10-v2` commit `e992aa7` (independent verification).
- Added `YONSEI_FINAL10_V2/scripts/v2_preflight.py` (35 gates, exits non-zero).
- Added `02_DENOVO_CPU/DENOVO_TOP3000_FOR_DOCKING_TAUTOMER_CORRECTED.csv`.
- Added `YONSEI_FINAL10_V2/SCREEN_REAL/` and `SCREEN_DRYRUN/`, including
  `SCREEN_REAL/DRY_RUN_VALIDATION.md`.
- Hardened `v2_run_screen.sh`; corrected the AZ8838 reference SMILES in
  `v2_postdock_rank.py`; added `--denovo-queue`/`--sources` to the preparer;
  made every shard and pose glob skip dotfiles.
- Updated `docs/PROJECT_STATUS.md`.

**What was completed**
- GCP access repaired and pinned in a named `par2` gcloud configuration.
- `h3` verified: x86_64, 88 physical cores, 346 GiB RAM, disk grown 10 to 60 GB.
- GNINA v1.3.3 deployed, SHA-256 matching the benchmarked binary exactly.
- 394 wrong-tautomer designs corrected; de novo library re-prepared to 2,988
  designs, 3,442 jobs, 36 shards.
- 35/35 pre-flight gates passed on `h3`.
- Reference redock on `h3` reproduced the August benchmark to four decimals.
- Real 12-design dry run passed all raw-score, pose-location and parser checks.
- Full 3,442-job EX8 screen launched at 22 processes x 4 CPU.

**Decisions made and why**
- Corrected the 394 affected designs rather than screening known-wrong chemistry
  or discarding them: molecular formula is preserved in all 394 and imidazole
  aromaticity restored in every case.
- Kept EX8 for the screen as instructed, retaining 9 modes, because the 5NDZ
  reference recovers its crystal pose at mode 2 rather than mode 1.
- Excluded IFP from the go decision because the reference fingerprints are known
  to contain no hydrogen bonds.

**Tests and verification actually executed**
Recorded with numbers in `SCREEN_REAL/DRY_RUN_VALIDATION.md`: box values match
the corrected definitions to 0.000000 A; crystal ligand centroids sit 0.0007 A
and 0.0004 A from the box centres; 17/17 and 38/38 ligand heavy atoms inside the
boxes; 88 and 61 receptor heavy atoms within 5 A of the crystal ligands; 199 and
259 receptor heavy atoms inside the boxes; 8/8 and 10/11 expected pocket
residues; no HETATM in either receptor; best-pose RMSD 0.6747 A (5NDD, pose 1)
and 0.8672 A (5NDZ, pose 2), both under the 2.0 A gate; all four score fields
present, finite and non-constant over 135 dry-run poses with 135 unique values
each; 135/135 dry-run pose centroids inside the configured box; parser versus raw
maximum absolute difference 0 for every score field; preparation accounting
3,000 = 2,995 + 5 with all failures itemised; routing 1,863 + 671 + 2 x 454 =
3,442 with 0 misrouted.

**Results**
Pre-flight verdict GO; the production screen is running.

**Failures or unresolved uncertainty**
- Three defects found and fixed during pre-flight: the wrong AZ8838 tautomer,
  AppleDouble `._*` files entering shard globs, and a temporary filename that
  made GNINA emit nothing while still exiting 0.
- The reference interaction fingerprints still contain no hydrogen bonds and
  must be repaired before IFP is weighted.
- Docking-queue membership was selected with the defective reference; about 19%
  of orthosteric slots would differ if reselected. Out of scope for this run.
- 5NDD best IFP recovery measured 0.600 on `h3` against 0.700 in the handoff.
- The screen had not finished when this entry was written.

**Effect on the overall project**
The engine is proven to dock into the real PAR2 pockets on the production
machine with both Vina and CNN scoring live, and the full screen is under way.

**Next intended step**
Collect the EX8 results and report the required sanity review before any
downstream ranking, clustering or similarity searching.

---

## 2026-09-04 · Real de novo EX8 screen completed on `h3`

**Branch:** `yonsei-final10-v2`
**Project stage:** V2 campaign, stage 5 — EX8 screen complete, sanity review done.

**Objective of the change**
Execute the validated de novo dual-pocket screen on all 88 cores and report the
required sanity review before any downstream stage.

**Files and systems changed**
- Added `SCREEN_REAL/screen_ex8/` results: per-pose scores, per-ligand-per-pocket
  aggregate, collection summary, run metadata and all 36 shard `.done` sentinels.
- Added `SCREEN_REAL/PREFLIGHT_H3.json`.
- Updated `docs/PROJECT_STATUS.md`.

**What was completed**
3,442 of 3,442 jobs succeeded, 0 failed. 30,978 poses parsed, exactly 9 per job.
2,988 unique designs scored. 60.4 minutes wall clock, 70.9 core-hours, mean 18.5
seconds per 4-CPU job. Every shard exited rc=0 at exhaustiveness 8, 9 modes,
device cpu.

**Decisions made and why**
No parameter was changed mid-run and no fallback was taken; the runner has none.
Results were collected but deliberately not ranked, fingerprinted or clustered,
because the user required a sanity review first.

**Tests and verification actually executed**
- Job and pose accounting: 3,442 requested = 3,442 successful; 30,978 poses
  expected = 30,978 parsed; 0 ligands with a pose count other than 9.
- Routing preserved: orthosteric 1,863, allosteric 671, exploratory 454 designs;
  2,317 5NDD jobs and 1,125 5NDZ jobs.
- Score integrity over all 30,978 poses: no NaN, no zeros, none constant;
  30,521 / 30,947 / 30,859 / 30,958 unique values for minimizedAffinity,
  CNNscore, CNNaffinity and CNN_VS respectively.
- Anomaly analysis: 8,444 of 30,978 poses (27.26%) have positive Vina affinity,
  and 119 ligands have a positive best pose. All 119 are in the small 5NDD box
  and are larger than average (median MW 360.5 vs 310.4, 26 vs 22 heavy atoms),
  so this is a steric-fit result, not a scoring defect.
- Pose ordering: only 672 of 3,442 ligands (19.5%) have their best Vina affinity
  at pose 1, because `--cnn_scoring rescore` sorts GNINA output by CNNscore
  rather than by Vina. Confirmed against the reference redock, whose CNNscore
  decreases monotonically down the pose list.

**Results**
Median best affinity -6.134 (5NDD) and -6.579 (5NDZ) kcal/mol; best -9.696 and
-8.715. Median best CNNscore 0.474 (5NDD) and 0.756 (5NDZ). 12 of the top 100
designs by CNN_VS are tautomer-corrected designs, so the correction is
materially represented in the leading chemistry.

**Failures or unresolved uncertainty**
- The reference interaction fingerprints still contain no hydrogen bonds and
  must be repaired before IFP is weighted in ranking.
- CNNscore and CNNaffinity remain uncalibrated ranking features.
- EX8 is a screening-level search; finalists still need EX32 refinement.

**Effect on the overall project**
The campaign now has real, validated docking evidence for every de novo design
in both intended pockets, replacing the synthetic plumbing data entirely.

**Next intended step**
Repair the reference fingerprints, then run ProLIF across poses, post-docking
ranking, EX32 refinement, clustering and seed selection.

---

## 2026-09-04 · Reference fingerprints repaired; batch-1 fingerprinted; batch-2 launched

**Branch:** `yonsei-final10-v2`
**Project stage:** V2 campaign, stage 6.

**Objective of the change**
Repair the reference interaction fingerprints before any ranking depends on them,
fingerprint every batch-1 pose against the repaired reference, and extend the
screen from the 3,000-design queue to the whole ~15,000-design de novo library.

**Files and systems changed**
- Added `scripts/v2_reference_ifp_repair.py`, `scripts/v2_merge_evidence.py`,
  `scripts/v2_full_library_audit.py`.
- Added `02_REFERENCE_VALIDATION_REPAIRED/` (protonated receptors, corrected
  protonated ligands, `REFERENCE_IFP_REPAIRED.json`).
- Added `SCREEN_REAL/EVIDENCE_batch1.csv` and its summary; batch-1
  `V2_POSE_INTERACTIONS_SUMMARY.csv`.
- Added `02_DENOVO_CPU/DENOVO_BATCH2_REMAINING12000_TAUTOMER_CORRECTED.csv`,
  `DENOVO_FULL_LIBRARY_AUDIT.csv/.md`, `DENOVO_REMAINING_TO_SCREEN.csv`.
- Added `PIPELINE_STATUS.md`.
- Updated `scripts/v2_interactions.py` to use the protonated receptors and the
  repaired reference keys, and to refuse to run against the unrepaired reference.
- Updated `scripts/v2_prepare_ligands.py` with `--id-prefix`, `--denovo-queue`
  and `--sources`; fixed two defects in `scripts/v2_preflight.py`.

**What was completed**
Reference repair passed. Batch-1 ProLIF over all 30,978 poses, 0 failures.
Batch-1 evidence table built. Full-library audit completed. Batch-2 prepared
(11,837 unique designs, 12,872 jobs, 130 shards) and its EX8 screen launched.

**Decisions made and why**
- A zero hydrogen-bond count for 5NDZ was reported as a finding rather than
  forced to be non-zero. The gate now proves hydrogen-bond DETECTION works
  (it fires twice in 5NDD through the identical code path) and reports the polar
  contact geometry explaining the zero, instead of assuming a bond must exist.
- Batch-2 ids use the `DL` prefix so they can never collide with batch-1 `DN`.
- The completed batch-1 run was neither rerun nor overwritten.

**Tests and verification actually executed**
- Reference repair four-condition control: 5NDD 8/0 → 10/0 → 15/2 → 16/2
  interactions/H-bonds across conditions A-D; 5NDZ 8/0 → 10/0 → 11/0 → 12/0.
  Corrected 5NDD InChIKey `IDFPQEHZYBXIFO-LBPRGKRZSA-N` matches wwPDB; aromatic
  bonds 6 → 11; max heavy-atom coordinate shift 0.000000 Å.
- 5NDD H-bonds recovered: TYR:82 2.475 Å DHA 153.9°, HIS:135 2.63 Å DHA 138.9°.
- 5NDZ polar diagnostic: 7 ligand polar atoms, 1 polar H, 1,541 receptor polar
  atoms, 4,533 receptor H, closest polar contact 3.393 Å, 1 pair within 3.5 Å.
- ProLIF over 30,978 batch-1 poses: 0 failures. Best-pose recovery 5NDD median
  0.75 / max 1.00 with 968 of 2,317 ligands making a hydrogen bond; 5NDZ median
  0.417 / max 0.833.
- Pose disagreement: of 3,442 pairs the CNN-ranked pose is the best-Vina pose in
  672 and the best-IFP pose in 441; best-Vina equals best-IFP in 684.
- Batch-2 preparation: 12,000 = 11,854 prepared + 146 failed (all EMBED_FAILED);
  11,854 - 17 duplicate InChIKeys = 11,837 unique.
- Batch-2 routing: 8,014 + 2,788 + 2 x 1,035 = 12,872 jobs, 0 misrouted.
- Pre-flight after the fixes: 36/36 gates on BOTH batches, with 25 molecules
  actually compared before/after in each (prefixes `DN` and `DL`).

**Results**
The repaired reference is in use, batch 1 is fully fingerprinted, and batch 2 is
docking.

**Failures or unresolved uncertainty**
- Two defects were found in my own pre-flight. One was cosmetic (completed runs
  flagged as contamination). The other was serious: the preparation before/after
  gate compared ZERO molecules for batch 2 and still reported PASS, because the
  cand_id prefix was hard-coded. Both are fixed and the gate now fails if fewer
  than 20 molecules are compared.
- `V2_LIGAND_TABLE.csv`'s `denovo_rank` is the queue rank, not the library rank
  (they agree in 52 of 2,988 rows). Joins must use `cand_id` or InChIKey.
- 7 batch-1 and 17 batch-2 "duplicate InChIKey" collapses come from
  `TautomerEnumerator().Canonicalize()` stripping stereo before the key is
  computed; at least two batch-1 pairs are genuine R/S epimers.
- The batch-2 screen had not finished when this entry was written.

**Effect on the overall project**
Interaction-fingerprint evidence is now chemically valid and usable in ranking,
and the screen is being extended from 20% to 100% of the de novo library.

**Next intended step**
Finish batch 2, fingerprint it, merge into one full-library universe, add
PIGNet2, then consensus-rank within pocket.

---

## 2026-09-04 · PIGNet2, clash filtering, consensus ranking, seeds and real analogues

**Branch:** `yonsei-final10-v2`
**Project stage:** V2 campaign, stage 7.

**Objective of the change**
Turn the batch-1 evidence into a ranked, clustered, seed-level deliverable and
retrieve real purchasable analogues, while batch 2 continues docking.

**Files and systems changed**
- Added `scripts/v2_pose_evidence.py` (clash-filtered per-molecule evidence),
  `scripts/v2_consensus_rank.py` (within-pocket consensus + PAR2 design profile).
- Added `A100_TRACK/` PIGNet2 outputs, `07_CONSENSUS/`, `08_CLUSTERS/`,
  `09_ANALOGUES/`.
- Fixed a silent data-loss bug in `scripts/v2_similarity_search.py`.

**What was completed**
PIGNet2 scored all 30,978 batch-1 poses on the A100 in 9 min 09 s, 0 failures.
Clash filtering, consensus ranking of 3,442 ligand-pocket rows, Butina
clustering per pocket, 34 seeds, and 521 unique real analogues retrieved.

**Decisions made and why**
- Metric families were set from the MEASURED Spearman structure rather than
  assumption: Vina/ligand-efficiency r = -0.958 and Vina/PIGNet2 r = 0.899 form
  one physics family; CNNscore/CNN_VS r = 0.988 form one CNN family; IFP
  recovery correlates |r| <= 0.19 with everything and is therefore the only
  orthogonal evidence, so it gets its own family instead of being outvoted.
- Poses with positive GNINA affinity are excluded before choosing the best-IFP
  pose, because a clashing pose can accumulate contacts and fake a high
  recovery. Molecules with no acceptable pose are flagged, not dropped.
- Agonist-mimicry geometry is a FLAG, not a filter: static docking cannot
  settle antagonist versus biased agonist.
- Pockets were clustered separately so 5NDZ stays represented as a hedge.

**Tests and verification actually executed**
- PIGNet2: 30,978 poses, 3,442 molecules x 9 poses, 0 failures, no NaN.
- Clash filter: 8,444 of 30,978 poses (27.26%) rejected; 119 molecules have no
  acceptable pose. Independently corroborated - GNINA's own minimizedAffinity is
  positive for the same poses.
- Consensus over 3,442 rows: 250 5NDD designs hydrogen-bond to at least one
  AZ8838 anchor, 12 to BOTH Asp228 and His135; 78 on the Pareto front;
  0 flagged for agonist-mimicry geometry.
- Clustering: 5NDD 267 clusters at 0.65 (172 at 0.55, 335 at 0.75), 5 convergent
  chemotypes; 5NDZ 216 clusters at 0.65.
- Seeds: 34 total (26 5NDD + 8 5NDZ), 34 distinct Murcko scaffolds, 34 distinct
  clusters, novelty split 20 novel / 13 scaffold-hop / 1 close-to-reference.
- Similarity search: 34 seeds queried, 522 raw hits, 521 unique after InChIKey
  deduplication, 27 of 34 seeds returned at least one hit. Morgan ECFP4 bands:
  1 hit in 0.70-0.80, 11 in 0.55-0.70, 20 in 0.50-0.55, 84 in 0.40-0.50.

**Results**
SEED03 retrieved genuine AZ8838-chemotype matter from PubChem, including
(4-fluoro-2-prop-1-enylphenyl)-(1H-imidazol-2-yl)methanol and two further
examples from patent US10550089 at Tanimoto 0.615, all sharing its Murcko
scaffold. The pipeline independently recovered real PAR2-antagonist chemistry.

**Failures or unresolved uncertainty**
- A silent data-loss bug was found in the similarity search: PubChem renamed
  `CanonicalSMILES` to `ConnectivitySMILES`, so every returned hit was being
  discarded and the first run reported 12 hits across 29 seeds. After the fix
  the same query returns 522. The code now accepts four SMILES spellings.
- No hit reaches Tanimoto 0.80, so no seed has a very close purchasable
  analogue; the designs are genuinely novel relative to public chemistry.
- Vendor, catalogue ID, price and stock remain PENDING - not looked up.
- Batch 2 was still docking when this entry was written, so the consensus,
  clusters and seeds cover batch 1 only and will be refreshed.
- EX32 refinement, Boltz-2 and MD were not started.

**Effect on the overall project**
There is now a complete, defensible chain from docking evidence to a diverse
seed set and real purchasable analogues, with the orthogonality of each metric
measured rather than assumed.

**Next intended step**
Merge batch 2 as it lands, refresh the consensus and seeds over the full
library, then EX32 refinement and the functional-assay handover.

---

## 2026-09-04 · Full-library consensus over 11,485 designs on six machines

**Branch:** `yonsei-final10-v2`
**Project stage:** V2 campaign, stage 7 (extended).

**Objective of the change**
Extend the screen across the whole de novo library inside a hard 15:17 UTC
deadline by adding compute, then refresh every downstream stage.

**Files and systems changed**
- Added `scripts/v2_final_report.py`; added `FINAL_CANDIDATES.md`.
- Refreshed `SCREEN_REAL/EVIDENCE_batch2.csv`, `07_CONSENSUS/`, `08_CLUSTERS/`.
- Added a pre-filter to `scripts/v2_interactions.py` so shortlist runs are cheap.

**What was completed**
Five additional workers were provisioned (c3-standard-88, n2-standard-80 x2,
h3-standard-88, plus a second h3) giving 512 cores. Batch 2 reached 8,899 of
12,872 jobs. Combined with batch 1 that is 12,341 of 16,314 jobs over 11,485
unique designs (76% of the library).

**Decisions made and why**
- The H3 CPU family quota capped at 176 vCPU in europe-west4, so capacity was
  spread across three machine families and two regions.
- Shards were re-split from 100 to 25 ligands. At ~36 s per ligand a 100-ligand
  shard needs ~60 minutes and only counts when complete, so nothing would have
  landed before the deadline. Ligand counts were verified preserved through
  every split (1900 -> 1900, 1723 -> 1723).
- h3 was left running its in-flight wave and switched automatically to
  fine-grained shards once that wave landed, rather than discarding work.

**Tests and verification actually executed**
- Every worker verified the GNINA binary SHA-256 as
  3340c1f49cd3c7c84d8699182a1c6af13c7fa2a22448d1204640446106f72172 before
  running, and each screen.log confirms exhaustiveness 8, num_modes 9,
  cnn_scoring rescore, device cpu.
- Batch-2 collection: 80,091 poses parsed over 8,899 ligand-pocket pairs.
- Batch-2 ProLIF: 80,091 poses, 0 failures; 5NDD best-pose recovery median
  0.8125, max 1.00; 3,391 5NDD ligands make at least one hydrogen bond.
- Batch-2 clash filter: 32,864 of 80,091 poses (41.03%) rejected; 1,457
  molecules have no acceptable pose and are flagged.
- Combined consensus: 12,341 rows, 11,485 unique designs, 9,066 5NDD and
  3,275 5NDZ. 1,298 5NDD designs hydrogen-bond at least one AZ8838 anchor and
  62 bond BOTH Asp228 and His135. Pareto front 130. Agonist-mimicry geometry
  flagged for 9 designs.
- Seeds refreshed: 34 (26 5NDD + 8 5NDZ) across 34 distinct Murcko scaffolds.

**Results**
`FINAL_CANDIDATES.md` carries the dual-anchor table, the top 20 in the primary
5NDD lane, the 34 seeds and the 521 retrieved real analogues.

**Failures or unresolved uncertainty**
- 24% of the library (3,973 jobs) had not finished docking at the deadline.
- Batch 2 has no PIGNet2 scores, so within the physics metric family batch-2
  rows are ranked on Vina and ligand efficiency only while batch-1 rows also
  carry PIGNet2. Cross-batch comparison is therefore not perfectly like-for-like.
- Batch-2 clash rate (41%) is much higher than batch-1 (27%), consistent with
  lower-ranked designs being larger and fitting the small 5NDD box poorly.
- EX32 refinement, Boltz-2 and MD were not started. No vendor check was done.

**Effect on the overall project**
Three quarters of the de novo library now has real, fingerprinted docking
evidence and a defensible ranked short list exists.

**Next intended step**
Finish the remaining 24%, add PIGNet2 for batch 2, then EX32 refinement of the
top 500-1,000 and the functional-assay handover.

---

## 2026-09-05 · Worker data recovery and disposable-VM deletion

**Branch:** `yonsei-final10-v2`
**Project stage:** V2 campaign, stage 7 — infrastructure cleanup, no new compute.

**Objective of the change**
Recover every unique artifact from the disposable PAR2 worker VMs, verify the
copies, then delete those VMs while preserving `a100`, `a100-40` and `h3`.

**Files and systems changed**
- Added `YONSEI_FINAL10_V2/RECOVERED_WORKERS/` with the four per-worker export
  manifests, the 282 recovered shard sentinels and `PAR2_RECOVERY_COMPLETE.md`.
- Updated `docs/PROJECT_STATUS.md`.
- No script or analysis output was modified; no ranking was recomputed.

**What was completed**
Four workers frozen (dispatcher stopped, GNINA terminated, filesystem synced),
inventoried, archived, pulled to the local Mac, verified, and deleted.

**Decisions made and why**
- Data was pulled to the Mac rather than to h3, on the user's explicit
  instruction, so it survives independently of any VM.
- Environments, virtualenvs, pip/conda caches and the 2 GB GNINA binary were
  excluded from the archives; they are reproducible and carry no project data.
- The 50 newly recovered pose shards were deliberately NOT merged into the
  committed rankings. Doing so would change published numbers without the
  ProLIF, clash-filter and consensus stages being rerun, and no compute was
  permitted.
- Raw archives (367 MB) are kept outside the repository; only manifests,
  sentinels and the recovery report are committed.

**Tests and verification actually executed**
- SHA-256 computed on each worker and again on the Mac after transfer:
  par2w3 89e7a578..., pw-c3a 49842974..., pw-h3b 33215d81..., pw-n2a 31b61931...
  All four match, and byte counts match exactly (21,050,184 / 18,131,069 /
  18,522,859 / 16,344,502).
- Archives re-extracted; path counts reconciled with `tar tzf` entry counts
  (475/381/331/435 entries).
- Recovered content: 282 pose shards and 282 `.done` sentinels.
- Overlap analysis against the 2026-09-04 merge: 50 pose shards were new.
- Deletion guard self-tested: attempting to delete `h3`, `a100` and `a100-40`
  each aborted on the allowlist check.
- Final instance list verified: only `a100`, `a100-40`, `h3` remain, TERMINATED.
- Origin verified to contain f342a8d, 7752707 and ca2f4a9.

**Results**
74,048,614 bytes recovered with full integrity; four VMs deleted; three
preserved; zero running instances.

**Failures or unresolved uncertainty**
- `pw-n2b` had already been deleted with its auto-delete boot disk before this
  cleanup started. Its output after the 14:45 pull on 2026-09-04 is
  unrecoverable. The earlier partial export survives and is in the analysis.
- The 50 recovered shards are not reflected in any committed ranking.
- 24 snapshots (1,250 GB nominal) from a daily schedule on the retired
  `moheetc4` continue to accrue storage cost.

**Effect on the overall project**
All worker-only data is preserved off-VM and billing from disposable workers has
ended. The committed science is unchanged.

**Next intended step**
None scheduled. If the campaign resumes, merge the 50 recovered shards and rerun
ProLIF, clash filtering and consensus before quoting new numbers.

---

## 2026-09-05 · Sprint checkpoint: recovered data, stereo audit, receptor and anchor corrections

**Branch:** `yonsei-final10-v2`
**Project stage:** V2 completion sprint, checkpoints 1-2.

**Objective of the change**
Reconcile the recovered worker data, audit stereochemistry, and resolve a
contradiction in the 5NDD anchor definition before any final ranking is built.

**Files and systems changed**
- Added `scripts/v2_anchor_metrics.py`, `v2_fix_receptor_protonation.py`,
  `v2_robust_anchors.py`.
- Added `10_FINAL/` with the complete EX8 universe, stereochemistry audit,
  AZ8838 reference interaction tables and the anchor definition audit.
- Added corrected receptors `*_receptor_pH74_FIXED.pdb`.

**What was completed**
The recovered shards were processed through the validated pipeline, the full
library was audited for stereochemistry, the 5NDD anchor definition was
re-derived from the structures, and two preparation defects were fixed.

**Decisions made and why**
- Anchors are now scored by heavy-atom polar distance rather than by ProLIF's
  hydrogen-bond call, because the hydrogen-bond assignment proved to be an
  artefact of preparation choices while the geometry is invariant.
- The previous `["ASP:228","HIS:135"]` anchor pair is retired.
- The agonist-mimicry flag is retired: two of its three residues (TYR:311 at
  8.7 A and LEU:230 at 10.6 A) do not line the pocket, so it measured nothing.

**Tests and verification actually executed**
- Complete EX8 universe: 13,591 ligand-pocket rows over 12,544 unique designs
  (9,641 5NDD, 3,950 5NDZ); 0 duplicate keys; 1,690 molecules have no
  acceptable pose. The recovered shards contributed 1,250 new rows.
- Stereochemistry: 15,000 designs audited, 0 parse failures. 8,581 PRESERVED,
  3,910 NEVER_PRESENT, 2,504 LOST, 5 ALTERED; 3,042 stereocentres lost.
  4,901 designs carry an unassigned stereocentre from the generator. The 24
  collapsed "duplicates" are 17 specified-vs-unspecified, 6 genuine epimeric
  pairs and 1 tautomer merge. 643 ranked designs need redocking: 201 were
  docked as the WRONG stereoisomer and 442 are ambiguous. A replication check
  reproduced the shipped InChIKey and prepared SMILES for all 14,825 rows.
- Receptor protonation: the campaign receptor was built with `obabel -h -p 7.4`,
  where `-h` overrides the pH model. Verified geometrically: all 39 lysines
  neutral (2 H on NZ), 17 of 29 aspartates and 10 of 23 glutamates protonated as
  neutral acids. No salt bridge was detectable anywhere in the campaign.
  Rebuilt with `-p 7.4` alone, which corrects the chemistry (39/39 Lys+, 0
  protonated acids) but renumbers every residue (PHE 59 -> PHE 167). Original
  numbering was transplanted by exact heavy-atom coordinate match, max shift
  0.000000 A.
- Reference fingerprint under the corrected receptor: 5NDD keeps 16 keys but
  LOSES `HIS:135|HBDonor` and GAINS `HIS:227|PiCation`, because Open Babel
  reassigned the histidine tautomers. 5NDZ is unchanged at 12 keys, still zero
  hydrogen bonds.
- Anchor recount (9,066 5NDD rows): old ASP228+HIS135 = 62; crystal
  TYR82+HIS135 = 81; the two sets are 95% disjoint (Jaccard 0.051, only 7 in
  common); any two of the three = 171; all three = 7.
- Robust anchor metric validated on the crystal reference: recovers 3/3 anchors
  at 2.475, 2.630 and 2.929 A, reproducing the crystallographic distances.

**Results**
The interaction-geometry evidence family, which carries the highest weight, has
been rebuilt on a preparation-independent basis.

**Failures or unresolved uncertainty**
- The published "62 dual-anchor designs" figure is wrong: only 7 of those 62
  reproduce the crystallographic hydrogen-bond signature. `FINAL_CANDIDATES.md`
  and `v2_final_report.py` still carry the old claim and must be corrected.
- ASP:228 was declared an anchor in `v2_consensus_rank.py` on the basis of a
  code comment citing "largest modelled electrostatic terms". There is no
  mutagenesis or FMO data in this repository to support it. That justification
  was unfounded.
- Which residues form hydrogen bonds depends on the ligand protomer AND the
  receptor histidine tautomer; all three ligand protomers share one InChIKey, so
  no integrity check catches the swap.
- The EX8 universe retains fingerprints computed against the old, incorrectly
  protonated receptor. Only the final selection pool will be re-fingerprinted.
- Web search and agent spawning are blocked in this session by a safety
  classifier, so live vendor, price and stock data cannot be obtained.

**Effect on the overall project**
The ranking is being rebuilt on evidence that survives preparation choices,
rather than on an anchor definition that did not match the crystal structure.

**Next intended step**
EX32 precision docking, the real-compound lane, then the final diverse panel.

---

## 2026-09-05 · Corrected stereochemistry audit and full library accounting

**Branch:** `yonsei-final10-v2`
**Project stage:** V2 completion sprint, checkpoint 1 finalised.

**Objective of the change**
Replace the intermediate stereochemistry artefacts committed in `5ed4448` with
the corrected finals, and add the exact full-library accounting.

**Files and systems changed**
- Corrected `10_FINAL/STEREO_REDOCK_LIST.csv`, `STEREOCHEMISTRY_AUDIT.summary.json`
  and `scripts/v2_stereo_audit.py` (bond-stereo counting and rank-scale fixes).
- Added `10_FINAL/FULL_LIBRARY_ACCOUNTING.{csv,md,summary.json}`,
  `MISSING_BATCH2_PARTITIONS.csv`, `STEREOCHEMISTRY_AUDIT.md`,
  `scripts/v2_full_accounting.py`, `scripts/v2_merge_universe.py`.

**What was completed**
The recovered shards were verified, merged and reconciled; the library was
accounted for exactly; and the stereochemistry defect was traced to its source.

**Decisions made and why**
- Irrecoverable loss is recorded as UNKNOWN rather than estimated. No surviving
  artefact records which partitions `pw-n2b` held, so the 2,723 jobs without a
  result are a joint total of "never dispatched" and "lost with pw-n2b", and
  splitting them would be invention.
- The de-duplication defect is documented but NOT fixed in place, because
  changing it would invalidate every committed identifier mid-sprint.

**Tests and verification actually executed**
- All 282 recovered shards re-hashed: 282/282 match their sentinel
  `output_sha256`; 0 non-zero GNINA return codes.
- 5,799 recovered results duplicate the 2026-09-04 analysis and were compared
  like-for-like: n_poses, top-pose affinity, best affinity, acceptable-pose
  count and clash flag agree to max absolute difference 0.0.
- 1,250 results are genuinely new, inside exactly 50 shards; 1,059 of those
  molecules had no prior result. ProLIF on 11,250 poses: 0 failures.
- Complete universe: 13,591 rows, 12,544 cand_ids, 12,543 distinct structures,
  0 duplicate keys, 0 numeric disagreements on merge.
- Accounting: 15,000 generated - 151 preparation failures - 24 InChIKey
  collapses = 14,825 ligands -> 16,314 jobs; 13,591 have a result, 2,723 do
  not; 10,919 cand_ids carry usable non-clashing evidence.
- Unique parents by identity: 15,000 by stereo InChIKey, 14,081 by connectivity
  (the library holds 919 extra stereoisomers of skeletons it already contains),
  14,975 by tautomer parent.
- Both join landmines measured, not assumed: batch-1 `denovo_rank` equals the
  true library rank in 52 of 3,000 rows; 487 `dock_priority_rank` values occur
  in both batches and all 487 name different molecules; `cand_id` never collides.
- Partition reconstruction: 515 partitions, 406 complete, 109 empty, 0 partial,
  so no truncated result entered the universe.
- Independent corroboration: Agent 3's `EX8_TRUE_MISSING_JOBS.csv` contains an
  identical 2,723-row (cand_id, pocket) set with the same 1,725/998 split.
- Stereo self-check: for all 14,825 docked designs the recomputed prepared
  InChIKey and SMILES match the shipped `V2_LIGAND_TABLE.csv` exactly.

**Results**
2,534 designs lost stereochemistry (3,042 centres, 36 double bonds), ALL of it
attributable to `TautomerEnumerator().Canonicalize()` measured per step -
`Cleanup`, `FragmentParent` and `protonate_ph74` destroyed none. The same call
also changed the CONSTITUTION of 1,199 designs (mostly enol to keto) and gave
2,241 designs a new unassigned stereocentre they never had.

**Failures or unresolved uncertainty**
- The 24 collapsed "duplicate InChIKeys" contain ZERO true duplicates: 6 genuine
  R/S epimeric pairs, 17 specified-vs-unspecified pairs, 1 tautomer merge.
- One structure was docked twice: de-duplication ran per batch, so DN00314 (R)
  and DL03110 (S) collapsed to the same prepared structure across batches and
  both were docked. DN00314 currently sits at consensus rank 240.
- 646 ranked finalists are affected - 207 WRONG_STEREOISOMER_DOCKED and 439
  AMBIGUOUS - including 7 of the current top 10, 27 of the top 50, 48 of the
  top 100, 15 of the 34 similarity seeds and 23 of the 56 ids named in
  FINAL_CANDIDATES.md.
- `SCORED_CANDIDATES.csv` holds 17,074 rows but 17,011 unique SMILES; both are
  reported. It is a pre-selection pool, so nothing downstream inherits it.

**Effect on the overall project**
The library is now accounted for exactly, and the stereochemistry defect has a
measured cause, scope and remediation list.

**Next intended step**
EX32 precision docking including the flagged stereoisomers, then the
real-compound lane and the final panel.
