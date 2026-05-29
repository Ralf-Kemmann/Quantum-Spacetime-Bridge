#!/usr/bin/env python3
"""QSB-ST-SHAPIROINFO24B gate checker dry-run skeleton.

This script reads only the existing J0740 manifest draft and the empty
Correction-State sidecar template. It does not download files, open linked
timing/parameter files, ingest .par/.tim data, run PINT/tempo2, or calculate
residuals.

The expected successful outcome is BLOCKED_EXPECTED: the checker works because
it confirms that the operational gates remain closed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_MANIFEST = (
    "data/QSB-ST-SHAPIROINFO/j0740_6620_download_manifest_manual_review.yaml"
)
DEFAULT_SIDECAR = "data/QSB-ST-SHAPIROINFO/correction_state_sidecar_template.yaml"
DEFAULT_OUTPUT_DIR = "runs/QSB-ST-SHAPIROINFO24B/gate_checker_dry_run_open"

CLAIM_FLAG_NAMES = (
    "bridge_confirmation_flag",
    "physical_validation_flag",
    "new_shapiro_effect_claim_flag",
    "gr_incomplete_claim_flag",
    "residual_implies_qsb_flag",
    "dataset_specific_evidence_claim_flag",
    "real_data_result_claim_flag",
    "candidate_residual_claim_flag",
    "derivation_of_c_claim_flag",
    "numerical_c_explanation_claim_flag",
)

BLOCKING_PLACEHOLDERS = {
    "unknown",
    "manual_review_required",
    "blocked_missing_correction_state",
    "NO_GO",
}

DISALLOWED_INPUT_SUFFIXES = {".par", ".tim"}
MISSING = object()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check closed SHAPIROINFO gates without real data contact. "
            "Exit 0 means BLOCKED_EXPECTED, not GO."
        )
    )
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--sidecar", default=DEFAULT_SIDECAR)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Explicitly overwrite the dry-run status JSON if it already exists.",
    )
    return parser.parse_args()


def load_existing_text(path: Path, label: str) -> str:
    suffix = path.suffix.lower()
    if suffix in DISALLOWED_INPUT_SUFFIXES:
        raise SystemExit(f"Refusing to read {label} with data suffix: {path}")
    if not path.is_file():
        raise SystemExit(f"Missing required {label}: {path}")
    return path.read_text(encoding="utf-8")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_scalar(raw_value: str) -> Any:
    value = raw_value.strip()
    if value == "":
        return ""
    if " #" in value:
        value = value.split(" #", 1)[0].strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1]
    if value == "true":
        return True
    if value == "false":
        return False
    if value == "[]":
        return []
    if value == "null":
        return None
    return value


def section_text(text: str, section_name: str) -> str:
    lines = text.splitlines()
    header_re = re.compile(rf"^{re.escape(section_name)}:\s*(?:#.*)?$")
    for index, line in enumerate(lines):
        if not header_re.match(line):
            continue
        block: list[str] = []
        for child in lines[index + 1 :]:
            stripped = child.strip()
            if stripped == "" or stripped.startswith("#"):
                block.append(child)
                continue
            indent = len(child) - len(child.lstrip(" "))
            if indent == 0:
                break
            block.append(child)
        return "\n".join(block)
    return ""


def scalar(text: str, key: str, section: str | None = None) -> Any:
    scope = section_text(text, section) if section else text
    if not scope:
        return MISSING
    if section:
        pattern = re.compile(rf"^\s+{re.escape(key)}:\s*(.*?)\s*$", re.MULTILINE)
    else:
        pattern = re.compile(rf"^{re.escape(key)}:\s*(.*?)\s*$", re.MULTILINE)
    match = pattern.search(scope)
    if not match:
        return MISSING
    return parse_scalar(match.group(1))


def check_equal(
    checks: list[dict[str, Any]],
    check_id: str,
    source: str,
    field_path: str,
    observed: Any,
    expected: Any,
    note: str,
) -> None:
    checks.append(
        {
            "check_id": check_id,
            "source": source,
            "field_path": field_path,
            "observed": "<missing>" if observed is MISSING else observed,
            "expected": expected,
            "passed": observed == expected,
            "note": note,
        }
    )


def check_true(
    checks: list[dict[str, Any]],
    check_id: str,
    source: str,
    observed: bool,
    note: str,
) -> None:
    checks.append(
        {
            "check_id": check_id,
            "source": source,
            "field_path": "computed",
            "observed": observed,
            "expected": True,
            "passed": bool(observed),
            "note": note,
        }
    )


def claim_flags(text: str) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for flag_name in CLAIM_FLAG_NAMES:
        pattern = re.compile(
            rf"^\s*{re.escape(flag_name)}:\s*(.*?)\s*$", re.MULTILINE
        )
        match = pattern.search(text)
        if match:
            values[flag_name] = parse_scalar(match.group(1))
    return values


def claim_flags_all_false(text: str) -> tuple[bool, dict[str, Any], list[str]]:
    values = claim_flags(text)
    missing = [name for name in CLAIM_FLAG_NAMES if name not in values]
    wrong = {name: value for name, value in values.items() if value is not False}
    return not missing and not wrong, values, missing


def count_downloaded_true(text: str) -> int:
    return len(re.findall(r"^\s*downloaded:\s*true\b", text, flags=re.MULTILINE))


def count_downloaded_false(text: str) -> int:
    return len(re.findall(r"^\s*downloaded:\s*false\b", text, flags=re.MULTILINE))


def build_checks(manifest_text: str, sidecar_text: str) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    check_equal(
        checks,
        "manifest_record_id",
        "manifest",
        "manifest_record_id",
        scalar(manifest_text, "manifest_record_id"),
        "J0740_6620_MANUAL_REVIEW_DRAFT_NO_DOWNLOAD",
        "Candidate manifest is the J0740 manual-review draft.",
    )
    check_equal(
        checks,
        "manifest_gate_blocked",
        "manifest",
        "manifest_gate_status",
        scalar(manifest_text, "manifest_gate_status"),
        "BLOCKED_MANUAL_REVIEW_REQUIRED",
        "Top-level manifest gate must remain blocked.",
    )
    check_equal(
        checks,
        "download_not_allowed",
        "manifest",
        "download_allowed",
        scalar(manifest_text, "download_allowed"),
        False,
        "No download is authorized by the manifest.",
    )
    check_equal(
        checks,
        "sidecar_population_not_allowed",
        "manifest",
        "sidecar_population_allowed",
        scalar(manifest_text, "sidecar_population_allowed"),
        False,
        "No dataset-specific sidecar population is authorized.",
    )
    check_equal(
        checks,
        "dry_run_preview_not_allowed",
        "manifest",
        "dry_run_preview_allowed",
        scalar(manifest_text, "dry_run_preview_allowed"),
        False,
        "No dry-run preview over real timing data is authorized.",
    )
    check_equal(
        checks,
        "download_gate_blocked",
        "manifest",
        "download_plan.download_gate_status",
        scalar(manifest_text, "download_gate_status", "download_plan"),
        "BLOCKED_BEFORE_DOWNLOAD",
        "Download gate remains closed.",
    )
    check_equal(
        checks,
        "raw_tracking_blocked",
        "manifest",
        "download_plan.raw_data_tracking_status",
        scalar(manifest_text, "raw_data_tracking_status", "download_plan"),
        "BLOCKED_RAW_DATA_TRACKING",
        "Raw-data tracking remains blocked.",
    )
    check_equal(
        checks,
        "downloaded_files_empty",
        "manifest",
        "download_plan.downloaded_files",
        scalar(manifest_text, "downloaded_files", "download_plan"),
        [],
        "No downloaded files are recorded.",
    )
    check_equal(
        checks,
        "sidecar_gate_blocked",
        "manifest",
        "downstream_gate.sidecar_gate_status",
        scalar(manifest_text, "sidecar_gate_status", "downstream_gate"),
        "BLOCKED_BEFORE_SIDECAR_DRAFT",
        "Sidecar gate remains closed.",
    )
    check_equal(
        checks,
        "dry_run_gate_blocked",
        "manifest",
        "downstream_gate.dry_run_gate_status",
        scalar(manifest_text, "dry_run_gate_status", "downstream_gate"),
        "BLOCKED_BEFORE_DRY_RUN",
        "Dry-run gate remains closed.",
    )
    check_equal(
        checks,
        "file_level_docs_unresolved",
        "manifest",
        "candidate_context.file_level_documentation_status",
        scalar(manifest_text, "file_level_documentation_status", "candidate_context"),
        "FILE_LEVEL_DOCUMENTATION_UNRESOLVED",
        "File-level documentation is still unresolved.",
    )
    check_equal(
        checks,
        "data_use_license_unresolved",
        "manifest",
        "candidate_context.data_use_license_status",
        scalar(manifest_text, "data_use_license_status", "candidate_context"),
        "DATA_USE_LICENSE_UNRESOLVED",
        "Dataset-specific data-use/license status remains unresolved.",
    )
    check_equal(
        checks,
        "correction_context_unresolved",
        "manifest",
        "candidate_context.correction_context_status",
        scalar(manifest_text, "correction_context_status", "candidate_context"),
        "CORRECTION_CONTEXT_UNRESOLVED",
        "Correction context remains unresolved.",
    )
    check_true(
        checks,
        "no_downloaded_true_entries",
        "manifest",
        count_downloaded_true(manifest_text) == 0,
        "No manifest download item is marked downloaded: true.",
    )
    check_true(
        checks,
        "downloaded_false_entries_present",
        "manifest",
        count_downloaded_false(manifest_text) >= 2,
        "Expected timing and parameter download items are explicitly false.",
    )

    manifest_claims_ok, manifest_claim_values, manifest_missing = claim_flags_all_false(
        manifest_text
    )
    check_true(
        checks,
        "manifest_claim_flags_false",
        "manifest",
        manifest_claims_ok,
        (
            "All manifest claim flags are false. "
            f"missing={manifest_missing}; observed={manifest_claim_values}"
        ),
    )

    check_equal(
        checks,
        "sidecar_schema_version",
        "sidecar_template",
        "correction_state_schema_version",
        scalar(sidecar_text, "correction_state_schema_version"),
        "SHAPIROINFO10",
        "Sidecar template follows the SHAPIROINFO10 field schema.",
    )
    for field_name in (
        "correction_state_record_id",
        "clock_correction_state",
        "ephemeris_state",
        "dm_ism_state",
        "backend_instrument_state",
        "noise_model_state",
        "qc_state",
        "adapter_readiness_label",
        "go_no_go_status",
    ):
        observed = scalar(sidecar_text, field_name)
        check_true(
            checks,
            f"sidecar_blocking_placeholder_{field_name}",
            "sidecar_template",
            observed in BLOCKING_PLACEHOLDERS,
            f"{field_name} remains a blocking placeholder: {observed}",
        )

    sidecar_claims_ok, sidecar_claim_values, sidecar_missing = claim_flags_all_false(
        sidecar_text
    )
    check_true(
        checks,
        "sidecar_claim_flags_false",
        "sidecar_template",
        sidecar_claims_ok,
        (
            "All sidecar claim flags are false. "
            f"missing={sidecar_missing}; observed={sidecar_claim_values}"
        ),
    )

    return checks


def json_scalar(value: Any) -> str:
    return json.dumps(value, sort_keys=True)


def missing_required_fields(failed_checks: list[dict[str, Any]]) -> list[str]:
    fields = []
    for check in failed_checks:
        if check.get("observed") == "<missing>":
            fields.append(str(check.get("field_path", check.get("check_id"))))
    return fields


def unexpected_open_fields(failed_checks: list[dict[str, Any]]) -> list[str]:
    fields = []
    for check in failed_checks:
        expected = check.get("expected")
        if expected is False or str(expected).startswith("BLOCKED_"):
            fields.append(str(check.get("field_path", check.get("check_id"))))
    return fields


def output_paths(output_dir: Path) -> dict[str, Path]:
    return {
        "status": output_dir / "gate_checker_status.json",
        "summary": output_dir / "summary.json",
        "readout": output_dir / "readout.md",
        "csv": output_dir / "gate_check_results.csv",
        "resolved_inputs": output_dir / "resolved_inputs.json",
    }


def ensure_writable(paths: dict[str, Path], overwrite: bool) -> None:
    if overwrite:
        return
    existing = [path for path in paths.values() if path.exists()]
    if existing:
        joined = ", ".join(str(path) for path in existing)
        raise SystemExit(f"Refusing to overwrite existing dry-run output: {joined}")


def build_summary(
    gate_decision: str,
    failed_checks: list[dict[str, Any]],
    manifest_text: str,
    sidecar_text: str,
) -> dict[str, Any]:
    manifest_claims_ok, _, _ = claim_flags_all_false(manifest_text)
    sidecar_claims_ok, _, _ = claim_flags_all_false(sidecar_text)
    expected_blocked_check_passed = gate_decision == "BLOCKED_EXPECTED"

    return {
        "block_id": "QSB-ST-SHAPIROINFO24B",
        "run_id": "gate_checker_dry_run_open",
        "overall_status": gate_decision,
        "expected_blocked_check_passed": expected_blocked_check_passed,
        "claim_flags_all_false": manifest_claims_ok and sidecar_claims_ok,
        "missing_required_fields": missing_required_fields(failed_checks),
        "unexpected_open_fields": unexpected_open_fields(failed_checks),
        "download_allowed": False,
        "sidecar_population_allowed": False,
        "dry_run_preview_allowed": False,
        "raw_data_tracking_allowed": False,
        "raw_data_commit_allowed": False,
    }


def build_readout(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# QSB-ST-SHAPIROINFO24B Gate Checker Dry-Run Readout",
            "",
            f"overall_status: {summary['overall_status']}",
            (
                "expected_blocked_check_passed: "
                f"{str(summary['expected_blocked_check_passed']).lower()}"
            ),
            (
                "claim_flags_all_false: "
                f"{str(summary['claim_flags_all_false']).lower()}"
            ),
            "",
            "## Gate Boundary",
            "",
            "- download_allowed: false",
            "- sidecar_population_allowed: false",
            "- dry_run_preview_allowed: false",
            "- raw_data_tracking_allowed: false",
            "- raw_data_commit_allowed: false",
            "",
            "## Claim Boundary",
            "",
            "- no Bridge confirmation",
            "- no physical validation",
            "- no new Shapiro effect claim",
            "- no claim that GR is incomplete",
            "- no claim that any residual implies QSB-ST",
            "- no dataset-specific evidence claim",
            "- no real-data result",
            "- no candidate residual claim from gate checking",
            "- no derivation of c",
            "- no explanation of the numerical value of c",
            "",
            "BLOCKED_EXPECTED means the dry-run checker found the expected closed gates.",
            "",
        ]
    )


def write_gate_check_csv(
    path: Path,
    checks: list[dict[str, Any]],
    manifest_path: Path,
    sidecar_path: Path,
) -> None:
    source_file_by_label = {
        "manifest": str(manifest_path),
        "sidecar_template": str(sidecar_path),
    }
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "field_name",
                "source_file",
                "observed_value",
                "expected_value",
                "check_status",
                "severity",
                "note",
            ]
        )
        for check in checks:
            passed = bool(check.get("passed", False))
            writer.writerow(
                [
                    check.get("field_path", check.get("check_id", "")),
                    source_file_by_label.get(
                        str(check.get("source", "")),
                        str(check.get("source", "")),
                    ),
                    json_scalar(check.get("observed")),
                    json_scalar(check.get("expected")),
                    "PASS" if passed else "FAIL",
                    "info" if passed else "blocking",
                    check.get("note", ""),
                ]
            )


def write_run_outputs(
    paths: dict[str, Path],
    status: dict[str, Any],
    summary: dict[str, Any],
    checks: list[dict[str, Any]],
    manifest_path: Path,
    sidecar_path: Path,
    output_dir: Path,
    overwrite: bool,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    ensure_writable(paths, overwrite)

    paths["status"].write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")
    paths["summary"].write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    paths["readout"].write_text(build_readout(summary), encoding="utf-8")
    write_gate_check_csv(paths["csv"], checks, manifest_path, sidecar_path)

    resolved_inputs = {
        "manifest_path": str(manifest_path),
        "sidecar_path": str(sidecar_path),
        "output_dir": str(output_dir),
        "overwrite": overwrite,
    }
    paths["resolved_inputs"].write_text(
        json.dumps(resolved_inputs, indent=2, sort_keys=True) + "\n"
    )


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest)
    sidecar_path = Path(args.sidecar)
    output_dir = Path(args.output_dir)
    paths = output_paths(output_dir)

    manifest_text = load_existing_text(manifest_path, "manifest")
    sidecar_text = load_existing_text(sidecar_path, "sidecar template")

    checks = build_checks(manifest_text, sidecar_text)
    failed_checks = [check for check in checks if not check["passed"]]
    gate_decision = "BLOCKED_EXPECTED" if not failed_checks else "UNEXPECTED_GATE_STATE"
    exit_code = 0 if gate_decision == "BLOCKED_EXPECTED" else 2

    status = {
        "schema_version": "SHAPIROINFO24B_GATE_CHECKER_DRY_RUN_STATUS_V1",
        "run_label": "QSB-ST-SHAPIROINFO24B gate checker dry-run open",
        "generated_at_utc": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "dry_run_only": True,
        "real_timing_data_contact": False,
        "download_performed": False,
        "linked_timing_data_or_parameter_file_opened": False,
        "par_tim_ingestion_performed": False,
        "pint_or_tempo2_execution_performed": False,
        "residual_calculation_performed": False,
        "expected_gate_decision": "BLOCKED_EXPECTED",
        "gate_decision": gate_decision,
        "exit_code": exit_code,
        "input_files": {
            "manifest": {
                "path": str(manifest_path),
                "sha256": sha256_text(manifest_text),
            },
            "sidecar_template": {
                "path": str(sidecar_path),
                "sha256": sha256_text(sidecar_text),
            },
        },
        "check_summary": {
            "check_count": len(checks),
            "passed_count": len(checks) - len(failed_checks),
            "failed_count": len(failed_checks),
        },
        "checks": checks,
        "claim_boundary": {
            "no_bridge_confirmation": True,
            "no_physical_validation": True,
            "no_new_shapiro_effect_claim": True,
            "no_gr_incomplete_claim": True,
            "no_dataset_specific_evidence_claim": True,
            "no_real_data_result": True,
            "no_candidate_residual_claim": True,
            "no_derivation_of_c": True,
            "no_explanation_of_numerical_value_of_c": True,
        },
    }

    summary = build_summary(gate_decision, failed_checks, manifest_text, sidecar_text)
    write_run_outputs(
        paths,
        status,
        summary,
        checks,
        manifest_path,
        sidecar_path,
        output_dir,
        args.overwrite,
    )

    print(f"gate_decision={gate_decision}")
    print(f"output={paths['status']}")
    print(f"failed_checks={len(failed_checks)}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
