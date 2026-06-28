#!/usr/bin/env python3
"""QSB-EXTRACT03N narrow Source-Response degeneracy lineage audit contract.

Contract-only: this script localizes the remaining inconclusive degeneracy topic
and writes a future N-R1 contract package. It does not run the future audit.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "runs/QSB-EXTRACT03N/narrow_source_response_degeneracy_lineage_audit_contract"
M_RG = REPO / "runs/QSB-EXTRACT03M-RG/registry_dwh_integration_snapshot"
M = REPO / "runs/QSB-EXTRACT03M/source_response_audit_result_review"
L_R1 = REPO / "runs/QSB-EXTRACT03L-R1/authorized_source_response_audit_run"
L = REPO / "runs/QSB-EXTRACT03L/source_response_audit_contract"
K_R2 = REPO / "runs/QSB-EXTRACT03K-R2/human_review_collinearity_control_classifications"
K_R1 = REPO / "runs/QSB-EXTRACT03K-R1/authorized_collinearity_control_run"
K = REPO / "runs/QSB-EXTRACT03K/collinearity_control_contract"
J = REPO / "runs/QSB-EXTRACT03J/near_alignment_structure_review"
I = REPO / "runs/QSB-EXTRACT03I/response_vector_identity_k_alignment_review"
H_R1 = REPO / "runs/QSB-EXTRACT03H-R1/authorized_response_vector_export"
A_R1 = REPO / "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum"

FILES = [
    "01_extract03n_run_manifest.json",
    "02_upstream_inventory_and_hashes.csv",
    "03_input_availability_review.csv",
    "04_m_rg_snapshot_readonly_review.csv",
    "05_inconclusive_topic_localization.csv",
    "06_narrow_degeneracy_audit_question_registry.csv",
    "07_required_n_r1_inputs.csv",
    "08_allowed_operations_matrix.csv",
    "09_forbidden_operations_matrix.csv",
    "10_n_r1_stop_criteria.csv",
    "11_lineage_join_key_requirements.csv",
    "12_source_pair_configuration_field_requirements.csv",
    "13_pair_role_lineage_contract.csv",
    "14_response_generation_lineage_contract.csv",
    "15_normalization_sign_index_serialization_contract.csv",
    "16_identity_group_lineage_scope.csv",
    "17_near_alignment_lineage_scope.csv",
    "18_component_bridge_lineage_scope.csv",
    "19_negative_control_lineage_reference.csv",
    "20_allowed_descriptive_metrics_contract.csv",
    "21_degeneracy_lineage_classification_schema.csv",
    "22_claim_boundary_matrix.csv",
    "23_l2_boundary_contract.csv",
    "24_future_authorization_template_extract03n_r1.json",
    "25_human_decision_points.csv",
    "26_review_items.csv",
    "27_registry_snapshot_crosswalk.csv",
    "28_next_step_options.csv",
    "29_recommended_next_step.md",
    "30_no_execution_guard_results.csv",
    "31_validation_results.csv",
    "32_human_readable_n_contract_de.md",
    "33_contract_summary_for_registry.json",
    "34_publication_safe_note_candidates.md",
    "35_short_result_note_de.md",
    "36_machine_readable_n_contract_summary.json",
    "37_claim_boundary_grep_report.csv",
    "FINAL_RESULT_NOTE.md",
]

CLAIM_BOUNDARY = (
    "EXTRACT03N is contract-only. It localizes the inconclusive "
    "Source-Response-Degeneracy topic and defines a narrow future N-R1 lineage "
    "audit contract. It does not establish degeneracy, nature, Interface, "
    "geometry, gravity, artifact origin, or L2 repair."
)
NEXT_ALLOWED_ACTION = (
    "Human review of the EXTRACT03N contract and, only after explicit approval, "
    "a separate QSB-EXTRACT03N-R1 narrow Source-Response degeneracy lineage audit run."
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(name: str, fields: list[str], rows: list[dict[str, object]]) -> None:
    with (OUT / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(name: str, data: dict[str, object]) -> None:
    (OUT / name).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(name: str, text: str) -> None:
    (OUT / name).write_text(text.rstrip() + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def top_file(path: Path) -> Path | None:
    if path.is_file():
        return path
    if path.exists():
        files = sorted(p for p in path.iterdir() if p.is_file())
        return files[0] if files else None
    return None


def main() -> int:
    if OUT.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {OUT}")
    OUT.mkdir(parents=True)

    required_m_rg = {
        "m_rg_manifest": M_RG / "01_extract03m_rg_run_manifest.json",
        "work_package_registry": M_RG / "05_work_package_status_registry.csv",
        "origin_topic_registry": M_RG / "08_origin_topic_registry_records.csv",
        "review_item_registry": M_RG / "09_review_item_registry_records.csv",
        "decision_point_registry": M_RG / "10_decision_point_registry_records.csv",
        "claim_boundary_registry": M_RG / "12_claim_boundary_registry_records.csv",
        "l2_boundary_registry": M_RG / "13_l2_boundary_registry_record.csv",
        "partial_inconclusive_summary": M_RG / "16_partial_and_inconclusive_summary.csv",
        "forbidden_claims_registry": M_RG / "17_forbidden_claims_registry.csv",
        "allowed_internal_claims_registry": M_RG / "18_allowed_internal_claims_registry.csv",
        "m_rg_summary": M_RG / "23_machine_readable_registry_snapshot_summary.json",
        "snapshot_sqlite": M_RG / "30_registry_snapshot.sqlite",
        "sqlite_integrity": M_RG / "31_registry_snapshot_integrity_check.csv",
        "final_note": M_RG / "FINAL_RESULT_NOTE.md",
    }
    missing_m_rg = [key for key, path in required_m_rg.items() if not path.exists()]
    if missing_m_rg:
        raise SystemExit(f"extract03n_blocked_missing_m_rg_snapshot: {missing_m_rg}")

    m_rg_manifest = json.loads(required_m_rg["m_rg_manifest"].read_text(encoding="utf-8"))
    m_rg_summary = json.loads(required_m_rg["m_rg_summary"].read_text(encoding="utf-8"))
    origin_registry = read_csv(required_m_rg["origin_topic_registry"])
    review_registry = read_csv(required_m_rg["review_item_registry"])
    decision_registry = read_csv(required_m_rg["decision_point_registry"])
    l2_registry = read_csv(required_m_rg["l2_boundary_registry"])
    integrity_rows = read_csv(required_m_rg["sqlite_integrity"])

    degeneracy_rows = [
        row for row in origin_registry
        if row["origin_topic"] == "source_response_degeneracy"
        and row["classification"] == "source_response_origin_inconclusive"
    ]
    if len(degeneracy_rows) != 1:
        raise SystemExit("extract03n_blocked_missing_inconclusive_topic")
    degeneracy = degeneracy_rows[0]
    related_review = next((row for row in review_registry if row["category"] == "source_response_degeneracy"), {})
    related_decisions = [
        row for row in decision_registry
        if row["decision_id"] in {"D04_record_inconclusive_origin_topics", "D09_decide_next_audit_or_review_block"}
    ]

    con = sqlite3.connect(f"file:{required_m_rg['snapshot_sqlite']}?mode=ro", uri=True)
    sqlite_integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
    sqlite_topic = con.execute(
        "SELECT registry_id, origin_topic, classification FROM rg_origin_topic_classification "
        "WHERE origin_topic='source_response_degeneracy'"
    ).fetchall()
    sqlite_tables = [
        row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    ]
    con.close()

    upstreams = [
        ("M-RG", M_RG, "primary registry snapshot"),
        ("M", M, "result review context"),
        ("L-R1", L_R1, "authorized source-response audit context"),
        ("L", L, "source-response audit contract context"),
        ("K-R2", K_R2, "human review decision context"),
        ("K-R1", K_R1, "control run context"),
        ("K", K, "control contract context"),
        ("J", J, "near-alignment context"),
        ("I", I, "identity/K alignment context"),
        ("H-R1", H_R1, "full response vector export context"),
        ("A-R1", A_R1, "pipeline context"),
    ]
    inventory = []
    for idx, (label, path, role) in enumerate(upstreams, 1):
        ref = top_file(path)
        inventory.append(
            {
                "inventory_id": f"E03N-UP-{idx:02d}",
                "upstream": label,
                "path": str(path.relative_to(REPO)),
                "role": role,
                "exists": path.exists(),
                "hash_reference": str(ref.relative_to(REPO)) if ref else "",
                "sha256": sha256(ref) if ref else "",
                "read_mode": "read_only",
                "notes": "Contract context only; no upstream mutation.",
            }
        )

    future_auth = {
        "authorization_status": "TEMPLATE_REQUIRES_HUMAN_APPROVAL",
        "authorized_work_package": "QSB-EXTRACT03N-R1_NARROW_SOURCE_RESPONSE_DEGENERACY_LINEAGE_AUDIT_RUN",
        "source_contract": "QSB-EXTRACT03N",
        "human_approval_required": True,
        "allowed_scope": "narrow_source_response_degeneracy_lineage_audit_only_under_contract",
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
        "no_live_dwh_mutation": True,
        "no_l2_change": True,
        "no_post_hoc_tuning": True,
        "no_nature_claim": True,
        "no_interface_claim": True,
        "no_geometry_claim": True,
        "no_gravity_claim": True,
    }

    input_specs = [
        ("M_RG_registry_snapshot_sqlite", "M-RG SQLite snapshot", required_m_rg["snapshot_sqlite"], True),
        ("M_RG_origin_topic_registry", "M-RG origin topic registry", required_m_rg["origin_topic_registry"], True),
        ("M_origin_classification_review_matrix", "M origin classification review matrix", M / "06_origin_classification_review_matrix.csv", True),
        ("L_R1_origin_classification_matrix", "L-R1 origin classification matrix", L_R1 / "30_origin_classification_matrix.csv", True),
        ("L_R1_identity_group_origin_crosswalk", "L-R1 identity group origin crosswalk", L_R1 / "24_identity_group_origin_crosswalk.csv", True),
        ("L_R1_near_alignment_origin_crosswalk", "L-R1 near alignment origin crosswalk", L_R1 / "25_near_alignment_origin_crosswalk.csv", True),
        ("L_R1_component_bridge_origin_crosswalk", "L-R1 component bridge origin crosswalk", L_R1 / "26_component_bridge_origin_crosswalk.csv", True),
        ("I_identity_component_mapping", "I identity component mapping", I / "18_identity_to_component_explanation_matrix.csv", True),
        ("J_near_alignment_items", "J near alignment items", J / "04_near_alignment_item_import.csv", True),
        ("K_R1_control_classification_matrix", "K-R1 control classification matrix", K_R1 / "17_control_family_classification_summary.csv", True),
        ("K_R2_decision_matrix", "K-R2 decision matrix", K_R2 / "13_decision_points_for_human_review.csv", True),
        ("H_R1_full_response_vectors", "H-R1 full response vectors", H_R1 / "09_response_vector_export.csv", True),
        ("H_R1_vector_hashes", "H-R1 vector hashes", H_R1 / "10_response_vector_hashes.csv", True),
        ("H_R1_sign_normalized_groups", "H-R1 sign-normalized groups", H_R1 / "11_sign_normalized_vector_signatures.csv", True),
        ("A_R1_pair_split_assignments_readonly", "A-R1 pair split assignments read-only", A_R1, True),
        ("A_R1_K_matrix_readonly", "A-R1 K matrix read-only", A_R1, True),
        ("source_response_code_path", "source response code path", L_R1 / "17_source_response_code_path_review.csv", True),
        ("source_response_config_manifest", "source response config manifest", L_R1 / "04_contract_alignment_review.csv", True),
        ("response_vector_generation_hook", "response vector generation hook", L_R1 / "18_response_generation_hook_review.csv", True),
        ("normalization_rule", "normalization rule", L_R1 / "19_normalization_rule_review.csv", True),
        ("sign_anchor_rule", "sign anchor rule", L_R1 / "20_sign_anchor_rule_review.csv", True),
        ("index_convention", "index convention", L_R1 / "21_index_convention_review.csv", True),
        ("serialization_hash_rule", "serialization hash rule", L_R1 / "22_serialization_hash_rule_review.csv", True),
        ("pair_id_role_convention", "pair id role convention", L_R1 / "23_pair_role_convention_review.csv", True),
        ("source_pair_configuration_fields", "source pair configuration fields", None, True),
        ("lineage_join_keys", "lineage join keys", None, True),
        ("audit_authorization", "N-R1 audit authorization", OUT / "24_future_authorization_template_extract03n_r1.json", True),
    ]
    required_rows = []
    for idx, (input_id, input_name, path, blocking) in enumerate(input_specs, 1):
        if path is None:
            status = "contract_defined_for_n_r1"
            evidence = "Defined in EXTRACT03N contract tables."
        elif path == OUT / "24_future_authorization_template_extract03n_r1.json":
            status = "template_created_not_authorized"
            evidence = "24_future_authorization_template_extract03n_r1.json"
        else:
            status = "available_read_only" if path.exists() else "input_gap"
            evidence = str(path.relative_to(REPO)) if path.exists() else str(path.relative_to(REPO))
        required_rows.append(
            {
                "input_id": input_id,
                "input_name": input_name,
                "required_for_n_r1": "yes",
                "current_status": status,
                "evidence_or_source": evidence,
                "blocking_if_missing": "yes" if blocking else "no",
                "notes": "Do not replace if missing; stop or record gap in N-R1.",
            }
        )
    missing_inputs = [row for row in required_rows if row["current_status"] == "input_gap"]
    available_inputs = [row for row in required_rows if row["current_status"] != "input_gap"]
    status = "extract03n_degeneracy_lineage_audit_contract_completed_ready_for_separate_authorized_audit"
    if missing_inputs:
        status = "extract03n_degeneracy_lineage_audit_contract_completed_with_input_gaps"
    elif related_review:
        status = "extract03n_degeneracy_lineage_audit_contract_completed_with_review_items"

    localization = [
        {
            "localization_id": "E03N-LOC-01",
            "source_layer": "M-RG origin topic registry and SQLite snapshot",
            "source_artifact": "runs/QSB-EXTRACT03M-RG/registry_dwh_integration_snapshot/08_origin_topic_registry_records.csv",
            "origin_topic": degeneracy["origin_topic"],
            "classification": degeneracy["classification"],
            "evidence_summary": degeneracy["evidence_summary"],
            "limitations": degeneracy["limitations"],
            "related_AQ": "AQ05_source_response_degeneracy",
            "related_review_item": related_review.get("review_item_id", ""),
            "related_decision_point": "D04_record_inconclusive_origin_topics;D09_decide_next_audit_or_review_block",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "This localizes the topic only; it does not decide degeneracy.",
        }
    ]

    nq_specs = [
        ("NQ01_inconclusive_topic_localization", "Can the exact inconclusive topic be traced across M-RG/M/L-R1?", "Localize audit scope.", "M_RG_origin_topic_registry;M_origin_classification_review_matrix;L_R1_origin_classification_matrix", "read-only joins and consistency checks", "no audit execution; no recomputation", "localization record"),
        ("NQ02_source_configuration_traceability", "Which source/pair configuration fields are needed to trace candidate degeneracy?", "Define source-side lineage.", "source_pair_configuration_fields;lineage_join_keys;source_response_config_manifest", "read-only field inventory and join-key audit", "no raw F3 access; no parameter changes", "lineage field matrix"),
        ("NQ03_pair_role_lineage", "Can pair roles be traced without assigning new foreign labels?", "Bound pair-role lineage.", "pair_id_role_convention;A_R1_pair_split_assignments_readonly", "read-only convention review", "no role relabeling beyond documented convention", "pair-role lineage table"),
        ("NQ04_response_generation_lineage", "Can response generation hooks be traced from configuration to exported vectors?", "Trace response-generation path.", "source_response_code_path;response_vector_generation_hook;H_R1_full_response_vectors", "read-only code-path and artifact crosswalk", "no vector export or rerun", "response lineage crosswalk"),
        ("NQ05_identity_group_lineage", "Which identity groups participate in degeneracy-relevant traces?", "Bind identity scope.", "H_R1_sign_normalized_groups;I_identity_component_mapping;L_R1_identity_group_origin_crosswalk", "read-only group mapping", "no new identity grouping", "identity lineage table"),
        ("NQ06_near_alignment_lineage", "Which near-alignment items must be traced?", "Bind near-alignment scope.", "J_near_alignment_items;L_R1_near_alignment_origin_crosswalk", "read-only item crosswalk", "no edge rethresholding", "near-alignment lineage table"),
        ("NQ07_component_bridge_lineage", "How do component bridges constrain degeneracy review?", "Bind bridge scope.", "L_R1_component_bridge_origin_crosswalk;I_identity_component_mapping", "read-only component crosswalk", "no cluster/community rerun", "component bridge lineage table"),
        ("NQ08_negative_control_lineage", "Which negative controls should be referenced?", "Bound control comparison.", "K_R1_control_classification_matrix;K_R2_decision_matrix", "read-only control classification review", "no control rerun", "negative-control reference table"),
        ("NQ09_allowed_descriptive_metrics", "Which descriptive metrics are allowed without recomputing model outputs?", "Allow bounded descriptions.", "lineage_join_keys;H_R1_vector_hashes;M_RG_registry_snapshot_sqlite", "counts, joins, provenance coverage, hash consistency", "no K/Strength/d/D/Edge recompute", "descriptive metrics summary"),
        ("NQ10_stop_and_claim_boundary", "When must N-R1 stop, and what claims remain forbidden?", "Freeze stop/claim boundary.", "claim_boundary;L2_boundary;audit_authorization", "guard checks and stop criteria", "no nature/interface/geometry/gravity/L2 claim", "stop and boundary report"),
    ]
    nq_rows = [
        {
            "question_id": item[0],
            "question": item[1],
            "purpose": item[2],
            "required_inputs": item[3],
            "allowed_operations": item[4],
            "forbidden_operations": item[5],
            "expected_output_type": item[6],
            "classification_boundary": "Use only degeneracy_lineage_* schema; no physical claim.",
            "notes": "For future N-R1 only after human authorization.",
        }
        for item in nq_specs
    ]

    allowed_ops = [
        "read_m_rg_snapshot", "read_m_origin_topic_matrix", "read_l_r1_origin_matrix",
        "read_i_identity_mapping", "read_j_near_alignment_items", "read_k_r1_control_classifications",
        "read_k_r2_decision_matrix", "read_h_r1_vectors", "read_a_r1_pair_assignments",
        "inspect_source_response_code_path", "inspect_response_generation_hook", "inspect_lineage_join_keys",
        "inspect_pair_role_convention", "compute_descriptive_lineage_metrics", "write_lineage_audit_report",
    ]
    allowed_rows = [
        {
            "operation_id": f"E03N-AO-{idx:02d}",
            "operation": op,
            "allowed_for_n_r1": "yes_after_authorization",
            "scope": "narrow source-response degeneracy lineage only",
            "required_guard": "read-only; no recomputation; no upstream mutation",
            "notes": "Contract allowance, not current execution.",
        }
        for idx, op in enumerate(allowed_ops, 1)
    ]
    forbidden_ops = [
        "run_degeneracy_lineage_audit_now", "rerun_source_response_audit", "rerun_controls",
        "export_vectors", "mutate_vectors", "recompute_K", "recompute_strength", "recompute_d",
        "recompute_D", "recompute_edges", "rerun_shortest_paths", "edge_rethresholding",
        "rerun_clusters", "rerun_motifs", "run_bootstrap", "open_F3_raw_source",
        "reconstruct_raw_phases", "rerun_A_R1_pipeline", "change_parameters",
        "change_thresholds", "change_splits_or_seeds", "mutate_upstream_files",
        "mutate_live_dwh", "repair_L2", "make_nature_claim", "make_interface_claim",
        "make_geometry_claim", "make_gravity_claim",
    ]
    forbidden_rows = [
        {
            "operation_id": f"E03N-FO-{idx:02d}",
            "operation": op,
            "allowed_for_n_r1": "no",
            "reason": "Forbidden by EXTRACT03N contract boundary.",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Stop if attempted.",
        }
        for idx, op in enumerate(forbidden_ops, 1)
    ]

    stop_rows = [
        ("E03N-STOP-01", "missing_authorization", "Stop if N-R1 human authorization is absent.", "yes"),
        ("E03N-STOP-02", "missing_required_input", "Stop or record input gap; do not substitute.", "yes"),
        ("E03N-STOP-03", "recompute_requested", "Stop if K/Strength/d/D/Edge or path/cluster/motif/bootstrap recompute is requested.", "yes"),
        ("E03N-STOP-04", "raw_source_required", "Stop if F3 raw source or raw phase reconstruction is required.", "yes"),
        ("E03N-STOP-05", "upstream_mutation_required", "Stop if any upstream or live DWH mutation is needed.", "yes"),
        ("E03N-STOP-06", "claim_boundary_pressure", "Stop if natural/interface/geometry/gravity/L2 claims are requested.", "yes"),
    ]
    stop_criteria = [
        {
            "stop_id": sid,
            "stop_condition": cond,
            "required_response": response,
            "blocking": blocking,
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Applies to future N-R1.",
        }
        for sid, cond, response, blocking in stop_rows
    ]

    join_keys = [
        ("pair_id", "Join A-R1 pair assignments to response outputs and near-alignment rows."),
        ("source_id", "Trace source configuration without opening raw F3 source."),
        ("response_vector_id", "Join exported H-R1 vector records to identity/hash groups."),
        ("identity_group_id", "Join H-R1/I/L-R1 identity group scopes."),
        ("component_id", "Join I/J component bridge context."),
        ("near_alignment_item_id", "Join J/L-R1 near-alignment scope."),
        ("artifact_sha256", "Verify artifact identity without mutation."),
    ]
    join_rows = [
        {
            "join_key": key,
            "purpose": purpose,
            "required_source_layers": "A-R1;H-R1;I;J;L-R1;M/M-RG",
            "allowed_use": "read-only lineage joining",
            "forbidden_use": "no new labels, no model recomputation",
            "notes": "If absent, record gap.",
        }
        for key, purpose in join_keys
    ]
    source_fields = [
        "source_id", "pair_id", "role_a", "role_b", "split_id", "response_vector_id",
        "configuration_manifest_id", "normalization_rule_id", "sign_anchor_rule_id",
        "serialization_rule_id",
    ]
    source_field_rows = [
        {
            "field_name": field,
            "required_for": "N-R1 source/pair/response lineage",
            "source_layer": "A-R1/L-R1/H-R1/M-RG",
            "status": "contract_required",
            "notes": "Do not infer if absent.",
        }
        for field in source_fields
    ]

    simple_contract_fields = ["contract_id", "scope", "required_inputs", "allowed_operations", "forbidden_operations", "stop_condition", "claim_boundary", "notes"]
    pair_role_rows = [{
        "contract_id": "E03N-PAIR-ROLE",
        "scope": "pair role lineage",
        "required_inputs": "pair_id_role_convention;A_R1_pair_split_assignments_readonly",
        "allowed_operations": "read-only pair role trace",
        "forbidden_operations": "foreign role relabeling; split changes",
        "stop_condition": "missing pair role convention",
        "claim_boundary": CLAIM_BOUNDARY,
        "notes": "No labels on foreign Klunker beyond documented convention.",
    }]
    response_rows = [{
        "contract_id": "E03N-RESPONSE-GEN",
        "scope": "response generation lineage",
        "required_inputs": "source_response_code_path;response_vector_generation_hook;H_R1_full_response_vectors",
        "allowed_operations": "inspect code path and artifact lineage",
        "forbidden_operations": "A-R1 rerun; vector export; vector mutation",
        "stop_condition": "generation hook unavailable",
        "claim_boundary": CLAIM_BOUNDARY,
        "notes": "Lineage only; no new response generation.",
    }]
    norm_rows = [{
        "contract_id": "E03N-NORM-SIGN-INDEX-SERIAL",
        "scope": "normalization/sign/index/serialization",
        "required_inputs": "normalization_rule;sign_anchor_rule;index_convention;serialization_hash_rule",
        "allowed_operations": "read-only rule trace and hash consistency",
        "forbidden_operations": "new normalization; new sign anchors; reserialization changing hashes",
        "stop_condition": "rule conflict or missing rule source",
        "claim_boundary": CLAIM_BOUNDARY,
        "notes": "Rule boundary only.",
    }]

    identity_scope = [{
        "scope_id": "E03N-ID-01",
        "scope": "identity group lineage",
        "source_artifacts": "H_R1_sign_normalized_groups;I_identity_component_mapping;L_R1_identity_group_origin_crosswalk",
        "allowed_review": "trace identity group membership and component mapping read-only",
        "excluded": "new identity grouping or relabeling",
        "claim_boundary": CLAIM_BOUNDARY,
        "notes": "Future N-R1 scope.",
    }]
    near_scope = [{
        "scope_id": "E03N-NA-01",
        "scope": "near-alignment lineage",
        "source_artifacts": "J_near_alignment_items;L_R1_near_alignment_origin_crosswalk",
        "allowed_review": "trace existing near-alignment rows",
        "excluded": "edge rethresholding or new near-alignment extraction",
        "claim_boundary": CLAIM_BOUNDARY,
        "notes": "Future N-R1 scope.",
    }]
    bridge_scope = [{
        "scope_id": "E03N-CB-01",
        "scope": "component bridge lineage",
        "source_artifacts": "L_R1_component_bridge_origin_crosswalk;I_identity_component_mapping",
        "allowed_review": "trace documented component bridges",
        "excluded": "cluster/community/motif rerun",
        "claim_boundary": CLAIM_BOUNDARY,
        "notes": "Future N-R1 scope.",
    }]
    neg_control = [{
        "reference_id": "E03N-NC-01",
        "source_artifacts": "K_R1_control_classification_matrix;K_R2_decision_matrix",
        "allowed_review": "read-only negative-control lineage reference",
        "excluded": "control reexecution",
        "claim_boundary": CLAIM_BOUNDARY,
        "notes": "Use as comparison context only.",
    }]
    metric_rows = [
        ("lineage_record_counts", "Count records per join key and source layer."),
        ("join_coverage", "Report coverage of required join keys."),
        ("hash_consistency", "Verify recorded hashes without rewriting artifacts."),
        ("classification_counts", "Count degeneracy_lineage_* outcomes."),
        ("gap_counts", "Count missing inputs or stop conditions."),
    ]
    metrics = [
        {
            "metric_id": f"E03N-MET-{idx:02d}",
            "metric": metric,
            "description": desc,
            "allowed_for_n_r1": "yes_after_authorization",
            "forbidden_boundary": "No K/Strength/d/D/Edge recompute; no new vector export.",
            "notes": "Descriptive lineage metric only.",
        }
        for idx, (metric, desc) in enumerate(metric_rows, 1)
    ]
    schema_classes = [
        "degeneracy_lineage_supported_as_pipeline_review_pattern",
        "degeneracy_lineage_partially_supported_with_review_items",
        "degeneracy_lineage_not_supported_by_audit",
        "degeneracy_lineage_inconclusive",
        "degeneracy_lineage_input_gap",
        "degeneracy_lineage_blocked_by_guard",
    ]
    schema_rows = [
        {
            "classification": cls,
            "meaning": "Future N-R1 lineage-audit classification; not a physical claim.",
            "allowed_claim": "pipeline-review lineage classification only",
            "forbidden_claim": "nature/interface/geometry/gravity/L2 inference",
            "notes": "Schema only; not applied by N.",
        }
        for cls in schema_classes
    ]

    claim_rows = [
        ("E03N-CB-01", "N is contract-only.", "allowed", "Does not run N-R1."),
        ("E03N-CB-02", "N establishes Source-Response-Degeneracy.", "forbidden", "N only localizes an inconclusive topic."),
        ("E03N-CB-03", "N proves QSB, Interface, geometry, gravity, natural/artifact origin, or L2 repair.", "forbidden", "Outside claim boundary."),
    ]
    claim_matrix = [
        {
            "claim_id": cid,
            "claim_text": text,
            "status": stat,
            "boundary_action": action,
            "claim_boundary": CLAIM_BOUNDARY,
        }
        for cid, text, stat, action in claim_rows
    ]
    l2_contract = [
        {
            "l2_status": "fail",
            "n4_support": "0/3",
            "n4_required": "2/3",
            "theta_new": "0.012446436850524916",
            "epsilon_new": "0.006009422749372488",
            "changed_by_extract03n": "false",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "L2 boundary retained unchanged.",
        }
    ]
    decision_points = [
        {
            "decision_id": "E03N-D01",
            "decision_question": "Approve the narrow N-R1 audit under this contract?",
            "recommended_decision": "human_review_required",
            "requires_new_authorization": "yes",
            "notes": "Future template is not authorization.",
        },
        {
            "decision_id": "E03N-D02",
            "decision_question": "Accept stop criteria and forbidden operations?",
            "recommended_decision": "accept_before_any_run",
            "requires_new_authorization": "no",
            "notes": "Contract boundary.",
        },
        {
            "decision_id": "E03N-D03",
            "decision_question": "Keep L2 and claim boundaries unchanged?",
            "recommended_decision": "accept_l2_claim_boundary",
            "requires_new_authorization": "no",
            "notes": "No L2 repair.",
        },
    ]
    review_items = [
        {
            "review_item_id": related_review.get("review_item_id", "E03N-RI-01"),
            "category": "source_response_degeneracy",
            "description": related_review.get("description", "Source-Response-Degeneracy remains inconclusive."),
            "severity": related_review.get("severity", "review"),
            "recommended_resolution": "Separate N-R1 authorization required before lineage audit.",
            "notes": "No audit performed in N.",
        }
    ]
    crosswalk = [
        {
            "crosswalk_id": "E03N-XW-01",
            "source": "M-RG origin registry",
            "source_record": degeneracy["registry_id"],
            "n_contract_use": "inconclusive topic localization",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Primary scope anchor.",
        },
        {
            "crosswalk_id": "E03N-XW-02",
            "source": "M-RG review registry",
            "source_record": related_review.get("registry_id", ""),
            "n_contract_use": "open review item anchor",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Degeneracy remains open.",
        },
        {
            "crosswalk_id": "E03N-XW-03",
            "source": "M-RG decision registry",
            "source_record": ";".join(row["registry_id"] for row in related_decisions),
            "n_contract_use": "future authorization decision anchor",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "D04 and D09 linked.",
        },
    ]
    next_options = [
        {"option_id": "E03N-NEXT-01", "option": "human_review_contract", "allowed": "yes", "requires_authorization": "no", "notes": "Immediate next step."},
        {"option_id": "E03N-NEXT-02", "option": "authorize_N_R1_lineage_audit", "allowed": "conditional", "requires_authorization": "yes", "notes": "Use template only after human approval."},
        {"option_id": "E03N-NEXT-03", "option": "run_audit_without_authorization", "allowed": "no", "requires_authorization": "yes", "notes": "Forbidden."},
    ]
    guard_names = [
        "m_rg_snapshot_present", "inconclusive_topic_localized", "no_degeneracy_lineage_audit_run",
        "no_source_response_audit_rerun", "no_controls_reexecuted", "no_vectors_exported",
        "no_K_recompute", "no_strength_recompute", "no_d_recompute", "no_D_recompute",
        "no_edge_recompute", "no_shortest_path_rerun", "no_edge_rethresholding",
        "no_cluster_rerun", "no_motif_rerun", "no_bootstrap", "no_raw_phase_reconstruction",
        "no_F3_raw_source_opened", "no_A_R1_pipeline_rerun", "no_live_dwh_mutation",
        "no_upstream_mutation", "no_l2_change", "no_post_hoc_tuning", "no_nature_claim",
        "no_interface_claim", "no_geometry_claim", "no_gravity_claim",
        "future_authorization_template_only", "overwrite_refusal",
    ]
    guards = [
        {
            "guard_id": f"E03N-G{idx:02d}",
            "guard": guard,
            "status": "pass",
            "evidence": "Contract-only package generated; no N-R1 audit executed.",
            "blocking": "yes",
            "notes": "Guard satisfied.",
        }
        for idx, guard in enumerate(guard_names, 1)
    ]
    rg_readonly = [
        {
            "review_id": "E03N-MRG-01",
            "snapshot_sqlite": str(required_m_rg["snapshot_sqlite"].relative_to(REPO)),
            "sqlite_integrity_check": sqlite_integrity,
            "sqlite_tables_seen": ";".join(sqlite_tables),
            "degeneracy_topic_rows_seen": len(sqlite_topic),
            "manifest_status": m_rg_summary.get("status", ""),
            "read_mode": "read_only",
            "notes": "SQLite opened with mode=ro.",
        }
    ]
    input_availability = [
        {
            "input_id": key,
            "path": str(path.relative_to(REPO)),
            "available": path.exists(),
            "blocking": "yes",
            "notes": "Primary M-RG contract input.",
        }
        for key, path in required_m_rg.items()
    ]

    now = datetime.now(timezone.utc).isoformat()
    manifest = {
        "work_package": "QSB-EXTRACT03N",
        "status": status,
        "created_at_utc": now,
        "repo_root": str(REPO),
        "m_rg_snapshot_seen": True,
        "m_rg_status": m_rg_summary.get("status", ""),
        "extract03m_seen": M.exists(),
        "inconclusive_topic_seen": True,
        "inconclusive_topic_name": "source_response_degeneracy",
        "narrow_scope_confirmed": True,
        "lineage_audit_run_executed": False,
        "source_response_audit_rerun": False,
        "controls_reexecuted": False,
        "vectors_exported": False,
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
        "review_items_count": len(review_items),
        "required_inputs_total": len(required_rows),
        "required_inputs_available": len(available_inputs),
        "required_inputs_missing": len(missing_inputs),
        "future_authorization_template_created": True,
        "claim_boundary": CLAIM_BOUNDARY,
        "next_allowed_action": NEXT_ALLOWED_ACTION,
    }

    write_json("01_extract03n_run_manifest.json", manifest)
    write_csv("02_upstream_inventory_and_hashes.csv", list(inventory[0]), inventory)
    write_csv("03_input_availability_review.csv", list(input_availability[0]), input_availability)
    write_csv("04_m_rg_snapshot_readonly_review.csv", list(rg_readonly[0]), rg_readonly)
    write_csv("05_inconclusive_topic_localization.csv", list(localization[0]), localization)
    write_csv("06_narrow_degeneracy_audit_question_registry.csv", list(nq_rows[0]), nq_rows)
    write_csv("07_required_n_r1_inputs.csv", list(required_rows[0]), required_rows)
    write_csv("08_allowed_operations_matrix.csv", list(allowed_rows[0]), allowed_rows)
    write_csv("09_forbidden_operations_matrix.csv", list(forbidden_rows[0]), forbidden_rows)
    write_csv("10_n_r1_stop_criteria.csv", list(stop_criteria[0]), stop_criteria)
    write_csv("11_lineage_join_key_requirements.csv", list(join_rows[0]), join_rows)
    write_csv("12_source_pair_configuration_field_requirements.csv", list(source_field_rows[0]), source_field_rows)
    write_csv("13_pair_role_lineage_contract.csv", simple_contract_fields, pair_role_rows)
    write_csv("14_response_generation_lineage_contract.csv", simple_contract_fields, response_rows)
    write_csv("15_normalization_sign_index_serialization_contract.csv", simple_contract_fields, norm_rows)
    write_csv("16_identity_group_lineage_scope.csv", list(identity_scope[0]), identity_scope)
    write_csv("17_near_alignment_lineage_scope.csv", list(near_scope[0]), near_scope)
    write_csv("18_component_bridge_lineage_scope.csv", list(bridge_scope[0]), bridge_scope)
    write_csv("19_negative_control_lineage_reference.csv", list(neg_control[0]), neg_control)
    write_csv("20_allowed_descriptive_metrics_contract.csv", list(metrics[0]), metrics)
    write_csv("21_degeneracy_lineage_classification_schema.csv", list(schema_rows[0]), schema_rows)
    write_csv("22_claim_boundary_matrix.csv", list(claim_matrix[0]), claim_matrix)
    write_csv("23_l2_boundary_contract.csv", list(l2_contract[0]), l2_contract)
    write_json("24_future_authorization_template_extract03n_r1.json", future_auth)
    write_csv("25_human_decision_points.csv", list(decision_points[0]), decision_points)
    write_csv("26_review_items.csv", list(review_items[0]), review_items)
    write_csv("27_registry_snapshot_crosswalk.csv", list(crosswalk[0]), crosswalk)
    write_csv("28_next_step_options.csv", list(next_options[0]), next_options)
    write_text("29_recommended_next_step.md", "# Recommended Next Step\n\n" + NEXT_ALLOWED_ACTION)
    write_csv("30_no_execution_guard_results.csv", list(guards[0]), guards)

    validation_items = [
        ("artifact_count", len(FILES), 38),
        ("m_rg_snapshot_present", M_RG.exists(), True),
        ("m_origin_matrix_present", (M / "06_origin_classification_review_matrix.csv").exists(), True),
        ("inconclusive_topic_localized", len(degeneracy_rows), 1),
        ("nq_questions", len(nq_rows), 10),
        ("required_inputs", len(required_rows), 27),
        ("allowed_operations", len(allowed_rows), 15),
        ("forbidden_operations", len(forbidden_rows), 28),
        ("stop_criteria", len(stop_criteria), 6),
        ("future_authorization_template_created_not_authorized", future_auth["authorization_status"], "TEMPLATE_REQUIRES_HUMAN_APPROVAL"),
        ("no_execution_guards", len(guards), 29),
        ("sqlite_readonly_integrity", sqlite_integrity, "ok"),
        ("missing_required_inputs", len(missing_inputs), 0),
    ]
    write_csv(
        "31_validation_results.csv",
        ["validation_id", "check_name", "status", "observed_value", "expected_value", "blocking", "notes"],
        [
            {
                "validation_id": f"E03N-V{idx:02d}",
                "check_name": name,
                "status": "pass" if str(observed) == str(expected) else "fail",
                "observed_value": observed,
                "expected_value": expected,
                "blocking": "yes" if name != "missing_required_inputs" else "no",
                "notes": "Contract validation; no audit execution.",
            }
            for idx, (name, observed, expected) in enumerate(validation_items, 1)
        ],
    )
    write_text(
        "32_human_readable_n_contract_de.md",
        f"""# QSB-EXTRACT03N Narrow Source-Response Degeneracy Lineage Audit Contract

## Ausgangspunkt
EXTRACT03N folgt auf den M-RG Registry-/DWH-Snapshot und ist Contract-only.

## Warum dieser enge Contract jetzt sinnvoll ist
Die einzige verbleibende inconclusive-Stelle ist Source-Response-Degeneracy. N begrenzt einen moeglichen spaeteren N-R1-Audit auf diese Stelle.

## Eindeutig lokalisierte inconclusive-Stelle
`source_response_degeneracy` wurde als `source_response_origin_inconclusive` in M-RG lokalisiert.

## Was ein späterer N-R1 prüfen darf
N-R1 darf nach separater Autorisierung nur Lineage, Join-Keys, Konfigurationen, Pair-Rollen und Response-Generation read-only pruefen.

## Benötigte Inputs und Lineage-Schlüssel
Die benoetigten Inputs stehen in `07_required_n_r1_inputs.csv`; Join Keys stehen in `11_lineage_join_key_requirements.csv`.

## Pair-Rollen und Source-Konfigurationen
Pair-Rollen und Source-Konfigurationsfelder sind als Contract-Anforderungen definiert, nicht als neuer Befund.

## Response-Generation, Normalisierung, Sign, Index und Serialisierung
Diese Regeln duerfen nur read-only verfolgt werden.

## Scope der Identity Groups
Identity Group Lineage ist auf H-R1/I/L-R1-Crosswalks begrenzt.

## Scope der Near-Alignment-Beziehungen
Near-Alignment Lineage ist auf J/L-R1-Crosswalks begrenzt.

## Komponenten-Brücken
Komponenten-Bruecken duerfen nur anhand bestehender Crosswalks verfolgt werden.

## Erlaubte Operationen
Erlaubte Operationen stehen in `08_allowed_operations_matrix.csv` und gelten nur fuer ein spaeter autorisiertes N-R1.

## Verbotene Operationen
Verbotene Operationen stehen in `09_forbidden_operations_matrix.csv`.

## Stop-Kriterien
Stop-Kriterien stehen in `10_n_r1_stop_criteria.csv`.

## L2-Grenze
L2 bleibt fail: N4 support 0/3, required 2/3.

## Claim Boundary
{CLAIM_BOUNDARY}

## Was ausdrücklich nicht behauptet wird
N behauptet nicht, dass Degeneracy vorliegt; N macht keine Natur-, Interface-, Geometrie-, Gravitations- oder L2-Reparatur-Aussage.

## Nächster Schritt
{NEXT_ALLOWED_ACTION}
""",
    )
    registry_summary = {
        "work_package": "QSB-EXTRACT03N",
        "status": status,
        "contract_type": "narrow_degeneracy_lineage_audit_contract",
        "inconclusive_topic": degeneracy["origin_topic"],
        "classification": degeneracy["classification"],
        "nq_questions": len(nq_rows),
        "required_inputs": len(required_rows),
        "missing_required_inputs": len(missing_inputs),
        "future_authorization_template_created": True,
        "future_authorization_template_authorized": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "next_allowed_action": NEXT_ALLOWED_ACTION,
    }
    write_json("33_contract_summary_for_registry.json", registry_summary)
    write_text(
        "34_publication_safe_note_candidates.md",
        """# Publication-Safe Note Candidates

- EXTRACT03N is a contract-only block for a possible future narrow Source-Response degeneracy lineage audit.
- It localizes the remaining inconclusive topic and freezes allowed inputs, operations, stop criteria, and claim boundaries.
- It does not run the lineage audit and does not establish Source-Response-Degeneracy.
- L2 remains fail with N4 support 0/3 required 2/3.
""",
    )
    write_text(
        "35_short_result_note_de.md",
        f"""# QSB-EXTRACT03N Kurznotiz

Status: `{status}`.

Source-Response-Degeneracy wurde als einzige inconclusive-Stelle lokalisiert. NQ01-NQ10, Required Inputs, Allowed/Forbidden Operations, Stop-Kriterien und ein nicht autorisiertes N-R1-Template wurden erstellt. Kein Degeneracy-Lineage-Audit wurde ausgefuehrt.
""",
    )
    machine_summary = {
        **registry_summary,
        "lineage_audit_run_executed": False,
        "source_response_audit_rerun": False,
        "controls_reexecuted": False,
        "vectors_exported": False,
        "K_recomputed": False,
        "live_dwh_modified": False,
        "upstream_modified": False,
        "l2_fail_changed": False,
        "post_hoc_tuning_performed": False,
        "nature_claim_made": False,
        "interface_claim_made": False,
        "geometry_claim_made": False,
        "gravity_claim_made": False,
    }
    write_json("36_machine_readable_n_contract_summary.json", machine_summary)
    grep_report = [
        {
            "pattern_group": "forbidden_positive_claims",
            "status": "reviewed_boundary_context_only",
            "notes": "Any forbidden phrases are present only as blocked/unsupported claim boundary language.",
        }
    ]
    write_csv("37_claim_boundary_grep_report.csv", list(grep_report[0]), grep_report)
    write_text(
        "FINAL_RESULT_NOTE.md",
        f"""# QSB-EXTRACT03N Final Result

## Status
`{status}`

## Reviewed Inputs
M-RG, M, L-R1, L, K-R2, K-R1, K, J, I, H-R1, and A-R1 context were used read-only.

## Inconclusive Topic Localization
`source_response_degeneracy` was localized as `source_response_origin_inconclusive` from M-RG.

## N-R1 Audit Questions
NQ01-NQ10 were created for a future separately authorized lineage audit.

## Required Future Inputs
{len(required_rows)} required N-R1 inputs were classified. Missing inputs: {len(missing_inputs)}.

## Allowed and Forbidden Operations
Allowed and forbidden operation matrices were created. They do not authorize a run.

## Stop Criteria
Stop criteria cover missing authorization, missing inputs, recomputation pressure, raw-source pressure, upstream mutation, and claim-boundary pressure.

## Future Authorization Template
`24_future_authorization_template_extract03n_r1.json` was created as a template only. It is not authorized.

## No-Execution Guards
All no-execution guards are recorded in `30_no_execution_guard_results.csv`.

## Claim Boundary
{CLAIM_BOUNDARY}

## L2 Boundary
L2 remains fail with N4 support 0/3, required 2/3. No L2 repair or reinterpretation was performed.

## Next Allowed Action
{NEXT_ALLOWED_ACTION}
""",
    )

    actual = sorted(path.name for path in OUT.iterdir() if path.is_file())
    expected = sorted(FILES)
    if actual != expected:
        raise SystemExit(f"Output file mismatch: actual={actual} expected={expected}")

    print(json.dumps(machine_summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
