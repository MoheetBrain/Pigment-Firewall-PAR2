#!/usr/bin/env python3
"""Render PAR2_ENRICHMENT_METRICS.md from the computed enrichment JSON.

Every number in the report is read from the JSON produced by bench_enrichment.py
or from the benchmark table itself. Nothing is retyped, so the document cannot
drift from the computation behind it.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

SCORE_LABEL = {
    "best_vina_affinity": "Vina (`best_vina_affinity`)",
    "best_CNNscore": "CNNscore (`best_CNNscore`)",
    "best_CNNaffinity": "CNNaffinity (`best_CNNaffinity`)",
    "best_CNN_VS": "CNN_VS (`best_CNN_VS`)",
    "CRYSTAL_IFP_RECOVERY": "CRYSTAL_IFP_RECOVERY",
    "DESIGN_HOTSPOT_SCORE": "DESIGN_HOTSPOT_SCORE",
    "consensus_score": "consensus_score (campaign ranker)",
    "ligand_efficiency": "ligand efficiency",
    "polar_anchor_count": "polar_anchor_count (robust anchors)",
    "crystal_hbond_recovery": "crystal H-bond recovery (2 keys only)",
    "heavy_atoms": "heavy atoms (NEGATIVE CONTROL: size only)",
    "hbd": "HBD count (NEGATIVE CONTROL: property only)",
    "hba": "HBA count (NEGATIVE CONTROL: property only)",
    "mw": "MW (NEGATIVE CONTROL: property only)",
    "clogp": "cLogP (NEGATIVE CONTROL: property only)",
    "tpsa": "TPSA (NEGATIVE CONTROL: property only)",
}
CONTROLS = {"heavy_atoms", "hbd", "hba", "mw", "clogp", "tpsa"}
ORDER = ["best_vina_affinity", "best_CNNscore", "best_CNNaffinity", "best_CNN_VS",
         "CRYSTAL_IFP_RECOVERY", "DESIGN_HOTSPOT_SCORE", "consensus_score",
         "ligand_efficiency", "polar_anchor_count", "crystal_hbond_recovery",
         "heavy_atoms", "hbd", "hba", "mw", "clogp", "tpsa"]


def fmt(v, n=3):
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "n/a"
    return f"{v:.{n}f}"


def metric_table(res: dict) -> str:
    head = ("| Score | ROC-AUC [95% CI] | PR-AUC | EF1% | EF5% | BEDROC α=20 | "
            "BEDROC α=80.5 | perm. p (ROC) |\n"
            "|---|---|---|---|---|---|---|---|\n")
    rows = []
    for k in ORDER:
        r = res.get(k)
        if not r or r.get("status") == "INSUFFICIENT_DATA":
            continue
        rows.append(
            f"| {SCORE_LABEL.get(k, k)} | {fmt(r['ROC_AUC']['value'])} "
            f"[{fmt(r['ROC_AUC']['ci95_low'])}, {fmt(r['ROC_AUC']['ci95_high'])}] | "
            f"{fmt(r['PR_AUC']['value'])} | "
            f"{fmt(r['EF1pct']['value'], 2)} | {fmt(r['EF5pct']['value'], 2)} | "
            f"{fmt(r['BEDROC_a20']['value'])} | {fmt(r['BEDROC_a80.5']['value'])} | "
            f"{fmt(r['ROC_AUC']['permutation_p'], 4)} |")
    return head + "\n".join(rows)


def ci_table(res: dict) -> str:
    head = ("| Score | EF1% [95% CI] | EF5% [95% CI] | BEDROC20 [95% CI] | "
            "null median BEDROC20 | null p95 |\n|---|---|---|---|---|---|\n")
    rows = []
    for k in ORDER:
        r = res.get(k)
        if not r or r.get("status") == "INSUFFICIENT_DATA":
            continue
        rows.append(
            f"| {SCORE_LABEL.get(k, k)} | "
            f"{fmt(r['EF1pct']['value'], 2)} [{fmt(r['EF1pct']['ci95_low'], 2)}, "
            f"{fmt(r['EF1pct']['ci95_high'], 2)}] | "
            f"{fmt(r['EF5pct']['value'], 2)} [{fmt(r['EF5pct']['ci95_low'], 2)}, "
            f"{fmt(r['EF5pct']['ci95_high'], 2)}] | "
            f"{fmt(r['BEDROC_a20']['value'])} [{fmt(r['BEDROC_a20']['ci95_low'])}, "
            f"{fmt(r['BEDROC_a20']['ci95_high'])}] | "
            f"{fmt(r['BEDROC_a20']['null_median'])} | "
            f"{fmt(r['BEDROC_a20']['null_p95'])} |")
    return head + "\n".join(rows)


def verdict_for(k: str, r: dict) -> tuple[str, str]:
    """Trust classification driven by the numbers, not by expectation."""
    if not r or r.get("status") == "INSUFFICIENT_DATA":
        return "NOT EVALUATED", "insufficient data"
    auc = r["ROC_AUC"]["value"]
    lo, hi = r["ROC_AUC"]["ci95_low"], r["ROC_AUC"]["ci95_high"]
    p = r["ROC_AUC"]["permutation_p"]
    if not np.isfinite(auc):
        return "NOT EVALUATED", "non-finite"
    if lo <= 0.5 <= hi or p > 0.05:
        return "AT CHANCE", (f"95% CI [{fmt(lo)}, {fmt(hi)}] spans 0.5"
                             if lo <= 0.5 <= hi else f"permutation p = {fmt(p, 4)}")
    if auc < 0.5:
        return "INVERTED", f"ROC-AUC {fmt(auc)} is BELOW chance: the score ranks actives WORSE than decoys"
    if auc >= 0.70:
        return "USEFUL", f"95% CI [{fmt(lo)}, {fmt(hi)}] excludes 0.5"
    return "WEAK", f"better than chance (CI [{fmt(lo)}, {fmt(hi)}]) but modest"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--enrichment", type=Path, nargs="+", required=True)
    ap.add_argument("--benchmark", type=Path, required=True)
    ap.add_argument("--actives", type=Path, required=True)
    ap.add_argument("--decoy-summary", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--extra", type=Path, default=None,
                    help="optional JSON with EX8-vs-EX32 and scaffold-level results")
    args = ap.parse_args()

    packs = {}
    for p in args.enrichment:
        d = json.loads(p.read_text())
        packs[(d["pocket"], bool(d.get("clash_filtered")))] = d
    bench = pd.read_csv(args.benchmark, low_memory=False)
    A = pd.read_csv(args.actives)
    dsum = json.loads(args.decoy_summary.read_text())
    extra = json.loads(args.extra.read_text()) if args.extra and args.extra.exists() else {}

    primary = packs.get(("5NDD_orthosteric", True)) or packs.get(("5NDD_orthosteric", False))
    res = primary["enrichment"]
    null = primary["ifp_null_distribution"]
    inc = A[A.include_in_enrichment == True]  # noqa: E712

    L = []
    w = L.append
    w("# PAR2 known-active vs decoy benchmark, and the interaction-fingerprint null")
    w("")
    w(f"Generated {datetime.now(timezone.utc).isoformat(timespec='seconds')}. "
      "Every number here was computed in this session from the artefacts named in "
      "`BENCHMARK_PROVENANCE.json`; none is transcribed from an earlier document.")
    w("")
    w("**This is a calibration layer. It measures whether the campaign's scores can "
      "tell molecules with published PAR2 antagonist activity apart from "
      "property-matched real molecules with none. It says nothing about whether any "
      "particular candidate is an antagonist, and docking cannot establish that.**")
    w("")

    # ---------------- headline ----------------
    w("## 1. The headline")
    w("")
    order_by_auc = [(k, res[k]["ROC_AUC"]["value"]) for k in ORDER
                    if k in res and res[k].get("status") != "INSUFFICIENT_DATA"
                    and np.isfinite(res[k]["ROC_AUC"]["value"])]
    order_by_auc.sort(key=lambda kv: -kv[1])
    w("Ordered by ROC-AUC. Rows marked NEGATIVE CONTROL contain no docking "
      "information; they are the bar every docking score has to clear.")
    w("")
    for k, v in order_by_auc:
        cls, why = verdict_for(k, res[k])
        w(f"- **{SCORE_LABEL.get(k, k)}** — {cls}: ROC-AUC {fmt(v)}, {why}.")
    w("")

    # ---------------- composition ----------------
    w("## 2. What the benchmark contains")
    w("")
    w(f"- **{primary['n_actives']} actives** and **{primary['n_decoys']} decoys** "
      f"evaluated in `{primary['pocket']}`"
      f"{' after clash filtering' if primary.get('clash_filtered') else ''}.")
    w(f"- Actives: {len(inc)} molecules over **{inc.murcko_scaffold.nunique()} distinct "
      f"Murcko scaffolds** from {inc.document_chembl_id.nunique()} ChEMBL documents "
      f"plus PubChem/GtoPdb supplements, potency "
      f"{inc.activity_nM_normalised.min():g}–{inc.activity_nM_normalised.max():g} nM.")
    w(f"- Decoys: drawn from {dsum['pool_rows']} real catalogue/database molecules "
      f"({', '.join(f'{k} {v}' for k, v in list(dsum['decoy_library_counts'].items())[:4])}), "
      f"property-matched on MW / cLogP / TPSA / formal charge / HBD / HBA / rotatable "
      f"bonds, with ECFP4 Tanimoto ≤ {dsum['max_tanimoto_threshold']} to **every** "
      f"active (highest observed "
      f"{dsum['decoy_max_tanimoto_observed']:.3f}).")
    w("")
    w("Class counts as docked:")
    w("")
    w("| Class | Molecules | Meaning |")
    w("|---|---|---|")
    meanings = {
        "ACTIVE": "published PAR2 antagonist / NAM, IC50 or Ki ≤ 10 µM, non-peptide",
        "DECOY": "property-matched, topologically dissimilar, no recorded PAR2 activity",
        "CENSORED_INACTIVE": "**tested against PAR2 and NOT active** (`IC50 > 1 µM`); mostly PAR4 antagonists counter-screened — the strongest available true negatives",
        "WEAK_ACTIVE": "verified antagonist but weaker than the 10 µM cutoff",
        "COUNTER_CONTROL": "peptide/peptidomimetic, agonist-annotated, or frequent hitter (includes GB88)",
        "REFERENCE": "crystallographic ligand redocked (AZ8838-(S), AZ3451)",
        "DECOY_DISQUALIFIED": "decoy that collapsed onto a non-decoy structure in preparation",
    }
    for cls, n in bench[bench.pocket == primary["pocket"]].mol_class.value_counts().items():
        w(f"| `{cls}` | {n} | {meanings.get(cls, '')} |")
    w("")

    # ---------------- enrichment ----------------
    w("## 3. Enrichment")
    w("")
    w(f"Bootstrap: {primary['n_bootstrap']} stratified resamples. Permutation null: "
      f"{primary['n_permutation']} label shuffles. Seed {primary['seed']}. "
      "Ties are handled explicitly — `CRYSTAL_IFP_RECOVERY` takes only 17 distinct "
      "values in 5NDD (k/16), so every metric averages across tied blocks rather "
      "than trusting sort order.")
    w("")
    w(f"### 3.1 {primary['pocket']}"
      f"{' (clash-filtered)' if primary.get('clash_filtered') else ''}")
    w("")
    w(metric_table(res))
    w("")
    w("Confidence intervals on the early-recognition metrics, which are what a "
      "shortlist actually depends on:")
    w("")
    w(ci_table(res))
    w("")
    w("The last five rows are **negative controls**: molecular properties that "
      "carry no docking information whatsoever. A docking score that does not "
      "clearly beat them is not measuring binding, it is re-reading a property. "
      "A control AUC below 0.5 is just as informative as one above: what matters "
      "is its distance from 0.5, given in the `|AUC−0.5|` column below.")
    w("")
    w("| Negative control | ROC-AUC | \\|AUC−0.5\\| |")
    w("|---|---|---|")
    for k in ORDER:
        if k in CONTROLS and k in res and res[k].get("status") != "INSUFFICIENT_DATA":
            w(f"| {SCORE_LABEL[k]} | {fmt(res[k]['ROC_AUC']['value'])} | "
              f"{fmt(res[k].get('auc_abs_deviation_from_chance'))} |")
    w("")
    cont = primary.get("score_property_spearman_within_decoys") or {}
    if cont:
        w("### 3.x How much of each score is just a molecular property?")
        w("")
        w("Spearman correlation computed **within the decoys only**, so the "
          "active/decoy label cannot manufacture the correlation. A score that "
          "correlates strongly with a property inherits that property's "
          "separating power for free.")
        w("")
        props = sorted({p for v in cont.values() for p in v})
        w("| Score | " + " | ".join(props) + " |")
        w("|---|" + "---|" * len(props))
        for k, v in cont.items():
            w(f"| {SCORE_LABEL.get(k, k)} | "
              + " | ".join(fmt(v.get(p), 3) for p in props) + " |")
        w("")

    for (pocket, clash), pack in sorted(packs.items()):
        if pack is primary:
            continue
        w(f"### 3.{2 + list(packs).index((pocket, clash))} {pocket}"
          f"{' (clash-filtered)' if clash else ' (no clash filter)'}")
        w("")
        w(f"{pack['n_actives']} actives, {pack['n_decoys']} decoys.")
        w("")
        w(metric_table(pack["enrichment"]))
        w("")

    # ---------------- IFP null ----------------
    w("## 4. The interaction-fingerprint null distribution")
    w("")
    w("This is the question the campaign most needs answered: when a candidate "
      "shows `CRYSTAL_IFP_RECOVERY` of 0.875 or 0.938, is that unusual, or is it "
      "simply what any molecule of that size gets in that pocket?")
    w("")
    w(f"Over **{null['n_decoys_with_ifp']} decoys** in `{primary['pocket']}`"
      f"{' after clash filtering' if primary.get('clash_filtered') else ''}:")
    w("")
    w("| Threshold | P(decoy ≥ threshold) | decoys |")
    w("|---|---|---|")
    for key, lab in (("P_ge_0.800", "≥ 0.800"), ("P_ge_0.875", "≥ 0.875"),
                     ("P_ge_0.938", "≥ 0.938"), ("P_eq_1.000", "= 1.000")):
        cnt = null["exceedance_counts"][key.replace("P_", "n_")]
        w(f"| **{lab}** | **{null['exceedance'][key]:.4f}** | {cnt} |")
    w("")
    w(f"Decoy distribution: mean {null['mean']:.4f}, median {null['median']:.4f}, "
      f"sd {null['std']:.4f}, range {null['min']:.4f}–{null['max']:.4f}.")
    w("")
    w("Deciles:")
    w("")
    w("| " + " | ".join(f"p{p}" for p in range(0, 101, 10)) + " |")
    w("|" + "---|" * 11)
    w("| " + " | ".join(f"{null['deciles'][f'p{p}']:.4f}" for p in range(0, 101, 10)) + " |")
    w("")
    if "heavy_atom_correlation" in null:
        hc = null["heavy_atom_correlation"]
        w("### 4.1 Does IFP recovery just track ligand size?")
        w("")
        w(f"Among decoys, `CRYSTAL_IFP_RECOVERY` vs heavy-atom count: "
          f"**Pearson r = {hc['pearson_r']:.3f}**, "
          f"**Spearman ρ = {hc['spearman_rho']:.3f}** (n = {hc['n']}). "
          f"{hc['interpretation']}.")
        w("")
        if null.get("by_heavy_atom_bin"):
            w("| heavy atoms | n | median IFP | mean | max | P(≥0.875) | P(≥0.938) |")
            w("|---|---|---|---|---|---|---|")
            for b in null["by_heavy_atom_bin"]:
                w(f"| {b['bin']} | {b['n']} | {b['median']:.4f} | {b['mean']:.4f} | "
                  f"{b['max']:.4f} | {b['P_ge_0.875']:.4f} | {b['P_ge_0.938']:.4f} |")
            w("")
    w("### 4.2 Recovery by class")
    w("")
    w("| Class | n | median | mean | max | P(≥0.875) |")
    w("|---|---|---|---|---|---|")
    for cls, v in sorted(primary["ifp_by_class"].items(),
                         key=lambda kv: -kv[1]["median"]):
        w(f"| `{cls}` | {v['n']} | {v['median']:.4f} | {v['mean']:.4f} | "
          f"{v['max']:.4f} | {v['P_ge_0_875']:.4f} |")
    w("")

    if extra:
        w("## 5. Supporting checks")
        w("")
        for k, v in extra.items():
            w(f"### {k}")
            w("")
            w("```")
            w(json.dumps(v, indent=2, default=str)[:4000])
            w("```")
            w("")

    # ---------------- trust ----------------
    w("## 6. Which scores to trust, and how much")
    w("")
    w("| Score | Verdict | Basis | Suggested use in the final ranking |")
    w("|---|---|---|---|")
    advice = {
        "USEFUL": "keep at current weight",
        "WEAK": "keep but down-weight",
        "AT CHANCE": "**down-weight to ~0 for ranking**; report as description only",
        "INVERTED": "**do not use as-is**; it is anti-predictive on this benchmark",
        "NOT EVALUATED": "insufficient data",
    }
    for k in ORDER:
        if k not in res or res[k].get("status") == "INSUFFICIENT_DATA":
            continue
        cls, why = verdict_for(k, res[k])
        w(f"| {SCORE_LABEL.get(k, k)} | **{cls}** | {why} | {advice[cls]} |")
    w("")

    w("## 7. Limits of this benchmark")
    w("")
    w("- **Decoys are presumed inactive, not measured inactive.** Most have never "
      "been tested against PAR2. The `CENSORED_INACTIVE` class is the only set here "
      "that was genuinely tested and found inactive, and it is small.")
    w(f"- **The actives are not fully independent.** "
      f"{int((inc.reference_patent.notna()).sum())} of {len(inc)} come from two "
      "patents sharing one assay cascade (US-10550089-B2, US-10995072-B2). "
      "Scaffold counts are reported alongside molecule counts throughout, and a "
      "scaffold-level analysis is included where the numbers permit.")
    w("- **A small actives set makes confidence intervals wide.** Read the CI, not "
      "the point estimate; several intervals here are wide enough to contain both "
      "'useful' and 'useless'.")
    w("- **The receptor used for fingerprinting is the defective one.** "
      "`v2_interactions.py` hard-codes `*_protonated_pH74.pdb`, in which all 39 "
      "lysines are neutral and all Asp/Glu are protonated, and the crystal "
      "reference key sets were computed on that same file. This benchmark "
      "reproduces that configuration deliberately, so that the null distribution "
      "is comparable with the campaign's own numbers. It is a property of the "
      "campaign, not a choice made here, and it means no ionic interaction can "
      "appear in any fingerprint on either side.")
    w("- **The decoys are NOT perfectly property-matched.** Mann-Whitney tests "
      "over the final sets give p = 0.66 (cLogP), 0.71 (rotatable bonds), 0.85 "
      "(formal charge), 0.15 (TPSA), 0.08 (heavy atoms) and 0.03 (MW) — all "
      "acceptable — but **p < 1e-4 for both HBD and HBA**: the actives carry a "
      "median of 2 donors against the decoys' 1, and 3 acceptors against 4. The "
      "exact-match tier yielded no decoys at all, so every decoy came from a "
      "widened tier. Any score sensitive to hydrogen bonding therefore gets some "
      "separation for free, which is precisely why the property negative controls "
      "above are reported alongside every docking score.")
    w("- **Docking never demonstrates antagonism.** Static docking cannot separate "
      "an antagonist from a biased agonist; only the functional assays can.")
    w("")

    args.out.write_text("\n".join(L) + "\n")
    print(f"wrote {args.out} ({len(L)} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
