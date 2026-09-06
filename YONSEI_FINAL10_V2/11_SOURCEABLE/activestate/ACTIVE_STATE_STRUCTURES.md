# Active-state PAR2 structures used in the counter-screen

Lane: ACTIVE-STATE COUNTER-SCREEN (Agent 4). Branch `yonsei-final10-v2`.
Everything below was computed in this lane from the deposited coordinates; nothing
is quoted from memory. Regeneration commands are in `ACTIVE_STATE_PROVENANCE.json`.

**Standing caveat.** Nothing in this document, and nothing in this lane, is
evidence that a molecule is an agonist or an antagonist. This lane produces a
structural **warning flag** only.

---

## 1. Structures verified

Four active-state structures were downloaded from RCSB and verified against the
deposited mmCIF metadata. All four are genuinely **human PAR2 (F2RL1, UniProt
P55085)** in a **G-protein-coupled active state**. None was rejected.

| PDB | Title (deposited) | Method | Resolution | Deposited | PAR2 chain | PAR2 residues modelled | Construct mutations in the PAR2 chain |
|---|---|---|---|---|---|---|---|
| **8ZMD** | Protease-activated receptor-2 (PAR2)/Gq complex | cryo-EM | 3.25 Å | 2024-05-23 | R | 37–42, 57–359 | **none** |
| **8ZME** | Protease-activated receptor-2 (PAR2)/miniG13 complex | cryo-EM | 3.20 Å | 2024-05-23 | R | 37–42, 57–180, 186–358 | **none** |
| **9D0A** | CryoEM structure of PAR2 with endogenous tethered ligand | cryo-EM | 3.10 Å | 2024-08-06 | R | 37–39, 62–359 | **none** |
| **9E7R** | CryoEM structure of PAR2 with GB88 | cryo-EM | 3.18 Å | 2024-11-04 | R | 61–356 | **none** |

Resolution source: `_em_3d_reconstruction.resolution` for 8ZMD/8ZME,
`_refine.ls_d_res_high` for 9D0A/9E7R.

### What is bound in each

| PDB | Transducer | Other chains | Orthosteric occupant |
|---|---|---|---|
| 8ZMD | engineered Gαq (chain A, PDB-defined sequence) + Gβ1 `P62873` + Gγ2 `P59768` | — | **endogenous tethered ligand SLIGKV**, residues 37–42, fully modelled |
| 8ZME | engineered G13 / miniG13 (chain A) + Gβ1 + Gγ2 | scFv16 (chain E) | **endogenous tethered ligand SLIGKV**, residues 37–42, fully modelled |
| 9D0A | Gαq/Gαs chimera (`P50148` res 7–197 + `P63092` res 216–394) + Gβ1 + Gγ2 | scFv16 (chain E) | tethered ligand **partially** modelled: only S37-L38-I39; residues 40–61 disordered |
| 9E7R | Gαq chimera + Gβ1 + Gγ2 | scFv16 (chain E) | **GB88**, PDB chemical component `A1BF3`, 40 heavy atoms, resolved in the pocket. No tethered ligand modelled (chain R starts at 61) |

The tethered-ligand sequence was read off the coordinates, not assumed:
chain R begins at Ser37, the residue exposed by cleavage after Arg36, and the
first six modelled residues of 8ZMD and 8ZME are **S-L-I-G-K-V**.

### Why 8ZME matters most for this project

The dangerous failure mode is a Gq-antagonist that is a **G12/13-agonist**.
**8ZME is PAR2 bound to miniG13** — the receptor conformation that couples to the
pathway we are most afraid of. 8ZMD is the matched Gq complex. Having both, at
comparable resolution and from the same deposition, is the closest structural
handle this project can get on that failure mode.

### 9E7R was added as the permitted extra structure

9E7R was not in the original target list. It was verified to the same standard and
added because it is **PAR2 in complex with GB88, the biased-agonist counter-control
itself**, with GB88's pose experimentally resolved. This converts "GB88-like
contact similarity" from a docking-derived guess into a measurement against a
crystallographic reference. Its ligand `A1BF3` is defined as the **(2S,3S)**
diastereomer.

> **Flag for the wider project.** IUPHAR/GtoPdb ligand 6658 and PubChem CID
> 73755230, both labelled "GB88", depict the **(2S,3R)** *allo*-isoleucine
> diastereomer. The experimental structure and CAS 1416435-96-5 / CHEMBL2431617
> give (2S,3S). This lane used the **(2S,3S)** form from the structure. Any
> earlier work in this repository that pulled GB88 by bare name from GtoPdb may
> be carrying the wrong diastereomer.

---

## 2. The inactive receptors are thermostabilised; the active ones are not

The campaign's inactive receptors come from 5NDD (2.80 Å) and 5NDZ (3.60 Å),
both X-ray structures of a **thermostabilised** PAR2 fusion construct
(T4 lysozyme + soluble cytochrome b562, residues numbered ≥1000 and ≥2000).
Both carry the same **ten engineered mutations** in the PAR2 chain:

`G89A · H108A · G157A · M166L · Y174A · V176E · N222Q · M268A · I289A · L293A`

The four active-state structures are **wild-type** across the modelled region.
Cα superposition confirms these ten positions are the *only* residue-identity
differences over the 289–295 commonly modelled residues.

This has two consequences, both recorded here rather than smoothed over:

1. **The orthosteric comparison is clean.** Of the 17 residues within 5 Å of
   AZ8838 in 5NDD, **zero** differ between the thermostabilised construct and the
   wild-type active structures.
2. **The allosteric comparison is mildly confounded.** Of the 13 residues within
   5 Å of AZ3451 in 5NDZ, **one** differs: **residue 157 is ALA in 5NDZ (the
   G157A thermostabilising mutation) and GLY in all four active structures**, and
   it sits **3.24 Å** from AZ3451. Any 5NDZ-vs-active difference at the allosteric
   site carries this sequence difference inside it. Allosteric results in this
   lane are reported with that caveat attached.

Separately: `Ala157` is also the residue behind campaign defect 6 (the dead
`GLY:157` key in the 5NDZ profile). It is ALA in the crystal because of the
engineered mutation, and GLY in the real receptor.

---

## 3. Structural alignment

Superposition is Kabsch on **Cα atoms of PAR2 residues 59–359 only** (fusion
partners at ≥1000 excluded). Two transforms were computed per pair:

* **GLOBAL** — every commonly modelled Cα.
* **POCKET-LOCAL** — the commonly modelled Cα of residues with any heavy atom
  within 8 Å of the crystallographic ligand. **Box mapping uses this transform**,
  because box placement is set by the local pocket frame, not by the TM6 swing
  that dominates the inactive→active global RMSD.

### Alignment onto 5NDD (orthosteric frame), 52 pocket-lining residues

| Active | common Cα | global Cα RMSD | pocket Cα | pocket-local Cα RMSD | global-vs-local box-centre disagreement |
|---|---|---|---|---|---|
| 9D0A | 292 | 2.315 Å | 52 | **1.045 Å** | 0.305 Å |
| 8ZMD | 295 | 2.529 Å | 52 | **1.145 Å** | 0.827 Å |
| 8ZME | 289 | 2.465 Å | 52 | **1.230 Å** | 0.838 Å |
| 9E7R | 290 | 2.064 Å | 52 | **0.993 Å** | 0.328 Å |

### Alignment onto 5NDZ (allosteric frame), 42 pocket-lining residues

| Active | common Cα | global Cα RMSD | pocket Cα | pocket-local Cα RMSD | disagreement |
|---|---|---|---|---|---|
| 9D0A | 292 | 2.304 Å | 42 | **0.929 Å** | 0.462 Å |
| 8ZMD | 295 | 2.498 Å | 42 | **0.863 Å** | 0.792 Å |
| 8ZME | 289 | 2.446 Å | 42 | **0.924 Å** | 0.789 Å |
| 9E7R | 290 | 2.046 Å | 42 | **0.876 Å** | 0.351 Å |

Global RMSD of 2.0–2.5 Å is the expected inactive→active difference for a class-A
GPCR. Pocket-local RMSD of 0.86–1.23 Å means the pocket frames themselves
correspond well, and the two independent transforms place the box centre within
0.31–0.84 Å of each other — i.e. the box mapping does not depend on which
superposition is used.

### Residue correspondence

Numbering is **identical** between the inactive and active structures (both use
UniProt P55085 numbering), so correspondence is the identity map, verified
residue by residue.

**Orthosteric pocket** (17 residues within 5 Å of AZ8838 in 5NDD) — all identical
in 9D0A / 8ZMD / 8ZME / 9E7R:

`LEU78 · TYR82 · LYS131 · TYR134 · HIS135 · TRP141 · LEU151 · ILE152 · PHE155 ·
TYR156 · CYS226 · HIS227 · ASP228 · TYR326 · ILE327 · LEU330 · CYS331`

**Allosteric pocket** (13 residues within 5 Å of AZ3451 in 5NDZ) — 12 identical,
one differs:

`LEU119 · ALA120 · LEU123 · SER124 · PHE154 · **ALA157→GLY157** · ASN158 ·
CYS161 · TRP199 · ILE202 · LEU203 · TYR210 · VAL211`

Full per-residue table: `work/residue_correspondence.json`.

---

## 4. Box mapping

The campaign's box rule was **re-derived, not assumed**:

> centre = crystal-ligand heavy-atom **centroid**;
> size = crystal-ligand heavy-atom axis-aligned **extent + 10.0 Å** per axis.

Recomputing it from the crystallographic ligands reproduces both committed
configs to **4.7 × 10⁻⁴ Å** (5NDD) and **2.9 × 10⁻⁴ Å** (5NDZ). The same rule was
then applied to define the new boxes. **No box centre was chosen by eye.**

| Box | State | Origin |
|---|---|---|
| `5NDD__ORTHO` | inactive | committed campaign config, unchanged |
| `5NDZ__ALLO` | inactive | committed campaign config, unchanged |
| `<ACTIVE>__ORTHO` | active | 5NDD box moved through the pocket-local transform |
| `<ACTIVE>__ALLO` | active | 5NDZ box moved through the pocket-local transform |
| `<ACTIVE>__TL` | active | campaign box rule applied to that structure's own modelled tethered ligand |
| `9E7R__GB88` | active | campaign box rule applied to the crystallographic GB88 pose (`A1BF3`) |

14 boxes total. Values in `configs/*.conf` and `work/boxes.json`.

### Box sanity checks

Mapping the crystal ligand itself through the transform puts **94.7–100 %** of its
heavy atoms inside the corresponding mapped box, with median clearance to the
active receptor of 2.4–4.1 Å — i.e. **both pockets are physically present and open
in the active state**, not collapsed. No fusion-partner atom lies inside either
inactive box.

---

## 5. The finding that reframes this lane

The AZ8838 "orthosteric" antagonist pocket and the tethered-ligand / GB88 site are
**two distinct, non-overlapping sites**, separated by a thin wall.

Measured in the 9E7R frame (8ZMD's SLIGKV mapped in via a 52-Cα pocket-local
superposition, RMSD 0.831 Å):

| Pair | centroid separation | closest atom pair | atoms of the first within 2.0 Å of the second |
|---|---|---|---|
| crystallographic GB88 vs **mapped SLIGKV tethered ligand** | **3.17 Å** | **0.09 Å** | **80.0 %** |
| crystallographic GB88 vs mapped AZ8838 pose | 13.99 Å | 7.76 Å | 0.0 % |
| mapped AZ8838 vs mapped SLIGKV tethered ligand | 16.87 Å | 7.05 Å | 0.0 % |

Residue-contact sets (heavy atom within 4.5 Å), Jaccard similarity:

| Pair | Jaccard |
|---|---|
| GB88 vs tethered ligand | **0.727** (16 shared residues) |
| GB88 vs AZ8838 site | 0.086 (only HIS227, ASP228, TYR323) |
| AZ8838 site vs tethered ligand | 0.103 |

* **GB88 occupies the tethered ligand's volume** — 80 % of its heavy atoms sit
  within 2.0 Å of a tethered-ligand atom, 97.5 % within 4.0 Å.
* **GB88 does not touch the AZ8838 pocket at all.**
* The two sites share only HIS227 / ASP228 / TYR323, the wall between them.

Contact residues:

* GB88 (crystallographic): `V61 S65 V68 L69 I216 F217 I218 H227 D228 V229 L230
  P231 E232 L235 H310 Y311 I314 G318 S320 H321 Y323 A324`
* AZ8838 site (mapped): `L78 Y82 K131 Y134 H135 W141 L151 I152 F155 Y156 C226
  H227 D228 Y323 I327 L330`

**Consequence for the campaign.** A molecule that binds the AZ8838 pocket is, by
geometry, *not* occupying the tethered-ligand/GB88 site — the two are 17 Å apart.
That is a structural argument that AZ8838-pocket binders carry low GB88-mimicry
risk. It is *not* an argument that they are antagonists: an allosteric ligand 17 Å
away can still bias transducer coupling, and only a functional assay can settle
that.

---

## 5b. Pocket cavity volume — measured, and found unusable for the orthosteric site

A 0.5 Å grid cavity volume was computed for every receptor-box (1.4 Å probe;
a point counts only if it is also buried, ≥15 of 26 rays striking protein within
10 Å). The largest cavity component containing the box centre is reported.

| Box | State | Central cavity (Å³) |
|---|---|---|
| `5NDD__ORTHO` | inactive | **103.2** |
| `9D0A__ORTHO` | active | 15.1 |
| `8ZMD__ORTHO` | active | 173.4 |
| `8ZME__ORTHO` | active | 224.8 |
| `9E7R__ORTHO` | active | 56.9 |
| `5NDZ__ALLO` | inactive | **56.9** |
| `9D0A__ALLO` | active | 67.8 |
| `8ZMD__ALLO` | active | 52.4 |
| `8ZME__ALLO` | active | 63.8 |
| `9E7R__ALLO` | active | 42.1 |
| `9D0A__TL` | active | 170.8 |
| `8ZMD__TL` | active | 457.8 |
| `8ZME__TL` | active | 442.1 |
| `9E7R__GB88` | active | 192.4 |

**What this does and does not support.**

* **Usable conclusion — both crystallographic pockets physically exist in the
  active state.** No mapped box is solid protein; every one contains a buried
  cavity. Combined with the box check in §4 (94.7–100 % of the mapped crystal
  ligand inside the box, median clearance 2.4–4.1 Å), the counter-screen is
  docking into real sites, not walls.
* **Usable conclusion — the allosteric pocket is state-independent.** Across four
  active structures it spans 42.1–67.8 Å³ against 56.9 Å³ inactive: the inactive
  value sits inside the active range. This agrees with the side-chain measurement
  in §5c (median shift 0.9–1.6 Å, only ASN158 moving ≥4 Å).
* **NOT usable — the orthosteric pocket.** The four active structures span
  **15.1 to 224.8 Å³, a 15-fold range within a single receptor state.** That
  spread is far larger than the inactive-versus-active difference the measurement
  was meant to detect. At 3.10–3.25 Å cryo-EM resolution, side-chain rotamers in
  a buried pocket are not determined well enough to support a cavity-volume
  comparison. **This channel is therefore reported as inconclusive for the
  orthosteric site and is not used by the classification rule.**

Reading a pocket collapse out of 9D0A (15.1 Å³) or a pocket opening out of 8ZME
(224.8 Å³) would be reading modelling noise. Both readings are available in the
same data, which is the reason to discard the channel rather than pick one.

---

## 5c. How much the pockets move between states

Per-residue displacement of the pocket residues after the same pocket-local Cα
superposition used for box mapping (`work/pocket_shift.json`):

| Pocket | Structure | residues | median side-chain max shift | 90th pct | max |
|---|---|---|---|---|---|
| ORTHO | 9D0A | 17 | 2.69 Å | 4.63 Å | 5.15 Å |
| ORTHO | 8ZMD | 17 | 2.33 Å | 4.30 Å | 4.82 Å |
| ORTHO | 8ZME | 17 | 1.67 Å | 4.87 Å | 5.87 Å |
| ORTHO | 9E7R | 17 | 2.62 Å | 4.00 Å | 5.06 Å |
| ALLO | 9D0A | 13 | 1.28 Å | 2.40 Å | 3.24 Å |
| ALLO | 8ZMD | 13 | 1.62 Å | 3.34 Å | 6.20 Å |
| ALLO | 8ZME | 13 | 1.56 Å | 3.31 Å | 5.67 Å |
| ALLO | 9E7R | 13 | 0.92 Å | 3.31 Å | 6.86 Å |

Residues moving ≥4.0 Å in at least one active structure:

* **ORTHO — six residues: LYS131, PHE155, HIS227, TYR326, ILE327, LEU330.**
* **ALLO — one residue: ASN158.**

The orthosteric pocket is substantially remodelled on activation and the
allosteric pocket is not. This is a **direction**, not a magnitude: the six
moving residues are the same ones whose rotamers are least reliable at this
resolution, which is why §5b's volume numbers scatter.

---

## 6. Activation microswitches — identified, then mostly ruled out

Class-A activation microswitches were located **in PAR2's own numbering** by motif
match on the modelled 8ZMD chain-R sequence. All five expected motifs were found
and matched exactly:

| Motif | PAR2 residues | Observed | Note |
|---|---|---|---|
| TM2 Na⁺ pocket (D2.50) | 120–122 | `ADL` | **D121** is the sodium-pocket aspartate |
| TM3 D(E)RY (3.49–3.51) | 172–174 | `QRY` | PAR2 carries **Q** at 3.49 |
| TM5 P5.50 (PIF connector) | 254 | `P` | |
| TM6 CWxP toggle (6.47–6.50) | 299–302 | `CFTP` | PAR2 carries **F300** at the 6.48 toggle, not Trp |
| TM7 NPxxY (7.49–7.53) | 340–344 | `DPFVY` | PAR2 carries **D** at 7.49 |

The distances then decide whether any of them is usable as ligand evidence.
Minimum heavy-atom distance in 8ZMD, to the mapped AZ8838 site, the mapped AZ3451
site, and the modelled SLIGKV tethered ligand:

| Residue | Motif | d(AZ8838 site) | d(AZ3451 site) | d(tethered ligand) |
|---|---|---|---|---|
| ALA120 | Na⁺ pocket | 13.43 | **3.76** | 21.22 |
| ASP121 | Na⁺ pocket (D2.50) | 13.63 | **5.78** | 21.28 |
| LEU122 | Na⁺ pocket | 14.25 | 6.46 | 22.64 |
| GLN172 | DRY-equivalent | 29.81 | 19.07 | 34.28 |
| ARG173 | DRY-equivalent | 28.30 | 19.79 | 33.38 |
| TYR174 | DRY-equivalent | 32.83 | 24.01 | 36.47 |
| PRO254 | P5.50 | 20.45 | 15.19 | 22.54 |
| CYS299 | CWxP | 13.10 | 15.94 | 16.65 |
| PHE300 | CWxP toggle | 13.17 | 12.04 | 15.36 |
| THR301 | CWxP | 15.22 | 18.57 | 15.32 |
| PRO302 | CWxP | 12.69 | 20.21 | 12.85 |
| ASP340 | NPxxY-equivalent | 17.56 | 11.93 | 23.52 |
| PRO341 | NPxxY-equivalent | 20.21 | 14.41 | 26.96 |
| PHE342 | NPxxY-equivalent | 22.68 | 18.13 | 29.98 |
| VAL343 | NPxxY-equivalent | 24.13 | 19.27 | 29.68 |
| TYR344 | NPxxY-equivalent | 22.50 | 15.90 | 27.73 |

With a 6.0 Å reach cutoff:

* **USABLE: ALA120 and ASP121 only, and only from the allosteric (AZ3451) site.**
* **EXCLUDED (out of reach of every site): the other 14 residues** — the entire
  DRY-equivalent, the entire NPxxY-equivalent, the entire CWxP toggle, and P5.50.

**Therefore the "microswitch-compatible contacts" evidence channel is not
measurable for the orthosteric pocket or for the tethered-ligand site.** No ligand
placed in either can contact any conserved activation microswitch — the nearest is
12.7 Å away. It is measurable only for the allosteric NAM pocket, where a ligand
can reach D2.50.

This is the *exact* failure that retired the earlier agonist-mimicry flag
(HANDOFF defect 5: two of its three residues sat 8.7 Å and 10.6 Å from the
ligand). The channel is therefore reported as **MISSING** for orthosteric and
tethered-ligand poses — never as zero — and the classification does not depend on
it.

---

## 7. Receptor preparation

All six receptors (5NDD, 5NDZ, 9D0A, 8ZMD, 8ZME, 9E7R) were prepared identically.

1. **Chain extraction.** For the active structures: chain R only, protein
   residues, alternative conformations and hydrogens removed, ligands and waters
   removed. Two variants kept — `*_holo.pdb` (tethered ligand retained, used for
   geometry) and `*_apo.pdb` (tethered-ligand residues removed, used as the
   docking receptor, so the pocket is genuinely empty and the overlap measurement
   is not circular). For the inactive receptors the campaign's committed
   `01_REFERENCE_POCKETS/receptors/*_clean.pdb` files were used unchanged.
2. **pH 7.4 protonation** with `obabel -p 7.4` — **`-h` is never passed**;
   the campaign's own audit (defect 2) showed `-h` overrides the pH model and
   leaves all lysines neutral.
3. **Numbering transplant** with the campaign's
   `scripts/v2_fix_receptor_protonation.py`, because `-p` alone renumbers every
   residue.
4. **Docking receptor**: `obabel <apo>.pdb -O <id>_receptor.pdbqt -xr`.

### Verification

Every receptor passes the protonation check with **0.000000 Å** heavy-atom shift:

| Receptor | heavy atoms | H added | Lys⁺ (3 H on NZ) | protonated Asp | protonated Glu | pH 7.4 state |
|---|---|---|---|---|---|---|
| 5NDD | 4498 | 4610 | 39 / 39 | 0 / 29 | 0 / 23 | correct |
| 5NDZ | 4421 | 4547 | 39 / 39 | 0 / 29 | 0 / 23 | correct |
| 9D0A | 2358 | 2456 | 13 / 13 | 0 | 0 | correct |
| 8ZMD | 2359 | 2449 | 9 / 9 | 0 | 0 | correct |
| 8ZME | 2297 | 2389 | 5 / 5 | 0 | 0 | correct |
| 9E7R | 2349 | 2448 | 12 / 12 | 0 | 0 | correct |

The 5NDD row reproduces the campaign's own `5NDD_orthosteric_receptor_pH74_FIXED.pdb`
exactly (4498 heavy atoms, 4610 hydrogens, 39/39 Lys⁺).

The re-prepared 5NDD PDBQT reproduces the committed historical PDBQT **exactly** —
4498 atoms with an identical AutoDock type distribution (2558 C, 800 OA, 733 NA,
369 A, 20 S, 18 N). The active receptors are therefore on the same docking footing
as the campaign's inactive one.

### A live defect found in passing

`scripts/v2_interactions.py`, which computes `max_ifp_recovery` for the whole
campaign, points at `02_REFERENCE_VALIDATION_REPAIRED/*_protonated_pH74.pdb`.
Those files are the **broken** `obabel -h -p 7.4` output, verified here:

| File | Lys⁺ | protonated Asp | protonated Glu |
|---|---|---|---|
| `5NDD_orthosteric_receptor_protonated_pH74.pdb` (used by `v2_interactions.py`) | **0 / 39** | **17 / 29** | **10 / 23** |
| `5NDD_orthosteric_receptor_pH74_FIXED.pdb` (the repair) | 39 / 39 | 0 / 29 | 0 / 23 |

`REFERENCE_IFP_REPAIRED.json` still records the Open Babel warning
"Both -p and -h options are set… hydrogens will be added without considering pH",
so the crystal reference keys were computed on the broken receptor too. The
campaign's IFP recovery is therefore *internally* consistent (reference and poses
share the same receptor) but cannot detect a salt bridge anywhere.

**This lane uses the corrected `*_pH74_FIXED.pdb` receptors throughout** and
recomputes its own crystal reference. Recomputing AZ8838's crystal fingerprint on
the corrected receptor independently reproduces the effect the handoff describes
(defect 4): the HIS135 hydrogen bond disappears and a HIS227 π-cation appears.

---

## 8. Crystallographic reference fingerprints (this lane)

ProLIF 2.2.1, computed against the pH-7.4-**correct** receptors.

| Reference | Keys | Composition |
|---|---|---|
| **5NDD / AZ8838** | 16 | 10 VdW, 4 hydrophobic, 1 π-cation (HIS227), 1 HB donor (TYR82) |
| **5NDZ / AZ3451** | 12 | 8 VdW, 4 hydrophobic, 0 H-bond |
| **9E7R / GB88** | 14 | 12 VdW, 2 hydrophobic, 1 HB acceptor (LEU230) |

GB88's bond orders were assigned from the independently verified SMILES; the
resulting InChIKey `DCUDDCGUKZLQLN-MCOVPRHSSA-N` matches the template exactly.

Keys are in `work/reference_ifp.json`.

---

## 9. Files

| Path (relative to this directory) | Contents |
|---|---|
| `structures/*.cif` | the six deposited mmCIF files, SHA-256 in the provenance JSON |
| `receptors/*_PAR2_{holo,apo,tethered}.pdb` | extracted PAR2 chains |
| `receptors/*_receptor_pH74_FIXED.pdb` | pH 7.4 receptors for interaction fingerprinting |
| `receptors/*_receptor.pdbqt` | docking receptors |
| `ligands/9E7R_GB88_crystal.pdb` | the experimental GB88 pose |
| `configs/*.conf` | the 14 docking boxes |
| `work/alignment.json` | transforms, RMSDs, mapped box centres |
| `work/boxes.json` | box definitions and the box-rule verification |
| `work/residue_correspondence.json` | full inactive↔active residue table |
| `work/microswitch.json` | motif identification and the reach measurement |
| `work/reference_ifp.json` | the three crystallographic reference fingerprints |
| `work/site_geometry.json` | GB88 / AZ8838 / tethered-ligand site comparison |
