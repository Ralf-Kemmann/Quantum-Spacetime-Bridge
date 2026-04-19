#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-.}"
RUN_ROOT="${2:-${PROJECT_ROOT}/runs/M33_V0_alpha_peak_robustness}"
OUT_ROOT="${RUN_ROOT}/M36d_auto_extend"

mkdir -p \
  "${OUT_ROOT}" \
  "${OUT_ROOT}/plots"

cat > "${OUT_ROOT}/selected_extension_cases.csv" <<'CSV'
run_id,t,p_family,theta,branch_basis,branch_label,selection_rank_within_branch,soft_overlap_score,hard_delta_alpha,nearest_branch_match_flag,soft_branch_match_flag,source_feature,best_p0,best_sigma_p,best_alpha_source,alpha_pref_readout,extension_reason,case_label
CSV

cat > "${OUT_ROOT}/skipped_missing_fit_cases.csv" <<'CSV'
run_id,t,p_family,theta,source_feature,case_label
CSV

cat > "${OUT_ROOT}/extended_pair_contributions.csv" <<'CSV'
run_id,t,p_family,theta,source_feature,best_p0,best_sigma_p,best_alpha_source,best_branch_source,alpha_pref_readout,branch_pref_readout,pair_i,pair_j,p_i,p_j,delta_p,delta_p2,pair_weight,kbar_ij,kbar_abs_ij,kbar_sign,contrib_neg,contrib_abs,contrib_signed,contrib_primary,pair_rank_primary,cumulative_primary,case_label,branch_basis,branch_label
CSV

cat > "${OUT_ROOT}/extended_pair_top_summary.csv" <<'CSV'
run_id,t,p_family,theta,source_feature,best_p0,best_sigma_p,best_alpha_source,best_branch_source,alpha_pref_readout,branch_pref_readout,n_pairs_total,top1_share,top3_share,top5_share,top10_share,effective_pair_count,dominance_label,case_label,branch_basis,branch_label
CSV

cat > "${OUT_ROOT}/extended_pair_class_summary.csv" <<'CSV'
run_id,t,p_family,theta,source_feature,class_mode,class_label,n_pairs_in_class,sum_pair_weight,sum_contrib_primary,mean_contrib_primary,max_contrib_primary,class_rank,cumulative_class_contrib,case_label,branch_basis,branch_label
CSV

cat > "${OUT_ROOT}/combined_pair_contributions.csv" <<'CSV'
run_id,t,p_family,theta,source_feature,best_p0,best_sigma_p,best_alpha_source,best_branch_source,alpha_pref_readout,branch_pref_readout,pair_i,pair_j,p_i,p_j,delta_p,delta_p2,pair_weight,kbar_ij,kbar_abs_ij,kbar_sign,contrib_neg,contrib_abs,contrib_signed,contrib_primary,pair_rank_primary,cumulative_primary,case_label,branch_basis,branch_label
CSV

cat > "${OUT_ROOT}/combined_pair_top_summary.csv" <<'CSV'
run_id,t,p_family,theta,source_feature,best_p0,best_sigma_p,best_alpha_source,best_branch_source,alpha_pref_readout,branch_pref_readout,n_pairs_total,top1_share,top3_share,top5_share,top10_share,effective_pair_count,dominance_label,case_label,branch_basis,branch_label
CSV

cat > "${OUT_ROOT}/combined_pair_class_summary.csv" <<'CSV'
run_id,t,p_family,theta,source_feature,class_mode,class_label,n_pairs_in_class,sum_pair_weight,sum_contrib_primary,mean_contrib_primary,max_contrib_primary,class_rank,cumulative_class_contrib,case_label,branch_basis,branch_label
CSV

cat > "${OUT_ROOT}/auto_extend_summary.json" <<'JSON'
{
  "target_cases_per_branch": 0,
  "already_audited_counts": {},
  "newly_selected_counts": {},
  "combined_counts": {},
  "n_new_cases": 0,
  "n_skipped_missing_fit_cases": 0,
  "selection_success": false,
  "final_label": ""
}
JSON

cat > "${OUT_ROOT}/auto_extend_report.md" <<'MD'
# M.3.6d Targeted Auto-Extend Pair Audit

## Status
initialized
MD

echo "Initialized M.3.6d auto-extend structure at: ${OUT_ROOT}"
echo "Next step:"
echo "  python ${PROJECT_ROOT}/src/m36d_auto_extend_runner_v3.py --project-root ${PROJECT_ROOT} --config ${PROJECT_ROOT}/configs/config_m33_v0.yaml"
