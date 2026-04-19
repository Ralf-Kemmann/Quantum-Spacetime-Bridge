#!/usr/bin/env bash
set -euo pipefail

# Mini-scan for:
#   K.0 at t=1.0
#   N.1a with alpha=0.5 at t=1.0
#   N.1a with alpha=2.0 at t=1.0
#
# Default theta values:
#   0.02 0.026 0.03 0.035 0.04
#
# Usage:
#   chmod +x run_n1a_miniscan.sh
#   ./run_n1a_miniscan.sh
#
# Optional:
#   THETAS="0.02 0.026 0.03 0.035 0.04 0.045" ./run_n1a_miniscan.sh

THETAS="${THETAS:-0.02 0.026 0.03 0.035 0.04}"
OUTROOT="${OUTROOT:-results/n1a_scan}"

echo "Running mini-scan with theta values: ${THETAS}"
echo "Output root: ${OUTROOT}"

for TH in ${THETAS}; do
  echo "========================================"
  echo "theta = ${TH}"
  echo "----------------------------------------"

  python -m dpb.k0_n0_reference run-k0 \
    --mode free \
    --p=-1.5,-0.5,0.5,1.5 \
    --m 1.0 \
    --t 1.0 \
    --L 10.0 \
    --theta "${TH}" \
    --outdir "${OUTROOT}/k0_t1/theta_${TH}"

  python -m dpb.k0_n0_reference run-n1a \
    --mode free \
    --p=-1.5,-0.5,0.5,1.5 \
    --m 1.0 \
    --t 1.0 \
    --L 10.0 \
    --theta "${TH}" \
    --dispersion-mode scaled_quadratic \
    --alpha 0.5 \
    --outdir "${OUTROOT}/n1a_alpha_0p5_t1/theta_${TH}"

  python -m dpb.k0_n0_reference run-n1a \
    --mode free \
    --p=-1.5,-0.5,0.5,1.5 \
    --m 1.0 \
    --t 1.0 \
    --L 10.0 \
    --theta "${TH}" \
    --dispersion-mode scaled_quadratic \
    --alpha 2.0 \
    --outdir "${OUTROOT}/n1a_alpha_2p0_t1/theta_${TH}"
done

echo
echo "Mini-scan finished."
echo

for TH in ${THETAS}; do
  echo "========================================"
  echo "theta = ${TH}"
  echo "--- K0 ---"
  grep -E "^(run_kind|theta:|theta_crit:|n_edges:|connected_components:|graph_diameter:|standard_pairs:|  d03_minus_d01:|  d03_minus_d12:|  d02_minus_d13:)" \
    "${OUTROOT}/k0_t1/theta_${TH}/summary.txt" || true

  echo "--- N1a alpha=0.5 ---"
  grep -E "^(run_kind|theta:|wrong_dispersion:|theta_crit:|n_edges:|connected_components:|graph_diameter:|standard_pairs:|  d03_minus_d01:|  d03_minus_d12:|  d02_minus_d13:)" \
    "${OUTROOT}/n1a_alpha_0p5_t1/theta_${TH}/summary.txt" || true

  echo "--- N1a alpha=2.0 ---"
  grep -E "^(run_kind|theta:|wrong_dispersion:|theta_crit:|n_edges:|connected_components:|graph_diameter:|standard_pairs:|  d03_minus_d01:|  d03_minus_d12:|  d02_minus_d13:)" \
    "${OUTROOT}/n1a_alpha_2p0_t1/theta_${TH}/summary.txt" || true
  echo
done
