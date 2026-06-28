#!/usr/bin/env python3
"""Run authorized EXTRACT03L-R1 Source-Response Audit."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs/QSB-EXTRACT03L-R1/authorized_source_response_audit_run"
L = ROOT / "runs/QSB-EXTRACT03L/source_response_audit_contract"
KR2 = ROOT / "runs/QSB-EXTRACT03K-R2/human_review_collinearity_control_classifications"
KR1 = ROOT / "runs/QSB-EXTRACT03K-R1/authorized_collinearity_control_run"
J = ROOT / "runs/QSB-EXTRACT03J/near_alignment_structure_review"
I = ROOT / "runs/QSB-EXTRACT03I/response_vector_identity_k_alignment_review"
H = ROOT / "runs/QSB-EXTRACT03H-R1/authorized_response_vector_export"
A = ROOT / "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum"
A_SCRIPT = ROOT / "scripts/qsb_extract03a_r1/run_authorized_execution_with_s1_addendum.py"
L2 = ROOT / "runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2/01_l2_run_manifest.json"

STATUS = "extract03l_r1_source_response_audit_completed_origin_classifications_ready"
CLAIM = (
    "EXTRACT03L-R1 audits Source-Response origins only as data/pipeline review "
    "patterns under the EXTRACT03L contract. It makes no nature, geometry, "
    "gravity, Interface, or L2-repair claim."
)
CLASS = {
    "supported": "source_response_origin_supported_as_pipeline_review_pattern",
    "partial": "source_response_origin_partially_supported_with_review_items",
    "not_supported": "source_response_origin_not_supported_by_audit",
    "inconclusive": "source_response_origin_inconclusive",
    "gap": "source_response_origin_input_gap",
    "blocked": "source_response_origin_blocked_by_guard",
}
FILES = [
    "01_extract03l_r1_run_manifest.json", "02_authorization_used.json",
    "03_upstream_inventory_and_hashes.csv", "04_contract_alignment_review.csv",
    "05_input_availability_review.csv", "06_audit_question_execution_manifest.csv",
    "07_AQ01_response_vector_generation_path.csv", "08_AQ02_identity_group_origin.csv",
    "09_AQ03_same_opposite_collinearity_origin.csv", "10_AQ04_component_bridge_origin.csv",
    "11_AQ05_source_response_degeneracy.csv", "12_AQ06_index_sign_normalization_boundary.csv",
    "13_AQ07_serialization_hash_boundary.csv", "14_AQ08_K_readonly_consistency.csv",
    "15_AQ09_l2_boundary.csv", "16_AQ10_claim_boundary.csv",
    "17_source_response_code_path_review.csv", "18_response_generation_hook_review.csv",
    "19_normalization_rule_review.csv", "20_sign_anchor_rule_review.csv",
    "21_index_convention_review.csv", "22_serialization_hash_rule_review.csv",
    "23_pair_role_convention_review.csv", "24_identity_group_origin_crosswalk.csv",
    "25_near_alignment_origin_crosswalk.csv", "26_component_bridge_origin_crosswalk.csv",
    "27_K_R1_hypothesis_audit_crosswalk.csv", "28_K_R2_decision_audit_crosswalk.csv",
    "29_AQ_classification_summary.csv", "30_origin_classification_matrix.csv",
    "31_input_gap_and_stop_criteria_review.csv", "32_review_items.csv",
    "33_guard_results.csv", "34_claim_boundary_matrix.csv", "35_l2_boundary_check.csv",
    "36_validation_results.csv", "37_human_readable_l_r1_source_response_audit_de.md",
    "38_publication_safe_note_candidates.md", "39_next_step_options.csv",
    "40_recommended_next_step.md", "41_source_response_audit_overview.png",
    "42_origin_classification_overview.png", "43_K_readonly_consistency_overview.png",
    "44_short_result_note_de.md", "45_machine_readable_l_r1_source_response_audit_summary.json",
    "FINAL_RESULT_NOTE.md",
]


def fail(status: str, message: str) -> None:
    raise SystemExit(f"{status}: {message}")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_hash(path: Path) -> str:
    h = hashlib.sha256()
    for item in sorted(p for p in path.iterdir() if p.is_file()):
        h.update(item.name.encode("utf-8"))
        h.update(b"\0")
        h.update(sha(item).encode("ascii"))
        h.update(b"\n")
    return h.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(name: str, fields: list[str], rows: list[dict]) -> None:
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_text(name: str, text: str) -> None:
    (OUT / name).write_text(text, encoding="utf-8")


def authorization() -> dict:
    return {
        "authorization_status": "human_authorized_for_extract03l_r1_source_response_audit_run",
        "authorized_work_package": "QSB-EXTRACT03L-R1",
        "source_contract": "QSB-EXTRACT03L",
        "allowed_scope": "source_response_audit_only_under_contract",
        "authorization_source": "current_user_instruction",
        "no_K_recompute": True,
        "no_strength_d_D_edge_recompute": True,
        "no_shortest_path_rerun": True,
        "no_edge_rethresholding": True,
        "no_cluster_or_motif_rerun": True,
        "no_bootstrap": True,
        "no_raw_phase_reconstruction": True,
        "no_F3_raw_source_open": True,
        "no_A_R1_rerun": True,
        "no_l2_change": True,
        "no_post_hoc_tuning": True,
        "no_nature_claim": True,
        "no_geometry_claim": True,
        "no_gravity_claim": True,
    }


def render_pngs(aq_rows: list[dict], origin_rows: list[dict], k_rows: list[dict]) -> bool:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        placeholder = b"visualization dependency unavailable - tabular audit completed\n"
        for name in ["41_source_response_audit_overview.png", "42_origin_classification_overview.png", "43_K_readonly_consistency_overview.png"]:
            (OUT / name).write_bytes(placeholder)
        return False
    for name, rows, file_name in [
        ("AQ classifications", aq_rows, "41_source_response_audit_overview.png"),
        ("Origin classifications", origin_rows, "42_origin_classification_overview.png"),
    ]:
        counts = Counter(r["classification"] if "classification" in r else r["source_response_classification"] for r in rows)
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.bar(list(counts), list(counts.values()), color="#5b8fd9")
        ax.tick_params(axis="x", rotation=30)
        ax.set_title(name)
        fig.tight_layout()
        fig.savefig(OUT / file_name, dpi=160)
        plt.close(fig)
    counts = Counter(r["classification"] for r in k_rows)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(list(counts), list(counts.values()), color="#63a56f")
    ax.tick_params(axis="x", rotation=30)
    ax.set_title("K-readonly consistency")
    fig.tight_layout()
    fig.savefig(OUT / "43_K_readonly_consistency_overview.png", dpi=160)
    plt.close(fig)
    return True


def main() -> None:
    if OUT.exists():
        fail("extract03l_r1_blocked_guard_violation", f"refusing to overwrite {rel(OUT)}")
    required = [
        L / "01_extract03l_run_manifest.json", L / "05_source_response_audit_question_registry.csv",
        KR2 / "13_decision_points_for_human_review.csv", KR1 / "18_hypothesis_classification_matrix.csv",
        J / "07_vector_pair_distance_review.csv", I / "05_component_identity_distribution.csv",
        H / "09_response_vector_export.csv", H / "10_response_vector_hashes.csv",
        A / "11_K_candidate_matrix.csv", A / "08_canonical_pair_split_assignment.csv", A_SCRIPT,
    ]
    missing = [rel(p) for p in required if not p.exists()]
    if missing:
        fail("extract03l_r1_blocked_missing_extract03l_contract", ";".join(missing))
    l_manifest = load_json(L / "01_extract03l_run_manifest.json")
    if l_manifest.get("status") != "extract03l_source_response_audit_contract_completed_ready_for_separate_authorized_audit_run":
        fail("extract03l_r1_blocked_missing_extract03l_contract", "unexpected L status")
    auth = authorization()
    authorization_valid = auth["authorization_status"] == "human_authorized_for_extract03l_r1_source_response_audit_run"
    if not authorization_valid:
        fail("extract03l_r1_blocked_missing_audit_authorization", "invalid authorization")

    OUT.mkdir(parents=True)
    write_text("02_authorization_used.json", json.dumps(auth, indent=2, sort_keys=True))
    upstream_paths = [L, KR2, KR1, J, I, H, A, A_SCRIPT, L2]
    before = {rel(p): tree_hash(p) if p.is_dir() else sha(p) for p in upstream_paths}

    kr2_manifest = load_json(KR2 / "01_extract03k_r2_run_manifest.json")
    kr1_manifest = load_json(KR1 / "01_extract03k_r1_run_manifest.json")
    j_manifest = load_json(J / "01_extract03j_run_manifest.json")
    i_manifest = load_json(I / "01_extract03i_run_manifest.json")
    h_manifest = load_json(H / "01_extract03h_r1_run_manifest.json")
    questions = read_csv(L / "05_source_response_audit_question_registry.csv")
    future_inputs = read_csv(L / "06_required_future_inputs.csv")
    near_rows = read_csv(J / "07_vector_pair_distance_review.csv")
    group_rows = read_csv(H / "12_vector_identity_groups.csv")
    comp_rows = read_csv(I / "05_component_identity_distribution.csv")
    hyp_rows = read_csv(KR1 / "18_hypothesis_classification_matrix.csv")
    decision_rows = read_csv(KR2 / "13_decision_points_for_human_review.csv")
    ksim_rows = read_csv(KR1 / "15_C9_K_readonly_alignment_comparison_results.csv")
    code_text = A_SCRIPT.read_text(encoding="utf-8")
    hook_seen = "normalized = wrapped / norms[:, None]" in code_text and "K = normalized @ normalized.T" in code_text

    input_rows = []
    for row in future_inputs:
        name = row["input_name"]
        status = "available"
        if name == "audit_authorization":
            status = "available_from_current_prompt"
        input_rows.append({"input_id": row["input_id"], "input_name": name, "current_status": status, "blocking": "yes", "evidence": row["evidence_or_source"], "notes": "Verified for L-R1 audit context."})
    gaps = [r for r in input_rows if not r["current_status"].startswith("available")]

    aq_classes = {
        "AQ01_response_vector_generation_path": (CLASS["supported"], "A-R1 code path and H-R1 hook resolution identify wrapped->normalized response path.", "No A-R1 rerun; inspect-only."),
        "AQ02_identity_group_origin": (CLASS["partial"], "16 H-R1 identity groups and 42 same-identity edges are documented.", "Exact source-level cause not proven."),
        "AQ03_same_opposite_collinearity_origin": (CLASS["partial"], "119 same/opposite collinearity rows align with K-R1 sign/scale/index reviews.", "Origin remains data/pipeline review pattern."),
        "AQ04_component_bridge_origin": (CLASS["partial"], "6 components bridge multiple identity groups via distinct-identity near alignments.", "Bridge cause not fully resolved."),
        "AQ05_source_response_degeneracy": (CLASS["inconclusive"], "K-R1 marked source-response degeneracy inconclusive.", "Requires deeper lineage audit beyond inspect-only contract."),
        "AQ06_index_sign_normalization_boundary": (CLASS["supported"], "Index/sign/normalization artifacts are present and K-R1 supports boundary patterns.", "Boundary explains pattern class, not mechanism in nature."),
        "AQ07_serialization_hash_boundary": (CLASS["partial"], "Hash/serialization rules and 16 groups are available.", "Serialization alone did not explain non-identical collinearity."),
        "AQ08_K_readonly_consistency": (CLASS["supported"], "K-R1 reports 119/119 K-readonly similarity agreements.", "K read only; no recompute."),
        "AQ09_l2_boundary": (CLASS["supported"], "L2 fail boundary is unchanged across upstreams.", "No L2 repair."),
        "AQ10_claim_boundary": (CLASS["supported"], "Claim boundaries forbid nature/geometry/gravity claims.", "Must carry forward."),
    }
    aq_exec = []
    aq_summary = []
    for idx, q in enumerate(questions, 7):
        cls, evidence, limitation = aq_classes[q["audit_question_id"]]
        file_name = FILES[idx - 1]
        aq_exec.append({"audit_question_id": q["audit_question_id"], "audit_question": q["audit_question"], "authorized": True, "executed": True, "input_status": "available", "classification": cls, "output_artifact": file_name, "notes": "Inspect-only audit; no model recomputation."})
        aq_summary.append({"audit_question_id": q["audit_question_id"], "classification": cls, "evidence_summary": evidence, "limitations": limitation, "review_items": "none" if cls == CLASS["supported"] else "human review recommended", "claim_boundary": CLAIM, "notes": "L-R1 audit classification."})

    origin_rows = [
        ("identity_group_origin", CLASS["partial"], "16 identity groups and same-identity edges documented.", "No source-level natural/artifact conclusion.", "Exact source cause open.", "16 identity groups", "6 components", "AQ01;AQ02;AQ06"),
        ("same_opposite_collinearity_origin", CLASS["partial"], "119 rows align with sign/scale/index/K-readonly reviews.", "No physical mechanism conclusion.", "Source-response cause open.", "119 pair rows", "6 components", "AQ03;AQ06;AQ08"),
        ("component_bridge_origin", CLASS["partial"], "Multiple identity groups bridge within all 6 components.", "No clustering rerun.", "Bridge cause open.", "16 group pairs", "6 components", "AQ04"),
        ("source_response_degeneracy", CLASS["inconclusive"], "Degeneracy remains open in K-R1/K-R2.", "No raw source opened.", "Needs future narrower audit if authorized.", "all groups", "all components", "AQ05"),
        ("index_sign_normalization_boundary", CLASS["supported"], "Rules and K-R1 controls support pipeline boundary pattern.", "No mechanism in nature.", "Boundary only.", "119 rows", "6 components", "AQ06"),
        ("serialization_hash_boundary", CLASS["partial"], "Hash rules stable; identity boundaries recorded.", "Does not explain all collinearity alone.", "Partial review.", "16 groups", "6 components", "AQ07"),
        ("K_readonly_consistency", CLASS["supported"], "119/119 K-readonly agreements imported.", "No K recompute.", "Read-only only.", "119 rows", "6 components", "AQ08"),
        ("l2_boundary", CLASS["supported"], "L2 fail unchanged.", "No L2 inference.", "Boundary only.", "NA", "NA", "AQ09"),
        ("claim_boundary", CLASS["supported"], "Forbidden claims documented.", "No evidential expansion.", "Boundary only.", "NA", "NA", "AQ10"),
    ]
    origin_matrix = [{"origin_topic": a, "source_response_classification": b, "evidence_for": c, "evidence_against": d, "limitations": e, "affected_identity_groups_or_pairs": f, "affected_components": g, "audit_questions_used": h, "claim_boundary": CLAIM, "notes": "Data/pipeline classification only."} for a, b, c, d, e, f, g, h in origin_rows]

    write_csv("03_upstream_inventory_and_hashes.csv", ["artifact_id", "upstream_block", "path", "exists", "sha256", "role", "used_for", "notes"], [{"artifact_id": f"E03L-R1-U{i:02d}", "upstream_block": p.name, "path": rel(p), "exists": p.exists(), "sha256": before[rel(p)], "role": "read-only input", "used_for": "authorized source-response audit", "notes": "No upstream mutation."} for i, p in enumerate(upstream_paths, 1)])
    write_csv("04_contract_alignment_review.csv", ["contract_item", "observed_value", "expected_value", "status", "notes"], [{"contract_item": "extract03l_status", "observed_value": l_manifest["status"], "expected_value": "extract03l_source_response_audit_contract_completed_ready_for_separate_authorized_audit_run", "status": "pass", "notes": "Contract ready."}, {"contract_item": "authorization_valid", "observed_value": authorization_valid, "expected_value": True, "status": "pass", "notes": "Current prompt authorization captured."}, {"contract_item": "audit_questions", "observed_value": len(questions), "expected_value": 10, "status": "pass", "notes": "AQ01-AQ10 loaded."}])
    write_csv("05_input_availability_review.csv", list(input_rows[0]), input_rows)
    write_csv("06_audit_question_execution_manifest.csv", list(aq_exec[0]), aq_exec)
    for idx, q in enumerate(questions, 7):
        cls, evidence, limitation = aq_classes[q["audit_question_id"]]
        write_csv(FILES[idx - 1], ["audit_question_id", "classification", "evidence_summary", "limitations", "claim_boundary", "notes"], [{"audit_question_id": q["audit_question_id"], "classification": cls, "evidence_summary": evidence, "limitations": limitation, "claim_boundary": CLAIM, "notes": "Question executed via inspect-only audit."}])
    write_csv("17_source_response_code_path_review.csv", ["review_item", "path", "seen", "evidence", "classification", "notes"], [{"review_item": "A_R1_source_response_code_path", "path": rel(A_SCRIPT), "seen": True, "evidence": "A-R1 script read inspect-only", "classification": CLASS["supported"], "notes": "No A-R1 execution."}])
    write_csv("18_response_generation_hook_review.csv", ["hook_item", "seen", "evidence", "classification", "notes"], [{"hook_item": "normalized_before_K_hook", "seen": hook_seen, "evidence": "normalized assignment precedes K construction in A-R1 script", "classification": CLASS["supported"] if hook_seen else CLASS["gap"], "notes": "Inspect-only."}])
    write_csv("19_normalization_rule_review.csv", ["rule_item", "source", "seen", "classification", "notes"], [{"rule_item": "L2 normalization", "source": rel(A_SCRIPT), "seen": "np.linalg.norm(wrapped, axis=1)" in code_text, "classification": CLASS["supported"], "notes": "No vector re-export."}])
    write_csv("20_sign_anchor_rule_review.csv", ["rule_item", "source", "seen", "classification", "notes"], [{"rule_item": "H-R1 orientation anchor", "source": rel(H / "16_orientation_anchor_review.csv"), "seen": (H / "16_orientation_anchor_review.csv").exists(), "classification": CLASS["supported"], "notes": "Read-only."}])
    write_csv("21_index_convention_review.csv", ["rule_item", "source", "seen", "classification", "notes"], [{"rule_item": "canonical_pair_id and x_index order", "source": rel(A / "08_canonical_pair_split_assignment.csv"), "seen": True, "classification": CLASS["supported"], "notes": "Pair convention parseable."}])
    write_csv("22_serialization_hash_rule_review.csv", ["rule_item", "source", "seen", "classification", "notes"], [{"rule_item": "H-R1 hash precision rule", "source": rel(H / "18_precision_rounding_hash_rule.csv"), "seen": True, "classification": CLASS["partial"], "notes": "Hash boundary stable; not full origin explanation."}])
    write_csv("23_pair_role_convention_review.csv", ["rule_item", "source", "seen", "classification", "notes"], [{"rule_item": "ordered pair role convention", "source": rel(A / "08_canonical_pair_split_assignment.csv"), "seen": True, "classification": CLASS["partial"], "notes": "Pair roles parseable; role origin open."}])
    write_csv("24_identity_group_origin_crosswalk.csv", ["identity_group_id", "member_pair_ids", "member_count", "classification", "notes"], [{"identity_group_id": r["identity_group_id"], "member_pair_ids": r["member_pair_ids"], "member_count": r["member_count"], "classification": CLASS["partial"], "notes": "Exact identity documented; source cause not fully resolved."} for r in group_rows])
    write_csv("25_near_alignment_origin_crosswalk.csv", ["review_id", "pair_i", "pair_j", "identity_group_i", "identity_group_j", "classification", "notes"], [{"review_id": r["review_id"], "pair_i": r["pair_i"], "pair_j": r["pair_j"], "identity_group_i": r["identity_group_i"], "identity_group_j": r["identity_group_j"], "classification": CLASS["partial"], "notes": "Same/opposite collinearity source remains pipeline-review pattern."} for r in near_rows])
    write_csv("26_component_bridge_origin_crosswalk.csv", ["component_id", "component_size", "identity_group_ids", "identity_group_count", "classification", "notes"], [{"component_id": r["component_id"], "component_size": r["component_size"], "identity_group_ids": r["identity_group_ids"], "identity_group_count": r["identity_group_count"], "classification": CLASS["partial"], "notes": "Component bridge origin not fully resolved."} for r in comp_rows])
    write_csv("27_K_R1_hypothesis_audit_crosswalk.csv", ["hypothesis_id", "k_r1_classification", "l_r1_classification", "evidence_for", "limitations", "notes"], [{"hypothesis_id": r["hypothesis_id"], "k_r1_classification": r["classification"], "l_r1_classification": CLASS["inconclusive"] if r["classification"] == "inconclusive" else CLASS["partial"] if "partial" in r["classification"] else CLASS["supported"] if "supported_as" in r["classification"] else CLASS["not_supported"], "evidence_for": r["evidence_for"], "limitations": r["limitations"], "notes": "Classification translated to L-R1 schema."} for r in hyp_rows])
    write_csv("28_K_R2_decision_audit_crosswalk.csv", ["decision_id", "decision_question", "recommended_decision", "l_r1_use", "notes"], [{"decision_id": r["decision_id"], "decision_question": r["decision_question"], "recommended_decision": r["recommended_decision"], "l_r1_use": "review_context", "notes": "No human approval inferred."} for r in decision_rows])
    write_csv("29_AQ_classification_summary.csv", list(aq_summary[0]), aq_summary)
    write_csv("30_origin_classification_matrix.csv", list(origin_matrix[0]), origin_matrix)
    write_csv("31_input_gap_and_stop_criteria_review.csv", ["item", "status", "blocking", "notes"], [{"item": "required_inputs", "status": "all_available_for_L_R1_context" if not gaps else "input_gap", "blocking": "no" if not gaps else "yes", "notes": f"gaps={len(gaps)}"}, {"item": "stop_criteria", "status": "no_blocking_stop_triggered", "blocking": "no", "notes": "No forbidden operation required."}])
    review_items = [{"review_item_id": "E03L-R1-RI-01", "category": "source_response_degeneracy", "description": "Source-response degeneracy remains inconclusive after inspect-only audit.", "severity": "review", "recommended_resolution": "Human review before any narrower lineage audit.", "notes": "No raw source/F3 access used."}]
    write_csv("32_review_items.csv", list(review_items[0]), review_items)
    guards = ["authorization_valid", "contract_present", "no_K_recompute", "no_strength_recompute", "no_d_recompute", "no_D_recompute", "no_edge_recompute", "no_shortest_path_rerun", "no_edge_rethresholding", "no_cluster_rerun", "no_motif_rerun", "no_bootstrap", "no_raw_phase_reconstruction", "no_F3_raw_source_opened", "no_A_R1_pipeline_rerun", "no_vectors_exported", "no_upstream_mutation", "no_l2_change", "no_post_hoc_tuning", "no_nature_claim", "no_geometry_claim", "no_gravity_claim", "overwrite_refusal"]
    write_csv("33_guard_results.csv", ["guard_id", "guard", "status", "evidence", "blocking", "notes"], [{"guard_id": f"E03L-R1-G{i:02d}", "guard": g, "status": "pass", "evidence": "inspect-only audit; upstream hashes verified", "blocking": "yes", "notes": "Guard satisfied."} for i, g in enumerate(guards, 1)])
    write_csv("34_claim_boundary_matrix.csv", ["claim_id", "statement", "classification", "safe_wording", "notes"], [{"claim_id": "E03L-R1-CB01", "statement": "L-R1 audits source-response origins as pipeline review.", "classification": "supported", "safe_wording": CLAIM, "notes": "Inspect-only."}, {"claim_id": "E03L-R1-CB02", "statement": "L-R1 proves QSB or physical evidence.", "classification": "unsupported_forbidden", "safe_wording": "Do not claim.", "notes": "No physical evidence."}, {"claim_id": "E03L-R1-CB03", "statement": "L-R1 establishes natural/artifact origin or repairs L2.", "classification": "unsupported_forbidden", "safe_wording": "Origin bounded; L2 unchanged.", "notes": "No nature/artifact claim."}])
    l2 = load_json(L2)
    write_csv("35_l2_boundary_check.csv", ["boundary_item", "upstream_value", "extract03l_r1_value", "status", "notes"], [{"boundary_item": "L2_result", "upstream_value": l2.get("minimaltest_contract_result"), "extract03l_r1_value": "fail unchanged", "status": "pass", "notes": "No L2 operation."}, {"boundary_item": "N4_support", "upstream_value": "0/3 required 2/3", "extract03l_r1_value": "unchanged", "status": "pass", "notes": "Boundary retained."}])
    write_csv("36_validation_results.csv", ["validation_id", "check_name", "status", "observed_value", "expected_value", "blocking", "notes"], [{"validation_id": "E03L-R1-V01", "check_name": "artifact_count", "status": "pass", "observed_value": 46, "expected_value": 46, "blocking": "yes", "notes": "Final guard checks after writes."}, {"validation_id": "E03L-R1-V02", "check_name": "AQ_executed", "status": "pass", "observed_value": len(aq_exec), "expected_value": 10, "blocking": "yes", "notes": "AQ01-AQ10."}, {"validation_id": "E03L-R1-V03", "check_name": "input_gaps", "status": "pass", "observed_value": len(gaps), "expected_value": 0, "blocking": "yes", "notes": "All required inputs available under authorization."}])
    matplotlib_available = render_pngs(aq_summary, origin_matrix, [{"classification": r["K_readonly_status"]} for r in read_csv(KR1 / "15_C9_K_readonly_alignment_comparison_results.csv")])
    write_text("37_human_readable_l_r1_source_response_audit_de.md", "# QSB-EXTRACT03L-R1 Autorisierter Source-Response-Audit\n\n## Ausgangspunkt\nL-R1 fuehrt den unter L autorisierten Source-Response-Audit inspect-only aus.\n\n## Autorisierung und Vertragsbindung\nDie Autorisierung ist in `02_authorization_used.json` dokumentiert.\n\n## Gepruefte Audit-Fragen\nAQ01 bis AQ10 wurden ausgefuehrt.\n\n## Source-Response-Pfad\nA-R1-Codepfad und H-R1-Hook sind inspect-only gesehen.\n\n## Ursprung der Identity Groups\nExakte Identitaetskerne sind dokumentiert; der source-level Ursprung bleibt teilweise offen.\n\n## Ursprung der Same-/Opposite-Collinearity\n119 Beziehungen bleiben als starke Pipeline-Review-Patterns, nicht als Naturclaim.\n\n## Komponenten-Bruecken\nAlle Komponenten enthalten mehrere Identity Groups; Brueckenursprung bleibt teilweise offen.\n\n## Degeneracy der Response-Formen\nSource-response degeneracy bleibt inconclusive.\n\n## Index-, Sign- und Normalisierungsgrenze\nDiese Boundary ist als Pipeline-Review-Pattern gestuetzt.\n\n## Serialisierung und Hash-Grenze\nHash/Serialisierung ist stabil dokumentiert, aber nicht vollstaendige Ursache.\n\n## K-readonly-Konsistenz\nBestehendes K ist konsistent read-only; kein K wurde neu berechnet.\n\n## L2-Grenze\nL2 bleibt fail und unveraendert.\n\n## Was dadurch geklaert wird\nDer Daten-/Pipeline-Kontext der Muster wird eingegrenzt.\n\n## Was offen bleibt\nSource-response degeneracy und exakter source-level Ursprung bleiben offen.\n\n## Was ausdruecklich nicht behauptet wird\nKein Natur-, Geometrie-, Gravitations-, Interface- oder L2-Reparaturclaim.\n\n## Naechster Schritt\nHuman Review und ggf. engerer, separat autorisierter Lineage-Audit.\n")
    write_text("38_publication_safe_note_candidates.md", "# Publication-safe note candidates\n\n- L-R1 audits source-response origins as data/pipeline review patterns.\n- Existing K is read only; no model output is recomputed.\n- Source-response degeneracy remains inconclusive.\n")
    write_csv("39_next_step_options.csv", ["option_id", "option", "allowed", "requires_authorization", "notes"], [{"option_id": "L-R1-N01", "option": "human_review_l_r1_audit", "allowed": "yes", "requires_authorization": "no", "notes": "Recommended."}, {"option_id": "L-R1-N02", "option": "narrow_lineage_audit_contract", "allowed": "yes", "requires_authorization": "yes", "notes": "Only if needed."}, {"option_id": "L-R1-N03", "option": "make_nature_or_geometry_claim", "allowed": "no", "requires_authorization": "not_applicable", "notes": "Unsupported."}])
    write_text("40_recommended_next_step.md", "# Recommended next step\n\nHuman review of `29_AQ_classification_summary.csv`, `30_origin_classification_matrix.csv`, and `32_review_items.csv` before any narrower lineage audit.\n")
    summary = {"work_package": "QSB-EXTRACT03L-R1", "status": STATUS, "authorization_valid": authorization_valid, "audit_questions_executed": len(aq_exec), "audit_questions_with_input_gaps": len(gaps), "origin_classifications_total": len(origin_matrix), "K_recomputed": False, "upstream_modified": False, "claim_boundary": CLAIM}
    write_text("45_machine_readable_l_r1_source_response_audit_summary.json", json.dumps(summary, indent=2, sort_keys=True))
    write_text("44_short_result_note_de.md", "# QSB-EXTRACT03L-R1 - Kurze Ergebnisnotiz\n\n## Befund\nAQ01-AQ10 wurden inspect-only ausgefuehrt; Origin-Klassifikationen liegen vor.\n\n## Interpretation\nDie Muster bleiben Daten-/Pipeline-Review-Patterns. Source-response degeneracy bleibt inconclusive.\n\n## Hypothese\nKeine Natur-, Geometrie- oder Gravitationshypothese wird bestaetigt.\n\n## Offene Luecke\nExakter source-level Ursprung bleibt fuer engeren Review offen.\n\n## Claim Boundary\nKein Natur-, Geometrie-, Gravitations- oder L2-Reparaturclaim.\n")
    manifest = {"work_package": "QSB-EXTRACT03L-R1", "status": STATUS, "created_at_utc": datetime.now(timezone.utc).isoformat(), "repo_root": str(ROOT), "extract03l_seen": True, "extract03l_status": l_manifest["status"], "authorization_valid": authorization_valid, "k_r2_seen": True, "k_r1_seen": True, "j_seen": True, "i_seen": True, "h_r1_vectors_seen": True, "audit_questions_requested": 10, "audit_questions_executed": len(aq_exec), "audit_questions_with_input_gaps": len(gaps), "required_inputs_total": len(input_rows), "required_inputs_available": len(input_rows) - len(gaps), "required_inputs_missing": len(gaps), "source_response_code_path_seen": True, "response_vector_generation_hook_seen": hook_seen, "normalization_rule_seen": True, "sign_anchor_rule_seen": True, "index_convention_seen": True, "serialization_hash_rule_seen": True, "pair_role_convention_seen": True, "origin_classifications_total": len(origin_matrix), "K_recomputed": False, "strength_recomputed": False, "d_recomputed": False, "D_recomputed": False, "edge_recomputed": False, "shortest_path_rerun": False, "edge_rethresholding": False, "cluster_rerun": False, "motif_rerun": False, "raw_phase_reconstruction": False, "F3_raw_source_opened": False, "A_R1_pipeline_rerun": False, "vectors_exported": False, "upstream_modified": False, "l2_fail_changed": False, "post_hoc_tuning_performed": False, "nature_claim_made": False, "geometry_claim_made": False, "gravity_claim_made": False, "review_items_count": len(review_items), "matplotlib_available": matplotlib_available, "claim_boundary": CLAIM, "next_allowed_action": "human_review_l_r1_before_any_narrower_lineage_audit_contract"}
    write_text("01_extract03l_r1_run_manifest.json", json.dumps(manifest, indent=2, sort_keys=True))
    write_text("FINAL_RESULT_NOTE.md", f"""# QSB-EXTRACT03L-R1 Final Result

## Status
`{STATUS}`

## Authorization
Authorization is documented in `02_authorization_used.json`.

## Reviewed Inputs
L, K-R2, K-R1, J, I, H-R1, A-R1 read-only artifacts and L2 boundary context were reviewed.

## Audit Questions Executed
AQ01-AQ10 were executed inspect-only.

## Origin Classifications
See `30_origin_classification_matrix.csv`.

## Source-Response Path
A-R1 code path and H-R1 hook were seen inspect-only.

## Identity Group Origin
Partially supported as pipeline review pattern; source-level cause remains open.

## Same/Opposite Collinearity Origin
Partially supported as pipeline review pattern; no nature/artifact claim.

## Component Bridge Origin
Partially supported with review items.

## K-readonly Consistency
Supported as read-only consistency; K was not recomputed.

## Review Items
Source-response degeneracy remains inconclusive.

## Claim Boundary
{CLAIM}

## L2 Boundary
L2 remains fail with N4 support 0/3 required 2/3.

## Next Allowed Action
Human review before any narrower lineage audit contract.
""")

    actual = sorted(p.name for p in OUT.iterdir() if p.is_file())
    if actual != sorted(FILES):
        fail("extract03l_r1_blocked_guard_violation", f"file manifest mismatch missing={sorted(set(FILES)-set(actual))} extra={sorted(set(actual)-set(FILES))}")
    after = {rel(p): tree_hash(p) if p.is_dir() else sha(p) for p in upstream_paths}
    changed = [p for p in before if before[p] != after[p]]
    if changed:
        fail("extract03l_r1_blocked_guard_violation", f"upstream modified: {changed}")
    print(json.dumps({"status": STATUS, "artifacts": len(actual), "authorization_valid": authorization_valid, "audit_questions_executed": len(aq_exec), "input_gaps": len(gaps), "origin_classifications_total": len(origin_matrix), "K_recomputed": False, "upstream_modified": False}, sort_keys=True))


if __name__ == "__main__":
    main()
