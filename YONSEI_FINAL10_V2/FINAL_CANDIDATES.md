# PAR2 candidate hand-over — computationally prioritised designs

Generated 2026-09-04T14:51:13.243716+00:00

**These are COMPUTATIONALLY PRIORITISED PAR2 CANDIDATES, not demonstrated antagonists.** Static docking cannot separate an antagonist from a biased agonist. The decisive experiments are the functional assays, above all Galpha-12/13 -> RhoA: a compound that blocks Gq but agonises G12/13 would still drive the actin machinery that engulfs melanocores.

## Coverage

- Designs with docking evidence: **11485**
- Ligand-pocket rows: 12341 (5NDD_orthosteric 9066, 5NDZ_allosteric 3275)
- By batch: {'batch2': 8899, 'batch1': 3442}
- Metrics used: best_vina_affinity, ligand_efficiency, pignet2_best, best_CNNscore, best_CNNaffinity, best_CNN_VS, max_ifp_recovery
- PIGNet2 available: True

## Why interaction fingerprints carry the weight

Measured Spearman correlations inside 5NDD showed the scoring functions are not independent: Vina and ligand efficiency correlate -0.958, Vina and PIGNet2 0.899, CNNscore and CNN_VS 0.988. Reference-antagonist interaction recovery correlates |r| <= 0.19 with every other metric, so it is the only orthogonal evidence and was given its own family rather than being outvoted by five correlated views of the same signal.

## The AZ8838 polar-anchor signature

The repaired crystallographic reference shows AZ8838 donating two hydrogen bonds, to TYR:82 (2.475 A) and HIS:135 (2.63 A). Designs reproducing hydrogen bonds to both principal anchors (ASP:228 and HIS:135) are the ones that anchor through specific polar contacts rather than greasy surface.

- 5NDD designs hydrogen-bonding at least one anchor: **1298**
- Hydrogen-bonding **both** anchors: **62**
- Flagged for agonist-mimicry geometry: 9 (flagged for functional testing, never silently removed)
- Pareto front: 130

## Dual-anchor designs, best first

| consensus_rank | cand_id | denovo_family | best_vina_affinity | best_CNNscore | pignet2_best | max_ifp_recovery | ifp_hbonds | ligand_efficiency | mw | clogp | fsp3 | qed | profile_fit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 15 | DN01763 | orthosteric | -6.384 | 0.665 | -2.568 | 0.938 | 2 | 0.278 | 316.353 | 2.047 | 0.444 | 0.905 | 0.935 |
| 84 | DN02439 | orthosteric | -6.466 | 0.575 | -3.889 | 0.875 | 2 | 0.269 | 340.415 | 2.194 | 0.611 | 0.806 | 0.857 |
| 101 | DN00710 | orthosteric | -7.270 | 0.526 | -3.172 | 0.938 | 2 | 0.316 | 320.360 | 3.178 | 0.444 | 0.794 | 0.788 |
| 136 | DN02427 | orthosteric | -7.592 | 0.528 | -5.508 | 0.938 | 4 | 0.362 | 298.354 | 1.711 | 0.625 | 0.791 | 0.775 |
| 140 | DL08218 | exploratory | -8.170 | 0.669 |  | 0.875 | 2 | 0.454 | 260.374 | 1.319 | 1.000 | 0.697 | 0.719 |
| 247 | DL05752 | orthosteric | -4.782 | 0.704 |  | 0.938 | 2 | 0.177 | 370.376 | 3.948 | 0.238 | 0.524 | 0.710 |
| 268 | DL09038 | orthosteric | -6.613 | 0.580 |  | 0.938 | 2 | 0.315 | 316.781 | 1.369 | 0.600 | 0.764 | 0.789 |
| 313 | DN01742 | orthosteric | -7.046 | 0.540 | -3.959 | 0.812 | 3 | 0.306 | 316.401 | 2.678 | 0.500 | 0.810 | 0.810 |
| 530 | DL13973 | orthosteric | -6.493 | 0.705 |  | 0.812 | 3 | 0.240 | 382.545 | 2.841 | 0.857 | 0.554 | 0.714 |
| 571 | DL13365 | orthosteric | -8.313 | 0.621 |  | 0.812 | 2 | 0.438 | 274.401 | 1.710 | 1.000 | 0.661 | 0.624 |
| 839 | DL09663 | orthosteric | -7.044 | 0.336 |  | 0.938 | 3 | 0.261 | 384.488 | 3.211 | 0.714 | 0.609 | 0.715 |
| 843 | DL08921 | orthosteric | -8.193 | 0.555 |  | 0.812 | 3 | 0.410 | 272.256 | 2.482 | 0.133 | 0.700 | 0.673 |
| 913 | DL10726 | orthosteric | -4.105 | 0.735 |  | 0.812 | 3 | 0.178 | 389.242 | 1.748 | 0.625 | 0.727 | 0.750 |
| 1075 | DN01673 | exploratory | -7.520 | 0.605 | -5.066 | 0.750 | 2 | 0.501 | 206.309 | 1.523 | 0.538 | 0.797 | 0.750 |
| 1455 | DL12794 | orthosteric | -7.114 | 0.456 |  | 0.875 | 2 | 0.309 | 318.373 | 1.149 | 0.412 | 0.555 | 0.516 |
| 1494 | DL08933 | exploratory | -6.868 | 0.529 |  | 0.875 | 2 | 0.275 | 352.383 | 1.495 | 0.500 | 0.596 | 0.499 |
| 1591 | DL12010 | orthosteric | -6.205 | 0.510 |  | 0.812 | 2 | 0.345 | 256.410 | 1.160 | 1.000 | 0.793 | 0.693 |
| 1664 | DL07012 | exploratory | -7.584 | 0.366 |  | 0.812 | 2 | 0.345 | 332.868 | 2.403 | 0.765 | 0.516 | 0.716 |
| 1696 | DN00318 | orthosteric | -2.254 | 0.496 | -0.227 | 0.875 | 2 | 0.098 | 314.341 | 3.240 | 0.294 | 0.754 | 0.746 |
| 1724 | DL10018 | orthosteric | -5.571 | 0.639 |  | 0.688 | 2 | 0.232 | 352.818 | 1.769 | 0.471 | 0.674 | 0.839 |

## Top 20 by consensus in the primary 5NDD lane

| consensus_rank | cand_id | denovo_family | best_vina_affinity | best_CNNscore | pignet2_best | max_ifp_recovery | ifp_hbonds | ligand_efficiency | mw | clogp | fsp3 | qed | profile_fit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | DN00464 | orthosteric | -7.904 | 0.768 | -4.190 | 0.938 | 2 | 0.344 | 320.364 | 1.600 | 0.471 | 0.809 | 0.943 |
| 2 | DN00361 | orthosteric | -8.794 | 0.849 | -4.379 | 0.875 | 0 | 0.366 | 328.368 | 1.291 | 0.389 | 0.885 | 0.924 |
| 3 | DN00375 | orthosteric | -8.570 | 0.770 | -5.711 | 0.938 | 1 | 0.390 | 304.365 | 2.845 | 0.353 | 0.744 | 0.779 |
| 4 | DN01387 | orthosteric | -8.314 | 0.657 | -5.176 | 0.875 | 1 | 0.378 | 310.365 | 2.626 | 0.588 | 0.839 | 0.891 |
| 5 | DN00626 | orthosteric | -7.889 | 0.693 | -3.816 | 0.875 | 1 | 0.359 | 306.337 | 1.730 | 0.438 | 0.832 | 0.916 |
| 6 | DN00613 | orthosteric | -7.702 | 0.575 | -5.052 | 0.875 | 1 | 0.335 | 322.380 | 1.859 | 0.529 | 0.869 | 0.921 |
| 7 | DN00332 | orthosteric | -8.180 | 0.723 | -5.361 | 0.875 | 0 | 0.409 | 278.327 | 1.844 | 0.467 | 0.883 | 0.757 |
| 8 | DN00075 | orthosteric | -8.457 | 0.622 | -4.932 | 0.875 | 1 | 0.384 | 304.317 | 3.304 | 0.294 | 0.861 | 0.817 |
| 9 | DN01597 | orthosteric | -7.531 | 0.617 | -5.459 | 0.875 | 1 | 0.301 | 352.402 | 2.529 | 0.526 | 0.738 | 0.875 |
| 10 | DL08660 | orthosteric | -8.053 | 0.787 |  | 0.938 | 1 | 0.350 | 324.373 | 2.378 | 0.588 | 0.808 | 0.826 |
| 11 | DN01146 | orthosteric | -7.193 | 0.562 | -4.696 | 0.875 | 1 | 0.300 | 338.419 | 2.974 | 0.632 | 0.866 | 0.945 |
| 12 | DN00762 | orthosteric | -8.421 | 0.689 | -5.588 | 0.875 | 1 | 0.421 | 282.355 | 2.740 | 0.625 | 0.892 | 0.750 |
| 13 | DN02957 | orthosteric | -8.452 | 0.672 | -4.637 | 0.875 | 1 | 0.445 | 266.380 | 2.344 | 0.625 | 0.865 | 0.750 |
| 14 | DL11846 | orthosteric | -9.236 | 0.855 |  | 0.875 | 0 | 0.440 | 298.379 | 2.319 | 0.812 | 0.623 | 0.851 |
| 15 | DN01763 | orthosteric | -6.384 | 0.665 | -2.568 | 0.938 | 2 | 0.278 | 316.353 | 2.047 | 0.444 | 0.905 | 0.935 |
| 16 | DL12777 | orthosteric | -8.590 | 0.865 |  | 0.875 | 1 | 0.390 | 314.422 | 2.200 | 0.824 | 0.580 | 0.807 |
| 17 | DN01522 | orthosteric | -7.916 | 0.470 | -5.528 | 0.875 | 0 | 0.344 | 322.376 | 2.779 | 0.500 | 0.661 | 0.914 |
| 18 | DN01726 | orthosteric | -9.040 | 0.654 | -5.909 | 0.875 | 0 | 0.476 | 264.296 | 2.914 | 0.467 | 0.606 | 0.750 |
| 19 | DL06438 | orthosteric | -7.143 | 0.696 |  | 0.875 | 2 | 0.298 | 334.412 | 3.202 | 0.526 | 0.639 | 0.936 |
| 20 | DN01099 | orthosteric | -7.509 | 0.504 | -5.653 | 0.875 | 0 | 0.326 | 320.360 | 2.555 | 0.389 | 0.661 | 0.911 |

## Similarity-search seeds

34 seeds across 34 distinct Murcko scaffolds and 34 clusters ({'5NDD_orthosteric': 26, '5NDZ_allosteric': 8}).

| seed_id | cand_id | pocket | family | postdock_rank | cluster_size | ifp_recovery | best_affinity | MW | cLogP | fsp3 | QED | novelty_band |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SEED01 | DN00464 | 5NDD_orthosteric | orthosteric | 1 | 2 | 0.938 | -7.904 | 320.364 | 1.600 | 0.471 | 0.809 | moderate_scaffold_hop |
| SEED02 | DN00361 | 5NDD_orthosteric | orthosteric | 2 | 2 | 0.875 | -8.794 | 328.368 | 1.291 | 0.389 | 0.885 | novel_chemotype |
| SEED03 | DN00375 | 5NDD_orthosteric | orthosteric | 3 | 1 | 0.938 | -8.570 | 304.365 | 2.845 | 0.353 | 0.744 | close_to_reference_antagonist |
| SEED04 | DN01387 | 5NDD_orthosteric | orthosteric | 4 | 8 | 0.875 | -8.314 | 310.365 | 2.626 | 0.588 | 0.839 | novel_chemotype |
| SEED05 | DN00613 | 5NDD_orthosteric | orthosteric | 6 | 1 | 0.875 | -7.702 | 322.380 | 1.859 | 0.529 | 0.869 | moderate_scaffold_hop |
| SEED06 | DN00075 | 5NDD_orthosteric | orthosteric | 8 | 1 | 0.875 | -8.457 | 304.317 | 3.304 | 0.294 | 0.861 | moderate_scaffold_hop |
| SEED07 | DN01597 | 5NDD_orthosteric | orthosteric | 9 | 1 | 0.875 | -7.531 | 352.402 | 2.529 | 0.526 | 0.738 | moderate_scaffold_hop |
| SEED08 | DL08660 | 5NDD_orthosteric | orthosteric | 10 | 1 | 0.938 | -8.053 | 324.373 | 2.378 | 0.588 | 0.808 | novel_chemotype |
| SEED09 | DN01146 | 5NDD_orthosteric | orthosteric | 11 | 2 | 0.875 | -7.193 | 338.419 | 2.974 | 0.632 | 0.866 | novel_chemotype |
| SEED10 | DN02957 | 5NDD_orthosteric | orthosteric | 13 | 1 | 0.875 | -8.452 | 266.380 | 2.344 | 0.625 | 0.865 | moderate_scaffold_hop |
| SEED11 | DL11846 | 5NDD_orthosteric | orthosteric | 14 | 3 | 0.875 | -9.236 | 298.379 | 2.319 | 0.812 | 0.623 | novel_chemotype |
| SEED12 | DN01763 | 5NDD_orthosteric | orthosteric | 15 | 1 | 0.938 | -6.384 | 316.353 | 2.047 | 0.444 | 0.905 | novel_chemotype |
| SEED13 | DL12777 | 5NDD_orthosteric | orthosteric | 16 | 5 | 0.875 | -8.590 | 314.422 | 2.200 | 0.824 | 0.580 | novel_chemotype |
| SEED14 | DN01522 | 5NDD_orthosteric | orthosteric | 17 | 1 | 0.875 | -7.916 | 322.376 | 2.779 | 0.500 | 0.661 | novel_chemotype |
| SEED15 | DN01726 | 5NDD_orthosteric | orthosteric | 18 | 1 | 0.875 | -9.040 | 264.296 | 2.914 | 0.467 | 0.606 | moderate_scaffold_hop |
| SEED16 | DL06438 | 5NDD_orthosteric | orthosteric | 19 | 6 | 0.875 | -7.143 | 334.412 | 3.202 | 0.526 | 0.639 | novel_chemotype |
| SEED17 | DN01099 | 5NDD_orthosteric | orthosteric | 20 | 3 | 0.875 | -7.509 | 320.360 | 2.555 | 0.389 | 0.661 | novel_chemotype |
| SEED18 | DN01682 | 5NDD_orthosteric | orthosteric | 21 | 4 | 0.875 | -6.126 | 328.380 | 2.200 | 0.647 | 0.867 | moderate_scaffold_hop |
| SEED19 | DN02978 | 5NDD_orthosteric | orthosteric | 27 | 1 | 0.875 | -8.424 | 320.316 | 1.772 | 0.294 | 0.803 | novel_chemotype |
| SEED20 | DN01394 | 5NDD_orthosteric | orthosteric | 29 | 1 | 0.938 | -7.384 | 324.392 | 2.485 | 0.611 | 0.873 | novel_chemotype |
| SEED21 | DN02825 | 5NDD_orthosteric | orthosteric | 30 | 1 | 0.812 | -8.137 | 346.221 | 2.846 | 0.643 | 0.823 | novel_chemotype |
| SEED22 | DL05321 | 5NDD_orthosteric | orthosteric | 36 | 1 | 0.875 | -7.570 | 336.428 | 2.956 | 0.632 | 0.781 | novel_chemotype |
| SEED23 | DL12213 | 5NDD_orthosteric | orthosteric | 37 | 1 | 0.875 | -7.201 | 280.364 | 1.818 | 0.688 | 0.611 | novel_chemotype |
| SEED24 | DL05657 | 5NDD_orthosteric | orthosteric | 39 | 1 | 0.875 | -7.787 | 294.347 | 1.726 | 0.562 | 0.827 | novel_chemotype |
| SEED25 | DN00486 | 5NDD_orthosteric | orthosteric | 43 | 4 | 0.875 | -5.477 | 362.397 | 2.277 | 0.400 | 0.854 | novel_chemotype |
| SEED26 | DN00283 | 5NDD_orthosteric | exploratory | 44 | 2 | 0.812 | -7.889 | 262.305 | 2.682 | 0.400 | 0.649 | novel_chemotype |
| SEEDZ01 | DN00595 | 5NDZ_allosteric | allosteric | 1 | 2 | 0.667 | -7.254 | 290.403 | 4.096 | 0.667 | 0.907 | moderate_scaffold_hop |
| SEEDZ02 | DN01870 | 5NDZ_allosteric | allosteric | 2 | 1 | 0.750 | -8.067 | 332.447 | 4.637 | 0.364 | 0.756 | novel_chemotype |
| SEEDZ03 | DN00029 | 5NDZ_allosteric | exploratory | 3 | 1 | 0.583 | -8.223 | 328.408 | 4.131 | 0.400 | 0.886 | novel_chemotype |
| SEEDZ04 | DN02003 | 5NDZ_allosteric | allosteric | 4 | 1 | 0.667 | -7.493 | 434.306 | 3.301 | 0.476 | 0.712 | moderate_scaffold_hop |
| SEEDZ05 | DN02096 | 5NDZ_allosteric | allosteric | 5 | 1 | 0.667 | -7.277 | 270.376 | 3.829 | 0.471 | 0.887 | novel_chemotype |
| SEEDZ06 | DN00900 | 5NDZ_allosteric | allosteric | 6 | 1 | 0.750 | -8.189 | 324.464 | 4.881 | 0.500 | 0.870 | moderate_scaffold_hop |
| SEEDZ07 | DN01355 | 5NDZ_allosteric | allosteric | 7 | 1 | 0.667 | -7.524 | 327.468 | 4.924 | 0.571 | 0.847 | moderate_scaffold_hop |
| SEEDZ08 | DN01718 | 5NDZ_allosteric | allosteric | 8 | 1 | 0.750 | -7.524 | 446.273 | 3.102 | 0.286 | 0.703 | moderate_scaffold_hop |

## Real purchasable analogues retrieved

521 unique real compounds from public databases, 27 seeds with at least one hit.

Bands: {'below_band': 509, 'broader_neighbour': 11, 'close_analogue': 1}

Closest real matter:

| seed_id | source_database | source_compound_id | source_name | tanimoto_to_seed | same_scaffold_as_seed | mcs_similarity |
| --- | --- | --- | --- | --- | --- | --- |
| SEED26 | PubChem | CID54697518 | Phaeochromycin C | 0.714 | False | 0.840 |
| SEED26 | PubChem | CID163105500 | 5-[(5-Hydroxy-6-oxopyran-2-yl)methyl]-2-propylchromen-4-one | 0.680 | False | 0.840 |
| SEED03 | PubChem | CID132116559 | US10550089, Example 9 | 0.615 | True | 0.625 |
| SEED03 | PubChem | CID132116808 | US10550089, Example 8 | 0.615 | True | 0.625 |
| SEED03 | PubChem | CID132116556 | (4-fluoro-2-prop-1-enylphenyl)-(1H-imidazol-2-yl)methanol | 0.615 | True | 0.625 |
| SEED26 | PubChem | CID11673192 | Phaeochromycin E | 0.612 | False | 0.577 |
| SEED03 | PubChem | CID80284548 | (4-fluoro-2-methylphenyl)-(1H-imidazol-2-yl)methanol | 0.580 | True | 0.682 |
| SEED03 | PubChem | CID80284554 | (2,4-difluorophenyl)-(1H-imidazol-2-yl)methanol | 0.571 | True | 0.609 |
| SEEDZ06 | PubChem | CID59709303 | 4-Methoxy-2-propan-2-ylquinoline | 0.565 | False | 0.625 |
| SEEDZ01 | PubChem | CID221882 | 1-(1,3-Dioxaindan-5-yl)ethan-1-ol | 0.564 | False | 0.500 |
| SEED24 | PubChem | CID11041857 | 6-Hydroxy-2-propyl-4h-chromen-4-one | 0.553 | False | 0.560 |
| SEEDZ06 | PubChem | CID101541016 | (R)-(4-methoxyquinolin-2-yl)-phenylmethanol | 0.551 | False | 0.419 |
| SEED03 | PubChem | CID80283461 | (5-fluoro-2-methylphenyl)-(1H-imidazol-2-yl)methanol | 0.549 | True | 0.609 |
| SEEDZ06 | PubChem | CID156769018 | 2-Cyclohexyl-4-methoxyquinoline | 0.540 | False | 0.400 |
| SEED03 | PubChem | CID80284551 | (2,5-difluorophenyl)-(1H-imidazol-2-yl)methanol | 0.540 | True | 0.542 |

**Vendor, catalogue ID, price and stock are PENDING for every row.** No catalogue was queried, so none of these is confirmed purchasable.

## What has NOT been done

- No EX32 precision redocking of the finalists.
- No Boltz-2 co-folding and no molecular dynamics.
- No vendor availability check.
- No wet-lab evidence of any kind.
- Part of the de novo library was still docking when this was written.

## Required next experiments

1. Gq: calcium mobilisation and IP1, agonist-mode first to prove silence.
2. G12/13: p115-RhoGEF recruitment - the pathway that must not be agonised.
3. beta-arrestin-2 recruitment, to exclude GB88-like biased agonism.
4. Keratinocyte melanocore-uptake assay as the biological endpoint.
