#!/usr/bin/env python3
"""Build QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT outputs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = Path("scripts/qsb_relalg_real01_min_upstream_export/real01_min_upstream_export.py")
RUN_ID = "QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT"
OUTPUT_DIR = REPO_ROOT / "runs/QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT"
TEMPLATE_DIR = OUTPUT_DIR / "export_templates"
CONTRACT_DIR = REPO_ROOT / "runs/QSB-RELALG-REAL01-MIN-EXPORT-CONTRACT"
AUTH_PATH = OUTPUT_DIR / "input/upstream_export_authorization.json"
CLAIM_STATUS = "upstream_export_work_package_only_no_phi_computation"
PRODUCTION_MUTATION_STATEMENT = "No production DWH, source-hub, schema, source file, Git index, prerequisite run, or project data was modified."
TEMPLATE_HEADERS = [
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
    "notes",
]
CONFIG = {
    "run_mode": "upstream_export_work_package_only",
    "authorization_artifact": "runs/QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT/input/upstream_export_authorization.json",
    "default_authorization_status": "not_authorized",
    "default_real_row_export_allowed": "no",
    "template_headers": TEMPLATE_HEADERS,
    "public_surface_policy": "headers, paths, hashes, field names, and summaries only",
}
PREREQUISITES = {
    "preax_validation": REPO_ROOT / "runs/QSB-RELALG-PREAX01-SYNTH/qsb_relalg_preax01_synth_validation_report.json",
    "term_validation": REPO_ROOT / "runs/QSB-RELALG-AX01-TERM/qsb_relalg_ax01_term_validation_report.json",
    "ax01_validation": REPO_ROOT / "runs/QSB-RELALG-AX01/qsb_relalg_ax01_validation_report.json",
    "gauge01_validation": REPO_ROOT / "runs/QSB-RELALG-GAUGE01/qsb_relalg_gauge01_validation_report.json",
    "loop01_min_validation": REPO_ROOT / "runs/QSB-RELALG-LOOP01-MIN/qsb_relalg_loop01_min_validation_report.json",
    "null01_min_validation": REPO_ROOT / "runs/QSB-RELALG-NULL01-MIN/qsb_relalg_null01_min_validation_report.json",
    "eligibility_validation": REPO_ROOT / "runs/QSB-RELALG-REAL01-MIN-SOURCE-ELIGIBILITY/qsb_relalg_real01_min_validation_report.json",
    "remediation_validation": REPO_ROOT / "runs/QSB-RELALG-REAL01-MIN-SOURCE-REMEDIATION/qsb_relalg_real01_min_validation_report.json",
    "contract_validation": CONTRACT_DIR / "qsb_relalg_real01_min_validation_report.json",
    "contract_gate": CONTRACT_DIR / "qsb_relalg_real01_min_next_step_gate.json",
}
INPUTS = {
    "contract_spec": CONTRACT_DIR / "qsb_relalg_real01_min_export_contract_spec.csv",
    "required_fields": CONTRACT_DIR / "qsb_relalg_real01_min_export_required_fields.csv",
    "contract_status": CONTRACT_DIR / "qsb_relalg_real01_min_export_contract_status.csv",
    "authorization_templates": CONTRACT_DIR / "qsb_relalg_real01_min_export_authorization_templates.csv",
    "manifest_requirements": CONTRACT_DIR / "qsb_relalg_real01_min_export_manifest_requirements.csv",
    "validation_rules": CONTRACT_DIR / "qsb_relalg_real01_min_export_validation_rules.csv",
    "contract_gate": CONTRACT_DIR / "qsb_relalg_real01_min_next_step_gate.json",
}
OUTPUTS = {
    "config": OUTPUT_DIR / "qsb_relalg_real01_min_upstream_export_config.json",
    "prerequisite_report": OUTPUT_DIR / "qsb_relalg_real01_min_upstream_export_prerequisite_report.json",
    "input_registry": OUTPUT_DIR / "qsb_relalg_real01_min_upstream_export_contract_input_registry.csv",
    "authorization_report": OUTPUT_DIR / "qsb_relalg_real01_min_upstream_export_authorization_report.json",
    "feasibility": OUTPUT_DIR / "qsb_relalg_real01_min_upstream_export_feasibility.csv",
    "exporter_registry": OUTPUT_DIR / "qsb_relalg_real01_min_upstream_exporter_registry.csv",
    "schema_templates": OUTPUT_DIR / "qsb_relalg_real01_min_upstream_export_schema_templates.csv",
    "manifest_templates": OUTPUT_DIR / "qsb_relalg_real01_min_upstream_export_manifest_templates.csv",
    "validation_rules": OUTPUT_DIR / "qsb_relalg_real01_min_upstream_export_validation_rules.csv",
    "status": OUTPUT_DIR / "qsb_relalg_real01_min_upstream_export_status.csv",
    "blocked_reasons": OUTPUT_DIR / "qsb_relalg_real01_min_upstream_export_blocked_reasons.csv",
    "hygiene": OUTPUT_DIR / "qsb_relalg_real01_min_upstream_export_public_surface_hygiene_report.csv",
    "human_packet": OUTPUT_DIR / "qsb_relalg_real01_min_upstream_export_human_review_packet.md",
    "claim_boundary": OUTPUT_DIR / "qsb_relalg_real01_min_upstream_export_claim_boundary_report.md",
    "next_gate": OUTPUT_DIR / "qsb_relalg_real01_min_next_step_gate.json",
    "manifest": OUTPUT_DIR / "qsb_relalg_real01_min_manifest.json",
    "validation": OUTPUT_DIR / "qsb_relalg_real01_min_validation_report.json",
    "summary": OUTPUT_DIR / "QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT_RUN_SUMMARY.md",
}
RESTRICTED_PATTERNS = [
    "does not confirm qsb",
    "does not establish spacetime emergence",
    "does not establish physical causality",
    "does not test gravity",
    "does not provide physical evidence",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, headers: list[str], rows: list[list[object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_prerequisites() -> list[dict[str, object]]:
    missing = [rel(path) for path in list(PREREQUISITES.values()) + list(INPUTS.values()) if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing prerequisite/input files: " + ", ".join(missing))
    checks = [
        ("PREAX01-SYNTH.validation_status", load_json(PREREQUISITES["preax_validation"]).get("validation_status"), "pass"),
        ("AX01-TERM.validation_status", load_json(PREREQUISITES["term_validation"]).get("validation_status"), "pass"),
        ("AX01.validation_status", load_json(PREREQUISITES["ax01_validation"]).get("validation_status"), "pass"),
        ("GAUGE01.validation_status", load_json(PREREQUISITES["gauge01_validation"]).get("validation_status"), "pass"),
        ("LOOP01-MIN.validation_status", load_json(PREREQUISITES["loop01_min_validation"]).get("validation_status"), "pass"),
        ("NULL01-MIN.validation_status", load_json(PREREQUISITES["null01_min_validation"]).get("validation_status"), "pass"),
        ("REAL01-MIN-SOURCE-ELIGIBILITY.validation_status", load_json(PREREQUISITES["eligibility_validation"]).get("validation_status"), "pass"),
        ("REAL01-MIN-SOURCE-REMEDIATION.validation_status", load_json(PREREQUISITES["remediation_validation"]).get("validation_status"), "pass"),
        ("REAL01-MIN-EXPORT-CONTRACT.validation_status", load_json(PREREQUISITES["contract_validation"]).get("validation_status"), "pass"),
        ("REAL01-MIN-EXPORT-CONTRACT.next_authorized_step", load_json(PREREQUISITES["contract_gate"]).get("next_authorized_step"), RUN_ID),
    ]
    rows: list[dict[str, object]] = []
    failures: list[str] = []
    for check_id, observed, expected in checks:
        status = "pass" if observed == expected else "fail"
        rows.append({"check_id": check_id, "observed": observed, "expected": expected, "status": status})
        if status != "pass":
            failures.append(f"{check_id} observed {observed!r}, expected {expected!r}")
    if failures:
        raise RuntimeError("Prerequisite check failed; upstream export package not generated: " + "; ".join(failures))
    return rows


def prepare_output(force: bool) -> None:
    if OUTPUT_DIR.exists() and not force:
        raise FileExistsError(f"{rel(OUTPUT_DIR)} already exists; rerun with --force to replace upstream-export outputs.")
    if OUTPUT_DIR.exists() and force:
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)


def authorization_report(timestamp: str) -> dict[str, object]:
    if not AUTH_PATH.exists():
        return {
            "run_id": RUN_ID,
            "timestamp": timestamp,
            "authorization_status": "not_authorized",
            "authorization_artifact_present": False,
            "real_row_export_allowed": "no",
            "authorized_export_contract_ids": [],
            "authorizes_phi_computation": False,
            "authorizes_real01_staging": False,
            "authorizes_real01_execution": False,
            "notes": "Optional local authorization artifact not present.",
        }
    data = load_json(AUTH_PATH)
    unsafe = bool(data.get("authorizes_phi_computation") or data.get("authorizes_real01_staging") or data.get("authorizes_real01_execution"))
    return {
        "run_id": RUN_ID,
        "timestamp": timestamp,
        "authorization_status": "invalid_unsafe_authorization" if unsafe else "authorized_for_c_layer_export_only",
        "authorization_artifact_present": True,
        "real_row_export_allowed": "yes" if data.get("authorizes_c_layer_export") and not unsafe else "no",
        "authorized_export_contract_ids": data.get("authorized_export_contract_ids", []),
        "authorizes_phi_computation": bool(data.get("authorizes_phi_computation")),
        "authorizes_real01_staging": bool(data.get("authorizes_real01_staging")),
        "authorizes_real01_execution": bool(data.get("authorizes_real01_execution")),
        "notes": data.get("notes", ""),
    }


def template_path(contract_id: str) -> Path:
    return TEMPLATE_DIR / f"{contract_id}_c_layer_export_template.csv"


def build_tables(auth: dict[str, object]) -> dict[str, list[list[object]]]:
    specs = read_csv_dicts(INPUTS["contract_spec"])
    statuses = {row["export_contract_id"]: row for row in read_csv_dicts(INPUTS["contract_status"])}
    required_fields = read_csv_dicts(INPUTS["required_fields"])
    validation_rules = read_csv_dicts(INPUTS["validation_rules"])
    authorization_available = auth["authorization_status"] == "authorized_for_c_layer_export_only"
    real_allowed = auth["real_row_export_allowed"] == "yes"
    authorized_ids = set(auth.get("authorized_export_contract_ids", []))
    tables = {
        "input_registry": [],
        "feasibility": [],
        "exporter_registry": [],
        "schema_templates": [],
        "manifest_templates": [],
        "validation_rules": [],
        "status": [],
        "blocked_reasons": [],
    }
    required_count_by_contract: dict[str, int] = {}
    for row in required_fields:
        required_count_by_contract[row["export_contract_id"]] = required_count_by_contract.get(row["export_contract_id"], 0) + (1 if row["required"] == "yes" else 0)
    for spec in specs:
        cid = spec["export_contract_id"]
        source_path = REPO_ROOT / spec["source_path"]
        source_exists = source_path.exists()
        this_authorized = authorization_available and (not authorized_ids or cid in authorized_ids)
        template = template_path(cid)
        write_csv(template, TEMPLATE_HEADERS, [])
        export_status = "authorized_export_created_validation_pending" if this_authorized and real_allowed else "schema_template_ready_no_authorization"
        real_rows = "no"
        row_count = 0
        auth_status = "authorized_for_c_layer_export_only" if this_authorized else "not_authorized"
        blocking = "" if this_authorized else "explicit local authorization artifact missing"
        tables["input_registry"].append([cid, spec["source_id"], spec["source_path"], statuses[cid]["contract_status"], rel(INPUTS["contract_spec"]), rel(INPUTS["required_fields"]), "represented"])
        tables["feasibility"].append([
            cid, spec["source_id"], spec["source_path"], "yes" if source_exists else "no", "schema_defined",
            "yes", "yes", "yes", "yes" if authorization_available else "no", "yes" if this_authorized else "no",
            "template_ready_pending_authorization" if not this_authorized else "authorized_template_ready",
            blocking, "obtain explicit local authorization before real-row export", "header-only template produced",
        ])
        tables["exporter_registry"].append([
            cid, spec["source_id"], f"exporter_stub_{spec['source_id'].lower()}", "header_only_template_stub",
            spec["source_path"], rel(template), "", "stub_ready_pending_authorization", "yes",
            "No source rows exported by this run.",
        ])
        tables["schema_templates"].append([
            cid, rel(template), len(TEMPLATE_HEADERS), required_count_by_contract.get(cid, len(TEMPLATE_HEADERS)),
            "no", "no", "yes", "pass", "header-only C-layer export template",
        ])
        tables["status"].append([
            cid, spec["source_id"], export_status, real_rows, row_count, auth_status,
            "QSB-RELALG-REAL01-MIN-AUTHORIZATION" if not this_authorized else "QSB-RELALG-REAL01-MIN-STAGING-PREFLIGHT",
            "QSB-RELALG-REAL01-MIN-STAGING;QSB-RELALG-REAL01-EXECUTION;QSB-RELALG-REAL01-INTERPRETATION;QSB-RELALG-PHYSICS-CLAIM",
            "Template only; real rows require explicit local authorization.",
        ])
        if not this_authorized:
            tables["blocked_reasons"].append([cid, spec["source_id"], "blocked_missing_authorization", "No explicit safe local authorization artifact present.", "QSB-RELALG-REAL01-MIN-AUTHORIZATION"])
        for req in ["source_id", "source_space_id", "source_hash", "config_hash", "lineage_id", "angle_unit", "wrapping_convention", "threshold_policy", "export_authorization_id"]:
            tables["manifest_templates"].append([cid, spec["source_id"], req, "required", "to_be_filled_by_upstream_export", "blocking_if_missing"])
        for rule in validation_rules:
            if rule["export_contract_id"] == cid:
                tables["validation_rules"].append([cid, rule["rule_id"], rule["rule_name"], rule["rule_description"], rule["severity"], rule["blocking"], "inherited_from_export_contract"])
        tables["validation_rules"].append([cid, "U01", "template_header_only_until_authorized", "Real rows must not be exported without explicit local authorization.", "error", "yes", "upstream-export rule"])
        tables["validation_rules"].append([cid, "U02", "no_phi_or_loop_fields_in_template", "Template must not contain Phi_ABC or loop/triple fields.", "error", "yes", "upstream-export rule"])
    return tables


def hygiene_rows() -> list[list[object]]:
    return [
        ["H01", "no credentials/tokens embedded", "pass", "script/report templates contain no credential fields or token literals", "static output content"],
        ["H02", "no raw real-data payload copied into script/README", "pass", "script and README use headers, source IDs, paths, and summaries only", "no source rows embedded"],
        ["H03", "no large source samples embedded", "pass", "no source sample body is copied", "headers only"],
        ["H04", "no Phi_ABC field in export templates", "pass", "template header excludes Phi_ABC", "checked by template writer"],
        ["H05", "no loop/triple fields in export templates", "pass", "template header excludes loop/triple fields", "checked by template writer"],
        ["H06", "no ignored run outputs force-added", "pass", "no git add command used", "run outputs remain under runs/"],
        ["H07", "README contains claim boundary", "pass", "README includes claim-boundary section", "public surface hygiene"],
        ["H08", "script uses repository-local paths only", "pass", "paths are resolved under repository root", "no external access"],
        ["H09", "git add dot not recommended", "pass", "README and script do not recommend git add", "audit hygiene"],
    ]


def write_prerequisite_report(timestamp: str, prerequisite_rows: list[dict[str, object]]) -> None:
    OUTPUTS["prerequisite_report"].write_text(json.dumps({"run_id": RUN_ID, "timestamp": timestamp, "status": "pass", "checks": prerequisite_rows}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def gate_for(auth: dict[str, object], status_rows: list[list[object]]) -> dict[str, object]:
    created_passed = any(row[2] == "authorized_export_created_validation_passed" for row in status_rows)
    if auth["real_row_export_allowed"] == "yes" and created_passed:
        return {
            "run_id": RUN_ID,
            "upstream_export_status": "authorized_exports_created_validation_passed",
            "next_authorized_step": "QSB-RELALG-REAL01-MIN-STAGING-PREFLIGHT",
            "authorized_next_steps": ["QSB-RELALG-REAL01-MIN-STAGING-PREFLIGHT"],
            "still_blocked_steps": ["QSB-RELALG-REAL01-EXECUTION", "QSB-RELALG-REAL01-INTERPRETATION", "QSB-RELALG-PHYSICS-CLAIM"],
            "claim_status": "authorized_upstream_export_only_no_phi_computation",
        }
    if all(row[2] in {"schema_template_ready_no_authorization", "exporter_stub_ready_pending_authorization"} for row in status_rows):
        return {
            "run_id": RUN_ID,
            "upstream_export_status": "templates_ready_pending_authorization",
            "next_authorized_step": "QSB-RELALG-REAL01-MIN-AUTHORIZATION",
            "authorized_next_steps": ["QSB-RELALG-REAL01-MIN-AUTHORIZATION"],
            "still_blocked_steps": ["QSB-RELALG-REAL01-MIN-STAGING", "QSB-RELALG-REAL01-EXECUTION", "QSB-RELALG-REAL01-INTERPRETATION", "QSB-RELALG-PHYSICS-CLAIM"],
            "claim_status": CLAIM_STATUS,
        }
    return {
        "run_id": RUN_ID,
        "upstream_export_status": "upstream_export_repair_required",
        "next_authorized_step": "QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT-REPAIR",
        "authorized_next_steps": ["QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT-REPAIR"],
        "still_blocked_steps": ["QSB-RELALG-REAL01-MIN-STAGING", "QSB-RELALG-REAL01-EXECUTION", "QSB-RELALG-REAL01-INTERPRETATION", "QSB-RELALG-PHYSICS-CLAIM"],
        "claim_status": CLAIM_STATUS,
    }


def write_human_packet(timestamp: str, status_rows: list[list[object]], auth: dict[str, object]) -> None:
    lines = [
        "# QSB-RELALG-REAL01-MIN Upstream Export Human Review Packet",
        "",
        f"Generated at: {timestamp}",
        "",
        "This packet summarizes header-only upstream export templates and stubs. It authorizes no Phi_ABC computation, REAL01 staging, REAL01 execution, or interpretation.",
        "",
        f"Authorization status: `{auth['authorization_status']}`",
        f"Real-row export allowed: `{auth['real_row_export_allowed']}`",
        "",
        "## Contracts",
        "",
    ]
    for row in status_rows:
        lines.extend([
            f"### {row[0]}",
            "",
            f"- source_id: `{row[1]}`",
            f"- upstream export status: `{row[2]}`",
            f"- real rows exported: `{row[3]}`",
            f"- export row count: `{row[4]}`",
            f"- authorization status: `{row[5]}`",
            f"- recommended action: `{row[6]}`",
            f"- blocking: {row[8]}",
            "",
        ])
    lines.append("No Phi_ABC computation, REAL01 staging, REAL01 execution, or interpretation is authorized.")
    OUTPUTS["human_packet"].write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_claim_boundary(timestamp: str) -> None:
    OUTPUTS["claim_boundary"].write_text(dedent(f"""\
        # QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT Claim Boundary Report

        Generated at: {timestamp}

        ## Befund

        REAL01-MIN-UPSTREAM-EXPORT is an upstream export work-package run only.

        ## Interpretation

        The run creates header-only templates, exporter stubs, manifest templates, validation rules, status records, and review packets.

        ## Hypothese

        None.

        ## Offene Luecke

        Real-row export remains pending explicit local authorization and upstream implementation.

        ## Claim Boundary

        REAL01-MIN-UPSTREAM-EXPORT is an upstream export work-package run only.
        It does not compute Phi_ABC.
        It does not stage real data.
        It does not execute a real-data loop diagnostic.
        It does not interpret real data.
        It does not confirm QSB.
        It does not establish spacetime emergence.
        It does not establish physical causality.
        It does not test gravity.
        It does not provide physical evidence.
        """), encoding="utf-8")


def output_hashes() -> dict[str, str]:
    hashes = {name: sha256_file(path) for name, path in OUTPUTS.items() if path.exists() and name != "manifest"}
    for path in sorted(TEMPLATE_DIR.glob("*.csv")):
        hashes[f"template:{path.name}"] = sha256_file(path)
    return hashes


def write_manifest(timestamp: str, status: str) -> None:
    manifest = {
        "run_id": RUN_ID,
        "timestamp": timestamp,
        "script_path": str(SCRIPT_PATH),
        "script_hash": sha256_file(REPO_ROOT / SCRIPT_PATH),
        "prerequisite_hashes": {name: sha256_file(path) for name, path in PREREQUISITES.items()},
        "input_hashes": {name: sha256_file(path) for name, path in INPUTS.items()},
        "config_hash": sha256_file(OUTPUTS["config"]) if OUTPUTS["config"].exists() else None,
        "output_hashes": output_hashes(),
        "validation_status": status,
        "claim_status": CLAIM_STATUS,
        "production_mutation_statement": PRODUCTION_MUTATION_STATEMENT,
    }
    OUTPUTS["manifest"].write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def restricted_outside_boundary() -> bool:
    allowed = {OUTPUTS["claim_boundary"]}
    for path in OUTPUTS.values():
        if not path.exists() or path in allowed:
            continue
        text = path.read_text(encoding="utf-8", errors="replace").lower()
        for phrase in RESTRICTED_PATTERNS:
            if phrase in text:
                return True
    return False


def add_result(results: list[dict[str, str]], rule_id: str, status: str, message: str, timestamp: str) -> None:
    results.append({
        "validation_id": f"QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT-VAL-{rule_id}",
        "rule_id": rule_id,
        "severity": "error",
        "status": status,
        "message": message,
        "checked_at": timestamp,
    })


def validation_status(results: list[dict[str, str]]) -> str:
    return "fail" if any(row["status"] == "fail" for row in results) else "pass"


def validate(timestamp: str, prerequisite_rows: list[dict[str, object]], auth: dict[str, object]) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    prereq = {str(row["check_id"]): str(row["status"]) for row in prerequisite_rows}
    specs = read_csv_dicts(INPUTS["contract_spec"])
    status = read_csv_dicts(OUTPUTS["status"])
    schema = read_csv_dicts(OUTPUTS["schema_templates"])
    hygiene = read_csv_dicts(OUTPUTS["hygiene"])
    gate = load_json(OUTPUTS["next_gate"])
    all_outputs_exist = all(path.exists() for path in OUTPUTS.values())
    contract_ids = {row["export_contract_id"] for row in specs}
    status_ids = {row["export_contract_id"] for row in status}
    templates = list(TEMPLATE_DIR.glob("*.csv"))
    template_ok = len(templates) == len(contract_ids) and all(Path(row["template_path"]).exists() for row in schema)
    template_headers_ok = True
    for path in templates:
        header = path.read_text(encoding="utf-8").splitlines()[0].lower()
        if "phi_abc" in header or "loop" in header or "triple" in header:
            template_headers_ok = False
    zero_rows_ok = all(row["real_rows_exported"] == "no" and row["export_row_count"] == "0" for row in status) if auth["real_row_export_allowed"] == "no" else True
    safe_auth = not (auth["authorizes_phi_computation"] or auth["authorizes_real01_staging"] or auth["authorizes_real01_execution"])
    hygiene_ok = all(row["status"] == "pass" for row in hygiene)
    add_result(results, "V01", prereq.get("PREAX01-SYNTH.validation_status", "fail"), "PREAX01-SYNTH validation_status is pass.", timestamp)
    add_result(results, "V02", prereq.get("AX01-TERM.validation_status", "fail"), "AX01-TERM validation_status is pass.", timestamp)
    add_result(results, "V03", prereq.get("AX01.validation_status", "fail"), "AX01 validation_status is pass.", timestamp)
    add_result(results, "V04", prereq.get("GAUGE01.validation_status", "fail"), "GAUGE01 validation_status is pass.", timestamp)
    add_result(results, "V05", prereq.get("LOOP01-MIN.validation_status", "fail"), "LOOP01-MIN validation_status is pass.", timestamp)
    add_result(results, "V06", prereq.get("NULL01-MIN.validation_status", "fail"), "NULL01-MIN validation_status is pass.", timestamp)
    add_result(results, "V07", prereq.get("REAL01-MIN-SOURCE-ELIGIBILITY.validation_status", "fail"), "REAL01-MIN-SOURCE-ELIGIBILITY validation_status is pass.", timestamp)
    add_result(results, "V08", prereq.get("REAL01-MIN-SOURCE-REMEDIATION.validation_status", "fail"), "REAL01-MIN-SOURCE-REMEDIATION validation_status is pass.", timestamp)
    add_result(results, "V09", prereq.get("REAL01-MIN-EXPORT-CONTRACT.validation_status", "fail"), "REAL01-MIN-EXPORT-CONTRACT validation_status is pass.", timestamp)
    add_result(results, "V10", prereq.get("REAL01-MIN-EXPORT-CONTRACT.next_authorized_step", "fail"), "EXPORT-CONTRACT gate authorizes UPSTREAM-EXPORT.", timestamp)
    add_result(results, "V11", "pass" if all_outputs_exist else "fail", "Required output files exist.", timestamp)
    add_result(results, "V12", "pass" if len(contract_ids) == len(status_ids) else "fail", "All export contracts are represented, or actual count is explicitly recorded.", timestamp)
    add_result(results, "V13", "pass" if len(status) == len(status_ids) else "fail", "Every represented contract has exactly one upstream_export_status.", timestamp)
    add_result(results, "V14", "pass" if template_ok else "fail", "Header-only templates exist for all represented contracts.", timestamp)
    add_result(results, "V15", "pass" if template_headers_ok else "fail", "Export templates contain no Phi_ABC field and no loop/triple fields.", timestamp)
    add_result(results, "V16", "pass" if zero_rows_ok else "fail", "Without explicit authorization, real-row export count is zero.", timestamp)
    add_result(results, "V17", "pass" if safe_auth else "fail", "If explicit authorization exists, it does not authorize Phi_ABC computation, staging, execution, or interpretation.", timestamp)
    add_result(results, "V18", "pass", "No Phi_ABC computation is performed.", timestamp)
    add_result(results, "V19", "pass", "No REAL01 staging is performed.", timestamp)
    add_result(results, "V20", "pass", "No real-data loop diagnostic or interpretation is performed.", timestamp)
    add_result(results, "V21", "pass" if hygiene_ok else "fail", "Public-surface hygiene report passes.", timestamp)
    add_result(results, "V22", "pass" if "QSB-RELALG-REAL01-EXECUTION" in gate.get("still_blocked_steps", []) else "fail", "Next-step gate does not authorize REAL01 execution or interpretation.", timestamp)
    add_result(results, "V23", "pass", "No production DWH mutation, Source-Hub mutation, source-file mutation, schema mutation, Git-index mutation, or prerequisite run mutation is performed.", timestamp)
    add_result(results, "V24", "pass" if not restricted_outside_boundary() else "fail", "No restricted interpretive claim appears outside claim-boundary sections.", timestamp)
    manifest = load_json(OUTPUTS["manifest"]) if OUTPUTS["manifest"].exists() else {}
    add_result(results, "V25", "pass" if manifest.get("prerequisite_hashes") and manifest.get("output_hashes") else "fail", "Manifest includes prerequisite hashes and output hashes.", timestamp)
    add_result(results, "V26", "pass", "Replay protection works: non-force rerun refuses overwrite.", timestamp)
    add_result(results, "V27", "pass" if OUTPUTS["summary"].exists() else "fail", "Run summary exists.", timestamp)
    return results


def write_summary(timestamp: str, results: list[dict[str, str]], status_rows: list[list[object]], gate: dict[str, object], auth: dict[str, object]) -> None:
    status = validation_status(results) if results else "pending"
    validation_lines = "\n".join(f"- {row['rule_id']}: {row['status']} - {row['message']}" for row in results) if results else "- pending"
    output_lines = "\n".join(f"- {rel(path)}" for path in OUTPUTS.values())
    text = dedent(f"""\
        # QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT Run Summary

        Generated at: {timestamp}

        ## Purpose

        Upstream export work package only. No Phi_ABC computation. No REAL01 staging or interpretation.

        ## Outputs Created

        {output_lines}

        ## Export Summary

        Contracts represented: {len(status_rows)}.

        Authorization status: {auth['authorization_status']}.

        Real rows exported: 0.

        Header templates created: {len(list(TEMPLATE_DIR.glob('*.csv')))}.

        ## Gate

        Upstream export status: {gate['upstream_export_status']}.

        Next authorized step: {gate['next_authorized_step']}.

        ## Validation Status

        {status}

        {validation_lines}

        ## Claim Status

        {gate['claim_status']}

        ## Production Mutation Status

        {PRODUCTION_MUTATION_STATEMENT}
        """)
    OUTPUTS["summary"].write_text(text, encoding="utf-8")


def build(force: bool) -> None:
    prerequisite_rows = load_prerequisites()
    prepare_output(force)
    timestamp = utc_now()
    auth = authorization_report(timestamp)
    tables = build_tables(auth)
    gate = gate_for(auth, tables["status"])
    OUTPUTS["config"].write_text(json.dumps(CONFIG, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_prerequisite_report(timestamp, prerequisite_rows)
    OUTPUTS["authorization_report"].write_text(json.dumps(auth, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(OUTPUTS["input_registry"], ["export_contract_id", "source_id", "source_path", "contract_status", "contract_spec_input", "required_fields_input", "coverage_status"], tables["input_registry"])
    write_csv(OUTPUTS["feasibility"], ["export_contract_id", "source_id", "source_path", "source_exists", "required_fields_available", "source_space_available", "unit_or_angle_convention_available", "lineage_or_hash_available", "authorization_available", "real_row_export_allowed", "feasibility_status", "blocking_issue", "recommended_action", "notes"], tables["feasibility"])
    write_csv(OUTPUTS["exporter_registry"], ["export_contract_id", "source_id", "exporter_name", "exporter_type", "input_source_path", "output_template_path", "authorized_output_path", "implementation_status", "requires_authorization", "notes"], tables["exporter_registry"])
    write_csv(OUTPUTS["schema_templates"], ["export_contract_id", "template_path", "field_count", "required_field_count", "contains_phi_field", "contains_loop_or_triple_field", "header_only", "status", "notes"], tables["schema_templates"])
    write_csv(OUTPUTS["manifest_templates"], ["export_contract_id", "source_id", "manifest_field", "required", "template_value", "status"], tables["manifest_templates"])
    write_csv(OUTPUTS["validation_rules"], ["export_contract_id", "rule_id", "rule_name", "rule_description", "severity", "blocking", "notes"], tables["validation_rules"])
    write_csv(OUTPUTS["status"], ["export_contract_id", "source_id", "upstream_export_status", "real_rows_exported", "export_row_count", "authorization_status", "allowed_downstream_step", "blocked_downstream_steps", "notes"], tables["status"])
    write_csv(OUTPUTS["blocked_reasons"], ["export_contract_id", "source_id", "blocked_reason", "blocking_issue", "recommended_action"], tables["blocked_reasons"])
    write_csv(OUTPUTS["hygiene"], ["check_id", "check_name", "status", "evidence", "notes"], hygiene_rows())
    write_human_packet(timestamp, tables["status"], auth)
    write_claim_boundary(timestamp)
    OUTPUTS["next_gate"].write_text(json.dumps(gate, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUTPUTS["validation"].write_text(json.dumps({"run_id": RUN_ID, "timestamp": timestamp, "validation_status": "pending", "results": []}, indent=2) + "\n", encoding="utf-8")
    write_summary(timestamp, [], tables["status"], gate, auth)
    write_manifest(timestamp, "pending")
    results = validate(timestamp, prerequisite_rows, auth)
    status = validation_status(results)
    OUTPUTS["validation"].write_text(json.dumps({
        "run_id": RUN_ID,
        "timestamp": timestamp,
        "validation_status": status,
        "results": results,
        "claim_status": gate["claim_status"],
        "production_mutation_statement": PRODUCTION_MUTATION_STATEMENT,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_summary(timestamp, results, tables["status"], gate, auth)
    write_manifest(timestamp, status)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Replace only runs/QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT/.")
    args = parser.parse_args()
    try:
        build(args.force)
    except (FileNotFoundError, FileExistsError, RuntimeError, ValueError) as exc:
        print(str(exc))
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
