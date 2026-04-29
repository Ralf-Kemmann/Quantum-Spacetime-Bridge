#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

FEATURETABLE_SCRIPT="${PROJECT_ROOT}/scripts/build_bmc08c_feature_table_from_m39x1_sign_sensitive_ring.py"
FEATURETABLE_CFG="${PROJECT_ROOT}/data/bmc08c_m39x1_sign_sensitive_ring_config.yaml"
KNN_BUILD_SCRIPT="${PROJECT_ROOT}/scripts/build_bmc09a_knn_inputs_from_bmc08c.py"
KNN_CFG="${PROJECT_ROOT}/data/bmc09a_knn_config.yaml"
RUNNER="${PROJECT_ROOT}/scripts/bmc07_backbone_variation_runner.py"
RUN_CFG="${PROJECT_ROOT}/data/bmc09a_realdata_config.yaml"

echo "[BMC-09a] Open run start"
echo "  project: ${PROJECT_ROOT}"
echo "  python : ${PYTHON_BIN}"

for f in "${FEATURETABLE_SCRIPT}" "${FEATURETABLE_CFG}" "${KNN_BUILD_SCRIPT}" "${KNN_CFG}" "${RUNNER}" "${RUN_CFG}"; do
  if [[ ! -f "${f}" ]]; then
    echo "ERROR: missing required file: ${f}" >&2
    exit 1
  fi
done

"${PYTHON_BIN}" "${FEATURETABLE_SCRIPT}" --config "${FEATURETABLE_CFG}"
"${PYTHON_BIN}" "${KNN_BUILD_SCRIPT}" --config "${KNN_CFG}"
"${PYTHON_BIN}" "${RUNNER}" --config "${RUN_CFG}"

echo "[BMC-09a] Open run finished"
