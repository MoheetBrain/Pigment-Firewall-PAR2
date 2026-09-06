# Project Status

Last updated: 2026-09-06 (in-stock catalogue searched; retrieval returned a negative result) · branch `yonsei-final10-v2` · **sourceable-hit sprint in progress**

## Project Objective

Identify a defensible, chemically diverse set of candidate PAR2 (F2RL1)
antagonists for experimental evaluation by Professor Wan Namkung.

The current objective chain is:

take the best de novo PAR2 chemistry → freeze it as similarity seeds →
retrieve REAL / SOURCEABLE molecules that are close analogues or
pharmacophore-preserving neighbours → revalidate them through the full PAR2
structural pipeline (EX8 → clash filter → ProLIF → EX32) → calibrate against a
known-active vs decoy benchmark → counter-screen against active-state PAR2 →
co-fold the finalists → nominate ~20 diverse, sourceable molecules.

No compound has been nominated. **No molecule in this repository is
demonstrated to bind or inhibit PAR2.**

## Current Stage

**Sourceable-hit selection sprint, in progress.** The prior sprint produced a
computationally prioritised panel whose vendor fields were all `PENDING`
because web access was blocked. This sprint converts that into a panel of
REAL, ORDERABLE molecules with co-folding evidence.

Completed this session:
- **STEP 1 — de novo seed set frozen.** 32 seeds selected diversity-aware from
  the 16,314-row de novo universe (26 × 5NDD orthosteric, 6 × 5NDZ allosteric),
  30 EX32-supported, 30 unique Murcko scaffolds, spanning three novelty bands.
- **Co-folding validated.** Boltz-2 reproduces the AZ8838 crystal binding mode
  blind — ligand RMSD 1.22 Å, centroid displacement 0.69 Å, backbone 1.16 Å
  over 295 Cα, consistent across all 5 diffusion samples.
- **The vendor gap is closed for the reference panel.** Real catalogue IDs now
  exist for AZ8838, AZ3451, both GB88 stereoisomers, I-287, propranolol and the
  agonist controls, each with a source URL and retrieval date.
- **Sourceability of the existing panel measured: 22 of 25 are NOT_SOURCEABLE.**
  The de novo designs cannot be bought. This is the empirical justification for
  the whole sprint.
- Co-folding batch 1 complete (references + IDEAL_DE_NOVO_TOP5, 21 jobs);
  control panel (18 jobs) and real-compound fallback (88 jobs) running.
- Fallback pool built: 3,095 already-docked real compounds scored for
  similarity to the frozen seeds (225 at Tanimoto ≥ 0.30, max 0.615).

In flight: real-analogue retrieval and redocking (the critical path);
active-vs-decoy benchmark and IFP null calibration; active-state
counter-screen; sourceability of the retrieved analogues.

## Current Branch

`yonsei-final10-v2`

## Current System Architecture

Ligand preparation → sharded GNINA docking (EX8 bulk, EX32 precision) → pose
collection over all 9 poses → clash filtering → ProLIF interaction fingerprints
against the crystallographic reference → preparation-independent polar-anchor
scoring → per-pocket consensus ranking → chemotype clustering → seed freezing →
real-chemical-space retrieval → analogue redocking → benchmark calibration →
active-state counter-screen → constrained co-folding → final integrated
ranking.

Scores are standardised **within** pocket. 5NDD and 5NDZ are never pooled.

New this session: `v3_freeze_denovo_seeds.py` (STEP 1) and the Boltz-2
co-folding harness under `11_SOURCEABLE/cofold/`.

## Capabilities Implemented

- Deterministic ligand preparation with a documented pH 7.4 ionisation rule set.
- Mechanistic pocket routing: orthosteric → 5NDD, allosteric → 5NDZ,
  exploratory → both.
- Sharded, resumable GNINA execution with per-shard checksums.
- Multi-pose collection; pose 1 is never assumed to be the best pose.
- ProLIF recovery against the correct crystallographic antagonist per pocket.
- Preparation-independent polar-anchor scoring (`v2_robust_anchors.py`),
  invariant to ligand protomer and receptor histidine tautomer.
- Butina chemotype clustering on ECFP4 r=2 2048-bit fingerprints.
- **New:** diversity-aware seed freezing that compresses correlated scores into
  evidence families rather than counting them as independent votes.
- **New:** constrained Boltz-2 co-folding against wild-type PAR2 with
  pocket-residue constraints and ligand-affinity prediction.

## Work Completed to Date

- V1 audit; corrected 5NDD/5NDZ reference pockets, clean receptors, and
  ligand-centred configs.
- Forced-CPU GNINA v1.3.3 reference benchmark: 5NDD best-pose RMSD 0.6747 Å,
  5NDZ best-pose RMSD 0.8672 Å.
- 15,000 de novo designs generated → 14,825 prepared.
- De novo EX8: **16,314 / 16,314 routed jobs complete**, 9 poses each.
- EX32 precision: 535 jobs over 513 molecules, diversity-selected.
- Real compounds EX8: 4,835 (approved drugs, natural products, retrieved
  analogues).
- Combined ranked universe: **21,149 ligand-pocket rows over 19,660 molecules**.
- `FINAL_TOP20_DIVERSE_PAR2_CANDIDATES.{csv,md}` and `IDEAL_DE_NOVO_TOP5.csv`.
- Ten substantive defects found and fixed (see §4 of the 2026-09-05 handoff),
  including a wrong AZ8838 tautomer, an unprotonated receptor, a wrong anchor
  definition, and stereochemistry destruction during preparation.
- **This session:** 32 de novo similarity seeds frozen; co-folding target
  verified; Boltz-2 deployed on two A100s.

## Important Files and Artifacts

- `YONSEI_FINAL10_V2/HANDOFF_2026-09-05.md` — **read first.** Campaign history,
  the ten defects, and the standing scientific guardrails.
- `YONSEI_FINAL10_V2/11_SOURCEABLE/seeds/FINAL_DE_NOVO_SIMILARITY_SEEDS.csv` —
  the frozen 32 seeds (this sprint's STEP 1 output).
- `YONSEI_FINAL10_V2/11_SOURCEABLE/cofold/PAR2_COFOLD_TARGET.json` — the
  verified co-folding construct, pocket residues, and residue-numbering offset.
- `YONSEI_FINAL10_V2/scripts/v3_freeze_denovo_seeds.py` — seed selection.
- `YONSEI_FINAL10_V2/10_FINAL/CONSENSUS_FINAL/CONSENSUS_WITH_PROVENANCE.csv` —
  the 21,149-row ranked universe.
- `YONSEI_FINAL10_V2/10_FINAL/DENOVO_EX32_ALL.csv` — EX32 precision results.
- `YONSEI_FINAL10_V2/10_FINAL/ROBUST_ANCHORS_BEST.csv` — anchor geometry.
- `YONSEI_FINAL10_V2/10_FINAL/STEREO_REDOCK_LIST.csv` — the 646 affected
  finalists (207 docked as the wrong stereoisomer).

Raw poses live **outside** the repo under `../PAR2_*_POSES_2026-09-05/`.

## Data Sources and Provenance

De novo designs from `02_DENOVO_CPU/` (BRICS enumeration, seed 20260812).
Real-compound universe from `03_SOURCEABILITY/V2_CANDIDATE_UNIVERSE.csv` (FDA
drugs, LOTUS, NPAtlas, COCONUT, MITF scaffolds, V1 hits). Reference pockets
from PDB 5NDD (AZ8838, orthosteric) and 5NDZ (AZ3451, allosteric). Active-state
structures 9D0A / 8ZMD / 8ZME retrieved this session for the counter-screen.
Co-folding target from UniProt P55085 (human F2RL1), residues 59–370.
RDKit 2026.03.6; preparation seed 20260904.

Validated docking system, unchanged throughout: **GNINA v1.3.3**, SHA-256
`3340c1f49cd3c7c84d8699182a1c6af13c7fa2a22448d1204640446106f72172`, CPU-only,
`--no_gpu --cnn_scoring rescore --cpu 4 --num_modes 9`, seed 20260904.
Box 5NDD centre `16.974 5.926 55.826` size `17.332 17.672 13.644`;
box 5NDZ centre `1.356 12.419 48.400` size `20.702 17.885 25.525`.

## Decisions and Rationale

- **Seeds are frozen, not re-derived.** The theoretical ranking was iterated
  enough; further churn buys nothing. Selection is diversity-aware and
  deliberately *not* ranks 1–40.
- **Correlated scores are compressed into evidence families.** Vina ↔ ligand
  efficiency −0.958, Vina ↔ PIGNet2 0.899, CNNscore ↔ CNN_VS 0.988. Interaction
  fingerprint recovery correlates ≤0.19 with all of them and is the only
  orthogonal structural evidence. Counting six correlated scores as six votes
  would be a measurement error, not conservatism.
- **`DESIGN_HOTSPOT_SCORE` defined explicitly** as
  `0.60 × polar_anchor_fraction + 0.40 × contact_fraction`, built on the
  preparation-independent anchor geometry. It is a geometric descriptor, not a
  claim that a hydrogen bond exists.
- **Molecules docked as the wrong stereoisomer cannot seed a search.** Their
  docking evidence describes a different molecule; 207 such designs were
  excluded from the seed gate.
- **Co-folding uses wild-type PAR2, not the crystal construct.** The
  crystallised receptor carries BRIL and T4-lysozyme fusions plus seven
  thermostabilising mutations. All 5NDD pocket residues are wild-type; the
  5NDZ pocket contains one construct mutation (G157A), which is recorded.
- **The N-terminal tethered-ligand region (residues 1–58) is excluded** from
  the co-folding construct so it cannot compete for the orthosteric site and
  confound an antagonist co-fold.
- **The GNINA pose is never given to the co-folding model.** Co-folding is
  constrained only by pocket residue identity, so that it yields an independent
  structural hypothesis rather than being handed the answer.

## Verification and Test Results

- Seed selection executed: 16,314 de novo rows → gates (14,336 not
  all-poses-clashing → 14,217 negative Vina affinity → 13,989 stereo not
  known-wrong) → 32 seeds. All 20 prior finalists (IDEAL_TOP5 + de novo panel
  members) carried forward; `forced_not_available` is empty.
- Co-folding residue mapping verified against UniProt P55085: all eight anchor
  and pocket residues (Y82, H135, D228, Y210, N158, C161, H227, G157) land on
  the expected amino acid after the −58 index offset.
- Crystal pocket residues recomputed from the structures at a 5.0 Å cutoff:
  5NDD gives 17 residues, 5NDZ gives 13.
- Network reachability re-tested this session: PubChem REST, ChEMBL API,
  enamine.net and api.molport.com all responded; mcule.com returned 403 to a
  bare request.
- Boltz-2.2.1 installed on `a100` and `a100-40`; `torch.cuda.is_available()`
  True on both, A100-SXM4-80GB and A100-SXM4-40GB respectively.
- **Co-folding reference validation PASSED.** AZ8838 co-folded blind into
  wild-type PAR2 recovers its crystal pose: over 295 common Cα, backbone RMSD
  0.98–1.16 Å, ligand RMSD 1.22–1.27 Å, centroid displacement 0.69–0.89 Å,
  across all five diffusion samples; confidence 0.953–0.960.
- Batch-1 co-folding: 21/21 jobs, 0 failures, confidence 0.92–0.96, pocket
  occupancy 0.82–1.00, 0–1 clashes. Sample consistency after receptor
  superposition: AZ8838 0.74 Å, AZ3451 0.82 Å, de novo 1.16–1.70 Å.
- Control structures independently verified by recomputing InChIKeys from
  SMILES: GB88 (2S,3S), GB88 allo-Ile, GB110, GB83, K-14585 — all five matched
  their claimed keys exactly. Propranolol corrected to (S) after CIP check.
- Sourceability of the existing panel: 22/25 NOT_SOURCEABLE, 1 IN_STOCK,
  2 REGISTERED_NOT_VERIFIED.
- `python -c "import ast; ast.parse(...)"` on `v3_freeze_denovo_seeds.py`:
  passed.

## Known Failures and Limitations

- **The existing de novo panel is essentially unbuyable**: 22 of 25 members
  resolve to NOT_SOURCEABLE against PubChem, ChEMBL, Mcule and Arthor. Prices
  and lead times remain UNKNOWN even for the molecules that were found.
- MolPort, the Enamine store API, eMolecules and Chemspace REST all require
  credentials or API keys this session does not hold; no query was completed
  against them. Enamine chemistry was reached through SmallWorld's
  Enamine-SC-Stock and REAL maps instead.
- The Boltz affinity module is a weak discriminator: it gives the
  crystallographic binder AZ8838 a binder probability of only 0.583 and scores
  several de novo designs above it. Used only as a low-weight relative signal.
- A frame-alignment defect in `v3_analyse_cofold.py` initially reported 13–17 Å
  sample consistency because diffusion samples are produced in independent
  global frames. Fixed by superposing receptors first; the bad values were
  never used downstream.
- 207 ranked finalists were docked as the wrong stereoisomer and 439 are
  stereochemically ambiguous; they are excluded from seeding but the affected
  panel rows have not yet been re-docked.
- The pH 7.4 model is a documented SMARTS heuristic, not a pKa prediction; one
  tautomer and one conformer are carried per ligand.
- 27% of batch-1 and 41% of batch-2 poses are sterically clashing.
- 44% of EX8 dual-anchor calls were sampling artefacts — only 30 of 54 survived
  re-docking at EX32.
- 66% of 5NDD ligand-pocket pairs already satisfy all three polar anchors, so
  anchor count alone is weakly discriminating.
- Batch-1 rows lack a clash metric entirely; those rows are flagged
  `clash_unknown` and penalised rather than imputed.

## Risks and Technical Debt

- Interaction-fingerprint recovery is geometric similarity to a crystal pose,
  not evidence of binding. Whether high IFP values are genuinely unusual is
  exactly what the active-vs-decoy null distribution is being computed to
  settle; until it returns, IFP weighting is provisional.
- CNNscore and CNNaffinity are ranking features, never calibrated
  probabilities of antagonism.
- Co-folding confidence is not a binding assay and cannot distinguish an
  antagonist from a biased agonist.
- The de novo dedup defect (dedup ran per batch, after tautomer
  canonicalisation) is deliberately unfixed — fixing it would invalidate every
  committed `cand_id` mid-campaign.
- The A100 boot disk has only ~19 GB free, which constrains how much co-folding
  output can be retained on-instance.

## Current Blockers

None mechanical. One **scientific** blocker shapes the deliverable:

**Close purchasable analogues of our de novo chemistry do not exist.** A local
ECFP4 search of 3,971,098 in-stock molecules returned 7 hits at >= 0.50
Tanimoto, all in the weakest band, best 0.556, from 2 of 32 seeds. A positive
control over the same catalogue returned 362 hits including exact matches, so
the search is sound and the result is real. Consequently the sourceable panel
must be built from real compounds that preserve the *interaction solution*
at moderate 2D similarity, not from close structural analogues.

Compute state: `a100` and `a100-40` are TERMINATED. `h3` is running the
active-vs-decoy benchmark, the active-state counter-screen and the wide
similarity search.

## Exact Next Actions

1. Complete the AZ8838 co-folding validation and record its real result; do not
   proceed to candidate co-folding until the reference recovers its own pocket.
2. Retrieve real analogues for the 32 frozen seeds across Enamine in-stock,
   Enamine REAL, Chemspace, MolPort, Mcule, eMolecules, PubChem and ChEMBL.
3. Redock the serious analogue pool: EX8 → clash filter → ProLIF → top 200–300
   → EX32.
4. Complete the active-vs-decoy benchmark and the IFP null distribution, and
   use it to set — or demote — the weight of each score family.
5. Complete the active-state counter-screen against 9D0A / 8ZMD / 8ZME.
6. Resolve vendor, catalogue ID, stock, price and lead time as hard data.
7. Co-fold the top 40–60 sourceable molecules plus AZ8838, AZ3451, GB88 and
   IDEAL_DE_NOVO_TOP5, with multiple seeds.
8. Build `FINAL_SOURCEABLE_PAR2_TOP20.{csv,md}` under hard gates and six
   independent evidence families.
9. Pull all unique cloud results back to the Mac and stop every VM.
