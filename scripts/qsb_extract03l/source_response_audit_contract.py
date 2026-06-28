#!/usr/bin/env python3
"""Create the EXTRACT03L Source-Response Audit contract."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs/QSB-EXTRACT03L/source_response_audit_contract"
KR2 = ROOT / "runs/QSB-EXTRACT03K-R2/human_review_collinearity_control_classifications"
KR1 = ROOT / "runs/QSB-EXTRACT03K-R1/authorized_collinearity_control_run"
K = ROOT / "runs/QSB-EXTRACT03K/collinearity_control_contract"
J = ROOT / "runs/QSB-EXTRACT03J/near_alignment_structure_review"
I = ROOT / "runs/QSB-EXTRACT03I/response_vector_identity_k_alignment_review"
H = ROOT / "runs/QSB-EXTRACT03H-R1/authorized_response_vector_export"
A = ROOT / "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum"
A_SCRIPT = ROOT / "scripts/qsb_extract03a_r1/run_authorized_execution_with_s1_addendum.py"
L2 = ROOT / "runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2/01_l2_run_manifest.json"

STATUS = "extract03l_source_response_audit_contract_completed_ready_for_separate_authorized_audit_run"
CLAIM = (
    "EXTRACT03L creates a Source-Response Audit contract for a later separately "
    "authorized audit. It executes no audit and makes no nature, geometry, "
    "gravity, Interface, or L2-repair claim."
)
FILES = [
    "01_extract03l_run_manifest.json", "02_upstream_inventory_and_hashes.csv",
    "03_input_availability_review.csv", "04_k_r2_decision_import_summary.csv",
    "05_source_response_audit_question_registry.csv", "06_required_future_inputs.csv",
    "07_required_future_outputs.csv", "08_allowed_operations_matrix.csv",
    "09_forbidden_operations_matrix.csv", "10_audit_stop_criteria.csv",
    "11_source_response_path_gap_review.csv", "12_normalization_sign_index_contract.csv",
    "13_serialization_hash_contract.csv", "14_pair_role_convention_review.csv",
    "15_K_readonly_boundary_contract.csv", "16_l2_boundary_contract.csv",
    "17_claim_boundary_matrix.csv", "18_future_audit_classification_schema.csv",
    "19_audit_execution_guard_contract.csv", "20_future_authorization_template_extract03l_r1.json",
    "21_human_decision_points.csv", "22_review_items.csv",
    "23_no_execution_guard_results.csv", "24_validation_results.csv",
    "25_human_readable_source_response_audit_contract_de.md",
    "26_publication_safe_note_candidates.md", "27_source_response_audit_run_outline.md",
    "28_disallowed_shortcuts.csv", "29_next_step_options.csv",
    "30_recommended_next_step.md", "31_contract_summary_for_registry.json",
    "32_short_result_note_de.md", "33_machine_readable_source_response_contract_summary.json",
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


def main() -> None:
    if OUT.exists():
        fail("extract03l_blocked_guard_violation", f"refusing to overwrite {rel(OUT)}")
    required = [
        KR2 / "01_extract03k_r2_run_manifest.json",
        KR2 / "13_decision_points_for_human_review.csv",
        KR1 / "01_extract03k_r1_run_manifest.json",
        J / "01_extract03j_run_manifest.json",
        I / "01_extract03i_run_manifest.json",
        H / "09_response_vector_export.csv",
    ]
    missing = [rel(p) for p in required if not p.exists()]
    if missing:
        fail("extract03l_blocked_missing_k_r2_outputs", ";".join(missing))
    kr2_manifest = load_json(KR2 / "01_extract03k_r2_run_manifest.json")
    if kr2_manifest.get("status") != "extract03k_r2_human_review_completed_decision_matrix_ready":
        fail("extract03l_blocked_missing_k_r2_outputs", "unexpected K-R2 status")

    OUT.mkdir(parents=True)
    upstream_paths = [KR2, KR1, K, J, I, H, A, L2, A_SCRIPT]
    upstream_paths = [p for p in upstream_paths if p.exists()]
    before = {rel(p): tree_hash(p) if p.is_dir() else sha(p) for p in upstream_paths}
    kr1_manifest = load_json(KR1 / "01_extract03k_r1_run_manifest.json")
    j_manifest = load_json(J / "01_extract03j_run_manifest.json")
    i_manifest = load_json(I / "01_extract03i_run_manifest.json")
    h_manifest = load_json(H / "01_extract03h_r1_run_manifest.json")
    decisions = read_csv(KR2 / "13_decision_points_for_human_review.csv")

    inv = [{"artifact_id": f"E03L-U{i:02d}", "upstream_block": p.name, "path": rel(p), "exists": p.exists(), "sha256": before[rel(p)], "role": "read-only contract input", "used_for": "source-response audit contract", "notes": "No audit execution or upstream mutation."} for i, p in enumerate(upstream_paths, 1)]
    write_csv("02_upstream_inventory_and_hashes.csv", list(inv[0]), inv)
    write_csv("03_input_availability_review.csv", ["input_id", "path", "available", "read_status", "purpose", "notes"], [{"input_id": f"E03L-I{i:02d}", "path": rel(p), "available": p.exists(), "read_status": "read_only", "purpose": "EXTRACT03L contract input", "notes": "No upstream execution."} for i, p in enumerate(upstream_paths, 1)])
    write_csv("04_k_r2_decision_import_summary.csv", ["summary_item", "value", "status", "notes"], [
        {"summary_item": "k_r2_status", "value": kr2_manifest["status"], "status": "imported", "notes": "Primary upstream."},
        {"summary_item": "decision_points", "value": len(decisions), "status": "imported", "notes": "Human decisions prepared, not approved."},
        {"summary_item": "future_audit_authorized", "value": kr2_manifest["future_audit_authorized"], "status": "not_authorized", "notes": "L creates contract/template only."},
        {"summary_item": "source_response_degeneracy", "value": "inconclusive", "status": "contract_basis", "notes": "Reason to define Source-Response Audit."},
    ])

    questions = [
        ("AQ01_response_vector_generation_path", "Which code/data paths generate the H-R1 response vectors?", "Trace generation path."),
        ("AQ02_identity_group_origin", "Do 16 Identity Groups arise from identical inputs, canonicalization, pair roles, or normalization?", "Review exact identity origins."),
        ("AQ03_same_opposite_collinearity_origin", "Do 119 collinearity items arise from sign/scale/source/index/serialization rules?", "Review near-collinearity origins."),
        ("AQ04_component_bridge_origin", "Why do multiple Identity Groups bridge into 6 components?", "Review component bridging."),
        ("AQ05_source_response_degeneracy", "Can distinct source configurations yield same/opposite response forms?", "Review degeneracy."),
        ("AQ06_index_sign_normalization_boundary", "Which portions are explained by index, sign, and normalization rules?", "Boundary review."),
        ("AQ07_serialization_hash_boundary", "Which portions are robust to serialization/hash choices?", "Serialization boundary."),
        ("AQ08_K_readonly_consistency", "How does existing K fit response-audit findings without K recompute?", "Read-only consistency."),
        ("AQ09_l2_boundary", "How is L2 fail kept untouched?", "L2 boundary."),
        ("AQ10_claim_boundary", "Which future wordings are allowed or forbidden?", "Claim boundary."),
    ]
    q_rows = [{"audit_question_id": qid, "audit_question": q, "purpose": purpose, "required_inputs": "see 06_required_future_inputs.csv", "allowed_operations": "read-only lineage inspection and descriptive audit metrics", "forbidden_operations": "model recomputation, raw phase reconstruction, F3 raw opening, physical claims", "expected_output_type": "contracted audit classification row", "classification_boundary": "pipeline review only", "notes": "Question is for future L-R1; not answered in L."} for qid, q, purpose in questions]
    write_csv("05_source_response_audit_question_registry.csv", list(q_rows[0]), q_rows)

    input_specs = [
        ("K_R2_decision_matrix", KR2 / "13_decision_points_for_human_review.csv", True),
        ("K_R1_classification_matrix", KR1 / "18_hypothesis_classification_matrix.csv", True),
        ("J_near_alignment_items", J / "04_near_alignment_item_import.csv", True),
        ("I_identity_component_mapping", I / "05_component_identity_distribution.csv", True),
        ("H_R1_full_response_vectors", H / "09_response_vector_export.csv", True),
        ("H_R1_vector_hashes", H / "10_response_vector_hashes.csv", True),
        ("H_R1_sign_normalized_groups", H / "28_component_signature_group_summary.csv", True),
        ("A_R1_K_matrix_readonly", A / "11_K_candidate_matrix.csv", True),
        ("A_R1_edge_result_readonly", A / "16_edge_candidate_result.csv", True),
        ("source_response_code_path", A_SCRIPT, True),
        ("source_response_config_manifest", A / "01_extract03a_r1_run_manifest.json", True),
        ("response_vector_generation_hook", H / "06_source_hook_resolution.csv", True),
        ("normalization_rule", H / "17_vector_index_convention.csv", True),
        ("sign_anchor_rule", H / "16_orientation_anchor_review.csv", True),
        ("index_convention", H / "17_vector_index_convention.csv", True),
        ("serialization_hash_rule", H / "18_precision_rounding_hash_rule.csv", True),
        ("pair_id_role_convention", A / "08_canonical_pair_split_assignment.csv", True),
        ("audit_authorization", OUT / "20_future_authorization_template_extract03l_r1.json", False),
    ]
    input_rows = []
    for idx, (name, path, expected_now) in enumerate(input_specs, 1):
        exists = path.exists()
        status = "available" if exists and expected_now else "template_only_not_authorized" if name == "audit_authorization" else "missing"
        input_rows.append({"input_id": f"L-IN-{idx:02d}", "input_name": name, "required_for_audit": "yes", "current_status": status, "evidence_or_source": rel(path) if path.is_absolute() and path.exists() else str(path), "blocking_if_missing": "yes", "notes": "Future L-R1 must verify this before execution."})
    write_csv("06_required_future_inputs.csv", list(input_rows[0]), input_rows)
    write_csv("07_required_future_outputs.csv", ["output_id", "output_name", "required", "format", "notes"], [
        {"output_id": "L-R1-OUT01", "output_name": "source_response_audit_manifest", "required": "yes", "format": "json", "notes": "Must record guard flags."},
        {"output_id": "L-R1-OUT02", "output_name": "audit_question_results", "required": "yes", "format": "csv", "notes": "AQ01-AQ10 classifications."},
        {"output_id": "L-R1-OUT03", "output_name": "lineage_boundary_review", "required": "yes", "format": "csv", "notes": "No model recompute."},
        {"output_id": "L-R1-OUT04", "output_name": "claim_l2_guard_results", "required": "yes", "format": "csv", "notes": "Must pass."},
    ])
    allowed_ops = ["read_K_R2_decision_matrix", "read_K_R1_classifications", "read_J_near_alignment_items", "read_I_identity_component_mapping", "read_H_R1_vectors", "read_A_R1_K_matrix_readonly", "inspect_source_response_code_path", "inspect_generation_hook", "inspect_normalization_rule", "inspect_sign_anchor_rule", "inspect_index_convention", "inspect_serialization_hash_rule", "inspect_pair_role_convention", "compute_descriptive_audit_metrics", "write_audit_report"]
    write_csv("08_allowed_operations_matrix.csv", ["operation", "allowed_in_L_contract", "allowed_in_future_L_R1", "requires_separate_authorization", "notes"], [{"operation": op, "allowed_in_L_contract": "read_or_define_only" if op.startswith("read_") or op.startswith("inspect_") else "no", "allowed_in_future_L_R1": "yes", "requires_separate_authorization": "yes", "notes": "Future L-R1 only; L contract does not execute audit."} for op in allowed_ops])
    forbidden_ops = ["run_source_response_audit_now", "recompute_K", "recompute_strength", "recompute_d", "recompute_D", "recompute_edges", "rerun_shortest_paths", "edge_rethresholding", "rerun_clusters", "rerun_motifs", "run_bootstrap", "open_F3_raw_source", "reconstruct_raw_phases", "rerun_A_R1_pipeline", "change_parameters", "change_thresholds", "change_splits_or_seeds", "mutate_upstream_files", "repair_L2", "make_nature_claim", "make_geometry_claim", "make_gravity_claim"]
    write_csv("09_forbidden_operations_matrix.csv", ["operation", "forbidden_in_L_contract", "forbidden_in_future_L_R1", "reason", "notes"], [{"operation": op, "forbidden_in_L_contract": "yes", "forbidden_in_future_L_R1": "yes", "reason": "Preserve contract, lineage, claim, and L2 boundaries.", "notes": "No workaround allowed."} for op in forbidden_ops])
    stops = [
        "source_response_code_path fehlt", "response_vector_generation_hook unklar ist", "normalization_rule fehlt", "sign_anchor_rule fehlt", "index_convention fehlt", "serialization_hash_rule fehlt", "pair_id_role_convention fehlt oder nicht pruefbar ist", "H-R1-Vektoren fehlen", "K-R2-Decision-Matrix fehlt", "Audit-Autorisierung fehlt", "eine verbotene Operation noetig waere"
    ]
    write_csv("10_audit_stop_criteria.csv", ["stop_id", "stop_condition", "blocking", "required_resolution", "notes"], [{"stop_id": f"L-STOP-{i:02d}", "stop_condition": s, "blocking": "yes", "required_resolution": "resolve before L-R1 execution", "notes": "Future audit must fail closed."} for i, s in enumerate(stops, 1)])
    write_csv("11_source_response_path_gap_review.csv", ["review_item", "current_status", "evidence", "gap_status", "notes"], [{"review_item": "source_response_code_path", "current_status": "available", "evidence": rel(A_SCRIPT), "gap_status": "no_current_gap_contract_level", "notes": "Future audit must inspect without rerun."}, {"review_item": "audit_authorization", "current_status": "template_only", "evidence": "20_future_authorization_template_extract03l_r1.json", "gap_status": "authorization_gap_for_execution", "notes": "Expected; L is contract-only."}])
    write_csv("12_normalization_sign_index_contract.csv", ["contract_item", "source_artifact", "future_audit_rule", "notes"], [{"contract_item": "normalization_rule", "source_artifact": rel(H / "17_vector_index_convention.csv"), "future_audit_rule": "read and compare only", "notes": "No vector re-export."}, {"contract_item": "sign_anchor_rule", "source_artifact": rel(H / "16_orientation_anchor_review.csv"), "future_audit_rule": "read and compare only", "notes": "No relabeling."}, {"contract_item": "index_convention", "source_artifact": rel(H / "17_vector_index_convention.csv"), "future_audit_rule": "read and compare only", "notes": "No shift tuning."}])
    write_csv("13_serialization_hash_contract.csv", ["contract_item", "source_artifact", "future_audit_rule", "notes"], [{"contract_item": "serialization_hash_rule", "source_artifact": rel(H / "18_precision_rounding_hash_rule.csv"), "future_audit_rule": "read-only hash/serialization review", "notes": "No hash rule change."}, {"contract_item": "vector_hashes", "source_artifact": rel(H / "10_response_vector_hashes.csv"), "future_audit_rule": "read-only compare", "notes": "No mutation."}])
    write_csv("14_pair_role_convention_review.csv", ["review_item", "source_artifact", "current_status", "future_audit_rule", "notes"], [{"review_item": "pair_id_role_convention", "source_artifact": rel(A / "08_canonical_pair_split_assignment.csv"), "current_status": "parseable_ordered_pair_ids", "future_audit_rule": "review pair roles without relabeling", "notes": "No role mechanism claim."}])
    write_csv("15_K_readonly_boundary_contract.csv", ["boundary_item", "source_artifact", "allowed_future_use", "forbidden_future_use", "notes"], [{"boundary_item": "A_R1_K_matrix", "source_artifact": rel(A / "11_K_candidate_matrix.csv"), "allowed_future_use": "read-only consistency comparison", "forbidden_future_use": "recompute/replace/correct K", "notes": "K remains upstream artifact."}])
    write_csv("16_l2_boundary_contract.csv", ["boundary_item", "value", "future_audit_rule", "notes"], [{"boundary_item": "L2_result", "value": "fail", "future_audit_rule": "preserve unchanged", "notes": "No repair."}, {"boundary_item": "N4_support", "value": "0/3 required 2/3", "future_audit_rule": "preserve unchanged", "notes": "No reinterpretation."}])
    write_csv("17_claim_boundary_matrix.csv", ["claim_id", "statement", "classification", "safe_wording", "notes"], [{"claim_id": "E03L-CB01", "statement": "L creates a Source-Response Audit contract.", "classification": "supported", "safe_wording": CLAIM, "notes": "Contract-only."}, {"claim_id": "E03L-CB02", "statement": "L proves QSB or physical mechanism.", "classification": "unsupported_forbidden", "safe_wording": "Do not claim.", "notes": "No audit executed."}, {"claim_id": "E03L-CB03", "statement": "L authorizes a future audit or repairs L2.", "classification": "unsupported_forbidden", "safe_wording": "Template only; L2 unchanged.", "notes": "No human approval claimed."}])
    schema = ["source_response_origin_supported_as_pipeline_review_pattern", "source_response_origin_partially_supported_with_review_items", "source_response_origin_not_supported_by_audit", "source_response_origin_inconclusive", "source_response_origin_input_gap", "source_response_origin_blocked_by_guard"]
    write_csv("18_future_audit_classification_schema.csv", ["classification", "meaning", "claim_boundary", "notes"], [{"classification": s, "meaning": "Future L-R1 bounded audit classification only.", "claim_boundary": "No nature, geometry, gravity, or physical mechanism claim.", "notes": "Not a physics category."} for s in schema])
    write_csv("19_audit_execution_guard_contract.csv", ["guard", "future_required_status", "blocking", "notes"], [{"guard": g, "future_required_status": "pass", "blocking": "yes", "notes": "Future audit must document this guard."} for g in ["authorization_valid", "no_K_recompute", "no_strength_d_D_edge_recompute", "no_shortest_path_rerun", "no_F3_raw_source_open", "no_l2_change", "no_nature_claim", "no_geometry_claim", "no_gravity_claim"]])
    auth_template = {"authorization_status": "TEMPLATE_REQUIRES_HUMAN_APPROVAL", "authorized_work_package": "QSB-EXTRACT03L-R1_SOURCE_RESPONSE_AUDIT_RUN", "source_contract": "QSB-EXTRACT03L", "human_approval_required": True, "allowed_scope": "source_response_audit_only_under_contract", "no_K_recompute": True, "no_strength_d_D_edge_recompute": True, "no_shortest_path_rerun": True, "no_edge_rethresholding": True, "no_cluster_or_motif_rerun": True, "no_bootstrap": True, "no_raw_phase_reconstruction": True, "no_F3_raw_source_open": True, "no_l2_change": True, "no_post_hoc_tuning": True, "no_nature_claim": True, "no_geometry_claim": True, "no_gravity_claim": True}
    write_text("20_future_authorization_template_extract03l_r1.json", json.dumps(auth_template, indent=2, sort_keys=True))
    write_csv("21_human_decision_points.csv", ["decision_id", "decision_question", "recommended_decision", "requires_authorization", "notes"], [{"decision_id": "L-D01", "decision_question": "Approve later L-R1 audit run?", "recommended_decision": "review_contract_first", "requires_authorization": "yes", "notes": "L does not approve."}, {"decision_id": "L-D02", "decision_question": "Accept no-physics claim boundary?", "recommended_decision": "accept_boundary", "requires_authorization": "no", "notes": "Required for future audit."}])
    review_items = [{"review_item_id": "E03L-RI-01", "category": "future_authorization_required", "description": "L-R1 audit is not authorized by L.", "severity": "blocking_future_execution", "recommended_resolution": "Human review and explicit future authorization.", "notes": "Expected contract state."}]
    write_csv("22_review_items.csv", list(review_items[0]), review_items)
    guards = ["no_audit_run_executed", "no_controls_reexecuted", "no_vectors_exported", "no_K_recompute", "no_strength_recompute", "no_d_recompute", "no_D_recompute", "no_edge_recompute", "no_shortest_path_rerun", "no_edge_rethresholding", "no_cluster_rerun", "no_motif_rerun", "no_bootstrap", "no_raw_phase_reconstruction", "no_F3_raw_source_opened", "no_A_R1_pipeline_rerun", "no_upstream_mutation", "no_l2_change", "no_post_hoc_tuning", "no_nature_claim", "no_geometry_claim", "no_gravity_claim", "future_authorization_template_only", "overwrite_refusal"]
    write_csv("23_no_execution_guard_results.csv", ["guard_id", "guard", "status", "evidence", "blocking", "notes"], [{"guard_id": f"E03L-G{i:02d}", "guard": g, "status": "pass", "evidence": "contract-only script; no audit execution path", "blocking": "yes", "notes": "Guard satisfied."} for i, g in enumerate(guards, 1)])
    write_csv("24_validation_results.csv", ["validation_id", "check_name", "status", "observed_value", "expected_value", "blocking", "notes"], [{"validation_id": "E03L-V01", "check_name": "artifact_count", "status": "pass", "observed_value": 34, "expected_value": 34, "blocking": "yes", "notes": "Final guard checks after writes."}, {"validation_id": "E03L-V02", "check_name": "audit_questions", "status": "pass", "observed_value": len(q_rows), "expected_value": 10, "blocking": "yes", "notes": "AQ01-AQ10."}, {"validation_id": "E03L-V03", "check_name": "future_authorization_template", "status": "pass", "observed_value": True, "expected_value": True, "blocking": "yes", "notes": "Template only."}])
    write_text("25_human_readable_source_response_audit_contract_de.md", f"""# QSB-EXTRACT03L Source-Response-Audit-Vertrag

## Ausgangspunkt
K-R2 macht die Source-Response-Frage zum naechsten methodischen Pfad.

## Warum der Source-Response-Audit der naechste Pfad ist
K-R1/K-R2 lassen Source-Response-Degeneracy inconclusive; ein Auditvertrag ist deshalb methodisch sinnvoll.

## Was K-R2 entschieden vorbereitet
K-R2 stellt Entscheidungsmatrizen bereit, autorisiert aber keinen Audit.

## Audit-Fragen
AQ01 bis AQ10 definieren Generation Path, Identity-Origin, Same/Opposite-Collinearity-Origin, Component-Bridge-Origin, Degeneracy, Index/Sign/Normalisierung, Serialisierung/Hash, K-readonly, L2 und Claim Boundary.

## Benoetigte Inputs
Siehe `06_required_future_inputs.csv`; Audit-Autorisierung ist nur Template und fehlt bis zur spaeteren Freigabe.

## Erlaubte Operationen
Read-only Lineage-Inspektion und deskriptive Audit-Metriken in einem spaeter autorisierten L-R1.

## Verbotene Operationen
Keine K-/d-/D-/Edge-Neuberechnung, kein F3-Rohdatenzugriff, kein A-R1-Rerun, kein Bootstrap, keine Natur-/Geometrie-/Gravitationsclaims.

## Stop-Kriterien
Siehe `10_audit_stop_criteria.csv`.

## L2-Grenze
L2 bleibt fail; keine Reparatur oder Umdeutung.

## Claim Boundary
{CLAIM}

## Was L ausdruecklich nicht ausfuehrt
Kein Audit-Run, keine Controls, kein Vektorexport.

## Was ein spaeterer L-R1 pruefen darf
Nur den Source-Response-Audit unter separater Autorisierung und mit Guards.

## Naechster Schritt
Human Review dieses Vertrags und ggf. separate L-R1-Autorisierung.
""")
    write_text("26_publication_safe_note_candidates.md", "# Publication-safe note candidates\n\n- EXTRACT03L defines a future Source-Response Audit contract.\n- EXTRACT03L executes no audit and creates no new model evidence.\n- Future audit classifications remain data/pipeline review categories only.\n")
    write_text("27_source_response_audit_run_outline.md", "# Source-Response Audit Run Outline\n\n1. Validate L-R1 authorization.\n2. Verify required future inputs.\n3. Apply stop criteria.\n4. Inspect source-response path read-only.\n5. Produce AQ01-AQ10 classifications.\n6. Report guards, L2 boundary, and claim boundary.\n")
    write_csv("28_disallowed_shortcuts.csv", ["shortcut_id", "shortcut", "allowed", "notes"], [{"shortcut_id": "DS01", "shortcut": "use L contract as audit authorization", "allowed": "no", "notes": "Template only."}, {"shortcut_id": "DS02", "shortcut": "open F3 raw source to resolve ambiguity", "allowed": "no", "notes": "Forbidden."}, {"shortcut_id": "DS03", "shortcut": "infer physical mechanism from pipeline pattern", "allowed": "no", "notes": "Unsupported."}])
    write_csv("29_next_step_options.csv", ["option_id", "option", "allowed", "requires_authorization", "notes"], [{"option_id": "L-N01", "option": "human_review_L_contract", "allowed": "yes", "requires_authorization": "no", "notes": "Recommended."}, {"option_id": "L-N02", "option": "authorize_L_R1_audit_run", "allowed": "yes", "requires_authorization": "yes", "notes": "Separate approval required."}, {"option_id": "L-N03", "option": "run_audit_now", "allowed": "no", "requires_authorization": "yes", "notes": "Not authorized by L."}])
    write_text("30_recommended_next_step.md", "# Recommended next step\n\nHuman review of `05_source_response_audit_question_registry.csv`, `06_required_future_inputs.csv`, `10_audit_stop_criteria.csv`, and `20_future_authorization_template_extract03l_r1.json`; then decide whether to separately authorize L-R1.\n")
    summary = {"work_package": "QSB-EXTRACT03L", "status": STATUS, "audit_questions": len(q_rows), "required_future_inputs": len(input_rows), "future_authorization_template_created": True, "audit_run_executed": False, "claim_boundary": CLAIM}
    write_text("31_contract_summary_for_registry.json", json.dumps(summary, indent=2, sort_keys=True))
    write_text("32_short_result_note_de.md", "# QSB-EXTRACT03L - Kurze Ergebnisnotiz\n\n## Befund\nDer Source-Response-Audit-Vertrag wurde erstellt.\n\n## Interpretation\nL ist Contract-only und fuehrt keinen Audit aus.\n\n## Hypothese\nKeine Source-Response-Hypothese wird entschieden.\n\n## Offene Luecke\nDer Audit-Run erfordert separate Autorisierung.\n\n## Claim Boundary\nKein Natur-, Geometrie-, Gravitations- oder L2-Reparaturclaim.\n")
    write_text("33_machine_readable_source_response_contract_summary.json", json.dumps(summary, indent=2, sort_keys=True))
    manifest = {"work_package": "QSB-EXTRACT03L", "status": STATUS, "created_at_utc": datetime.now(timezone.utc).isoformat(), "repo_root": str(ROOT), "extract03k_r2_seen": True, "extract03k_r2_status": kr2_manifest["status"], "extract03k_r1_seen": True, "extract03j_seen": True, "extract03i_seen": True, "h_r1_vectors_seen": True, "k_r2_decision_matrix_seen": True, "future_authorization_template_created": True, "audit_run_executed": False, "controls_reexecuted": False, "vectors_exported": False, "K_recomputed": False, "strength_recomputed": False, "d_recomputed": False, "D_recomputed": False, "edge_recomputed": False, "shortest_path_rerun": False, "raw_phase_reconstruction": False, "F3_raw_source_opened": False, "bootstrap_run": False, "upstream_modified": False, "l2_fail_changed": False, "post_hoc_tuning_performed": False, "nature_claim_made": False, "geometry_claim_made": False, "gravity_claim_made": False, "review_items_count": len(review_items), "claim_boundary": CLAIM, "next_allowed_action": "human_review_then_separate_authorization_for_EXTRACT03L_R1_if_desired"}
    write_text("01_extract03l_run_manifest.json", json.dumps(manifest, indent=2, sort_keys=True))
    write_text("FINAL_RESULT_NOTE.md", f"""# QSB-EXTRACT03L Final Result

## Status
`{STATUS}`

## Reviewed Inputs
K-R2, K-R1, K, J, I, H-R1, A-R1 read-only context, and L2 boundary were reviewed.

## Audit Questions
AQ01-AQ10 are defined in `05_source_response_audit_question_registry.csv`.

## Required Future Inputs
Listed in `06_required_future_inputs.csv`; audit authorization remains template-only.

## Allowed and Forbidden Operations
Defined in `08_allowed_operations_matrix.csv` and `09_forbidden_operations_matrix.csv`.

## Stop Criteria
Defined in `10_audit_stop_criteria.csv`.

## Future Authorization Template
Created as `20_future_authorization_template_extract03l_r1.json`; not approved.

## No-Execution Guards
All no-execution guards passed.

## Claim Boundary
{CLAIM}

## L2 Boundary
L2 remains fail with N4 support 0/3 required 2/3.

## Next Allowed Action
Human review, then separate authorization for L-R1 if desired.
""")

    actual = sorted(p.name for p in OUT.iterdir() if p.is_file())
    if actual != sorted(FILES):
        fail("extract03l_blocked_guard_violation", f"file manifest mismatch missing={sorted(set(FILES)-set(actual))} extra={sorted(set(actual)-set(FILES))}")
    after = {rel(p): tree_hash(p) if p.is_dir() else sha(p) for p in upstream_paths}
    changed = [p for p in before if before[p] != after[p]]
    if changed:
        fail("extract03l_blocked_guard_violation", f"upstream modified: {changed}")
    print(json.dumps({"status": STATUS, "artifacts": len(actual), "k_r2_imported": True, "k_r1_imported": True, "audit_questions": len(q_rows), "required_future_inputs": len(input_rows), "future_authorization_template_created": True, "audit_run_executed": False, "controls_reexecuted": False, "upstream_modified": False}, sort_keys=True))


if __name__ == "__main__":
    main()
