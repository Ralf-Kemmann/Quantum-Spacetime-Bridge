#!/usr/bin/env python3
"""Run QSB-CAUSALITY06B-05 robustness and negative-control checks."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import run_qsb_causality06b04_inner_sphere_et_admissibility as qsb04


RUN_ID = "QSB-CAUSALITY06B-05_admissibility_robustness"
FINAL_COMPLETED = "inner_sphere_et_admissibility_robustness_completed"
FINAL_INCONCLUSIVE = "inner_sphere_et_admissibility_robustness_inconclusive"
OUTPUT_FILES = [
    "resolved_config.json",
    "validated_test_cases.json",
    "robustness_results.csv",
    "robustness_results.json",
    "failure_reason_summary.csv",
    "german_alias_view.csv",
    "run_summary.json",
    "readout.md",
]
RESULT_COLUMNS = [
    "test_case_id",
    "test_case_class",
    "expected_forward_admissible",
    "actual_forward_admissible",
    "expectation_matched",
    "failure_origin",
    "validation_failed",
    "validation_failure_reason",
    "rule_evaluation_performed",
    "redox_consistent",
    "redox_reason",
    "chloride_bridge_consistent",
    "chloride_bridge_reason",
    "coordination_consistent",
    "coordination_reason",
    "state_change_coherent",
    "state_change_reason",
    "failed_rule_groups",
    "expected_rule_failures",
    "actual_rule_failures",
    "missing_expected_rule_failures",
    "unexpected_rule_failures",
    "expected_rule_failures_subset_matched",
    "exact_rule_failure_match",
    "minimal_path_without_discrete_S3",
]
RULE_FAILURE_FIELDS = {
    "redox_consistency": "redox_consistent",
    "chloride_bridge_consistency": "chloride_bridge_consistent",
    "coordination_consistency": "coordination_consistent",
    "state_change_coherence": "state_change_coherent",
}
FAILURE_SUMMARY_CATEGORY = {
    "redox_consistency": "redox_consistency_failure",
    "chloride_bridge_consistency": "chloride_bridge_consistency_failure",
    "coordination_consistency": "coordination_consistency_failure",
    "state_change_coherence": "state_change_coherence_failure",
}


class RunError(RuntimeError):
    """Raised for input, validation, or output failures."""


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def validate_record(record: dict[str, Any]) -> tuple[bool, str]:
    try:
        qsb04.validate_cross_field(record)
        species = record["species_status"]
        if species["classification"] == "candidate_configuration" and species["separately_isolated"] == "yes":
            return False, "candidate_configuration marked as separately_isolated"
    except (KeyError, qsb04.RunError) as exc:
        return False, str(exc)
    return True, "not_applicable"


def failed_rule_groups(result: dict[str, Any]) -> list[str]:
    return [
        rule_name
        for rule_name, result_key in RULE_FAILURE_FIELDS.items()
        if not result[result_key]
    ]


def evaluate_case(test_case: dict[str, Any]) -> dict[str, Any]:
    source = test_case["source_state"]
    target = test_case["target_state"]
    source_ok, source_reason = validate_record(source)
    target_ok, target_reason = validate_record(target)
    validation_failed = not (source_ok and target_ok)
    validation_reason = "not_applicable"
    if validation_failed:
        validation_reason = source_reason if not source_ok else target_reason

    expected_validation_failure = test_case["expected_validation_failure"]
    if validation_failed:
        actual = False
        rule_result = {
            "redox_consistent": None,
            "redox_reason": "not_evaluated_due_to_validation_path",
            "chloride_bridge_consistent": None,
            "chloride_bridge_reason": "not_evaluated_due_to_validation_path",
            "coordination_consistent": None,
            "coordination_reason": "not_evaluated_due_to_validation_path",
            "state_change_coherent": None,
            "state_change_reason": "not_evaluated_due_to_validation_path",
            "admissible": False,
        }
        actual_rule_failures: list[str] = []
        missing_expected_rule_failures: list[str] = []
        unexpected_rule_failures: list[str] = []
        rule_evaluation_performed = False
        expected_rule_failures_subset_matched = True
        exact_rule_failure_match = True
        failure_origin = "validation"
        expectation_matched = (
            expected_validation_failure is True
            and validation_failed is True
            and rule_evaluation_performed is False
        )
    else:
        rule_result = qsb04.assess_pair(source, target)
        actual = rule_result["admissible"]
        actual_rule_failures = failed_rule_groups(rule_result)
        expected = set(test_case["expected_rule_failures"])
        actual_set = set(actual_rule_failures)
        missing_expected_rule_failures = sorted(expected - actual_set)
        unexpected_rule_failures = sorted(actual_set - expected)
        rule_evaluation_performed = True
        expected_rule_failures_subset_matched = not missing_expected_rule_failures
        exact_rule_failure_match = (
            not missing_expected_rule_failures
            and not unexpected_rule_failures
        )
        failure_origin = "rule_evaluation" if actual_rule_failures else "none"
        expectation_matched = test_case["expected_forward_admissible"] == actual
        if test_case["test_case_class"] == "negative_control_case":
            expectation_matched = (
                actual is False
                and exact_rule_failure_match
            )

    return {
        "test_case_id": test_case["test_case_id"],
        "test_case_class": test_case["test_case_class"],
        "expected_forward_admissible": test_case["expected_forward_admissible"],
        "actual_forward_admissible": actual,
        "expectation_matched": expectation_matched,
        "failure_origin": failure_origin,
        "validation_failed": validation_failed,
        "validation_failure_reason": validation_reason,
        "rule_evaluation_performed": rule_evaluation_performed,
        "redox_consistent": rule_result["redox_consistent"],
        "redox_reason": rule_result["redox_reason"],
        "chloride_bridge_consistent": rule_result["chloride_bridge_consistent"],
        "chloride_bridge_reason": rule_result["chloride_bridge_reason"],
        "coordination_consistent": rule_result["coordination_consistent"],
        "coordination_reason": rule_result["coordination_reason"],
        "state_change_coherent": rule_result["state_change_coherent"],
        "state_change_reason": rule_result["state_change_reason"],
        "failed_rule_groups": actual_rule_failures,
        "expected_rule_failures": test_case["expected_rule_failures"],
        "actual_rule_failures": actual_rule_failures,
        "missing_expected_rule_failures": missing_expected_rule_failures,
        "unexpected_rule_failures": unexpected_rule_failures,
        "expected_rule_failures_subset_matched": expected_rule_failures_subset_matched,
        "exact_rule_failure_match": exact_rule_failure_match,
        "minimal_path_without_discrete_S3": test_case["minimal_path_without_discrete_S3"],
        "expected_validation_failure": expected_validation_failure,
        "notes": test_case["notes"],
    }


def serialize_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    serialized = []
    for row in rows:
        item = dict(row)
        for key in [
            "failed_rule_groups",
            "expected_rule_failures",
            "actual_rule_failures",
            "missing_expected_rule_failures",
            "unexpected_rule_failures",
        ]:
            item[key] = "|".join(row[key]) if row[key] else "none"
        serialized.append(item)
    return serialized


def alias_rows(rows: list[dict[str, Any]], alias_bundle: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    alias_map = {entry["canonical_field_name"]: entry["display_alias"] for entry in alias_bundle["aliases"]}
    columns = [alias_map.get(column, column) for column in RESULT_COLUMNS]
    output = []
    for row in serialize_rows(rows):
        output.append({display: row[canonical] for canonical, display in zip(RESULT_COLUMNS, columns)})
    return output, columns


def metric(numerator: int, denominator: int) -> float | str:
    if denominator == 0:
        return "not_applicable"
    return numerator / denominator


def build_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    classes = Counter(row["test_case_class"] for row in results)
    positives = [row for row in results if row["test_case_class"] == "positive_reference_case"]
    negatives = [row for row in results if row["test_case_class"] == "negative_control_case"]
    minimals = [row for row in results if row["test_case_class"] == "minimal_path_case"]
    positive_cases_passed = sum(1 for row in positives if row["expectation_matched"] and row["actual_forward_admissible"])
    negative_controls_rejected = sum(1 for row in negatives if row["expectation_matched"] and not row["actual_forward_admissible"])
    minimal_path_cases_passed = sum(1 for row in minimals if row["expectation_matched"] and row["actual_forward_admissible"])
    expectation_mismatch_count = sum(1 for row in results if not row["expectation_matched"])
    rule_failure_mismatch_count = sum(
        1
        for row in results
        if row["rule_evaluation_performed"]
        and row["test_case_class"] == "negative_control_case"
        and not row["exact_rule_failure_match"]
    )
    unexpected_positive_count = sum(
        1 for row in results if row["actual_forward_admissible"] and not row["expected_forward_admissible"]
    )
    unexpected_negative_count = sum(
        1 for row in results if not row["actual_forward_admissible"] and row["expected_forward_admissible"]
    )
    final_status = FINAL_COMPLETED
    if (
        expectation_mismatch_count
        or unexpected_positive_count
        or unexpected_negative_count
        or rule_failure_mismatch_count
        or positive_cases_passed != len(positives)
        or negative_controls_rejected != len(negatives)
        or minimal_path_cases_passed != len(minimals)
    ):
        final_status = FINAL_INCONCLUSIVE
    return {
        "run_id": RUN_ID,
        "data_status": "curated_source_bound_candidate_state_data",
        "positive_reference_case_count": classes["positive_reference_case"],
        "negative_control_case_count": classes["negative_control_case"],
        "minimal_path_case_count": classes["minimal_path_case"],
        "positive_cases_passed": positive_cases_passed,
        "negative_controls_rejected": negative_controls_rejected,
        "minimal_path_cases_passed": minimal_path_cases_passed,
        "expectation_match_count": sum(1 for row in results if row["expectation_matched"]),
        "expectation_mismatch_count": expectation_mismatch_count,
        "unexpected_positive_count": unexpected_positive_count,
        "unexpected_negative_count": unexpected_negative_count,
        "validation_failure_count": sum(1 for row in results if row["validation_failed"]),
        "rule_evaluated_failure_case_count": sum(
            1
            for row in results
            if row["rule_evaluation_performed"] and row["actual_rule_failures"]
        ),
        "rule_group_failure_occurrence_count": sum(
            len(row["actual_rule_failures"])
            for row in results
            if row["rule_evaluation_performed"]
        ),
        "cases_with_any_failure_marker": sum(
            1
            for row in results
            if row["validation_failed"] or row["actual_rule_failures"]
        ),
        "exact_rule_failure_match_count": sum(
            1
            for row in results
            if row["rule_evaluation_performed"] and row["exact_rule_failure_match"]
        ),
        "rule_failure_mismatch_count": rule_failure_mismatch_count,
        "positive_recall": metric(positive_cases_passed, len(positives)),
        "negative_control_rejection_rate": metric(negative_controls_rejected, len(negatives)),
        "localized_aliases_used_as_logic_inputs": False,
        "physical_causality_claimed": False,
        "final_status": final_status,
    }


def failure_summary(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts = Counter()
    for row in results:
        if row["validation_failed"]:
            counts["validation_failure"] += 1
        if row["rule_evaluation_performed"]:
            for failure in row["actual_rule_failures"]:
                counts[FAILURE_SUMMARY_CATEGORY[failure]] += 1
    keys = [
        "validation_failure",
        "redox_consistency_failure",
        "chloride_bridge_consistency_failure",
        "coordination_consistency_failure",
        "state_change_coherence_failure",
    ]
    return [{"failure_category": key, "failure_count": counts[key]} for key in keys]


def build_readout(results: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# QSB-CAUSALITY06B-05 Readout",
            "",
            "## Befund",
            "",
            f"Positive reference cases passed: {summary['positive_cases_passed']} / {summary['positive_reference_case_count']}.",
            f"Negative controls rejected: {summary['negative_controls_rejected']} / {summary['negative_control_case_count']}.",
            f"Minimal path cases passed: {summary['minimal_path_cases_passed']} / {summary['minimal_path_case_count']}.",
            f"Expectation mismatches: {summary['expectation_mismatch_count']}.",
            f"{summary['validation_failure_count']} controls were rejected during run-critical subset validation and were not evaluated by the four chemical admissibility rule groups. {summary['rule_evaluated_failure_case_count']} controls passed validation and were rejected by the declared chemical rules.",
            "",
            "## Interpretation",
            "",
            "The constructed controls test consistency of the declared rule implementation under selected mutations.",
            "",
            "## Hypothese",
            "",
            "The declared rule implementation remains internally consistent for the tested positive, negative-control, and minimal-path cases.",
            "",
            "## Offene Luecke",
            "",
            "The negative controls are constructed tests, not additional experimental observations.",
            "",
            "## Claim Boundary",
            "",
            "Positive recall and negative-control rejection rate are descriptive run metrics, not population statistics. Formal admissibility does not establish thermodynamic favorability, kinetic accessibility, irreversibility, or physical causality. Localized aliases are presentation metadata only.",
            "",
            f"final_status = {summary['final_status']}",
            "",
        ]
    )


def run(args: argparse.Namespace) -> None:
    input_root = Path(args.input_root)
    output_dir = Path(args.output_dir)
    if output_dir.exists():
        if not args.overwrite:
            raise RunError(f"output directory exists; pass --overwrite: {output_dir}")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = {
        "robustness_test_cases": input_root / "data/QSB-CAUSALITY06B-05/robustness_test_cases.json",
        "negative_control_state_pairs": input_root / "data/QSB-CAUSALITY06B-05/negative_control_state_pairs.json",
        "field_aliases_de": input_root / "data/QSB-CAUSALITY06B-05/field_aliases_de.json",
        "qsb04_state_records": input_root / "data/QSB-CAUSALITY06B-04/inner_sphere_et_state_records.json",
        "qsb04_runner": input_root / "scripts/run_qsb_causality06b04_inner_sphere_et_admissibility.py",
    }
    test_bundle = load_json(paths["robustness_test_cases"])
    control_bundle = load_json(paths["negative_control_state_pairs"])
    alias_bundle = load_json(paths["field_aliases_de"])
    if alias_bundle.get("localized_aliases_used_as_logic_inputs") is not False:
        raise RunError("localized aliases must not be logic inputs")

    test_cases = test_bundle["test_cases"]
    if len([case for case in test_cases if case["test_case_class"] == "positive_reference_case"]) < 5:
        raise RunError("expected at least five positive reference cases")
    if len([case for case in test_cases if case["test_case_class"] == "negative_control_case"]) < 8:
        raise RunError("expected at least eight negative control cases")
    if len([case for case in test_cases if case["test_case_class"] == "minimal_path_case"]) < 1:
        raise RunError("expected at least one minimal path case")

    results = [evaluate_case(case) for case in test_cases]
    summary = build_summary(results)

    resolved_config = {
        "run_id": RUN_ID,
        "input_paths": {key: str(path) for key, path in paths.items()},
        "negative_control_count": len(control_bundle["negative_controls"]),
        "test_case_count": len(test_cases),
        "rule_source": "scripts/run_qsb_causality06b04_inner_sphere_et_admissibility.py",
        "rule_duplication": "none_imported_qsb04_assessment_helpers",
        "reference_order_used_as_logic_input": False,
        "localized_aliases_used_as_logic_inputs": False,
        "physical_causality_claimed": False,
    }

    write_json(output_dir / "resolved_config.json", resolved_config)
    write_json(output_dir / "validated_test_cases.json", {"run_id": RUN_ID, "test_cases": test_cases})
    write_csv(output_dir / "robustness_results.csv", serialize_rows(results), RESULT_COLUMNS)
    write_json(output_dir / "robustness_results.json", {"run_id": RUN_ID, "robustness_results": results})
    write_csv(output_dir / "failure_reason_summary.csv", failure_summary(results), ["failure_category", "failure_count"])
    german_rows, german_columns = alias_rows(results, alias_bundle)
    write_csv(output_dir / "german_alias_view.csv", german_rows, german_columns)
    write_json(output_dir / "run_summary.json", summary)
    (output_dir / "readout.md").write_text(build_readout(results, summary), encoding="utf-8")

    actual_outputs = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    if actual_outputs != sorted(OUTPUT_FILES):
        raise RunError(f"output file set mismatch: {actual_outputs}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", default=".", help="Repository root containing data/ and scripts/.")
    parser.add_argument(
        "--output-dir",
        default="runs/QSB-CAUSALITY06B-05/admissibility_robustness",
        help="Output directory for the eight robustness artifacts.",
    )
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing output directory.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        run(args)
    except RunError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
