#!/usr/bin/env bash
set -euo pipefail

# Reproducible reference-only GNINA gate. This script never launches candidate
# docking; candidate work remains blocked until both corrected systems pass.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
V2_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ROOT_DIR="$(cd "${V2_DIR}/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
if [[ -z "${GNINA_BIN:-}" ]]; then
  if [[ -x "${HOME}/bin/gnina" ]]; then
    GNINA_BIN="${HOME}/bin/gnina"
  elif [[ -x "${HOME}/bin/gnina.cuda12.8.static" ]]; then
    GNINA_BIN="${HOME}/bin/gnina.cuda12.8.static"
  else
    GNINA_BIN="$(command -v gnina || true)"
  fi
fi
CPU_THREADS="${GNINA_CPU_THREADS:-4}"
SEED="${GNINA_SEED:-20260811}"

# Force GNINA onto CPU even if a future VM image exposes a CUDA device.
export CUDA_VISIBLE_DEVICES=-1

# The official GNINA v1.3.3 Linux binary dynamically links CUDA/cuDNN even
# when no NVIDIA device is present. The VM runner installs these exact runtime
# wheels under ~/gnina-cuda-libs and exposes their lib directories here.
if [[ -z "${GNINA_CUDA_LIB_DIRS:-}" && -d "${HOME}/gnina-cuda-libs" ]]; then
  GNINA_CUDA_LIB_DIRS="$(find "${HOME}/gnina-cuda-libs" -type d -name lib -print | paste -sd: -)"
fi
if [[ -n "${GNINA_CUDA_LIB_DIRS:-}" ]]; then
  export LD_LIBRARY_PATH="${GNINA_CUDA_LIB_DIRS}:${LD_LIBRARY_PATH:-}"
fi

if [[ -z "${GNINA_BIN}" || ! -x "${GNINA_BIN}" ]]; then
  echo "GNINA executable not found; candidate docking remains blocked." >&2
  exit 2
fi

mkdir -p "${V2_DIR}/01_BENCHMARK_REPAIR/corrected_redock"
"${PYTHON_BIN}" "${V2_DIR}/scripts/run_reference_redock.py" \
  --root "${ROOT_DIR}" --gnina "${GNINA_BIN}" --cpu "${CPU_THREADS}" \
  --seed "${SEED}" 5NDD_AZ8838
"${PYTHON_BIN}" "${V2_DIR}/scripts/run_reference_redock.py" \
  --root "${ROOT_DIR}" --gnina "${GNINA_BIN}" --cpu "${CPU_THREADS}" \
  --seed "${SEED}" 5NDZ_AZ3451
"${PYTHON_BIN}" "${V2_DIR}/scripts/validate_reference_redock.py" \
  --root "${ROOT_DIR}" --gnina "${GNINA_BIN}"

"${PYTHON_BIN}" - "${V2_DIR}/02_REFERENCE_VALIDATION/reference_redock_validation.json" <<'PY'
import json
import sys

result = json.load(open(sys.argv[1], encoding="utf-8"))
status = result.get("corrected_config_benchmark_status")
print(f"OPEN_REFERENCE_BENCHMARK_PASSED={status == 'PASS_BOTH_SYSTEMS_RMSD_UNDER_2A'}")
if status != "PASS_BOTH_SYSTEMS_RMSD_UNDER_2A":
    raise SystemExit("Corrected reference benchmark did not pass both systems; candidate docking remains blocked.")
PY
