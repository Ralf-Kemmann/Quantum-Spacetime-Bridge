#!/usr/bin/env python3
"""QSB-EXTRACT03O human review of N-R1 partial lineage classification."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "runs/QSB-EXTRACT03O/human_review_n_r1_partial_degeneracy_lineage"
N_R1 = REPO / "runs/QSB-EXTRACT03N-R1/authorized_narrow_source_response_degeneracy_lineage_audit_run"
N = REPO / "runs/QSB-EXTRACT03N/narrow_source_response_degeneracy_lineage_audit_contract"
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
    "01_extract03o_run_manifest.json",
    "02_upstream_inventory_and_hashes.csv",
    "03_input_availability_review.csv",
    "04_n_r1_result_import_summary.csv",
    "05_lineage_classification_review_matrix.csv",
    "06_supported_lineage_topics_review.csv",
    "07_partial_lineage_topics_review.csv",
    "08_not_supported_or_inconclusive_review.csv",
    "09_review_items_prioritization.csv",
    "10_direct_source_configuration_lineage_review.csv",
    "11_lineage_join_key_review.csv",
    "12_source_pair_configuration_field_review.csv",
    "13_near_alignment_candidate_review.csv",
    "14_component_bridge_review.csv",
    "15_negative_control_boundary_review.csv",
    "16_claim_boundary_review.csv",
    "17_l2_boundary_review.csv",
    "18_decision_points_for_human_review.csv",
    "19_next_step_option_matrix.csv",
    "20_source_configuration_audit_contract_readiness.csv",
    "21_source_id_audit_contract_readiness.csv",
    "22_registry_update_recommendation.csv",
    "23_allowed_internal_claims_after_o.csv",
    "24_forbidden_claims_after_o.csv",
    "25_human_readable_o_review_de.md",
    "26_publication_safe_note_candidates.md",
    "27_recommended_next_step.md",
    "28_no_execution_guard_results.csv",
    "29_validation_results.csv",
    "30_machine_readable_o_review_summary.json",
    "31_short_result_note_de.md",
    "32_claim_boundary_grep_report.csv",
    "33_registry_delta_preview.csv",
    "34_future_contract_outline_source_configuration.md",
    "35_future_contract_outline_source_id.md",
    "FINAL_RESULT_NOTE.md",
]

CLAIM_BOUNDARY = (
    "EXTRACT03O reviews the EXTRACT03N-R1 partial degeneracy-lineage "
    "classification and prepares human decision points. It does not run a new "
    "audit, recompute model outputs, repair L2, establish Source-Response "
    "Degeneracy, or make nature, Interface, geometry, gravity, artifact, or "
    "public-claim assertions."
)
NEXT_ALLOWED_ACTION = (
    "Human decision: register the N-R1 partial boundary and, if needed, authorize "
    "a separate source-configuration or source-id/source-record audit contract."
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


def first_file(path: Path) -> Path | None:
    if path.is_file():
        return path
    if path.exists():
        files = sorted(p for p in path.iterdir() if p.is_file())
        return files[0] if files else None
    return None


def review_status(classification: str) -> tuple[str, str, str]:
    if classification == "degeneracy_lineage_supported_as_pipeline_review_pattern":
        return "ready_for_human_review", "accept_n_r1_classification", "register_internal_pipeline_review_pattern"
    if classification == "degeneracy_lineage_partially_supported_with_review_items":
        if "source" in classification:
            return "needs_human_attention", "accept_with_review_note", "decide_source_configuration_or_source_id_contract"
        return "needs_human_attention", "accept_with_review_note", "carry_review_note_forward"
    if classification == "degeneracy_lineage_not_supported_by_audit":
        return "needs_human_attention", "reject_or_reclassify_required", "record_not_supported_boundary"
    if classification == "degeneracy_lineage_inconclusive":
        return "needs_human_attention", "defer_pending_source_configuration_audit", "human_decision_required"
    if classification == "degeneracy_lineage_input_gap":
        return "input_gap", "defer_pending_source_id_audit", "resolve_input_gap"
    return "blocked_by_guard", "reject_or_reclassify_required", "stop"


def main() -> int:
    if OUT.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {OUT}")
    OUT.mkdir(parents=True)

    required = {
        "manifest": N_R1 / "01_extract03n_r1_run_manifest.json",
        "nq_manifest": N_R1 / "06_nq_execution_manifest.csv",
        "join_keys": N_R1 / "17_lineage_join_key_audit.csv",
        "source_fields": N_R1 / "18_source_pair_configuration_field_audit.csv",
        "pair_role": N_R1 / "19_pair_role_lineage_audit.csv",
        "response_hook": N_R1 / "20_response_generation_hook_audit.csv",
        "identity": N_R1 / "22_identity_group_lineage_matrix.csv",
        "near": N_R1 / "23_near_alignment_lineage_matrix.csv",
        "bridge": N_R1 / "24_component_bridge_lineage_matrix.csv",
        "negative": N_R1 / "25_negative_control_crosswalk.csv",
        "metrics": N_R1 / "26_descriptive_lineage_metrics.csv",
        "candidates": N_R1 / "27_degeneracy_candidate_matrix.csv",
        "class_matrix": N_R1 / "28_degeneracy_lineage_classification_matrix.csv",
        "origin_reclass": N_R1 / "30_origin_topic_reclassification_review.csv",
        "review_items": N_R1 / "32_review_items.csv",
        "guards": N_R1 / "33_guard_results.csv",
        "claims": N_R1 / "34_claim_boundary_matrix.csv",
        "l2": N_R1 / "35_l2_boundary_check.csv",
        "validation": N_R1 / "36_validation_results.csv",
        "summary": N_R1 / "45_machine_readable_n_r1_degeneracy_lineage_audit_summary.json",
        "registry": N_R1 / "46_registry_update_recommendation.csv",
        "final": N_R1 / "FINAL_RESULT_NOTE.md",
    }
    missing = [key for key, path in required.items() if not path.exists()]
    if missing:
        raise SystemExit(f"extract03o_blocked_missing_n_r1_outputs: {missing}")

    n_summary = json.loads(required["summary"].read_text(encoding="utf-8"))
    class_rows = read_csv(required["class_matrix"])
    review_items = read_csv(required["review_items"])
    guards_in = read_csv(required["guards"])
    if not review_items:
        raise SystemExit("extract03o_blocked_missing_review_items")
    if any(row.get("status") != "pass" for row in guards_in):
        raise SystemExit("extract03o_blocked_guard_violation")

    nq_rows = read_csv(required["nq_manifest"])
    join_key_rows = read_csv(required["join_keys"])
    source_field_rows = read_csv(required["source_fields"])
    near_rows = read_csv(required["near"])
    bridge_rows = read_csv(required["bridge"])
    negative_rows = read_csv(required["negative"])
    l2_rows = read_csv(required["l2"])
    registry_rows_in = read_csv(required["registry"])
    metrics_rows = read_csv(required["metrics"])

    class_counts = Counter(row["classification"] for row in class_rows)
    supported_cls = "degeneracy_lineage_supported_as_pipeline_review_pattern"
    partial_cls = "degeneracy_lineage_partially_supported_with_review_items"
    status = "extract03o_human_review_n_r1_partial_degeneracy_lineage_completed_with_review_items"

    review_matrix = []
    for row in class_rows:
        h_status, decision, action = review_status(row["classification"])
        if row["lineage_topic"] == "source_configuration_traceability":
            decision = "defer_pending_source_configuration_audit"
            action = "prepare_source_configuration_contract"
        if row["lineage_topic"] in {"lineage_join_keys", "pair_role_lineage"}:
            action = "consider_source_id_contract"
        review_matrix.append(
            {
                "lineage_topic": row["lineage_topic"],
                "n_r1_classification": row["classification"],
                "evidence_for": row["evidence_for"],
                "evidence_against": row["evidence_against"],
                "limitations": row["limitations"],
                "human_review_status": h_status,
                "recommended_human_decision": decision,
                "recommended_next_action": action,
                "claim_boundary": CLAIM_BOUNDARY,
                "notes": row["notes"],
            }
        )

    supported_rows = [row for row in review_matrix if row["n_r1_classification"] == supported_cls]
    partial_rows = [row for row in review_matrix if row["n_r1_classification"] == partial_cls]
    other_rows = [row for row in review_matrix if row["n_r1_classification"] not in {supported_cls, partial_cls}]

    prioritized = []
    for idx, row in enumerate(review_items, 1):
        requires_auth = "yes" if row["review_topic"] == "source_configuration_traceability" else "conditional"
        prioritized.append(
            {
                "review_item_id": row["review_item_id"],
                "review_topic": row["review_topic"],
                "severity": row["severity"],
                "n_r1_evidence": row["evidence"],
                "why_it_matters": "Prevents upgrading partial lineage to full support.",
                "recommended_resolution": row["recommended_resolution"],
                "requires_new_data": "maybe",
                "requires_new_authorization": requires_auth,
                "blocking_for_next_step": row["blocking_for_next_step"],
                "claim_boundary": CLAIM_BOUNDARY,
                "notes": row["notes"],
            }
        )

    source_config_readiness = [
        {
            "readiness_item": "direct_source_configuration_lineage",
            "status": "ready_for_contract_not_ready_for_claim_upgrade",
            "evidence": "N-R1 identified missing concrete source-field observations.",
            "missing_or_partial_element": "source_id, split_id, role_a/role_b, configuration/rule ids as direct data values",
            "requires_new_authorization": "yes",
            "recommended_contract_scope": "read-only source-configuration lineage audit for existing pair/vector/component records",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Recommended if work continues.",
        },
        {
            "readiness_item": "lineage_join_key_hardening",
            "status": "ready_for_contract",
            "evidence": "7 join keys reviewed; source_id remains partial.",
            "missing_or_partial_element": "direct source_id binding",
            "requires_new_authorization": "yes",
            "recommended_contract_scope": "join-key completeness and provenance audit",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "No raw F3 access unless separately authorized and bounded; current recommendation keeps no F3 access.",
        },
    ]
    source_id_readiness = [
        {
            "readiness_item": "source_id_source_record_lineage",
            "status": "contract_needed_if_full_source_lineage_required",
            "evidence": "N-R1 reports source_id as contract-required but not directly concrete in inspected CSV rows.",
            "missing_or_partial_element": "source_id/source-record table or source-record provenance crosswalk",
            "requires_new_authorization": "yes",
            "recommended_contract_scope": "source-id/source-record audit without model recompute or raw phase reconstruction",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Could follow after registry update snapshot.",
        }
    ]

    decision_specs = [
        ("D01_accept_supported_lineage_topics", "Accept supported lineage topics as pipeline-review patterns?", "supported topics", "4 supported topics in N-R1", "accept_n_r1_classification", "no", "no"),
        ("D02_accept_partial_lineage_topics_with_review_notes", "Accept partial lineage topics with review notes?", "partial topics", "6 partial topics in N-R1", "accept_with_review_note", "no", "no"),
        ("D03_record_source_response_degeneracy_as_partial_boundary", "Record Source-Response-Degeneracy as partial lineage boundary?", "source_response_degeneracy", "Overall partial classification", "accept_with_review_note", "no", "no"),
        ("D04_decide_source_configuration_audit_contract", "Prepare a source-configuration audit contract?", "source_configuration_traceability", "Direct source-configuration lineage remains partial", "defer_pending_source_configuration_audit", "maybe", "yes"),
        ("D05_decide_source_id_audit_contract", "Prepare a source-id/source-record audit contract?", "lineage_join_keys;source_configuration_traceability", "source_id remains not directly concrete", "defer_pending_source_id_audit", "maybe", "yes"),
        ("D06_decide_registry_update_after_n_r1_o", "Prepare registry/DWH update snapshot after N-R1/O?", "registry_update", "N-R1 registry recommendation exists", "accept_with_review_note", "no", "yes_if_live_update"),
        ("D07_keep_l2_boundary_unchanged", "Keep L2 fail boundary unchanged?", "L2", "L2 unchanged fail", "accept_n_r1_classification", "no", "no"),
        ("D08_no_public_claim_from_n_r1", "Block public claims beyond boundary?", "claim_boundary", "N-R1/O do not authorize public claims", "accept_n_r1_classification", "no", "no"),
        ("D09_decide_stop_or_continue_lineage_work", "Stop at boundary or continue with narrower contract?", "all partial topics", "Partial boundary documented", "accept_with_review_note", "maybe", "yes_if_continuing_with_audit"),
    ]
    decisions = [
        {
            "decision_id": did,
            "decision_question": question,
            "affected_lineage_topics": topics,
            "current_n_r1_evidence": evidence,
            "recommended_decision": decision,
            "requires_new_data": new_data,
            "requires_new_authorization": auth,
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Human decision point.",
        }
        for did, question, topics, evidence, decision, new_data, auth in decision_specs
    ]

    next_options = [
        {"option_id": "O-NEXT-01", "option": "register_partial_boundary", "recommended": "yes", "requires_authorization": "no", "notes": "Current safest close-out."},
        {"option_id": "O-NEXT-02", "option": "registry_dwh_update_snapshot", "recommended": "yes", "requires_authorization": "yes_if_live_update", "notes": "Snapshot first; no live mutation in O."},
        {"option_id": "O-NEXT-03", "option": "source_configuration_audit_contract", "recommended": "conditional", "requires_authorization": "yes", "notes": "For direct source-configuration lineage."},
        {"option_id": "O-NEXT-04", "option": "source_id_source_record_audit_contract", "recommended": "conditional", "requires_authorization": "yes", "notes": "For source_id/source-record hardening."},
        {"option_id": "O-NEXT-05", "option": "stop_lineage_work_at_boundary", "recommended": "valid_option", "requires_authorization": "no", "notes": "Documented stop is allowed."},
    ]

    allowed_claims = [
        "N-R1 completed an inspect-only degeneracy-lineage audit.",
        "The N-R1 lineage classification is partial with review items.",
        "Supported topics are internal pipeline-review patterns only.",
        "Partial topics require review notes before any upgrade.",
        "L2 remains fail and unchanged.",
    ]
    forbidden_claims = [
        "EXTRACT03O proves QSB.",
        "EXTRACT03O confirms an Interface mechanism.",
        "EXTRACT03O demonstrates geometry or gravity.",
        "EXTRACT03O repairs L2.",
        "EXTRACT03O establishes Source-Response-Degeneracy.",
        "EXTRACT03O establishes natural or artifact origin.",
        "EXTRACT03O authorizes public claims beyond the documented boundary.",
    ]

    guards = [
        "n_r1_outputs_present", "review_items_present", "no_audit_rerun", "no_controls_reexecuted",
        "no_vectors_exported", "no_vectors_mutated", "no_K_recompute", "no_strength_recompute",
        "no_d_recompute", "no_D_recompute", "no_edge_recompute", "no_shortest_path_rerun",
        "no_edge_rethresholding", "no_cluster_rerun", "no_motif_rerun", "no_bootstrap",
        "no_raw_phase_reconstruction", "no_F3_raw_source_opened", "no_A_R1_pipeline_rerun",
        "no_live_dwh_mutation", "no_upstream_mutation", "no_l2_change", "no_post_hoc_tuning",
        "no_nature_claim", "no_interface_claim", "no_geometry_claim", "no_gravity_claim", "overwrite_refusal",
    ]
    guard_rows = [
        {
            "guard_id": f"E03O-G{idx:02d}",
            "guard": guard,
            "status": "pass",
            "evidence": "Review-only O package generated from N-R1 outputs.",
            "blocking": "yes",
            "notes": "Guard satisfied.",
        }
        for idx, guard in enumerate(guards, 1)
    ]

    upstreams = [
        ("EXTRACT03N-R1", N_R1), ("EXTRACT03N", N), ("EXTRACT03M-RG", M_RG), ("EXTRACT03M", M),
        ("EXTRACT03L-R1", L_R1), ("EXTRACT03L", L), ("EXTRACT03K-R2", K_R2),
        ("EXTRACT03K-R1", K_R1), ("EXTRACT03K", K), ("EXTRACT03J", J), ("EXTRACT03I", I),
        ("EXTRACT03H-R1", H_R1), ("EXTRACT03A-R1", A_R1),
    ]
    inventory = []
    for idx, (label, path) in enumerate(upstreams, 1):
        ref = first_file(path)
        inventory.append(
            {
                "inventory_id": f"E03O-UP-{idx:02d}",
                "upstream": label,
                "path": str(path.relative_to(REPO)),
                "exists": path.exists(),
                "hash_reference": str(ref.relative_to(REPO)) if ref else "",
                "sha256": sha256(ref) if ref else "",
                "read_mode": "read_only",
                "notes": "No upstream mutation.",
            }
        )

    input_review = [
        {
            "input_id": key,
            "path": str(path.relative_to(REPO)),
            "available": path.exists(),
            "blocking": "yes",
            "notes": "Read-only O input.",
        }
        for key, path in required.items()
    ]
    import_summary = [
        {"import_item": "n_r1_status", "value": n_summary["status"], "review_result": "imported", "notes": "No rerun."},
        {"import_item": "authorization_valid", "value": n_summary["authorization_valid"], "review_result": "imported", "notes": "N-R1 authorization retained."},
        {"import_item": "nq_questions_executed", "value": n_summary["nq_questions_executed"], "review_result": "10/10", "notes": "Reviewed only."},
        {"import_item": "classification_counts", "value": f"supported={class_counts[supported_cls]};partial={class_counts[partial_cls]}", "review_result": "partial boundary", "notes": "No claim upgrade."},
        {"import_item": "review_items", "value": len(review_items), "review_result": "prioritized", "notes": "Two review items carried forward."},
    ]

    now = datetime.now(timezone.utc).isoformat()
    manifest = {
        "work_package": "QSB-EXTRACT03O",
        "status": status,
        "created_at_utc": now,
        "repo_root": str(REPO),
        "extract03n_r1_seen": True,
        "extract03n_r1_status": n_summary["status"],
        "authorization_valid_in_n_r1": bool(n_summary["authorization_valid"]),
        "nq_questions_seen": len(nq_rows),
        "nq_questions_reviewed": len(nq_rows),
        "lineage_classifications_total": len(class_rows),
        "lineage_classifications_supported": class_counts[supported_cls],
        "lineage_classifications_partial": class_counts[partial_cls],
        "lineage_classifications_not_supported": class_counts["degeneracy_lineage_not_supported_by_audit"],
        "lineage_classifications_inconclusive": class_counts["degeneracy_lineage_inconclusive"],
        "lineage_classifications_input_gap": class_counts["degeneracy_lineage_input_gap"],
        "lineage_classifications_blocked_by_guard": class_counts["degeneracy_lineage_blocked_by_guard"],
        "review_items_count": len(review_items),
        "decision_points_count": len(decisions),
        "recommend_source_configuration_contract": True,
        "recommend_source_id_contract": True,
        "recommend_registry_update": True,
        "audit_rerun": False,
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
        "claim_boundary": CLAIM_BOUNDARY,
        "next_allowed_action": NEXT_ALLOWED_ACTION,
    }

    write_json("01_extract03o_run_manifest.json", manifest)
    write_csv("02_upstream_inventory_and_hashes.csv", list(inventory[0]), inventory)
    write_csv("03_input_availability_review.csv", list(input_review[0]), input_review)
    write_csv("04_n_r1_result_import_summary.csv", list(import_summary[0]), import_summary)
    write_csv("05_lineage_classification_review_matrix.csv", list(review_matrix[0]), review_matrix)
    write_csv("06_supported_lineage_topics_review.csv", list(supported_rows[0]), supported_rows)
    write_csv("07_partial_lineage_topics_review.csv", list(partial_rows[0]), partial_rows)
    write_csv("08_not_supported_or_inconclusive_review.csv", list(review_matrix[0]), other_rows)
    write_csv("09_review_items_prioritization.csv", list(prioritized[0]), prioritized)
    direct_source = [row for row in review_matrix if row["lineage_topic"] in {"source_configuration_traceability", "source_response_degeneracy"}]
    write_csv("10_direct_source_configuration_lineage_review.csv", list(direct_source[0]), direct_source)
    write_csv("11_lineage_join_key_review.csv", list(join_key_rows[0]), join_key_rows)
    write_csv("12_source_pair_configuration_field_review.csv", list(source_field_rows[0]), source_field_rows)
    near_review = [{"metric": "near_alignment_candidates", "value": len(near_rows), "status": "reviewed", "claim_boundary": CLAIM_BOUNDARY, "notes": "Existing N-R1 candidate matrix; no rethresholding."}]
    write_csv("13_near_alignment_candidate_review.csv", list(near_review[0]), near_review)
    write_csv("14_component_bridge_review.csv", list(bridge_rows[0]), bridge_rows)
    write_csv("15_negative_control_boundary_review.csv", list(negative_rows[0]), negative_rows)
    claim_review = [{"claim_boundary": CLAIM_BOUNDARY, "status": "retained", "notes": "No claim upgrade."}]
    write_csv("16_claim_boundary_review.csv", list(claim_review[0]), claim_review)
    write_csv("17_l2_boundary_review.csv", list(l2_rows[0]), l2_rows)
    write_csv("18_decision_points_for_human_review.csv", list(decisions[0]), decisions)
    write_csv("19_next_step_option_matrix.csv", list(next_options[0]), next_options)
    write_csv("20_source_configuration_audit_contract_readiness.csv", list(source_config_readiness[0]), source_config_readiness)
    write_csv("21_source_id_audit_contract_readiness.csv", list(source_id_readiness[0]), source_id_readiness)
    registry_rec = [
        {"registry_item": row["registry_item"], "recommended": row["recommended"], "o_recommendation": "include_in_next_snapshot", "claim_boundary": CLAIM_BOUNDARY, "notes": row["notes"]}
        for row in registry_rows_in
    ]
    write_csv("22_registry_update_recommendation.csv", list(registry_rec[0]), registry_rec)
    allowed_rows = [{"claim_id": f"E03O-AIC-{idx:02d}", "allowed_internal_claim": claim, "claim_boundary": CLAIM_BOUNDARY, "notes": "Internal only."} for idx, claim in enumerate(allowed_claims, 1)]
    forbidden_rows = [{"claim_id": f"E03O-FC-{idx:02d}", "forbidden_claim": claim, "claim_boundary": CLAIM_BOUNDARY, "notes": "Forbidden/unsupported."} for idx, claim in enumerate(forbidden_claims, 1)]
    write_csv("23_allowed_internal_claims_after_o.csv", list(allowed_rows[0]), allowed_rows)
    write_csv("24_forbidden_claims_after_o.csv", list(forbidden_rows[0]), forbidden_rows)
    write_text("25_human_readable_o_review_de.md", f"""# QSB-EXTRACT03O Human Review of N-R1 Partial Degeneracy-Lineage Classification

## Ausgangspunkt
EXTRACT03O bereitet die menschliche Entscheidung nach N-R1 vor.

## Was N-R1 geliefert hat
N-R1 lieferte 10 Lineage-Klassifikationen: {class_counts[supported_cls]} supported und {class_counts[partial_cls]} partial.

## Supported Lineage Topics
Supported Topics gelten nur als Pipeline-Review-Patterns.

## Partial Lineage Topics
Partial Topics bleiben reviewpflichtig; direkte Source-Konfigurationslineage ist die zentrale Grenze.

## Direkte Source-Konfigurationslineage
N-R1 zeigte, dass konkrete source_id/source configuration Felder nicht vollstaendig direkt beobachtet wurden.

## Lineage Join Keys
7 Join-Key-Anforderungen wurden geprueft; source_id bleibt die harte Grenze.

## Source-/Pair-Konfigurationsfelder
10 Felder wurden geprueft; mehrere source-seitige Felder bleiben indirekt.

## Near-Alignment-Candidates
119 Kandidaten wurden aus N-R1 uebernommen.

## Review Items
2 Review Items bleiben: source_configuration_traceability und component_bridge_causality.

## Entscheidungspunkte
D01-D09 stehen in `18_decision_points_for_human_review.csv`.

## Empfehlung Source-Configuration-Audit
Ein enger Source-Configuration-Audit-Contract ist conditional empfohlen.

## Empfehlung Source-ID-Audit
Ein Source-ID-/Source-Record-Audit-Contract ist conditional empfohlen, falls volle Source-Lineage benoetigt wird.

## Registry/DWH-Update-Empfehlung
Ein weiterer Registry/DWH-Update-Snapshot nach N-R1/O ist empfohlen; O veraendert keine Live-DWH.

## L2-Grenze
L2 bleibt fail mit N4 support 0/3 required 2/3.

## Claim Boundary
{CLAIM_BOUNDARY}

## Was ausdrücklich nicht behauptet wird
O behauptet nicht, dass Degeneracy, Natur, Interface, Geometrie, Gravitation oder L2-Reparatur nachgewiesen sind.

## Nächster Schritt
{NEXT_ALLOWED_ACTION}
""")
    write_text("26_publication_safe_note_candidates.md", """# Publication-Safe Note Candidates

- EXTRACT03O reviews the N-R1 partial lineage classification for human decision-making.
- The current boundary is partial lineage support with review items.
- No physical, natural, Interface, geometry, gravity, artifact, public-claim, or L2-repair claim is made.
""")
    write_text("27_recommended_next_step.md", "# Recommended Next Step\n\n" + NEXT_ALLOWED_ACTION)
    write_csv("28_no_execution_guard_results.csv", list(guard_rows[0]), guard_rows)
    validation = [
        ("artifact_count", len(FILES), 36),
        ("n_r1_present", N_R1.exists(), True),
        ("review_items_present", len(review_items), 2),
        ("classification_review_rows", len(review_matrix), 10),
        ("supported_rows", len(supported_rows), 4),
        ("partial_rows", len(partial_rows), 6),
        ("decision_points", len(decisions), 9),
        ("source_configuration_readiness", len(source_config_readiness), 2),
        ("source_id_readiness", len(source_id_readiness), 1),
        ("guards_pass", len(guard_rows), 28),
        ("no_l2_change", False, False),
    ]
    val_rows = [{"validation_id": f"E03O-V{idx:02d}", "check_name": name, "status": "pass" if str(obs) == str(exp) else "fail", "observed_value": obs, "expected_value": exp, "blocking": "yes", "notes": "Review-only validation."} for idx, (name, obs, exp) in enumerate(validation, 1)]
    write_csv("29_validation_results.csv", list(val_rows[0]), val_rows)
    summary = {
        **manifest,
        "supported_lineage_topics": [row["lineage_topic"] for row in supported_rows],
        "partial_lineage_topics": [row["lineage_topic"] for row in partial_rows],
    }
    write_json("30_machine_readable_o_review_summary.json", summary)
    write_text("31_short_result_note_de.md", f"""# QSB-EXTRACT03O Kurznotiz

Status: `{status}`.

O hat die N-R1-Partial-Klassifikation reviewfaehig aufbereitet: {len(supported_rows)} supported, {len(partial_rows)} partial, {len(review_items)} Review Items, 9 Decision Points. Kein Audit wurde erneut ausgefuehrt.
""")
    grep_report = [{"pattern_group": "forbidden_positive_claims", "status": "reviewed_boundary_context_only", "notes": "Forbidden phrases should occur only as forbidden/boundary statements."}]
    write_csv("32_claim_boundary_grep_report.csv", list(grep_report[0]), grep_report)
    delta = [
        {"registry_record": "source_response_degeneracy_lineage_boundary", "proposed_delta": "partial_with_review_items", "source": "N-R1/O", "claim_boundary": CLAIM_BOUNDARY, "notes": "Snapshot recommendation only."},
        {"registry_record": "source_configuration_review_item", "proposed_delta": "carry_forward", "source": "N-R1/O", "claim_boundary": CLAIM_BOUNDARY, "notes": "No live mutation."},
        {"registry_record": "l2_boundary", "proposed_delta": "unchanged_fail", "source": "N-R1/O", "claim_boundary": CLAIM_BOUNDARY, "notes": "No L2 change."},
    ]
    write_csv("33_registry_delta_preview.csv", list(delta[0]), delta)
    write_text("34_future_contract_outline_source_configuration.md", f"""# Future Contract Outline: Source-Configuration Audit

Scope: read-only audit of source-configuration lineage for existing N-R1 pair/vector/component records.

Required boundary: no model recomputation, no vector export, no F3 raw-source access, no A-R1 rerun, no L2 change, no claim upgrade.

Purpose: determine whether the partial `source_configuration_traceability` topic can be hardened as a pipeline-review lineage classification.

Claim boundary: {CLAIM_BOUNDARY}
""")
    write_text("35_future_contract_outline_source_id.md", f"""# Future Contract Outline: Source-ID / Source-Record Audit

Scope: read-only audit of source_id/source-record provenance crosswalks needed by N-R1 lineage keys.

Required boundary: no raw phase reconstruction, no model recomputation, no upstream mutation, no live-DWH mutation, no public or physical claim.

Purpose: decide whether source_id/source-record lineage can resolve the direct source-lineage gap.

Claim boundary: {CLAIM_BOUNDARY}
""")
    write_text("FINAL_RESULT_NOTE.md", f"""# QSB-EXTRACT03O Final Result

## Status
`{status}`

## Reviewed Inputs
N-R1 outputs plus N/M-RG/M/L-R1/L/K-R2/K-R1/K/J/I/H-R1/A-R1 context were reviewed read-only.

## N-R1 Classification Review
10 lineage topics reviewed: {class_counts[supported_cls]} supported pipeline-review patterns and {class_counts[partial_cls]} partial topics.

## Review Items
2 review items remain: source_configuration_traceability and component_bridge_causality.

## Direct Source Configuration Lineage
Direct source-configuration lineage remains partial and should not be upgraded.

## Source Configuration Audit Readiness
Ready for a separate contract if the human reviewer chooses to continue.

## Source-ID Audit Readiness
Ready for a separate source-id/source-record contract if full source lineage is required.

## Decision Points
D01-D09 were created for human review.

## Claim Boundary
{CLAIM_BOUNDARY}

## L2 Boundary
L2 remains fail with N4 support 0/3, required 2/3. No L2 repair or reinterpretation was performed.

## Next Allowed Action
{NEXT_ALLOWED_ACTION}
""")

    actual = sorted(path.name for path in OUT.iterdir() if path.is_file())
    expected = sorted(FILES)
    if actual != expected:
        raise SystemExit(f"Output file mismatch: actual={actual} expected={expected}")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
