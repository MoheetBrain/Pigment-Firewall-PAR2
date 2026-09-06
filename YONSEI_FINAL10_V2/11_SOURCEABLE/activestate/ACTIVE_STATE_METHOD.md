# Active-state counter-screen — method, normalisation and decision rule

Lane: ACTIVE-STATE COUNTER-SCREEN (Agent 4).
Companion documents: `ACTIVE_STATE_STRUCTURES.md` (what was verified),
`ACTIVE_STATE_PROVENANCE.json` (commands, hashes, counts),
`SOURCEABLE_ACTIVE_STATE_COUNTERSCREEN.csv` (the result).

> **This lane produces a WARNING FLAG, not a mechanism call.** Nothing here is
> evidence that a molecule is a PAR2 agonist or a PAR2 antagonist. A docking
> campaign cannot establish transducer bias. The only thing that can is the
> functional assay — a keratinocyte melanocore-uptake readout plus a
> G12/13→RhoA counter-screen. Everything below exists to decide which molecules
> deserve that assay first and which carry a structural reason for concern.

---

## 1. The question this lane answers

The project's dangerous failure mode is a molecule that antagonises Gq but
**agonises G12/13**: it would still drive melanocore engulfment while looking
like a success in a calcium assay. Docking cannot settle that.

What structure *can* answer is narrower and answerable:

> Does the candidate look more compatible with the **inactive, antagonist-bound**
> pocket, or with the **active-state** receptor and the volume the endogenous
> tethered ligand and the biased agonist GB88 occupy?

A candidate that fits the active-state agonist volume as well as or better than
the antagonist pocket gets a warning flag. That is the whole claim.

---

## 2. Why a rank, and never a ΔG difference

**Raw Vina scores are never differenced across receptor conformations here.**
Different receptor conformations carry different score offsets; a raw ΔG
comparison between 5NDD and 8ZMD would not be a binding free-energy difference,
it would be an artefact. In this campaign the offsets have three independent
sources at once:

1. genuine conformational difference (inactive vs active, global Cα RMSD 2.0–2.5 Å);
2. **sequence** difference — the inactive receptors carry ten thermostabilising
   mutations the active ones do not;
3. box geometry — the boxes are ligand-shaped and differ in volume by ~3×.

### The normalisation actually used

For **every receptor-box independently**, each ligand's best clash-filtered Vina
score is converted to a **rank over the identical ligand population docked into
that same box**. Three normalisations are computed; one is primary and two are
declared robustness channels. All three were fixed before any control result was
inspected.

**PRIMARY — size-residualised Vina percentile (`RPCT__<box>`).**
Vina scores scale with heavy-atom count, and these boxes differ ~3× in volume, so
a raw percentile is not guaranteed to carry the *same* size bias in every box —
which would leak into a difference of percentiles. Within each box, `best_vina`
is regressed on `heavy_atoms` by ordinary least squares over the ligands that
have an acceptable pose in that box, and the **residual** is percentile-ranked:

```
resid  = best_vina - (a + b * heavy_atoms)          # fitted per box
RPCT__<box> = rank(resid, ascending=False, pct=True)   # within that box
```

`1.0` = does better than its size predicts, in that box; `0.0` = worse.

**Robustness A — raw Vina percentile (`PCT__<box>`, `STATE_PREFERENCE_SCORE_RAW`).**
Simple, but size-confounded.

**Robustness B — ligand-efficiency percentile (`LEPCT__<box>`,
`STATE_PREFERENCE_SCORE_LE`)**, using −Vina / heavy atoms. Over-corrects, and
favours small molecules.

Only clash-filtered poses contribute. A ligand with **no acceptable pose in a box
gets a MISSING rank — never 0.0.** Every cross-receptor comparison is therefore a
comparison of *positions within matched populations*, never of energies.
The classification is reported under the primary channel and cross-checked
against both robustness channels.

---

## 3. The three site groups

Fourteen receptor-boxes were docked (see `ACTIVE_STATE_STRUCTURES.md` §4). They
group as:

| Group | Boxes | What it represents |
|---|---|---|
| **ANTAGONIST POCKETS** | `5NDD__ORTHO`, `5NDZ__ALLO` | the two crystallographic antagonist/NAM pockets, in the inactive thermostabilised receptors |
| **AGONIST VOLUME** | `8ZMD__TL`, `8ZME__TL`, `9E7R__GB88` | the volume the endogenous SLIGKV tethered ligand occupies in the Gq and G13 complexes, and the volume the biased agonist GB88 occupies crystallographically |
| **ACTIVE-STATE POCKET COMPATIBILITY** | `<active>__ORTHO`, `<active>__ALLO` | the same two crystallographic pockets mapped into the active receptors — does the pocket itself survive activation? |

`9D0A__TL` was docked but is **excluded from the AGONIST VOLUME group**: 9D0A
models only S37-L38-I39 of the tethered ligand, so its volume is not comparable
with the complete SLIGKV hexapeptide of 8ZMD/8ZME. Its columns are retained in
the CSV, marked, and not used by the rule.

The group split is meaningful because of the structural finding in
`ACTIVE_STATE_STRUCTURES.md` §5: **the AZ8838 antagonist pocket and the
tethered-ligand/GB88 site are 17 Å apart and share no atoms** (centroid
separation 16.9 Å, closest heavy-atom pair 7.05 Å, residue-contact Jaccard
0.103). Crystallographic GB88 overlaps the tethered ligand at 80 % of its heavy
atoms and the AZ8838 pocket at 0 %. The two site groups are therefore genuinely
different places in the receptor, not two scorings of one place.

---

## 4. Evidence columns

Per pose, then reduced per (ligand, box) over **clash-filtered poses only**.

**Clash filter — the campaign's own rule, unchanged:** a pose is acceptable when
GNINA `minimizedAffinity < 0`. Molecules with no acceptable pose in a box are
kept and flagged (`CLASH__<box> = True`), never dropped and never scored as zero.
This rule was independently corroborated here: poses with positive
`minimizedAffinity` carry 4–8 sterically overlapping heavy atoms and 2.9–6.7 Å of
summed vdW overlap, while accepted poses carry none.

| Column family | Meaning |
|---|---|
| `RPCT__<box>` | **primary** within-box size-residualised Vina percentile (§2) |
| `PCT__<box>` | within-box raw Vina percentile (robustness A) |
| `LEPCT__<box>` | within-box ligand-efficiency percentile (robustness B) |
| `VRESID__<box>` | the raw size residual behind `RPCT` |
| `VINA__<box>` | raw best clash-filtered Vina — **reported for traceability, never differenced across boxes** |
| `CLASH__<box>` | True when no pose in that box passed the clash filter |
| `NOK__<box>` | number of acceptable poses out of 9 |
| `CLASHFRAC__<box>` | fraction of ligand heavy atoms sterically overlapping the receptor in the retained pose (geometric, vdW sum − 0.5 Å) |
| `BURIED__<box>` | fraction of ligand heavy atoms with ≥6 receptor heavy atoms within 4.5 Å — pocket occupancy |
| `IFPREC__<box>` | ProLIF fingerprint recovery against that box's crystallographic reference |
| `GB88SIM__<box>` | Jaccard similarity of the pose's residue-contact set to **crystallographic** GB88's contact set |
| `TLOV__<box>` | fraction of pose heavy atoms within 2.0 Å of a modelled tethered-ligand heavy atom |
| `GB88OV__9E7R__GB88` | same, against the crystallographic GB88 pose |
| `MICRO__<box>` | contacts with reachable activation microswitches — **measurable only in `ALLO` boxes** (§5) |
| `campaign_max_ifp_recovery` | the candidate's `CRYSTAL_IFP_RECOVERY` in 5NDD carried through from `10_FINAL/*.csv` for comparison |

Derived:

```
ANTAG_POCKET_PCT_BEST      = max(RPCT__5NDD__ORTHO, RPCT__5NDZ__ALLO)          # skipna
AGONIST_VOLUME_PCT         = mean(RPCT__8ZMD__TL, RPCT__8ZME__TL, RPCT__9E7R__GB88)   # skipna
STATE_PREFERENCE_SCORE     = ANTAG_POCKET_PCT_BEST - AGONIST_VOLUME_PCT
GB88_CONTACT_SIM_MAX       = max(GB88SIM__<agonist-volume boxes>)
AGONIST_VOLUME_OVERLAP_MAX = max(TLOV__8ZMD__TL, TLOV__8ZME__TL, GB88OV__9E7R__GB88)
N_ANTAG_BOXES              = count of antagonist-pocket boxes with a non-missing percentile
N_AGONIST_BOXES            = count of agonist-volume boxes with a non-missing percentile
```

`STATE_PREFERENCE_SCORE` is positive when the molecule sits higher in its own
population in the crystallographic antagonist pocket than in the agonist volume,
and negative when the reverse holds.

---

## 5. The microswitch channel is reported as MISSING, not zero

Five class-A activation microswitches were located in PAR2's own numbering by
motif match on the modelled 8ZMD chain-R sequence, all five matching exactly:
`ADL` at 120–122 (D2.50), `QRY` at 172–174 (DRY-equivalent), `P254` (P5.50),
`CFTP` at 299–302 (CWxP toggle, F not W), `DPFVY` at 340–344 (NPxxY-equivalent).

Their measured distances to the ligand sites then disqualify almost all of them.
Only **ALA120 and ASP121** lie within 6 Å of any ligand site, and only of the
**allosteric** one (3.76 Å and 5.78 Å). Every other motif residue is 12.7–36.5 Å
from every site — including the entire DRY-equivalent (28.3–36.5 Å), the entire
NPxxY-equivalent (11.9–30.0 Å) and the whole CWxP toggle (12.0–20.2 Å).

**No ligand in the orthosteric pocket or the tethered-ligand volume can contact
any conserved activation microswitch.** This is precisely the defect that retired
the earlier agonist-mimicry flag (two of its three residues sat 8.7 Å and 10.6 Å
from the ligand). `MICRO__<box>` is therefore written as **NaN** for every
`ORTHO`, `TL` and `GB88` box, and carries a real count only in `ALLO` boxes.
The decision rule does not use it at all.

---

## 6. Decision rule

Applied in order; the first matching rule wins. Every constant was fixed **before
the control molecules were inspected**, and every term is a column of
`SOURCEABLE_ACTIVE_STATE_COUNTERSCREEN.csv`, so the rule is reproducible from the
CSV alone.

```
PCT_TOP_HALF      = 0.50    # "scores well" in a site group
STATE_MARGIN      = 0.25    # margin for a clear inactive-state lean
GB88_CONTACT_SIM  = 0.30    # residue-contact Jaccard to crystallographic GB88
TL_OVERLAP        = 0.25    # fraction of heavy atoms in the agonist volume
MIN_AGONIST_BOXES = 2       # of 3
MIN_ANTAG_BOXES   = 1       # of 2
```

**R0 — no agonist-volume evidence → `INCONCLUSIVE`**
`N_AGONIST_BOXES < 2`. The state preference cannot be evaluated.

**R1 — sterically excluded from both antagonist pockets → `ACTIVE/GB88 WARNING`**
`N_ANTAG_BOXES == 0` and `AGONIST_VOLUME_PCT >= 0.50`.
The molecule has no non-clashing pose in *either* crystallographic antagonist
pocket, yet the tethered-ligand/GB88 volume accommodates it in the top half of
the population. That is the geometric signature of an agonist-site binder.

**R1b — no antagonist-pocket evidence and weak agonist placement → `INCONCLUSIVE`**
`N_ANTAG_BOXES == 0` and `AGONIST_VOLUME_PCT < 0.50`. Nothing to compare.

**R2 — agonist volume preferred, with mimicry → `ACTIVE/GB88 WARNING`**
`AGONIST_VOLUME_PCT >= 0.50` **and** `STATE_PREFERENCE_SCORE <= 0.0` **and**
(`GB88_CONTACT_SIM_MAX >= 0.30` **or** `AGONIST_VOLUME_OVERLAP_MAX >= 0.25`).
The molecule does at least as well in the agonist volume as in the antagonist
pocket *and* physically reproduces the agonist site — either GB88's contacts or
the tethered ligand's occupied space.

**R3 — antagonist pocket clearly preferred → `INACTIVE-LEANING`**
`STATE_PREFERENCE_SCORE >= 0.25` **and not**
(`GB88_CONTACT_SIM_MAX >= 0.30` **and** `AGONIST_VOLUME_PCT >= 0.50`).

**R4 — everything else → `STATE-AMBIGUOUS`**

The applied rule id is recorded per molecule in `STATE_CLASS_RULE`, and the
numeric reason in `STATE_CLASS_REASON`.

### What each class does and does not mean

| Class | Means | Does **not** mean |
|---|---|---|
| `INACTIVE-LEANING` | better placed in the crystallographic antagonist pocket than in the agonist volume, with no GB88 mimicry | that it is an antagonist, or that it lacks G12/13 bias |
| `STATE-AMBIGUOUS` | no clear structural preference either way | anything about activity |
| `ACTIVE/GB88 WARNING` | fits the tethered-ligand/GB88 volume at least as well as the antagonist pocket, or is sterically excluded from the antagonist pocket entirely | that it is an agonist |
| `INCONCLUSIVE` | the evidence needed by the rule is missing | that the molecule failed |

---

## 7. Control sanity-check

The rule is only trustworthy if the controls behave. The pre-registered
expectations are:

* **AZ8838** (orthosteric antagonist, ligand of 5NDD) → `INACTIVE-LEANING`
* **AZ3451** (allosteric NAM, ligand of 5NDZ) → `INACTIVE-LEANING`
* **GB88** (biased agonist, ligand of 9E7R) → `ACTIVE/GB88 WARNING`

If they do not come out that way, **the rule is wrong or the evidence is too
weak**, and the affected molecules are marked `INCONCLUSIVE` rather than the rule
being tuned until it gives the expected answer.

Two further controls are reported but not pre-registered, because their expected
behaviour is genuinely uncertain: **SLIGKV-NH₂** (the activating peptide — a
flexible hexapeptide that rigid-receptor docking scores unreliably) and
**I-287** (reported as a NAM selective for Gq and G12/13).

*(Results are filled in below once the docking completes — see §9.)*

---

## 8. Deliberate deviations from campaign scripts, and why

1. **`rdMolStandardize.TautomerEnumerator().Canonicalize()` is not called.**
   The campaign's `v2_prepare_ligands.py` calls it; the campaign's own audit
   (HANDOFF defect 7) showed it destroyed stereochemistry in 2,534 designs,
   changed the constitution of 1,199 and invented unassigned stereocentres in
   2,241. Candidates are embedded from `smiles_prepared`, which is already
   standardised and pH-7.4 protonated, so re-running it would dock a *different*
   molecule from the one the campaign ranked. Reference molecules arriving as raw
   SMILES get `Cleanup` + `FragmentParent` + the campaign's own `protonate_ph74`,
   with the same call omitted.
2. **Interaction fingerprints use `*_pH74_FIXED.pdb`, not
   `*_protonated_pH74.pdb`.** The latter — still referenced by
   `scripts/v2_interactions.py` — was verified here to have 0/39 charged
   lysines and 17/29 protonated aspartates. See `ACTIVE_STATE_STRUCTURES.md` §7.
3. **The counter-screen re-docks the inactive receptors too.** The campaign's
   existing 5NDD numbers come from a different ligand population, so their
   percentiles would not be comparable. Every ligand is docked into all boxes
   under one protocol so that every within-box population is identical.
4. **GB88 is used as the (2S,3S) diastereomer** defined by PDB ligand `A1BF3`
   of 9E7R, not the (2S,3R) *allo*-isoleucine form depicted by IUPHAR GtoPdb
   ligand 6658 and PubChem CID 73755230.

## 9. Results

*(filled in after the run — see the final section of this file.)*
