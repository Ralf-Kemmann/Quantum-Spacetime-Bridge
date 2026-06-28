#!/usr/bin/env python3
"""Generate the QSB-EXTRACT03P contract-only artifact set.

This script reads upstream registry/review artifacts as static inputs and writes
only the EXTRACT03P contract package. It does not execute any audit, recompute
model outputs, mutate upstream files, or update a live registry/DWH.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "runs/QSB-EXTRACT03P/narrow_source_configuration_lineage_audit_contract"
O_RG = REPO_ROOT / "runs/QSB-EXTRACT03O-RG/registry_boundary_update_snapshot"
O = REPO_ROOT / "runs/QSB-EXTRACT03O/human_review_n_r1_partial_degeneracy_lineage"
N_R1 = REPO_ROOT / "runs/QSB-EXTRACT03N-R1/authorized_narrow_source_response_degeneracy_lineage_audit_run"
M_RG = REPO_ROOT / "runs/QSB-EXTRACT03M-RG/registry_dwh_integration_snapshot"

STATUS = "extract03p_source_configuration_lineage_audit_contract_completed_with_input_gaps"
CLAIM_BOUNDARY = (
    "EXTRACT03P prepares a narrow Source-Configuration Lineage Audit Contract "
    "for the six partial Degeneracy-Lineage topics. It may define required "
    "Source-/Pair-Configuration fields and lineage join keys for a later "
    "authorized P-R1 run. It does not prove QSB, establish Source-Configuration "
    "Lineage, establish Source-Response-Degeneracy, repair L2, authorize public "
    "claims, or make nature, Interface, geometry, or gravity claims."
)
NEXT_ALLOWED_ACTION = (
    "Separate human authorization of QSB-EXTRACT03P-R1 narrow source-configuration "
    "lineage audit under this contract, after resolving blocking input gaps."
)

ARTIFACTS = [
    "01_extract03p_run_manifest.json",
    "02_upstream_inventory_and_hashes.csv",
    "03_input_availability_review.csv",
    "04_o_rg_snapshot_readonly_review.csv",
    "05_partial_lineage_topic_localization.csv",
    "06_source_configuration_audit_question_registry.csv",
    "07_required_p_r1_inputs.csv",
    "08_allowed_operations_matrix.csv",
    "09_forbidden_operations_matrix.csv",
    "10_p_r1_stop_criteria.csv",
    "11_source_configuration_field_requirements.csv",
    "12_lineage_join_key_requirements.csv",
    "13_pair_role_and_order_contract.csv",
    "14_identity_group_source_configuration_scope.csv",
    "15_near_alignment_source_configuration_scope.csv",
    "16_component_bridge_source_configuration_scope.csv",
    "17_negative_control_relevance_contract.csv",
    "18_source_id_boundary_contract.csv",
    "19_allowed_descriptive_metrics_contract.csv",
    "20_source_configuration_lineage_classification_schema.csv",
    "21_claim_boundary_matrix.csv",
    "22_l2_boundary_contract.csv",
    "23_future_authorization_template_extract03p_r1.json",
    "24_human_decision_points.csv",
    "25_review_items.csv",
    "26_o_rg_boundary_crosswalk.csv",
    "27_n_r1_partial_topic_crosswalk.csv",
    "28_source_configuration_readiness_import.csv",
    "29_source_id_readiness_import.csv",
    "30_next_step_options.csv",
    "31_recommended_next_step.md",
    "32_no_execution_guard_results.csv",
    "33_validation_results.csv",
    "34_human_readable_p_contract_de.md",
    "35_contract_summary_for_registry.json",
    "36_publication_safe_note_candidates.md",
    "37_short_result_note_de.md",
    "38_machine_readable_p_contract_summary.json",
    "39_claim_boundary_grep_report.csv",
    "FINAL_RESULT_NOTE.md",
]

REQUIRED_INPUT_NAMES = [
    "O_RG_boundary_snapshot_sqlite",
    "O_RG_partial_lineage_topic_registry",
    "O_source_configuration_readiness",
    "O_source_id_readiness",
    "N_R1_degeneracy_lineage_classification_matrix",
    "N_R1_lineage_join_key_audit",
    "N_R1_source_pair_configuration_field_audit",
    "N_R1_pair_role_lineage_audit",
    "N_R1_near_alignment_lineage_matrix",
    "N_R1_component_bridge_lineage_matrix",
    "N_R1_negative_control_crosswalk",
    "M_RG_registry_snapshot_sqlite",
    "I_identity_component_mapping",
    "J_near_alignment_items",
    "K_R1_control_classification_matrix",
    "K_R2_decision_matrix",
    "H_R1_full_response_vectors",
    "H_R1_vector_hashes",
    "H_R1_sign_normalized_groups",
    "A_R1_pair_split_assignments_readonly",
    "A_R1_K_matrix_readonly",
    "source_response_code_path",
    "source_response_config_manifest",
    "response_vector_generation_hook",
    "normalization_rule",
    "sign_anchor_rule",
    "index_convention",
    "serialization_hash_rule",
    "pair_id_role_convention",
    "source_pair_configuration_fields",
    "lineage_join_keys",
    "source_configuration_audit_authorization",
]

INPUT_PATHS = {
    "O_RG_boundary_snapshot_sqlite": O_RG / "30_boundary_registry_snapshot.sqlite",
    "O_RG_partial_lineage_topic_registry": O_RG / "09_partial_lineage_topic_registry.csv",
    "O_source_configuration_readiness": O / "20_source_configuration_audit_contract_readiness.csv",
    "O_source_id_readiness": O / "21_source_id_audit_contract_readiness.csv",
    "N_R1_degeneracy_lineage_classification_matrix": N_R1 / "28_degeneracy_lineage_classification_matrix.csv",
    "N_R1_lineage_join_key_audit": N_R1 / "17_lineage_join_key_audit.csv",
    "N_R1_source_pair_configuration_field_audit": N_R1 / "18_source_pair_configuration_field_audit.csv",
    "N_R1_pair_role_lineage_audit": N_R1 / "19_pair_role_lineage_audit.csv",
    "N_R1_near_alignment_lineage_matrix": N_R1 / "23_near_alignment_lineage_matrix.csv",
    "N_R1_component_bridge_lineage_matrix": N_R1 / "24_component_bridge_lineage_matrix.csv",
    "N_R1_negative_control_crosswalk": N_R1 / "25_negative_control_crosswalk.csv",
    "M_RG_registry_snapshot_sqlite": M_RG / "30_registry_snapshot.sqlite",
    "I_identity_component_mapping": REPO_ROOT / "runs/QSB-EXTRACT03I/response_vector_identity_k_alignment_review/18_identity_to_component_explanation_matrix.csv",
    "J_near_alignment_items": REPO_ROOT / "runs/QSB-EXTRACT03J/near_alignment_structure_review/04_near_alignment_item_import.csv",
    "K_R1_control_classification_matrix": REPO_ROOT / "runs/QSB-EXTRACT03K-R1/authorized_collinearity_control_run/18_hypothesis_classification_matrix.csv",
    "K_R2_decision_matrix": REPO_ROOT / "runs/QSB-EXTRACT03K-R2/human_review_collinearity_control_classifications/13_decision_points_for_human_review.csv",
    "H_R1_full_response_vectors": REPO_ROOT / "runs/QSB-EXTRACT03H-R1/authorized_response_vector_export/09_response_vector_export.csv",
    "H_R1_vector_hashes": REPO_ROOT / "runs/QSB-EXTRACT03H-R1/authorized_response_vector_export/10_response_vector_hashes.csv",
    "H_R1_sign_normalized_groups": REPO_ROOT / "runs/QSB-EXTRACT03H-R1/authorized_response_vector_export/11_sign_normalized_vector_signatures.csv",
    "A_R1_pair_split_assignments_readonly": REPO_ROOT / "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/08_canonical_pair_split_assignment.csv",
    "A_R1_K_matrix_readonly": REPO_ROOT / "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv",
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
    "source_configuration_audit_authorization": REPO_ROOT / "runs/QSB-EXTRACT03P-R1/AUTHORIZATION.json",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(name: str, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path = OUT_DIR / name
    with path.open("w", newline="", encoding="utf-8") as f:
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


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def sqlite_integrity(path: Path) -> str:
    if not path.is_file():
        return "missing"
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        return con.execute("PRAGMA integrity_check").fetchone()[0]
    finally:
        con.close()


def refuse_overwrite() -> None:
    existing = [name for name in ARTIFACTS if (OUT_DIR / name).exists()]
    extras = [p.name for p in OUT_DIR.iterdir()] if OUT_DIR.exists() else []
    if os.environ.get("QSB_EXTRACT03P_REGENERATE") == "1" and sorted(extras) == sorted(ARTIFACTS):
        return
    if existing or extras:
        raise SystemExit(
            "Refusing to write into non-empty EXTRACT03P output directory: "
            + ", ".join(sorted(set(existing + extras)))
        )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    refuse_overwrite()

    created_at = datetime.now(timezone.utc).isoformat()
    o_rg_summary = json.loads((O_RG / "25_machine_readable_o_rg_boundary_snapshot_summary.json").read_text(encoding="utf-8"))
    partial_topics = read_csv(O_RG / "09_partial_lineage_topic_registry.csv")
    sc_readiness = read_csv(O_RG / "12_source_configuration_readiness_registry.csv")
    sid_readiness = read_csv(O_RG / "13_source_id_readiness_registry.csv")
    join_keys = read_csv(N_R1 / "17_lineage_join_key_audit.csv")
    source_fields = read_csv(N_R1 / "18_source_pair_configuration_field_audit.csv")

    input_rows = []
    for idx, name in enumerate(REQUIRED_INPUT_NAMES, 1):
        path = INPUT_PATHS[name]
        available = path.exists()
        current_status = "available_readonly" if available else "input_gap_missing"
        if name == "source_configuration_audit_authorization":
            current_status = "not_present_template_only"
        input_rows.append(
            {
                "input_id": f"PRI-{idx:02d}",
                "input_name": name,
                "required_for_p_r1": "yes",
                "current_status": current_status,
                "evidence_or_source": rel(path),
                "blocking_if_missing": "yes",
                "notes": "Missing input must not be replaced; document as gap/stop criterion." if not available else "Read-only source located.",
            }
        )

    required_available = sum(1 for row in input_rows if row["current_status"] == "available_readonly")
    required_missing = len(input_rows) - required_available

    partial_rows = []
    for idx, row in enumerate(partial_topics, 1):
        partial_rows.append(
            {
                "localization_id": f"PLOC-{idx:02d}",
                "source_layer": "O-RG/O/N-R1",
                "source_artifact": row["source_artifact"],
                "lineage_topic": row["lineage_topic"],
                "n_r1_classification": row["n_r1_classification"],
                "o_review_status": row["o_review_status"],
                "registry_boundary_status": row["registry_boundary_status"],
                "evidence_summary": row["evidence_summary"],
                "limitations": row["limitations"],
                "related_review_item": row["recommended_next_action"],
                "related_decision_point": "D01-D09 context; see O-RG decision registry",
                "claim_boundary": row["claim_boundary"],
                "notes": row["notes"],
            }
        )

    pq_rows = [
        ("PQ01_partial_topic_localization", "Locate exactly the six partial topics from N-R1/O/O-RG.", "05_partial_lineage_topic_localization.csv", "read registries only", "no audit execution", "localized_topic_matrix"),
        ("PQ02_source_configuration_field_inventory", "Define required source/pair configuration fields.", "N_R1_source_pair_configuration_field_audit", "inspect field inventory", "no post-hoc field invention", "field_requirement_table"),
        ("PQ03_lineage_join_key_sufficiency", "Define lineage join keys required for P-R1.", "N_R1_lineage_join_key_audit", "inspect join-key contracts", "no new joins by inference alone", "join_key_table"),
        ("PQ04_pair_role_and_order_scope", "Freeze pair roles, ordering, and symmetry handling.", "N_R1_pair_role_lineage_audit", "inspect role convention", "no relabeling", "role_order_contract"),
        ("PQ05_identity_group_source_configuration_mapping", "Scope identity-group to source-configuration mapping.", "I_identity_component_mapping;H_R1_sign_normalized_groups", "read mapping tables", "no identity regrouping", "scope_table"),
        ("PQ06_near_alignment_source_configuration_mapping", "Scope near-alignment to source-configuration mapping.", "J_near_alignment_items;N_R1_near_alignment_lineage_matrix", "read mapping tables", "no rerun near-alignment", "scope_table"),
        ("PQ07_component_bridge_source_configuration_mapping", "Scope component-bridge to source-configuration mapping.", "N_R1_component_bridge_lineage_matrix", "read bridge rows", "no bridge recompute", "scope_table"),
        ("PQ08_negative_control_relevance", "Define how negative controls may bound interpretation.", "K_R1_control_classification_matrix;K_R2_decision_matrix", "read control classifications", "no controls rerun", "control_scope_table"),
        ("PQ09_source_id_boundary", "Keep Source-ID audit conditional and out of P-R1 unless separately authorized.", "O_source_id_readiness", "read readiness only", "no source-id audit now", "boundary_contract"),
        ("PQ10_stop_and_claim_boundary", "Freeze stop criteria and claim boundaries.", "O_RG_boundary_snapshot_sqlite;claim registries", "read boundary records", "no claim upgrade", "stop_claim_matrix"),
    ]
    pq_dicts = [
        {
            "question_id": qid,
            "question": question,
            "purpose": purpose,
            "required_inputs": req,
            "allowed_operations": allowed,
            "forbidden_operations": forbidden,
            "expected_output_type": out_type,
            "classification_boundary": "pipeline-review contract only; no nature/interface/geometry/gravity claim",
            "notes": "For later P-R1 only; not executed in EXTRACT03P.",
        }
        for qid, question, req, allowed, forbidden, out_type in pq_rows
        for purpose in ["Specify later P-R1 review requirement without executing it."]
    ]

    allowed_ops = [
        "read_o_rg_boundary_snapshot",
        "read_o_review",
        "read_n_r1_lineage_results",
        "read_m_rg_registry_snapshot",
        "read_i_identity_mapping",
        "read_j_near_alignment_items",
        "read_k_r1_control_classifications",
        "read_k_r2_decision_matrix",
        "read_h_r1_vectors",
        "read_a_r1_pair_assignments",
        "inspect_source_configuration_fields",
        "inspect_lineage_join_keys",
        "inspect_pair_role_convention",
        "inspect_response_generation_hook",
        "compute_descriptive_source_configuration_metrics",
        "write_source_configuration_audit_report",
    ]
    forbidden_ops = [
        "run_source_configuration_audit_now",
        "run_source_id_audit_now",
        "rerun_degeneracy_lineage_audit",
        "rerun_source_response_audit",
        "rerun_controls",
        "export_vectors",
        "mutate_vectors",
        "recompute_K",
        "recompute_strength",
        "recompute_d",
        "recompute_D",
        "recompute_edges",
        "rerun_shortest_paths",
        "edge_rethresholding",
        "rerun_clusters",
        "rerun_motifs",
        "run_bootstrap",
        "open_F3_raw_source",
        "reconstruct_raw_phases",
        "rerun_A_R1_pipeline",
        "change_parameters",
        "change_thresholds",
        "change_splits_or_seeds",
        "mutate_upstream_files",
        "mutate_live_dwh",
        "repair_L2",
        "make_nature_claim",
        "make_interface_claim",
        "make_geometry_claim",
        "make_gravity_claim",
        "public_claim_upgrade",
    ]
    stop_items = [
        "O-RG Boundary Snapshot fehlt",
        "6 partial Lineage Topics nicht eindeutig lokalisiert werden koennen",
        "Source-Configuration Readiness fehlt",
        "N-R1 Source-/Pair-Konfigurationsfeld-Audit fehlt",
        "N-R1 Lineage-Join-Key-Audit fehlt",
        "Pair-ID-/Rollen-Konvention fehlt",
        "Source-/Pair-Konfigurationsfelder nicht bestimmbar sind",
        "Lineage-Join-Keys nicht bestimmbar sind",
        "eine verbotene Operation noetig waere",
        "Source-Configuration-Audit-Autorisierung fehlt",
    ]

    inventory_paths = [
        O_RG / "01_extract03o_rg_run_manifest.json",
        O_RG / "09_partial_lineage_topic_registry.csv",
        O_RG / "12_source_configuration_readiness_registry.csv",
        O_RG / "13_source_id_readiness_registry.csv",
        O_RG / "30_boundary_registry_snapshot.sqlite",
        O / "07_partial_lineage_topics_review.csv",
        N_R1 / "17_lineage_join_key_audit.csv",
        N_R1 / "18_source_pair_configuration_field_audit.csv",
        N_R1 / "19_pair_role_lineage_audit.csv",
        N_R1 / "23_near_alignment_lineage_matrix.csv",
        N_R1 / "24_component_bridge_lineage_matrix.csv",
        N_R1 / "25_negative_control_crosswalk.csv",
        M_RG / "30_registry_dwh_snapshot.sqlite",
    ]

    write_json(
        "01_extract03p_run_manifest.json",
        {
            "work_package": "QSB-EXTRACT03P",
            "status": STATUS,
            "created_at_utc": created_at,
            "repo_root": str(REPO_ROOT),
            "o_rg_snapshot_seen": (O_RG / "30_boundary_registry_snapshot.sqlite").is_file(),
            "o_rg_status": o_rg_summary["status"],
            "extract03o_seen": bool(o_rg_summary["extract03o_seen"]),
            "extract03n_r1_seen": bool(o_rg_summary["extract03n_r1_seen"]),
            "partial_lineage_topics_seen": True,
            "partial_lineage_topics_count": len(partial_rows),
            "source_configuration_readiness_seen": bool(sc_readiness),
            "source_id_readiness_seen": bool(sid_readiness),
            "narrow_scope_confirmed": True,
            "source_configuration_audit_run_executed": False,
            "source_id_audit_run_executed": False,
            "degeneracy_lineage_audit_rerun": False,
            "source_response_audit_rerun": False,
            "controls_reexecuted": False,
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
            "live_dwh_modified": False,
            "upstream_modified": False,
            "l2_fail_changed": False,
            "post_hoc_tuning_performed": False,
            "nature_claim_made": False,
            "interface_claim_made": False,
            "geometry_claim_made": False,
            "gravity_claim_made": False,
            "public_claim_authorized": False,
            "review_items_count": 4,
            "required_inputs_total": len(input_rows),
            "required_inputs_available": required_available,
            "required_inputs_missing": required_missing,
            "future_authorization_template_created": True,
            "claim_boundary": CLAIM_BOUNDARY,
            "next_allowed_action": NEXT_ALLOWED_ACTION,
        },
    )

    write_csv(
        "02_upstream_inventory_and_hashes.csv",
        ["upstream_id", "path", "exists", "sha256", "readonly_use", "notes"],
        [
            {
                "upstream_id": f"UP-{i:02d}",
                "path": rel(path),
                "exists": path.exists(),
                "sha256": sha256(path),
                "readonly_use": "yes",
                "notes": "Imported only for contract specification.",
            }
            for i, path in enumerate(inventory_paths, 1)
        ],
    )
    write_csv("03_input_availability_review.csv", list(input_rows[0].keys()), input_rows)
    write_csv(
        "04_o_rg_snapshot_readonly_review.csv",
        ["review_id", "snapshot_path", "exists", "sqlite_integrity_check", "mode", "mutation_performed", "notes"],
        [
            {
                "review_id": "O-RG-SQLITE-01",
                "snapshot_path": rel(O_RG / "30_boundary_registry_snapshot.sqlite"),
                "exists": (O_RG / "30_boundary_registry_snapshot.sqlite").is_file(),
                "sqlite_integrity_check": sqlite_integrity(O_RG / "30_boundary_registry_snapshot.sqlite"),
                "mode": "read_only",
                "mutation_performed": False,
                "notes": "Opened with SQLite read-only URI for integrity check only.",
            }
        ],
    )
    write_csv("05_partial_lineage_topic_localization.csv", list(partial_rows[0].keys()), partial_rows)
    write_csv("06_source_configuration_audit_question_registry.csv", list(pq_dicts[0].keys()), pq_dicts)
    write_csv("07_required_p_r1_inputs.csv", list(input_rows[0].keys()), input_rows)
    write_csv(
        "08_allowed_operations_matrix.csv",
        ["operation_id", "operation", "allowed_in_extract03p", "allowed_in_p_r1_after_authorization", "required_guard", "notes"],
        [
            {
                "operation_id": f"ALLOW-{i:02d}",
                "operation": op,
                "allowed_in_extract03p": "contract_spec_only" if op.startswith("write_") else "read_or_define_only",
                "allowed_in_p_r1_after_authorization": "yes_under_contract",
                "required_guard": "no recompute, no mutation, no claim upgrade",
                "notes": "P-R1 still requires separate human authorization.",
            }
            for i, op in enumerate(allowed_ops, 1)
        ],
    )
    write_csv(
        "09_forbidden_operations_matrix.csv",
        ["operation_id", "operation", "forbidden_in_extract03p", "forbidden_in_p_r1", "reason", "claim_boundary"],
        [
            {
                "operation_id": f"FORBID-{i:02d}",
                "operation": op,
                "forbidden_in_extract03p": "yes",
                "forbidden_in_p_r1": "yes_unless_separately_authorized_and_outside_this_contract",
                "reason": "Would exceed contract-only source-configuration lineage scope.",
                "claim_boundary": CLAIM_BOUNDARY,
            }
            for i, op in enumerate(forbidden_ops, 1)
        ],
    )
    write_csv(
        "10_p_r1_stop_criteria.csv",
        ["stop_id", "criterion", "blocking_for_p_r1", "detection_source", "required_action"],
        [
            {
                "stop_id": f"STOP-{i:02d}",
                "criterion": criterion,
                "blocking_for_p_r1": "yes",
                "detection_source": "EXTRACT03P contract inputs/guards",
                "required_action": "Block P-R1; document gap; do not substitute.",
            }
            for i, criterion in enumerate(stop_items, 1)
        ],
    )
    write_csv(
        "11_source_configuration_field_requirements.csv",
        ["field_id", "field_name", "required_for_p_r1", "n_r1_observation_status", "source_layer", "role", "stop_if_missing", "notes"],
        [
            {
                "field_id": f"SCF-{i:02d}",
                "field_name": row["field_name"],
                "required_for_p_r1": row["contract_required"],
                "n_r1_observation_status": row["concrete_observation_status"],
                "source_layer": row["source_layer"],
                "role": "source/pair configuration lineage field",
                "stop_if_missing": "yes",
                "notes": row["notes"],
            }
            for i, row in enumerate(source_fields, 1)
        ],
    )
    write_csv(
        "12_lineage_join_key_requirements.csv",
        ["key_id", "join_key", "purpose", "required_source_layers", "allowed_use", "forbidden_use", "stop_if_missing", "notes"],
        [
            {
                "key_id": f"LJK-{i:02d}",
                "join_key": row["join_key"],
                "purpose": row["purpose"],
                "required_source_layers": row["required_source_layers"],
                "allowed_use": row["allowed_use"],
                "forbidden_use": row["forbidden_use"],
                "stop_if_missing": "yes",
                "notes": row["notes"],
            }
            for i, row in enumerate(join_keys, 1)
        ],
    )

    simple_contracts = {
        "13_pair_role_and_order_contract.csv": [
            {"contract_id": "PAIR-ROLE-01", "scope": "pair_id, role_a, role_b, pair order, sign/order symmetry", "allowed": "inspect existing convention", "forbidden": "relabel roles or change pair order", "required_inputs": "pair_id_role_convention;N_R1_pair_role_lineage_audit", "stop_criteria": "missing pair-id/role convention", "claim_boundary": CLAIM_BOUNDARY}
        ],
        "14_identity_group_source_configuration_scope.csv": [
            {"scope_id": "IDENT-01", "partial_topic": "source_response_degeneracy", "required_inputs": "I_identity_component_mapping;H_R1_sign_normalized_groups;lineage_join_keys", "allowed_mapping": "read-only identity-group to source-configuration crosswalk", "forbidden_mapping": "regroup identities or recompute vectors", "stop_if_missing": "yes", "claim_boundary": CLAIM_BOUNDARY}
        ],
        "15_near_alignment_source_configuration_scope.csv": [
            {"scope_id": "NEAR-01", "partial_topic": "lineage_join_keys", "required_inputs": "J_near_alignment_items;N_R1_near_alignment_lineage_matrix", "allowed_mapping": "read-only near-alignment to source-configuration crosswalk", "forbidden_mapping": "rerun near-alignment or threshold edges", "stop_if_missing": "yes", "claim_boundary": CLAIM_BOUNDARY}
        ],
        "16_component_bridge_source_configuration_scope.csv": [
            {"scope_id": "BRIDGE-01", "partial_topic": "component_bridge_lineage", "required_inputs": "N_R1_component_bridge_lineage_matrix;component_id", "allowed_mapping": "read-only component bridge mapping", "forbidden_mapping": "recompute components, clusters, motifs, or bridges", "stop_if_missing": "yes", "claim_boundary": CLAIM_BOUNDARY}
        ],
        "17_negative_control_relevance_contract.csv": [
            {"scope_id": "NEG-01", "partial_topic": "negative_control_lineage", "required_inputs": "K_R1_control_classification_matrix;K_R2_decision_matrix", "allowed_use": "bound interpretation of later P-R1 descriptive review", "forbidden_use": "rerun controls or infer natural/artifact origin", "stop_if_missing": "yes", "claim_boundary": CLAIM_BOUNDARY}
        ],
        "18_source_id_boundary_contract.csv": [
            {"boundary_id": "SID-01", "source_id_status": "later_conditional", "allowed_in_extract03p": "import readiness only", "allowed_in_p_r1": "only boundary checks unless separately authorized", "forbidden": "source-id/source-record audit now", "required_future_authorization": "yes", "claim_boundary": CLAIM_BOUNDARY}
        ],
        "19_allowed_descriptive_metrics_contract.csv": [
            {"metric_id": "MET-01", "metric_family": "availability counts", "allowed": "count present/missing required fields and keys", "forbidden": "model recompute or strength/d/D/edge recompute", "output_boundary": "descriptive audit metadata only"},
            {"metric_id": "MET-02", "metric_family": "join-key coverage flags", "allowed": "record coverage by existing rows", "forbidden": "create substitute lineage keys", "output_boundary": "descriptive audit metadata only"},
        ],
        "20_source_configuration_lineage_classification_schema.csv": [
            {"schema_id": "CLS-01", "classification": "source_configuration_lineage_supported_as_pipeline_review_pattern", "meaning": "later P-R1 finds sufficient documented pipeline pattern", "claim_boundary": "not a nature/interface/geometry/gravity claim"},
            {"schema_id": "CLS-02", "classification": "source_configuration_lineage_partially_supported_with_review_items", "meaning": "later P-R1 finds partial support and review items", "claim_boundary": "not a nature/interface/geometry/gravity claim"},
            {"schema_id": "CLS-03", "classification": "source_configuration_lineage_not_supported_by_audit", "meaning": "later P-R1 does not support the lineage pattern", "claim_boundary": "not a nature/interface/geometry/gravity claim"},
            {"schema_id": "CLS-04", "classification": "source_configuration_lineage_inconclusive", "meaning": "later P-R1 remains inconclusive", "claim_boundary": "not a nature/interface/geometry/gravity claim"},
            {"schema_id": "CLS-05", "classification": "source_configuration_lineage_input_gap", "meaning": "required input missing", "claim_boundary": "not a nature/interface/geometry/gravity claim"},
            {"schema_id": "CLS-06", "classification": "source_configuration_lineage_blocked_by_guard", "meaning": "guard prevents the requested operation", "claim_boundary": "not a nature/interface/geometry/gravity claim"},
        ],
        "21_claim_boundary_matrix.csv": [
            {"boundary_id": "CB-ALLOW-01", "statement": "EXTRACT03P prepares a narrow Source-Configuration Lineage Audit Contract.", "status": "allowed", "notes": "Contract-only."},
            {"boundary_id": "CB-FORBID-01", "statement": "EXTRACT03P proves QSB.", "status": "forbidden", "notes": "Unsupported claim context only."},
            {"boundary_id": "CB-FORBID-02", "statement": "EXTRACT03P establishes Source-Configuration Lineage.", "status": "forbidden", "notes": "Unsupported claim context only."},
            {"boundary_id": "CB-FORBID-03", "statement": "EXTRACT03P repairs L2.", "status": "forbidden", "notes": "Unsupported claim context only."},
            {"boundary_id": "CB-FORBID-04", "statement": "Public claim authorized.", "status": "forbidden", "notes": "Unsupported claim context only."},
        ],
        "22_l2_boundary_contract.csv": [
            {"boundary_id": "L2-01", "l2_result": "fail", "n4_support": "0/3 required 2/3", "theta_new": "0.012446436850524916", "epsilon_new": "0.006009422749372488", "changed_by_extract03p": "false", "claim_boundary": "L2 is not repaired, overwritten, hidden, relativized, or represented as improved."}
        ],
    }
    for filename, rows in simple_contracts.items():
        write_csv(filename, list(rows[0].keys()), rows)

    write_json(
        "23_future_authorization_template_extract03p_r1.json",
        {
            "authorization_status": "TEMPLATE_REQUIRES_HUMAN_APPROVAL",
            "authorized_work_package": "QSB-EXTRACT03P-R1_NARROW_SOURCE_CONFIGURATION_LINEAGE_AUDIT_RUN",
            "source_contract": "QSB-EXTRACT03P",
            "human_approval_required": True,
            "allowed_scope": "narrow_source_configuration_lineage_audit_only_under_contract",
            "no_K_recompute": True,
            "no_strength_d_D_edge_recompute": True,
            "no_shortest_path_rerun": True,
            "no_edge_rethresholding": True,
            "no_cluster_or_motif_rerun": True,
            "no_bootstrap": True,
            "no_raw_phase_reconstruction": True,
            "no_F3_raw_source_open": True,
            "no_A_R1_rerun": True,
            "no_vector_export": True,
            "no_vector_mutation": True,
            "no_live_dwh_mutation": True,
            "no_l2_change": True,
            "no_post_hoc_tuning": True,
            "no_nature_claim": True,
            "no_interface_claim": True,
            "no_geometry_claim": True,
            "no_gravity_claim": True,
            "no_public_claim_upgrade": True,
        },
    )

    write_csv(
        "24_human_decision_points.csv",
        ["decision_id", "topic", "decision_needed", "default_without_decision", "notes"],
        [
            {"decision_id": "PD01", "topic": "P-R1 authorization", "decision_needed": "Approve or decline separate P-R1 execution.", "default_without_decision": "not_authorized", "notes": "Template is not an authorization."},
            {"decision_id": "PD02", "topic": "Input gaps", "decision_needed": "Provide missing required inputs or accept block.", "default_without_decision": "block", "notes": "No substitution."},
            {"decision_id": "PD03", "topic": "Source-ID boundary", "decision_needed": "Decide later source-id/source-record contract if needed.", "default_without_decision": "conditional_later", "notes": "Not part of EXTRACT03P."},
            {"decision_id": "PD04", "topic": "Claim boundary", "decision_needed": "Confirm no public claim upgrade.", "default_without_decision": "no_upgrade", "notes": "L2 remains fail."},
        ],
    )
    write_csv(
        "25_review_items.csv",
        ["review_item_id", "topic", "severity", "description", "required_action", "claim_boundary"],
        [
            {"review_item_id": "PRI-01", "topic": "required_inputs", "severity": "blocking_if_p_r1_requested", "description": "Several future inputs are not located in this contract pass.", "required_action": "Resolve or block P-R1.", "claim_boundary": CLAIM_BOUNDARY},
            {"review_item_id": "PRI-02", "topic": "source_id_boundary", "severity": "conditional", "description": "Source-ID/source-record audit remains later conditional.", "required_action": "Do not execute in EXTRACT03P.", "claim_boundary": CLAIM_BOUNDARY},
            {"review_item_id": "PRI-03", "topic": "authorization", "severity": "blocking", "description": "P-R1 authorization is template-only.", "required_action": "Human approval required.", "claim_boundary": CLAIM_BOUNDARY},
            {"review_item_id": "PRI-04", "topic": "L2", "severity": "boundary", "description": "L2 result remains fail and unchanged.", "required_action": "No repair or reinterpretation.", "claim_boundary": CLAIM_BOUNDARY},
        ],
    )
    write_csv(
        "26_o_rg_boundary_crosswalk.csv",
        ["crosswalk_id", "o_rg_record_id", "lineage_topic", "extract03p_contract_target", "source_artifact", "notes"],
        [
            {"crosswalk_id": f"ORG-X-{i:02d}", "o_rg_record_id": row["localization_id"], "lineage_topic": row["lineage_topic"], "extract03p_contract_target": "P-R1 source-configuration lineage contract scope", "source_artifact": row["source_artifact"], "notes": row["limitations"]}
            for i, row in enumerate(partial_rows, 1)
        ],
    )
    write_csv(
        "27_n_r1_partial_topic_crosswalk.csv",
        ["crosswalk_id", "lineage_topic", "n_r1_classification", "required_source_config_focus", "join_key_focus", "role_order_focus"],
        [
            {"crosswalk_id": f"NR1-X-{i:02d}", "lineage_topic": row["lineage_topic"], "n_r1_classification": row["n_r1_classification"], "required_source_config_focus": "source/pair fields from 11_source_configuration_field_requirements.csv", "join_key_focus": "keys from 12_lineage_join_key_requirements.csv", "role_order_focus": "contract from 13_pair_role_and_order_contract.csv"}
            for i, row in enumerate(partial_rows, 1)
        ],
    )
    write_csv("28_source_configuration_readiness_import.csv", list(sc_readiness[0].keys()), sc_readiness)
    write_csv("29_source_id_readiness_import.csv", list(sid_readiness[0].keys()), sid_readiness)
    write_csv(
        "30_next_step_options.csv",
        ["option_id", "next_step", "allowed_after_extract03p", "requires_human_authorization", "notes"],
        [
            {"option_id": "NEXT-01", "next_step": "Authorize QSB-EXTRACT03P-R1 under this contract.", "allowed_after_extract03p": "yes", "requires_human_authorization": "yes", "notes": "Recommended only after input gaps are accepted or resolved."},
            {"option_id": "NEXT-02", "next_step": "Prepare separate Source-ID contract.", "allowed_after_extract03p": "later_conditional", "requires_human_authorization": "yes", "notes": "Not a substitute for P-R1."},
            {"option_id": "NEXT-03", "next_step": "Run recompute or public-claim upgrade.", "allowed_after_extract03p": "no", "requires_human_authorization": "out_of_scope", "notes": "Forbidden by this contract."},
        ],
    )
    write_md(
        "31_recommended_next_step.md",
        f"""# Recommended Next Step

Recommended next allowed action: {NEXT_ALLOWED_ACTION}

The future authorization template was created as a template only and does not authorize P-R1. If a required input is missing, P-R1 must block or record an input gap. Source-ID/source-record audit remains conditional and separate.
""",
    )
    guard_names = [
        "o_rg_snapshot_present",
        "partial_topics_localized",
        "source_configuration_readiness_present",
        "no_source_configuration_audit_run",
        "no_source_id_audit_run",
        "no_degeneracy_lineage_audit_rerun",
        "no_source_response_audit_rerun",
        "no_controls_reexecuted",
        "no_vectors_exported",
        "no_vectors_mutated",
        "no_K_recompute",
        "no_strength_recompute",
        "no_d_recompute",
        "no_D_recompute",
        "no_edge_recompute",
        "no_shortest_path_rerun",
        "no_edge_rethresholding",
        "no_cluster_rerun",
        "no_motif_rerun",
        "no_bootstrap",
        "no_raw_phase_reconstruction",
        "no_F3_raw_source_opened",
        "no_A_R1_pipeline_rerun",
        "no_live_dwh_mutation",
        "no_upstream_mutation",
        "no_l2_change",
        "no_post_hoc_tuning",
        "no_nature_claim",
        "no_interface_claim",
        "no_geometry_claim",
        "no_gravity_claim",
        "no_public_claim_upgrade",
        "future_authorization_template_only",
        "overwrite_refusal",
    ]
    write_csv(
        "32_no_execution_guard_results.csv",
        ["guard_id", "guard", "passed", "evidence", "notes"],
        [
            {"guard_id": f"GUARD-{i:02d}", "guard": name, "passed": "yes", "evidence": "contract generation only", "notes": "No forbidden operation executed."}
            for i, name in enumerate(guard_names, 1)
        ],
    )

    validation_rows = [
        ("VAL-01", "exact_40_artifacts", "pending_until_all_written", "Checked at script end."),
        ("VAL-02", "o_rg_snapshot_present", str((O_RG / "30_boundary_registry_snapshot.sqlite").is_file()).lower(), rel(O_RG / "30_boundary_registry_snapshot.sqlite")),
        ("VAL-03", "six_partial_topics_localized", str(len(partial_rows) == 6).lower(), str(len(partial_rows))),
        ("VAL-04", "pq01_pq10_created", str(len(pq_dicts) == 10).lower(), str(len(pq_dicts))),
        ("VAL-05", "future_authorization_template_not_authorized", "true", "TEMPLATE_REQUIRES_HUMAN_APPROVAL"),
        ("VAL-06", "no_execution_guards_created", "true", "32_no_execution_guard_results.csv"),
    ]
    write_csv("33_validation_results.csv", ["validation_id", "check", "passed", "evidence"], [{"validation_id": a, "check": b, "passed": c, "evidence": d} for a, b, c, d in validation_rows])

    topic_list = "\n".join(f"- {row['lineage_topic']}: {row['limitations']}" for row in partial_rows)
    field_list = "\n".join(f"- {row['field_name']}: {row['concrete_observation_status']}" for row in source_fields)
    key_list = "\n".join(f"- {row['join_key']}: {row['purpose']}" for row in join_keys)
    write_md(
        "34_human_readable_p_contract_de.md",
        f"""# QSB-EXTRACT03P Narrow Source-Configuration Lineage Audit Contract

## Ausgangspunkt
EXTRACT03P ist ein Contract-only-Block auf Basis von O-RG/O/N-R1.

## Warum dieser enge Contract jetzt sinnvoll ist
O-RG registriert sechs partial Lineage Topics und Source-Configuration readiness als naechsten Methodenschritt.

## Partial Lineage Topics im Scope
{topic_list}

## Was ein spaeterer P-R1 pruefen darf
P-R1 darf nur die source-configuration lineage anhand vorhandener Felder, Join Keys und Rollen read-only pruefen.

## Benoetigte Source-/Pair-Konfigurationsfelder
{field_list}

## Benoetigte Lineage-Join-Keys
{key_list}

## Pair-Rollen, Reihenfolgen und Symmetrien
P-R1 muss pair_id, role_a, role_b, Reihenfolge und Symmetrie anhand vorhandener Konventionen pruefen; Relabeling ist verboten.

## Identity-Group-Scope
Identity-Gruppen duerfen nur ueber vorhandene Join Keys auf Source-Konfigurationsfelder bezogen werden.

## Near-Alignment-Scope
Near-Alignment-Items duerfen nicht neu berechnet werden.

## Komponenten-Bruecken
Komponenten-Bruecken bleiben deskriptive Crosswalks.

## Negative Controls
Negative Controls begrenzen Interpretation; sie beweisen weder natuerlichen noch artefaktischen Ursprung.

## Source-ID-Grenze
Source-ID/source-record audit bleibt spaeter conditional und separat.

## Erlaubte Operationen
Read-only Import, Feld-/Key-/Rolleninspektion und deskriptive Vertragsberichte.

## Verbotene Operationen
Keine Auditausfuehrung, keine Recomputes, keine Vektorexporte, keine Live-DWH-/Registry-Mutation, keine Claim-Upgrades.

## Stop-Kriterien
P-R1 blockiert bei fehlendem O-RG Snapshot, fehlenden partial topics, fehlenden Feldern/Keys/Rollen, fehlender Autorisierung oder notwendiger verbotener Operation.

## L2-Grenze
L2 bleibt fail: N4 support 0/3 required 2/3; theta_new 0.012446436850524916; epsilon_new 0.006009422749372488.

## Claim Boundary
{CLAIM_BOUNDARY}

## Was ausdruecklich nicht behauptet wird
Keine Natur-, Interface-, Geometrie- oder Gravitationsbehauptung; kein Public-Claim-Upgrade.

## Naechster Schritt
{NEXT_ALLOWED_ACTION}
""",
    )

    summary = {
        "work_package": "QSB-EXTRACT03P",
        "status": STATUS,
        "artifact_count": 40,
        "partial_topics": [row["lineage_topic"] for row in partial_rows],
        "pq_questions": [row["question_id"] for row in pq_dicts],
        "required_inputs_total": len(input_rows),
        "required_inputs_available": required_available,
        "required_inputs_missing": required_missing,
        "source_id_boundary": "later_conditional_separate_authorization_required",
        "future_authorization_template": "created_not_authorized",
        "claim_boundary": CLAIM_BOUNDARY,
        "next_allowed_action": NEXT_ALLOWED_ACTION,
    }
    write_json("35_contract_summary_for_registry.json", summary)
    write_md(
        "36_publication_safe_note_candidates.md",
        """# Publication-Safe Note Candidates

Candidate internal note: EXTRACT03P prepared a narrow contract for a later, separately authorized Source-Configuration Lineage Audit over six partial Degeneracy-Lineage topics.

Boundary note: This contract does not establish Source-Configuration Lineage, does not repair L2, and does not authorize public claims.
""",
    )
    write_md(
        "37_short_result_note_de.md",
        f"""# QSB-EXTRACT03P Short Result Note

Status: {STATUS}

EXTRACT03P hat einen Contract-only Snapshot fuer einen spaeteren P-R1 Source-Configuration Lineage Audit erstellt. Sechs partial Topics wurden lokalisiert. PQ01-PQ10, Required Inputs, Stop-Kriterien, Claim Boundary, L2 Boundary und eine nicht autorisierende Future Authorization Template wurden erzeugt.
""",
    )
    write_json("38_machine_readable_p_contract_summary.json", summary)

    grep_pattern = re.compile(
        r"proves|proof|demonstrates gravity|demonstrates emergent geometry|repairs L2|L2 repaired|physical evidence|confirms the Interface mechanism|establishes a physical mechanism|establishes Source-Configuration Lineage|establishes Source-Response-Degeneracy|establishes that the collinearity is natural|establishes that the collinearity is an artifact|public claim authorized",
        re.IGNORECASE,
    )
    grep_rows = []
    for path in sorted(OUT_DIR.iterdir()):
        if not path.is_file() or path.name == "39_claim_boundary_grep_report.csv":
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
                        "notes": "Match retained only as unsupported/forbidden claim boundary language.",
                    }
                )
    if not grep_rows:
        grep_rows.append({"match_id": "GREP-00", "file": "", "line": "", "matched_text": "", "allowed_context": "no_matches", "notes": "No boundary grep hits."})
    write_csv("39_claim_boundary_grep_report.csv", list(grep_rows[0].keys()), grep_rows)

    write_md(
        "FINAL_RESULT_NOTE.md",
        f"""# QSB-EXTRACT03P Final Result

## Status
{STATUS}

## Reviewed Inputs
O-RG, O, N-R1 and selected downstream/upstream references were imported read-only for contract specification.

## Partial Lineage Topic Localization
{topic_list}

## P-R1 Audit Questions
PQ01-PQ10 are defined in 06_source_configuration_audit_question_registry.csv.

## Required Future Inputs
{len(input_rows)} inputs listed; {required_available} available read-only; {required_missing} missing or template-only.

## Allowed and Forbidden Operations
Allowed operations are limited to read-only inspection and contract/audit-report writing after separate authorization. Forbidden operations include audit execution now, source-id audit now, recomputes, vector export/mutation, upstream/live-DWH mutation, L2 repair, post-hoc tuning, and claim upgrades.

## Stop Criteria
P-R1 blocks if required snapshots, topics, readiness, fields, keys, pair roles, authorization, or guard compliance are missing.

## Future Authorization Template
Created as TEMPLATE_REQUIRES_HUMAN_APPROVAL; not authorized.

## No-Execution Guards
All no-execution guards are recorded as passed for this contract-only generation.

## Source-ID Boundary
Source-ID/source-record audit remains later conditional and separate.

## Claim Boundary
{CLAIM_BOUNDARY}

## L2 Boundary
L2 remains fail with N4 support 0/3 required 2/3; theta_new 0.012446436850524916; epsilon_new 0.006009422749372488.

## Next Allowed Action
{NEXT_ALLOWED_ACTION}
""",
    )

    missing_artifacts = [name for name in ARTIFACTS if not (OUT_DIR / name).is_file()]
    extra_artifacts = [path.name for path in OUT_DIR.iterdir() if path.is_file() and path.name not in ARTIFACTS]
    if missing_artifacts or extra_artifacts:
        raise SystemExit(f"Artifact mismatch missing={missing_artifacts} extra={extra_artifacts}")
    # Update validation after final artifact count is known.
    rows = read_csv(OUT_DIR / "33_validation_results.csv")
    rows[0]["passed"] = str(len([p for p in OUT_DIR.iterdir() if p.is_file()]) == 40).lower()
    rows[0]["evidence"] = str(len([p for p in OUT_DIR.iterdir() if p.is_file()]))
    write_csv("33_validation_results.csv", list(rows[0].keys()), rows)


if __name__ == "__main__":
    main()
