# Independent verification of the CPU de novo production artifacts

**Result: PASSED**

This report was produced by `scripts/verify_denovo_outputs.py`, which re-derives every descriptor, the Morgan reference Tanimoto, and the `design_score` from each stored SMILES using the specification in `HANDOFF_TO_CLAUDE.md` sections 11-12. It does not import the generator, so documentation/output drift is detectable.

Verification is a reproducibility and internal-consistency check on the committed CSVs. It says nothing about PAR2 biological activity.

## Environment

| Component | Version |
|---|---|
| Python | 3.11.15 |
| RDKit | 2026.03.5 |
| pandas | 3.0.5 |
| NumPy | 2.4.6 |
| Workers | 4 |

## Reference ligands used for `ref_tanimoto`

| Family | Canonical SMILES |
|---|---|
| orthosteric (5NDD / AZ8838 / 8TZ) | `CCCc1cc(F)ccc1[C@H](O)C1N=CC=N1` |
| allosteric (5NDZ / AZ3451 / 8UN) | `C[C@@H](C1CCCCC1)n1c(-c2cc3c(cc2Br)OCO3)nc2cc(C(=O)Nc3ccc(C#N)cc3)ccc21` |

## Per-table checks

| Check | DENOVO_15000 | DENOVO_TOP3000 |
|---|---:|---:|
| Rows | 15000 | 3000 |
| Unparsable SMILES | 0 | 0 |
| Unique stored SMILES | 15000 | 3000 |
| Stored SMILES already canonical | True | True |
| Rows with recomputed-value mismatch | 0 | 0 |
| Rows failing family hard filters | 0 | 0 |
| PAINS A/B/C positive rows | 0 | 0 |
| Reactive-group rows | 0 | 0 |
| Heavy-atom range violations (12-44) | 0 | 0 |
| Unique Murcko scaffolds | 6725 | 1492 |
| Max scaffold repeat | 109 | 12 |

## Family allocation

| Family | DENOVO_15000 | Specified | DENOVO_TOP3000 | Routes to |
|---|---:|---:|---:|---|
| orthosteric | 10000 | 10000 | 1867 | 5NDD |
| allosteric | 3500 | 3500 | 678 | 5NDZ |
| exploratory | 1500 | 1500 | 455 | 5NDD, 5NDZ |

## Cross-table relations

| Check | Value |
|---|---|
| TOP3000 is a subset of DENOVO_15000 | True |
| TOP3000 rows absent from the 15,000 | 0 |
| TOP3000 max scaffold repeat (cap 12) | 12 |
| Scaffold cap respected | True |
| Planned ligand-pocket docking assignments | 3455 |
| Family allocation matches specification | True |

## Descriptor summary (recomputation-verified stored values)

| Field | Min | Median | Mean | Max |
|---|---:|---:|---:|---:|
| design_score | 0.3569 | 0.6894 | 0.6804 | 0.9648 |
| ref_tanimoto | 0.0521 | 0.1505 | 0.1571 | 0.8462 |
| mw | 200.2050 | 344.4360 | 348.2758 | 518.7160 |
| logp | 0.5034 | 3.2925 | 3.2393 | 5.6724 |
| tpsa | 15.7900 | 75.9900 | 74.6444 | 124.9000 |
| hba | 0.0000 | 5.0000 | 4.8925 | 10.0000 |
| hbd | 0.0000 | 2.0000 | 1.8861 | 4.0000 |
| rotb | 0.0000 | 4.0000 | 4.4081 | 10.0000 |
| fsp3 | 0.0000 | 0.5000 | 0.5055 | 1.0000 |
| qed | 0.2102 | 0.7347 | 0.7118 | 0.9465 |

## Interpretation limits

- A pass means the committed CSVs are internally consistent and reproducible from their own SMILES under the documented method.
- `design_score`, `ref_tanimoto` and QED remain two-dimensional design priors. They are not probabilities of PAR2 inhibition.
- No pose, GNINA score, interaction fingerprint, or procurement fact is established by this report.
