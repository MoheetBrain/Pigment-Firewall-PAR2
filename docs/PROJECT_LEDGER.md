# Project Ledger

Append-only. One entry per commit, in chronological order.

---

## 2026-09-04 · V2 screen pipeline built; de novo ligand library prepared

**Branch:** `yonsei-final10-v2`
**Project stage:** V2 campaign, stage 4 — ligand preparation complete, GNINA
screen not yet executed.

**Objective of the change**
Turn the finished 15,000-design de novo campaign into an executable, resumable
dual-pocket GNINA screen and the analysis chain that follows it, so that the
best de novo chemotypes can be identified and used as similarity-search queries
for real, purchasable analogue molecules.

Mid-task the user issued a course correction: do not expand this into a mass
screening pipeline, restrict actual GNINA screening to roughly the best 3,000
de novo designs, keep the 15,000-design library intact, and stop short of
nominating a final ten. The work below reflects that corrected scope.

**Files and systems changed**
- Added `YONSEI_FINAL10_V2/scripts/v2_prepare_ligands.py`
- Added `YONSEI_FINAL10_V2/scripts/v2_select_screen_set.py`
- Added `YONSEI_FINAL10_V2/scripts/v2_run_screen.sh`
- Added `YONSEI_FINAL10_V2/scripts/v2_collect_scores.py`
- Added `YONSEI_FINAL10_V2/scripts/v2_interactions.py`
- Added `YONSEI_FINAL10_V2/scripts/v2_postdock_rank.py`
- Added `YONSEI_FINAL10_V2/scripts/v2_cluster_and_seed.py`
- Added `YONSEI_FINAL10_V2/scripts/v2_similarity_search.py`
- Added `YONSEI_FINAL10_V2/scripts/v2_rank_and_select.py` (later gate)
- Added `YONSEI_FINAL10_V2/04_V2_SCREEN/` outputs and `RUNBOOK.md`
- Added `docs/PROJECT_STATUS.md` and `docs/PROJECT_LEDGER.md`
- Updated `.gitignore`

**What was completed**
- 8,973 input rows (3,000 de novo + 5,973 sourceable) standardised, protonated
  at approximate pH 7.4, embedded in 3D and deduplicated to 7,324 unique
  ligands (2,985 de novo, 4,339 sourceable).
- De novo screen set built: 2,985 designs, 3,436 ligand-pocket jobs
  (5NDD 2,314 · 5NDZ 1,122), 15 shards, coordinates copied verbatim from the
  prepared library.
- Complete downstream chain implemented and rehearsed end to end.
- Runbook written for `h3` (88 cores, 22 GNINA processes × 4 CPU).

**Decisions made and why**
- Screen scope narrowed to the de novo designs, per the user's course
  correction. The sourceable universe remains prepared but unscreened.
- Single-stage screening at the validated benchmark settings (exhaustiveness
  32, 9 poses) instead of a reduced-exhaustiveness pre-pass: on 88 cores the
  full de novo screen is roughly 1.5–2 hours, so a pre-pass saves nothing and
  would produce scores not comparable to the reference benchmark.
- All poses retained rather than pose 1, because the benchmark showed the 5NDZ
  top-ranked pose at 2.23 Å against a best pose of 0.87 Å.
- Ranking z-scores computed within each pocket; 5NDD and 5NDZ never pooled.
- Novelty implemented as a capped one-sided bonus, never a penalty.
- Seed selection uses a 25% per-pocket floor plus rank-driven fill, rather than
  a fixed 50/50 quota, so both mechanisms appear without overriding evidence.
- The 51 MB full prepared shard library is gitignored as deterministically
  reproducible; the 14 MB de novo screen set is committed because the VM needs
  it.

**Tests and verification actually executed**
- `ast.parse` on all eight new Python scripts: passed.
- `bash -n YONSEI_FINAL10_V2/scripts/v2_run_screen.sh`: passed.
- Protonation rule set on 20 hand-picked structures: all expected. This found a
  real defect — the first implementation used reaction SMARTS without atom maps
  and silently reduced molecules to their matched fragment (a 18-heavy-atom
  acid became formate). Replaced with direct atom edits and re-verified.
- `v2_prepare_ligands.py --limit 40` smoke test: 150 SDF records, 0 unparsable,
  exactly 1 conformer per record.
- Full preparation on 8,973 rows: 8,469 prepared, 504 failed (188 too few heavy
  atoms, 293 too many, 16 embed failures, 7 unsupported elements), 1,145
  duplicate InChIKeys collapsed, 7,324 unique ligands.
- `v2_select_screen_set.py`: 2,985 ligands, 3,436 jobs, 15 shards.
- `v2_run_screen.sh --dry-run`: GNINA command lines carried the exact validated
  box centres and sizes for both pockets.
- Synthetic-score rehearsal at production scale: `v2_collect_scores.py` (288
  poses on the small set; 3,436 synthetic rows on the full set),
  `v2_interactions.py` (ProLIF 2.2.1, 96 pairs, 0 failures),
  `v2_postdock_rank.py` (2,985 designs, 451 dual-pocket),
  `v2_cluster_and_seed.py` (400 designs; 259/326/381 clusters at
  0.55/0.65/0.75; 30 seeds across 30 clusters and 30 scaffolds).

**Results**
The pipeline runs end to end and the de novo ligand library is ready to screen.

**Failures or unresolved uncertainty**
- **No GNINA docking has been run.** Every score in the rehearsal is randomly
  generated and scientifically meaningless. The rehearsal proves plumbing only.
- `v2_similarity_search.py` has never contacted the live PubChem or ChEMBL
  endpoints; those calls are unverified.
- The reference benchmark has not been re-run on `h3`.
- Blocker: the authenticated gcloud account `cloud@hamiltonianlabs.co` cannot
  see project `project-08679972-d14a-4025-94f`. Both `moheetc4` and `h3` return
  `Required 'compute.instances.get' permission`. A `gcloud auth login` flow is
  open and waiting for a verification code.

**Effect on the overall project**
The campaign moves from "15,000 designs on disk" to "3,436 docking jobs queued
and every downstream analysis stage written and rehearsed". The only thing
between here and a ranked chemotype map is compute access.

**Next intended step**
Authenticate, SSH to `h3`, install pinned GNINA, re-pass the reference gate on
that machine, then run the 3,436-job de novo screen.
