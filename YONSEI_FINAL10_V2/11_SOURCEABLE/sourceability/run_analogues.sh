#!/bin/sh
# Resolve Agent 2's deduplicated analogue set in chunks so partial results
# always survive on disk.  Sequential by design: the resolver already runs
# Arthor 3-way concurrent internally and the public APIs must not be hammered.
OUT=YONSEI_FINAL10_V2/11_SOURCEABLE/sourceability
for f in $OUT/chunks/analogues_chunk*.csv; do
  tag=$(basename "$f" .csv | sed 's/analogues_chunk/ANALOGUES/')
  if [ -f "$OUT/${tag}_SOURCEABILITY_SUMMARY.csv" ]; then
    echo "SKIP $tag (already done)"; continue
  fi
  echo "START $tag $(date +%H:%M:%S)"
  .venv-v2/bin/python YONSEI_FINAL10_V2/scripts/v2_sourceability.py \
     --input "$f" --id-col analogue_id --smiles-col canonical_smiles \
     --inchikey-col inchikey --outdir "$OUT" --cache-dir "$OUT/cache" \
     --tag "$tag" > "$OUT/logs_${tag}.txt" 2>&1
  echo "DONE  $tag $(date +%H:%M:%S) $(grep -o 'classification counts.*' $OUT/logs_${tag}.txt)"
done
echo "ALL_ANALOGUE_CHUNKS_COMPLETE"
