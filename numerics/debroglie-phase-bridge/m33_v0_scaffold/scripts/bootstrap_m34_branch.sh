#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-.}"
RUN_ROOT="${2:-${PROJECT_ROOT}/runs/M33_V0_alpha_peak_robustness}"
OUT_ROOT="${RUN_ROOT}/M34_branch_scan"

mkdir -p \
  "${OUT_ROOT}" \
  "${OUT_ROOT}/plots"

cat > "${OUT_ROOT}/branch_assignment.csv" <<'CSV'
run_id,t,p_family,theta,preferred_scope,preferred_alpha_coherent,preferred_coherence_score,readout_label,branch_id,branch_center,branch_left,branch_right,distance_to_branch_center,in_branch_flag,source_alpha_reference,delta_source_branch,source_link_flag
CSV

cat > "${OUT_ROOT}/branch_summary_by_condition.csv" <<'CSV'
run_id,t,p_family,theta,n_candidates,preferred_branch,preferred_alpha,preferred_score,branch_B1_flag,branch_B2_flag,branch_B3_flag,source_link_flag,branch_label
CSV

cat > "${OUT_ROOT}/branch_frequency_table.csv" <<'CSV'
run_id,aggregation_level,aggregation_key,n_total,n_B1,n_B2,n_B3,frac_B1,frac_B2,frac_B3,dominant_branch,branch_entropy
CSV

cat > "${OUT_ROOT}/branch_drift_table.csv" <<'CSV'
run_id,branch_id,p_family,theta,t_min,t_max,alpha_at_t_min,alpha_at_t_max,delta_alpha,monotonicity_flag,drift_label
CSV

cat > "${OUT_ROOT}/branch_transition_table.csv" <<'CSV'
run_id,scan_axis,group_id,step_from,step_to,branch_from,branch_to,transition_type,delta_alpha,score_from,score_to
CSV

cat > "${OUT_ROOT}/branch_source_coupling.csv" <<'CSV'
run_id,t,p_family,theta,preferred_branch,preferred_alpha,source_alpha_reference,delta_source_branch,source_feature,source_label,source_link_flag
CSV

cat > "${OUT_ROOT}/branch_summary.json" <<'JSON'
{
  "final_label": "",
  "dominant_branch": null,
  "frac_B1": null,
  "frac_B2": null,
  "frac_B3": null,
  "branch_entropy": null,
  "adjacent_jumps": null,
  "nonlocal_jumps": null,
  "source_link_frac": null
}
JSON

cat > "${OUT_ROOT}/branch_report.md" <<'MD'
# M.3.4 Branch Analysis Report

## Status
initialized
MD

echo "Initialized M.3.4 branch structure at: ${OUT_ROOT}"
echo "Next step:"
echo "  python ${PROJECT_ROOT}/src/m34_branch_runner.py --project-root ${PROJECT_ROOT} --config ${PROJECT_ROOT}/configs/config_m33_v0.yaml"
