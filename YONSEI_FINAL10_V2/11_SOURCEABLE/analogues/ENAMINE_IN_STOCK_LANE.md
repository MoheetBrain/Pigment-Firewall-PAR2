# ENAMINE_IN_STOCK lane — local catalogue similarity search

**Date:** 2026-09-06 · machine `h3` · lane tag `ZINC_IN_STOCK`
**Kept separate from** the `ENAMINE_REAL_MAKE_ON_DEMAND` lane (SmallWorld REAL maps).

## 1. What was asked, and what was actually possible

The instruction was to download the official Enamine Screening Collection SDFs
(~4.8M in-stock compounds) and search them locally.

**The official Enamine SDFs are behind a login wall.** The download links on
`enamine.net/compound-collections/screening-collection` are
`/component/download/?view=file&f=<id>`; every one of them returns an HTML
**"Login - Enamine"** page, not a file. Creating an account or entering
credentials is out of scope for this session, so that route was not taken and
nothing was fabricated in its place.

`zinc20.docking.org` also now serves a **"Verify you're human"** challenge.
That was **not** bypassed.

**What was used instead:** `files.docking.org/2D/`, the plain ZINC20 file
server, which serves the same vendor-indexed chemistry with no login and no
challenge. This is the substitute for the Enamine SDF, and it is a substitute —
the difference is stated here rather than papered over.

## 2. Which tranches, and why those

ZINC20 2D tranche files are named `<MW bin><logP bin><reactivity><purchasability>.smi`.
The purchasability character was resolved **empirically**, by measuring file
sizes in a single MW/logP bin:

| 4th char | lines in bin `CD` | read as |
|---|---|---|
| A | 88,612 | in-stock |
| B | 255,605 | in-stock |
| C | 2,412 | in-stock |
| **D** | **8,854,471** | make-on-demand — **not downloaded** |
| **E** | **18,092,353** | make-on-demand — **not downloaded** |
| F | 60,209 | in-stock |

D and E hold 8.8M and 18M molecules *in one MW/logP bin alone*; that is
REAL-scale on-demand space, not stock. Only **A, B, C and F** were downloaded,
across all 121 MW/logP directories and 6 reactivity classes.

**Catalogue actually searched: 430 files, 258 MB, 3,971,098 molecules**
(3,448,188 after the 200–600 Da envelope filter). That is the same order as the
~4.8M in-stock figure the instruction referenced.

## 3. Method

Morgan/ECFP4, radius 2, 2048 bits, Tanimoto — streamed shard by shard, 30
worker processes, never loading the catalogue into RAM. Queried with all 32
frozen seeds, using `stereo_smiles_input` where it exists and differs.

Molecules the campaign has **already screened** were excluded by full InChIKey
(22,028 keys, including neutralised parents of the 19,660 screened molecules),
so no compute can be spent re-docking something already done.

Retention bands: `>=0.80`, `0.70–0.80`, `0.60–0.70`, `0.50–0.60`.

## 4. Result — and it is a negative one

**7 hits from 3,971,098 in-stock molecules.** All seven sit in the weakest band
(0.50–0.60); the best is **0.556**. They come from only **2 of the 32 seeds**
(SEED026/DN00100 and SEED002/DN01379). Nothing reached 0.60.

## 5. The negative result is real, not a broken pipeline

This was checked rather than assumed. The **identical search, over the identical
catalogue**, was re-run with five ordinary drug-like query molecules:

| query | hits | best Tanimoto |
|---|---|---|
| propranolol | 128 | — |
| ibuprofen | 124 | — |
| imatinib | 84 | — |
| GB88 | 26 | — |
| AZ8838 | 0 | — |
| **total** | **362** | **1.00 (exact match found)** |

Band distribution: 6 at ≥0.80, 36 at 0.70–0.80, 80 at 0.60–0.70, 240 at
0.50–0.60.

The pipeline finds close neighbours, and exact matches, when they exist. It
returns almost nothing for our de novo seeds because **almost nothing is there**.

(AZ8838 returning 0 is consistent: at MW 220 it is fragment-sized, and small
molecules have sparse fingerprints and low Tanimoto to everything. It is not
evidence against the search.)

## 6. What this means for the campaign

**Our de novo chemistry is not purchasable, and it does not have purchasable
close analogues either.** The seeds are high-Fsp3, sugar- and terpenoid-like
BRICS constructions (Fsp3 up to 1.00); in-stock screening catalogues are
dominated by flat aromatic amide chemistry. The two populations barely overlap.

This is consistent with, and explains, the independent sourceability result:
**22 of 25 members of the existing panel resolve to NOT_SOURCEABLE.**

The consequence for the final deliverable is direct and must not be dressed up:
a TOP20 of *close analogues of our de novo designs* is **not achievable from
in-stock catalogue space**. The sourceable panel has to be built from real
compounds that preserve the *interaction solution* — pocket, archetype,
pharmacophore — at moderate 2D similarity, rather than from close structural
analogues. Any claim of close analogy would be false.

## 7. Honest limits of this lane

- The official Enamine Screening Collection was **not** searched; ZINC20's
  in-stock tranches were searched as a substitute.
- The ZINC in-stock snapshot is not dated in the files themselves; the vendor
  lane separately reports its largest in-stock index as 2019-Q4, so some
  currently-orderable chemistry will be missing.
- Only ECFP4/Tanimoto was applied in this lane. MCS, pharmacophore and 3D-shape
  neighbours were **not** searched here, and a pharmacophore-preserving scaffold
  hop below 0.50 Tanimoto would not appear in this table.
- Purchasability is inferred from the ZINC tranche tier, not from a live stock
  check. Every hit still has to pass the vendor resolver before it can be
  called orderable.
