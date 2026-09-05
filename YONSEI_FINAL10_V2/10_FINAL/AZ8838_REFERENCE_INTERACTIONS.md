# The AZ8838 reference interactions, and which anchor definition the ranking should use

Independent recomputation from the prepared structure files, not a reading of
`REFERENCE_IFP_REPAIRED.json`. Every number below was produced on this Mac with
`/Users/moheet/Documents/ChatGPT/PAR2/.venv-v2/bin/python` (ProLIF 2.2.1, RDKit
2026.03.6, pandas 3.0.5, NumPy 2.5.2) and is reproducible with the commands in
[§9](#9-what-was-actually-run).

---

## 1. The finding in one paragraph

`v2_consensus_rank.py` ranks 5NDD designs against
`anchor_residues = ["ASP:228", "HIS:135"]`. The repaired crystallographic
complex makes its two hydrogen bonds to **TYR:82** and **HIS:135**.
`FINAL_CANDIDATES.md` line 21 states both facts in consecutive sentences without
noticing they disagree. The recount below shows the two definitions select
populations that are **95% disjoint**: 62 designs under the old definition, 81
under the crystallographic one, and only **7 in common**. The previous ranking
did not get one anchor wrong in a mild way — it got **one of the two anchors
wrong outright**, and it was the *stronger* of the two: TYR:82 is the shortest
polar contact in the entire pocket at 2.475 Å.

But the honest answer is not simply "swap ASP:228 for TYR:82". ASP:228 is a real
polar contact at 2.929 Å, and whether ProLIF calls it a hydrogen bond depends on
a hydrogen atom the crystal structure does not resolve ([§4](#4-the-crux-asp228-and-the-imidazole-protomer)).
The recommendation in [§8](#8-recommendation) reflects that.

---

## 2. What the crystal complex actually shows — 5NDD / AZ8838

Inputs, both read directly:

- `02_REFERENCE_VALIDATION_REPAIRED/5NDD_AZ8838_corrected_protonated_ligand.sdf`
  — 17 heavy atoms + 15 H, `CCCc1cc(F)ccc1[C@H](O)c1ncc[nH]1`,
  InChIKey `IDFPQEHZYBXIFO-LBPRGKRZSA-N` (matches wwPDB 8TZ).
- `02_REFERENCE_VALIDATION_REPAIRED/5NDD_orthosteric_receptor_protonated_pH74.pdb`

The full ProLIF fingerprint is **16 interaction occurrences over 16 unique
`residue|interaction` keys**. This reproduces
`REFERENCE_IFP_REPAIRED.json → systems.5NDD_AZ8838.reference_fingerprint_keys`
exactly, key for key.

### 2.1 Hydrogen bonds — exactly two, both ligand-as-donor

| Residue | Type | D···A distance | D–H···A angle | Donor |
|---|---|---:|---:|---|
| **TYR:82:A** | HBDonor | **2.475 Å** | **153.933°** | ligand imidazole N1–H ··· TYR:82 OH |
| **HIS:135:A** | HBDonor | **2.630 Å** | **138.878°** | ligand hydroxyl O2–H ··· HIS:135 NE2 |

There are **no** HBAcceptor terms, no PiStacking, no Cationic/Anionic, no
CationPi. The interaction set searched was the full ProLIF default: `Anionic,
CationPi, Cationic, HBAcceptor, HBDonor, Hydrophobic, PiCation, PiStacking,
VdWContact`.

Two supporting facts, measured from the receptor file, explain the direction of
both bonds:

- **HIS:135 is the ND1–H tautomer.** NE2 carries no hydrogen, so it can only
  accept. This is why HIS:135 is an H-bond under *every* ligand protomer tested.
- **TYR:82's hydroxyl proton points away from the ligand** — the O–H···N1 angle
  is 62.8°, and the H is 2.759 Å from N1, *further* than the O···N1 distance of
  2.475 Å. TYR:82 therefore cannot donate in this model, so the ligand does. Note
  that a tyrosine hydroxyl torsion is freely rotatable and was placed by Open
  Babel, not observed; this direction is a modelling artefact, not a measurement.

### 2.2 The other fourteen keys

| Type | Residues |
|---|---|
| Hydrophobic (4) | ILE:152 (4.016 Å), PHE:155 (4.396 Å), CYS:226 (4.489 Å), HIS:227 (3.500 Å) |
| VdWContact (10) | TYR:82 (2.475), LYS:131 (3.065), TYR:134 (2.726), HIS:135 (2.630), TRP:141 (2.640), ILE:152 (2.430), PHE:155 (3.138), CYS:226 (2.408), **ASP:228 (2.929)**, ILE:327 (3.129) |

**Only 2 of the 16 reference keys are hydrogen bonds.** Any recovery figure
computed over all 16 keys is therefore dominated by contact terms that nearly
every pose filling the box reproduces — see the threshold table in [§6](#6-the-recount).

### 2.3 The pre-repair fingerprint, for comparison

Refingerprinting the original `01_REFERENCE_POCKETS/` ligand and receptor (no
hydrogens on either) gives **10 keys and 0 hydrogen bonds**, confirming Defect 2
of `04_VERIFICATION/REFERENCE_MODEL_DEFECTS.md`. One inconsistency worth
recording: that document's table reports condition A as 10 interactions, while
`REFERENCE_IFP_REPAIRED.json → conditions.A_as_committed` records 8. My
recomputation gives 10. The difference is two `Hydrophobic` keys (ILE:152,
PHE:155) that appear or not depending on whether the ligand is sanitised on
read. Both agree on the load-bearing point — zero hydrogen bonds — so this is a
bookkeeping discrepancy, not a scientific one.

---

## 3. The contact shell, computed without ProLIF

Minimum heavy-atom distance from every receptor residue to any ligand heavy
atom, straight from coordinates. **14 residues within 4.0 Å; 17 within 5.0 Å.**

| Residue | min dist (Å) | rec. heavy atoms ≤4 Å | ≤5 Å | min polar–polar (Å) | ProLIF term |
|---|---:|---:|---:|---:|---|
| TYR:82 | 2.475 | 7 | 21 | **2.475** | HBDonor, VdW |
| HIS:135 | 2.630 | 7 | 16 | **2.630** | HBDonor, VdW |
| ASP:228 | 2.929 | 5 | 20 | **2.929** | VdW only |
| LYS:131 | 3.065 | 2 | 19 | 4.067 | VdW |
| ILE:327 | 3.129 | 9 | 21 | 4.347 | VdW |
| PHE:155 | 3.138 | 12 | 30 | 9.802 | Hydrophobic, VdW |
| CYS:226 | 3.447 | 4 | 15 | 5.944 | Hydrophobic, VdW |
| ILE:152 | 3.467 | 3 | 15 | 8.682 | Hydrophobic, VdW |
| HIS:227 | 3.500 | 14 | 46 | 4.463 | Hydrophobic |
| TRP:141 | 3.536 | 2 | 5 | 10.741 | VdW |
| TYR:134 | 3.566 | 3 | 15 | 6.717 | VdW |
| TYR:156 | 3.604 | 2 | 6 | 7.753 | *(none)* |
| LEU:330 | 3.629 | 4 | 21 | 5.036 | *(none)* |
| LEU:78 | 3.850 | 2 | 9 | 7.457 | *(none)* |
| CYS:331 | 4.037 | 0 | 6 | 4.577 | *(none)* |
| LEU:151 | 4.201 | 0 | 5 | 8.361 | *(none)* |
| TYR:326 | 4.810 | 0 | 1 | 5.898 | *(none)* |

**Exactly three residues have a polar heavy-atom pair inside hydrogen-bonding
distance: TYR:82 (2.475), HIS:135 (2.630) and ASP:228 (2.929).** Nothing else
comes closer than 4.067 Å. That geometric fact is protomer-independent and is
the firmest thing in this report.

---

## 4. The crux: ASP:228 and the imidazole protomer

ASP:228 OD1 sits 2.929 Å from ligand N4 — the second imidazole nitrogen. That is
squarely an H-bond distance. ProLIF nonetheless scores only `VdWContact`, and
the reason is unambiguous once the hydrogens are inspected:

- ASP:228 **OD1 carries no hydrogen** (its OD2 does — see [§5](#5-a-second-defect-the-receptor-is-not-protonated-at-ph-74)), so OD1 can only accept.
- ligand **N4 carries no hydrogen** in the tautomer as built, so it can only accept.

Acceptor–acceptor. No hydrogen bond is possible, and ProLIF is right to refuse
one. **This is not a bug and ASP:228 must not be forced into the fingerprint.**

But the N–H that decides this was *placed*, not observed. AZ8838's 2-substituted
imidazole has two neutral tautomers and a pKa-accessible imidazolium.
`v2_reference_ifp_repair.py` fixes the placement through
`AllChem.AssignBondOrdersFromTemplate(Chem.MolFromSmiles("...c1[nH]ccn1"), raw)`,
which resolves it by substructure match — arbitrarily with respect to the pocket.

Building all three protomers on **identical crystallographic heavy-atom
coordinates** and refingerprinting each:

| Protomer | Formal charge | Hydrogen bonds detected | Keys |
|---|---:|---|---:|
| **T1** N–H on N1 *(as built by the repair script)* | 0 | TYR:82 (2.475, 153.9°) · HIS:135 (2.630, 138.9°) | 16 |
| **T2** N–H on N4 *(the other neutral tautomer)* | 0 | **ASP:228 (2.929, 140.7°)** · HIS:135 (2.630, 138.9°) | 16 |
| **T3** imidazolium, both N–H | +1 | TYR:82 · **ASP:228** · HIS:135 | 17 |

All three protomers share the same InChIKey (`IDFPQEHZYBXIFO-LBPRGKRZSA-N` for
the neutral pair — InChI normalises mobile imidazole hydrogens), so the existing
InChIKey regression gate in `check_reference_tautomers.py` cannot distinguish
them. It would pass on all of them.

### What this means

1. **HIS:135 is the only protomer-robust hydrogen bond.** It survives every
   protonation choice. It is the single most defensible polar requirement.
2. **TYR:82 and ASP:228 are symmetric on the available evidence.** Each is a
   sub-3 Å polar contact; each is a hydrogen bond under some accessible protomer
   and not under others. There is no basis in these files for keeping one and
   discarding the other — which is precisely what the old definition did, in the
   direction that discarded the *shorter* contact.
3. The old definition was therefore not wrong to name ASP:228. It was wrong to
   **omit TYR:82**, and wrong to present the resulting pair as the
   crystallographic signature when the file it cites says otherwise.

---

## 5. A second defect: the receptor is not protonated at pH 7.4

New finding, not recorded in `REFERENCE_MODEL_DEFECTS.md`. The file is named
`5NDD_orthosteric_receptor_protonated_pH74.pdb`, but Open Babel's own warning —
already stored verbatim in `REFERENCE_IFP_REPAIRED.json` — says the pH was
ignored:

> "Both -p and -h options are set. All implicit hydrogens (-h) will be added
> without considering pH."

Counting hydrogens on the ionisable side chains of the prepared 5NDD receptor
confirms it:

| Side chain | Probe atom | Observed | Expected at pH 7.4 | Correct |
|---|---|---|---|---:|
| LYS | NZ | all 39 have 2 H (neutral amine) | 3 H (NH₃⁺) | **0 / 39** |
| ASP | OD2 | 17 of 29 protonated (neutral COOH) | 0 H (COO⁻) | **12 / 29** |
| GLU | OE2 | 10 of 23 protonated | 0 H | **13 / 23** |
| ARG | NH1 | 2 H | 2 H | 23 / 23 ✓ |

Consequences for every fingerprint in the campaign, reference and pose alike:

- **No salt bridge can ever be detected.** ProLIF's `Cationic`/`Anionic`
  detectors need formal charges; with neutral Lys and neutral Asp/Glu they
  cannot fire. Both reference fingerprints contain zero ionic terms, and that
  is an artefact rather than a finding.
- **Protonated Asp/Glu become spurious donors** elsewhere in the pocket.
- For ASP:228 specifically the error happens to be harmless at the contact face:
  OD2 got the proton, OD1 faces the ligand and is bare. Had it landed on OD1,
  ASP:228 would have been scored a hydrogen bond and this audit would have
  reached the opposite conclusion for the opposite reason. That fragility is
  itself the argument for the recommendation in [§8](#8-recommendation).

This defect does **not** invalidate the two hydrogen bonds in §2.1 — both are
ligand-donated to neutral acceptors and are unaffected by side-chain ionisation.

---

## 6. The recount

Source: `07_CONSENSUS/DENOVO_EX8_CONSENSUS_ALL.csv`, the `ifp_keys` column,
9,066 rows in `5NDD_orthosteric` (12,341 rows total). Full table in
`ANCHOR_DEFINITION_AUDIT.csv`; per-design terms in `ANCHOR_PER_POSE_TERMS.csv`
(9,066 rows × 69 columns).

**Two cross-checks were run before trusting any of this.** My parser reproduces
both published figures exactly — `anchor_hbond_fraction ≥ 1.0` → **62**
(published 62) and `> 0` → **1,298** (published 1,298) — and my
`CRYSTAL_IFP_RECOVERY` agrees with the stored `max_ifp_recovery` column to
max |Δ| = 0.00e+00 over all 9,066 rows.

### 6.1 Anchor definitions, side by side

| Definition | Designs | % of 9,066 | ∩ old 62 | missed by old | in consensus top-500 | median rank | median crystal recovery |
|---|---:|---:|---:|---:|---:|---:|---:|
| **OLD** — ASP:228 **and** HIS:135 H-bond | **62** | 0.68% | 62 | 0 | 8 | 2,775 | 0.8125 |
| **CRYSTAL** — TYR:82 **and** HIS:135 H-bond | **81** | 0.89% | **7** | **74** | 11 | 2,351 | 0.8750 |
| Any **two** of TYR:82 / HIS:135 / ASP:228 | **171** | 1.89% | 62 | 109 | 23 | — | — |
| **All three** of TYR:82 / HIS:135 / ASP:228 | **7** | 0.08% | 7 | 0 | 1 | 2,541 | 0.9375 |
| HIS:135 alone | 759 | 8.37% | 62 | 697 | 77 | — | — |
| TYR:82 alone | 965 | 10.64% | 7 | 958 | 106 | — | — |
| ASP:228 alone | 601 | 6.63% | 62 | 539 | 51 | — | — |
| Any **one** of the three | 2,147 | 23.68% | 62 | 2,085 | 210 | — | — |

The old and crystallographic populations overlap in **7 designs**. Jaccard index
**0.051**. They are, for practical purposes, different sets of molecules.

Pairwise decomposition of the "any two" population: TYR:82+HIS:135 = 81,
ASP:228+HIS:135 = 62, TYR:82+ASP:228 = 42, all three = 7.

### 6.2 CRYSTAL_IFP_RECOVERY thresholds

| Threshold (of 16 observed keys) | Designs | % | ∩ old 62 |
|---|---:|---:|---:|
| ≥ 0.500 | 8,859 | 97.72% | 62 |
| ≥ 0.625 | 8,145 | 89.84% | 61 |
| ≥ 0.750 | 5,701 | 62.88% | 49 |
| ≥ 0.875 | 1,607 | 17.73% | 28 |
| = 1.000 | **10** | 0.11% | **0** |

Recovery is a weak filter below 0.875 — 98% of the library clears 0.5, because
14 of the 16 keys are contact terms. Note that **none** of the 10 designs
achieving full fingerprint recovery is in the old dual-anchor set.

Exact-key reproduction (ligand-as-donor, matching the crystal direction):
`TYR:82:A|HBDonor` in 942 designs (10.39%), `HIS:135:A|HBDonor` in 756 (8.34%),
both in **79**. The 81 in the table above use residue-level H-bonding in either
direction; the two extra designs satisfy TYR:82 as an acceptor.

---

## 7. Residue classification

Full table with distances, evidence text and library census:
**`AZ8838_REFERENCE_INTERACTIONS.csv`** (34 rows covering both pockets).

Classes: **A** observed crystal H-bond · **B** observed crystal non-H-bond
contact · **C** mutagenesis-supported · **D** FMO/modelling hotspot ·
**E** design prior only.

### 7.1 No residue can be classified C or D

Searched every `.md`, `.py`, `.json`, `.txt` and `.sh` under
`YONSEI_FINAL10_V2/` and `docs/` for `Y82A`, `H135A`, `F155A`, `D228A`,
`mutagenesis`, `alanine scan`, `FMO`, `fragment molecular orbital`,
`pair interaction energy`, `PIEDA`. **There are no hits of substance.** The one
relevant line is `HANDOFF_TO_CLAUDE.md:429`, which states the opposite of the
premise:

> "No molecular dynamics, FMO, P2Rank, fpocket, PocketMiner, Boltz, Chai, new ML
> training, or synthesis planning has been performed."

So the working hypothesis that "ASP:228 may be a genuine design hotspot from the
literature (FMO/mutagenesis)" is **not supported by anything in this
repository**. `anchor_residues = ["ASP:228", "HIS:135"]` appears in a single
commit (`7752707`) with the code comment *"Polar anchors: hydrogen bonds to these
carry the largest modelled electrostatic terms for AZ8838"* — a claim about
modelled electrostatics with no calculation behind it anywhere in the tree.
ASP:228 is therefore classified **E** alongside its A\*/B labels, and
`v2_anchor_metrics.py` exposes `load_external_evidence()` so that real
mutagenesis or FMO data can be attached later without silently editing weights.

### 7.2 5NDD / AZ8838

| Residue | dist (Å) | Class | Evidence | Hotspot weight | Old PROFILE role | % designs H-bonding | % contacting |
|---|---:|---|---|---:|---|---:|---:|
| **HIS:135** | 2.630 | **A**, B | HBDonor 2.630 Å DHA 138.9°; NE2 bare ⇒ acceptor; H-bond under **all three** protomers | **1.00** | anchor | 8.37% | 88.6% |
| **TYR:82** | 2.475 | **A**, B | HBDonor 2.475 Å DHA 153.9°; shortest polar contact in the pocket; H-bond under T1, T3 | **0.80** | *contact only* | 10.64% | 86.9% |
| **ASP:228** | 2.929 | **A\***, B, **E** | OD1···N4 2.929 Å; acceptor–acceptor in T1 so VdW only; H-bond under T2, T3; declared an anchor with no evidence recorded | **0.80** | **anchor** | 6.63% | 95.6% |
| PHE:155 | 3.138 | B | Hydrophobic + VdW; 12 heavy atoms ≤4 Å, densest lipophilic wall | 0.45 | contact | 0.51% | 96.9% |
| HIS:227 | 3.500 | B | Hydrophobic; 14 heavy atoms ≤4 Å | 0.45 | contact | 5.53% | 97.2% |
| ILE:152 | 3.467 | B | Hydrophobic + VdW | 0.45 | contact | 1.06% | 90.8% |
| CYS:226 | 3.447 | B | Hydrophobic + VdW | 0.45 | *(not in PROFILE)* | 1.59% | 89.8% |
| LYS:131 | 3.065 | B | VdW; NZ 4.067 Å from nearest ligand polar atom — too far to anchor | 0.20 | contact | 20.58% | 98.7% |
| ILE:327 | 3.129 | B | VdW | 0.20 | *(not in PROFILE)* | 1.89% | 83.0% |
| TYR:134 | 3.566 | B | VdW | 0.20 | *(not in PROFILE)* | 0.11% | 83.3% |
| TRP:141 | 3.536 | B | VdW; **no design in 9,066 H-bonds it** | 0.20 | *(not in PROFILE)* | 0.00% | 68.2% |
| TYR:156 | 3.604 | B | ≤5 Å, no ProLIF term | 0.20 | *(not in PROFILE)* | 0.15% | 22.2% |
| LEU:330 | 3.629 | B, E | ≤5 Å but no ProLIF term in the crystal complex | 0.20 | contact | 0.77% | 96.8% |
| LEU:78 | 3.850 | B | ≤5 Å, no ProLIF term; **never H-bonds** | 0.20 | *(not in PROFILE)* | 0.00% | 54.6% |
| CYS:331 | 4.037 | B | rim | 0.00 | *(not in PROFILE)* | 1.07% | 15.8% |
| LEU:151 | 4.201 | B | rim; contacted by 97.6% of designs yet absent from PROFILE | 0.00 | *(not in PROFILE)* | 0.79% | 97.6% |
| TYR:326 | 4.810 | B, E | rim | 0.00 | switch | 0.10% | 22.6% |
| TYR:323 | **6.703** | **E** | not pocket lining | 0.00 | switch | 0.36% | 6.4% |
| TYR:311 | **8.724** | **E** | not pocket lining | 0.00 | contact + agonist | 0.00% | **0.29%** |
| LEU:230 | **10.645** | **E** | not pocket lining | 0.00 | agonist | 0.00% | **0.15%** |

### 7.3 Three further problems in the existing PROFILE

1. **`contact_residues` includes TYR:311, 8.724 Å from the crystallographic
   ligand.** Only 26 of 9,066 designs (0.29%) reach it, so **73.4% of designs sit
   at exactly 6/7** and 99.85% are at 6/7 or below; just 14 designs (0.15%) score
   7/7. `contact_fraction` carries weight 0.15 in `consensus_score`, so this is a
   near-uniform ~0.021 deduction that discriminates almost nothing. I initially
   predicted a *hard* 6/7 ceiling and that was wrong — checking it showed the
   docking box extends well past the crystal ligand footprint, with poses
   touching 46 distinct residues outside the 5 Å crystal shell.
2. **`AGONIST_PATTERN = {LEU:230, TYR:311, ASP:228}` is nearly inert.** Two of
   its three residues are 8.7 Å and 10.6 Å from the crystal ligand. It fires on
   **9 of 12,341 rows** (all 5NDD). Whatever agonist-mimicry risk exists, this
   term is not measuring it.
3. **`switch_residues` are mostly out of reach.** TYR:323 is 6.703 Å out and
   TYR:326 4.810 Å; `switch_contact` is true for 24.4% of 5NDD designs, and
   TYR:326 supplies almost all of it (2,051 designs vs 576 for TYR:323).

### 7.4 5NDZ / AZ3451 — done to the same standard

**12 fingerprint keys, and genuinely zero hydrogen bonds.** This is a real
finding, not a detection failure: the ligand carries 7 polar atoms but only one
polar hydrogen, and the closest polar–polar approach in the whole pocket is
TYR:210 OH ··· ligand N1 at **3.393 Å**, which ProLIF scores as `Hydrophobic`,
not an H-bond. 10 residues within 4.0 Å, 13 within 5.0 Å. The pocket is
lipophilic and an anchor-based metric does not apply to it — which is what
`anchor_residues = []` in the profile already says, correctly.

Keys: `Hydrophobic` — PHE:154, ILE:202, LEU:203, TYR:210; `VdWContact` —
ALA:120, LEU:123, PHE:154, ALA:157, CYS:161, TRP:199, LEU:203, VAL:211.

**One dead key found.** The 5NDZ profile lists `GLY:157`, but residue 157 in
`5NDZ_allosteric_receptor_protonated_pH74.pdb` is **ALA**
(`ATOM 782 N ALA A 157`). `GLY:157` matches **0 of 3,275** designs, so the 5NDZ
`contact_fraction` has a genuine hard ceiling of 9/10 — and in practice the
observed maximum is **0.8 (8/10)**, reached by 26 designs. ALA:157 *is* a real
crystal contact (3.243 Å, VdWContact, touched by 73.8% of designs) and is simply
misnamed in the profile.

---

## 8. Recommendation

**Use `CRYSTAL_IFP_RECOVERY` and `DESIGN_HOTSPOT_SCORE` as two reported
metrics, and replace the binary dual-anchor gate with a graded polar-anchor
count over {TYR:82, HIS:135, ASP:228}.**

Concretely, for `5NDD_orthosteric`:

1. **Retire `anchor_residues = ["ASP:228", "HIS:135"]`.** It is unsourced, it
   contradicts the file the same document cites, and it selects a population 95%
   disjoint from the crystallographic one.
2. **Do not replace it with `["TYR:82", "HIS:135"]` as a hard gate either.**
   That pair is correct for the *as-built protomer only*, and §4 shows the
   protomer was chosen by substructure match rather than by evidence. Hard-gating
   on it would repeat the original mistake with better provenance.
3. **Adopt the protomer-robust anchor set** `{TYR:82, HIS:135, ASP:228}` — the
   three and only three residues with a sub-3 Å polar heavy-atom pair — and score
   the *number* satisfied, not a boolean. Weight HIS:135 highest (1.00), since it
   is the only H-bond that survives every protomer; TYR:82 and ASP:228 equally
   (0.80 each), since the evidence for them is symmetric.
4. **Report `n_polar_anchors_hbonded ∈ {0,1,2,3}` alongside the score**, so a
   reader can apply their own threshold. The candidate populations are 2,147 /
   171 / 7 for ≥1 / ≥2 / =3.
5. **If a single headline number is needed for the shortlist**, use
   **"any two of TYR:82 / HIS:135 / ASP:228" = 171 designs**. It is protomer-
   robust, it is a strict superset of both the old 62 and the crystallographic
   81, it does not require choosing between two equally-supported residues, and
   at 1.9% of the library it is still selective.
6. **Correct `FINAL_CANDIDATES.md` and `v2_final_report.py:79-80`**, which
   currently assert the crystal H-bonds and then count a different pair.
7. **Fix the three PROFILE errors in §7.3 and the `GLY:157`→`ALA:157` typo**
   before any re-rank, and **re-protonate both receptors with a tool that
   honours pH** (§5) before any new fingerprinting. Open Babel's `-h` and `-p`
   flags are mutually exclusive in the way used here.

### Why not simply keep the higher-recovery definition?

Because the two metrics answer different questions and should not be merged.
`CRYSTAL_IFP_RECOVERY` is empirical and answers *"does this pose look like the
crystal complex?"* — no prior in it. `DESIGN_HOTSPOT_SCORE` answers *"does this
pose engage the positions we believe matter for antagonism?"* — and those beliefs
are, in this repository, unevidenced beyond the crystal geometry itself. Measured
across the 9,066 5NDD designs the two rank-correlate at Spearman **0.581** —
related, but far from redundant. Collapsing them would hide exactly the
disagreement this audit exists to surface.

### What this changes about the shortlist

The 62 "dual-anchor designs" in `FINAL_CANDIDATES.md` are not wrong molecules,
but the **label is wrong**: they are not the designs reproducing AZ8838's
crystallographic hydrogen-bond signature. Only 7 of them are. If that table is
meant to show crystallographic mimicry it should be rebuilt; if it is meant to
show ASP:228 engagement it should say so and drop the sentence that precedes it.
Neither set is large: 8 of the 62 and 11 of the 81 fall in the consensus top 500.

---

## 9. What was actually run

```bash
PY=/Users/moheet/Documents/ChatGPT/PAR2/.venv-v2/bin/python

# 1. self-verification of every frozen constant against the structure files
$PY YONSEI_FINAL10_V2/scripts/v2_anchor_metrics.py --verify
#    -> VERIFY: PASS
#       5NDD: 16 fingerprint keys reproduce exactly; TYR:82 2.475 A / DHA 153.933,
#             HIS:135 2.63 A / DHA 138.878; 17 residues in the 5.0 A shell
#       5NDZ: 12 fingerprint keys; 13 residues in the 5.0 A shell

# 2. the recount + per-pose terms
$PY YONSEI_FINAL10_V2/scripts/v2_anchor_metrics.py \
    --consensus YONSEI_FINAL10_V2/07_CONSENSUS/DENOVO_EX8_CONSENSUS_ALL.csv \
    --pocket 5NDD_orthosteric --out YONSEI_FINAL10_V2/10_FINAL
#    -> [crosscheck] CRYSTAL_IFP_RECOVERY vs stored max_ifp_recovery,
#       9066 rows, max |delta| = 0.00e+00 (AGREE)
```

Also executed, as one-off analyses in the session scratchpad rather than
committed scripts: the full-metadata fingerprint dump of both systems and both
pre-repair originals; the receptor donor-geometry probe; the three-protomer
rebuild; the ionisation-state census; and the library census behind §6 and §7.

### Not run, and therefore not claimed

- No redocking, no rescoring, no re-ranking. `consensus_score` is untouched.
- No molecular dynamics, no QM, no pKa calculation. The imidazolium protomer T3
  is shown to be *geometrically* consistent with the pocket; nothing here
  establishes that it is the populated state.
- No external literature was consulted. Every statement about evidence is a
  statement about **this repository**.
- `07_CONSENSUS/DENOVO_EX8_CONSENSUS_ALL.csv` is gitignored; the recount was run
  against the local copy, 12,341 rows, and reproduces both published figures.

### Limits of interpretation

Nothing here establishes PAR2 activity for any molecule, or that any anchor
definition predicts antagonism. Fingerprint recovery is geometric similarity to
a crystal pose. Static docking cannot separate an antagonist from a biased
agonist. These metrics are prioritisation features, and the decisive experiments
remain the functional assays.

---

## Files

| File | Contents |
|---|---|
| `AZ8838_REFERENCE_INTERACTIONS.md` | this document |
| `AZ8838_REFERENCE_INTERACTIONS.csv` | 34 rows, one per residue, both pockets: distances, contact counts, ProLIF terms, protomer dependence, classification, evidence, hotspot weight, old PROFILE role, library census |
| `ANCHOR_DEFINITION_AUDIT.csv` | 13 anchor definitions and recovery thresholds side by side with counts, overlaps, Jaccard vs the old definition, and rank impact |
| `ANCHOR_PER_POSE_TERMS.csv` | 9,066 × 69 — both metrics plus `HBOND_<RES>` / `CONTACT_<RES>` for every pocket-lining residue and a `DEF_<definition>` flag per definition |
| `../scripts/v2_anchor_metrics.py` | the reusable module, with `--verify` |
