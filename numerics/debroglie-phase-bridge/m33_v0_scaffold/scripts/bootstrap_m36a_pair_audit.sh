#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-.}"
RUN_ROOT="${2:-${PROJECT_ROOT}/runs/M33_V0_alpha_peak_robustness}"
OUT_ROOT="${RUN_ROOT}/M36a_pair_audit"

mkdir -p   "${OUT_ROOT}"   "${OUT_ROOT}/plots"

cat > "${OUT_ROOT}/pair_contributions.csv" <<'CSV'
run_id,t,p_family,theta,source_feature,best_p0,best_sigma_p,best_alpha_source,best_branch_source,alpha_pref_readout,branch_pref_readout,pair_i,pair_j,p_i,p_j,delta_p,delta_p2,pair_weight,kbar_ij,kbar_abs_ij,kbar_sign,contrib_neg,contrib_abs,contrib_signed,contrib_primary,pair_rank_primary,cumulative_primary
CSV

cat > "${OUT_ROOT}/pair_top_summary.csv" <<'CSV'
run_id,t,p_family,theta,source_feature,best_p0,best_sigma_p,best_alpha_source,best_branch_source,alpha_pref_readout,branch_pref_readout,n_pairs_total,top1_share,top3_share,top5_share,top10_share,effective_pair_count,dominance_label
CSV

cat > "${OUT_ROOT}/pair_class_summary.csv" <<'CSV'
run_id,t,p_family,theta,source_feature,class_mode,class_label,n_pairs_in_class,sum_pair_weight,sum_contrib_primary,mean_contrib_primary,max_contrib_primary,class_rank,cumulative_class_contrib
CSV

cat > "${OUT_ROOT}/pair_audit_summary.json" <<'JSON'
{
  "n_audit_cases": 0,
  "dominant_mechanism": null,
  "median_top3_share": null,
  "median_effective_pair_count": null,
  "primary_class_mode_supported": null
}
JSON

cat > "${OUT_ROOT}/pair_audit_report.md" <<'MD'
# M.3.6a Pair Audit Report

## Status
initialized
MD

echo "Initialized M.3.6a pair-audit structure at: ${OUT_ROOT}"
echo "Next step:"
echo "  python ${PROJECT_ROOT}/src/m36a_pair_audit_runner.py --project-root ${PROJECT_ROOT} --config ${PROJECT_ROOT}/configs/config_m33_v0.yaml"
