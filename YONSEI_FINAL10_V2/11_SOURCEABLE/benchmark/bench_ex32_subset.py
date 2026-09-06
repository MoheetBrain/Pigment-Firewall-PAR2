#!/usr/bin/env python3
"""Select the EX32 precision subset: every active plus a random decoy sample.

The purpose is narrow. EX8 is the benchmark; EX32 exists only to test whether
the EX8 conclusion survives a four-fold increase in sampling. The campaign's own
finding was that EX32 is a resampling rather than an upgrade (194 molecules
improved on Vina, 245 got worse, median change 0.0), so the decoy sample only
has to be large enough to detect a change in enrichment, not to re-derive it.

The decoy sample is drawn uniformly at random from the docked decoys with a
fixed seed, NOT from the top of any score. Sampling the top would bias the EX32
comparison towards molecules that EX8 already liked.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ligand-table", type=Path, nargs="+", required=True)
    ap.add_argument("--input", type=Path, nargs="+", required=True)
    ap.add_argument("--actives", type=Path, required=True)
    ap.add_argument("--n-decoys", type=int, default=250)
    ap.add_argument("--seed", type=int, default=20260906)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    lig = pd.concat([pd.read_csv(p) for p in args.ligand_table], ignore_index=True)
    inp = pd.concat([pd.read_csv(p) for p in args.input], ignore_index=True)
    prepared = set(lig.cand_id)

    A = pd.read_csv(args.actives)
    inc_ids = set(A.loc[A.include_in_enrichment == True, "chembl_id"].dropna())  # noqa: E712
    supp = set(A.loc[A.supplementary_source.notna()
                     & (A.include_in_enrichment == True), "name_canonical"].dropna())  # noqa: E712

    keep = inp[inp.cand_id.isin(prepared)].copy()
    is_active = keep.source_ref.isin(inc_ids) | keep.label_name.isin(supp)
    # every non-decoy is carried at EX32: actives, controls, references
    non_decoy = keep[keep.mol_class != "DECOY"]
    decoys = keep[keep.mol_class == "DECOY"]
    n = min(args.n_decoys, len(decoys))
    pick = rng.choice(decoys.index.to_numpy(), size=n, replace=False)
    sel = pd.concat([non_decoy, decoys.loc[pick]], ignore_index=True)
    sel["pockets"] = "5NDD_orthosteric;5NDZ_allosteric"
    sel["smiles"] = sel.smiles
    args.out.parent.mkdir(parents=True, exist_ok=True)
    sel.to_csv(args.out, index=False)
    print(f"EX32 subset: {len(sel)} molecules "
          f"({int(is_active.sum())} enrichment-set actives among "
          f"{len(non_decoy)} non-decoys, {n} randomly sampled decoys)")
    print(sel.mol_class.value_counts().to_string())
    print(f"decoy sampling fraction: {n}/{len(decoys)} = {n / max(len(decoys), 1):.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
