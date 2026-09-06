# Sourceability method, sources, and honest coverage limits

**Lane:** AGENT 5 — vendor / sourceability infrastructure + reference control panel
**Date of retrieval:** 2026-09-06 (all network retrievals in this document were made on this date)
**Tool:** `YONSEI_FINAL10_V2/scripts/v2_sourceability.py`
**Cache:** `YONSEI_FINAL10_V2/11_SOURCEABLE/sourceability/cache/` (every HTTP response, keyed by exact request)

---

## 0. Why this document exists

In the previous session web access was blocked, so every `vendor`, `catalogue_ID`,
`stock_status` and `approximate_price` field in `FINAL_TOP20_DIVERSE_PAR2_CANDIDATES.csv`
is the literal string `PENDING`. This lane replaces guesswork with retrieved data
**and with retrieved negatives**. A negative here is a real result, not a gap: it means
the structure was searched for in named indexes on a named date and was not found.

The single most important thing a reader needs from this file is **which fields are
real**. Section 6 answers that field by field.

### Outputs in this directory

| File | Contents |
|---|---|
| `SOURCEABILITY_MASTER.csv` | 985 rows — one per molecule per vendor/registry hit. Every row carries `source_url`, `source_endpoint`, `retrieved_date`, `match_type`. |
| `SOURCEABILITY_SUMMARY.csv` | 36 rows — one per molecule, best classification + `classification_reason`. |
| `PAR2_REFERENCE_PANEL_FOR_WAN.csv` | 12 rows — the assay control panel, with mechanism, citations and the scientific cautions as columns. **Separate from the candidate quota by design.** |
| `SOURCEABILITY_PROVENANCE.json` | Endpoints hit, per-run counts, cache location, classification tallies, blocked-source list. |
| `SOURCEABILITY_METHOD.md` | This file. |
| `cache/` | Every HTTP response, keyed by exact request — reruns are free and auditable. |
| `REFERENCE_PANEL_SEED.csv` | Verified structures fed to the resolver for the control panel. |
| `build_reference_panel.py`, `merge_outputs.py` | Panel assembly and run consolidation. |
| `YONSEI_FINAL10_V2/scripts/v2_sourceability.py` | The reusable resolver. |

Across all 985 master rows: **935 `EXACT` matches, 50 `CONNECTIVITY_ONLY`**;
**81 distinct named vendors** and **670 distinct catalogue identifiers** retrieved; every
row carries a `source_endpoint`, a `source_url` and a `retrieved_date` (100% complete,
all 2026-09-06); `price`, `quantity`, `purity` and `lead_time` are `UNKNOWN` in 100% of
rows (see Section 5.2). One resolver failure in the whole run, recorded (Section 5.6).

---

## 1. Matching rules (the part that decides whether an order is useful)

All matching is on **InChIKey**, never on name.

| Match class | Definition | Consequence |
|---|---|---|
| `EXACT` | Full 27-character InChIKey identical to the query, or to the query's neutralised parent | The same compound. Can support `IN_STOCK` / `MAKE_ON_DEMAND`. |
| `CONNECTIVITY_ONLY` | First 14 characters (skeleton block) identical, full key differs | **A DIFFERENT COMPOUND.** Same skeleton, different stereochemistry / isotope / protonation. Never allowed to produce `IN_STOCK`. |
| `NO_MATCH` | Neither | Discarded. |

**Why this is not pedantry.** Our candidates carry defined stereochemistry. Ordering a
connectivity-only match buys the wrong stereoisomer and wastes an assay slot — and the
purchase order will look perfectly correct while doing so. Every connectivity-only hit in
`SOURCEABILITY_MASTER.csv` is labelled in both `match_type` and `notes`.

**Protonation handling.** The `smiles_prepared` column in this project is *ligand-prep
output*: it is protonated (e.g. `[NH2+]`), so its InChIKey carries a `-O` / non-`-N` final
block that will never match a registry entry for the neutral parent. Every query is
therefore resolved **twice** — as supplied, and as the neutralised, largest-fragment
parent (RDKit `rdMolStandardize.Uncharger` + `LargestFragmentChooser`). Both keys are
recorded (`query_inchikey`, `neutral_inchikey`) and a hit on either counts as `EXACT`.
Without this step every protonated candidate would have falsely resolved to
`NOT_SOURCEABLE`.

---

## 2. Classification definitions

These are the definitions implemented in `classify_molecule()`; they are reproduced in
the tool's docstring.

- **`IN_STOCK`** — a named vendor lists a specific catalogue ID together with an
  affirmative in-stock/available status **that this tool actually retrieved**. In practice
  this means the exact structure was found in a vendor **in-stock catalogue snapshot**,
  whose vintage is recorded verbatim in `catalogue_snapshot`. Only awarded on an `EXACT`
  match.
- **`MAKE_ON_DEMAND`** — exact-match member of a synthesise-on-demand chemical space
  (Enamine REAL, ZINC on-demand, Mcule Ultimate/Virtual) with a space identifier, no
  physical stock asserted.
- **`REGISTERED_NOT_VERIFIED`** — the structure exists in a registry (PubChem / ChEMBL /
  UniChem) and may carry supplier annotations, but no purchasable catalogue entry could be
  confirmed. **PubChem "Chemical Vendors" annotations land here by design** — a PubChem
  vendor annotation is a lead to verify, not stock confirmation. A confirmed vendor
  catalogue *listing* with no retrievable stock statement (e.g. a MolPort or Mcule
  catalogue ID) also lands here, with the catalogue ID recorded.
- **`NOT_SOURCEABLE`** — every configured resolver ran and returned no exact hit of any
  kind. `classification_reason` names the resolvers that were run, so the negative is
  auditable.

### An important honesty caveat on `IN_STOCK`

`IN_STOCK` here means *"present in a vendor in-stock catalogue snapshot"*, **not**
*"I queried the vendor's live inventory today"*. Every route that returns live stock and
price is credential-gated (Section 4). The snapshot vintage is always carried in
`catalogue_snapshot` and the wording of the evidence is in `stock_evidence`. The ZINC
in-stock aggregate is a **2019-Q4** snapshot — nearly seven years old. Treat `IN_STOCK` as
*"there is a real, specific, checkable vendor route"*, and have someone check it before
raising a purchase order.

---

## 3. Sources that worked (no credentials, public endpoints)

| Source | Endpoint | What it gave us |
|---|---|---|
| **PubChem PUG-REST** | `/rest/pug/compound/inchikey/{key}/cids/TXT` | Exact structure → CID. The structure-matching backbone. |
| **PubChem PUG-REST** | `/rest/pug/compound/fastidentity/smiles/{smi}/cids/TXT?identity_type=same_connectivity` | Connectivity-only siblings (the stereo trap detector). |
| **PubChem PUG-View** | `/rest/pug_view/categories/compound/{cid}/JSON` | The **"Chemical Vendors"** category: vendor `SourceName`, `RegistryID` (real catalogue numbers) and `SourceRecordURL` (direct product pages). Highest-yield vendor route we have. |
| **UniChem v1** | `POST https://www.ebi.ac.uk/unichem/api/v1/compounds` | InChIKey → cross-references. **Source 28 is MolPort** (5.83 M compounds) and returns genuine `Molport-xxx-xxx-xxx` catalogue IDs. Sources 2/14/34/46 (DrugBank / FDA-SRS / DrugCentral / ClinicalTrials) recorded as clinical-status evidence. |
| **ChEMBL** | `/chembl/api/data/molecule.json?molecule_structures__standard_inchi_key=` | Exact lookup; `max_phase` captured as approval evidence. |
| **Mcule** | `https://mcule.com/api/v1/search/lookup/?query={smiles}` and `/api/v1/compound/{id}/` | **Works anonymously.** Returns `MCULE-xxxxxxxxxx` IDs, product URLs and the compound's own InChIKey for exact verification. |
| **Arthor** (UCSF) | `https://arthor.docking.org/dt/{db}/search?query={smi}&type=Substructure` | The machine-readable route into vendor catalogues **including Enamine REAL**, without an Enamine account. Databases queried are listed below. |
| **RCSB PDB** | `/rest/v1/core/chemcomp/{id}` | Authoritative reference-ligand structures (8TZ = AZ8838, 8UN = AZ3451). |
| **Crossref / NCBI eutils** | `api.crossref.org/works/{doi}`, `esummary.fcgi` | Independent verification of the reference-panel citations. |

### Arthor catalogue databases queried

Arthor has no `Exact` search type (valid types: `Similarity`, `Substructure`, `Smarts`,
`Formula`, `None`). We therefore run a **Substructure** search with the whole molecule as
the query — the molecule is necessarily a substructure of itself, so an exact match is
always among the hits — and then **re-match every returned SMILES locally on InChIKey**.
This is what lets us separate `EXACT` from `CONNECTIVITY_ONLY`: Arthor's SMARTS
translation deliberately relaxes stereochemistry (`[CD>2Z6;@,@@]`), so the server-side
hit set is stereo-blind and the stereo decision is made by RDKit on our side.

| Database | Vendor / meaning | Kind | Snapshot |
|---|---|---|---|
| `MMcule-In-Stock-25Q3-6.5M` | Mcule in-stock | in_stock | 2025-Q3 |
| `ChemSpace-SC-Stock-Mar2022-346K` | Chemspace screening stock | in_stock | 2022-03 |
| `In-Stock-19Q4-14.1M` | ZINC in-stock aggregate (multi-vendor) | in_stock | **2019-Q4 (stale)** |
| `REAL-Database-22Q1` | **Enamine REAL** | on_demand | 2022-Q1 |
| `ZINC-On-Demand-19Q4-311M` | ZINC on-demand aggregate | on_demand | 2019-Q4 |
| `Mcule-Ultimate-25Q3-111M` | Mcule Ultimate (virtual) | on_demand | 2025-Q3 |
| `ZINC20-ForSale-22Q1` | ZINC20 for-sale aggregate | for_sale | 2022-Q1 |
| `DB-world-approved-2506-2.6K` | DrugBank world-approved | approved_drug | 2025-06 |
| `DB-US-approved-2506-1.9K` | DrugBank US-approved | approved_drug | 2025-06 |

---

## 4. Sources investigated and BLOCKED

These are recorded, not silently dropped. Each was probed on 2026-09-06.

| Source | What happened | Consequence |
|---|---|---|
| **MolPort API** | `POST api.molport.com/api/chemical-search/search` returns HTTP 200 with body `{"Result":{"Status":2,"Message":"Username or password is incorrect!"}}` | Live stock, price and lead time from MolPort are unavailable. MolPort **catalogue IDs** are still obtained, via UniChem source 28. |
| **Mcule prices / availability** | `/api/v1/compound/{id}/prices/` and `/availability/` return HTTP 401 `{"detail":"Authentication credentials were not provided."}` | Mcule catalogue IDs obtained; **no price, no stock, no lead time**. |
| **Mcule rate limiting** | The anonymous `search/lookup/` endpoint starts returning HTTP **429** under sustained use, and by the end of this session was returning 429 to *every* request including trivial ones — i.e. a sustained quota, not a per-request throttle. | Handled: 429 is retried with `Retry-After` honoured, the per-host interval was raised to 1.5 s, 429 is **never cached**, and a **circuit breaker** opens after 5 consecutive throttling responses so a large input list degrades into an explicitly-recorded coverage gap (`hosts_rate_limited_circuit_open` in the provenance JSON, `resolvers_failed = mcule:429` per molecule) instead of hours of retry backoff. Mcule catalogue IDs obtained before the limit hit are in the data and are real. |
| **Enamine REAL API** | `real.enamine.net` requires an Enamine REAL Explorer account and an `X-API-KEY` header. The REAL bulk download is ~13.6 billion molecules — not tractable here. | REAL membership established instead via the Arthor `REAL-Database-22Q1` index. Note this is a **2022-Q1** REAL snapshot; current REAL is far larger (SmallWorld indexes a 2025-Q3 REAL at ~10.1 B), so **REAL non-membership in our data is a weak negative**. |
| **Chemspace API** | `api.chem-space.com` requires an API key. | Chemspace reached only via the Arthor `ChemSpace-SC-Stock-Mar2022-346K` index. |
| **ZINC web UI** | `zinc20.docking.org` / `zinc15.docking.org` redirect to `/captcha`. **Not bypassed** — bypassing bot-detection is out of bounds. | ZINC content reached instead through Arthor and SmallWorld, which are not captcha-gated. |
| **eMolecules** | No public unauthenticated search API located; `www.emolecules.com/api/v1/search` 404s. | Not queried. |
| **MedChemExpress** | `medchemexpress.com` returns HTTP 403 to programmatic access (both `WebFetch` and a browser-UA `curl`). | The reported MCE catalogue number for P2L-003 could **not** be verified and is recorded as `NOT_VERIFIED`. |

**No account was created, no credential was entered, no terms or consent banner was
accepted, no form was submitted and nothing was purchased.** Only public catalogue
information was gathered.

---

## 5. Known limitations of this exercise — read this before trusting a number

1. **No live stock check was performed for any compound.** Every stock signal is a
   catalogue-snapshot membership test. The freshest in-stock index used is 2025-Q3; the
   largest (ZINC in-stock) is 2019-Q4.
2. **No price, quantity, purity or lead time was retrieved for any compound, anywhere.**
   Every route carrying those fields is credential-gated. These four columns are
   `UNKNOWN` throughout, by design. They are not zero and they are not estimated.
3. **`NOT_SOURCEABLE` is scoped to the indexes queried.** It means "absent from PubChem,
   ChEMBL, UniChem, Mcule and the nine Arthor catalogues on 2026-09-06". It does **not**
   mean "no chemist can make this". For de-novo generated structures the honest reading is
   *"not purchasable off a shelf; would require custom synthesis"*.
4. **The Enamine REAL snapshot is 2022-Q1.** A de-novo molecule reported as not in REAL
   might well be in the current 2025-Q3 REAL space. This is the single largest
   false-negative risk in the whole table. Re-running against a current REAL index (or an
   Enamine REAL Explorer account) is the highest-value follow-up.
5. **PubChem vendor annotations are leads, not stock.** 56 vendor annotations on one
   compound does not mean 56 vendors have it on a shelf today.
6. **One persistent upstream failure.** PubChem's `fastidentity` same-connectivity search
   returns HTTP 500 for `RX01677` (a chloro-enyne oxocine) on repeated attempts. That
   compound's *exact* match still resolved normally (CID 163188876); only its
   connectivity-sibling enumeration is missing. Recorded in `resolvers_failed`.
7. **Peptides are a different market.** The peptide agonist controls resolve through the
   same registries, but peptides are routinely made to order by custom-synthesis houses
   that do not appear in small-molecule catalogue indexes at all. A `REGISTERED_NOT_VERIFIED`
   result for a peptide substantially **understates** how easy it is to obtain — any
   custom peptide supplier will synthesise a hexapeptide amide to order. This asymmetry is
   flagged in the reference panel rather than corrected, because we could not retrieve a
   specific quote.
8. **Salt and formulation forms are not resolved.** A vendor may stock the TFA salt or the
   hydrochloride rather than the free base recorded here.
9. **A caching bug was found and fixed mid-run — disclosed because it affected real
   results.** The cache originally treated any status below 500 as a definitive answer.
   Mcule returns HTTP **429** when rate-limited, and 429 < 500, so **seven rate-limit
   responses were cached as if they were genuine "not found" results**. That silently
   converted a throttling blip into a permanent negative for those lookups. The fix:
   408/425/429 are now retried with `Retry-After` honoured and are never cached, and the
   Mcule per-host interval was raised to 1.5 s. The affected cache entries were purged and
   **both sets were fully re-run**; the classifications did not change, but they are now
   backed by real responses rather than cached throttling. The general lesson is baked
   into the tool: *only a definitive answer may be cached*.
10. **Mcule's anonymous quota is exhausted for this session.** By the end of the run
    `mcule.com` was returning HTTP 429 to every request. The Mcule catalogue IDs already in
    the data were retrieved before that and are real; but **any future run — including the
    Agent 2 analogue set — should expect Mcule coverage to be partial or absent** until the
    quota resets. Those gaps appear as `resolvers_failed = mcule:429` per molecule and as
    `hosts_rate_limited_circuit_open` in the provenance JSON. They are recorded, not
    hidden. Mcule is a secondary source here — PubChem vendor annotations, UniChem/MolPort
    and Arthor are unaffected — so this degrades coverage rather than invalidating it.
    **The data shipped here is not affected**: both the candidate set and the reference
    panel were resolved *before* the quota was exhausted, and both carry **zero
    Mcule-related resolver failures** (78 of 90 cached Mcule responses are HTTP 200; the
    remainder are legitimate 404 "not in Mcule" answers). A later reference-panel re-run
    was deliberately abandoned rather than allowed to overwrite that complete data with a
    rate-limited, partial version — re-running into a closed quota would have made the
    deliverable *worse*, not fresher.

---

## 6. Which fields are REAL — field-by-field verdict

| Field | Status |
|---|---|
| `inchikey`, `neutral_inchikey`, `skeleton14` | **REAL** — computed locally by RDKit from the supplied SMILES. |
| `match_type` (`EXACT` / `CONNECTIVITY_ONLY`) | **REAL** — computed locally by comparing full and 14-character InChIKeys. |
| `pubchem_cid_exact`, `chembl_id` | **REAL** — retrieved, endpoint recorded per row. |
| `vendor`, `catalogue_id` | **REAL where present** — every value came from a named endpoint recorded in `source_endpoint`, with a `source_url`. Never invented. |
| `source_url`, `source_endpoint`, `retrieved_date` | **REAL** — recorded for every single row. |
| `enamine_real_member` | **REAL but against a 2022-Q1 snapshot** — a `NO` is a weak negative. |
| `in_stock_catalogues`, `stock_status` | **REAL as snapshot membership**, NOT as live inventory. Always read with `catalogue_snapshot`. |
| `approved_drug_evidence` | **REAL and deliberately strict** — only ChEMBL `max_phase = 4`, DrugCentral (an approved-drugs-only resource), and membership of the DrugBank *approved* subsets count. A bare DrugBank ID or an FDA-SRS UNII does **not**, because DrugBank covers experimental/investigational compounds and a UNII is only a substance identifier; those go in `regulatory_registry_crossrefs` instead so they cannot be misread as regulatory status. |
| `clinical_phase_note` | **REAL** — plain-language reading of ChEMBL `max_phase`, so "3.0" cannot be mistaken for approval. |
| `regulatory_registry_crossrefs` | **REAL** — DrugBank / ClinicalTrials / FDA-SRS / Guide-to-Pharmacology cross-references. Presence, **not** approval. |
| `price`, `quantity`, `purity`, `lead_time` | **UNKNOWN everywhere. Nothing was retrieved. Nothing was estimated.** |
| Reference-panel mechanism / potency / citation columns | **Retrieved from literature and spot-checked**; fields that could not be confirmed say `NOT_VERIFIED` and say why (see Section 7). |

---

## 7. Reference control panel — verification notes

`PAR2_REFERENCE_PANEL_FOR_WAN.csv`. **These are assay controls. They must NOT be used to
fill the final TOP20 candidate quota and are kept in a separate file for that reason.**

Structures were taken from the PDB chemical component dictionary where a co-crystal exists
(AZ8838 = ligand `8TZ` in 5NDD; AZ3451 = ligand `8UN` in 5NDZ — the very structures this
project docks against), otherwise from PubChem with the identity confirmed against the
compound's synonym list.

**Structure-integrity check:** all 11 seed SMILES in `REFERENCE_PANEL_SEED.csv` were
round-tripped through RDKit and their recomputed InChIKeys compared to the recorded ones —
**11/11 match, 0 mismatches**, and the AZ8838 key reproduces the PDB `8TZ` descriptor
exactly. So no transcription error was introduced between the API responses and the panel.

Four findings that change how the panel should be used:

1. **GB88 is a biased ligand, encoded as `biased_agonist_flag = YES` and
   `role_in_panel = COUNTER_CONTROL_BIASED_AGONIST`.** It antagonises the Gq/11–Ca²⁺–PKC
   arm while *acting as an agonist* on cAMP/Gi-o, ERK1/2 and RhoA (Suen et al., Br J
   Pharmacol 2014;171:4112–24, PMID 24821440). Do not use it as a clean antagonist
   positive control.
2. **GB88 has an unresolved public-record stereochemistry conflict.** Two different
   stereoisomers are both publicly labelled "GB88", sharing skeleton hash
   `DCUDDCGUKZLQLN`: the (2S,3R) *allo*-Ile form (`-ZEZZXZOMSA-N`, PubChem CID 73755230,
   GtoPdb GTPL6658) and the (2S,3S) L-Ile form (`-MCOVPRHSSA-N`, PubChem CID 57330164,
   ChEMBL2431617, CAS 1416435-96-5). Verified in this session by resolving both CIDs.
   **Both are included in the panel as separate rows** so the choice is made deliberately
   rather than by accident. The published name uses plain "Ile" (= L-Ile = 2S,3S), which
   favours the CAS-bearing record.
3. **RWJ-50353 is not a PAR2 ligand at all**, encoded as `par2_ligand_flag = NO`,
   `selectivity_flag = SELECTIVE_THROMBIN_INHIBITOR_NOT_A_PAR2_LIGAND`,
   `historical_control_flag = YES`. It is a D-Phe-Pro-Arg benzothiazolyl-ketone
   active-site serine-protease inhibitor. **Correction to this project's working
   assumption:** the brief described it as a *broad* serine protease inhibitor; the
   primary paper (Giardino et al., Thromb Res 2000;98:83–93, PMID 10706936) reports it as
   a *selective thrombin* inhibitor — Kᵢ 0.19 nM, 16-fold over trypsin, ≥330-fold over
   other serine proteases. The core caution is unchanged and in fact sharper: it works
   upstream, by removing the protease stimulus, not by blocking the receptor.
4. **The "~80% melanin-uptake reduction" figure attributed to RWJ-50353 is
   `NOT_VERIFIED`.** It could not be located in any accessible abstract, full text or
   citing review. The pigmentation papers (Seiberg et al., J Invest Dermatol
   2000;115:162–167, PMID 10951231; Seiberg et al., Exp Cell Res 2000;254:25–32, PMID
   10623462; Sharlow et al., J Cell Sci 2000;113:3093–3101) state only "dose-dependent"
   and "visible" lightening. **Do not cite ~80% without opening those figures directly.**

### The GB88 stereochemistry conflict is resolved *by the market*

Running both stereoisomers through the resolver separately settles the practical question
even though it does not settle the literature question:

| Form | InChIKey | PubChem vendor leads | Catalogue IDs | In-stock catalogue membership | Class |
|---|---|---|---|---|---|
| **(2S,3S)** L-Ile | `DCUDDCGUKZLQLN-MCOVPRHSSA-N` | **30** | MolPort `Molport-046-925-938`; Mcule `MCULE-3630518373`, `MCULE-6246414487`; Chemspace `CSSS00161188992` | Mcule in-stock **2025-Q3**; Chemspace stock 2022-03; ZINC in-stock 2019-Q4 | **IN_STOCK** |
| (2S,3R) *allo*-Ile | `DCUDDCGUKZLQLN-ZEZZXZOMSA-N` | 1 (Glixx Labs only) | none | none | REGISTERED_NOT_VERIFIED |

**The compound the chemical supply chain actually sells as "GB88" is the (2S,3S) L-Ile
form**, which is also what the published chemical name implies. Order that one. The GtoPdb
(2S,3R) assignment is retained in the panel as a separate row so the discrepancy stays
visible, but it is not the orderable material.

Two further notes:

- **AZ8838 stereochemistry.** PDB ligand `8TZ` is the **(S)** enantiomer
  (`IDFPQEHZYBXIFO-LBPRGKRZSA-N` = PubChem CID 126961334 = ChEMBL4127372). PubChem CID
  132117112 is the *flat* record (`IDFPQEHZYBXIFO-UHFFFAOYSA-N`, no stereo layer) yet
  carries a depositor synonym asserting "(R)-", contradicting the deposited crystal
  structure. Verified in this session by resolving both CIDs. Order the (S) enantiomer.
- **P2L-003 is real, recent, and from the host laboratory.** Park J, Lim H, Lee Y, Kim T,
  Song H, Lee S, Heo Y, Kim J, **Namkung W**, Han G. *Bioorg Chem* 2025;167:109285, PMID
  41308341, DOI 10.1016/j.bioorg.2025.109285. Verified independently in this session via
  the Crossref API and NCBI eutils — both return the same title, journal, volume and
  author list, and **Wan Namkung is a co-author**. It has **no PubChem CID and no ChEMBL
  ID**, so no structure-based vendor search could be run; its structure must come from the
  paper's supporting information or from the authors. A MedChemExpress catalogue number
  and a CAS number were reported by secondary web research but MedChemExpress returns HTTP
  403 to programmatic access, so **neither was verified** and both are recorded as
  `NOT_VERIFIED`. The cheapest route to this compound is almost certainly to ask the host
  lab directly.

---

## 8. Results

### 8.1 FINAL_TOP20 + IDEAL_DE_NOVO_TOP5 (25 molecules)

| Class | n | Which |
|---|---|---|
| `IN_STOCK` | **1** | `RX02731` (resatorvid / TAK-242) |
| `REGISTERED_NOT_VERIFIED` | **2** | `RX02990`, `RX01677` — in registries, **no vendor route found anywhere** |
| `NOT_SOURCEABLE` | **22** | `RX05505`, `RX00387`, and all 15 de-novo TOP20 entries + all 5 IDEAL_DE_NOVO_TOP5 |
| `MAKE_ON_DEMAND` | **0** | no molecule matched Enamine REAL (2022-Q1 snapshot) or any on-demand space |

Match-type tally across the 90 master rows for this set: **82 `EXACT`, 8 `CONNECTIVITY_ONLY`**.
Only **3 of 25** molecules produced any exact registry hit at all.

**The one genuinely orderable candidate — `RX02731` / resatorvid (TAK-242), CAS
243984-11-4:** PubChem CID 11703255, ChEMBL225157, 56 PubChem chemical-vendor annotations
with real catalogue numbers and direct product pages, MolPort `Molport-035-773-739`, Mcule
`MCULE-7427418182` and `MCULE-8159223642`, exact member of the ZINC in-stock aggregate
(`ZINC000013982410`, 2019-Q4) and ZINC20 for-sale (2022-Q1). One vendor product page was
additionally fetched directly to confirm the lead is live: LGC Standards
`https://www.lgcstandards.com/GB/en/p/TRC-R144570` returns HTTP 200 with the page title
*"Resatorvid | CAS 243984-11-4 | LGC Standards"*. Its stock indicator is rendered
client-side, so an affirmative stock statement could **not** be captured — the compound is
clearly catalogued and offered by many suppliers, but no live inventory check was made.

*Caveat on resatorvid's project label — please fix this upstream:* it is tagged
`source_lane = APPROVED_REPURPOSING` and `human_exposure = FDA_LIBRARY_LABEL` in
`REAL_COMPOUND_PROVENANCE.csv`. **Resatorvid is not an approved drug.** Retrieved directly
from ChEMBL: `CHEMBL225157`, `max_phase = 3`, `first_approval = null` — i.e. it reached
Phase 3 and stopped. Its `approved_drug_evidence` is `NONE_FOUND`; what it does have is
`regulatory_registry_crossrefs = DrugBank:DB05943; FDA-SRS:H2MZ648C31;
ClinicalTrials:NCT00143611, NCT00633477, NCT04620148` — registry presence and trial
history, not approval. (Contrast propranolol in the reference panel, which returns
`approved_drug_evidence = ChEMBL max_phase=4; DrugBank US-approved set; DrugBank
world-approved set; DrugCentral:2303` — that is what real approval evidence looks like
here.) Resatorvid being cheap and easy to buy is the genuinely useful fact; "approved" is
not, and the human-exposure claim attached to it should be downgraded accordingly.

`RX02990` (PubChem CID 5321290, CHEMBL1944654) and `RX01677` (PubChem CID 163188876) are
real registered compounds with **no vendor route at all**. This was double-checked by
fetching their PubChem source-category listings directly: neither CID has a "Chemical
Vendors" category, so the negative is genuine and not a parsing artefact.

### 8.2 Reference control panel (12 rows)

| Class | n | Which |
|---|---|---|
| `IN_STOCK` | **7** | AZ8838, AZ3451, GB88 (2S,3S), I-287, propranolol, SLIGKV-NH₂, SLIGRL-NH₂ |
| `REGISTERED_NOT_VERIFIED` | **5** | GB88 (2S,3R), C391, RWJ-50353, 2-furoyl-LIGRLO-NH₂, P2L-003 |

Catalogue identifiers actually retrieved (all `EXACT` matches; the Mcule 2025-Q3 in-stock
snapshot is the freshest stock signal available to this pipeline):

| Compound | MolPort | Mcule (2025-Q3 in-stock unless noted) | Other | PubChem vendor leads |
|---|---|---|---|---|
| AZ8838 | `Molport-051-516-363` | `MCULE-4401006455`, `MCULE-3230952760` | ZINC in-stock `ZINC000914431265` | 22 |
| AZ3451 | `Molport-046-683-290` | `MCULE-6778184595`, `MCULE-3081646873` | Chemspace `CSSS00134616029`; ZINC in-stock `ZINC000914431341` | 48 |
| GB88 (2S,3S) | `Molport-046-925-938` | `MCULE-3630518373`, `MCULE-6246414487` | Chemspace `CSSS00161188992`; ZINC in-stock | 30 |
| I-287 | `Molport-051-906-774` | `MCULE-9742074451` | — | 12 |
| SLIGKV-NH₂ | `Molport-023-276-631` | `MCULE-6308066722`, `MCULE-6067917481` | Chemspace `CSSS00132303451`; ZINC in-stock | 40 |
| 2-furoyl-LIGRLO-NH₂ | `Molport-023-276-635` | `MCULE-2721031012`, `MCULE-4017210905` (listed, **not** in-stock) | — | 35 |
| GB88 (2S,3R) | — | — | — | 1 |
| C391 | — | — | — | **0** |
| RWJ-50353 | — | — | — | **0** |

**Both AZ compounds — the actual co-crystal ligands of the two receptor models this project
docks against — are readily orderable**, with 2025-Q3 in-stock catalogue membership. That
matters: the panel can be anchored on the reference antagonist the whole ranking was built
around.

**`2-furoyl-LIGRLO-NH₂` is better than its label suggests.** It has a MolPort catalogue ID,
two Mcule IDs and 35 PubChem vendor leads — it is definitely *listed* — but no in-stock
catalogue membership was retrieved, so under the stated definitions it is
`REGISTERED_NOT_VERIFIED` rather than `IN_STOCK`. Combined with the peptide caveat in
Section 5.7 (any custom-synthesis house will make a hexapeptide amide to order), treat this
as "obtainable, confirm lead time" rather than "hard to get".

**`C391` and `RWJ-50353` are the genuinely hard ones**: zero vendor annotations, zero
catalogue IDs, zero in-stock membership across every index queried. C391 is a research
peptidomimetic and RWJ-50353 is a discontinued 2000-era J&J compound; both would likely need
custom synthesis or an author request. Budget time for them, or drop them.

---

## 9. Findings that affect other lanes

These fell out of the structure-matching work and are reported because they change how the
final panel should be read. They are **not** sourceability results — they are data-integrity
results.

1. **All five "real compound" rows in FINAL_TOP20 are tagged `source = DENOVO`,
   `library = DE_NOVO_BRICS`, `triage_class = DE_NOVO` in the upstream consensus table**
   (`11_SOURCEABLE/analogues/REAL_COMPOUNDS_WITH_SEED_SIMILARITY.csv`). The
   `source_lane` labels in FINAL_TOP20 (`NATURAL_PRODUCT_OR_V1_HIT`,
   `REAL_ANALOGUE_PUBCHEM`, `APPROVED_REPURPOSING`) are therefore assigned labels, not
   independent evidence that the molecule is a real, purchasable compound. Three of the
   five do turn out to have exact registry identity; two do not. **The structure-level
   test below is the one to trust, not the lane label.**

2. **`RX05505` — the number-one ranked candidate — does not correspond to its recorded
   source structure.** Its recorded `source_id` is InChIKey
   `WHMZADUPVDOIRR-YDHLFZDLSA-N`; the prepared structure's key is
   `WHMZADUPVDOIRR-YOYPFHDYSA-O` (neutral parent `-YOYPFHDYSA-N`). Same skeleton block,
   **different stereochemistry descriptor**. PubChem returns no compound at all for the
   prepared key. The ligand-prep step also converted an imidic-acid input
   (`.../C(O)=N/...`) into an amide. Net effect: what was docked and ranked is not what the
   provenance record points at.

3. **`RX00387` does not correspond to its recorded source CID.** Recorded source is PubChem
   `CID162821083`; that CID's InChIKey is `BLNOILRPTLHYRM-...`, while the prepared
   structure is `BAVQXBXBCIDJKT-GOSISDBHSA-N`. Same molecular formula (C18H18O6) but a
   **different InChIKey skeleton block**, i.e. different constitution — the ring
   carbonyl/hydroxyl positions differ (2-pyranone vs 4-pyranone). Verified locally with
   RDKit and against PubChem's own record for that CID.

4. **The two compounds in (2) and (3) are exactly the two that resolved to
   `NOT_SOURCEABLE` with connectivity-only hits.** The sourceability resolver detected the
   provenance problem independently, from structure alone, without being told to look for
   it. That is a useful validation of the connectivity-vs-exact matching rule.

---

## 10. Reproducing / extending

```bash
# resolve any structure list
.venv-v2/bin/python YONSEI_FINAL10_V2/scripts/v2_sourceability.py \
    --input  <candidates.csv> \
    --id-col cand_id --smiles-col smiles_prepared --inchikey-col inchikey \
    --outdir YONSEI_FINAL10_V2/11_SOURCEABLE/sourceability \
    --cache-dir YONSEI_FINAL10_V2/11_SOURCEABLE/sourceability/cache \
    --tag <TAG>

# then consolidate every tagged run into the canonical filenames
.venv-v2/bin/python YONSEI_FINAL10_V2/11_SOURCEABLE/sourceability/merge_outputs.py
```

The cache is keyed by the exact request, so re-running on an overlapping list costs
nothing for molecules already seen. Transport failures, 5xx responses **and throttling
responses (408/425/429)** are deliberately **not** cached, so a rerun retries them rather
than inheriting a transient blip as a permanent negative. `--refresh` forces a full
re-fetch.

### The Agent 2 analogue set

`11_SOURCEABLE/analogues/SOURCEABLE_ANALOGUES_DEDUP.csv` (**1043 analogues**) arrived at
17:47 on 2026-09-06 and is being resolved by this lane. Because a single 1043-molecule pass
would take several hours and the tool only writes its CSVs at the end of a run, the input is
**split into seven chunks of ~150** (`chunks/analogues_chunk01..07.csv`) and driven by
`run_analogues.sh`, so partial results always survive on disk and the job is resumable — the
driver skips any chunk whose summary already exists.

```bash
OUT=YONSEI_FINAL10_V2/11_SOURCEABLE/sourceability
sh $OUT/run_analogues.sh          # resumable; skips completed chunks
.venv-v2/bin/python $OUT/merge_outputs.py    # folds all chunks into the canonical files
```

Column mapping: Agent 2 uses `analogue_id` / `canonical_smiles` / `inchikey`, passed via
`--id-col analogue_id --smiles-col canonical_smiles`. `merge_outputs.py` maps every
`ANALOGUES**` chunk tag to the single panel label `AGENT2_SOURCEABLE_ANALOGUES`.

Two expectations to set. First, **this is complementary to Agent 2's own retrieval, not a
duplicate of it**: their `source_databases` column shows the analogues came from ChEMBL and
PubChem *registry* searches and their `catalogues` column is largely empty — this lane adds
the vendor/catalogue layer on top. Second, **Mcule coverage will be partial or absent**
because its anonymous quota was exhausted earlier in the session (Section 5.10); the circuit
breaker records those gaps explicitly per molecule rather than hiding them, and the other
four resolvers are unaffected.

### Options that matter for large lists

The nine Arthor catalogue queries are the throughput bottleneck. They are issued
concurrently (3 simultaneous connections — measured as the most `arthor.docking.org`
serves reliably; it drops connections at 5), which is roughly a 10× speed-up over serial.
For very large inputs the catalogue set can also be narrowed:

```bash
# see what is configured
.venv-v2/bin/python YONSEI_FINAL10_V2/scripts/v2_sourceability.py --list-arthor-dbs --input x --outdir x

# fast mode: the three catalogues that carry most of the decision weight
--arthor-dbs In-Stock-19Q4-14.1M,REAL-Database-22Q1,MMcule-In-Stock-25Q3-6.5M
```

Whatever subset is used is written into `SOURCEABILITY_PROVENANCE.json`
(`arthor_databases_queried`), so a narrowed run can never be mistaken for full coverage.
Other useful flags: `--skip pubchem,unichem,chembl,mcule,arthor` to disable resolvers,
`--min-interval` for global politeness, `--limit N` for a debug subset.
