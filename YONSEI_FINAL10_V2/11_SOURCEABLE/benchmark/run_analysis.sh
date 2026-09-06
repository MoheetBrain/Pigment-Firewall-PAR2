#!/usr/bin/env bash
# Local driver: pull the h3 analysis products, merge, compute enrichment and the
# IFP null, and render the report. Run after bench_postdock.sh has completed on
# h3 for the stage named by $STAGE.
set -euo pipefail

ROOT="/Users/moheet/Documents/ChatGPT/PAR2"
B="$ROOT/YONSEI_FINAL10_V2/11_SOURCEABLE/benchmark"
PY="$ROOT/.venv-v2/bin/python"
STAGE="${1:-ex8}"
EX32_ARG=()
[[ -f "$B/remote/ex32/DENOVO_EX8_CONSENSUS_ALL.csv" ]] && \
  EX32_ARG=(--ex32 "$B/remote/ex32/DENOVO_EX8_CONSENSUS_ALL.csv")

cd "$ROOT"

echo "=== merge ==="
"$PY" "$B/bench_merge.py" \
  --consensus "$B/remote/$STAGE/DENOVO_EX8_CONSENSUS_ALL.csv" \
  --anchors   "$B/remote/$STAGE/ROBUST_ANCHORS_${STAGE}_BEST.csv" \
  --input     "$B/BENCH_DOCKING_INPUT.csv" "$B/BENCH_DOCKING_INPUT_SUPP.csv" \
  --ligand-table "$B/BENCH_LIGAND_TABLE_ALL.csv" \
  --actives   "$B/PAR2_KNOWN_ACTIVES.csv" \
  --decoys    "$B/BENCH_DECOYS.csv" \
  "${EX32_ARG[@]}" \
  --out       "$B/PAR2_ACTIVE_DECOY_BENCHMARK.csv"

echo "=== enrichment: 5NDD, clash-filtered (PRIMARY) ==="
"$PY" "$B/bench_enrichment.py" --benchmark "$B/PAR2_ACTIVE_DECOY_BENCHMARK.csv" \
  --pocket 5NDD_orthosteric --clash-filter --out "$B/ENRICHMENT_5NDD_clashfiltered.json"

echo "=== enrichment: 5NDD, no clash filter ==="
"$PY" "$B/bench_enrichment.py" --benchmark "$B/PAR2_ACTIVE_DECOY_BENCHMARK.csv" \
  --pocket 5NDD_orthosteric --out "$B/ENRICHMENT_5NDD_allposes.json"

echo "=== enrichment: 5NDZ, clash-filtered ==="
"$PY" "$B/bench_enrichment.py" --benchmark "$B/PAR2_ACTIVE_DECOY_BENCHMARK.csv" \
  --pocket 5NDZ_allosteric --clash-filter --out "$B/ENRICHMENT_5NDZ_clashfiltered.json"

echo "=== sensitivity: one active per Murcko scaffold (analogue-bias guard) ==="
"$PY" "$B/bench_enrichment.py" --benchmark "$B/PAR2_ACTIVE_DECOY_BENCHMARK.csv" \
  --pocket 5NDD_orthosteric --clash-filter --one-active-per-scaffold \
  --out "$B/ENRICHMENT_5NDD_one_per_scaffold.json"

echo "=== sensitivity: potent actives only (<= 1 uM) ==="
"$PY" "$B/bench_enrichment.py" --benchmark "$B/PAR2_ACTIVE_DECOY_BENCHMARK.csv" \
  --pocket 5NDD_orthosteric --clash-filter --potency-cutoff-nM 1000 \
  --out "$B/ENRICHMENT_5NDD_potent_only.json"

echo "=== sensitivity: negatives = molecules MEASURED inactive at PAR2 ==="
"$PY" "$B/bench_enrichment.py" --benchmark "$B/PAR2_ACTIVE_DECOY_BENCHMARK.csv" \
  --pocket 5NDD_orthosteric --clash-filter --negatives CENSORED_INACTIVE \
  --out "$B/ENRICHMENT_5NDD_measured_inactives.json" || \
  echo "  (skipped: too few measured inactives)"

echo "=== extra analyses ==="
"$PY" "$B/bench_extra.py" --benchmark "$B/PAR2_ACTIVE_DECOY_BENCHMARK.csv" \
  --primary "$B/ENRICHMENT_5NDD_clashfiltered.json" \
  --sensitivity "$B/ENRICHMENT_5NDD_allposes.json" \
                "$B/ENRICHMENT_5NDD_one_per_scaffold.json" \
                "$B/ENRICHMENT_5NDD_potent_only.json" \
                "$B/ENRICHMENT_5NDD_measured_inactives.json" \
  --out "$B/BENCH_EXTRA_ANALYSES.json"

echo "=== report ==="
"$PY" "$B/bench_report.py" \
  --enrichment "$B/ENRICHMENT_5NDD_clashfiltered.json" \
               "$B/ENRICHMENT_5NDD_allposes.json" \
               "$B/ENRICHMENT_5NDZ_clashfiltered.json" \
  --benchmark  "$B/PAR2_ACTIVE_DECOY_BENCHMARK.csv" \
  --actives    "$B/PAR2_KNOWN_ACTIVES.csv" \
  --decoy-summary "$B/BENCH_DECOYS.summary.json" \
  --extra      "$B/BENCH_EXTRA_ANALYSES.json" \
  --out        "$B/PAR2_ENRICHMENT_METRICS.md"

echo "=== provenance ==="
"$PY" "$B/bench_provenance.py" --root "$ROOT" --bench "$B" \
  --commands "$B/COMMANDS_RUN.txt" --out "$B/BENCHMARK_PROVENANCE.json"

echo "=== DONE ==="
ls -la "$B"/PAR2_*.csv "$B"/PAR2_*.md "$B"/BENCHMARK_PROVENANCE.json
