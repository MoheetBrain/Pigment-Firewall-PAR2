# Yonsei final-10 V2 work products

Branch: `yonsei-final10-v2`

This directory contains a non-destructive audit, corrected reference-pocket artifacts, ProLIF crystal fingerprints, reference-redocking diagnostics, and sourceability triage for the existing PAR2 V1 project. Historical V1 data under `GNINA_SCREEN_EX32/`, `RESULTS/`, `PROTEINS/`, `BENCHMARK_LIGS/`, and `SCREENING/` is preserved.

## Current gate

The corrected ligand-centred 5NDD/5NDZ structures and configs were run fresh on the Debian x86_64 GCP VM `moheetc4` with official GNINA v1.3.3 CPU execution. Both corrected reference systems pass the primary geometric benchmark by their best pose:

| System | Historical best symmetry-corrected heavy-atom RMSD | Best ProLIF fingerprint recovery | Corrected-config pass |
|---|---:|---:|---|
| 5NDD / AZ8838 | 0.465 Å | 0.700 | PASS; corrected best 0.675 Å |
| 5NDZ / AZ3451 | 1.002 Å | 0.889 | PASS; corrected best 0.867 Å |

The corrected benchmark gate is now `OPEN_REFERENCE_BENCHMARK_PASSED`. The top-ranked pose is crystallographic-like for 5NDD (0.675 Å), while 5NDZ's top-ranked pose is close but above the 2 Å geometric cutoff (2.227 Å); its second pose is the best geometric match (0.867 Å) and the top-ranked pose still recovers 0.889 of the reference ProLIF keys. No candidate redocking or V2 TOP100/TOP50/TOP20 ranking has been launched.

## Re-run sequence

```text
python YONSEI_FINAL10_V2/scripts/audit_v1.py
python YONSEI_FINAL10_V2/scripts/build_reference_models.py
python YONSEI_FINAL10_V2/scripts/reference_interactions.py
python YONSEI_FINAL10_V2/scripts/build_candidate_universe.py
python YONSEI_FINAL10_V2/scripts/verify_reference_systems.py
bash YONSEI_FINAL10_V2/scripts/run_gnina_reference.sh
```

The reference runner records the exact GNINA command, seed, output, log, and binary version for each system. The validation script uses symmetry-corrected heavy-atom spyrmsd and ProLIF fingerprints, explicitly marks historical `BIN/GNINA_RUN_EX32_CPU` outputs as diagnostic-only, and unlocks candidate redocking only when both corrected systems meet RMSD <=2.0 Å.

## Key outputs

- `00_AUDIT/V1_AUDIT.md` and `00_AUDIT/V1_AUDIT_SUMMARY.json`: V1 counts, top prefixes, library linkage, receptor/config/source inventories, benchmark inconsistencies, and Pass-2 status.
- `01_REFERENCE_POCKETS/`: clean 8TZ/8UN ligand files, clean ATOM-only receptor files, exact heavy-atom geometry, and ligand-centred GNINA configs.
- `01_BENCHMARK_REPAIR/`: VM environment report, reference-system integrity check, corrected GNINA SDF/log/metadata outputs, and the pinned reference-only runner.
- `02_REFERENCE_VALIDATION/`: ProLIF reference fingerprints, corrected-redock RMSD/IFP metrics, and the gate report.
- `03_SOURCEABILITY/V2_CANDIDATE_UNIVERSE.csv`: deduplicated triage universe with preserved V1 values, RDKit descriptors, and procurement fields intentionally set to `PENDING`.
- `03_SOURCEABILITY/V1_TOP100_SOURCEABILITY.csv`: V1 top-100 procurement-status view.

No final experimental ten is nominated in this phase because the corrected GNINA benchmark and live procurement fields are incomplete.
