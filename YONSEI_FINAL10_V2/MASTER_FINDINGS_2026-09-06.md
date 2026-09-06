# PAR2 SOURCEABLE-HIT CAMPAIGN — MASTER FINDINGS
**2026-09-06 · branch `yonsei-final10-v2` · all compute stopped**

This is the complete record of the sourceable-hit sprint: every finding, every
defect, every negative result, and every limit. It supersedes nothing — read it
alongside `HANDOFF_2026-09-05.md`, which covers the preceding campaign.

**Standing label for everything below: COMPUTATIONALLY PRIORITISED PAR2
CANDIDATES.** No molecule in this repository has been shown to bind or inhibit
PAR2. Docking, interaction fingerprints and co-folding are structural
hypotheses, not assays, and none of them distinguishes an antagonist from a
biased agonist.

---

# 1. THE HEADLINE RESULT

`YONSEI_FINAL10_V2/11_SOURCEABLE/final/FINAL_SOURCEABLE_PAR2_TOP20.csv`

**20 candidates · 20 unique Murcko scaffolds · 16 orthosteric (5NDD) / 4
allosteric (5NDZ) · 20/20 vendor-listed.**

Every row carries: an exact InChIKey match in PubChem with named suppliers
(median **36.5** vendors, range 5–96); fresh EX32 docking behind a passing
fail-closed hash gate; ProLIF crystal-IFP recovery (0.583–0.875);
preparation-independent anchor geometry; and full physicochemistry.

**The `PENDING` vendor problem that ended the previous sprint is solved.** No
field in the panel is a placeholder.

---

# 2. THE MOST IMPORTANT FINDING IS A NEGATIVE ONE

## 2.1 Our de novo chemistry cannot be bought, and has no purchasable neighbours

Two independent measurements say the same thing.

**(a) The existing panel is unbuyable.** Vendor resolution of the previous
`FINAL_TOP20_DIVERSE_PAR2_CANDIDATES` plus `IDEAL_DE_NOVO_TOP5` (25 molecules):

| class | n |
|---|---|
| NOT_SOURCEABLE | **22** |
| REGISTERED_NOT_VERIFIED | 2 |
| IN_STOCK | **1** (resatorvid/TAK-242) |

**(b) There are no close analogues either.** A streaming ECFP4 (r=2, 2048-bit)
Tanimoto search of **3,971,098 in-stock molecules** — 430 ZINC20 tranche files,
258 MB, downloaded to h3 and searched locally — against all 32 frozen seeds
returned:

- **7 hits at ≥ 0.50**, every one in the weakest band (0.50–0.60), best **0.556**
- from only **2 of 32 seeds**
- nothing at all reached 0.60

Lowering the floor to 0.35 gave 672 hits across 17 seeds, median Tanimoto
0.368 — i.e. weak neighbours, not analogues.

## 2.2 The negative was validated, not assumed

The identical search over the identical catalogue with ordinary drug-like
queries returned **362 hits**:

| query | hits |
|---|---|
| propranolol | 128 |
| ibuprofen | 124 |
| imatinib | 84 |
| GB88 | 26 |
| AZ8838 | 0 (MW 220, fragment-sized — sparse fingerprint) |

Band distribution: **6 at ≥0.80, 36 at 0.70–0.80, 80 at 0.60–0.70**, best
Tanimoto **1.00 with an exact match retrieved**.

The pipeline finds neighbours, and exact matches, when they exist. It returns
almost nothing for our seeds because almost nothing is there.

## 2.3 Why

The de novo seeds are high-Fsp3 sugar- and terpenoid-like BRICS constructions
(Fsp3 up to 1.00). In-stock screening catalogues are dominated by flat aromatic
amide chemistry. The two populations barely intersect.

## 2.4 Consequence — stated plainly

**The delivered TOP20 is a repurposing panel, not a de novo analogue panel.**
19 of 20 are approved/clinical drugs at Tanimoto **0.154–0.397** to the seeds.
Only one (`ZI54096226`, 0.397) is a genuine de novo-connected in-stock molecule.

The brief's requirement *"meaningfully similar to one of our strongest de novo
designs"* is **NOT MET** by 19 of the 20. They earn their place on PAR2 pocket
evidence and orderability. Anyone presenting this list must say so.

---

# 3. DEFECTS FOUND THIS SPRINT

## 3.1 In inherited code (found, recorded, not silently patched)

1. **`v2_prepare_ligands.py:132` still calls
   `rdMolStandardize.TautomerEnumerator().Canonicalize()`** — the exact defect
   handoff §4.7 blames for destroying stereochemistry in 2,534 designs,
   changing the constitution of 1,199, inventing unassigned stereocentres in
   2,241, and causing **207 finalists to be docked as the wrong stereoisomer**.
   It was never removed. Sourceable finalists were therefore prepared with a
   new `v3_prepare_finalists.py` that omits the call and imports the pH 7.4
   protonation function unchanged. Result: **80/80 prepared, 0 failed,
   0 stereocentres lost.**

2. **`v2_interactions.py` reads the defective `*_protonated_pH74.pdb`**
   (0/39 charged lysines — the broken `obabel -h -p 7.4` product). **Every
   `max_ifp_recovery` in the entire campaign was computed on a receptor that
   cannot detect a salt bridge.** Internally consistent, so rankings are not
   invalidated, but ionic interactions are systematically understated.

3. **All 4,835 real-compound rows carry `source=DENOVO`,
   `library=DE_NOVO_BRICS`** in the consensus table. Those labels are inherited
   and wrong. Real provenance must be read from `REAL_COMPOUND_PROVENANCE.csv`.

4. **Two members of the previous TOP20 do not match their recorded provenance
   structures**: RX05505 differs in stereo descriptor; RX00387 differs in
   *constitution* (different InChIKey skeleton from its recorded CID). Both
   were among the compounds that resolved NOT_SOURCEABLE.

5. **Resatorvid is not approved** (ChEMBL `max_phase=3`, `first_approval=null`).
   Its `APPROVED_REPURPOSING` tag overstates its status.

## 3.2 In my own work (found and fixed)

6. **Co-fold consistency was computed on unaligned frames.** Each diffusion
   sample is generated in its own global frame, so raw ligand-coordinate
   comparison produced nonsensical 13–17 Å "consistency". Fixed by superposing
   receptors first; values became 0.70–3.21 Å. **The bad numbers were never
   used downstream** — verified: only two files carry the column and both are
   post-fix.

7. **I powered h3 off while another lane was mid-run.** My EX32 auto-shutdown
   watchdog fired at 16:45 UTC and killed the active-vs-decoy benchmark at
   30/152 shards and the counter-screen at 36/210. Both are resumable (`.done`
   sentinels intact, 0 corrupt pose files verified) but **neither produced its
   deliverable.** Self-inflicted, and the direct reason the panel has no
   calibration or active-state columns.

8. **`v2_sourceability.py` stalled three times** on hanging requests (Mcule
   HTTP 429 quota, then requests with no timeout). Replaced for the finalists
   by `v3_vendor_check.py`, which hard-timeouts every call and flushes
   continuously — it resolved all 80 finalists in ~2 minutes.

## 3.3 In external data (verified independently)

9. **PubChem name lookups return the WRONG stereoisomer for GB88, GB110 and
   C391.** All three resolve to GtoPdb-derived records that are
   stereochemically or constitutionally defective:
   - GB88: name search → CID 73755230 (**allo-Ile**); published is CID 57330164
     (**2S,3S** L-Ile). Verified by recomputing InChIKeys from SMILES:
     `DCUDDCGUKZLQLN-ZEZZXZOMSA-N` vs `DCUDDCGUKZLQLN-MCOVPRHSSA-N`.
   - GB110: name search → CID 49843508, Ile Cβ **undefined**.
   - C391: PubChem holds the **free acid**; the published compound is the
     C-terminal **amide**.
   The market resolves GB88: the (2S,3S) form has 30 vendor leads, the GtoPdb
   form has one. **Order the (2S,3S).**

10. **C376 does not exist** in the indexed literature — likely a transcription
    slip for C732. **PZ-235 is a lipidated 18-mer pepducin** acting on the
    intracellular face; it is not a docking benchmark. **C781 has no deposited
    structure anywhere** — reconstructible only from patent US11952379B2.

---

# 4. SCIENTIFIC FINDINGS

## 4.1 Co-folding was validated against the crystal — and it works

Boltz-2.2.1, wild-type human PAR2 (UniProt P55085) residues **59–370** — no
BRIL/T4L fusion, no thermostabilising mutations, and the N-terminal tethered
ligand (1–58) deliberately excluded so it cannot compete for the orthosteric
site. **The GNINA pose was never supplied**; the only spatial information was
the identity of the 17 crystallographic contact residues at 6 Å.

AZ8838 recovered its own crystal binding mode:

| model | confidence | ligand ipTM | backbone RMSD | ligand RMSD | centroid displacement |
|---|---|---|---|---|---|
| 0 | 0.960 | 0.979 | 1.16 Å | 1.22 Å | **0.69 Å** |
| 1–4 | 0.953–0.958 | 0.974–0.980 | 0.98–1.14 Å | 1.23–1.27 Å | 0.71–0.89 Å |

All five diffusion samples agree. MSA: ColabFold MMseqs2, 6,463 sequences,
computed once and reused.

## 4.2 Sample-to-sample consistency is the real discriminator

Confidence does **not** separate classes — everything scores 0.87–0.96, and
GB110 (a confirmed **agonist**) scores 0.926, above two de novo designs. Pocket
occupancy does not separate them either — the GB-series all reach 1.00 simply
by being large enough to touch every constrained residue.

**Consistency separates them cleanly:**

| class | consistency |
|---|---|
| crystal orthosteric binders + propranolol (AZ8838 0.74, propranolol 0.70, AZ3451 0.82) | **0.70–0.82 Å** |
| de novo designs | **1.16–1.70 Å** |
| GB-series peptidomimetics (GB88 2.65, GB88-alloIle 2.38, GB83 3.20, GB110 3.21) | **2.38–3.21 Å** |

## 4.3 Two independent methods agree that GB88 is not in the AZ8838 pocket

The active-state lane established from **PDB 9E7R (PAR2/GB88)** that GB88 binds
at the tethered-ligand site, **~17 Å from the AZ8838 pocket**, overlapping the
tethered ligand at **80%** of its heavy atoms and the AZ8838 pocket at **0%**.

Independently, co-folding shows GB88 cannot converge on a pose when forced into
that pocket. **A crystal structure and a co-folding consistency measurement
agree.** This is the strongest internal validation the campaign produced.

Corroborating this, the tethered-ligand-box smoke test ranked **GB88 1st in
8ZME and 3rd in 8ZMD** on size-residualised score, while **AZ8838 scored worse
than its size predicts in both** (+0.42, +0.21) — the correct direction.

## 4.4 The Boltz affinity head is not trustworthy here

It gives the crystallographic binder AZ8838 a binder probability of only
**0.583**, and ranks GB88 (−0.935) and GB110 (−0.655) as *better* binders than
AZ8838 (+0.789) — i.e. it scores a confirmed agonist above the crystal
antagonist. **Demoted to 10% of the co-folding family (~2% of the final
score).** Structural evidence carries the other 90%.

## 4.5 Interaction-fingerprint recovery is weaker evidence than it looks

- **Only 2 of the 16 crystal reference keys in 5NDD are hydrogen bonds.** A pose
  that merely fills the pocket can reach **0.875 recovery without forming a
  single H-bond.**
- **67 of 80 finalists hit all three 5NDD polar anchors** (and 66% of the
  full campaign universe did). Anchor count is necessary, not sufficient.
- The decoy null that would quantify this **did not finish** (see §6).

Treat IFP recovery as a filter, never as a score.

## 4.6 The allosteric (5NDZ) lane is weakly supported

| metric | 5NDD | 5NDZ |
|---|---|---|
| median IFP recovery | **0.75** (max 0.875) | **0.42** (max 0.75) |
| finalists hitting all 3 anchors | **67/80** | **0/80** (max 1 of 3) |
| DESIGN_HOTSPOT_SCORE in panel | 0.88–0.95 | **0.32–0.37** |

The brief said not to reserve a lane for symmetry if its chemistry is bad. **On
this evidence it is bad. Recommend cutting the 4 allosteric slots to 0–2.**

## 4.7 Cavity volume was discarded rather than cherry-picked

Across the four active-state structures the *same* orthosteric pocket measured
**15.1 to 224.8 Å³** — a 15-fold scatter, larger than the effect it was meant
to detect. At 3.10–3.25 Å cryo-EM resolution the buried rotamers are not
determined. You could read "the pocket collapses" from 9D0A and "the pocket
opens" from 8ZME from the same data, so the channel was recorded **inconclusive
and excluded**. The allosteric pocket behaved consistently (42–68 Å³ active vs
56.9 Å³ inactive) and remains usable.

## 4.8 Microswitch contacts are mostly unmeasurable
All five class-A motifs were located in PAR2 numbering and matched exactly, but
only ALA120/ASP121 (D2.50) lie within reach of any ligand site, and only from
the allosteric pocket. DRY-equivalent is 28–36 Å away, NPxxY 12–30 Å, CWxP
toggle 12–20 Å. Recorded **MISSING, never zero** — this is the same trap that
retired the earlier agonist-mimicry flag.

## 4.9 Propranolol
Co-folds as well as the crystal ligand: best ligand ipTM in the whole set
(**0.984**), consistency 0.70 Å, binder probability 0.663 (above AZ8838's
0.591). Consistent with its previously noted crystal-IFP recovery of 0.938.
Cheap, approved, topically formulated, decades of human exposure. Kept in the
reference panel as a probe. **This is not evidence it antagonises PAR2.**

## 4.10 Findings for the Wan conversation

- **P2L-003 is Professor Wan Namkung's own compound** — Park et al., *Bioorg
  Chem* 2025;167:109285, PMID 41308341, co-authored by him. Verified via
  Crossref and NCBI. No PubChem/ChEMBL structure exists, so no structure search
  was possible. **Asking the authors is the cheapest route to it.**
- **RWJ-50353 is a selective thrombin inhibitor** (Kᵢ 0.19 nM, ≥330-fold
  selectivity) — *not* a broad serine-protease inhibitor as the handoff stated.
  The caution is sharper, not weaker.
- **The "~80% melanin-uptake reduction" figure could not be found in any
  accessible source.** Flagged NOT_VERIFIED. The project's founding premise is
  weaker than the handoff implies.
- **Both AZ compounds are in stock** with 2025-Q3 catalogue membership.
- **C391 and RWJ-50353 have zero vendor hits** — budget custom synthesis or
  drop them.

---

# 5. WHAT WAS BUILT AND RUN

| stage | result |
|---|---|
| De novo seeds frozen | **32** (26 5NDD / 6 5NDZ), 30 EX32-supported, 30 scaffolds, 3 novelty bands; all 20 prior finalists carried forward |
| In-stock catalogue searched | **3,971,098** molecules, 430 files, 258 MB, local ECFP4 |
| Analogues retrieved (Agent 2) | **1,043** deduplicated; 218 with supplier records, **48 with native Enamine catalogue IDs** |
| Finalist queue | **80** molecules, 74 scaffolds (50 already-screened real + 30 never-screened in-stock) |
| Finalist preparation | 80/80, 0 failed, **0 stereocentres lost** |
| Finalist EX32 | **16/16 shards**, 1,440 poses (80 × 2 pockets × 9) |
| ProLIF | **160 ligand-pocket pairs, 0 failures** |
| Vendor resolution | 43 IN_STOCK_VENDOR_LISTED / 34 REGISTERED_NOT_VERIFIED / 3 NOT_SOURCEABLE; **72 EXACT**, 5 connectivity-only, 3 no-match |
| Co-folding | AZ8838 + AZ3451 validation; 21 batch-1 jobs; 18 control jobs; 98 finalist jobs launched (**incomplete**) |
| Benchmark actives curated | **124** rows (72 verified, 35 scaffolds) + **1,757** property-matched decoys |
| Reference control panel | **12** compounds with real catalogue IDs |

**Validated docking system, unchanged and hash-verified before every run:**
GNINA v1.3.3 `3340c1f4…6f72172`; 5NDD receptor `c2411d4d…09c4e`; 5NDZ
`af9f9eec…220b92`; `--no_gpu --cnn_scoring rescore --cpu 4 --num_modes 9 --seed
20260904`. Boxes: 5NDD centre `16.974 5.926 55.826` size `17.332 17.672
13.644`; 5NDZ centre `1.356 12.419 48.400` size `20.702 17.885 25.525`.

---

# 6. WHAT IS MISSING, AND WHY

| missing | why | recoverable? |
|---|---|---|
| **Co-folding columns in the panel** | 98 jobs launched on a100-40; the session rate limit ended the orchestration and the VM self-terminated at ~6/98 | Yes — restart a100-40, results on its boot disk |
| **Active-vs-decoy enrichment (ROC-AUC, EF1%, BEDROC) and the IFP null** | My watchdog powered h3 off at 30/152 shards | Yes — `~/BENCH/run_all.sh` is resumable, `.done` sentinels intact |
| **Active-state warning column** | Same shutdown; counter-screen reached 223 done-markers of 322 jobs | Yes — resumable |
| **Price, quantity, purity, lead time** | Every route carrying them is credential-gated (MolPort API, Enamine store API, Chemspace, eMolecules all need keys/accounts) | Only with vendor accounts |
| **Agent 2's 1,043 analogues in the panel** | Landed at 17:47, after the finalist queue was frozen | Yes — highest-value next step |
| **Short MD tie-breaker** | Deliberately not run; the brief said not to let it delay the TOP20 | N/A |

## Sources that were blocked — recorded, not worked around
- **Official Enamine Screening Collection SDFs: behind a login wall.** Every
  `/component/download/?view=file&f=<id>` link returns an HTML "Login - Enamine"
  page. **No account was created and no credentials entered.** ZINC20's plain
  file server was used as a labelled substitute.
- **`zinc20.docking.org` now serves a "Verify you're human" challenge. It was
  NOT bypassed.** `files.docking.org` needed neither.
- MolPort API (credentials), Enamine store API (account+key), Chemspace REST
  (key), eMolecules (no public API), Mcule prices (401, then 429 quota),
  MedChemExpress (403).

---

# 7. HOW TO FINISH

1. **Restart `a100-40`**, pull `~/COFOLD_FINALISTS.tgz`, run
   `v3_analyse_cofold.py`, re-run `v3_final_sourceable_panel.py --cofold`.
2. **Restart `h3`**, resume `~/BENCH/run_all.sh` and the `~/activestate` runner.
   Both skip completed shards. Archive of current state:
   `../PAR2_LANE_RESULTS_2026-09-06/H3_LANES_FINAL.tgz` (19.7 MB, 1,181 entries).
3. **Fold in the 1,043 retrieved analogues** — 48 carry native Enamine
   catalogue IDs and are the best chance of fixing §2.4.
4. **Re-rank** with the active-state hard gate and a decoy-calibrated IFP
   weight, and **cut the 5NDZ lane** to what §4.6 supports.
5. **Do not** re-run the de novo screen, the 4,835-compound real screen, or
   broad MD.

---

# 8. STANDING GUARDRAILS

- Never call a molecule a PAR2 antagonist from docking, CNN, similarity or
  co-folding.
- Keep 5NDD and 5NDZ evidence separate; never pool raw scores across pockets.
- CNNscore, CNNaffinity and Boltz affinity are ranking features, not calibrated
  probabilities.
- **Missing values stay missing.** Never write 0 for an absent measurement.
- Correlated scores are one vote, not six (Vina↔LE −0.958, Vina↔PIGNet2 0.899,
  CNNscore↔CNN_VS 0.988; IFP recovery correlates ≤0.19 with all — it is the
  only orthogonal channel).
- The dangerous failure mode is **Gq-antagonist + G12/13-agonist**. Only the
  functional assay finds it.
- **The largest uncertainty in the whole project is unchanged and is not
  chemical:** nobody has shown that selective PAR2 antagonism reduces melanocore
  uptake. The cheapest way to settle it is the reference panel
  (`PAR2_REFERENCE_PANEL_FOR_WAN.csv`) in a keratinocyte melanocore-uptake assay
  plus a G12/13→RhoA counter-screen. **That is worth more than any molecule we
  designed.**
