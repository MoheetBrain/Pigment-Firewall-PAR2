# Corrected reference benchmark results

Execution host: `moheetc4` (Debian 13, x86_64, GCP zone `europe-west2-c`).

1. OS/architecture: Debian GNU/Linux 13 (trixie), x86_64; no Docker/Colima, Conda/Mamba, CUDA device, or Apple Silicon.
2. GNINA installation method: official GNINA Linux x86_64 v1.3.3 static release, with CUDA 12/cuDNN runtime libraries supplied by pinned NVIDIA Python wheels; CPU execution.
3. GNINA version: `gnina v1.3.3 master:6fe1ce2 Built Jun 30 2026`; binary SHA256 `3340c1f49cd3c7c84d8699182a1c6af13c7fa2a22448d1204640446106f72172`.
4. Corrected 5NDD box: centre `(16.974, 5.926, 55.826)` Å; dimensions `(17.332, 17.672, 13.644)` Å.
5. Corrected 5NDZ box: centre `(1.356, 12.419, 48.400)` Å; dimensions `(20.702, 17.885, 25.525)` Å.
6. 5NDD/AZ8838 best symmetry-corrected heavy-atom RMSD: `0.674658` Å (pose 1; strong pass).
7. 5NDD top-ranked-pose RMSD: `0.674658` Å; top-ranked ProLIF recovery `0.500`.
8. 5NDD IFP recovery: best-pose recovery `0.700`; the relevant orthosteric antagonist pocket is reproduced by the best pose.
9. 5NDZ/AZ3451 best symmetry-corrected heavy-atom RMSD: `0.867183` Å (pose 2; strong pass).
10. 5NDZ top-ranked-pose RMSD: `2.227395` Å; top-ranked ProLIF recovery `0.889`.
11. 5NDZ IFP recovery: best-pose recovery `0.889`; the relevant allosteric antagonist pocket is reproduced by the best pose. The top-ranked pose reproduces the interaction fingerprint but is not itself under the 2 Å geometric cutoff.
12. PASS/FAIL: 5NDD PASS; 5NDZ PASS by best-pose RMSD <=2 Å, both strong by best-pose RMSD <=1.5 Å.
13. `OPEN_REFERENCE_BENCHMARK_PASSED=TRUE`.
14. Exact next action: stop before candidate docking and present these benchmark results; after approval, run the existing V1 final-500 plus FDA/approved-drug candidates against both corrected pockets using GNINA and pocket-specific ProLIF comparison.
15. Git commit hash: see the `yonsei-final10-v2` branch commit containing this report; the final hash is reported at handoff.

The exact GNINA commands, forced-CPU settings (`CUDA_VISIBLE_DEVICES=-1`, `--no_gpu`), random seed (`20260811`), exhaustiveness (`32`), pose count (`9`), CPU threads (`4`), receptor/ligand/config paths, and output/log paths are in the two `*_run_metadata.json` files in `corrected_redock/`. No historical `BIN/GNINA_RUN_EX32_CPU/GNINA_OUT_*_Redock.sdf` file was used for this benchmark.
