#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-.}"
RUN_ROOT="${2:-${PROJECT_ROOT}/runs/M33_V0_alpha_peak_robustness}"
OUT_ROOT="${RUN_ROOT}/M37_sigma_robustness"

mkdir -p \
  "${OUT_ROOT}" \
  "${OUT_ROOT}/plots"

cat > "${OUT_ROOT}/sigma_case_grid.csv" <<'CSV'
run_id,case_label,branch_label,mode,t,p_family,theta,source_feature,best_p0,sigma_p_base,sigma_factor,sigma_p_test,best_alpha_source,diversity_group,group_weight
CSV

cat > "${OUT_ROOT}/sigma_pair_top_summary.csv" <<'CSV'
run_id,case_label,branch_label,mode,sigma_factor,sigma_p_test,t,p_family,theta,source_feature,best_p0,sigma_p_base,best_alpha_source,diversity_group,group_weight,n_pairs_total,top1_share,top3_share,top5_share,effective_pair_count,dominance_label
CSV

cat > "${OUT_ROOT}/sigma_class_summary.csv" <<'CSV'
run_id,case_label,branch_label,mode,sigma_factor,sigma_p_test,t,p_family,theta,source_feature,best_p0,sigma_p_base,best_alpha_source,diversity_group,group_weight,class_mode,class_label,class_rank,sum_contrib_primary,normalized_class_contrib
CSV

cat > "${OUT_ROOT}/sigma_global_scores.csv" <<'CSV'
run_id,mode,sigma_factor,n_cases_effective,pair_within_overlap_top3,pair_between_overlap_top3,delta_p_within_overlap_top3,delta_p_between_overlap_top3,delta_p2_within_overlap_top3,delta_p2_between_overlap_top3,pair_separability_score,delta_p_separability_score,delta_p2_separability_score,dominant_identity_level,robust_identity_label
CSV

cat > "${OUT_ROOT}/sigma_branch_scores.csv" <<'CSV'
run_id,mode,branch_label,sigma_factor,n_cases_effective,pair_separability_score,delta_p_separability_score,delta_p2_separability_score,signature_label
CSV

cat > "${OUT_ROOT}/sigma_pair_overlap.csv" <<'CSV'
run_id,case_label_a,case_label_b,branch_a,branch_b,top_k,pair_overlap_count,pair_overlap_fraction_a,pair_overlap_fraction_b,weighted_pair_overlap,case_weight_a,case_weight_b,pair_overlap_weighted_by_case,relation_type,mode,sigma_factor
CSV

cat > "${OUT_ROOT}/sigma_class_overlap.csv" <<'CSV'
run_id,case_label_a,case_label_b,branch_a,branch_b,class_mode,top_k,class_overlap_count,class_overlap_fraction_a,class_overlap_fraction_b,weighted_class_overlap,case_weight_a,case_weight_b,class_overlap_weighted_by_case,relation_type,mode,sigma_factor
CSV

cat > "${OUT_ROOT}/sigma_robustness_summary.json" <<'JSON'
{
  "best_identity_level": null,
  "delta_p2_positive_fraction": 0.0,
  "delta_p_positive_fraction": 0.0,
  "pair_positive_fraction": 0.0,
  "sigma_robust_band_delta_p2": [],
  "sigma_collapse_threshold_pair": null,
  "replicate_sensitive_flag": 0,
  "final_label": ""
}
JSON

cat > "${OUT_ROOT}/sigma_robustness_report.md" <<'MD'
# M.3.7 Sigma Robustness Sweep

## Status
initialized
MD

echo "Initialized M.3.7 sigma robustness structure at: ${OUT_ROOT}"
echo "Next step:"
echo "  python ${PROJECT_ROOT}/src/m37_sigma_robustness_runner_v2.py --project-root ${PROJECT_ROOT} --config ${PROJECT_ROOT}/configs/config_m33_v0.yaml"
