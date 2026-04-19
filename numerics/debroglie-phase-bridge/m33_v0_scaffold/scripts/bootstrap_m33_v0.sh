#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-./m33_v0_project}"
RUN_ID="${2:-M33_V0_alpha_peak_robustness}"
RUN_ROOT="${PROJECT_ROOT}/runs/${RUN_ID}"

mkdir -p \
  "${PROJECT_ROOT}/src" \
  "${PROJECT_ROOT}/configs" \
  "${PROJECT_ROOT}/scripts" \
  "${PROJECT_ROOT}/runs" \
  "${PROJECT_ROOT}/logs" \
  "${RUN_ROOT}/logs" \
  "${RUN_ROOT}/V0_source_scan/plots" \
  "${RUN_ROOT}/M33_readout_scan/plots" \
  "${RUN_ROOT}/combined"

touch \
  "${RUN_ROOT}/logs/run.log" \
  "${RUN_ROOT}/logs/warnings.log"

cat > "${PROJECT_ROOT}/README_M33_V0.md" <<'MD'
# M33 / V0 scaffold

## Layout
- src/: python modules
- configs/: yaml configs
- scripts/: helper shell scripts
- runs/: output runs

## Expected core files
- src/config_schema.py
- src/columns_m33_v0.py
- src/m33_v0_runner.py
- configs/config_m33_v0.yaml

## Typical usage
python src/m33_v0_runner.py --project-root . --config configs/config_m33_v0.yaml
MD

cat > "${RUN_ROOT}/run_manifest.json" <<'JSON'
{
  "run_id": "",
  "tag": "",
  "timestamp_utc": "",
  "seed": 0,
  "script_version": "m33_v0_runner.py",
  "config_snapshot": "config_snapshot.yaml",
  "status": "initialized"
}
JSON

cat > "${RUN_ROOT}/config_snapshot.yaml" <<'YAML'
project:
  run_id: ""
  tag: ""
  seed: 0
  output_root: ""
YAML

cat > "${RUN_ROOT}/V0_source_scan/phase_pair_stats.csv" <<'CSV'
run_id,t,p_family,alpha,pair_i,pair_j,p_i,p_j,delta_p,E_i,E_j,delta_E,var_dphi_x,mean_dphi_x,mean_cos_dphi,mean_abs_cos_dphi,mean_sin_dphi,kbar_ij,kbar_abs_ij,kbar_sign,finite_fraction
CSV

cat > "${RUN_ROOT}/V0_source_scan/kernel_sign_stats.csv" <<'CSV'
run_id,t,p_family,alpha,n_nodes,n_pairs,I_net,I_abs,f_pos,f_neg,f_zero,mean_kpos,mean_kneg,sum_kpos,sum_kneg,lambda_max_kpos,lambda_max_kneg,lambda_max_kabs,sign_imbalance,source_peak_flag,source_feature,finite_fraction
CSV

cat > "${RUN_ROOT}/V0_source_scan/source_peak_summary.csv" <<'CSV'
run_id,t,p_family,alpha_star_source,source_feature,source_peak_type,source_peak_value,source_prominence,source_width,source_in_band_flag,t0_control_flag,source_label
CSV

cat > "${RUN_ROOT}/V0_source_scan/source_summary.json" <<'JSON'
{
  "source_hypothesis": "",
  "n_total_runs": 0,
  "n_valid_runs": 0,
  "median_alpha_star_source": null,
  "frac_source_in_band": null,
  "t0_control_pass": null,
  "dominant_source_feature": "",
  "source_label_global": ""
}
JSON

cat > "${RUN_ROOT}/M33_readout_scan/alpha_scan.csv" <<'CSV'
run_id,t,p_family,theta,alpha,kernel_mode,chi,rho_pos,rho_neg,lambda_max_pos,lambda_max_neg,lambda_max_abs,lambda2_abs,weighted_clustering_abs,natural_connectivity_abs,global_efficiency_abs,n_components_abs,finite_fraction,peak_flag_chi,peak_flag_lambda2,peak_flag_wclust
CSV

cat > "${RUN_ROOT}/M33_readout_scan/alpha_scan_summary.csv" <<'CSV'
run_id,t,p_family,theta,alpha_star_chi,alpha_star_lambda2,alpha_star_wclust,chi_peak_value,lambda2_min_value,wclust_peak_value,chi_prominence,lambda2_prominence,wclust_prominence,delta_chi_lambda2,delta_chi_wclust,readout_in_band_flag,readout_label
CSV

cat > "${RUN_ROOT}/M33_readout_scan/robustness_table.csv" <<'CSV'
run_id,t,p_family,alpha_star_chi,alpha_star_lambda2,alpha_star_wclust,delta_peak_alignment,peak_prominence_chi,peak_prominence_lambda2,peak_prominence_wclust,stability_label
CSV

cat > "${RUN_ROOT}/M33_readout_scan/readout_summary.json" <<'JSON'
{
  "median_alpha_star_chi": null,
  "median_alpha_star_lambda2": null,
  "median_alpha_star_wclust": null,
  "frac_readout_in_band": null,
  "frac_coherent": null,
  "readout_label_global": ""
}
JSON

cat > "${RUN_ROOT}/combined/source_readout_alignment.csv" <<'CSV'
run_id,t,p_family,theta,alpha_star_source,alpha_star_chi,alpha_star_lambda2,alpha_star_wclust,delta_source_chi,delta_source_lambda2,delta_source_wclust,source_peak_flag,readout_peak_flag,coherent_peak_flag,t0_control_flag,asymmetry_valid_flag,combined_label
CSV

cat > "${RUN_ROOT}/combined/combined_decision_table.csv" <<'CSV'
run_id,aggregation_level,p_family,n_valid_runs,frac_source_in_band,frac_readout_in_band,frac_coherent,median_alpha_source,median_alpha_chi,median_alpha_lambda2,median_alpha_wclust,median_delta_source_chi,median_delta_chi_lambda2,global_t0_control_pass,global_asymmetry_pass,final_decision,kill_signal
CSV

cat > "${RUN_ROOT}/combined/combined_summary.json" <<'JSON'
{
  "source_readout_link_supported": null,
  "median_delta_source_chi": null,
  "median_delta_source_lambda2": null,
  "global_t0_control_pass": null,
  "global_asymmetry_pass": null,
  "final_decision": "",
  "interpretation": ""
}
JSON

cat > "${RUN_ROOT}/combined/combined_report.md" <<'MD'
# Combined Report

## Status
initialized
MD

echo "Scaffold initialized at: ${PROJECT_ROOT}"
echo "Run root initialized at: ${RUN_ROOT}"
echo "Next step:"
echo "  python ${PROJECT_ROOT}/src/m33_v0_runner.py --project-root ${PROJECT_ROOT} --config ${PROJECT_ROOT}/configs/config_m33_v0.yaml"
