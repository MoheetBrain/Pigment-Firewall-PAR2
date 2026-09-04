# Pre-flight and dry-run validation — real de novo GNINA screen on `h3`

Date: 2026-09-04 · Machine: `h3` · Verdict: **GO**

Fail-closed validation performed before any production docking. Every gate below
was executed on `h3` itself, not inferred from the August benchmark. Nothing
here establishes that any molecule binds or inhibits PAR2.

## Machine and environment

| | |
|---|---|
| Host | `h3`, x86_64, Linux 6.12.105+deb13-cloud-amd64, Debian 13 |
| CPU | Intel Xeon Platinum 8481C @ 2.70 GHz, 88 cores (2 sockets x 44, 1 thread/core) |
| Memory | 346 GiB, no swap configured |
| Disk | 59 GB (expanded from 10 GB) |
| GPU | none present |
| Python | 3.13, RDKit 2026.03.6, ProLIF 2.2.1 (identical versions to the local build) |

## Phase 1 — GNINA binary provenance

| | |
|---|---|
| Binary | `~/bin/gnina`, from the official `v1.3.3` release asset `gnina.cuda12.8.static` |
| Version string | `gnina v1.3.3  master:6fe1ce2   Built Jun 30 2026.` |
| SHA-256 | `3340c1f49cd3c7c84d8699182a1c6af13c7fa2a22448d1204640446106f72172` |
| Match to benchmarked binary | **exact** |

The binary dynamically links CUDA/cuDNN even for CPU execution, so the same
pinned NVIDIA runtime wheels recorded in `01_BENCHMARK_REPAIR/environment_report.md`
were installed under `~/gnina-cuda-libs` and exposed via `LD_LIBRARY_PATH`.

## Phase 2 — CPU-only, fail closed

Runner environment: `CUDA_VISIBLE_DEVICES=-1`, `OMP_NUM_THREADS=1`,
`MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `NUMEXPR_NUM_THREADS=1`,
`VECLIB_MAXIMUM_THREADS=1`.

Every invocation carries `--no_gpu --cnn_scoring rescore --cpu 4 --num_modes 9`
and, for the screen, `--exhaustiveness 8`. The runner contains no fallback path:
it cannot drop `--cnn_scoring`, retry with `cnn_scoring=none`, switch to
Vina-only, change binary, receptor, config or box. A failing shard is reported
and left incomplete.

## Phase 3 — receptors, configs and parsed box values

| File | SHA-256 |
|---|---|
| `BoxA_orthosteric_5NDD_ligand_centered.conf` | `c7e47db6025bc7317e506a37cca78761ed2b42a02127c31de03bd25729c9153a` |
| `5NDD_inactive_orthosteric_receptor_clean.pdbqt` | `c2411d4df5ba64956326d5c92152ca35c04b019a79100b311649cc79cd709c4e` |
| `5NDD_inactive_orthosteric_receptor_clean.pdb` | `68890d8b74b33f76816876b1a49750497f18a689af52439542f120be5195f5b2` |
| `5NDD_AZ8838_crystallographic_clean.sdf` | `92b4211c0fd5834c8d4db97bba0f909f5b645bae90938d1d3c9a2583037645bf` |
| `BoxB_allosteric_5NDZ_ligand_centered.conf` | `679ba2d70d91730b7beb8a6813cd0cdc4fc03d8a535510e2d3468cc24b091e2b` |
| `5NDZ_inactive_allosteric_receptor_clean.pdbqt` | `af9f9eec77bcbbc4d21a19702af68c8143f503f8e889427bb3cd550903220b92` |
| `5NDZ_inactive_allosteric_receptor_clean.pdb` | `64159534d826c572215877770705479917722a9e4d96691843c32c84e363d155` |
| `5NDZ_AZ3451_crystallographic_clean.sdf` | `b2f01773aa0ae7e2c074d9bdd2f1c85964dd7e57bf52ebee71ffdb94ddc95bb6` |

Values the runner actually sends to GNINA, read back from the runtime command
line, not from the config text:

```
5NDD  --center_x 16.974 --center_y 5.926  --center_z 55.826
      --size_x   17.332 --size_y   17.672 --size_z   13.644
5NDZ  --center_x 1.356  --center_y 12.419 --center_z 48.400
      --size_x   20.702 --size_y   17.885 --size_z   25.525
```

Maximum |delta| against the required corrected definitions: **0.000000 Å** over
all six fields in both pockets. The historical broad Box A / Box B definitions
are not referenced anywhere in the runner.

## Phase 4 — geometric frame and empty-space test

| Check | 5NDD / AZ8838 | 5NDZ / AZ3451 |
|---|---|---|
| Crystal ligand centroid | (16.974, 5.926, 55.826) | (1.356, 12.419, 48.400) |
| Centroid → box-centre offset | **0.0007 Å** | **0.0004 Å** |
| Ligand heavy atoms inside box | 17 / 17 | 38 / 38 |
| Min margin to any box face | 4.383 Å | 2.699 Å |
| Per-axis min margin (x, y, z) | 4.581 / 4.383 / 4.717 Å | 4.157 / 4.581 / 2.699 Å |
| Receptor heavy atoms loaded | 4,498 | 4,421 |
| Receptor heavy atoms within 5 Å of ligand | 88 | 61 |
| Atom pairs in 2–5 Å | 271 | 252 |
| Closest contact | 2.475 Å | 2.973 Å |
| Receptor heavy atoms inside box | 199 (box 4,179 Å³) | 259 (box 9,451 Å³) |
| Expected pocket residues found | **8 / 8** | 10 / 11 (`GLY:157` beyond 5 Å) |
| HETATM records in docking receptor | none | none |

Both receptors are free of their own crystallographic ligand — the receptor PDBs
contain no HETATM records at all, so neither 8TZ nor 8UN can contaminate a
docking run. Neither box is empty space.

## Phase 5 — reference redocking on `h3`

EX32, 9 modes, CPU-only, corrected receptors and boxes, clean crystal ligands.
Both runs completed in 74 s wall.

| System | Best pose | Best RMSD | Gate < 2.0 Å | Top-ranked RMSD | Best IFP recovery |
|---|---:|---:|---|---:|---:|
| 5NDD / AZ8838 | #1 | **0.6747 Å** | PASS | 0.6747 Å | 0.600 |
| 5NDZ / AZ3451 | #2 | **0.8672 Å** | PASS | 2.2274 Å | 0.889 |

These reproduce the August benchmark values (0.674658 Å and 0.867183 Å) to four
decimal places on a different machine. The 5NDZ result is the clearest possible
justification for retaining all nine modes: pose 1 is 2.23 Å while pose 2 is
0.87 Å, so ranking on pose 1 alone would have judged this pocket wrongly.

5NDD best IFP recovery here is 0.600 against 0.700 reported in the handoff. The
reference fingerprints are known to be defective (see Limitations), so IFP
numbers are treated as provisional and are not part of the go decision.

## Phase 6 — raw score validation

Property tags actually present in GNINA v1.3.3 output SDFs:
`CNN_VS`, `CNNaffinity`, `CNNaffinity_variance`, `CNNscore`, `minimizedAffinity`.

Reference redock raw values, read directly from the SDF, not via the collector:

| system | pose | vina_affinity | CNNscore | CNNaffinity |
|---|---:|---:|---:|---:|
| 5NDD | 1 | -8.0917 | 0.8579 | 7.6101 |
| 5NDD | 5 | -7.4616 | 0.4632 | 6.9942 |
| 5NDD | 9 | -6.0546 | 0.3451 | 6.3932 |
| 5NDZ | 1 | -8.0766 | 0.7755 | 8.0564 |
| 5NDZ | 5 | -6.4983 | 0.5277 | 7.0510 |
| 5NDZ | 9 | -6.8653 | 0.4918 | 7.0656 |

All three fields present in 9/9 poses for both systems, all finite, none
all-zero, none constant. The absent tag `minimizedRMSD` is parsed as `None`,
never as 0 — verified explicitly.

## Phase 7 — ligand-preparation integrity

Accounting from 3,000 inputs, with nothing disappearing silently:

```
3,000 inputs = 2,995 prepared + 5 failed
2,995 prepared - 7 duplicate InChIKeys = 2,988 unique ligands
```

All five failures are 3D embedding failures on strained fused-ring systems, and
each is listed by id, reason and SMILES:

| cand_id | reason |
|---|---|
| DN00362 | EMBED_FAILED |
| DN01479 | EMBED_FAILED |
| DN02319 | EMBED_FAILED |
| DN02898 | EMBED_FAILED |
| DN02899 | EMBED_FAILED |

25 sampled designs were compared before and after preparation on heavy-atom
count, ring count, fragment count and heavy-atom skeleton: **0 problems**. No
molecule lost a ring, was severed, duplicated or reduced to a reaction fragment.
Every prepared record has exactly one conformer with finite coordinates,
non-collapsed geometry and bond lengths in 0.7–2.6 Å: **0 geometry problems**
across all 36 shards.

## Phase 8 — family routing audit

Recomputed independently of the manifest:

```
orthosteric 1,863 + allosteric 671 + 2 x exploratory 454 = 3,442 jobs
shards contain 3,442 jobs over 2,988 ligands
```

2,988 ligands audited; **0 misrouted**; 0 shard ligands missing from the
screen-set table. Orthosteric designs reach only 5NDD, allosteric only 5NDZ, and
exploratory designs reach both.

## Phase 9 — real 12-design dry run

12 designs spanning 5 orthosteric, 4 allosteric and 3 exploratory, 12 distinct
Murcko scaffolds, generation ranks 1–3000, MW 234–434, cLogP 0.82–4.50.
15 jobs, 135 poses, 4 concurrent workers, 87 s wall.

| Field | present | finite | min | median | max | unique | all-zero | constant |
|---|---|---|---:|---:|---:|---:|---|---|
| vina_affinity | 135/135 | 135 | -8.6597 | -5.3267 | 36.1721 | 135 | no | no |
| CNNscore | 135/135 | 135 | 0.1988 | 0.4117 | 0.9048 | 135 | no | no |
| CNNaffinity | 135/135 | 135 | 4.2510 | 5.8516 | 7.9146 | 135 | no | no |
| CNN_VS | 135/135 | 135 | 1.0380 | 2.6407 | 6.1115 | 135 | no | no |

Pose locations: **135/135 pose centroids lie inside the configured box**, maximum
centroid-to-centre distance 8.705 Å. Four poses place 1–2 heavy atoms marginally
outside a box face, which is expected — GNINA constrains the search volume, not
every atom.

The single positive `vina_affinity` maximum (+36.17) is a genuine clashing
high-index pose in GNINA's own output, not a parser artefact.

Parser cross-check on the dry run: 135 raw poses, 135 CSV rows, maximum
|raw − parsed| = **0** for all four score fields.

## Defects found and fixed during pre-flight

1. **Wrong AZ8838 tautomer in the reference model** (found by an independent
   verification pass, commit `e992aa7`). The stored 8TZ is a non-aromatic
   4H-imidazole, InChIKey `BBGRVUDFEGKPGW-LBPRGKRZSA-N`, versus the wwPDB
   `IDFPQEHZYBXIFO-LBPRGKRZSA-N`. It propagated into 394 of the 3,000
   docking-priority designs. All 394 were rebuilt from the corrected SMILES —
   molecular formula preserved in 394/394 and imidazole aromaticity restored in
   every case — and the whole de novo library was re-prepared from the corrected
   queue. The hard-coded reference SMILES in the post-docking ranker was also
   corrected and now reproduces the wwPDB InChIKey exactly.
2. **AppleDouble contamination.** macOS `tar` wrote `._*` resource-fork files
   that a `*.sdf` glob accepted as ligand shards, producing 15 unparsable
   records. Every shard hash still matched (15/15 in both directories), so the
   data was intact, but the runner would have launched 15 junk jobs. All globs
   now skip dotfiles and the runner uses `find ... ! -name '.*'`.
3. **Temporary-filename bug in the runner.** Writing to `<name>.sdf.gz.partial`
   made GNINA emit nothing, because it selects output format by extension. The
   run exited 0 with no output; the atomic-completion check caught it and
   refused to mark the shard done. Fixed to `<name>.partial.sdf.gz`.

## Limitations carried forward

- The reference ProLIF fingerprints contain no hydrogen bonds: neither ligand
  nor receptor is protonated before fingerprinting, so ProLIF's donor/acceptor
  detectors cannot fire (verification commit `e992aa7`, defect 2). IFP recovery
  is therefore measured against an incomplete reference and must be repaired —
  protonating both ligand and receptor — before it is weighted in ranking.
- 394 designs were structurally corrected, but the *membership* of the 3,000
  docking queue was chosen using the defective reference; roughly 19% of the
  orthosteric slots would differ had the queue been selected with the corrected
  reference. Regenerating the queue was out of scope for this run.
- CNNscore and CNNaffinity are ranking features. They are not calibrated
  probabilities of PAR2 antagonism.

## Go / no-go

All 35 automated gates pass, plus the manual raw-score, reference-redock and
dry-run inspections above. **GO.**
