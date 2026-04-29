#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNNER="${PROJECT_ROOT}/scripts/bmc07_backbone_variation_runner.py"
CONFIG="${PROJECT_ROOT}/data/bmc08_realdata_config.yaml"
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "[BMC-08a] Open run start"
echo "  project: ${PROJECT_ROOT}"
echo "  runner : ${RUNNER}"
echo "  config : ${CONFIG}"
echo "  python : ${PYTHON_BIN}"

if [[ ! -f "${RUNNER}" ]]; then
  echo "ERROR: runner not found: ${RUNNER}" >&2
  exit 1
fi

if [[ ! -f "${CONFIG}" ]]; then
  echo "ERROR: config not found: ${CONFIG}" >&2
  exit 1
fi

if [[ ! -f "${PROJECT_ROOT}/data/baseline_relational_table_real.csv" ]]; then
  echo "ERROR: missing input: ${PROJECT_ROOT}/data/baseline_relational_table_real.csv" >&2
  exit 1
fi

if [[ ! -f "${PROJECT_ROOT}/data/node_metadata_real.csv" ]]; then
  echo "ERROR: missing input: ${PROJECT_ROOT}/data/node_metadata_real.csv" >&2
  exit 1
fi

"${PYTHON_BIN}" "${RUNNER}" --config "${CONFIG}"

echo "[BMC-08a] Open run finished"
