#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-.}"
RUN_ROOT="${2:-${PROJECT_ROOT}/runs/M33_V0_alpha_peak_robustness}"
OUT_ROOT="${RUN_ROOT}/M38b_branch_dispersion"

mkdir -p \
  "${OUT_ROOT}" \
  "${OUT_ROOT}/plots"

cat > "${OUT_ROOT}/branch_dispersion_case_table.csv" <<'CSV'
run_id,case_id,p_family,k0,sigma_k,t,v,nu,dispersion_mode,reference_mode,branch_label_none,branch_label_quadratic,nearest_branch_none,nearest_branch_quadratic,soft_branch_none,soft_branch_quadratic,hard_branch_change_flag,nearest_branch_change_flag,soft_branch_change_flag,x_width_delta,dispersion_sensitive_flag
CSV

cat > "${OUT_ROOT}/branch_dispersion_match_scores.csv" <<'CSV'
run_id,case_id,dispersion_mode,reference_mode,branch_candidate,dist_to_S1,dist_to_S2,dist_to_S3,soft_overlap_S1,soft_overlap_S2,soft_overlap_S3,best_branch,best_branch_score
CSV

cat > "${OUT_ROOT}/branch_dispersion_class_shift.csv" <<'CSV'
run_id,case_id,reference_mode,class_mode,top_k,branch_label_none,branch_label_quadratic,class_overlap_none_vs_quadratic,weighted_class_shift,identity_preserved_flag
CSV

cat > "${OUT_ROOT}/branch_dispersion_pair_shift.csv" <<'CSV'
run_id,case_id,reference_mode,top_k,branch_label_none,branch_label_quadratic,pair_overlap_none_vs_quadratic,weighted_pair_shift,identity_preserved_flag
CSV

cat > "${OUT_ROOT}/branch_dispersion_branch_summary.csv" <<'CSV'
run_id,reference_mode,branch_label,n_cases,hard_preservation_rate,nearest_preservation_rate,soft_preservation_rate,mean_delta_p_shift,mean_delta_p2_shift,mean_pair_shift,mean_x_width_delta,dispersion_sensitivity_rate,signature_label
CSV

cat > "${OUT_ROOT}/branch_dispersion_global_summary.json" <<'JSON'
{
  "n_cases_total": 0,
  "hard_branch_preservation_rate": 0.0,
  "nearest_branch_preservation_rate": 0.0,
  "soft_branch_preservation_rate": 0.0,
  "delta_p_preservation_rate": 0.0,
  "delta_p2_preservation_rate": 0.0,
  "pair_preservation_rate": 0.0,
  "most_stable_identity_level": null,
  "most_dispersion_sensitive_branch": null,
  "final_label": ""
}
JSON

cat > "${OUT_ROOT}/branch_dispersion_report.md" <<'MD'
# M.3.8b Branch-Coupled Dispersion Test

## Status
initialized
MD

echo "Initialized M.3.8b branch-dispersion structure at: ${OUT_ROOT}"
echo "Next step:"
echo "  python ${PROJECT_ROOT}/src/m38b_branch_dispersion_runner.py --project-root ${PROJECT_ROOT} --config ${PROJECT_ROOT}/configs/config_m33_v0.yaml"
