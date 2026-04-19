#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-.}"
RUN_ROOT="${2:-${PROJECT_ROOT}/runs/M33_V0_alpha_peak_robustness}"
OUT_ROOT="${RUN_ROOT}/M36e_combined_identity"

mkdir -p \
  "${OUT_ROOT}" \
  "${OUT_ROOT}/plots"

cat > "${OUT_ROOT}/combined_pair_overlap.csv" <<'CSV'
run_id,case_label_a,case_label_b,branch_a,branch_b,top_k,pair_overlap_count,pair_overlap_fraction_a,pair_overlap_fraction_b,weighted_pair_overlap,relation_type
CSV

cat > "${OUT_ROOT}/combined_class_overlap.csv" <<'CSV'
run_id,case_label_a,case_label_b,branch_a,branch_b,class_mode,top_k,class_overlap_count,class_overlap_fraction_a,class_overlap_fraction_b,weighted_class_overlap,relation_type
CSV

cat > "${OUT_ROOT}/branch_identity_summary.csv" <<'CSV'
run_id,branch_label,n_cases,mean_within_pair_overlap_top3,mean_between_pair_overlap_top3,mean_within_class_overlap_top3_delta_p,mean_between_class_overlap_top3_delta_p,mean_within_class_overlap_top3_delta_p2,mean_between_class_overlap_top3_delta_p2,pair_separability_score,delta_p_separability_score,delta_p2_separability_score,consensus_top1_pair,consensus_top1_delta_p,consensus_top1_delta_p2,consensus_top3_classes_delta_p,consensus_top3_classes_delta_p2,signature_label
CSV

cat > "${OUT_ROOT}/global_identity_summary.json" <<'JSON'
{
  "n_cases_total": 0,
  "n_branches_total": 0,
  "pair_within_overlap_top3": null,
  "pair_between_overlap_top3": null,
  "delta_p_within_overlap_top3": null,
  "delta_p_between_overlap_top3": null,
  "delta_p2_within_overlap_top3": null,
  "delta_p2_between_overlap_top3": null,
  "pair_separability_score": null,
  "delta_p_separability_score": null,
  "delta_p2_separability_score": null,
  "dominant_identity_level": null,
  "final_label": ""
}
JSON

cat > "${OUT_ROOT}/global_identity_report.md" <<'MD'
# M.3.6e Combined Branch Identity Audit

## Status
initialized
MD

echo "Initialized M.3.6e combined identity structure at: ${OUT_ROOT}"
echo "Next step:"
echo "  python ${PROJECT_ROOT}/src/m36e_combined_identity_runner.py --project-root ${PROJECT_ROOT} --config ${PROJECT_ROOT}/configs/config_m33_v0.yaml"
