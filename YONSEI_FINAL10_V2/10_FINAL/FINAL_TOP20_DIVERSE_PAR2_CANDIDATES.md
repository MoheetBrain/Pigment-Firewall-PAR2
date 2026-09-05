# FINAL TOP 20 — computationally prioritised PAR2 candidates

Generated 2026-09-05T21:46:15.817735+00:00 · commit lineage on branch `yonsei-final10-v2`

## READ THIS FIRST

**WE HAVE NOT SHOWN THAT DIRECT PAR2 ANTAGONISM REDUCES MELANOCORE UPTAKE.** The historical pigmentation evidence used RWJ-50353, a broad serine-protease inhibitor, not a selective PAR2 antagonist. P2L-003 has never been tested on a pigmentation endpoint. **That gap is a larger uncertainty than the difference between rank 3 and rank 12 on this list.**

These are COMPUTATIONALLY PRIORITISED PAR2 CANDIDATES — not demonstrated antagonists, not pigmentation inhibitors. Static docking cannot separate an antagonist from a biased agonist. The decisive counter-screen is **G12/13 → RhoA**: a compound that blocks Gq but agonises G12/13 would still drive the actin machinery that engulfs melanocores.

PAR2 blockade cannot abolish pigment transfer outright — filopodial conduits, cytophagocytosis and baseline phagocytosis are PAR2-independent. The realistic aim is maximal suppression of the PAR2-dependent melanocore route.

## Screened universe

| | |
|---|---|
| De novo EX8 | **16,314 / 16,314** routed jobs, 14,825 molecules, 9 poses each |
| EX32 precision | 535 jobs / 513 molecules |
| Real compounds EX8 | **4,835** approved drugs, natural products and retrieved analogues |
| Combined ranked universe | **21,149 ligand–pocket rows over 19,660 molecules** |
| Validity gates | parseable 21149 → has_non_clashing_pose 17431 → real_negative_affinity 17312 → stereo_not_known_wrong 17084 |

## Panel composition

- **20 unique Murcko scaffolds** out of 20 · 19 clusters · 6 interaction archetypes
- Pocket: {'5NDD_orthosteric': 17, '5NDZ_allosteric': 3}
- Provenance lanes: {'DE_NOVO_EX32_REFINED': 15, 'NATURAL_PRODUCT_OR_V1_HIT': 3, 'REAL_ANALOGUE_PUBCHEM': 1, 'APPROVED_REPURPOSING': 1}
- Requiring synthesis: **15** · already-existing compounds: **5** · approved: **1**
- Stereochemistry: {'OK': 14, 'AMBIGUOUS': 6}

## Sourceability — the honest position

**No vendor, catalogue number, price or stock status could be obtained.** Live web lookups were blocked for this entire session, so every vendor field reads PENDING. Five of the twenty are real registered compounds (one approved drug) and are sourceable *in principle*; the other fifteen are de novo designs requiring synthesis. No retrieved analogue exceeded Tanimoto 0.80 to any seed.

## The panel

| FINAL_RANK | cand_id | source_lane | pocket | primary_archetype | best_vina_affinity | max_ifp_recovery | anchor_hbond_fraction | ligand_efficiency | mw | clogp | fsp3 | qed | stereo_flag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | RX05505 | NATURAL_PRODUCT_OR_V1_HIT | 5NDD_orthosteric | crystal_contact_reproducer | -7.025 | 0.938 | 0.333 | 0.270 | 382.550 | 2.440 | 0.632 | 0.481 | OK |
| 2 | RX00387 | REAL_ANALOGUE_PUBCHEM | 5NDD_orthosteric | crystal_contact_reproducer | -7.948 | 0.875 | 0.000 | 0.331 | 330.336 | 2.390 | 0.333 | 0.893 | OK |
| 3 | RX02990 | NATURAL_PRODUCT_OR_V1_HIT | 5NDD_orthosteric | crystal_contact_reproducer | -8.784 | 0.875 | 0.000 | 0.338 | 356.418 | 5.265 | 0.286 | 0.319 | OK |
| 4 | RX01677 | NATURAL_PRODUCT_OR_V1_HIT | 5NDD_orthosteric | crystal_contact_reproducer | -8.519 | 0.875 | 0.333 | 0.387 | 326.820 | 2.590 | 0.588 | 0.365 | OK |
| 5 | RX02731 | APPROVED_REPURPOSING | 5NDD_orthosteric | general_binder | -7.056 | 0.812 | 0.000 | 0.307 | 361.822 | 3.263 | 0.400 | 0.817 | OK |
| 6 | DN00100 | DE_NOVO_EX32_REFINED | 5NDZ_allosteric | allosteric_hedge | -8.155 | 0.750 | nan | 0.355 | 306.361 | 3.699 | 0.150 | 0.799 | OK |
| 7 | DL13598 | DE_NOVO_EX32_REFINED | 5NDZ_allosteric | allosteric_hedge | -9.356 | 0.750 | nan | 0.267 | 478.585 | 5.030 | 0.414 | 0.517 | OK |
| 8 | DL10170 | DE_NOVO_EX32_REFINED | 5NDZ_allosteric | high_sp3_wedge | -8.693 | 0.667 | nan | 0.290 | 412.570 | 5.352 | 0.615 | 0.700 | OK |
| 9 | DN00464 | DE_NOVO_EX32_REFINED | 5NDD_orthosteric | crystal_contact_reproducer | -7.904 | 0.938 | 0.333 | 0.344 | 320.364 | 1.600 | 0.471 | 0.809 | AMBIGUOUS |
| 10 | DN00375 | DE_NOVO_EX32_REFINED | 5NDD_orthosteric | reference_adjacent | -7.821 | 0.938 | 0.333 | 0.355 | 304.365 | 2.845 | 0.353 | 0.744 | AMBIGUOUS |
| 11 | DN01763 | DE_NOVO_EX32_REFINED | 5NDD_orthosteric | dual_anchor | -6.398 | 0.938 | 0.667 | 0.278 | 316.353 | 2.047 | 0.444 | 0.905 | OK |
| 12 | DL08960 | DE_NOVO_EX32_REFINED | 5NDD_orthosteric | dual_anchor | -8.621 | 0.938 | 0.667 | 0.375 | 318.369 | 2.288 | 0.500 | 0.728 | OK |
| 13 | DL12771 | DE_NOVO_EX32_REFINED | 5NDD_orthosteric | dual_anchor | -8.731 | 0.812 | 0.667 | 0.416 | 294.391 | 2.044 | 0.824 | 0.604 | AMBIGUOUS |
| 14 | DN01005 | DE_NOVO_EX32_REFINED | 5NDD_orthosteric | high_sp3_wedge | -8.859 | 0.812 | 0.000 | 0.403 | 310.365 | 1.962 | 0.588 | 0.872 | AMBIGUOUS |
| 15 | DL11846 | DE_NOVO_EX32_REFINED | 5NDD_orthosteric | high_sp3_wedge | -9.255 | 0.812 | 0.333 | 0.441 | 298.379 | 2.319 | 0.812 | 0.623 | AMBIGUOUS |
| 16 | DL08779 | DE_NOVO_EX32_REFINED | 5NDD_orthosteric | dual_anchor | -6.315 | 1.000 | 0.667 | 0.275 | 322.401 | 3.130 | 0.556 | 0.573 | OK |
| 17 | DL12464 | DE_NOVO_EX32_REFINED | 5NDD_orthosteric | high_sp3_wedge | -7.190 | 0.812 | 0.333 | 0.288 | 348.439 | 2.146 | 0.800 | 0.747 | OK |
| 18 | DN01388 | DE_NOVO_EX32_REFINED | 5NDD_orthosteric | dual_anchor | -8.593 | 0.812 | 0.667 | 0.391 | 310.365 | 2.626 | 0.588 | 0.839 | OK |
| 19 | DN00079 | DE_NOVO_EX32_REFINED | 5NDD_orthosteric | reference_adjacent | -7.423 | 0.812 | 0.333 | 0.323 | 316.332 | 2.955 | 0.294 | 0.854 | AMBIGUOUS |
| 20 | DN00058 | DE_NOVO_EX32_REFINED | 5NDD_orthosteric | reference_adjacent | -7.532 | 0.875 | 0.333 | 0.359 | 284.315 | 2.550 | 0.250 | 0.771 | OK |

### Why each was selected

**1. RX05505** — NATURAL_PRODUCT_OR_V1_HIT, 5NDD, crystal_contact_reproducer. competitive orthosteric wedge; blocks tethered-ligand docking. Teaches: whether reproducing the AZ8838 contact set predicts activity. Uncertainty: antagonist vs biased agonist undetermined by docking.
**2. RX00387** — REAL_ANALOGUE_PUBCHEM, 5NDD, crystal_contact_reproducer. competitive orthosteric wedge; blocks tethered-ligand docking. Teaches: whether reproducing the AZ8838 contact set predicts activity. Uncertainty: antagonist vs biased agonist undetermined by docking.
**3. RX02990** — NATURAL_PRODUCT_OR_V1_HIT, 5NDD, crystal_contact_reproducer. competitive orthosteric wedge; blocks tethered-ligand docking. Teaches: whether reproducing the AZ8838 contact set predicts activity. Uncertainty: antagonist vs biased agonist undetermined by docking.
**4. RX01677** — NATURAL_PRODUCT_OR_V1_HIT, 5NDD, crystal_contact_reproducer. competitive orthosteric wedge; blocks tethered-ligand docking. Teaches: whether reproducing the AZ8838 contact set predicts activity. Uncertainty: antagonist vs biased agonist undetermined by docking.
**5. RX02731** — APPROVED_REPURPOSING, 5NDD, general_binder. competitive orthosteric wedge; blocks tethered-ligand docking. Teaches: general structure-activity information. Uncertainty: antagonist vs biased agonist undetermined by docking.
**6. DN00100** — DE_NOVO_EX32_REFINED, 5NDZ, allosteric_hedge. extrahelical negative allosteric modulation of TM2-4. Teaches: whether the allosteric site is a viable fallback mechanism. Uncertainty: antagonist vs biased agonist undetermined by docking.
**7. DL13598** — DE_NOVO_EX32_REFINED, 5NDZ, allosteric_hedge. extrahelical negative allosteric modulation of TM2-4. Teaches: whether the allosteric site is a viable fallback mechanism. Uncertainty: antagonist vs biased agonist undetermined by docking.
**8. DL10170** — DE_NOVO_EX32_REFINED, 5NDZ, high_sp3_wedge. extrahelical negative allosteric modulation of TM2-4. Teaches: whether 3D sp3-rich cores improve on the flat reference chemotype. Uncertainty: antagonist vs biased agonist undetermined by docking.
**9. DN00464** — DE_NOVO_EX32_REFINED, 5NDD, crystal_contact_reproducer. competitive orthosteric wedge; blocks tethered-ligand docking. Teaches: whether reproducing the AZ8838 contact set predicts activity. Uncertainty: stereochemistry unassigned in the design; docked isomer is one of several.
**10. DN00375** — DE_NOVO_EX32_REFINED, 5NDD, reference_adjacent. competitive orthosteric wedge; blocks tethered-ligand docking. Teaches: whether AZ8838-like chemistry reproduces in our hands. Uncertainty: stereochemistry unassigned in the design; docked isomer is one of several.
**11. DN01763** — DE_NOVO_EX32_REFINED, 5NDD, dual_anchor. competitive orthosteric wedge; blocks tethered-ligand docking. Teaches: whether two of three anchors suffice. Uncertainty: antagonist vs biased agonist undetermined by docking.
**12. DL08960** — DE_NOVO_EX32_REFINED, 5NDD, dual_anchor. competitive orthosteric wedge; blocks tethered-ligand docking. Teaches: whether two of three anchors suffice. Uncertainty: antagonist vs biased agonist undetermined by docking.
**13. DL12771** — DE_NOVO_EX32_REFINED, 5NDD, dual_anchor. competitive orthosteric wedge; blocks tethered-ligand docking. Teaches: whether two of three anchors suffice. Uncertainty: stereochemistry unassigned in the design; docked isomer is one of several.
**14. DN01005** — DE_NOVO_EX32_REFINED, 5NDD, high_sp3_wedge. competitive orthosteric wedge; blocks tethered-ligand docking. Teaches: whether 3D sp3-rich cores improve on the flat reference chemotype. Uncertainty: stereochemistry unassigned in the design; docked isomer is one of several.
**15. DL11846** — DE_NOVO_EX32_REFINED, 5NDD, high_sp3_wedge. competitive orthosteric wedge; blocks tethered-ligand docking. Teaches: whether 3D sp3-rich cores improve on the flat reference chemotype. Uncertainty: stereochemistry unassigned in the design; docked isomer is one of several.
**16. DL08779** — DE_NOVO_EX32_REFINED, 5NDD, dual_anchor. competitive orthosteric wedge; blocks tethered-ligand docking. Teaches: whether two of three anchors suffice. Uncertainty: antagonist vs biased agonist undetermined by docking.
**17. DL12464** — DE_NOVO_EX32_REFINED, 5NDD, high_sp3_wedge. competitive orthosteric wedge; blocks tethered-ligand docking. Teaches: whether 3D sp3-rich cores improve on the flat reference chemotype. Uncertainty: antagonist vs biased agonist undetermined by docking.
**18. DN01388** — DE_NOVO_EX32_REFINED, 5NDD, dual_anchor. competitive orthosteric wedge; blocks tethered-ligand docking. Teaches: whether two of three anchors suffice. Uncertainty: antagonist vs biased agonist undetermined by docking.
**19. DN00079** — DE_NOVO_EX32_REFINED, 5NDD, reference_adjacent. competitive orthosteric wedge; blocks tethered-ligand docking. Teaches: whether AZ8838-like chemistry reproduces in our hands. Uncertainty: stereochemistry unassigned in the design; docked isomer is one of several.
**20. DN00058** — DE_NOVO_EX32_REFINED, 5NDD, reference_adjacent. competitive orthosteric wedge; blocks tethered-ligand docking. Teaches: whether AZ8838-like chemistry reproduces in our hands. Uncertainty: antagonist vs biased agonist undetermined by docking.

## IDEAL_DE_NOVO_TOP5 — closest to the theoretical model

These answer *which designs best match the target profile*, not *which to buy*.

| cand_id | max_ifp_recovery | anchor_hbond_fraction | profile_fit | fsp3 | mw | clogp | qed | ideal_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DL13973 | 0.812 | 1.000 | 0.714 | 0.857 | 382.545 | 2.841 | 0.554 | 0.856 |
| DL13271 | 0.812 | 0.667 | 1.000 | 0.800 | 350.455 | 2.331 | 0.603 | 0.804 |
| DL13943 | 0.875 | 0.667 | 0.739 | 1.000 | 302.411 | 1.232 | 0.712 | 0.804 |
| DL11368 | 0.938 | 1.000 | 0.414 | 0.583 | 450.597 | 3.724 | 0.389 | 0.798 |
| DL11051 | 0.875 | 0.667 | 0.706 | 1.000 | 272.409 | 1.234 | 0.809 | 0.797 |

## Known weaknesses

- **The single approved drug on the list (rank 5, RESATORVID / TAK-242) is a TLR4 inhibitor**, not a PAR2 ligand. It is here because it scored, not because there is prior PAR2 evidence. Propranolol also scored strongly (IFP 0.938, two of three anchors, LE 0.448) but lost its slot to scaffold diversity — it is worth considering as a cheap, topically-formulated, human-exposed probe.
- **6 of 20 have unassigned stereocentres**, so the docked isomer is one of several.
- **Anchor calls are sampling-sensitive**: only 30 of 54 EX8 dual-anchor assignments survived re-docking at EX32, so roughly 44% were artefacts.
- **EX32 is a resampling, not an upgrade**: 194 molecules improved on Vina, 245 got worse.
- **Real compounds carry only EX8 evidence**, de novo carry EX32 — the two lanes are not strictly comparable, which is why real-compound slots were reserved rather than won.
- **PIGNet2 covers only batch-1 rows.** It also correlates 0.899 with Vina, so it was never independent evidence.
- The 5NDZ hedge (3 of 20) targets a site whose own crystal ligand forms **zero hydrogen bonds**, and whose reference antagonist AZ3451 shows incomplete, biphasic blockade of protease activation.
- **1,740 of 4,835 real compounds had no non-clashing pose** in the small 5NDD box, mostly on size grounds.

## Required next experiments

1. **Reference panel first** — AZ8838, AZ3451, C391, I-287, GB88, RWJ-50353, SLIGKV. Establish whether direct PAR2 antagonism blocks melanocore uptake at all. This is worth more than any molecule on this list.
2. Gq: calcium and IP1, in agonist mode first to prove silence.
3. **G12/13: p115-RhoGEF recruitment** — the pathway that must not be agonised.
4. β-arrestin-2 recruitment, to exclude GB88-like bias.
5. Keratinocyte melanocore-uptake assay. **Do not assume this capability exists in the current collaboration — verify it.**
