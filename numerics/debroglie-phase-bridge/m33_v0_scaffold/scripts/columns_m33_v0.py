
from __future__ import annotations

from typing import Dict, List
import pandas as pd


RUN_MANIFEST_COLUMNS: List[str] = [
    "run_id",
    "tag",
    "timestamp_utc",
    "seed",
    "script_version",
    "config_snapshot",
    "status",
]

PHASE_PAIR_STATS_COLUMNS: List[str] = [
    "run_id",
    "t",
    "p_family",
    "alpha",
    "pair_i",
    "pair_j",
    "p_i",
    "p_j",
    "delta_p",
    "E_i",
    "E_j",
    "delta_E",
    "var_dphi_x",
    "mean_dphi_x",
    "mean_cos_dphi",
    "mean_abs_cos_dphi",
    "mean_sin_dphi",
    "kbar_ij",
    "kbar_abs_ij",
    "kbar_sign",
    "finite_fraction",
]

KERNEL_SIGN_STATS_COLUMNS: List[str] = [
    "run_id",
    "t",
    "p_family",
    "alpha",
    "n_nodes",
    "n_pairs",
    "I_net",
    "I_abs",
    "f_pos",
    "f_neg",
    "f_zero",
    "mean_kpos",
    "mean_kneg",
    "sum_kpos",
    "sum_kneg",
    "lambda_max_kpos",
    "lambda_max_kneg",
    "lambda_max_kabs",
    "sign_imbalance",
    "source_peak_flag",
    "source_feature",
    "finite_fraction",
]

SOURCE_PEAK_SUMMARY_COLUMNS: List[str] = [
    "run_id",
    "t",
    "p_family",
    "alpha_star_source",
    "source_feature",
    "source_peak_type",
    "source_peak_value",
    "source_prominence",
    "source_width",
    "source_in_band_flag",
    "t0_control_flag",
    "source_label",
]

ALPHA_SCAN_COLUMNS: List[str] = [
    "run_id",
    "t",
    "p_family",
    "theta",
    "alpha",
    "kernel_mode",
    "chi",
    "rho_pos",
    "rho_neg",
    "lambda_max_pos",
    "lambda_max_neg",
    "lambda_max_abs",
    "lambda2_abs",
    "weighted_clustering_abs",
    "natural_connectivity_abs",
    "global_efficiency_abs",
    "n_components_abs",
    "finite_fraction",
    "peak_flag_chi",
    "peak_flag_lambda2",
    "peak_flag_wclust",
]

ALPHA_SCAN_SUMMARY_COLUMNS: List[str] = [
    "run_id",
    "t",
    "p_family",
    "theta",
    "alpha_star_chi",
    "alpha_star_lambda2",
    "alpha_star_wclust",
    "chi_peak_value",
    "lambda2_min_value",
    "wclust_peak_value",
    "chi_prominence",
    "lambda2_prominence",
    "wclust_prominence",
    "delta_chi_lambda2",
    "delta_chi_wclust",
    "readout_in_band_flag",
    "readout_label",
]

ROBUSTNESS_TABLE_COLUMNS: List[str] = [
    "run_id",
    "t",
    "p_family",
    "alpha_star_chi",
    "alpha_star_lambda2",
    "alpha_star_wclust",
    "delta_peak_alignment",
    "peak_prominence_chi",
    "peak_prominence_lambda2",
    "peak_prominence_wclust",
    "stability_label",
]

SOURCE_READOUT_ALIGNMENT_COLUMNS: List[str] = [
    "run_id",
    "t",
    "p_family",
    "theta",
    "alpha_star_source",
    "alpha_star_chi",
    "alpha_star_lambda2",
    "alpha_star_wclust",
    "delta_source_chi",
    "delta_source_lambda2",
    "delta_source_wclust",
    "source_peak_flag",
    "readout_peak_flag",
    "coherent_peak_flag",
    "t0_control_flag",
    "asymmetry_valid_flag",
    "combined_label",
]

COMBINED_DECISION_TABLE_COLUMNS: List[str] = [
    "run_id",
    "aggregation_level",
    "p_family",
    "n_valid_runs",
    "frac_source_in_band",
    "frac_readout_in_band",
    "frac_coherent",
    "median_alpha_source",
    "median_alpha_chi",
    "median_alpha_lambda2",
    "median_alpha_wclust",
    "median_delta_source_chi",
    "median_delta_chi_lambda2",
    "global_t0_control_pass",
    "global_asymmetry_pass",
    "final_decision",
    "kill_signal",
]

CSV_SCHEMAS: Dict[str, List[str]] = {
    "phase_pair_stats.csv": PHASE_PAIR_STATS_COLUMNS,
    "kernel_sign_stats.csv": KERNEL_SIGN_STATS_COLUMNS,
    "source_peak_summary.csv": SOURCE_PEAK_SUMMARY_COLUMNS,
    "alpha_scan.csv": ALPHA_SCAN_COLUMNS,
    "alpha_scan_summary.csv": ALPHA_SCAN_SUMMARY_COLUMNS,
    "robustness_table.csv": ROBUSTNESS_TABLE_COLUMNS,
    "source_readout_alignment.csv": SOURCE_READOUT_ALIGNMENT_COLUMNS,
    "combined_decision_table.csv": COMBINED_DECISION_TABLE_COLUMNS,
}


def empty_df(columns: List[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=columns)


def schema_df(name: str) -> pd.DataFrame:
    if name not in CSV_SCHEMAS:
        raise KeyError(f"Unknown schema name: {name}")
    return empty_df(CSV_SCHEMAS[name])
