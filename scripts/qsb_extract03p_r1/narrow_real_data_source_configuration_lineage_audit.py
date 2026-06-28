#!/usr/bin/env python3
"""Generate QSB-EXTRACT03P-R1 narrow source-configuration lineage audit.

The audit is limited to read-only inspection of the EXTRACT03P contract and
existing QSB artifacts. It records field, join-key, role/order, and crosswalk
coverage for the six partial topics without Source-ID audit, model recompute,
vector export, upstream mutation, live registry/DWH mutation, or claim upgrade.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT = REPO_ROOT / "runs/QSB-EXTRACT03P/narrow_source_configuration_lineage_audit_contract"
OUT_DIR = REPO_ROOT / "runs/QSB-EXTRACT03P-R1/narrow_real_data_source_configuration_lineage_audit"
O_RG = REPO_ROOT / "runs/QSB-EXTRACT03O-RG/registry_boundary_update_snapshot"
N_R1 = REPO_ROOT / "runs/QSB-EXTRACT03N-R1/authorized_narrow_source_response_degeneracy_lineage_audit_run"
H_R1 = REPO_ROOT / "runs/QSB-EXTRACT03H-R1/authorized_response_vector_export"
A_R1 = REPO_ROOT / "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum"
I_RUN = REPO_ROOT / "runs/QSB-EXTRACT03I/response_vector_identity_k_alignment_review"
J_RUN = REPO_ROOT / "runs/QSB-EXTRACT03J/near_alignment_structure_review"
K_R1 = REPO_ROOT / "runs/QSB-EXTRACT03K-R1/authorized_collinearity_control_run"
K_R2 = REPO_ROOT / "runs/QSB-EXTRACT03K-R2/human_review_collinearity_control_classifications"
M_RG = REPO_ROOT / "runs/QSB-EXTRACT03M-RG/registry_dwh_integration_snapshot"

STATUS = "extract03p_r1_source_configuration_lineage_audit_completed_partial_with_review_items_and_field_gaps"
CLAIM_BOUNDARY = (
    "EXTRACT03P-R1 is a narrow real-data Source-Configuration Lineage Audit "
    "over six previously localized partial topics. It records pipeline-review "
    "field/key/role/crosswalk coverage only. It does not establish "
    "Source-Configuration Lineage, establish Source-Response-Degeneracy, repair "
    "L2, authorize public claims, or make nature, Interface, geometry, or "
    "gravity claims."
)
NEXT_ALLOWED_ACTION = (
    "Human review of P-R1 field gaps and review items; if work continues, prepare "
    "a separate Source-ID/source-record contract without recompute or claim upgrade."
)

ARTIFACTS = [
    "01_extract03p_r1_run_manifest.json",
    "02_authorization_used.json",
    "03_contract_import_review.csv",
    "04_upstream_inventory_and_hashes.csv",
    "05_required_input_resolution.csv",
    "06_stop_criteria_review.csv",
    "07_partial_topic_scope.csv",
    "08_pq_execution_matrix.csv",
    "09_source_configuration_field_observation_matrix.csv",
    "10_lineage_join_key_coverage_matrix.csv",
    "11_pair_role_order_symmetry_audit.csv",
    "12_source_pair_configuration_crosswalk.csv",
    "13_identity_group_source_configuration_mapping.csv",
    "14_near_alignment_source_configuration_mapping.csv",
    "15_component_bridge_source_configuration_mapping.csv",
    "16_negative_control_relevance_audit.csv",
    "17_source_id_boundary_review.csv",
    "18_descriptive_metrics.csv",
    "19_partial_topic_classification_results.csv",
    "20_matrix_results_summary.csv",
    "21_blockers_and_review_items.csv",
    "22_no_execution_guard_results.csv",
    "23_l2_boundary_check.csv",
    "24_claim_boundary_matrix.csv",
    "25_validation_results.csv",
    "26_recommended_next_step.md",
    "27_human_readable_audit_report_de.md",
    "28_publication_safe_note_candidates.md",
    "29_short_result_note_de.md",
    "30_machine_readable_summary.json",
    "31_claim_boundary_grep_report.csv",
    "32_readonly_sqlite_integrity_checks.csv",
    "33_artifact_manifest.csv",
    "FINAL_RESULT_NOTE.md",
]

INPUT_PATHS = {
    "O_RG_boundary_snapshot_sqlite": O_RG / "30_boundary_registry_snapshot.sqlite",
    "O_RG_partial_lineage_topic_registry": O_RG / "09_partial_lineage_topic_registry.csv",
    "O_source_configuration_readiness": CONTRACT / "28_source_configuration_readiness_import.csv",
    "O_source_id_readiness": CONTRACT / "29_source_id_readiness_import.csv",
    "N_R1_degeneracy_lineage_classification_matrix": N_R1 / "28_degeneracy_lineage_classification_matrix.csv",
    "N_R1_lineage_join_key_audit": N_R1 / "17_lineage_join_key_audit.csv",
    "N_R1_source_pair_configuration_field_audit": N_R1 / "18_source_pair_configuration_field_audit.csv",
    "N_R1_pair_role_lineage_audit": N_R1 / "19_pair_role_lineage_audit.csv",
    "N_R1_near_alignment_lineage_matrix": N_R1 / "23_near_alignment_lineage_matrix.csv",
    "N_R1_component_bridge_lineage_matrix": N_R1 / "24_component_bridge_lineage_matrix.csv",
    "N_R1_negative_control_crosswalk": N_R1 / "25_negative_control_crosswalk.csv",
    "M_RG_registry_snapshot_sqlite": M_RG / "30_registry_snapshot.sqlite",
    "I_identity_component_mapping": I_RUN / "18_identity_to_component_explanation_matrix.csv",
    "J_near_alignment_items": J_RUN / "04_near_alignment_item_import.csv",
    "K_R1_control_classification_matrix": K_R1 / "18_hypothesis_classification_matrix.csv",
    "K_R2_decision_matrix": K_R2 / "13_decision_points_for_human_review.csv",
    "H_R1_full_response_vectors": H_R1 / "09_response_vector_export.csv",
    "H_R1_vector_hashes": H_R1 / "10_response_vector_hashes.csv",
    "H_R1_sign_normalized_groups": H_R1 / "11_sign_normalized_vector_signatures.csv",
    "A_R1_pair_split_assignments_readonly": A_R1 / "08_canonical_pair_split_assignment.csv",
    "A_R1_K_matrix_readonly": A_R1 / "11_K_candidate_matrix.csv",
    "source_response_code_path": REPO_ROOT / "scripts/qsb_extract03h_r1",
    "source_response_config_manifest": N_R1 / "21_normalization_sign_index_serialization_audit.csv",
    "response_vector_generation_hook": N_R1 / "20_response_generation_hook_audit.csv",
    "normalization_rule": N_R1 / "21_normalization_sign_index_serialization_audit.csv",
    "sign_anchor_rule": N_R1 / "21_normalization_sign_index_serialization_audit.csv",
    "index_convention": N_R1 / "21_normalization_sign_index_serialization_audit.csv",
    "serialization_hash_rule": N_R1 / "21_normalization_sign_index_serialization_audit.csv",
    "pair_id_role_convention": N_R1 / "19_pair_role_lineage_audit.csv",
    "source_pair_configuration_fields": N_R1 / "18_source_pair_configuration_field_audit.csv",
    "lineage_join_keys": N_R1 / "17_lineage_join_key_audit.csv",
}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def csv_header(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8") as f:
        return next(csv.reader(f))


def csv_count(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        return sum(1 for _ in reader)


def write_csv(name: str, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with (OUT_DIR / name).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_json(name: str, obj: object) -> None:
    (OUT_DIR / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_md(name: str, text: str) -> None:
    (OUT_DIR / name).write_text(text.strip() + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    if not path.is_file():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def sqlite_integrity(path: Path) -> str:
    if not path.is_file():
        return "missing"
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        return con.execute("PRAGMA integrity_check").fetchone()[0]
    finally:
        con.close()


def refuse_overwrite() -> None:
    if OUT_DIR.exists() and any(OUT_DIR.iterdir()):
        raise SystemExit(f"Refusing to overwrite non-empty output directory: {OUT_DIR}")


def observed_sources_for_field(field: str, headers: dict[str, set[str]]) -> list[str]:
    direct = []
    aliases = {
        "source_id": {"source_id"},
        "pair_id": {"pair_id", "canonical_pair_id", "row_pair_id", "column_pair_id", "pair_i", "pair_j"},
        "role_a": {"role_a", "pair_i"},
        "role_b": {"role_b", "pair_j"},
        "split_id": {"split_id", "split_protocol_id", "split_label"},
        "response_vector_id": {"response_vector_id", "pair_id", "pair_index"},
        "configuration_manifest_id": {"configuration_manifest_id", "lineage_bundle_sha256", "split_protocol_id"},
        "normalization_rule_id": {"normalization_rule_id", "normalization_rule", "rule"},
        "sign_anchor_rule_id": {"sign_anchor_rule_id", "sign_anchor_rule", "orientation_anchor_index", "orientation_sign", "rule"},
        "serialization_rule_id": {"serialization_rule_id", "serialization_hash_rule", "hash_precision_rule", "rule"},
    }
    for source_name, source_headers in headers.items():
        if field in source_headers:
            direct.append(f"{source_name}:direct")
        elif aliases.get(field, set()) & source_headers:
            direct.append(f"{source_name}:alias")
    return direct


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    refuse_overwrite()

    created_at = datetime.now(timezone.utc).isoformat()
    partial_topics = read_csv(CONTRACT / "05_partial_lineage_topic_localization.csv")
    pq_rows = read_csv(CONTRACT / "06_source_configuration_audit_question_registry.csv")
    required_inputs = read_csv(CONTRACT / "07_required_p_r1_inputs.csv")
    stop_rows = read_csv(CONTRACT / "10_p_r1_stop_criteria.csv")
    field_requirements = read_csv(CONTRACT / "11_source_configuration_field_requirements.csv")
    join_key_requirements = read_csv(CONTRACT / "12_lineage_join_key_requirements.csv")
    n_r1_class = read_csv(N_R1 / "28_degeneracy_lineage_classification_matrix.csv")
    identity_rows = read_csv(N_R1 / "22_identity_group_lineage_matrix.csv")
    near_rows = read_csv(N_R1 / "23_near_alignment_lineage_matrix.csv")
    bridge_rows = read_csv(N_R1 / "24_component_bridge_lineage_matrix.csv")
    negative_rows = read_csv(N_R1 / "25_negative_control_crosswalk.csv")

    headers = {
        "A_R1_pair_split": set(csv_header(A_R1 / "08_canonical_pair_split_assignment.csv")),
        "A_R1_K_matrix": set(csv_header(A_R1 / "11_K_candidate_matrix.csv")),
        "H_R1_vectors": set(csv_header(H_R1 / "09_response_vector_export.csv")),
        "H_R1_hashes": set(csv_header(H_R1 / "10_response_vector_hashes.csv")),
        "H_R1_signatures": set(csv_header(H_R1 / "11_sign_normalized_vector_signatures.csv")),
        "H_R1_identity_groups": set(csv_header(H_R1 / "12_vector_identity_groups.csv")),
        "N_R1_identity": set(csv_header(N_R1 / "22_identity_group_lineage_matrix.csv")),
        "N_R1_near_alignment": set(csv_header(N_R1 / "23_near_alignment_lineage_matrix.csv")),
        "N_R1_component_bridge": set(csv_header(N_R1 / "24_component_bridge_lineage_matrix.csv")),
        "N_R1_negative_control": set(csv_header(N_R1 / "25_negative_control_crosswalk.csv")),
        "N_R1_rules": set(csv_header(N_R1 / "21_normalization_sign_index_serialization_audit.csv")),
    }

    input_resolution = []
    for row in required_inputs:
        name = row["input_name"]
        if name == "source_configuration_audit_authorization":
            status = "authorized_by_human_for_p_r1"
            path = "chat_authorization_current_turn"
        else:
            path_obj = INPUT_PATHS.get(name)
            status = "available_readonly" if path_obj and path_obj.exists() else "missing"
            path = rel(path_obj) if path_obj else row["evidence_or_source"]
        input_resolution.append(
            {
                "input_id": row["input_id"],
                "input_name": name,
                "contract_status": row["current_status"],
                "p_r1_status": status,
                "evidence_or_source": path,
                "blocking_if_missing": row["blocking_if_missing"],
                "notes": "Human authorization accepted for P-R1 execution only." if name == "source_configuration_audit_authorization" else "Read-only input resolved.",
            }
        )

    missing_inputs = [row for row in input_resolution if row["p_r1_status"] == "missing"]
    localized_topics_ok = len(partial_topics) == 6
    run_level_stop_triggered = bool(missing_inputs) or not localized_topics_ok

    field_rows = []
    field_gap_count = 0
    for row in field_requirements:
        observed = observed_sources_for_field(row["field_name"], headers)
        direct = [item for item in observed if item.endswith(":direct")]
        alias = [item for item in observed if item.endswith(":alias")]
        if direct:
            status = "direct_field_observed"
        elif alias:
            status = "alias_or_contract_artifact_observed"
            field_gap_count += 1
        else:
            status = "not_observed_in_readonly_artifacts"
            field_gap_count += 1
        field_rows.append(
            {
                "field_id": row["field_id"],
                "field_name": row["field_name"],
                "required_for_p_r1": row["required_for_p_r1"],
                "contract_observation_status": row["n_r1_observation_status"],
                "p_r1_observation_status": status,
                "observed_sources": ";".join(observed),
                "gap_or_limitation": "" if status == "direct_field_observed" else "Direct source-configuration field remains unresolved in allowed read-only scope.",
                "classification_effect": "supports_pipeline_review_pattern" if status == "direct_field_observed" else "partial_with_review_item",
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )

    join_rows = []
    key_gap_count = 0
    for row in join_key_requirements:
        key = row["join_key"]
        observed = []
        aliases = {
            "pair_id": {"pair_id", "canonical_pair_id", "row_pair_id", "column_pair_id", "pair_i", "pair_j"},
            "source_id": {"source_id"},
            "response_vector_id": {"response_vector_id", "pair_id", "pair_index"},
            "identity_group_id": {"identity_group_id", "identity_group_i", "identity_group_j"},
            "component_id": {"component_id"},
            "near_alignment_item_id": {"near_alignment_item_id", "review_id"},
            "artifact_sha256": {"artifact_sha256", "sha256", "lineage_bundle_sha256", "raw_vector_sha256", "rounded_vector_sha256", "sign_normalized_sha256"},
        }
        for source_name, source_headers in headers.items():
            if key in source_headers:
                observed.append(f"{source_name}:direct")
            elif aliases[key] & source_headers:
                observed.append(f"{source_name}:alias")
        if any(item.endswith(":direct") for item in observed):
            status = "direct_key_observed"
        elif observed:
            status = "alias_or_artifact_key_observed"
            if key == "source_id":
                key_gap_count += 1
        else:
            status = "not_observed"
            key_gap_count += 1
        join_rows.append(
            {
                "key_id": row["key_id"],
                "join_key": key,
                "purpose": row["purpose"],
                "p_r1_coverage_status": status,
                "observed_sources": ";".join(observed),
                "gap_or_limitation": "source_id is not directly observed; Source-ID audit remains forbidden in this run." if key == "source_id" and status != "direct_key_observed" else "",
                "classification_effect": "partial_with_review_item" if key == "source_id" and status != "direct_key_observed" else "supports_pipeline_review_pattern",
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )

    topic_class = []
    classifications = {
        "source_response_degeneracy": "source_configuration_lineage_partially_supported_with_review_items",
        "source_configuration_traceability": "source_configuration_lineage_partially_supported_with_review_items",
        "pair_role_lineage": "source_configuration_lineage_partially_supported_with_review_items",
        "component_bridge_lineage": "source_configuration_lineage_partially_supported_with_review_items",
        "negative_control_lineage": "source_configuration_lineage_partially_supported_with_review_items",
        "lineage_join_keys": "source_configuration_lineage_partially_supported_with_review_items",
    }
    for topic in partial_topics:
        lineage_topic = topic["lineage_topic"]
        evidence = {
            "source_response_degeneracy": "Existing pair/vector/component/identity/near-alignment rows are crosswalkable read-only, but direct source-level cause is not resolved.",
            "source_configuration_traceability": f"{len(field_rows)} required fields reviewed; direct/alias coverage is visible, with unresolved direct-field gaps.",
            "pair_role_lineage": "pair_id, pair_i, pair_j, canonical_pair_id and role-order artifacts are visible; role_a/role_b field names are not direct.",
            "component_bridge_lineage": f"{len(bridge_rows)} component bridge rows imported read-only; no bridge or cluster recompute.",
            "negative_control_lineage": f"{len(negative_rows)} K-R1/K-R2 crosswalk rows imported read-only; controls were not rerun.",
            "lineage_join_keys": f"{len(join_rows)} join keys reviewed; source_id remains not directly observed in allowed artifacts.",
        }[lineage_topic]
        topic_class.append(
            {
                "topic_id": topic["localization_id"],
                "lineage_topic": lineage_topic,
                "p_r1_classification": classifications[lineage_topic],
                "evidence_summary": evidence,
                "unresolved_limitation": topic["limitations"],
                "resolved_by_p_r1": "no",
                "review_item_required": "yes",
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )

    component_counts = Counter(row["component_id"] for row in near_rows if row.get("component_id"))
    identity_summary_rows = [
        {
            "mapping_id": f"IG-SC-{i:02d}",
            "component_id": row["component_id"],
            "identity_group_id": row["identity_group_id"],
            "member_count": row["member_count"],
            "member_pair_ids": row["member_pair_ids"],
            "source_configuration_join_basis": "pair_id;component_id;identity_group_id",
            "coverage_status": "crosswalk_visible_readonly",
            "claim_boundary": CLAIM_BOUNDARY,
        }
        for i, row in enumerate(identity_rows, 1)
    ]
    near_summary_rows = [
        {
            "component_id": component_id,
            "near_alignment_rows": count,
            "source_configuration_join_basis": "pair_i;pair_j;component_id;identity_group_i;identity_group_j",
            "coverage_status": "crosswalk_visible_readonly",
            "forbidden_operation_guard": "no near-alignment rerun or edge rethresholding",
            "claim_boundary": CLAIM_BOUNDARY,
        }
        for component_id, count in sorted(component_counts.items())
    ]

    write_json(
        "01_extract03p_r1_run_manifest.json",
        {
            "work_package": "QSB-EXTRACT03P-R1",
            "status": STATUS,
            "created_at_utc": created_at,
            "repo_root": str(REPO_ROOT),
            "source_contract": rel(CONTRACT),
            "authorization_status": "authorized_by_human_for_p_r1",
            "partial_topics_count": len(partial_topics),
            "pq_questions_count": len(pq_rows),
            "required_inputs_total": len(input_resolution),
            "required_inputs_resolved": len(input_resolution) - len(missing_inputs),
            "required_inputs_missing": len(missing_inputs),
            "field_requirements_total": len(field_rows),
            "field_requirements_with_direct_or_alias_coverage": sum(1 for row in field_rows if row["p_r1_observation_status"] != "not_observed_in_readonly_artifacts"),
            "field_requirements_with_direct_field_gaps": field_gap_count,
            "join_keys_total": len(join_rows),
            "join_keys_with_direct_or_alias_coverage": sum(1 for row in join_rows if row["p_r1_coverage_status"] != "not_observed"),
            "join_keys_with_gaps": key_gap_count,
            "run_level_stop_triggered": run_level_stop_triggered,
            "source_id_audit_run_executed": False,
            "source_response_audit_rerun": False,
            "controls_rerun": False,
            "vectors_exported": False,
            "vectors_mutated": False,
            "K_recomputed": False,
            "strength_recomputed": False,
            "d_recomputed": False,
            "D_recomputed": False,
            "edge_recomputed": False,
            "shortest_path_rerun": False,
            "edge_rethresholding": False,
            "cluster_rerun": False,
            "motif_rerun": False,
            "bootstrap_run": False,
            "raw_phase_reconstruction": False,
            "F3_raw_source_opened": False,
            "A_R1_pipeline_rerun": False,
            "upstream_modified": False,
            "live_dwh_modified": False,
            "l2_fail_changed": False,
            "post_hoc_tuning_performed": False,
            "nature_claim_made": False,
            "interface_claim_made": False,
            "geometry_claim_made": False,
            "gravity_claim_made": False,
            "public_claim_authorized": False,
            "claim_boundary": CLAIM_BOUNDARY,
            "next_allowed_action": NEXT_ALLOWED_ACTION,
        },
    )
    write_json(
        "02_authorization_used.json",
        {
            "authorization_status": "authorized_by_human_for_p_r1",
            "authorized_work_package": "QSB-EXTRACT03P-R1_NARROW_SOURCE_CONFIGURATION_LINEAGE_AUDIT_RUN",
            "source_contract": rel(CONTRACT),
            "scope": [row["lineage_topic"] for row in partial_topics],
            "source_configuration_audit_authorization": "authorized_by_human_for_p_r1",
            "no_source_id_audit": True,
            "no_recompute_or_mutation": True,
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )

    write_csv(
        "03_contract_import_review.csv",
        ["contract_artifact", "exists", "sha256", "readonly_import", "notes"],
        [
            {"contract_artifact": rel(CONTRACT / name), "exists": (CONTRACT / name).exists(), "sha256": sha256(CONTRACT / name), "readonly_import": "yes", "notes": "Imported from EXTRACT03P contract."}
            for name in [
                "05_partial_lineage_topic_localization.csv",
                "06_source_configuration_audit_question_registry.csv",
                "07_required_p_r1_inputs.csv",
                "10_p_r1_stop_criteria.csv",
                "11_source_configuration_field_requirements.csv",
                "12_lineage_join_key_requirements.csv",
                "13_pair_role_and_order_contract.csv",
            ]
        ],
    )
    inventory_rows = [
        {"upstream_id": f"UP-{i:02d}", "input_name": name, "path": rel(path), "exists": path.exists(), "sha256": sha256(path), "readonly_use": "yes"}
        for i, (name, path) in enumerate(INPUT_PATHS.items(), 1)
    ]
    write_csv("04_upstream_inventory_and_hashes.csv", list(inventory_rows[0].keys()), inventory_rows)
    write_csv("05_required_input_resolution.csv", list(input_resolution[0].keys()), input_resolution)
    write_csv(
        "06_stop_criteria_review.csv",
        ["stop_id", "criterion", "triggered", "evidence", "action_taken"],
        [
            {
                "stop_id": row["stop_id"],
                "criterion": row["criterion"],
                "triggered": "yes" if run_level_stop_triggered and row["stop_id"] in {"STOP-01", "STOP-02", "STOP-03", "STOP-04", "STOP-05", "STOP-06", "STOP-10"} else "no",
                "evidence": "All run-level required inputs/scope guards resolved; field-level gaps recorded as review items." if not run_level_stop_triggered else "Missing run-level prerequisite.",
                "action_taken": "continued within scope" if not run_level_stop_triggered else "blocked",
            }
            for row in stop_rows
        ],
    )
    write_csv("07_partial_topic_scope.csv", list(partial_topics[0].keys()), partial_topics)
    write_csv(
        "08_pq_execution_matrix.csv",
        ["question_id", "executed_in_p_r1", "result_artifact", "classification_boundary", "notes"],
        [
            {"question_id": row["question_id"], "executed_in_p_r1": "yes_readonly", "result_artifact": {
                "PQ01_partial_topic_localization": "07_partial_topic_scope.csv",
                "PQ02_source_configuration_field_inventory": "09_source_configuration_field_observation_matrix.csv",
                "PQ03_lineage_join_key_sufficiency": "10_lineage_join_key_coverage_matrix.csv",
                "PQ04_pair_role_and_order_scope": "11_pair_role_order_symmetry_audit.csv",
                "PQ05_identity_group_source_configuration_mapping": "13_identity_group_source_configuration_mapping.csv",
                "PQ06_near_alignment_source_configuration_mapping": "14_near_alignment_source_configuration_mapping.csv",
                "PQ07_component_bridge_source_configuration_mapping": "15_component_bridge_source_configuration_mapping.csv",
                "PQ08_negative_control_relevance": "16_negative_control_relevance_audit.csv",
                "PQ09_source_id_boundary": "17_source_id_boundary_review.csv",
                "PQ10_stop_and_claim_boundary": "06_stop_criteria_review.csv;24_claim_boundary_matrix.csv",
            }[row["question_id"]], "classification_boundary": row["classification_boundary"], "notes": "No forbidden operation used."}
            for row in pq_rows
        ],
    )
    write_csv("09_source_configuration_field_observation_matrix.csv", list(field_rows[0].keys()), field_rows)
    write_csv("10_lineage_join_key_coverage_matrix.csv", list(join_rows[0].keys()), join_rows)
    write_csv(
        "11_pair_role_order_symmetry_audit.csv",
        ["audit_id", "pair_id_fields_seen", "role_order_basis", "symmetry_basis", "row_count_a_r1_pairs", "row_count_h_r1_vectors", "classification", "limitations", "claim_boundary"],
        [
            {
                "audit_id": "P-R1-PAIR-01",
                "pair_id_fields_seen": "canonical_pair_id;pair_id;pair_i;pair_j",
                "role_order_basis": "A-R1 pair_i/pair_j and canonical_pair_id read-only",
                "symmetry_basis": "N-R1 pair role lineage and H-R1 orientation/signature artifacts read-only",
                "row_count_a_r1_pairs": csv_count(A_R1 / "08_canonical_pair_split_assignment.csv"),
                "row_count_h_r1_vectors": csv_count(H_R1 / "09_response_vector_export.csv"),
                "classification": "source_configuration_lineage_partially_supported_with_review_items",
                "limitations": "role_a/role_b names are not direct fields; no relabeling or role-swap rerun performed.",
                "claim_boundary": CLAIM_BOUNDARY,
            }
        ],
    )
    write_csv(
        "12_source_pair_configuration_crosswalk.csv",
        ["crosswalk_id", "source_layer", "field_or_key_basis", "rows_seen", "coverage_status", "limitations", "claim_boundary"],
        [
            {"crosswalk_id": "SPC-01", "source_layer": "A-R1 pair split", "field_or_key_basis": "canonical_pair_id;pair_i;pair_j;split_protocol_id;split_label;lineage_bundle_sha256", "rows_seen": csv_count(A_R1 / "08_canonical_pair_split_assignment.csv"), "coverage_status": "read_only_crosswalk_visible", "limitations": "source_id not present.", "claim_boundary": CLAIM_BOUNDARY},
            {"crosswalk_id": "SPC-02", "source_layer": "H-R1 vector export", "field_or_key_basis": "pair_id;pair_i;pair_j;split_label;component_id;pair_index", "rows_seen": csv_count(H_R1 / "09_response_vector_export.csv"), "coverage_status": "read_only_crosswalk_visible", "limitations": "response_vector_id is represented by pair_id/pair_index, not direct response_vector_id field.", "claim_boundary": CLAIM_BOUNDARY},
            {"crosswalk_id": "SPC-03", "source_layer": "N-R1 rule audit", "field_or_key_basis": "rule;source;seen;classification", "rows_seen": csv_count(N_R1 / "21_normalization_sign_index_serialization_audit.csv"), "coverage_status": "read_only_rule_artifacts_visible", "limitations": "rule ids are not direct *_rule_id fields.", "claim_boundary": CLAIM_BOUNDARY},
        ],
    )
    write_csv("13_identity_group_source_configuration_mapping.csv", list(identity_summary_rows[0].keys()), identity_summary_rows)
    write_csv("14_near_alignment_source_configuration_mapping.csv", list(near_summary_rows[0].keys()), near_summary_rows)
    write_csv(
        "15_component_bridge_source_configuration_mapping.csv",
        ["component_id", "near_alignment_items", "identity_groups_seen", "coverage_status", "classification", "limitations", "claim_boundary"],
        [
            {"component_id": row["component_id"], "near_alignment_items": row["near_alignment_items"], "identity_groups_seen": row["identity_groups_seen"], "coverage_status": "read_only_bridge_visible", "classification": "source_configuration_lineage_partially_supported_with_review_items", "limitations": "Bridge remains descriptive; no component or cluster recompute.", "claim_boundary": CLAIM_BOUNDARY}
            for row in bridge_rows
        ],
    )
    neg_counts = Counter(row["source"] for row in negative_rows)
    write_csv(
        "16_negative_control_relevance_audit.csv",
        ["source", "rows_seen", "coverage_status", "allowed_interpretation", "forbidden_interpretation", "claim_boundary"],
        [
            {"source": source, "rows_seen": count, "coverage_status": "read_only_control_context_visible", "allowed_interpretation": "Controls bound interpretation of P-R1 findings.", "forbidden_interpretation": "No natural/artifact-origin decision; no control rerun.", "claim_boundary": CLAIM_BOUNDARY}
            for source, count in sorted(neg_counts.items())
        ],
    )
    write_csv(
        "17_source_id_boundary_review.csv",
        ["boundary_id", "source_id_directly_observed", "source_id_audit_executed", "p_r1_effect", "future_boundary", "claim_boundary"],
        [
            {"boundary_id": "SID-P-R1-01", "source_id_directly_observed": "no", "source_id_audit_executed": "false", "p_r1_effect": "lineage_join_keys and source_configuration_traceability remain partial with review items", "future_boundary": "separate Source-ID/source-record contract required if pursued", "claim_boundary": CLAIM_BOUNDARY}
        ],
    )
    write_csv(
        "18_descriptive_metrics.csv",
        ["metric_id", "metric", "value", "source", "notes"],
        [
            {"metric_id": "M01", "metric": "partial_topics_in_scope", "value": len(partial_topics), "source": "07_partial_topic_scope.csv", "notes": "Six-topic scope retained."},
            {"metric_id": "M02", "metric": "pq_questions_executed_readonly", "value": len(pq_rows), "source": "08_pq_execution_matrix.csv", "notes": "PQ01-PQ10."},
            {"metric_id": "M03", "metric": "field_requirements_total", "value": len(field_rows), "source": "09_source_configuration_field_observation_matrix.csv", "notes": "Contract fields."},
            {"metric_id": "M04", "metric": "field_requirements_with_direct_field_gaps", "value": field_gap_count, "source": "09_source_configuration_field_observation_matrix.csv", "notes": "Direct field gaps remain."},
            {"metric_id": "M05", "metric": "join_keys_total", "value": len(join_rows), "source": "10_lineage_join_key_coverage_matrix.csv", "notes": "Contract join keys."},
            {"metric_id": "M06", "metric": "join_keys_with_gaps", "value": key_gap_count, "source": "10_lineage_join_key_coverage_matrix.csv", "notes": "source_id gap remains."},
            {"metric_id": "M07", "metric": "identity_group_rows", "value": len(identity_rows), "source": "13_identity_group_source_configuration_mapping.csv", "notes": "Read-only."},
            {"metric_id": "M08", "metric": "near_alignment_rows", "value": len(near_rows), "source": "14_near_alignment_source_configuration_mapping.csv", "notes": "Read-only input rows summarized by component."},
            {"metric_id": "M09", "metric": "component_bridge_rows", "value": len(bridge_rows), "source": "15_component_bridge_source_configuration_mapping.csv", "notes": "Read-only."},
            {"metric_id": "M10", "metric": "negative_control_rows", "value": len(negative_rows), "source": "16_negative_control_relevance_audit.csv", "notes": "Read-only."},
        ],
    )
    write_csv("19_partial_topic_classification_results.csv", list(topic_class[0].keys()), topic_class)
    summary_rows = [
        {"matrix": "field_observation", "rows": len(field_rows), "supporting_rows": sum(1 for row in field_rows if row["classification_effect"] == "supports_pipeline_review_pattern"), "partial_or_review_rows": sum(1 for row in field_rows if row["classification_effect"] != "supports_pipeline_review_pattern"), "classification": "partial_with_review_items"},
        {"matrix": "join_key_coverage", "rows": len(join_rows), "supporting_rows": sum(1 for row in join_rows if row["classification_effect"] == "supports_pipeline_review_pattern"), "partial_or_review_rows": sum(1 for row in join_rows if row["classification_effect"] != "supports_pipeline_review_pattern"), "classification": "partial_with_review_items"},
        {"matrix": "partial_topic_results", "rows": len(topic_class), "supporting_rows": 0, "partial_or_review_rows": len(topic_class), "classification": "partial_with_review_items"},
    ]
    write_csv("20_matrix_results_summary.csv", list(summary_rows[0].keys()), summary_rows)
    review_items = [
        {"review_item_id": "P-R1-RI-01", "topic": "source_configuration_traceability", "severity": "unresolved_field_gap", "description": "Direct source_id and several direct rule/role/split id fields remain absent in allowed read-only artifacts.", "stop_triggered": "no_run_level_stop", "required_action": "Human review; do not widen scope inside P-R1.", "claim_boundary": CLAIM_BOUNDARY},
        {"review_item_id": "P-R1-RI-02", "topic": "lineage_join_keys", "severity": "source_id_key_gap", "description": "source_id join key is contract-required but not directly observed.", "stop_triggered": "no_run_level_stop", "required_action": "Separate Source-ID/source-record contract if pursued.", "claim_boundary": CLAIM_BOUNDARY},
        {"review_item_id": "P-R1-RI-03", "topic": "pair_role_lineage", "severity": "role_alias_boundary", "description": "pair_i/pair_j provide role/order basis, but role_a/role_b are not direct fields.", "stop_triggered": "no_run_level_stop", "required_action": "Keep role lineage partial; no relabeling.", "claim_boundary": CLAIM_BOUNDARY},
    ]
    write_csv("21_blockers_and_review_items.csv", list(review_items[0].keys()), review_items)
    guards = [
        "no_source_id_audit",
        "no_source_response_audit_rerun",
        "no_controls_rerun",
        "no_vector_export_or_mutation",
        "no_K_strength_d_D_edge_recompute",
        "no_shortest_path_rerun",
        "no_edge_rethresholding",
        "no_cluster_motif_bootstrap_run",
        "no_raw_phase_reconstruction",
        "no_F3_raw_data_access_beyond_allowed_artifacts",
        "no_A_R1_rerun",
        "no_upstream_mutation",
        "no_live_dwh_or_registry_mutation",
        "no_L2_change",
        "no_post_hoc_tuning",
        "no_nature_interface_geometry_gravity_claim",
        "no_public_claim_upgrade",
    ]
    write_csv(
        "22_no_execution_guard_results.csv",
        ["guard_id", "guard", "passed", "evidence", "notes"],
        [{"guard_id": f"GUARD-{i:02d}", "guard": guard, "passed": "yes", "evidence": "P-R1 read-only audit generation", "notes": "No forbidden operation executed."} for i, guard in enumerate(guards, 1)],
    )
    write_csv(
        "23_l2_boundary_check.csv",
        ["boundary_id", "l2_result", "n4_support", "theta_new", "epsilon_new", "changed_by_p_r1", "claim_boundary"],
        [{"boundary_id": "L2-P-R1-01", "l2_result": "fail", "n4_support": "0/3 required 2/3", "theta_new": "0.012446436850524916", "epsilon_new": "0.006009422749372488", "changed_by_p_r1": "false", "claim_boundary": "L2 remains unchanged and not repaired."}],
    )
    claim_rows = [
        {"boundary_id": "CB-P-R1-ALLOW-01", "statement": "P-R1 records narrow read-only source-configuration field/key/role/crosswalk coverage.", "status": "allowed"},
        {"boundary_id": "CB-P-R1-FORBID-01", "statement": "P-R1 establishes Source-Configuration Lineage.", "status": "forbidden"},
        {"boundary_id": "CB-P-R1-FORBID-02", "statement": "P-R1 establishes Source-Response-Degeneracy.", "status": "forbidden"},
        {"boundary_id": "CB-P-R1-FORBID-03", "statement": "P-R1 repairs L2.", "status": "forbidden"},
        {"boundary_id": "CB-P-R1-FORBID-04", "statement": "P-R1 authorizes public claims.", "status": "forbidden"},
    ]
    write_csv("24_claim_boundary_matrix.csv", list(claim_rows[0].keys()), claim_rows)
    validations = [
        ("VAL-01", "artifact_count_34", "pending", ""),
        ("VAL-02", "authorization_resolved", "true", "authorized_by_human_for_p_r1"),
        ("VAL-03", "six_partial_topics_retained", str(len(partial_topics) == 6).lower(), str(len(partial_topics))),
        ("VAL-04", "pq01_pq10_executed_readonly", str(len(pq_rows) == 10).lower(), str(len(pq_rows))),
        ("VAL-05", "required_inputs_resolved", str(len(missing_inputs) == 0).lower(), str(len(missing_inputs))),
        ("VAL-06", "run_level_stop_not_triggered", str(not run_level_stop_triggered).lower(), str(run_level_stop_triggered)),
        ("VAL-07", "guards_recorded", "true", "22_no_execution_guard_results.csv"),
        ("VAL-08", "l2_unchanged", "true", "23_l2_boundary_check.csv"),
    ]
    write_csv("25_validation_results.csv", ["validation_id", "check", "passed", "evidence"], [{"validation_id": a, "check": b, "passed": c, "evidence": d} for a, b, c, d in validations])
    write_md("26_recommended_next_step.md", f"# Recommended Next Step\n\n{NEXT_ALLOWED_ACTION}\n")
    topics_md = "\n".join(f"- {row['lineage_topic']}: {row['p_r1_classification']}; {row['evidence_summary']}" for row in topic_class)
    write_md(
        "27_human_readable_audit_report_de.md",
        f"""# QSB-EXTRACT03P-R1 Source-Configuration Lineage Audit

## Status
{STATUS}

## Befund
P-R1 hat die sechs partial Topics read-only gegen Source-/Pair-Konfigurationsfelder, Join Keys, Pair-Rollen, Reihenfolgen und bestehende Crosswalks geprueft.

{topics_md}

## Interpretation
Die vorhandenen Artefakte tragen eine auditierbare Pipeline-Review-Struktur. Direkte Source-Konfigurationswerte bleiben jedoch teilweise nicht sichtbar.

## Hypothese
Eine spaetere, separat autorisierte Source-ID/source-record Pruefung koennte klaeren, ob die fehlenden direkten source_id/source-record Bindungen extern vorhanden sind.

## Offene Luecke
Direct source_id, role_a/role_b, split_id und mehrere rule-id Feldnamen sind nicht als direkte Felder in den erlaubten read-only Artefakten beobachtet.

## Claim Boundary
{CLAIM_BOUNDARY}

## L2 Boundary
L2 bleibt fail und unveraendert.
""",
    )
    write_md(
        "28_publication_safe_note_candidates.md",
        "# Publication-Safe Note Candidates\n\nInternal note only: P-R1 records a partial, review-item-bearing source-configuration audit matrix over six prior partial topics. No public claim upgrade is authorized.\n",
    )
    write_md(
        "29_short_result_note_de.md",
        f"# QSB-EXTRACT03P-R1 Short Result\n\nStatus: {STATUS}\n\nAlle sechs partial Topics bleiben nach P-R1 partial with review items. Die Matrixstruktur ist sichtbar; direkte Source-ID/source-record Bindungen bleiben ausserhalb dieses Runs.\n",
    )
    summary = {
        "work_package": "QSB-EXTRACT03P-R1",
        "status": STATUS,
        "artifact_count": 34,
        "partial_topics": [row["lineage_topic"] for row in partial_topics],
        "topic_classifications": {row["lineage_topic"]: row["p_r1_classification"] for row in topic_class},
        "resolved_topics": [],
        "unresolved_partial_topics": [row["lineage_topic"] for row in topic_class],
        "field_requirements_total": len(field_rows),
        "field_requirements_with_direct_field_gaps": field_gap_count,
        "join_keys_total": len(join_rows),
        "join_keys_with_gaps": key_gap_count,
        "run_level_stop_triggered": run_level_stop_triggered,
        "review_items_count": len(review_items),
        "claim_boundary": CLAIM_BOUNDARY,
        "next_allowed_action": NEXT_ALLOWED_ACTION,
    }
    write_json("30_machine_readable_summary.json", summary)

    grep_pattern = re.compile(
        r"proves|proof|demonstrates gravity|demonstrates emergent geometry|repairs L2|L2 repaired|physical evidence|confirms the Interface mechanism|establishes a physical mechanism|establishes Source-Configuration Lineage|establishes Source-Response-Degeneracy|public claim authorized|authorizes public claims",
        re.IGNORECASE,
    )
    grep_rows = []
    for path in sorted(OUT_DIR.iterdir()):
        if not path.is_file() or path.name == "31_claim_boundary_grep_report.csv":
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if grep_pattern.search(line):
                grep_rows.append(
                    {
                        "match_id": f"GREP-{len(grep_rows) + 1:02d}",
                        "file": rel(path),
                        "line": lineno,
                        "matched_text": line[:300],
                        "allowed_context": "forbidden_or_boundary_context",
                    }
                )
    if not grep_rows:
        grep_rows.append({"match_id": "GREP-00", "file": "", "line": "", "matched_text": "", "allowed_context": "no_matches"})
    write_csv("31_claim_boundary_grep_report.csv", list(grep_rows[0].keys()), grep_rows)
    sqlite_rows = [
        {"sqlite_id": "SQL-01", "path": rel(O_RG / "30_boundary_registry_snapshot.sqlite"), "integrity_check": sqlite_integrity(O_RG / "30_boundary_registry_snapshot.sqlite"), "mode": "read_only"},
        {"sqlite_id": "SQL-02", "path": rel(M_RG / "30_registry_snapshot.sqlite"), "integrity_check": sqlite_integrity(M_RG / "30_registry_snapshot.sqlite"), "mode": "read_only"},
    ]
    write_csv("32_readonly_sqlite_integrity_checks.csv", list(sqlite_rows[0].keys()), sqlite_rows)
    write_csv(
        "33_artifact_manifest.csv",
        ["artifact_name", "created", "notes"],
        [{"artifact_name": name, "created": "pending" if name == "33_artifact_manifest.csv" else "yes", "notes": "P-R1 output artifact"} for name in ARTIFACTS],
    )
    write_md(
        "FINAL_RESULT_NOTE.md",
        f"""# QSB-EXTRACT03P-R1 Final Result

## Status
{STATUS}

## Reviewed Inputs
EXTRACT03P contract artifacts and existing QSB upstream artifacts were read only. Human authorization resolved the EXTRACT03P authorization input gap for P-R1 execution only.

## Real-Data Source-Configuration Lineage Findings
The audit found visible read-only pipeline crosswalks for pair_id/pair_i/pair_j, split labels/protocols, response vector pair identifiers, identity groups, near-alignment rows, component bridge rows, and negative-control context. Direct source_id and several direct source-configuration/rule/role field names remain unresolved within the allowed artifact scope.

## Resolved and Unresolved Partial Topics
Resolved topics: none upgraded to supported. Unresolved partial topics: source_response_degeneracy, source_configuration_traceability, pair_role_lineage, component_bridge_lineage, negative_control_lineage, lineage_join_keys.

## Matrix Results
Field matrix: {len(field_rows)} rows with {field_gap_count} direct-field gaps. Join-key matrix: {len(join_rows)} rows with {key_gap_count} source-key gap. Topic matrix: six partial-with-review-items classifications.

## Blockers
No run-level stop criterion was triggered. Review-item blockers remain for direct source_id, direct role_a/role_b, direct source/rule ids, and Source-ID/source-record boundary.

## Stop Criteria
Stop criteria were reviewed. The audit did not widen scope; unresolved direct-field gaps were recorded instead of substituting data.

## Validation Checks
Validation artifacts record authorization, six-topic scope, PQ01-PQ10 execution, input resolution, no-execution guards, and unchanged L2 boundary.

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
    rows = read_csv(OUT_DIR / "25_validation_results.csv")
    rows[0]["passed"] = str(len(files) == len(ARTIFACTS)).lower()
    rows[0]["evidence"] = str(len(files))
    write_csv("25_validation_results.csv", list(rows[0].keys()), rows)
    artifact_rows = read_csv(OUT_DIR / "33_artifact_manifest.csv")
    for row in artifact_rows:
        row["created"] = "yes"
    write_csv("33_artifact_manifest.csv", list(artifact_rows[0].keys()), artifact_rows)


if __name__ == "__main__":
    main()
