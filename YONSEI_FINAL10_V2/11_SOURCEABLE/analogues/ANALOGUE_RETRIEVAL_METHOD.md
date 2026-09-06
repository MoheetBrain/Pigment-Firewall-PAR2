# Retrieval of real / sourceable neighbours of the frozen PAR2 de novo seeds

Agent 2 lane. Run 2026-09-06. Branch `yonsei-final10-v2`.

**Status while docking is still running: RETRIEVAL SECTIONS ARE FINAL, docking
sections are marked `PENDING` until the runs complete.**

Nothing in this document is evidence that any molecule binds PAR2 or antagonises
it. Similarity is retrieval. Docking is a geometric hypothesis. Neither is an
assay.

---

## 1. Input

`YONSEI_FINAL10_V2/11_SOURCEABLE/seeds/FINAL_DE_NOVO_SIMILARITY_SEEDS.csv`,
used frozen and unmodified: 32 seeds, 26 routed to the 5NDD orthosteric pocket
and 6 to the 5NDZ allosteric pocket. Two molecules appear twice because they
were docked into both pockets (DN00100 as SEED026/SEED031, DL11368 as
SEED025/SEED032), so the 32 seeds carry **30 unique query structures** and one
network query was issued per unique structure.

**Query structure rule.** `stereo_smiles_input` was used when it was present and
non-empty, otherwise `smiles_prepared`. Seven seeds carry a
`stereo_smiles_input`; for six of them it is character-identical to
`smiles_prepared`, and only **SEED004 (DN00464)** actually differs. Every output
row records which field was used in `query_smiles_field`.

The seeds were not re-ranked, re-selected or filtered.

---

## 2. Sources actually queried

| Source | Endpoint | Query types | Result |
|---|---|---|---|
| PubChem | `pug/compound/fastsimilarity_2d` (GET and POST) | Tanimoto thresholds 90, 80, 70 (GET) and 80, 65 (POST) | worked |
| PubChem | `pug/compound/fastsubstructure` (GET and POST) | Bemis-Murcko scaffold; largest ring system | worked |
| PubChem | `pug/compound/cid/.../property/...` | structure retrieval in batches of 150 | worked |
| PubChem | `pug_view/categories/compound/<CID>` | "Chemical Vendors" section | worked |
| ChEMBL | `chembl/api/data/similarity/{smi}/{pct}` | thresholds 70 and 55, paged | worked |
| SmallWorld (sw.docking.org) | `search/submit`, `search/view`, `search/export` | graph edit distance over 7 vendor catalogues | worked, with a hard limit (§6) |

SmallWorld catalogues searched, and why each was chosen:

| Map key | Size | What it is |
|---|---|---|
| `Enamine-SC-Stock-Mar2022.smi.anon` | 346,634 | Enamine screening collection, in stock — the brief's PRIMARY space |
| `in-stock-25Q2.smi.anon` | 11,302,744 | ZINC in-stock, vendor-indexed |
| `Mcule_In_Stock_25Q3.smi.anon` | 6,554,871 | Mcule in stock |
| `ChemspaceBB_202408.smi.anon` | 478,411 | Chemspace building blocks |
| `interesting.smi.anon` | 320,845 | ZINC "interesting" (annotated / bioactive) |
| `REALDB-2025-07.smi.anon` | 10,102,659,506 | Enamine REAL, make-on-demand — the brief's SECONDARY space |
| `wait-ok-25Q2.smi.anon` | 877,967,502 | ZINC orderable with lead time |

Hit identifiers come back in each catalogue's own namespace and are recorded
verbatim: Enamine REAL reaction-space ids (`s_22__12857784__18233754`), Mcule
ids (`MCULE-9857935169`), ZINC numeric ids, and Chemspace ids (`CSSS…`, `CSCS…`)
in the Enamine-SC and Chemspace maps.

### Sources attempted and blocked — recorded, not worked around

* **MolPort API** (`api.molport.com/api/chemical-search/search`) — reachable,
  HTTP 200, but the body is
  `{"Status":2,"Message":"Username or password is incorrect!"}`. The API needs
  credentials this session does not hold. **No MolPort query was completed.**
* **Enamine store API** (`new.enaminestore.com/api/v1/catalog`) — HTTP 302,
  no anonymous programmatic access. Enamine chemistry was reached instead
  through the SmallWorld Enamine-SC-Stock and REAL maps and through PubChem's
  Enamine vendor records.
* **mcule.com** — HTTP 403 to a bare request even with a browser User-Agent.
  Reached through the SmallWorld Mcule-In-Stock map instead.
* **eMolecules / Chemspace REST** — both require an API key. Not queried.
* **PubChem `fastsimilarity_3d`** — returns `PUGREST.NotFound` for a SMILES
  input; the endpoint needs a CID with a precomputed conformer. Axis not used.
* **No bulk catalogue SDF/SMILES file was downloadable** without registration,
  so the planned "download and fingerprint locally on h3" route was not
  available. SmallWorld was used as the substitute, since it indexes exactly
  those catalogues server-side.

---

## 3. The PubChem field-name trap, and a new one

Defect 9 in `HANDOFF_2026-09-05.md` records that PubChem renamed
`CanonicalSMILES` to `ConnectivitySMILES` and that an earlier run silently
discarded every hit. Field names were therefore re-verified live before any
bulk query on 2026-09-06:

* `SMILES` — present, and it is the **isomeric** SMILES.
* `ConnectivitySMILES` — present.
* `IsomericSMILES` — **silently dropped from the response**; requesting it
  yields no such key rather than an error.
* `CanonicalSMILES` — accepted, but the response comes back keyed
  `ConnectivitySMILES`.

Structures are therefore read `SMILES` first, `ConnectivitySMILES` second, and
the retrieval asserts a non-empty result rather than writing an empty file.

**A second, previously unrecorded PubChem defect was hit in this run.** The GET
form of `fastsimilarity_2d` puts the SMILES in the URL *path*, so a `/` in a
double-bond stereo specifier percent-encodes to `%2F` and the PubChem front end
answers **HTTP 500**. `SEED005` (`C/C=C(/C)C(=O)O[C@@H]1...`) lost all three of
its GET similarity queries to this and returned zero records. It is the only
seed in the set containing `/`. The repair was to re-query **every** seed over
POST with the SMILES in the request body, which succeeds; both passes are kept
and merged so coverage is uniform.

---

## 4. Similarity metrics

Every structure returned by every source was re-scored locally with RDKit
(2026.03.6) so the reported number is reproducible and independent of each
database's own fingerprint or distance.

| Metric | Definition |
|---|---|
| `ecfp4_tanimoto` | **PRIMARY.** Morgan radius 2, 2048 bits, Tanimoto |
| `fcfp4_tanimoto` | feature Morgan radius 2, 2048 bits (scaffold-hop sensitive) |
| `pharm2d_tanimoto` | RDKit Gobbi 2D pharmacophore fingerprint |
| `mcs_fraction` | `rdFMCS` MCS atoms / union heavy atoms, `ringMatchesRingOnly`, `completeRingsOnly`, 2 s timeout |
| `murcko_same` | identical achiral Bemis-Murcko scaffold |
| `murcko_tanimoto` | ECFP4 Tanimoto between the two Murcko scaffolds |
| `sw_graph_edit_distance` | SmallWorld topological edit distance, where a SmallWorld hit exists |

Bands are exactly the brief's: `T>=0.80`, `T0.70-0.80`, `T0.60-0.70`,
`T0.50-0.60`.

**USRCAT / 3D shape similarity was NOT run.** It needs a conformer per hit, and
the retrieved set is large enough that embedding all of it would have cost more
than the docking that follows — and the docking answers the same question
better, because it evaluates the shape *in the pocket* rather than in vacuum.
This is a real gap, recorded rather than papered over.

### Retention lanes

A hit is kept for docking in exactly one of three labelled lanes.

* **`close_analogue_2D`** — `ecfp4_tanimoto >= 0.50`.
* **`scaffold_hop`** — below 0.50, but with independent structural
  corroboration: identical Murcko scaffold, or `mcs_fraction >= 0.55`, or
  `pharm2d_tanimoto >= 0.80`, or `fcfp4_tanimoto >= 0.55`, or SmallWorld graph
  edit distance <= 5.
* **`best_available_neighbour`** — neither of the above, but among the top 40
  for that seed on a nan-safe composite of the four 2D metrics
  (weights 0.40 ECFP4 / 0.25 FCFP4 / 0.20 MCS / 0.15 pharm2D, renormalised over
  the metrics that exist for that pair, so an absent metric contributes nothing
  and is never imputed as 0). **These are not analogues and are never described
  as analogues.** They exist because for most of these seeds no real molecule
  above the band floor exists at all, and the only honest way to answer "can we
  buy something that keeps the binding solution?" is to dock the closest real
  chemistry there is and let the pocket decide.

Every row carries its lane, its actual similarity, and the specific evidence
string that admitted it.

### Physicochemical and alert handling

MW window 200–600 and the RDKit PAINS_A/B/C + BRENK + NIH filter catalogues are
applied as **soft** filters: every hit is scored, `structural_alerts` and
`physchem_in_envelope` are recorded on every row, and exclusions are written
into `excluded_reason` (`MW_outside_200_600`, `PAINS_alert`, or
`not_excluded`). Nothing is deleted silently.

### Deduplication

Global and **stereo-aware**: the full 27-character InChIKey. The connectivity
block (first 14 characters) is recorded separately as
`connectivity_collision_group`, with `connectivity_collision_group_size`, so
two "different" hits that are the same skeleton in different stereochemistry are
visible before an assay slot is spent on them. Per-seed the retained set is
capped at 100, lane-ordered (close analogues first).

---

## 5. Docking

PENDING — filled in when the runs complete.

---

## 6. Honest coverage limits

1. **SmallWorld cannot finish a search for most of these seeds.** Measured
   behaviour: for a flexible, largely aliphatic query the graph search exceeds
   its own node budget and returns `state=ERROR` with zero records at edit
   distance >= 3, while distance 2 completes cleanly (`state=DONE`) and honestly
   reports zero neighbours. The retrieval therefore walks distance 4 -> 3 -> 2
   and records the distance at which the search actually completed. For the
   rigid aromatic seeds it completes at distance 4 and returns real hits; for
   the polyketide/sugar-like seeds it does not complete above distance 2. That
   is a genuine limit of the tool on this chemistry, not a configuration error.
2. **Concurrency degrades the SmallWorld service.** Six concurrent searches
   drove it to HTTP 502 and connection refusal; the run was restarted at two
   concurrent searches. Two earlier partial runs were discarded and are kept on
   disk as `SMALLWORLD_RAW_RECORDS.aborted-run1.csv` / `-run2.csv` rather than
   deleted.
3. **No vendor stock, price, lead time or purity was checked.** Vendor names and
   catalogue identifiers recorded here arrived *with* the structure during
   retrieval. Commercial verification is Agent 5's resolver.
4. **PubChem vendor annotation is a presence signal, not a stock check.** A
   supplier record can be stale.
5. **USRCAT / 3D shape and pharmacophore-geometry similarity were not run** (§4).
6. **The retrieval floor.** Pairs below ECFP4 0.30 are counted but not written
   to `SOURCEABLE_ANALOGUES_RAW.csv`; the count is in
   `RETRIEVAL_SCORING_SUMMARY.json`. Writing every one of the several hundred
   thousand retrieved records against all 30 queries would have produced a file
   of no analytical value.
