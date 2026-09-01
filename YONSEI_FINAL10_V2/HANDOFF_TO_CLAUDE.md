# Handoff to Claude: PAR2/F2RL1 Yonsei V2 and CPU de novo campaign

## 1. Purpose of this handoff

This document is the complete working handoff for the existing `MoheetBrain/Pigment-Firewall-PAR2` computational drug-discovery project. It is intended to let Claude—or another technically capable collaborator—continue the work without rediscovering the project history, repeating invalid V1 assumptions, confusing historical diagnostics with validated V2 results, or overstating what the computational evidence establishes.

The branch is `yonsei-final10-v2`. This is an extension of an existing project, not a clean-room redesign. Historical V1 files and rankings were deliberately preserved. New work was written beneath `YONSEI_FINAL10_V2/` and in new commits. The branch began from GitHub `main` at commit `b771e01` and contains the audit/reference-model commit `71325ea`, the forced-CPU GNINA benchmark commit `3ef8dab`, and a later commit containing the de novo outputs, the exact production script, this handoff, and README updates.

The scientific objective remains prospective nomination of approximately ten sourceable, chemically diverse PAR2/F2RL1 antagonist or inhibitor candidates for functional testing in Wan Namkung's laboratory at Yonsei University. Computational outputs are prioritisation evidence. They are not proof of PAR2 antagonism and must not be presented as calibrated probabilities of inhibition.

## 2. Scope history and why the work changed phases

The original V2 instructions required a non-destructive audit of V1, repair of two reference-pocket models, fresh GNINA redocking, sourceability triage, corrected candidate redocking only after both references passed, and then an integrated top-100/top-50/top-20 ranking. Large de novo generation was explicitly out of scope during that validation phase.

The audit and reference preparation were completed first. Local execution on Apple Silicon was not a reliable path to the required GNINA benchmark, so candidate redocking was correctly blocked until a compatible environment became available. The work then moved to the GCP VM `moheetc4`, where GNINA was installed and forced to CPU. Both fresh corrected reference redocks passed the primary best-pose RMSD gate. Candidate docking was still not launched at that point, in accordance with the instruction to report the benchmark before beginning a large screen.

A later explicit user request supplied `par2_denovo_cpu.py`, requested that errors be fixed, required a 15,000-molecule result, authorised VM optimisation, and specifically required CPU operation. That later request expanded the scope. The completed de novo campaign therefore does not represent an accidental violation of the earlier phase boundary; it was separately authorised after the reference benchmark work. Chemistry targets and scientific priors were preserved, while implementation and execution logic were repaired and optimised for the 24-vCPU VM.

## 3. Repository and data-preservation rules

Repository remote:

```text
https://github.com/MoheetBrain/Pigment-Firewall-PAR2.git
```

Working branch:

```text
yonsei-final10-v2
```

Historical V1 directories were treated as read-only evidence:

- `GNINA_SCREEN_EX32/`
- `RESULTS/`
- `PROTEINS/`
- `BENCHMARK_LIGS/`
- `SCREENING/`
- `BIN/GNINA_RUN_EX32_CPU/`

No V1 result, receptor, benchmark ligand, score table, or screening library was deleted or overwritten. Corrected models, audits, reports, and generated products live under `YONSEI_FINAL10_V2/`. Some source SDF/library files are intentionally ignored by `.gitignore` because of size. Private keys under `KEYS/` are also ignored and must never be committed.

The temporary gcloud browser-verification credential supplied during login was used only to authenticate the CLI session. It was not written into a project file or committed. Do not copy authentication codes, SSH private keys, access tokens, or cloud credentials into this repository.

## 4. Scientific model: two distinct antagonist mechanisms

The project must preserve two separate PAR2 antagonist hypotheses because the sites are physically and mechanistically distinct.

### 4.1 5NDD / AZ8838 / 8TZ: orthosteric-extracellular site

The 5NDD model represents inactive PAR2 with AZ8838 in the orthosteric/extracellular antagonist pocket. The clean crystallographic ligand residue is `8TZ`. The de novo script calls this the `orthosteric` family and allocates the largest design budget to it.

The working medicinal-chemistry prior favours compact, non-peptide-like, moderately lipophilic, non-planar/sp3-rich molecules with enough aromatic/hydrophobic surface and hydrogen-bond acceptor capacity to potentially reproduce the extracellular-loop/transmembrane-cleft interactions after three-dimensional docking. Those are soft design priors; the actual test is pose recovery and pocket-specific interaction analysis.

### 4.2 5NDZ / AZ3451 / 8UN: extrahelical allosteric site

The 5NDZ model represents inactive PAR2 with AZ3451 in the lipid-facing extrahelical negative-allosteric pocket between transmembrane helices. The clean crystallographic ligand residue is `8UN`. The de novo script calls this the `allosteric` family.

This pocket can tolerate somewhat greater lipophilicity, but the design logic deliberately caps cLogP and retains heteroatom/polar requirements. This is intended to avoid simply selecting greasy molecules that score favourably in a lipid-facing Box B environment. The allosteric mechanism is retained as an independent route, while acknowledging possible lipophilicity artefacts and probe-dependent pharmacology.

### 4.3 Exploratory family

The `exploratory` family preserves uncertainty. It is not anchored to a single reference family during BRICS generation. Its 1,500-molecule allocation explores valid chemistry assembled from the shared project-derived fragment pool and is routed to both corrected pockets for downstream docking.

No universal PAR2 pharmacophore was created. No 2D score was allowed to substitute for pocket-specific 3D evidence.

## 5. What V1 actually contained

The V1 audit is reproducible through `YONSEI_FINAL10_V2/scripts/audit_v1.py`. Its principal human-readable result is `00_AUDIT/V1_AUDIT.md`; detailed machine-readable results are in `V1_AUDIT_SUMMARY.json` and supporting CSV/JSON inventories.

### 5.1 Pass-1 and final ranking counts

Confirmed counts:

- Pass-1 contained 2,487 result rows and 1,255 unique row keys.
- Box A/orthosteric contributed 1,256 Pass-1 result rows.
- Box B/allosteric contributed 1,231 Pass-1 result rows.
- Pass-1 library rows were 317 COCONUT, 8 FDA drugs, 1,798 LOTUS, 36 MITF scaffolds, and 328 NPAtlas.
- `RESULTS/CNN_FINAL_SCORES.csv` contains the historical final 500.
- The final 500 contains 389 LOTUS, 77 NPAtlas, 32 COCONUT, and 2 MITF records.
- The final 500 site allocation is 396 Box A and 104 Box B.
- Thirty-two final-500 rows could not be linked back to Pass-1 by exact InChIKey or SMILES.
- The final-500 table has 111 missing InChIKeys and 121 missing Wikidata IDs.

The rank-prefix composition explains why the original list was not a procurement-ready experimental list:

| Prefix | Box A | Box B | Main library composition |
|---:|---:|---:|---|
| Top 10 | 0 | 10 | 9 LOTUS, 1 COCONUT |
| Top 50 | 9 | 41 | 42 LOTUS, 5 COCONUT, 3 NPAtlas |
| Top 100 | 32 | 68 | 82 LOTUS, 10 COCONUT, 6 NPAtlas, 2 MITF |
| Top 500 | 396 | 104 | 389 LOTUS, 77 NPAtlas, 32 COCONUT, 2 MITF |

The V1 top ten was entirely Box B and heavily dominated by natural products. That ranking must not be treated as a final experimental shortlist. Natural-product database presence does not establish commercial availability, and GNINA/CNN values are ranking features rather than calibrated biological probabilities.

### 5.2 Historical Pass-2 status

The repository contains 35 non-empty Pass-2 input structures, but all 105 expected Pass-2 output files are empty. Therefore, a clean completed historical 35-candidate Pass-2 shortlist does not exist. Log filenames are evidence that jobs were configured, not evidence that usable Pass-2 outputs were produced.

### 5.3 Historical implementation and path problems

The V1 GNINA driver hard-coded `/Users/mk/PycharmProjects/Pigment-Firewall-PAR2`, which is not the checked-out repository path. It referenced several absent library files, including historical COCONUT, LOTUS, NPAtlas, and generated bleaching SDF paths. Historical Box A and Box B configuration files also resolve to receptor filenames that are absent from the checkout.

There are 313 historical GNINA command logs: 208 Pass-1 and 105 Pass-2. All recorded `min_rmsd_filter` values are 2.0. The audit found 313 no-GPU warnings. The presence of these logs is useful provenance but does not repair missing outputs or incorrect boxes.

## 6. Benchmark defects confirmed and repaired

### 6.1 Contaminated historical ligand files

The historical `BENCHMARK_LIGS/lig_AZ8838_orthosteric_boxA.pdb` contained the desired 17-heavy-atom 8TZ ligand plus ten waters, one sodium, and five phosphate residues. The historical `lig_AZ3451_allosteric_boxB.pdb` contained the desired 38-heavy-atom 8UN ligand plus two waters and one sodium.

For V2, only the crystallographic antagonist residue was retained in each clean ligand. Receptors and ligands remained in the original experimental coordinate frame. Unrelated HETATM species were excluded. Clean ligand and receptor artifacts are in `01_REFERENCE_POCKETS/ligands/` and `01_REFERENCE_POCKETS/receptors/`.

### 6.2 Displaced and oversized historical boxes

The old Box A centre was 13.889 Å from the AZ8838 heavy-atom centroid and used a 40 Å cube. The old Box B centre was 6.001 Å from the AZ3451 heavy-atom centroid and was also broad. These were not accepted for V2.

Corrected boxes were calculated directly from the clean crystallographic heavy-atom coordinates and used ligand dimensions plus 5 Å on every side. This is approximately the requested 6 Å padding and is recorded exactly in the configs and metadata.

| System | Heavy atoms | Centre x/y/z (Å) | Ligand span x/y/z (Å) | Corrected size x/y/z (Å) |
|---|---:|---|---|---|
| 5NDD / AZ8838 / 8TZ | 17 | 16.974, 5.926, 55.826 | 7.332, 7.672, 3.644 | 17.332, 17.672, 13.644 |
| 5NDZ / AZ3451 / 8UN | 38 | 1.356, 12.419, 48.400 | 10.702, 7.885, 15.525 | 20.702, 17.885, 25.525 |

The exact configs are:

- `01_REFERENCE_POCKETS/configs/BoxA_orthosteric_5NDD_ligand_centered.conf`
- `01_REFERENCE_POCKETS/configs/BoxB_allosteric_5NDZ_ligand_centered.conf`

### 6.3 Historical redock files were not treated as V2 passes

Historical diagnostic SDFs under `BIN/GNINA_RUN_EX32_CPU/` gave encouraging best symmetry-corrected RMSDs of approximately 0.465 Å for 5NDD/AZ8838 and 1.002 Å for 5NDZ/AZ3451. They were explicitly not counted as V2 benchmark passes because the original command/config provenance was unavailable and the corrected ligand-centred boxes could not be established. Fresh output was required.

## 7. GNINA environment and forced-CPU benchmark

### 7.1 VM

The execution VM was:

```text
Name: moheetc4
GCP project: project-08679972-d14a-4025-94f
Zone: europe-west2-c
OS: Debian GNU/Linux 13 (trixie)
Architecture: x86_64
Machine type: c4-standard-24
CPU: 24 vCPUs, Intel Emerald Rapids
Memory: 90 GB
GPU: none
```

SSH entry point:

```bash
gcloud compute ssh --zone "europe-west2-c" "moheetc4" --project "project-08679972-d14a-4025-94f"
```

The VM had no Docker/Colima, Conda/Mamba, NVIDIA device, or Apple Silicon. CPU execution was therefore mandatory.

### 7.2 GNINA installation

The official Linux x86_64 GNINA v1.3.3 static release was installed at `/home/moheet/bin/gnina.cuda12.8.static`.

Recorded version:

```text
gnina v1.3.3 master:6fe1ce2 Built Jun 30 2026
```

Binary SHA-256:

```text
3340c1f49cd3c7c84d8699182a1c6af13c7fa2a22448d1204640446106f72172
```

Although docking was forced to CPU, the official binary dynamically links CUDA libraries. Pinned NVIDIA Python wheels were installed under `/home/moheet/gnina-cuda-libs` to satisfy runtime loading: CUDA runtime 12.9.79, NVRTC 12.9.86, cuDNN 9.24.0.43, cuBLAS 12.9.2.10, cuSPARSE 12.5.10.65, cuFFT 11.4.1.4, cuSOLVER 11.7.5.82, and NVJitLink 12.9.86.

The validation virtual environment was `/home/moheet/par2-v2-venv`, using Python 3.13.5 with RDKit 2026.3.5, ProLIF 2.2.1, spyrmsd 0.9.0, BioPython 1.88, PLIP 3.0.1, pandas 3.0.5, NumPy 2.5.2, and SciPy 1.18.0. Debian Open Babel 3.1.1 was also available.

### 7.3 Exact benchmark settings

`scripts/run_gnina_reference.sh` is the reproducible reference-only runner. Both jobs used:

```text
CUDA_VISIBLE_DEVICES=-1
--no_gpu
--exhaustiveness 32
--num_modes 9
--cnn_scoring rescore
--min_rmsd_filter 2.0
--seed 20260811
--cpu 4
```

The runner saves the exact command, GNINA version, seed, receptor, ligand, config, SDF, and log in `01_BENCHMARK_REPAIR/corrected_redock/`. `verify_reference_systems.py` checks the clean residues, contaminants, coordinate frame, and calculated centres before execution. `validate_reference_redock.py` calculates symmetry-corrected heavy-atom RMSD with spyrmsd and pocket-specific ProLIF interaction recovery.

### 7.4 Fresh corrected benchmark results

| System | Poses | Best RMSD | Top-ranked RMSD | Top-ranked IFP recovery | Best IFP recovery | Gate |
|---|---:|---:|---:|---:|---:|---|
| 5NDD / AZ8838 | 9 | 0.674658 Å, pose 1 | 0.674658 Å | 0.500 | 0.700 | strong PASS |
| 5NDZ / AZ3451 | 9 | 0.867183 Å, pose 2 | 2.227395 Å | 0.889 | 0.889 | strong best-pose PASS |

The primary gate is best symmetry-corrected heavy-atom RMSD no greater than 2.0 Å; no greater than 1.5 Å is a strong result. Both systems therefore passed strongly by their best pose, and `OPEN_REFERENCE_BENCHMARK_PASSED=TRUE`.

The nuance for 5NDZ must be retained: its top GNINA-ranked pose is not under the 2 Å geometric threshold, although it recovers 0.889 of the reference ProLIF keys. Pose 2 is the crystallographic-like geometric result at 0.867 Å. Do not report that the 5NDZ top-ranked pose itself passed the geometric criterion.

## 8. Sourceability triage completed before de novo generation

`scripts/build_candidate_universe.py` created `03_SOURCEABILITY/V2_CANDIDATE_UNIVERSE.csv`, a 5,973-structure deduplicated triage universe. It combines:

- all 500 V1 final-ranking rows;
- 4,487 FDA/approved-library records represented in the universe;
- 1,075 other identifiable V1 hits.

All 5,973 structures parse in RDKit. The table preserves original V1 rank, box/site, library, and score information where available and adds sourceability/procurement fields. No live vendor lookup was performed, so commercial availability, vendor, catalogue ID, price, and stock remain explicitly `PENDING`. The V1 top-100 sourceability table contains 100 matched rows, all with `PENDING_LIVE_VENDOR_LOOKUP` and no established human-exposure status from live verification.

The sourceability report was originally written while fresh reference docking was blocked. Its historical wording reflects that point in time. The later benchmark result supersedes only the gate status; it does not fabricate procurement information or turn the universe into a biological ranking.

## 9. CPU de novo campaign: objective and allocation

The production objective was exactly 15,000 unique, filtered small-molecule designs, optimised for a 24-vCPU CPU-only VM. The fixed allocation was:

- 10,000 orthosteric-family designs (66.67%);
- 3,500 allosteric-family designs (23.33%);
- 1,500 exploratory designs (10.00%).

The asymmetric allocation reflects a stronger first-pass case for the orthosteric/AZ8838 family in a topical pigmentation programme, while preserving the allosteric/AZ3451 mechanism and an exploratory uncertainty budget. It is a design-resource allocation, not a claim that one mechanism is biologically proven superior.

The exact production script is committed as `scripts/par2_denovo_cpu.py`. It is byte-identical to `/home/moheet/par2_denovo_cpu.py` on the VM and the recovered local copy in Downloads. Its SHA-256 is:

```text
10f8e089d8163ed7c08db0983c105950987024398e22387efdab049e5735a60f
```

## 10. De novo inputs and fragment construction

The run used three project-derived inputs:

1. `00_AUDIT/V1_TOP500.csv` as the donor-chemistry table;
2. clean crystallographic 5NDD/AZ8838 SDF as the orthosteric reference seed;
3. clean crystallographic 5NDZ/AZ3451 SDF as the allosteric reference seed.

The production VM paths recorded in the manifest are `/home/moheet/YONSEI_FINAL10_V2/00_AUDIT/V1_TOP500.csv`, `/home/moheet/YONSEI_FINAL10_V2/01_REFERENCE_POCKETS/ligands/5NDD_AZ8838_crystallographic_clean.sdf`, and the analogous 5NDZ/AZ3451 path.

The script reads up to 500 valid donor SMILES from V1. V1 molecules are used only as fragment donors and diversity chemistry. Their old CNN scores or rank are not inherited as biological truth.

RDKit BRICS decomposition is applied to both clean reference ligands and the donor set. General fragment-pool fragments must contain 3–16 heavy atoms. Family reference fragments use a broader 2–20-heavy-atom range. The final shared pool contained 903 unique BRICS fragments; AZ8838 produced four usable seed fragments and AZ3451 produced six.

Orthosteric and allosteric generation is initially anchored to at least one fragment from the corresponding crystallographic ligand. Exploratory generation is unanchored. If a seeded family cannot fill its raw quota within the bounded shard runtime, the algorithm allows unseeded recombination from the same project-derived pool instead of silently returning an undersized campaign. This fallback broadens chemistry but does not change descriptor/filter/scoring logic.

Canonical isomeric SMILES are used for deduplication. Molecules with fewer than 12 or more than 44 heavy atoms are rejected during canonicalisation.

## 11. De novo family priors and hard filters

The following are exact script settings. Gaussian targets are soft preferences; hard ranges are eligibility limits.

### 11.1 Orthosteric family

Soft targets: MW 360, cLogP 3.0, TPSA 65, HBA 3.5, HBD 1.0, rotatable bonds 4.0, fraction sp3 0.35, aromatic rings 2.0, and Morgan reference Tanimoto 0.38.

Gaussian sigmas: MW 85, cLogP 1.0, TPSA 25, HBA 2.0, HBD 1.3, rotatable bonds 3.0, fraction sp3 0.22, aromatic rings 1.2, and reference similarity 0.20.

Hard limits: MW 230–500, cLogP 1.0–5.0, TPSA 25–115, HBA 1–9, HBD 0–3, rotatable bonds 0–9, formal charge −1 to +1, and no more than six rings.

### 11.2 Allosteric family

Soft targets: MW 375, cLogP 3.7, TPSA 52, HBA 3.0, HBD 0.7, rotatable bonds 3.5, fraction sp3 0.30, aromatic rings 2.0, and Morgan reference Tanimoto 0.35.

Gaussian sigmas: MW 90, cLogP 1.0, TPSA 24, HBA 1.8, HBD 1.1, rotatable bonds 2.8, fraction sp3 0.22, aromatic rings 1.2, and reference similarity 0.20.

Hard limits: MW 240–510, cLogP 1.8–5.5, TPSA 18–100, HBA 1–8, HBD 0–3, rotatable bonds 0–8, formal charge −1 to +1, and no more than six rings.

### 11.3 Exploratory family

Soft targets: MW 350, cLogP 3.1, TPSA 62, HBA 3.5, HBD 1.0, rotatable bonds 4.0, fraction sp3 0.32, aromatic rings 2.0, and maximum reference Tanimoto 0.25.

Gaussian sigmas: MW 110, cLogP 1.4, TPSA 34, HBA 2.5, HBD 1.7, rotatable bonds 4.0, fraction sp3 0.28, aromatic rings 1.5, and reference similarity 0.25.

Hard limits: MW 200–520, cLogP 0.5–5.7, TPSA 15–125, HBA 0–10, HBD 0–4, rotatable bonds 0–10, formal charge −1 to +1, and no more than six rings.

### 11.4 Structural alerts

All families are rejected if they match RDKit PAINS A, B, or C. A deliberately narrow reactive-group screen rejects acyl halides, sulfonyl halides, isocyanates, isothiocyanates, peroxides, and diazo groups. An enormous generic blacklist was intentionally avoided because it could discard valid medicinal chemistry. Surviving molecules still require expert review; passing these alerts is not a safety or developability guarantee.

## 12. De novo scoring logic

For each valid molecule, RDKit calculates molecular weight, Crippen cLogP, TPSA, hydrogen-bond acceptors, hydrogen-bond donors, rotatable bonds, fraction sp3, total rings, aromatic rings, formal charge, QED, a 2,048-bit radius-2 Morgan fingerprint, and a chirality-aware Bemis–Murcko scaffold.

Reference similarity is Tanimoto similarity to AZ8838 for the orthosteric family, to AZ3451 for the allosteric family, and the maximum of those two similarities for the exploratory family.

The score is exactly:

```text
design_score =
    0.50 * property_score
  + 0.20 * QED
  + 0.20 * novelty_score
  + 0.10 * family_feature_score
```

`property_score` is the mean of eight Gaussian preference terms: MW, cLogP, TPSA, HBA, HBD, rotatable bonds, fraction sp3, and aromatic rings.

`novelty_score` is a Gaussian around the family reference-similarity target. It implements a “Goldilocks” prior: avoid exact reference clones while avoiding chemistry that is completely unrelated to the working antagonist family.

The orthosteric feature term averages Gaussian preferences for HBA, aromatic rings, and fraction sp3. The allosteric term averages HBA, aromatic rings, cLogP, and fraction sp3. The exploratory term averages HBA and fraction sp3.

These are count-level two-dimensional design priors. They do not claim to know residue-specific contacts. Residue-level evidence is intentionally deferred to corrected GNINA poses and ProLIF/PLIP fingerprints.

## 13. VM performance work and error fixes

The chemistry definitions above were preserved. Engineering changes focused on making the script complete reliably and quickly on Linux CPU.

### 13.1 Parallel deterministic BRICS shards

Large serial BRICS generators have an expensive long tail. Generation was split into deterministic shards of approximately 500 desired products. Shards use independent seeds derived from the global seed, family offset, round, and shard index. Up to 200 shards per family are allowed. Four raw-generation rounds refill only remaining deficits.

### 13.2 Linux fork multiprocessing

On Linux the script uses the `fork` multiprocessing context, avoiding repeated serialisation of large RDKit objects. Twenty workers were used on the 24-vCPU VM, leaving four CPUs of headroom for the operating system and filesystem.

### 13.3 Cached BRICS matcher index

Stock `BRICSBuild` repeatedly rescans every fragment against both reaction matchers at every recursion. The production script precomputes compatible fragments for each reverse BRICS reaction once per generation worker. `fast_brics_build` preserves the same reaction chemistry and ordering semantics while using this cached matcher index.

### 13.4 Bounded shard runtime

Each generation shard has a 20-second monotonic deadline. This bounds pathological BRICS branches and allows many independent shards to keep all CPU cores productive.

### 13.5 Parallel scoring

Medicinal-chemistry filtering and scoring runs in a 20-worker pool with a chunksize of 128. Fingerprint generators, reference fingerprints, and the PAINS filter catalogue are initialised once per worker.

### 13.6 Filtered-quota refill

Raw oversampling does not guarantee enough molecules survive family-specific hard filters, PAINS/reactivity checks, and deduplication. The production script detects filtered deficits and performs up to four deterministic refill campaigns, generating only deficient families with an oversampling factor of at least 10. This was the key correctness fix that guaranteed the requested count without relaxing chemistry rules.

### 13.7 Cross-family deduplication and exact-count enforcement

The script assigns the scarcest family first, deduplicates exact canonical SMILES across families, and backfills from the ranked family pool. If the final cross-family unique count is not exactly the requested total, it raises a runtime error instead of silently emitting fewer molecules.

## 14. Production execution trace

The default global seed was `20260812`. The successful run detected 24 CPUs, used 20 workers, used raw oversampling 4.0, a 20-second generation-shard limit, and up to four filtered refill rounds.

`denovo.log` is append-only and contains two production-scale attempts:

1. The first attempt began at 09:25 on 12 August 2026 with a larger raw oversampling campaign. It scored 107,829 raw candidates but produced only 2,706 of the required 3,500 unique filtered allosteric designs. This diagnosed that raw oversampling alone could not guarantee the post-filter family quota.
2. The repaired successful attempt began at 09:35. It used the filtered-quota refill logic. Initial filtered deficits were 3,867 orthosteric, 2,111 allosteric, and one exploratory. Refill 1 generated 50,144 new unique raw molecules and 6,758 survivors. Refill 2 addressed a remaining 1,038 allosteric deficit with 8,204 new raw molecules and 526 survivors. Refill 3 addressed the remaining 512 allosteric deficit with 4,055 new raw molecules and 769 survivors. The final output completed at 09:46:41.

Aggregate raw-generation counts recorded in the successful manifest are 72,100 orthosteric, 42,230 allosteric, and 6,001 exploratory. After chemistry filtering, the pooled rows were 11,811 orthosteric, 3,757 allosteric, and 1,506 exploratory. `SCORED_CANDIDATES.csv` contains 17,074 family-labelled rows; 17,011 canonical SMILES are unique because the same chemistry can occur in multiple family-labelled pools before final cross-family assignment.

## 15. Final de novo results

### 15.1 Full 15,000 set

`02_DENOVO_CPU/DENOVO_15000.csv` contains exactly 15,000 data rows and 15,000 unique canonical SMILES. The family counts exactly match the requested 10,000/3,500/1,500 allocation. There are 6,725 unique recorded Murcko scaffolds.

Overall full-set descriptor summary:

| Field | Min | Median | Mean | Max |
|---|---:|---:|---:|---:|
| Design score | 0.3569 | 0.6894 | 0.6804 | 0.9648 |
| Reference Tanimoto | 0.0521 | 0.1505 | 0.1571 | 0.8462 |
| MW | 200.205 | 344.436 | 348.276 | 518.716 |
| cLogP | 0.503 | 3.293 | 3.239 | 5.672 |
| TPSA | 15.79 | 75.99 | 74.64 | 124.90 |
| HBA | 0 | 5 | 4.89 | 10 |
| HBD | 0 | 2 | 1.89 | 4 |
| Rotatable bonds | 0 | 4 | 4.41 | 10 |
| Fraction sp3 | 0.000 | 0.500 | 0.506 | 1.000 |
| QED | 0.210 | 0.735 | 0.712 | 0.946 |

The full-family selection attempts a maximum of 25 instances per scaffold within each family, but the cap is intentionally soft: after the capped pass, overflow rows can be used to fill an exact family quota. The maximum repeated scaffold in the complete set is therefore 109 across family-labelled selection and overflow. Do not claim the complete 15,000 has a universal hard 25-per-scaffold maximum.

### 15.2 Docking-priority 3,000 set

`DENOVO_TOP3000_FOR_DOCKING.csv` is not simply the top 3,000 numerical scores. It re-applies scaffold selection with a cap of 12, maintaining higher diversity before docking. It contains 3,000 unique SMILES and 1,492 unique scaffolds; no scaffold appears more than 12 times.

Family and routing counts:

- 1,867 orthosteric designs route to corrected 5NDD;
- 678 allosteric designs route to corrected 5NDZ;
- 455 exploratory designs route to both 5NDD and 5NDZ.

This corresponds to 3,455 ligand–pocket docking assignments before considering multiple poses or replicates.

Docking-set summary:

| Field | Min | Median | Mean | Max |
|---|---:|---:|---:|---:|
| Design score | 0.7595 | 0.8023 | 0.8102 | 0.9648 |
| Reference Tanimoto | 0.0714 | 0.1791 | 0.1879 | 0.5682 |
| MW | 200.285 | 314.341 | 311.702 | 465.296 |
| cLogP | 0.503 | 3.419 | 3.370 | 5.546 |
| TPSA | 17.07 | 62.04 | 61.63 | 105.64 |
| QED | 0.371 | 0.838 | 0.825 | 0.946 |

The docking subset is enriched for higher QED, lower MW, and higher design scores than the full filtered set because those quantities contribute directly or indirectly to ranking.

### 15.3 Output checksums

These checksums were verified after pulling the production directory from the VM to the local repository:

| File | SHA-256 |
|---|---|
| `DENOVO_15000.csv` | `43d894c2341aa51b3b2d0cb393ef4e0050aecbe205a717e9f86b77c7cf11568a` |
| `DENOVO_TOP3000_FOR_DOCKING.csv` | `d7461251ddbae77a2cc80573f74ea8636e2fae311167385fe1f29242c37a228c` |
| `SCORED_CANDIDATES.csv` | `ba7f1532c81cc49bb247482718c8d3a29647367f74283f5788aef1cd2e8790eb` |
| `GENERATION_MANIFEST.json` | `33a6af552b1e5873adf4248e8eb646a884b80b7e7942064d1635da513c1d9216` |
| `denovo.log` | `17dee19162d26e28adaf163881e8aefea008829472466aeebd9b9769b294f265` |
| `scripts/par2_denovo_cpu.py` | `10f8e089d8163ed7c08db0983c105950987024398e22387efdab049e5735a60f` |

The five production artifacts were compared against the remote `/home/moheet/YONSEI_FINAL10_V2/02_DENOVO_CPU` inventory and matched byte-for-byte. The script also matched `/home/moheet/par2_denovo_cpu.py` byte-for-byte.

This was not a full VM clone. GNINA/CUDA runtime installations, the Python environment, operating-system files, and temporary smoke-test directories remain on the VM. Everything needed to audit the completed run is local and committed, but rebuilding the runtime still requires the pinned environment details above.

## 16. What has not been done

The following work remains incomplete and must not be implied by the existence of the 15,000 designs:

- The 3,000 priority designs have not been converted into a complete protonation/tautomer/3D-conformer docking library.
- The 3,455 planned ligand–pocket assignments have not been run through corrected GNINA.
- No generated design has a corrected-pose GNINA score, ligand efficiency, ProLIF/PLIP fingerprint, or reference-IFP similarity.
- No generated design has been checked through live vendor catalogues.
- No V2 top 100, top 50, top 20, or final experimental ten has been produced.
- The existing 5,973-member V1/FDA sourceability universe has not yet undergone the corrected dual-pocket screen.
- No molecular dynamics, FMO, P2Rank, fpocket, PocketMiner, Boltz, Chai, new ML training, or synthesis planning has been performed.
- No wet-lab evidence has been generated.

Do not interpret `design_score`, `ref_tanimoto`, QED, GNINA CNN scores, or future docking values as probabilities of biological inhibition. The de novo CSVs are a design queue, not a candidate nomination.

## 17. Recommended next action

The immediate computational decision is whether to dock the de novo top 3,000 first, the sourceable V1/FDA universe first, or schedule both as separate campaigns. For the user’s stated goal of approximately ten sourceable compounds for near-term experimental testing, the existing FDA/approved and identifiable V1 universe has the clearer procurement path. De novo molecules may require analogue sourcing or synthesis and should not displace sourceability work merely because they are new.

For de novo docking, preserve the routing already written into `DENOVO_TOP3000_FOR_DOCKING.csv`:

```text
orthosteric -> corrected 5NDD/AZ8838 pocket
allosteric  -> corrected 5NDZ/AZ3451 pocket
exploratory -> both corrected pockets
```

Use the same official GNINA version and forced-CPU runtime unless a validated GPU environment is intentionally introduced. Retain multiple poses. Record exact command, seed, exhaustiveness, pose count, receptor/config checksum, input identity, return code, log, and output checksum per shard. Do not merge the two pockets into one universal score.

For every docked molecule calculate at minimum:

- GNINA/Vina affinity and CNN ranking features;
- best-pose and top-ranked-pose identity;
- ligand efficiency based on heavy atoms;
- pocket-specific ProLIF/PLIP interaction fingerprint;
- recovery/similarity to the correct crystallographic antagonist fingerprint;
- MW, cLogP, TPSA, HBA, HBD, rotatable bonds, fraction sp3, formal charge, QED;
- reactive/problematic chemistry flags;
- scaffold identity and diversity contribution;
- original V1 provenance or de novo family/rank;
- commercial availability, vendor, catalogue ID, price, and stock, with `PENDING` when unknown.

Ranking should retain separate 5NDD and 5NDZ lists and then integrate validated docking, reference-interaction recovery, ligand efficiency, avoidance of Box-B lipophilicity artefacts, chemical plausibility, sourceability, price, and scaffold diversity. Do not force an arbitrary quota from either pocket. A final ten should only be produced once benchmark provenance, compound identity, procurement, and chemical-diversity fields are sufficiently complete.

## 18. Reproduction commands

From the repository root, the audit/reference sequence is:

```bash
python YONSEI_FINAL10_V2/scripts/audit_v1.py
python YONSEI_FINAL10_V2/scripts/build_reference_models.py
python YONSEI_FINAL10_V2/scripts/reference_interactions.py
python YONSEI_FINAL10_V2/scripts/build_candidate_universe.py
python YONSEI_FINAL10_V2/scripts/verify_reference_systems.py
bash YONSEI_FINAL10_V2/scripts/run_gnina_reference.sh
```

The de novo smoke test is:

```bash
python YONSEI_FINAL10_V2/scripts/par2_denovo_cpu.py \
  --repo . \
  --n-total 300 \
  --top-docking 100 \
  --workers 8
```

The full CPU run is:

```bash
python YONSEI_FINAL10_V2/scripts/par2_denovo_cpu.py \
  --repo . \
  --n-total 15000 \
  --top-docking 3000 \
  --workers 20 \
  --oversample 4.0 \
  --seed 20260812 \
  --generation-shard-seconds 20 \
  --max-filter-refill-rounds 4
```

The script requires RDKit, pandas, NumPy, and tqdm. Exact output can depend on RDKit version, process scheduling, and BRICS enumeration order even with fixed seeds; the committed outputs and checksums are the canonical completed production artifacts. Do not rerun over them casually. Use a separate output directory for experiments.

## 19. File map for continuation

- `README.md`: concise current project status.
- `HANDOFF_TO_CLAUDE.md`: this full narrative and continuation contract.
- `00_AUDIT/V1_AUDIT.md`: human-readable V1 audit.
- `00_AUDIT/V1_AUDIT_SUMMARY.json`: comprehensive machine-readable audit.
- `00_AUDIT/V1_TOP10.csv`, `V1_TOP50.csv`, `V1_TOP100.csv`, `V1_TOP500.csv`: preserved V1 rank prefixes.
- `01_REFERENCE_POCKETS/`: corrected clean ligands, receptors, configs, and geometry metadata.
- `01_BENCHMARK_REPAIR/environment_report.md`: exact VM/GNINA/runtime record.
- `01_BENCHMARK_REPAIR/BENCHMARK_RESULTS.md`: concise fresh benchmark result.
- `01_BENCHMARK_REPAIR/reference_system_check.json`: programmatic pre-run integrity check.
- `01_BENCHMARK_REPAIR/corrected_redock/`: fresh SDFs, logs, and run metadata.
- `02_REFERENCE_VALIDATION/`: crystal fingerprints, pose metrics, interaction tables, and gate JSON/Markdown.
- `03_SOURCEABILITY/`: 5,973-candidate universe and V1 top-100 procurement view.
- `02_DENOVO_CPU/DENOVO_15000.csv`: final 15,000-design set.
- `02_DENOVO_CPU/DENOVO_TOP3000_FOR_DOCKING.csv`: diversity-aware downstream queue.
- `02_DENOVO_CPU/SCORED_CANDIDATES.csv`: preserved post-filter candidate pool.
- `02_DENOVO_CPU/GENERATION_MANIFEST.json`: production parameters and counts.
- `02_DENOVO_CPU/denovo.log`: complete append-only execution trace, including the failed first attempt and successful repaired run.
- `scripts/par2_denovo_cpu.py`: exact production generator.
- `scripts/run_gnina_reference.sh`: pinned forced-CPU reference runner.
- `scripts/validate_reference_redock.py`: RMSD/IFP validation and gate logic.

## 20. Final continuation guardrails

1. Preserve V1 and all current generated outputs.
2. Do not call a molecule a PAR2 antagonist from 2D design, docking, CNN, or similarity evidence alone.
3. Keep 5NDD and 5NDZ evidence separate until final multi-criteria prioritisation.
4. Treat the 5NDZ top-pose geometric nuance honestly.
5. Keep historical GNINA redocks diagnostic-only.
6. Do not invent procurement information.
7. Prefer sourceable candidates when the immediate goal is a near-term wet-lab ten.
8. Use exact checksums and run metadata for every large computational stage.
9. Use a new output directory for reruns; do not overwrite the canonical production CSVs.
10. The correct current state is: audit complete; corrected reference systems complete; fresh CPU GNINA benchmark passed; sourceability universe assembled but not live-verified; 15,000 de novo designs complete; 3,000-design docking queue prepared; candidate docking, integrated ranking, and final ten not yet complete.
