#!/usr/bin/env python3
"""QSB-ST COMP01-D1o refined D1m metadata runner.

This runner reads original D1m outputs and D1n audit artifacts, appends
explicit warning/dominance metadata, and writes a new D1o output folder. It
does not modify original D1m outputs and does not rerun D1m.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover - environment guard
    raise SystemExit(
        "PyYAML is required to read the D1o config. Activate the project environment or install PyYAML."
    ) from exc


PROFILE_EXTRA_FIELDS = [
    "dominant_channel_share",
    "single_channel_dominance_threshold",
    "dominance_warning_reason",
    "warning_origin_count_global",
    "warning_origin_count_case",
    "warning_origin_count_policy",
    "warning_origin_count_input",
    "warning_origin_count_claim_boundary",
    "profile_score_component_count",
    "aggregate_broadcast_component_count",
    "case_level_component_count",
    "profile_warning_origin_summary",
    "profile_warning_granularity_summary",
    "dominance_interpretation_note",
    "runner_refinement_version",
]

CHANNEL_EXTRA_FIELDS = [
    "score_granularity",
    "warning_granularity",
    "broadcast_warning_flag",
    "interpretation_role",
    "refinement_needed",
    "recommended_change",
    "aggregate_broadcast_score_flag",
    "runner_refinement_version",
]

WARNING_EXTRA_FIELDS = [
    "warning_origin",
    "warning_granularity",
    "inherited_from",
    "broadcast_warning_flag",
    "interpretation_boundary_refined",
    "runner_refinement_version",
]

DOMINANCE_FIELDS = [
    "dominance_metric",
    "value",
    "description",
    "interpretation_boundary",
    "runner_refinement_version",
]

COMPARISON_FIELDS = [
    "comparison_item",
    "original_d1m_value",
    "refined_d1o_value",
    "changed",
    "interpretation_boundary",
]

SCORE_FIELDS = [
    "phase_exposure_score",
    "residual_mimicry_score",
    "component_ablation_stability_score",
    "threshold_weight_stability_score",
    "channel_specific_separability_score",
]

SCORE_FIELD_BY_CHANNEL = {
    "phase_exposure": "phase_exposure_score",
    "residual_mimicry": "residual_mimicry_score",
    "component_ablation": "component_ablation_stability_score",
    "threshold_weight_robustness": "threshold_weight_stability_score",
    "channel_specific_separability": "channel_specific_separability_score",
}

AGGREGATE_BROADCAST_FIELDS = {
    "component_ablation_stability_score",
    "threshold_weight_stability_score",
}

CASE_LEVEL_SCORE_FIELDS = {
    "phase_exposure_score",
    "residual_mimicry_score",
    "channel_specific_separability_score",
}

DOMINANCE_NOTE = "dominant_channel_id is descriptive; single_channel_dominance_warning is threshold-based"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create refined D1m metadata outputs from existing D1m and D1n artifacts."
    )
    parser.add_argument("--config", required=True, help="Path to D1o YAML config.")
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_path(root: Path, value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else root / path


def read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Missing config file: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"Config did not parse to a mapping: {path}")
    return data


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader), reader.fieldnames or []


def write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: format_cell(row.get(field, "")) for field in fields})


def format_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return ""
        return f"{value:.12g}"
    return str(value)


def safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n", ""}:
        return False
    return default


def safe_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def safe_int(value: Any) -> int:
    number = safe_float(value)
    if number is None:
        return 0
    return int(number)


def ensure_inputs_exist(input_paths: dict[str, Path]) -> None:
    missing = [str(path) for path in input_paths.values() if not path.exists()]
    if missing:
        raise SystemExit("Missing required input artifacts; D1m/D1n will not be rerun:\n" + "\n".join(missing))


def append_fields(original: list[str], extra: list[str]) -> list[str]:
    fields = list(original)
    for field in extra:
        if field not in fields:
            fields.append(field)
    return fields


def key_value_summary(counts: dict[str, int]) -> str:
    return ";".join(f"{key}={counts[key]}" for key in sorted(counts))


def active_warning_rows(warning_origin_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in warning_origin_rows if safe_int(row.get("active_count")) > 0]


def global_origin_counts(warning_origin_rows: list[dict[str, str]]) -> dict[str, int]:
    counts = Counter(row.get("warning_origin", "unknown") for row in active_warning_rows(warning_origin_rows))
    return dict(counts)


def global_granularity_counts(warning_origin_rows: list[dict[str, str]]) -> dict[str, int]:
    counts = Counter(row.get("warning_granularity", "unknown") for row in active_warning_rows(warning_origin_rows))
    return dict(counts)


def per_row_counts(row: dict[str, str], warning_origin_rows: list[dict[str, str]]) -> tuple[dict[str, int], dict[str, int]]:
    origin_counts = Counter()
    granularity_counts = Counter()
    for warning in active_warning_rows(warning_origin_rows):
        warning_id = warning.get("warning_id", "")
        granularity = warning.get("warning_granularity", "")
        origin = warning.get("warning_origin", "")
        applies = False
        if granularity == "global_broadcast":
            applies = True
        elif granularity == "claim_boundary":
            applies = safe_bool(row.get(warning_id), False)
        elif granularity == "input_level":
            applies = safe_bool(row.get(warning_id), False)
        elif warning_id == "near_duplicate_intrusion_warning":
            applies = safe_bool(row.get("near_duplicate_intrusion_flag"), False)
        elif warning_id == "residual_mimicry_warning":
            applies = row.get("residual_mimicry_score", "").strip() != ""
        elif warning_id == "single_channel_dominance_warning":
            applies = safe_bool(row.get("single_channel_dominance_warning"), False)
        else:
            applies = safe_bool(row.get(warning_id), False)
        if applies:
            origin_counts[origin or "unknown"] += 1
            granularity_counts[granularity or "unknown"] += 1
    return dict(origin_counts), dict(granularity_counts)


def calculate_dominance(row: dict[str, str], threshold: float) -> tuple[float | None, str, int, int, int]:
    numeric_scores: dict[str, float] = {}
    for field in SCORE_FIELDS:
        number = safe_float(row.get(field))
        if number is not None:
            numeric_scores[field] = number
    positive_sum = sum(value for value in numeric_scores.values() if value > 0)
    component_count = len(numeric_scores)
    aggregate_count = sum(1 for field in AGGREGATE_BROADCAST_FIELDS if field in numeric_scores)
    case_level_count = sum(1 for field in CASE_LEVEL_SCORE_FIELDS if field in numeric_scores)
    dominant_channel = row.get("dominant_channel_id", "")
    dominant_field = SCORE_FIELD_BY_CHANNEL.get(dominant_channel)
    dominant_value = numeric_scores.get(dominant_field, 0.0) if dominant_field else 0.0
    if positive_sum <= 0:
        return None, "dominance_share_unavailable", component_count, aggregate_count, case_level_count
    share = dominant_value / positive_sum if dominant_value > 0 else max(numeric_scores.values()) / positive_sum
    reason = (
        "dominant_channel_share_crosses_threshold"
        if share >= threshold
        else "dominant_channel_share_below_threshold"
    )
    return share, reason, component_count, aggregate_count, case_level_count


def refine_profile_rows(
    original_rows: list[dict[str, str]],
    warning_origin_rows: list[dict[str, str]],
    threshold: float,
    runner_refinement_version: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    refined_rows: list[dict[str, Any]] = []
    shares: list[float] = []
    crossing_count = 0
    dominant_distribution = Counter()
    for row in original_rows:
        refined = dict(row)
        share, reason, component_count, aggregate_count, case_level_count = calculate_dominance(row, threshold)
        if share is not None:
            shares.append(share)
            if share >= threshold:
                crossing_count += 1
        dominant_distribution[row.get("dominant_channel_id", "")] += 1
        origin_counts, granularity_counts = per_row_counts(row, warning_origin_rows)
        refined.update(
            {
                "dominant_channel_share": share,
                "single_channel_dominance_threshold": threshold,
                "dominance_warning_reason": reason,
                "warning_origin_count_global": origin_counts.get("inherited_d1l_global", 0),
                "warning_origin_count_case": origin_counts.get("d1m_case_or_family_logic", 0),
                "warning_origin_count_policy": origin_counts.get("d1m_interpretation_policy", 0),
                "warning_origin_count_input": origin_counts.get("d1m_input_join", 0),
                "warning_origin_count_claim_boundary": origin_counts.get("claim_boundary_guard", 0),
                "profile_score_component_count": component_count,
                "aggregate_broadcast_component_count": aggregate_count,
                "case_level_component_count": case_level_count,
                "profile_warning_origin_summary": key_value_summary(origin_counts),
                "profile_warning_granularity_summary": key_value_summary(granularity_counts),
                "dominance_interpretation_note": DOMINANCE_NOTE,
                "runner_refinement_version": runner_refinement_version,
            }
        )
        refined_rows.append(refined)
    dominance_stats = {
        "rows_crossing_dominance_threshold": crossing_count,
        "dominant_channel_distribution": dict(dominant_distribution),
        "max_dominant_channel_share": max(shares) if shares else None,
        "mean_dominant_channel_share": sum(shares) / len(shares) if shares else None,
        "rows_with_dominant_channel_phase_exposure": dominant_distribution.get("phase_exposure", 0),
    }
    return refined_rows, dominance_stats


def refine_warning_rows(
    original_rows: list[dict[str, str]],
    warning_origin_rows: list[dict[str, str]],
    runner_refinement_version: str,
) -> list[dict[str, Any]]:
    origin_map = {row.get("warning_id", ""): row for row in warning_origin_rows}
    refined_rows: list[dict[str, Any]] = []
    for row in original_rows:
        refined = dict(row)
        mapped = origin_map.get(row.get("warning_id", ""), {})
        granularity = mapped.get("warning_granularity", "")
        active = safe_int(row.get("active_count")) > 0
        refined.update(
            {
                "warning_origin": mapped.get("warning_origin", "d1m_output_warning"),
                "warning_granularity": granularity or "channel_level",
                "inherited_from": mapped.get("inherited_from", "D1m"),
                "broadcast_warning_flag": granularity == "global_broadcast" and active,
                "interpretation_boundary_refined": "Refined warning metadata qualifies D1m output semantics only.",
                "runner_refinement_version": runner_refinement_version,
            }
        )
        refined_rows.append(refined)
    return refined_rows


def refine_channel_rows(
    original_rows: list[dict[str, str]],
    channel_semantics_rows: list[dict[str, str]],
    runner_refinement_version: str,
) -> list[dict[str, Any]]:
    semantics_map = {row.get("channel_id", ""): row for row in channel_semantics_rows}
    refined_rows: list[dict[str, Any]] = []
    for row in original_rows:
        refined = dict(row)
        mapped = semantics_map.get(row.get("channel_id", ""), {})
        score_granularity = mapped.get("score_granularity", "")
        refined.update(
            {
                "score_granularity": score_granularity,
                "warning_granularity": mapped.get("warning_granularity", ""),
                "broadcast_warning_flag": safe_bool(mapped.get("broadcast_warning_flag")),
                "interpretation_role": mapped.get("interpretation_role", ""),
                "refinement_needed": safe_bool(mapped.get("refinement_needed")),
                "recommended_change": mapped.get("recommended_change", ""),
                "aggregate_broadcast_score_flag": score_granularity == "aggregate_broadcast",
                "runner_refinement_version": runner_refinement_version,
            }
        )
        refined_rows.append(refined)
    return refined_rows


def build_dominance_summary(
    threshold: float,
    dominance_stats: dict[str, Any],
    d1m_summary: dict[str, Any],
    runner_refinement_version: str,
) -> list[dict[str, Any]]:
    distribution = json.dumps(dominance_stats["dominant_channel_distribution"], sort_keys=True)
    boundary = "Dominance metadata is descriptive diagnostic metadata only."
    return [
        {
            "dominance_metric": "single_channel_dominance_threshold",
            "value": threshold,
            "description": "Threshold used for single-channel dominance warning.",
            "interpretation_boundary": boundary,
            "runner_refinement_version": runner_refinement_version,
        },
        {
            "dominance_metric": "dominant_channel_distribution",
            "value": distribution,
            "description": "Distribution of dominant_channel_id in refined rows.",
            "interpretation_boundary": boundary,
            "runner_refinement_version": runner_refinement_version,
        },
        {
            "dominance_metric": "max_dominant_channel_share",
            "value": dominance_stats["max_dominant_channel_share"],
            "description": "Largest calculated dominant channel share.",
            "interpretation_boundary": boundary,
            "runner_refinement_version": runner_refinement_version,
        },
        {
            "dominance_metric": "mean_dominant_channel_share",
            "value": dominance_stats["mean_dominant_channel_share"],
            "description": "Mean calculated dominant channel share.",
            "interpretation_boundary": boundary,
            "runner_refinement_version": runner_refinement_version,
        },
        {
            "dominance_metric": "rows_crossing_dominance_threshold",
            "value": dominance_stats["rows_crossing_dominance_threshold"],
            "description": "Rows whose dominant_channel_share crosses the threshold.",
            "interpretation_boundary": boundary,
            "runner_refinement_version": runner_refinement_version,
        },
        {
            "dominance_metric": "rows_with_dominant_channel_phase_exposure",
            "value": dominance_stats["rows_with_dominant_channel_phase_exposure"],
            "description": "Rows where dominant_channel_id is phase_exposure.",
            "interpretation_boundary": boundary,
            "runner_refinement_version": runner_refinement_version,
        },
        {
            "dominance_metric": "d1m_summary_single_channel_dominance_warning",
            "value": d1m_summary.get("single_channel_dominance_warning", False),
            "description": "Original D1m summary-level dominance warning.",
            "interpretation_boundary": boundary,
            "runner_refinement_version": runner_refinement_version,
        },
        {
            "dominance_metric": "dominance_interpretation_note",
            "value": DOMINANCE_NOTE,
            "description": "Clarifies label versus threshold semantics.",
            "interpretation_boundary": boundary,
            "runner_refinement_version": runner_refinement_version,
        },
    ]


def label_counts(rows: list[dict[str, str]]) -> dict[str, int]:
    return dict(Counter(row.get("profile_decision_label", "") for row in rows))


def build_comparison_rows(
    d1m_summary: dict[str, Any],
    refined_rows: list[dict[str, Any]],
    dominance_stats: dict[str, Any],
    refined_active_warning_count: int,
) -> list[dict[str, Any]]:
    original_counts = d1m_summary.get("profile_decision_label_counts", {})
    refined_counts = label_counts(refined_rows)
    original_case_count = d1m_summary.get("case_count")
    refined_case_count = len(refined_rows)
    boundary = "Comparison tracks schema and metadata changes only."
    items = [
        ("case_count", original_case_count, refined_case_count),
        ("profile_decision_label_counts", json.dumps(original_counts, sort_keys=True), json.dumps(refined_counts, sort_keys=True)),
        ("active_warning_count", d1m_summary.get("active_warning_count"), refined_active_warning_count),
        ("single_channel_dominance_warning", d1m_summary.get("single_channel_dominance_warning"), dominance_stats["rows_crossing_dominance_threshold"] > 0),
        ("output_schema_extended", "false", "true"),
        ("warning_origin_metadata_added", "false", "true"),
        ("warning_granularity_metadata_added", "false", "true"),
        ("dominance_share_metadata_added", "false", "true"),
        ("output_tracking_policy_added", "false", "true"),
    ]
    return [
        {
            "comparison_item": name,
            "original_d1m_value": original,
            "refined_d1o_value": refined,
            "changed": str(original) != str(refined),
            "interpretation_boundary": boundary,
        }
        for name, original, refined in items
    ]


def artifact_status(path: Path) -> dict[str, Any]:
    status: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "bytes": path.stat().st_size if path.exists() else 0,
    }
    if path.exists() and path.suffix == ".csv":
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            status["row_count"] = sum(1 for _ in reader)
            status["field_count"] = len(reader.fieldnames or [])
    return status


def write_readout(
    path: Path,
    summary: dict[str, Any],
    output_files: dict[str, str],
) -> None:
    file_lines = [f"- {name}" for name in output_files.values()]
    text = "\n".join(
        [
            "# QSB-ST COMP01-D1o D1m Refined Multi-Channel Profile \u2014 Readout",
            "",
            "## 1. Purpose",
            "D1o refines D1m output metadata only. D1o does not modify original D1m outputs and does not rerun D1m.",
            "",
            "## 2. Inputs",
            f"- original_d1m_case_count: {summary['original_d1m_case_count']}",
            f"- refined_case_count: {summary['refined_case_count']}",
            "- D1n warning-origin, channel-semantics, and dominance-semantics audit artifacts were used as metadata maps.",
            "",
            "## 3. Refinement summary",
            f"- runner_refinement_version: {summary['runner_refinement_version']}",
            f"- single_channel_dominance_threshold: {summary['single_channel_dominance_threshold']}",
            f"- rows_crossing_dominance_threshold: {summary['rows_crossing_dominance_threshold']}",
            "- warning-qualified output remains warning-qualified.",
            "",
            "## 4. Warning-origin and granularity summary",
            f"- warning_origin_counts: {summary['warning_origin_counts']}",
            f"- warning_granularity_counts: {summary['warning_granularity_counts']}",
            f"- broadcast_warning_count: {summary['broadcast_warning_count']}",
            f"- case_level_warning_count: {summary['case_level_warning_count']}",
            "",
            "## 5. Dominance summary",
            f"- dominant_channel_distribution: {summary['dominant_channel_distribution']}",
            "- dominant_channel_id remains descriptive.",
            "- single_channel_dominance_warning is threshold-based.",
            "",
            "## 6. Channel-semantics refinement",
            f"- aggregate_broadcast_channel_count: {summary['aggregate_broadcast_channel_count']}",
            f"- case_level_channel_count: {summary['case_level_channel_count']}",
            "- aggregate-broadcast channel origins are marked explicitly.",
            "",
            "## 7. Comparison to original D1m",
            f"- original_d1m_active_warning_count: {summary['original_d1m_active_warning_count']}",
            f"- refined_active_warning_count: {summary['refined_active_warning_count']}",
            "- D1o extends schema/metadata; it does not reinterpret D1m into physical evidence.",
            "",
            "## 8. Befund",
            "D1o created a refined metadata view of D1m outputs. It preserves decisions and warning-qualified interpretation while exposing warning origin, warning granularity, broadcast status, and dominance semantics.",
            "",
            "## 9. Interpretation",
            "The refined output is a semantic aid. It is not a score-tuning step and not a physical-model validation step.",
            "",
            "## 10. Hypothese",
            "Explicit metadata can make the D1m warning-qualified profile easier to audit without changing the synthetic diagnostic claim boundary.",
            "",
            "## 11. Offene L\u00fccke",
            "- no real data",
            "- no physical-model validation",
            "- no physical phase",
            "- no physical wavefunction",
            "- no physical spacetime geometry",
            "- no diagnostic specificity",
            "- D1m warnings remain active",
            "- Mastermind/Knuth/manifold remain parked",
            "",
            "## 12. Claim Boundary",
            "- specificity_established: false",
            "- phase_is_physical: false",
            "- phase_is_synthetic_diagnostic: true",
            "- Mastermind status: parked_not_implemented",
            "- Knuth status: parked_not_implemented",
            "- manifold status: parked_not_implemented",
            "",
            "## 13. Files created",
            *file_lines,
            "",
        ]
    )
    path.write_text(text, encoding="utf-8")


def main() -> int:
    args = parse_args()
    root = repo_root()
    config_path = resolve_path(root, args.config)
    if config_path is None:
        raise SystemExit("Config path is required.")
    config = read_yaml(config_path)
    runner_refinement_version = str(config.get("runner_refinement_version", "d1o_refined_semantics_v1"))
    threshold = safe_float((config.get("refinement") or {}).get("single_channel_dominance_threshold"))
    if threshold is None:
        threshold = 0.80

    input_paths = {
        key: resolve_path(root, value)
        for key, value in (config.get("input_paths") or {}).items()
    }
    resolved_inputs = {key: value for key, value in input_paths.items() if value is not None}
    ensure_inputs_exist(resolved_inputs)

    d1m_summary = read_json(resolved_inputs["d1m_original_summary"])
    d1n_summary = read_json(resolved_inputs["d1n_summary"])
    _ = resolved_inputs["d1n_output_tracking_policy"].read_text(encoding="utf-8")
    original_profile_rows, profile_fields = read_csv_rows(resolved_inputs["d1m_original_profile_case_summary"])
    original_channel_rows, channel_fields = read_csv_rows(resolved_inputs["d1m_original_channel_summary"])
    original_control_rows, _ = read_csv_rows(resolved_inputs["d1m_original_control_family_summary"])
    original_warning_rows, warning_fields = read_csv_rows(resolved_inputs["d1m_original_warning_taxonomy_summary"])
    warning_origin_rows, _ = read_csv_rows(resolved_inputs["d1n_warning_origin_summary"])
    channel_semantics_rows, _ = read_csv_rows(resolved_inputs["d1n_channel_semantics_audit"])
    _dominance_semantics_rows, _ = read_csv_rows(resolved_inputs["d1n_dominance_semantics_audit"])
    _ = original_control_rows  # read to confirm input availability.

    refined_profile_rows, dominance_stats = refine_profile_rows(
        original_profile_rows,
        warning_origin_rows,
        threshold,
        runner_refinement_version,
    )
    refined_warning_rows = refine_warning_rows(original_warning_rows, warning_origin_rows, runner_refinement_version)
    refined_channel_rows = refine_channel_rows(original_channel_rows, channel_semantics_rows, runner_refinement_version)
    dominance_rows = build_dominance_summary(threshold, dominance_stats, d1m_summary, runner_refinement_version)

    warning_origin_counts = d1n_summary.get("warning_origin_counts") or global_origin_counts(warning_origin_rows)
    warning_granularity_counts = d1n_summary.get("warning_granularity_counts") or global_granularity_counts(warning_origin_rows)
    refined_active_warning_count = int(d1m_summary.get("active_warning_count", 0))
    comparison_rows = build_comparison_rows(
        d1m_summary,
        refined_profile_rows,
        dominance_stats,
        refined_active_warning_count,
    )

    aggregate_broadcast_channel_count = sum(
        1 for row in refined_channel_rows if safe_bool(row.get("aggregate_broadcast_score_flag"))
    )
    case_level_channel_count = sum(
        1 for row in refined_channel_rows if row.get("score_granularity") == "case_level"
    )

    output_dir = resolve_path(root, config.get("output_dir"))
    if output_dir is None:
        raise SystemExit("Config output_dir is required.")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_config = config.get("output_files") or {}
    output_files = {
        "summary_json": output_config.get("summary_json", "summary.json"),
        "readout_md": output_config.get("readout_md", "readout.md"),
        "profile_case_summary_csv": output_config.get("profile_case_summary_csv", "profile_case_summary.csv"),
        "channel_summary_csv": output_config.get("channel_summary_csv", "channel_summary.csv"),
        "warning_taxonomy_summary_csv": output_config.get("warning_taxonomy_summary_csv", "warning_taxonomy_summary.csv"),
        "dominance_summary_csv": output_config.get("dominance_summary_csv", "dominance_summary.csv"),
        "refinement_comparison_summary_csv": output_config.get("refinement_comparison_summary_csv", "refinement_comparison_summary.csv"),
        "resolved_config_json": output_config.get("resolved_config_json", "resolved_config.json"),
    }

    profile_output_fields = append_fields(profile_fields, PROFILE_EXTRA_FIELDS)
    channel_output_fields = append_fields(channel_fields, CHANNEL_EXTRA_FIELDS)
    warning_output_fields = append_fields(warning_fields, WARNING_EXTRA_FIELDS)

    write_csv(output_dir / output_files["profile_case_summary_csv"], profile_output_fields, refined_profile_rows)
    write_csv(output_dir / output_files["channel_summary_csv"], channel_output_fields, refined_channel_rows)
    write_csv(output_dir / output_files["warning_taxonomy_summary_csv"], warning_output_fields, refined_warning_rows)
    write_csv(output_dir / output_files["dominance_summary_csv"], DOMINANCE_FIELDS, dominance_rows)
    write_csv(output_dir / output_files["refinement_comparison_summary_csv"], COMPARISON_FIELDS, comparison_rows)

    claim_boundary = dict(config.get("claim_boundary") or {})
    summary = {
        "block_id": config.get("block_id", "QSB-ST-COMP01D1O"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "runner_refinement_version": runner_refinement_version,
        "input_artifacts": {key: artifact_status(value) for key, value in resolved_inputs.items()},
        "original_d1m_case_count": int(d1m_summary.get("case_count", len(original_profile_rows))),
        "refined_case_count": len(refined_profile_rows),
        "original_d1m_joined_case_count": int(d1m_summary.get("joined_case_count", len(original_profile_rows))),
        "refined_joined_case_count": len(refined_profile_rows),
        "original_d1m_active_warning_count": int(d1m_summary.get("active_warning_count", 0)),
        "refined_active_warning_count": refined_active_warning_count,
        "original_profile_decision_label_counts": d1m_summary.get("profile_decision_label_counts", {}),
        "refined_profile_decision_label_counts": label_counts(refined_profile_rows),
        "single_channel_dominance_threshold": threshold,
        "rows_crossing_dominance_threshold": dominance_stats["rows_crossing_dominance_threshold"],
        "dominant_channel_distribution": dominance_stats["dominant_channel_distribution"],
        "warning_origin_counts": warning_origin_counts,
        "warning_granularity_counts": warning_granularity_counts,
        "broadcast_warning_count": d1n_summary.get("broadcast_warning_count", 0),
        "case_level_warning_count": d1n_summary.get("case_level_warning_count", 0),
        "family_level_warning_count": warning_granularity_counts.get("family_level", 0),
        "channel_level_warning_count": warning_granularity_counts.get("channel_level", 0),
        "input_level_warning_count": warning_granularity_counts.get("input_level", 0),
        "claim_boundary_warning_count": warning_granularity_counts.get("claim_boundary", 0),
        "aggregate_broadcast_channel_count": aggregate_broadcast_channel_count,
        "case_level_channel_count": case_level_channel_count,
        "output_tracking_policy": d1n_summary.get(
            "output_tracking_recommendation",
            "keep_config_runner_and_result_notes_tracked_leave_full_runs_untracked_by_default",
        ),
        "specificity_established": False,
        "phase_is_physical": False,
        "phase_is_synthetic_diagnostic": True,
        "mastermind_status": claim_boundary.get("mastermind_status", "parked_not_implemented"),
        "knuth_status": claim_boundary.get("knuth_status", "parked_not_implemented"),
        "manifold_status": claim_boundary.get("manifold_status", "parked_not_implemented"),
        "runner_scope": "synthetic diagnostic D1m metadata refinement",
        "claim_boundary": claim_boundary,
        "output_files": {key: str(output_dir / value) for key, value in output_files.items()},
    }

    (output_dir / output_files["summary_json"]).write_text(
        json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    resolved_config = {
        "config": config,
        "config_path": str(config_path),
        "repo_root": str(root),
        "resolved_input_paths": {key: str(value) for key, value in resolved_inputs.items()},
    }
    (output_dir / output_files["resolved_config_json"]).write_text(
        json.dumps(resolved_config, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_readout(output_dir / output_files["readout_md"], summary, output_files)

    print("QSB-ST COMP01-D1o refined D1m metadata run complete")
    print(f"output_dir: {output_dir}")
    print(f"refined_case_count: {len(refined_profile_rows)}")
    print(f"rows_crossing_dominance_threshold: {dominance_stats['rows_crossing_dominance_threshold']}")
    print(f"runner_refinement_version: {runner_refinement_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
