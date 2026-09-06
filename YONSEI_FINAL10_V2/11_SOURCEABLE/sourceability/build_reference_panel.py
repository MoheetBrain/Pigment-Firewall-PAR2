#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
build_reference_panel.py -- assemble PAR2_REFERENCE_PANEL_FOR_WAN.csv.

Joins the literature/mechanism annotation block (curated here, every claim
carrying its own source) to the machine-retrieved sourceability block produced
by ``YONSEI_FINAL10_V2/scripts/v2_sourceability.py`` on REFERENCE_PANEL_SEED.csv.

The two scientific cautions demanded by the brief are encoded as COLUMNS, not
buried in prose:

  biased_agonist_flag        GB88 is a BIASED agonist/antagonist, not a clean
                             antagonist -> it is labelled a COUNTER_CONTROL.
  par2_ligand_flag /
  selectivity_flag           RWJ-50353 is NOT a PAR2 ligand at all.  It is a
                             selective thrombin active-site inhibitor and is
                             labelled HISTORICAL_NON_SELECTIVE_CONTROL.

THIS FILE IS A CONTROL PANEL.  These compounds must NOT be used to fill the
final TOP20 candidate quota -- they are deliberately kept in a separate file.

Every annotation field below was either (a) retrieved by this session directly
from a public API (PubChem / RCSB / ChEMBL / Crossref / NCBI eutils), or
(b) taken from a literature-research pass whose citations were then spot-checked
against Crossref/PubMed.  Fields that could not be verified say NOT_VERIFIED and
say why.
"""

from __future__ import annotations

import csv
import datetime as _dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TODAY = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")
NV = "NOT_VERIFIED"

# ---------------------------------------------------------------------------
# Curated annotation block.  Keys match cand_id in REFERENCE_PANEL_SEED.csv.
# ---------------------------------------------------------------------------
ANN = {
    "AZ8838": dict(
        compound_name="AZ8838",
        aliases="(S)-(4-fluoro-2-propylphenyl)(1H-imidazol-2-yl)methanol; PDB ligand 8TZ",
        role_in_panel="ANTAGONIST_REFERENCE_ORTHOSTERIC",
        what_it_actually_is=(
            "Small-molecule PAR2 antagonist that occupies a fully occluded pocket near "
            "the extracellular surface formed by TM1-TM3, TM7 and ECL2. Cheng et al. "
            "2017 originally described this pocket as allosteric; later work "
            "(summarised in McIntosh 2020) reassigns it as the ORTHOSTERIC site, i.e. a "
            "competitive antagonist of the tethered ligand. Deliberately slow binding "
            "kinetics so it can compete with a tethered agonist."),
        target_and_site="PAR2 (F2RL1); buried extracellular/orthosteric pocket (TM1-3, TM7, ECL2)",
        arms_blocked="Ca2+ (Gq/11) and beta-arrestin-2 recruitment (PAR2-1321N1 cells)",
        is_clean_antagonist="YES",
        biased_agonist_flag="NO",
        par2_ligand_flag="YES",
        selectivity_flag="PAR2-directed",
        counter_control_flag="NO",
        historical_control_flag="NO",
        do_not_use_as="",
        potency_reported="Kd/binding 344 +/- 74 nM; SPR/Biacore 125 +/- 6 nM; functional IC50 0.63-4.2 uM",
        potency_assay="ligand binding; SPR; functional Ca2+/arrestin in PAR2-1321N1",
        primary_reference=("Cheng RKY, Fiez-Vandal C, Schlenker O, Edman K, et al. "
                           "Structural insight into allosteric modulation of "
                           "protease-activated receptor 2. Nature 2017;545(7652):112-115."),
        primary_doi="10.1038/nature22309",
        primary_pmid="28445455",
        stereochemistry_caution=(
            "USE THE (S) ENANTIOMER. PDB 5NDD ligand 8TZ is named by the PDB chemical "
            "component dictionary as (S)-(4-fluoranyl-2-propyl-phenyl)-(1H-imidazol-2-yl)"
            "methanol, InChIKey IDFPQEHZYBXIFO-LBPRGKRZSA-N, which equals PubChem CID "
            "126961334 and ChEMBL4127372. PubChem CID 132117112 is the FLAT record "
            "(InChIKey IDFPQEHZYBXIFO-UHFFFAOYSA-N, no stereo layer) and carries a "
            "depositor synonym asserting '(R)-' that contradicts the deposited crystal "
            "structure. Verified in this session by resolving both CIDs. Do not order "
            "against CID 132117112 without specifying the enantiomer."),
        project_relevance=("This is the co-crystal ligand of PDB 5NDD, the orthosteric "
                           "receptor model used for this project's docking; it is the "
                           "reference antagonist all TOP20 candidates were scored against."),
    ),
    "AZ3451": dict(
        compound_name="AZ3451",
        aliases="PDB ligand 8UN; CAS 2100284-59-9",
        role_in_panel="NEGATIVE_ALLOSTERIC_MODULATOR_REFERENCE",
        what_it_actually_is=(
            "Negative allosteric modulator binding a remote pocket OUTSIDE the helical "
            "bundle, formed by TM2/TM3/TM4 and facing the lipid bilayer. Prevents the "
            "conformational rearrangement required for receptor activation."),
        target_and_site="PAR2 (F2RL1); remote lipid-facing allosteric pocket (TM2/TM3/TM4)",
        arms_blocked="Ca2+, beta-arrestin-2 recruitment, and complete inhibition of ERK phosphorylation",
        is_clean_antagonist="YES",
        biased_agonist_flag="NO",
        par2_ligand_flag="YES",
        selectivity_flag="PAR2-directed",
        counter_control_flag="NO",
        historical_control_flag="NO",
        do_not_use_as=("Not an orthosteric probe -- it will not report on competition "
                       "with the tethered ligand."),
        potency_reported=("SPR/Biacore 13.5 +/- 3 nM; functional IC50 assay-dependent, "
                          "reported range <2.5 nM to 6.6 uM; vendor consensus headline "
                          "IC50 = 23 nM citing Cheng 2017"),
        potency_assay="SPR; functional Ca2+/arrestin/ERK in PAR2-1321N1",
        primary_reference=("Cheng RKY, et al. Structural insight into allosteric "
                           "modulation of protease-activated receptor 2. "
                           "Nature 2017;545(7652):112-115."),
        primary_doi="10.1038/nature22309",
        primary_pmid="28445455",
        stereochemistry_caution=("No conflict: all stereo-defined public records agree on "
                                 "(1S)-1-cyclohexylethyl. PDB 8UN, PubChem CID 126961335 "
                                 "and ChEMBL4128763 all give InChIKey "
                                 "FJAOGFGHTPYADT-SFHVURJKSA-N."),
        project_relevance=("Co-crystal ligand of PDB 5NDZ, the allosteric receptor model "
                           "used in this project's second docking pocket."),
    ),
    "GB88_2S3R": dict(
        compound_name="GB88 -- (2S,3R) allo-Ile form",
        aliases="GB-88; GTPL6658; PubChem CID 73755230",
        role_in_panel="COUNTER_CONTROL_BIASED_AGONIST",
        what_it_actually_is=(
            "*** BIASED LIGAND, NOT A CLEAN ANTAGONIST. *** GB88 antagonises the "
            "PAR2/Gq-11/Ca2+/PKC arm while simultaneously ACTING AS AN AGONIST on at "
            "least three other PAR2 arms: it attenuates forskolin-induced cAMP (Gi/o), "
            "increases ERK1/2 phosphorylation, and activates RhoA (plus myosin "
            "phosphatase phosphorylation and actin rearrangement). It also shows partial "
            "agonist behaviour (EC50 ~3 uM) and internalises the receptor."),
        target_and_site="PAR2 (F2RL1); pathway-selective / biased",
        arms_blocked=("BLOCKS: Ca2+ (Gq/11) and PKC. ACTIVATES: cAMP/Gi-o, ERK1/2, RhoA. "
                      "This is the whole point of the counter-control."),
        is_clean_antagonist="NO",
        biased_agonist_flag="YES",
        par2_ligand_flag="YES",
        selectivity_flag="PAR2-directed but PATHWAY-BIASED",
        counter_control_flag="YES",
        historical_control_flag="NO",
        do_not_use_as=(
            "DO NOT use as a clean antagonist positive control. A compound that looks "
            "'active' next to GB88 in a Ca2+ assay may be equally biased. Use it "
            "specifically to detect bias: a candidate that blocks Ca2+ like GB88 but "
            "does NOT raise ERK/RhoA is the better molecule."),
        potency_reported=("IC50 ~2 uM (HT29 Ca2+, Suen 2012); functional antagonist range "
                          "1-10 uM; partial agonist EC50 ~3 uM; 1.6 +/- 0.5 uM in human "
                          "monocyte-derived macrophages; 8 uM in colonocytes"),
        potency_assay="HT29 Ca2+ mobilisation; CHO-hPAR2; human kidney tubule cells",
        primary_reference=(
            "First description: Suen JY, Barry GD, Lohman RJ, Halili MA, Cotterell AJ, "
            "Le GT, Fairlie DP. Modulating human proteinase activated receptor 2 with a "
            "novel antagonist (GB88) and agonist (GB110). Br J Pharmacol "
            "2012;165(5):1413-23. | BIAS PAPER: Suen JY, Cotterell A, Lohman RJ, et al., "
            "Fairlie DP. Pathway-selective antagonism of proteinase activated receptor 2. "
            "Br J Pharmacol 2014;171(17):4112-24. | Independent corroboration of agonist "
            "behaviour: Ungefroren H, et al. Int J Mol Sci 2017;18(12):2776."),
        primary_doi="10.1111/bph.12757 (bias paper); 10.1111/j.1476-5381.2011.01610.x (first description)",
        primary_pmid="24821440 (bias); 21806599 (first description); 29261154 (corroboration)",
        stereochemistry_caution=(
            "*** UNRESOLVED PUBLIC-RECORD CONFLICT -- RESOLVE BEFORE ORDERING. *** Two "
            "different stereoisomers are both publicly labelled 'GB88', sharing skeleton "
            "hash DCUDDCGUKZLQLN. THIS ROW is the (2S,3R) allo-isoleucine form "
            "(DCUDDCGUKZLQLN-ZEZZXZOMSA-N) asserted by Guide to Pharmacology GTPL6658 and "
            "PubChem CID 73755230. The other row (GB88_2S3S) is the (2S,3S) L-Ile form "
            "with a CAS number. The published chemical name uses plain 'Ile', which by "
            "convention means L-Ile = (2S,3S), favouring the OTHER row. Both are included "
            "in this panel deliberately so the choice is made explicitly rather than by "
            "accident. *** DO NOT ORDER THIS ROW: *** resolving both stereoisomers "
            "separately, this (2S,3R) form returns ONE vendor annotation (Glixx Labs), no "
            "catalogue IDs and no in-stock catalogue membership, while the (2S,3S) form "
            "returns 30 vendor annotations, MolPort/Mcule/Chemspace catalogue IDs and "
            "2025-Q3 in-stock membership. Order GB88_2S3S."),
        project_relevance=("Bias counter-control. Retained ONLY to keep the public-record "
                           "stereochemistry discrepancy visible -- not the orderable form."),
    ),
    "GB88_2S3S": dict(
        compound_name="GB88 -- (2S,3S) L-Ile form",
        aliases="GB-88; CAS 1416435-96-5; ChEMBL2431617; PubChem CID 57330164",
        role_in_panel="COUNTER_CONTROL_BIASED_AGONIST",
        what_it_actually_is=(
            "*** BIASED LIGAND, NOT A CLEAN ANTAGONIST. *** Same compound identity as the "
            "GB88_2S3R row -- see that row for the full pharmacology. This row carries the "
            "(2S,3S) L-isoleucine stereochemistry, which is what the published chemical "
            "name ('...-Cha-Ile-...') implies and which is the form that carries a CAS "
            "number and a ChEMBL entry."),
        target_and_site="PAR2 (F2RL1); pathway-selective / biased",
        arms_blocked="BLOCKS: Ca2+ (Gq/11), PKC. ACTIVATES: cAMP/Gi-o, ERK1/2, RhoA.",
        is_clean_antagonist="NO",
        biased_agonist_flag="YES",
        par2_ligand_flag="YES",
        selectivity_flag="PAR2-directed but PATHWAY-BIASED",
        counter_control_flag="YES",
        historical_control_flag="NO",
        do_not_use_as="DO NOT use as a clean antagonist positive control. See GB88_2S3R.",
        potency_reported="See GB88_2S3R row (pharmacology is reported without stereo disambiguation).",
        potency_assay="HT29 Ca2+ mobilisation; CHO-hPAR2; human kidney tubule cells",
        primary_reference=("Suen JY, et al., Fairlie DP. Br J Pharmacol 2012;165(5):1413-23 "
                           "(first description); Suen JY, et al. Br J Pharmacol "
                           "2014;171(17):4112-24 (bias)."),
        primary_doi="10.1111/bph.12757; 10.1111/j.1476-5381.2011.01610.x",
        primary_pmid="24821440; 21806599",
        stereochemistry_caution=(
            "*** UNRESOLVED PUBLIC-RECORD CONFLICT -- see GB88_2S3R. *** This is the "
            "(2S,3S) L-Ile form, DCUDDCGUKZLQLN-MCOVPRHSSA-N, CAS 1416435-96-5, "
            "ChEMBL2431617, PubChem CID 57330164. On the balance of evidence (the "
            "published name uses 'Ile', and this is the form with a CAS registry number) "
            "THIS is the more likely intended GB88 -- but the assertion is not certain and "
            "GtoPdb disagrees. Confirm with the vendor's own analytical data before the "
            "assay. *** THE MARKET SETTLES THE PRACTICAL QUESTION: *** resolving both "
            "stereoisomers separately, THIS (2S,3S) form returns 30 PubChem vendor "
            "annotations, a MolPort catalogue ID, two Mcule IDs that are both in the "
            "2025-Q3 Mcule IN-STOCK catalogue, a Chemspace in-stock ID and a ZINC in-stock "
            "hit, and classifies IN_STOCK. The (2S,3R) form returns a single vendor "
            "annotation (Glixx Labs), no catalogue IDs and no in-stock membership. "
            "The material the supply chain actually sells as 'GB88' is this one. ORDER "
            "THIS ROW."),
        project_relevance=("Bias counter-control for the assay panel. THIS IS THE ORDERABLE "
                           "GB88 -- the (2S,3R) row is retained only to keep the "
                           "literature discrepancy visible."),
    ),
    "I287": dict(
        compound_name="I-287",
        aliases="CAS 2014368-93-3; GTPL12491; PubChem CID 134296695",
        role_in_panel="BIASED_NEGATIVE_ALLOSTERIC_MODULATOR_REFERENCE",
        what_it_actually_is=(
            "Small molecule (NOT a pepducin -- it is a furo[3,2-b]pyridine-2-carbonyl "
            "piperazinyl pyridine carboxylic acid). Biased negative allosteric modulator: "
            "blocks Galpha-q and Galpha-12/13 and their effectors (DAG, PKC, Ca2+, RhoA, "
            "SRF-RE, FAK) with NO effect on Gi/o signalling or beta-arrestin-2 "
            "recruitment. Inhibition is insurmountable / non-competitive."),
        target_and_site=("PAR2 (F2RL1); allosteric BY INFERENCE from insurmountable "
                         "kinetics. Binding site NOT structurally determined; the authors "
                         "state it is unlikely to occupy either the AZ8838 or the AZ3451 "
                         "pocket. Do not assert a site for it."),
        arms_blocked="Gq and G12/13 arms only. Gi/o and beta-arrestin-2 are NOT blocked.",
        is_clean_antagonist="PARTIAL_PATHWAY_SELECTIVE",
        biased_agonist_flag="NO",
        par2_ligand_flag="YES",
        selectivity_flag="PAR2-directed but PATHWAY-SELECTIVE (Gq + G12/13 only)",
        counter_control_flag="NO",
        historical_control_flag="NO",
        do_not_use_as=("Not a pan-pathway antagonist control -- it is silent on Gi/o and "
                       "beta-arrestin."),
        potency_reported=(NV + " -- no numeric IC50 could be extracted from an accessible "
                          "version of the primary paper. Off-target Ca2+/PKC effects are "
                          "noted only above 1 uM, implying sub-micromolar on-target "
                          "potency, but no stated value was retrieved."),
        potency_assay="BRET2/ebBRET Galpha sensors and p115-RhoGEF recruitment in HEK293; Ca2+; IL-8 secretion; CFA in vivo",
        primary_reference=("Avet C, Sturino C, Grastilleur S, Le Gouill C, et al., "
                           "Bouvier M. The PAR2 inhibitor I-287 selectively targets Galpha-q "
                           "and Galpha-12/13 signaling and has anti-inflammatory effects. "
                           "Commun Biol 2020;3:719."),
        primary_doi="10.1038/s42003-020-01453-8",
        primary_pmid="NOT_FOUND (PMC7695697)",
        stereochemistry_caution="Achiral (InChIKey WPJYZCYPCSYODL-UHFFFAOYSA-N). No stereo risk.",
        project_relevance="Second mechanistic class of antagonist for the panel.",
    ),
    "C391": dict(
        compound_name="C391",
        aliases="GTPL9570; PubChem CID 126970682",
        role_in_panel="ANTAGONIST_REFERENCE_ORTHOSTERIC_PEPTIDOMIMETIC",
        what_it_actually_is=(
            "Peptidomimetic orthosteric antagonist built by modifying the agonist "
            "2-furoyl-LIGRLO-NH2, so it occupies the tethered-ligand docking site. Blocks "
            "both Gq-dependent Ca2+ and MAPK/ERK against peptidomimetic AND proteinase "
            "(trypsin) activation, and blocks beta-arrestin recruitment. It does not "
            "inhibit the proteases themselves."),
        target_and_site="PAR2 (F2RL1); orthosteric / tethered-ligand docking site (ECL2)",
        arms_blocked="Ca2+ (Gq), MAPK/ERK, beta-arrestin recruitment",
        is_clean_antagonist="YES",
        biased_agonist_flag="NO",
        par2_ligand_flag="YES",
        selectivity_flag="PAR2-directed",
        counter_control_flag="NO",
        historical_control_flag="NO",
        do_not_use_as=("Peptidomimetic -- poor oral/topical drug-likeness; use as a "
                       "mechanistic control, not a lead comparator."),
        potency_reported="IC50 1-14 uM; EC50 17.9-19.6 uM; in vivo 7.5-75 ug intraplantar",
        potency_assay="16HBE14o- Ca2+ and ERK; HEK293 beta-arrestin",
        primary_reference=("Boitano S, Hoffman J, Flynn AN, Asiedu MN, et al., Vagner J, "
                           "Price TJ. The novel PAR2 ligand C391 blocks multiple PAR2 "
                           "signalling pathways in vitro and in vivo. Br J Pharmacol "
                           "2015;172(18):4535-4545."),
        primary_doi="10.1111/bph.13238",
        primary_pmid="26140338",
        stereochemistry_caution=(
            "Multiple defined stereocentres (InChIKey OHQDORKALTUSJJ-ZHLQKWORSA-N). "
            "CURATION WARNING: PubChem CID 126970682 carries the synonym 'compound 5 "
            "[PMID: 27994760]', cross-linking it to a GB88-derivative paper. C391 is not a "
            "GB88 derivative; treat that synonym as a PubChem curation error."),
        project_relevance="Orthosteric peptidomimetic comparator.",
    ),
    "RWJ50353": dict(
        compound_name="RWJ-50353",
        aliases="RWJ 50353; CHEMBL270437; CHEMBL339122; PubChem CID 9872263",
        role_in_panel="HISTORICAL_NON_SELECTIVE_CONTROL",
        what_it_actually_is=(
            "*** NOT A PAR2 ANTAGONIST. NOT A PAR2 LIGAND AT ALL. *** It is a reversible, "
            "active-site-directed SERINE PROTEASE INHIBITOR of the D-Phe-Pro-Arg "
            "benzothiazolyl-ketone class, and specifically a POTENT AND SELECTIVE THROMBIN "
            "inhibitor. It acts UPSTREAM of PAR2 by inhibiting trypsin-like proteases that "
            "cleave the PAR2 N-terminus, thereby preventing receptor activation. There is "
            "no reported direct binding to PAR2. "
            "CORRECTION TO THIS PROJECT'S WORKING ASSUMPTION: the project brief described "
            "it as a BROAD serine protease inhibitor. The primary paper reports it as "
            "SELECTIVE for thrombin (16-fold over trypsin, >=330-fold over other "
            "biologically important serine proteases). The core caution is unchanged and "
            "in fact sharper -- it is not a PAR2 antagonist and must not be treated as one."),
        target_and_site="Human alpha-thrombin active site. NOT PAR2.",
        arms_blocked=("None directly. It removes the protease stimulus rather than blocking "
                      "the receptor."),
        is_clean_antagonist="NO -- NOT A RECEPTOR ANTAGONIST",
        biased_agonist_flag="NO",
        par2_ligand_flag="NO",
        selectivity_flag="SELECTIVE_THROMBIN_INHIBITOR_NOT_A_PAR2_LIGAND",
        counter_control_flag="NO",
        historical_control_flag="YES",
        do_not_use_as=(
            "DO NOT use as a PAR2 antagonist reference. DO NOT place it on a PAR2 "
            "orthosteric/allosteric potency axis. In a PAR2 receptor-binding or "
            "receptor-signalling assay it is a mechanistic decoy / negative control. Its "
            "only legitimate role here is as the HISTORICAL positive control for the "
            "skin-pigmentation / melanosome-transfer phenotype."),
        potency_reported=("Ki = 0.19 +/- 0.02 nM vs human alpha-thrombin; 16-fold selectivity "
                          "over trypsin; >=330-fold over other serine proteases; IC50 32 +/- 6 "
                          "nM for alpha-thrombin-induced platelet aggregation"),
        potency_assay="enzyme kinetics vs human alpha-thrombin; gel-filtered platelet aggregation",
        primary_reference=("Giardino EC, Costanzo MJ, Kauffman JA, Li QS, Maryanoff BE, "
                           "Andrade-Gordon P. Antithrombotic properties of RWJ-50353, a "
                           "potent and novel thrombin inhibitor. Thromb Res 2000;98(1):83-93."),
        primary_doi="10.1016/s0049-3848(99)00219-4",
        primary_pmid="10706936",
        stereochemistry_caution=("Defined stereocentres, InChIKey QRBIRSCLEVEODD-BDTNDASRSA-N. "
                                 "PubChem also lists a TFA salt form; specify the free base or "
                                 "record the salt."),
        project_relevance=(
            "THIS is the compound behind the historical skin-lightening / melanosome-transfer "
            "result that motivates the PAR2-pigmentation programme -- NOT a PAR2 antagonist. "
            "Pigmentation papers: Seiberg M, Paine C, Sharlow E, et al. Inhibition of "
            "melanosome transfer results in skin lightening. J Invest Dermatol "
            "2000;115(2):162-167 (PMID 10951231, DOI 10.1046/j.1523-1747.2000.00035.x); "
            "Seiberg M, et al. Exp Cell Res 2000;254(1):25-32 (PMID 10623462); Sharlow ER, "
            "et al. J Cell Sci 2000;113(Pt 17):3093-3101. "
            "*** THE OFTEN-QUOTED '~80% MELANIN-UPTAKE REDUCTION' FIGURE IS " + NV + ". *** "
            "It could not be located in any accessible abstract, full text or citing review. "
            "The abstracts state only 'dose-dependent' and 'visible' lightening, with no "
            "percentage. Do not cite ~80% without opening the Seiberg 2000 JID or Sharlow "
            "2000 JCS figures directly."),
    ),
    "PROPRANOLOL": dict(
        compound_name="Propranolol",
        aliases="CAS 525-66-6; PubChem CID 4946; DrugBank DB00571",
        role_in_panel="APPROVED_REPURPOSING_CANDIDATE",
        what_it_actually_is=("Non-selective beta-adrenoceptor antagonist. Approved drug, "
                             "decades of human exposure, cheap, and available in topical "
                             "formulations. NOT a PAR2 ligand and no PAR2 mechanism is "
                             "claimed for it here."),
        target_and_site="beta-1 / beta-2 adrenoceptors. NOT PAR2.",
        arms_blocked="N/A -- not a PAR2 ligand",
        is_clean_antagonist="N/A_FOR_PAR2",
        biased_agonist_flag="NO",
        par2_ligand_flag="NO",
        selectivity_flag="BETA_BLOCKER_NOT_A_PAR2_LIGAND",
        counter_control_flag="NO",
        historical_control_flag="NO",
        do_not_use_as="Do not present as a PAR2 antagonist. It is a repurposing arm only.",
        potency_reported="N/A for PAR2",
        potency_assay="N/A for PAR2",
        primary_reference=("Included by prior project decision as an approved, cheap, "
                           "topically formulated repurposing arm with a long human-exposure "
                           "record. No PAR2 primary reference is asserted."),
        primary_doi="",
        primary_pmid="",
        stereochemistry_caution=("Racemate in clinical use (InChIKey "
                                 "AQHHHDLHHXJYJD-UHFFFAOYSA-N is the flat/racemic record). "
                                 "Single enantiomers exist; specify if it matters."),
        project_relevance="Repurposing arm; sourceability data only, no PAR2 claim.",
    ),
    "SLIGKV_NH2": dict(
        compound_name="SLIGKV-NH2",
        aliases="PAR-2 (1-6) amide (human); Ser-Leu-Ile-Gly-Lys-Val-NH2; CAS 190383-13-2; PubChem CID 10483914; CHEMBL4084322",
        role_in_panel="AGONIST_CONTROL_HUMAN_TETHERED_LIGAND",
        what_it_actually_is=("The HUMAN PAR2 tethered-ligand hexapeptide (receptor residues "
                             "36-41) supplied as a free soluble peptide. Activates PAR2 "
                             "without proteolysis."),
        target_and_site="PAR2 (F2RL1); orthosteric tethered-ligand site",
        arms_blocked="N/A -- AGONIST",
        is_clean_antagonist="NO -- AGONIST",
        biased_agonist_flag="NO",
        par2_ligand_flag="YES",
        selectivity_flag="PAR2-directed; species-matched to HUMAN",
        counter_control_flag="NO",
        historical_control_flag="NO",
        do_not_use_as=("Weakest of the agonist options -- mid-micromolar. If assay window is "
                       "a concern use 2-furoyl-LIGRLO-NH2 instead."),
        potency_reported="Mid-micromolar range (described in the literature as 'less than optimal')",
        potency_assay="Ca2+ mobilisation",
        primary_reference=("Species assignment (human SLIGKV vs rodent SLIGRL) per McIntosh "
                           "KA, Cunningham MR, Bushell T, Plevin R. Biochem Soc Trans "
                           "2020;48(6):2525-2537, corroborated by the PubChem record title "
                           "'PAR-2 (1-6) amide (human)'."),
        primary_doi="10.1042/BST20200191",
        primary_pmid="33242065",
        stereochemistry_caution="All-L peptide; InChIKey HOWDUIVVWDUEED-WAUHAFJUSA-N. Specify C-terminal amide.",
        project_relevance="Species-correct human agonist control to define the assay window.",
    ),
    "FUROYL_LIGRLO_NH2": dict(
        compound_name="2-furoyl-LIGRLO-NH2",
        aliases="2-furoyl-LIGRLO-amide; CAS 729589-58-6; PubChem CID 10395438; CHEMBL509819",
        role_in_panel="AGONIST_CONTROL_PREFERRED_POTENT",
        what_it_actually_is=("Synthetic optimised PAR2 agonist built on the RODENT LIGRL core "
                             "with a C-terminal ornithine and an N-terminal 2-furoyl cap. "
                             "Cross-species active and the cleanest peptide agonist reference "
                             "-- unlike trans-cinnamoyl-LIGRLO-NH2 it does not cause a "
                             "prominent non-PAR2-mediated contraction."),
        target_and_site="PAR2 (F2RL1); orthosteric tethered-ligand site",
        arms_blocked="N/A -- AGONIST",
        is_clean_antagonist="NO -- AGONIST",
        biased_agonist_flag="NO",
        par2_ligand_flag="YES",
        selectivity_flag="PAR2-directed; cross-species",
        counter_control_flag="NO",
        historical_control_flag="NO",
        do_not_use_as="",
        potency_reported=("10-25x more potent than SLIGRL-NH2 for intracellular Ca2+ in "
                          "cultured human and rat PAR2-expressing cells; 10-300x in tissue "
                          "bioassays. NOTE: the widely quoted blanket '300x' figure is the "
                          "UPPER BOUND of the tissue bioassay range, not the cell Ca2+ "
                          "figure. For a cell Ca2+ assay 10-25x is the defensible number."),
        potency_assay="Ca2+ in human and rat PAR2-expressing cells; arterial vasodilation/hyperpolarisation bioassay",
        primary_reference=("McGuire JJ, Saifeddine M, Triggle CR, Sun K, Hollenberg MD. "
                           "2-furoyl-LIGRLO-amide: a potent and selective proteinase-"
                           "activated receptor 2 agonist. J Pharmacol Exp Ther "
                           "2004;309(3):1124-31."),
        primary_doi="10.1124/jpet.103.064584",
        primary_pmid="14976230",
        stereochemistry_caution=(
            "InChIKey OSKIRYSKGDEIOG-WTWMNNMUSA-N. DO NOT CONFUSE with 2-furoyl-LIGRL-NH2 "
            "(no ornithine), a different compound (Kawabata 2005, PMID 15655521)."),
        project_relevance="Preferred potent agonist control for defining maximal response.",
    ),
    "SLIGRL_NH2": dict(
        compound_name="SLIGRL-NH2",
        aliases="PAR-2 (1-6) amide (mouse, rat); CAS 171436-38-7; PubChem CID 9831050; CHEMBL238078",
        role_in_panel="AGONIST_CONTROL_RODENT_TETHERED_LIGAND",
        what_it_actually_is=("The RAT/MOUSE PAR2 tethered-ligand hexapeptide. Included so the "
                             "species distinction is explicit and cannot be made by accident."),
        target_and_site="PAR2 (F2RL1); orthosteric tethered-ligand site",
        arms_blocked="N/A -- AGONIST",
        is_clean_antagonist="NO -- AGONIST",
        biased_agonist_flag="NO",
        par2_ligand_flag="YES",
        selectivity_flag="PAR2-directed; species-matched to RAT/MOUSE, NOT human",
        counter_control_flag="NO",
        historical_control_flag="NO",
        do_not_use_as=("*** SPECIES CAUTION: this is the RODENT tethered-ligand sequence. "
                       "For a human PAR2 assay use SLIGKV-NH2 or 2-furoyl-LIGRLO-NH2. ***"),
        potency_reported="More potent than SLIGKV-NH2; 10-25x less potent than 2-furoyl-LIGRLO-NH2 in cell Ca2+",
        potency_assay="Ca2+ mobilisation",
        primary_reference=("Species assignment per McIntosh KA, et al. Biochem Soc Trans "
                           "2020;48(6):2525-2537 and the PubChem record title "
                           "'PAR-2 (1-6) amide (mouse, rat)'."),
        primary_doi="10.1042/BST20200191",
        primary_pmid="33242065",
        stereochemistry_caution="All-L peptide; InChIKey SGPMJRPYYIJZPC-JYAZKYGWSA-N.",
        project_relevance="Species control / rodent-model agonist.",
    ),
}

# Compound with NO resolvable structure -- appended as a row with the structure
# fields explicitly empty, never guessed.
P2L003 = dict(
    cand_id="P2L_003",
    compound_name="P2L-003",
    aliases="reported CAS 1359416-20-8 (UNVERIFIED by this pipeline)",
    role_in_panel="ANTAGONIST_REFERENCE_HOST_LAB_COMPOUND",
    what_it_actually_is=(
        "Selective small-molecule PAR2 antagonist with an sp3-rich "
        "tetrahydropyrazolopyridine core, derived by scaffold replacement from the "
        "indazole virtual-screening hit S757-0124. Compound selection was filtered on "
        "antagonist-like Na+ displacement (<1.4 A) at the conserved allosteric sodium "
        "site, so the binding-site rationale is COMPUTATIONAL: the paper reports no "
        "experimental co-structure."),
    target_and_site=("PAR2 (F2RL1). Site inferred computationally from allosteric-sodium-"
                     "site dynamics; NOT experimentally determined."),
    arms_blocked="Ca2+ mobilisation; dose-dependently suppresses ERK1/2 and p38 phosphorylation (3-30 uM, 24 h)",
    is_clean_antagonist="YES (as reported)",
    biased_agonist_flag="NO",
    par2_ligand_flag="YES",
    selectivity_flag="PAR2-directed; reported no effect on PAR1, PAR4 or ATP-mediated signalling",
    counter_control_flag="NO",
    historical_control_flag="NO",
    do_not_use_as="",
    potency_reported="IC50 0.62 uM. No cytotoxicity 0-30 uM.",
    potency_assay="PAR2-mediated Ca2+ mobilisation in HT-29 cells",
    primary_reference=(
        "Park J, Lim H, Lee Y, Kim T, Song H, Lee S, Heo Y, Kim J, Namkung W, Han G. "
        "Discovery of PAR2 antagonists through fragment molecular orbital-based hotspot "
        "analysis and allosteric sodium site dynamics simulations. Bioorg Chem "
        "2025;167:109285."),
    primary_doi="10.1016/j.bioorg.2025.109285",
    primary_pmid="41308341",
    stereochemistry_caution="Structure not resolved -- no stereochemistry can be asserted.",
    project_relevance=(
        "*** HOST-LAB COMPOUND. *** The author list includes Wan Namkung and Gyoonhee Han "
        "(Yonsei University). Citation VERIFIED IN THIS SESSION independently via the "
        "Crossref API (api.crossref.org/works/10.1016/j.bioorg.2025.109285) and NCBI "
        "eutils esummary for PMID 41308341 -- both return the same title, journal, volume "
        "and author list. The compound may already be in hand in the host laboratory, "
        "which would make it the cheapest possible positive control to obtain."),
)


def read_summary(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        return {r["molecule_id"]: r for r in csv.DictReader(fh)}


def main():
    seed_path = os.path.join(HERE, "REFERENCE_PANEL_SEED.csv")
    summ_path = os.path.join(HERE, "REFPANEL_SOURCEABILITY_SUMMARY.csv")
    out_path = os.path.join(HERE, "PAR2_REFERENCE_PANEL_FOR_WAN.csv")

    src = read_summary(summ_path)
    if not src:
        print(f"WARNING: {summ_path} not found -- sourceability columns will be "
              f"NOT_RESOLVED_YET", file=sys.stderr)

    with open(seed_path, "r", encoding="utf-8-sig", newline="") as fh:
        seed = list(csv.DictReader(fh))

    fields = [
        "panel_id", "compound_name", "aliases", "role_in_panel",
        # --- the two mandated scientific-caution columns, up front ---
        "biased_agonist_flag", "counter_control_flag",
        "par2_ligand_flag", "selectivity_flag", "historical_control_flag",
        "is_clean_antagonist", "do_not_use_as",
        # --- mechanism ---
        "what_it_actually_is", "target_and_site", "arms_blocked",
        "potency_reported", "potency_assay",
        # --- structure + provenance ---
        "isomeric_smiles", "inchikey", "structure_source",
        "structure_source_url", "stereochemistry_caution",
        # --- literature ---
        "primary_reference", "primary_doi", "primary_pmid", "project_relevance",
        # --- sourceability (machine-retrieved) ---
        "sourceability_class", "sourceability_reason",
        "best_vendor", "best_catalogue_id", "best_source_url",
        "exact_match_found", "connectivity_only_match_found",
        "pubchem_cid_exact", "chembl_id", "chembl_max_phase",
        "approved_drug_evidence", "clinical_phase_note",
        "regulatory_registry_crossrefs", "vendor_leads_pubchem",
        "molport_catalogue_ids", "mcule_ids", "enamine_real_member",
        "in_stock_catalogues", "on_demand_catalogues",
        "price", "quantity", "purity", "lead_time",
        "retrieved_date",
    ]

    rows = []
    for s in seed:
        cid = s["cand_id"]
        a = ANN.get(cid, {})
        r = {f: "" for f in fields}
        r.update({
            "panel_id": cid,
            "isomeric_smiles": s["smiles_prepared"],
            "inchikey": s["inchikey"],
            "structure_source": s.get("structure_source", ""),
            "retrieved_date": TODAY,
        })
        for k, v in a.items():
            if k in r:
                r[k] = v
        # structure source URL
        pc = ""
        for tok in s.get("structure_source", "").split():
            if tok.isdigit():
                pc = tok
                break
        r["structure_source_url"] = (
            f"https://pubchem.ncbi.nlm.nih.gov/compound/{pc}" if pc else "")

        sm = src.get(cid)
        if sm:
            r.update({
                "sourceability_class": sm.get("classification", ""),
                "sourceability_reason": sm.get("classification_reason", ""),
                "best_vendor": sm.get("best_vendor", ""),
                "best_catalogue_id": sm.get("best_catalogue_id", ""),
                "best_source_url": sm.get("best_source_url", ""),
                "exact_match_found": sm.get("exact_match_found", ""),
                "connectivity_only_match_found": sm.get("connectivity_only_match_found", ""),
                "pubchem_cid_exact": sm.get("pubchem_cid_exact", ""),
                "chembl_id": sm.get("chembl_id", ""),
                "chembl_max_phase": sm.get("chembl_max_phase", ""),
                "approved_drug_evidence": sm.get("approved_drug_evidence", ""),
                "clinical_phase_note": sm.get("clinical_phase_note", ""),
                "regulatory_registry_crossrefs": sm.get(
                    "regulatory_registry_crossrefs", ""),
                "vendor_leads_pubchem": sm.get("vendor_leads_pubchem", ""),
                "molport_catalogue_ids": sm.get("molport_catalogue_ids", ""),
                "mcule_ids": sm.get("mcule_ids", ""),
                "enamine_real_member": sm.get("enamine_real_member", ""),
                "in_stock_catalogues": sm.get("in_stock_catalogues", ""),
                "on_demand_catalogues": sm.get("on_demand_catalogues", ""),
                "price": sm.get("price", "UNKNOWN"),
                "quantity": sm.get("quantity", "UNKNOWN"),
                "purity": sm.get("purity", "UNKNOWN"),
                "lead_time": sm.get("lead_time", "UNKNOWN"),
            })
        else:
            r["sourceability_class"] = "NOT_RESOLVED_YET"
        rows.append(r)

    # P2L-003: structure could not be resolved -- explicit, never invented.
    p = {f: "" for f in fields}
    for k, v in P2L003.items():
        if k in p:
            p[k] = v
    p.update({
        "panel_id": "P2L_003",
        "isomeric_smiles": "STRUCTURE_NOT_RESOLVED",
        "inchikey": "STRUCTURE_NOT_RESOLVED",
        "structure_source": ("NO PubChem CID and NO ChEMBL ID exist for this compound as "
                             "of " + TODAY + " (searched PubChem name endpoint for "
                             "'P2L-003', 'PZ-235'; both returned PUGREST.NotFound). The "
                             "paper is 10 months old. Structure must be taken from the "
                             "primary paper's supporting information or requested from "
                             "the authors."),
        "structure_source_url": "https://doi.org/10.1016/j.bioorg.2025.109285",
        "sourceability_class": "REGISTERED_NOT_VERIFIED",
        "sourceability_reason": (
            "Compound is published and named but has no registry structure record, so no "
            "structure-based vendor search could be run. A MedChemExpress catalogue number "
            "HY-180244 and CAS 1359416-20-8 were REPORTED by secondary web research but "
            "medchemexpress.com returns HTTP 403 to programmatic access, so NEITHER WAS "
            "VERIFIED by this pipeline. Do not treat the catalogue number as confirmed. "
            "Highest-value next action: ask the host lab directly -- Wan Namkung is a "
            "co-author."),
        "best_vendor": NV,
        "best_catalogue_id": NV,
        "best_source_url": "https://doi.org/10.1016/j.bioorg.2025.109285",
        "exact_match_found": "NO",
        "connectivity_only_match_found": "NO",
        "pubchem_cid_exact": "NONE_EXISTS",
        "chembl_id": "NONE_EXISTS",
        "chembl_max_phase": "UNKNOWN",
        "approved_drug_evidence": "NONE_FOUND",
        "clinical_phase_note": "UNKNOWN",
        "regulatory_registry_crossrefs": "NONE_FOUND",
        "vendor_leads_pubchem": "UNKNOWN",
        "molport_catalogue_ids": "UNKNOWN",
        "mcule_ids": "UNKNOWN",
        "enamine_real_member": "UNKNOWN",
        "in_stock_catalogues": "UNKNOWN",
        "on_demand_catalogues": "UNKNOWN",
        "price": "UNKNOWN", "quantity": "UNKNOWN",
        "purity": "UNKNOWN", "lead_time": "UNKNOWN",
        "retrieved_date": TODAY,
    })
    rows.append(p)

    with open(out_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print(f"wrote {out_path} ({len(rows)} rows)")
    for r in rows:
        print(f"  {r['panel_id']:<20} {r['role_in_panel']:<46} "
              f"{r['sourceability_class']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
