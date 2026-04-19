#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_PATH="configs/config_m39a_family_full_audit.yaml"
RUNNER_PATH="src/m39a_family_full_audit_runner.py"

echo "=== M.3.9a.2 Family Full Audit ==="
echo "PROJECT_ROOT: ${PROJECT_ROOT}"
echo "CONFIG_PATH : ${CONFIG_PATH}"
echo "RUNNER_PATH : ${RUNNER_PATH}"
echo

if [[ ! -f "${PROJECT_ROOT}/${CONFIG_PATH}" ]]; then
  echo "ERROR: Config not found: ${CONFIG_PATH}" >&2
  exit 1
fi

if [[ ! -f "${PROJECT_ROOT}/${RUNNER_PATH}" ]]; then
  echo "ERROR: Runner not found: ${RUNNER_PATH}" >&2
  exit 1
fi

PYTHON_BIN="python3"
if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "ERROR: python3 not found in PATH" >&2
  exit 1
fi

echo "Using Python: ${PYTHON_BIN}"
echo

cd "${PROJECT_ROOT}"

"${PYTHON_BIN}" "${RUNNER_PATH}" \
  --project-root . \
  --config "${CONFIG_PATH}"

echo
echo "M.3.9a.2 completed."