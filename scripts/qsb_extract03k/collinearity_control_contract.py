#!/usr/bin/env python3
"""Create the EXTRACT03K prospective collinearity control contract."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs/QSB-EXTRACT03K/collinearity_control_contract"
J = ROOT / "runs/QSB-EXTRACT03J/near_alignment_structure_review"
I = ROOT / "runs/QSB-EXTRACT03I/response_vector_identity_k_alignment_review"
H = ROOT / "runs/QSB-EXTRACT03H-R1/authorized_response_vector_export"
AUTH01 = ROOT / "runs/QSB-EXTRACT03H-AUTH01/response_vector_export_authorization"
G = ROOT / "runs/QSB-EXTRACT03G/response_vector_export_contract"
F = ROOT / "runs/QSB-EXTRACT03F/response_vector_signature_export"
E = ROOT / "runs/QSB-EXTRACT03E/perfection_origin_review"
D = ROOT / "runs/QSB-EXTRACT03D/block_mechanism_review"
L2 = ROOT / "runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2/01_l2_run_manifest.json"

STATUS_OK = "extract03k_collinearity_control_contract_completed_ready_for_separate_authorized_control_run"
CLAIM = (
    "EXTRACT03K defines a prospective control contract for testing data/pipeline "
    "origins of near-perfect collinearity patterns observed in EXTRACT03J. "
    "EXTRACT03K does not run the controls and does not create new model evidence."
)
CONTROL_SEED = 20260623
DRAW_ALGORITHM = "extract03_sha256_counter_draw_v1"
SORT_RULE = "canonical_pair_id_lexicographic_order"
TIE_BREAK_RULE = "sha256(pair_id || control_id || control_seed)"
FILES = [
    "01_extract03k_run_manifest.json",
    "02_upstream_inventory_and_hashes.csv",
    "03_input_availability_review.csv",
    "04_j_result_import_summary.csv",
    "05_collinearity_hypothesis_registry.csv",
    "06_control_family_contract.csv",
    "07_index_order_integrity_control_contract.csv",
    "08_shift_screening_control_contract.csv",
    "09_sign_orientation_control_contract.csv",
    "10_scale_normalization_control_contract.csv",
    "11_offset_centering_control_contract.csv",
    "12_serialization_precision_hash_control_contract.csv",
    "13_identity_group_label_permutation_contract.csv",
    "14_component_membership_permutation_contract.csv",
    "15_K_readonly_alignment_comparison_contract.csv",
    "16_pair_symmetry_role_review_contract.csv",
    "17_allowed_forbidden_operations_matrix.csv",
    "18_required_future_inputs.csv",
    "19_required_future_outputs.csv",
    "20_future_authorization_template.json",
    "21_no_execution_guard_results.csv",
    "22_claim_boundary_matrix.csv",
    "23_l2_boundary_check.csv",
    "24_validation_results.csv",
    "25_review_items.csv",
    "26_human_readable_control_contract_de.md",
    "27_publication_safe_note_candidates.md",
    "28_next_step_options.csv",
    "29_recommended_next_step.md",
    "30_contract_machine_readable_summary.json",
    "31_short_result_note_de.md",
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


def control_rows() -> list[dict]:
    families = [
        ("C1_index_order_integrity_control", "Check canonical pair/vector index ordering and lineage consistency."),
        ("C2_fixed_small_shift_screening_contract", "Specify fixed small shifts [-2,-1,0,1,2] for later review-only screening."),
        ("C3_global_sign_orientation_anchor_control", "Review global sign and orientation anchor policy without changing H-R1 vectors."),
        ("C4_scale_normalization_ablation_contract", "Specify how later controls may compare normalized and permitted ablation summaries."),
        ("C5_offset_centering_review_contract", "Specify baseline/offset and centering checks as review metrics only."),
        ("C6_serialization_precision_hash_control", "Review float64, rounding, hash, and serialization stability."),
        ("C7_identity_group_label_permutation_control", "Specify label permutation controls for identity-group assignments."),
        ("C8_component_membership_permutation_control", "Specify component membership permutation controls without rerunning clustering."),
        ("C9_K_readonly_alignment_comparison_control", "Compare later control summaries against existing K only read-only."),
        ("C10_pair_symmetry_role_review_contract", "Review ordered-pair and possible role symmetry patterns descriptively."),
    ]
    rows = []
    for cid, purpose in families:
        rows.append({
            "control_id": cid,
            "control_family": cid,
            "purpose": purpose,
            "allowed_inputs": "EXTRACT03J tables; EXTRACT03I tables; H-R1 exported vectors/hashes; existing A-R1 K read-only where specified",
            "forbidden_inputs": "F3 raw source; reconstructed raw phases; mutable upstream DBs; new model outputs",
            "allowed_operations": "read inputs; compute contract-specified review metrics in future K-R1 only; write local K-R1 outputs if authorized",
            "forbidden_operations": "recompute K/Strength/d/D/Edge; shortest paths; edge thresholding; clustering; motifs; bootstrap; physical interpretation",
            "required_outputs": "control result CSV; guard results; claim boundary; no-upstream-mutation audit",
            "determinism_rule": f"control_seed={CONTROL_SEED}; draw_algorithm={DRAW_ALGORITHM}; sort_rule={SORT_RULE}; tie_break_rule={TIE_BREAK_RULE}",
            "run_now": "no",
            "blocks_if_missing": "yes",
            "interpretation_boundary": "Future results may support data/pipeline artifact, review pattern, or robust descriptive pattern only.",
            "notes": "EXTRACT03K defines contract only and executes no control.",
        })
    return rows


def main() -> None:
    if OUT.exists():
        fail("extract03k_blocked_guard_violation", f"refusing to overwrite {rel(OUT)}")
    required = [
        J / "01_extract03j_run_manifest.json",
        J / "04_near_alignment_item_import.csv",
        J / "05_identity_group_pair_near_alignment_summary.csv",
        H / "09_response_vector_export.csv",
    ]
    missing = [rel(path) for path in required if not path.exists()]
    if missing:
        fail("extract03k_blocked_missing_extract03j_outputs", ";".join(missing))
    j_manifest = load_json(J / "01_extract03j_run_manifest.json")
    if j_manifest.get("status") != "extract03j_near_alignment_structure_review_completed_near_alignment_patterns_characterized":
        fail("extract03k_blocked_missing_extract03j_outputs", "unexpected EXTRACT03J status")
    vector_rows = read_csv(H / "09_response_vector_export.csv")
    if len(vector_rows) != 42:
        fail("extract03k_blocked_missing_h_r1_vectors", "expected 42 H-R1 vector rows")

    OUT.mkdir(parents=True)
    upstream_paths = [J, I, H, AUTH01, G, F, E, D, L2]
    upstream_paths = [path for path in upstream_paths if path.exists()]
    before = {rel(path): tree_hash(path) if path.is_dir() else sha(path) for path in upstream_paths}

    near_items = read_csv(J / "04_near_alignment_item_import.csv")
    group_pairs = read_csv(J / "05_identity_group_pair_near_alignment_summary.csv")
    component_rows = read_csv(J / "06_component_near_alignment_distribution.csv")
    controls = control_rows()
    control_ids = [row["control_id"] for row in controls]

    inv_rows = []
    for idx, path in enumerate(upstream_paths, 1):
        inv_rows.append({
            "artifact_id": f"E03K-U{idx:02d}",
            "upstream_block": path.name,
            "path": rel(path),
            "exists": path.exists(),
            "sha256": before[rel(path)],
            "role": "read-only contract input",
            "used_for": "control contract context and boundary",
            "notes": "No control execution or upstream mutation.",
        })
    write_csv("02_upstream_inventory_and_hashes.csv", list(inv_rows[0]), inv_rows)
    write_csv("03_input_availability_review.csv", ["input_id", "path", "available", "read_status", "purpose", "notes"], [
        {"input_id": f"E03K-I{i:02d}", "path": rel(path), "available": path.exists(), "read_status": "read_only", "purpose": "EXTRACT03K contract input", "notes": "No upstream execution."}
        for i, path in enumerate(upstream_paths, 1)
    ])
    write_csv("04_j_result_import_summary.csv", ["summary_item", "value", "status", "notes"], [
        {"summary_item": "extract03j_status", "value": j_manifest["status"], "status": "imported", "notes": "Primary upstream status."},
        {"summary_item": "near_alignment_items", "value": len(near_items), "status": "imported", "notes": "J near-alignment basis."},
        {"summary_item": "identity_group_pair_count", "value": len(group_pairs), "status": "imported", "notes": "J group-pair contract basis."},
        {"summary_item": "components_with_near_alignment", "value": j_manifest["components_with_near_alignment"], "status": "imported", "notes": "All components reviewed in J."},
        {"summary_item": "controls_executed_in_K", "value": False, "status": "guarded", "notes": "K is contract-only."},
    ])
    hypotheses = [
        ("HYP_INDEX_ORDER", "Index/order hypothesis", "Collinearity may follow from index convention, ordering, or deterministic axis alignment.", "yes"),
        ("HYP_SMALL_SHIFT", "Small shift hypothesis", "Collinearity may be sensitive to tiny fixed index shifts.", "yes"),
        ("HYP_GLOBAL_SIGN", "Global sign/orientation hypothesis", "Opposite collinearity may follow from sign or anchor conventions.", "yes"),
        ("HYP_SCALE_NORMALIZATION", "Scale/normalization hypothesis", "L2 normalization may remove amplitude differences and expose collinearity.", "yes"),
        ("HYP_OFFSET_CENTERING", "Offset/centering hypothesis", "Offsets or baseline-like structures may affect shape review.", "yes"),
        ("HYP_SERIALIZATION_PRECISION", "Serialization/precision hypothesis", "Rounding, float64, or hash precision may affect exact identity boundaries.", "yes"),
        ("HYP_IDENTITY_LABELING", "Identity-labeling hypothesis", "Group labels may obscure equivalent structural roles.", "yes"),
        ("HYP_COMPONENT_MEMBERSHIP", "Component-membership hypothesis", "Component assignment may concentrate collinearity patterns.", "yes"),
        ("HYP_PAIR_SYMMETRY_ROLE", "Pair-symmetry/role hypothesis", "Ordered pairs or mirror-like roles may organize same/opposite patterns.", "yes"),
        ("HYP_SOURCE_RESPONSE_DEGENERACY", "Source-response degeneracy hypothesis", "The response construction may generate degenerate or nearly degenerate shapes.", "yes"),
    ]
    write_csv("05_collinearity_hypothesis_registry.csv", ["hypothesis_id", "hypothesis_name", "description", "supported_by_J", "could_explain_same_collinearity", "could_explain_opposite_collinearity", "requires_future_control", "claim_boundary", "notes"], [
        {"hypothesis_id": hid, "hypothesis_name": name, "description": desc, "supported_by_J": supported, "could_explain_same_collinearity": "yes", "could_explain_opposite_collinearity": "yes", "requires_future_control": "yes", "claim_boundary": CLAIM, "notes": "Registry only; hypothesis not tested in K."}
        for hid, name, desc, supported in hypotheses
    ])
    write_csv("06_control_family_contract.csv", list(controls[0]), controls)
    for idx, row in enumerate(controls, 7):
        filename = FILES[idx - 1]
        write_csv(filename, list(row), [row])
    operations = [
        ("read_H_R1_vectors", "yes", "yes", "no", "K may inventory; K-R1 may read if authorized."),
        ("read_J_near_alignment_items", "yes", "yes", "no", "Contract basis."),
        ("compute_review_distances", "no", "yes", "yes", "Future K-R1 only."),
        ("compute_review_similarity", "no", "yes", "yes", "Future K-R1 only; not K."),
        ("run_index_permutation_control", "no", "yes", "yes", "Future K-R1 only."),
        ("run_sign_control", "no", "yes", "yes", "Future K-R1 only."),
        ("run_scale_control", "no", "yes", "yes", "Future K-R1 only."),
        ("run_offset_control", "no", "yes", "yes", "Future K-R1 only."),
        ("run_serialization_control", "no", "yes", "yes", "Future K-R1 only."),
        ("recompute_K", "no", "no", "not_allowed", "Forbidden."),
        ("recompute_strength", "no", "no", "not_allowed", "Forbidden."),
        ("recompute_d", "no", "no", "not_allowed", "Forbidden."),
        ("recompute_D", "no", "no", "not_allowed", "Forbidden."),
        ("recompute_edges", "no", "no", "not_allowed", "Forbidden."),
        ("rerun_shortest_paths", "no", "no", "not_allowed", "Forbidden."),
        ("rerun_clusters", "no", "no", "not_allowed", "Forbidden."),
        ("rerun_motifs", "no", "no", "not_allowed", "Forbidden."),
        ("run_bootstrap", "no", "no", "not_allowed", "Forbidden."),
        ("open_F3_raw_source", "no", "no", "not_allowed", "Forbidden."),
        ("reconstruct_raw_phases", "no", "no", "not_allowed", "Forbidden."),
        ("make_physical_claim", "no", "no", "not_allowed", "Forbidden."),
    ]
    write_csv("17_allowed_forbidden_operations_matrix.csv", ["operation", "allowed_in_K", "allowed_in_future_K_R1", "requires_separate_authorization", "notes"], [
        {"operation": op, "allowed_in_K": k, "allowed_in_future_K_R1": kr1, "requires_separate_authorization": auth, "notes": notes}
        for op, k, kr1, auth, notes in operations
    ])
    write_csv("18_required_future_inputs.csv", ["input_id", "required_input", "source_path", "required_for_controls", "read_mode", "notes"], [
        {"input_id": "K-R1-IN01", "required_input": "H-R1 exported vectors", "source_path": "runs/QSB-EXTRACT03H-R1/authorized_response_vector_export/09_response_vector_export.csv", "required_for_controls": "C1-C10", "read_mode": "read_only", "notes": "No vector mutation."},
        {"input_id": "K-R1-IN02", "required_input": "J near-alignment items", "source_path": "runs/QSB-EXTRACT03J/near_alignment_structure_review/04_near_alignment_item_import.csv", "required_for_controls": "C1-C10", "read_mode": "read_only", "notes": "Primary relation set."},
        {"input_id": "K-R1-IN03", "required_input": "J group-pair summary", "source_path": "runs/QSB-EXTRACT03J/near_alignment_structure_review/05_identity_group_pair_near_alignment_summary.csv", "required_for_controls": "C7-C10", "read_mode": "read_only", "notes": "Group-level controls."},
        {"input_id": "K-R1-IN04", "required_input": "existing A-R1 K matrix", "source_path": "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv", "required_for_controls": "C9", "read_mode": "read_only", "notes": "Comparison only; no K recompute."},
    ])
    write_csv("19_required_future_outputs.csv", ["output_id", "required_output", "required_for_controls", "format", "notes"], [
        {"output_id": "K-R1-OUT01", "required_output": "control_run_manifest", "required_for_controls": "C1-C10", "format": "json", "notes": "Must record guard flags."},
        {"output_id": "K-R1-OUT02", "required_output": "control_family_results", "required_for_controls": "C1-C10", "format": "csv", "notes": "One row per control family."},
        {"output_id": "K-R1-OUT03", "required_output": "no_recompute_guard_results", "required_for_controls": "C1-C10", "format": "csv", "notes": "Must pass before interpretation."},
        {"output_id": "K-R1-OUT04", "required_output": "claim_boundary_matrix", "required_for_controls": "C1-C10", "format": "csv", "notes": "No physical claim expansion."},
    ])
    auth_template = {
        "authorization_status": "TEMPLATE_REQUIRES_HUMAN_APPROVAL",
        "authorized_work_package": "QSB-EXTRACT03K-R1",
        "source_contract": "QSB-EXTRACT03K",
        "allowed_control_families": control_ids,
        "control_seed": CONTROL_SEED,
        "draw_algorithm": DRAW_ALGORITHM,
        "no_K_recompute": True,
        "no_strength_d_D_edge_recompute": True,
        "no_shortest_path_rerun": True,
        "no_edge_rethresholding": True,
        "no_cluster_or_motif_rerun": True,
        "no_bootstrap": True,
        "no_raw_phase_reconstruction": True,
        "no_F3_raw_source_open": True,
        "no_l2_change": True,
        "no_post_hoc_tuning": True,
        "no_physical_claim": True,
        "no_geometry_claim": True,
        "no_gravity_claim": True,
    }
    write_text("20_future_authorization_template.json", json.dumps(auth_template, indent=2, sort_keys=True))
    guards = [
        "no_controls_executed", "no_K_recompute", "no_strength_recompute", "no_d_recompute",
        "no_D_recompute", "no_edge_recompute", "no_shortest_path_rerun", "no_cluster_rerun",
        "no_motif_rerun", "no_bootstrap", "no_raw_phase_reconstruction", "no_F3_raw_source_opened",
        "no_upstream_mutation", "no_l2_change", "no_post_hoc_tuning", "no_physical_claim",
        "no_geometry_claim", "no_gravity_claim", "overwrite_refusal",
    ]
    write_csv("21_no_execution_guard_results.csv", ["guard_id", "guard", "status", "evidence", "blocking", "notes"], [
        {"guard_id": f"E03K-G{i:02d}", "guard": guard, "status": "pass", "evidence": "contract-only script; no control execution code path", "blocking": "yes", "notes": "Guard satisfied."}
        for i, guard in enumerate(guards, 1)
    ])
    write_csv("22_claim_boundary_matrix.csv", ["claim_id", "statement", "classification", "safe_wording", "notes"], [
        {"claim_id": "E03K-CB01", "statement": "EXTRACT03K defines a prospective control contract.", "classification": "supported", "safe_wording": CLAIM, "notes": "Contract-only."},
        {"claim_id": "E03K-CB02", "statement": "EXTRACT03K proves QSB or confirms a physical mechanism.", "classification": "unsupported_forbidden", "safe_wording": "Do not claim.", "notes": "No controls executed."},
        {"claim_id": "E03K-CB03", "statement": "EXTRACT03K demonstrates geometry or gravity.", "classification": "unsupported_forbidden", "safe_wording": "Do not claim.", "notes": "No physical interpretation."},
        {"claim_id": "E03K-CB04", "statement": "EXTRACT03K repairs L2.", "classification": "unsupported_forbidden", "safe_wording": "L2 fail remains unchanged.", "notes": "No L2 operation."},
        {"claim_id": "E03K-CB05", "statement": "EXTRACT03K establishes that collinearity is natural or an artifact.", "classification": "unsupported_forbidden", "safe_wording": "Origin remains open until separately authorized controls.", "notes": "K is not an execution block."},
    ])
    l2 = load_json(L2)
    write_csv("23_l2_boundary_check.csv", ["boundary_item", "upstream_value", "extract03k_value", "status", "notes"], [
        {"boundary_item": "L2_result", "upstream_value": l2.get("minimaltest_contract_result"), "extract03k_value": "fail unchanged", "status": "pass", "notes": "No L2 rerun."},
        {"boundary_item": "N4_support", "upstream_value": "0/3 required 2/3", "extract03k_value": "unchanged", "status": "pass", "notes": "Boundary retained."},
        {"boundary_item": "theta_new", "upstream_value": "0.012446436850524916", "extract03k_value": "unchanged", "status": "pass", "notes": "No tuning."},
        {"boundary_item": "epsilon_new", "upstream_value": "0.006009422749372488", "extract03k_value": "unchanged", "status": "pass", "notes": "No tuning."},
    ])
    write_csv("24_validation_results.csv", ["validation_id", "check_name", "status", "observed_value", "expected_value", "blocking", "notes"], [
        {"validation_id": "E03K-V01", "check_name": "artifact_count", "status": "pass", "observed_value": 32, "expected_value": 32, "blocking": "yes", "notes": "Final manifest guard checks this again."},
        {"validation_id": "E03K-V02", "check_name": "control_families", "status": "pass", "observed_value": len(controls), "expected_value": 10, "blocking": "yes", "notes": "All required families defined."},
        {"validation_id": "E03K-V03", "check_name": "run_now_all_no", "status": "pass", "observed_value": all(r["run_now"] == "no" for r in controls), "expected_value": True, "blocking": "yes", "notes": "No controls executed."},
        {"validation_id": "E03K-V04", "check_name": "future_authorization_template", "status": "pass", "observed_value": True, "expected_value": True, "blocking": "yes", "notes": "Template created."},
    ])
    write_csv("25_review_items.csv", ["review_item_id", "category", "description", "severity", "recommended_resolution", "notes"], [
        {"review_item_id": "E03K-RI-01", "category": "requires_human_authorization", "description": "K-R1 controls must not run from this contract without explicit human approval.", "severity": "blocking_future_execution", "recommended_resolution": "Review and approve a filled authorization derived from 20_future_authorization_template.json.", "notes": "Contract ready."}
    ])
    write_text("26_human_readable_control_contract_de.md", f"""# QSB-EXTRACT03K Collinearity Control Contract

## Ausgangspunkt
EXTRACT03J charakterisiert 119 Near-Alignment-Beziehungen als nahezu perfekte Same-/Opposite-Collinearity-Patterns.

## Befund aus EXTRACT03J
J importierte H-R1-Vektoren, fand {len(near_items)} Near-Alignment-Items, {len(group_pairs)} Identity-Group-Paare und {j_manifest['components_with_near_alignment']} Komponenten mit Near-Alignment.

## Warum ein Kontrollvertrag noetig ist
Der Ursprung dieser Kollinearitaet ist offen. K friert nur fest, wie spaetere Kontrollen pruefen duerfen.

## Kontrollhypothesen
Index, Shift, Sign/Orientierung, Scale/Normalisierung, Offset, Serialisierung, Identity-Labeling, Component Membership, Pair-Symmetrie und Source-Response-Degeneracy werden als Hypothesen registriert.

## Kontrollfamilien
Es werden 10 Kontrollfamilien C1 bis C10 definiert. Alle haben `run_now=no`.

## Erlaubte und verbotene Operationen
K darf lesen und Vertragsartefakte schreiben. K darf keine Kontrolltests, keine K-/d-/D-/Edge-Rechnung und keine Pipeline-Reruns ausfuehren.

## Determinismus und Seeds
Fuer spaetere Kontrollen werden `control_seed=20260623`, `{DRAW_ALGORITHM}`, `{SORT_RULE}` und `{TIE_BREAK_RULE}` eingefroren.

## Was K ausdruecklich nicht ausfuehrt
Keine Kontrollen, keine Permutationen, keine Rechenkontrollen, kein F3-Rohdatenzugriff, kein Bootstrap.

## Was ein spaeterer K-R1 pruefen darf
Nur die autorisierten Kontrollfamilien aus dem Template, read-only gegen die eingefrorenen Inputs und ohne verbotene Modellneuberechnungen.

## Was ausdruecklich nicht behauptet wird
K behauptet nicht, dass die Kollinearitaet natuerlich oder ein Artefakt ist. K macht keinen Physik-, Geometrie-, Gravitations- oder L2-Reparaturclaim.

## Naechster Schritt
Human Review des Vertrags und ggf. separate Autorisierung fuer QSB-EXTRACT03K-R1.
""")
    write_text("27_publication_safe_note_candidates.md", """# Publication-safe note candidates

- EXTRACT03K defines a prospective control contract for near-collinearity origin tests.
- EXTRACT03K executes no controls and creates no new model evidence.
- Future controls require separate human authorization and must not recompute K, d, D, Strength, or Edges.
- The origin of the collinearity remains open.
""")
    write_csv("28_next_step_options.csv", ["option_id", "option", "allowed", "notes"], [
        {"option_id": "E03K-N01", "option": "Human review of control contract", "allowed": "yes", "notes": "Recommended next step."},
        {"option_id": "E03K-N02", "option": "Fill and approve K-R1 authorization template", "allowed": "yes_after_review", "notes": "Required before execution."},
        {"option_id": "E03K-N03", "option": "Run controls now", "allowed": "no", "notes": "K is contract-only."},
    ])
    write_text("29_recommended_next_step.md", "# Recommended next step\n\nReview `06_control_family_contract.csv` and `20_future_authorization_template.json`; if acceptable, create a separately approved QSB-EXTRACT03K-R1 authorization.\n")
    summary = {
        "work_package": "QSB-EXTRACT03K",
        "status": STATUS_OK,
        "near_alignment_items": len(near_items),
        "identity_group_pair_count": len(group_pairs),
        "control_families": control_ids,
        "control_seed": CONTROL_SEED,
        "draw_algorithm": DRAW_ALGORITHM,
        "run_now": False,
        "controls_executed": False,
        "claim_boundary": CLAIM,
    }
    write_text("30_contract_machine_readable_summary.json", json.dumps(summary, indent=2, sort_keys=True))
    write_text("31_short_result_note_de.md", """# QSB-EXTRACT03K - Kurze Ergebnisnotiz

## Befund
Der Collinearity-Control-Vertrag wurde erstellt. Er definiert 10 Kontrollfamilien fuer einen spaeteren, separat autorisierten K-R1-Block.

## Interpretation
K ist Contract-only. Es wurden keine Kontrolltests ausgefuehrt.

## Hypothese
Keine Ursprungshypothese wird in K entschieden.

## Offene Luecke
Der Ursprung der Same-/Opposite-Collinearity-Patterns bleibt bis zu separat autorisierten Kontrollen offen.

## Claim Boundary
Kein Physik-, Geometrie-, Gravitations-, Artifact-/Naturalness- oder L2-Reparaturclaim.
""")
    manifest = {
        "work_package": "QSB-EXTRACT03K",
        "status": STATUS_OK,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(ROOT),
        "extract03j_seen": True,
        "extract03j_status": j_manifest["status"],
        "h_r1_vectors_seen": True,
        "near_alignment_items": len(near_items),
        "identity_group_pair_count": len(group_pairs),
        "component_count": j_manifest["component_count"],
        "component_sizes": j_manifest["component_sizes"],
        "control_families_defined": len(controls),
        "future_authorization_template_created": True,
        "run_now": False,
        "controls_executed": False,
        "K_recomputed": False,
        "strength_recomputed": False,
        "d_recomputed": False,
        "D_recomputed": False,
        "edge_recomputed": False,
        "shortest_path_rerun": False,
        "raw_phase_reconstruction": False,
        "bootstrap_run": False,
        "upstream_modified": False,
        "l2_fail_changed": False,
        "post_hoc_tuning_performed": False,
        "physical_evidence_claim_made": False,
        "geometry_claim_made": False,
        "gravity_claim_made": False,
        "review_items_count": 1,
        "claim_boundary": CLAIM,
        "next_allowed_action": "human_review_then_separate_authorization_for_QSB_EXTRACT03K_R1_control_run",
    }
    write_text("01_extract03k_run_manifest.json", json.dumps(manifest, indent=2, sort_keys=True))
    write_text("FINAL_RESULT_NOTE.md", f"""# QSB-EXTRACT03K Final Result

## Status
`{STATUS_OK}`

## Reviewed Inputs
EXTRACT03J, EXTRACT03I, H-R1, D/E/F/G/AUTH01, and L2 context were read as contract inputs only.

## J Near-Alignment Basis
K imported the J basis of {len(near_items)} near-alignment items and {len(group_pairs)} identity-group pairs.

## Control Hypotheses
Ten origin-review hypotheses were registered for future controls.

## Control Family Contract
Ten control families C1-C10 were defined with `run_now=no`.

## Future Authorization Template
`20_future_authorization_template.json` was created for a later human-approved QSB-EXTRACT03K-R1.

## No-Execution Guards
No controls were executed. No K/Strength/d/D/Edge, shortest-path, clustering, motif, bootstrap, raw-phase, or F3 raw-source operation occurred.

## Claim Boundary
{CLAIM}

## L2 Boundary
L2 remains fail with N4 support 0/3 required 2/3; no tuning or repair was performed.

## Next Allowed Action
Human review of this contract, then separate authorization for QSB-EXTRACT03K-R1 if desired.
""")

    actual = sorted(p.name for p in OUT.iterdir() if p.is_file())
    if actual != sorted(FILES):
        fail("extract03k_blocked_guard_violation", f"file manifest mismatch missing={sorted(set(FILES)-set(actual))} extra={sorted(set(actual)-set(FILES))}")
    after = {rel(path): tree_hash(path) if path.is_dir() else sha(path) for path in upstream_paths}
    changed = [path for path in before if before[path] != after[path]]
    if changed:
        fail("extract03k_blocked_guard_violation", f"upstream modified: {changed}")
    print(json.dumps({
        "status": STATUS_OK,
        "artifacts": len(actual),
        "near_alignment_items": len(near_items),
        "identity_group_pair_count": len(group_pairs),
        "control_families_defined": len(controls),
        "run_now": False,
        "controls_executed": False,
        "K_recomputed": False,
        "upstream_modified": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
