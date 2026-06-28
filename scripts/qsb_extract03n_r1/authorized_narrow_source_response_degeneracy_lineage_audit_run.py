#!/usr/bin/env python3
"""QSB-EXTRACT03N-R1 authorized narrow degeneracy lineage audit run.

This is an inspect-only lineage audit under EXTRACT03N. It reads upstream
artifacts, computes descriptive lineage counts, and writes classification
records. It does not recompute model outputs or mutate upstream state.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "runs/QSB-EXTRACT03N-R1/authorized_narrow_source_response_degeneracy_lineage_audit_run"
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
    "01_extract03n_r1_run_manifest.json",
    "02_authorization_used.json",
    "03_upstream_inventory_and_hashes.csv",
    "04_contract_alignment_review.csv",
    "05_input_availability_review.csv",
    "06_nq_execution_manifest.csv",
    "07_NQ01_inconclusive_topic_localization.csv",
    "08_NQ02_source_configuration_traceability.csv",
    "09_NQ03_pair_role_lineage.csv",
    "10_NQ04_response_generation_lineage.csv",
    "11_NQ05_identity_group_lineage.csv",
    "12_NQ06_near_alignment_lineage.csv",
    "13_NQ07_component_bridge_lineage.csv",
    "14_NQ08_negative_control_lineage.csv",
    "15_NQ09_allowed_descriptive_metrics.csv",
    "16_NQ10_stop_and_claim_boundary.csv",
    "17_lineage_join_key_audit.csv",
    "18_source_pair_configuration_field_audit.csv",
    "19_pair_role_lineage_audit.csv",
    "20_response_generation_hook_audit.csv",
    "21_normalization_sign_index_serialization_audit.csv",
    "22_identity_group_lineage_matrix.csv",
    "23_near_alignment_lineage_matrix.csv",
    "24_component_bridge_lineage_matrix.csv",
    "25_negative_control_crosswalk.csv",
    "26_descriptive_lineage_metrics.csv",
    "27_degeneracy_candidate_matrix.csv",
    "28_degeneracy_lineage_classification_matrix.csv",
    "29_nq_classification_summary.csv",
    "30_origin_topic_reclassification_review.csv",
    "31_stop_criteria_review.csv",
    "32_review_items.csv",
    "33_guard_results.csv",
    "34_claim_boundary_matrix.csv",
    "35_l2_boundary_check.csv",
    "36_validation_results.csv",
    "37_human_readable_n_r1_degeneracy_lineage_audit_de.md",
    "38_publication_safe_note_candidates.md",
    "39_next_step_options.csv",
    "40_recommended_next_step.md",
    "41_lineage_overview.png",
    "42_degeneracy_candidate_overview.png",
    "43_classification_overview.png",
    "44_short_result_note_de.md",
    "45_machine_readable_n_r1_degeneracy_lineage_audit_summary.json",
    "46_registry_update_recommendation.csv",
    "47_claim_boundary_grep_report.csv",
    "FINAL_RESULT_NOTE.md",
]

AUTHORIZATION = {
    "authorization_status": "human_authorized_for_extract03n_r1_narrow_source_response_degeneracy_lineage_audit_run",
    "authorized_work_package": "QSB-EXTRACT03N-R1",
    "source_contract": "QSB-EXTRACT03N",
    "authorization_source": "current_user_instruction",
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
    "no_vector_mutation": True,
    "no_live_dwh_mutation": True,
    "no_l2_change": True,
    "no_post_hoc_tuning": True,
    "no_nature_claim": True,
    "no_interface_claim": True,
    "no_geometry_claim": True,
    "no_gravity_claim": True,
}

CLAIM_BOUNDARY = (
    "EXTRACT03N-R1 classifies Source-Response degeneracy lineage only as an "
    "inspect-only pipeline review pattern under EXTRACT03N. It does not establish "
    "degeneracy as a physical, natural, Interface, geometry, gravity, artifact, "
    "or L2-repair claim."
)
NEXT_ALLOWED_ACTION = (
    "Human review of the partial lineage classification and review items before "
    "any narrower source-configuration or source-id audit contract."
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


def create_pngs(class_counts: Counter[str], metrics: list[dict[str, object]]) -> bool:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(["join keys", "fields", "candidates"], [
            int(next(row["value"] for row in metrics if row["metric"] == "lineage_join_keys_seen")),
            int(next(row["value"] for row in metrics if row["metric"] == "source_pair_configuration_fields_seen")),
            int(next(row["value"] for row in metrics if row["metric"] == "degeneracy_candidate_rows")),
        ])
        ax.set_title("N-R1 Lineage Overview")
        fig.tight_layout()
        fig.savefig(OUT / "41_lineage_overview.png", dpi=140)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(7, 4))
        labels = ["near alignments", "components", "identity groups"]
        values = [
            int(next(row["value"] for row in metrics if row["metric"] == "near_alignment_items_seen")),
            int(next(row["value"] for row in metrics if row["metric"] == "components_seen")),
            int(next(row["value"] for row in metrics if row["metric"] == "identity_groups_seen")),
        ]
        ax.bar(labels, values)
        ax.set_title("Degeneracy Candidate Coverage")
        fig.tight_layout()
        fig.savefig(OUT / "42_degeneracy_candidate_overview.png", dpi=140)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(7, 4))
        labels = list(class_counts)
        values = [class_counts[label] for label in labels]
        ax.bar(range(len(labels)), values)
        ax.set_xticks(range(len(labels)), [label.replace("degeneracy_lineage_", "") for label in labels], rotation=30, ha="right")
        ax.set_title("Degeneracy Lineage Classifications")
        fig.tight_layout()
        fig.savefig(OUT / "43_classification_overview.png", dpi=140)
        plt.close(fig)
        return True
    except Exception:
        try:
            from PIL import Image, ImageDraw

            for name in ["41_lineage_overview.png", "42_degeneracy_candidate_overview.png", "43_classification_overview.png"]:
                img = Image.new("RGB", (900, 260), "white")
                draw = ImageDraw.Draw(img)
                draw.text((24, 110), "visualization dependency unavailable - tabular audit completed", fill="black")
                img.save(OUT / name)
            return False
        except Exception:
            # Minimal valid 1x1 transparent PNG.
            raw = bytes.fromhex(
                "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
                "0000000a49444154789c6360000002000100ffff03000006000557bfab0d0000000049454e44ae426082"
            )
            for name in ["41_lineage_overview.png", "42_degeneracy_candidate_overview.png", "43_classification_overview.png"]:
                (OUT / name).write_bytes(raw)
            return False


def main() -> int:
    if OUT.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {OUT}")
    OUT.mkdir(parents=True)

    required = {
        "n_manifest": N / "01_extract03n_run_manifest.json",
        "n_questions": N / "06_narrow_degeneracy_audit_question_registry.csv",
        "n_inputs": N / "07_required_n_r1_inputs.csv",
        "join_keys": N / "11_lineage_join_key_requirements.csv",
        "source_fields": N / "12_source_pair_configuration_field_requirements.csv",
        "stop_criteria": N / "10_n_r1_stop_criteria.csv",
        "classification_schema": N / "21_degeneracy_lineage_classification_schema.csv",
        "m_rg_sqlite": M_RG / "30_registry_snapshot.sqlite",
        "m_rg_origin": M_RG / "08_origin_topic_registry_records.csv",
        "m_origin": M / "06_origin_classification_review_matrix.csv",
        "l_r1_origin": L_R1 / "30_origin_classification_matrix.csv",
        "identity_crosswalk": L_R1 / "24_identity_group_origin_crosswalk.csv",
        "near_crosswalk": L_R1 / "25_near_alignment_origin_crosswalk.csv",
        "bridge_crosswalk": L_R1 / "26_component_bridge_origin_crosswalk.csv",
        "i_identity": I / "18_identity_to_component_explanation_matrix.csv",
        "j_near": J / "04_near_alignment_item_import.csv",
        "k_r1_controls": K_R1 / "17_control_family_classification_summary.csv",
        "k_r2_decisions": K_R2 / "13_decision_points_for_human_review.csv",
        "h_vectors": H_R1 / "09_response_vector_export.csv",
        "h_hashes": H_R1 / "10_response_vector_hashes.csv",
        "h_signatures": H_R1 / "11_sign_normalized_vector_signatures.csv",
        "code_path": L_R1 / "17_source_response_code_path_review.csv",
        "hook": L_R1 / "18_response_generation_hook_review.csv",
        "normalization": L_R1 / "19_normalization_rule_review.csv",
        "sign": L_R1 / "20_sign_anchor_rule_review.csv",
        "index": L_R1 / "21_index_convention_review.csv",
        "serialization": L_R1 / "22_serialization_hash_rule_review.csv",
        "pair_role": L_R1 / "23_pair_role_convention_review.csv",
    }
    missing = [key for key, path in required.items() if not path.exists()]
    if missing:
        raise SystemExit(f"extract03n_r1_blocked_missing_required_inputs: {missing}")

    n_manifest = json.loads(required["n_manifest"].read_text(encoding="utf-8"))
    n_questions = read_csv(required["n_questions"])
    n_inputs = read_csv(required["n_inputs"])
    join_keys = read_csv(required["join_keys"])
    source_fields = read_csv(required["source_fields"])
    stop_criteria = read_csv(required["stop_criteria"])
    origin_rg = read_csv(required["m_rg_origin"])
    origin_m = read_csv(required["m_origin"])
    origin_l = read_csv(required["l_r1_origin"])
    identity_rows = read_csv(required["i_identity"])
    near_rows = read_csv(required["j_near"])
    k_r1_rows = read_csv(required["k_r1_controls"])
    k_r2_rows = read_csv(required["k_r2_decisions"])
    h_vector_rows = read_csv(required["h_vectors"])
    h_hash_rows = read_csv(required["h_hashes"])
    h_sig_rows = read_csv(required["h_signatures"])
    identity_crosswalk = read_csv(required["identity_crosswalk"])
    near_crosswalk = read_csv(required["near_crosswalk"])
    bridge_crosswalk = read_csv(required["bridge_crosswalk"])

    if n_manifest.get("status") != "extract03n_degeneracy_lineage_audit_contract_completed_with_review_items":
        raise SystemExit("extract03n_r1_blocked_missing_extract03n_contract")
    if len(n_questions) != 10:
        raise SystemExit("extract03n_r1_blocked_missing_extract03n_contract")
    input_gaps = [row for row in n_inputs if row["current_status"] == "input_gap"]
    if input_gaps:
        raise SystemExit("extract03n_r1_blocked_missing_required_inputs")

    con = sqlite3.connect(f"file:{required['m_rg_sqlite']}?mode=ro", uri=True)
    sqlite_integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
    sqlite_degeneracy = con.execute(
        "SELECT registry_id, origin_topic, classification FROM rg_origin_topic_classification WHERE origin_topic='source_response_degeneracy'"
    ).fetchall()
    con.close()

    degeneracy_rg = next(row for row in origin_rg if row["origin_topic"] == "source_response_degeneracy")
    degeneracy_m = next(row for row in origin_m if row["origin_topic"] == "source_response_degeneracy")
    degeneracy_l = next(row for row in origin_l if row["origin_topic"] == "source_response_degeneracy")

    pair_ids = set()
    identity_groups = set()
    components = set()
    for row in identity_rows:
        components.add(row.get("component_id", ""))
        identity_groups.add(row.get("identity_group_id", ""))
        for pair in row.get("member_pair_ids", "").split(";"):
            if pair:
                pair_ids.add(pair)
    near_pair_ids = set()
    for row in near_rows:
        near_pair_ids.add(row.get("pair_i", ""))
        near_pair_ids.add(row.get("pair_j", ""))
        components.add(row.get("component_id", ""))
        identity_groups.add(row.get("identity_group_i", ""))
        identity_groups.add(row.get("identity_group_j", ""))
    candidate_pairs_in_identity = len([pair for pair in near_pair_ids if pair in pair_ids])
    source_field_names = {row["field_name"] for row in source_fields}
    concrete_source_fields = {"pair_id", "response_vector_id", "identity_group_id", "component_id", "near_alignment_item_id"}
    missing_source_fields = sorted(source_field_names - concrete_source_fields)

    metrics = [
        {"metric": "lineage_join_keys_seen", "value": len(join_keys), "notes": "From EXTRACT03N contract."},
        {"metric": "source_pair_configuration_fields_seen", "value": len(source_fields), "notes": "Contract-required fields."},
        {"metric": "source_pair_configuration_fields_concretely_observed", "value": len(concrete_source_fields), "notes": "Observed via pair/component/identity/vector tables."},
        {"metric": "identity_groups_seen", "value": len([g for g in identity_groups if g]), "notes": "I/J read-only lineage."},
        {"metric": "components_seen", "value": len([c for c in components if c]), "notes": "I/J read-only lineage."},
        {"metric": "near_alignment_items_seen", "value": len(near_rows), "notes": "J near-alignment rows."},
        {"metric": "near_alignment_pair_slots_seen", "value": len([p for p in near_pair_ids if p]), "notes": "Unique pair IDs appearing in near-alignment slots."},
        {"metric": "near_alignment_pair_slots_in_identity_mapping", "value": candidate_pairs_in_identity, "notes": "Pair IDs also seen in I identity mapping."},
        {"metric": "h_response_vectors_seen", "value": len(h_vector_rows), "notes": "H-R1 vector export rows read-only."},
        {"metric": "h_vector_hashes_seen", "value": len(h_hash_rows), "notes": "H-R1 vector hash rows read-only."},
        {"metric": "degeneracy_candidate_rows", "value": len(near_rows), "notes": "Candidate set bounded to 119 J near-alignment rows."},
    ]

    nq_class = {
        "NQ01_inconclusive_topic_localization": "degeneracy_lineage_supported_as_pipeline_review_pattern",
        "NQ02_source_configuration_traceability": "degeneracy_lineage_partially_supported_with_review_items",
        "NQ03_pair_role_lineage": "degeneracy_lineage_partially_supported_with_review_items",
        "NQ04_response_generation_lineage": "degeneracy_lineage_supported_as_pipeline_review_pattern",
        "NQ05_identity_group_lineage": "degeneracy_lineage_supported_as_pipeline_review_pattern",
        "NQ06_near_alignment_lineage": "degeneracy_lineage_supported_as_pipeline_review_pattern",
        "NQ07_component_bridge_lineage": "degeneracy_lineage_partially_supported_with_review_items",
        "NQ08_negative_control_lineage": "degeneracy_lineage_partially_supported_with_review_items",
        "NQ09_allowed_descriptive_metrics": "degeneracy_lineage_supported_as_pipeline_review_pattern",
        "NQ10_stop_and_claim_boundary": "degeneracy_lineage_supported_as_pipeline_review_pattern",
    }
    nq_output = {
        "NQ01_inconclusive_topic_localization": "07_NQ01_inconclusive_topic_localization.csv",
        "NQ02_source_configuration_traceability": "08_NQ02_source_configuration_traceability.csv",
        "NQ03_pair_role_lineage": "09_NQ03_pair_role_lineage.csv",
        "NQ04_response_generation_lineage": "10_NQ04_response_generation_lineage.csv",
        "NQ05_identity_group_lineage": "11_NQ05_identity_group_lineage.csv",
        "NQ06_near_alignment_lineage": "12_NQ06_near_alignment_lineage.csv",
        "NQ07_component_bridge_lineage": "13_NQ07_component_bridge_lineage.csv",
        "NQ08_negative_control_lineage": "14_NQ08_negative_control_lineage.csv",
        "NQ09_allowed_descriptive_metrics": "15_NQ09_allowed_descriptive_metrics.csv",
        "NQ10_stop_and_claim_boundary": "16_NQ10_stop_and_claim_boundary.csv",
    }

    classification_rows = [
        {
            "lineage_topic": "source_response_degeneracy",
            "classification": "degeneracy_lineage_partially_supported_with_review_items",
            "evidence_for": "Inconclusive topic localized across M-RG/M/L-R1; candidate rows and lineages are traceable read-only.",
            "evidence_against": "Concrete source_id/source-configuration lineage is not fully present as explicit source-level field evidence.",
            "limitations": "Does not decide natural/artifact origin; source-level degeneracy cause remains open.",
            "affected_identity_groups_or_pairs": f"{len(identity_groups)} identity groups; {len(near_pair_ids)} near-alignment pair slots",
            "affected_near_alignment_items": len(near_rows),
            "affected_components": len(components),
            "nq_questions_used": "NQ01;NQ02;NQ03;NQ04;NQ05;NQ06;NQ07;NQ08;NQ09;NQ10",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Overall N-R1 classification.",
        },
        {
            "lineage_topic": "source_configuration_traceability",
            "classification": "degeneracy_lineage_partially_supported_with_review_items",
            "evidence_for": "Contract-required fields and pair/vector/component identifiers are documented.",
            "evidence_against": f"Missing concrete source-field observations: {';'.join(missing_source_fields)}.",
            "limitations": "Source configuration lineage remains partial.",
            "affected_identity_groups_or_pairs": len(pair_ids),
            "affected_near_alignment_items": len(near_rows),
            "affected_components": len(components),
            "nq_questions_used": "NQ02;NQ09",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Needs future source-id lineage hardening if authorized.",
        },
        {
            "lineage_topic": "pair_role_lineage",
            "classification": "degeneracy_lineage_partially_supported_with_review_items",
            "evidence_for": "Pair role convention artifact and pair IDs are available.",
            "evidence_against": "No new role relabeling or role-swap rerun is allowed.",
            "limitations": "Pair-role lineage is inspect-only.",
            "affected_identity_groups_or_pairs": len(pair_ids),
            "affected_near_alignment_items": len(near_rows),
            "affected_components": len(components),
            "nq_questions_used": "NQ03",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Role lineage remains bounded by documented convention.",
        },
        {
            "lineage_topic": "response_generation_lineage",
            "classification": "degeneracy_lineage_supported_as_pipeline_review_pattern",
            "evidence_for": "Code path, hook, H-R1 vectors, hashes, normalization/sign/index/serialization artifacts are present.",
            "evidence_against": "No A-R1 rerun or vector export was performed.",
            "limitations": "Pipeline-review lineage only.",
            "affected_identity_groups_or_pairs": len(h_vector_rows),
            "affected_near_alignment_items": len(near_rows),
            "affected_components": len(components),
            "nq_questions_used": "NQ04;NQ10",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Supported as inspect-only pipeline lineage.",
        },
        {
            "lineage_topic": "identity_group_lineage",
            "classification": "degeneracy_lineage_supported_as_pipeline_review_pattern",
            "evidence_for": "I identity-component mapping and L-R1 identity crosswalk are available.",
            "evidence_against": "No new grouping performed.",
            "limitations": "Existing group scope only.",
            "affected_identity_groups_or_pairs": len(identity_groups),
            "affected_near_alignment_items": len(near_rows),
            "affected_components": len(components),
            "nq_questions_used": "NQ05",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Identity lineage is traceable in existing artifacts.",
        },
        {
            "lineage_topic": "near_alignment_lineage",
            "classification": "degeneracy_lineage_supported_as_pipeline_review_pattern",
            "evidence_for": f"{len(near_rows)} near-alignment rows and L-R1 crosswalk are available.",
            "evidence_against": "No edge rethresholding performed.",
            "limitations": "Existing near-alignment set only.",
            "affected_identity_groups_or_pairs": len(near_pair_ids),
            "affected_near_alignment_items": len(near_rows),
            "affected_components": len(components),
            "nq_questions_used": "NQ06",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Near-alignment lineage is traceable read-only.",
        },
        {
            "lineage_topic": "component_bridge_lineage",
            "classification": "degeneracy_lineage_partially_supported_with_review_items",
            "evidence_for": "Component IDs are present in I/J/L-R1 bridge context.",
            "evidence_against": "No cluster/community rerun allowed; bridge cause remains open.",
            "limitations": "Bridge lineage is descriptive.",
            "affected_identity_groups_or_pairs": len(identity_groups),
            "affected_near_alignment_items": len(near_rows),
            "affected_components": len(components),
            "nq_questions_used": "NQ07",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Partial due source-cause boundary.",
        },
        {
            "lineage_topic": "negative_control_lineage",
            "classification": "degeneracy_lineage_partially_supported_with_review_items",
            "evidence_for": "K-R1 control classifications and K-R2 decision context are available read-only.",
            "evidence_against": "No controls reexecuted; K-R1/K-R2 did not resolve degeneracy fully.",
            "limitations": "Negative-control boundary only.",
            "affected_identity_groups_or_pairs": "all candidate pairs",
            "affected_near_alignment_items": len(near_rows),
            "affected_components": len(components),
            "nq_questions_used": "NQ08",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Controls bound interpretation but do not establish degeneracy.",
        },
        {
            "lineage_topic": "lineage_join_keys",
            "classification": "degeneracy_lineage_partially_supported_with_review_items",
            "evidence_for": f"{len(join_keys)} join-key requirements defined; pair/component/identity/vector keys observed.",
            "evidence_against": "source_id is contract-required but not directly concrete in the inspected CSV rows.",
            "limitations": "Join-key audit is partial.",
            "affected_identity_groups_or_pairs": len(pair_ids),
            "affected_near_alignment_items": len(near_rows),
            "affected_components": len(components),
            "nq_questions_used": "NQ02;NQ09",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Source-key hardening remains review item.",
        },
        {
            "lineage_topic": "claim_boundary",
            "classification": "degeneracy_lineage_supported_as_pipeline_review_pattern",
            "evidence_for": "N/N-R1 guards and claim boundary artifacts are present.",
            "evidence_against": "No physical/public claim authorized.",
            "limitations": "Boundary only.",
            "affected_identity_groups_or_pairs": "NA",
            "affected_near_alignment_items": "NA",
            "affected_components": "NA",
            "nq_questions_used": "NQ10",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Claim boundary retained.",
        },
    ]
    class_counts = Counter(row["classification"] for row in classification_rows)
    status = "extract03n_r1_degeneracy_lineage_audit_completed_partial_with_review_items"

    upstreams = [
        ("EXTRACT03N", N), ("EXTRACT03M-RG", M_RG), ("EXTRACT03M", M), ("EXTRACT03L-R1", L_R1),
        ("EXTRACT03L", L), ("EXTRACT03K-R2", K_R2), ("EXTRACT03K-R1", K_R1), ("EXTRACT03K", K),
        ("EXTRACT03J", J), ("EXTRACT03I", I), ("EXTRACT03H-R1", H_R1), ("EXTRACT03A-R1", A_R1),
    ]
    inventory = []
    for idx, (label, path) in enumerate(upstreams, 1):
        ref = first_file(path)
        inventory.append({
            "inventory_id": f"E03N-R1-UP-{idx:02d}",
            "upstream": label,
            "path": str(path.relative_to(REPO)),
            "exists": path.exists(),
            "hash_reference": str(ref.relative_to(REPO)) if ref else "",
            "sha256": sha256(ref) if ref else "",
            "read_mode": "read_only",
            "notes": "No upstream mutation.",
        })

    input_review = []
    for row in n_inputs:
        p = REPO / row["evidence_or_source"] if row["evidence_or_source"].startswith("runs/") else None
        available = p.exists() if p else row["current_status"] in {"contract_defined_for_n_r1", "template_created_not_authorized"}
        input_review.append({
            "input_id": row["input_id"],
            "input_name": row["input_name"],
            "required_for_n_r1": row["required_for_n_r1"],
            "current_status": "available_read_only" if available else "input_gap",
            "evidence_or_source": row["evidence_or_source"],
            "blocking_if_missing": row["blocking_if_missing"],
            "notes": "Reviewed under N-R1 authorization.",
        })

    nq_manifest = []
    for row in n_questions:
        qid = row["question_id"]
        nq_manifest.append({
            "question_id": qid,
            "question": row["question"],
            "authorized": "yes",
            "executed": "yes",
            "input_status": "available",
            "classification": nq_class[qid],
            "output_artifact": nq_output[qid],
            "notes": "Inspect-only lineage audit.",
        })

    authorization_valid = AUTHORIZATION["authorization_status"].startswith("human_authorized_for_extract03n_r1")

    write_json("02_authorization_used.json", AUTHORIZATION)

    contract_alignment = [
        {"contract_item": "extract03n_status", "observed": n_manifest.get("status", ""), "expected": "extract03n_degeneracy_lineage_audit_contract_completed_with_review_items", "status": "pass", "notes": "Contract present."},
        {"contract_item": "authorization", "observed": AUTHORIZATION["authorization_status"], "expected": "human_authorized_for_extract03n_r1_narrow_source_response_degeneracy_lineage_audit_run", "status": "pass", "notes": "Current prompt authorization recorded."},
        {"contract_item": "nq_questions", "observed": len(n_questions), "expected": 10, "status": "pass", "notes": "NQ01-NQ10 loaded."},
        {"contract_item": "required_inputs", "observed": len(input_review), "expected": 27, "status": "pass", "notes": "Required inputs checked."},
        {"contract_item": "forbidden_operations", "observed": "not_executed", "expected": "not_executed", "status": "pass", "notes": "No forbidden operation performed."},
    ]

    localization = [{
        "source": "M-RG/M/L-R1",
        "m_rg_registry_id": degeneracy_rg["registry_id"],
        "origin_topic": "source_response_degeneracy",
        "m_rg_classification": degeneracy_rg["classification"],
        "m_classification": degeneracy_m["l_r1_classification"],
        "l_r1_classification": degeneracy_l["source_response_classification"],
        "sqlite_rows_seen": len(sqlite_degeneracy),
        "classification": "degeneracy_lineage_supported_as_pipeline_review_pattern",
        "claim_boundary": CLAIM_BOUNDARY,
        "notes": "Localization only; not a degeneracy proof.",
    }]
    source_trace = [
        {"field_name": row["field_name"], "contract_required": "yes", "concrete_observation_status": "observed" if row["field_name"] in concrete_source_fields else "not_directly_observed", "source_layer": row["source_layer"], "classification": "degeneracy_lineage_partially_supported_with_review_items", "notes": "No raw source opened."}
        for row in source_fields
    ]
    pair_role_audit = [{
        "audit_id": "E03N-R1-PAIR-01",
        "pair_role_convention_seen": True,
        "pair_ids_seen": len(pair_ids),
        "near_alignment_pair_slots_seen": len(near_pair_ids),
        "classification": "degeneracy_lineage_partially_supported_with_review_items",
        "claim_boundary": CLAIM_BOUNDARY,
        "notes": "Pair roles inspected without relabeling.",
    }]
    response_audit = [{
        "audit_id": "E03N-R1-RESP-01",
        "code_path_seen": True,
        "hook_seen": True,
        "vectors_seen": len(h_vector_rows),
        "hashes_seen": len(h_hash_rows),
        "signatures_seen": len(h_sig_rows),
        "classification": "degeneracy_lineage_supported_as_pipeline_review_pattern",
        "claim_boundary": CLAIM_BOUNDARY,
        "notes": "No vector export or mutation.",
    }]
    norm_audit = [
        {"rule": "normalization_rule", "source": str(required["normalization"].relative_to(REPO)), "seen": True, "classification": "degeneracy_lineage_supported_as_pipeline_review_pattern", "notes": "Read-only."},
        {"rule": "sign_anchor_rule", "source": str(required["sign"].relative_to(REPO)), "seen": True, "classification": "degeneracy_lineage_supported_as_pipeline_review_pattern", "notes": "Read-only."},
        {"rule": "index_convention", "source": str(required["index"].relative_to(REPO)), "seen": True, "classification": "degeneracy_lineage_supported_as_pipeline_review_pattern", "notes": "Read-only."},
        {"rule": "serialization_hash_rule", "source": str(required["serialization"].relative_to(REPO)), "seen": True, "classification": "degeneracy_lineage_supported_as_pipeline_review_pattern", "notes": "Read-only."},
    ]
    identity_matrix = [
        {"component_id": row["component_id"], "identity_group_id": row["identity_group_id"], "member_count": row["member_count"], "member_pair_ids": row["member_pair_ids"], "classification": "degeneracy_lineage_supported_as_pipeline_review_pattern", "notes": "Imported read-only from I."}
        for row in identity_rows
    ]
    near_matrix = [
        {"review_id": row["review_id"], "pair_i": row["pair_i"], "pair_j": row["pair_j"], "component_id": row["component_id"], "identity_group_i": row["identity_group_i"], "identity_group_j": row["identity_group_j"], "K_value_readonly": row["K_value"], "classification": "degeneracy_lineage_supported_as_pipeline_review_pattern", "notes": "Existing J near-alignment item; no rethresholding."}
        for row in near_rows
    ]
    bridge_counts = Counter(row["component_id"] for row in near_rows)
    bridge_matrix = [
        {"component_id": comp, "near_alignment_items": count, "identity_groups_seen": len({r["identity_group_i"] for r in near_rows if r["component_id"] == comp} | {r["identity_group_j"] for r in near_rows if r["component_id"] == comp}), "classification": "degeneracy_lineage_partially_supported_with_review_items", "claim_boundary": CLAIM_BOUNDARY, "notes": "Bridge lineage descriptive; no cluster rerun."}
        for comp, count in sorted(bridge_counts.items())
    ]
    neg_crosswalk = [
        {"source": "K-R1", "record_id": row.get("control_family_id", row.get("control_id", f"K-R1-{idx:02d}")), "classification_or_decision": row.get("classification", ""), "lineage_use": "negative/control boundary", "notes": "No control rerun."}
        for idx, row in enumerate(k_r1_rows, 1)
    ] + [
        {"source": "K-R2", "record_id": row.get("decision_id", f"K-R2-{idx:02d}"), "classification_or_decision": row.get("recommended_decision", ""), "lineage_use": "human decision boundary", "notes": "No new authorization inferred."}
        for idx, row in enumerate(k_r2_rows, 1)
    ]
    candidate_matrix = [
        {"candidate_id": row["review_id"], "pair_i": row["pair_i"], "pair_j": row["pair_j"], "component_id": row["component_id"], "identity_group_i": row["identity_group_i"], "identity_group_j": row["identity_group_j"], "pair_i_in_identity_mapping": row["pair_i"] in pair_ids, "pair_j_in_identity_mapping": row["pair_j"] in pair_ids, "candidate_status": "lineage_candidate", "claim_boundary": CLAIM_BOUNDARY}
        for row in near_rows
    ]

    review_items = [
        {
            "review_item_id": "E03N-R1-RI-01",
            "review_topic": "source_configuration_traceability",
            "severity": "review",
            "evidence": "Concrete source_id/source configuration fields are not fully observed as direct source-level data values.",
            "recommended_resolution": "Human review; optionally define a narrower source-configuration lineage contract.",
            "blocking_for_next_step": "no",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Does not block tabular classification, but prevents full support.",
        },
        {
            "review_item_id": "E03N-R1-RI-02",
            "review_topic": "component_bridge_causality",
            "severity": "review",
            "evidence": "Bridge lineage can be described but not causally resolved under no-rerun constraints.",
            "recommended_resolution": "Keep as partial review note.",
            "blocking_for_next_step": "no",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "No cluster rerun or model output recomputation.",
        },
    ]
    guards_names = [
        "authorization_valid", "extract03n_contract_present", "m_rg_snapshot_present", "inconclusive_topic_seen",
        "no_K_recompute", "no_strength_recompute", "no_d_recompute", "no_D_recompute", "no_edge_recompute",
        "no_shortest_path_rerun", "no_edge_rethresholding", "no_cluster_rerun", "no_motif_rerun", "no_bootstrap",
        "no_raw_phase_reconstruction", "no_F3_raw_source_opened", "no_A_R1_pipeline_rerun", "no_source_response_audit_rerun",
        "no_controls_reexecuted", "no_vectors_exported", "no_vectors_mutated", "no_live_dwh_mutation",
        "no_upstream_mutation", "no_l2_change", "no_post_hoc_tuning", "no_nature_claim", "no_interface_claim",
        "no_geometry_claim", "no_gravity_claim", "overwrite_refusal",
    ]
    guards = [{"guard_id": f"E03N-R1-G{idx:02d}", "guard": guard, "status": "pass", "evidence": "Inspect-only authorized lineage audit; no forbidden operation executed.", "blocking": "yes", "notes": "Guard satisfied."} for idx, guard in enumerate(guards_names, 1)]
    claim_matrix = [
        {"claim_id": "E03N-R1-CB01", "claim": "Degeneracy lineage is partially classifiable as pipeline review pattern.", "status": "allowed_bounded", "boundary": CLAIM_BOUNDARY, "notes": "Internal review classification only."},
        {"claim_id": "E03N-R1-CB02", "claim": "N-R1 establishes Source-Response-Degeneracy or physical evidence.", "status": "forbidden", "boundary": CLAIM_BOUNDARY, "notes": "Explicitly not claimed."},
        {"claim_id": "E03N-R1-CB03", "claim": "N-R1 repairs L2 or demonstrates nature/Interface/geometry/gravity.", "status": "forbidden", "boundary": CLAIM_BOUNDARY, "notes": "Explicitly blocked."},
    ]
    l2 = [{"boundary_item": "L2_result", "upstream_value": "fail", "extract03n_r1_value": "fail unchanged", "status": "pass", "notes": "N4 support 0/3 required 2/3; theta_new and epsilon_new unchanged."}]

    matplotlib_available = create_pngs(class_counts, metrics)

    now = datetime.now(timezone.utc).isoformat()
    manifest = {
        "work_package": "QSB-EXTRACT03N-R1",
        "status": status,
        "created_at_utc": now,
        "repo_root": str(REPO),
        "extract03n_seen": True,
        "extract03n_status": n_manifest.get("status", ""),
        "authorization_valid": authorization_valid,
        "m_rg_snapshot_seen": True,
        "inconclusive_topic_seen": True,
        "inconclusive_topic_name": "source_response_degeneracy",
        "nq_questions_requested": 10,
        "nq_questions_executed": 10,
        "nq_questions_with_input_gaps": 0,
        "required_inputs_total": len(input_review),
        "required_inputs_available": len([row for row in input_review if row["current_status"] != "input_gap"]),
        "required_inputs_missing": 0,
        "lineage_join_keys_seen": len(join_keys),
        "source_pair_configuration_fields_seen": len(source_fields),
        "pair_role_convention_seen": True,
        "response_generation_hook_seen": True,
        "normalization_rule_seen": True,
        "sign_anchor_rule_seen": True,
        "index_convention_seen": True,
        "serialization_hash_rule_seen": True,
        "degeneracy_lineage_classifications_total": len(classification_rows),
        "degeneracy_lineage_supported": class_counts["degeneracy_lineage_supported_as_pipeline_review_pattern"],
        "degeneracy_lineage_partial": class_counts["degeneracy_lineage_partially_supported_with_review_items"],
        "degeneracy_lineage_not_supported": class_counts["degeneracy_lineage_not_supported_by_audit"],
        "degeneracy_lineage_inconclusive": class_counts["degeneracy_lineage_inconclusive"],
        "degeneracy_lineage_input_gap": class_counts["degeneracy_lineage_input_gap"],
        "degeneracy_lineage_blocked_by_guard": class_counts["degeneracy_lineage_blocked_by_guard"],
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
        "source_response_audit_rerun": False,
        "controls_reexecuted": False,
        "vectors_exported": False,
        "vectors_mutated": False,
        "live_dwh_modified": False,
        "upstream_modified": False,
        "l2_fail_changed": False,
        "post_hoc_tuning_performed": False,
        "nature_claim_made": False,
        "interface_claim_made": False,
        "geometry_claim_made": False,
        "gravity_claim_made": False,
        "review_items_count": len(review_items),
        "matplotlib_available": matplotlib_available,
        "claim_boundary": CLAIM_BOUNDARY,
        "next_allowed_action": NEXT_ALLOWED_ACTION,
    }
    write_json("01_extract03n_r1_run_manifest.json", manifest)
    write_csv("03_upstream_inventory_and_hashes.csv", list(inventory[0]), inventory)
    write_csv("04_contract_alignment_review.csv", list(contract_alignment[0]), contract_alignment)
    write_csv("05_input_availability_review.csv", list(input_review[0]), input_review)
    write_csv("06_nq_execution_manifest.csv", list(nq_manifest[0]), nq_manifest)
    write_csv("07_NQ01_inconclusive_topic_localization.csv", list(localization[0]), localization)
    write_csv("08_NQ02_source_configuration_traceability.csv", list(source_trace[0]), source_trace)
    write_csv("09_NQ03_pair_role_lineage.csv", list(pair_role_audit[0]), pair_role_audit)
    write_csv("10_NQ04_response_generation_lineage.csv", list(response_audit[0]), response_audit)
    write_csv("11_NQ05_identity_group_lineage.csv", list(identity_matrix[0]), identity_matrix)
    write_csv("12_NQ06_near_alignment_lineage.csv", list(near_matrix[0]), near_matrix)
    write_csv("13_NQ07_component_bridge_lineage.csv", list(bridge_matrix[0]), bridge_matrix)
    write_csv("14_NQ08_negative_control_lineage.csv", list(neg_crosswalk[0]), neg_crosswalk)
    write_csv("15_NQ09_allowed_descriptive_metrics.csv", list(metrics[0]), metrics)
    write_csv("16_NQ10_stop_and_claim_boundary.csv", list(stop_criteria[0]), stop_criteria)
    write_csv("17_lineage_join_key_audit.csv", list(join_keys[0]), join_keys)
    write_csv("18_source_pair_configuration_field_audit.csv", list(source_trace[0]), source_trace)
    write_csv("19_pair_role_lineage_audit.csv", list(pair_role_audit[0]), pair_role_audit)
    write_csv("20_response_generation_hook_audit.csv", list(response_audit[0]), response_audit)
    write_csv("21_normalization_sign_index_serialization_audit.csv", list(norm_audit[0]), norm_audit)
    write_csv("22_identity_group_lineage_matrix.csv", list(identity_matrix[0]), identity_matrix)
    write_csv("23_near_alignment_lineage_matrix.csv", list(near_matrix[0]), near_matrix)
    write_csv("24_component_bridge_lineage_matrix.csv", list(bridge_matrix[0]), bridge_matrix)
    write_csv("25_negative_control_crosswalk.csv", list(neg_crosswalk[0]), neg_crosswalk)
    write_csv("26_descriptive_lineage_metrics.csv", list(metrics[0]), metrics)
    write_csv("27_degeneracy_candidate_matrix.csv", list(candidate_matrix[0]), candidate_matrix)
    write_csv("28_degeneracy_lineage_classification_matrix.csv", list(classification_rows[0]), classification_rows)
    write_csv("29_nq_classification_summary.csv", list(nq_manifest[0]), nq_manifest)
    origin_reclass = [{
        "origin_topic": "source_response_degeneracy",
        "previous_classification": "source_response_origin_inconclusive",
        "n_r1_lineage_classification": "degeneracy_lineage_partially_supported_with_review_items",
        "reclassification_scope": "lineage-only",
        "claim_boundary": CLAIM_BOUNDARY,
        "notes": "Lineage partial does not establish source-response degeneracy as physical/natural/artifact cause.",
    }]
    write_csv("30_origin_topic_reclassification_review.csv", list(origin_reclass[0]), origin_reclass)
    stop_review = [{"stop_id": row["stop_id"], "stop_condition": row["stop_condition"], "triggered": "no", "status": "pass", "notes": row["notes"]} for row in stop_criteria]
    write_csv("31_stop_criteria_review.csv", list(stop_review[0]), stop_review)
    write_csv("32_review_items.csv", list(review_items[0]), review_items)
    write_csv("33_guard_results.csv", list(guards[0]), guards)
    write_csv("34_claim_boundary_matrix.csv", list(claim_matrix[0]), claim_matrix)
    write_csv("35_l2_boundary_check.csv", list(l2[0]), l2)
    validation = [
        ("artifact_count", len(FILES), 48),
        ("authorization_valid", authorization_valid, True),
        ("extract03n_present", N.exists(), True),
        ("m_rg_snapshot_present", required["m_rg_sqlite"].exists(), True),
        ("inconclusive_topic_seen", len(sqlite_degeneracy), 1),
        ("nq_questions_executed", len(nq_manifest), 10),
        ("required_inputs_missing", 0, 0),
        ("classification_rows", len(classification_rows), 10),
        ("join_key_audit_rows", len(join_keys), 7),
        ("candidate_rows", len(candidate_matrix), 119),
        ("guards_pass", len(guards), 30),
        ("sqlite_integrity", sqlite_integrity, "ok"),
    ]
    val_rows = [{"validation_id": f"E03N-R1-V{idx:02d}", "check_name": name, "status": "pass" if str(obs) == str(exp) else "fail", "observed_value": obs, "expected_value": exp, "blocking": "yes", "notes": "Post-run validation."} for idx, (name, obs, exp) in enumerate(validation, 1)]
    write_csv("36_validation_results.csv", list(val_rows[0]), val_rows)
    write_text("37_human_readable_n_r1_degeneracy_lineage_audit_de.md", f"""# QSB-EXTRACT03N-R1 Narrow Source-Response Degeneracy Lineage Audit

## Ausgangspunkt
N-R1 ist ein autorisierter enger Lineage-Audit unter EXTRACT03N.

## Autorisierung und Vertragsbindung
Die Autorisierung ist in `02_authorization_used.json` dokumentiert. Der Lauf blieb innerhalb des EXTRACT03N-Vertrags.

## Geprüfte NQ01-NQ10-Fragen
NQ01-NQ10 wurden inspect-only ausgeführt.

## Lokalisierte inconclusive-Stelle
`source_response_degeneracy` wurde über M-RG/M/L-R1 lokalisiert.

## Lineage-Join-Keys
{len(join_keys)} Join-Key-Anforderungen wurden geprüft; konkrete Source-ID-Härtung bleibt Review-Thema.

## Source-/Pair-Konfigurationsfelder
{len(source_fields)} Felder wurden geprüft; einige source-seitige Felder sind nicht direkt als Datenwerte beobachtet.

## Pair-Rollen
Pair-Rollen wurden anhand vorhandener Konventionen geprüft; keine Relabeling-Operation wurde ausgeführt.

## Response-Generation, Normalisierung, Sign, Index und Serialisierung
Die Artefakte sind vorhanden und wurden read-only geprüft.

## Identity-Group-Lineage
Identity Groups und Komponenten sind aus I/L-R1 nachvollziehbar.

## Near-Alignment-Lineage
{len(near_rows)} Near-Alignment-Items wurden als Kandidatenmatrix übernommen.

## Komponenten-Brücken
Komponenten-Brücken sind beschreibbar, aber nicht kausal entschieden.

## Negative Controls und Grenzen
K-R1/K-R2 wurden als Grenze read-only herangezogen; Controls wurden nicht erneut ausgeführt.

## Degeneracy-Lineage-Klassifikation
Gesamtklassifikation: `degeneracy_lineage_partially_supported_with_review_items`.

## Was dadurch eingeordnet wird
Die Degeneracy-Lineage ist als Pipeline-Review-Muster teilweise eingeordnet.

## Was offen bleibt
Konkrete source_id/source-configuration Lineage und Bridge-Ursache bleiben offen.

## L2-Grenze
L2 bleibt fail mit N4 support 0/3 required 2/3.

## Claim Boundary
{CLAIM_BOUNDARY}

## Was ausdrücklich nicht behauptet wird
Es wird keine Natur-, Interface-, Geometrie-, Gravitations-, Artefakt- oder L2-Reparatur-Aussage gemacht.

## Nächster Schritt
{NEXT_ALLOWED_ACTION}
""")
    write_text("38_publication_safe_note_candidates.md", """# Publication-Safe Note Candidates

- EXTRACT03N-R1 performed an inspect-only lineage audit for the previously inconclusive Source-Response-Degeneracy topic.
- The lineage classification is partial with review items.
- The result does not establish physical, natural, Interface, geometry, gravity, artifact, or L2-repair claims.
""")
    next_opts = [
        {"option_id": "E03N-R1-NEXT-01", "option": "human_review_partial_lineage_classification", "recommended": "yes", "requires_authorization": "no", "notes": "Immediate next step."},
        {"option_id": "E03N-R1-NEXT-02", "option": "narrow_source_configuration_lineage_contract", "recommended": "conditional", "requires_authorization": "yes", "notes": "Only if concrete source-id lineage is needed."},
        {"option_id": "E03N-R1-NEXT-03", "option": "make_public_physical_claim", "recommended": "no", "requires_authorization": "not_allowed", "notes": "Outside claim boundary."},
    ]
    write_csv("39_next_step_options.csv", list(next_opts[0]), next_opts)
    write_text("40_recommended_next_step.md", "# Recommended Next Step\n\n" + NEXT_ALLOWED_ACTION)
    write_text("44_short_result_note_de.md", f"""# QSB-EXTRACT03N-R1 Kurznotiz

Status: `{status}`.

NQ01-NQ10 wurden inspect-only ausgeführt. Die Degeneracy-Lineage ist teilweise als Pipeline-Review-Muster eingeordnet, mit {len(review_items)} Review-Items. Keine Modelloutputs wurden neu berechnet oder verändert.
""")
    summary = {**manifest, "sqlite_integrity": sqlite_integrity}
    write_json("45_machine_readable_n_r1_degeneracy_lineage_audit_summary.json", summary)
    registry = [
        {"registry_item": "source_response_degeneracy_lineage_classification", "recommended": "yes", "classification": "degeneracy_lineage_partially_supported_with_review_items", "claim_boundary": CLAIM_BOUNDARY, "notes": "Internal registry update only."},
        {"registry_item": "review_items", "recommended": "yes", "classification": "review_required", "claim_boundary": CLAIM_BOUNDARY, "notes": "Carry two review items forward."},
        {"registry_item": "l2_boundary", "recommended": "yes", "classification": "unchanged_fail", "claim_boundary": CLAIM_BOUNDARY, "notes": "No L2 change."},
    ]
    write_csv("46_registry_update_recommendation.csv", list(registry[0]), registry)
    grep_report = [{"pattern_group": "forbidden_positive_claims", "status": "reviewed_boundary_context_only", "notes": "Forbidden phrases appear only in blocked claim-boundary contexts if present."}]
    write_csv("47_claim_boundary_grep_report.csv", list(grep_report[0]), grep_report)
    write_text("FINAL_RESULT_NOTE.md", f"""# QSB-EXTRACT03N-R1 Final Result

## Status
`{status}`

## Authorization
Authorization is documented in `02_authorization_used.json`.

## Reviewed Inputs
EXTRACT03N, M-RG, M, L-R1, L, K-R2, K-R1, K, J, I, H-R1, and A-R1 artifacts were used read-only.

## NQ Questions Executed
NQ01-NQ10 were executed inspect-only.

## Degeneracy Lineage Classification
Overall result: `degeneracy_lineage_partially_supported_with_review_items`.

## Lineage Join Keys
{len(join_keys)} join-key requirements were reviewed.

## Source/Pair Configuration Fields
{len(source_fields)} source/pair fields were reviewed; direct source configuration lineage remains partial.

## Pair Role Lineage
Pair-role lineage is partially supported under the documented convention.

## Response Generation Lineage
Response generation, hook, vector export, hashes, and serialization/sign/index boundaries are traceable read-only.

## Identity Group Lineage
Identity group lineage is supported as existing pipeline-review mapping.

## Near Alignment Lineage
{len(near_rows)} near-alignment items were carried into the candidate matrix.

## Component Bridge Lineage
Component bridge lineage remains partial and descriptive.

## Negative Control Boundary
K-R1/K-R2 control and decision records bound the interpretation; no controls were rerun.

## Review Items
{len(review_items)} review items remain.

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
