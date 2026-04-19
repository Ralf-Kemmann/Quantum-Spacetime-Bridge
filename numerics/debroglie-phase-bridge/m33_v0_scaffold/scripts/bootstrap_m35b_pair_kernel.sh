#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-.}"
RUN_ROOT="${2:-${PROJECT_ROOT}/runs/M33_V0_alpha_peak_robustness}"
OUT_ROOT="${RUN_ROOT}/V0_source_scan"

mkdir -p "${OUT_ROOT}"

cat > "${OUT_ROOT}/source_pair_kernel_alpha.csv" <<'CSV'
run_id,t,p_family,alpha,pair_i,pair_j,p_i,p_j,kbar_ij,kbar_abs_ij,kbar_sign
CSV

cat > "${OUT_ROOT}/source_pair_kernel_alpha_validation.csv" <<'CSV'
run_id,t,p_family,alpha,expected_pairs,found_pairs,pair_count_ok,finite_fraction,sign_consistency_ok
CSV

cat > "${OUT_ROOT}/source_pair_kernel_alpha_summary.json" <<'JSON'
{
  "run_id": "",
  "n_rows": 0,
  "n_t_values": 0,
  "n_p_families": 0,
  "n_alpha_values": 0,
  "n_pairs_per_family": {},
  "finite_fraction_global": null,
  "source_origin": "",
  "all_pair_count_ok": false,
  "all_sign_consistency_ok": false
}
JSON

echo "Initialized M.3.5b.1 pair-kernel export structure at: ${OUT_ROOT}"
echo "Next step:"
echo "  python ${PROJECT_ROOT}/src/m35b_pair_kernel_exporter.py --project-root ${PROJECT_ROOT} --config ${PROJECT_ROOT}/configs/config_m33_v0.yaml"
