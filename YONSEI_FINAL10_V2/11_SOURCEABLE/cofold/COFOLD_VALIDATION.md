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

---

# Control panel result — co-fold consistency is a real discriminator

Run on `a100-40`, 6 controls × 3 seeds × 5 diffusion samples, identical
settings. Combined with batch 1:

| molecule | role | confidence | ligand ipTM | binder prob | pocket occ. | **sample consistency (Å)** |
|---|---|---:|---:|---:|---:|---:|
| AZ8838 | 5NDD crystal antagonist | 0.956 | 0.979 | 0.591 | 0.94 | **0.74** |
| propranolol | repurposing probe | 0.954 | 0.984 | 0.663 | 0.76 | **0.70** |
| AZ3451 | 5NDZ crystal NAM | 0.951 | 0.967 | 0.654 | 0.85 | **0.82** |
| DL13973 | de novo | 0.948 | 0.962 | 0.533 | 0.94 | 1.22 |
| DL11051 | de novo | 0.941 | 0.971 | 0.631 | 0.94 | 1.44 |
| DL13943 | de novo | 0.940 | 0.964 | 0.551 | 0.82 | 1.22 |
| DL13271 | de novo | 0.939 | 0.964 | 0.375 | 1.00 | 1.16 |
| **GB83** | contested antagonist | 0.938 | 0.943 | 0.481 | 1.00 | **3.20** |
| **GB110** | **agonist** | 0.926 | 0.967 | 0.331 | 1.00 | **3.21** |
| DL11368 | de novo | 0.923 | 0.972 | 0.468 | 1.00 | 1.70 |
| **GB88** | **biased agonist** | 0.918 | 0.942 | 0.346 | 1.00 | **2.65** |
| **GB88 allo-Ile** | wrong-stereoisomer control | 0.914 | 0.907 | 0.328 | 1.00 | **2.38** |
| K-14585 | peptidomimetic, MW 916 | 0.870 | 0.871 | 0.268 | 1.00 | 1.65 |

## What separates the classes

**Confidence does not separate them.** Every molecule scores 0.87–0.96, and
GB110 — a confirmed *agonist* — scores 0.926, above two de novo designs. Nor
does pocket occupancy: the GB-series all reach 1.00 simply by being large
enough to touch every constrained residue. **Neither should be used alone.**

**Sample-to-sample consistency does separate them**, cleanly:

- crystallographic orthosteric binders and propranolol: **0.70–0.82 Å**
- de novo designs: **1.16–1.70 Å**
- the GB-series peptidomimetics: **2.38–3.21 Å**

The GB-series does not settle into a reproducible pose in this pocket. Across
independent seeds and diffusion samples it lands differently every time.

## Why that is the expected answer, from independent evidence

The active-state lane established crystallographically (PDB **9E7R**, PAR2/GB88)
that **GB88 binds at the tethered-ligand site, ~17 Å from the AZ8838 pocket,
overlapping the tethered ligand at 80% of its heavy atoms and the AZ8838 pocket
at 0%.** GB88 has no business in the orthosteric pocket, and when the constraint
forces it there it cannot converge.

Two independent methods — a crystal structure and a co-folding consistency
measurement — agree. That is the strongest internal validation this lane has.

## Consequences for the ranking

1. **Sample consistency is weighted, confidence is not trusted alone.** In the
   final ranking the co-folding family gives 30% to pocket occupancy, 25% to
   GNINA/co-fold pose convergence, 20% to sample consistency and only 15% to
   confidence.
2. **The Boltz affinity head is demoted to 10% of that family** (~2% of the
   final score). It ranks GB88 (`-0.935`) and GB110 (`-0.655`) as *better*
   binders than AZ8838 (`+0.789`) — i.e. it scores a confirmed agonist above the
   crystallographic antagonist. It cannot be trusted for direction.
3. **The two GB88 stereoisomers are nearly indistinguishable here** (2.65 vs
   2.38 Å, confidence 0.918 vs 0.914). Co-folding does **not** resolve which
   stereoisomer to buy. That has to come from the literature and the vendor
   record, where the published (2S,3S) L-Ile form is the one with 30 vendor
   leads.
4. **Propranolol co-folds as well as the crystal ligand** — the best ligand ipTM
   in the whole set (0.984), consistency 0.70 Å, binder probability above
   AZ8838's. This is consistent with its previously noted crystal-IFP recovery
   of 0.938, and supports keeping it in the reference panel as a cheap,
   already-approved probe. It is **not** evidence that it antagonises PAR2.
