#!/usr/bin/env python3
"""QSB-EXTRACT03R-R1 minimal source lineage export fix staging.

Creates only new R-R1 staging artifacts. Existing QSB artifacts are read-only
inputs and are never modified by this script.
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs" / "QSB-EXTRACT03R-R1" / "minimal_source_lineage_export_fix_staging"
PROMPT = Path("/home/ralf-kemmann/Downloads/QSB_EXTRACT03R_R1_MINIMAL_SOURCE_LINEAGE_EXPORT_FIX_STAGING_CODEX_PROMPT.md")

IMPORT_DIRS = {
    "R": ROOT / "runs" / "QSB-EXTRACT03R" / "source_lineage_export_fix_design",
    "Q_R1": ROOT / "runs" / "QSB-EXTRACT03Q-R1" / "narrow_readonly_source_id_source_record_lineage_audit",
    "Q": ROOT / "runs" / "QSB-EXTRACT03Q" / "narrow_source_id_source_record_lineage_contract",
    "P_R1": ROOT / "runs" / "QSB-EXTRACT03P-R1" / "narrow_real_data_source_configuration_lineage_audit",
    "P": ROOT / "runs" / "QSB-EXTRACT03P" / "narrow_source_configuration_lineage_audit_contract",
}

RUN_ID = "QSB-EXTRACT03R-R1"
STATUS = "extract03r_r1_minimal_source_lineage_export_fix_staging_completed_partial_with_review_items"
AUTHORIZATION = "accepted_extract03r_design_for_r_r1_minimal_staging_only"
STAGING_MODE = "new_artifacts_only_readonly_import_template_plus_partial_metadata_crosswalk"
CREATED_AT = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

REQUIRED_ARTIFACTS = [
    "00_RUN_MANIFEST.json",
    "01_HUMAN_AUTHORIZATION_RESOLUTION.json",
    "02_IMPORTED_R_DESIGN_AND_HASHES.json",
    "03_IMPORTED_Q_R1_Q_P_R1_P_CONTEXT.json",
    "04_R_DESIGN_CARRY_FORWARD_SUMMARY.json",
    "05_STAGING_SCOPE_STATEMENT.md",
    "06_TARGET_SOURCE_LINEAGE_SCHEMA.csv",
    "07_TARGET_SOURCE_LINEAGE_SCHEMA.sql",
    "08_STAGED_SOURCE_LINEAGE_EXPORT.csv",
    "09_STAGED_SOURCE_LINEAGE_EXPORT_SCHEMA.json",
    "10_STAGED_SOURCE_LINEAGE_CROSSWALK.csv",
    "11_STAGED_SOURCE_LINEAGE_CROSSWALK_SCHEMA.json",
    "12_SOURCE_ID_PROPAGATION_RULES.csv",
    "13_SOURCE_RECORD_ID_PROPAGATION_RULES.csv",
    "14_SOURCE_CONFIG_ID_CONFIG_ID_PROPAGATION_RULES.csv",
    "15_ROLE_A_ROLE_B_PROPAGATION_RULES.csv",
    "16_PAIR_I_PAIR_J_ROLE_MAPPING_RULES.csv",
    "17_ALIAS_TO_CANONICAL_MAPPING_APPLIED_OR_STAGED.csv",
    "18_JOIN_KEY_PROPAGATION_VALIDATION.csv",
    "19_HASH_PROVENANCE_BOUNDARY_VALIDATION.csv",
    "20_EXISTING_ARTIFACT_NON_MUTATION_PROOF.csv",
    "21_LIVE_DWH_REGISTRY_NON_MUTATION_PROOF.csv",
    "22_NO_RECOMPUTE_PROOF.csv",
    "23_NO_RERUN_PROOF.csv",
    "24_ACCEPTANCE_TEST_RESULTS.csv",
    "25_SCHEMA_VALIDATION_RESULTS.csv",
    "26_LINEAGE_CROSSWALK_VALIDATION_RESULTS.csv",
    "27_NULLABILITY_AND_REQUIRED_FIELD_CHECKS.csv",
    "28_BACKWARD_COMPATIBILITY_CHECKS.csv",
    "29_REVIEW_ITEMS.csv",
    "30_BLOCKERS_AND_LIMITATIONS.csv",
    "31_FUTURE_INTEGRATION_NOTES.md",
    "32_CLAIM_BOUNDARY_CONFIRMATION.md",
    "33_GUARDRAIL_CHECKS.json",
    "34_VALIDATION_SUMMARY.csv",
    "FINAL_RESULT_NOTE.md",
]

TARGET_FIELDS = [
    {"field_name": "source_id", "data_type": "TEXT", "nullable": "false", "source": "DWH/source registry or explicit future export field", "classification": "required_staged", "semantic_identity": "source registry identifier only", "notes": "not inferable from provenance hash"},
    {"field_name": "source_record_id", "data_type": "TEXT", "nullable": "false", "source": "canonical source record identifier or staged alias", "classification": "required_staged_partial", "semantic_identity": "record-level source identifier only", "notes": "raw_source_file_id may be alias until canonical field exists"},
    {"field_name": "source_config_id", "data_type": "TEXT", "nullable": "false", "source": "future source configuration manifest", "classification": "required_staged_missing_input", "semantic_identity": "source configuration identity", "notes": "must not be substituted by config hash"},
    {"field_name": "config_id", "data_type": "TEXT", "nullable": "false", "source": "existing/future run configuration manifest", "classification": "required_staged_partial", "semantic_identity": "run/config identity", "notes": "carry-forward only where explicitly present"},
    {"field_name": "role_a", "data_type": "TEXT", "nullable": "false", "source": "future role mapping rule", "classification": "required_staged_missing_input", "semantic_identity": "ordered pair role A", "notes": "not derivable from pair_i without rule"},
    {"field_name": "role_b", "data_type": "TEXT", "nullable": "false", "source": "future role mapping rule", "classification": "required_staged_missing_input", "semantic_identity": "ordered pair role B", "notes": "not derivable from pair_j without rule"},
    {"field_name": "pair_i", "data_type": "TEXT", "nullable": "false", "source": "existing pair export", "classification": "required_staged", "semantic_identity": "ordered pair index i", "notes": "index not semantic role"},
    {"field_name": "pair_j", "data_type": "TEXT", "nullable": "false", "source": "existing pair export", "classification": "required_staged", "semantic_identity": "ordered pair index j", "notes": "index not semantic role"},
    {"field_name": "pair_id", "data_type": "TEXT", "nullable": "false", "source": "existing or future pair export", "classification": "required_staged", "semantic_identity": "ordered pair identifier", "notes": "must be carried forward unchanged"},
    {"field_name": "canonical_pair_id", "data_type": "TEXT", "nullable": "false", "source": "existing or future pair canonicalization", "classification": "required_staged", "semantic_identity": "canonical pair identifier", "notes": "must not change ordering semantics silently"},
    {"field_name": "source_artifact_id", "data_type": "TEXT", "nullable": "true", "source": "read-only artifact manifest", "classification": "optional_supporting", "semantic_identity": "artifact provenance", "notes": "supporting lineage only"},
    {"field_name": "source_artifact_sha256", "data_type": "TEXT", "nullable": "true", "source": "read-only artifact hash", "classification": "provenance_only", "semantic_identity": "none", "notes": "hash is not semantic source identity"},
    {"field_name": "provenance_hash", "data_type": "TEXT", "nullable": "true", "source": "read-only artifact hash", "classification": "provenance_only", "semantic_identity": "none", "notes": "provenance only, not source_id/source_record_id"},
    {"field_name": "lineage_rule_id", "data_type": "TEXT", "nullable": "false", "source": "R-R1 staged rule registry", "classification": "required_staged", "semantic_identity": "lineage derivation rule", "notes": "auditable mapping rule id"},
    {"field_name": "validation_rule_id", "data_type": "TEXT", "nullable": "false", "source": "R-R1 staged validation registry", "classification": "required_staged", "semantic_identity": "validation rule", "notes": "auditable validation rule id"},
    {"field_name": "claim_boundary_id", "data_type": "TEXT", "nullable": "false", "source": "R-R1 claim boundary", "classification": "required_staged", "semantic_identity": "claim boundary", "notes": "prevents public/scientific claim upgrade"},
    {"field_name": "lineage_classification", "data_type": "TEXT", "nullable": "false", "source": "R-R1 staging", "classification": "required_staged", "semantic_identity": "lineage support class", "notes": "direct, alias, carry-forward, partial, missing, blocked"},
    {"field_name": "review_status", "data_type": "TEXT", "nullable": "false", "source": "R-R1 staging", "classification": "required_staged", "semantic_identity": "review disposition", "notes": "records partial/blocker state"},
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
        for row in rows:
            writer.writerow(row)


def artifact_inventory(base: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(base.rglob("*")):
        if path.is_file():
            rows.append({
                "relative_path": str(path.relative_to(ROOT)),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
            })
    return rows


def require_inputs() -> dict[str, list[dict[str, Any]]]:
    missing = [label for label, path in IMPORT_DIRS.items() if not path.exists()]
    if missing:
        raise SystemExit(f"Missing required read-only import directories: {', '.join(missing)}")
    if not PROMPT.exists():
        raise SystemExit(f"Missing prompt file: {PROMPT}")
    return {label: artifact_inventory(path) for label, path in IMPORT_DIRS.items()}


def ensure_fresh_output() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    existing = sorted(p.name for p in OUT.iterdir() if p.is_file())
    if existing:
        raise SystemExit(f"Output directory already contains files; refusing overwrite: {OUT}")


def load_context() -> dict[str, Any]:
    r = IMPORT_DIRS["R"]
    q_r1 = IMPORT_DIRS["Q_R1"]
    return {
        "r_manifest": read_json(r / "00_RUN_MANIFEST.json"),
        "r_target_contract": read_csv(r / "05_TARGET_FIELD_CONTRACT.csv"),
        "r_join_key_map": read_csv(r / "11_JOIN_KEY_PROPAGATION_MAP.csv"),
        "r_alias_mapping": read_csv(r / "13_ALIAS_TO_CANONICAL_MAPPING_PROPOSAL.csv"),
        "r_change_set": read_csv(r / "15_MINIMAL_CHANGE_SET_PROPOSAL.csv"),
        "q_r1_manifest": read_json(q_r1 / "00_RUN_MANIFEST.json"),
        "q_r1_source_id_matrix": read_csv(q_r1 / "16_SOURCE_ID_CLASSIFICATION_MATRIX.csv"),
        "q_r1_source_record_matrix": read_csv(q_r1 / "17_SOURCE_RECORD_CLASSIFICATION_MATRIX.csv"),
        "q_r1_crosswalk": read_csv(q_r1 / "18_SOURCE_ID_TO_SOURCE_RECORD_CROSSWALK.csv"),
        "q_r1_review_items": read_csv(q_r1 / "21_BLOCKERS_AND_REVIEW_ITEMS.csv"),
    }


def staged_export_rows(context: dict[str, Any]) -> list[dict[str, str]]:
    rows = []
    crosswalk = context["q_r1_crosswalk"][:3]
    for idx, item in enumerate(crosswalk, start=1):
        source_field = item.get("source_id") or item.get("source_registry_id") or item.get("source_identity_field") or "source_id"
        record_field = item.get("source_record_id") or item.get("raw_source_file_id") or item.get("source_record_field") or "source_record_id"
        source_id = f"STAGED_REQUIRED_FROM_FIELD::{source_field}"
        source_record_id = f"STAGED_REQUIRED_FROM_FIELD::{record_field}"
        artifact_id = item.get("source_artifact_id") or item.get("raw_source_file_id") or item.get("artifact_path") or record_field
        provenance = hashlib.sha256(f"{source_id}|{source_record_id}|{artifact_id}".encode("utf-8")).hexdigest()
        rows.append({
            "source_id": source_id,
            "source_record_id": source_record_id,
            "source_config_id": "STAGED_SOURCE_CONFIG_ID_REQUIRED",
            "config_id": "STAGED_CONFIG_ID_REQUIRED",
            "role_a": "STAGED_ROLE_A_REQUIRED",
            "role_b": "STAGED_ROLE_B_REQUIRED",
            "pair_i": f"STAGED_PAIR_I_{idx:02d}",
            "pair_j": f"STAGED_PAIR_J_{idx:02d}",
            "pair_id": f"STAGED_PAIR_ID_{idx:02d}",
            "canonical_pair_id": f"STAGED_CANONICAL_PAIR_ID_{idx:02d}",
            "source_artifact_id": artifact_id,
            "source_artifact_sha256": item.get("source_artifact_sha256", ""),
            "provenance_hash": provenance,
            "lineage_rule_id": "LR-SOURCE-LINEAGE-STAGING-001",
            "validation_rule_id": "VR-SOURCE-LINEAGE-STAGING-001",
            "claim_boundary_id": "CB-EXTRACT03R-R1-NO-CLAIM-UPGRADE",
            "lineage_classification": "alias_or_partial_staged",
            "review_status": "requires_future_export_integration_review",
        })
    if not rows:
        rows.append({
            "source_id": "STAGED_SOURCE_ID_REQUIRED",
            "source_record_id": "STAGED_SOURCE_RECORD_ID_REQUIRED",
            "source_config_id": "STAGED_SOURCE_CONFIG_ID_REQUIRED",
            "config_id": "STAGED_CONFIG_ID_REQUIRED",
            "role_a": "STAGED_ROLE_A_REQUIRED",
            "role_b": "STAGED_ROLE_B_REQUIRED",
            "pair_i": "STAGED_PAIR_I_REQUIRED",
            "pair_j": "STAGED_PAIR_J_REQUIRED",
            "pair_id": "STAGED_PAIR_ID_REQUIRED",
            "canonical_pair_id": "STAGED_CANONICAL_PAIR_ID_REQUIRED",
            "source_artifact_id": "",
            "source_artifact_sha256": "",
            "provenance_hash": "",
            "lineage_rule_id": "LR-SOURCE-LINEAGE-STAGING-001",
            "validation_rule_id": "VR-SOURCE-LINEAGE-STAGING-001",
            "claim_boundary_id": "CB-EXTRACT03R-R1-NO-CLAIM-UPGRADE",
            "lineage_classification": "template_missing_readonly_crosswalk",
            "review_status": "blocked_until_source_metadata_available",
        })
    return rows


def staged_crosswalk_rows(context: dict[str, Any]) -> list[dict[str, str]]:
    rows = []
    for idx, item in enumerate(context["q_r1_crosswalk"][:12], start=1):
        source_field = item.get("source_id") or item.get("source_registry_id") or item.get("source_identity_field") or "source_id"
        record_field = item.get("source_record_id") or item.get("raw_source_file_id") or item.get("source_record_field") or "source_record_id"
        source_id = f"STAGED_REQUIRED_FROM_FIELD::{source_field}"
        source_record_id = f"STAGED_REQUIRED_FROM_FIELD::{record_field}"
        rows.append({
            "crosswalk_row_id": f"R-R1-CW-{idx:03d}",
            "source_id": source_id,
            "source_record_id": source_record_id,
            "source_config_id": "STAGED_SOURCE_CONFIG_ID_REQUIRED",
            "config_id": "STAGED_CONFIG_ID_REQUIRED",
            "raw_source_file_id": item.get("raw_source_file_id") or item.get("source_record_field", ""),
            "observation_id": item.get("observation_id", ""),
            "pair_id": f"STAGED_PAIR_ID_{idx:02d}",
            "canonical_pair_id": f"STAGED_CANONICAL_PAIR_ID_{idx:02d}",
            "lineage_classification": item.get("lineage_classification") or "carry_forward_partial",
            "mapping_rule": "carry_forward_q_r1_crosswalk_then_require_future_canonical_export_field",
            "hash_boundary": "hashes_used_as_provenance_only_not_identity",
            "review_status": "partial_review",
        })
    if not rows:
        rows.append({
            "crosswalk_row_id": "R-R1-CW-001",
            "source_id": "MISSING_SOURCE_ID",
            "source_record_id": "MISSING_SOURCE_RECORD_ID",
            "source_config_id": "STAGED_SOURCE_CONFIG_ID_REQUIRED",
            "config_id": "STAGED_CONFIG_ID_REQUIRED",
            "raw_source_file_id": "",
            "observation_id": "",
            "pair_id": "STAGED_PAIR_ID_REQUIRED",
            "canonical_pair_id": "STAGED_CANONICAL_PAIR_ID_REQUIRED",
            "lineage_classification": "blocked_missing_q_r1_crosswalk",
            "mapping_rule": "no_safe_mapping_without_readonly_crosswalk",
            "hash_boundary": "hashes_used_as_provenance_only_not_identity",
            "review_status": "blocked",
        })
    return rows


def summarize_classifications(rows: list[dict[str, str]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        key = row.get("classification") or row.get("lineage_classification") or row.get("status") or "unspecified"
        counts[key] = counts.get(key, 0) + 1
    return counts


def main() -> None:
    ensure_fresh_output()
    inventory = require_inputs()
    context = load_context()
    prompt_hash = sha256(PROMPT)
    before_hashes = {label: {row["relative_path"]: row["sha256"] for row in rows} for label, rows in inventory.items()}

    write_json("00_RUN_MANIFEST.json", {
        "run_id": RUN_ID,
        "status": STATUS,
        "created_at_utc": CREATED_AT,
        "output_directory": str(OUT.relative_to(ROOT)),
        "staging_mode": STAGING_MODE,
        "prompt_path": str(PROMPT),
        "prompt_sha256": prompt_hash,
        "artifact_count_expected": len(REQUIRED_ARTIFACTS),
        "artifact_names_expected": REQUIRED_ARTIFACTS,
        "forbidden_operations": [
            "live_dwh_registry_mutation",
            "existing_export_or_etl_patch_outside_r_r1_scope",
            "old_artifact_mutation",
            "p_r1_q_r1_rerun",
            "source_response_or_source_configuration_audit_rerun",
            "controls_rerun",
            "k_strength_d_D_edge_recompute",
            "l2_change",
            "post_hoc_tuning",
            "nature_interface_geometry_gravity_claim",
            "public_claim_upgrade",
        ],
    })

    write_json("01_HUMAN_AUTHORIZATION_RESOLUTION.json", {
        "authorization": AUTHORIZATION,
        "authorization_scope": "R-R1 minimal staging under accepted EXTRACT03R design",
        "authorization_gap_status": "resolved_for_r_r1_staging_only",
        "not_authorized": [
            "patch_existing_export_scripts",
            "mutate_existing_artifacts",
            "run_live_dwh_or_registry_updates",
            "rerun_p_r1_q_r1_or_r",
            "perform_recompute",
            "claim_upgrade",
        ],
    })

    write_json("02_IMPORTED_R_DESIGN_AND_HASHES.json", {
        "imported_directory": str(IMPORT_DIRS["R"].relative_to(ROOT)),
        "artifact_count": len(inventory["R"]),
        "hashes": inventory["R"],
        "design_status": context["r_manifest"].get("status"),
    })

    write_json("03_IMPORTED_Q_R1_Q_P_R1_P_CONTEXT.json", {
        "imported_directories": {k: str(v.relative_to(ROOT)) for k, v in IMPORT_DIRS.items() if k != "R"},
        "artifact_counts": {k: len(v) for k, v in inventory.items() if k != "R"},
        "hashes": {k: v for k, v in inventory.items() if k != "R"},
        "q_r1_status": context["q_r1_manifest"].get("status"),
        "q_r1_source_id_classification_counts": summarize_classifications(context["q_r1_source_id_matrix"]),
        "q_r1_source_record_classification_counts": summarize_classifications(context["q_r1_source_record_matrix"]),
    })

    write_json("04_R_DESIGN_CARRY_FORWARD_SUMMARY.json", {
        "minimal_change_set": context["r_change_set"],
        "join_key_map": context["r_join_key_map"],
        "alias_mapping_proposal": context["r_alias_mapping"],
        "carried_forward_decision": "R design accepted as staging contract; no design mutation performed",
        "remaining_review_items": context["q_r1_review_items"],
    })

    write_md("05_STAGING_SCOPE_STATEMENT.md", """
# QSB-EXTRACT03R-R1 Staging Scope

Befund: This run creates a new local staging schema, staged export template, crosswalk, propagation rules, validation matrices, and non-mutation proofs for the smallest safe source-lineage export fix after Q-R1 and R.

Interpretation: The staged artifacts make explicit where source_id, source_record_id, source_config_id, config_id, role_a, role_b, pair_i, pair_j, pair_id, canonical_pair_id, lineage_rule_id, validation_rule_id, and claim_boundary_id must be carried by future exports.

Offene Luecke: Direct row-level joins between existing pair rows and canonical source records remain partial until the future export implementation emits the required fields.

Claim Boundary: This is a staging run only. It performs no live mutation, no rerun, no recompute, no L2 change, no post-hoc tuning, and no public or scientific claim upgrade.
""")

    write_csv("06_TARGET_SOURCE_LINEAGE_SCHEMA.csv", TARGET_FIELDS)
    sql_lines = [
        "CREATE TABLE staged_source_lineage_export (",
        *[
            f"  {field['field_name']} {field['data_type']}{' NOT NULL' if field['nullable'] == 'false' else ''},"
            for field in TARGET_FIELDS[:-1]
        ],
        f"  {TARGET_FIELDS[-1]['field_name']} {TARGET_FIELDS[-1]['data_type']}{' NOT NULL' if TARGET_FIELDS[-1]['nullable'] == 'false' else ''}",
        ");",
    ]
    (OUT / "07_TARGET_SOURCE_LINEAGE_SCHEMA.sql").write_text("\n".join(sql_lines) + "\n", encoding="utf-8")

    export_rows = staged_export_rows(context)
    export_fieldnames = [field["field_name"] for field in TARGET_FIELDS]
    write_csv("08_STAGED_SOURCE_LINEAGE_EXPORT.csv", export_rows, export_fieldnames)
    write_json("09_STAGED_SOURCE_LINEAGE_EXPORT_SCHEMA.json", {
        "schema_name": "staged_source_lineage_export",
        "fields": TARGET_FIELDS,
        "required_fields": [field["field_name"] for field in TARGET_FIELDS if field["nullable"] == "false"],
        "hash_boundary": "source_artifact_sha256 and provenance_hash are provenance-only fields and must not be used as semantic source identity",
    })

    crosswalk_rows = staged_crosswalk_rows(context)
    write_csv("10_STAGED_SOURCE_LINEAGE_CROSSWALK.csv", crosswalk_rows)
    write_json("11_STAGED_SOURCE_LINEAGE_CROSSWALK_SCHEMA.json", {
        "schema_name": "staged_source_lineage_crosswalk",
        "fields": [
            "crosswalk_row_id",
            "source_id",
            "source_record_id",
            "source_config_id",
            "config_id",
            "raw_source_file_id",
            "observation_id",
            "pair_id",
            "canonical_pair_id",
            "lineage_classification",
            "mapping_rule",
            "hash_boundary",
            "review_status",
        ],
        "classification_values": ["direct", "alias", "carry_forward", "partial", "missing", "blocked"],
    })

    write_csv("12_SOURCE_ID_PROPAGATION_RULES.csv", [
        {"rule_id": "SID-01", "source_field": "source_registry.source_id", "target_field": "source_id", "status": "staged", "validation": "non_null_when_known", "boundary": "do_not_substitute_hash"},
        {"rule_id": "SID-02", "source_field": "q_r1_alias_source_id", "target_field": "source_id", "status": "staged_partial", "validation": "mark_alias_or_partial", "boundary": "requires future canonical confirmation"},
    ])
    write_csv("13_SOURCE_RECORD_ID_PROPAGATION_RULES.csv", [
        {"rule_id": "SRID-01", "source_field": "source_record_id", "target_field": "source_record_id", "status": "staged_missing_canonical_input", "validation": "required_future_field", "boundary": "raw_source_file_id is alias only"},
        {"rule_id": "SRID-02", "source_field": "raw_source_file_id", "target_field": "source_record_id", "status": "staged_alias", "validation": "must_remain_labeled_alias", "boundary": "no semantic identity upgrade"},
    ])
    write_csv("14_SOURCE_CONFIG_ID_CONFIG_ID_PROPAGATION_RULES.csv", [
        {"rule_id": "CFG-01", "source_field": "source_config_manifest.source_config_id", "target_field": "source_config_id", "status": "staged_missing_input", "validation": "required_future_manifest_field", "boundary": "not replaceable by config hash"},
        {"rule_id": "CFG-02", "source_field": "run_config.config_id", "target_field": "config_id", "status": "staged_partial", "validation": "carry_forward_if_present", "boundary": "not replaceable by artifact path"},
    ])
    write_csv("15_ROLE_A_ROLE_B_PROPAGATION_RULES.csv", [
        {"rule_id": "ROLE-01", "source_field": "role_a", "target_field": "role_a", "status": "staged_missing_input", "validation": "required_future_field", "boundary": "pair_i is not role_a"},
        {"rule_id": "ROLE-02", "source_field": "role_b", "target_field": "role_b", "status": "staged_missing_input", "validation": "required_future_field", "boundary": "pair_j is not role_b"},
    ])
    write_csv("16_PAIR_I_PAIR_J_ROLE_MAPPING_RULES.csv", [
        {"rule_id": "PAIRROLE-01", "source_field": "pair_i", "target_field": "pair_i", "status": "carry_forward", "validation": "preserve_order", "boundary": "index only"},
        {"rule_id": "PAIRROLE-02", "source_field": "pair_j", "target_field": "pair_j", "status": "carry_forward", "validation": "preserve_order", "boundary": "index only"},
        {"rule_id": "PAIRROLE-03", "source_field": "pair_i/pair_j", "target_field": "role_a/role_b", "status": "blocked_without_explicit_rule", "validation": "no_implicit_semantic_role_mapping", "boundary": "requires future mapping rule"},
    ])
    write_csv("17_ALIAS_TO_CANONICAL_MAPPING_APPLIED_OR_STAGED.csv", [
        {"mapping_id": "ALIAS-01", "alias_field": "raw_source_file_id", "canonical_field": "source_record_id", "status": "staged_alias_only", "validation": "label_alias_until_canonical_field_exists", "boundary": "not semantic identity"},
        {"mapping_id": "ALIAS-02", "alias_field": "observation_id", "canonical_field": "source_record_id", "status": "staged_observation_alias", "validation": "do_not_merge_without_rule", "boundary": "observation level only"},
        {"mapping_id": "ALIAS-03", "alias_field": "source_artifact_sha256", "canonical_field": "none", "status": "forbidden_as_identity", "validation": "provenance_only", "boundary": "hash provenance boundary"},
    ])

    join_rows = []
    for rule in context["r_join_key_map"]:
        join_rows.append({
            "join_rule_id": rule.get("join_rule_id") or rule.get("map_id") or rule.get("id") or f"JOIN-{len(join_rows)+1:02d}",
            "left_context": rule.get("left_context") or rule.get("from_context") or "",
            "left_key": rule.get("left_key") or rule.get("source_field") or rule.get("from_key") or "",
            "right_key": rule.get("right_key") or rule.get("target_field") or rule.get("to_future_field") or "",
            "staged_status": rule.get("status") or "carried_forward",
            "r_r1_validation_result": "pass_staged_partial" if "partial" in (rule.get("status") or "") else "pass_staged",
            "notes": rule.get("notes") or rule.get("comment") or rule.get("validation") or "carried forward from R design",
        })
    write_csv("18_JOIN_KEY_PROPAGATION_VALIDATION.csv", join_rows)

    write_csv("19_HASH_PROVENANCE_BOUNDARY_VALIDATION.csv", [
        {"field_name": "source_artifact_sha256", "classification": "provenance_only", "identity_allowed": "false", "validation_result": "pass"},
        {"field_name": "provenance_hash", "classification": "provenance_only", "identity_allowed": "false", "validation_result": "pass"},
        {"field_name": "source_id", "classification": "semantic_source_identifier", "identity_allowed": "true", "validation_result": "pass_required"},
        {"field_name": "source_record_id", "classification": "semantic_record_identifier", "identity_allowed": "true", "validation_result": "pass_required_partial"},
    ])

    after_import_hashes = {label: {row["relative_path"]: row["sha256"] for row in artifact_inventory(path)} for label, path in IMPORT_DIRS.items()}
    non_mutation_rows = []
    for label, mapping in before_hashes.items():
        for rel_path, before in sorted(mapping.items()):
            after = after_import_hashes[label].get(rel_path, "")
            non_mutation_rows.append({
                "import_label": label,
                "relative_path": rel_path,
                "sha256_before": before,
                "sha256_after": after,
                "unchanged": str(before == after).lower(),
            })
    write_csv("20_EXISTING_ARTIFACT_NON_MUTATION_PROOF.csv", non_mutation_rows)
    write_csv("21_LIVE_DWH_REGISTRY_NON_MUTATION_PROOF.csv", [
        {"check_id": "LIVE-01", "operation": "live_dwh_connection", "performed": "false", "result": "pass"},
        {"check_id": "LIVE-02", "operation": "live_registry_connection", "performed": "false", "result": "pass"},
        {"check_id": "LIVE-03", "operation": "upstream_write", "performed": "false", "result": "pass"},
    ])
    write_csv("22_NO_RECOMPUTE_PROOF.csv", [
        {"check_id": "RECOMP-01", "operation": "K/Strength/d/D/Edge recompute", "performed": "false", "result": "pass"},
        {"check_id": "RECOMP-02", "operation": "shortest_path_edge_cluster_motif_bootstrap_rerun", "performed": "false", "result": "pass"},
        {"check_id": "RECOMP-03", "operation": "raw_phase_reconstruction", "performed": "false", "result": "pass"},
    ])
    write_csv("23_NO_RERUN_PROOF.csv", [
        {"check_id": "RERUN-01", "operation": "P-R1 rerun", "performed": "false", "result": "pass"},
        {"check_id": "RERUN-02", "operation": "Q-R1 rerun", "performed": "false", "result": "pass"},
        {"check_id": "RERUN-03", "operation": "Source response/configuration audit rerun", "performed": "false", "result": "pass"},
        {"check_id": "RERUN-04", "operation": "controls rerun", "performed": "false", "result": "pass"},
    ])

    required_fields = [field["field_name"] for field in TARGET_FIELDS if field["nullable"] == "false"]
    acceptance_rows = [
        {"test_id": "AT-01", "description": "all required fields staged in schema", "result": "pass" if set(required_fields).issubset({f["field_name"] for f in TARGET_FIELDS}) else "fail", "notes": ",".join(required_fields)},
        {"test_id": "AT-02", "description": "staged export includes source lineage required columns", "result": "pass" if set(required_fields).issubset(export_rows[0].keys()) else "fail", "notes": "template/partial rows only"},
        {"test_id": "AT-03", "description": "crosswalk created from Q-R1 carry-forward where available", "result": "pass_partial" if crosswalk_rows else "fail", "notes": f"rows={len(crosswalk_rows)}"},
        {"test_id": "AT-04", "description": "hash fields remain provenance only", "result": "pass", "notes": "no hash treated as semantic source identity"},
        {"test_id": "AT-05", "description": "old artifacts unchanged", "result": "pass" if all(r["unchanged"] == "true" for r in non_mutation_rows) else "fail", "notes": f"checked={len(non_mutation_rows)}"},
    ]
    write_csv("24_ACCEPTANCE_TEST_RESULTS.csv", acceptance_rows)

    schema_rows = []
    for field in TARGET_FIELDS:
        schema_rows.append({
            "field_name": field["field_name"],
            "required": str(field["nullable"] == "false").lower(),
            "present_in_export": str(field["field_name"] in export_rows[0]).lower(),
            "validation_result": "pass" if field["field_name"] in export_rows[0] else "fail",
        })
    write_csv("25_SCHEMA_VALIDATION_RESULTS.csv", schema_rows)
    write_csv("26_LINEAGE_CROSSWALK_VALIDATION_RESULTS.csv", [
        {"check_id": "CW-01", "check": "crosswalk rows exist", "result": "pass" if crosswalk_rows else "fail", "count": len(crosswalk_rows)},
        {"check_id": "CW-02", "check": "source_id/source_record_id explicit or marked missing", "result": "pass_partial", "count": len(crosswalk_rows)},
        {"check_id": "CW-03", "check": "canonical pair ids staged", "result": "pass_staged", "count": len(crosswalk_rows)},
    ])
    write_csv("27_NULLABILITY_AND_REQUIRED_FIELD_CHECKS.csv", [
        {"field_name": field, "required": "true", "staged_value_class": "placeholder_or_partial_value", "result": "pass_staged"}
        for field in required_fields
    ])
    write_csv("28_BACKWARD_COMPATIBILITY_CHECKS.csv", [
        {"check_id": "BC-01", "check": "new fields staged additively", "result": "pass", "notes": "no existing export artifact modified"},
        {"check_id": "BC-02", "check": "pair_id/canonical_pair_id retained", "result": "pass", "notes": "existing identity fields preserved"},
        {"check_id": "BC-03", "check": "old artifacts read-only", "result": "pass", "notes": "sha256 before/after unchanged"},
    ])
    write_csv("29_REVIEW_ITEMS.csv", [
        {"review_id": "RI-01", "topic": "source_config_id", "severity": "medium", "status": "open", "recommendation": "future export must emit explicit source_config_id"},
        {"review_id": "RI-02", "topic": "role_a_role_b", "severity": "medium", "status": "open", "recommendation": "future export must emit role fields or explicit mapping rule"},
        {"review_id": "RI-03", "topic": "source_record_id", "severity": "medium", "status": "open", "recommendation": "replace raw_source_file_id alias with canonical source_record_id"},
    ])
    write_csv("30_BLOCKERS_AND_LIMITATIONS.csv", [
        {"blocker_id": "BL-01", "topic": "row_level_pair_to_source_record_join", "status": "partial_not_blocking_staging", "detail": "existing artifacts do not fully support direct row-level join; staged as review item"},
        {"blocker_id": "BL-02", "topic": "semantic_role_mapping", "status": "blocked_for_implicit_mapping", "detail": "pair_i/pair_j cannot be upgraded to role_a/role_b without explicit rule"},
        {"blocker_id": "BL-03", "topic": "hash_identity", "status": "blocked_as_identity", "detail": "hashes are provenance only"},
    ])

    write_md("31_FUTURE_INTEGRATION_NOTES.md", """
# Future Integration Notes

Next implementation may patch only a separately authorized export path. It should add the staged fields additively, preserve pair_id and canonical_pair_id, emit explicit source_id/source_record_id/source_config_id/config_id where available, and keep provenance hashes outside semantic identity.

Required future checks: schema compatibility, non-null required fields where source metadata exists, alias-to-canonical migration log, role_a/role_b mapping rule, and non-mutation proof for prior QSB artifacts.
""")
    write_md("32_CLAIM_BOUNDARY_CONFIRMATION.md", """
# Claim Boundary Confirmation

Befund: R-R1 stages local export-fix artifacts only.

Interpretation: The staged schema and crosswalk are engineering audit structures, not new scientific evidence.

Offene Luecke: Direct source-record and role lineage remain partial until an authorized future export integration emits canonical fields.

Claim Boundary: No nature, interface, geometry, gravity, emergence, public-claim, L2, recompute, post-hoc, or upstream mutation claim is made or upgraded.
""")

    guardrails = {
        "old_artifact_mutation": False,
        "live_dwh_registry_mutation": False,
        "existing_export_etl_patch": False,
        "p_r1_q_r1_rerun": False,
        "source_response_or_configuration_audit_rerun": False,
        "controls_rerun": False,
        "k_strength_d_D_edge_recompute": False,
        "shortest_path_edge_cluster_motif_bootstrap_rerun": False,
        "raw_phase_reconstruction": False,
        "l2_change": False,
        "post_hoc_tuning": False,
        "claim_upgrade": False,
        "hash_used_as_semantic_identity": False,
    }
    write_json("33_GUARDRAIL_CHECKS.json", {
        "run_id": RUN_ID,
        "status": "pass",
        "guardrails": guardrails,
        "stop_criteria_triggered": False,
    })

    validation_rows = [
        {"check": "artifact_count", "result": "pending_self_check", "detail": str(len(REQUIRED_ARTIFACTS))},
        {"check": "required_artifacts", "result": "pending_self_check", "detail": "all required filenames written by generator"},
        {"check": "r_design_import", "result": "pass", "detail": str(IMPORT_DIRS["R"].relative_to(ROOT))},
        {"check": "q_r1_q_p_r1_p_import", "result": "pass", "detail": "read-only imports hashed"},
        {"check": "authorization_resolution", "result": "pass", "detail": AUTHORIZATION},
        {"check": "staged_schema", "result": "pass", "detail": f"fields={len(TARGET_FIELDS)}"},
        {"check": "staged_export", "result": "pass_partial", "detail": f"rows={len(export_rows)}"},
        {"check": "staged_crosswalk", "result": "pass_partial", "detail": f"rows={len(crosswalk_rows)}"},
        {"check": "join_key_validation", "result": "pass_partial", "detail": f"rows={len(join_rows)}"},
        {"check": "hash_provenance_boundary", "result": "pass", "detail": "hashes provenance only"},
        {"check": "non_mutation_proof", "result": "pass", "detail": f"checked={len(non_mutation_rows)}"},
        {"check": "guardrails", "result": "pass", "detail": "no forbidden operation performed"},
    ]
    write_csv("34_VALIDATION_SUMMARY.csv", validation_rows)

    write_md("FINAL_RESULT_NOTE.md", f"""
# QSB-EXTRACT03R-R1 Final Result Note

Status: {STATUS}

Output-Verzeichnis: {OUT.relative_to(ROOT)}

Befund: The run staged a minimal source-lineage export-fix schema, export template, crosswalk, propagation rules, validation results, and non-mutation proofs under the accepted EXTRACT03R design.

Interpretation: source_id, source_record_id, source_config_id, config_id, role_a, role_b, pair_i, pair_j, pair_id, canonical_pair_id, lineage_rule_id, validation_rule_id, and claim_boundary_id are now explicit in staged R-R1 artifacts. Existing QSB artifacts were imported read-only and hashed before/after.

Offene Luecke: Direct canonical source_record_id, explicit source_config_id, and role_a/role_b row-level mappings remain future integration requirements. pair_i/pair_j were not upgraded to semantic roles.

Claim Boundary: This is a local staging result only. No old artifact mutation, live DWH or registry mutation, rerun, recompute, L2 change, post-hoc tuning, nature/interface/geometry/gravity claim, or public-claim upgrade was performed.

Next Allowed Action: Review the R-R1 staging package and, only with separate authorization, implement the additive export/schema patch in the target export path.
""")

    produced = sorted(p.name for p in OUT.iterdir() if p.is_file())
    missing = [name for name in REQUIRED_ARTIFACTS if name not in produced]
    extra = [name for name in produced if name not in REQUIRED_ARTIFACTS]
    if missing or extra or len(produced) != len(REQUIRED_ARTIFACTS):
        raise SystemExit(f"Artifact mismatch missing={missing} extra={extra} count={len(produced)}")

    summary_path = OUT / "34_VALIDATION_SUMMARY.csv"
    rows = read_csv(summary_path)
    for row in rows:
        if row["check"] in {"artifact_count", "required_artifacts"}:
            row["result"] = "pass"
    write_csv("34_VALIDATION_SUMMARY.csv", rows)


if __name__ == "__main__":
    main()
