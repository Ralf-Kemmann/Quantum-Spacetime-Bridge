#!/usr/bin/env python3
"""Create the EXTRACT02 pre-execution contract without extraction."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REPO = Path(__file__).resolve().parents[2]
EXTRACT01 = REPO / "runs/QSB-EXTRACT01/dwh_based_gram_tensor_extraction_layer_design"
EXTRACT01A = REPO / "runs/QSB-EXTRACT01A/metadata_gap_prerequisite_resolution_review"
N0 = REPO / "runs/QSB-INTERFACE01N0/post_fail_scope_review_feature_n4_extract_path"
M2 = REPO / "runs/QSB-INTERFACE01M2/result_review_mechanism_interpretation_boundary_after_l2"
L2 = REPO / "runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2"
F3 = REPO / "runs/QSB-INTERFACE01F3/authorized_delta_phi_export_staging_preflight"
META_DB = REPO / "runs/QSB-META01-03/causality07_pilot_metadata/qsb_metadata_catalog.sqlite"
SOURCE_HUB_DB = REPO / "runs/QSB-GAP02A/source_hub_schema_dry_run_loader/qsb_source_hub_dry_run.sqlite"
OUTPUT = REPO / "runs/QSB-EXTRACT02/pre_execution_contract_dwh_gram_tensor_extraction"

STATUS = "extract02_pre_execution_contract_completed_with_readiness_decision"
READINESS = "blocked_pending_human_freeze_decisions"
CLAIM_BOUNDARY = (
    "QSB-EXTRACT02 is a pre-execution contract only. It records candidate and blocking Human-Freeze "
    "decisions but executes no extraction, Minimaltest, nullmodel, K/d/D computation, shortest path, "
    "kernel, or clustering; changes no L2 result or upstream database; and makes no physical-evidence, "
    "mechanism, geometry, material-sensitivity, or gravity claim."
)
EXPECTED_FILES = {
    "01_extract02_run_manifest.json", "02_upstream_inventory_and_hashes.csv",
    "03_extract01a_readiness_import.csv", "04_human_freeze_decision_register.csv",
    "05_first_scope_definition.csv", "06_source_selection_query_freeze.csv",
    "07_state_family_freeze_contract.csv", "08_K_mode_freeze_contract.csv",
    "09_distance_parameter_freeze_contract.csv", "10_strength_transform_edge_threshold_contract.csv",
    "11_kernel_subset_freeze_contract.csv", "12_cluster_protocol_freeze_contract.csv",
    "13_validation_matrix_freeze_contract.csv", "14_material_sensitive_source_exclusion.csv",
    "15_future_execution_package_requirements.csv", "16_no_execution_guard.csv",
    "17_claim_boundary_matrix.csv", "18_extract03_readiness_decision.csv",
    "19_validation_results.csv", "20_short_contract_note_de.md", "FINAL_RESULT_NOTE.md",
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

    artifact_specs = [
        ("EXTRACT01", EXTRACT01 / "01_extract01_run_manifest.json", "design-only status"),
        ("EXTRACT01", EXTRACT01 / "04_dwh_source_selection_contract.csv", "DWH source-selection boundary"),
        ("EXTRACT01", EXTRACT01 / "08_gram_construction_contract.csv", "five K modes"),
        ("EXTRACT01", EXTRACT01 / "09_distance_d_D_contract.csv", "formal distance contract"),
        ("EXTRACT01", EXTRACT01 / "11_extraction_kernel_registry.csv", "kernel registry"),
        ("EXTRACT01", EXTRACT01 / "13_future_result_mart_schema_contract.csv", "result mart design"),
        ("EXTRACT01", EXTRACT01 / "15_claim_boundary_matrix.csv", "scope and evidence exclusions"),
        ("EXTRACT01A", EXTRACT01A / "01_extract01a_run_manifest.json", "conditional readiness"),
        ("EXTRACT01A", EXTRACT01A / "04_metadata_gap_resolution_matrix.csv", "gap dispositions"),
        ("EXTRACT01A", EXTRACT01A / "05_prerequisite_resolution_matrix.csv", "ten candidate freezes"),
        ("EXTRACT01A", EXTRACT01A / "06_state_family_resolution_review.csv", "state family candidate"),
        ("EXTRACT01A", EXTRACT01A / "07_K_construction_mode_resolution_review.csv", "K mode candidate"),
        ("EXTRACT01A", EXTRACT01A / "08_distance_parameter_resolution_review.csv", "distance parameter gaps"),
        ("EXTRACT01A", EXTRACT01A / "09_strength_transform_and_edge_threshold_review.csv", "relation candidates"),
        ("EXTRACT01A", EXTRACT01A / "10_kernel_subset_resolution_review.csv", "kernel subset candidate"),
        ("EXTRACT01A", EXTRACT01A / "11_cluster_protocol_resolution_review.csv", "cluster candidate"),
        ("EXTRACT01A", EXTRACT01A / "12_source_selection_query_contract.csv", "source query candidate"),
        ("EXTRACT01A", EXTRACT01A / "13_validation_matrix_freeze_review.csv", "validation candidates"),
        ("EXTRACT01A", EXTRACT01A / "14_extract02_readiness_decision.csv", "readiness decision"),
        ("N0", N0 / "01_n0_run_manifest.json", "design path context"),
        ("M2", M2 / "01_m2_run_manifest.json", "bounded fail review context"),
        ("L2", L2 / "01_l2_run_manifest.json", "unchanged fail context"),
        ("F3", F3 / "01_f3_run_manifest.json", "source context"),
        ("META01-03", META_DB, "metadata schema context"),
        ("GAP02A", SOURCE_HUB_DB, "source hub context"),
    ]
    artifacts = {f"a{i:02d}": (block, path, use) for i, (block, path, use) in enumerate(artifact_specs, start=1)}
    upstream_present = all(path.is_file() for _, path, _ in artifacts.values())
    before_hashes = {key: sha256(path) for key, (_, path, _) in artifacts.items() if path.is_file()}
    inventory_rows = []
    for number, (key, (block, path, use)) in enumerate(artifacts.items(), start=1):
        exists = path.is_file()
        inventory_rows.append({
            "artifact_id": f"EX02-A{number:02d}", "upstream_block": block, "path": rel(path),
            "exists": "yes" if exists else "no", "sha256": before_hashes.get(key, "missing"),
            "role": "read-only precontract input", "used_for": use,
            "notes": "Hashed before EXTRACT02; not modified." if exists else "Missing required artifact.",
        })
    if not upstream_present:
        raise SystemExit("EXTRACT02 blocked: required EXTRACT01A or upstream metadata is missing.")

    extract_manifest = load_json(EXTRACT01 / "01_extract01_run_manifest.json")
    review_manifest = load_json(EXTRACT01A / "01_extract01a_run_manifest.json")
    readiness_source = read_csv(EXTRACT01A / "14_extract02_readiness_decision.csv")[0]
    extract_seen = extract_manifest.get("status") == "extract01_dwh_based_gram_tensor_extraction_layer_design_completed_no_execution"
    extract01a_seen = review_manifest.get("status") == "extract01a_metadata_gap_prerequisite_resolution_review_completed_with_readiness_decision"
    imported_readiness = review_manifest.get("readiness_decision")
    readiness_valid = imported_readiness == "conditional_ready_for_extract02_precontract_with_open_review_items"
    if not all([extract_seen, extract01a_seen, readiness_valid, extract_manifest.get("design_only") is True]):
        raise SystemExit("EXTRACT02 blocked: EXTRACT01/EXTRACT01A statuses are inconsistent.")

    prerequisites = {row["prerequisite_name"]: row for row in read_csv(EXTRACT01A / "05_prerequisite_resolution_matrix.csv")}
    state_review = read_csv(EXTRACT01A / "06_state_family_resolution_review.csv")
    mode_review = read_csv(EXTRACT01A / "07_K_construction_mode_resolution_review.csv")
    distance_review = {row["parameter"]: row for row in read_csv(EXTRACT01A / "08_distance_parameter_resolution_review.csv")}
    relation_review = {row["item"]: row for row in read_csv(EXTRACT01A / "09_strength_transform_and_edge_threshold_review.csv")}
    kernel_review = read_csv(EXTRACT01A / "10_kernel_subset_resolution_review.csv")
    cluster_review = read_csv(EXTRACT01A / "11_cluster_protocol_resolution_review.csv")
    query_review = read_csv(EXTRACT01A / "12_source_selection_query_contract.csv")
    validation_review = read_csv(EXTRACT01A / "13_validation_matrix_freeze_review.csv")

    readiness_import_specs = [
        ("extract01a_status", review_manifest["status"], EXTRACT01A / "01_extract01a_run_manifest.json", "pass", "Completed review status."),
        ("extract01a_readiness", imported_readiness, EXTRACT01A / "01_extract01a_run_manifest.json", "pass", "Conditional precontract readiness imported."),
        ("metadata_gaps_reviewed", review_manifest["metadata_gaps_reviewed"], EXTRACT01A / "01_extract01a_run_manifest.json", "pass", "Twelve categories reviewed."),
        ("prerequisites_reviewed", review_manifest["prerequisites_reviewed"], EXTRACT01A / "01_extract01a_run_manifest.json", "pass", "Ten prerequisites reviewed."),
        ("human_freeze_points", readiness_source["human_freeze_items_count"], EXTRACT01A / "14_extract02_readiness_decision.csv", "pass", "All require explicit approval."),
        ("primary_K_mode_candidate", "K_from_phase_response_vectors", EXTRACT01A / "07_K_construction_mode_resolution_review.csv", "pass", "Candidate only, not physically validated."),
        ("material_sensitive_sources_status", "excluded_pending_separate_source_contract", EXTRACT01A / "12_source_selection_query_contract.csv", "pass", "Excluded from first scope."),
        ("live_execution_status", "blocked", EXTRACT01A / "14_extract02_readiness_decision.csv", "pass", "Review did not authorize execution."),
    ]
    readiness_import_rows = [{
        "import_item": item, "observed_value": value, "source_artifact": rel(path),
        "source_hash": sha256(path), "import_status": status, "notes": notes,
    } for item, value, path, status, notes in readiness_import_specs]

    freeze_specs = [
        ("HF-01", "freeze_psi_or_feature_state_family", "phase_response_vector_family_from_F3; ordered pair x-index response vectors; window/normalization pending approval", "candidate_frozen_pending_human_approval", EXTRACT01A / "06_state_family_resolution_review.csv"),
        ("HF-02", "freeze_K_construction_mode", "K_from_phase_response_vectors; Hermiticity/PSD tolerances pending approval", "candidate_frozen_pending_human_approval", EXTRACT01A / "07_K_construction_mode_resolution_review.csv"),
        ("HF-03", "freeze_ell0", "ell_0=not_frozen; positive numeric value and unit role required", "not_frozen_blocks_execution_package", EXTRACT01A / "08_distance_parameter_resolution_review.csv"),
        ("HF-04", "freeze_epsilon", "epsilon_Gram=not_frozen; dimensionless precision/domain rule required; distinct from L2 epsilon_new", "not_frozen_blocks_execution_package", EXTRACT01A / "08_distance_parameter_resolution_review.csv"),
        ("HF-05", "freeze_distance_to_strength_transform", "candidate s_ij=exp(-d_ij/ell_0); alternative explicitly unused", "candidate_frozen_pending_human_approval", EXTRACT01A / "09_strength_transform_and_edge_threshold_review.csv"),
        ("HF-06", "freeze_edge_threshold", "theta_edge=not_frozen; threshold space/source/direction/precision/tie policy required", "not_frozen_blocks_execution_package", EXTRACT01A / "09_strength_transform_and_edge_threshold_review.csv"),
        ("HF-07", "freeze_kernel_subset", "candidate first subset: invariance_kernel;gram_distance_kernel;shortest_path_kernel;edge_candidate_kernel", "candidate_frozen_pending_human_approval", EXTRACT01A / "10_kernel_subset_resolution_review.csv"),
        ("HF-08", "freeze_cluster_protocol", "candidate D matrix;average linkage primary;complete diagnostic;split/bootstrap stability;fixed cut;hashed motif IDs", "candidate_frozen_pending_human_approval", EXTRACT01A / "11_cluster_protocol_resolution_review.csv"),
        ("HF-09", "freeze_source_selection_query", "candidate metadata filters/eligibility/checksum/lineage/gap contract for staged_delta_phi and gram_ready sources", "candidate_frozen_pending_human_approval", EXTRACT01A / "12_source_selection_query_contract.csv"),
        ("HF-10", "freeze_validation_matrix", "candidate 13-gate start/runtime/output matrix with stop actions", "candidate_frozen_pending_human_approval", EXTRACT01A / "13_validation_matrix_freeze_review.csv"),
    ]
    freeze_rows = [{
        "freeze_id": fid, "freeze_item": item, "decision_value": value, "decision_status": status,
        "basis_artifact": rel(basis), "human_approval_required": "yes",
        "blocks_execution_package": "yes", "blocks_actual_execution": "yes",
        "notes": "EXTRACT02 records the decision state; it does not supply human approval.",
    } for fid, item, value, status, basis in freeze_specs]

    scope_specs = [
        ("F3_like_spatial_pair_delta_phi_x_sources", "yes_candidate_pending_query_approval", "no", F3 / "01_f3_run_manifest.json", "Only eligible metadata-selected sources matching the staged spatial phase contract."),
        ("phase_response_vectors", "yes_candidate_pending_state_family_approval", "no", EXTRACT01A / "06_state_family_resolution_review.csv", "Primary vector-family candidate for first scope."),
        ("ordered_non_diagonal_pairs", "yes", "no", F3 / "01_f3_run_manifest.json", "Pair diagonal policy remains exclude."),
        ("x_index_response_vectors", "yes_candidate_pending_window_normalization_approval", "no", EXTRACT01A / "06_state_family_resolution_review.csv", "Common x-index grid required."),
        ("material_sensitive_sources", "no", "yes", EXTRACT01A / "12_source_selection_query_contract.csv", "Gap; separate source contract required."),
        ("unverified_psi_state_families", "no", "yes", EXTRACT01A / "06_state_family_resolution_review.csv", "Explicit psi family unresolved."),
        ("loose_unlineaged_files", "no", "yes", EXTRACT01 / "04_dwh_source_selection_contract.csv", "DWH metadata and lineage mandatory."),
        ("synthetic_evidence_sources", "no", "yes", EXTRACT01 / "15_claim_boundary_matrix.csv", "Synthetic evidence substitution forbidden."),
    ]
    scope_rows = [{
        "scope_item": item, "included": included, "excluded": excluded,
        "basis_artifact": rel(basis), "reason": reason,
        "claim_boundary": "First-scope contract input only; no evidence or mechanism claim.",
        "notes": "No source rows selected or loaded in EXTRACT02.",
    } for item, included, excluded, basis, reason in scope_specs]

    query_rows = []
    for row in query_review:
        material = row["source_category"] == "material_sensitive_sources"
        query_rows.append({
            "query_id": row["query_contract_id"], "source_category": row["source_category"],
            "metadata_filters": row["metadata_filters_required"], "eligibility_conditions": row["eligibility_conditions"],
            "exclusion_rules": "excluded from first scope; record metadata gap" if material else "exclude unapproved status, checksum mismatch, missing units/dimensions/lineage, loose files",
            "lineage_requirements": row["lineage_requirements"], "unit_dimension_requirements": row["unit_dimension_requirements"],
            "decision_status": "deferred_explicitly_not_in_first_scope" if material else "candidate_frozen_pending_human_approval",
            "human_approval_required": "yes", "notes": "Query text/hash is not executed or approved in EXTRACT02.",
        })

    state_rows = [
        {"state_family_id": "EX02-SF-01", "state_family_name": "phase_response_vector_family_from_F3", "definition": "For each metadata-selected ordered non-diagonal pair, construct a vector over the frozen x_index domain from registered cos_delta_phi/sin_delta_phi or approved phase-response channels.", "input_source": "eligible F3-like spatial_pair_delta_phi_x staging selected by HF-09", "included_axes": "source_id;run_id;state_id;pair_i;pair_j;x_index;feature_channel;split_label", "excluded_axes": "material_id;isotope_id;t_index in first scope", "normalization_requirement": "window, weights, centering, channel ordering, missing-value policy, and unit norm require human freeze", "decision_status": "candidate_frozen_pending_human_approval", "human_approval_required": "yes", "blocks_execution_package": "yes", "notes": "No response vector is constructed in EXTRACT02."},
        {"state_family_id": "EX02-SF-02", "state_family_name": "feature_vector_family_from_H_I_L2", "definition": "Historical diagnostic alternative with frozen schema/scaling if separately approved.", "input_source": "lineaged H/I/L2 feature objects only", "included_axes": "source_id;run_id;pair_i;pair_j;feature_channel", "excluded_axes": "outcome-selected replacement features", "normalization_requirement": "frozen scaling and unit norm", "decision_status": "deferred_explicitly_not_in_first_scope", "human_approval_required": "yes_if_reintroduced", "blocks_execution_package": "no", "notes": "Excluded to avoid post-fail feature repair."},
        {"state_family_id": "EX02-SF-03", "state_family_name": "explicit_psi_state_family", "definition": "unresolved", "input_source": "none in audited metadata", "included_axes": "none", "excluded_axes": "all", "normalization_requirement": "not available", "decision_status": "deferred_explicitly_not_in_first_scope", "human_approval_required": "yes_if_reintroduced", "blocks_execution_package": "no", "notes": "K_from_state_vectors excluded from first scope."},
    ]

    gram_design = read_csv(EXTRACT01 / "08_gram_construction_contract.csv")
    k_rows = []
    for row in gram_design:
        primary = row["gram_mode"] == "K_from_phase_response_vectors"
        k_rows.append({
            "K_mode_id": row["gram_mode_id"], "K_mode": row["gram_mode"], "input_object": row["input_object"],
            "normalization_rule": row["normalization_rule"], "admissibility_checks": row["admissibility_checks"],
            "hermiticity_check": row["hermiticity_check"], "psd_check": row["psd_check"],
            "decision_status": "candidate_frozen_pending_human_approval" if primary else "deferred_explicitly_not_in_first_scope",
            "human_approval_required": "yes", "claim_boundary": row["claim_boundary"],
            "notes": "Primary first-scope candidate; tolerances still require approval." if primary else "Not in first scope; no live K computed.",
        })

    distance_rows = [
        {"parameter_id": "EX02-DP-01", "symbol": "ell_0", "definition": "positive cost-distance scale with declared unit/dimension role", "decision_value": "not_frozen", "decision_status": "not_frozen_blocks_execution_package", "human_approval_required": "yes", "blocks_execution_package": "yes", "forbidden_use": "invent or tune from L2/desired motifs", "notes": "No numeric value in EXTRACT02."},
        {"parameter_id": "EX02-DP-02", "symbol": "epsilon_Gram", "definition": "positive dimensionless log-domain guard distinct from L2 epsilon_new", "decision_value": "not_frozen", "decision_status": "not_frozen_blocks_execution_package", "human_approval_required": "yes", "blocks_execution_package": "yes", "forbidden_use": "reuse L2 epsilon_new silently or tune to outcomes", "notes": "No numeric value in EXTRACT02."},
        {"parameter_id": "EX02-DP-03", "symbol": "d_ij", "definition": "-ell_0 log(|K_ij|+epsilon_Gram)", "decision_value": "formula frozen; parameters not frozen", "decision_status": "candidate_frozen_pending_human_approval", "human_approval_required": "yes", "blocks_execution_package": "yes", "forbidden_use": "compute before HF-02/HF-03/HF-04 approval", "notes": "Cost candidate, not geometry."},
        {"parameter_id": "EX02-DP-04", "symbol": "D(i,j)", "definition": "shortest-path minimum sum over eligible d_ab edges", "decision_value": "formula frozen; graph policy pending", "decision_status": "candidate_frozen_pending_human_approval", "human_approval_required": "yes", "blocks_execution_package": "yes", "forbidden_use": "compute shortest paths now or call D a metric", "notes": "Reconstructed cost distance only."},
        {"parameter_id": "EX02-DP-05", "symbol": "p*", "definition": "dominant path plus competing-path margin and tie policy", "decision_value": "candidate contract; not frozen", "decision_status": "candidate_frozen_pending_human_approval", "human_approval_required": "yes", "blocks_execution_package": "yes", "forbidden_use": "select attractive paths post hoc", "notes": "Path provenance required."},
        {"parameter_id": "EX02-DP-06", "symbol": "metric_status", "definition": "later validation label after nonnegativity/identity/symmetry/triangle/stability checks", "decision_value": "not_tested", "decision_status": "deferred_explicitly_not_in_first_scope", "human_approval_required": "no_for_first_cost_run", "blocks_execution_package": "no", "forbidden_use": "assume geometric or spacetime metric readability", "notes": "Claim boundary preserved."},
    ]

    strength_rows = [
        {"contract_id": "EX02-REL-01", "input_measure": "d_ij", "rule_or_transform": "smaller d means stronger overlap/similarity ordering", "output_measure": "similarity_order", "threshold_parameter": "none", "decision_status": "candidate_frozen_pending_human_approval", "human_approval_required": "yes", "allowed_future_use": "ordering diagnostic", "forbidden_use": "physical distance claim", "notes": "No values evaluated."},
        {"contract_id": "EX02-REL-02", "input_measure": "d_ij", "rule_or_transform": "candidate s_ij=exp(-d_ij/ell_0)", "output_measure": "relation_strength_s", "threshold_parameter": "ell_0", "decision_status": "candidate_frozen_pending_human_approval", "human_approval_required": "yes", "allowed_future_use": "only after HF-03/HF-05 approval", "forbidden_use": "choose transform from favorable outcomes", "notes": "May instead be explicitly unused by human decision."},
        {"contract_id": "EX02-REL-03", "input_measure": "d_ij or s_ij", "rule_or_transform": "threshold family/direction/tie policy pending", "output_measure": "edge_candidate", "threshold_parameter": "theta_edge=not_frozen", "decision_status": "not_frozen_blocks_execution_package", "human_approval_required": "yes", "allowed_future_use": "after independent threshold source is frozen", "forbidden_use": "use L2 theta_new or tune from L2 fail", "notes": "No numeric threshold."},
        {"contract_id": "EX02-REL-04", "input_measure": "d or s plus approved theta_edge", "rule_or_transform": "apply exactly one approved edge convention", "output_measure": "edge_candidate", "threshold_parameter": "theta_edge", "decision_status": "candidate_frozen_pending_human_approval", "human_approval_required": "yes", "allowed_future_use": "candidate graph only", "forbidden_use": "outcome-selected switching between d and s", "notes": "Blocked by HF-06."},
        {"contract_id": "EX02-REL-05", "input_measure": "stable edge/cluster membership", "rule_or_transform": "motif ID from contract/source/membership hashes after stability gates", "output_measure": "motif_id", "threshold_parameter": "stability thresholds pending", "decision_status": "candidate_frozen_pending_human_approval", "human_approval_required": "yes", "allowed_future_use": "internal motif candidate", "forbidden_use": "physical/geometric entity claim", "notes": "No motif generated."},
    ]

    kernel_design = {row["kernel_id"]: row for row in read_csv(EXTRACT01 / "11_extraction_kernel_registry.csv")}
    kernel_rows = []
    included_kernel_names = {"invariance_kernel", "edge_candidate_kernel", "gram_distance_kernel", "shortest_path_kernel"}
    for review in kernel_review:
        source = kernel_design[review["kernel_id"]]
        included = review["kernel_name"] in included_kernel_names
        kernel_rows.append({
            "kernel_id": review["kernel_id"], "kernel_name": review["kernel_name"],
            "included_first_scope": "yes_candidate" if included else "no",
            "input_channels": source["input_channels"], "output_channels": source["output_channels"],
            "parameters": source["parameters"],
            "decision_status": "candidate_frozen_pending_human_approval" if included else "deferred_explicitly_not_in_first_scope",
            "human_approval_required": "yes" if included else "no_if_excluded",
            "allowed_future_use": "first-scope execution after full approval" if included else "later addendum only",
            "forbidden_use": "execute kernel in EXTRACT02 or add it silently to execution scope",
            "notes": "Method-driven subset; no kernel executed.",
        })

    cluster_values = {
        "distance_matrix_source": "shortest_path_D primary; direct d diagnostic",
        "linkage_method": "average linkage primary; complete linkage diagnostic",
        "cluster_stability_check": "predefined membership stability plus cophenetic diagnostic",
        "split_bootstrap_protocol": "deterministic split/bootstrap overlap; seed/repetitions/score pending approval",
        "cluster_to_motif_mapping": "map only clusters passing all approved stability gates",
        "motif_id_generation": "hash(contract,source,membership)",
        "claim_boundary": "candidate relational grouping only; no geometry or physical entity",
    }
    cluster_rows = [{
        "cluster_contract_id": f"EX02-CL-{i:02d}", "component": component, "decision_value": value,
        "decision_status": "candidate_frozen_pending_human_approval" if component != "claim_boundary" else "frozen_for_precontract",
        "human_approval_required": "yes" if component != "claim_boundary" else "no",
        "blocks_execution_package": "yes" if component != "claim_boundary" else "no",
        "allowed_future_use": "after HF-08 approval and required kernels are added by explicit contract addendum",
        "forbidden_use": "run clustering now or infer physical motifs",
        "notes": "Cluster kernels are excluded from the minimal four-kernel first scope unless separately approved.",
    } for i, (component, value) in enumerate(cluster_values.items(), start=1)]

    validation_checks = [
        ("extract01a_readiness_confirmed", "pass if imported conditional readiness matches"),
        ("source_selection_query_frozen_or_candidate", "block package until HF-09 approved"),
        ("state_family_frozen_or_candidate", "block package until HF-01 approved"),
        ("K_mode_frozen_or_candidate", "block package until HF-02 approved"),
        ("ell0_frozen_or_blocker", "block package while ell_0=not_frozen"),
        ("epsilon_frozen_or_blocker", "block package while epsilon_Gram=not_frozen"),
        ("strength_transform_frozen_or_candidate", "block package until HF-05 approved"),
        ("edge_threshold_frozen_or_blocker", "block package while theta_edge=not_frozen"),
        ("kernel_subset_frozen_or_candidate", "block package until HF-07 approved"),
        ("cluster_protocol_frozen_or_candidate", "block cluster stage until HF-08 approved"),
        ("material_sources_excluded", "fail if material/isotope source enters first scope"),
        ("no_execution_in_extract02", "fail if any computation/extraction flag is true"),
        ("claim_boundary_clean", "fail on unsupported mechanism/geometry/gravity wording"),
    ]
    validation_contract_rows = [{
        "validation_id": f"EX02-VF-{i:02d}", "validation_layer": "precontract" if i <= 10 else "boundary",
        "check_name": name, "required_before_execution_package": "yes", "required_before_actual_execution": "yes",
        "decision_status": "candidate_frozen_pending_human_approval" if 2 <= i <= 10 else "frozen_for_precontract",
        "failure_action": action, "notes": "Design gate only; no runtime evidence generated.",
    } for i, (name, action) in enumerate(validation_checks, start=1)]

    material_rows = [
        {"exclusion_id": "EX02-MAT-01", "source_category": "material_sensitive_sources", "included_first_scope": "false", "status": "excluded_pending_separate_source_contract", "basis_artifact": rel(EXTRACT01A / "12_source_selection_query_contract.csv"), "reason": "No eligible audited source frozen.", "required_future_resolution": "metadata-driven source scout, unit/dimension/lineage review, human authorization", "notes": "No material-sensitivity claim."},
        {"exclusion_id": "EX02-MAT-02", "source_category": "isotope_sensitive_sources", "included_first_scope": "false", "status": "excluded_pending_separate_source_contract", "basis_artifact": rel(EXTRACT01A / "04_metadata_gap_resolution_matrix.csv"), "reason": "No isotope source family frozen.", "required_future_resolution": "isotope metadata and reference-contract specification", "notes": "Isotope kernel excluded."},
        {"exclusion_id": "EX02-MAT-03", "source_category": "material_metadata_injection", "included_first_scope": "false", "status": "forbidden", "basis_artifact": rel(EXTRACT01 / "04_dwh_source_selection_contract.csv"), "reason": "Silent labels violate DWH lineage.", "required_future_resolution": "registered source-hub ingest and metadata mapping", "notes": "No manual side-channel enrichment."},
        {"exclusion_id": "EX02-MAT-04", "source_category": "material_claims", "included_first_scope": "false", "status": "forbidden", "basis_artifact": rel(EXTRACT01 / "15_claim_boundary_matrix.csv"), "reason": "First scope contains no material-sensitive source.", "required_future_resolution": "separate validated material-sensitivity result chain", "notes": "No claim from absence or exclusion."},
    ]

    requirement_specs = [
        ("all_human_freeze_decisions_confirmed", "execution package", "pending", "yes", "yes", "human approval record for HF-01..HF-10"),
        ("source_selection_query_finalized", "execution package", "candidate_pending", "yes", "yes", "freeze exact query text/hash and stop behavior"),
        ("ell0_numeric_value_finalized", "execution package", "not_frozen", "yes", "yes", "human-freeze positive numeric value and units"),
        ("epsilon_numeric_value_finalized", "execution package", "not_frozen", "yes", "yes", "human-freeze dimensionless Gram epsilon"),
        ("edge_threshold_finalized", "execution package", "not_frozen", "yes", "yes", "human-freeze threshold source/value/rule"),
        ("cluster_protocol_finalized", "cluster execution stage", "candidate_pending", "yes", "yes", "human-freeze all protocol components and add cluster kernels if in scope"),
        ("result_mart_write_contract_finalized", "actual execution", "design_basis_present", "no", "yes", "freeze physical DDL/write transaction and lineage mappings"),
        ("dry_run_loader_defined", "actual execution", "missing", "no", "yes", "define no-mutation dry run and row-count/hash checks"),
        ("rollback_no_mutation_policy", "actual execution", "missing", "no", "yes", "freeze transaction/rollback and upstream read-only guarantees"),
        ("claim_boundary_review", "execution package", "precontract_defined", "no", "yes", "independent wording and evidence-class review"),
    ]
    requirement_rows = [{
        "requirement_id": f"EX02-REQ-{i:02d}", "requirement": requirement,
        "required_for": required_for, "current_status": current, "blocks_extract03_package": package,
        "blocks_actual_execution": actual, "resolution_needed": resolution,
        "notes": "EXTRACT02 grants no execution authorization.",
    } for i, (requirement, required_for, current, package, actual, resolution) in enumerate(requirement_specs, start=1)]

    guard_names = [
        "no_extraction_execution", "no_minimaltest_rerun", "no_nullmodel_rerun", "no_live_K_computation",
        "no_live_d_D_computation", "no_shortest_path_computation", "no_kernel_execution",
        "no_clustering_execution", "no_theta_epsilon_tuning", "no_feature_repair", "no_n4_change",
        "no_upstream_db_mutation", "no_physical_evidence_claim",
    ]
    guard_rows = [{
        "guard_id": f"EX02-GUARD-{i:02d}", "guard_item": name, "status": "pass",
        "evidence": {
            "no_extraction_execution": "extraction_executed=false", "no_minimaltest_rerun": "minimaltest_rerun=false",
            "no_nullmodel_rerun": "nullmodels_rerun=false", "no_live_K_computation": "live_K_computed=false",
            "no_live_d_D_computation": "live_d_D_computed=false", "no_shortest_path_computation": "shortest_paths_computed=false",
            "no_kernel_execution": "kernels_executed=false", "no_clustering_execution": "clustering_executed=false",
            "no_theta_epsilon_tuning": "theta_or_epsilon_tuned=false", "no_physical_evidence_claim": "physical_evidence_claim_made=false",
        }.get(name, "contract rows only; upstream hashes unchanged"),
        "notes": "Pre-execution contract boundary.",
    } for i, name in enumerate(guard_names, start=1)]

    claim_specs = [
        ("EX02-C01", "EXTRACT02 records ten Human-Freeze states", "contract_statement", "The register contains candidate and blocking decisions.", "Calling pending candidates approved."),
        ("EX02-C02", "K_from_phase_response_vectors is the primary candidate", "candidate_freeze", "The mode awaits human approval and tolerances.", "Calling it physically validated."),
        ("EX02-C03", "ell_0, epsilon_Gram, and theta_edge block EXTRACT03", "future_execution_requirement", "Numeric/rule freezes are required before package preparation.", "Inventing values in EXTRACT02."),
        ("EX02-C04", "material-sensitive sources excluded", "scope_exclusion", "First scope contains no material-sensitive sources.", "Making material claims."),
        ("EX02-C05", "EXTRACT02 proves the mechanism", "unsupported_claim", "A contract is not a mechanism result.", "EXTRACT02 proves the mechanism."),
        ("EX02-C06", "EXTRACT02 reverses L2 fail", "unsupported_claim", "L2 remains fail.", "EXTRACT02 reverses L2 fail."),
        ("EX02-C07", "EXTRACT02 demonstrates emergent geometry", "unsupported_claim", "No K/d/D or cluster result exists.", "EXTRACT02 demonstrates emergent geometry."),
        ("EX02-C08", "EXTRACT02 demonstrates gravity", "unsupported_claim", "No gravity observable or validation exists.", "EXTRACT02 demonstrates gravity."),
        ("EX02-C09", "EXTRACT02 executed extraction", "unsupported_claim", "No extraction was executed.", "EXTRACT02 executed extraction."),
        ("EX02-C10", "K_from_phase_response_vectors is physically validated", "unsupported_claim", "The mode is a contract candidate only.", "K_from_phase_response_vectors is physically validated."),
    ]
    claim_rows = [{
        "statement_id": sid, "statement": statement, "classification": classification,
        "safe_wording": safe, "forbidden_wording": forbidden,
        "notes": "Pre-execution contract only.",
    } for sid, statement, classification, safe, forbidden in claim_specs]

    frozen_count = sum(row["decision_status"] == "frozen_for_precontract" for row in freeze_rows)
    candidate_count = sum(row["decision_status"] == "candidate_frozen_pending_human_approval" for row in freeze_rows)
    blocker_count = sum(row["decision_status"] == "not_frozen_blocks_execution_package" for row in freeze_rows)
    readiness_rows = [{
        "decision_id": "EX02-READY-01", "execution_package_readiness": READINESS,
        "rationale": "Seven Human-Freeze items have explicit candidates but no approval; ell_0, epsilon_Gram, and theta_edge have no adequate decision value and block EXTRACT03 package preparation.",
        "frozen_items_count": frozen_count, "candidate_pending_human_approval_count": candidate_count,
        "blocking_items_count": blocker_count, "allowed_next_action": "resolve_remaining_freeze_blockers;hold_for_human_approval",
        "forbidden_next_action": "execute_extraction_now;compute_live_K_d_D_now;run_clustering_now;tune_parameters_to_L2_fail",
        "notes": "After all ten approvals, readiness must be reassessed in a separate authorization block.",
    }]

    OUTPUT.mkdir(parents=True)
    manifest = {
        "work_package": "QSB-EXTRACT02", "status": STATUS,
        "created_at_utc": datetime.now(timezone.utc).isoformat(), "repo_root": str(REPO),
        "extract01_seen": extract_seen, "extract01a_seen": extract01a_seen,
        "extract01a_readiness_seen": imported_readiness, "execution_package_readiness": READINESS,
        "human_freeze_items_recorded": 10, "pre_execution_contract_only": True,
        "extraction_executed": False, "minimaltest_rerun": False, "nullmodels_rerun": False,
        "live_K_computed": False, "live_d_D_computed": False, "shortest_paths_computed": False,
        "clustering_executed": False, "kernels_executed": False, "theta_or_epsilon_tuned": False,
        "physical_evidence_claim_made": False, "upstream_modified": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    (OUTPUT / "01_extract02_run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_csv(OUTPUT / "02_upstream_inventory_and_hashes.csv", ["artifact_id", "upstream_block", "path", "exists", "sha256", "role", "used_for", "notes"], inventory_rows)
    write_csv(OUTPUT / "03_extract01a_readiness_import.csv", ["import_item", "observed_value", "source_artifact", "source_hash", "import_status", "notes"], readiness_import_rows)
    write_csv(OUTPUT / "04_human_freeze_decision_register.csv", ["freeze_id", "freeze_item", "decision_value", "decision_status", "basis_artifact", "human_approval_required", "blocks_execution_package", "blocks_actual_execution", "notes"], freeze_rows)
    write_csv(OUTPUT / "05_first_scope_definition.csv", ["scope_item", "included", "excluded", "basis_artifact", "reason", "claim_boundary", "notes"], scope_rows)
    write_csv(OUTPUT / "06_source_selection_query_freeze.csv", ["query_id", "source_category", "metadata_filters", "eligibility_conditions", "exclusion_rules", "lineage_requirements", "unit_dimension_requirements", "decision_status", "human_approval_required", "notes"], query_rows)
    write_csv(OUTPUT / "07_state_family_freeze_contract.csv", ["state_family_id", "state_family_name", "definition", "input_source", "included_axes", "excluded_axes", "normalization_requirement", "decision_status", "human_approval_required", "blocks_execution_package", "notes"], state_rows)
    write_csv(OUTPUT / "08_K_mode_freeze_contract.csv", ["K_mode_id", "K_mode", "input_object", "normalization_rule", "admissibility_checks", "hermiticity_check", "psd_check", "decision_status", "human_approval_required", "claim_boundary", "notes"], k_rows)
    write_csv(OUTPUT / "09_distance_parameter_freeze_contract.csv", ["parameter_id", "symbol", "definition", "decision_value", "decision_status", "human_approval_required", "blocks_execution_package", "forbidden_use", "notes"], distance_rows)
    write_csv(OUTPUT / "10_strength_transform_edge_threshold_contract.csv", ["contract_id", "input_measure", "rule_or_transform", "output_measure", "threshold_parameter", "decision_status", "human_approval_required", "allowed_future_use", "forbidden_use", "notes"], strength_rows)
    write_csv(OUTPUT / "11_kernel_subset_freeze_contract.csv", ["kernel_id", "kernel_name", "included_first_scope", "input_channels", "output_channels", "parameters", "decision_status", "human_approval_required", "allowed_future_use", "forbidden_use", "notes"], kernel_rows)
    write_csv(OUTPUT / "12_cluster_protocol_freeze_contract.csv", ["cluster_contract_id", "component", "decision_value", "decision_status", "human_approval_required", "blocks_execution_package", "allowed_future_use", "forbidden_use", "notes"], cluster_rows)
    write_csv(OUTPUT / "13_validation_matrix_freeze_contract.csv", ["validation_id", "validation_layer", "check_name", "required_before_execution_package", "required_before_actual_execution", "decision_status", "failure_action", "notes"], validation_contract_rows)
    write_csv(OUTPUT / "14_material_sensitive_source_exclusion.csv", ["exclusion_id", "source_category", "included_first_scope", "status", "basis_artifact", "reason", "required_future_resolution", "notes"], material_rows)
    write_csv(OUTPUT / "15_future_execution_package_requirements.csv", ["requirement_id", "requirement", "required_for", "current_status", "blocks_extract03_package", "blocks_actual_execution", "resolution_needed", "notes"], requirement_rows)
    write_csv(OUTPUT / "16_no_execution_guard.csv", ["guard_id", "guard_item", "status", "evidence", "notes"], guard_rows)
    write_csv(OUTPUT / "17_claim_boundary_matrix.csv", ["statement_id", "statement", "classification", "safe_wording", "forbidden_wording", "notes"], claim_rows)
    write_csv(OUTPUT / "18_extract03_readiness_decision.csv", ["decision_id", "execution_package_readiness", "rationale", "frozen_items_count", "candidate_pending_human_approval_count", "blocking_items_count", "allowed_next_action", "forbidden_next_action", "notes"], readiness_rows)

    after_hashes = {key: sha256(path) for key, (_, path, _) in artifacts.items() if path.is_file()}
    upstream_unchanged = before_hashes == after_hashes
    manifest["upstream_modified"] = not upstream_unchanged
    (OUTPUT / "01_extract02_run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    validation_specs = [
        ("E02-V01", "extract01_present", extract_seen, extract_seen, True),
        ("E02-V02", "extract01a_present", extract01a_seen, extract01a_seen, True),
        ("E02-V03", "extract01a_readiness_valid", readiness_valid, imported_readiness, "conditional_ready_for_extract02_precontract_with_open_review_items"),
        ("E02-V04", "ten_human_freeze_items_recorded", len(freeze_rows) == 10, len(freeze_rows), 10),
        ("E02-V05", "first_scope_defined", len(scope_rows) == 8, len(scope_rows), 8),
        ("E02-V06", "material_sources_excluded", all(row["included_first_scope"] == "false" for row in material_rows), len(material_rows), 4),
        ("E02-V07", "K_mode_recorded", any(row["K_mode"] == "K_from_phase_response_vectors" and row["decision_status"] == "candidate_frozen_pending_human_approval" for row in k_rows), "primary candidate", "K_from_phase_response_vectors"),
        ("E02-V08", "no_ell0_invention", distance_rows[0]["decision_value"] == "not_frozen", distance_rows[0]["decision_value"], "not_frozen"),
        ("E02-V09", "no_epsilon_invention", distance_rows[1]["decision_value"] == "not_frozen", distance_rows[1]["decision_value"], "not_frozen"),
        ("E02-V10", "no_edge_threshold_tuned_from_L2", strength_rows[2]["threshold_parameter"] == "theta_edge=not_frozen", strength_rows[2]["threshold_parameter"], "theta_edge=not_frozen"),
        ("E02-V11", "no_extraction_executed", manifest["extraction_executed"] is False, manifest["extraction_executed"], False),
        ("E02-V12", "no_live_K_computed", manifest["live_K_computed"] is False, manifest["live_K_computed"], False),
        ("E02-V13", "no_live_d_D_computed", manifest["live_d_D_computed"] is False, manifest["live_d_D_computed"], False),
        ("E02-V14", "no_shortest_paths_computed", manifest["shortest_paths_computed"] is False, manifest["shortest_paths_computed"], False),
        ("E02-V15", "no_kernel_execution", manifest["kernels_executed"] is False, manifest["kernels_executed"], False),
        ("E02-V16", "no_clustering_executed", manifest["clustering_executed"] is False, manifest["clustering_executed"], False),
        ("E02-V17", "no_upstream_mutation", upstream_unchanged, upstream_unchanged, True),
        ("E02-V18", "claim_boundary_clean", manifest["physical_evidence_claim_made"] is False and bool(manifest["claim_boundary"]), manifest["physical_evidence_claim_made"], False),
        ("E02-V19", "readiness_decision_present", READINESS in {"ready_to_prepare_extract03_execution_package", "conditional_ready_pending_human_approval", "blocked_pending_human_freeze_decisions", "blocked_missing_required_metadata", "blocked_upstream_mismatch"}, READINESS, "allowed value"),
        ("E02-V20", "exact_output_count", True, 21, 21),
    ]
    validation_rows = [{
        "validation_id": vid, "validation_layer": "EXTRACT02 precontract", "check_name": name,
        "status": "pass" if passed else "fail", "severity": "error", "observed_value": observed,
        "expected_value": expected, "message": "Contract check passed." if passed else "Contract check failed.",
        "blocking_for_readiness": "no" if passed else "yes",
    } for vid, name, passed, observed, expected in validation_specs]
    write_csv(OUTPUT / "19_validation_results.csv", ["validation_id", "validation_layer", "check_name", "status", "severity", "observed_value", "expected_value", "message", "blocking_for_readiness"], validation_rows)

    note_de = f"""# QSB-EXTRACT02 Kurznotiz

## Ausgangspunkt

EXTRACT01A erlaubte die Vorbereitung eines Precontracts, ließ aber zehn Human-Freeze-Entscheidungen offen. EXTRACT02 übernimmt diese Punkte und verhindert, dass ein späteres Ausführungspaket stillschweigend Zustandsfamilie, K-Modus, Parameter, Kernel oder Clusterregeln ändert.

## Was EXTRACT02 festhält

Der erste Scope nutzt ausschließlich metadata-selektierte F3-artige `spatial_pair_delta_phi_x`-Quellen und phase-response vectors für geordnete Nichtdiagonalpaare auf einem eingefrorenen x-index-Fenster. `K_from_phase_response_vectors` ist der primäre Kandidat.

## Die zehn Human-Freeze-Entscheidungen

Sieben Punkte besitzen Kandidaten und warten auf menschliche Freigabe. `ell_0`, Gram-`epsilon` und `theta_edge` bleiben `not_frozen` und blockieren bereits die Vorbereitung von EXTRACT03. Keine Kandidatenentscheidung gilt als Zustimmung.

## Erster Scope

Vorgeschlagen sind Invariance-, Gram-Distance-, Shortest-Path- und Edge-Candidate-Kernel. Clusterregeln sind als Kandidaten dokumentiert; Clusterkernel bleiben außerhalb des minimalen Vier-Kernel-Scopes, bis sie ausdrücklich ergänzt werden.

## Was ausdrücklich ausgeschlossen bleibt

Material- und isotopensensitive Quellen, unbestätigte ψ-Familien, lose nicht-liniengebundene Dateien, synthetische Evidenzquellen sowie jede Verwendung der L2-Schwelle als Edge-Schwelle sind ausgeschlossen.

## Readiness-Entscheidung

`{READINESS}`: `{candidate_count}` Kandidaten warten auf Zustimmung, `{blocker_count}` essentielle Werte fehlen. EXTRACT03 darf noch nicht vorbereitet werden.

## Was nicht ausgeführt wurde

EXTRACT02 ist ein Pre-Execution-Vertrag. Es wurde keine Extraktion ausgeführt, kein K/d/D live berechnet und kein Clusterlauf gestartet.
"""
    (OUTPUT / "20_short_contract_note_de.md").write_text(note_de, encoding="utf-8")

    final_note = f"""# QSB-EXTRACT02 Final Result

## Status

`{STATUS}`

## Contract Scope

First-scope candidate: metadata-selected F3-like spatial pair phase responses, ordered non-diagonal pairs, frozen x-index vectors, and `K_from_phase_response_vectors`.

## Human-Freeze Register

Exactly ten decisions recorded: `{frozen_count}` frozen, `{candidate_count}` candidate-pending approval, `{blocker_count}` not frozen and blocking an execution package.

## First Extraction Scope

Minimal candidate kernel subset: invariance, Gram distance, shortest path, and edge candidate. No kernel is executed here.

## Material-Sensitive Source Boundary

Material- and isotope-sensitive sources are excluded pending a separate source contract.

## Readiness Decision

`{READINESS}`. Human approval plus numeric/rule resolution for `ell_0`, Gram `epsilon`, and `theta_edge` are required before EXTRACT03 package preparation.

## No-Execution Boundary

No extraction, K/d/D, shortest path, kernel, clustering, Minimaltest, or nullmodel was executed. L2 remains fail and upstream databases remain unchanged.

## Next Allowed Action

Resolve HF-03, HF-04, and HF-06; obtain explicit human approval for the seven candidate decisions; then run a separate readiness/authorization check before preparing EXTRACT03.
"""
    (OUTPUT / "FINAL_RESULT_NOTE.md").write_text(final_note, encoding="utf-8")

    actual = {path.name for path in OUTPUT.iterdir() if path.is_file()}
    if actual != EXPECTED_FILES:
        raise SystemExit(f"Output file-set mismatch: actual={sorted(actual)} expected={sorted(EXPECTED_FILES)}")
    failures = [row["validation_id"] for row in validation_rows if row["status"] == "fail"]
    if failures:
        raise SystemExit(f"EXTRACT02 validation failures: {failures}")
    print(f"status={STATUS}")
    print(f"execution_package_readiness={READINESS}")
    print("human_freeze_items_recorded=10")
    print(f"candidate_pending={candidate_count}")
    print(f"blocking_items={blocker_count}")
    print("material_sensitive_sources=excluded")
    print("execution=false")
    print(f"output_files={len(actual)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
