#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

FEATURETABLE_CFG="${PROJECT_ROOT}/data/bmc08b_m39x1_no_ring_mirror_config.yaml"
FEATURETABLE_SCRIPT="${PROJECT_ROOT}/scripts/build_bmc08a_feature_table_from_m39x1_no_ring_mirror.py"
INPUT_BUILD_SCRIPT="${PROJECT_ROOT}/scripts/build_bmc08a_realdata_inputs.py"
VARIANT_RUNNER="${PROJECT_ROOT}/scripts/bmc07_backbone_variation_runner.py"
RUN_CONFIG="${PROJECT_ROOT}/data/bmc08b_realdata_config.yaml"

echo "[BMC-08b] Open run start"
echo "  project: ${PROJECT_ROOT}"
echo "  python : ${PYTHON_BIN}"

for f in "${FEATURETABLE_SCRIPT}" "${FEATURETABLE_CFG}" "${INPUT_BUILD_SCRIPT}" "${VARIANT_RUNNER}" "${RUN_CONFIG}"; do
  if [[ ! -f "${f}" ]]; then
    echo "ERROR: missing required file: ${f}" >&2
    exit 1
  fi
done

"${PYTHON_BIN}" "${FEATURETABLE_SCRIPT}" --config "${FEATURETABLE_CFG}"

"${PYTHON_BIN}" "${INPUT_BUILD_SCRIPT}"   --input "${PROJECT_ROOT}/data/bmc08b_real_units_feature_table.csv"   --output-dir "${PROJECT_ROOT}/data"

cp "${PROJECT_ROOT}/data/baseline_relational_table_real.csv" "${PROJECT_ROOT}/data/baseline_relational_table_real_bmc08b.csv"
cp "${PROJECT_ROOT}/data/node_metadata_real.csv" "${PROJECT_ROOT}/data/node_metadata_real_bmc08b.csv"

"${PYTHON_BIN}" "${VARIANT_RUNNER}" --config "${RUN_CONFIG}"

echo "[BMC-08b] Open run finished"
