#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
merge_outputs.py -- consolidate every tagged v2_sourceability.py run into the
canonical deliverable filenames for this lane.

Reads whatever <TAG>_SOURCEABILITY_MASTER.csv / <TAG>_SOURCEABILITY_SUMMARY.csv
and <TAG>_SOURCEABILITY_PROVENANCE.json files exist in this directory and writes:

    SOURCEABILITY_MASTER.csv      one row per molecule per vendor/registry hit
    SOURCEABILITY_SUMMARY.csv     one row per molecule, best classification
    SOURCEABILITY_PROVENANCE.json merged provenance across all runs

A ``panel`` column records which input set each row came from, so the TOP20
candidates, the de-novo TOP5, the reference control panel and (when it lands)
Agent 2's analogue set stay distinguishable inside one table.
"""

from __future__ import annotations

import csv
import datetime as _dt
import glob
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))

# tag -> human-readable panel label
PANEL_LABEL = {
    "PANEL": "FINAL_TOP20_and_IDEAL_DE_NOVO_TOP5",
    "REFPANEL": "PAR2_REFERENCE_CONTROL_PANEL",
    "ANALOGUES": "AGENT2_SOURCEABLE_ANALOGUES",
}


def load(pattern):
    out = []
    for p in sorted(glob.glob(os.path.join(HERE, pattern))):
        tag = os.path.basename(p).split("_SOURCEABILITY_")[0]
        with open(p, "r", encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh):
                # ANALOGUES01, ANALOGUES02, ... are chunks of one input set
                base = "ANALOGUES" if tag.startswith("ANALOGUES") else tag
                r["panel"] = PANEL_LABEL.get(base, tag)
                r["run_tag"] = tag
                out.append(r)
    return out


def write(path, rows, lead):
    if not rows:
        print(f"  (nothing to write for {os.path.basename(path)})")
        return
    keys = list(rows[0].keys())
    fields = lead + [k for k in keys if k not in lead]
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({f: r.get(f, "") for f in fields})
    print(f"  wrote {os.path.basename(path)}  ({len(rows)} rows)")


def main():
    master = load("*_SOURCEABILITY_MASTER.csv")
    summary = load("*_SOURCEABILITY_SUMMARY.csv")

    write(os.path.join(HERE, "SOURCEABILITY_MASTER.csv"), master,
          ["panel", "molecule_id", "vendor", "catalogue_id", "match_type",
           "stock_status", "make_on_demand_status"])
    write(os.path.join(HERE, "SOURCEABILITY_SUMMARY.csv"), summary,
          ["panel", "molecule_id", "classification", "best_vendor",
           "best_catalogue_id", "exact_match_found",
           "connectivity_only_match_found"])

    prov = {
        "lane": "AGENT 5 -- vendor / sourceability infrastructure",
        "generated_utc": _dt.datetime.now(_dt.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
        "tool": "YONSEI_FINAL10_V2/scripts/v2_sourceability.py",
        "cache_location": os.path.join(HERE, "cache"),
        "runs": {},
        "totals": {
            "master_rows": len(master),
            "molecules": len(summary),
            "classification_counts": dict(Counter(
                r["classification"] for r in summary)),
            "classification_by_panel": {
                p: dict(Counter(r["classification"] for r in summary
                                if r["panel"] == p))
                for p in sorted({r["panel"] for r in summary})},
            "match_type_counts": dict(Counter(
                r["match_type"] for r in master)),
            "resolver_counts": dict(Counter(r["resolver"] for r in master)),
            "vendor_counts": dict(Counter(
                r["vendor"] for r in master
                if r.get("record_class") in ("VENDOR_LEAD",
                                             "VENDOR_CATALOGUE_ID",
                                             "IN_STOCK_CATALOGUE",
                                             "ON_DEMAND_CATALOGUE",
                                             "FOR_SALE_CATALOGUE"))),
        },
    }
    for p in sorted(glob.glob(os.path.join(HERE, "*_SOURCEABILITY_PROVENANCE.json"))):
        tag = os.path.basename(p).split("_SOURCEABILITY_")[0]
        with open(p, "r", encoding="utf-8") as fh:
            prov["runs"][tag] = json.load(fh)

    out = os.path.join(HERE, "SOURCEABILITY_PROVENANCE.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(prov, fh, indent=2)
    print(f"  wrote SOURCEABILITY_PROVENANCE.json")
    print(json.dumps(prov["totals"]["classification_by_panel"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
