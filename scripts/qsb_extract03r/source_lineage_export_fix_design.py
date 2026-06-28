#!/usr/bin/env python3
"""Generate QSB-EXTRACT03R source-lineage export fix design artifacts.

Design-only: no schema/export patch, no ETL modification, no rerun, no recompute,
no upstream/live mutation, no L2 change, and no claim upgrade.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "runs/QSB-EXTRACT03R/source_lineage_export_fix_design"
Q_R1 = REPO_ROOT / "runs/QSB-EXTRACT03Q-R1/narrow_readonly_source_id_source_record_lineage_audit"
Q = REPO_ROOT / "runs/QSB-EXTRACT03Q/narrow_source_id_source_record_lineage_contract"
P_R1 = REPO_ROOT / "runs/QSB-EXTRACT03P-R1/narrow_real_data_source_configuration_lineage_audit"
P = REPO_ROOT / "runs/QSB-EXTRACT03P/narrow_source_configuration_lineage_audit_contract"

STATUS = "extract03r_source_lineage_export_fix_design_completed_ready_for_review"
CLAIM_BOUNDARY = (
    "EXTRACT03R is a design-only source-lineage export/schema fix block. It "
    "does not implement a schema/export patch, modify ETL/export code, rewrite "
    "old artifacts, rerun audits, recompute K/Strength/d/D/Edge, mutate upstream "
    "or live DWH/registry state, change L2, perform post-hoc tuning, or upgrade "
    "physical/public claims."
)
NEXT_ALLOWED_ACTION = (
    "Human review of the R design. If accepted, separately authorize R1 to "
    "implement or stage the minimal export/schema fix."
)

ARTIFACTS = [
    "00_RUN_MANIFEST.json",
    "01_IMPORTED_CONTEXT_AND_HASHES.json",
    "02_Q_R1_FINDINGS_CARRIED_FORWARD.json",
    "03_FIX_SCOPE_STATEMENT.md",
    "04_CURRENT_GAP_SUMMARY.csv",
    "05_TARGET_FIELD_CONTRACT.csv",
    "06_SOURCE_ID_PROPAGATION_DESIGN.csv",
    "07_SOURCE_RECORD_ID_DESIGN.csv",
    "08_SOURCE_CONFIG_ID_CONFIG_ID_DESIGN.csv",
    "09_ROLE_A_ROLE_B_DESIGN.csv",
    "10_PAIR_I_PAIR_J_TO_ROLE_MAPPING_RULES.csv",
    "11_JOIN_KEY_PROPAGATION_MAP.csv",
    "12_DWH_REGISTRY_CARRY_FORWARD_MAP.csv",
    "13_ALIAS_TO_CANONICAL_MAPPING_PROPOSAL.csv",
    "14_EXPORT_HOOK_CANDIDATES.csv",
    "15_MINIMAL_CHANGE_SET_PROPOSAL.csv",
    "16_BACKWARD_COMPATIBILITY_PLAN.md",
    "17_EXISTING_ARTIFACT_NON_MUTATION_PLAN.md",
    "18_IMPLEMENTATION_RISK_REGISTER.csv",
    "19_ACCEPTANCE_TEST_PLAN.csv",
    "20_VALIDATION_QUERY_PLAN.csv",
    "21_NO_RECOMPUTE_VERIFICATION_PLAN.csv",
    "22_CLAIM_BOUNDARY_CONFIRMATION.md",
    "23_ALLOWED_OPERATIONS_FOR_FUTURE_R1.csv",
    "24_FORBIDDEN_OPERATIONS_FOR_FUTURE_R1.csv",
    "25_STOP_CRITERIA_FOR_FUTURE_R1.csv",
    "26_FUTURE_IMPLEMENTATION_AUTHORIZATION_TEMPLATE_EXTRACT03R_R1.json",
    "27_REVIEW_ITEMS.csv",
    "28_GUARDRAIL_CHECKS.json",
    "29_VALIDATION_SUMMARY.csv",
    "FINAL_RESULT_NOTE.md",
]

CONTEXT = {
    "Q_R1_manifest": Q_R1 / "00_RUN_MANIFEST.json",
    "Q_R1_review_items": Q_R1 / "21_BLOCKERS_AND_REVIEW_ITEMS.csv",
    "Q_R1_fix_recommendations": Q_R1 / "23_SCHEMA_OR_EXPORT_FIX_RECOMMENDATIONS.md",
    "Q_R1_source_id_matrix": Q_R1 / "16_SOURCE_ID_CLASSIFICATION_MATRIX.csv",
    "Q_R1_source_record_matrix": Q_R1 / "17_SOURCE_RECORD_CLASSIFICATION_MATRIX.csv",
    "Q_R1_join_key_audit": Q_R1 / "13_JOIN_KEY_COMPATIBILITY_AUDIT.csv",
    "Q_manifest": Q / "00_RUN_MANIFEST.json",
    "Q_target_source_id_fields": Q / "04_SOURCE_ID_FIELD_REQUIREMENTS.csv",
    "Q_target_source_record_fields": Q / "05_SOURCE_RECORD_FIELD_REQUIREMENTS.csv",
    "P_R1_manifest": P_R1 / "01_extract03p_r1_run_manifest.json",
    "P_R1_field_matrix": P_R1 / "09_source_configuration_field_observation_matrix.csv",
    "P_R1_join_key_matrix": P_R1 / "10_lineage_join_key_coverage_matrix.csv",
    "P_manifest": P / "01_extract03p_run_manifest.json",
    "DWH_external_source_registry": REPO_ROOT / "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/db28_external_source_registry.csv",
    "DWH_raw_source_file_migration": REPO_ROOT / "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/dwh05_raw_source_file_migration.csv",
    "DWH_source_to_core_dataset_map": REPO_ROOT / "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/dwh05_source_to_core_dataset_map.csv",
    "SourceHub_schema": REPO_ROOT / "scripts/qsb_source_hub/source_hub_schema.sql",
}

TARGET_FIELDS = [
    ("source_id", "Direct source identity for each future pair/config row", "DWH/registry source identity or validated source registry crosswalk", "direct", "required", "not_null_after_fix", "source_id;source_registry_id", "must join to source registry without alias overstatement"),
    ("source_record_id", "Canonical source-record identity", "new canonical record id or accepted alias map from raw_source_file_id/observation_id", "direct_or_alias", "required", "not_null_or_documented_alias", "source_record_id;raw_source_file_id;observation_id", "canonical or alias mapping must be explicit"),
    ("source_config_id", "Source configuration identity", "future source configuration manifest/export metadata", "direct", "required", "not_null_after_fix", "source_config_id;config_id", "must be present or blocked"),
    ("config_id", "Configuration identifier", "future export manifest/config registry", "direct_or_alias", "required", "not_null_after_fix", "config_id;source_config_id", "must map to source_config_id"),
    ("role_a", "Explicit first role in pair", "future pair export from pair_i semantic mapping", "derived", "required", "not_null_after_fix", "pair_id;role_a", "must preserve pair_i and document semantic rule"),
    ("role_b", "Explicit second role in pair", "future pair export from pair_j semantic mapping", "derived", "required", "not_null_after_fix", "pair_id;role_b", "must preserve pair_j and document semantic rule"),
    ("pair_i", "Existing first pair coordinate", "existing pair export", "carry_forward", "required", "not_null", "pair_id;pair_i", "must remain backward compatible"),
    ("pair_j", "Existing second pair coordinate", "existing pair export", "carry_forward", "required", "not_null", "pair_id;pair_j", "must remain backward compatible"),
    ("pair_id", "Existing pair join key", "existing pair/vector export", "carry_forward", "required", "not_null", "pair_id", "must remain unchanged"),
    ("canonical_pair_id", "Canonical pair key", "existing/future pair split export", "carry_forward", "required", "not_null", "canonical_pair_id;pair_id", "must not rewrite old rows"),
    ("source_artifact_id", "Artifact identity for source lineage", "DWH raw source file or future artifact registry", "alias", "optional", "nullable_with_source_record_id", "source_artifact_id;raw_source_file_id", "alias-only unless direct field exists"),
    ("source_manifest_id", "Manifest identity for source lineage", "future export manifest", "direct", "optional", "nullable", "source_manifest_id", "future new export only"),
    ("artifact_hash", "Artifact provenance hash", "hash manifests/source hub", "carry_forward", "optional", "nullable", "artifact_hash;sha256", "provenance only"),
    ("source_hash", "Source provenance hash", "Source-Hub/DWH metadata", "carry_forward", "optional", "nullable", "source_hash", "not semantic identity alone"),
    ("config_hash", "Config provenance hash", "future config manifest", "carry_forward", "optional", "nullable", "config_hash", "not semantic identity alone"),
    ("run_hash", "Run provenance hash", "run manifest/hash inventory", "carry_forward", "optional", "nullable", "run_hash;sha256", "not semantic identity alone"),
    ("lineage_stage", "Lineage stage marker", "future export stage metadata", "direct", "required", "not_null_after_fix", "lineage_stage", "must distinguish source/config/pair/vector stages"),
    ("lineage_rule_id", "Lineage rule reference", "future rule registry", "direct", "required", "not_null_after_fix", "lineage_rule_id", "must identify mapping rule"),
    ("validation_rule_id", "Validation rule reference", "future validation plan", "direct", "required", "not_null_after_fix", "validation_rule_id", "must identify acceptance test"),
    ("claim_boundary_id", "Claim boundary reference", "existing claim boundary registry or run note", "carry_forward", "required", "not_null", "claim_boundary_id;claim_boundary", "must prevent claim upgrade"),
]


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def sha256(path: Path) -> str:
    if not path.is_file():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(name: str, fields: list[str], rows: list[dict[str, object]]) -> None:
    with (OUT_DIR / name).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(name: str, obj: object) -> None:
    (OUT_DIR / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_md(name: str, text: str) -> None:
    (OUT_DIR / name).write_text(text.strip() + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if any(OUT_DIR.iterdir()):
        raise SystemExit(f"Refusing to overwrite non-empty output directory: {OUT_DIR}")

    created_at = datetime.now(timezone.utc).isoformat()
    q_r1_manifest = json.loads((Q_R1 / "00_RUN_MANIFEST.json").read_text(encoding="utf-8"))
    q_manifest = json.loads((Q / "00_RUN_MANIFEST.json").read_text(encoding="utf-8"))
    p_r1_manifest = json.loads((P_R1 / "01_extract03p_r1_run_manifest.json").read_text(encoding="utf-8"))
    p_manifest = json.loads((P / "01_extract03p_run_manifest.json").read_text(encoding="utf-8"))
    q_r1_review_items = read_csv(Q_R1 / "21_BLOCKERS_AND_REVIEW_ITEMS.csv")

    imported = [
        {"context_id": f"CTX-{idx:02d}", "name": name, "path": rel(path), "exists": path.exists(), "sha256": sha256(path), "readonly_use": "yes"}
        for idx, (name, path) in enumerate(CONTEXT.items(), 1)
    ]
    gap_rows = [
        {"gap_id": "GAP-01", "gap": "explicit P-R1 source_id linkage", "q_r1_status": "partial_review", "design_response": "add source_id to future pair/config export rows", "old_artifacts_mutated": "false"},
        {"gap_id": "GAP-02", "gap": "canonical source_record_id", "q_r1_status": "partial_review", "design_response": "define canonical source_record_id or documented alias map from raw_source_file_id/observation_id", "old_artifacts_mutated": "false"},
        {"gap_id": "GAP-03", "gap": "direct role_a / role_b", "q_r1_status": "partial_review", "design_response": "add role_a/role_b or explicit semantic mapping from pair_i/pair_j", "old_artifacts_mutated": "false"},
        {"gap_id": "GAP-04", "gap": "source_config_id / config_id", "q_r1_status": "missing", "design_response": "add config identity fields to future source-configuration export manifests", "old_artifacts_mutated": "false"},
    ]
    target_rows = [
        {
            "canonical_name": name,
            "purpose": purpose,
            "source_of_value": source,
            "value_type": value_type,
            "required_or_optional": required,
            "allowed_nullability": nullability,
            "expected_join_keys": joins,
            "validation_rule": validation,
            "backward_compatibility_behavior": "future exports add field; existing artifacts remain untouched",
            "future_new_export_only": "yes",
            "existing_artifacts_must_remain_untouched": "yes",
        }
        for name, purpose, source, value_type, required, nullability, joins, validation in TARGET_FIELDS
    ]

    source_id_design = [
        {"design_id": "SID-D-01", "design_step": "locate direct source_id", "current_evidence": "DWH registry has source_id context", "future_fix": "future P-R1-style rows include source_id", "validation": "source_id non-null and joins to source registry", "boundary": "no alias-to-direct overstatement"},
        {"design_id": "SID-D-02", "design_step": "connect source identity to pair/config rows", "current_evidence": "P-R1 lacks direct source_id in pair/config artifacts", "future_fix": "export source_id via source metadata crosswalk at export time", "validation": "pair_id/source_id crosswalk complete", "boundary": "no recompute"},
        {"design_id": "SID-D-03", "design_step": "hash handling", "current_evidence": "hashes are provenance carry-forward only", "future_fix": "keep hashes as artifact_hash/source_hash fields", "validation": "hashes preserved but not used as semantic identity", "boundary": "no claim upgrade"},
    ]
    source_record_design = [
        {"record_id": "SREC-D-01", "candidate": "raw_source_file_id", "classification": "alias_source_record_identity", "future_design": "map to canonical source_record_id if R1 authorized", "requires_raw_access": "no"},
        {"record_id": "SREC-D-02", "candidate": "observation_id", "classification": "alias_source_record_identity", "future_design": "record as observation-level alias", "requires_raw_access": "no"},
        {"record_id": "SREC-D-03", "candidate": "source_record_id", "classification": "missing", "future_design": "new explicit canonical field in future export", "requires_raw_access": "no_if_using_existing_metadata_snapshot"},
        {"record_id": "SREC-D-04", "candidate": "source_file_id/source_artifact_id", "classification": "partial_review", "future_design": "document file/artifact mapping to source_record_id", "requires_raw_access": "no"},
        {"record_id": "SREC-D-05", "candidate": "content/source/config/run hashes", "classification": "carry_forward_provenance_only", "future_design": "preserve as provenance only", "requires_raw_access": "no"},
    ]
    config_design = [
        {"design_id": "CFG-D-01", "field": "source_config_id", "current_status": "missing", "future_design": "add explicit source_config_id to source-configuration export manifest", "validation": "non-null or blocked"},
        {"design_id": "CFG-D-02", "field": "config_id", "current_status": "missing", "future_design": "add config_id or alias to source_config_id", "validation": "joins to config manifest"},
    ]
    role_design = [
        {"design_id": "ROLE-D-01", "field": "role_a", "required": "yes", "mapping": "pair_i -> role_a only if semantic rule is declared", "invariant": "pair_i preserved; no relabeling of old artifacts"},
        {"design_id": "ROLE-D-02", "field": "role_b", "required": "yes", "mapping": "pair_j -> role_b only if semantic rule is declared", "invariant": "pair_j preserved; no relabeling of old artifacts"},
        {"design_id": "ROLE-D-03", "field": "pair_i/pair_j", "required": "yes", "mapping": "carry-forward ordinal pair context", "invariant": "not automatically semantic role identity"},
    ]
    pair_rules = [
        {"rule_id": "PAIR-RULE-01", "source_field": "pair_i", "target_field": "role_a", "mapping_type": "ordinal_to_semantic_if_declared", "required_invariant": "pair_i unchanged; mapping rule id present", "forbidden_overstatement": "do not claim semantic role without rule"},
        {"rule_id": "PAIR-RULE-02", "source_field": "pair_j", "target_field": "role_b", "mapping_type": "ordinal_to_semantic_if_declared", "required_invariant": "pair_j unchanged; mapping rule id present", "forbidden_overstatement": "do not infer symmetry semantics"},
    ]
    join_map = [
        {"map_id": "JOIN-01", "from_context": "DWH source registry", "from_key": "source_id", "to_future_field": "source_id", "validation": "exact non-null join", "status": "designed"},
        {"map_id": "JOIN-02", "from_context": "DWH raw source file migration", "from_key": "raw_source_file_id", "to_future_field": "source_record_id", "validation": "canonical or alias map explicit", "status": "designed_partial"},
        {"map_id": "JOIN-03", "from_context": "P-R1 pair/config rows", "from_key": "pair_id/canonical_pair_id", "to_future_field": "pair_id/canonical_pair_id", "validation": "backward-compatible unchanged", "status": "carry_forward"},
        {"map_id": "JOIN-04", "from_context": "future config manifest", "from_key": "source_config_id/config_id", "to_future_field": "source_config_id/config_id", "validation": "manifest row exists", "status": "designed_missing_input"},
    ]
    carry_forward = [
        {"carry_id": "CF-01", "source": "DWH external source registry", "field": "source_id", "carry_forward_use": "direct source identity context", "boundary": "future export must propagate explicitly"},
        {"carry_id": "CF-02", "source": "DWH raw source file migration", "field": "raw_source_file_id", "carry_forward_use": "source-record alias", "boundary": "not canonical unless mapped"},
        {"carry_id": "CF-03", "source": "Q/Q-R1/P/P-R1 manifests", "field": "hash/status/claim boundary", "carry_forward_use": "audit context", "boundary": "no repeated human decision if unchanged"},
    ]
    alias_map = [
        {"alias_id": "ALIAS-01", "alias_field": "raw_source_file_id", "canonical_target": "source_record_id", "proposal_status": "proposed_alias_until_canonical_defined", "validation": "one-to-one or documented many-to-one map"},
        {"alias_id": "ALIAS-02", "alias_field": "observation_id", "canonical_target": "source_record_id", "proposal_status": "observation_level_alias", "validation": "explicit relation to raw_source_file_id/source_id"},
        {"alias_id": "ALIAS-03", "alias_field": "pair_i/pair_j", "canonical_target": "role_a/role_b", "proposal_status": "semantic_mapping_requires_rule", "validation": "lineage_rule_id present"},
    ]
    hook_candidates = [
        {"hook_id": "HOOK-01", "candidate": "future P-R1 pair/config export writer", "reason": "smallest point to add source_id/source_record_id/config/role fields", "implementation_now": "no"},
        {"hook_id": "HOOK-02", "candidate": "future source-configuration manifest export", "reason": "source_config_id/config_id can be introduced at manifest level", "implementation_now": "no"},
        {"hook_id": "HOOK-03", "candidate": "future read-only lineage crosswalk output", "reason": "can avoid rewriting old artifacts", "implementation_now": "no"},
    ]
    minimal_change = [
        {"change_id": "MIN-01", "change": "add explicit fields to future export rows", "fields": "source_id;source_record_id;source_config_id;config_id;role_a;role_b", "scope": "future exports only", "required": "yes"},
        {"change_id": "MIN-02", "change": "add read-only source lineage crosswalk output", "fields": "pair_id;source_id;source_record_id;raw_source_file_id;observation_id", "scope": "new artifact only", "required": "yes"},
        {"change_id": "MIN-03", "change": "add validation tests", "fields": "lineage_rule_id;validation_rule_id;claim_boundary_id", "scope": "future R1", "required": "yes"},
        {"change_id": "MIN-04", "change": "preserve old artifacts unchanged", "fields": "all existing P/P-R1/Q/Q-R1 outputs", "scope": "non-mutation", "required": "yes"},
    ]
    risk_rows = [
        {"risk_id": "RISK-01", "risk": "alias-to-direct overstatement", "severity": "high", "mitigation": "require explicit direct source_id/source_record_id or label alias"},
        {"risk_id": "RISK-02", "risk": "role order mistaken for semantic role", "severity": "medium", "mitigation": "require lineage_rule_id for pair_i/pair_j -> role_a/role_b"},
        {"risk_id": "RISK-03", "risk": "old artifact rewrite temptation", "severity": "high", "mitigation": "future export only; old artifacts immutable"},
        {"risk_id": "RISK-04", "risk": "hash treated as semantic identity", "severity": "medium", "mitigation": "hash fields provenance only"},
    ]
    acceptance = [
        {"test_id": "ACC-01", "test": "explicit source_id present in new pair/config export", "expected": "pass with non-null source_id", "forbidden": "no recompute"},
        {"test_id": "ACC-02", "test": "canonical source_record_id present or alias mapping documented", "expected": "pass", "forbidden": "no raw access required"},
        {"test_id": "ACC-03", "test": "source_config_id/config_id present or mapped", "expected": "pass", "forbidden": "no live mutation"},
        {"test_id": "ACC-04", "test": "role_a/role_b present or mapped with invariant checks", "expected": "pass", "forbidden": "no relabeling"},
        {"test_id": "ACC-05", "test": "pair_i/pair_j preserved", "expected": "unchanged", "forbidden": "no old rewrite"},
        {"test_id": "ACC-06", "test": "hashes preserved as provenance only", "expected": "pass", "forbidden": "no semantic identity overstatement"},
        {"test_id": "ACC-07", "test": "existing artifacts unchanged", "expected": "hashes unchanged", "forbidden": "no mutation"},
        {"test_id": "ACC-08", "test": "no K/Strength/d/D/Edge recompute; no L2 change; no claim upgrade", "expected": "all false", "forbidden": "all listed operations"},
    ]
    validation_query = [
        {"query_id": "VQ-01", "query": "count rows where source_id is null", "expected": "0 for future export rows", "scope": "future R1 only"},
        {"query_id": "VQ-02", "query": "join future pair rows to source registry on source_id", "expected": "all rows join or documented block", "scope": "future R1 only"},
        {"query_id": "VQ-03", "query": "verify pair_i/pair_j unchanged from source rows", "expected": "all equal", "scope": "future R1 only"},
        {"query_id": "VQ-04", "query": "verify claim_boundary_id present", "expected": "all rows carry boundary", "scope": "future R1 only"},
    ]
    no_recompute = [
        {"check_id": "NRC-01", "check": "no K/Strength/d/D/Edge outputs generated", "expected": "no new model output files"},
        {"check_id": "NRC-02", "check": "no P-R1/Q-R1 rerun markers", "expected": "false"},
        {"check_id": "NRC-03", "check": "old artifact hashes unchanged", "expected": "same imported hashes"},
    ]
    allowed = ["read R/Q-R1/Q/P-R1/P artifacts", "inspect metadata snapshots read-only", "design field contracts", "design alias/canonical mappings", "design validation tests", "create new R design artifacts only"]
    forbidden = ["no schema/export implementation", "no code patch outside new R generator script", "no existing ETL/export modification", "no P-R1/Q-R1 rerun", "no source-response/source-configuration audit rerun", "no controls rerun", "no vector export/mutation", "no K/Strength/d/D/Edge recompute", "no upstream/live mutation", "no L2 change", "no post-hoc tuning", "no physical/public claim upgrade", "no old-artifact rewrite"]
    stop = ["Q-R1 output missing", "Q contract missing", "P/P-R1 context missing", "Q-R1 core findings cannot be imported", "direct source identity cannot be located", "no plausible future export hook candidate", "role semantics require forbidden assumptions", "canonical source-record design requires raw access/live mutation", "proposed fix requires recomputation", "proposed fix mutates old artifacts", "proposed fix upgrades claims", "design requires L2 change", "design requires post-hoc tuning"]

    write_json(
        "00_RUN_MANIFEST.json",
        {
            "work_package": "QSB-EXTRACT03R",
            "status": STATUS,
            "created_at_utc": created_at,
            "repo_root": str(REPO_ROOT),
            "q_r1_status": q_r1_manifest["status"],
            "q_status": q_manifest["status"],
            "p_r1_status": p_r1_manifest["status"],
            "p_status": p_manifest["status"],
            "design_only": True,
            "schema_export_patch_applied": False,
            "existing_export_or_etl_modified": False,
            "old_artifacts_modified": False,
            "p_r1_q_r1_rerun": False,
            "recompute_performed": False,
            "upstream_or_live_mutation": False,
            "l2_changed": False,
            "post_hoc_tuning": False,
            "claim_upgrade": False,
            "artifact_count": len(ARTIFACTS),
            "claim_boundary": CLAIM_BOUNDARY,
            "next_allowed_action": NEXT_ALLOWED_ACTION,
        },
    )
    write_json("01_IMPORTED_CONTEXT_AND_HASHES.json", {"contexts": imported})
    write_json(
        "02_Q_R1_FINDINGS_CARRIED_FORWARD.json",
        {
            "q_r1_status": q_r1_manifest["status"],
            "review_items": q_r1_review_items,
            "carried_forward_findings": [
                "DWH registry has direct source_id context.",
                "Direct source_id is absent in P-R1 pair/config artifacts.",
                "raw_source_file_id and observation_id provide source-record aliases.",
                "P-R1 source_id join remains partial.",
                "Hashes are provenance carry-forward only.",
                "role_a/role_b remain absent; pair_i/pair_j are carry-forward role/order context only.",
            ],
        },
    )
    write_md("03_FIX_SCOPE_STATEMENT.md", f"# Fix Scope Statement\n\nDesign the smallest future export/schema change that adds explicit source lineage fields to future artifacts while leaving all existing artifacts untouched.\n\n{CLAIM_BOUNDARY}")
    write_csv("04_CURRENT_GAP_SUMMARY.csv", list(gap_rows[0].keys()), gap_rows)
    write_csv("05_TARGET_FIELD_CONTRACT.csv", list(target_rows[0].keys()), target_rows)
    write_csv("06_SOURCE_ID_PROPAGATION_DESIGN.csv", list(source_id_design[0].keys()), source_id_design)
    write_csv("07_SOURCE_RECORD_ID_DESIGN.csv", list(source_record_design[0].keys()), source_record_design)
    write_csv("08_SOURCE_CONFIG_ID_CONFIG_ID_DESIGN.csv", list(config_design[0].keys()), config_design)
    write_csv("09_ROLE_A_ROLE_B_DESIGN.csv", list(role_design[0].keys()), role_design)
    write_csv("10_PAIR_I_PAIR_J_TO_ROLE_MAPPING_RULES.csv", list(pair_rules[0].keys()), pair_rules)
    write_csv("11_JOIN_KEY_PROPAGATION_MAP.csv", list(join_map[0].keys()), join_map)
    write_csv("12_DWH_REGISTRY_CARRY_FORWARD_MAP.csv", list(carry_forward[0].keys()), carry_forward)
    write_csv("13_ALIAS_TO_CANONICAL_MAPPING_PROPOSAL.csv", list(alias_map[0].keys()), alias_map)
    write_csv("14_EXPORT_HOOK_CANDIDATES.csv", list(hook_candidates[0].keys()), hook_candidates)
    write_csv("15_MINIMAL_CHANGE_SET_PROPOSAL.csv", list(minimal_change[0].keys()), minimal_change)
    write_md("16_BACKWARD_COMPATIBILITY_PLAN.md", "# Backward Compatibility Plan\n\nExisting P/P-R1/Q/Q-R1 artifacts remain immutable. Future exports add fields or emit a new crosswalk artifact. Existing `pair_i`, `pair_j`, `pair_id`, and `canonical_pair_id` remain unchanged.")
    write_md("17_EXISTING_ARTIFACT_NON_MUTATION_PLAN.md", "# Existing Artifact Non-Mutation Plan\n\nNo existing artifact is rewritten. Imported hashes in `01_IMPORTED_CONTEXT_AND_HASHES.json` provide carry-forward reference only. Any implementation must create new future artifacts.")
    write_csv("18_IMPLEMENTATION_RISK_REGISTER.csv", list(risk_rows[0].keys()), risk_rows)
    write_csv("19_ACCEPTANCE_TEST_PLAN.csv", list(acceptance[0].keys()), acceptance)
    write_csv("20_VALIDATION_QUERY_PLAN.csv", list(validation_query[0].keys()), validation_query)
    write_csv("21_NO_RECOMPUTE_VERIFICATION_PLAN.csv", list(no_recompute[0].keys()), no_recompute)
    write_md("22_CLAIM_BOUNDARY_CONFIRMATION.md", f"# Claim Boundary Confirmation\n\n{CLAIM_BOUNDARY}")
    write_csv("23_ALLOWED_OPERATIONS_FOR_FUTURE_R1.csv", ["operation_id", "operation", "boundary"], [{"operation_id": f"ALLOW-{i:02d}", "operation": op, "boundary": "future R1 only under separate authorization"} for i, op in enumerate(allowed, 1)])
    write_csv("24_FORBIDDEN_OPERATIONS_FOR_FUTURE_R1.csv", ["operation_id", "operation", "boundary"], [{"operation_id": f"FORBID-{i:02d}", "operation": op, "boundary": "forbidden by R design"} for i, op in enumerate(forbidden, 1)])
    write_csv("25_STOP_CRITERIA_FOR_FUTURE_R1.csv", ["stop_id", "criterion", "required_action"], [{"stop_id": f"STOP-{i:02d}", "criterion": criterion, "required_action": "stop and record blocker; do not widen scope"} for i, criterion in enumerate(stop, 1)])
    write_json(
        "26_FUTURE_IMPLEMENTATION_AUTHORIZATION_TEMPLATE_EXTRACT03R_R1.json",
        {
            "authorization_status": "TEMPLATE_REQUIRES_HUMAN_APPROVAL",
            "authorized_work_package": "QSB-EXTRACT03R-R1_SOURCE_LINEAGE_EXPORT_FIX_IMPLEMENTATION",
            "source_design": "QSB-EXTRACT03R",
            "human_approval_required": True,
            "allowed_scope": "implement_or_stage_minimal_export_schema_fix_only",
            "no_recompute": True,
            "no_audit_rerun": True,
            "no_live_dwh_or_registry_mutation_without_explicit_authorization": True,
            "no_l2_change": True,
            "no_claim_upgrade": True,
        },
    )
    write_csv("27_REVIEW_ITEMS.csv", ["review_item_id", "topic", "severity", "description", "next_action"], [
        {"review_item_id": "R-RI-01", "topic": "source_id propagation", "severity": "design_review", "description": "Confirm source_id source-of-truth and export hook.", "next_action": "human review"},
        {"review_item_id": "R-RI-02", "topic": "source_record_id canonicalization", "severity": "design_review", "description": "Decide canonical source_record_id vs alias map.", "next_action": "human review"},
        {"review_item_id": "R-RI-03", "topic": "role semantics", "severity": "design_review", "description": "Confirm whether pair_i/pair_j may map to semantic role_a/role_b.", "next_action": "human review"},
        {"review_item_id": "R-RI-04", "topic": "config identity", "severity": "design_review", "description": "Confirm source_config_id/config_id source.", "next_action": "human review"},
    ])
    write_json("28_GUARDRAIL_CHECKS.json", {"schema_export_patch_applied": False, "existing_export_or_etl_modified": False, "old_artifacts_modified": False, "p_r1_q_r1_rerun": False, "recompute_performed": False, "upstream_modified": False, "live_dwh_modified": False, "live_registry_modified": False, "l2_changed": False, "post_hoc_tuning": False, "claim_upgrade": False})
    validation = [
        ("VAL-01", "artifact_count_31", "pending", ""),
        ("VAL-02", "q_r1_q_p_r1_p_imported", "true", "contexts loaded"),
        ("VAL-03", "q_r1_findings_carried_forward", "true", "02_Q_R1_FINDINGS_CARRIED_FORWARD.json"),
        ("VAL-04", "target_field_contract_created", "true", str(len(target_rows))),
        ("VAL-05", "source_id_propagation_design_created", "true", str(len(source_id_design))),
        ("VAL-06", "source_record_id_design_created", "true", str(len(source_record_design))),
        ("VAL-07", "role_design_created", "true", str(len(role_design))),
        ("VAL-08", "join_key_map_created", "true", str(len(join_map))),
        ("VAL-09", "alias_to_canonical_proposal_created", "true", str(len(alias_map))),
        ("VAL-10", "minimal_change_set_created", "true", str(len(minimal_change))),
        ("VAL-11", "acceptance_test_plan_created", "true", str(len(acceptance))),
        ("VAL-12", "future_r1_template_not_authorized", "true", "TEMPLATE_REQUIRES_HUMAN_APPROVAL"),
        ("VAL-13", "guardrails_no_patch_no_rerun_no_recompute", "true", "28_GUARDRAIL_CHECKS.json"),
    ]
    write_csv("29_VALIDATION_SUMMARY.csv", ["validation_id", "check", "passed", "evidence"], [{"validation_id": a, "check": b, "passed": c, "evidence": d} for a, b, c, d in validation])
    write_md(
        "FINAL_RESULT_NOTE.md",
        f"""# QSB-EXTRACT03R Final Result

## Status
{STATUS}

## Imported Context
Q-R1, Q, P-R1, P, and referenced read-only DWH/Source-Hub metadata contexts were imported by path/hash only.

## Carried-Forward Q-R1 Findings
The design carries forward direct P-R1 `source_id` absence, source-record alias status, missing config identity, and role_a/role_b absence.

## Proposed Minimal Change Set
Add explicit source lineage fields to future exports, add a read-only crosswalk artifact, add validation tests, and preserve old artifacts unchanged.

## Claim Boundary
{CLAIM_BOUNDARY}

## Next Allowed Action
{NEXT_ALLOWED_ACTION}
""",
    )

    files = sorted(path.name for path in OUT_DIR.iterdir() if path.is_file())
    missing = [name for name in ARTIFACTS if name not in files]
    extra = [name for name in files if name not in ARTIFACTS]
    if missing or extra:
        raise SystemExit(f"Artifact mismatch missing={missing} extra={extra}")
    rows = read_csv(OUT_DIR / "29_VALIDATION_SUMMARY.csv")
    rows[0]["passed"] = str(len(files) == len(ARTIFACTS)).lower()
    rows[0]["evidence"] = str(len(files))
    write_csv("29_VALIDATION_SUMMARY.csv", list(rows[0].keys()), rows)


if __name__ == "__main__":
    main()
