#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-.}"
RUN_ROOT="${2:-${PROJECT_ROOT}/runs/M33_V0_alpha_peak_robustness}"
OUT_ROOT="${RUN_ROOT}/M38b_branch_dispersion_v2"

mkdir -p \
  "${OUT_ROOT}" \
  "${OUT_ROOT}/plots"

cat > "${OUT_ROOT}/branch_dispersion_case_table.csv" <<'CSV'
run_id,case_id,p_family,k0,sigma_k,t,v,nu,reference_mode,x_width_delta,branch_label_none_hard,branch_label_quadratic_hard,branch_label_none_nearest,branch_label_quadratic_nearest,branch_label_none_soft,branch_label_quadratic_soft,hard_branch_change_flag,nearest_branch_change_flag,soft_branch_change_flag,hard_branch_ambiguous_flag_none,hard_branch_ambiguous_flag_quadratic,dispersion_sensitive_flag,pair_migration_label
CSV

cat > "${OUT_ROOT}/branch_dispersion_match_scores.csv" <<'CSV'
run_id,case_id,side,reference_mode,dist_to_S1,dist_to_S2,dist_to_S3,score_S1,score_S2,score_S3,best_branch,second_branch,best_score,second_score,score_margin,hard_assignment_flag
CSV

cat > "${OUT_ROOT}/branch_dispersion_pair_shift.csv" <<'CSV'
run_id,case_id,reference_mode,top_k,branch_label_none,branch_label_quadratic,pair_overlap_none_vs_quadratic,weighted_pair_overlap,n_entering_pairs,n_leaving_pairs,mean_rank_shift_shared_pairs,dominant_pair_preserved_flag,pair_migration_label,identity_preserved_flag
CSV

cat > "${OUT_ROOT}/branch_dispersion_pair_migration_detail.csv" <<'CSV'
run_id,case_id,reference_mode,top_k,pair_i,pair_j,present_in_none,present_in_quadratic,rank_none,rank_quadratic,weight_none,weight_quadratic,rank_shift,weight_shift,migration_type
CSV

cat > "${OUT_ROOT}/branch_dispersion_class_shift.csv" <<'CSV'
run_id,case_id,reference_mode,class_mode,top_k,branch_label_none,branch_label_quadratic,class_overlap_none_vs_quadratic,weighted_class_shift,identity_preserved_flag
CSV

cat > "${OUT_ROOT}/branch_dispersion_branch_summary.csv" <<'CSV'
run_id,reference_mode,branch_label,n_cases,hard_preservation_rate,nearest_preservation_rate,soft_preservation_rate,hard_ambiguity_rate,mean_pair_overlap_top3,mean_pair_overlap_top5,mean_weighted_pair_overlap_top3,mean_delta_p_shift,mean_delta_p2_shift,mean_x_width_delta,dispersion_sensitivity_rate,stable_reweighting_rate,major_migration_rate,signature_label
CSV

cat > "${OUT_ROOT}/branch_dispersion_migration_matrix.csv" <<'CSV'
run_id,reference_mode,branch_from,branch_to,n_cases,fraction,mode
CSV

cat > "${OUT_ROOT}/S2_focus_summary.csv" <<'CSV'
run_id,reference_mode,n_cases_S2,hard_preservation_rate,nearest_preservation_rate,soft_preservation_rate,mean_pair_overlap_top3,mean_weighted_pair_overlap_top3,mean_delta_p_shift,mean_delta_p2_shift,mean_x_width_delta,stable_reweighting_rate,major_migration_rate,hard_ambiguity_rate,S2_sensitivity_label
CSV

cat > "${OUT_ROOT}/branch_dispersion_global_summary.json" <<'JSON'
{
  "n_cases_total": 0,
  "hard_branch_preservation_rate": 0.0,
  "nearest_branch_preservation_rate": 0.0,
  "soft_branch_preservation_rate": 0.0,
  "hard_branch_ambiguity_rate": 0.0,
  "delta_p_preservation_rate": 0.0,
  "delta_p2_preservation_rate": 0.0,
  "pair_preservation_rate": 0.0,
  "pair_overlap_top3_mean": 0.0,
  "weighted_pair_overlap_top3_mean": 0.0,
  "most_stable_identity_level": null,
  "most_dispersion_sensitive_branch": null,
  "S2_migration_mode": null,
  "final_label": ""
}
JSON

cat > "${OUT_ROOT}/branch_dispersion_report.md" <<'MD'
# M.3.8b-v2 Hard-Branch / Full-Pair Validation

## Status
initialized
MD

echo "Initialized M.3.8b-v2 branch-dispersion structure at: ${OUT_ROOT}"
echo "Next step:"
echo "  python ${PROJECT_ROOT}/src/m38b_branch_dispersion_runner_v2.py --project-root ${PROJECT_ROOT} --config ${PROJECT_ROOT}/configs/config_m33_v0.yaml"
