#!/usr/bin/env bash
# V2 corrected dual-pocket GNINA screen.
#
# Runs the sharded ligand library produced by v2_prepare_ligands.py against the
# corrected 5NDD orthosteric and 5NDZ allosteric pockets. Resumable: a shard
# with a matching .done sentinel is skipped.
#
# Usage:
#   bash v2_run_screen.sh --shards DIR --out DIR [options]
#
# Options:
#   --gnina PATH          gnina binary (default: gnina on PATH)
#   --stage fast|refine   parameter preset (default: fast)
#   --exhaustiveness N    override preset
#   --num-modes N         override preset
#   --jobs N              concurrent gnina processes (default: 4)
#   --cpu-per-job N       --cpu passed to gnina (default: 2)
#   --device gpu|cpu      GPU (default) or forced CPU
#   --pocket NAME         restrict to one pocket
#   --seed N              gnina seed (default 20260904)
#   --dry-run             print the commands only
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
POCKETS_DIR="$ROOT/YONSEI_FINAL10_V2/01_REFERENCE_POCKETS"
GNINA_BIN="${GNINA_BIN:-gnina}"
STAGE="fast"; EXH=""; MODES=""; JOBS=4; CPUJ=2; DEVICE="gpu"
SHARDS=""; OUT=""; ONLY_POCKET=""; SEED=20260904; DRY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --shards) SHARDS="$2"; shift 2;;
    --out) OUT="$2"; shift 2;;
    --gnina) GNINA_BIN="$2"; shift 2;;
    --stage) STAGE="$2"; shift 2;;
    --exhaustiveness) EXH="$2"; shift 2;;
    --num-modes) MODES="$2"; shift 2;;
    --jobs) JOBS="$2"; shift 2;;
    --cpu-per-job) CPUJ="$2"; shift 2;;
    --device) DEVICE="$2"; shift 2;;
    --pocket) ONLY_POCKET="$2"; shift 2;;
    --seed) SEED="$2"; shift 2;;
    --dry-run) DRY=1; shift;;
    *) echo "unknown option: $1" >&2; exit 2;;
  esac
done

[[ -n "$SHARDS" && -n "$OUT" ]] || { echo "--shards and --out are required" >&2; exit 2; }

case "$STAGE" in
  fast)   : "${EXH:=8}";  : "${MODES:=5}";;
  refine) : "${EXH:=32}"; : "${MODES:=9}";;
  *) echo "--stage must be fast or refine" >&2; exit 2;;
esac

DEVICE_FLAGS=()
if [[ "$DEVICE" == "cpu" ]]; then
  DEVICE_FLAGS+=(--no_gpu)
  export CUDA_VISIBLE_DEVICES=-1
fi

mkdir -p "$OUT/poses" "$OUT/logs" "$OUT/done"

command -v "$GNINA_BIN" >/dev/null 2>&1 || [[ -x "$GNINA_BIN" ]] || {
  echo "gnina not found at '$GNINA_BIN'" >&2; exit 3; }

RUNMETA="$OUT/RUN_METADATA.json"
{
  printf '{\n'
  printf '  "started_utc": "%s",\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf '  "host": "%s",\n' "$(hostname)"
  printf '  "gnina_version": "%s",\n' "$("$GNINA_BIN" --version 2>&1 | head -1 | tr -d '"')"
  printf '  "stage": "%s",\n' "$STAGE"
  printf '  "exhaustiveness": %s,\n' "$EXH"
  printf '  "num_modes": %s,\n' "$MODES"
  printf '  "cnn_scoring": "rescore",\n'
  printf '  "device": "%s",\n' "$DEVICE"
  printf '  "jobs": %s,\n' "$JOBS"
  printf '  "cpu_per_job": %s,\n' "$CPUJ"
  printf '  "seed": %s,\n' "$SEED"
  printf '  "gpu": "%s"\n' "$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)"
  printf '}\n'
} > "$RUNMETA"
cat "$RUNMETA"

_sha256() { command -v sha256sum >/dev/null 2>&1 && sha256sum "$1" | cut -d" " -f1 || shasum -a 256 "$1" | cut -d" " -f1; }
export -f _sha256

run_shard() {
  local sdf="$1"
  local base pocket conf receptor done_file out_sdf log
  base="$(basename "$sdf" .sdf)"
  pocket="${base%%_shard*}"
  case "$pocket" in
    5NDD_orthosteric) conf="$POCKETS_DIR/configs/BoxA_orthosteric_5NDD_ligand_centered.conf";
                      receptor="$POCKETS_DIR/receptors/5NDD_inactive_orthosteric_receptor_clean.pdbqt";;
    5NDZ_allosteric)  conf="$POCKETS_DIR/configs/BoxB_allosteric_5NDZ_ligand_centered.conf";
                      receptor="$POCKETS_DIR/receptors/5NDZ_inactive_allosteric_receptor_clean.pdbqt";;
    *) echo "SKIP unknown pocket for $base" >&2; return 0;;
  esac
  done_file="$OUT/done/$base.done"
  out_sdf="$OUT/poses/${base}_out.sdf.gz"
  log="$OUT/logs/${base}.log"
  if [[ -s "$done_file" && -s "$out_sdf" ]]; then
    echo "SKIP $base (already complete)"; return 0
  fi
  # Box geometry comes from the validated config; the receptor is passed
  # explicitly so a relative path inside the config cannot bind the wrong file.
  local cx cy cz sx sy sz
  local -a cmd dflags=()
  [[ "$DEVICE" == "cpu" ]] && dflags+=(--no_gpu)
  cx=$(awk -F'= *' '/center_x/{print $2}' "$conf"); cy=$(awk -F'= *' '/center_y/{print $2}' "$conf")
  cz=$(awk -F'= *' '/center_z/{print $2}' "$conf"); sx=$(awk -F'= *' '/size_x/{print $2}' "$conf")
  sy=$(awk -F'= *' '/size_y/{print $2}' "$conf"); sz=$(awk -F'= *' '/size_z/{print $2}' "$conf")
  cmd=("$GNINA_BIN" --receptor "$receptor" --ligand "$sdf" --out "$out_sdf"
       --center_x "$cx" --center_y "$cy" --center_z "$cz"
       --size_x "$sx" --size_y "$sy" --size_z "$sz"
       --exhaustiveness "$EXH" --num_modes "$MODES" --cnn_scoring rescore
       --seed "$SEED" --cpu "$CPUJ" "${dflags[@]}")
  if [[ "$DRY" == "1" ]]; then printf '%q ' "${cmd[@]}"; echo; return 0; fi
  local start rc
  start=$(date +%s)
  "${cmd[@]}" > "$log" 2>&1
  rc=$?
  if [[ $rc -ne 0 || ! -s "$out_sdf" ]]; then
    echo "FAIL $base rc=$rc (see $log)" >&2
    return 1
  fi
  {
    printf '{"shard":"%s","pocket":"%s","rc":%d,"seconds":%d,' "$base" "$pocket" "$rc" "$(( $(date +%s) - start ))"
    printf '"input_sha256":"%s","output_sha256":"%s",' \
      "$(_sha256 "$sdf")" "$(_sha256 "$out_sdf")"
    printf '"exhaustiveness":%s,"num_modes":%s,"stage":"%s","device":"%s"}\n' "$EXH" "$MODES" "$STAGE" "$DEVICE"
  } > "$done_file"
  echo "OK $base ($(( $(date +%s) - start ))s)"
}
export -f run_shard
export OUT POCKETS_DIR GNINA_BIN EXH MODES SEED CPUJ DRY STAGE DEVICE

SHARD_LIST=()
while IFS= read -r shard_path; do
  [[ -n "$ONLY_POCKET" && "$shard_path" != *"$ONLY_POCKET"* ]] && continue
  SHARD_LIST+=("$shard_path")
done < <(ls "$SHARDS"/*.sdf | sort)
[[ ${#SHARD_LIST[@]} -gt 0 ]] || { echo "no shards found in $SHARDS" >&2; exit 2; }
echo "shards to process: ${#SHARD_LIST[@]}"

printf '%s\n' "${SHARD_LIST[@]}" \
  | xargs -P "$JOBS" -I{} bash -c 'run_shard "$@"' _ {} \
  | tee -a "$OUT/progress.log"

TOTAL=${#SHARD_LIST[@]}
DONE=$(ls "$OUT/done" 2>/dev/null | wc -l | tr -d ' ')
echo "completed shards: $DONE / $TOTAL"
[[ "$DONE" -eq "$TOTAL" ]] || { echo "INCOMPLETE: rerun the same command to resume" >&2; exit 4; }
echo "V2_SCREEN_STAGE_${STAGE}_COMPLETE"
