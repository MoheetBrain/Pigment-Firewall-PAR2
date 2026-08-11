# Yonsei final-10 V2 work products

Branch: `yonsei-final10-v2`

This directory contains a non-destructive audit, corrected reference-pocket artifacts, ProLIF crystal fingerprints, reference-redocking diagnostics, and sourceability triage for the existing PAR2 V1 project. Historical V1 data under `GNINA_SCREEN_EX32/`, `RESULTS/`, `PROTEINS/`, `BENCHMARK_LIGS/`, and `SCREENING/` is preserved.

## Current gate

The corrected ligand-centred 5NDD/5NDZ structures and configs were built, but a compatible GNINA executable is not available on this Apple Silicon host. Historical GNINA redock SDFs were evaluated only as diagnostics:

| System | Historical best symmetry-corrected heavy-atom RMSD | Best ProLIF fingerprint recovery | Corrected-config pass |
|---|---:|---:|---|
| 5NDD / AZ8838 | 0.465 Å | 0.600 | Not validated |
| 5NDZ / AZ3451 | 1.002 Å | 0.889 | Not validated |

The corrected benchmark gate therefore remains blocked and no candidate redocking or V2 TOP100/TOP50/TOP20 ranking is claimed.

## Re-run sequence

```text
python YONSEI_FINAL10_V2/scripts/audit_v1.py
python YONSEI_FINAL10_V2/scripts/build_reference_models.py
python YONSEI_FINAL10_V2/scripts/reference_interactions.py
python YONSEI_FINAL10_V2/scripts/validate_reference_redock.py
python YONSEI_FINAL10_V2/scripts/build_candidate_universe.py
python YONSEI_FINAL10_V2/scripts/run_reference_redock.py 5NDD_AZ8838 --gnina /path/to/compatible/gnina
python YONSEI_FINAL10_V2/scripts/run_reference_redock.py 5NDZ_AZ3451 --gnina /path/to/compatible/gnina
```

After a corrected GNINA run, recalculate RMSD/contact recovery with the validation script and unlock candidate redocking only if both systems meet RMSD <2.0 Å. The existing `validate_reference_redock.py` explicitly marks historical `BIN/GNINA_RUN_EX32_CPU` outputs as diagnostic-only.

## Key outputs

- `00_AUDIT/V1_AUDIT.md` and `00_AUDIT/V1_AUDIT_SUMMARY.json`: V1 counts, top prefixes, library linkage, receptor/config/source inventories, benchmark inconsistencies, and Pass-2 status.
- `01_REFERENCE_POCKETS/`: clean 8TZ/8UN ligand files, clean ATOM-only receptor files, exact heavy-atom geometry, and ligand-centred GNINA configs.
- `02_REFERENCE_VALIDATION/`: ProLIF reference fingerprints and historical-redock diagnostics.
- `03_SOURCEABILITY/V2_CANDIDATE_UNIVERSE.csv`: deduplicated triage universe with preserved V1 values, RDKit descriptors, and procurement fields intentionally set to `PENDING`.
- `03_SOURCEABILITY/V1_TOP100_SOURCEABILITY.csv`: V1 top-100 procurement-status view.

No final experimental ten is nominated in this phase because the corrected GNINA benchmark and live procurement fields are incomplete.
