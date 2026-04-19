#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

CONFIG_PATH="configs/config_m39x3f_type_b_map.yaml"
RUNNER_PATH="src/m39x3f_type_b_map_runner.py"
OUTDIR="runs/M39x3f_type_b_map"
VENV_DIR="${PROJECT_ROOT}/.venv"
VENV_PYTHON="${VENV_DIR}/bin/python"

echo "[INFO] Project root: ${PROJECT_ROOT}"
echo "[INFO] Config: ${CONFIG_PATH}"
echo "[INFO] Runner: ${RUNNER_PATH}"
echo "[INFO] Output dir: ${OUTDIR}"
echo "[INFO] Virtualenv dir: ${VENV_DIR}"

if [[ ! -f "${CONFIG_PATH}" ]]; then
  echo "[ERROR] Missing config: ${CONFIG_PATH}" >&2
  exit 1
fi

if [[ ! -f "${RUNNER_PATH}" ]]; then
  echo "[ERROR] Missing runner: ${RUNNER_PATH}" >&2
  exit 1
fi

if [[ ! -d "${VENV_DIR}" ]]; then
  echo "[INFO] Creating local virtual environment at ${VENV_DIR} ..."
  python3 -m venv "${VENV_DIR}"
fi

if [[ ! -x "${VENV_PYTHON}" ]]; then
  echo "[ERROR] Missing virtualenv python: ${VENV_PYTHON}" >&2
  exit 1
fi

echo "[INFO] Using python: ${VENV_PYTHON}"
"${VENV_PYTHON}" -V

echo "[INFO] Upgrading pip in local virtualenv ..."
"${VENV_PYTHON}" -m pip install --upgrade pip

echo "[INFO] Ensuring required packages are installed ..."
"${VENV_PYTHON}" -m pip install numpy pandas pyyaml tabulate

mkdir -p "${OUTDIR}"

echo "[INFO] Starting M.3.9x.3f bootstrap run ..."
"${VENV_PYTHON}" "${RUNNER_PATH}" --config "${CONFIG_PATH}"

echo "[INFO] Run finished."
echo "[INFO] Generated artifacts in ${OUTDIR}:"
find "${OUTDIR}" -maxdepth 1 -type f | sort