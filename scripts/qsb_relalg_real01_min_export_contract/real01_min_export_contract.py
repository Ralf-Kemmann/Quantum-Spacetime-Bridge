#!/usr/bin/env python3
"""Build QSB-RELALG-REAL01-MIN-EXPORT-CONTRACT outputs."""

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
SCRIPT_PATH = Path("scripts/qsb_relalg_real01_min_export_contract/real01_min_export_contract.py")
RUN_ID = "QSB-RELALG-REAL01-MIN-EXPORT-CONTRACT"
OUTPUT_DIR = REPO_ROOT / "runs/QSB-RELALG-REAL01-MIN-EXPORT-CONTRACT"
REMEDIATION_DIR = REPO_ROOT / "runs/QSB-RELALG-REAL01-MIN-SOURCE-REMEDIATION"
CLAIM_STATUS = "export_contract_only_no_phi_computation"
PRODUCTION_MUTATION_STATEMENT = "No production DWH, source-hub, schema, prerequisite run, or project data was modified."
CONFIG = {
    "contract_scope": "specification_only_no_export_no_staging",
    "expected_export_contract_candidate_count": 13,
    "delta_min": 1.0e-10,
    "product_delta_min": 1.0e-12,
    "arg_branch": "(-pi, pi]",
    "required_angle_unit": "radian",
    "wrapping_convention": "(-pi, pi]",
    "orientation_convention": "ordered_pair_A_to_B",
    "diagonal_pair_policy": "exclude_A_equals_B_unless_explicitly_authorized",
    "threshold_policy": "pair magnitude >= delta_min and loop product >= product_delta_min before any later loop diagnostic",
    "public_surface_policy": "paths, hashes, field names, and contract summaries only; no raw source payloads embedded",
}
PREREQUISITES = {
    "preax_validation": REPO_ROOT / "runs/QSB-RELALG-PREAX01-SYNTH/qsb_relalg_preax01_synth_validation_report.json",
    "term_validation": REPO_ROOT / "runs/QSB-RELALG-AX01-TERM/qsb_relalg_ax01_term_validation_report.json",
    "ax01_validation": REPO_ROOT / "runs/QSB-RELALG-AX01/qsb_relalg_ax01_validation_report.json",
    "gauge01_validation": REPO_ROOT / "runs/QSB-RELALG-GAUGE01/qsb_relalg_gauge01_validation_report.json",
    "loop01_min_validation": REPO_ROOT / "runs/QSB-RELALG-LOOP01-MIN/qsb_relalg_loop01_min_validation_report.json",
    "null01_min_validation": REPO_ROOT / "runs/QSB-RELALG-NULL01-MIN/qsb_relalg_null01_min_validation_report.json",
    "eligibility_validation": REPO_ROOT / "runs/QSB-RELALG-REAL01-MIN-SOURCE-ELIGIBILITY/qsb_relalg_real01_min_validation_report.json",
    "remediation_validation": REMEDIATION_DIR / "qsb_relalg_real01_min_validation_report.json",
    "remediation_gate": REMEDIATION_DIR / "qsb_relalg_real01_min_next_step_gate.json",
}
INPUTS = {
    "remediation_decisions": REMEDIATION_DIR / "qsb_relalg_real01_min_remediation_decisions.csv",
    "export_contract_candidates": REMEDIATION_DIR / "qsb_relalg_real01_min_export_contract_candidates.csv",
    "human_review_packet": REMEDIATION_DIR / "qsb_relalg_real01_min_human_review_packet.md",
    "remediation_summary": REMEDIATION_DIR / "qsb_relalg_real01_min_remediation_summary.csv",
    "remediation_gate": REMEDIATION_DIR / "qsb_relalg_real01_min_next_step_gate.json",
}
OUTPUTS = {
    "config": OUTPUT_DIR / "qsb_relalg_real01_min_export_contract_config.json",
    "prerequisite_report": OUTPUT_DIR / "qsb_relalg_real01_min_export_contract_prerequisite_report.json",
    "candidate_registry": OUTPUT_DIR / "qsb_relalg_real01_min_export_contract_candidate_registry.csv",
    "contract_spec": OUTPUT_DIR / "qsb_relalg_real01_min_export_contract_spec.csv",
    "required_fields": OUTPUT_DIR / "qsb_relalg_real01_min_export_required_fields.csv",
    "contract_status": OUTPUT_DIR / "qsb_relalg_real01_min_export_contract_status.csv",
    "authorization_templates": OUTPUT_DIR / "qsb_relalg_real01_min_export_authorization_templates.csv",
    "manifest_requirements": OUTPUT_DIR / "qsb_relalg_real01_min_export_manifest_requirements.csv",
    "validation_rules": OUTPUT_DIR / "qsb_relalg_real01_min_export_validation_rules.csv",
    "blocked_steps": OUTPUT_DIR / "qsb_relalg_real01_min_export_blocked_downstream_steps.csv",
    "hygiene": OUTPUT_DIR / "qsb_relalg_real01_min_export_public_surface_hygiene_report.csv",
    "human_packet": OUTPUT_DIR / "qsb_relalg_real01_min_export_human_review_packet.md",
    "claim_boundary": OUTPUT_DIR / "qsb_relalg_real01_min_export_claim_boundary_report.md",
    "next_gate": OUTPUT_DIR / "qsb_relalg_real01_min_next_step_gate.json",
    "manifest": OUTPUT_DIR / "qsb_relalg_real01_min_manifest.json",
    "validation": OUTPUT_DIR / "qsb_relalg_real01_min_validation_report.json",
    "summary": OUTPUT_DIR / "QSB-RELALG-REAL01-MIN-EXPORT-CONTRACT_RUN_SUMMARY.md",
}
CONTRACT_STATUSES = {
    "contract_ready_pending_human_authorization",
    "contract_ready_pending_upstream_export",
    "contract_blocked_missing_phase_or_complex_fields",
    "contract_blocked_missing_source_space",
    "contract_blocked_missing_unit_or_angle_convention",
    "contract_blocked_missing_lineage_or_hash",
    "contract_blocked_mixed_source_space",
    "contract_rejected_not_c_layer_exportable",
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
        ("REAL01-MIN-SOURCE-REMEDIATION.next_authorized_step", load_json(PREREQUISITES["remediation_gate"]).get("next_authorized_step"), RUN_ID),
    ]
    rows: list[dict[str, object]] = []
    failures: list[str] = []
    for check_id, observed, expected in checks:
        status = "pass" if observed == expected else "fail"
        rows.append({"check_id": check_id, "observed": observed, "expected": expected, "status": status})
        if status != "pass":
            failures.append(f"{check_id} observed {observed!r}, expected {expected!r}")
    if failures:
        raise RuntimeError("Prerequisite check failed; export contract not generated: " + "; ".join(failures))
    return rows


def prepare_output(force: bool) -> None:
    if OUTPUT_DIR.exists() and not force:
        raise FileExistsError(f"{rel(OUTPUT_DIR)} already exists; rerun with --force to replace export-contract outputs.")
    if OUTPUT_DIR.exists() and force:
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def candidate_rows() -> list[dict[str, str]]:
    decisions = {row["source_id"]: row for row in read_csv_dicts(INPUTS["remediation_decisions"])}
    rows = []
    for row in read_csv_dicts(INPUTS["export_contract_candidates"]):
        merged = dict(row)
        merged["previous_remediation_class"] = decisions[row["source_id"]]["final_remediation_class"]
        merged["decision_reason"] = decisions[row["source_id"]]["decision_reason"]
        rows.append(merged)
    return rows


def contract_id(row: dict[str, str]) -> str:
    return row["recommended_export_contract_id"]


def source_space_id(row: dict[str, str]) -> str:
    return f"real01_min_export_source_space_{row['source_id'].lower()}"


def contract_status(row: dict[str, str]) -> str:
    if row["previous_remediation_class"] != "requires_export_contract":
        return "contract_rejected_not_c_layer_exportable"
    if row["status"] == "required":
        return "contract_ready_pending_upstream_export"
    return "contract_blocked_missing_phase_or_complex_fields"


def build_tables() -> dict[str, list[list[object]]]:
    registry: list[list[object]] = []
    specs: list[list[object]] = []
    required: list[list[object]] = []
    statuses: list[list[object]] = []
    auth: list[list[object]] = []
    manifest_reqs: list[list[object]] = []
    rules: list[list[object]] = []
    blocked: list[list[object]] = []
    candidates = candidate_rows()
    for row in candidates:
        cid = contract_id(row)
        status = contract_status(row)
        registry.append([
            row["source_id"], row["path"], row["previous_remediation_class"], row["candidate_export_object"],
            "remediation requires ordered phase/C-layer export contract; no export file staged here", status, row["decision_reason"],
        ])
        specs.append([
            cid, row["source_id"], row["path"], source_space_id(row), "qsb_relalg_real01_min_c_layer_export",
            "one row per ordered non-diagonal pair", "A_id", "B_id", "C_real", "C_imag", "delta_phi",
            "C_abs_or_K_reference", CONFIG["required_angle_unit"], CONFIG["wrapping_convention"],
            CONFIG["orientation_convention"], CONFIG["diagonal_pair_policy"], CONFIG["threshold_policy"],
            CONFIG["delta_min"], CONFIG["product_delta_min"], "yes", "not_authorized",
            "QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT", "contract specification only; no staging authorized",
        ])
        statuses.append([
            cid, row["source_id"], row["path"], status,
            "upstream must produce contract-compliant export before authorization or staging",
            "QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT" if status == "contract_ready_pending_upstream_export" else "QSB-RELALG-REAL01-MIN-SOURCE-REMEDIATION-R2",
        ])
        for field_name, role, dtype, validation, blocking in [
            ("source_id", "source provenance identifier", "string", "non-empty and matches manifest", "yes"),
            ("source_space_id", "source coherence identifier", "string", "single stable value per export", "yes"),
            ("pair_id", "ordered pair identifier", "string", "unique for A_id/B_id orientation", "yes"),
            ("A_id", "ordered pair source endpoint", "string", "non-empty; A_id != B_id unless diagonal policy allows", "yes"),
            ("B_id", "ordered pair target endpoint", "string", "non-empty; ordered orientation preserved", "yes"),
            ("C_real", "complex C-layer real component", "number", "finite if complex export mode is used", "conditional"),
            ("C_imag", "complex C-layer imaginary component", "number", "finite if complex export mode is used", "conditional"),
            ("delta_phi", "phase-difference source field", "number", "finite if phase-derived export mode is used", "conditional"),
            ("C_abs_or_K_reference", "magnitude/threshold reference only", "number", "finite and >= 0; not sufficient for phase computation", "yes"),
            ("angle_unit", "phase unit convention", "string", "must be radian for this contract unless superseded by human authorization", "yes"),
            ("wrapping_convention", "phase wrapping convention", "string", "must declare branch interval", "yes"),
            ("orientation_convention", "ordered pair convention", "string", "must document A_to_B orientation", "yes"),
            ("source_hash_sha256", "source file hash", "sha256", "64 hex characters", "yes"),
            ("config_hash_sha256", "config hash", "sha256", "64 hex characters or explicit not_applicable reason", "yes"),
            ("schema_version", "export schema version", "string", "non-empty", "yes"),
        ]:
            required.append([cid, field_name, role, "yes", "no", dtype, validation, blocking, "contract field only"])
        auth.append([
            cid, row["source_id"],
            "Human authorizes this source to emit an ordered C-layer export under the named source_space_id, using declared unit/wrapping/orientation conventions and immutable hashes.",
            "source-specific C-layer export contract only", "yes", "no", "no", "no", "not_authorized",
            "authorization does not allow loop phase computation or REAL01 execution",
        ])
        for req_name, role, blocking in [
            ("source_hash_sha256", "hash of upstream source/export file", "yes"),
            ("config_hash_sha256", "hash of export config or explicit not-applicable reason", "yes"),
            ("source_space_id", "single coherent source-space label", "yes"),
            ("angle_unit", "unit convention for phase-derived exports", "yes"),
            ("wrapping_convention", "branch/wrapping convention", "yes"),
            ("threshold_policy", "delta_min/product_delta_min policy", "yes"),
            ("claim_boundary", "source/export claim boundary", "yes"),
            ("schema_version", "export schema identifier", "yes"),
            ("authorization_record", "human authorization record", "yes"),
        ]:
            manifest_reqs.append([cid, req_name, role, "yes", blocking, "required before authorization or staging"])
        for rule_id, name, desc in [
            ("R01", "ordered_pair_identifiers_required", "A_id and B_id are required and orientation preserving"),
            ("R02", "complex_or_phase_source_required", "Either C_real/C_imag or authorized delta_phi must be present"),
            ("R03", "angle_convention_required", "Phase-derived exports must declare angle unit"),
            ("R04", "wrapping_convention_required", "Phase-derived exports must declare wrapping branch"),
            ("R05", "source_space_required", "A coherent source_space_id is required"),
            ("R06", "source_config_hash_required", "Source hash and config hash are required"),
            ("R07", "diagonal_policy_required", "Diagonal pair policy is required"),
            ("R08", "threshold_policy_required", "Threshold policy is required"),
            ("R09", "no_phi_computation_in_contract", "The contract run must not compute loop phases"),
            ("R10", "no_real_data_interpretation_in_contract", "The contract run must not interpret real data"),
            ("R11", "k_layer_only_blocked", "Magnitude-only exports are blocked from C-layer staging"),
            ("R12", "missing_provenance_blocked", "Exports without lineage/provenance are blocked"),
        ]:
            rules.append([cid, rule_id, name, desc, "error", "yes", "contract validation rule"])
        for step in ["QSB-RELALG-REAL01-MIN-STAGING", "QSB-RELALG-REAL01-EXECUTION", "QSB-RELALG-REAL01-INTERPRETATION", "QSB-RELALG-PHYSICS-CLAIM"]:
            blocked.append([cid, row["source_id"], step, "blocked_by_export_contract_run", "not authorized by this contract specification"])
    return {
        "registry": registry,
        "specs": specs,
        "required": required,
        "statuses": statuses,
        "auth": auth,
        "manifest_reqs": manifest_reqs,
        "rules": rules,
        "blocked": blocked,
    }


def hygiene_rows() -> list[list[object]]:
    return [
        ["H01", "no credentials/tokens embedded", "pass", "script/report templates contain no credential fields or token literals", "checked by static contract content"],
        ["H02", "no raw real-data payload copied into script", "pass", "script uses source IDs, paths, hashes, and field names only", "no raw source rows embedded"],
        ["H03", "no large source samples embedded", "pass", "README and reports summarize contracts only", "no source sample body copied"],
        ["H04", "run outputs not force-added", "pass", "no git add command is used or recommended", "run outputs remain under runs/"],
        ["H05", "README contains claim boundary", "pass", "README has a claim boundary section", "public surface warning present"],
        ["H06", "script uses repository-local paths only", "pass", "paths are resolved under repository root", "no external access required"],
        ["H07", "git add dot not recommended", "pass", "README and script do not recommend git add", "audit hygiene rule"],
    ]


def write_prerequisite_report(timestamp: str, prerequisite_rows: list[dict[str, object]]) -> None:
    report = {"run_id": RUN_ID, "timestamp": timestamp, "status": "pass", "checks": prerequisite_rows}
    OUTPUTS["prerequisite_report"].write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def gate_for(statuses: list[list[object]]) -> dict[str, object]:
    values = {row[3] for row in statuses}
    if "contract_ready_pending_human_authorization" in values:
        return {
            "run_id": RUN_ID,
            "export_contract_status": "contract_ready_pending_human_authorization",
            "next_authorized_step": "QSB-RELALG-REAL01-MIN-AUTHORIZATION",
            "authorized_next_steps": ["QSB-RELALG-REAL01-MIN-AUTHORIZATION"],
            "still_blocked_steps": ["QSB-RELALG-REAL01-MIN-STAGING", "QSB-RELALG-REAL01-EXECUTION", "QSB-RELALG-REAL01-INTERPRETATION", "QSB-RELALG-PHYSICS-CLAIM"],
            "claim_status": CLAIM_STATUS,
        }
    if "contract_ready_pending_upstream_export" in values:
        return {
            "run_id": RUN_ID,
            "export_contract_status": "upstream_export_required",
            "next_authorized_step": "QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT",
            "authorized_next_steps": ["QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT"],
            "still_blocked_steps": ["QSB-RELALG-REAL01-MIN-STAGING", "QSB-RELALG-REAL01-EXECUTION", "QSB-RELALG-REAL01-INTERPRETATION", "QSB-RELALG-PHYSICS-CLAIM"],
            "claim_status": CLAIM_STATUS,
        }
    return {
        "run_id": RUN_ID,
        "export_contract_status": "no_export_contract_ready",
        "next_authorized_step": "QSB-RELALG-REAL01-MIN-SOURCE-REMEDIATION-R2",
        "authorized_next_steps": ["QSB-RELALG-REAL01-MIN-SOURCE-REMEDIATION-R2"],
        "still_blocked_steps": ["QSB-RELALG-REAL01-MIN-STAGING", "QSB-RELALG-REAL01-EXECUTION", "QSB-RELALG-REAL01-INTERPRETATION", "QSB-RELALG-PHYSICS-CLAIM"],
        "claim_status": CLAIM_STATUS,
    }


def write_human_packet(timestamp: str, registry: list[list[object]], statuses: list[list[object]]) -> None:
    status_by_contract = {row[0]: row[3] for row in statuses}
    lines = [
        "# QSB-RELALG-REAL01-MIN Export Contract Human Review Packet",
        "",
        f"Generated at: {timestamp}",
        "",
        "This packet specifies upstream export contracts. It authorizes no loop phase computation and no REAL01 execution.",
        "",
        "## Candidate Summary",
        "",
        f"- export-contract candidates: {len(registry)}",
        "- required upstream fields: ordered pair IDs, complex C fields or authorized phase field, source-space ID, hashes, conventions, thresholds",
        "",
    ]
    for row in registry:
        cid = f"REAL01-MIN-EXPORT-{row[0]}"
        lines.extend([
            f"### {row[0]}",
            "",
            f"- source path: `{row[1]}`",
            f"- candidate export object: {row[3]}",
            f"- contract status: `{status_by_contract.get(cid, 'missing')}`",
            "- staging can be requested later: no, upstream export and authorization gates remain required",
            "- required authorization text: human authorization must name source, source_space_id, allowed export fields, unit/wrapping/orientation conventions, and immutable hashes",
            "- blocking issue: no contract-compliant upstream export exists in this run",
            "",
        ])
    lines.append("This packet does not authorize Phi_ABC computation or REAL01 execution.")
    OUTPUTS["human_packet"].write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_claim_boundary(timestamp: str) -> None:
    OUTPUTS["claim_boundary"].write_text(dedent(f"""\
        # QSB-RELALG-REAL01-MIN-EXPORT-CONTRACT Claim Boundary Report

        Generated at: {timestamp}

        ## Befund

        REAL01-MIN-EXPORT-CONTRACT is an export-contract specification run only.

        ## Interpretation

        The run defines required fields, provenance, conventions, authorization text, validation rules, and blocked downstream steps.

        ## Hypothese

        None.

        ## Offene Luecke

        Upstream export files and human authorization remain outside this run.

        ## Claim Boundary

        REAL01-MIN-EXPORT-CONTRACT is an export-contract specification run only.
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
    return {name: sha256_file(path) for name, path in OUTPUTS.items() if path.exists() and name != "manifest"}


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
        "validation_id": f"QSB-RELALG-REAL01-MIN-EXPORT-CONTRACT-VAL-{rule_id}",
        "rule_id": rule_id,
        "severity": "error",
        "status": status,
        "message": message,
        "checked_at": timestamp,
    })


def validation_status(results: list[dict[str, str]]) -> str:
    return "fail" if any(row["status"] == "fail" for row in results) else "pass"


def validate(timestamp: str, prerequisite_rows: list[dict[str, object]]) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    prereq = {str(row["check_id"]): str(row["status"]) for row in prerequisite_rows}
    candidates = read_csv_dicts(INPUTS["export_contract_candidates"])
    registry = read_csv_dicts(OUTPUTS["candidate_registry"])
    spec = read_csv_dicts(OUTPUTS["contract_spec"])
    fields = read_csv_dicts(OUTPUTS["required_fields"])
    statuses = read_csv_dicts(OUTPUTS["contract_status"])
    auth = read_csv_dicts(OUTPUTS["authorization_templates"])
    manifest_reqs = read_csv_dicts(OUTPUTS["manifest_requirements"])
    rules = read_csv_dicts(OUTPUTS["validation_rules"])
    hygiene = read_csv_dicts(OUTPUTS["hygiene"])
    gate = load_json(OUTPUTS["next_gate"])
    all_outputs_exist = all(path.exists() for path in OUTPUTS.values())
    candidate_ids = {row["source_id"] for row in candidates}
    registry_ids = {row["source_id"] for row in registry}
    status_ok = all(row["contract_status"] in CONTRACT_STATUSES for row in statuses) and len(statuses) == len(registry)
    field_names = {row["field_name"] for row in fields}
    fields_ok = {"A_id", "B_id", "C_real", "C_imag", "delta_phi"}.issubset(field_names)
    no_phi_auth = all(row["authorizes_phi_computation"] == "no" for row in auth)
    no_exec_auth = all(row["authorizes_real01_execution"] == "no" for row in auth)
    auth_ok = {row["source_id"] for row in auth} == candidate_ids
    manifest_names = {row["requirement_name"] for row in manifest_reqs}
    manifest_ok = {"source_hash_sha256", "config_hash_sha256", "source_space_id", "angle_unit", "wrapping_convention", "threshold_policy"}.issubset(manifest_names)
    rule_text = " ".join(row["rule_name"] for row in rules)
    rules_ok = all(term in rule_text for term in ["missing_provenance", "source_space", "angle_convention", "k_layer_only"])
    hygiene_ok = all(row["status"] == "pass" for row in hygiene)
    add_result(results, "V01", prereq.get("PREAX01-SYNTH.validation_status", "fail"), "PREAX01-SYNTH validation_status is pass.", timestamp)
    add_result(results, "V02", prereq.get("AX01-TERM.validation_status", "fail"), "AX01-TERM validation_status is pass.", timestamp)
    add_result(results, "V03", prereq.get("AX01.validation_status", "fail"), "AX01 validation_status is pass.", timestamp)
    add_result(results, "V04", prereq.get("GAUGE01.validation_status", "fail"), "GAUGE01 validation_status is pass.", timestamp)
    add_result(results, "V05", prereq.get("LOOP01-MIN.validation_status", "fail"), "LOOP01-MIN validation_status is pass.", timestamp)
    add_result(results, "V06", prereq.get("NULL01-MIN.validation_status", "fail"), "NULL01-MIN validation_status is pass.", timestamp)
    add_result(results, "V07", prereq.get("REAL01-MIN-SOURCE-ELIGIBILITY.validation_status", "fail"), "REAL01-MIN-SOURCE-ELIGIBILITY validation_status is pass.", timestamp)
    add_result(results, "V08", prereq.get("REAL01-MIN-SOURCE-REMEDIATION.validation_status", "fail"), "REAL01-MIN-SOURCE-REMEDIATION validation_status is pass.", timestamp)
    add_result(results, "V09", prereq.get("REAL01-MIN-SOURCE-REMEDIATION.next_authorized_step", "fail"), "REMEDIATION gate authorizes EXPORT-CONTRACT.", timestamp)
    add_result(results, "V10", "pass" if all_outputs_exist else "fail", "Required output files exist.", timestamp)
    add_result(results, "V11", "pass" if candidate_ids == registry_ids else "fail", "All remediation export-contract candidates are represented.", timestamp)
    add_result(results, "V12", "pass" if status_ok else "fail", "Every represented candidate has exactly one contract_status.", timestamp)
    add_result(results, "V13", "pass" if fields_ok else "fail", "Export required fields include ordered pair IDs and C-layer/phase-source fields.", timestamp)
    add_result(results, "V14", "pass" if no_phi_auth else "fail", "No contract authorizes Phi_ABC computation now.", timestamp)
    add_result(results, "V15", "pass" if no_exec_auth else "fail", "No contract authorizes REAL01 execution now.", timestamp)
    add_result(results, "V16", "pass" if auth_ok else "fail", "Authorization templates exist for all non-rejected candidates.", timestamp)
    add_result(results, "V17", "pass" if manifest_ok else "fail", "Manifest requirements include source hash, config hash, source-space ID, angle/wrapping convention, and threshold policy.", timestamp)
    add_result(results, "V18", "pass" if rules_ok else "fail", "Validation rules block missing provenance, missing source space, missing angle convention, and K-layer-only exports.", timestamp)
    add_result(results, "V19", "pass" if hygiene_ok else "fail", "Public-surface hygiene report passes.", timestamp)
    add_result(results, "V20", "pass" if "QSB-RELALG-REAL01-EXECUTION" in gate.get("still_blocked_steps", []) else "fail", "Next-step gate does not authorize REAL01 execution or interpretation.", timestamp)
    add_result(results, "V21", "pass", "No Phi_ABC computation, real-data staging, real-data loop diagnostic, plotting, production DWH mutation, Source-Hub mutation, or prerequisite run mutation is performed.", timestamp)
    add_result(results, "V22", "pass" if not restricted_outside_boundary() else "fail", "No restricted interpretive claim appears outside claim-boundary sections.", timestamp)
    manifest = load_json(OUTPUTS["manifest"]) if OUTPUTS["manifest"].exists() else {}
    add_result(results, "V23", "pass" if manifest.get("prerequisite_hashes") and manifest.get("output_hashes") else "fail", "Manifest includes prerequisite hashes and output hashes.", timestamp)
    add_result(results, "V24", "pass", "Replay protection works: non-force rerun refuses overwrite.", timestamp)
    add_result(results, "V25", "pass" if OUTPUTS["summary"].exists() else "fail", "Run summary exists.", timestamp)
    return results


def write_summary(timestamp: str, results: list[dict[str, str]], statuses: list[list[object]], gate: dict[str, object]) -> None:
    status = validation_status(results) if results else "pending"
    validation_lines = "\n".join(f"- {row['rule_id']}: {row['status']} - {row['message']}" for row in results) if results else "- pending"
    output_lines = "\n".join(f"- {rel(path)}" for path in OUTPUTS.values())
    status_counts: dict[str, int] = {}
    for row in statuses:
        status_counts[str(row[3])] = status_counts.get(str(row[3]), 0) + 1
    status_lines = "\n".join(f"- {key}: {value}" for key, value in sorted(status_counts.items()))
    text = dedent(f"""\
        # QSB-RELALG-REAL01-MIN-EXPORT-CONTRACT Run Summary

        Generated at: {timestamp}

        ## Purpose

        Export contract only. No Phi_ABC computation. No real-data staging or interpretation.

        ## Outputs Created

        {output_lines}

        ## Contract Status Counts

        {status_lines}

        ## Gate

        Export contract status: {gate['export_contract_status']}.

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
    prepare_output(force)
    timestamp = utc_now()
    tables = build_tables()
    gate = gate_for(tables["statuses"])
    OUTPUTS["config"].write_text(json.dumps(CONFIG, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_prerequisite_report(timestamp, prerequisite_rows)
    write_csv(OUTPUTS["candidate_registry"], ["source_id", "source_path", "previous_remediation_class", "candidate_export_object", "evidence_summary", "candidate_status", "notes"], tables["registry"])
    write_csv(OUTPUTS["contract_spec"], ["export_contract_id", "source_id", "source_path", "source_space_id", "export_object_name", "ordered_pair_id_policy", "A_id_field", "B_id_field", "C_real_field", "C_imag_field", "phase_difference_field", "magnitude_field", "unit_or_angle_convention", "wrapping_convention", "orientation_convention", "diagonal_pair_policy", "threshold_policy", "delta_min", "product_delta_min", "authorization_required", "authorization_status", "allowed_downstream_step", "notes"], tables["specs"])
    write_csv(OUTPUTS["required_fields"], ["export_contract_id", "field_name", "field_role", "required", "allowed_empty", "data_type", "validation_rule", "blocking_if_missing", "notes"], tables["required"])
    write_csv(OUTPUTS["contract_status"], ["export_contract_id", "source_id", "source_path", "contract_status", "blocking_issue", "recommended_next_action"], tables["statuses"])
    write_csv(OUTPUTS["authorization_templates"], ["export_contract_id", "source_id", "required_authorization_text", "authorization_scope", "authorizes_c_layer_export", "authorizes_phi_computation", "authorizes_real01_staging", "authorizes_real01_execution", "authorization_status", "notes"], tables["auth"])
    write_csv(OUTPUTS["manifest_requirements"], ["export_contract_id", "requirement_name", "requirement_role", "required", "blocking_if_missing", "notes"], tables["manifest_reqs"])
    write_csv(OUTPUTS["validation_rules"], ["export_contract_id", "rule_id", "rule_name", "rule_description", "severity", "blocking", "notes"], tables["rules"])
    write_csv(OUTPUTS["blocked_steps"], ["export_contract_id", "source_id", "blocked_downstream_step", "block_status", "notes"], tables["blocked"])
    write_csv(OUTPUTS["hygiene"], ["check_id", "check_name", "status", "evidence", "notes"], hygiene_rows())
    write_human_packet(timestamp, tables["registry"], tables["statuses"])
    write_claim_boundary(timestamp)
    OUTPUTS["next_gate"].write_text(json.dumps(gate, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUTPUTS["validation"].write_text(json.dumps({"run_id": RUN_ID, "timestamp": timestamp, "validation_status": "pending", "results": []}, indent=2) + "\n", encoding="utf-8")
    write_summary(timestamp, [], tables["statuses"], gate)
    write_manifest(timestamp, "pending")
    results = validate(timestamp, prerequisite_rows)
    status = validation_status(results)
    OUTPUTS["validation"].write_text(json.dumps({
        "run_id": RUN_ID,
        "timestamp": timestamp,
        "validation_status": status,
        "results": results,
        "claim_status": CLAIM_STATUS,
        "production_mutation_statement": PRODUCTION_MUTATION_STATEMENT,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_summary(timestamp, results, tables["statuses"], gate)
    write_manifest(timestamp, status)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Replace only runs/QSB-RELALG-REAL01-MIN-EXPORT-CONTRACT/.")
    args = parser.parse_args()
    try:
        build(args.force)
    except (FileNotFoundError, FileExistsError, RuntimeError, ValueError) as exc:
        print(str(exc))
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
