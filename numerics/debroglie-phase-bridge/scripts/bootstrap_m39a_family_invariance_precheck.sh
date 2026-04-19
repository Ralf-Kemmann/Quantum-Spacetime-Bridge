#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-$(pwd)}"
CONFIG_PATH="${2:-configs/config_m39a_family_invariance_precheck.yaml}"
RUNNER_PATH="${3:-src/m39a_family_invariance_precheck_runner.py}"

echo "=== M.3.9a.1 Family Invariance Precheck ==="
echo "PROJECT_ROOT: ${PROJECT_ROOT}"
echo "CONFIG_PATH : ${CONFIG_PATH}"
echo "RUNNER_PATH : ${RUNNER_PATH}"
echo

cd "${PROJECT_ROOT}"

if [ ! -f "${CONFIG_PATH}" ]; then
  echo "ERROR: Config not found: ${CONFIG_PATH}" >&2
  exit 1
fi

if [ ! -f "${RUNNER_PATH}" ]; then
  echo "ERROR: Runner not found: ${RUNNER_PATH}" >&2
  exit 1
fi

PYTHON_BIN="python3"
if [ -x ".venv/bin/python" ]; then
  PYTHON_BIN=".venv/bin/python"
fi

echo "Using Python: ${PYTHON_BIN}"
echo

"${PYTHON_BIN}" "${RUNNER_PATH}" \
  --project-root "${PROJECT_ROOT}" \
  --config "${CONFIG_PATH}"

echo
echo "M.3.9a.1 completed."
