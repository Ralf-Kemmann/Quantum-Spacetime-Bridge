#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-.}"
RUN_ROOT="${2:-${PROJECT_ROOT}/runs/M33_V0_alpha_peak_robustness}"
OUT_ROOT="${RUN_ROOT}/M35b_packet_kernel"

mkdir -p   "${OUT_ROOT}"   "${OUT_ROOT}/plots"

cat > "${OUT_ROOT}/source_curve_grid.csv" <<'CSV'
run_id,t,p_family,theta,packet_model,source_feature,p0,sigma_p,alpha,source_curve_value
CSV

cat > "${OUT_ROOT}/source_candidate_grid.csv" <<'CSV'
run_id,t,p_family,theta,packet_model,source_feature,p0,sigma_p,alpha_candidate,candidate_value,candidate_prominence,source_branch_id,source_branch_center,delta_to_branch_center
CSV

cat > "${OUT_ROOT}/packet_fit_grid.csv" <<'CSV'
run_id,t,p_family,theta,packet_model,source_feature,p0,sigma_p,alpha_pref_source_model,branch_pref_source_model,source_score_model,alpha_pref_readout,branch_pref_readout,readout_score,delta_alpha,branch_match_flag,alpha_match_flag,loss_total
CSV

cat > "${OUT_ROOT}/packet_fit_best.csv" <<'CSV'
run_id,t,p_family,theta,packet_model,source_feature,best_p0,best_sigma_p,best_alpha_source,best_branch_source,alpha_pref_readout,branch_pref_readout,delta_alpha,branch_match_flag,alpha_match_flag,best_loss_total,fit_label
CSV

cat > "${OUT_ROOT}/packet_frequency_table.csv" <<'CSV'
run_id,aggregation_level,aggregation_key,n_total,n_S1,n_S2,n_S3,frac_S1,frac_S2,frac_S3,dominant_source_branch,source_branch_entropy
CSV

cat > "${OUT_ROOT}/packet_summary.json" <<'JSON'
{
  "final_label": "",
  "n_source_curve_rows": 0,
  "n_source_candidate_rows": 0,
  "n_fit_grid_rows": 0,
  "n_best_rows": 0,
  "branch_match_frac": null,
  "alpha_match_frac": null,
  "mean_delta_alpha": null
}
JSON

cat > "${OUT_ROOT}/packet_report.md" <<'MD'
# M.3.5b Packet Kernel Report

## Status
initialized
MD

echo "Initialized M.3.5b packet-kernel structure at: ${OUT_ROOT}"
echo "Next step:"
echo "  python ${PROJECT_ROOT}/src/m35b_packet_runner.py --project-root ${PROJECT_ROOT} --config ${PROJECT_ROOT}/configs/config_m33_v0.yaml"
