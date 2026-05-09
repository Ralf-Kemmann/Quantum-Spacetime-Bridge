#!/usr/bin/env python3
"""Disabled Stage-3 FU02g4c full-replay wrapper scaffold.

This first version performs read-only gate checks only. It never calls the
FU02g4c enumerator, replay runner, aggregator, shell runner, inspector, or
photo runner, and it never writes output files.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = (
    "data/bms_fu02g4c_full_raw_order_replay_stage3_disabled_full_replay_config.yaml"
)
DEFAULT_OUTPUT_DIR = (
    "runs/BMS-FU02g4c-full-replay/stage3_full_raw_order_replay_certification_001/"
)
DEFAULT_CANDIDATE_COUNT = 11
CANDIDATE_005_ID = "candidate_005"
CANDIDATE_005_RAW_INDEX = "26157530"
CANDIDATE_008_ID = "candidate_008"
CANDIDATE_008_RAW_INDEX = "26187175"


CLAIM_BOUNDARY = [
    "This scaffold performs read-only Stage-3 gate checks only.",
    "No FU02g4c full raw-order replay is started.",
    "No FU02g4c enumeration is started.",
    "No existing runner is executed.",
    "No FU02g4c anchor files are mutated.",
    "No output files are written by this scaffold.",
    "No full raw-order coverage is certified.",
    "candidate_005 remains a degeneracy stress case, not exact.",
    "candidate_008 is a positive control, not a substitute for full coverage.",
    "near_distance=0 is not identity or isomorphism.",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Disabled-by-default Stage-3 FU02g4c full-replay wrapper scaffold. "
            "Performs read-only config/path/CSV candidate gate checks only."
        )
    )
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--candidate-count-expected",
        type=int,
        default=DEFAULT_CANDIDATE_COUNT,
    )
    parser.add_argument(
        "--dry-run",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Keep this scaffold in read-only dry-run gate mode. Defaults to true.",
    )
    parser.add_argument(
        "--enable-stage3-full-replay",
        action="store_true",
        default=False,
        help="Requested future execution flag. This scaffold still blocks execution.",
    )
    parser.add_argument(
        "--confirm-full-raw-order-coverage",
        action="store_true",
        default=False,
        help="Requested future coverage confirmation. This scaffold still blocks execution.",
    )
    parser.add_argument(
        "--require-stage2-candidate008-pass",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Require the Stage-2 candidate_008 PASS note to exist. Defaults to true.",
    )
    parser.add_argument(
        "--write-claim-boundary",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Require claim boundary text in stdout summary. Defaults to true.",
    )
    return parser.parse_args()


def load_yaml(path: Path) -> tuple[bool, dict[str, Any], str | None]:
    try:
        import yaml
    except ImportError as exc:
        return False, {}, f"PyYAML import failed: {exc}"

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - reported as BLOCKED.
        return False, {}, str(exc)
    if not isinstance(data, dict):
        return False, {}, "YAML root is not a mapping"
    return True, data, None


def read_csv_minimal(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "read_ok": False,
        "row_count": None,
        "column_count": None,
        "headers": [],
        "candidate_005_present": False,
        "candidate_008_present": False,
        "candidate_005_raw_index_present": False,
        "candidate_008_raw_index_present": False,
        "error": None,
    }
    if not path.exists():
        return result

    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = list(reader.fieldnames or [])
            rows = list(reader)
    except Exception as exc:  # noqa: BLE001 - reported in summary.
        result["error"] = str(exc)
        return result

    result["read_ok"] = True
    result["row_count"] = len(rows)
    result["column_count"] = len(headers)
    result["headers"] = headers

    for row in rows:
        values = {str(value) for value in row.values() if value is not None}
        joined = " ".join(values)
        if CANDIDATE_005_ID in values or CANDIDATE_005_ID in joined:
            result["candidate_005_present"] = True
        if CANDIDATE_008_ID in values or CANDIDATE_008_ID in joined:
            result["candidate_008_present"] = True
        if CANDIDATE_005_RAW_INDEX in values or CANDIDATE_005_RAW_INDEX in joined:
            result["candidate_005_raw_index_present"] = True
        if CANDIDATE_008_RAW_INDEX in values or CANDIDATE_008_RAW_INDEX in joined:
            result["candidate_008_raw_index_present"] = True

    return result


def collect_paths(config: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for section_name in ("references", "original_fu02g4c_bundle", "runner_plan"):
        section = config.get(section_name, {})
        if isinstance(section, dict):
            for value in section.values():
                if isinstance(value, str):
                    paths.append(value)
    candidate_tables = config.get("candidate_tables", {})
    if isinstance(candidate_tables, dict):
        for key, value in candidate_tables.items():
            if key.endswith("_csv") and isinstance(value, str):
                paths.append(value)
    return paths


def path_checks(repo_root: Path, paths: list[str]) -> list[dict[str, Any]]:
    checks = []
    for value in paths:
        path = repo_root / value
        checks.append({"path": value, "exists": path.exists()})
    return checks


def build_summary(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path.cwd()
    config_path = repo_root / args.config
    config_parse_ok, config, config_error = load_yaml(config_path)
    blocked_reasons: list[str] = []
    warnings: list[str] = []

    if not config_parse_ok:
        blocked_reasons.append(f"config_yaml_parse_failed: {config_error}")

    run = config.get("run", {}) if isinstance(config.get("run", {}), dict) else {}
    candidate_tables = (
        config.get("candidate_tables", {})
        if isinstance(config.get("candidate_tables", {}), dict)
        else {}
    )
    candidate_handling = (
        config.get("candidate_handling", {})
        if isinstance(config.get("candidate_handling", {}), dict)
        else {}
    )
    references = (
        config.get("references", {})
        if isinstance(config.get("references", {}), dict)
        else {}
    )

    if config_parse_ok and run.get("stage") != 3:
        blocked_reasons.append("config run.stage must be 3")
    if config_parse_ok and run.get("execution_enabled") is not False:
        blocked_reasons.append("config execution_enabled must remain false")
    if config_parse_ok and run.get("full_replay_enabled") is not False:
        blocked_reasons.append("config full_replay_enabled must remain false")
    if config_parse_ok and run.get("full_certification") is not False:
        blocked_reasons.append("config full_certification must remain false")

    checks = path_checks(repo_root, collect_paths(config)) if config_parse_ok else []
    missing_paths = [item["path"] for item in checks if not item["exists"]]
    if missing_paths:
        blocked_reasons.append("one or more referenced paths are missing")

    stage2_note = references.get("stage2_candidate_008_reference_smoke_pass_note", "")
    stage2_note_exists = bool(stage2_note) and (repo_root / str(stage2_note)).exists()
    if args.require_stage2_candidate008_pass and not stage2_note_exists:
        blocked_reasons.append("Stage-2 candidate_008 PASS note is required but missing")

    csv_checks: dict[str, dict[str, Any]] = {}
    for key, value in candidate_tables.items():
        if key.endswith("_csv") and isinstance(value, str):
            csv_checks[key] = read_csv_minimal(repo_root / value)

    csv_row_counts_ok = True
    for key, check in csv_checks.items():
        if not check["read_ok"]:
            csv_row_counts_ok = False
            blocked_reasons.append(f"candidate table not readable: {key}")
        elif check["row_count"] != args.candidate_count_expected:
            csv_row_counts_ok = False
            blocked_reasons.append(
                f"{key} row_count={check['row_count']} expected={args.candidate_count_expected}"
            )

    candidate_005_marker_ok = any(
        check["candidate_005_present"] and check["candidate_005_raw_index_present"]
        for check in csv_checks.values()
    )
    candidate_008_marker_ok = any(
        check["candidate_008_present"] and check["candidate_008_raw_index_present"]
        for check in csv_checks.values()
    )

    configured_c005 = (
        candidate_handling.get("candidate_005", {})
        if isinstance(candidate_handling.get("candidate_005", {}), dict)
        else {}
    )
    configured_c008 = (
        candidate_handling.get("candidate_008", {})
        if isinstance(candidate_handling.get("candidate_008", {}), dict)
        else {}
    )
    candidate_005_config_ok = (
        configured_c005.get("candidate_id") == CANDIDATE_005_ID
        and str(configured_c005.get("raw_index")) == CANDIDATE_005_RAW_INDEX
    )
    candidate_008_config_ok = (
        configured_c008.get("candidate_id") == CANDIDATE_008_ID
        and str(configured_c008.get("raw_index")) == CANDIDATE_008_RAW_INDEX
    )

    if not candidate_005_config_ok:
        blocked_reasons.append("candidate_005 config marker missing or mismatched")
    if not candidate_008_config_ok:
        blocked_reasons.append("candidate_008 config marker missing or mismatched")
    if not candidate_005_marker_ok:
        warnings.append("candidate_005 table marker not found in a single CSV row")
    if not candidate_008_marker_ok:
        warnings.append("candidate_008 table marker not found in a single CSV row")

    execution_requested = bool(
        args.enable_stage3_full_replay or args.confirm_full_raw_order_coverage or not args.dry_run
    )
    if execution_requested:
        blocked_reasons.append("stage3 execution path not implemented in this scaffold")

    status = "BLOCKED" if blocked_reasons else "DRY_RUN_READY"
    return {
        "stage": 3,
        "mode": "stage3_full_replay_wrapper_scaffold_read_only_gate",
        "status": status,
        "config_path": args.config,
        "config_yaml_parse_ok": config_parse_ok,
        "config_yaml_error": config_error,
        "output_dir": args.output_dir,
        "candidate_count_expected": args.candidate_count_expected,
        "dry_run": args.dry_run,
        "enable_stage3_full_replay": args.enable_stage3_full_replay,
        "confirm_full_raw_order_coverage": args.confirm_full_raw_order_coverage,
        "require_stage2_candidate008_pass": args.require_stage2_candidate008_pass,
        "write_claim_boundary": args.write_claim_boundary,
        "stage2_candidate_008_pass_note_exists": stage2_note_exists,
        "path_checks": checks,
        "missing_paths": missing_paths,
        "csv_checks": csv_checks,
        "csv_row_counts_ok": csv_row_counts_ok,
        "candidate_005_config_ok": candidate_005_config_ok,
        "candidate_008_config_ok": candidate_008_config_ok,
        "candidate_005_marker_ok": candidate_005_marker_ok,
        "candidate_008_marker_ok": candidate_008_marker_ok,
        "full_replay_started": False,
        "enumerator_called": False,
        "replay_runner_called": False,
        "aggregator_called": False,
        "shell_runner_called": False,
        "inspect_runner_called": False,
        "photo_runner_called": False,
        "outputs_written": False,
        "fu02g4c_anchor_files_mutated": False,
        "full_certification": False,
        "blocked_reasons": blocked_reasons,
        "warnings": warnings,
        "claim_boundary": CLAIM_BOUNDARY if args.write_claim_boundary else [],
    }


def main() -> int:
    args = parse_args()
    summary = build_summary(args)
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"STAGE3_GATE_STATUS={summary['status']}")
    return 0 if summary["status"] == "DRY_RUN_READY" else 2


if __name__ == "__main__":
    sys.exit(main())
