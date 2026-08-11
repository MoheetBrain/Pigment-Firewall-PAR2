# Reference redocking validation

## Gate status

- GNINA executable detected: `False`.
- Corrected-config benchmark status: **BLOCKED_NO_COMPATIBLE_GNINA_EXECUTABLE**.
- Candidate redocking gate: **BLOCKED_UNTIL_CORRECTED_REFERENCE_REDOCK_PASSES**.

The repository's `BIN/GNINA_RUN_EX32_CPU/GNINA_OUT_*_Redock.sdf` files are evaluated below as historical diagnostics only unless corrected outputs are present in `corrected_redock/`. Their original command/config provenance is not present, so they cannot establish that the corrected ligand-centred boxes were used.

| System | Evaluated poses | Best symmetry-corrected heavy-atom RMSD (Å) | Best ProLIF recovery | Corrected benchmark passed |
|---|---:|---:|---:|---|
| 5NDD_AZ8838 | 9 | 0.4648852458023434 | 0.6 | False |
| 5NDZ_AZ3451 | 9 | 1.0024936773655457 | 0.8888888888888888 | False |

V2 candidate redocking and V2 rank files are produced only after this script reports `OPEN_REFERENCE_BENCHMARK_PASSED`.
