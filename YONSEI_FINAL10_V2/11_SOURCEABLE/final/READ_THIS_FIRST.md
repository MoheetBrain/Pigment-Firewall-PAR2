# FINAL_SOURCEABLE_PAR2_TOP20 — what it is, and two things wrong with it

**Status: the deliverable exists and every candidate is real and orderable.
It does NOT yet meet one of the brief's requirements. Read both caveats.**

## What is solid

- **20 candidates, 20 unique Murcko scaffolds, 100% vendor-listed.** Every one
  resolved to an exact InChIKey match in PubChem with named suppliers
  (median 33 vendors: Enamine, Sigma-Aldrich, MedChemExpress, Molport, TCI…).
  Vendor counts and CIDs are retrieved data with a date, not `PENDING`.
- **All carry fresh EX32 evidence** (exhaustiveness 32, 9 poses) produced under
  a fail-closed hash gate: 5NDD receptor `c2411d4d…`, 5NDZ `af9f9eec…`,
  GNINA `3340c1f4…` — all verified against `EX32_RUN_PROVENANCE.json`.
- **All prepared without the stereo-destroying tautomer call.** 80/80 prepared,
  0 failures, **0 stereocentres lost**.
- ProLIF crystal-IFP recovery and preparation-independent anchor geometry
  computed for every row.

## CAVEAT 1 — this is a repurposing panel, not a de novo analogue panel

**19 of 20 are approved/clinical drugs with Tanimoto 0.15–0.23 to our de novo
seeds.** That is not meaningful structural similarity. Only **ZI54096226**
(Tanimoto 0.397) is a genuine de novo-connected in-stock molecule.

This is a direct consequence of the validated negative result: a local ECFP4
search of **3,971,098 in-stock molecules** returned **7 hits ≥ 0.50** for our
32 seeds, best 0.556, while a positive control over the same catalogue returned
**362 hits including exact matches**. Our de novo chemistry is high-Fsp3
sugar/terpenoid-like; screening catalogues are flat aromatic amides. The two
spaces barely intersect.

So the brief's requirement *"meaningfully similar to one of our strongest de
novo designs"* is **not met** by 19 of these 20. They earn their place on PAR2
pocket evidence and orderability, not on de novo provenance. Anyone presenting
this list must say so.

## CAVEAT 2 — the four 5NDZ candidates are weakly supported

Ranks 5, 6, 12 and 16 are allosteric. Their `DESIGN_HOTSPOT_SCORE` is
**0.32–0.37** versus 0.88–0.95 for the orthosteric rows, and no 5NDZ finalist
reached more than **1 of 3** polar anchors (5NDD: 67/80 hit all three). Median
5NDZ IFP recovery was 0.42 versus 0.75 for 5NDD.

The brief said not to reserve a lane for symmetry if its chemistry is bad.
**On this evidence it is bad.** Recommend dropping to 0–2 allosteric slots and
backfilling from the orthosteric pool.

## Calibration context you must apply

The benchmark lane established that **only 2 of the 16 crystal reference keys
in 5NDD are hydrogen bonds**, so **0.875 IFP recovery is reachable by
pocket-filling alone**. Treat IFP recovery as necessary, not sufficient. The
decoy null that would quantify this did not finish (see below).

## What is missing

| Missing | Why |
|---|---|
| Co-folding columns | Running now on `a100-40`, 98 jobs, auto-collects to `~/COFOLD_FINALISTS.tgz` then self-powers-off |
| Active-vs-decoy enrichment + IFP null | h3 was powered off by the EX32 watchdog at 16:45 UTC while the benchmark was at 30/152 shards; work is resumable, `.done` sentinels intact |
| Active-state warning column | Same reboot; counter-screen incomplete |
| Price / lead time | Every route carrying them is credential-gated. UNKNOWN everywhere, honestly |

## To finish

1. Restart `a100-40` only if its watchdog has not already collected; pull
   `~/COFOLD_FINALISTS.tgz`, run `v3_analyse_cofold.py`, re-run
   `v3_final_sourceable_panel.py` with `--cofold`.
2. Restart `h3`, resume `~/BENCH/run_all.sh` and the `~/activestate` lane.
3. Re-rank with the active-state gate and the decoy-calibrated IFP weight, and
   cut the 5NDZ lane to what the evidence supports.

**Nothing here is a demonstrated PAR2 antagonist.** Docking, fingerprints and
co-folding are structural hypotheses. The decisive experiment remains the
melanocore-uptake assay plus the G12/13→RhoA counter-screen.
