#!/usr/bin/env python3
"""Controlled FU02g4c Stage-3 execution-path scaffold.

This runner intentionally does not implement replay or certification work.
It only validates that the Stage-3 execution path is reachable under a
disabled-by-default gate and that dry-run path validation remains non-replay.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = Path("data/fu02g4c_stage3_execution_config.json")
DEFAULT_RUNS_ROOT = Path("runs")
NEGATIVE_STATUS = "execution_gate_blocked_as_expected"
DRY_RUN_STATUS = "dry_run_path_validated"
CLAIM_BOUNDARY = "Stage 3 validates a controlled execution path scaffold."
BLOCKED_OPERATIONS = {
    "full_raw_order_replay",
    "full_certification",
    "global_non_genericity_claim",
}


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    if not isinstance(config, dict):
        raise ValueError("Config root must be a JSON object.")
    return config


def validate_config(config: dict[str, Any]) -> None:
    required = {
        "stage",
        "date",
        "execution_enabled",
        "dry_run_allowed",
        "reference_smoke_candidate",
        "degeneracy_stress_candidate",
        "candidate_ids",
        "blocked_operations",
        "claim_boundary",
    }
    missing = sorted(required - set(config))
    if missing:
        raise ValueError(f"Missing config keys: {', '.join(missing)}")

    if config["execution_enabled"] is not False:
        raise ValueError("Stage-3 execution must remain disabled in this scaffold.")
    if config["dry_run_allowed"] is not True:
        raise ValueError("Dry-run path validation must be explicitly allowed.")

    candidate_ids = config["candidate_ids"]
    if not isinstance(candidate_ids, list) or not all(
        isinstance(item, str) for item in candidate_ids
    ):
        raise ValueError("candidate_ids must be a list of strings.")

    reference = config["reference_smoke_candidate"]
    degeneracy = config["degeneracy_stress_candidate"]
    if reference != "candidate_008":
        raise ValueError("reference_smoke_candidate must remain candidate_008.")
    if degeneracy != "candidate_005":
        raise ValueError("degeneracy_stress_candidate must remain candidate_005.")
    if reference not in candidate_ids or degeneracy not in candidate_ids:
        raise ValueError("Required Stage-3 candidate IDs are not visible in candidate_ids.")

    blocked = set(config["blocked_operations"])
    missing_blocked = sorted(BLOCKED_OPERATIONS - blocked)
    if missing_blocked:
        raise ValueError(f"Missing blocked operations: {', '.join(missing_blocked)}")

    if config["claim_boundary"] != CLAIM_BOUNDARY:
        raise ValueError("Claim boundary must remain limited to the Stage-3 scaffold.")


def build_summary(
    *,
    mode: str,
    status: str,
    config_path: Path,
    config: dict[str, Any],
    output_dir: Path,
) -> dict[str, Any]:
    return {
        "stage": config["stage"],
        "date": config["date"],
        "mode": mode,
        "status": status,
        "execution_enabled": config["execution_enabled"],
        "dry_run_allowed": config["dry_run_allowed"],
        "config_path": str(config_path),
        "output_dir": str(output_dir),
        "candidate_ids": config["candidate_ids"],
        "reference_smoke_candidate": config["reference_smoke_candidate"],
        "degeneracy_stress_candidate": config["degeneracy_stress_candidate"],
        "blocked_operations": config["blocked_operations"],
        "replay_started": False,
        "certification_started": False,
        "claim_boundary": config["claim_boundary"],
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def readout_text(summary: dict[str, Any]) -> str:
    mode = summary["mode"]
    status = summary["status"]
    candidates = ", ".join(summary["candidate_ids"])
    blocked = ", ".join(summary["blocked_operations"])
    reference = summary["reference_smoke_candidate"]
    degeneracy = summary["degeneracy_stress_candidate"]

    if mode == "negative-gate":
        finding = (
            "The runner reached the Stage-3 scaffold and blocked execution because "
            "execution_enabled is false."
        )
        interpretation = (
            "The negative execution gate is reachable and blocks replay work as expected."
        )
        hypothesis = (
            "The disabled-by-default Stage-3 path can be invoked without starting replay "
            "or certification work."
        )
    else:
        finding = (
            "The runner validated the dry-run path, candidate visibility, and blocked "
            "operation list without starting replay work."
        )
        interpretation = (
            f"{reference} remains the Reference-Smoke context and {degeneracy} remains "
            "the Degeneracy-Stress case."
        )
        hypothesis = (
            "The path-validation mode can expose the intended Stage-3 inputs while "
            "remaining non-executing."
        )

    return "\n".join(
        [
            f"# FU02g4c Stage 3 Execution Path Readout",
            "",
            f"Status: {status}",
            f"Mode: {mode}",
            f"Candidates: {candidates}",
            f"Blocked operations: {blocked}",
            "",
            "## Befund",
            finding,
            "",
            "## Interpretation",
            interpretation,
            "",
            "## Hypothese",
            hypothesis,
            "",
            "## Offene Lücke",
            "Full Raw-Order Replay was not executed. Full Certification was not executed.",
            "",
            "## Claim Boundary",
            summary["claim_boundary"],
            "",
        ]
    )


def write_outputs(output_dir: Path, summary: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "manifest.json").write_text(
        json.dumps(
            {
                "files": ["readout.md", "summary.json", "manifest.json"],
                "status": summary["status"],
                "claim_boundary": summary["claim_boundary"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (output_dir / "readout.md").write_text(readout_text(summary), encoding="utf-8")


def output_dir_for(mode: str, run_id: str | None, runs_root: Path) -> Path:
    safe_mode = mode.replace("-", "_")
    suffix = run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return runs_root / f"FU02g4c_stage3_execution_path_{suffix}_{safe_mode}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the FU02g4c Stage-3 controlled execution-path scaffold."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to the Stage-3 execution config.",
    )
    parser.add_argument(
        "--mode",
        choices=("negative-gate", "dry-run"),
        default="negative-gate",
        help="Execution scaffold mode. Both modes remain non-replay.",
    )
    parser.add_argument(
        "--runs-root",
        type=Path,
        default=DEFAULT_RUNS_ROOT,
        help="Root directory for run artifacts.",
    )
    parser.add_argument(
        "--run-id",
        help="Optional deterministic run ID for audit-friendly output paths.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    validate_config(config)

    status = NEGATIVE_STATUS if args.mode == "negative-gate" else DRY_RUN_STATUS
    output_dir = output_dir_for(args.mode, args.run_id, args.runs_root)
    summary = build_summary(
        mode=args.mode,
        status=status,
        config_path=args.config,
        config=config,
        output_dir=output_dir,
    )
    write_outputs(output_dir, summary)

    print(f"status={status}")
    print(f"output_dir={output_dir}")
    print(f"candidates={','.join(config['candidate_ids'])}")
    print(f"claim_boundary={config['claim_boundary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
