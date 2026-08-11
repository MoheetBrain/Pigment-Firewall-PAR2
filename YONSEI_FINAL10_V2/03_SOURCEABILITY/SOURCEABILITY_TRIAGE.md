# V2 sourceability triage

Candidate universe size: **5,973 unique structure keys**.

The universe combines the V1 final 500, all FDA_DRUGS records in the repository, and identifiable non-FDA Pass-1 hits. Procurement fields are all `PENDING` because no live vendor lookup was performed.

## Counts

| Measure | Count |
|---|---:|
| V1 final-500 rows represented | 500 |
| FDA/approved-library records represented | 4487 |
| Other identifiable V1 hits represented | 1075 |
| RDKit-parseable structures | 5973 |

No `V2_TOP100.csv`, `V2_TOP50.csv`, or `V2_TOP20.csv` is generated in this phase because the corrected reference redocking gate is blocked.

`V1_TOP100_SOURCEABILITY.csv` contains the V1 top-100 rows with procurement status. All live procurement fields are `PENDING`.
