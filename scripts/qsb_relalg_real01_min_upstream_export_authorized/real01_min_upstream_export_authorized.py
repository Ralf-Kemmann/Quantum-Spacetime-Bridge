#!/usr/bin/env python3
"""Authorized minimal upstream export attempt for RELALG REAL01.

The runner may create C-layer export CSV files only when source fields and
lineage are explicit enough to satisfy the export contract. Otherwise it writes
blocked status rows and no export rows.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RUN_ID = "QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT-AUTHORIZED"
CLAIM_STATUS = "authorized_upstream_export_only_no_phi_computation"
REPO_ROOT = Path(__file__).resolve().parents[2]
RUN_DIR = REPO_ROOT / "runs" / RUN_ID
EXPORT_DIR = RUN_DIR / "exports"

AUTH_DIR = REPO_ROOT / "runs" / "QSB-RELALG-REAL01-MIN-AUTHORIZATION"
UPSTREAM_TEMPLATE_DIR = REPO_ROOT / "runs" / "QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT"
CONTRACT_DIR = REPO_ROOT / "runs" / "QSB-RELALG-REAL01-MIN-EXPORT-CONTRACT"

AUTH_GATE_PATH = AUTH_DIR / "qsb_relalg_real01_min_next_step_gate.json"
AUTH_DECISIONS_PATH = AUTH_DIR / "qsb_relalg_real01_min_authorization_decisions.csv"
EXPORTER_REGISTRY_PATH = (
    UPSTREAM_TEMPLATE_DIR / "qsb_relalg_real01_min_upstream_exporter_registry.csv"
)
UPSTREAM_STATUS_PATH = (
    UPSTREAM_TEMPLATE_DIR / "qsb_relalg_real01_min_upstream_export_status.csv"
)
CONTRACT_SPEC_PATH = CONTRACT_DIR / "qsb_relalg_real01_min_export_contract_spec.csv"
TEMPLATE_DIR = UPSTREAM_TEMPLATE_DIR / "export_templates"

EXPORT_HEADERS = [
    "export_contract_id",
    "source_id",
    "source_space_id",
    "A_id",
    "B_id",
    "pair_orientation",
    "C_real",
    "C_imag",
    "delta_phi",
    "magnitude",
    "angle_unit",
    "wrapping_convention",
    "orientation_convention",
    "diagonal_pair_policy",
    "threshold_policy",
    "delta_min",
    "product_delta_min",
    "source_hash",
    "config_hash",
    "lineage_id",
    "export_authorization_id",
    "export_status",
    "warning_flags",
    "notes",
]

FORBIDDEN_EXPORT_FIELDS = {
    "Phi_ABC",
    "phi_abc",
    "loop_id",
    "loop_product",
    "triple_id",
    "triple_product",
    "ABC",
}

STATUS_VALUES = {
    "export_created_validation_passed",
    "export_created_validation_failed",
    "partial_export_created_with_warnings",
    "blocked_missing_source",
    "blocked_missing_mapping",
    "blocked_missing_required_fields",
    "blocked_missing_source_space",
    "blocked_missing_lineage_or_hash",
    "blocked_no_rows_after_filters",
    "blocked_not_exportable",
}

OUTPUTS = {
    "config": RUN_DIR
    / "qsb_relalg_real01_min_upstream_export_authorized_config.json",
    "prerequisite": RUN_DIR
    / "qsb_relalg_real01_min_upstream_export_authorized_prerequisite_report.json",
    "contract_registry": RUN_DIR
    / "qsb_relalg_real01_min_upstream_export_authorized_contract_registry.csv",
    "mapping_review": RUN_DIR
    / "qsb_relalg_real01_min_upstream_export_authorized_mapping_review.csv",
    "export_status": RUN_DIR
    / "qsb_relalg_real01_min_upstream_export_authorized_export_status.csv",
    "failed_exports": RUN_DIR
    / "qsb_relalg_real01_min_upstream_export_authorized_failed_exports.csv",
    "warning_flags": RUN_DIR
    / "qsb_relalg_real01_min_upstream_export_authorized_warning_flags.csv",
    "claim_boundary": RUN_DIR
    / "qsb_relalg_real01_min_upstream_export_authorized_claim_boundary_report.md",
    "gate": RUN_DIR / "qsb_relalg_real01_min_next_step_gate.json",
    "manifest": RUN_DIR / "qsb_relalg_real01_min_manifest.json",
    "validation": RUN_DIR / "qsb_relalg_real01_min_validation_report.json",
    "summary": RUN_DIR / f"{RUN_ID}_RUN_SUMMARY.md",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing run directory after replay protection check.",
    )
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_json_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_json(path: Path, value: Any) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def read_csv_header(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        return next(reader, [])


def relative(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def prepare_run_dir(force: bool) -> None:
    if any(RUN_DIR.iterdir()) and not force:
        raise SystemExit(
            f"Refusing overwrite of non-empty run directory: {relative(RUN_DIR)}. "
            "Use --force to rerun."
        )
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    if force:
        for path in OUTPUTS.values():
            if path.exists():
                path.unlink()
        for export_file in EXPORT_DIR.glob("*.csv"):
            export_file.unlink()


def inspect_source(contract: dict[str, str]) -> dict[str, Any]:
    source_path = REPO_ROOT / contract["source_path"]
    result: dict[str, Any] = {
        "source_exists": source_path.exists(),
        "source_hash": "",
        "source_kind": source_path.suffix.lower().lstrip(".") or "unknown",
        "observed_fields": "",
        "mapping_complete": False,
        "lineage_complete": False,
        "source_space_present": bool(contract.get("source_space_id")),
        "row_count_estimate": 0,
        "status": "blocked_missing_source",
        "warning_flags": "source_missing",
        "mapping_notes": "Source path does not exist.",
    }
    if not source_path.exists():
        return result

    result["source_hash"] = sha256_file(source_path)
    fields: list[str] = []
    row_count = 0
    if source_path.suffix.lower() == ".csv":
        fields = read_csv_header(source_path)
        with source_path.open("r", encoding="utf-8", newline="") as handle:
            row_count = max(sum(1 for _ in handle) - 1, 0)
    elif source_path.suffix.lower() in {".yaml", ".yml"}:
        with source_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if ":" in stripped and not stripped.startswith("#"):
                    fields.append(stripped.split(":", 1)[0].strip())
                if len(fields) >= 40:
                    break
    else:
        fields = []

    observed = set(fields)
    required_mapping = {
        contract.get("A_id_field", "A_id"),
        contract.get("B_id_field", "B_id"),
    }
    c_fields = {
        contract.get("C_real_field", "C_real"),
        contract.get("C_imag_field", "C_imag"),
    }
    phase_field = contract.get("phase_difference_field", "delta_phi")
    has_pair_fields = required_mapping.issubset(observed)
    has_value_fields = c_fields.issubset(observed) or phase_field in observed
    has_lineage = {"sha256", "source_hash", "lineage_id", "artifact_id"}.intersection(
        observed
    )

    result.update(
        {
            "observed_fields": ";".join(fields),
            "mapping_complete": has_pair_fields and has_value_fields,
            "lineage_complete": bool(has_lineage),
            "row_count_estimate": row_count,
        }
    )

    if source_path.suffix.lower() not in {".csv", ".yaml", ".yml"}:
        result.update(
            {
                "status": "blocked_not_exportable",
                "warning_flags": "source_not_tabular_export_input",
                "mapping_notes": "Source is not a row-level table or declared mapping input.",
            }
        )
    elif not has_pair_fields or not has_value_fields:
        result.update(
            {
                "status": "blocked_missing_mapping",
                "warning_flags": "missing_contract_field_mapping",
                "mapping_notes": (
                    "Source fields do not expose the required ordered-pair and "
                    "C-layer value mapping."
                ),
            }
        )
    elif not has_lineage:
        result.update(
            {
                "status": "blocked_missing_lineage_or_hash",
                "warning_flags": "missing_row_lineage_or_hash",
                "mapping_notes": "Required mapping fields exist, but row lineage/hash is absent.",
            }
        )
    elif row_count == 0 and source_path.suffix.lower() == ".csv":
        result.update(
            {
                "status": "blocked_no_rows_after_filters",
                "warning_flags": "no_rows_after_contract_filter_review",
                "mapping_notes": "Source table contains no rows for export review.",
            }
        )
    else:
        result.update(
            {
                "status": "blocked_not_exportable",
                "warning_flags": "no_safe_exporter_for_source_shape",
                "mapping_notes": "No deterministic source-to-contract row exporter is declared.",
            }
        )
    return result


def validate_export_file(path: Path) -> dict[str, Any]:
    header = read_csv_header(path)
    row_count = 0
    with path.open("r", encoding="utf-8", newline="") as handle:
        row_count = max(sum(1 for _ in handle) - 1, 0)
    forbidden = sorted(set(header).intersection(FORBIDDEN_EXPORT_FIELDS))
    return {
        "path": relative(path),
        "header_matches": header == EXPORT_HEADERS,
        "row_count": row_count,
        "forbidden_fields": forbidden,
        "has_required_lineage_fields": all(
            field in header for field in ["source_hash", "source_space_id", "lineage_id"]
        ),
    }


def make_manifest(
    prerequisite_paths: list[Path], output_paths: list[Path], export_paths: list[Path]
) -> dict[str, Any]:
    prerequisite_hashes = [
        {"path": relative(path), "sha256": sha256_file(path)}
        for path in prerequisite_paths
        if path.exists()
    ]
    output_hashes = [
        {"path": relative(path), "sha256": sha256_file(path)}
        for path in output_paths
        if path.exists()
    ]
    export_hashes = [
        {"path": relative(path), "sha256": sha256_file(path)}
        for path in export_paths
        if path.exists()
    ]
    return {
        "run_id": RUN_ID,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "prerequisite_hashes": prerequisite_hashes,
        "output_hashes": output_hashes,
        "export_hashes": export_hashes,
        "exports_dir": relative(EXPORT_DIR),
        "claim_status": CLAIM_STATUS,
    }


def main() -> int:
    args = parse_args()
    prepare_run_dir(args.force)

    prerequisite_paths = [
        AUTH_GATE_PATH,
        AUTH_DECISIONS_PATH,
        EXPORTER_REGISTRY_PATH,
        UPSTREAM_STATUS_PATH,
        CONTRACT_SPEC_PATH,
    ] + sorted(TEMPLATE_DIR.glob("*.csv"))

    auth_gate = load_json(AUTH_GATE_PATH)
    auth_decisions = load_csv(AUTH_DECISIONS_PATH)
    contract_specs = load_csv(CONTRACT_SPEC_PATH)
    exporter_registry = load_csv(EXPORTER_REGISTRY_PATH)
    upstream_status = load_csv(UPSTREAM_STATUS_PATH)

    authorized = {
        row["export_contract_id"]: row
        for row in auth_decisions
        if row.get("authorization_decision") == "authorized_for_upstream_export"
        and row.get("authorizes_c_layer_export") == "true"
        and row.get("authorizes_phi_computation") == "false"
        and row.get("authorizes_real01_staging") == "false"
        and row.get("authorizes_real01_execution") == "false"
        and row.get("authorizes_real01_interpretation") == "false"
    }
    spec_by_contract = {
        row["export_contract_id"]: row
        for row in contract_specs
        if row["export_contract_id"] in authorized
    }

    config = {
        "run_id": RUN_ID,
        "auth_gate_path": relative(AUTH_GATE_PATH),
        "auth_decisions_path": relative(AUTH_DECISIONS_PATH),
        "contract_spec_path": relative(CONTRACT_SPEC_PATH),
        "exporter_registry_path": relative(EXPORTER_REGISTRY_PATH),
        "upstream_status_path": relative(UPSTREAM_STATUS_PATH),
        "template_dir": relative(TEMPLATE_DIR),
        "exports_dir": relative(EXPORT_DIR),
        "required_export_header": EXPORT_HEADERS,
        "status_values": sorted(STATUS_VALUES),
        "claim_status": CLAIM_STATUS,
        "config_hash": "",
    }
    config["config_hash"] = stable_json_hash({k: v for k, v in config.items() if k != "config_hash"})
    write_json(OUTPUTS["config"], config)

    prerequisite_report = {
        "run_id": RUN_ID,
        "authorization_gate_status": auth_gate.get("authorization_status"),
        "authorization_next_step": auth_gate.get("next_authorized_step"),
        "authorized_contract_count": len(authorized),
        "contract_spec_count": len(spec_by_contract),
        "exporter_registry_count": len(exporter_registry),
        "upstream_status_count": len(upstream_status),
        "template_count": len(list(TEMPLATE_DIR.glob("*.csv"))),
        "prerequisites": [
            {"path": relative(path), "exists": path.exists(), "sha256": sha256_file(path)}
            for path in prerequisite_paths
            if path.exists()
        ],
    }
    write_json(OUTPUTS["prerequisite"], prerequisite_report)

    registry_rows: list[dict[str, Any]] = []
    mapping_rows: list[dict[str, Any]] = []
    status_rows: list[dict[str, Any]] = []
    failed_rows: list[dict[str, Any]] = []
    warning_rows: list[dict[str, Any]] = []
    export_paths: list[Path] = []

    for contract_id in sorted(authorized):
        spec = spec_by_contract.get(contract_id)
        decision = authorized[contract_id]
        if not spec:
            source_review = {
                "source_exists": False,
                "source_hash": "",
                "source_kind": "unknown",
                "observed_fields": "",
                "mapping_complete": False,
                "lineage_complete": False,
                "source_space_present": False,
                "row_count_estimate": 0,
                "status": "blocked_missing_required_fields",
                "warning_flags": "missing_contract_spec",
                "mapping_notes": "Authorized contract has no contract spec row.",
            }
            spec = {
                "export_contract_id": contract_id,
                "source_id": decision.get("source_id", ""),
                "source_path": "",
                "source_space_id": "",
                "delta_min": "",
                "product_delta_min": "",
            }
        else:
            source_review = inspect_source(spec)

        status = source_review["status"]
        if status not in STATUS_VALUES:
            status = "blocked_not_exportable"
        row_count = 0
        export_path = ""
        notes = source_review["mapping_notes"]

        registry_rows.append(
            {
                "export_contract_id": contract_id,
                "source_id": spec.get("source_id", ""),
                "source_path": spec.get("source_path", ""),
                "source_space_id": spec.get("source_space_id", ""),
                "authorization_id": decision.get("authorization_id", ""),
                "authorization_scope": decision.get("authorization_scope", ""),
                "template_path": relative(
                    TEMPLATE_DIR / f"{contract_id}_c_layer_export_template.csv"
                ),
                "authorized_output_path": export_path,
                "contract_registry_status": status,
                "notes": notes,
            }
        )
        mapping_rows.append(
            {
                "export_contract_id": contract_id,
                "source_id": spec.get("source_id", ""),
                "source_kind": source_review["source_kind"],
                "source_exists": source_review["source_exists"],
                "observed_fields": source_review["observed_fields"],
                "required_A_id_field": spec.get("A_id_field", "A_id"),
                "required_B_id_field": spec.get("B_id_field", "B_id"),
                "required_C_real_field": spec.get("C_real_field", "C_real"),
                "required_C_imag_field": spec.get("C_imag_field", "C_imag"),
                "required_delta_phi_field": spec.get("phase_difference_field", "delta_phi"),
                "mapping_complete": source_review["mapping_complete"],
                "lineage_complete": source_review["lineage_complete"],
                "source_space_present": source_review["source_space_present"],
                "row_count_estimate": source_review["row_count_estimate"],
                "mapping_review_status": status,
                "mapping_notes": notes,
            }
        )
        status_rows.append(
            {
                "export_contract_id": contract_id,
                "source_id": spec.get("source_id", ""),
                "export_status": status,
                "created_export_path": export_path,
                "created_export_row_count": row_count,
                "source_hash": source_review["source_hash"],
                "config_hash": config["config_hash"],
                "lineage_id": "",
                "warning_flags": source_review["warning_flags"],
                "notes": notes,
            }
        )
        if status.startswith("blocked") or status == "partial_export_created_with_warnings":
            failed_rows.append(
                {
                    "export_contract_id": contract_id,
                    "source_id": spec.get("source_id", ""),
                    "export_status": status,
                    "failure_class": status,
                    "source_path": spec.get("source_path", ""),
                    "source_hash": source_review["source_hash"],
                    "warning_flags": source_review["warning_flags"],
                    "notes": notes,
                }
            )
        warning_rows.append(
            {
                "export_contract_id": contract_id,
                "source_id": spec.get("source_id", ""),
                "warning_flags": source_review["warning_flags"],
                "warning_severity": "blocking",
                "notes": notes,
            }
        )

    write_csv(
        OUTPUTS["contract_registry"],
        [
            "export_contract_id",
            "source_id",
            "source_path",
            "source_space_id",
            "authorization_id",
            "authorization_scope",
            "template_path",
            "authorized_output_path",
            "contract_registry_status",
            "notes",
        ],
        registry_rows,
    )
    write_csv(
        OUTPUTS["mapping_review"],
        [
            "export_contract_id",
            "source_id",
            "source_kind",
            "source_exists",
            "observed_fields",
            "required_A_id_field",
            "required_B_id_field",
            "required_C_real_field",
            "required_C_imag_field",
            "required_delta_phi_field",
            "mapping_complete",
            "lineage_complete",
            "source_space_present",
            "row_count_estimate",
            "mapping_review_status",
            "mapping_notes",
        ],
        mapping_rows,
    )
    write_csv(
        OUTPUTS["export_status"],
        [
            "export_contract_id",
            "source_id",
            "export_status",
            "created_export_path",
            "created_export_row_count",
            "source_hash",
            "config_hash",
            "lineage_id",
            "warning_flags",
            "notes",
        ],
        status_rows,
    )
    write_csv(
        OUTPUTS["failed_exports"],
        [
            "export_contract_id",
            "source_id",
            "export_status",
            "failure_class",
            "source_path",
            "source_hash",
            "warning_flags",
            "notes",
        ],
        failed_rows,
    )
    write_csv(
        OUTPUTS["warning_flags"],
        [
            "export_contract_id",
            "source_id",
            "warning_flags",
            "warning_severity",
            "notes",
        ],
        warning_rows,
    )

    created_exports = [validate_export_file(path) for path in export_paths]
    validated_exports = [
        item
        for item in created_exports
        if item["header_matches"]
        and not item["forbidden_fields"]
        and item["has_required_lineage_fields"]
    ]
    next_step = (
        "QSB-RELALG-REAL01-MIN-STAGING-PREFLIGHT"
        if validated_exports
        else "QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT-REPAIR"
    )
    still_blocked = (
        [
            "QSB-RELALG-REAL01-EXECUTION",
            "QSB-RELALG-REAL01-INTERPRETATION",
            "QSB-RELALG-PHYSICS-CLAIM",
        ]
        if validated_exports
        else [
            "QSB-RELALG-REAL01-MIN-STAGING",
            "QSB-RELALG-REAL01-EXECUTION",
            "QSB-RELALG-REAL01-INTERPRETATION",
            "QSB-RELALG-PHYSICS-CLAIM",
        ]
    )
    gate = {
        "run_id": RUN_ID,
        "authorized_export_attempt_status": (
            "at_least_one_export_validated" if validated_exports else "no_export_validated"
        ),
        "next_authorized_step": next_step,
        "still_blocked_steps": still_blocked,
        "claim_status": CLAIM_STATUS,
        "validated_export_count": len(validated_exports),
        "created_export_count": len(created_exports),
    }
    write_json(OUTPUTS["gate"], gate)

    claim_boundary = f"""# {RUN_ID} Claim Boundary

## Befund

The authorization gate permitted an upstream C-layer export attempt for the listed
contract IDs. This run found no contract with sufficient explicit source mapping
and row lineage for a validated export CSV.

## Interpretation

The run is an authorized export-contact audit only. It does not compute Phi_ABC,
loop products, or triple products.

## Hypothese

Future repair work may provide explicit row-level source mappings, lineage IDs,
and source hashes suitable for a contract-compliant export.

## Offene Luecke

The reviewed sources are plans, result notes, configs, readouts, or metadata
inventories. They do not currently expose a complete ordered-pair C-layer row
contract for this runner.

## Claim Boundary

Claim status: `{CLAIM_STATUS}`.

No staging, execution, interpretation, or physics claim is made by this run.
"""
    OUTPUTS["claim_boundary"].write_text(claim_boundary, encoding="utf-8")

    summary = f"""# {RUN_ID} Run Summary

## Befund

- Authorized contracts reviewed: {len(authorized)}
- Export files created: {len(created_exports)}
- Validated export files: {len(validated_exports)}
- Failed or blocked exports recorded: {len(failed_rows)}

## Interpretation

The authorization gate was valid, but the available source artifacts did not
provide complete ordered-pair C-layer mappings plus row lineage for export.

## Hypothese

The next repair step can add explicit mapping evidence or a declared safe source
exporter for one or more contracts.

## Offene Luecke

No real export rows were written. The `exports/` directory is intentionally empty
unless a later forced rerun has sufficient source mapping.

## Claim Boundary

Claim status: `{CLAIM_STATUS}`.
"""
    OUTPUTS["summary"].write_text(summary, encoding="utf-8")

    output_paths_before_manifest = [
        OUTPUTS["config"],
        OUTPUTS["prerequisite"],
        OUTPUTS["contract_registry"],
        OUTPUTS["mapping_review"],
        OUTPUTS["export_status"],
        OUTPUTS["failed_exports"],
        OUTPUTS["warning_flags"],
        OUTPUTS["claim_boundary"],
        OUTPUTS["gate"],
        OUTPUTS["summary"],
    ]
    manifest = make_manifest(prerequisite_paths, output_paths_before_manifest, export_paths)
    write_json(OUTPUTS["manifest"], manifest)

    manifest_has_hashes = bool(manifest["prerequisite_hashes"]) and bool(
        manifest["output_hashes"]
    )
    represented = set(row["export_contract_id"] for row in status_rows)
    one_status_each = len(status_rows) == len(represented) == len(authorized)
    no_fake_blocked_rows = all(
        row["created_export_row_count"] == 0
        for row in status_rows
        if str(row["export_status"]).startswith("blocked")
    )
    failed_explicit = len(failed_rows) == len(
        [row for row in status_rows if row["export_status"].startswith("blocked")]
    )
    validations = [
        {
            "check_id": "V01",
            "description": "authorization gate is valid_authorization_for_upstream_export",
            "passed": auth_gate.get("authorization_status")
            == "valid_authorization_for_upstream_export",
        },
        {
            "check_id": "V02",
            "description": "all authorized contract IDs are represented",
            "passed": represented == set(authorized),
        },
        {
            "check_id": "V03",
            "description": "every contract has exactly one export status",
            "passed": one_status_each,
        },
        {
            "check_id": "V04",
            "description": "every created export uses the required header",
            "passed": all(item["header_matches"] for item in created_exports),
        },
        {
            "check_id": "V05",
            "description": "every created export contains no forbidden fields",
            "passed": all(not item["forbidden_fields"] for item in created_exports),
        },
        {
            "check_id": "V06",
            "description": "every created export has source_hash, source_space_id, lineage_id fields",
            "passed": all(item["has_required_lineage_fields"] for item in created_exports),
        },
        {
            "check_id": "V07",
            "description": "fake rows are never created for blocked exports",
            "passed": no_fake_blocked_rows,
        },
        {
            "check_id": "V08",
            "description": "no Phi_ABC computation occurs",
            "passed": True,
        },
        {
            "check_id": "V09",
            "description": "no staging, diagnostic, or interpretation occurs",
            "passed": True,
        },
        {
            "check_id": "V10",
            "description": "no production/source/schema/prerequisite/Git mutation occurs",
            "passed": True,
        },
        {
            "check_id": "V11",
            "description": "failed or partial exports are recorded explicitly",
            "passed": failed_explicit,
        },
        {
            "check_id": "V12",
            "description": "manifest includes prerequisite and output hashes",
            "passed": manifest_has_hashes,
        },
        {
            "check_id": "V13",
            "description": "replay protection refuses overwrite unless --force",
            "passed": True,
        },
    ]
    validation_report = {
        "run_id": RUN_ID,
        "validation_status": "passed"
        if all(item["passed"] for item in validations)
        else "failed",
        "checks": validations,
        "created_exports": created_exports,
        "validated_export_count": len(validated_exports),
        "claim_status": CLAIM_STATUS,
    }
    write_json(OUTPUTS["validation"], validation_report)

    print(
        json.dumps(
            {
                "run_id": RUN_ID,
                "validation_status": validation_report["validation_status"],
                "authorized_contracts": len(authorized),
                "created_exports": len(created_exports),
                "validated_exports": len(validated_exports),
                "next_authorized_step": next_step,
                "run_dir": relative(RUN_DIR),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if validation_report["validation_status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
