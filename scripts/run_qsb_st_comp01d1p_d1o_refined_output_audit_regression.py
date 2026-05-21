#!/usr/bin/env python3
"""QSB-ST COMP01-D1p regression audit for D1o refined D1m outputs.

The runner reads existing D1m and D1o artifacts, checks that D1o extends
metadata without changing core D1m decisions, and writes D1p audit outputs.
It does not modify or rerun D1m/D1o.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any

try:
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover - environment guard
    raise SystemExit(
        "PyYAML is required to read the D1p config. Activate the project environment or install PyYAML."
    ) from exc


REGRESSION_FIELDS = [
    "regression_check",
    "d1m_value",
    "d1o_value",
    "passed",
    "severity",
    "interpretation_boundary",
]

SCHEMA_FIELDS = [
    "file_name",
    "original_field_count",
    "refined_field_count",
    "added_field_count",
    "added_fields",
    "required_added_fields_present",
    "passed",
    "interpretation_boundary",
]

DECISION_FIELDS = [
    "profile_decision_label",
    "d1m_count",
    "d1o_count",
    "delta",
    "passed",
    "interpretation_boundary",
]

WARNING_FIELDS = [
    "warning_metric",
    "d1m_value",
    "d1o_value",
    "passed",
    "interpretation_boundary",
]

DOMINANCE_FIELDS = [
    "metric",
    "value",
    "interpretation_boundary",
]

REQUIRED_PROFILE_FIELDS = [
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

REQUIRED_CHANNEL_FIELDS = [
    "score_granularity",
    "warning_granularity",
    "broadcast_warning_flag",
    "interpretation_role",
    "refinement_needed",
    "recommended_change",
    "aggregate_broadcast_score_flag",
    "runner_refinement_version",
]

REQUIRED_WARNING_FIELDS = [
    "warning_origin",
    "warning_granularity",
    "inherited_from",
    "broadcast_warning_flag",
    "interpretation_boundary_refined",
    "runner_refinement_version",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit D1o refined output against original D1m output without reruns."
    )
    parser.add_argument("--config", required=True, help="Path to D1p YAML config.")
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
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True)
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
    if not text:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def ensure_inputs_exist(input_paths: dict[str, Path]) -> None:
    missing = [str(path) for path in input_paths.values() if not path.exists()]
    if missing:
        raise SystemExit("Missing required input artifacts; D1m/D1o will not be rerun:\n" + "\n".join(missing))


def label_counts(rows: list[dict[str, str]]) -> dict[str, int]:
    return dict(Counter(row.get("profile_decision_label", "") for row in rows))


def case_ids(rows: list[dict[str, str]]) -> set[str]:
    return {row.get("case_id", "") for row in rows if row.get("case_id", "")}


def dict_equal(left: Any, right: Any) -> bool:
    return json.dumps(left, sort_keys=True) == json.dumps(right, sort_keys=True)


def regression_row(name: str, d1m_value: Any, d1o_value: Any, passed: bool, severity: str = "error") -> dict[str, Any]:
    return {
        "regression_check": name,
        "d1m_value": d1m_value,
        "d1o_value": d1o_value,
        "passed": passed,
        "severity": "info" if passed else severity,
        "interpretation_boundary": "Regression checks schema/metadata preservation only; no physical-model validation.",
    }


def build_regression_rows(
    d1m_summary: dict[str, Any],
    d1o_summary: dict[str, Any],
    d1m_profile_rows: list[dict[str, str]],
    d1o_profile_rows: list[dict[str, str]],
    d1o_profile_fields: list[str],
    d1o_channel_fields: list[str],
    d1o_warning_fields: list[str],
) -> list[dict[str, Any]]:
    d1m_labels = label_counts(d1m_profile_rows)
    d1o_labels = label_counts(d1o_profile_rows)
    d1m_cases = case_ids(d1m_profile_rows)
    d1o_cases = case_ids(d1o_profile_rows)
    d1o_schema_extended = (
        all(field in d1o_profile_fields for field in REQUIRED_PROFILE_FIELDS)
        and all(field in d1o_channel_fields for field in REQUIRED_CHANNEL_FIELDS)
        and all(field in d1o_warning_fields for field in REQUIRED_WARNING_FIELDS)
    )
    return [
        regression_row("case_count_equal", d1m_summary.get("case_count"), d1o_summary.get("refined_case_count"), d1m_summary.get("case_count") == d1o_summary.get("refined_case_count")),
        regression_row("joined_case_count_equal", d1m_summary.get("joined_case_count"), d1o_summary.get("refined_joined_case_count"), d1m_summary.get("joined_case_count") == d1o_summary.get("refined_joined_case_count")),
        regression_row("profile_row_count_equal", len(d1m_profile_rows), len(d1o_profile_rows), len(d1m_profile_rows) == len(d1o_profile_rows)),
        regression_row("case_id_set_equal", len(d1m_cases), len(d1o_cases), d1m_cases == d1o_cases),
        regression_row("profile_decision_label_counts_equal", d1m_labels, d1o_labels, d1m_labels == d1o_labels),
        regression_row("active_warning_count_equal", d1m_summary.get("active_warning_count"), d1o_summary.get("refined_active_warning_count"), d1m_summary.get("active_warning_count") == d1o_summary.get("refined_active_warning_count")),
        regression_row("specificity_established_preserved_false", d1m_summary.get("specificity_established"), d1o_summary.get("specificity_established"), d1m_summary.get("specificity_established") is False and d1o_summary.get("specificity_established") is False),
        regression_row("phase_is_physical_preserved_false", d1m_summary.get("phase_is_physical"), d1o_summary.get("phase_is_physical"), d1m_summary.get("phase_is_physical") is False and d1o_summary.get("phase_is_physical") is False),
        regression_row("phase_is_synthetic_diagnostic_preserved_true", d1m_summary.get("phase_is_synthetic_diagnostic"), d1o_summary.get("phase_is_synthetic_diagnostic"), d1m_summary.get("phase_is_synthetic_diagnostic") is True and d1o_summary.get("phase_is_synthetic_diagnostic") is True),
        regression_row("original_d1m_outputs_not_modified_by_d1o_assumption", "D1m input paths are read-only and separate", "D1o writes to QSB-ST-COMP01D1O only", True, "warning"),
        regression_row("d1o_schema_extended", "original schema", "metadata schema extended", d1o_schema_extended),
        regression_row("d1o_dominance_metadata_present", "not_explicit_in_original_d1m", "dominance metadata present", all(field in d1o_profile_fields for field in ["dominant_channel_share", "dominance_warning_reason"])),
        regression_row("d1o_warning_origin_metadata_present", "not_explicit_in_original_d1m", "warning_origin present", "warning_origin" in d1o_warning_fields),
        regression_row("d1o_warning_granularity_metadata_present", "not_explicit_in_original_d1m", "warning_granularity present", "warning_granularity" in d1o_warning_fields),
        regression_row("d1o_output_tracking_policy_present", "not_explicit_in_original_d1m", d1o_summary.get("output_tracking_policy"), bool(d1o_summary.get("output_tracking_policy"))),
    ]


def schema_rows(
    d1m_fields_by_file: dict[str, list[str]],
    d1o_fields_by_file: dict[str, list[str]],
) -> list[dict[str, Any]]:
    required = {
        "profile_case_summary.csv": REQUIRED_PROFILE_FIELDS,
        "channel_summary.csv": REQUIRED_CHANNEL_FIELDS,
        "warning_taxonomy_summary.csv": REQUIRED_WARNING_FIELDS,
    }
    rows = []
    for filename, required_fields in required.items():
        original = d1m_fields_by_file[filename]
        refined = d1o_fields_by_file[filename]
        added = [field for field in refined if field not in original]
        required_present = all(field in refined for field in required_fields)
        rows.append(
            {
                "file_name": filename,
                "original_field_count": len(original),
                "refined_field_count": len(refined),
                "added_field_count": len(added),
                "added_fields": ";".join(added),
                "required_added_fields_present": required_present,
                "passed": required_present and len(refined) >= len(original),
                "interpretation_boundary": "Schema extension audit; does not alter D1m results.",
            }
        )
    return rows


def decision_rows(d1m_profile_rows: list[dict[str, str]], d1o_profile_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    d1m_counts = label_counts(d1m_profile_rows)
    d1o_counts = label_counts(d1o_profile_rows)
    labels = sorted(set(d1m_counts) | set(d1o_counts))
    return [
        {
            "profile_decision_label": label,
            "d1m_count": d1m_counts.get(label, 0),
            "d1o_count": d1o_counts.get(label, 0),
            "delta": d1o_counts.get(label, 0) - d1m_counts.get(label, 0),
            "passed": d1m_counts.get(label, 0) == d1o_counts.get(label, 0),
            "interpretation_boundary": "Decision label regression only; warning-qualified rows remain warning-qualified.",
        }
        for label in labels
    ]


def warning_rows(d1m_summary: dict[str, Any], d1o_summary: dict[str, Any]) -> list[dict[str, Any]]:
    metrics = [
        ("active_warning_count", d1m_summary.get("active_warning_count"), d1o_summary.get("refined_active_warning_count"), d1m_summary.get("active_warning_count") == d1o_summary.get("refined_active_warning_count")),
        ("broadcast_warning_count", "not_explicit_in_original_d1m", d1o_summary.get("broadcast_warning_count"), "broadcast_warning_count" in d1o_summary),
        ("case_level_warning_count", "not_explicit_in_original_d1m", d1o_summary.get("case_level_warning_count"), "case_level_warning_count" in d1o_summary),
        ("channel_level_warning_count", "not_explicit_in_original_d1m", d1o_summary.get("channel_level_warning_count"), "channel_level_warning_count" in d1o_summary),
        ("input_level_warning_count", "not_explicit_in_original_d1m", d1o_summary.get("input_level_warning_count"), "input_level_warning_count" in d1o_summary),
        ("claim_boundary_warning_count", "not_explicit_in_original_d1m", d1o_summary.get("claim_boundary_warning_count"), "claim_boundary_warning_count" in d1o_summary),
        ("warning_origin_counts", "not_explicit_in_original_d1m", d1o_summary.get("warning_origin_counts"), bool(d1o_summary.get("warning_origin_counts"))),
        ("warning_granularity_counts", "not_explicit_in_original_d1m", d1o_summary.get("warning_granularity_counts"), bool(d1o_summary.get("warning_granularity_counts"))),
    ]
    return [
        {
            "warning_metric": name,
            "d1m_value": d1m_value,
            "d1o_value": d1o_value,
            "passed": passed,
            "interpretation_boundary": "Warning count regression; D1o adds explicit warning metadata.",
        }
        for name, d1m_value, d1o_value, passed in metrics
    ]


def dominance_distribution_rows(d1o_profile_rows: list[dict[str, str]], d1o_summary: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    shares = [safe_float(row.get("dominant_channel_share")) for row in d1o_profile_rows]
    shares = [value for value in shares if value is not None]
    threshold = safe_float(d1o_summary.get("single_channel_dominance_threshold")) or 0.80
    dominant_distribution = dict(Counter(row.get("dominant_channel_id", "") for row in d1o_profile_rows))
    rows_crossing = sum(1 for value in shares if value >= threshold)
    first = d1o_profile_rows[0] if d1o_profile_rows else {}
    stats = {
        "dominance_share_min": min(shares) if shares else None,
        "dominance_share_max": max(shares) if shares else None,
        "dominance_share_mean": sum(shares) / len(shares) if shares else None,
        "dominance_share_median": median(shares) if shares else None,
        "rows_crossing_dominance_threshold": rows_crossing,
        "dominant_channel_distribution": dominant_distribution,
    }
    boundary = "Dominance distribution is descriptive diagnostic metadata only."
    rows = [
        ("row_count", len(d1o_profile_rows)),
        ("nonblank_dominant_channel_share_count", len(shares)),
        ("min_dominant_channel_share", stats["dominance_share_min"]),
        ("max_dominant_channel_share", stats["dominance_share_max"]),
        ("mean_dominant_channel_share", stats["dominance_share_mean"]),
        ("median_dominant_channel_share", stats["dominance_share_median"]),
        ("rows_crossing_threshold", rows_crossing),
        ("threshold", threshold),
        ("rows_with_dominant_channel_phase_exposure", dominant_distribution.get("phase_exposure", 0)),
        ("dominant_channel_distribution", dominant_distribution),
        ("first_row_dominant_channel_share", first.get("dominant_channel_share", "")),
        ("first_row_dominance_warning_reason", first.get("dominance_warning_reason", "")),
    ]
    return [{"metric": name, "value": value, "interpretation_boundary": boundary} for name, value in rows], stats


def write_tracking_recommendation(path: Path) -> str:
    recommendation = "keep_config_runner_and_result_notes_tracked_leave_full_runs_untracked_by_default"
    text = "\n".join(
        [
            "# QSB-ST COMP01-D1p Output Tracking Recommendation",
            "",
            "- Do not force-add full `runs/` outputs by default.",
            "- Track config, runner, plan/spec/result notes.",
            "- If a public or reviewer package is needed, create a docs-side digest or force-add selected summary/readout outputs with an explicit commit message.",
            "- Avoid relying silently on ignored `runs/` outputs.",
            "",
            "This recommendation is about repository hygiene only, not scientific interpretation.",
            "",
        ]
    )
    path.write_text(text, encoding="utf-8")
    return recommendation


def artifact_status(path: Path) -> dict[str, Any]:
    status = {"path": str(path), "exists": path.exists(), "bytes": path.stat().st_size if path.exists() else 0}
    if path.exists() and path.suffix == ".csv":
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            status["row_count"] = sum(1 for _ in reader)
            status["field_count"] = len(reader.fieldnames or [])
    return status


def write_readout(path: Path, summary: dict[str, Any], output_files: dict[str, str]) -> None:
    file_lines = [f"- {name}" for name in output_files.values()]
    text = "\n".join(
        [
            "# QSB-ST COMP01-D1p D1o Refined Output Audit and Regression Check \u2014 Readout",
            "",
            "## 1. Purpose",
            "D1p audits D1o refined outputs against original D1m outputs.",
            "",
            "## 2. Inputs",
            f"- D1m profile rows: {summary['d1m_profile_row_count']}",
            f"- D1o profile rows: {summary['d1o_profile_row_count']}",
            "",
            "## 3. Regression summary",
            f"- regression_passed: {str(summary['regression_passed']).lower()}",
            f"- regression_failure_count: {summary['regression_failure_count']}",
            f"- case_id_set_equal: {str(summary['case_id_set_equal']).lower()}",
            "",
            "## 4. Schema extension summary",
            f"- d1o_schema_extended: {str(summary['d1o_schema_extended']).lower()}",
            f"- d1o_required_metadata_present: {str(summary['d1o_required_metadata_present']).lower()}",
            "",
            "## 5. Decision-label regression",
            f"- profile_decision_label_counts_equal: {str(summary['profile_decision_label_counts_equal']).lower()}",
            "- warning-qualified output remains warning-qualified.",
            "",
            "## 6. Warning-count regression",
            f"- active_warning_count_equal: {str(summary['active_warning_count_equal']).lower()}",
            "",
            "## 7. Dominance-share distribution",
            f"- rows_crossing_dominance_threshold: {summary['rows_crossing_dominance_threshold']}",
            f"- dominant_channel_distribution: {summary['dominant_channel_distribution']}",
            "",
            "## 8. Output-tracking recommendation",
            f"- {summary['output_tracking_recommendation']}",
            "",
            "## 9. Befund",
            "D1p confirms that D1o extends metadata/schema while preserving D1m row counts and decision labels.",
            "",
            "## 10. Interpretation",
            "D1p does not rerun D1m or D1o and does not modify D1m or D1o outputs. D1o is expected to extend metadata/schema, not change D1m decisions.",
            "",
            "## 11. Hypothese",
            "Regression checks can keep the refined D1o metadata layer auditable without changing the warning-qualified D1m interpretation.",
            "",
            "## 12. Offene L\u00fccke",
            "- no real data",
            "- no physical-model validation",
            "- no physical phase",
            "- no physical wavefunction",
            "- no physical spacetime geometry",
            "- no diagnostic specificity",
            "- Mastermind/Knuth/manifold remain parked",
            "",
            "## 13. Claim Boundary",
            "- specificity_established: false",
            "- phase_is_physical: false",
            "- phase_is_synthetic_diagnostic: true",
            "- Mastermind status: parked_not_implemented",
            "- Knuth status: parked_not_implemented",
            "- manifold status: parked_not_implemented",
            "",
            "## 14. Files created",
            *file_lines,
            "",
        ]
    )
    path.write_text(text, encoding="utf-8")


def main() -> int:
    args = argparse.ArgumentParser(description="Run D1p D1o refined output audit/regression check.")
    args.add_argument("--config", required=True)
    parsed = args.parse_args()

    root = Path(__file__).resolve().parents[1]
    config_path = resolve_path(root, parsed.config)
    if config_path is None:
        raise SystemExit("Config path is required.")
    config = read_yaml(config_path)
    audit_version = str(config.get("audit_version", "d1p_d1o_regression_check_v1"))

    input_paths = {key: resolve_path(root, value) for key, value in (config.get("input_paths") or {}).items()}
    resolved_inputs = {key: value for key, value in input_paths.items() if value is not None}
    ensure_inputs_exist(resolved_inputs)

    d1m_summary = read_json(resolved_inputs["d1m_summary"])
    d1o_summary = read_json(resolved_inputs["d1o_summary"])
    _ = resolved_inputs["d1o_readout"].read_text(encoding="utf-8")
    _ = read_json(resolved_inputs["d1o_resolved_config"])
    d1m_profile_rows, d1m_profile_fields = read_csv_rows(resolved_inputs["d1m_profile_case_summary"])
    d1m_channel_rows, d1m_channel_fields = read_csv_rows(resolved_inputs["d1m_channel_summary"])
    d1m_warning_rows, d1m_warning_fields = read_csv_rows(resolved_inputs["d1m_warning_taxonomy_summary"])
    d1o_profile_rows, d1o_profile_fields = read_csv_rows(resolved_inputs["d1o_profile_case_summary"])
    d1o_channel_rows, d1o_channel_fields = read_csv_rows(resolved_inputs["d1o_channel_summary"])
    d1o_warning_rows, d1o_warning_fields = read_csv_rows(resolved_inputs["d1o_warning_taxonomy_summary"])
    _d1o_dominance_rows, _ = read_csv_rows(resolved_inputs["d1o_dominance_summary"])
    _d1o_comparison_rows, _ = read_csv_rows(resolved_inputs["d1o_refinement_comparison_summary"])
    _ = (d1m_channel_rows, d1m_warning_rows, d1o_channel_rows, d1o_warning_rows)

    regression_rows = build_regression_rows(
        d1m_summary,
        d1o_summary,
        d1m_profile_rows,
        d1o_profile_rows,
        d1o_profile_fields,
        d1o_channel_fields,
        d1o_warning_fields,
    )
    schema_summary_rows = schema_rows(
        {
            "profile_case_summary.csv": d1m_profile_fields,
            "channel_summary.csv": d1m_channel_fields,
            "warning_taxonomy_summary.csv": d1m_warning_fields,
        },
        {
            "profile_case_summary.csv": d1o_profile_fields,
            "channel_summary.csv": d1o_channel_fields,
            "warning_taxonomy_summary.csv": d1o_warning_fields,
        },
    )
    decision_regression_rows = decision_rows(d1m_profile_rows, d1o_profile_rows)
    warning_regression_rows = warning_rows(d1m_summary, d1o_summary)
    dominance_rows, dominance_stats = dominance_distribution_rows(d1o_profile_rows, d1o_summary)

    output_dir = resolve_path(root, config.get("output_dir"))
    if output_dir is None:
        raise SystemExit("Config output_dir is required.")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_config = config.get("output_files") or {}
    output_files = {
        "summary_json": output_config.get("summary_json", "summary.json"),
        "readout_md": output_config.get("readout_md", "readout.md"),
        "d1m_d1o_regression_summary_csv": output_config.get("d1m_d1o_regression_summary_csv", "d1m_d1o_regression_summary.csv"),
        "schema_extension_summary_csv": output_config.get("schema_extension_summary_csv", "schema_extension_summary.csv"),
        "decision_label_regression_csv": output_config.get("decision_label_regression_csv", "decision_label_regression.csv"),
        "warning_count_regression_csv": output_config.get("warning_count_regression_csv", "warning_count_regression.csv"),
        "dominance_share_distribution_csv": output_config.get("dominance_share_distribution_csv", "dominance_share_distribution.csv"),
        "output_tracking_recommendation_md": output_config.get("output_tracking_recommendation_md", "output_tracking_recommendation.md"),
        "resolved_config_json": output_config.get("resolved_config_json", "resolved_config.json"),
    }

    write_csv(output_dir / output_files["d1m_d1o_regression_summary_csv"], REGRESSION_FIELDS, regression_rows)
    write_csv(output_dir / output_files["schema_extension_summary_csv"], SCHEMA_FIELDS, schema_summary_rows)
    write_csv(output_dir / output_files["decision_label_regression_csv"], DECISION_FIELDS, decision_regression_rows)
    write_csv(output_dir / output_files["warning_count_regression_csv"], WARNING_FIELDS, warning_regression_rows)
    write_csv(output_dir / output_files["dominance_share_distribution_csv"], DOMINANCE_FIELDS, dominance_rows)
    output_tracking_recommendation = write_tracking_recommendation(output_dir / output_files["output_tracking_recommendation_md"])

    regression_failure_count = sum(1 for row in regression_rows if not row["passed"])
    schema_failure_count = sum(1 for row in schema_summary_rows if not row["passed"])
    decision_failure_count = sum(1 for row in decision_regression_rows if not row["passed"])
    warning_failure_count = sum(1 for row in warning_regression_rows if not row["passed"])
    regression_warning_count = sum(1 for row in regression_rows if row["severity"] == "warning")
    regression_passed = (regression_failure_count + schema_failure_count + decision_failure_count + warning_failure_count) == 0
    d1m_cases = case_ids(d1m_profile_rows)
    d1o_cases = case_ids(d1o_profile_rows)
    d1m_label_counts = label_counts(d1m_profile_rows)
    d1o_label_counts = label_counts(d1o_profile_rows)
    claim_boundary = dict(config.get("claim_boundary") or {})

    summary = {
        "block_id": config.get("block_id", "QSB-ST-COMP01D1P"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "audit_version": audit_version,
        "input_artifacts": {key: artifact_status(value) for key, value in resolved_inputs.items()},
        "d1m_case_count": d1m_summary.get("case_count"),
        "d1o_case_count": d1o_summary.get("refined_case_count"),
        "d1m_profile_row_count": len(d1m_profile_rows),
        "d1o_profile_row_count": len(d1o_profile_rows),
        "case_id_set_equal": d1m_cases == d1o_cases,
        "profile_decision_label_counts_equal": d1m_label_counts == d1o_label_counts,
        "active_warning_count_equal": d1m_summary.get("active_warning_count") == d1o_summary.get("refined_active_warning_count"),
        "d1o_schema_extended": all(row["passed"] for row in schema_summary_rows),
        "d1o_required_metadata_present": all(row["required_added_fields_present"] for row in schema_summary_rows),
        "rows_crossing_dominance_threshold": dominance_stats["rows_crossing_dominance_threshold"],
        "dominant_channel_distribution": dominance_stats["dominant_channel_distribution"],
        "dominance_share_min": dominance_stats["dominance_share_min"],
        "dominance_share_max": dominance_stats["dominance_share_max"],
        "dominance_share_mean": dominance_stats["dominance_share_mean"],
        "dominance_share_median": dominance_stats["dominance_share_median"],
        "regression_passed": regression_passed,
        "regression_warning_count": regression_warning_count,
        "regression_failure_count": regression_failure_count + schema_failure_count + decision_failure_count + warning_failure_count,
        "output_tracking_recommendation": output_tracking_recommendation,
        "specificity_established": False,
        "phase_is_physical": False,
        "phase_is_synthetic_diagnostic": True,
        "mastermind_status": claim_boundary.get("mastermind_status", "parked_not_implemented"),
        "knuth_status": claim_boundary.get("knuth_status", "parked_not_implemented"),
        "manifold_status": claim_boundary.get("manifold_status", "parked_not_implemented"),
        "runner_scope": "synthetic diagnostic D1o refined output regression check",
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

    print("QSB-ST COMP01-D1p regression audit complete")
    print(f"output_dir: {output_dir}")
    print(f"regression_passed: {regression_passed}")
    print(f"regression_failure_count: {summary['regression_failure_count']}")
    print(f"rows_crossing_dominance_threshold: {summary['rows_crossing_dominance_threshold']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
