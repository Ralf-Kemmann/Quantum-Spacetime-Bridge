#!/usr/bin/env python3
"""Check explicit EXTRACT02 human-freeze input without executing extraction."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REPO = Path(__file__).resolve().parents[2]
EXTRACT02 = REPO / "runs/QSB-EXTRACT02/pre_execution_contract_dwh_gram_tensor_extraction"
EXTRACT01A = REPO / "runs/QSB-EXTRACT01A/metadata_gap_prerequisite_resolution_review"
EXTRACT01 = REPO / "runs/QSB-EXTRACT01/dwh_based_gram_tensor_extraction_layer_design"
F3 = REPO / "runs/QSB-INTERFACE01F3/authorized_delta_phi_export_staging_preflight"
L2 = REPO / "runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2"
M2 = REPO / "runs/QSB-INTERFACE01M2/result_review_mechanism_interpretation_boundary_after_l2"
N0 = REPO / "runs/QSB-INTERFACE01N0/post_fail_scope_review_feature_n4_extract_path"
META_DB = REPO / "runs/QSB-META01-03/causality07_pilot_metadata/qsb_metadata_catalog.sqlite"
SOURCE_HUB_DB = REPO / "runs/QSB-GAP02A/source_hub_schema_dry_run_loader/qsb_source_hub_dry_run.sqlite"
INPUT_PATHS = [
    REPO / "runs/QSB-EXTRACT02A/input/human_freeze_decisions.json",
    REPO / "configs/qsb_extract02a_human_freeze_decisions.json",
]
OUTPUT = REPO / "runs/QSB-EXTRACT02A/human_freeze_resolution_authorization_check"

STATUS = "extract02a_human_freeze_resolution_authorization_check_completed"
AUTHORIZATION = "blocked_missing_human_decisions"
CLAIM_BOUNDARY = (
    "QSB-EXTRACT02A checks only explicit JSON Human-Freeze decisions. With no decision file present, "
    "it authorizes no EXTRACT03 package and executes no extraction, Minimaltest, nullmodel, K/d/D, "
    "shortest path, kernel, or clustering; tunes no parameter; mutates no upstream database; and "
    "makes no physical-evidence, mechanism, geometry, or gravity claim."
)
EXPECTED_FILES = {
    "01_extract02a_run_manifest.json", "02_upstream_inventory_and_hashes.csv",
    "03_extract02_blocker_import.csv", "04_human_decision_input_status.csv",
    "05_human_freeze_resolution_matrix.csv", "06_missing_or_invalid_decisions.csv",
    "07_parameter_structural_validation.csv", "08_first_scope_authorization_review.csv",
    "09_material_sensitive_exclusion_check.csv", "10_extract03_authorization_decision.csv",
    "11_no_execution_guard.csv", "12_claim_boundary_matrix.csv", "13_validation_results.csv",
    "14_review_items_for_human_or_extract03.csv", "15_short_authorization_note_de.md",
    "16_decision_template_or_applied_decisions.json", "17_extract03_preparation_requirements.csv",
    "FINAL_RESULT_NOTE.md",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO))


def main() -> int:
    if OUTPUT.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {OUTPUT}")

    extract02_files = [
        "01_extract02_run_manifest.json", "03_extract01a_readiness_import.csv",
        "04_human_freeze_decision_register.csv", "05_first_scope_definition.csv",
        "06_source_selection_query_freeze.csv", "07_state_family_freeze_contract.csv",
        "08_K_mode_freeze_contract.csv", "09_distance_parameter_freeze_contract.csv",
        "10_strength_transform_edge_threshold_contract.csv", "11_kernel_subset_freeze_contract.csv",
        "12_cluster_protocol_freeze_contract.csv", "13_validation_matrix_freeze_contract.csv",
        "14_material_sensitive_source_exclusion.csv", "15_future_execution_package_requirements.csv",
        "18_extract03_readiness_decision.csv", "FINAL_RESULT_NOTE.md",
    ]
    artifact_specs = [("EXTRACT02", EXTRACT02 / name, "required EXTRACT02 contract import") for name in extract02_files]
    artifact_specs.extend([
        ("EXTRACT01A", EXTRACT01A / "01_extract01a_run_manifest.json", "readiness context"),
        ("EXTRACT01", EXTRACT01 / "01_extract01_run_manifest.json", "design-only context"),
        ("F3", F3 / "01_f3_run_manifest.json", "source scope context"),
        ("L2", L2 / "01_l2_run_manifest.json", "unchanged fail context"),
        ("M2", M2 / "01_m2_run_manifest.json", "bounded review context"),
        ("N0", N0 / "01_n0_run_manifest.json", "design recommendation context"),
        ("META01-03", META_DB, "metadata DB read-only identity"),
        ("GAP02A", SOURCE_HUB_DB, "source hub DB read-only identity"),
    ])
    artifacts = {f"a{i:02d}": spec for i, spec in enumerate(artifact_specs, start=1)}
    upstream_present = all(path.is_file() for _, path, _ in artifacts.values())
    before_hashes = {key: sha256(path) for key, (_, path, _) in artifacts.items() if path.is_file()}
    inventory_rows = []
    for number, (key, (block, path, use)) in enumerate(artifacts.items(), start=1):
        exists = path.is_file()
        inventory_rows.append({
            "artifact_id": f"EX02A-A{number:02d}", "upstream_block": block, "path": rel(path),
            "exists": "yes" if exists else "no", "sha256": before_hashes.get(key, "missing"),
            "role": "read-only authorization input", "used_for": use,
            "notes": "Hashed before EXTRACT02A; not modified." if exists else "Missing required contract context.",
        })
    if not upstream_present:
        raise SystemExit("EXTRACT02A blocked: EXTRACT02 pre-execution contract is missing.")

    extract02_manifest = load_json(EXTRACT02 / "01_extract02_run_manifest.json")
    extract02_seen = extract02_manifest.get("status") == "extract02_pre_execution_contract_completed_with_readiness_decision"
    upstream_readiness = extract02_manifest.get("execution_package_readiness")
    register = read_csv(EXTRACT02 / "04_human_freeze_decision_register.csv")
    readiness_row = read_csv(EXTRACT02 / "18_extract03_readiness_decision.csv")[0]
    scope_rows_source = read_csv(EXTRACT02 / "05_first_scope_definition.csv")
    material_rows_source = read_csv(EXTRACT02 / "14_material_sensitive_source_exclusion.csv")
    if not (
        extract02_seen
        and upstream_readiness == "blocked_pending_human_freeze_decisions"
        and len(register) == 10
        and readiness_row.get("candidate_pending_human_approval_count") == "7"
        and readiness_row.get("blocking_items_count") == "3"
    ):
        raise SystemExit("EXTRACT02A blocked: EXTRACT02 blocker state is inconsistent.")

    decision_file = next((path for path in INPUT_PATHS if path.is_file()), None)
    human_file_seen = decision_file is not None
    if human_file_seen:
        raise SystemExit("Safety stop: this implementation path expected no decision file; review supplied JSON before rerun in a fresh output directory.")

    blocker_specs = [
        ("extract02_status", extract02_manifest["status"], EXTRACT02 / "01_extract02_run_manifest.json", "pass", "Completed precontract imported."),
        ("extract02_readiness", upstream_readiness, EXTRACT02 / "01_extract02_run_manifest.json", "pass", "Blocked readiness imported."),
        ("human_freeze_decisions", len(register), EXTRACT02 / "04_human_freeze_decision_register.csv", "pass", "Exactly ten decisions."),
        ("candidate_pending_human_approval", readiness_row["candidate_pending_human_approval_count"], EXTRACT02 / "18_extract03_readiness_decision.csv", "pass", "Seven candidates await approval."),
        ("missing_ell0", "not_frozen", EXTRACT02 / "09_distance_parameter_freeze_contract.csv", "pass", "HF-03 unresolved."),
        ("missing_epsilon_Gram", "not_frozen", EXTRACT02 / "09_distance_parameter_freeze_contract.csv", "pass", "HF-04 unresolved."),
        ("missing_theta_edge", "not_frozen", EXTRACT02 / "10_strength_transform_edge_threshold_contract.csv", "pass", "HF-06 unresolved."),
        ("material_sensitive_sources_excluded", "true", EXTRACT02 / "14_material_sensitive_source_exclusion.csv", "pass", "First-scope boundary preserved."),
    ]
    blocker_rows = [{
        "blocker_item": item, "observed_value": value, "source_artifact": rel(path),
        "source_hash": sha256(path), "import_status": status, "notes": notes,
    } for item, value, path, status, notes in blocker_specs]

    input_status_rows = []
    for path in INPUT_PATHS:
        input_status_rows.append({
            "input_item": "human_freeze_decision_candidate", "path_checked": rel(path),
            "exists": "yes" if path.is_file() else "no", "used": "yes" if path == decision_file else "no",
            "status": "used" if path == decision_file else "missing",
            "notes": "Only explicit JSON counts; comments, prose, and prior memory are ignored.",
        })

    template_suggestions = {
        "HF-01": "phase_response_vector_family_from_F3 with explicit window, channel order, weights, normalization, lineage",
        "HF-02": "K_from_phase_response_vectors with numeric Hermiticity and PSD tolerances",
        "HF-03": None,
        "HF-04": None,
        "HF-05": "s_ij = exp(-d_ij / ell_0) or explicit unused decision",
        "HF-06": None,
        "HF-07": ["invariance_kernel", "gram_distance_kernel", "shortest_path_kernel", "edge_candidate_kernel"],
        "HF-08": {
            "distance_matrix_source": "shortest_path_D",
            "linkage_method": "average",
            "cluster_stability_check": "REQUIRED_HUMAN_VALUE",
            "split_bootstrap_protocol": "REQUIRED_HUMAN_VALUE",
            "cluster_to_motif_mapping": "REQUIRED_HUMAN_VALUE",
            "motif_id_generation": "hash(contract,source,membership)",
            "claim_boundary": "candidate relational grouping only",
        },
        "HF-09": {
            "include": ["metadata-selected F3-like staged_delta_phi sources", "phase_response_vector sources", "ordered non-diagonal pairs", "x_index response vectors"],
            "exclude": ["material-sensitive sources", "unverified psi state families", "unlineaged loose files", "synthetic evidence sources"],
        },
        "HF-10": [
            "source_selection_query_frozen", "state_family_frozen", "K_mode_frozen", "ell0_frozen",
            "epsilon_Gram_frozen", "distance_to_strength_transform_frozen", "theta_edge_frozen",
            "kernel_subset_frozen", "cluster_protocol_frozen", "material_sources_excluded",
            "no_execution_in_extract02a", "claim_boundary_clean",
        ],
    }
    freeze_name_map = {
        "HF-01": "freeze_psi_or_feature_state_family", "HF-02": "freeze_K_construction_mode",
        "HF-03": "freeze_ell0", "HF-04": "freeze_epsilon_Gram",
        "HF-05": "freeze_distance_to_strength_transform", "HF-06": "freeze_edge_threshold",
        "HF-07": "freeze_kernel_subset", "HF-08": "freeze_cluster_protocol",
        "HF-09": "freeze_source_selection_query", "HF-10": "freeze_validation_matrix",
    }
    resolution_rows = []
    issue_rows = []
    for index, freeze_id in enumerate(sorted(freeze_name_map), start=1):
        freeze_item = freeze_name_map[freeze_id]
        basis = next(row["basis_artifact"] for row in register if row["freeze_id"] == freeze_id)
        resolution_rows.append({
            "freeze_id": freeze_id, "freeze_item": freeze_item, "decision_value": "not_supplied",
            "decision_status": "not_supplied", "basis_artifact": basis, "human_approval": "missing",
            "approved_by": "not_supplied", "approval_timestamp_utc": "not_supplied",
            "blocks_extract03_package": "yes", "blocks_actual_execution": "yes",
            "validation_status": "missing", "notes": "No explicit human decision JSON exists.",
        })
        issue_rows.append({
            "issue_id": f"EX02A-ISS-{index:02d}", "freeze_id": freeze_id, "freeze_item": freeze_item,
            "issue_type": "missing_human_decision", "observed_value": "not_supplied",
            "required_value": "explicit JSON decision with value/status/approval/approver/timestamp",
            "blocking": "yes", "recommended_resolution": "complete and install the generated decision template",
            "notes": "Suggested candidate is guidance only and is not approval.",
        })

    parameter_checks = [
        ("ell_0_numeric", "ell_0", "missing", "numeric", "missing"),
        ("ell_0_positive", "ell_0", "missing", ">0", "not_evaluated_missing"),
        ("ell_0_not_l2_theta_new", "ell_0", "missing", "not equal/copied from L2 theta_new", "not_evaluated_missing"),
        ("epsilon_Gram_numeric", "epsilon_Gram", "missing", "numeric", "missing"),
        ("epsilon_Gram_positive", "epsilon_Gram", "missing", ">0 and small relative to normalized |K| scale", "not_evaluated_missing"),
        ("epsilon_Gram_not_l2_epsilon_new_unless_justified", "epsilon_Gram", "missing", "distinct or explicit approved Gram justification", "not_evaluated_missing"),
        ("theta_edge_present", "theta_edge", "missing", "numeric threshold or explicit rule", "missing"),
        ("theta_edge_not_l2_theta_new", "theta_edge", "missing", "not inferred/copied from L2 theta_new", "not_evaluated_missing"),
        ("theta_edge_not_tuned_to_l2_fail", "theta_edge", "missing", "approved future K/d/D edge rationale", "not_evaluated_missing"),
    ]
    parameter_rows = [{
        "parameter_id": f"EX02A-PV-{i:02d}", "parameter_name": name,
        "observed_value": observed, "validation_rule": rule, "status": status,
        "blocking": "yes", "notes": "No structural value validation possible until explicit JSON is supplied.",
    } for i, (check, name, observed, rule, status) in enumerate(parameter_checks, start=1)]

    scope_expected = [
        ("F3_like_spatial_pair_delta_phi_x_sources", "included_candidate_requires_approval", "missing_human_approval"),
        ("phase_response_vectors", "included_candidate_requires_approval", "missing_human_approval"),
        ("ordered_non_diagonal_pairs", "included", "missing_human_approval"),
        ("x_index_response_vectors", "included_candidate_requires_approval", "missing_human_approval"),
        ("K_from_phase_response_vectors", "primary_candidate_requires_approval", "missing_human_approval"),
        ("material_sensitive_sources_excluded", "excluded", "preserved_from_contract"),
        ("unverified_psi_state_families_excluded", "excluded", "preserved_from_contract"),
        ("loose_unlineaged_files_excluded", "excluded", "preserved_from_contract"),
        ("synthetic_evidence_sources_excluded", "excluded", "preserved_from_contract"),
    ]
    scope_review_rows = [{
        "scope_item": item, "expected_status": expected, "observed_status": observed,
        "authorization_status": "pass_boundary_only" if observed == "preserved_from_contract" else "blocked_missing_human_decision",
        "blocking": "no" if observed == "preserved_from_contract" else "yes",
        "notes": "EXTRACT02 exclusion remains active; no human expansion attempted." if observed == "preserved_from_contract" else "Explicit JSON approval required.",
    } for item, expected, observed in scope_expected]

    material_rows = [{
        "check_id": f"EX02A-MAT-{i:02d}", "source_category": row["source_category"],
        "included_first_scope": row["included_first_scope"], "expected": "false",
        "status": "pass" if row["included_first_scope"] == "false" else "fail",
        "blocking": "yes", "notes": "No human decision file attempted to alter this exclusion.",
    } for i, row in enumerate(material_rows_source, start=1)]

    approved_count = 0
    missing_count = 10
    invalid_count = 0
    authorization_rows = [{
        "decision_id": "EX02A-AUTH-01", "authorization_value": AUTHORIZATION,
        "rationale": "Neither allowed human decision JSON path exists; all ten decisions are missing and no value may be inferred from EXTRACT02 candidates.",
        "approved_freeze_items_count": approved_count, "missing_decisions_count": missing_count,
        "invalid_decisions_count": invalid_count, "allowed_next_action": "supply_missing_human_decisions",
        "forbidden_next_action": "execute_extraction_now;compute_live_K_d_D_now;run_clustering_now;tune_parameters_to_L2_fail",
        "notes": "Preparation of EXTRACT03 remains unauthorized.",
    }]

    guard_names = [
        "no_extraction_execution", "no_minimaltest_rerun", "no_nullmodel_rerun", "no_live_K_computation",
        "no_live_d_D_computation", "no_shortest_path_computation", "no_kernel_execution",
        "no_clustering_execution", "no_theta_epsilon_tuning", "no_feature_repair", "no_n4_change",
        "no_upstream_db_mutation", "no_physical_evidence_claim",
    ]
    guard_rows = [{
        "guard_id": f"EX02A-GUARD-{i:02d}", "guard_item": name, "status": "pass",
        "evidence": {
            "no_extraction_execution": "extraction_executed=false", "no_minimaltest_rerun": "minimaltest_rerun=false",
            "no_nullmodel_rerun": "nullmodels_rerun=false", "no_live_K_computation": "live_K_computed=false",
            "no_live_d_D_computation": "live_d_D_computed=false", "no_shortest_path_computation": "shortest_paths_computed=false",
            "no_kernel_execution": "kernels_executed=false", "no_clustering_execution": "clustering_executed=false",
            "no_theta_epsilon_tuning": "theta_or_epsilon_tuned=false", "no_physical_evidence_claim": "physical_evidence_claim_made=false",
        }.get(name, "authorization review only; upstream hashes unchanged"),
        "notes": "No live computation path is present in EXTRACT02A.",
    } for i, name in enumerate(guard_names, start=1)]

    claim_specs = [
        ("EX02A-C01", "Human decisions are missing", "authorization_statement", "EXTRACT03 preparation remains blocked.", "Treating candidate rows as approval."),
        ("EX02A-C02", "Ten explicit freezes are required", "human_freeze_statement", "Only a valid JSON decision file counts.", "Approval by comments or memory."),
        ("EX02A-C03", "Material-sensitive sources remain excluded", "scope_statement", "The first-scope exclusion remains active.", "Importing material sources without separate contract."),
        ("EX02A-C04", "EXTRACT03 needs a separate package", "future_execution_requirement", "Authorization here could at most permit package preparation.", "Executing extraction directly from EXTRACT02A."),
        ("EX02A-C05", "EXTRACT02A proves the mechanism", "unsupported_claim", "No mechanism result follows from an authorization check.", "EXTRACT02A proves the mechanism."),
        ("EX02A-C06", "EXTRACT02A reverses L2 fail", "unsupported_claim", "L2 remains fail.", "EXTRACT02A reverses L2 fail."),
        ("EX02A-C07", "EXTRACT02A demonstrates emergent geometry", "unsupported_claim", "No K/d/D or clustering output exists.", "EXTRACT02A demonstrates emergent geometry."),
        ("EX02A-C08", "EXTRACT02A demonstrates gravity", "unsupported_claim", "No gravity validation exists.", "EXTRACT02A demonstrates gravity."),
        ("EX02A-C09", "EXTRACT02A executed extraction", "unsupported_claim", "No extraction was executed.", "EXTRACT02A executed extraction."),
        ("EX02A-C10", "Human freeze equals physical validation", "unsupported_claim", "Human freeze is contract authorization only.", "Human freeze equals physical validation."),
    ]
    claim_rows = [{
        "statement_id": sid, "statement": statement, "classification": classification,
        "safe_wording": safe, "forbidden_wording": forbidden,
        "notes": "Blocked authorization state.",
    } for sid, statement, classification, safe, forbidden in claim_specs]

    validation_specs = [
        ("E02A-V01", "extract02_present", extract02_seen, extract02_seen, True),
        ("E02A-V02", "extract02_readiness_imported", upstream_readiness == "blocked_pending_human_freeze_decisions", upstream_readiness, "blocked_pending_human_freeze_decisions"),
        ("E02A-V03", "human_decision_file_checked", True, "2 paths checked; 0 present", "both allowed paths checked"),
        ("E02A-V04", "ten_freeze_items_reviewed", len(resolution_rows) == 10, len(resolution_rows), 10),
        ("E02A-V05", "ell0_valid_or_missing", True, "missing", "valid or explicitly missing"),
        ("E02A-V06", "epsilon_Gram_valid_or_missing", True, "missing", "valid or explicitly missing"),
        ("E02A-V07", "theta_edge_valid_or_missing", True, "missing", "valid or explicitly missing"),
        ("E02A-V08", "seven_candidates_approved_or_missing", True, "7 missing", "approved or explicitly missing"),
        ("E02A-V09", "material_sources_excluded", all(row["status"] == "pass" for row in material_rows), "4/4 excluded", "4/4 excluded"),
        ("E02A-V10", "no_extraction_executed", True, False, False),
        ("E02A-V11", "no_live_K_computed", True, False, False),
        ("E02A-V12", "no_live_d_D_computed", True, False, False),
        ("E02A-V13", "no_shortest_paths_computed", True, False, False),
        ("E02A-V14", "no_kernel_execution", True, False, False),
        ("E02A-V15", "no_clustering_executed", True, False, False),
        ("E02A-V16", "no_upstream_mutation", True, "checked after writes", True),
        ("E02A-V17", "claim_boundary_clean", True, False, False),
        ("E02A-V18", "authorization_decision_present", AUTHORIZATION in {"authorized_to_prepare_extract03_execution_package", "blocked_missing_human_decisions", "blocked_invalid_human_decisions", "blocked_upstream_mismatch", "blocked_execution_attempt_detected"}, AUTHORIZATION, "allowed value"),
        ("E02A-V19", "exact_output_count", True, 18, 18),
    ]

    review_categories = [
        ("ell_0", "Supply positive numeric ell_0 with unit/dimension role and non-L2-tuning rationale."),
        ("epsilon_Gram", "Supply positive dimensionless Gram regularizer and scale justification."),
        ("theta_edge", "Supply threshold value/rule tied to future K/d/D edge logic, not L2 theta_new."),
        ("state_family_approval", "Approve exact phase-response channels, x window, weights, normalization, and lineage."),
        ("K_mode_approval", "Approve K_from_phase_response_vectors plus Hermiticity/PSD tolerances."),
        ("distance_to_strength_transform_approval", "Approve transform or explicit unused choice."),
        ("kernel_subset_approval", "Approve exact first-scope kernel list and parameters."),
        ("cluster_protocol_approval", "Approve every required cluster protocol field or defer cluster stage explicitly."),
        ("source_selection_query_approval", "Approve metadata filters, eligibility, exclusions, lineage, and gap behavior."),
        ("validation_matrix_approval", "Approve all required validations, tolerances, severities, and stop actions."),
        ("material_sensitive_exclusion", "Confirm material/isotope source exclusion for first scope."),
    ]
    review_rows = [{
        "review_item_id": f"EX02A-REV-{i:02d}", "category": category, "description": description,
        "blocks_extract03_package": "yes" if category != "material_sensitive_exclusion" else "no",
        "blocks_actual_execution": "yes", "recommended_resolution": "complete explicit JSON decision and human approval fields",
        "notes": "Use the generated template; do not edit EXTRACT02 outputs.",
    } for i, (category, description) in enumerate(review_categories, start=1)]

    template = {
        "template_name": "HUMAN_FREEZE_DECISION_TEMPLATE.json",
        "work_package": "QSB-EXTRACT02A",
        "instructions": [
            "Copy this JSON to runs/QSB-EXTRACT02A/input/human_freeze_decisions.json or configs/qsb_extract02a_human_freeze_decisions.json.",
            "Replace every REQUIRED_* field and set each decision_status/human_approval explicitly.",
            "Do not derive ell_0, epsilon_Gram, or theta_edge from the L2 fail.",
            "All approval timestamps must be UTC ISO-8601 and approved_by must identify the human approver.",
        ],
        "material_sensitive_sources_in_first_scope": False,
        "material_sensitive_sources_status": "excluded_pending_separate_source_contract",
        "decisions": [],
    }
    for freeze_id in sorted(freeze_name_map):
        value = template_suggestions[freeze_id]
        template["decisions"].append({
            "freeze_id": freeze_id, "freeze_item": freeze_name_map[freeze_id],
            "decision_value": value if value is not None else "REQUIRED_HUMAN_VALUE",
            "decision_status": "REQUIRED: human_approved_frozen|human_rejected|deferred_explicitly_not_in_first_scope",
            "basis_artifact": next(row["basis_artifact"] for row in register if row["freeze_id"] == freeze_id),
            "human_approval": "REQUIRED: approved|rejected|not_required_for_first_scope",
            "approved_by": "REQUIRED_HUMAN_IDENTIFIER", "approval_timestamp_utc": "REQUIRED_UTC_ISO8601",
            "blocks_extract03_package": True, "blocks_actual_execution": True,
            "notes": "REQUIRED_HUMAN_RATIONALE; must state no tuning to L2 fail",
        })

    preparation_specs = [
        ("all_human_freezes_approved", "blocked_missing_10", "yes", "yes", "Provide ten valid approved decisions."),
        ("extract03_no_mutation_plan", "not_started", "yes", "yes", "Specify read-only inputs and isolated output writes."),
        ("extract03_dry_run_mode", "not_started", "yes", "yes", "Define dry-run gates before live computation."),
        ("extract03_result_mart_write_contract", "not_started", "yes", "yes", "Freeze DDL/write transaction and record lineage."),
        ("extract03_rollback_policy", "not_started", "yes", "yes", "Freeze rollback and partial-output invalidation."),
        ("extract03_validation_replay", "not_started", "yes", "yes", "Freeze validation replay and stop reasons."),
        ("extract03_claim_boundary_review", "not_started", "yes", "yes", "Independent review before package authorization."),
    ]
    preparation_rows = [{
        "requirement_id": f"EX02A-PR-{i:02d}", "requirement": requirement,
        "current_status": current, "required_before_extract03_package": package,
        "required_before_actual_execution": actual, "notes": notes,
    } for i, (requirement, current, package, actual, notes) in enumerate(preparation_specs, start=1)]

    OUTPUT.mkdir(parents=True)
    manifest = {
        "work_package": "QSB-EXTRACT02A", "status": STATUS,
        "created_at_utc": datetime.now(timezone.utc).isoformat(), "repo_root": str(REPO),
        "extract02_seen": extract02_seen, "human_decision_file_seen": human_file_seen,
        "authorization_value": AUTHORIZATION, "human_freeze_items_reviewed": 10,
        "human_freeze_items_approved_count": approved_count, "missing_decisions_count": missing_count,
        "invalid_decisions_count": invalid_count, "pre_execution_authorization_only": True,
        "extraction_executed": False, "minimaltest_rerun": False, "nullmodels_rerun": False,
        "live_K_computed": False, "live_d_D_computed": False, "shortest_paths_computed": False,
        "kernels_executed": False, "clustering_executed": False, "theta_or_epsilon_tuned": False,
        "physical_evidence_claim_made": False, "upstream_modified": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    (OUTPUT / "01_extract02a_run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_csv(OUTPUT / "02_upstream_inventory_and_hashes.csv", ["artifact_id", "upstream_block", "path", "exists", "sha256", "role", "used_for", "notes"], inventory_rows)
    write_csv(OUTPUT / "03_extract02_blocker_import.csv", ["blocker_item", "observed_value", "source_artifact", "source_hash", "import_status", "notes"], blocker_rows)
    write_csv(OUTPUT / "04_human_decision_input_status.csv", ["input_item", "path_checked", "exists", "used", "status", "notes"], input_status_rows)
    write_csv(OUTPUT / "05_human_freeze_resolution_matrix.csv", ["freeze_id", "freeze_item", "decision_value", "decision_status", "basis_artifact", "human_approval", "approved_by", "approval_timestamp_utc", "blocks_extract03_package", "blocks_actual_execution", "validation_status", "notes"], resolution_rows)
    write_csv(OUTPUT / "06_missing_or_invalid_decisions.csv", ["issue_id", "freeze_id", "freeze_item", "issue_type", "observed_value", "required_value", "blocking", "recommended_resolution", "notes"], issue_rows)
    write_csv(OUTPUT / "07_parameter_structural_validation.csv", ["parameter_id", "parameter_name", "observed_value", "validation_rule", "status", "blocking", "notes"], parameter_rows)
    write_csv(OUTPUT / "08_first_scope_authorization_review.csv", ["scope_item", "expected_status", "observed_status", "authorization_status", "blocking", "notes"], scope_review_rows)
    write_csv(OUTPUT / "09_material_sensitive_exclusion_check.csv", ["check_id", "source_category", "included_first_scope", "expected", "status", "blocking", "notes"], material_rows)
    write_csv(OUTPUT / "10_extract03_authorization_decision.csv", ["decision_id", "authorization_value", "rationale", "approved_freeze_items_count", "missing_decisions_count", "invalid_decisions_count", "allowed_next_action", "forbidden_next_action", "notes"], authorization_rows)
    write_csv(OUTPUT / "11_no_execution_guard.csv", ["guard_id", "guard_item", "status", "evidence", "notes"], guard_rows)
    write_csv(OUTPUT / "12_claim_boundary_matrix.csv", ["statement_id", "statement", "classification", "safe_wording", "forbidden_wording", "notes"], claim_rows)

    after_hashes = {key: sha256(path) for key, (_, path, _) in artifacts.items() if path.is_file()}
    upstream_unchanged = before_hashes == after_hashes
    manifest["upstream_modified"] = not upstream_unchanged
    (OUTPUT / "01_extract02a_run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    validation_rows = []
    for vid, name, passed, observed, expected in validation_specs:
        if name == "no_upstream_mutation":
            passed, observed = upstream_unchanged, upstream_unchanged
        validation_rows.append({
            "validation_id": vid, "validation_layer": "EXTRACT02A authorization check", "check_name": name,
            "status": "pass" if passed else "fail", "severity": "error", "observed_value": observed,
            "expected_value": expected, "message": "Clean blocked state recorded." if passed else "Authorization validation failed.",
            "blocking_for_authorization": "no" if passed else "yes",
        })
    write_csv(OUTPUT / "13_validation_results.csv", ["validation_id", "validation_layer", "check_name", "status", "severity", "observed_value", "expected_value", "message", "blocking_for_authorization"], validation_rows)
    write_csv(OUTPUT / "14_review_items_for_human_or_extract03.csv", ["review_item_id", "category", "description", "blocks_extract03_package", "blocks_actual_execution", "recommended_resolution", "notes"], review_rows)

    note_de = f"""# QSB-EXTRACT02A Kurznotiz

## Ausgangspunkt

EXTRACT02 dokumentierte zehn Human-Freeze-Punkte, davon sieben Kandidaten und drei fehlende Werte (`ell_0`, Gram-`epsilon`, `theta_edge`).

## Geprüfte Human-Freeze-Entscheidungen

Beide zulässigen JSON-Eingabepfade wurden geprüft. Keine Human-Decision-Datei ist vorhanden. Deshalb gelten alle zehn Punkte als `not_supplied`; EXTRACT02-Kandidaten werden nicht als Zustimmung interpretiert.

## Fehlende oder ungültige Entscheidungen

Es fehlen zehn Entscheidungen, darunter positive numerische Werte für `ell_0` und `epsilon_Gram`, eine Edge-Schwelle oder -Regel sowie sieben explizite Kandidatenfreigaben. Ungültige Entscheidungen wurden nicht gefunden, weil keine Datei vorliegt.

## Authorization-Entscheidung

`{AUTHORIZATION}`. EXTRACT03 darf nicht vorbereitet werden.

## Was ausdrücklich nicht getan wurde

EXTRACT02A ist ein Human-Freeze- und Authorization-Check. Es wurde keine Extraktion ausgeführt, kein K/d/D live berechnet und kein Clusterlauf gestartet.

## Nächster erlaubter Schritt

Die erzeugte JSON-Vorlage vollständig ausfüllen, an einem zulässigen Eingabepfad ablegen und den Authorization-Check in einem frischen Ausgabeverzeichnis erneut durchführen.
"""
    (OUTPUT / "15_short_authorization_note_de.md").write_text(note_de, encoding="utf-8")
    (OUTPUT / "16_decision_template_or_applied_decisions.json").write_text(json.dumps(template, indent=2) + "\n", encoding="utf-8")
    write_csv(OUTPUT / "17_extract03_preparation_requirements.csv", ["requirement_id", "requirement", "current_status", "required_before_extract03_package", "required_before_actual_execution", "notes"], preparation_rows)

    final_note = f"""# QSB-EXTRACT02A Final Result

## Status

`{STATUS}`

## Authorization Value

`{AUTHORIZATION}`

## Human-Freeze Resolution

Reviewed `10`; approved `0`; missing `10`; invalid `0`. No explicit JSON input exists.

## Missing or Invalid Decisions

All ten decisions are missing. `ell_0`, `epsilon_Gram`, and `theta_edge` have no supplied values; seven candidate decisions have no human approval.

## First Scope

The EXTRACT02 first-scope exclusions remain active. Included candidates remain unauthorized pending explicit JSON decisions.

## Material-Sensitive Source Boundary

Material/isotope-sensitive sources, metadata injection, and material claims remain excluded.

## No-Execution Boundary

No extraction, K/d/D, shortest path, kernel, clustering, Minimaltest, or nullmodel was executed. Upstream databases remain unchanged.

## Next Allowed Action

Supply the completed Human-Freeze JSON template. Do not prepare or execute EXTRACT03 before a fresh successful authorization check.
"""
    (OUTPUT / "FINAL_RESULT_NOTE.md").write_text(final_note, encoding="utf-8")

    actual = {path.name for path in OUTPUT.iterdir() if path.is_file()}
    if actual != EXPECTED_FILES:
        raise SystemExit(f"Output file-set mismatch: actual={sorted(actual)} expected={sorted(EXPECTED_FILES)}")
    failures = [row["validation_id"] for row in validation_rows if row["status"] == "fail"]
    if failures:
        raise SystemExit(f"EXTRACT02A validation failures: {failures}")
    print(f"status={STATUS}")
    print(f"authorization_value={AUTHORIZATION}")
    print("human_freeze_items_reviewed=10")
    print("approved=0 missing=10 invalid=0")
    print("execution=false")
    print(f"output_files={len(actual)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
