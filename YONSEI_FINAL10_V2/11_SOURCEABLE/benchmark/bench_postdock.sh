#!/usr/bin/env bash
# Post-docking analysis for the actives/decoys benchmark.
#
# Every stage is a CAMPAIGN script run with campaign conventions, so the numbers
# this produces are directly comparable to YONSEI_FINAL10_V2 evidence tables:
#   v2_collect_scores.py   GNINA pose scores from the gzipped output SDFs
#   v2_interactions.py     ProLIF fingerprints + CRYSTAL_IFP_RECOVERY
#   v2_pose_evidence.py    clash filter (minimizedAffinity < 0) + per-molecule evidence
#   v2_robust_anchors.py   protomer-independent polar-anchor geometry
#
# Usage: bash bench_postdock.sh <screen_dir> <ligand_table.csv> <tag>
set -euo pipefail

SCREEN="${1:?screen dir, e.g. $HOME/BENCH/ex8}"
LIGTAB="${2:?ligand table CSV with cand_id and heavy_atoms}"
TAG="${3:?tag, e.g. ex8}"

ROOT="$HOME/PAR2"
PY="$ROOT/.venv/bin/python"
S="$ROOT/YONSEI_FINAL10_V2/scripts"
OUT="$HOME/BENCH/analysis/$TAG"
mkdir -p "$OUT"
cd "$ROOT"

echo "=== [1/4] v2_collect_scores.py ==="
"$PY" "$S/v2_collect_scores.py" \
  --screen "$SCREEN" --ligand-table "$LIGTAB" --out "$OUT"

echo "=== [2/4] v2_interactions.py (all 9 poses) ==="
"$PY" "$S/v2_interactions.py" \
  --root "$ROOT" --screen "$SCREEN" --out "$OUT" \
  --pose all --max-pose 9 --workers 40

echo "=== [3/4] v2_pose_evidence.py (clash filter) ==="
"$PY" "$S/v2_pose_evidence.py" \
  --poses "$OUT/V2_POSE_SCORES.csv" \
  --interactions "$OUT/V2_POSE_INTERACTIONS.csv" \
  --ligand-table "$LIGTAB" \
  --out "$OUT/EVIDENCE_${TAG}.csv" --batch "bench_${TAG}"

echo "=== [4/4] v2_robust_anchors.py ==="
"$PY" "$S/v2_robust_anchors.py" \
  --poses "$SCREEN/poses" \
  --receptor-5ndd "$ROOT/YONSEI_FINAL10_V2/02_REFERENCE_VALIDATION_REPAIRED/5NDD_orthosteric_receptor_pH74_FIXED.pdb" \
  --receptor-5ndz "$ROOT/YONSEI_FINAL10_V2/02_REFERENCE_VALIDATION_REPAIRED/5NDZ_allosteric_receptor_pH74_FIXED.pdb" \
  --out "$OUT/ROBUST_ANCHORS_${TAG}.csv"

echo "=== POSTDOCK COMPLETE: $OUT ==="
ls -la "$OUT"
