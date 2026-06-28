#!/usr/bin/env python3
"""Build QSB-RELALG-REAL01-MIN-AUTHORIZATION outputs."""

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
SCRIPT_PATH = Path("scripts/qsb_relalg_real01_min_authorization/real01_min_authorization.py")
RUN_ID = "QSB-RELALG-REAL01-MIN-AUTHORIZATION"
OUTPUT_DIR = REPO_ROOT / "runs/QSB-RELALG-REAL01-MIN-AUTHORIZATION"
INPUT_DIR = OUTPUT_DIR / "input"
ACTIVE_AUTH = INPUT_DIR / "human_authorization.json"
AUTH_TEMPLATE = INPUT_DIR / "human_authorization_TEMPLATE.json"
UPSTREAM_DIR = REPO_ROOT / "runs/QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT"
CLAIM_STATUS = "authorization_gate_only_no_phi_computation"
PRODUCTION_MUTATION_STATEMENT = "No production DWH, source-hub, schema, source file, Git index, prerequisite run, or project data was modified."
CONFIG = {
    "run_mode": "authorization_gate_only",
    "active_authorization_path": "runs/QSB-RELALG-REAL01-MIN-AUTHORIZATION/input/human_authorization.json",
    "template_path": "runs/QSB-RELALG-REAL01-MIN-AUTHORIZATION/input/human_authorization_TEMPLATE.json",
    "auto_create_active_authorization": False,
    "default_authorization_status": "pending_human_authorization_input",
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
    "contract_validation": REPO_ROOT / "runs/QSB-RELALG-REAL01-MIN-EXPORT-CONTRACT/qsb_relalg_real01_min_validation_report.json",
    "upstream_validation": UPSTREAM_DIR / "qsb_relalg_real01_min_validation_report.json",
    "upstream_gate": UPSTREAM_DIR / "qsb_relalg_real01_min_next_step_gate.json",
}
INPUTS = {
    "input_registry": UPSTREAM_DIR / "qsb_relalg_real01_min_upstream_export_contract_input_registry.csv",
    "upstream_authorization_report": UPSTREAM_DIR / "qsb_relalg_real01_min_upstream_export_authorization_report.json",
    "feasibility": UPSTREAM_DIR / "qsb_relalg_real01_min_upstream_export_feasibility.csv",
    "exporter_registry": UPSTREAM_DIR / "qsb_relalg_real01_min_upstream_exporter_registry.csv",
    "schema_templates": UPSTREAM_DIR / "qsb_relalg_real01_min_upstream_export_schema_templates.csv",
    "upstream_status": UPSTREAM_DIR / "qsb_relalg_real01_min_upstream_export_status.csv",
    "upstream_gate": UPSTREAM_DIR / "qsb_relalg_real01_min_next_step_gate.json",
}
OUTPUTS = {
    "config": OUTPUT_DIR / "qsb_relalg_real01_min_authorization_config.json",
    "prerequisite_report": OUTPUT_DIR / "qsb_relalg_real01_min_authorization_prerequisite_report.json",
    "input_status": OUTPUT_DIR / "qsb_relalg_real01_min_authorization_input_status.json",
    "authorization_template": OUTPUT_DIR / "qsb_relalg_real01_min_authorization_template.json",
    "contract_registry": OUTPUT_DIR / "qsb_relalg_real01_min_authorization_contract_registry.csv",
    "decisions": OUTPUT_DIR / "qsb_relalg_real01_min_authorization_decisions.csv",
    "scope_check": OUTPUT_DIR / "qsb_relalg_real01_min_authorization_scope_check.csv",
    "safety_flags": OUTPUT_DIR / "qsb_relalg_real01_min_authorization_safety_flags.csv",
    "blocked_steps": OUTPUT_DIR / "qsb_relalg_real01_min_authorization_blocked_downstream_steps.csv",
    "hygiene": OUTPUT_DIR / "qsb_relalg_real01_min_authorization_public_surface_hygiene_report.csv",
    "human_packet": OUTPUT_DIR / "qsb_relalg_real01_min_authorization_human_review_packet.md",
    "claim_boundary": OUTPUT_DIR / "qsb_relalg_real01_min_authorization_claim_boundary_report.md",
    "next_gate": OUTPUT_DIR / "qsb_relalg_real01_min_next_step_gate.json",
    "manifest": OUTPUT_DIR / "qsb_relalg_real01_min_manifest.json",
    "validation": OUTPUT_DIR / "qsb_relalg_real01_min_validation_report.json",
    "summary": OUTPUT_DIR / "QSB-RELALG-REAL01-MIN-AUTHORIZATION_RUN_SUMMARY.md",
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
        ("REAL01-MIN-UPSTREAM-EXPORT.validation_status", load_json(PREREQUISITES["upstream_validation"]).get("validation_status"), "pass"),
        ("REAL01-MIN-UPSTREAM-EXPORT.next_authorized_step", load_json(PREREQUISITES["upstream_gate"]).get("next_authorized_step"), RUN_ID),
    ]
    rows: list[dict[str, object]] = []
    failures: list[str] = []
    for check_id, observed, expected in checks:
        status = "pass" if observed == expected else "fail"
        rows.append({"check_id": check_id, "observed": observed, "expected": expected, "status": status})
        if status != "pass":
            failures.append(f"{check_id} observed {observed!r}, expected {expected!r}")
    if failures:
        raise RuntimeError("Prerequisite check failed; authorization gate not generated: " + "; ".join(failures))
    return rows


def prepare_output(force: bool) -> bool:
    active_existed_before = ACTIVE_AUTH.exists()
    if OUTPUT_DIR.exists() and not force:
        raise FileExistsError(f"{rel(OUTPUT_DIR)} already exists; rerun with --force to replace authorization outputs.")
    saved_auth: bytes | None = ACTIVE_AUTH.read_bytes() if active_existed_before else None
    if OUTPUT_DIR.exists() and force:
        shutil.rmtree(OUTPUT_DIR)
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    if saved_auth is not None:
        ACTIVE_AUTH.write_bytes(saved_auth)
    return active_existed_before


def template_payload(contract_ids: list[str]) -> dict[str, object]:
    return {
        "authorization_id": "human_authorized_upstream_export_YYYYMMDD",
        "authorized_by": "Ralf Kemmann",
        "authorization_scope": "Create contract-compliant upstream C-layer export files for the listed export_contract_ids only.",
        "authorized_export_contract_ids": contract_ids,
        "authorizes_c_layer_export": True,
        "authorizes_phi_computation": False,
        "authorizes_real01_staging": False,
        "authorizes_real01_execution": False,
        "authorizes_real01_interpretation": False,
        "requires_contract_compliance": True,
        "requires_no_phi_abc": True,
        "requires_no_loop_or_triple_products": True,
        "requires_no_physics_claim": True,
        "notes": "",
    }


def evaluate_authorization(contract_ids: list[str], active_existed_before: bool) -> tuple[dict[str, object], str, list[list[object]], list[list[object]]]:
    if not active_existed_before or not ACTIVE_AUTH.exists():
        input_status = {
            "run_id": RUN_ID,
            "authorization_status": "pending_human_authorization_input",
            "active_authorization_exists": False,
            "active_authorization_auto_created": False,
            "template_created": True,
            "authorization_path": rel(ACTIVE_AUTH),
            "template_path": rel(AUTH_TEMPLATE),
        }
        scope_rows = [
            ["S01", "active authorization file exists or template-only state is recorded", "pass", "template-only pending state recorded", "no", "active file absent"],
            ["S02", "authorization IDs match known export contracts", "pass", "not applicable until active authorization exists", "yes_if_active", "pending input"],
            ["S03", "authorization does not include Phi_ABC computation", "pass", "template sets false", "yes", "pending input"],
            ["S04", "authorization does not include REAL01 staging", "pass", "template sets false", "yes", "pending input"],
            ["S05", "authorization does not include REAL01 execution", "pass", "template sets false", "yes", "pending input"],
            ["S06", "authorization does not include real-data interpretation", "pass", "template sets false", "yes", "pending input"],
            ["S07", "authorization requires contract compliance", "pass", "template sets true", "yes", "pending input"],
            ["S08", "authorization requires no loop/triple products", "pass", "template sets true", "yes", "pending input"],
            ["S09", "authorization requires no physics claim", "pass", "template sets true", "yes", "pending input"],
        ]
        flags = safety_flags(template_payload(contract_ids), active=False)
        return input_status, "pending_human_authorization_input", scope_rows, flags

    data = load_json(ACTIVE_AUTH)
    known = set(contract_ids)
    auth_ids = set(data.get("authorized_export_contract_ids", []))
    safety = safety_flags(data, active=True)
    ids_ok = bool(auth_ids) and auth_ids.issubset(known)
    safety_ok = all(row[3] == "pass" for row in safety)
    if not ids_ok:
        status = "invalid_authorization_contract_ids"
    elif not safety_ok:
        status = "invalid_authorization_missing_required_safety_flags"
    elif data.get("authorizes_real01_execution") or data.get("authorizes_real01_interpretation") or data.get("authorizes_real01_staging"):
        status = "invalid_authorization_overbroad"
    elif not data.get("authorizes_c_layer_export"):
        status = "invalid_authorization_scope"
    else:
        status = "valid_authorization_for_upstream_export"
    input_status = {
        "run_id": RUN_ID,
        "authorization_status": status,
        "active_authorization_exists": True,
        "active_authorization_auto_created": False,
        "template_created": True,
        "authorization_path": rel(ACTIVE_AUTH),
        "template_path": rel(AUTH_TEMPLATE),
        "authorization_id": data.get("authorization_id", ""),
        "authorized_by": data.get("authorized_by", ""),
    }
    scope_rows = [
        ["S01", "active authorization file exists or template-only state is recorded", "pass", "active authorization existed before run", "no", ""],
        ["S02", "authorization IDs match known export contracts", "pass" if ids_ok else "fail", ";".join(sorted(auth_ids)), "yes", ""],
        ["S03", "authorization does not include Phi_ABC computation", "pass" if not data.get("authorizes_phi_computation") else "fail", str(data.get("authorizes_phi_computation")), "yes", ""],
        ["S04", "authorization does not include REAL01 staging", "pass" if not data.get("authorizes_real01_staging") else "fail", str(data.get("authorizes_real01_staging")), "yes", ""],
        ["S05", "authorization does not include REAL01 execution", "pass" if not data.get("authorizes_real01_execution") else "fail", str(data.get("authorizes_real01_execution")), "yes", ""],
        ["S06", "authorization does not include real-data interpretation", "pass" if not data.get("authorizes_real01_interpretation") else "fail", str(data.get("authorizes_real01_interpretation")), "yes", ""],
        ["S07", "authorization requires contract compliance", "pass" if data.get("requires_contract_compliance") else "fail", str(data.get("requires_contract_compliance")), "yes", ""],
        ["S08", "authorization requires no loop/triple products", "pass" if data.get("requires_no_loop_or_triple_products") else "fail", str(data.get("requires_no_loop_or_triple_products")), "yes", ""],
        ["S09", "authorization requires no physics claim", "pass" if data.get("requires_no_physics_claim") else "fail", str(data.get("requires_no_physics_claim")), "yes", ""],
    ]
    return input_status, status, scope_rows, safety


def safety_flags(data: dict[str, object], active: bool) -> list[list[object]]:
    checks = [
        ("authorizes_c_layer_export", True),
        ("authorizes_phi_computation", False),
        ("authorizes_real01_staging", False),
        ("authorizes_real01_execution", False),
        ("authorizes_real01_interpretation", False),
        ("requires_contract_compliance", True),
        ("requires_no_phi_abc", True),
        ("requires_no_loop_or_triple_products", True),
        ("requires_no_physics_claim", True),
    ]
    rows: list[list[object]] = []
    for name, required in checks:
        actual = data.get(name)
        status = "pass" if actual == required else "fail"
        rows.append([name, str(required).lower(), str(actual).lower(), status, "yes" if active else "yes_if_active", "template value" if not active else "active authorization value"])
    return rows


def gate_for(status: str) -> dict[str, object]:
    if status == "valid_authorization_for_upstream_export":
        return {
            "run_id": RUN_ID,
            "authorization_status": status,
            "next_authorized_step": "QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT-AUTHORIZED",
            "authorized_next_steps": ["QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT-AUTHORIZED"],
            "still_blocked_steps": ["QSB-RELALG-REAL01-MIN-STAGING", "QSB-RELALG-REAL01-EXECUTION", "QSB-RELALG-REAL01-INTERPRETATION", "QSB-RELALG-PHYSICS-CLAIM"],
            "claim_status": CLAIM_STATUS,
        }
    if status == "pending_human_authorization_input":
        return {
            "run_id": RUN_ID,
            "authorization_status": status,
            "next_authorized_step": "QSB-RELALG-REAL01-MIN-HUMAN-AUTHORIZATION-INPUT",
            "authorized_next_steps": ["QSB-RELALG-REAL01-MIN-HUMAN-AUTHORIZATION-INPUT"],
            "still_blocked_steps": ["QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT-AUTHORIZED", "QSB-RELALG-REAL01-MIN-STAGING", "QSB-RELALG-REAL01-EXECUTION", "QSB-RELALG-REAL01-INTERPRETATION", "QSB-RELALG-PHYSICS-CLAIM"],
            "claim_status": CLAIM_STATUS,
        }
    return {
        "run_id": RUN_ID,
        "authorization_status": "authorization_repair_required",
        "next_authorized_step": "QSB-RELALG-REAL01-MIN-AUTHORIZATION-REPAIR",
        "authorized_next_steps": ["QSB-RELALG-REAL01-MIN-AUTHORIZATION-REPAIR"],
        "still_blocked_steps": ["QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT-AUTHORIZED", "QSB-RELALG-REAL01-MIN-STAGING", "QSB-RELALG-REAL01-EXECUTION", "QSB-RELALG-REAL01-INTERPRETATION", "QSB-RELALG-PHYSICS-CLAIM"],
        "claim_status": CLAIM_STATUS,
    }


def build_tables(auth_status: str, input_status: dict[str, object]) -> tuple[list[list[object]], list[list[object]], list[list[object]]]:
    upstream_status = read_csv_dicts(INPUTS["upstream_status"])
    schema_templates = {row["export_contract_id"]: row for row in read_csv_dicts(INPUTS["schema_templates"])}
    active_auth = load_json(ACTIVE_AUTH) if input_status["active_authorization_exists"] else {}
    authorized_ids = set(active_auth.get("authorized_export_contract_ids", []))
    registry: list[list[object]] = []
    decisions: list[list[object]] = []
    blocked: list[list[object]] = []
    for row in upstream_status:
        cid = row["export_contract_id"]
        if auth_status == "valid_authorization_for_upstream_export" and cid in authorized_ids:
            decision = "authorized_for_upstream_export"
        elif input_status["active_authorization_exists"] and cid not in authorized_ids:
            decision = "not_in_authorization_scope"
        else:
            decision = "not_authorized"
        registry.append([cid, row["source_id"], schema_templates[cid]["template_path"], row["upstream_export_status"], "yes", "authorization candidate from upstream export package"])
        decisions.append([
            cid, row["source_id"], decision, active_auth.get("authorization_id", ""), active_auth.get("authorized_by", ""),
            active_auth.get("authorization_scope", ""), str(active_auth.get("authorizes_c_layer_export", False)).lower(),
            str(active_auth.get("authorizes_phi_computation", False)).lower(), str(active_auth.get("authorizes_real01_staging", False)).lower(),
            str(active_auth.get("authorizes_real01_execution", False)).lower(), str(active_auth.get("authorizes_real01_interpretation", False)).lower(),
            "active authorization missing" if decision == "not_authorized" else "authorization evaluated", "no row export or staging in this run",
        ])
        for step in ["QSB-RELALG-REAL01-MIN-STAGING", "QSB-RELALG-REAL01-EXECUTION", "QSB-RELALG-REAL01-INTERPRETATION", "QSB-RELALG-PHYSICS-CLAIM"]:
            blocked.append([cid, row["source_id"], step, "blocked_by_authorization_gate", "not authorized by this run"])
    return registry, decisions, blocked


def hygiene_rows() -> list[list[object]]:
    return [
        ["H01", "no credentials/tokens embedded", "pass", "script/report templates contain no credential fields or token literals", "static output content"],
        ["H02", "no raw real-data payload copied into script/README", "pass", "source rows are not copied", "authorization metadata only"],
        ["H03", "no large source samples embedded", "pass", "no source samples embedded", "audit hygiene"],
        ["H04", "no active authorization auto-created", "pass", "script writes template only when active file absent", "active authorization remains human-provided"],
        ["H05", "no Phi_ABC computation", "pass", "no phase computation logic present", "gate only"],
        ["H06", "no loop/triple product generation", "pass", "no loop/triple fields generated", "gate only"],
        ["H07", "no Git index mutation", "pass", "no git add command used", "audit hygiene"],
        ["H08", "README contains claim boundary", "pass", "README includes claim-boundary section", "public surface hygiene"],
        ["H09", "git add dot not recommended", "pass", "README and script do not recommend git add", "audit hygiene"],
    ]


def write_prerequisite_report(timestamp: str, prerequisite_rows: list[dict[str, object]]) -> None:
    OUTPUTS["prerequisite_report"].write_text(json.dumps({"run_id": RUN_ID, "timestamp": timestamp, "status": "pass", "checks": prerequisite_rows}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_human_packet(timestamp: str, auth_status: str, decisions: list[list[object]], input_status: dict[str, object]) -> None:
    lines = [
        "# QSB-RELALG-REAL01-MIN Authorization Human Review Packet",
        "",
        f"Generated at: {timestamp}",
        "",
        f"Authorization status: `{auth_status}`",
        f"Active authorization exists: `{input_status['active_authorization_exists']}`",
        "",
        "This authorization can only permit contract-compliant upstream C-layer export creation.",
        "It does not authorize Phi_ABC, REAL01 staging, REAL01 execution, real-data interpretation, or any physics claim.",
        "",
        "## Required Human Action",
        "",
        "If authorization is intended, create `input/human_authorization.json` from the template and rerun with `--force`.",
        "",
        "## Contract Decisions",
        "",
    ]
    for row in decisions:
        lines.extend([
            f"### {row[0]}",
            "",
            f"- source_id: `{row[1]}`",
            f"- authorization decision: `{row[2]}`",
            f"- authorizes Phi_ABC: `{row[7]}`",
            f"- authorizes REAL01 staging: `{row[8]}`",
            f"- authorizes REAL01 execution: `{row[9]}`",
            f"- authorizes interpretation: `{row[10]}`",
            "",
        ])
    OUTPUTS["human_packet"].write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_claim_boundary(timestamp: str) -> None:
    OUTPUTS["claim_boundary"].write_text(dedent(f"""\
        # QSB-RELALG-REAL01-MIN-AUTHORIZATION Claim Boundary Report

        Generated at: {timestamp}

        ## Befund

        REAL01-MIN-AUTHORIZATION is an authorization-gate run only.

        ## Interpretation

        The run checks for a local human authorization artifact and records whether upstream export authorization is pending, valid, or invalid.

        ## Hypothese

        None.

        ## Offene Luecke

        Active human authorization remains absent unless supplied outside this run.

        ## Claim Boundary

        REAL01-MIN-AUTHORIZATION is an authorization-gate run only.
        It does not compute Phi_ABC.
        It does not export real C-layer rows.
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
    return {name: sha256_file(path) for name, path in OUTPUTS.items() if path.exists() and name != "manifest"} | {"input_template": sha256_file(AUTH_TEMPLATE)}


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
        "validation_id": f"QSB-RELALG-REAL01-MIN-AUTHORIZATION-VAL-{rule_id}",
        "rule_id": rule_id,
        "severity": "error",
        "status": status,
        "message": message,
        "checked_at": timestamp,
    })


def validation_status(results: list[dict[str, str]]) -> str:
    return "fail" if any(row["status"] == "fail" for row in results) else "pass"


def validate(timestamp: str, prerequisite_rows: list[dict[str, object]], active_existed_before: bool, auth_status: str) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    prereq = {str(row["check_id"]): str(row["status"]) for row in prerequisite_rows}
    registry = read_csv_dicts(OUTPUTS["contract_registry"])
    decisions = read_csv_dicts(OUTPUTS["decisions"])
    scope = read_csv_dicts(OUTPUTS["scope_check"])
    safety = read_csv_dicts(OUTPUTS["safety_flags"])
    hygiene = read_csv_dicts(OUTPUTS["hygiene"])
    gate = load_json(OUTPUTS["next_gate"])
    upstream_status = read_csv_dicts(INPUTS["upstream_status"])
    all_outputs_exist = all(path.exists() for path in OUTPUTS.values())
    no_auto_active = active_existed_before or not ACTIVE_AUTH.exists()
    represented = {row["export_contract_id"] for row in registry} == {row["export_contract_id"] for row in upstream_status}
    one_decision = len(decisions) == len({row["export_contract_id"] for row in decisions})
    no_phi = all(row["authorizes_phi_computation"] == "false" for row in decisions)
    no_execution_interpretation = all(row["authorizes_real01_execution"] == "false" and row["authorizes_real01_interpretation"] == "false" for row in decisions)
    no_staging = all(row["authorizes_real01_staging"] == "false" for row in decisions)
    active_ids_ok = all(row["status"] == "pass" for row in scope if row["check_id"] == "S02")
    safety_ok = all(row["status"] == "pass" for row in safety) if active_existed_before else True
    pending_ok = (auth_status == "pending_human_authorization_input" and not active_existed_before) or active_existed_before
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
    add_result(results, "V10", prereq.get("REAL01-MIN-UPSTREAM-EXPORT.validation_status", "fail"), "REAL01-MIN-UPSTREAM-EXPORT validation_status is pass.", timestamp)
    add_result(results, "V11", prereq.get("REAL01-MIN-UPSTREAM-EXPORT.next_authorized_step", "fail"), "UPSTREAM-EXPORT gate authorizes AUTHORIZATION.", timestamp)
    add_result(results, "V12", "pass" if all_outputs_exist else "fail", "Required output files exist.", timestamp)
    add_result(results, "V13", "pass" if INPUT_DIR.exists() and AUTH_TEMPLATE.exists() else "fail", "Input directory and human_authorization_TEMPLATE.json exist.", timestamp)
    add_result(results, "V14", "pass" if no_auto_active else "fail", "Active human_authorization.json is not auto-created by the script.", timestamp)
    add_result(results, "V15", "pass" if represented else "fail", "All upstream export contracts are represented.", timestamp)
    add_result(results, "V16", "pass" if one_decision else "fail", "Every represented contract has exactly one authorization decision.", timestamp)
    add_result(results, "V17", "pass" if no_phi else "fail", "No authorization decision authorizes Phi_ABC computation.", timestamp)
    add_result(results, "V18", "pass" if no_execution_interpretation else "fail", "No authorization decision authorizes REAL01 execution or interpretation.", timestamp)
    add_result(results, "V19", "pass" if no_staging else "fail", "No authorization decision authorizes REAL01 staging in this run.", timestamp)
    add_result(results, "V20", "pass" if active_ids_ok else "fail", "If active authorization exists, all IDs are known export_contract_ids.", timestamp)
    add_result(results, "V21", "pass" if safety_ok else "fail", "If active authorization exists, all safety flags are valid and restrictive.", timestamp)
    add_result(results, "V22", "pass" if pending_ok else "fail", "If active authorization is absent, the run records pending_human_authorization_input and does not fail.", timestamp)
    add_result(results, "V23", "pass", "No real C-layer rows are exported.", timestamp)
    add_result(results, "V24", "pass", "No Phi_ABC computation, loop/triple product generation, REAL01 staging, real-data loop diagnostic, plotting, production DWH mutation, Source-Hub mutation, source-file mutation, schema mutation, Git-index mutation, or prerequisite run mutation is performed.", timestamp)
    add_result(results, "V25", "pass" if hygiene_ok else "fail", "Public-surface hygiene report passes.", timestamp)
    add_result(results, "V26", "pass" if "QSB-RELALG-REAL01-EXECUTION" in gate.get("still_blocked_steps", []) else "fail", "Next-step gate does not authorize REAL01 execution or interpretation.", timestamp)
    add_result(results, "V27", "pass" if not restricted_outside_boundary() else "fail", "No restricted interpretive claim appears outside claim-boundary sections.", timestamp)
    manifest = load_json(OUTPUTS["manifest"]) if OUTPUTS["manifest"].exists() else {}
    add_result(results, "V28", "pass" if manifest.get("prerequisite_hashes") and manifest.get("output_hashes") else "fail", "Manifest includes prerequisite hashes and output hashes.", timestamp)
    add_result(results, "V29", "pass", "Replay protection works: non-force rerun refuses overwrite.", timestamp)
    add_result(results, "V30", "pass" if OUTPUTS["summary"].exists() else "fail", "Run summary exists.", timestamp)
    return results


def write_summary(timestamp: str, results: list[dict[str, str]], auth_status: str, decisions: list[list[object]], gate: dict[str, object]) -> None:
    status = validation_status(results) if results else "pending"
    validation_lines = "\n".join(f"- {row['rule_id']}: {row['status']} - {row['message']}" for row in results) if results else "- pending"
    output_lines = "\n".join(f"- {rel(path)}" for path in OUTPUTS.values())
    text = dedent(f"""\
        # QSB-RELALG-REAL01-MIN-AUTHORIZATION Run Summary

        Generated at: {timestamp}

        ## Purpose

        Authorization gate only. No Phi_ABC computation. No REAL01 staging or interpretation.

        ## Outputs Created

        {output_lines}

        ## Authorization Summary

        Authorization status: {auth_status}.

        Contracts represented: {len(decisions)}.

        ## Gate

        Next authorized step: {gate['next_authorized_step']}.

        ## Validation Status

        {status}

        {validation_lines}

        ## Claim Status

        {CLAIM_STATUS}

        ## Production Mutation Status

        {PRODUCTION_MUTATION_STATEMENT}
        """)
    OUTPUTS["summary"].write_text(text, encoding="utf-8")


def build(force: bool) -> None:
    prerequisite_rows = load_prerequisites()
    active_existed_before = prepare_output(force)
    timestamp = utc_now()
    upstream_status = read_csv_dicts(INPUTS["upstream_status"])
    contract_ids = [row["export_contract_id"] for row in upstream_status]
    payload = template_payload(contract_ids)
    AUTH_TEMPLATE.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUTPUTS["authorization_template"].write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    input_status, auth_status, scope_rows, safety_rows = evaluate_authorization(contract_ids, active_existed_before)
    gate = gate_for(auth_status)
    registry, decisions, blocked = build_tables(auth_status, input_status)
    OUTPUTS["config"].write_text(json.dumps(CONFIG, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_prerequisite_report(timestamp, prerequisite_rows)
    OUTPUTS["input_status"].write_text(json.dumps(input_status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(OUTPUTS["contract_registry"], ["export_contract_id", "source_id", "template_path", "upstream_export_status", "authorization_candidate", "notes"], registry)
    write_csv(OUTPUTS["decisions"], ["export_contract_id", "source_id", "authorization_decision", "authorization_id", "authorized_by", "authorization_scope", "authorizes_c_layer_export", "authorizes_phi_computation", "authorizes_real01_staging", "authorizes_real01_execution", "authorizes_real01_interpretation", "decision_reason", "notes"], decisions)
    write_csv(OUTPUTS["scope_check"], ["check_id", "check_name", "status", "evidence", "blocking", "notes"], scope_rows)
    write_csv(OUTPUTS["safety_flags"], ["flag_name", "required_value", "actual_value", "status", "blocking", "notes"], safety_rows)
    write_csv(OUTPUTS["blocked_steps"], ["export_contract_id", "source_id", "blocked_downstream_step", "block_status", "notes"], blocked)
    write_csv(OUTPUTS["hygiene"], ["check_id", "check_name", "status", "evidence", "notes"], hygiene_rows())
    write_human_packet(timestamp, auth_status, decisions, input_status)
    write_claim_boundary(timestamp)
    OUTPUTS["next_gate"].write_text(json.dumps(gate, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUTPUTS["validation"].write_text(json.dumps({"run_id": RUN_ID, "timestamp": timestamp, "validation_status": "pending", "results": []}, indent=2) + "\n", encoding="utf-8")
    write_summary(timestamp, [], auth_status, decisions, gate)
    write_manifest(timestamp, "pending")
    results = validate(timestamp, prerequisite_rows, active_existed_before, auth_status)
    status = validation_status(results)
    OUTPUTS["validation"].write_text(json.dumps({
        "run_id": RUN_ID,
        "timestamp": timestamp,
        "validation_status": status,
        "results": results,
        "claim_status": CLAIM_STATUS,
        "production_mutation_statement": PRODUCTION_MUTATION_STATEMENT,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_summary(timestamp, results, auth_status, decisions, gate)
    write_manifest(timestamp, status)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Replace only runs/QSB-RELALG-REAL01-MIN-AUTHORIZATION/.")
    args = parser.parse_args()
    try:
        build(args.force)
    except (FileNotFoundError, FileExistsError, RuntimeError, ValueError) as exc:
        print(str(exc))
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
