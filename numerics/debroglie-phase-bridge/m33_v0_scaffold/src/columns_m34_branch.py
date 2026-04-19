from __future__ import annotations

from typing import Dict, List
import pandas as pd


BRANCH_ASSIGNMENT_COLUMNS: List[str] = [
    "run_id",
    "t",
    "p_family",
    "theta",
    "preferred_scope",
    "preferred_alpha_coherent",
    "preferred_coherence_score",
    "readout_label",
    "branch_id",
    "branch_center",
    "branch_left",
    "branch_right",
    "distance_to_branch_center",
    "in_branch_flag",
    "source_alpha_reference",
    "delta_source_branch",
    "source_link_flag",
]

BRANCH_SUMMARY_BY_CONDITION_COLUMNS: List[str] = [
    "run_id",
    "t",
    "p_family",
    "theta",
    "n_candidates",
    "preferred_branch",
    "preferred_alpha",
    "preferred_score",
    "branch_B1_flag",
    "branch_B2_flag",
    "branch_B3_flag",
    "source_link_flag",
    "branch_label",
]

BRANCH_FREQUENCY_TABLE_COLUMNS: List[str] = [
    "run_id",
    "aggregation_level",
    "aggregation_key",
    "n_total",
    "n_B1",
    "n_B2",
    "n_B3",
    "frac_B1",
    "frac_B2",
    "frac_B3",
    "dominant_branch",
    "branch_entropy",
]

BRANCH_DRIFT_TABLE_COLUMNS: List[str] = [
    "run_id",
    "branch_id",
    "p_family",
    "theta",
    "t_min",
    "t_max",
    "alpha_at_t_min",
    "alpha_at_t_max",
    "delta_alpha",
    "monotonicity_flag",
    "drift_label",
]

BRANCH_TRANSITION_TABLE_COLUMNS: List[str] = [
    "run_id",
    "scan_axis",
    "group_id",
    "step_from",
    "step_to",
    "branch_from",
    "branch_to",
    "transition_type",
    "delta_alpha",
    "score_from",
    "score_to",
]

BRANCH_SOURCE_COUPLING_COLUMNS: List[str] = [
    "run_id",
    "t",
    "p_family",
    "theta",
    "preferred_branch",
    "preferred_alpha",
    "source_alpha_reference",
    "delta_source_branch",
    "source_feature",
    "source_label",
    "source_link_flag",
]

CSV_SCHEMAS: Dict[str, List[str]] = {
    "branch_assignment.csv": BRANCH_ASSIGNMENT_COLUMNS,
    "branch_summary_by_condition.csv": BRANCH_SUMMARY_BY_CONDITION_COLUMNS,
    "branch_frequency_table.csv": BRANCH_FREQUENCY_TABLE_COLUMNS,
    "branch_drift_table.csv": BRANCH_DRIFT_TABLE_COLUMNS,
    "branch_transition_table.csv": BRANCH_TRANSITION_TABLE_COLUMNS,
    "branch_source_coupling.csv": BRANCH_SOURCE_COUPLING_COLUMNS,
}


def empty_df(columns: List[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=columns)


def schema_df(name: str) -> pd.DataFrame:
    if name not in CSV_SCHEMAS:
        raise KeyError(f"Unknown schema name: {name}")
    return empty_df(CSV_SCHEMAS[name])
