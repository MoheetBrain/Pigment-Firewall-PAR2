# Corrected GNINA benchmark environment

This file records the execution environment and the pinned GNINA binary used for the two reference-only redocks.

## Platform detection

- Host: `moheetc4`
- OS: Debian GNU/Linux 13 (trixie)
- Architecture: x86_64
- Apple Silicon: false
- Docker/Colima: not available
- Conda/Mamba: not available
- CUDA/nvidia-smi: not available; CPU execution is used

## GNINA

- Installation method: official GNINA Linux x86_64 static release binary
- Release URL: `https://github.com/gnina/gnina/releases/download/v1.3.3/gnina.cuda12.8.static`
- Version: `gnina v1.3.3 master:6fe1ce2   Built Jun 30 2026.`
- SHA256: `3340c1f49cd3c7c84d8699182a1c6af13c7fa2a22448d1204640446106f72172`
- Executable on VM: `/home/moheet/bin/gnina.cuda12.8.static`
- CUDA/cuDNN runtime support: NVIDIA Python wheels installed under `/home/moheet/gnina-cuda-libs` because the official binary dynamically links CUDA libraries even for CPU execution.
- Runtime wheel versions: `nvidia-cuda-runtime-cu12==12.9.79`, `nvidia-cuda-nvrtc-cu12==12.9.86`, `nvidia-cudnn-cu12==9.24.0.43`, `nvidia-cublas-cu12==12.9.2.10`, `nvidia-cusparse-cu12==12.5.10.65`, `nvidia-cufft-cu12==11.4.1.4`, `nvidia-cusolver-cu12==11.7.5.82`, `nvidia-nvjitlink-cu12==12.9.86`.

## Corrected benchmark command

The committed `scripts/run_gnina_reference.sh` runs only `5NDD_AZ8838` and `5NDZ_AZ3451`, with `CUDA_VISIBLE_DEVICES=-1`, GNINA `--no_gpu`, `--exhaustiveness 32`, `--num_modes 9`, `--cnn_scoring rescore`, `--min_rmsd_filter 2.0`, `--seed 20260811`, and `--cpu 4` for forced CPU execution. It writes all GNINA SDF/log/metadata outputs under `01_BENCHMARK_REPAIR/corrected_redock/` and validates them with the existing V2 ProLIF/spyrmsd script.

## Reference geometry

The cleaned ligand/receptor coordinate frames and ligand-centred boxes are the existing V2 artifacts under `01_REFERENCE_POCKETS/`. The boxes use the cleaned crystallographic ligand heavy-atom centroid and 5 Å padding on each side (approximately the requested 6 Å padding):

| System | Centre (x, y, z Å) | Size (x, y, z Å) |
|---|---|---|
| 5NDD / AZ8838 / 8TZ | 16.974, 5.926, 55.826 | 17.332, 17.672, 13.644 |
| 5NDZ / AZ3451 / 8UN | 1.356, 12.419, 48.400 | 20.702, 17.885, 25.525 |

## Python validation environment

The VM uses Python 3.13.5 in `/home/moheet/par2-v2-venv` with: `rdkit==2026.3.5`, `prolif==2.2.1`, `spyrmsd==0.9.0`, `biopython==1.88`, `plip==3.0.1`, `pandas==3.0.5`, `numpy==2.5.2`, and `scipy==1.18.0`. Open Babel is also installed from Debian (`3.1.1+dfsg-12`).

## Benchmark result

`verify_reference_systems.py` passed for both systems. Fresh corrected GNINA outputs were written under `corrected_redock/` and validated by `validate_reference_redock.py`:

| System | Best RMSD (Å) | Top-ranked RMSD (Å) | Top-ranked IFP recovery | Best IFP recovery | Gate |
|---|---:|---:|---:|---:|---|
| 5NDD / AZ8838 | 0.674658 | 0.674658 | 0.500 | 0.700 | PASS; strong |
| 5NDZ / AZ3451 | 0.867183 | 2.227395 | 0.889 | 0.889 | PASS; strong |

The final status is `OPEN_REFERENCE_BENCHMARK_PASSED`. Candidate docking was not launched in this run.
