#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-.}"
RUN_ROOT="${2:-${PROJECT_ROOT}/runs/M33_V0_alpha_peak_robustness}"
OUT_ROOT="${RUN_ROOT}/M35c_soft_branch"

mkdir -p   "${OUT_ROOT}"   "${OUT_ROOT}/plots"

cat > "${OUT_ROOT}/nearest_branch_assignment.csv" <<'CSV'
run_id,t,p_family,theta,source_feature,best_alpha_source,hard_branch_source,hard_branch_readout,nearest_branch_source,nearest_branch_readout,dist_to_S1,dist_to_S2,dist_to_S3,nearest_branch_match_flag,hard_to_nearest_upgrade_flag
CSV

cat > "${OUT_ROOT}/soft_branch_scores.csv" <<'CSV'
run_id,t,p_family,theta,source_feature,best_alpha_source,alpha_pref_readout,mu_S1_source,mu_S2_source,mu_S3_source,mu_S1_readout,mu_S2_readout,mu_S3_readout,soft_overlap_score,soft_best_branch_source,soft_best_branch_readout,soft_branch_match_flag
CSV

cat > "${OUT_ROOT}/soft_branch_summary.csv" <<'CSV'
run_id,t,p_family,theta,source_feature,hard_branch_match_flag,nearest_branch_match_flag,soft_branch_match_flag,hard_delta_alpha,nearest_delta_center,soft_overlap_score,upgrade_label
CSV

cat > "${OUT_ROOT}/soft_branch_frequency_table.csv" <<'CSV'
run_id,aggregation_level,aggregation_key,n_total,n_S1,n_S2,n_S3,frac_S1,frac_S2,frac_S3,dominant_branch,branch_entropy,mode
CSV

cat > "${OUT_ROOT}/soft_branch_summary.json" <<'JSON'
{
  "final_label": "",
  "n_best_rows": 0,
  "hard_branch_match_frac": null,
  "nearest_branch_match_frac": null,
  "soft_branch_match_frac": null,
  "soft_overlap_mean": null,
  "upgrade_rate": null
}
JSON

cat > "${OUT_ROOT}/soft_branch_report.md" <<'MD'
# M.3.5c Soft / Nearest Branch Report

## Status
initialized
MD

echo "Initialized M.3.5c soft-branch structure at: ${OUT_ROOT}"
echo "Next step:"
echo "  python ${PROJECT_ROOT}/src/m35c_soft_branch_runner.py --project-root ${PROJECT_ROOT} --config ${PROJECT_ROOT}/configs/config_m33_v0.yaml"
