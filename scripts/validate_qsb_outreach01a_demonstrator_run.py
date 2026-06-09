#!/usr/bin/env python3
"""Validate QSB-OUTREACH01A synthetic demonstrator run outputs."""
from __future__ import annotations

import argparse
import csv
import importlib.util
import inspect
import json
from pathlib import Path


REQUIRED_FILES = {
    "resolved_config.json",
    "synthetic_states.csv",
    "relational_pairs.csv",
    "lag_profile.csv",
    "case_summary.csv",
    "status_summary.csv",
    "summary.json",
    "readout.md",
}

REQUIRED_STATE_COLUMNS = {
    "case_id",
    "event_instance_id",
    "cycle_index",
    "forcing_phase",
    "response_phase_class",
    "observable_value",
    "observable_vector_json",
    "background_state_json",
    "history_representation_type",
    "history_descriptor_json",
    "is_observed",
    "source_sequence_index",
    "random_seed",
    "transformation_version",
    "source_record_id",
    "source_checksum",
    "source_checksum_algorithm",
}

REQUIRED_PAIR_COLUMNS = {
    "case_id",
    "model_run_id",
    "model_version",
    "state_i_id",
    "state_j_id",
    "lag",
    "similarity_score",
    "observable_similarity",
    "forcing_phase_similarity_reference",
    "similarity_features_used",
    "excluded_similarity_features",
    "pair_logic",
    "source_type",
    "config_hash",
}

REQUIRED_LAG_COLUMNS = {
    "case_id",
    "lag",
    "pair_count",
    "median_similarity",
    "mean_similarity",
    "std_similarity",
    "window_count",
    "valid_window_count",
    "robustness_status",
}

REQUIRED_CASE_COLUMNS = {
    "case_id",
    "case_role",
    "expected_detection_family",
    "detected_status",
    "expected_control_outcome",
    "control_interpretation",
    "observed_fraction",
    "valid_window_fraction",
    "minimum_valid_pairs_met",
    "data_quality_status",
}

FORBIDDEN_DETECTOR_PARAMETERS = {
    "case_id",
    "case_role",
    "expected_status",
    "expected_detection_family",
    "control_interpretation",
}


def load_runner_module():
    script_path = Path(__file__).resolve().with_name("run_qsb_outreach01a_synthetic_demonstrator.py")
    spec = importlib.util.spec_from_file_location("qsb_outreach01a_synthetic_runner", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load synthetic demonstrator runner module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_detector_signature() -> list[str]:
    module = load_runner_module()
    function = getattr(module, "detect_status_from_metrics", None)
    if function is None:
        return ["detect_status_from_metrics function missing from runner"]
    signature = inspect.signature(function)
    parameter_names = set(signature.parameters)
    forbidden = sorted(parameter_names & FORBIDDEN_DETECTOR_PARAMETERS)
    if forbidden:
        return [f"detect_status_from_metrics has forbidden parameters: {forbidden}"]
    expected = ["metrics", "config"]
    if list(signature.parameters) != expected:
        return [f"detect_status_from_metrics signature is {signature}, expected (metrics, config)"]
    return []


def read_csv(path: Path) -> tuple[list[dict[str, str]], set[str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader), set(reader.fieldnames or [])


def ensure_columns(name: str, columns: set[str], required: set[str]) -> list[str]:
    missing = sorted(required - columns)
    return [f"{name} missing columns: {missing}"] if missing else []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    out = args.output_dir
    issues: list[str] = []

    missing_files = sorted(name for name in REQUIRED_FILES if not (out / name).exists())
    if missing_files:
        issues.append(f"Missing output files: {missing_files}")

    if not issues:
        issues.extend(validate_detector_signature())
        resolved_config = json.loads((out / "resolved_config.json").read_text(encoding="utf-8"))
        summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
        states, state_columns = read_csv(out / "synthetic_states.csv")
        pairs, pair_columns = read_csv(out / "relational_pairs.csv")
        lags, lag_columns = read_csv(out / "lag_profile.csv")
        case_rows, case_columns = read_csv(out / "case_summary.csv")

        issues.extend(ensure_columns("synthetic_states.csv", state_columns, REQUIRED_STATE_COLUMNS))
        issues.extend(ensure_columns("relational_pairs.csv", pair_columns, REQUIRED_PAIR_COLUMNS))
        issues.extend(ensure_columns("lag_profile.csv", lag_columns, REQUIRED_LAG_COLUMNS))
        issues.extend(ensure_columns("case_summary.csv", case_columns, REQUIRED_CASE_COLUMNS))

        event_ids = [row["event_instance_id"] for row in states]
        if len(event_ids) != len(set(event_ids)):
            issues.append("event_instance_id values are not unique")

        for row in states:
            json.loads(row["observable_vector_json"])
            json.loads(row["background_state_json"])
            json.loads(row["history_descriptor_json"])
            if row["source_checksum"] and not row["source_checksum_algorithm"]:
                issues.append("source_checksum without source_checksum_algorithm")
            if float(row["forcing_phase"]) != 0.0:
                issues.append("forcing_phase is not stroboscopic reference 0.0")

        observed_values = {row["observable_value"] for row in states if row["is_observed"] == "true"}
        if len(observed_values) < 2:
            issues.append("observable_value does not vary in observed synthetic data")

        seen_pairs: set[tuple[str, str]] = set()
        for row in pairs:
            left = row["state_i_id"]
            right = row["state_j_id"]
            if left == right:
                issues.append("self-pair found")
            if not left < right:
                issues.append("non-canonical pair order found")
            if (left, right) in seen_pairs or (right, left) in seen_pairs:
                issues.append("duplicate or mirror pair found")
            seen_pairs.add((left, right))
            score = float(row["similarity_score"])
            if not 0.0 <= score <= 1.0:
                issues.append("similarity_score outside [0,1]")
            if row["similarity_features_used"] != "observable_value":
                issues.append("similarity_features_used is not observable_value")
            excluded = set(row["excluded_similarity_features"].split(","))
            forbidden_inputs = {
                "forcing_phase",
                "response_phase_class",
                "observable_recurrence_class",
                "state_descriptor_id",
                "case_role",
            }
            if not forbidden_inputs.issubset(excluded):
                issues.append("forbidden truth-label or metadata fields are not listed as excluded")
            if float(row["forcing_phase_similarity_reference"]) != 1.0:
                issues.append("forcing_phase reference similarity should be 1.0 under stroboscopic sampling")

        expected_case_count = len(resolved_config["cases"])
        if summary["case_count"] != expected_case_count:
            issues.append("summary case_count does not match resolved_config")
        if summary["state_record_count"] != len(states):
            issues.append("summary state_record_count mismatch")
        if summary["relational_pair_count"] != len(pairs):
            issues.append("summary relational_pair_count mismatch")
        if summary["lag_record_count"] != len(lags):
            issues.append("summary lag_record_count mismatch")
        if summary.get("persistent_migration_executed") is not False:
            issues.append("persistent_migration_executed is not false")
        if summary.get("real_data_used") is not False:
            issues.append("real_data_used is not false")
        if summary.get("physics_claim_gate") != "closed":
            issues.append("physics_claim_gate is not closed")
        legacy_independence_field = "name_" + "independence_check_passed"
        if legacy_independence_field in summary:
            issues.append("legacy detector-independence summary field is still present")
        if summary.get("detector_input_independence_check_passed") is not True:
            issues.append("detector_input_independence_check_passed is not true")
        if summary.get("similarity_features_used") != ["observable_value"]:
            issues.append("summary similarity_features_used is not observable-only")
        if any(row["detected_status"] == "time_crystal_confirmed" for row in case_rows):
            issues.append("forbidden physical status found")

        for row in case_rows:
            if row["case_id"] == "MISSING_OBSERVATIONS":
                if row["data_quality_status"] == "insufficient" and row["detected_status"] != "data_quality_inconclusive":
                    issues.append("missing-data insufficient quality did not produce data_quality_inconclusive")
                if row["data_quality_status"] == "sufficient" and row["detected_status"] == "data_quality_inconclusive":
                    issues.append("missing-data case became inconclusive despite sufficient quality")
            if row["detected_status"] == "t_like_recurrence_supported":
                diff = float(row["lag2_minus_lag1"])
                if diff >= float(resolved_config["minimal_lag_difference"]):
                    issues.append("T-like detection overlaps with robust 2T lag dominance")

        db_files = list(out.glob("*.db")) + list(out.glob("*.sqlite")) + list(out.glob("*.sqlite3"))
        if db_files:
            issues.append(f"Persistent database files found: {[str(path) for path in db_files]}")

    if issues:
        for issue in issues:
            print(f"FAIL: {issue}")
        return 1
    print("QSB-OUTREACH01A synthetic demonstrator run validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
