from __future__ import annotations

from typing import Dict, List
import pandas as pd


SOURCE_CURVE_GRID_COLUMNS: List[str] = [
    "run_id",
    "t",
    "p_family",
    "theta",
    "packet_model",
    "source_feature",
    "p0",
    "sigma_p",
    "alpha",
    "source_curve_value",
]

SOURCE_CANDIDATE_GRID_COLUMNS: List[str] = [
    "run_id",
    "t",
    "p_family",
    "theta",
    "packet_model",
    "source_feature",
    "p0",
    "sigma_p",
    "alpha_candidate",
    "candidate_value",
    "candidate_prominence",
    "source_branch_id",
    "source_branch_center",
    "delta_to_branch_center",
]

PACKET_FIT_GRID_COLUMNS: List[str] = [
    "run_id",
    "t",
    "p_family",
    "theta",
    "packet_model",
    "source_feature",
    "p0",
    "sigma_p",
    "alpha_pref_source_model",
    "branch_pref_source_model",
    "source_score_model",
    "alpha_pref_readout",
    "branch_pref_readout",
    "readout_score",
    "delta_alpha",
    "branch_match_flag",
    "alpha_match_flag",
    "loss_total",
]

PACKET_FIT_BEST_COLUMNS: List[str] = [
    "run_id",
    "t",
    "p_family",
    "theta",
    "packet_model",
    "source_feature",
    "best_p0",
    "best_sigma_p",
    "best_alpha_source",
    "best_branch_source",
    "alpha_pref_readout",
    "branch_pref_readout",
    "delta_alpha",
    "branch_match_flag",
    "alpha_match_flag",
    "best_loss_total",
    "fit_label",
]

PACKET_FREQUENCY_TABLE_COLUMNS: List[str] = [
    "run_id",
    "aggregation_level",
    "aggregation_key",
    "n_total",
    "n_S1",
    "n_S2",
    "n_S3",
    "frac_S1",
    "frac_S2",
    "frac_S3",
    "dominant_source_branch",
    "source_branch_entropy",
]

CSV_SCHEMAS: Dict[str, List[str]] = {
    "source_curve_grid.csv": SOURCE_CURVE_GRID_COLUMNS,
    "source_candidate_grid.csv": SOURCE_CANDIDATE_GRID_COLUMNS,
    "packet_fit_grid.csv": PACKET_FIT_GRID_COLUMNS,
    "packet_fit_best.csv": PACKET_FIT_BEST_COLUMNS,
    "packet_frequency_table.csv": PACKET_FREQUENCY_TABLE_COLUMNS,
}


def empty_df(columns: List[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=columns)


def schema_df(name: str) -> pd.DataFrame:
    if name not in CSV_SCHEMAS:
        raise KeyError(f"Unknown schema name: {name}")
    return empty_df(CSV_SCHEMAS[name])
