# Yonsei final-10 V2 work products

> **START HERE (2026-09-05):** read `HANDOFF_2026-09-05.md`. It supersedes
> `HANDOFF_TO_CLAUDE.md`, which predates every correction made since 12 Aug.
> Final deliverables are in `10_FINAL/`. All cloud instances are stopped.


Branch: `yonsei-final10-v2`

This directory contains a non-destructive audit, corrected reference-pocket artifacts, ProLIF crystal fingerprints, fresh forced-CPU GNINA reference redocking, sourceability triage, and a completed 15,000-molecule CPU de novo generation campaign for the existing PAR2 V1 project. Historical V1 data under `GNINA_SCREEN_EX32/`, `RESULTS/`, `PROTEINS/`, `BENCHMARK_LIGS/`, and `SCREENING/` is preserved.

## Current gate

The corrected ligand-centred 5NDD/5NDZ structures and configs were run fresh on the Debian x86_64 GCP VM `moheetc4` with official GNINA v1.3.3 CPU execution. Both corrected reference systems pass the primary geometric benchmark by their best pose:

| System | Historical best symmetry-corrected heavy-atom RMSD | Best ProLIF fingerprint recovery | Corrected-config pass |
|---|---:|---:|---|
| 5NDD / AZ8838 | 0.465 Å | 0.700 | PASS; corrected best 0.675 Å |
| 5NDZ / AZ3451 | 1.002 Å | 0.889 | PASS; corrected best 0.867 Å |

The corrected benchmark gate is now `OPEN_REFERENCE_BENCHMARK_PASSED`. The top-ranked pose is crystallographic-like for 5NDD (0.675 Å), while 5NDZ's top-ranked pose is close but above the 2 Å geometric cutoff (2.227 Å); its second pose is the best geometric match (0.867 Å) and the top-ranked pose still recovers 0.889 of the reference ProLIF keys.

After the reference benchmark passed, a later explicit request expanded the work to CPU de novo generation. The production run created exactly 15,000 unique filtered designs: 10,000 orthosteric-family, 3,500 allosteric-family, and 1,500 exploratory. A scaffold-capped 3,000-design subset is prepared for corrected pocket-specific docking. Generated molecules have not yet been docked and are not claimed to be PAR2 antagonists.

## Verification status (added after independent review)

An independent verification pass over commit `3a80c0b` confirmed that the de novo
production artifacts are internally consistent: all six checksums match and every
row of both design tables recomputes exactly. It also found **two defects in the
reference models** those designs were built on. See
[`04_VERIFICATION/REFERENCE_MODEL_DEFECTS.md`](04_VERIFICATION/REFERENCE_MODEL_DEFECTS.md).

1. **The orthosteric reference ligand is the wrong tautomer.** The stored 8TZ is a
   non-aromatic 4H-imidazole, not AZ8838 (wwPDB InChIKey mismatch; same formula and
   mass, which is why earlier checks passed). It propagated into BRICS seeding:
   **2,131 of the 15,000 designs - and 394 of the 3,000 in the docking queue -
   carry the wrong motif structurally**, which rescoring cannot fix. The allosteric
   reference (8UN / AZ3451) is clean.
2. **The reference ProLIF fingerprints contain no hydrogen bonds**, because neither
   ligand nor receptor was protonated before fingerprinting. The `0.700` and `0.889`
   recovery figures in the gate table above are therefore measured against an
   incomplete reference and should not be quoted as interaction-level validation
   until regenerated.

**The RMSD half of the benchmark gate is unaffected** - RMSD is purely geometric,
so both systems still pass the primary <=2.0 A best-pose criterion, and the 5NDZ
top-pose nuance stands as written.

Recommended sequencing is in the defects report; in short, repair the reference
ligand and the fingerprints before spending GNINA CPU time on the current docking
queue. The sourceable V1/FDA route is not blocked by either defect.

## Re-run sequence

```text
python YONSEI_FINAL10_V2/scripts/audit_v1.py
python YONSEI_FINAL10_V2/scripts/build_reference_models.py
python YONSEI_FINAL10_V2/scripts/reference_interactions.py
python YONSEI_FINAL10_V2/scripts/build_candidate_universe.py
python YONSEI_FINAL10_V2/scripts/verify_reference_systems.py
bash YONSEI_FINAL10_V2/scripts/run_gnina_reference.sh
python YONSEI_FINAL10_V2/scripts/par2_denovo_cpu.py --repo . --n-total 15000 --top-docking 3000 --workers 20
```

The reference runner records the exact GNINA command, seed, output, log, and binary version for each system. The validation script uses symmetry-corrected heavy-atom spyrmsd and ProLIF fingerprints, explicitly marks historical `BIN/GNINA_RUN_EX32_CPU` outputs as diagnostic-only, and unlocks candidate redocking only when both corrected systems meet RMSD <=2.0 Å.

## Key outputs

- `00_AUDIT/V1_AUDIT.md` and `00_AUDIT/V1_AUDIT_SUMMARY.json`: V1 counts, top prefixes, library linkage, receptor/config/source inventories, benchmark inconsistencies, and Pass-2 status.
- `01_REFERENCE_POCKETS/`: clean 8TZ/8UN ligand files, clean ATOM-only receptor files, exact heavy-atom geometry, and ligand-centred GNINA configs.
- `01_BENCHMARK_REPAIR/`: VM environment report, reference-system integrity check, corrected GNINA SDF/log/metadata outputs, and the pinned reference-only runner.
- `02_REFERENCE_VALIDATION/`: ProLIF reference fingerprints, corrected-redock RMSD/IFP metrics, and the gate report.
- `03_SOURCEABILITY/V2_CANDIDATE_UNIVERSE.csv`: deduplicated triage universe with preserved V1 values, RDKit descriptors, and procurement fields intentionally set to `PENDING`.
- `03_SOURCEABILITY/V1_TOP100_SOURCEABILITY.csv`: V1 top-100 procurement-status view.
- `02_DENOVO_CPU/DENOVO_15000.csv`: the final 15,000 unique filtered de novo designs with family, score, reference similarity, scaffold, and descriptors.
- `02_DENOVO_CPU/DENOVO_TOP3000_FOR_DOCKING.csv`: diversity-aware docking queue with pocket routing.
- `02_DENOVO_CPU/SCORED_CANDIDATES.csv`: all 17,074 family-labelled candidates that survived the hard chemistry filters before cross-family selection.
- `02_DENOVO_CPU/GENERATION_MANIFEST.json` and `denovo.log`: exact run settings, counts, input paths, script checksum, refill history, and execution trace.
- `scripts/par2_denovo_cpu.py`: byte-identical source used for the VM production run.
- `HANDOFF_TO_CLAUDE.md`: comprehensive project history, scientific reasoning, implementation details, results, limitations, and next actions.

No final experimental ten is nominated. The reference benchmark is complete and passed, but the generated designs and the existing candidate universe still require corrected pocket-specific docking/IFP analysis, live procurement verification, and experimental prioritisation.
