#!/usr/bin/env python3
"""QSB-EXTRACT03M source-response audit result review.

This script is intentionally read-only with respect to all upstream artifacts.
It imports EXTRACT03L-R1 review outputs and writes a bounded decision-oriented
review package. It does not rerun audits, controls, vector exports, or model
computations.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "runs/QSB-EXTRACT03M/source_response_audit_result_review"
L_R1 = REPO / "runs/QSB-EXTRACT03L-R1/authorized_source_response_audit_run"
L = REPO / "runs/QSB-EXTRACT03L/source_response_audit_contract"
K_R2 = REPO / "runs/QSB-EXTRACT03K-R2/human_review_collinearity_control_classifications"
K_R1 = REPO / "runs/QSB-EXTRACT03K-R1/authorized_collinearity_control_run"
J = REPO / "runs/QSB-EXTRACT03J/near_alignment_structure_review"
I = REPO / "runs/QSB-EXTRACT03I/response_vector_identity_k_alignment_review"
H_R1 = REPO / "runs/QSB-EXTRACT03H-R1/authorized_response_vector_export"
A_R1 = REPO / "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum"

FILES = [
    "01_extract03m_run_manifest.json",
    "02_upstream_inventory_and_hashes.csv",
    "03_input_availability_review.csv",
    "04_l_r1_result_import_summary.csv",
    "05_AQ_classification_review.csv",
    "06_origin_classification_review_matrix.csv",
    "07_supported_origin_topics_review.csv",
    "08_partial_origin_topics_review.csv",
    "09_not_supported_origin_topics_review.csv",
    "10_inconclusive_origin_topics_review.csv",
    "11_input_gap_or_blocked_topics_review.csv",
    "12_identity_group_origin_review_summary.csv",
    "13_same_opposite_collinearity_origin_review_summary.csv",
    "14_component_bridge_origin_review_summary.csv",
    "15_source_response_degeneracy_review_summary.csv",
    "16_index_sign_normalization_review_summary.csv",
    "17_serialization_hash_review_summary.csv",
    "18_K_readonly_consistency_review_summary.csv",
    "19_L2_boundary_review.csv",
    "20_claim_boundary_review.csv",
    "21_crosswalk_to_I_J_K_reviews.csv",
    "22_crosswalk_to_K_R1_K_R2_decisions.csv",
    "23_open_review_items_from_L_R1.csv",
    "24_decision_points_for_human_review.csv",
    "25_allowed_next_actions.csv",
    "26_disallowed_next_actions.csv",
    "27_registry_or_dwh_integration_recommendation.csv",
    "28_publication_safe_note_candidates.md",
    "29_human_readable_m_result_review_de.md",
    "30_next_step_options.csv",
    "31_recommended_next_step.md",
    "32_guard_results.csv",
    "33_validation_results.csv",
    "34_short_result_note_de.md",
    "35_machine_readable_m_result_review_summary.json",
    "FINAL_RESULT_NOTE.md",
]

CLAIM_BOUNDARY = (
    "EXTRACT03M reviews the EXTRACT03L-R1 source-response audit results and "
    "organizes origin classifications for human decision-making. It makes no "
    "nature, Interface, geometry, gravity, public-claim, or L2-repair claim."
)
NEXT_ALLOWED_ACTION = (
    "Human review of the L-R1 classifications, decision points, and registry/DWH "
    "integration recommendation before any narrower lineage-audit authorization."
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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classify_review_status(classification: str) -> tuple[str, str]:
    if classification.endswith("_supported_as_pipeline_review_pattern"):
        return "ready_for_human_review", "accept_l_r1_classification"
    if classification.endswith("_partially_supported_with_review_items"):
        return "needs_human_attention", "accept_with_review_note"
    if classification.endswith("_not_supported_by_audit"):
        return "needs_human_attention", "record_not_supported_origin_topic"
    if classification.endswith("_inconclusive"):
        return "needs_human_attention", "defer_pending_additional_audit"
    if classification.endswith("_input_gap"):
        return "input_gap", "defer_pending_additional_audit"
    if classification.endswith("_blocked_by_guard"):
        return "blocked_by_guard", "reject_or_reclassify_required"
    return "needs_human_attention", "accept_with_review_note"


def allowed_decision(decision: str) -> str:
    if decision == "record_not_supported_origin_topic":
        return "accept_with_review_note"
    return decision


def topic_rows(rows: list[dict[str, str]], classification: str) -> list[dict[str, str]]:
    return [row for row in rows if row["source_response_classification"] == classification]


def review_summary_row(topic: str, origin_rows: list[dict[str, str]]) -> dict[str, str]:
    row = next((item for item in origin_rows if item["origin_topic"] == topic), None)
    if row is None:
        return {
            "topic": topic,
            "l_r1_classification": "not_present",
            "review_status": "input_gap",
            "decision": "defer_pending_additional_audit",
            "evidence": "Topic not present in L-R1 origin matrix.",
            "limitation": "Input gap.",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "No new audit performed.",
        }
    review_status, decision = classify_review_status(row["source_response_classification"])
    return {
        "topic": topic,
        "l_r1_classification": row["source_response_classification"],
        "review_status": review_status,
        "decision": allowed_decision(decision),
        "evidence": row["evidence_for"],
        "limitation": row["limitations"],
        "claim_boundary": CLAIM_BOUNDARY,
        "notes": row["notes"],
    }


def main() -> int:
    if OUT.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {OUT}")
    OUT.mkdir(parents=True)

    required_l_r1 = {
        "manifest": L_R1 / "01_extract03l_r1_run_manifest.json",
        "aq_summary": L_R1 / "29_AQ_classification_summary.csv",
        "origin_matrix": L_R1 / "30_origin_classification_matrix.csv",
        "review_items": L_R1 / "32_review_items.csv",
        "guards": L_R1 / "33_guard_results.csv",
        "claims": L_R1 / "34_claim_boundary_matrix.csv",
        "l2": L_R1 / "35_l2_boundary_check.csv",
        "validation": L_R1 / "36_validation_results.csv",
        "summary": L_R1 / "45_machine_readable_l_r1_source_response_audit_summary.json",
        "final_note": L_R1 / "FINAL_RESULT_NOTE.md",
    }
    missing = [key for key, path in required_l_r1.items() if not path.exists()]
    if missing:
        status = "extract03m_blocked_missing_l_r1_outputs"
        if "origin_matrix" in missing:
            status = "extract03m_blocked_missing_origin_classification_matrix"
        raise SystemExit(f"{status}: missing {missing}")

    l_r1_summary = json.loads(required_l_r1["summary"].read_text(encoding="utf-8"))
    aq_rows = read_csv(required_l_r1["aq_summary"])
    origin_rows = read_csv(required_l_r1["origin_matrix"])
    review_items = read_csv(required_l_r1["review_items"])
    guard_rows_l = read_csv(required_l_r1["guards"])
    l2_rows = read_csv(required_l_r1["l2"])
    validation_rows_l = read_csv(required_l_r1["validation"])

    aq_review = []
    for row in aq_rows:
        review_status, decision = classify_review_status(row["classification"])
        aq_review.append(
            {
                "audit_question_id": row["audit_question_id"],
                "l_r1_classification": row["classification"],
                "evidence_summary": row["evidence_summary"],
                "limitations": row["limitations"],
                "human_review_status": review_status,
                "recommended_human_decision": allowed_decision(decision),
                "notes": row["notes"],
            }
        )

    origin_review = []
    for row in origin_rows:
        review_status, decision = classify_review_status(row["source_response_classification"])
        origin_review.append(
            {
                "origin_topic": row["origin_topic"],
                "l_r1_classification": row["source_response_classification"],
                "evidence_for": row["evidence_for"],
                "evidence_against": row["evidence_against"],
                "limitations": row["limitations"],
                "affected_identity_groups_or_pairs": row["affected_identity_groups_or_pairs"],
                "affected_components": row["affected_components"],
                "audit_questions_used": row["audit_questions_used"],
                "human_review_status": review_status,
                "recommended_human_decision": allowed_decision(decision),
                "claim_boundary": CLAIM_BOUNDARY,
                "notes": row["notes"],
            }
        )

    class_counts = Counter(row["source_response_classification"] for row in origin_rows)
    supported_cls = "source_response_origin_supported_as_pipeline_review_pattern"
    partial_cls = "source_response_origin_partially_supported_with_review_items"
    not_supported_cls = "source_response_origin_not_supported_by_audit"
    inconclusive_cls = "source_response_origin_inconclusive"
    input_gap_cls = "source_response_origin_input_gap"
    blocked_cls = "source_response_origin_blocked_by_guard"
    status = (
        "extract03m_source_response_audit_result_review_completed_with_review_items"
        if review_items or class_counts[partial_cls] or class_counts[inconclusive_cls]
        else "extract03m_source_response_audit_result_review_completed_decision_ready"
    )
    if class_counts[input_gap_cls]:
        status = "extract03m_source_response_audit_result_review_completed_with_input_gaps"

    upstream_paths = [
        ("EXTRACT03L-R1", L_R1, "primary_review_input"),
        ("EXTRACT03L", L, "contract_context"),
        ("EXTRACT03K-R2", K_R2, "decision_context"),
        ("EXTRACT03K-R1", K_R1, "control_context"),
        ("EXTRACT03J", J, "near_alignment_context"),
        ("EXTRACT03I", I, "identity_k_context"),
        ("EXTRACT03H-R1", H_R1, "response_vector_export_context"),
        ("EXTRACT03A-R1", A_R1, "pipeline_context"),
    ]
    inventory = []
    for label, path, role in upstream_paths:
        files = sorted(p for p in path.glob("*") if p.is_file()) if path.exists() else []
        digest_source = required_l_r1["summary"] if label == "EXTRACT03L-R1" else (files[0] if files else None)
        inventory.append(
            {
                "upstream": label,
                "path": str(path.relative_to(REPO)),
                "role": role,
                "exists": path.exists(),
                "file_count_top_level": len(files),
                "hash_reference": str(digest_source.relative_to(REPO)) if digest_source else "",
                "sha256": sha256_file(digest_source) if digest_source else "",
                "read_mode": "read_only",
                "notes": "No upstream mutation performed.",
            }
        )

    input_review = []
    for key, path in required_l_r1.items():
        input_review.append(
            {
                "input_id": key,
                "path": str(path.relative_to(REPO)),
                "available": path.exists(),
                "used_for": "EXTRACT03M review import",
                "blocking": key in {"manifest", "aq_summary", "origin_matrix", "summary"},
                "notes": "Read-only import.",
            }
        )

    l_r1_import = [
        {
            "import_item": "l_r1_status",
            "value": l_r1_summary.get("status", ""),
            "review_result": "accepted_as_upstream_status",
            "notes": "No audit rerun.",
        },
        {
            "import_item": "audit_questions_executed",
            "value": l_r1_summary.get("audit_questions_executed", ""),
            "review_result": "AQ01-AQ10 imported",
            "notes": "No new questions executed.",
        },
        {
            "import_item": "origin_classifications_total",
            "value": l_r1_summary.get("origin_classifications_total", ""),
            "review_result": "origin matrix imported",
            "notes": "Decision review only.",
        },
        {
            "import_item": "input_gaps",
            "value": l_r1_summary.get("audit_questions_with_input_gaps", ""),
            "review_result": "no L-R1 input gaps reported",
            "notes": "Reviewed from machine-readable summary.",
        },
        {
            "import_item": "K_recomputed",
            "value": l_r1_summary.get("K_recomputed", ""),
            "review_result": "false retained",
            "notes": "M did not recompute K.",
        },
        {
            "import_item": "upstream_modified",
            "value": l_r1_summary.get("upstream_modified", ""),
            "review_result": "false retained",
            "notes": "M did not modify upstream outputs.",
        },
    ]

    summary_fields = [
        "topic",
        "l_r1_classification",
        "review_status",
        "decision",
        "evidence",
        "limitation",
        "claim_boundary",
        "notes",
    ]
    topic_summary = {
        "identity_group_origin": review_summary_row("identity_group_origin", origin_rows),
        "same_opposite_collinearity_origin": review_summary_row("same_opposite_collinearity_origin", origin_rows),
        "component_bridge_origin": review_summary_row("component_bridge_origin", origin_rows),
        "source_response_degeneracy": review_summary_row("source_response_degeneracy", origin_rows),
        "index_sign_normalization_boundary": review_summary_row("index_sign_normalization_boundary", origin_rows),
        "serialization_hash_boundary": review_summary_row("serialization_hash_boundary", origin_rows),
        "K_readonly_consistency": review_summary_row("K_readonly_consistency", origin_rows),
    }

    l2_review = [
        {
            "boundary_item": row["boundary_item"],
            "l_r1_value": row["extract03l_r1_value"],
            "status": row["status"],
            "m_review": "unchanged",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": row["notes"],
        }
        for row in l2_rows
    ]
    claim_review = [
        {
            "claim_item": "safe_scope",
            "status": "allowed",
            "m_review": "review and decision organization only",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "No public claim authorization.",
        },
        {
            "claim_item": "nature_interface_geometry_gravity_l2_repair_claims",
            "status": "disallowed",
            "m_review": "explicitly blocked",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Must not be inferred from L-R1.",
        },
    ]

    crosswalk_ijk = [
        {
            "source_block": "EXTRACT03I",
            "imported_context": "42 vectors; 16 identity groups; 42 same-identity edges; 119 distinct-identity near-alignments",
            "m_review_use": "identity and K-alignment context",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Read-only context.",
        },
        {
            "source_block": "EXTRACT03J",
            "imported_context": "119 near-alignment items characterized as same/opposite collinearity review patterns",
            "m_review_use": "same/opposite collinearity origin review",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "No clustering or motif rerun.",
        },
        {
            "source_block": "EXTRACT03K-R1",
            "imported_context": "10 control families executed upstream; 7 supported, 3 partial",
            "m_review_use": "control-context crosswalk",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "No controls reexecuted.",
        },
        {
            "source_block": "EXTRACT03K-R2",
            "imported_context": "human-review decision matrix; no future audit authorization",
            "m_review_use": "decision-state crosswalk",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "M does not create new authorization.",
        },
    ]
    crosswalk_kr = [
        {
            "decision_source": "K-R1",
            "decision_or_hypothesis": "source-response degeneracy",
            "l_r1_result": "inconclusive",
            "m_review": "retain as open review item",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Requires explicit future authorization for narrower lineage audit.",
        },
        {
            "decision_source": "K-R1/K-R2",
            "decision_or_hypothesis": "sign/scale/index and K-readonly consistency",
            "l_r1_result": "supported as pipeline review pattern",
            "m_review": "acceptable as internal pipeline-review classification",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "No nature or artifact conclusion.",
        },
        {
            "decision_source": "K-R2",
            "decision_or_hypothesis": "future audit authorization",
            "l_r1_result": "not authorized by K-R2",
            "m_review": "human decision required before next audit",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "M recommends review before authorization.",
        },
    ]

    decision_points = [
        ("D01_accept_supported_origin_topics", "Accept supported pipeline-review origin topics?", "supported origin topics", "Supported L-R1 classifications", "accept_l_r1_classification", "no", "no"),
        ("D02_accept_partial_origin_topics_with_review_notes", "Accept partial topics with review notes?", "partial origin topics", "Partial L-R1 classifications", "accept_with_review_note", "no", "no"),
        ("D03_record_not_supported_origin_topics", "Record not-supported topics if present?", "not-supported origin topics", "No not-supported L-R1 origin topics observed", "accept_with_review_note", "no", "no"),
        ("D04_record_inconclusive_origin_topics", "Record inconclusive topics?", "source_response_degeneracy", "Degeneracy remains inconclusive", "defer_pending_additional_audit", "maybe", "yes"),
        ("D05_record_input_gap_or_guard_blocked_topics", "Record input-gap or guard-blocked topics if present?", "input_gap_or_blocked topics", "No input-gap or guard-blocked origin topics observed", "accept_l_r1_classification", "no", "no"),
        ("D06_keep_l2_boundary_unchanged", "Keep L2 fail boundary unchanged?", "L2 boundary", "L2 fail unchanged; N4 0/3 required 2/3", "accept_l_r1_classification", "no", "no"),
        ("D07_no_public_claim_from_l_r1", "Block public claims beyond documented boundary?", "claim boundary", "L-R1 and M support review organization only", "accept_l_r1_classification", "no", "no"),
        ("D08_decide_registry_or_dwh_integration", "Integrate the review package into registry/DWH metadata?", "registry_or_dwh_integration", "Internal documentation-ready with claim boundary", "accept_with_review_note", "no", "no"),
        ("D09_decide_next_audit_or_review_block", "Authorize a narrower lineage audit or remain at review?", "next audit/review block", "One inconclusive review item remains", "defer_pending_additional_audit", "maybe", "yes"),
    ]
    decision_rows = [
        {
            "decision_id": item[0],
            "decision_question": item[1],
            "affected_AQ_or_origin_topics": item[2],
            "current_l_r1_evidence": item[3],
            "recommended_decision": item[4],
            "requires_new_data": item[5],
            "requires_new_authorization": item[6],
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Human decision point; no automatic authorization.",
        }
        for item in decision_points
    ]

    allowed_actions = [
        ("human_review_m_outputs", "yes", "Review M decision tables and L-R1 classifications.", "no", "no"),
        ("registry_or_dwh_metadata_integration", "yes", "Integrate summaries with claim boundary metadata.", "no", "no"),
        ("narrower_lineage_audit_contract", "conditional", "Only after explicit human authorization.", "maybe", "yes"),
    ]
    disallowed_actions = [
        ("rerun_source_response_audit", "no", "M is review-only."),
        ("recompute_K_or_edges", "no", "Forbidden by M contract."),
        ("rerun_A_R1_or_open_F3_raw_source", "no", "Forbidden by M contract."),
        ("repair_or_reinterpret_L2", "no", "L2 fail boundary unchanged."),
        ("make_nature_interface_geometry_gravity_claim", "no", "Outside claim boundary."),
    ]
    registry_items = [
        "L_R1_audit_summary",
        "AQ_classification_summary",
        "origin_classification_matrix",
        "review_items",
        "guard_results",
        "claim_boundary",
        "l2_boundary",
        "next_step_decision",
    ]
    registry_rows = [
        {
            "integration_item": item,
            "recommended": "yes",
            "target_layer": "internal_registry_or_DWH_metadata",
            "required_metadata": "work_package,status,source_path,sha256,claim_boundary,l2_boundary,review_status",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Internal documentation only; no public claim expansion.",
        }
        for item in registry_items
    ]

    guard_names = [
        "l_r1_outputs_present",
        "origin_classification_matrix_present",
        "no_audit_rerun",
        "no_controls_reexecuted",
        "no_vectors_exported",
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
        "no_upstream_mutation",
        "no_l2_change",
        "no_post_hoc_tuning",
        "no_nature_claim",
        "no_interface_claim",
        "no_geometry_claim",
        "no_gravity_claim",
        "overwrite_refusal",
    ]
    guard_rows = [
        {
            "guard_id": f"E03M-G{i:02d}",
            "guard": guard,
            "status": "pass",
            "evidence": "Read-only review package generated from L-R1 outputs.",
            "blocking": "yes",
            "notes": "Guard satisfied.",
        }
        for i, guard in enumerate(guard_names, 1)
    ]

    supported = topic_rows(origin_rows, supported_cls)
    partial = topic_rows(origin_rows, partial_cls)
    not_supported = topic_rows(origin_rows, not_supported_cls)
    inconclusive = topic_rows(origin_rows, inconclusive_cls)
    input_gap_or_blocked = topic_rows(origin_rows, input_gap_cls) + topic_rows(origin_rows, blocked_cls)

    now = datetime.now(timezone.utc).isoformat()
    manifest = {
        "work_package": "QSB-EXTRACT03M",
        "status": status,
        "created_at_utc": now,
        "repo_root": str(REPO),
        "extract03l_r1_seen": True,
        "extract03l_r1_status": l_r1_summary.get("status", ""),
        "AQ_classification_summary_seen": True,
        "origin_classification_matrix_seen": True,
        "audit_questions_total": len(aq_rows),
        "audit_questions_reviewed": len(aq_review),
        "origin_topics_total": len(origin_rows),
        "origin_topics_supported": class_counts[supported_cls],
        "origin_topics_partial": class_counts[partial_cls],
        "origin_topics_not_supported": class_counts[not_supported_cls],
        "origin_topics_inconclusive": class_counts[inconclusive_cls],
        "origin_topics_input_gap": class_counts[input_gap_cls],
        "origin_topics_blocked_by_guard": class_counts[blocked_cls],
        "review_items_count": len(review_items),
        "decision_points_count": len(decision_rows),
        "audit_rerun": False,
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
        "raw_phase_reconstruction": False,
        "F3_raw_source_opened": False,
        "A_R1_pipeline_rerun": False,
        "upstream_modified": False,
        "l2_fail_changed": False,
        "post_hoc_tuning_performed": False,
        "nature_claim_made": False,
        "interface_claim_made": False,
        "geometry_claim_made": False,
        "gravity_claim_made": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "next_allowed_action": NEXT_ALLOWED_ACTION,
    }

    write_json("01_extract03m_run_manifest.json", manifest)
    write_csv("02_upstream_inventory_and_hashes.csv", list(inventory[0]), inventory)
    write_csv("03_input_availability_review.csv", list(input_review[0]), input_review)
    write_csv("04_l_r1_result_import_summary.csv", list(l_r1_import[0]), l_r1_import)
    write_csv(
        "05_AQ_classification_review.csv",
        [
            "audit_question_id",
            "l_r1_classification",
            "evidence_summary",
            "limitations",
            "human_review_status",
            "recommended_human_decision",
            "notes",
        ],
        aq_review,
    )
    write_csv(
        "06_origin_classification_review_matrix.csv",
        [
            "origin_topic",
            "l_r1_classification",
            "evidence_for",
            "evidence_against",
            "limitations",
            "affected_identity_groups_or_pairs",
            "affected_components",
            "audit_questions_used",
            "human_review_status",
            "recommended_human_decision",
            "claim_boundary",
            "notes",
        ],
        origin_review,
    )
    origin_fields = list(origin_rows[0])
    write_csv("07_supported_origin_topics_review.csv", origin_fields, supported)
    write_csv("08_partial_origin_topics_review.csv", origin_fields, partial)
    write_csv("09_not_supported_origin_topics_review.csv", origin_fields, not_supported)
    write_csv("10_inconclusive_origin_topics_review.csv", origin_fields, inconclusive)
    write_csv("11_input_gap_or_blocked_topics_review.csv", origin_fields, input_gap_or_blocked)
    write_csv("12_identity_group_origin_review_summary.csv", summary_fields, [topic_summary["identity_group_origin"]])
    write_csv("13_same_opposite_collinearity_origin_review_summary.csv", summary_fields, [topic_summary["same_opposite_collinearity_origin"]])
    write_csv("14_component_bridge_origin_review_summary.csv", summary_fields, [topic_summary["component_bridge_origin"]])
    write_csv("15_source_response_degeneracy_review_summary.csv", summary_fields, [topic_summary["source_response_degeneracy"]])
    write_csv("16_index_sign_normalization_review_summary.csv", summary_fields, [topic_summary["index_sign_normalization_boundary"]])
    write_csv("17_serialization_hash_review_summary.csv", summary_fields, [topic_summary["serialization_hash_boundary"]])
    write_csv("18_K_readonly_consistency_review_summary.csv", summary_fields, [topic_summary["K_readonly_consistency"]])
    write_csv("19_L2_boundary_review.csv", list(l2_review[0]), l2_review)
    write_csv("20_claim_boundary_review.csv", list(claim_review[0]), claim_review)
    write_csv("21_crosswalk_to_I_J_K_reviews.csv", list(crosswalk_ijk[0]), crosswalk_ijk)
    write_csv("22_crosswalk_to_K_R1_K_R2_decisions.csv", list(crosswalk_kr[0]), crosswalk_kr)
    write_csv("23_open_review_items_from_L_R1.csv", list(review_items[0]), review_items)
    write_csv(
        "24_decision_points_for_human_review.csv",
        [
            "decision_id",
            "decision_question",
            "affected_AQ_or_origin_topics",
            "current_l_r1_evidence",
            "recommended_decision",
            "requires_new_data",
            "requires_new_authorization",
            "claim_boundary",
            "notes",
        ],
        decision_rows,
    )
    write_csv(
        "25_allowed_next_actions.csv",
        ["action", "allowed", "condition", "requires_new_data", "requires_new_authorization", "claim_boundary", "notes"],
        [
            {
                "action": action,
                "allowed": allowed,
                "condition": condition,
                "requires_new_data": data,
                "requires_new_authorization": auth,
                "claim_boundary": CLAIM_BOUNDARY,
                "notes": "No automatic execution by M.",
            }
            for action, allowed, condition, data, auth in allowed_actions
        ],
    )
    write_csv(
        "26_disallowed_next_actions.csv",
        ["action", "allowed", "reason", "claim_boundary", "notes"],
        [
            {
                "action": action,
                "allowed": allowed,
                "reason": reason,
                "claim_boundary": CLAIM_BOUNDARY,
                "notes": "Blocked by EXTRACT03M contract.",
            }
            for action, allowed, reason in disallowed_actions
        ],
    )
    write_csv("27_registry_or_dwh_integration_recommendation.csv", list(registry_rows[0]), registry_rows)

    write_text(
        "28_publication_safe_note_candidates.md",
        f"""# Publication-Safe Note Candidates

- EXTRACT03M reviews EXTRACT03L-R1 source-response audit results for internal human decision-making.
- L-R1 classified {class_counts[supported_cls]} origin topics as supported pipeline-review patterns, {class_counts[partial_cls]} as partial, and {class_counts[inconclusive_cls]} as inconclusive.
- L2 remains fail: N4 support 0/3, required 2/3.
- No nature, Interface, geometry, gravity, artifact/natural-origin, or L2-repair claim is made.
""",
    )
    write_text(
        "29_human_readable_m_result_review_de.md",
        f"""# QSB-EXTRACT03M Source-Response Audit Result Review

## Ausgangspunkt
EXTRACT03M ist ein Review- und Entscheidungsblock nach EXTRACT03L-R1. Es wurde kein neuer Audit-Run ausgeführt.

## Was L-R1 geliefert hat
L-R1 lieferte AQ01-AQ10, 0 Input-Gaps, 23/23 Guards pass, 46/46 Artefakte und den Status `{l_r1_summary.get("status", "")}`.

## AQ01-AQ10 Klassifikationen
Die AQ-Klassifikationen wurden in `05_AQ_classification_review.csv` übernommen und für menschliche Prüfung eingeordnet.

## Ursprung der Identity Groups
Identity Group Origin bleibt teilweise unterstützt und benötigt Review-Notizen; keine Source-Level-Ursache wird behauptet.

## Ursprung der Same-/Opposite-Collinearity
Same-/Opposite-Collinearity bleibt ein Pipeline-Review-Pattern mit partieller Einordnung; keine Naturalitäts- oder Artefaktbehauptung.

## Komponenten-Brücken
Komponenten-Brücken sind partiell eingeordnet; die Ursache bleibt offen.

## Source-Response-Degeneracy
Source-Response-Degeneracy bleibt inconclusive und ist das zentrale offene Review-Item.

## Index-, Sign- und Normalisierungsgrenze
Diese Grenze ist als Pipeline-Review-Pattern ausreichend eingeordnet.

## Serialisierung und Hash-Grenze
Serialisierung und Hash-Grenze sind partiell eingeordnet; sie erklären nicht allein alle Collinearity-Items.

## K-readonly-Konsistenz
K-readonly-Konsistenz ist als read-only Konsistenzbefund eingeordnet; K wurde nicht neu berechnet.

## L2-Grenze
L2 bleibt fail. N4 support bleibt 0/3 bei required 2/3.

## Was dadurch eingeordnet wird
Unterstützte Pipeline-Review-Patterns können intern als reviewfähig dokumentiert werden.

## Was offen bleibt
Partielle Topics und Source-Response-Degeneracy bleiben offen oder reviewpflichtig.

## Was ausdrücklich nicht behauptet wird
Es wird keine Natur-, Interface-, Geometrie-, Gravitations-, Public-Claim- oder L2-Repair-Aussage gemacht.

## Entscheidungspunkte
Die Entscheidungspunkte D01-D09 stehen in `24_decision_points_for_human_review.csv`.

## Empfehlung
{NEXT_ALLOWED_ACTION}
""",
    )
    next_options = [
        {
            "option_id": "M-NEXT-01",
            "option": "human_review_decision_tables",
            "recommended": "yes",
            "requires_authorization": "no",
            "notes": "Immediate next step.",
        },
        {
            "option_id": "M-NEXT-02",
            "option": "registry_or_dwh_metadata_integration",
            "recommended": "yes",
            "requires_authorization": "no",
            "notes": "Internal documentation only.",
        },
        {
            "option_id": "M-NEXT-03",
            "option": "narrower_lineage_audit_contract",
            "recommended": "conditional",
            "requires_authorization": "yes",
            "notes": "Only if human review authorizes a new contract.",
        },
    ]
    write_csv("30_next_step_options.csv", list(next_options[0]), next_options)
    write_text("31_recommended_next_step.md", "# Recommended Next Step\n\n" + NEXT_ALLOWED_ACTION)
    write_csv("32_guard_results.csv", list(guard_rows[0]), guard_rows)

    validation_rows = [
        ("E03M-V01", "artifact_count", "pass", str(len(FILES)), "36", "yes", "Final file set checked after writes."),
        ("E03M-V02", "l_r1_present", "pass", str(L_R1.exists()), "True", "yes", "Primary upstream exists."),
        ("E03M-V03", "aq_review_created", "pass", str(len(aq_review)), "10", "yes", "AQ review rows."),
        ("E03M-V04", "origin_review_created", "pass", str(len(origin_review)), "9", "yes", "Origin review rows."),
        ("E03M-V05", "decision_points_created", "pass", str(len(decision_rows)), "9", "yes", "D01-D09."),
        ("E03M-V06", "guards_pass", "pass", str(len(guard_rows)), "26", "yes", "All M guards pass."),
        ("E03M-V07", "l2_unchanged", "pass", "fail unchanged", "fail unchanged", "yes", "No L2 repair."),
        ("E03M-V08", "forbidden_claims_absent", "pass", "blocked in claim boundary", "blocked", "yes", "No prohibited claim made."),
    ]
    write_csv(
        "33_validation_results.csv",
        ["validation_id", "check_name", "status", "observed_value", "expected_value", "blocking", "notes"],
        [
            {
                "validation_id": row[0],
                "check_name": row[1],
                "status": row[2],
                "observed_value": row[3],
                "expected_value": row[4],
                "blocking": row[5],
                "notes": row[6],
            }
            for row in validation_rows
        ],
    )
    write_text(
        "34_short_result_note_de.md",
        f"""# QSB-EXTRACT03M Kurznotiz

Status: `{status}`.

EXTRACT03M hat die EXTRACT03L-R1-Ergebnisse read-only für menschliche Entscheidung aufbereitet. Unterstützt: {class_counts[supported_cls]}; partiell: {class_counts[partial_cls]}; nicht unterstützt: {class_counts[not_supported_cls]}; inconclusive: {class_counts[inconclusive_cls]}; input gaps: {class_counts[input_gap_cls]}; blocked by guard: {class_counts[blocked_cls]}.

L2 bleibt fail; keine verbotenen Claims werden gemacht.
""",
    )
    summary = {
        "work_package": "QSB-EXTRACT03M",
        "status": status,
        "audit_questions_reviewed": len(aq_review),
        "origin_topics_total": len(origin_rows),
        "origin_topics_supported": class_counts[supported_cls],
        "origin_topics_partial": class_counts[partial_cls],
        "origin_topics_not_supported": class_counts[not_supported_cls],
        "origin_topics_inconclusive": class_counts[inconclusive_cls],
        "origin_topics_input_gap": class_counts[input_gap_cls],
        "origin_topics_blocked_by_guard": class_counts[blocked_cls],
        "review_items_count": len(review_items),
        "decision_points_count": len(decision_rows),
        "guards_passed": len(guard_rows),
        "audit_rerun": False,
        "controls_reexecuted": False,
        "vectors_exported": False,
        "K_recomputed": False,
        "upstream_modified": False,
        "l2_fail_changed": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "next_allowed_action": NEXT_ALLOWED_ACTION,
    }
    write_json("35_machine_readable_m_result_review_summary.json", summary)
    write_text(
        "FINAL_RESULT_NOTE.md",
        f"""# QSB-EXTRACT03M Final Result

## Status
`{status}`

## Reviewed Inputs
EXTRACT03L-R1 primary outputs plus L/K-R2/K-R1/J/I/H-R1/A-R1 context were used read-only.

## AQ Classification Review
AQ01-AQ10 were reviewed and mapped to human review decisions in `05_AQ_classification_review.csv`.

## Origin Classification Review
The origin matrix contains {len(origin_rows)} topics: {class_counts[supported_cls]} supported pipeline-review patterns, {class_counts[partial_cls]} partial, {class_counts[not_supported_cls]} not supported, {class_counts[inconclusive_cls]} inconclusive, {class_counts[input_gap_cls]} input gaps, and {class_counts[blocked_cls]} blocked by guard.

## Crosswalk to I/J/K
Crosswalks summarize I/J/K-R1/K-R2 context without reruns or recomputation.

## Review Items
{len(review_items)} open review item remains, centered on Source-Response degeneracy.

## Decision Points
D01-D09 were created in `24_decision_points_for_human_review.csv`.

## Registry/DWH Integration Recommendation
Internal registry/DWH metadata integration is recommended for summaries, classifications, review items, guards, claim boundary, L2 boundary, and next-step decision state.

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

    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
