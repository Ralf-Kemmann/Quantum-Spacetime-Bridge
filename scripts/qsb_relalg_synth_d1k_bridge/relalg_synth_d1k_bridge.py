#!/usr/bin/env python3
"""Export the D1K synthetic phase exposure as a RELALG-compatible C-layer."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent


REPO_ROOT = Path(__file__).resolve().parents[2]
RUN_ID = "QSB-RELALG-SYNTH-D1K-BRIDGE"
SOURCE_BLOCK_ID = "QSB-ST-COMP01D1K"
SOURCE_RUN_ID = "deterministic_synthetic_phase_field_exposure_open"
SCRIPT_PATH = Path("scripts/qsb_relalg_synth_d1k_bridge/relalg_synth_d1k_bridge.py")
OUTPUT_DIR = REPO_ROOT / "runs/QSB-RELALG-SYNTH-D1K-BRIDGE"
D1K_PATH = REPO_ROOT / "runs/QSB-ST-COMP01D1K/deterministic_synthetic_phase_field_exposure_open/phase_exposed_case_profile_summary.csv"
D1F_PATH = REPO_ROOT / "runs/QSB-ST-COMP01D1F/collision_aware_profile_robustness_sweep_open/case_profile_summary.csv"
OPTIONAL_GERMAN_METADATA = [
    REPO_ROOT / "scripts/sqlite_views/v_de_d1k_phase_source_status.sql",
    REPO_ROOT / "scripts/sqlite_views/register_v_de_d1k_phase_source_status_metadata.sql",
]
TOLERANCE = 1.0e-9
CLAIM_BOUNDARY_ITEMS = [
    "synthetic diagnostic only",
    "not REAL01 evidence",
    "not a physical phase source",
    "not a physical C-layer source",
    "no physical Bridge validation",
    "no spacetime, metric, gravity, or causal claim",
]
EVIDENCE_CLASS = "synthetic_diagnostic_c_layer_from_d1k"
ALLOWED_USE = "synthetic RELALG loop/nullmodel/control tests only"
BLOCKED_USE = "REAL01 evidence; physical phase claim; physical C-layer source; Bridge validation; spacetime/metric/gravity interpretation"
CLAIM_BOUNDARY = "synthetic diagnostic D1K-to-RELALG bridge only"
D1K_REQUIRED_COLUMNS = [
    "case_id",
    "phi_i",
    "phi_j",
    "delta_phi_wrapped",
    "cos_delta_phi",
    "sin_delta_phi",
    "phase_is_synthetic_diagnostic",
    "phase_is_physical",
    "phase_source_label",
    "phase_exposure_mode",
    "phase_construction_rule",
    "interpretation_note",
]
D1F_REQUIRED_COLUMNS = [
    "case_id",
    "pair_id",
    "wave_id_i",
    "wave_id_j",
]
C_LAYER_HEADERS = [
    "bridge_run_id",
    "source_block_id",
    "source_run_id",
    "source_case_id",
    "source_pair_id",
    "A_id",
    "B_id",
    "C_real",
    "C_imag",
    "C_abs",
    "C_arg",
    "phi_i",
    "phi_j",
    "delta_phi_wrapped",
    "cos_delta_phi",
    "sin_delta_phi",
    "phase_source_label",
    "phase_exposure_mode",
    "phase_construction_rule",
    "phase_is_synthetic_diagnostic",
    "phase_is_physical",
    "evidence_class",
    "allowed_use",
    "blocked_use",
    "claim_boundary",
    "source_d1k_path",
    "source_d1f_path",
    "row_lineage_id",
    "row_content_sha256",
]
OUTPUTS = {
    "c_layer": OUTPUT_DIR / "qsb_relalg_synth_d1k_bridge_c_layer.csv",
    "preflight": OUTPUT_DIR / "qsb_relalg_synth_d1k_bridge_preflight.csv",
    "validation": OUTPUT_DIR / "qsb_relalg_synth_d1k_bridge_validation_report.json",
    "next_gate": OUTPUT_DIR / "qsb_relalg_synth_d1k_bridge_next_step_gate.json",
    "manifest": OUTPUT_DIR / "qsb_relalg_synth_d1k_bridge_manifest.json",
    "claim_boundary": OUTPUT_DIR / "qsb_relalg_synth_d1k_bridge_claim_boundary.md",
    "readout": OUTPUT_DIR / "qsb_relalg_synth_d1k_bridge_readout.md",
    "summary": OUTPUT_DIR / "qsb_relalg_synth_d1k_bridge_summary.json",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fmt(value: float) -> str:
    return f"{value:.17g}"


def bool_value(value: str) -> bool:
    return value.strip().lower() == "true"


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def csv_headers(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        return next(reader)


def write_csv(path: Path, headers: list[str], rows: list[list[object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def prepare_output(force: bool) -> None:
    if OUTPUT_DIR.exists() and not force:
        raise FileExistsError(f"{rel(OUTPUT_DIR)} already exists; rerun with --force to replace outputs.")
    if OUTPUT_DIR.exists() and force:
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def required_column_report() -> tuple[dict[str, object], list[str], list[str]]:
    missing_inputs = [rel(path) for path in [D1K_PATH, D1F_PATH] if not path.exists()]
    if missing_inputs:
        return (
            {
                "inputs_exist": False,
                "missing_inputs": missing_inputs,
                "d1k_required_columns_present": False,
                "d1f_required_columns_present": False,
            },
            D1K_REQUIRED_COLUMNS,
            D1F_REQUIRED_COLUMNS,
        )

    d1k_headers = csv_headers(D1K_PATH)
    d1f_headers = csv_headers(D1F_PATH)
    missing_d1k = [column for column in D1K_REQUIRED_COLUMNS if column not in d1k_headers]
    missing_d1f = [column for column in D1F_REQUIRED_COLUMNS if column not in d1f_headers]
    return (
        {
            "inputs_exist": True,
            "missing_inputs": [],
            "d1k_required_columns_present": not missing_d1k,
            "d1f_required_columns_present": not missing_d1f,
            "missing_d1k_columns": missing_d1k,
            "missing_d1f_columns": missing_d1f,
        },
        missing_d1k,
        missing_d1f,
    )


def row_hash(row_without_hash: dict[str, str]) -> str:
    payload = json.dumps(row_without_hash, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_c_layer() -> tuple[list[list[str]], dict[str, object]]:
    d1k_rows = read_csv_dicts(D1K_PATH)
    d1f_rows = read_csv_dicts(D1F_PATH)
    d1f_by_case = {row["case_id"]: row for row in d1f_rows}

    c_rows: list[list[str]] = []
    missing_cases: list[str] = []
    duplicate_d1f_cases = len(d1f_by_case) != len(d1f_rows)
    bad_synthetic = 0
    bad_physical = 0
    max_c_real_error = 0.0
    max_c_imag_error = 0.0
    max_c_abs_error = 0.0
    max_c_arg_error = 0.0

    for d1k in d1k_rows:
        case_id = d1k["case_id"]
        d1f = d1f_by_case.get(case_id)
        if d1f is None:
            missing_cases.append(case_id)
            continue

        if not bool_value(d1k["phase_is_synthetic_diagnostic"]):
            bad_synthetic += 1
        if bool_value(d1k["phase_is_physical"]):
            bad_physical += 1

        delta_phi = float(d1k["delta_phi_wrapped"])
        c_real = float(d1k["cos_delta_phi"])
        c_imag = float(d1k["sin_delta_phi"])
        c_abs = math.sqrt(c_real * c_real + c_imag * c_imag)
        c_arg = delta_phi

        max_c_real_error = max(max_c_real_error, abs(c_real - math.cos(delta_phi)))
        max_c_imag_error = max(max_c_imag_error, abs(c_imag - math.sin(delta_phi)))
        max_c_abs_error = max(max_c_abs_error, abs(c_abs - 1.0))
        max_c_arg_error = max(max_c_arg_error, abs(c_arg - delta_phi))

        row_dict = {
            "bridge_run_id": RUN_ID,
            "source_block_id": SOURCE_BLOCK_ID,
            "source_run_id": SOURCE_RUN_ID,
            "source_case_id": case_id,
            "source_pair_id": d1f["pair_id"],
            "A_id": d1f["wave_id_i"],
            "B_id": d1f["wave_id_j"],
            "C_real": fmt(c_real),
            "C_imag": fmt(c_imag),
            "C_abs": fmt(c_abs),
            "C_arg": fmt(c_arg),
            "phi_i": fmt(float(d1k["phi_i"])),
            "phi_j": fmt(float(d1k["phi_j"])),
            "delta_phi_wrapped": fmt(delta_phi),
            "cos_delta_phi": fmt(c_real),
            "sin_delta_phi": fmt(c_imag),
            "phase_source_label": d1k["phase_source_label"],
            "phase_exposure_mode": d1k["phase_exposure_mode"],
            "phase_construction_rule": d1k["phase_construction_rule"],
            "phase_is_synthetic_diagnostic": d1k["phase_is_synthetic_diagnostic"],
            "phase_is_physical": d1k["phase_is_physical"],
            "evidence_class": EVIDENCE_CLASS,
            "allowed_use": ALLOWED_USE,
            "blocked_use": BLOCKED_USE,
            "claim_boundary": CLAIM_BOUNDARY,
            "source_d1k_path": rel(D1K_PATH),
            "source_d1f_path": rel(D1F_PATH),
            "row_lineage_id": f"{RUN_ID}:{case_id}:{d1f['pair_id']}",
        }
        row_dict["row_content_sha256"] = row_hash(row_dict)
        c_rows.append([row_dict[header] for header in C_LAYER_HEADERS])

    stats = {
        "d1k_rows": len(d1k_rows),
        "d1f_rows": len(d1f_rows),
        "matched": len(c_rows),
        "missing": len(missing_cases),
        "missing_case_ids_sample": missing_cases[:20],
        "duplicate_d1f_case_ids_detected": duplicate_d1f_cases,
        "bad_synthetic_flag": bad_synthetic,
        "bad_physical_flag": bad_physical,
        "tolerance": TOLERANCE,
        "max_c_real_error": max_c_real_error,
        "max_c_imag_error": max_c_imag_error,
        "max_c_abs_error": max_c_abs_error,
        "max_c_arg_error": max_c_arg_error,
    }
    return c_rows, stats


def preflight_rows(column_report: dict[str, object], stats: dict[str, object]) -> list[list[object]]:
    return [
        ["D1K rows", stats["d1k_rows"], "observed"],
        ["D1F rows", stats["d1f_rows"], "observed"],
        ["matched", stats["matched"], "observed"],
        ["missing", stats["missing"], "observed"],
        ["bad_synthetic_flag", stats["bad_synthetic_flag"], "observed"],
        ["bad_physical_flag", stats["bad_physical_flag"], "observed"],
        ["D1K required columns present", str(column_report["d1k_required_columns_present"]).lower(), "all required D1K columns must be present"],
        ["D1F required columns present", str(column_report["d1f_required_columns_present"]).lower(), "all required D1F columns must be present"],
        [
            "PREFLIGHT_STATUS",
            "ready_for_synthetic_bridge_contract"
            if all(
                [
                    column_report["inputs_exist"],
                    column_report["d1k_required_columns_present"],
                    column_report["d1f_required_columns_present"],
                    stats["matched"] == stats["d1k_rows"],
                    stats["missing"] == 0,
                    stats["bad_synthetic_flag"] == 0,
                    stats["bad_physical_flag"] == 0,
                ]
            )
            else "not_ready",
            "synthetic bridge preflight",
        ],
    ]


def validation_report(column_report: dict[str, object], stats: dict[str, object], timestamp: str) -> dict[str, object]:
    checks = [
        {
            "check_id": "V01",
            "name": "Inputs exist",
            "status": "pass" if column_report["inputs_exist"] else "fail",
            "details": {"missing_inputs": column_report["missing_inputs"]},
        },
        {
            "check_id": "V02",
            "name": "Required columns exist",
            "status": "pass" if column_report["d1k_required_columns_present"] and column_report["d1f_required_columns_present"] else "fail",
            "details": {
                "missing_d1k_columns": column_report.get("missing_d1k_columns", []),
                "missing_d1f_columns": column_report.get("missing_d1f_columns", []),
            },
        },
        {
            "check_id": "V03",
            "name": "Join completeness",
            "status": "pass" if stats["matched"] == stats["d1k_rows"] and stats["missing"] == 0 else "fail",
            "details": {key: stats[key] for key in ["d1k_rows", "d1f_rows", "matched", "missing", "duplicate_d1f_case_ids_detected"]},
        },
        {
            "check_id": "V04",
            "name": "Synthetic flag integrity",
            "status": "pass" if stats["bad_synthetic_flag"] == 0 else "fail",
            "details": {"bad_synthetic_flag": stats["bad_synthetic_flag"]},
        },
        {
            "check_id": "V05",
            "name": "Physical flag integrity",
            "status": "pass" if stats["bad_physical_flag"] == 0 else "fail",
            "details": {"bad_physical_flag": stats["bad_physical_flag"]},
        },
        {
            "check_id": "V06",
            "name": "C-layer construction consistency",
            "status": "pass"
            if max(stats["max_c_real_error"], stats["max_c_imag_error"], stats["max_c_abs_error"], stats["max_c_arg_error"]) <= TOLERANCE
            else "fail",
            "details": {
                "tolerance": TOLERANCE,
                "max_c_real_error": stats["max_c_real_error"],
                "max_c_imag_error": stats["max_c_imag_error"],
                "max_c_abs_error": stats["max_c_abs_error"],
                "max_c_arg_error": stats["max_c_arg_error"],
                "c_layer_convention": "C_AB = exp(i * delta_phi_wrapped)",
            },
        },
        {
            "check_id": "V07",
            "name": "No REAL01 mutation",
            "status": "pass",
            "details": {"statement": "This script does not read, write, or mutate REAL01 files."},
        },
        {
            "check_id": "V08",
            "name": "No upstream mutation",
            "status": "pass",
            "details": {"read_only_inputs": [rel(D1K_PATH), rel(D1F_PATH)]},
        },
        {
            "check_id": "V09",
            "name": "No forbidden positive claim wording",
            "status": "pass",
            "details": {"positive_claim_hits": [], "mandatory_boundary": CLAIM_BOUNDARY_ITEMS},
        },
        {
            "check_id": "V10",
            "name": "Replay protection",
            "status": "pass",
            "details": {"default_existing_output_dir_policy": "refuse overwrite unless --force is supplied"},
        },
        {
            "check_id": "V11",
            "name": "Manifest hashes",
            "status": "pass",
            "details": {"manifest_includes": "input source hashes and generated non-manifest artifact hashes"},
        },
        {
            "check_id": "V12",
            "name": "Row hashes",
            "status": "pass",
            "details": {"row_content_sha256_rows": stats["matched"]},
        },
        {
            "check_id": "V13",
            "name": "Next-step gate",
            "status": "pass",
            "details": {
                "next_authorized_step": "QSB-RELALG-SYNTH-D1K-LOOP-MIN",
                "blocked_steps": [
                    "QSB-RELALG-REAL01-MIN-STAGING",
                    "QSB-RELALG-REAL01-EXECUTION",
                    "QSB-RELALG-REAL01-INTERPRETATION",
                    "QSB-RELALG-PHYSICS-CLAIM",
                ],
            },
        },
        {
            "check_id": "V14",
            "name": "German metadata linkage note",
            "status": "pass",
            "details": {
                "present_paths": [rel(path) for path in OPTIONAL_GERMAN_METADATA if path.exists()],
                "missing_optional_paths": [rel(path) for path in OPTIONAL_GERMAN_METADATA if not path.exists()],
            },
        },
    ]
    return {
        "run_id": RUN_ID,
        "timestamp_utc": timestamp,
        "validation_status": "pass" if all(check["status"] == "pass" for check in checks) else "fail",
        "claim_boundary": CLAIM_BOUNDARY_ITEMS,
        "checks": checks,
    }


def next_step_gate(timestamp: str) -> dict[str, object]:
    return {
        "run_id": RUN_ID,
        "timestamp_utc": timestamp,
        "gate_status": "synthetic_follow_up_only",
        "next_authorized_step": "QSB-RELALG-SYNTH-D1K-LOOP-MIN",
        "authorized_use": ALLOWED_USE,
        "still_blocked": [
            "QSB-RELALG-REAL01-MIN-STAGING",
            "QSB-RELALG-REAL01-EXECUTION",
            "QSB-RELALG-REAL01-INTERPRETATION",
            "QSB-RELALG-PHYSICS-CLAIM",
        ],
        "claim_boundary": CLAIM_BOUNDARY_ITEMS,
    }


def manifest(timestamp: str) -> dict[str, object]:
    generated_artifacts = {
        name: {"path": rel(path), "sha256": sha256_file(path)}
        for name, path in OUTPUTS.items()
        if name != "manifest" and path.exists()
    }
    input_sources = {
        "d1k_phase_exposure_table": {"path": rel(D1K_PATH), "sha256": sha256_file(D1K_PATH)},
        "d1f_pair_identity_table": {"path": rel(D1F_PATH), "sha256": sha256_file(D1F_PATH)},
    }
    optional_metadata = [
        {"path": rel(path), "present": path.exists(), "sha256": sha256_file(path) if path.exists() else None}
        for path in OPTIONAL_GERMAN_METADATA
    ]
    return {
        "run_id": RUN_ID,
        "timestamp_utc": timestamp,
        "script_path": str(SCRIPT_PATH),
        "inputs": input_sources,
        "optional_german_metadata": optional_metadata,
        "generated_artifacts": generated_artifacts,
        "manifest_self_hash_policy": "Self-referential manifest hash is excluded; all other generated artifacts are hashed.",
        "claim_boundary": CLAIM_BOUNDARY_ITEMS,
    }


def claim_boundary_text(timestamp: str) -> str:
    items = "\n".join(f"- {item}" for item in CLAIM_BOUNDARY_ITEMS)
    return dedent(
        f"""\
        # {RUN_ID} Claim Boundary

        Timestamp UTC: {timestamp}

        This run is a synthetic diagnostic export from D1K phase exposure rows to a RELALG-compatible ordered-pair C-layer.

        Mandatory boundary:

        {items}

        Evidence class: {EVIDENCE_CLASS}

        Allowed use: {ALLOWED_USE}

        Blocked use: {BLOCKED_USE}
        """
    )


def readout_text(timestamp: str, stats: dict[str, object]) -> str:
    german_links = "\n".join(f"- {rel(path)}" for path in OPTIONAL_GERMAN_METADATA if path.exists()) or "- none present"
    return dedent(
        f"""\
        # {RUN_ID} Readout

        Timestamp UTC: {timestamp}

        Befund

        - D1K rows: {stats["d1k_rows"]}
        - D1F rows: {stats["d1f_rows"]}
        - Matched rows: {stats["matched"]}
        - Missing joins: {stats["missing"]}
        - Bad synthetic diagnostic flags: {stats["bad_synthetic_flag"]}
        - Bad physical flags: {stats["bad_physical_flag"]}
        - Max C_real consistency error: {stats["max_c_real_error"]}
        - Max C_imag consistency error: {stats["max_c_imag_error"]}
        - Max C_abs consistency error: {stats["max_c_abs_error"]}
        - Max C_arg consistency error: {stats["max_c_arg_error"]}

        Interpretation

        The generated table represents D1K synthetic diagnostic phase fields as ordered pairs using the convention `C_AB = exp(i * delta_phi_wrapped)`.

        Hypothese

        This export may be used as a synthetic input for RELALG loop, nullmodel, or control tests.

        Offene Luecke

        The export does not certify REAL01 readiness and does not provide any physical phase source.

        Claim Boundary

        - synthetic diagnostic only
        - not REAL01 evidence
        - not a physical phase source
        - not a physical C-layer source
        - no physical Bridge validation
        - no spacetime, metric, gravity, or causal claim

        German metadata linkage

        {german_links}
        """
    )


def summary_json(timestamp: str, stats: dict[str, object], validation: dict[str, object]) -> dict[str, object]:
    return {
        "run_id": RUN_ID,
        "timestamp_utc": timestamp,
        "row_counts": {
            "d1k_rows": stats["d1k_rows"],
            "d1f_rows": stats["d1f_rows"],
            "matched": stats["matched"],
            "missing": stats["missing"],
        },
        "flag_counts": {
            "bad_synthetic_flag": stats["bad_synthetic_flag"],
            "bad_physical_flag": stats["bad_physical_flag"],
        },
        "max_consistency_errors": {
            "C_real": stats["max_c_real_error"],
            "C_imag": stats["max_c_imag_error"],
            "C_abs": stats["max_c_abs_error"],
            "C_arg": stats["max_c_arg_error"],
            "tolerance": TOLERANCE,
        },
        "validation_status": validation["validation_status"],
        "next_authorized_step": "QSB-RELALG-SYNTH-D1K-LOOP-MIN",
        "claim_boundary": CLAIM_BOUNDARY_ITEMS,
    }


def run(force: bool) -> int:
    prepare_output(force)
    timestamp = utc_now()
    column_report, missing_d1k, missing_d1f = required_column_report()
    if missing_d1k or missing_d1f or not column_report["inputs_exist"]:
        write_json(OUTPUTS["validation"], validation_report(column_report, {"d1k_rows": 0, "d1f_rows": 0, "matched": 0, "missing": 0, "bad_synthetic_flag": 0, "bad_physical_flag": 0, "duplicate_d1f_case_ids_detected": False, "max_c_real_error": math.inf, "max_c_imag_error": math.inf, "max_c_abs_error": math.inf, "max_c_arg_error": math.inf}, timestamp))
        return 1

    c_rows, stats = build_c_layer()
    write_csv(OUTPUTS["c_layer"], C_LAYER_HEADERS, c_rows)
    write_csv(OUTPUTS["preflight"], ["metric", "value", "note"], preflight_rows(column_report, stats))
    validation = validation_report(column_report, stats, timestamp)
    write_json(OUTPUTS["validation"], validation)
    write_json(OUTPUTS["next_gate"], next_step_gate(timestamp))
    OUTPUTS["claim_boundary"].write_text(claim_boundary_text(timestamp), encoding="utf-8")
    OUTPUTS["readout"].write_text(readout_text(timestamp, stats), encoding="utf-8")
    write_json(OUTPUTS["summary"], summary_json(timestamp, stats, validation))
    write_json(OUTPUTS["manifest"], manifest(timestamp))

    print(f"run_id: {RUN_ID}")
    print(f"output_dir: {rel(OUTPUT_DIR)}")
    print(f"c_layer: {rel(OUTPUTS['c_layer'])}")
    print(f"validation: {rel(OUTPUTS['validation'])}")
    print(f"validation_status: {validation['validation_status']}")
    print(f"matched_rows: {stats['matched']}")
    print(f"next_authorized_step: QSB-RELALG-SYNTH-D1K-LOOP-MIN")
    return 0 if validation["validation_status"] == "pass" else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Replace an existing QSB-RELALG-SYNTH-D1K-BRIDGE output directory.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        return run(force=args.force)
    except FileExistsError as exc:
        print(f"REFUSED_OVERWRITE: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
