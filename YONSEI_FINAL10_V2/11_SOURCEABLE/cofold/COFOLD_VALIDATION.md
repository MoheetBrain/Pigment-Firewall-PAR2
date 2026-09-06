# Co-folding reference validation — Boltz-2 vs the 5NDD crystal

**Date:** 2026-09-06 · machine `a100` (A100-SXM4-80GB) · Boltz-2.2.1

## Why this had to be run first

Co-folding is only worth doing if the model can put a known ligand back where
the crystal says it goes, **without being told the answer**. The GNINA pose was
never supplied. The only spatial information given was the identity of the 17
crystallographic contact residues of the 5NDD orthosteric pocket, with a 6 Å
`max_distance` — i.e. "the ligand binds somewhere near these residues", not
"the ligand sits here".

## Setup

- Target: wild-type human PAR2 (UniProt P55085) residues 59–370. No BRIL/T4L
  fusion, no thermostabilising mutations, and the N-terminal tethered-ligand
  region (1–58) excluded so it cannot compete for the orthosteric site.
- Ligand: AZ8838, corrected aromatic-imidazole tautomer
  `CC(Oc1cccc(F)c1)c1ncc[nH]1`.
- MSA: ColabFold MMseqs2 server, 6,463 sequences. Cached and reused.
- 5 diffusion samples, 3 recycling steps, 200 sampling steps, seed 20260906,
  `--no_kernels` (the `cuequivariance_torch` kernels are not installed; the
  first attempt crashed on that import and was relaunched).

## Result — the model recovers the crystal binding mode

Alignment is over 295 common Cα atoms (co-folded chain A renumbered to UniProt
by +58), then the ligand is compared in the crystal frame.

| model | confidence | ligand ipTM | backbone RMSD (Å) | ligand RMSD (Å) | centroid displacement (Å) |
|---:|---:|---:|---:|---:|---:|
| 0 | 0.960 | 0.979 | 1.16 | 1.22 | 0.69 |
| 1 | 0.958 | 0.978 | 0.98 | 1.23 | 0.89 |
| 2 | 0.957 | 0.980 | 1.14 | 1.22 | 0.71 |
| 3 | 0.957 | 0.977 | 1.12 | 1.24 | 0.76 |
| 4 | 0.953 | 0.974 | 1.12 | 1.27 | 0.83 |

**Best ligand RMSD 1.22 Å; best centroid displacement 0.69 Å.** All five
diffusion samples agree with each other and with the crystal, so this is not a
lucky single sample.

The ligand RMSD figure is a symmetry-free nearest-neighbour surrogate (see
`v3_analyse_cofold.py`). It slightly **under**-estimates a true
atom-correspondence RMSD, so it is used to separate "same site and orientation"
from "different", and is not quoted as a crystallographic RMSD. The centroid
displacement carries no such caveat: at 0.69 Å the ligand is unambiguously in
the crystallographic pocket, in the right place.

## Affinity module reference point

AZ8838 co-fold affinity output:

```
affinity_pred_value          0.686
affinity_probability_binary  0.583
```

`affinity_pred_value` is Boltz-2's log-scale affinity readout, not a measured
constant. AZ8838's real potency is roughly IC50 ~0.4 µM, and the predicted
value corresponds to a considerably weaker figure, so **the absolute number is
not trustworthy**. It is retained only as an anchor for RELATIVE comparison
across candidates run under identical settings. A binder probability of 0.58
for a genuine crystallographic binder also shows this module is not a
confident discriminator — candidate binder probabilities must be read against
this reference, not against 1.0.

## What this validation does and does not license

It licenses using co-folding as an **orthogonal structural filter**: a
candidate that co-folds confidently into the same pocket with a consistent
pose has independent structural support beyond GNINA.

It does **not** license any claim about antagonism. Co-folding predicts a
structure, not a function, and cannot separate an antagonist from a biased
agonist. That distinction needs the G12/13→RhoA counter-screen in the wet lab.
