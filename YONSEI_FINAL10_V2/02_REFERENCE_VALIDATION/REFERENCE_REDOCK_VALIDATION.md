# Reference redocking validation

## Gate status

- GNINA executable detected: `True`.
- Corrected-config benchmark status: **PASS_BOTH_SYSTEMS_RMSD_UNDER_2A**.
- Candidate redocking gate: **OPEN_REFERENCE_BENCHMARK_PASSED**.

The repository's `BIN/GNINA_RUN_EX32_CPU/GNINA_OUT_*_Redock.sdf` files are evaluated below as historical diagnostics only unless corrected outputs are present in `corrected_redock/`. Their original command/config provenance is not present, so they cannot establish that the corrected ligand-centred boxes were used.

| System | Evaluated poses | Best RMSD (Å) | Top-ranked RMSD (Å) | Top-ranked ProLIF recovery | Best ProLIF recovery | Corrected benchmark passed |
|---|---:|---:|---:|---:|---:|---|
| 5NDD_AZ8838 | 9 | 0.674657594200024 | 0.674657594200024 | 0.5 | 0.7 | True |
| 5NDZ_AZ3451 | 9 | 0.867182900333937 | 2.2273950244033593 | 0.8888888888888888 | 0.8888888888888888 | True |

V2 candidate redocking and V2 rank files are produced only after this script reports `OPEN_REFERENCE_BENCHMARK_PASSED`.
