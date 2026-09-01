# 04_VERIFICATION — independent verification of the V2 campaign

An independent pass over `yonsei-final10-v2` at commit `3a80c0b`. Nothing here
modifies, replaces, or deletes a production artifact; every script is read-only
with respect to `02_DENOVO_CPU/`, `01_REFERENCE_POCKETS/`, and `00_AUDIT/`.

## Result in one line

The de novo artifacts are internally consistent and reproduce exactly. Two
defects were found in the **reference models** they were built on.

## Contents

| File | What it is |
|---|---|
| `REFERENCE_MODEL_DEFECTS.md` | **Start here.** The two confirmed defects, their quantified impact, and recommended sequencing. |
| `DENOVO_VERIFICATION.md` / `.json` | Row-by-row recomputation of both design tables. PASSED. |
| `REFERENCE_TAUTOMER_CHECK.json` | wwPDB identity check on both reference ligands, plus scoring impact. |
| `REFERENCE_IFP_DIAGNOSIS.json` | Controlled ProLIF experiment isolating the missing-hydrogen defect. |
| `affected_designs_wrong_tautomer.csv` | The 2,131 designs carrying the wrong tautomer, each with its corrected SMILES. |

## Reproducing

Requires RDKit, pandas, NumPy, SciPy and ProLIF. Versions used are recorded in
`DENOVO_VERIFICATION.json`; RDKit 2026.03.5 and ProLIF 2.2.1 match the
production VM.

```bash
python YONSEI_FINAL10_V2/scripts/verify_denovo_outputs.py
python YONSEI_FINAL10_V2/scripts/check_reference_tautomers.py --impact --scan-designs
python YONSEI_FINAL10_V2/scripts/diagnose_reference_ifp.py
```

Each script exits non-zero when it finds a problem, so all three are usable as
regression gates in CI or before a future production run.
