# FINAL TOP 20 — computationally prioritised PAR2 candidates

Generated 2026-09-05T19:48:18.851767+00:00

## READ THIS FIRST

**We have NOT shown that direct PAR2 antagonism reduces melanocore uptake.** The historical pigmentation evidence used RWJ-50353, a broad serine-protease inhibitor, not a selective PAR2 antagonist, and P2L-003 has never been tested on a pigmentation endpoint. That gap is a LARGER uncertainty than the difference between rank 3 and rank 12 on this list.

These are **COMPUTATIONALLY PRIORITISED PAR2 CANDIDATES**, not demonstrated antagonists and not pigmentation inhibitors. Static docking cannot separate an antagonist from a biased agonist. The decisive counter-screen is **G12/13 -> RhoA**: a compound that blocks Gq but agonises G12/13 would still drive the actin machinery that engulfs melanocores.

PAR2 blockade also cannot abolish pigment transfer outright - filopodial conduits, cytophagocytosis and baseline phagocytosis are PAR2-independent. The realistic aim is maximal suppression of the PAR2-dependent melanocore route.

## Provenance of this panel

- Screened universe: **16,314 of 16,314** routed jobs over **14,825** molecules, 9 poses each
- Validity gates: 16314 rows -> parseable 16314 -> has_non_clashing_pose 14217 -> real_negative_affinity 14217 -> stereo_not_known_wrong 13989
- All 20 carry **EX32 precision evidence** (exhaustiveness 32, 9 modes)
- Unique Murcko scaffolds: **20/20**; clusters 19; interaction archetypes 6
- Pocket split: {'5NDD_orthosteric': 17, '5NDZ_allosteric': 3}
- Stereochemistry: {'OK': 12, 'AMBIGUOUS': 8} (molecules known to have been docked as the WRONG stereoisomer were excluded by gate)

## Sourceability - the honest position

**All 20 require synthesis. None is confirmed purchasable.** Live vendor, catalogue, price and stock lookups could not run in this session, and the retrieved-analogue lane found no purchasable neighbour above Tanimoto 0.80 for any seed. Vendor fields read PENDING throughout - that is a real gap, not a formatting placeholder.

## The panel

| FINAL_RANK | cand_id | pocket | primary_archetype | best_vina_affinity | best_CNNscore | max_ifp_recovery | anchor_hbond_fraction | ligand_efficiency | mw | clogp | fsp3 | qed | stereo_flag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | DN00100 | 5NDZ_allosteric | allosteric_hedge | -8.155 | 0.827 | 0.750 | nan | 0.355 | 306.361 | 3.699 | 0.150 | 0.799 | OK |
| 2 | DL13598 | 5NDZ_allosteric | allosteric_hedge | -9.356 | 0.893 | 0.750 | nan | 0.267 | 478.585 | 5.030 | 0.414 | 0.517 | OK |
| 3 | DL10170 | 5NDZ_allosteric | high_sp3_wedge | -8.693 | 0.802 | 0.667 | nan | 0.290 | 412.570 | 5.352 | 0.615 | 0.700 | OK |
| 4 | DN00464 | 5NDD_orthosteric | crystal_contact_reproducer | -7.904 | 0.768 | 0.938 | 0.333 | 0.344 | 320.364 | 1.600 | 0.471 | 0.809 | AMBIGUOUS |
| 5 | DN01763 | 5NDD_orthosteric | dual_anchor | -6.398 | 0.649 | 0.938 | 0.667 | 0.278 | 316.353 | 2.047 | 0.444 | 0.905 | OK |
| 6 | DN00375 | 5NDD_orthosteric | reference_adjacent | -7.821 | 0.801 | 0.938 | 0.333 | 0.355 | 304.365 | 2.845 | 0.353 | 0.744 | AMBIGUOUS |
| 7 | DN00830 | 5NDD_orthosteric | crystal_contact_reproducer | -7.350 | 0.644 | 0.938 | 0.333 | 0.306 | 328.343 | 1.798 | 0.222 | 0.804 | AMBIGUOUS |
| 8 | DL11488 | 5NDD_orthosteric | crystal_contact_reproducer | -8.820 | 0.819 | 0.875 | 0.333 | 0.420 | 296.407 | 3.149 | 0.706 | 0.481 | OK |
| 9 | DN01844 | 5NDD_orthosteric | crystal_contact_reproducer | -2.478 | 0.591 | 0.938 | 0.333 | 0.099 | 346.358 | 1.826 | 0.389 | 0.800 | AMBIGUOUS |
| 10 | DL03617 | 5NDD_orthosteric | crystal_contact_reproducer | -8.938 | 0.784 | 0.875 | 0.000 | 0.406 | 306.402 | 3.424 | 0.556 | 0.818 | OK |
| 11 | DL08960 | 5NDD_orthosteric | dual_anchor | -8.621 | 0.523 | 0.938 | 0.667 | 0.375 | 318.369 | 2.288 | 0.500 | 0.728 | OK |
| 12 | DL12771 | 5NDD_orthosteric | dual_anchor | -8.731 | 0.717 | 0.812 | 0.667 | 0.416 | 294.391 | 2.044 | 0.824 | 0.604 | AMBIGUOUS |
| 13 | DN01005 | 5NDD_orthosteric | high_sp3_wedge | -8.859 | 0.643 | 0.812 | 0.000 | 0.403 | 310.365 | 1.962 | 0.588 | 0.872 | AMBIGUOUS |
| 14 | DL12464 | 5NDD_orthosteric | high_sp3_wedge | -7.190 | 0.519 | 0.812 | 0.333 | 0.288 | 348.439 | 2.146 | 0.800 | 0.747 | OK |
| 15 | DL11846 | 5NDD_orthosteric | high_sp3_wedge | -9.255 | 0.856 | 0.812 | 0.333 | 0.441 | 298.379 | 2.319 | 0.812 | 0.623 | AMBIGUOUS |
| 16 | DN00079 | 5NDD_orthosteric | reference_adjacent | -7.423 | 0.650 | 0.812 | 0.333 | 0.323 | 316.332 | 2.955 | 0.294 | 0.854 | AMBIGUOUS |
| 17 | DN01388 | 5NDD_orthosteric | dual_anchor | -8.593 | 0.577 | 0.812 | 0.667 | 0.391 | 310.365 | 2.626 | 0.588 | 0.839 | OK |
| 18 | DN00058 | 5NDD_orthosteric | reference_adjacent | -7.532 | 0.780 | 0.875 | 0.333 | 0.359 | 284.315 | 2.550 | 0.250 | 0.771 | OK |
| 19 | DL07822 | 5NDD_orthosteric | dual_anchor | -7.983 | 0.640 | 0.938 | 0.667 | 0.333 | 334.368 | 1.288 | 0.500 | 0.782 | OK |
| 20 | DN00041 | 5NDD_orthosteric | compact_efficient | -8.938 | 0.813 | 0.812 | 0.000 | 0.447 | 276.307 | 3.418 | 0.312 | 0.910 | OK |

### Why each was selected

**1. DN00100** (5NDZ, allosteric_hedge) — extrahelical negative allosteric modulation of TM2-4. Whether the allosteric site is a viable fallback mechanism. Uncertainty: antagonist vs biased agonist undetermined by docking.
**2. DL13598** (5NDZ, allosteric_hedge) — extrahelical negative allosteric modulation of TM2-4. Whether the allosteric site is a viable fallback mechanism. Uncertainty: antagonist vs biased agonist undetermined by docking.
**3. DL10170** (5NDZ, high_sp3_wedge) — extrahelical negative allosteric modulation of TM2-4. Whether 3d sp3-rich cores improve on the flat reference chemotype. Uncertainty: antagonist vs biased agonist undetermined by docking.
**4. DN00464** (5NDD, crystal_contact_reproducer) — competitive orthosteric wedge; blocks tethered-ligand docking. Whether reproducing the az8838 contact set predicts activity. Uncertainty: stereochemistry unassigned in the design; docked isomer is one of several.
**5. DN01763** (5NDD, dual_anchor) — competitive orthosteric wedge; blocks tethered-ligand docking. Whether two of three anchors suffice. Uncertainty: antagonist vs biased agonist undetermined by docking.
**6. DN00375** (5NDD, reference_adjacent) — competitive orthosteric wedge; blocks tethered-ligand docking. Whether az8838-like chemistry reproduces in our hands. Uncertainty: stereochemistry unassigned in the design; docked isomer is one of several.
**7. DN00830** (5NDD, crystal_contact_reproducer) — competitive orthosteric wedge; blocks tethered-ligand docking. Whether reproducing the az8838 contact set predicts activity. Uncertainty: stereochemistry unassigned in the design; docked isomer is one of several.
**8. DL11488** (5NDD, crystal_contact_reproducer) — competitive orthosteric wedge; blocks tethered-ligand docking. Whether reproducing the az8838 contact set predicts activity. Uncertainty: antagonist vs biased agonist undetermined by docking.
**9. DN01844** (5NDD, crystal_contact_reproducer) — competitive orthosteric wedge; blocks tethered-ligand docking. Whether reproducing the az8838 contact set predicts activity. Uncertainty: stereochemistry unassigned in the design; docked isomer is one of several.
**10. DL03617** (5NDD, crystal_contact_reproducer) — competitive orthosteric wedge; blocks tethered-ligand docking. Whether reproducing the az8838 contact set predicts activity. Uncertainty: antagonist vs biased agonist undetermined by docking.
**11. DL08960** (5NDD, dual_anchor) — competitive orthosteric wedge; blocks tethered-ligand docking. Whether two of three anchors suffice. Uncertainty: antagonist vs biased agonist undetermined by docking.
**12. DL12771** (5NDD, dual_anchor) — competitive orthosteric wedge; blocks tethered-ligand docking. Whether two of three anchors suffice. Uncertainty: stereochemistry unassigned in the design; docked isomer is one of several.
**13. DN01005** (5NDD, high_sp3_wedge) — competitive orthosteric wedge; blocks tethered-ligand docking. Whether 3d sp3-rich cores improve on the flat reference chemotype. Uncertainty: stereochemistry unassigned in the design; docked isomer is one of several.
**14. DL12464** (5NDD, high_sp3_wedge) — competitive orthosteric wedge; blocks tethered-ligand docking. Whether 3d sp3-rich cores improve on the flat reference chemotype. Uncertainty: antagonist vs biased agonist undetermined by docking.
**15. DL11846** (5NDD, high_sp3_wedge) — competitive orthosteric wedge; blocks tethered-ligand docking. Whether 3d sp3-rich cores improve on the flat reference chemotype. Uncertainty: stereochemistry unassigned in the design; docked isomer is one of several.
**16. DN00079** (5NDD, reference_adjacent) — competitive orthosteric wedge; blocks tethered-ligand docking. Whether az8838-like chemistry reproduces in our hands. Uncertainty: stereochemistry unassigned in the design; docked isomer is one of several.
**17. DN01388** (5NDD, dual_anchor) — competitive orthosteric wedge; blocks tethered-ligand docking. Whether two of three anchors suffice. Uncertainty: antagonist vs biased agonist undetermined by docking.
**18. DN00058** (5NDD, reference_adjacent) — competitive orthosteric wedge; blocks tethered-ligand docking. Whether az8838-like chemistry reproduces in our hands. Uncertainty: antagonist vs biased agonist undetermined by docking.
**19. DL07822** (5NDD, dual_anchor) — competitive orthosteric wedge; blocks tethered-ligand docking. Whether two of three anchors suffice. Uncertainty: antagonist vs biased agonist undetermined by docking.
**20. DN00041** (5NDD, compact_efficient) — competitive orthosteric wedge; blocks tethered-ligand docking. Whether a small efficient binder can hold the occluded subpocket. Uncertainty: antagonist vs biased agonist undetermined by docking.

## IDEAL_DE_NOVO_TOP5 - closest to the theoretical model

These answer 'which designs best match the target profile', NOT 'which should be bought'. They are ranked on interaction geometry, anchor satisfaction, property fit and 3D character.

| cand_id | max_ifp_recovery | anchor_hbond_fraction | profile_fit | fsp3 | mw | clogp | qed | ideal_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DL13973 | 0.812 | 1.000 | 0.714 | 0.857 | 382.545 | 2.841 | 0.554 | 0.856 |
| DL13271 | 0.812 | 0.667 | 1.000 | 0.800 | 350.455 | 2.331 | 0.603 | 0.804 |
| DL13943 | 0.875 | 0.667 | 0.739 | 1.000 | 302.411 | 1.232 | 0.712 | 0.804 |
| DL11368 | 0.938 | 1.000 | 0.414 | 0.583 | 450.597 | 3.724 | 0.389 | 0.798 |
| DL11051 | 0.875 | 0.667 | 0.706 | 1.000 | 272.409 | 1.234 | 0.809 | 0.797 |

## Known weaknesses of this panel

- **Rank 9 (DN01844) has weak physics**: Vina -2.478 and ligand efficiency 0.099. It entered on interaction geometry alone (IFP 0.938). Treat it as an archetype probe, not a likely binder.
- **8 of 20 have AMBIGUOUS stereochemistry** - the generator never assigned those centres, so the docked isomer is one of several possibilities.
- **Anchor calls are sampling-sensitive**: only 30 of 54 EX8 dual-anchor assignments survived re-docking at EX32, so roughly 44% were artefacts. Anchor fractions here come from EX32 where available.
- **EX32 is a resampling, not an upgrade**: across the refined set 194 molecules improved on Vina and 245 got worse.
- **PIGNet2 covers only batch-1 rows**, so the physics family is not like-for-like.
- The 5NDZ allosteric hedge (3 of 20) targets a site whose own crystal ligand forms **zero hydrogen bonds**, and whose reference antagonist AZ3451 shows incomplete, biphasic blockade of protease activation - a known liability for a pigmentation product.

## Required next experiments

1. **Reference panel first** - AZ8838, AZ3451, C391, I-287, GB88, RWJ-50353, SLIGKV. Establish whether direct PAR2 antagonism blocks melanocore uptake at all. This is worth more than any molecule on this list.
2. Gq: calcium and IP1, run in agonist mode first to prove silence.
3. G12/13: p115-RhoGEF recruitment - the pathway that must not be agonised.
4. beta-arrestin-2 recruitment to exclude GB88-like bias.
5. Keratinocyte melanocore-uptake assay as the biological endpoint. Do not assume this capability exists in the current collaboration; verify it.
