# Project Status

Last updated: 2026-09-05 (completion sprint) · branch `yonsei-final10-v2`

## Project Objective

Identify a defensible, chemically diverse set of candidate PAR2 (F2RL1)
antagonists for experimental evaluation, working from the corrected V2 pocket
definitions. The current objective chain is:

de novo designs → GNINA dual-pocket screen → transparent post-docking ranking →
chemotype clustering → a small number of similarity-search seeds → retrieval of
real, existing analogue molecules → redocking of those analogues → eventual
nomination of compounds for Wan Namkung.

No compound has been nominated. No molecule in this repository is demonstrated
to bind or inhibit PAR2.

## Current Stage

Stage 7 of the V2 campaign: **11,485 of ~15,000 de novo designs (76%) now carry
real GNINA evidence, interaction fingerprints against the repaired reference,
consensus ranking, chemotype clusters, 34 seeds and 521 real analogues.**
A 35-gate fail-closed pre-flight passed on that machine, both reference pockets
re-recovered their crystal poses there, and a real 12-design dry run produced
finite, varying Vina and CNN scores that the collector reproduces exactly.
Batch 1: 3,442 jobs, 0 failures, 30,978 poses, 60.4 min wall (70.9 core-hours),
all 30,978 poses fingerprinted against the repaired reference. Batch 2: 11,837
designs, 12,872 jobs, 130 shards, running. No ranking, clustering or similarity
searching has been performed and no candidate has been nominated.
See YONSEI_FINAL10_V2/PIPELINE_STATUS.md for the live view.

## Current Branch

`yonsei-final10-v2`

## Current System Architecture

Six sequential stages, each resumable and each writing its own provenance:

1. `v2_prepare_ligands.py` — standardise, protonate at approximate pH 7.4,
   embed one low-energy 3D conformer, deduplicate by InChIKey, shard by pocket.
2. `v2_select_screen_set.py` — carve a screening subset out of the prepared
   library without re-embedding anything.
3. `v2_run_screen.sh` — sharded GNINA docking against the corrected 5NDD and
   5NDZ pockets, resumable via per-shard `.done` sentinels carrying input and
   output SHA-256, return code and wall time.
4. `v2_collect_scores.py` — parse every pose, aggregate per ligand per pocket,
   keeping best-pose and top-ranked-pose values separately.
5. `v2_interactions.py` — ProLIF fingerprints across multiple poses, compared
   with the crystallographic AZ8838 (5NDD) and AZ3451 (5NDZ) fingerprints.
6. `v2_postdock_rank.py` → `v2_cluster_and_seed.py` → `v2_similarity_search.py`
   — ranking, Butina chemotype clustering, seed selection, analogue retrieval.

`v2_rank_and_select.py` implements the diversity-constrained final short-list
selection and belongs to the later analogue-nomination gate, not to this one.

## Capabilities Implemented

- Deterministic ligand preparation with a documented pH 7.4 ionisation rule set
  applied by direct atom edits (carboxylic/sulfonic/phosphonic acids, tetrazole,
  amidine/guanidine, aliphatic amines), capped at |charge| 2.
- Mechanistic routing preserved: orthosteric → 5NDD, allosteric → 5NDZ,
  exploratory → both pockets.
- Sharded, resumable GNINA execution on CPU or GPU with per-shard checksums.
- Multi-pose score collection; pose 1 is never assumed to be the best pose.
- ProLIF recovery against the correct crystallographic antagonist per pocket.
- Post-docking ranking standardised within each pocket, never pooling 5NDD and
  5NDZ, with every ranking term written out per molecule so it can be audited.
- Novelty relative to the reference antagonist treated as a capped bonus and
  never as a penalty.
- Butina clustering at 0.55 / 0.65 / 0.75 on ECFP4 radius-2 2048-bit
  fingerprints, primary view 0.65, with convergent-chemotype detection.
- Seed selection that spreads across clusters, scaffolds, both mechanisms and
  three novelty bands rather than taking the top N molecules.
- Analogue retrieval from PubChem and ChEMBL with local ECFP4 re-scoring, plus
  Murcko relationship, MCS overlap and optional USRCAT 3D shape similarity.

## Work Completed to Date

- V1 audit (2,487 Pass-1 rows; contaminated benchmark ligands, displaced boxes
  and missing receptors identified).
- Corrected 5NDD and 5NDZ reference pockets, clean receptors and ligand-centred
  configs.
- Forced-CPU GNINA v1.3.3 reference benchmark passed: 5NDD best-pose RMSD
  0.6747 Å, 5NDZ best-pose RMSD 0.8672 Å (5NDZ top-ranked pose 2.2274 Å).
- 5,973-member sourceable candidate universe assembled (vendor data PENDING).
- 15,000 de novo designs generated; 3,000-design docking queue prepared.
- **New on 2026-09-04:** full V2 screen pipeline implemented and hardened; the
  394 wrong-tautomer designs reported by verification commit `e992aa7` were
  corrected and the de novo library re-prepared (2,988 designs, 3,442 jobs, 36
  shards); GCP access repaired; GNINA v1.3.3 deployed on `h3` with a SHA-256
  matching the benchmarked binary; a 35-gate fail-closed pre-flight, both
  reference redocks and a real 12-design dry run all passed on `h3`; the full
  EX8 screen was launched.

## Important Files and Artifacts

- `YONSEI_FINAL10_V2/04_V2_SCREEN/V2_LIGAND_TABLE.csv` — 7,324 prepared ligands.
- `YONSEI_FINAL10_V2/04_V2_SCREEN/V2_PREP_MANIFEST.json` — preparation
  provenance and shard checksums.
- `YONSEI_FINAL10_V2/04_V2_SCREEN/denovo_screen_set/` — the 15 shards, 3,436
  jobs, actually queued for GNINA.
- `YONSEI_FINAL10_V2/04_V2_SCREEN/RUNBOOK.md` — exact commands for `h3`.
- `YONSEI_FINAL10_V2/HANDOFF_TO_CLAUDE.md` — full campaign narrative.

## Data Sources and Provenance

De novo designs from `02_DENOVO_CPU/DENOVO_TOP3000_FOR_DOCKING.csv` (BRICS
enumeration, seed 20260812). Sourceable universe from
`03_SOURCEABILITY/V2_CANDIDATE_UNIVERSE.csv` (FDA drugs, LOTUS, NPAtlas,
COCONUT, MITF scaffolds, V1 hits). Reference pockets from PDB 5NDD and 5NDZ.
Preparation seed 20260904, RDKit 2026.03.6.

## Decisions and Rationale

- **Screen scope restricted to the de novo designs.** Directed by the user on
  2026-09-04. The sourceable universe stays prepared but unscreened; the aim is
  to find the best de novo chemotypes and use them as similarity queries rather
  than to run a mass virtual screen.
- **Single-stage screening at benchmark settings** (exhaustiveness 32, 9 poses)
  rather than a fast pre-pass. With 88 cores on `h3` the whole de novo screen is
  roughly 1.5–2 hours, so the cheaper pre-pass buys nothing and would make
  scores non-comparable to the validated benchmark.
- **All 9 poses retained.** The benchmark showed the 5NDZ top-ranked pose sits
  at 2.23 Å while its best pose is 0.87 Å; ranking on pose 1 alone would
  systematically misjudge that pocket.
- **Per-pocket standardisation.** 5NDD and 5NDZ are different binding sites and
  their scores are never pooled into one z-score.
- **Novelty as a one-sided bonus.** A design is not penalised for modest
  Tanimoto to AZ8838 or AZ3451.
- **Full prepared shard library excluded from git** (51 MB, deterministically
  reproducible); the de novo screen set is committed because the VM needs it.

## Verification and Test Results

- `python -c "import ast; ast.parse(...)"` on all seven new scripts: passed.
- `bash -n v2_run_screen.sh`: passed.
- Protonation rule set checked against 20 hand-picked structures (carboxylic
  acid, sulfonic acid, tetrazole, guanidine, primary/secondary/tertiary amine,
  aniline, amide, pyridine, glutamate, EDTA, methanol): all gave the expected
  ionisation state. An earlier reaction-SMARTS implementation was found to
  discard the unmatched part of the molecule and was replaced with direct atom
  edits.
- `v2_prepare_ligands.py` smoke test on 80 rows: 150 SDF records, 0 unparsable,
  1 conformer each.
- Full preparation run on 8,973 rows: 8,469 prepared, 504 failed (188 too few
  heavy atoms, 293 too many, 16 embed failures, 7 unsupported elements), 1,145
  duplicate InChIKeys collapsed, 7,324 unique ligands.
- `v2_select_screen_set.py`: 2,985 de novo ligands → 3,436 jobs → 15 shards.
- `v2_run_screen.sh --dry-run`: emitted GNINA command lines carrying the exact
  validated box centres and sizes for both pockets.
- End-to-end rehearsal on **synthetic** scores at production scale (3,436 rows):
  `v2_collect_scores.py`, `v2_interactions.py` (ProLIF 2.2.1, 0 failures),
  `v2_postdock_rank.py` (2,985 designs ranked, 451 scored in both pockets) and
  `v2_cluster_and_seed.py` (400 designs clustered; 259/326/381 clusters at
  0.55/0.65/0.75; 30 seeds across 30 clusters and 30 scaffolds) all completed.
  These rehearsal outputs are synthetic plumbing checks and were deliberately
  not committed as results.

**No GNINA docking of any de novo design has been executed.** Every score in the
rehearsal is randomly generated and carries no scientific meaning.

## Known Failures and Limitations

- 15 of 3,000 de novo designs did not survive preparation (5 embed failures,
  10 duplicate InChIKeys).
- The pH 7.4 model is a documented SMARTS heuristic, not a pKa prediction, and
  one tautomer and one conformer are carried per ligand.
- `v2_similarity_search.py` has not been executed against live endpoints; the
  PubChem and ChEMBL calls are unverified in practice.
- The reference benchmark passed on `moheetc4` (CPU). It has not been re-run on
  `h3` and must be before any screen result is trusted.
- Vendor, catalogue ID, price and stock are `PENDING` everywhere.

## Risks and Technical Debt

- Interaction-fingerprint recovery is geometric similarity to a crystal pose,
  not evidence of binding, and is weighted at 0.26 in the ranking; a systematic
  ProLIF parameter difference would shift the ranking.
- CNNscore and CNNaffinity are ranking features only and are not calibrated
  probabilities of antagonism.
- Butina cluster counts at 0.65 on a 400-molecule set are dominated by
  singletons, which limits how much "convergent chemotype" evidence exists.
- The rehearsal validated plumbing, not scientific behaviour; term
  distributions on real docking output may need reweighting.

## Current Blockers

None. All PAR2 compute is stopped. Four disposable workers were exported,
verified and deleted on 2026-09-05; `a100`, `a100-40` and `h3` remain, all
TERMINATED. 50 recovered pose shards (~1,250 ligand-pocket results) are held
outside the repository and are NOT part of the committed rankings. Remote access was resolved: `abdulmoheetahmed@gmail.com` was granted
`roles/compute.instanceAdmin.v1` and `roles/iam.serviceAccountUser`, and a named
gcloud configuration `par2` now pins that account, the project and zone
`europe-west4-b` so the failure cannot recur silently. `cloud@hamiltonianlabs.co`
holds `roles/owner` in IAM but its CLI token is still refused from this machine,
which points at a Workspace context-aware-access rule, not a missing role.

## Exact Next Actions

1. Finish the batch-2 EX8 screen and fingerprint its poses.
2. Merge batch 1 and batch 2 into one full-library EX8 universe.
3. Add PIGNet2 rescoring from the A100, then consensus-rank within pocket.
4. EX32 refinement of roughly the top 500-1,000, re-fingerprint.
5. Butina clustering at 0.65 (with 0.55/0.75 sensitivity views), per pocket.
6. Select 20-40 chemically distinct seeds, 5NDD-weighted.
7. Similarity search against purchasable chemistry, then redock the analogues.
8. Do not nominate a final ten before real-compound availability is checked.
