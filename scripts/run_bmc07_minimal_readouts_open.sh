#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNNER="${PROJECT_ROOT}/scripts/bmc07_backbone_scaffold_isolation_runner_minimal_readouts.py"
CONFIG="${PROJECT_ROOT}/data/bmc07_config_minimal_readouts.yaml"
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "[BMC-07] Open run start"
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

"${PYTHON_BIN}" "${RUNNER}" --config "${CONFIG}"

echo "[BMC-07] Open run finished"
