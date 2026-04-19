#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-.}"
RUN_ROOT="${2:-${PROJECT_ROOT}/runs/M33_V0_alpha_peak_robustness}"
OUT_ROOT="${RUN_ROOT}/M36c_branch_expanded"

mkdir -p   "${OUT_ROOT}"   "${OUT_ROOT}/plots"

cat > "${OUT_ROOT}/selected_branch_cases.csv" <<'CSV'
run_id,t,p_family,theta,selection_mode,branch_basis,branch_label,selection_rank,nearest_branch_match_flag,soft_branch_match_flag,soft_overlap_score,hard_delta_alpha,source_feature,best_p0,best_sigma_p,best_alpha_source,alpha_pref_readout,case_label
CSV

cat > "${OUT_ROOT}/branch_pair_identity.csv" <<'CSV'
run_id,case_label,branch_basis,branch_label,t,p_family,theta,source_feature,pair_i,pair_j,p_i,p_j,delta_p,delta_p2,pair_rank_primary,contrib_primary,normalized_contrib_primary,is_top1_pair,is_top3_pair,is_top5_pair
CSV

cat > "${OUT_ROOT}/branch_pair_overlap.csv" <<'CSV'
run_id,case_label_a,case_label_b,branch_a,branch_b,top_k,pair_overlap_count,pair_overlap_fraction_a,pair_overlap_fraction_b,weighted_pair_overlap,relation_type
CSV

cat > "${OUT_ROOT}/branch_class_identity.csv" <<'CSV'
run_id,case_label,branch_basis,branch_label,t,p_family,theta,source_feature,class_mode,class_label,class_rank,sum_contrib_primary,normalized_class_contrib,is_top1_class,is_top3_class,is_top5_class
CSV

cat > "${OUT_ROOT}/branch_class_overlap.csv" <<'CSV'
run_id,case_label_a,case_label_b,branch_a,branch_b,class_mode,top_k,class_overlap_count,class_overlap_fraction_a,class_overlap_fraction_b,weighted_class_overlap,relation_type
CSV

cat > "${OUT_ROOT}/branch_identity_summary.csv" <<'CSV'
run_id,branch_basis,branch_label,n_cases,mean_within_pair_overlap_top3,mean_within_class_overlap_top3_delta_p,mean_within_class_overlap_top3_delta_p2,consensus_top1_pair,consensus_top1_delta_p,consensus_top1_delta_p2,consensus_top3_classes_delta_p,consensus_top3_classes_delta_p2,signature_label
CSV

cat > "${OUT_ROOT}/global_identity_summary.json" <<'JSON'
{
  "n_selected_cases": 0,
  "n_selected_branches": 0,
  "pair_within_overlap_top3": null,
  "pair_between_overlap_top3": null,
  "delta_p_within_overlap_top3": null,
  "delta_p_between_overlap_top3": null,
  "delta_p2_within_overlap_top3": null,
  "delta_p2_between_overlap_top3": null,
  "pair_separability_score": null,
  "delta_p_separability_score": null,
  "delta_p2_separability_score": null,
  "final_label": ""
}
JSON

cat > "${OUT_ROOT}/global_identity_report.md" <<'MD'
# M.3.6c Branch-conditioned Expanded Audit

## Status
initialized
MD

echo "Initialized M.3.6c branch-expanded structure at: ${OUT_ROOT}"
echo "Next step:"
echo "  python ${PROJECT_ROOT}/src/m36c_branch_expanded_runner_v2.py --project-root ${PROJECT_ROOT} --config ${PROJECT_ROOT}/configs/config_m33_v0.yaml"
