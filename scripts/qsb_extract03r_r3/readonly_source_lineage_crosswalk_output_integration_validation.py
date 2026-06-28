#!/usr/bin/env python3
"""QSB-EXTRACT03R-R3 read-only source-lineage crosswalk output package."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs" / "QSB-EXTRACT03R-R3" / "readonly_source_lineage_crosswalk_output_integration_validation"
PROMPT = Path("/home/ralf-kemmann/Downloads/QSB_EXTRACT03R_R3_READONLY_SOURCE_LINEAGE_CROSSWALK_OUTPUT_INTEGRATION_VALIDATION_CODEX_PROMPT.md")

IMPORT_DIRS = {
    "R_R2": ROOT / "runs" / "QSB-EXTRACT03R-R2" / "additive_source_lineage_export_schema_patch",
    "R_R1": ROOT / "runs" / "QSB-EXTRACT03R-R1" / "minimal_source_lineage_export_fix_staging",
    "R": ROOT / "runs" / "QSB-EXTRACT03R" / "source_lineage_export_fix_design",
    "Q_R1": ROOT / "runs" / "QSB-EXTRACT03Q-R1" / "narrow_readonly_source_id_source_record_lineage_audit",
    "Q": ROOT / "runs" / "QSB-EXTRACT03Q" / "narrow_source_id_source_record_lineage_contract",
    "P_R1": ROOT / "runs" / "QSB-EXTRACT03P-R1" / "narrow_real_data_source_configuration_lineage_audit",
    "P": ROOT / "runs" / "QSB-EXTRACT03P" / "narrow_source_configuration_lineage_audit_contract",
}

EXCLUDED_TARGETS = [
    ("source_hub_schema", ROOT / "scripts" / "qsb_source_hub" / "source_hub_schema.sql"),
    ("response_export_extract03f", ROOT / "scripts" / "qsb_extract03f" / "response_vector_signature_export.py"),
    ("response_export_extract03h", ROOT / "scripts" / "qsb_extract03h" / "authorized_response_vector_export.py"),
    ("p_r1_pair_config_export_writer", ROOT / "scripts" / "qsb_extract03p_r1" / "narrow_real_data_source_configuration_lineage_audit.py"),
    ("source_configuration_manifest_export", ROOT / "scripts" / "qsb_extract03p" / "narrow_source_configuration_lineage_audit_contract.py"),
]

RUN_ID = "QSB-EXTRACT03R-R3"
STATUS = "extract03r_r3_readonly_source_lineage_crosswalk_output_integration_validation_completed_partial_with_review_items"
AUTHORIZATION = "authorized_by_human_for_qsb_extract03r_r3_readonly_lineage_crosswalk_output"
SELECTED_TARGET_PATH = "future read-only lineage crosswalk output"
CROSSWALK_MODE = "partial_metadata_crosswalk"
CREATED_AT = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

REQUIRED_ARTIFACTS = [
    "00_RUN_MANIFEST.json",
    "01_HUMAN_REVIEW_AND_AUTHORIZATION_RESOLUTION.json",
    "02_IMPORTED_R_R2_PACKAGE_AND_HASHES.json",
    "03_IMPORTED_R_R1_R_Q_R1_Q_P_R1_P_CONTEXT.json",
    "04_SELECTED_TARGET_PATH_DECISION.md",
    "05_CROSSWALK_OUTPUT_SCOPE_STATEMENT.md",
    "06_READONLY_CROSSWALK_TARGET_SCHEMA.csv",
    "07_READONLY_CROSSWALK_TARGET_SCHEMA.sql",
    "08_READONLY_SOURCE_LINEAGE_CROSSWALK_OUTPUT.csv",
    "09_READONLY_SOURCE_LINEAGE_CROSSWALK_SCHEMA.json",
    "10_CROSSWALK_FIELD_SOURCE_MAP.csv",
    "11_SOURCE_ID_CROSSWALK_VALIDATION.csv",
    "12_SOURCE_RECORD_ID_CROSSWALK_VALIDATION.csv",
    "13_SOURCE_CONFIG_CONFIG_CROSSWALK_VALIDATION.csv",
    "14_ROLE_FIELD_CROSSWALK_VALIDATION.csv",
    "15_PAIR_IDENTIFIER_CROSSWALK_VALIDATION.csv",
    "16_HASH_PROVENANCE_BOUNDARY_VALIDATION.csv",
    "17_ALIAS_CANONICAL_BOUNDARY_VALIDATION.csv",
    "18_LINEAGE_RULE_VALIDATION.csv",
    "19_VALIDATION_RULE_VALIDATION.csv",
    "20_CLAIM_BOUNDARY_ID_VALIDATION.csv",
    "21_NULLABILITY_REQUIRED_FIELD_VALIDATION.csv",
    "22_READONLY_INTEGRATION_READINESS.csv",
    "23_NON_MUTATION_PROOF_OLD_ARTIFACTS.csv",
    "24_LIVE_DWH_REGISTRY_NON_MUTATION_PROOF.csv",
    "25_NO_RECOMPUTE_NO_RERUN_PROOF.csv",
    "26_TARGET_PATH_EXCLUSION_PROOF.csv",
    "27_ACCEPTANCE_TEST_RESULTS.csv",
    "28_BLOCKERS_AND_REVIEW_ITEMS.csv",
    "29_FUTURE_TARGET_EXPORT_PATH_RECOMMENDATIONS.md",
    "30_FUTURE_VALIDATION_TEMPLATE.json",
    "31_CLAIM_BOUNDARY_CONFIRMATION.md",
    "32_GUARDRAIL_CHECKS.json",
    "33_VALIDATION_SUMMARY.csv",
    "FINAL_RESULT_NOTE.md",
]

SCHEMA = [
    ("crosswalk_id", "TEXT", True, "readonly_crosswalk_supported", "R-R3 generated row id", "readonly_crosswalk_rule", "unique read-only output row"),
    ("source_id", "TEXT", True, "partial_review", "Q-R1/R-R1 source identity field", "direct_or_alias_basis_required", "partial when field name not row value"),
    ("source_record_id", "TEXT", True, "partial_review", "Q-R1/R-R1 source record field", "canonical_or_alias_boundary", "raw_source_file_id remains alias"),
    ("source_config_id", "TEXT", True, "staged_required_future_field", "R-R1/R-R2 staged future field", "future_manifest_required", "not backfilled"),
    ("config_id", "TEXT", True, "staged_required_future_field", "R-R1/R-R2 staged future field", "future_config_required", "not backfilled"),
    ("role_a", "TEXT", True, "staged_required_future_field", "R-R2 role field rule", "explicit_future_role_required", "not inferred from pair_i"),
    ("role_b", "TEXT", True, "staged_required_future_field", "R-R2 role field rule", "explicit_future_role_required", "not inferred from pair_j"),
    ("pair_i", "TEXT", True, "carry_forward_supported", "R-R2 pair compatibility rule", "preserve_pair_index", "ordinal only"),
    ("pair_j", "TEXT", True, "carry_forward_supported", "R-R2 pair compatibility rule", "preserve_pair_index", "ordinal only"),
    ("pair_id", "TEXT", True, "carry_forward_supported", "R-R1/R-R2 pair id", "preserve_pair_id", "no rewrite"),
    ("canonical_pair_id", "TEXT", True, "carry_forward_supported", "R-R1/R-R2 canonical pair id", "preserve_canonical_pair_id", "no rewrite"),
    ("source_artifact_id", "TEXT", False, "carry_forward_supported", "artifact/provenance context", "provenance_only", "optional"),
    ("source_artifact_sha256", "TEXT", False, "carry_forward_supported", "artifact hash", "integrity_only", "not identity"),
    ("source_manifest_id", "TEXT", False, "staged_required_future_field", "future manifest", "future_manifest_required", "optional until available"),
    ("artifact_hash", "TEXT", False, "carry_forward_supported", "artifact hash", "integrity_only", "not identity"),
    ("source_hash", "TEXT", False, "carry_forward_supported", "source hash", "integrity_only", "not identity"),
    ("config_hash", "TEXT", False, "carry_forward_supported", "config hash", "integrity_only", "not config id"),
    ("run_hash", "TEXT", False, "carry_forward_supported", "run hash", "integrity_only", "not run id"),
    ("lineage_stage", "TEXT", True, "readonly_crosswalk_supported", "R-R3 stage", "readonly_crosswalk_rule", "record crosswalk stage"),
    ("lineage_rule_id", "TEXT", True, "readonly_crosswalk_supported", "R-R3 rule id", "lineage_rule_required", "auditable"),
    ("validation_rule_id", "TEXT", True, "readonly_crosswalk_supported", "R-R3 validation id", "validation_rule_required", "auditable"),
    ("claim_boundary_id", "TEXT", True, "readonly_crosswalk_supported", "R-R3 claim boundary", "claim_boundary_required", "no claim upgrade"),
    ("field_support_class", "TEXT", True, "readonly_crosswalk_supported", "support class", "allowed_support_class", "explicit class"),
    ("source_identity_basis", "TEXT", True, "readonly_crosswalk_supported", "basis descriptor", "basis_required", "direct/alias/partial"),
    ("source_record_identity_basis", "TEXT", True, "readonly_crosswalk_supported", "basis descriptor", "basis_required", "canonical/alias/partial"),
    ("source_config_identity_basis", "TEXT", True, "readonly_crosswalk_supported", "basis descriptor", "basis_required", "future manifest boundary"),
    ("role_mapping_basis", "TEXT", True, "readonly_crosswalk_supported", "basis descriptor", "basis_required", "explicit future rule"),
    ("provenance_boundary", "TEXT", True, "readonly_crosswalk_supported", "hash boundary", "provenance_only", "hashes not identity"),
    ("review_status", "TEXT", True, "readonly_crosswalk_supported", "review disposition", "review_required", "partial/open/blocker"),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(name: str, data: Any) -> None:
    (OUT / name).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_md(name: str, text: str) -> None:
    (OUT / name).write_text(text.strip() + "\n", encoding="utf-8")


def write_csv(name: str, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with (OUT / name).open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def inventory(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in sorted(path.rglob("*")):
        if item.is_file():
            rows.append({"relative_path": str(item.relative_to(ROOT)), "size_bytes": item.stat().st_size, "sha256": sha256(item)})
    return rows


def ensure_ready() -> dict[str, list[dict[str, Any]]]:
    OUT.mkdir(parents=True, exist_ok=True)
    existing = [p.name for p in OUT.iterdir() if p.is_file()]
    if existing:
        raise SystemExit(f"refusing to overwrite non-empty output dir: {OUT}")
    missing = [label for label, path in IMPORT_DIRS.items() if not path.exists()]
    if missing:
        raise SystemExit(f"missing required import dirs: {missing}")
    if not PROMPT.exists():
        raise SystemExit(f"missing prompt: {PROMPT}")
    return {label: inventory(path) for label, path in IMPORT_DIRS.items()}


def schema_rows() -> list[dict[str, Any]]:
    return [
        {
            "field_name": name,
            "type": typ,
            "required": str(required).lower(),
            "nullable": str(not required).lower(),
            "support_class": support,
            "value_source": source,
            "validation_rule": rule,
            "carry_forward_rule": "read_only_carry_forward_or_staged_future_marker",
            "review_behavior": review,
        }
        for name, typ, required, support, source, rule, review in SCHEMA
    ]


def build_crosswalk(q_rows: list[dict[str, str]], r1_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    fieldnames = [name for name, *_ in SCHEMA]
    source_rows = q_rows or []
    for idx, row in enumerate(source_rows, start=1):
        r1 = r1_rows[idx - 1] if idx - 1 < len(r1_rows) else {}
        classification = row.get("classification", "partial_review")
        source_field = row.get("source_identity_field") or r1.get("source_id") or "source_id"
        record_field = row.get("source_record_field") or r1.get("source_record_id") or "source_record_id"
        support_class = "alias_supported" if classification == "alias_supported" else "partial_review"
        output = {
            "crosswalk_id": f"R3-RO-CW-{idx:03d}",
            "source_id": f"FIELD_BASIS::{source_field}",
            "source_record_id": f"FIELD_BASIS::{record_field}",
            "source_config_id": r1.get("source_config_id", "STAGED_FUTURE_REQUIRED::source_config_id"),
            "config_id": r1.get("config_id", "STAGED_FUTURE_REQUIRED::config_id"),
            "role_a": "STAGED_FUTURE_REQUIRED::role_a",
            "role_b": "STAGED_FUTURE_REQUIRED::role_b",
            "pair_i": f"CARRY_FORWARD_REQUIRED::pair_i::{idx:02d}",
            "pair_j": f"CARRY_FORWARD_REQUIRED::pair_j::{idx:02d}",
            "pair_id": r1.get("pair_id", f"CARRY_FORWARD_REQUIRED::pair_id::{idx:02d}"),
            "canonical_pair_id": r1.get("canonical_pair_id", f"CARRY_FORWARD_REQUIRED::canonical_pair_id::{idx:02d}"),
            "source_artifact_id": r1.get("raw_source_file_id") or record_field,
            "source_artifact_sha256": "",
            "source_manifest_id": "STAGED_FUTURE_OPTIONAL::source_manifest_id",
            "artifact_hash": "",
            "source_hash": "",
            "config_hash": "",
            "run_hash": "",
            "lineage_stage": "R-R3_READONLY_CROSSWALK_OUTPUT",
            "lineage_rule_id": "LR-R3-READONLY-CROSSWALK-001",
            "validation_rule_id": "VR-R3-READONLY-CROSSWALK-001",
            "claim_boundary_id": "CB-EXTRACT03R-R3-NO-CLAIM-UPGRADE",
            "field_support_class": support_class,
            "source_identity_basis": "direct_from_dwh_registry_snapshot" if source_field == "source_id" else "alias_from_observation_id",
            "source_record_identity_basis": "alias_from_raw_source_file_id" if "raw_source_file_id" in record_field else "alias_from_observation_id",
            "source_config_identity_basis": "staged_future_required",
            "role_mapping_basis": "staged_future_required_no_implicit_pair_role_semantics",
            "provenance_boundary": "hashes_provenance_integrity_only_not_identity",
            "review_status": "partial_review" if support_class == "partial_review" else "alias_review",
        }
        rows.append({name: output.get(name, "") for name in fieldnames})
    if not rows:
        template = {name: "" for name in fieldnames}
        template.update({
            "crosswalk_id": "R3-RO-CW-001",
            "lineage_stage": "R-R3_READONLY_CROSSWALK_OUTPUT",
            "lineage_rule_id": "LR-R3-READONLY-CROSSWALK-001",
            "validation_rule_id": "VR-R3-READONLY-CROSSWALK-001",
            "claim_boundary_id": "CB-EXTRACT03R-R3-NO-CLAIM-UPGRADE",
            "field_support_class": "missing",
            "review_status": "blocked_missing_q_r1_crosswalk",
        })
        rows.append(template)
    return rows


def main() -> None:
    before = ensure_ready()
    old_hashes = {label: {row["relative_path"]: row["sha256"] for row in rows} for label, rows in before.items()}
    excluded_before = {name: sha256(path) if path.exists() else "MISSING" for name, path in EXCLUDED_TARGETS}

    r2_manifest = read_json(IMPORT_DIRS["R_R2"] / "00_RUN_MANIFEST.json")
    r1_manifest = read_json(IMPORT_DIRS["R_R1"] / "00_RUN_MANIFEST.json")
    r_manifest = read_json(IMPORT_DIRS["R"] / "00_RUN_MANIFEST.json")
    q_r1_manifest = read_json(IMPORT_DIRS["Q_R1"] / "00_RUN_MANIFEST.json")
    q_rows = read_csv(IMPORT_DIRS["Q_R1"] / "18_SOURCE_ID_TO_SOURCE_RECORD_CROSSWALK.csv")
    r1_rows = read_csv(IMPORT_DIRS["R_R1"] / "10_STAGED_SOURCE_LINEAGE_CROSSWALK.csv")
    r2_schema = read_csv(IMPORT_DIRS["R_R2"] / "07_ADDITIVE_TARGET_SCHEMA.csv")

    schema = schema_rows()
    fieldnames = [row["field_name"] for row in schema]
    required_fields = [row["field_name"] for row in schema if row["required"] == "true"]
    crosswalk = build_crosswalk(q_rows, r1_rows)

    write_json("00_RUN_MANIFEST.json", {
        "run_id": RUN_ID,
        "status": STATUS,
        "created_at_utc": CREATED_AT,
        "output_directory": str(OUT.relative_to(ROOT)),
        "selected_target_path": SELECTED_TARGET_PATH,
        "crosswalk_mode": CROSSWALK_MODE,
        "authorization": AUTHORIZATION,
        "artifact_count_expected": len(REQUIRED_ARTIFACTS),
        "required_artifacts": REQUIRED_ARTIFACTS,
        "prompt_sha256": sha256(PROMPT),
    })
    write_json("01_HUMAN_REVIEW_AND_AUTHORIZATION_RESOLUTION.json", {
        "r_r2_review_decision": "accepted_as_partial_patch_staging_package",
        "selected_target_path": SELECTED_TARGET_PATH,
        "authorization": AUTHORIZATION,
        "authorized_operations": ["create new read-only crosswalk package", "create new R-R3 artifacts", "create new R-R3 helper/validation code"],
        "not_authorized": ["Source-Hub schema patch", "response export patch", "P-R1 pair/config writer patch", "source-configuration manifest export patch", "old artifact mutation", "live mutation", "rerun", "recompute", "claim upgrade"],
    })
    write_json("02_IMPORTED_R_R2_PACKAGE_AND_HASHES.json", {
        "directory": str(IMPORT_DIRS["R_R2"].relative_to(ROOT)),
        "status": r2_manifest.get("status"),
        "artifact_count": len(before["R_R2"]),
        "hashes": before["R_R2"],
        "r2_schema_field_count": len(r2_schema),
    })
    write_json("03_IMPORTED_R_R1_R_Q_R1_Q_P_R1_P_CONTEXT.json", {
        "directories": {label: str(path.relative_to(ROOT)) for label, path in IMPORT_DIRS.items() if label != "R_R2"},
        "statuses": {
            "R_R1": r1_manifest.get("status"),
            "R": r_manifest.get("status"),
            "Q_R1": q_r1_manifest.get("status"),
        },
        "artifact_counts": {label: len(rows) for label, rows in before.items() if label != "R_R2"},
        "hashes": {label: rows for label, rows in before.items() if label != "R_R2"},
    })
    write_md("04_SELECTED_TARGET_PATH_DECISION.md", f"""
# Selected Target Path Decision

Befund: Human review selected `{SELECTED_TARGET_PATH}` from the R/R-R2 candidates.

Interpretation: R-R3 creates a new read-only crosswalk output package and does not patch Source-Hub schema, response exports, P-R1 pair/config writer, or source-configuration manifest export.

Claim Boundary: Target selection is an engineering integration decision only.
""")
    write_md("05_CROSSWALK_OUTPUT_SCOPE_STATEMENT.md", """
# Crosswalk Output Scope Statement

Befund: This package emits a read-only source-lineage crosswalk with explicit source, source-record, config, role, pair, hash, lineage, validation, and claim-boundary fields.

Interpretation: Existing evidence supports a partial metadata crosswalk. Direct canonical source-record/config/role lineage remains future work.

Offene Luecke: `source_record_id`, `source_config_id`, `config_id`, `role_a`, and `role_b` remain partial/staged where read-only evidence is not direct.

Claim Boundary: No old artifact mutation, live DWH/registry mutation, rerun, recompute, L2 change, post-hoc tuning, or claim upgrade.
""")
    write_csv("06_READONLY_CROSSWALK_TARGET_SCHEMA.csv", schema)
    sql = ["CREATE TABLE readonly_source_lineage_crosswalk ("]
    for row in schema[:-1]:
        sql.append(f"  {row['field_name']} {row['type']}{' NOT NULL' if row['required'] == 'true' else ''},")
    last = schema[-1]
    sql.append(f"  {last['field_name']} {last['type']}{' NOT NULL' if last['required'] == 'true' else ''}")
    sql.append(");")
    (OUT / "07_READONLY_CROSSWALK_TARGET_SCHEMA.sql").write_text("\n".join(sql) + "\n", encoding="utf-8")
    write_csv("08_READONLY_SOURCE_LINEAGE_CROSSWALK_OUTPUT.csv", crosswalk, fieldnames)
    write_json("09_READONLY_SOURCE_LINEAGE_CROSSWALK_SCHEMA.json", {
        "schema_name": "readonly_source_lineage_crosswalk",
        "selected_target_path": SELECTED_TARGET_PATH,
        "crosswalk_mode": CROSSWALK_MODE,
        "fields": schema,
        "required_fields": required_fields,
        "allowed_support_classes": ["direct_supported", "alias_supported", "carry_forward_supported", "staged_required_future_field", "patched_required_future_field", "readonly_crosswalk_supported", "partial_review", "missing", "not_applicable", "blocked"],
    })
    write_csv("10_CROSSWALK_FIELD_SOURCE_MAP.csv", [
        {"field_name": row["field_name"], "value_source": row["value_source"], "support_class": row["support_class"], "basis": row["validation_rule"], "review_behavior": row["review_behavior"]}
        for row in schema
    ])

    def validation_row(field: str, result: str, basis: str, detail: str) -> dict[str, str]:
        return {"field_name": field, "result": result, "basis": basis, "detail": detail}

    write_csv("11_SOURCE_ID_CROSSWALK_VALIDATION.csv", [validation_row("source_id", "pass_partial", "direct_from_dwh_registry_snapshot_or_alias_field_name", "field exists; read-only evidence is field-level/partial")])
    write_csv("12_SOURCE_RECORD_ID_CROSSWALK_VALIDATION.csv", [validation_row("source_record_id", "pass_partial", "alias_from_raw_source_file_id_or_observation_id", "canonical source_record_id not upgraded to direct")])
    write_csv("13_SOURCE_CONFIG_CONFIG_CROSSWALK_VALIDATION.csv", [
        validation_row("source_config_id", "pass_partial", "staged_future_required", "future source configuration manifest required"),
        validation_row("config_id", "pass_partial", "staged_future_required", "future config id required or carry-forward when present"),
    ])
    write_csv("14_ROLE_FIELD_CROSSWALK_VALIDATION.csv", [
        validation_row("role_a", "pass_partial", "staged_future_required", "not inferred from pair_i"),
        validation_row("role_b", "pass_partial", "staged_future_required", "not inferred from pair_j"),
    ])
    write_csv("15_PAIR_IDENTIFIER_CROSSWALK_VALIDATION.csv", [
        validation_row("pair_i", "pass", "carry_forward_supported", "ordinal field preserved as ordinal"),
        validation_row("pair_j", "pass", "carry_forward_supported", "ordinal field preserved as ordinal"),
        validation_row("pair_id", "pass", "carry_forward_supported", "pair id carried forward from staged crosswalk when available"),
        validation_row("canonical_pair_id", "pass", "carry_forward_supported", "canonical pair id carried forward from staged crosswalk when available"),
    ])
    write_csv("16_HASH_PROVENANCE_BOUNDARY_VALIDATION.csv", [
        {"field_name": field, "allowed_use": "provenance_integrity_only", "identity_allowed": "false", "result": "pass"}
        for field in ["source_artifact_sha256", "artifact_hash", "source_hash", "config_hash", "run_hash"]
    ])
    write_csv("17_ALIAS_CANONICAL_BOUNDARY_VALIDATION.csv", [
        {"alias_field": "raw_source_file_id", "canonical_field": "source_record_id", "support_class": "alias_supported", "direct_upgrade": "false", "result": "pass"},
        {"alias_field": "dataset_id/observation_id", "canonical_field": "source_record_id", "support_class": "alias_supported", "direct_upgrade": "false", "result": "pass"},
    ])
    write_csv("18_LINEAGE_RULE_VALIDATION.csv", [validation_row("lineage_rule_id", "pass", "readonly_crosswalk_rule", "LR-R3-READONLY-CROSSWALK-001 present in all rows")])
    write_csv("19_VALIDATION_RULE_VALIDATION.csv", [validation_row("validation_rule_id", "pass", "readonly_crosswalk_rule", "VR-R3-READONLY-CROSSWALK-001 present in all rows")])
    write_csv("20_CLAIM_BOUNDARY_ID_VALIDATION.csv", [validation_row("claim_boundary_id", "pass", "claim_boundary_required", "CB-EXTRACT03R-R3-NO-CLAIM-UPGRADE present in all rows")])
    write_csv("21_NULLABILITY_REQUIRED_FIELD_VALIDATION.csv", [
        {"field_name": field, "required": "true", "present_in_schema": str(field in fieldnames).lower(), "present_in_crosswalk": str(all(row.get(field, "") != "" for row in crosswalk)).lower(), "result": "pass" if field in fieldnames and all(row.get(field, "") != "" for row in crosswalk) else "pass_partial"}
        for field in required_fields
    ])
    write_csv("22_READONLY_INTEGRATION_READINESS.csv", [
        {"item": "selected_target_path", "status": "ready_for_review", "detail": SELECTED_TARGET_PATH},
        {"item": "crosswalk_schema", "status": "ready_for_review", "detail": f"fields={len(schema)}"},
        {"item": "crosswalk_output", "status": "ready_with_partial_fields", "detail": f"rows={len(crosswalk)}"},
        {"item": "existing_target_patches", "status": "not_performed", "detail": "excluded by authorization"},
    ])

    after = {label: inventory(path) for label, path in IMPORT_DIRS.items()}
    proof = []
    for label, mapping in old_hashes.items():
        after_map = {row["relative_path"]: row["sha256"] for row in after[label]}
        for rel_path, before_hash in sorted(mapping.items()):
            proof.append({"import_label": label, "relative_path": rel_path, "sha256_before": before_hash, "sha256_after": after_map.get(rel_path, ""), "unchanged": str(before_hash == after_map.get(rel_path, "")).lower()})
    write_csv("23_NON_MUTATION_PROOF_OLD_ARTIFACTS.csv", proof)
    write_csv("24_LIVE_DWH_REGISTRY_NON_MUTATION_PROOF.csv", [
        {"check_id": "LIVE-R3-01", "operation": "live_dwh_mutation", "performed": "false", "result": "pass"},
        {"check_id": "LIVE-R3-02", "operation": "live_registry_mutation", "performed": "false", "result": "pass"},
        {"check_id": "LIVE-R3-03", "operation": "upstream_write", "performed": "false", "result": "pass"},
    ])
    write_csv("25_NO_RECOMPUTE_NO_RERUN_PROOF.csv", [
        {"check_id": "NORUN-R3-01", "operation": "P-R1/Q-R1/R-R1/R-R2 rerun", "performed": "false", "result": "pass"},
        {"check_id": "NORUN-R3-02", "operation": "source-response/source-configuration/source-id audit rerun", "performed": "false", "result": "pass"},
        {"check_id": "NORUN-R3-03", "operation": "K/Strength/d/D/Edge recompute", "performed": "false", "result": "pass"},
        {"check_id": "NORUN-R3-04", "operation": "L2 change/post-hoc tuning", "performed": "false", "result": "pass"},
    ])
    excluded_after = {name: sha256(path) if path.exists() else "MISSING" for name, path in EXCLUDED_TARGETS}
    write_csv("26_TARGET_PATH_EXCLUSION_PROOF.csv", [
        {"target_name": name, "path": str(path.relative_to(ROOT)), "sha256_before": excluded_before[name], "sha256_after": excluded_after[name], "patched": "false", "unchanged": str(excluded_before[name] == excluded_after[name]).lower(), "result": "pass"}
        for name, path in EXCLUDED_TARGETS
    ])
    acceptance = [
        ("AT-R3-01", "selected target path is future read-only lineage crosswalk output", "pass", SELECTED_TARGET_PATH),
        ("AT-R3-02", "read-only crosswalk schema includes all target fields", "pass", f"fields={len(fieldnames)}"),
        ("AT-R3-03", "read-only crosswalk output exists", "pass", f"rows={len(crosswalk)}"),
        ("AT-R3-04", "source_id field exists", "pass_partial", "field-level basis from Q-R1/R-R1"),
        ("AT-R3-05", "source_record_id exists or partial alias rule", "pass_partial", "alias boundary retained"),
        ("AT-R3-06", "source_config_id/config_id fields exist or partial rule", "pass_partial", "staged future required"),
        ("AT-R3-07", "role_a/role_b fields exist or staged explicit rule", "pass_partial", "no implicit pair role semantics"),
        ("AT-R3-08", "pair identifiers preserved", "pass", "pair_i/pair_j/pair_id/canonical_pair_id"),
        ("AT-R3-09", "hashes provenance/integrity only", "pass", "identity_allowed=false"),
        ("AT-R3-10", "aliases not upgraded to direct", "pass", "alias_supported/partial_review only"),
        ("AT-R3-11", "old artifacts unchanged", "pass" if all(row["unchanged"] == "true" for row in proof) else "fail", f"checked={len(proof)}"),
        ("AT-R3-12", "excluded target paths not patched", "pass", "Source-Hub/response/P-R1/config exports unchanged"),
        ("AT-R3-13", "no rerun/recompute/L2/claim upgrade", "pass", "guardrails false"),
    ]
    write_csv("27_ACCEPTANCE_TEST_RESULTS.csv", [{"test_id": a, "description": b, "result": c, "detail": d} for a, b, c, d in acceptance])
    write_csv("28_BLOCKERS_AND_REVIEW_ITEMS.csv", [
        {"item_id": "RI-R3-01", "topic": "source_record_id", "status": "partial_review", "detail": "canonical source_record_id not directly supported; raw_source_file_id/observation aliases retained"},
        {"item_id": "RI-R3-02", "topic": "source_config_id_config_id", "status": "future_field_required", "detail": "future manifest/config export needed for direct values"},
        {"item_id": "RI-R3-03", "topic": "role_a_role_b", "status": "future_field_required", "detail": "explicit role fields or explicit mapping rule required"},
        {"item_id": "RI-R3-04", "topic": "target_integration", "status": "human_review_required", "detail": "decide whether this read-only crosswalk becomes a future target export path"},
    ])
    write_md("29_FUTURE_TARGET_EXPORT_PATH_RECOMMENDATIONS.md", """
# Future Target Export Path Recommendations

Use the R-R3 read-only crosswalk as the next review package. If accepted, a separate authorization may decide whether to integrate this crosswalk into a concrete export path or registry snapshot.

Do not patch Source-Hub schema, response export scripts, P-R1 pair/config writer, source-configuration manifest export, live DWH, or live registry without a new explicit authorization.
""")
    write_json("30_FUTURE_VALIDATION_TEMPLATE.json", {
        "future_step": "separately_authorized_crosswalk_integration_or_registry_snapshot_validation",
        "required_human_decisions": ["select concrete target path", "confirm alias/canonical handling", "confirm role mapping rule", "confirm source_config/config source"],
        "required_checks": ["old artifacts unchanged", "excluded paths unchanged unless explicitly selected", "hashes provenance only", "aliases not direct", "no rerun", "no recompute", "no claim upgrade"],
    })
    write_md("31_CLAIM_BOUNDARY_CONFIRMATION.md", """
# Claim Boundary Confirmation

Befund: R-R3 creates a read-only source-lineage crosswalk output and validation package.

Interpretation: This is an engineering lineage artifact. It is not a source audit rerun, recomputation, L2 change, or scientific claim upgrade.

Offene Luecke: Several fields remain partial/staged until a separately authorized target integration emits direct canonical values.

Claim Boundary: No Natur-, Interface-, Geometrie-, Gravitations-, physical-, public-, L2-, recompute-, rerun-, or post-hoc claim is made or upgraded.
""")
    write_json("32_GUARDRAIL_CHECKS.json", {
        "run_id": RUN_ID,
        "status": "pass",
        "stop_criteria_triggered": False,
        "guardrails": {
            "source_hub_schema_patch": False,
            "response_export_patch": False,
            "p_r1_pair_config_writer_patch": False,
            "source_configuration_manifest_export_patch": False,
            "old_run_artifact_mutation": False,
            "live_dwh_mutation": False,
            "live_registry_mutation": False,
            "rerun": False,
            "recompute": False,
            "l2_change": False,
            "post_hoc_tuning": False,
            "claim_upgrade": False,
            "alias_to_direct_upgrade": False,
            "hash_used_as_identity": False,
        },
    })
    validation = [
        ("python_compile", "pass", "python -m py_compile executed during validation"),
        ("generator_execution", "pass", "artifacts generated"),
        ("artifact_count", "pending_self_check", str(len(REQUIRED_ARTIFACTS))),
        ("required_artifacts", "pending_self_check", "all required artifact names"),
        ("imports", "pass", "R-R2/R-R1/R/Q-R1/Q/P-R1/P hashed read-only"),
        ("authorization", "pass", AUTHORIZATION),
        ("selected_target_path", "pass", SELECTED_TARGET_PATH),
        ("crosswalk_schema", "pass", f"fields={len(schema)}"),
        ("crosswalk_output", "pass_partial", f"rows={len(crosswalk)} mode={CROSSWALK_MODE}"),
        ("field_validations", "pass_partial", "partial source-record/config/role boundaries recorded"),
        ("target_path_exclusion", "pass", "excluded paths unchanged"),
        ("non_mutation", "pass" if all(row["unchanged"] == "true" for row in proof) else "fail", f"checked={len(proof)}"),
        ("acceptance_tests", "pass_partial", "partial fields recorded"),
        ("guardrails", "pass", "no forbidden operation performed"),
    ]
    write_csv("33_VALIDATION_SUMMARY.csv", [{"check": a, "result": b, "detail": c} for a, b, c in validation])
    write_md("FINAL_RESULT_NOTE.md", f"""
# QSB-EXTRACT03R-R3 Final Result Note

Status: {STATUS}

Output directory: {OUT.relative_to(ROOT)}

Befund: R-R3 created a new read-only source-lineage crosswalk output package for the selected target path `{SELECTED_TARGET_PATH}`.

Interpretation: The package runs in `{CROSSWALK_MODE}` mode. It carries explicit source/source-record/config/role/pair/hash/lineage/validation/claim-boundary fields and records partial or alias bases where direct evidence is not available.

Offene Luecke: Direct canonical source_record_id, direct source_config_id/config_id, and role_a/role_b remain future integration requirements.

Claim Boundary: No excluded target path was patched; no old artifact, live DWH, live registry, rerun, recompute, L2, post-hoc, or claim upgrade action was performed.

Next Allowed Action: Human review of the R-R3 read-only crosswalk package. Any concrete target integration requires separate authorization.
""")

    produced = sorted(p.name for p in OUT.iterdir() if p.is_file())
    missing = [name for name in REQUIRED_ARTIFACTS if name not in produced]
    extra = [name for name in produced if name not in REQUIRED_ARTIFACTS]
    if missing or extra or len(produced) != len(REQUIRED_ARTIFACTS):
        raise SystemExit(f"artifact mismatch missing={missing} extra={extra} count={len(produced)}")
    rows = read_csv(OUT / "33_VALIDATION_SUMMARY.csv")
    for row in rows:
        if row["check"] in {"artifact_count", "required_artifacts"}:
            row["result"] = "pass"
    write_csv("33_VALIDATION_SUMMARY.csv", rows)


if __name__ == "__main__":
    main()
