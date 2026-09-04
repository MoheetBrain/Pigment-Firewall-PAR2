# V2 de novo dual-pocket screen — runbook for `h3`

Scope, after the 4 Sep 2026 course correction: screen the **de novo designs
only**. The 5,973-member sourceable universe was prepared and is retained in the
library, but it is not part of this screen. The 15,000-design source library is
untouched.

Objective chain: screen de novo designs → rank → cluster into chemotypes →
choose a small number of similarity-search seeds → retrieve real existing
analogues → redock those. No final ten is nominated at this stage.

## What is already prepared locally

| Item | Value |
|---|---|
| De novo designs prepared | 2,985 of 3,000 (5 embed failures, 10 duplicate InChIKeys) |
| Family split | orthosteric 1,863 · allosteric 671 · exploratory 451 |
| Docking jobs | 3,436 (5NDD 2,314 · 5NDZ 1,122) |
| Shards | 15 SDF shards of 250 ligands |
| Routing | orthosteric → 5NDD · allosteric → 5NDZ · exploratory → both |

Screen set: `YONSEI_FINAL10_V2/04_V2_SCREEN/denovo_screen_set/shards`
Ligand table: `YONSEI_FINAL10_V2/04_V2_SCREEN/V2_LIGAND_TABLE.csv`

## 0. Machine

`h3`, 88 physical cores. GNINA's Monte Carlo search is CPU-bound, so throughput
is set by core count. Plan: 22 concurrent GNINA processes × 4 CPU = 88 cores.

At benchmark settings (exhaustiveness 32, 9 poses) the whole de novo screen is
roughly 500,000 core-seconds, so about 1.5–2 hours wall clock on 88 cores. There
is no need for a reduced-exhaustiveness pre-pass: run the validated settings
directly, which also keeps every score comparable to the reference benchmark and
preserves all 9 poses as required for 5NDZ.

## 1. Copy the repository and install GNINA at the pinned version

```bash
gcloud compute scp --zone europe-west4-b --project project-08679972-d14a-4025-94f \
  --recurse ~/Documents/ChatGPT/PAR2 h3:~/PAR2
```

```bash
sudo apt-get update && sudo apt-get install -y python3-venv python3-pip
mkdir -p ~/bin && cd ~/bin
curl -L -o gnina https://github.com/gnina/gnina/releases/download/v1.3.3/gnina
chmod +x gnina
sha256sum gnina   # must be 3340c1f49cd3c7c84d8699182a1c6af13c7fa2a22448d1204640446106f72172
./gnina --version # expect 1.3.3  master:6fe1ce2
```

```bash
cd ~/PAR2 && python3 -m venv .venv && ./.venv/bin/pip install rdkit pandas numpy prolif
```

## 2. Re-run the reference gate on this machine

Do not screen before the corrected redock passes on `h3` itself.

```bash
cd ~/PAR2
GNINA_BIN=~/bin/gnina bash YONSEI_FINAL10_V2/scripts/run_gnina_reference.sh
./.venv/bin/python YONSEI_FINAL10_V2/scripts/validate_reference_redock.py
```

Expected: 5NDD best-pose RMSD ≈ 0.675 Å, 5NDZ best-pose RMSD ≈ 0.867 Å. The
5NDZ top-ranked pose is known to sit near 2.23 Å — that is why every pose is
kept downstream rather than pose 1 alone. Stop if either pocket fails.

## 3. Screen the de novo designs

```bash
cd ~/PAR2
bash YONSEI_FINAL10_V2/scripts/v2_run_screen.sh \
  --shards YONSEI_FINAL10_V2/04_V2_SCREEN/denovo_screen_set/shards \
  --out    YONSEI_FINAL10_V2/04_V2_SCREEN/denovo_screen \
  --gnina  ~/bin/gnina \
  --stage  refine \
  --jobs 22 --cpu-per-job 4 --device cpu
```

`--stage refine` is exhaustiveness 32, 9 poses, `cnn_scoring rescore` — the
validated benchmark parameters. Use `--device gpu` instead if a GPU is attached
and the reference gate passed on GPU. Rerunning the identical command resumes:
completed shards are skipped via their `.done` sentinels, each of which records
the exact input and output SHA-256, return code, and wall time.

## 4. Collect scores

```bash
./.venv/bin/python YONSEI_FINAL10_V2/scripts/v2_collect_scores.py \
  --screen YONSEI_FINAL10_V2/04_V2_SCREEN/denovo_screen \
  --ligand-table YONSEI_FINAL10_V2/04_V2_SCREEN/V2_LIGAND_TABLE.csv
```

Writes every pose to `V2_POSE_SCORES.csv` and the per-ligand-per-pocket
aggregate — including best-pose and top-ranked-pose values separately — to
`V2_LIGAND_POCKET_SCORES.csv`.

## 5. Interaction fingerprints across multiple poses

```bash
./.venv/bin/python YONSEI_FINAL10_V2/scripts/v2_interactions.py \
  --screen YONSEI_FINAL10_V2/04_V2_SCREEN/denovo_screen \
  --pose all --max-pose 5 --workers 22
```

5NDD designs are compared with the crystallographic AZ8838 fingerprint, 5NDZ
designs with AZ3451, using the reference keys already stored in
`02_REFERENCE_VALIDATION`. Recovery is geometric similarity, not activity.

## 6. Post-docking ranking

```bash
./.venv/bin/python YONSEI_FINAL10_V2/scripts/v2_postdock_rank.py \
  --ligand-table YONSEI_FINAL10_V2/04_V2_SCREEN/V2_LIGAND_TABLE.csv \
  --scores       YONSEI_FINAL10_V2/04_V2_SCREEN/denovo_screen/V2_LIGAND_POCKET_SCORES.csv \
  --interactions YONSEI_FINAL10_V2/04_V2_SCREEN/denovo_screen/V2_POSE_INTERACTIONS_SUMMARY.csv \
  --out          YONSEI_FINAL10_V2/05_POSTDOCK
```

Produces `DENOVO_POSTDOCK_ALL.csv`, `_TOP500.csv`, `_TOP300.csv` and a
per-pocket table. Scores are standardised **within** a pocket, never pooled
across 5NDD and 5NDZ. Novelty relative to the reference antagonist is a capped
bonus and never a penalty.

## 7. Cluster chemotypes and pick similarity-search seeds

```bash
./.venv/bin/python YONSEI_FINAL10_V2/scripts/v2_cluster_and_seed.py \
  --postdock YONSEI_FINAL10_V2/05_POSTDOCK/DENOVO_POSTDOCK_ALL.csv \
  --out      YONSEI_FINAL10_V2/06_CLUSTERS \
  --top-n 400 --n-seeds 30
```

Butina on ECFP4 (radius 2, 2048 bits) at 0.55 / 0.65 / 0.75, primary view 0.65.
Produces `DENOVO_CLUSTER_MEMBERS.csv`, `DENOVO_CLUSTER_SUMMARY.csv` and
`SIMILARITY_SEARCH_SEEDS.csv`. Seeds take at most one molecule per cluster and
per Murcko scaffold, guarantee each pocket a floor of 25% of the seeds, and fill
the rest strictly by rank.

## 8. Retrieve real analogues

```bash
./.venv/bin/python YONSEI_FINAL10_V2/scripts/v2_similarity_search.py \
  --seeds YONSEI_FINAL10_V2/06_CLUSTERS/SIMILARITY_SEARCH_SEEDS.csv \
  --out   YONSEI_FINAL10_V2/07_ANALOGUES \
  --max-per-seed-per-source 60 --shape-similarity
```

Queries PubChem and ChEMBL similarity endpoints, then re-scores every hit
locally with RDKit ECFP4 Tanimoto so the reported number is reproducible.
Bands: ≥0.80 very close, 0.70–0.80 close, 0.55–0.70 broader neighbour. Also
records Murcko relationship, MCS overlap and USRCAT 3D shape so a strong
low-Tanimoto analogue is not thrown away. Writes `SIMILARITY_HITS_RAW.csv`,
`SIMILARITY_HITS_DEDUP.csv`, and `SEED_QUERY_SET.csv` for catalogues with no
programmatic interface.

## 9. Next gate, not yet run

Analogues → corrected GNINA docking into the originating seed's pocket → IFP
comparison → chemistry and sourceability → final candidate ranking. No final ten
is nominated before that gate.

Vendor, catalogue ID, price and stock remain `PENDING` throughout. Nothing in
this runbook establishes that any molecule binds or inhibits PAR2.
