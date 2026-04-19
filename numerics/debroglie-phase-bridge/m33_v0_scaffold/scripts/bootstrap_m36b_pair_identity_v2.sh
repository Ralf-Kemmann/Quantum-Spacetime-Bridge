#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-.}"
RUN_ROOT="${2:-${PROJECT_ROOT}/runs/M33_V0_alpha_peak_robustness}"
OUT_ROOT="${RUN_ROOT}/M36b_pair_identity"

mkdir -p   "${OUT_ROOT}"   "${OUT_ROOT}/plots"

cat > "${OUT_ROOT}/pair_identity_comparison.csv" <<'CSV'
run_id,case_label,t,p_family,theta,source_feature,branch_label,pair_i,pair_j,p_i,p_j,delta_p,delta_p2,pair_rank_primary,contrib_primary,normalized_contrib_primary,is_top1_pair,is_top3_pair,is_top5_pair
CSV

cat > "${OUT_ROOT}/pair_overlap_summary.csv" <<'CSV'
run_id,case_label_a,case_label_b,branch_a,branch_b,top_k,pair_overlap_count,pair_overlap_fraction_a,pair_overlap_fraction_b,weighted_pair_overlap,identity_relation
CSV

cat > "${OUT_ROOT}/class_identity_comparison.csv" <<'CSV'
run_id,case_label,t,p_family,theta,source_feature,branch_label,class_mode,class_label,class_rank,sum_contrib_primary,normalized_class_contrib,is_top1_class,is_top3_class,is_top5_class
CSV

cat > "${OUT_ROOT}/class_overlap_summary.csv" <<'CSV'
run_id,case_label_a,case_label_b,branch_a,branch_b,class_mode,top_k,class_overlap_count,class_overlap_fraction_a,class_overlap_fraction_b,weighted_class_overlap,identity_relation
CSV

cat > "${OUT_ROOT}/branch_identity_signature.csv" <<'CSV'
run_id,branch_label,n_cases,dominant_pair_mode,dominant_class_mode,consensus_top1_pair,consensus_top1_delta_p,consensus_top1_delta_p2,consensus_top3_classes,within_branch_overlap,between_branch_overlap,signature_label
CSV

cat > "${OUT_ROOT}/pair_identity_summary.json" <<'JSON'
{
  "n_cases": 0,
  "mean_within_pair_overlap_top3": null,
  "mean_between_pair_overlap_top3": null,
  "strongest_class_mode": null,
  "final_label": ""
}
JSON

cat > "${OUT_ROOT}/pair_identity_report.md" <<'MD'
# M.3.6b Pair Identity Report

## Status
initialized
MD

echo "Initialized M.3.6b pair-identity structure at: ${OUT_ROOT}"
echo "Next step:"
echo "  python ${PROJECT_ROOT}/src/m36b_pair_identity_runner_v2.py --project-root ${PROJECT_ROOT} --config ${PROJECT_ROOT}/configs/config_m33_v0.yaml"
