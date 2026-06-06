#!/usr/bin/env python3
"""QSB-SHAPIROMART20 within-context continuous confounder test.

This block audits the SHAPIROMART18/19 pattern against construction,
context, observation-file, continuous-distance, and coarse signal controls.
No Shapiro delay, timing residual, model fit, or physical interpretation is
performed.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


RESEARCH_BLOCK = "QSB-SHAPIROMART20"
EXPECTED_ROWS = 7419
PRIMARY_THRESHOLD = 0.05
SECONDARY_THRESHOLD = 0.15
DEFAULT_PERMUTATIONS = 2000
DEFAULT_RANDOM_SEED = 20260606
DEFAULT_MINIMUM_CLUSTER_COUNT = 20
DEFAULT_MINIMUM_GROUP_COUNT = 30
SIGNAL_FREQUENCY_CALIPER_MHZ = 20.0

ROOT = Path(__file__).resolve().parents[1]
SHAPIROMART11_DIR = ROOT / "runs/QSB-SHAPIROMART/SHAPIROMART11_CONTROLLED_PINT_RECONSTRUCTION"
SHAPIROMART15_DIR = ROOT / "runs/QSB-SHAPIROMART/SHAPIROMART15_ROW_LEVEL_CONTEXT_ENRICHMENT"
SHAPIROMART17_DIR = (
    ROOT
    / "runs/QSB-SHAPIROMART/SHAPIROMART17_THRESHOLD_CONSOLIDATION_EXPOSURE_PREPARATION"
)
SHAPIROMART18_DIR = (
    ROOT / "runs/QSB-SHAPIROMART/SHAPIROMART18_EXPOSURE_GROUP_FINGERPRINT_COMPARISON"
)
SHAPIROMART19_DIR = (
    ROOT
    / "runs/QSB-SHAPIROMART/SHAPIROMART19_FINGERPRINT_DIMENSION_SEMANTICS_SPECIFICITY"
)
DEFAULT_OUTPUT_DIR = (
    ROOT
    / "runs/QSB-SHAPIROMART/SHAPIROMART20_WITHIN_CONTEXT_CONTINUOUS_GEOMETRY_CONFOUNDER_TEST"
)

OUTPUT_FILES = [
    "shapiromart20_readout.md",
    "shapiromart20_summary.json",
    "shapiromart20_circularity_assessment.csv",
    "shapiromart20_context_group_contingency.csv",
    "shapiromart20_cluster_structure_inventory.csv",
    "shapiromart20_continuous_geometry_associations.csv",
    "shapiromart20_within_context_matched_comparison.csv",
    "shapiromart20_blocked_permutation_results.csv",
    "shapiromart20_negative_control_sensitivity.csv",
    "shapiromart20_finer_observable_inventory.csv",
    "shapiromart20_conventional_explanation_matrix.csv",
    "shapiromart20_final_status.csv",
]

TARGETS = [
    ("observing_frequency_mhz", "observing frequency / band"),
    ("signal_value_primary", "SNR"),
    ("signal_value_secondary", "Flux"),
]

CIRCULARITY_FIELDS = [
    "analyzed_dimension",
    "upstream_dependency",
    "group_definition_dependency",
    "mathematical_relation",
    "independence_status",
    "construction_expected_fraction_or_status",
    "additional_information_after_control",
    "circularity_status",
    "implication",
    "notes",
]

CONTINGENCY_FIELDS = [
    "threshold_role",
    "threshold_value",
    "context_name",
    "group_name",
    "observed_count",
    "expected_count",
    "row_fraction",
    "column_fraction",
    "standardized_residual",
    "cramers_v",
    "independence_test_statistic",
    "independence_test_pvalue",
    "descriptive_dependence_status",
    "notes",
]

CLUSTER_FIELDS = [
    "cluster_candidate",
    "source_field",
    "source_artifact",
    "unique_cluster_count",
    "missing_count",
    "minimum_cluster_size",
    "median_cluster_size",
    "maximum_cluster_size",
    "mean_cluster_size",
    "cluster_suitability",
    "selected_as_primary_cluster",
    "limitation",
    "notes",
]

CONTINUOUS_FIELDS = [
    "target_variable",
    "analysis_scope",
    "context_name",
    "phase_side",
    "model_type",
    "predictor",
    "count",
    "cluster_key",
    "association_measure",
    "association_value",
    "standard_error",
    "clustered_standard_error",
    "ci_lower",
    "ci_upper",
    "monotonicity_status",
    "direction",
    "context_consistency_status",
    "side_consistency_status",
    "continuous_association_status",
    "notes",
]

MATCHED_FIELDS = [
    "target_variable",
    "context_name",
    "matching_block",
    "matching_variables",
    "caliper_definition",
    "matched_set_count",
    "matched_inside_count",
    "matched_outside_count",
    "unmatched_inside_count",
    "unmatched_outside_count",
    "balance_status",
    "mean_difference",
    "median_difference",
    "standardized_effect",
    "robust_effect",
    "matched_analysis_status",
    "notes",
]

PERMUTATION_FIELDS = [
    "target_variable",
    "analysis_scope",
    "block_definition",
    "permutation_scheme",
    "observed_statistic",
    "permutation_mean",
    "permutation_standard_deviation",
    "permutation_ci_lower",
    "permutation_ci_upper",
    "tail_fraction",
    "replicate_count",
    "random_seed",
    "permutation_validity",
    "permutation_result_status",
    "notes",
]

NEGATIVE_FIELDS = [
    "signal_dimension",
    "measurement_role",
    "calibration_status",
    "context_comparability",
    "frequency_dependence",
    "detects_global_amplitude_change",
    "detects_profile_shape_change",
    "detects_scattering_change",
    "detects_polarization_change",
    "detects_timing_residual_change",
    "current_null_status",
    "negative_control_status",
    "interpretation_limit",
    "notes",
]

OBSERVABLE_FIELDS = [
    "observable_id",
    "observable_name",
    "source_artifact",
    "source_field",
    "unit",
    "row_level_available",
    "available_row_count",
    "context_comparable",
    "independent_from_group_construction",
    "diagnostic_relevance",
    "semantic_status",
    "readiness_status",
    "main_gap",
    "notes",
]

EXPLANATION_FIELDS = [
    "observed_pattern",
    "conventional_explanation",
    "supporting_evidence",
    "contradicting_evidence",
    "test_performed",
    "test_result",
    "explanation_status",
    "residual_open_question",
    "notes",
]

FINAL_FIELDS = [
    "research_block",
    "input_rows",
    "circularity_assessment_completed",
    "toa_mjd_circularity_status",
    "context_group_dependence_assessed",
    "cluster_structure_assessed",
    "primary_cluster_key",
    "continuous_geometry_analysis_completed",
    "within_context_analysis_completed",
    "matched_analysis_completed",
    "blocked_permutation_completed",
    "snr_flux_sensitivity_assessed",
    "finer_observable_inventory_completed",
    "conventional_explanation_assessed",
    "current_pattern_explanation_status",
    "residual_nontrivial_association_found",
    "timing_residual_analysis_performed",
    "shapiro_delay_calculated",
    "timing_model_fit_performed",
    "model_parameters_modified",
    "physical_interpretation_performed",
    "qsb_claim_made",
    "database_access",
    "database_modified",
    "additional_gate_created",
    "final_status",
    "recommended_next_action",
    "limitations",
]


class ControlledStop(RuntimeError):
    """Raised when a required input or validation check fails."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SHAPIROMART20 confounder test.")
    parser.add_argument(
        "--phase-input",
        type=Path,
        default=SHAPIROMART11_DIR / "shapiromart11_toa_orbital_phase.csv",
    )
    parser.add_argument(
        "--enriched-context-input",
        type=Path,
        default=SHAPIROMART15_DIR / "shapiromart15_enriched_phase_geometry.csv",
    )
    parser.add_argument(
        "--prepared-groups-input",
        type=Path,
        default=SHAPIROMART17_DIR / "shapiromart17_prepared_exposure_groups.csv",
    )
    parser.add_argument("--shapiromart18-dir", type=Path, default=SHAPIROMART18_DIR)
    parser.add_argument("--shapiromart19-dir", type=Path, default=SHAPIROMART19_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--cluster-key", default="source_filename_name")
    parser.add_argument("--permutation-replicates", type=int, default=DEFAULT_PERMUTATIONS)
    parser.add_argument("--random-seed", type=int, default=DEFAULT_RANDOM_SEED)
    parser.add_argument("--minimum-cluster-count", type=int, default=DEFAULT_MINIMUM_CLUSTER_COUNT)
    parser.add_argument("--minimum-group-count", type=int, default=DEFAULT_MINIMUM_GROUP_COUNT)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not math.isfinite(number):
        return ""
    return format(number, ".12g")


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not path.exists():
        raise ControlledStop(f"Required input missing: {rel(path)}")
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        return rows, list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ControlledStop(f"Required JSON input missing: {rel(path)}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def to_float(value: Any, name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ControlledStop(f"Invalid numeric value for {name}: {value!r}") from exc
    if not math.isfinite(number):
        raise ControlledStop(f"Non-finite numeric value for {name}: {value!r}")
    return number


def parse_flags(text: str) -> dict[str, str]:
    try:
        value = ast.literal_eval(text)
    except (SyntaxError, ValueError) as exc:
        raise ControlledStop("Unable to parse SHAPIROMART11 source flags.") from exc
    if not isinstance(value, dict):
        raise ControlledStop("SHAPIROMART11 source flags are not a dictionary.")
    return {str(k): str(v) for k, v in value.items()}


def prepare_output_dir(args: argparse.Namespace) -> None:
    if args.output_dir.exists():
        existing = [path for path in args.output_dir.iterdir() if path.is_file()]
        if existing and not args.overwrite:
            raise ControlledStop(f"Output directory already has files: {rel(args.output_dir)}")
    args.output_dir.mkdir(parents=True, exist_ok=True)


def load_inputs(args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    phase_rows, _ = read_csv(args.phase_input)
    context_rows, _ = read_csv(args.enriched_context_input)
    group_rows, _ = read_csv(args.prepared_groups_input)
    if len(phase_rows) != EXPECTED_ROWS or len(context_rows) != EXPECTED_ROWS or len(group_rows) != EXPECTED_ROWS:
        raise ControlledStop("Expected 7419 rows in phase, context, and group inputs.")

    context_by_index = {row["source_row_index"]: row for row in context_rows}
    group_by_index = {row["source_row_index"]: row for row in group_rows}
    if set(context_by_index) != set(group_by_index):
        raise ControlledStop("Context and group source_row_index keys do not match.")

    joined: list[dict[str, Any]] = []
    for row in phase_rows:
        source_index = row["source_row_index"]
        if source_index not in context_by_index or source_index not in group_by_index:
            raise ControlledStop("Phase input source_row_index is not fully matched.")
        flags = parse_flags(row["source_filename"])
        context = context_by_index[source_index]
        group = group_by_index[source_index]
        primary_threshold = to_float(group["primary_threshold"], "primary_threshold")
        secondary_threshold = to_float(group["secondary_threshold"], "secondary_threshold")
        if not math.isclose(primary_threshold, PRIMARY_THRESHOLD, rel_tol=0.0, abs_tol=1e-12):
            raise ControlledStop("Primary threshold differs from the fixed SHAPIROMART17 value.")
        if not math.isclose(secondary_threshold, SECONDARY_THRESHOLD, rel_tol=0.0, abs_tol=1e-12):
            raise ControlledStop("Secondary threshold differs from the fixed SHAPIROMART17 value.")
        signed = to_float(group["signed_phase_offset"], "signed_phase_offset")
        phase_side = "pre_conjunction_side" if signed < 0 else "post_conjunction_side"
        joined_row = {
            "source_row_index": int(source_index),
            "source_filename_name": flags.get("name", ""),
            "observatory": row["observatory"],
            "receiver": context["receiver"],
            "backend": context["backend"],
            "context_name": context["context_name"],
            "receiver_backend_context": f"{context['receiver']} / {context['backend']}",
            "observing_frequency_mhz": to_float(row["observing_frequency_mhz"], "observing_frequency_mhz"),
            "toa_mjd_file": to_float(row["toa_mjd_file"], "toa_mjd_file"),
            "processed_time_value": to_float(row["processed_time_value"], "processed_time_value"),
            "integer_mjd_day": int(math.floor(to_float(row["toa_mjd_file"], "toa_mjd_file"))),
            "orbital_phase": to_float(group["orbital_phase"], "orbital_phase"),
            "signed_phase_offset": signed,
            "absolute_phase_distance": to_float(group["absolute_phase_distance"], "absolute_phase_distance"),
            "phase_side": phase_side,
            "primary_group": group["primary_group"],
            "secondary_group": group["secondary_group"],
            "source_flag_fe": flags.get("fe", ""),
            "source_flag_be": flags.get("be", ""),
            "source_flag_f": flags.get("f", ""),
            "source_flag_proc": flags.get("proc", ""),
            "source_flag_pta": flags.get("pta", ""),
            "source_flag_ver": flags.get("ver", ""),
            "source_flag_tmplt": flags.get("tmplt", ""),
            "source_flag_bw": safe_float(flags.get("bw")),
            "source_flag_tobs": safe_float(flags.get("tobs")),
            "source_flag_gof": safe_float(flags.get("gof")),
            "source_flag_nbin": safe_float(flags.get("nbin")),
            "source_flag_nch": safe_float(flags.get("nch")),
            "source_flag_chan": safe_float(flags.get("chan")),
            "source_flag_subint": safe_float(flags.get("subint")),
            "signal_value_primary": safe_float(flags.get("snr")),
            "source_flag_wt": safe_float(flags.get("wt")),
            "signal_value_secondary": safe_float(flags.get("flux")),
            "source_flag_fluxe": safe_float(flags.get("fluxe")),
        }
        expected_primary = (
            "inside_primary_threshold"
            if joined_row["absolute_phase_distance"] <= PRIMARY_THRESHOLD
            else "outside_primary_threshold"
        )
        expected_secondary = (
            "inside_secondary_threshold"
            if joined_row["absolute_phase_distance"] <= SECONDARY_THRESHOLD
            else "outside_secondary_threshold"
        )
        if joined_row["primary_group"] != expected_primary or joined_row["secondary_group"] != expected_secondary:
            raise ControlledStop("Fixed group assignment does not match absolute_phase_distance.")
        joined.append(joined_row)
    if len(joined) != EXPECTED_ROWS or len({row["source_row_index"] for row in joined}) != EXPECTED_ROWS:
        raise ControlledStop("Joined rows are not complete and unique.")

    metadata = {
        "shapiromart18_summary": read_json(args.shapiromart18_dir / "shapiromart18_summary.json"),
        "shapiromart19_summary": read_json(args.shapiromart19_dir / "shapiromart19_summary.json"),
        "shapiromart19_final": read_csv(args.shapiromart19_dir / "shapiromart19_final_status.csv")[0],
        "shapiromart18_final": read_csv(args.shapiromart18_dir / "shapiromart18_final_status.csv")[0],
    }
    return joined, metadata


def safe_float(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return math.nan
    return number if math.isfinite(number) else math.nan


def values(rows: list[dict[str, Any]], field: str) -> np.ndarray:
    return np.asarray([float(row[field]) for row in rows if math.isfinite(float(row[field]))], dtype=float)


def rankdata(data: np.ndarray) -> np.ndarray:
    order = np.argsort(data, kind="mergesort")
    sorted_values = data[order]
    ranks = np.empty(data.size, dtype=float)
    start = 0
    while start < data.size:
        end = start + 1
        while end < data.size and sorted_values[end] == sorted_values[start]:
            end += 1
        ranks[order[start:end]] = (start + 1 + end) / 2.0
        start = end
    return ranks


def pearson(x: np.ndarray, y: np.ndarray) -> float:
    if x.size < 2 or y.size < 2:
        return math.nan
    x0 = x - np.mean(x)
    y0 = y - np.mean(y)
    denom = math.sqrt(float(np.sum(x0 * x0) * np.sum(y0 * y0)))
    if denom <= 0:
        return math.nan
    return float(np.sum(x0 * y0) / denom)


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    if x.size < 2 or y.size < 2:
        return math.nan
    return pearson(rankdata(x), rankdata(y))


def slope_and_se(
    x: np.ndarray, y: np.ndarray, clusters: list[str] | None = None
) -> tuple[float, float, float, float, float]:
    if x.size < 3 or y.size < 3:
        return math.nan, math.nan, math.nan, math.nan, math.nan
    design = np.column_stack([np.ones(x.size), x])
    beta, *_ = np.linalg.lstsq(design, y, rcond=None)
    residuals = y - design @ beta
    xtx_inv = np.linalg.inv(design.T @ design)
    sigma2 = float(np.sum(residuals * residuals) / max(1, x.size - 2))
    cov = sigma2 * xtx_inv
    se = math.sqrt(float(cov[1, 1])) if cov[1, 1] >= 0 else math.nan
    cluster_se = math.nan
    if clusters is not None:
        meat = np.zeros((2, 2), dtype=float)
        by_cluster: dict[str, list[int]] = defaultdict(list)
        for idx, cluster in enumerate(clusters):
            by_cluster[cluster].append(idx)
        if len(by_cluster) > 1:
            for indices in by_cluster.values():
                xg = design[indices, :]
                eg = residuals[indices]
                score = xg.T @ eg
                meat += np.outer(score, score)
            scale = (len(by_cluster) / (len(by_cluster) - 1)) * ((x.size - 1) / max(1, x.size - 2))
            cluster_cov = scale * xtx_inv @ meat @ xtx_inv
            cluster_se = math.sqrt(float(cluster_cov[1, 1])) if cluster_cov[1, 1] >= 0 else math.nan
    chosen_se = cluster_se if math.isfinite(cluster_se) else se
    lower = float(beta[1] - 1.96 * chosen_se) if math.isfinite(chosen_se) else math.nan
    upper = float(beta[1] + 1.96 * chosen_se) if math.isfinite(chosen_se) else math.nan
    return float(beta[1]), se, cluster_se, lower, upper


def pooled_sd(a: np.ndarray, b: np.ndarray) -> float:
    if a.size < 2 or b.size < 2:
        return math.nan
    denom = a.size + b.size - 2
    if denom <= 0:
        return math.nan
    variance = (((a.size - 1) * np.var(a, ddof=1)) + ((b.size - 1) * np.var(b, ddof=1))) / denom
    return math.sqrt(float(variance)) if variance > 0 else math.nan


def standardized_mean_difference(a: np.ndarray, b: np.ndarray) -> float:
    scale = pooled_sd(a, b)
    if not math.isfinite(scale) or scale <= 0:
        return math.nan
    return (float(np.mean(a)) - float(np.mean(b))) / scale


def robust_pair_effect(differences: np.ndarray) -> float:
    if differences.size < 2:
        return math.nan
    q1, q3 = np.quantile(differences, [0.25, 0.75])
    scale = (q3 - q1) / 1.349
    if not math.isfinite(scale) or scale <= 0:
        return math.nan
    return float(np.median(differences)) / scale


def direction(value: float, floor: float = 1.0e-12) -> str:
    if not math.isfinite(value):
        return "not_computed"
    if abs(value) <= floor:
        return "near_zero"
    return "positive" if value > 0 else "negative"


def association_status(value: float) -> str:
    if not math.isfinite(value):
        return "insufficient_count"
    magnitude = abs(value)
    if magnitude < 0.05:
        return "no_material_continuous_association"
    if magnitude < 0.15:
        return "weak_continuous_association"
    if magnitude < 0.30:
        return "moderate_continuous_association"
    return "strong_continuous_association"


def circularity_assessment(rows: list[dict[str, Any]], cluster_key: str) -> list[dict[str, Any]]:
    total_spearman = spearman(values(rows, "toa_mjd_file"), values(rows, "absolute_phase_distance"))
    by_cluster = []
    for cluster, selected in group_rows(rows, cluster_key).items():
        if len(selected) >= 3:
            local = spearman(values(selected, "toa_mjd_file"), values(selected, "absolute_phase_distance"))
            if math.isfinite(local):
                by_cluster.append(local)
    cluster_median = float(np.median(np.asarray(by_cluster))) if by_cluster else math.nan
    return [
        {
            "analyzed_dimension": "coordinate_secondary_TOA_MJD",
            "upstream_dependency": "TOA_MJD -> PINT processed time -> orbital_phase -> signed_phase_offset -> absolute_phase_distance",
            "group_definition_dependency": "primary and secondary groups are deterministic functions of absolute_phase_distance",
            "mathematical_relation": "periodic modulo mapping from model-consistent TOA to binary orbital phase, then distance to superior-conjunction phase",
            "independence_status": "not_independent_of_group_definition",
            "construction_expected_fraction_or_status": "largely_construction_expected",
            "additional_information_after_control": f"overall_spearman_TOA_abs_distance={fmt(total_spearman)}; median_within_{cluster_key}_spearman={fmt(cluster_median)}",
            "circularity_status": "largely_construction_expected",
            "implication": "TOA_MJD should be treated as construction and scheduling context, not as an independent signal outcome.",
            "notes": "Permutation does not treat TOA_MJD as a permuted target because its relation to phase is deterministic by construction.",
        }
    ]


def group_rows(rows: list[dict[str, Any]], field: str) -> dict[str, list[dict[str, Any]]]:
    output: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        output[str(row[field])].append(row)
    return output


def contingency_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    specs = [
        ("primary", fmt(PRIMARY_THRESHOLD), "primary_group"),
        ("secondary", fmt(SECONDARY_THRESHOLD), "secondary_group"),
        ("pre_post_side", "", "phase_side"),
    ]
    output: list[dict[str, Any]] = []
    for role, threshold, group_field in specs:
        contexts = sorted({row["context_name"] for row in rows})
        groups = sorted({row[group_field] for row in rows})
        row_totals = {context: sum(1 for row in rows if row["context_name"] == context) for context in contexts}
        col_totals = {group: sum(1 for row in rows if row[group_field] == group) for group in groups}
        total = len(rows)
        chi2 = 0.0
        table_counts: dict[tuple[str, str], tuple[int, float]] = {}
        for context in contexts:
            for group in groups:
                observed = sum(
                    1
                    for row in rows
                    if row["context_name"] == context and row[group_field] == group
                )
                expected = row_totals[context] * col_totals[group] / total
                if expected > 0:
                    chi2 += ((observed - expected) ** 2) / expected
                table_counts[(context, group)] = (observed, expected)
        denom = total * max(1, min(len(contexts) - 1, len(groups) - 1))
        cramers = math.sqrt(chi2 / denom) if denom > 0 else math.nan
        pvalue = math.erfc(math.sqrt(chi2 / 2.0)) if len(contexts) == 2 and len(groups) == 2 else math.nan
        status = "descriptive_dependence" if math.isfinite(cramers) and cramers >= 0.05 else "weak_or_no_descriptive_dependence"
        for context in contexts:
            for group in groups:
                observed, expected = table_counts[(context, group)]
                output.append(
                    {
                        "threshold_role": role,
                        "threshold_value": threshold,
                        "context_name": context,
                        "group_name": group,
                        "observed_count": observed,
                        "expected_count": fmt(expected),
                        "row_fraction": fmt(observed / row_totals[context]),
                        "column_fraction": fmt(observed / col_totals[group]),
                        "standardized_residual": fmt((observed - expected) / math.sqrt(expected) if expected > 0 else math.nan),
                        "cramers_v": fmt(cramers),
                        "independence_test_statistic": fmt(chi2),
                        "independence_test_pvalue": fmt(pvalue),
                        "descriptive_dependence_status": status,
                        "notes": "Chi-square pvalue is supplemental; clustered dependence limits row-level interpretation.",
                    }
                )
    return output


def cluster_inventory(rows: list[dict[str, Any]], selected_key: str, min_clusters: int) -> list[dict[str, Any]]:
    candidates = [
        ("source_filename_name", "source flags name", "SHAPIROMART11 source_filename"),
        ("integer_mjd_day", "floor(toa_mjd_file)", "SHAPIROMART11 toa_mjd_file"),
        ("observatory", "observatory", "SHAPIROMART11 TOA export"),
        ("receiver_backend_context", "receiver/backend", "SHAPIROMART15 context mapping"),
        ("source_flag_proc", "source flag proc", "SHAPIROMART11 source_filename"),
        ("source_flag_subint", "source flag subint", "SHAPIROMART11 source_filename"),
        ("source_flag_chan", "source flag chan", "SHAPIROMART11 source_filename"),
        ("source_flag_tmplt", "source flag tmplt", "SHAPIROMART11 source_filename"),
        ("source_flag_ver", "source flag ver", "SHAPIROMART11 source_filename"),
    ]
    output: list[dict[str, Any]] = []
    for field, source_field, source_artifact in candidates:
        raw_values = [row.get(field, "") for row in rows]
        missing = sum(1 for value in raw_values if value == "" or (isinstance(value, float) and math.isnan(value)))
        counts = Counter(str(value) for value in raw_values if str(value) != "")
        sizes = sorted(counts.values())
        unique = len(counts)
        if missing:
            suitability = "unavailable"
            limitation = "missing values present"
        elif unique == len(rows):
            suitability = "too_granular"
            limitation = "one row per cluster"
        elif unique < 2:
            suitability = "too_coarse"
            limitation = "single or near-single cluster"
        elif field == "source_filename_name" and unique >= min_clusters:
            suitability = "cluster_key_proxy"
            limitation = "observation file proxy; not a separately documented session ID"
        elif unique >= min_clusters and max(sizes) > 1:
            suitability = "cluster_key_proxy"
            limitation = "proxy cluster key; lower priority than source filename"
        elif unique < min_clusters:
            suitability = "too_coarse"
            limitation = "below minimum cluster count"
        else:
            suitability = "non_unique"
            limitation = "not selected"
        output.append(
            {
                "cluster_candidate": field,
                "source_field": source_field,
                "source_artifact": source_artifact,
                "unique_cluster_count": unique,
                "missing_count": missing,
                "minimum_cluster_size": min(sizes) if sizes else "",
                "median_cluster_size": fmt(np.median(np.asarray(sizes, dtype=float))) if sizes else "",
                "maximum_cluster_size": max(sizes) if sizes else "",
                "mean_cluster_size": fmt(np.mean(np.asarray(sizes, dtype=float))) if sizes else "",
                "cluster_suitability": suitability,
                "selected_as_primary_cluster": "yes" if field == selected_key else "no",
                "limitation": limitation,
                "notes": "No row-order key is used as a cluster candidate.",
            }
        )
    if selected_key not in {row["cluster_candidate"] for row in output}:
        raise ControlledStop(f"Unsupported cluster key: {selected_key}")
    selected = next(row for row in output if row["cluster_candidate"] == selected_key)
    if selected["cluster_suitability"] not in {"cluster_key_direct", "cluster_key_proxy"}:
        raise ControlledStop(f"Selected cluster key is not suitable: {selected_key}")
    return output


def consistency_status(rows: list[dict[str, Any]], target: str, scope_field: str) -> str:
    local_dirs = []
    for _, selected in group_rows(rows, scope_field).items():
        if len(selected) >= DEFAULT_MINIMUM_GROUP_COUNT:
            corr = spearman(values(selected, "absolute_phase_distance"), values(selected, target))
            if math.isfinite(corr) and abs(corr) >= 0.05:
                local_dirs.append(direction(corr, 0.05))
    if not local_dirs:
        return "insufficient_or_near_zero"
    if len(set(local_dirs)) == 1:
        return "direction_consistent"
    return "direction_mixed"


def continuous_associations(rows: list[dict[str, Any]], cluster_key: str, minimum_count: int) -> list[dict[str, Any]]:
    scopes: list[tuple[str, str, str, list[dict[str, Any]]]] = [("overall", "overall", "overall", rows)]
    for context, selected in group_rows(rows, "context_name").items():
        scopes.append(("context", context, "overall", selected))
    for side, selected in group_rows(rows, "phase_side").items():
        scopes.append(("phase_side", "overall", side, selected))
    for context, context_rows in group_rows(rows, "context_name").items():
        for side, selected in group_rows(context_rows, "phase_side").items():
            scopes.append(("context_phase_side", context, side, selected))

    output: list[dict[str, Any]] = []
    for target, label in TARGETS:
        context_status = consistency_status(rows, target, "context_name")
        side_status = consistency_status(rows, target, "phase_side")
        for scope_name, context, side, selected in scopes:
            count = len(selected)
            if count < minimum_count:
                slope = se = cse = lower = upper = corr = math.nan
                monotonicity = "insufficient_count"
                assoc_status = "insufficient_count"
            else:
                x = values(selected, "absolute_phase_distance")
                y = values(selected, target)
                clusters = [str(row[cluster_key]) for row in selected]
                slope, se, cse, lower, upper = slope_and_se(x, y, clusters)
                corr = spearman(x, y)
                monotonicity = association_status(corr)
                assoc_status = association_status(corr)
            output.append(
                {
                    "target_variable": label,
                    "analysis_scope": scope_name,
                    "context_name": context,
                    "phase_side": side,
                    "model_type": "linear_y_on_absolute_phase_distance_plus_spearman",
                    "predictor": "absolute_phase_distance",
                    "count": count,
                    "cluster_key": cluster_key,
                    "association_measure": "spearman_and_linear_slope",
                    "association_value": fmt(corr),
                    "standard_error": fmt(se),
                    "clustered_standard_error": fmt(cse),
                    "ci_lower": fmt(lower),
                    "ci_upper": fmt(upper),
                    "monotonicity_status": monotonicity,
                    "direction": direction(corr, 0.05),
                    "context_consistency_status": context_status,
                    "side_consistency_status": side_status,
                    "continuous_association_status": assoc_status,
                    "notes": "TOA_MJD is not treated as an independent signal target in this table.",
                }
            )
    return output


def matched_comparisons(rows: list[dict[str, Any]], cluster_key: str, minimum_count: int) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    contexts = ["overall"] + sorted(group_rows(rows, "context_name"))
    for target, label in TARGETS:
        for context in contexts:
            selected = rows if context == "overall" else [row for row in rows if row["context_name"] == context]
            pairs: list[float] = []
            matched_inside = 0
            matched_outside = 0
            inside_total = sum(1 for row in selected if row["primary_group"] == "inside_primary_threshold")
            outside_total = sum(1 for row in selected if row["primary_group"] == "outside_primary_threshold")
            for _, block_rows in group_rows(selected, cluster_key).items():
                inside_rows = [row for row in block_rows if row["primary_group"] == "inside_primary_threshold"]
                outside_rows = [row for row in block_rows if row["primary_group"] == "outside_primary_threshold"]
                used_outside: set[int] = set()
                for inside in inside_rows:
                    candidates = []
                    for idx, outside in enumerate(outside_rows):
                        if idx in used_outside:
                            continue
                        if target != "observing_frequency_mhz":
                            freq_delta = abs(
                                float(inside["observing_frequency_mhz"])
                                - float(outside["observing_frequency_mhz"])
                            )
                            if freq_delta > SIGNAL_FREQUENCY_CALIPER_MHZ:
                                continue
                        candidates.append((abs(float(inside["absolute_phase_distance"]) - float(outside["absolute_phase_distance"])), idx, outside))
                    if not candidates:
                        continue
                    _, idx, outside = min(candidates, key=lambda item: item[0])
                    used_outside.add(idx)
                    pairs.append(float(inside[target]) - float(outside[target]))
                    matched_inside += 1
                    matched_outside += 1
            diff = np.asarray(pairs, dtype=float)
            if diff.size < minimum_count:
                status = "not_supported_by_available_structure"
                mean_diff = median_diff = std_effect = robust = math.nan
            else:
                status = "matched_comparison_supported_descriptively"
                mean_diff = float(np.mean(diff))
                median_diff = float(np.median(diff))
                std = float(np.std(diff, ddof=1)) if diff.size > 1 else math.nan
                std_effect = mean_diff / std if math.isfinite(std) and std > 0 else math.nan
                robust = robust_pair_effect(diff)
            output.append(
                {
                    "target_variable": label,
                    "context_name": context,
                    "matching_block": cluster_key,
                    "matching_variables": "context and observation file; frequency caliper for SNR/Flux only",
                    "caliper_definition": "frequency <= 20 MHz for SNR/Flux; no frequency caliper for frequency target",
                    "matched_set_count": int(diff.size),
                    "matched_inside_count": matched_inside,
                    "matched_outside_count": matched_outside,
                    "unmatched_inside_count": inside_total - matched_inside,
                    "unmatched_outside_count": outside_total - matched_outside,
                    "balance_status": "frequency_caliper_used_for_signal_targets" if target != "observing_frequency_mhz" else "same_context_and_file",
                    "mean_difference": fmt(mean_diff),
                    "median_difference": fmt(median_diff),
                    "standardized_effect": fmt(std_effect),
                    "robust_effect": fmt(robust),
                    "matched_analysis_status": status,
                    "notes": "Matching uses fixed structure and does not use SNR or Flux as matching criteria.",
                }
            )
    return output


def slope_statistic(rows: list[dict[str, Any]], target: str) -> float:
    x = values(rows, "absolute_phase_distance")
    y = values(rows, target)
    slope, _, _, _, _ = slope_and_se(x, y, None)
    return slope


def slope_from_arrays(x: np.ndarray, y: np.ndarray) -> float:
    if x.size < 3 or y.size < 3:
        return math.nan
    x0 = x - np.mean(x)
    denom = float(np.sum(x0 * x0))
    if denom <= 0:
        return math.nan
    return float(np.sum(x0 * (y - np.mean(y))) / denom)


def stable_seed(seed: int, *parts: str) -> int:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()
    return (seed + int(digest[:8], 16)) % (2**32)


def blocked_permutations(
    rows: list[dict[str, Any]],
    cluster_key: str,
    replicates: int,
    seed: int,
    minimum_group_count: int,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    scopes: list[tuple[str, list[dict[str, Any]]]] = [("overall", rows)]
    for context, selected in group_rows(rows, "context_name").items():
        scopes.append((context, selected))
    for target, label in TARGETS:
        for scope_name, selected in scopes:
            usable_blocks = [
                block
                for block in group_rows(selected, f"{cluster_key}").values()
                if len(block) >= 2
            ]
            validity = (
                "valid_blocked_within_context_file"
                if len(usable_blocks) >= 20
                else "limited_block_count"
            )
            x = values(selected, "absolute_phase_distance")
            y = values(selected, target)
            observed = slope_from_arrays(x, y) if len(selected) >= minimum_group_count else math.nan
            rng = np.random.default_rng(stable_seed(seed, target, scope_name))
            index_blocks: list[np.ndarray] = []
            index_by_source = {int(row["source_row_index"]): idx for idx, row in enumerate(selected)}
            for block in group_rows(selected, cluster_key).values():
                indices = np.asarray(
                    [index_by_source[int(row["source_row_index"])] for row in block],
                    dtype=int,
                )
                if indices.size >= 2:
                    index_blocks.append(indices)
            permuted_stats: list[float] = []
            for _ in range(replicates):
                y_perm = y.copy()
                for indices in index_blocks:
                    y_perm[indices] = rng.permutation(y_perm[indices])
                stat = slope_from_arrays(x, y_perm)
                if math.isfinite(stat):
                    permuted_stats.append(stat)
            arr = np.asarray(permuted_stats, dtype=float)
            if arr.size:
                center = float(np.mean(arr))
                spread = float(np.std(arr, ddof=1)) if arr.size > 1 else 0.0
                low, high = np.quantile(arr, [0.025, 0.975])
                tail = float(np.mean(np.abs(arr) >= abs(observed))) if math.isfinite(observed) else math.nan
            else:
                center = spread = low = high = tail = math.nan
            if not math.isfinite(observed):
                result_status = "not_computed"
            elif validity != "valid_blocked_within_context_file":
                result_status = "limited_block_structure"
            elif math.isfinite(tail) and tail <= 0.05 and label not in {"SNR", "Flux"}:
                result_status = "configuration_association_outside_permutation_reference"
            elif math.isfinite(tail) and tail <= 0.05:
                result_status = "signal_association_outside_permutation_reference"
            else:
                result_status = "within_block_reference_not_exceeded"
            output.append(
                {
                    "target_variable": label,
                    "analysis_scope": scope_name,
                    "block_definition": f"context_name + {cluster_key}",
                    "permutation_scheme": "shuffle target values within blocks while preserving continuous geometry",
                    "observed_statistic": fmt(observed),
                    "permutation_mean": fmt(center),
                    "permutation_standard_deviation": fmt(spread),
                    "permutation_ci_lower": fmt(low),
                    "permutation_ci_upper": fmt(high),
                    "tail_fraction": fmt(tail),
                    "replicate_count": len(permuted_stats),
                    "random_seed": seed,
                    "permutation_validity": validity,
                    "permutation_result_status": result_status,
                    "notes": "No global shuffling is used. TOA_MJD is not permuted as a target.",
                }
            )
    return output


def negative_control_sensitivity() -> list[dict[str, Any]]:
    return [
        {
            "signal_dimension": "signal_value_primary",
            "measurement_role": "SNR source flag",
            "calibration_status": "source_flag_not_full_calibration",
            "context_comparability": "limited_by_receiver_frequency_and_observation_file",
            "frequency_dependence": "possible",
            "detects_global_amplitude_change": "coarsely_yes",
            "detects_profile_shape_change": "no",
            "detects_scattering_change": "no",
            "detects_polarization_change": "no",
            "detects_timing_residual_change": "no",
            "current_null_status": "no_material_group_association_in_SHAPIROMART18_19",
            "negative_control_status": "limited_negative_control",
            "interpretation_limit": "Stable SNR does not prove signal invariance.",
            "notes": "Useful as a coarse amplitude check only.",
        },
        {
            "signal_dimension": "signal_value_secondary",
            "measurement_role": "Flux source flag",
            "calibration_status": "source_flag_not_full_calibration",
            "context_comparability": "context_limited",
            "frequency_dependence": "expected_possible",
            "detects_global_amplitude_change": "coarsely_yes",
            "detects_profile_shape_change": "no",
            "detects_scattering_change": "no",
            "detects_polarization_change": "no",
            "detects_timing_residual_change": "no",
            "current_null_status": "no_material_group_association_in_SHAPIROMART18_19",
            "negative_control_status": "context_limited_negative_control",
            "interpretation_limit": "Stable flux does not prove signal invariance.",
            "notes": "Flux is coarse and may be frequency or calibration dependent.",
        },
    ]


def finer_observable_inventory(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    row_count = len(rows)
    return [
        observable("OBS001", "timing residuals", "allowed local SHAPIROMART artifacts", "", "time", "no", 0, "not_applicable", "yes", "high", "absent", "not_available", "No residual field exported.", "No residual analysis performed."),
        observable("OBS002", "pre-fit residuals", "allowed local SHAPIROMART artifacts", "", "time", "no", 0, "not_applicable", "yes", "high", "absent", "not_available", "No pre-fit residual field exported.", "No residual analysis performed."),
        observable("OBS003", "published residuals", "allowed local SHAPIROMART artifacts", "", "time", "no", 0, "not_applicable", "yes", "high", "absent", "requires_external_data", "No local published residual table.", "External retrieval is outside this block."),
        observable("OBS004", "pulse width W50/W10", "SHAPIROMART11 source flags", "", "profile width", "no", 0, "not_applicable", "yes", "high", "absent", "not_available", "No pulse-width flag exported.", ""),
        observable("OBS005", "profile shape coefficients", "SHAPIROMART11 source flags", "", "profile", "no", 0, "not_applicable", "yes", "high", "absent", "not_available", "No profile coefficient fields exported.", ""),
        observable("OBS006", "scattering timescale", "SHAPIROMART11 source flags", "", "time", "no", 0, "not_applicable", "yes", "high", "absent", "not_available", "No scattering field exported.", ""),
        observable("OBS007", "dispersion measure variations", "SHAPIROMART11 source flags", "", "pc cm^-3", "no", 0, "not_applicable", "yes", "medium", "absent", "not_available", "No row-level DM variation field exported.", ""),
        observable("OBS008", "polarization measures", "SHAPIROMART11 source flags", "", "various", "no", 0, "not_applicable", "yes", "medium", "absent", "not_available", "No polarization field exported.", ""),
        observable("OBS009", "spectral index", "SHAPIROMART11 source flags", "", "dimensionless", "no", 0, "not_applicable", "yes", "medium", "absent", "not_available", "No spectral-index field exported.", ""),
        observable("OBS010", "profile component ratios", "SHAPIROMART11 source flags", "", "ratio", "no", 0, "not_applicable", "yes", "high", "absent", "not_available", "No component-ratio fields exported.", ""),
        observable("OBS011", "goodness of fit", "SHAPIROMART11 source flags", "gof", "dimensionless", "yes", row_count, "limited", "partly", "medium", "source_flag_semantics_incomplete", "available_but_semantics_incomplete", "Semantics are not sufficient for a signal-shape conclusion.", "Can be prioritized for a later controlled quality-readout block."),
        observable("OBS012", "TOA weight", "SHAPIROMART11 source flags", "wt", "dimensionless", "yes", row_count, "limited", "partly", "medium", "source_flag_semantics_incomplete", "available_but_semantics_incomplete", "Weight direction and calibration role are not resolved.", ""),
        observable("OBS013", "flux uncertainty", "SHAPIROMART11 source flags", "fluxe", "flux units", "yes", row_count, "limited", "yes", "medium", "source_flag_semantics_incomplete", "available_but_semantics_incomplete", "Uncertainty semantics need review.", ""),
        observable("OBS014", "channelized configuration", "SHAPIROMART11 source flags", "chan;nch;bw", "configuration", "yes", row_count, "context_limited", "yes", "low_for_signal", "configuration_not_signal", "available_but_semantics_incomplete", "Configuration fields are not independent signal observables.", ""),
        observable("OBS015", "pulse-profile template identity", "SHAPIROMART11 source flags", "tmplt", "template id", "yes", row_count, "context_limited", "yes", "medium", "identity_only", "summary_only", "Template name is not the calibrated profile.", ""),
        observable("OBS016", "calibrated profiles", "local exported artifacts", "", "profile", "no", 0, "not_applicable", "yes", "high", "absent", "requires_external_data", "No calibrated profile files are part of the controlled SHAPIROMART export.", ""),
    ]


def observable(
    obs_id: str,
    name: str,
    artifact: str,
    field: str,
    unit: str,
    row_available: str,
    count: int,
    comparable: str,
    independent: str,
    relevance: str,
    semantic: str,
    readiness: str,
    gap: str,
    notes: str,
) -> dict[str, Any]:
    return {
        "observable_id": obs_id,
        "observable_name": name,
        "source_artifact": artifact,
        "source_field": field,
        "unit": unit,
        "row_level_available": row_available,
        "available_row_count": count,
        "context_comparable": comparable,
        "independent_from_group_construction": independent,
        "diagnostic_relevance": relevance,
        "semantic_status": semantic,
        "readiness_status": readiness,
        "main_gap": gap,
        "notes": notes,
    }


def conventional_matrix(
    circularity: list[dict[str, Any]],
    contingency: list[dict[str, Any]],
    cluster_rows: list[dict[str, Any]],
    continuous: list[dict[str, Any]],
    permutation: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    primary_cramers = max(
        safe_float(row["cramers_v"])
        for row in contingency
        if row["threshold_role"] == "primary"
    )
    selected_cluster = next(row for row in cluster_rows if row["selected_as_primary_cluster"] == "yes")
    signal_continuous = [
        row
        for row in continuous
        if row["target_variable"] in {"SNR", "Flux"} and row["analysis_scope"] == "overall"
    ]
    signal_status = "; ".join(
        f"{row['target_variable']}={row['continuous_association_status']}" for row in signal_continuous
    )
    signal_perm = [
        row
        for row in permutation
        if row["target_variable"] in {"SNR", "Flux"} and row["analysis_scope"] == "overall"
    ]
    signal_perm_status = "; ".join(
        f"{row['target_variable']}={row['permutation_result_status']}" for row in signal_perm
    )
    return [
        {
            "observed_pattern": "coordinate_secondary group difference",
            "conventional_explanation": "TOA-derived phase construction and observation scheduling",
            "supporting_evidence": circularity[0]["circularity_status"],
            "contradicting_evidence": "Some within-file residual structure may remain, but TOA_MJD is upstream of the grouping axis.",
            "test_performed": "formal dependency chain and within-cluster association summary",
            "test_result": circularity[0]["additional_information_after_control"],
            "explanation_status": "largely_explained_by_observation_design",
            "residual_open_question": "Separate time sampling from binary phase geometry in a future design.",
            "notes": "TOA_MJD is not carried forward as an independent signal outcome.",
        },
        {
            "observed_pattern": "context x inside/outside imbalance",
            "conventional_explanation": "receiver/backend composition and observing allocation",
            "supporting_evidence": f"primary_cramers_v={fmt(primary_cramers)}",
            "contradicting_evidence": "Both receiver/backend contexts have inside and outside rows.",
            "test_performed": "context by group contingency",
            "test_result": "descriptive dependence assessed",
            "explanation_status": "partly_explained_by_observation_design",
            "residual_open_question": "Context-specific sampling remains uneven.",
            "notes": "Cramer value is descriptive under clustered rows.",
        },
        {
            "observed_pattern": "coordinate_primary threshold-localized difference",
            "conventional_explanation": "frequency-band allocation within observation files and receiver context",
            "supporting_evidence": "frequency is an observing configuration coordinate",
            "contradicting_evidence": "Within-context rows still span multiple channels.",
            "test_performed": "continuous and matched frequency readouts",
            "test_result": "configuration association, not signal target",
            "explanation_status": "largely_explained_by_observation_design",
            "residual_open_question": "Channel scheduling can be documented more finely if needed.",
            "notes": "No new geometry threshold selected.",
        },
        {
            "observed_pattern": "SNR and Flux no material group difference",
            "conventional_explanation": "coarse source flags are insensitive to profile/residual effects",
            "supporting_evidence": signal_status,
            "contradicting_evidence": "SNR/Flux are limited negative controls.",
            "test_performed": "continuous and blocked permutation specificity checks",
            "test_result": signal_perm_status,
            "explanation_status": "partly_explained_by_observation_design",
            "residual_open_question": "Finer independent signal observables are mostly absent or incomplete.",
            "notes": "No signal invariance statement is made.",
        },
        {
            "observed_pattern": "TOA-level bootstrap sensitivity",
            "conventional_explanation": "multiple TOAs per observation file create dependence",
            "supporting_evidence": f"selected_cluster={selected_cluster['cluster_candidate']}; max_cluster_size={selected_cluster['maximum_cluster_size']}",
            "contradicting_evidence": "There are more than 20 observation-file clusters.",
            "test_performed": "cluster inventory and blocked permutation",
            "test_result": selected_cluster["cluster_suitability"],
            "explanation_status": "partly_explained_by_observation_design",
            "residual_open_question": "A later block may use cluster bootstrap if a target outcome is specified.",
            "notes": "TOA-level independence should not be assumed without the cluster structure.",
        },
    ]


def final_status(
    rows: list[dict[str, Any]],
    circularity: list[dict[str, Any]],
    cluster_rows: list[dict[str, Any]],
    continuous: list[dict[str, Any]],
    matched: list[dict[str, Any]],
    permutation: list[dict[str, Any]],
    negative: list[dict[str, Any]],
    observable_rows: list[dict[str, Any]],
    explanation_rows: list[dict[str, Any]],
    cluster_key: str,
) -> dict[str, Any]:
    signal_rows = [
        row
        for row in continuous
        if row["target_variable"] in {"SNR", "Flux"}
        and row["analysis_scope"] in {"overall", "context"}
    ]
    signal_supported = any(
        row["continuous_association_status"] in {"moderate_continuous_association", "strong_continuous_association"}
        for row in signal_rows
    )
    signal_perm_supported = any(
        row["target_variable"] in {"SNR", "Flux"}
        and row["permutation_result_status"] == "signal_association_outside_permutation_reference"
        for row in permutation
    )
    residual = "yes" if signal_supported and signal_perm_supported else "no"
    cluster_selected = next(row for row in cluster_rows if row["selected_as_primary_cluster"] == "yes")
    cluster_partial = cluster_selected["cluster_suitability"] != "cluster_key_direct"
    if residual == "yes":
        final = "residual_descriptive_association_after_confounder_controls"
        pattern = "current_pattern_partly_explained_with_residual_nontrivial_association"
    else:
        final = "current_pattern_explained_without_independent_signal_association"
        pattern = "current_pattern_partly_explained_with_no_independent_signal_association"
    if cluster_partial and final == "within_context_continuous_geometry_confounder_test_completed":
        final = "confounder_test_completed_cluster_structure_partial"
    return {
        "research_block": RESEARCH_BLOCK,
        "input_rows": len(rows),
        "circularity_assessment_completed": "yes",
        "toa_mjd_circularity_status": circularity[0]["circularity_status"],
        "context_group_dependence_assessed": "yes",
        "cluster_structure_assessed": "yes",
        "primary_cluster_key": cluster_key,
        "continuous_geometry_analysis_completed": "yes" if continuous else "no",
        "within_context_analysis_completed": "yes",
        "matched_analysis_completed": "yes" if matched else "no",
        "blocked_permutation_completed": "yes" if permutation else "no",
        "snr_flux_sensitivity_assessed": "yes" if len(negative) == 2 else "no",
        "finer_observable_inventory_completed": "yes" if observable_rows else "no",
        "conventional_explanation_assessed": "yes" if explanation_rows else "no",
        "current_pattern_explanation_status": pattern,
        "residual_nontrivial_association_found": residual,
        "timing_residual_analysis_performed": "no",
        "shapiro_delay_calculated": "no",
        "timing_model_fit_performed": "no",
        "model_parameters_modified": "no",
        "physical_interpretation_performed": "no",
        "qsb_claim_made": "no",
        "database_access": "none",
        "database_modified": "no",
        "additional_gate_created": "no",
        "final_status": final,
        "recommended_next_action": "Prioritize finer independent signal observables before any further interpretation.",
        "limitations": "Source filename is a cluster proxy, SNR and Flux are coarse controls, and no residual or model-fit analysis was performed.",
    }


def write_readout(path: Path, final_row: dict[str, Any], cluster_rows: list[dict[str, Any]], continuous: list[dict[str, Any]], negative: list[dict[str, Any]], observable_rows: list[dict[str, Any]]) -> None:
    selected_cluster = next(row for row in cluster_rows if row["selected_as_primary_cluster"] == "yes")
    overall_cont = {
        row["target_variable"]: row
        for row in continuous
        if row["analysis_scope"] == "overall"
    }
    ready_observables = [row for row in observable_rows if row["readiness_status"] == "ready_for_controlled_analysis"]
    incomplete_observables = [
        row
        for row in observable_rows
        if row["readiness_status"] in {"available_but_semantics_incomplete", "summary_only"}
    ]
    lines = [
        "# QSB-SHAPIROMART20 Readout",
        "",
        "## Purpose",
        "",
        "This block tests the SHAPIROMART18/19 pattern against construction, context, cluster, and continuous-distance objections.",
        "",
        "## Red-Team Questions Addressed",
        "",
        "The analysis covers TOA-MJD circularity, receiver/backend dependence, observation-file clustering, continuous absolute phase distance, blocked permutation, and the limits of SNR/Flux controls.",
        "",
        "## Input Identity",
        "",
        f"Input rows: {final_row['input_rows']}. Primary cluster key: {final_row['primary_cluster_key']}.",
        "",
        "## TOA-MJD Circularity Assessment",
        "",
        f"TOA-MJD circularity status: {final_row['toa_mjd_circularity_status']}. TOA-MJD is upstream of orbital phase and group construction.",
        "",
        "## Receiver/Backend and Group Dependence",
        "",
        "Context by group dependence was assessed with observed counts, expected counts, residuals, and Cramer's V.",
        "",
        "## Epoch, Session, and Campaign Structure",
        "",
        f"Selected cluster proxy: {selected_cluster['cluster_candidate']} with {selected_cluster['unique_cluster_count']} clusters, median size {selected_cluster['median_cluster_size']}, maximum size {selected_cluster['maximum_cluster_size']}.",
        "",
        "## Continuous Geometry Associations",
        "",
        f"- Frequency overall: {overall_cont['observing frequency / band']['continuous_association_status']} ({overall_cont['observing frequency / band']['association_value']}).",
        f"- SNR overall: {overall_cont['SNR']['continuous_association_status']} ({overall_cont['SNR']['association_value']}).",
        f"- Flux overall: {overall_cont['Flux']['continuous_association_status']} ({overall_cont['Flux']['association_value']}).",
        "",
        "## Within-Context and Matched Comparisons",
        "",
        "Matched comparisons used same observation-file blocks and a fixed frequency caliper for SNR/Flux. No outcome-based matching was used.",
        "",
        "## Blocked Permutation Results",
        "",
        "Permutation shuffled target values only within context plus observation-file blocks while preserving the continuous geometry axis.",
        "",
        "## SNR and Flux Sensitivity Limits",
        "",
        f"- SNR: {negative[0]['negative_control_status']}.",
        f"- Flux: {negative[1]['negative_control_status']}.",
        "",
        "## Finer Observable Inventory",
        "",
        f"Ready finer observables: {len(ready_observables)}. Available but incomplete or summary-only: {len(incomplete_observables)}.",
        "",
        "## Conventional Explanation Assessment",
        "",
        f"Current pattern explanation status: {final_row['current_pattern_explanation_status']}.",
        "",
        "## Consolidated Result",
        "",
        f"Final status: {final_row['final_status']}. Residual nontrivial association found: {final_row['residual_nontrivial_association_found']}.",
        "",
        "## What This Does Not Establish",
        "",
        "This block does not establish a physical interpretation, a QSB claim, Shapiro delay, timing residual behavior, model-fit behavior, or signal invariance.",
        "",
        "## Recommended Next Scientific Action",
        "",
        final_row["recommended_next_action"],
        "",
        "## Limitations",
        "",
        final_row["limitations"],
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def run(args: argparse.Namespace) -> dict[str, Any]:
    if args.permutation_replicates < 2000:
        raise ControlledStop("permutation_replicates must be at least 2000.")
    prepare_output_dir(args)
    rows, metadata = load_inputs(args)
    cluster_rows = cluster_inventory(rows, args.cluster_key, args.minimum_cluster_count)
    circularity = circularity_assessment(rows, args.cluster_key)
    contingency = contingency_rows(rows)
    continuous = continuous_associations(rows, args.cluster_key, args.minimum_group_count)
    matched = matched_comparisons(rows, args.cluster_key, args.minimum_group_count)
    permutation = blocked_permutations(
        rows,
        args.cluster_key,
        args.permutation_replicates,
        args.random_seed,
        args.minimum_group_count,
    )
    negative = negative_control_sensitivity()
    observables = finer_observable_inventory(rows)
    explanation = conventional_matrix(circularity, contingency, cluster_rows, continuous, permutation)
    final_row = final_status(
        rows,
        circularity,
        cluster_rows,
        continuous,
        matched,
        permutation,
        negative,
        observables,
        explanation,
        args.cluster_key,
    )
    summary = {
        "research_block": RESEARCH_BLOCK,
        "timestamp_utc": now_utc(),
        "inputs_read": {
            "phase_input": rel(args.phase_input),
            "enriched_context_input": rel(args.enriched_context_input),
            "prepared_groups_input": rel(args.prepared_groups_input),
            "shapiromart18_dir": rel(args.shapiromart18_dir),
            "shapiromart19_dir": rel(args.shapiromart19_dir),
        },
        "output_dir": rel(args.output_dir),
        "output_files": [rel(args.output_dir / name) for name in OUTPUT_FILES],
        "method": {
            "cluster_key": args.cluster_key,
            "permutation_replicates": args.permutation_replicates,
            "random_seed": args.random_seed,
            "minimum_cluster_count": args.minimum_cluster_count,
            "minimum_group_count": args.minimum_group_count,
            "new_threshold_selected": "no",
            "groups_redefined": "no",
            "database_access": "none",
        },
        "input_rows": len(rows),
        "metadata_context": {
            "shapiromart18_final_status": metadata["shapiromart18_final"][0].get("final_status", ""),
            "shapiromart19_final_status": metadata["shapiromart19_final"][0].get("final_status", ""),
        },
        "final_status": final_row,
    }

    write_csv(args.output_dir / "shapiromart20_circularity_assessment.csv", circularity, CIRCULARITY_FIELDS)
    write_csv(args.output_dir / "shapiromart20_context_group_contingency.csv", contingency, CONTINGENCY_FIELDS)
    write_csv(args.output_dir / "shapiromart20_cluster_structure_inventory.csv", cluster_rows, CLUSTER_FIELDS)
    write_csv(args.output_dir / "shapiromart20_continuous_geometry_associations.csv", continuous, CONTINUOUS_FIELDS)
    write_csv(args.output_dir / "shapiromart20_within_context_matched_comparison.csv", matched, MATCHED_FIELDS)
    write_csv(args.output_dir / "shapiromart20_blocked_permutation_results.csv", permutation, PERMUTATION_FIELDS)
    write_csv(args.output_dir / "shapiromart20_negative_control_sensitivity.csv", negative, NEGATIVE_FIELDS)
    write_csv(args.output_dir / "shapiromart20_finer_observable_inventory.csv", observables, OBSERVABLE_FIELDS)
    write_csv(args.output_dir / "shapiromart20_conventional_explanation_matrix.csv", explanation, EXPLANATION_FIELDS)
    write_csv(args.output_dir / "shapiromart20_final_status.csv", [final_row], FINAL_FIELDS)
    write_json(args.output_dir / "shapiromart20_summary.json", summary)
    write_readout(
        args.output_dir / "shapiromart20_readout.md",
        final_row,
        cluster_rows,
        continuous,
        negative,
        observables,
    )
    return summary


def main() -> int:
    args = parse_args()
    try:
        summary = run(args)
    except Exception as exc:
        print(f"{RESEARCH_BLOCK} failed: {exc}")
        return 1
    print(f"{RESEARCH_BLOCK} completed: {summary['output_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
