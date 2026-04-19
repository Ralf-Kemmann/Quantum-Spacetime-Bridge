#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-.}"
RUN_ROOT="${2:-${PROJECT_ROOT}/runs/M33_V0_alpha_peak_robustness}"
OUT_ROOT="${RUN_ROOT}/M36f_diversity_identity"

mkdir -p \
  "${OUT_ROOT}" \
  "${OUT_ROOT}/plots"

cat > "${OUT_ROOT}/diversity_case_table.csv" <<'CSV'
run_id,case_label,branch_label,t,p_family,theta,source_feature,best_alpha_source,best_sigma_p,diversity_group,group_rank,group_weight,is_group_representative,selection_mode
CSV

cat > "${OUT_ROOT}/pruned_pair_overlap.csv" <<'CSV'
run_id,case_label_a,case_label_b,branch_a,branch_b,top_k,pair_overlap_count,pair_overlap_fraction_a,pair_overlap_fraction_b,weighted_pair_overlap,relation_type
CSV

cat > "${OUT_ROOT}/pruned_class_overlap.csv" <<'CSV'
run_id,case_label_a,case_label_b,branch_a,branch_b,class_mode,top_k,class_overlap_count,class_overlap_fraction_a,class_overlap_fraction_b,weighted_class_overlap,relation_type
CSV

cat > "${OUT_ROOT}/weighted_pair_overlap.csv" <<'CSV'
run_id,case_label_a,case_label_b,branch_a,branch_b,top_k,pair_overlap_count,pair_overlap_fraction_a,pair_overlap_fraction_b,weighted_pair_overlap,case_weight_a,case_weight_b,pair_overlap_weighted_by_case,relation_type
CSV

cat > "${OUT_ROOT}/weighted_class_overlap.csv" <<'CSV'
run_id,case_label_a,case_label_b,branch_a,branch_b,class_mode,top_k,class_overlap_count,class_overlap_fraction_a,class_overlap_fraction_b,weighted_class_overlap,case_weight_a,case_weight_b,class_overlap_weighted_by_case,relation_type
CSV

cat > "${OUT_ROOT}/diversity_branch_summary.csv" <<'CSV'
run_id,mode,branch_label,n_cases_raw,n_cases_effective,mean_within_pair_overlap_top3,mean_between_pair_overlap_top3,mean_within_class_overlap_top3_delta_p,mean_between_class_overlap_top3_delta_p,mean_within_class_overlap_top3_delta_p2,mean_between_class_overlap_top3_delta_p2,pair_separability_score,delta_p_separability_score,delta_p2_separability_score,signature_label
CSV

cat > "${OUT_ROOT}/diversity_global_summary.json" <<'JSON'
{
  "n_cases_raw": 0,
  "n_cases_pruned": 0,
  "n_cases_effective_weighted": 0.0,
  "pair_separability_pruned": null,
  "delta_p_separability_pruned": null,
  "delta_p2_separability_pruned": null,
  "pair_separability_weighted": null,
  "delta_p_separability_weighted": null,
  "delta_p2_separability_weighted": null,
  "dominant_identity_level_pruned": null,
  "dominant_identity_level_weighted": null,
  "replicate_sensitivity_flag": 0,
  "final_label": ""
}
JSON

cat > "${OUT_ROOT}/diversity_global_report.md" <<'MD'
# M.3.6f Diversity-aware Combined Identity Audit

## Status
initialized
MD

echo "Initialized M.3.6f diversity-aware identity structure at: ${OUT_ROOT}"
echo "Next step:"
echo "  python ${PROJECT_ROOT}/src/m36f_diversity_identity_runner.py --project-root ${PROJECT_ROOT} --config ${PROJECT_ROOT}/configs/config_m33_v0.yaml"
