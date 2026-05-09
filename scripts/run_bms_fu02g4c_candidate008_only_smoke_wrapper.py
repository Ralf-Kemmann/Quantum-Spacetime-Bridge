#!/usr/bin/env python3
"""Disabled-by-default candidate_008-only Stage-2 smoke wrapper.

This wrapper is intentionally narrow. It never calls the FU02g4c enumerator,
the replay runner, the single-patch inspector, or the photo-check runner.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = (
    "data/bms_fu02g4c_full_raw_order_replay_stage2_candidate_008_disabled_smoke_config.yaml"
)
DEFAULT_CANDIDATE_ID = "candidate_008"
DEFAULT_RAW_INDEX = 26187175
DEFAULT_OUTPUT_DIR = (
    "runs/BMS-FU02g4c-full-replay/stage2_bounded_smoke_check_candidate_008/"
)
EXCLUDED_CANDIDATE_ID = "candidate_005"
EXCLUDED_RAW_INDEX = 26157530


CLAIM_BOUNDARY = [
    "Stage 2 candidate_008-only wrapper metadata check only.",
    "No FU02g4c full raw-order replay is started by this wrapper.",
    "No FU02g4c enumeration is started by this wrapper.",
    "No existing FU02g4c anchor files are mutated by this wrapper.",
    "No full raw-order coverage is certified by this wrapper.",
    "candidate_008 is a positive control, not a substitute for full coverage.",
    "candidate_005 remains excluded and remains a degeneracy stress case.",
    "near_distance=0 is not identity or isomorphism.",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Disabled-by-default candidate_008-only Stage-2 smoke wrapper. "
            "This version performs only config/path/metadata checks and never "
            "calls replay, inspection, photo-generation, or enumeration scripts."
        )
    )
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--candidate-id", default=DEFAULT_CANDIDATE_ID)
    parser.add_argument("--raw-index", type=int, default=DEFAULT_RAW_INDEX)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--enable-candidate-008-smoke",
        action="store_true",
        default=False,
        help="Explicitly enable the bounded candidate_008 metadata smoke gate.",
    )
    parser.add_argument(
        "--dry-run",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Keep execution in dry-run mode. Defaults to true.",
    )
    return parser.parse_args()


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required to parse the Stage-2 config.") from exc

    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise RuntimeError(f"Config did not parse to a mapping: {path}")
    return data


def as_bool(value: Any) -> bool:
    return bool(value) if isinstance(value, bool) else False


def add_block(blocked_reasons: list[str], condition: bool, reason: str) -> None:
    if condition:
        blocked_reasons.append(reason)


def check_reference_paths(repo_root: Path, config: dict[str, Any]) -> list[dict[str, Any]]:
    path_checks: list[dict[str, Any]] = []
    for section_name in ("references", "input_bundle"):
        section = config.get(section_name, {})
        if not isinstance(section, dict):
            continue
        for key, value in section.items():
            if not isinstance(value, str):
                continue
            path = repo_root / value
            path_checks.append(
                {
                    "section": section_name,
                    "key": key,
                    "path": value,
                    "exists": path.exists(),
                }
            )
    return path_checks


def build_summary(args: argparse.Namespace, repo_root: Path) -> tuple[dict[str, Any], str]:
    config_path = repo_root / args.config
    config_yaml_parse_ok = False
    config: dict[str, Any] = {}
    warnings: list[str] = []
    blocked_reasons: list[str] = []

    try:
        config = load_yaml(config_path)
        config_yaml_parse_ok = True
    except Exception as exc:  # noqa: BLE001 - report as BLOCKED, do not continue silently.
        blocked_reasons.append(f"config_yaml_parse_failed: {exc}")

    run = config.get("run", {}) if isinstance(config.get("run", {}), dict) else {}
    safety = config.get("safety", {}) if isinstance(config.get("safety", {}), dict) else {}
    smoke_target = (
        config.get("smoke_target", {})
        if isinstance(config.get("smoke_target", {}), dict)
        else {}
    )
    excluded = (
        config.get("excluded_from_stage2_first_smoke", {})
        if isinstance(config.get("excluded_from_stage2_first_smoke", {}), dict)
        else {}
    )
    proposed = (
        config.get("proposed_disabled_execution", {})
        if isinstance(config.get("proposed_disabled_execution", {}), dict)
        else {}
    )

    add_block(
        blocked_reasons,
        args.candidate_id != DEFAULT_CANDIDATE_ID,
        f"candidate_id must be {DEFAULT_CANDIDATE_ID}",
    )
    add_block(
        blocked_reasons,
        args.raw_index != DEFAULT_RAW_INDEX,
        f"raw_index must be {DEFAULT_RAW_INDEX}",
    )
    add_block(
        blocked_reasons,
        args.candidate_id == EXCLUDED_CANDIDATE_ID or args.raw_index == EXCLUDED_RAW_INDEX,
        "candidate_005 is explicitly excluded from this wrapper",
    )
    add_block(
        blocked_reasons,
        as_bool(run.get("full_certification")),
        "config full_certification must remain false",
    )
    add_block(
        blocked_reasons,
        as_bool(run.get("allow_long_replay_run")),
        "allow_long_replay_run must remain false",
    )
    add_block(
        blocked_reasons,
        as_bool(run.get("replay_started")),
        "config replay_started must remain false",
    )
    add_block(
        blocked_reasons,
        smoke_target.get("candidate_id") != DEFAULT_CANDIDATE_ID,
        "config smoke_target.candidate_id must be candidate_008",
    )
    add_block(
        blocked_reasons,
        smoke_target.get("raw_index") != DEFAULT_RAW_INDEX,
        "config smoke_target.raw_index must be 26187175",
    )
    add_block(
        blocked_reasons,
        excluded.get("candidate_id") != EXCLUDED_CANDIDATE_ID,
        "config must explicitly exclude candidate_005",
    )
    add_block(
        blocked_reasons,
        excluded.get("raw_index") != EXCLUDED_RAW_INDEX,
        "config must explicitly exclude candidate_005 raw_index 26157530",
    )
    add_block(
        blocked_reasons,
        safety.get("max_candidates_allowed_for_smoke_check") != 1,
        "max_candidates_allowed_for_smoke_check must be 1",
    )
    add_block(
        blocked_reasons,
        not as_bool(safety.get("full_replay_must_remain_disabled")),
        "full_replay_must_remain_disabled must be true",
    )
    add_block(
        blocked_reasons,
        as_bool(proposed.get("unbounded_replay_allowed")),
        "unbounded replay must not be allowed",
    )
    add_block(
        blocked_reasons,
        as_bool(proposed.get("full_raw_order_replay_allowed")),
        "full raw-order replay must not be allowed",
    )

    path_checks = check_reference_paths(repo_root, config) if config_yaml_parse_ok else []
    missing_paths = [item["path"] for item in path_checks if not item["exists"]]
    if missing_paths:
        warnings.append("Some referenced paths are missing; wrapper remains metadata-only.")

    execution_enabled = bool(args.enable_candidate_008_smoke)
    dry_run = bool(args.dry_run)
    smoke_check_started = False
    candidates_checked_count = 0
    smoke_check_status = "BLOCKED" if blocked_reasons else "DRY_RUN_READY"

    if not execution_enabled:
        blocked_reasons.append("execution disabled: --enable-candidate-008-smoke not set")
        smoke_check_status = "BLOCKED"
    elif not dry_run:
        blocked_reasons.append(
            "non-dry-run execution is not implemented in this wrapper version"
        )
        smoke_check_status = "BLOCKED"

    if execution_enabled and dry_run and not blocked_reasons:
        smoke_check_started = False
        candidates_checked_count = 0
        smoke_check_status = "DRY_RUN_READY"

    summary = {
        "run_id": "BMS-FU02g4c_candidate008_only_smoke_wrapper_v0",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "stage": 2,
        "mode": "candidate_008_only_smoke_wrapper_disabled_by_default",
        "config_path": args.config,
        "config_yaml_parse_ok": config_yaml_parse_ok,
        "execution_enabled": execution_enabled,
        "smoke_check_enabled": execution_enabled and dry_run and not blocked_reasons,
        "dry_run": dry_run,
        "candidate_id": args.candidate_id,
        "raw_index": args.raw_index,
        "expected_candidate_id": DEFAULT_CANDIDATE_ID,
        "expected_raw_index": DEFAULT_RAW_INDEX,
        "candidate_005_checked": False,
        "candidate_005_excluded": True,
        "smoke_check_started": smoke_check_started,
        "smoke_check_status": smoke_check_status,
        "full_replay_started": False,
        "full_certification": False,
        "unbounded_enumeration_started": False,
        "replay_runner_called": False,
        "enumerator_called": False,
        "inspect_script_called": False,
        "photo_runner_called": False,
        "candidates_checked_count": candidates_checked_count,
        "max_candidates_allowed": 1,
        "output_dir": args.output_dir,
        "path_checks": path_checks,
        "missing_paths": missing_paths,
        "blocked_reasons": blocked_reasons,
        "warnings": warnings,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    readout = build_readout(summary)
    return summary, readout


def build_readout(summary: dict[str, Any]) -> str:
    blocked = summary.get("blocked_reasons", [])
    warnings = summary.get("warnings", [])
    blocked_text = "\n".join(f"- {item}" for item in blocked) if blocked else "- none"
    warnings_text = "\n".join(f"- {item}" for item in warnings) if warnings else "- none"
    claim_text = "\n".join(f"- {item}" for item in CLAIM_BOUNDARY)
    return f"""# BMS FU02g4c candidate_008-only Stage-2 Smoke Wrapper Readout

## A) Befund

- stage: {summary['stage']}
- mode: {summary['mode']}
- config_yaml_parse_ok: {summary['config_yaml_parse_ok']}
- execution_enabled: {summary['execution_enabled']}
- dry_run: {summary['dry_run']}
- candidate_id: {summary['candidate_id']}
- raw_index: {summary['raw_index']}
- smoke_check_status: {summary['smoke_check_status']}
- candidates_checked_count: {summary['candidates_checked_count']}
- candidate_005_checked: {summary['candidate_005_checked']}
- full_replay_started: {summary['full_replay_started']}
- full_certification: {summary['full_certification']}

## B) Interpretation

This wrapper version is disabled by default and performs no replay, no enumeration,
no inspector call, and no photo-runner call. It is limited to config, path, and
candidate metadata checks.

## C) Offene Luecke

The actual candidate_008 smoke execution remains open. A non-dry-run execution
path is intentionally not implemented in this wrapper version.

## D) Claim Boundary

{claim_text}

## E) Naechster vorgeschlagener Schritt

Run this wrapper only as an enabled dry-run gate after explicit Ralf approval.

## Blocked Reasons

{blocked_text}

## Warnings

{warnings_text}
"""


def write_outputs(summary: dict[str, Any], readout: str, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "readout.md").write_text(readout, encoding="utf-8")


def main() -> int:
    args = parse_args()
    repo_root = Path.cwd()
    summary, readout = build_summary(args, repo_root)

    # Default and --help runs do not write outputs. Future enabled dry-runs may
    # write the planned summary/readout, still without replay or enumeration.
    if args.enable_candidate_008_smoke and args.dry_run:
        if summary["smoke_check_status"] == "DRY_RUN_READY":
            write_outputs(summary, readout, repo_root / args.output_dir)
        else:
            print(json.dumps(summary, indent=2, sort_keys=True))
            return 2
    else:
        print(json.dumps(summary, indent=2, sort_keys=True))

    return 0 if summary["smoke_check_status"] == "DRY_RUN_READY" else 2


if __name__ == "__main__":
    sys.exit(main())
