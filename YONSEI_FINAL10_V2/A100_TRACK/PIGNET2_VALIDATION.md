# PIGNet2 Control Validation - Track B, Phase 0 + B1

**Status: PIGNet2 installed and validated on the A100. All verification checks PASS.**
Generated 2026-09-04T14:00:39Z on `a100-40`.

Scope: bring-up + install + control validation ONLY. The 30,978 production poses have
**not** been scored - that is a later phase gated on this validation.

---

## 1. Machine provenance (Phase 0)

| Field | Value |
|---|---|
| GCP instance | `a100-40`, zone `us-central1-b`, project `project-08679972-d14a-4025-94f` |
| Machine type | `a2-highgpu-1g` |
| State at start | **Already RUNNING** - no `instances start` was needed |
| Hostname | `a100-40` |
| OS / kernel | Ubuntu 22.04.5 LTS / `6.8.0-1066-gcp` |
| vCPU / RAM | 12 / 83Gi |
| Root disk | 97G total, 41G avail |
| GPU | NVIDIA A100-SXM4-40GB, 40960 MiB, 580.173.02 |
| Compute capability | (8, 0) (sm_80) |
| nvcc | **not present** system-wide (CUDA 11.1 runtime supplied via conda) |
| System python | Python 3.10.12 (unused; env uses 3.9) |

**Disk resize: NOT performed.** Root was 97 GB with 55 GB free at Phase 0, above the ~50 GB
threshold in the task, so `disks resize` / `growpart` / `resize2fs` were deliberately skipped.

Full manifest: `raw/machine_manifest.txt`. Machine + software JSON: `A100_PROVENANCE.json`.

---

## 2. PIGNet2 install

| Field | Value |
|---|---|
| Repo | https://github.com/ACE-KAIST/PIGNet2.git (the official ACE-KAIST implementation) |
| **Commit SHA** | `f621aaaa9fe781e67763c8adbffff6faca6db95b` |
| Commit date | 2024-03-06 10:56:21 +0900 |
| Env | conda (Miniforge), env `pignet2`, Python 3.9.18 |
| torch | 1.9.1+cu111 (CUDA 11.1), `torch.cuda.is_available()` = True |
| rdkit | 2022.03.4 (README-pinned) |

Repo files were **not modified**. Full package list: `raw/pip_freeze.txt`, `raw/conda_list.txt`.

### Pretrained checkpoints (SHA-256)

The README states the `pda` models (positive + negative data augmentation) are the best models,
and recommends a 4-model ensemble. All four were used.

| Checkpoint | SHA-256 |
|---|---|
| `src/ckpt/pda_0.pt` | `5c2fc12393e415b9e7174bf7b26998a85b833383df852f431763ae9ed321691f` |
| `src/ckpt/pda_1.pt` | `9d01bcfa64c26fbfc4fad4b55b9a2f228e256c1ab5a0d0b54c1cc43229d7351d` |
| `src/ckpt/pda_2.pt` | `363f75e6f878a8c1e74b734a2e52724d0ccc408f8b2c94ae56398be20cbf746e` |
| `src/ckpt/pda_3.pt` | `f3b6a0ddec7a493fa5a9c2bd3a77482e36547212c78e4fba3b8f438a1403cdbd` |

The checkpoints carry their own config: model class **`models.pignet_morse.PIGNetMorse`**
(not the base `PIGNet`), `include_ionic: False`, `rotor_penalty: True`.

### Deviations from the README (all documented, none silent)

1. **`dimorphite_dl`** - installed as `conda-forge dimorphite-dl=1.3.2` instead of via pip.
   Every PyPI release (1.2.5, 2.0.x) declares `requires-python >=3.10` *and* genuinely uses
   PEP-604 `str | None` syntax, which raises `TypeError` on the README's Python 3.9. Installing
   1.2.5 with `--ignore-requires-python` failed at import. The conda-forge 1.3.2 build works on
   3.9 and exposes the exact `DimorphiteDL(...).protonate()` API that `protonate.py` calls.
   Functionally verified: benzoic acid -> `O=C([O-])c1ccccc1`, ethylamine -> `CC[NH3+]` at pH 7.4.
2. **`reduce` 4.15** (bioconda) - `dataset/preprocess/protonate.py` shells out to a `reduce`
   binary that `requirements.txt` never installs.
3. **`cudatoolkit=11.1`** (conda-forge) - `torch-sparse`/`scatter`/`cluster` dynamically link
   `libcusparse.so.11`; torch 1.9.1+cu111 bundles its own copies but the PyG extensions do not.
   Runtime needs `LD_LIBRARY_PATH=$CONDA_PREFIX/lib`.
4. **`libgl1`, `libglib2.0-0`, `libxrender1`, `libxext6`** (apt) - pymol needs `libGL.so.1`,
   absent on the headless image.
5. **rdkit restored** - an early pip attempt at dimorphite-dl pulled in rdkit 2025.9.2 over the
   pinned conda build; reverted to 2022.03.4 and re-verified.

### Install validated against the repo's own shipped reference

The repo ships `examples/case1.txt`. Re-running its documented command reproduced it:

```
command : python src/exe/predict.py ./src/ckpt/pda_0.pt -p examples/protein.pdb \
                 -l examples/ligand_single_conformation.sdf -o /tmp/case1_repro.txt
shipped : protein_ligand_single_conformation_0  0.000  -3.990  -2.074  -1.021  0.000  -0.894  0.000
obtained: protein_ligand_single_conformation_0  0.000  -3.989  -2.073  -1.021  0.000  -0.894  0.000
```

Agreement to 0.001 on the vdW term (and hence the total); H-bond, metal, hydrophobic and ionic
terms are bit-identical. The 0.001 is last-digit GPU/library nondeterminism, not a porting error.

---

## 3. Output format and energy components

`src/exe/utils.py:write_predictions` writes, per row:

```
key <TAB> true_label <TAB> sum(pred) <TAB> pred[0] ... pred[4]
```

`true_label` is `0.000` for prediction (no experimental value supplied). From
`src/models/pignet_morse.py:97-155` the five components are, in order:

| # | Component | Source |
|---|---|---|
| 0 | van der Waals | `physics.morse_potential` |
| 1 | hydrogen bond | `linear_potential`, minimum `-(hbond_coeff**2)` |
| 2 | metal-ligand | `linear_potential`, minimum `-(metal_ligand_coeff**2)` |
| 3 | hydrophobic | `linear_potential`, minimum `-(hydrophobic_coeff**2)` |
| 4 | ionic | **structurally zero** - `include_ionic: False` in the checkpoints; the code comments `ionic_coeff` as "NOT USED" |

All five are divided by the rotor penalty `1 + rotor_coeff**2 * n_rotors`. The total is their sum.
Metal is 0.000 throughout (no metal in either pocket) and ionic is 0.000 by construction - both
expected, not a failure.

---

## 4. SCORE DIRECTION: **lower (more negative) = stronger predicted binding**

Determined from the repo's code, not assumed. Four independent lines of evidence:

1. **Training label convention** - `src/data/data.py:345-346`:
   ```python
   # pK_d -> kcal/mol
   label = self.id_to_y[key] * -1.36
   ```
   The regression target is pKd x (-1.36). `loss_regression` is
   `F.mse_loss(energies.sum(-1,True), true)`, so the model's total regresses directly onto that
   scale: a **higher** pKd (stronger binder) maps to a **more negative** target.
2. **Docking power** - `src/benchmark/docking_power.py:67-71`:
   ```python
   pred, sorted_keys = zip(*sorted(zip(pred, selected_keys)))
   ...
   if min(rmsd[:topn]) < 2.0:
   ```
   Python's `sorted` is ascending, and success is "a near-native pose (RMSD < 2 A) is among the
   **lowest**-scoring N". Lowest = best pose.
3. **Screening power** - `src/benchmark/screening_power.py:38,79`: `retval[key] = min(retval[key])`
   takes the **minimum** prediction as a ligand's representative score, then sorts ascending to
   rank actives first.
4. **Physics** - every interaction minimum is negative (`-(coeff**2)`), so more favourable
   contacts drive the total more negative.

Conversion back to affinity: **pKd ~= total / (-1.36)** (column `predicted_pKd_from_ensemble_mean`).

---

## 5. Control results (4-model pda ensemble)

Units are the model's kcal/mol-like output scale. Lower = stronger.

### 5NDD / AZ8838 (orthosteric) - crystallographic
| pose | ens.mean | ens.SD | pda_0 | pda_1 | pda_2 | pda_3 | vdW | H-bond | metal | hydroph | ionic | pred pKd |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | **-4.7637** | 1.3064 | -3.107 | -6.127 | -5.397 | -4.424 | -2.959 | -0.58 | 0.0 | -1.2248 | 0.0 | 3.5028 |

### 5NDD / AZ8838 (orthosteric) - 9 GNINA redock poses
| pose | ens.mean | ens.SD | pda_0 | pda_1 | pda_2 | pda_3 | vdW | H-bond | metal | hydroph | ionic | pred pKd |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | **-5.9623** | 1.6833 | -4.067 | -6.725 | -7.886 | -5.171 | -4.275 | -0.4163 | 0.0 | -1.271 | 0.0 | 4.384 |
| 1 | **-4.905** | 1.1945 | -3.401 | -5.211 | -6.281 | -4.727 | -3.508 | -0.288 | 0.0 | -1.1085 | 0.0 | 3.6066 |
| 2 | **-3.5355** | 0.5794 | -3.202 | -4.312 | -3.626 | -3.002 | -1.858 | -0.2578 | 0.0 | -1.4198 | 0.0 | 2.5996 |
| 3 | **-4.287** | 0.9624 | -3.47 | -5.624 | -4.334 | -3.72 | -2.201 | -0.7292 | 0.0 | -1.3565 | 0.0 | 3.1522 |
| 4 | **-4.9355** | 0.9237 | -3.586 | -5.606 | -5.104 | -5.446 | -3.0667 | -0.608 | 0.0 | -1.2603 | 0.0 | 3.629 |
| 5 | **-5.859** | 1.4208 | -4.701 | -7.792 | -6.054 | -4.889 | -4.52 | -0.284 | 0.0 | -1.0553 | 0.0 | 4.3081 |
| 6 | **-4.3068** | 1.4262 | -3.068 | -5.024 | -3.168 | -5.967 | -3.114 | -0.2735 | 0.0 | -0.9195 | 0.0 | 3.1667 |
| 7 | **-5.4837** | 1.0252 | -4.12 | -5.857 | -6.555 | -5.403 | -3.565 | -0.5917 | 0.0 | -1.327 | 0.0 | 4.0322 |
| 8 | **-2.9677** | 0.2143 | -2.848 | -3.284 | -2.824 | -2.915 | -1.4632 | -0.7302 | 0.0 | -0.774 | 0.0 | 2.1822 |

### 5NDZ / AZ3451 (allosteric) - crystallographic
| pose | ens.mean | ens.SD | pda_0 | pda_1 | pda_2 | pda_3 | vdW | H-bond | metal | hydroph | ionic | pred pKd |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | **-5.917** | 0.5116 | -5.851 | -6.444 | -5.241 | -6.132 | -4.4657 | -0.044 | 0.0 | -1.4078 | 0.0 | 4.3507 |

### 5NDZ / AZ3451 (allosteric) - 9 GNINA redock poses
| pose | ens.mean | ens.SD | pda_0 | pda_1 | pda_2 | pda_3 | vdW | H-bond | metal | hydroph | ionic | pred pKd |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | **-5.9512** | 0.476 | -5.771 | -5.365 | -6.404 | -6.265 | -3.978 | -0.1573 | 0.0 | -1.8165 | 0.0 | 4.3759 |
| 1 | **-6.5468** | 0.5591 | -6.799 | -6.195 | -5.986 | -7.207 | -4.8342 | -0.1255 | 0.0 | -1.5875 | 0.0 | 4.8138 |
| 2 | **-5.069** | 0.3012 | -5.414 | -4.892 | -5.217 | -4.753 | -3.312 | -0.4665 | 0.0 | -1.2902 | 0.0 | 3.7272 |
| 3 | **-4.5635** | 0.3298 | -4.117 | -4.529 | -4.875 | -4.733 | -3.5285 | -0.0795 | 0.0 | -0.9557 | 0.0 | 3.3555 |
| 4 | **-4.8145** | 0.3418 | -4.557 | -5.288 | -4.571 | -4.842 | -3.6887 | 0.0 | 0.0 | -1.1258 | 0.0 | 3.5401 |
| 5 | **-3.2073** | 0.1981 | -3.134 | -3.496 | -3.153 | -3.046 | -1.903 | -0.1797 | 0.0 | -1.1245 | 0.0 | 2.3583 |
| 6 | **-5.5907** | 1.2734 | -5.048 | -4.937 | -7.498 | -4.88 | -4.2497 | -0.1398 | 0.0 | -1.201 | 0.0 | 4.1108 |
| 7 | **-4.5663** | 0.8972 | -5.263 | -3.608 | -5.396 | -3.998 | -3.2055 | -0.0372 | 0.0 | -1.3235 | 0.0 | 3.3575 |
| 8 | **-4.8498** | 0.5204 | -5.491 | -4.347 | -4.517 | -5.044 | -3.7305 | 0.0 | 0.0 | -1.1195 | 0.0 | 3.566 |

### Summary

| System | Pocket | Source | n | best (min) | worst (max) | mean |
|---|---|---|---|---|---|---|
| 5NDD AZ8838 | orthosteric | crystal | 1 | -4.764 | -4.764 | -4.764 |
| 5NDD AZ8838 | orthosteric | redock | 9 | -5.962 | -2.968 | -4.694 |
| 5NDZ AZ3451 | allosteric | crystal | 1 | -5.917 | -5.917 | -5.917 |
| 5NDZ AZ3451 | allosteric | redock | 9 | -6.547 | -3.207 | -5.018 |

Observation (reported, not a pass/fail criterion): in both systems the best redock pose scores
slightly better than the crystallographic pose (-5.962 vs -4.764 for 5NDD;
-6.547 vs -5.917 for 5NDZ). This is expected - the redock poses were
energy-minimised by GNINA/SMINA whereas the crystal pose was not, and the README explicitly
recommends SMINA-optimised conformations. The allosteric AZ3451 system scores stronger than the
orthosteric AZ8838 system, consistent with AZ3451's larger size (38 vs 17 heavy atoms).

---

## 6. Verification checklist

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | GPU actually used | **PASS** | Every one of the 16 runs printed `device: device(type='cuda', index=0)`. `nvidia-smi --query-compute-apps` polled at 1 Hz during the run captured the python PID holding 518-1840 MiB of GPU memory (see `raw/gpu_usage_poll.log`, 128 sampled lines with an active python process). `torch.cuda.get_device_name(0)` = NVIDIA A100-SXM4-40GB, capability (8,0). |
| 2 | All predictions finite | **PASS** | 80 predictions, 0 NaN, 0 inf across 20 poses x 4 models. |
| 3 | Outputs not constant across the 9 poses | **PASS** | All 8 (system x model) combinations give 9 distinct values; see table below. |
| 4 | Correct ligand/pose-index mapping | **PASS** | Each 9-pose SDF was split into 9 **byte-exact** singleton files and rescored independently; singleton *i* reproduces batch index *i* for all 18 poses (max abs delta 0.001). |
| 5 | Score direction determined from the repo | **PASS** | Section 4 - four independent code-level lines of evidence. |

### Check 3 detail - spread across the 9 poses

| Set | Model | min | max | range | distinct |
|---|---|---|---|---|---|
| 5NDD_redock | pda_0 | -4.701 | -2.848 | 1.853 | 9/9 |
| 5NDD_redock | pda_1 | -7.792 | -3.284 | 4.508 | 9/9 |
| 5NDD_redock | pda_2 | -7.886 | -2.824 | 5.062 | 9/9 |
| 5NDD_redock | pda_3 | -5.967 | -2.915 | 3.052 | 9/9 |
| 5NDZ_redock | pda_0 | -6.799 | -3.134 | 3.665 | 9/9 |
| 5NDZ_redock | pda_1 | -6.195 | -3.496 | 2.699 | 9/9 |
| 5NDZ_redock | pda_2 | -7.498 | -3.153 | 4.345 | 9/9 |
| 5NDZ_redock | pda_3 | -7.207 | -3.046 | 4.161 | 9/9 |

### Check 4 detail - batch index vs independent singleton rescoring (pda_0)

| System | Pose | Batch total | Singleton total | abs delta |
|---|---|---|---|---|
| 5NDD | 0 | -4.067 | -4.067 | 0.0 |
| 5NDD | 1 | -3.401 | -3.401 | 0.0 |
| 5NDD | 2 | -3.202 | -3.203 | 0.001 |
| 5NDD | 3 | -3.47 | -3.471 | 0.001 |
| 5NDD | 4 | -3.586 | -3.586 | 0.0 |
| 5NDD | 5 | -4.701 | -4.7 | 0.001 |
| 5NDD | 6 | -3.068 | -3.068 | 0.0 |
| 5NDD | 7 | -4.12 | -4.12 | 0.0 |
| 5NDD | 8 | -2.848 | -2.848 | 0.0 |
| 5NDZ | 0 | -5.771 | -5.771 | 0.0 |
| 5NDZ | 1 | -6.799 | -6.799 | 0.0 |
| 5NDZ | 2 | -5.414 | -5.414 | 0.0 |
| 5NDZ | 3 | -4.117 | -4.117 | 0.0 |
| 5NDZ | 4 | -4.557 | -4.558 | 0.001 |
| 5NDZ | 5 | -3.134 | -3.134 | 0.0 |
| 5NDZ | 6 | -5.048 | -5.048 | 0.0 |
| 5NDZ | 7 | -5.263 | -5.263 | 0.0 |
| 5NDZ | 8 | -5.491 | -5.491 | 0.0 |

Supporting identity checks: heavy-atom counts are constant and correct within each system
(5NDD/AZ8838 = 17 heavy atoms, C13 N2 O1 F1; 5NDZ/AZ3451 = 38 heavy atoms, C30 N4 O3 Br1), each
matching its crystallographic reference; exactly 9 redock poses were scored per system (none
silently dropped by `predict.py`'s error filter); and per-pose heavy-atom centroids are all
distinct, recorded in the CSV as `ligand_centroid_xyz`.

---

## 7. Exact commands

```bash
# Repo
git clone https://github.com/ACE-KAIST/PIGNet2.git      # commit f621aaaa9fe7

# Environment (README) + the five documented additions
conda create -n pignet2 python=3.9
conda install -n pignet2 rdkit=2022.03.4 openbabel pymol-open-source -c conda-forge
pip install -r requirements.txt                         # minus dimorphite_dl
conda install -c conda-forge dimorphite-dl=1.3.2
conda install -c bioconda -c conda-forge reduce
conda install -c conda-forge cudatoolkit=11.1
sudo apt-get install -y libgl1 libglib2.0-0 libxrender1 libxext6
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH

# Controls: 4 sets x 4 checkpoints = 16 runs
for ck in 0 1 2 3; do
  python src/exe/predict.py ./src/ckpt/pda_${ck}.pt \
     -p controls/5NDD_inactive_orthosteric_receptor_clean.pdb \
     -l controls/5NDD_AZ8838_crystallographic_clean.sdf   -o results/5NDD_crystal_pda${ck}.txt
  python src/exe/predict.py ./src/ckpt/pda_${ck}.pt \
     -p controls/5NDD_inactive_orthosteric_receptor_clean.pdb \
     -l controls/5NDD_AZ8838_corrected_gnina_redock.sdf   -o results/5NDD_redock_pda${ck}.txt
  python src/exe/predict.py ./src/ckpt/pda_${ck}.pt \
     -p controls/5NDZ_inactive_allosteric_receptor_clean.pdb \
     -l controls/5NDZ_AZ3451_crystallographic_clean.sdf   -o results/5NDZ_crystal_pda${ck}.txt
  python src/exe/predict.py ./src/ckpt/pda_${ck}.pt \
     -p controls/5NDZ_inactive_allosteric_receptor_clean.pdb \
     -l controls/5NDZ_AZ3451_corrected_gnina_redock.sdf   -o results/5NDZ_redock_pda${ck}.txt
done
```

No `--no-prot-pdb` / `--no-prot-sdf` flags were used, so the repo's **default** protonation
pipeline ran (receptor: PyMOL HETATM fix -> `reduce -Trim` -> `reduce -BUILD -NUC -NOFLIP` ->
PyMOL re-save; ligand: Dimorphite-DL dominant microspecies at pH 7.4 then
`AssignBondOrdersFromTemplate`). Both operate on temporary copies - **no receptor or ligand file
in the repo was altered**, and input SHA-256s were verified identical on the Mac and the A100
before and after (`raw/input_sha256.txt`).

---

## 8. Limitations and things NOT done

- **Production scoring not run.** The 30,978 poses are untouched, per instruction.
- **No experimental affinity anchor.** `true_label` is 0.000 everywhere; the controls establish
  that the model runs correctly and discriminates poses, *not* that its absolute affinities are
  accurate for PAR2. There is no measured pKd here to calibrate against.
- **n = 2 ligands.** Ensemble SD is within-ensemble (model-to-model) spread only; it is not a
  confidence interval on the true affinity.
- **1 explicit H in the redock SDFs** is dropped by `SDMolSupplier(removeHs=True)` before
  Dimorphite-DL re-protonates, so redock and crystal ligands enter the model on the same
  heavy-atom footing. Verified: 17 and 38 heavy atoms respectively in both sources.
- **`nvcc` absent**; only the CUDA runtime libraries are present. Fine for these prebuilt wheels,
  but anything needing on-the-fly CUDA compilation would need a full toolkit.
- The 0.001 discrepancy vs the shipped example is hardware/library nondeterminism. If exact
  bit-reproducibility against the authors ever matters, it is not achieved here.

## 9. Files

| File | Contents |
|---|---|
| `PIGNET2_CONTROL_VALIDATION.csv` | 20 rows - one per scored pose. Ensemble mean/SD, all 4 per-model totals, all 5 energy components per model and ensemble-averaged, predicted pKd, heavy-atom count, centroid, GNINA reference scores, PIGNet2 key. |
| `PIGNET2_VALIDATION.md` | This report. |
| `A100_PROVENANCE.json` | Machine + software manifest, checkpoint and input hashes, install deviations, chemistry-handling record, full `pip freeze`. |
| `raw/` | Unmodified `predict.py` outputs (16 batch + 18 singleton), GPU poll log, manifests, hashes, `pip_freeze.txt`, `conda_list.txt`. |
