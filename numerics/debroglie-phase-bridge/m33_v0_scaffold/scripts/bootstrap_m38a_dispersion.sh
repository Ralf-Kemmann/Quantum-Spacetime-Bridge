#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-.}"
RUN_ROOT="${2:-${PROJECT_ROOT}/runs/M33_V0_alpha_peak_robustness}"
OUT_ROOT="${RUN_ROOT}/M38a_dispersion_test"

mkdir -p \
  "${OUT_ROOT}" \
  "${OUT_ROOT}/plots"

cat > "${OUT_ROOT}/wavepacket_case_grid.csv" <<'CSV'
run_id,case_id,dispersion_mode,p_family,k0,sigma_k,t,v,nu,x_grid_size,k_grid_size,norm_ok
CSV

cat > "${OUT_ROOT}/wavepacket_metrics.csv" <<'CSV'
run_id,case_id,dispersion_mode,p_family,k0,sigma_k,t,v,nu,x_center,x_width,x_width_delta,x_skewness,x_kurtosis,phase_curvature_proxy
CSV

cat > "${OUT_ROOT}/dispersion_pair_top_summary.csv" <<'CSV'
run_id,case_id,dispersion_mode,p_family,k0,sigma_k,t,v,nu,n_pairs_total,top1_share,top3_share,top5_share,effective_pair_count,dominance_label
CSV

cat > "${OUT_ROOT}/dispersion_class_summary.csv" <<'CSV'
run_id,case_id,dispersion_mode,p_family,k0,sigma_k,t,v,nu,class_mode,class_label,class_rank,sum_contrib_primary,normalized_class_contrib
CSV

cat > "${OUT_ROOT}/dispersion_identity_comparison.csv" <<'CSV'
run_id,comparison_id,p_family,k0,sigma_k,t,v,nu,pair_sep_none,pair_sep_quadratic,delta_p_sep_none,delta_p_sep_quadratic,delta_p2_sep_none,delta_p2_sep_quadratic,delta_width_x,pair_sep_shift,delta_p_sep_shift,delta_p2_sep_shift,identity_shift_label
CSV

cat > "${OUT_ROOT}/dispersion_summary.json" <<'JSON'
{
  "n_cases_total": 0,
  "width_growth_detected_fraction": 0.0,
  "delta_p2_identity_preserved_fraction": 0.0,
  "delta_p_identity_preserved_fraction": 0.0,
  "pair_identity_preserved_fraction": 0.0,
  "dispersion_sensitive_fraction": 0.0,
  "dominant_preserved_identity_level": null,
  "final_label": ""
}
JSON

cat > "${OUT_ROOT}/dispersion_report.md" <<'MD'
# M.3.8a Dispersion Test

## Status
initialized
MD

echo "Initialized M.3.8a dispersion test structure at: ${OUT_ROOT}"
echo "Next step:"
echo "  python ${PROJECT_ROOT}/src/m38a_dispersion_runner.py --project-root ${PROJECT_ROOT} --config ${PROJECT_ROOT}/configs/config_m33_v0.yaml"
