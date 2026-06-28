#!/usr/bin/env python3
"""Review EXTRACT01 gaps and prerequisites without extraction or parameter tuning."""

from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REPO = Path(__file__).resolve().parents[2]
EXTRACT01 = REPO / "runs/QSB-EXTRACT01/dwh_based_gram_tensor_extraction_layer_design"
N0 = REPO / "runs/QSB-INTERFACE01N0/post_fail_scope_review_feature_n4_extract_path"
M2 = REPO / "runs/QSB-INTERFACE01M2/result_review_mechanism_interpretation_boundary_after_l2"
L2 = REPO / "runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2"
F3 = REPO / "runs/QSB-INTERFACE01F3/authorized_delta_phi_export_staging_preflight"
META_DB = REPO / "runs/QSB-META01-03/causality07_pilot_metadata/qsb_metadata_catalog.sqlite"
SOURCE_HUB_DB = REPO / "runs/QSB-GAP02A/source_hub_schema_dry_run_loader/qsb_source_hub_dry_run.sqlite"
OUTPUT = REPO / "runs/QSB-EXTRACT01A/metadata_gap_prerequisite_resolution_review"

STATUS = "extract01a_metadata_gap_prerequisite_resolution_review_completed_with_readiness_decision"
READINESS = "conditional_ready_for_extract02_precontract_with_open_review_items"
CLAIM_BOUNDARY = (
    "QSB-EXTRACT01A reviews and proposes resolutions for EXTRACT01 metadata gaps and prerequisites "
    "only. It executes no extraction, Minimaltest, nullmodel, live K/d/D computation, or clustering; "
    "freezes no numeric parameter without human approval; mutates no upstream database; and makes no "
    "physical-evidence, mechanism, geometry, or gravity claim."
)
EXPECTED_FILES = {
    "01_extract01a_run_manifest.json", "02_upstream_inventory_and_hashes.csv",
    "03_imported_extract01_gap_and_prerequisite_summary.csv", "04_metadata_gap_resolution_matrix.csv",
    "05_prerequisite_resolution_matrix.csv", "06_state_family_resolution_review.csv",
    "07_K_construction_mode_resolution_review.csv", "08_distance_parameter_resolution_review.csv",
    "09_strength_transform_and_edge_threshold_review.csv", "10_kernel_subset_resolution_review.csv",
    "11_cluster_protocol_resolution_review.csv", "12_source_selection_query_contract.csv",
    "13_validation_matrix_freeze_review.csv", "14_extract02_readiness_decision.csv",
    "15_no_execution_guard.csv", "16_claim_boundary_matrix.csv",
    "17_review_items_for_extract02_precontract.csv", "18_short_review_note_de.md",
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


def sqlite_tables(path: Path) -> set[str]:
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    connection.close()
    return tables


def main() -> int:
    if OUTPUT.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {OUTPUT}")

    extract_files = [
        "01_extract01_run_manifest.json", "05_metadata_gap_register.csv", "06_tensor_axis_contract.csv",
        "07_channel_contract.csv", "08_gram_construction_contract.csv", "09_distance_d_D_contract.csv",
        "10_relation_strength_and_edge_rule_contract.csv", "11_extraction_kernel_registry.csv",
        "12_dendrogram_cluster_design.csv", "13_future_result_mart_schema_contract.csv",
        "14_validation_rule_matrix.csv", "17_next_run_prerequisites.csv",
        "18_review_items_for_extract02_or_future_run.csv", "FINAL_RESULT_NOTE.md",
    ]
    artifacts: dict[str, tuple[str, Path, str]] = {}
    for index, name in enumerate(extract_files, start=1):
        artifacts[f"extract_{index:02d}"] = ("EXTRACT01", EXTRACT01 / name, "required EXTRACT01 design import")
    artifacts.update({
        "n0_manifest": ("N0", N0 / "01_n0_run_manifest.json", "design-path recommendation"),
        "m2_manifest": ("M2", M2 / "01_m2_run_manifest.json", "failure-review context"),
        "l2_manifest": ("L2", L2 / "01_l2_run_manifest.json", "unchanged fail context"),
        "f3_manifest": ("F3", F3 / "01_f3_run_manifest.json", "staged source context"),
        "f3_input": ("F3", REPO / "runs/QSB-INTERFACE01F3/input_manifest/interface01f3_delta_phi_input_manifest.json", "phase-response source metadata"),
        "h_features": ("H", REPO / "runs/QSB-INTERFACE01H/controlled_minimal_pilot_from_staged_delta_phi/03_pair_feature_table.csv", "feature-vector candidate basis"),
        "meta_db": ("META01-03", META_DB, "metadata schema basis"),
        "source_hub_db": ("GAP02A", SOURCE_HUB_DB, "source-selection schema basis"),
    })
    upstream_present = all(path.is_file() for _, path, _ in artifacts.values())
    before_hashes = {key: sha256(path) for key, (_, path, _) in artifacts.items() if path.is_file()}
    inventory_rows = []
    for number, (key, (block, path, use)) in enumerate(artifacts.items(), start=1):
        exists = path.is_file()
        inventory_rows.append({
            "artifact_id": f"EX01A-A{number:02d}", "upstream_block": block, "path": rel(path),
            "exists": "yes" if exists else "no", "sha256": before_hashes.get(key, "missing"),
            "role": "read-only resolution-review input", "used_for": use,
            "notes": "Hashed before EXTRACT01A; not modified." if exists else "Missing required context.",
        })
    if not upstream_present:
        raise SystemExit("EXTRACT01A blocked: required EXTRACT01 or upstream context is missing.")

    extract_manifest = load_json(EXTRACT01 / "01_extract01_run_manifest.json")
    extract_seen = extract_manifest.get("status") == "extract01_dwh_based_gram_tensor_extraction_layer_design_completed_no_execution"
    design_only = (
        extract_manifest.get("design_only") is True
        and extract_manifest.get("extraction_executed") is False
        and extract_manifest.get("live_K_computed") is False
        and extract_manifest.get("live_d_D_computed") is False
        and extract_manifest.get("clustering_executed") is False
    )
    l2_manifest = load_json(L2 / "01_l2_run_manifest.json")
    m2_manifest = load_json(M2 / "01_m2_run_manifest.json")
    n0_manifest = load_json(N0 / "01_n0_run_manifest.json")
    context_ok = (
        l2_manifest.get("minimaltest_contract_result") == "fail"
        and m2_manifest.get("failure_review_mode") is True
        and n0_manifest.get("primary_recommendation") == "prepare_extract01_design"
    )
    meta_tables = sqlite_tables(META_DB)
    hub_tables = sqlite_tables(SOURCE_HUB_DB)
    dwh_basis = {"meta_source", "meta_object", "meta_field", "meta_lineage", "meta_unit", "meta_validation_rule", "meta_result_table"} <= meta_tables and {"qsb_source_object", "qsb_source_file", "qsb_source_ingest_event", "qsb_source_claim_boundary_flag"} <= hub_tables
    if not all([extract_seen, design_only, context_ok, dwh_basis]):
        raise SystemExit("EXTRACT01A blocked: design-only or DWH context is inconsistent.")

    extract_gaps = read_csv(EXTRACT01 / "05_metadata_gap_register.csv")
    prerequisites = read_csv(EXTRACT01 / "17_next_run_prerequisites.csv")
    gram_modes = read_csv(EXTRACT01 / "08_gram_construction_contract.csv")
    distance_contract = read_csv(EXTRACT01 / "09_distance_d_D_contract.csv")
    relation_contract = read_csv(EXTRACT01 / "10_relation_strength_and_edge_rule_contract.csv")
    kernels = read_csv(EXTRACT01 / "11_extraction_kernel_registry.csv")
    cluster_design = read_csv(EXTRACT01 / "12_dendrogram_cluster_design.csv")
    validation_design = read_csv(EXTRACT01 / "14_validation_rule_matrix.csv")
    channels = read_csv(EXTRACT01 / "07_channel_contract.csv")
    marts = read_csv(EXTRACT01 / "13_future_result_mart_schema_contract.csv")

    imported_rows = []
    for i, row in enumerate(extract_gaps, start=1):
        imported_rows.append({
            "import_item_id": f"EX01A-IMP-G{i:02d}", "source_file": rel(EXTRACT01 / "05_metadata_gap_register.csv"),
            "item_type": "metadata_gap", "item_name": row["missing_element"],
            "imported_value": row["required_resolution"], "status_in_extract01": "blocking_for_execution",
            "extract01a_initial_status": "review_required", "notes": f"Imported exact gap_id={row['gap_id']}.",
        })
    prerequisite_names = [
        "freeze_psi_or_feature_state_family", "freeze_K_construction_mode", "freeze_ell0", "freeze_epsilon",
        "freeze_distance_to_strength_transform", "freeze_edge_threshold", "freeze_kernel_subset",
        "freeze_cluster_protocol", "freeze_source_selection_query", "freeze_validation_matrix",
    ]
    for i, (row, name) in enumerate(zip(prerequisites, prerequisite_names), start=1):
        imported_rows.append({
            "import_item_id": f"EX01A-IMP-P{i:02d}", "source_file": rel(EXTRACT01 / "17_next_run_prerequisites.csv"),
            "item_type": "prerequisite", "item_name": name, "imported_value": row["description"],
            "status_in_extract01": "not_frozen_blocks_execution", "extract01a_initial_status": "candidate_resolution_review",
            "notes": f"Imported exact prerequisite_id={row['prerequisite_id']}.",
        })

    gap_specs = [
        ("EX01-GAP-01", "state_family", "explicit_psi_state_family", "blocking", "open", EXTRACT01 / "08_gram_construction_contract.csv", "Keep explicit psi gap open; use phase-response candidate for first precontract.", "no", "yes"),
        ("EX01-GAP-02", "gram_source", "gram_construction_source", "blocking", "partially_closed", EXTRACT01 / "08_gram_construction_contract.csv", "Propose K_from_phase_response_vectors; human freeze required.", "no", "yes"),
        ("EX01-GAP-03", "distance_parameter", "ell0_numeric_freeze", "blocking", "open", EXTRACT01 / "09_distance_d_D_contract.csv", "Carry ell_0 as not_frozen human decision; no numeric proposal.", "no", "yes"),
        ("EX01-GAP-04", "distance_parameter", "epsilon_numeric_freeze", "blocking", "open", EXTRACT01 / "09_distance_d_D_contract.csv", "Carry epsilon_Gram as not_frozen and distinct from L2 epsilon_new.", "no", "yes"),
        ("EX01-GAP-05", "source", "material_sensitive_sources", "blocking_for_material_kernel", "deferred", SOURCE_HUB_DB, "Exclude material kernels from first scope; retain metadata gap for later source scout.", "no", "yes"),
        ("EX01-GAP-06", "cluster_protocol", "cluster_stability_protocol", "blocking", "partially_closed", EXTRACT01 / "12_dendrogram_cluster_design.csv", "Propose average-linkage primary plus split/bootstrap stability; human freeze required.", "no", "yes"),
        ("EX01A-GAP-07", "relation_rule", "distance_to_strength_transform", "not_frozen", "partially_closed", EXTRACT01 / "10_relation_strength_and_edge_rule_contract.csv", "Candidate s=exp(-d/ell_0); allow declaration unused; human freeze required.", "no", "yes"),
        ("EX01A-GAP-08", "edge_rule", "edge_threshold", "not_frozen", "open", EXTRACT01 / "10_relation_strength_and_edge_rule_contract.csv", "Freeze threshold family, calibration partition, direction, and tie rule in EXTRACT02.", "no", "yes"),
        ("EX01A-GAP-09", "kernel_registry", "kernel_subset", "not_frozen", "partially_closed", EXTRACT01 / "11_extraction_kernel_registry.csv", "Propose minimal four-kernel subset; human freeze required.", "no", "yes"),
        ("EX01A-GAP-10", "source_selection", "source_selection_query", "not_frozen", "partially_closed", META_DB, "Draft metadata query contract in EXTRACT01A; freeze exact query/hash in EXTRACT02.", "no", "yes"),
        ("EX01A-GAP-11", "validation", "validation_matrix_freeze", "not_frozen", "partially_closed", EXTRACT01 / "14_validation_rule_matrix.csv", "Runtime gate set assembled; severities/tolerances require human freeze.", "no", "yes"),
        ("EX01A-GAP-12", "result_mart", "result_mart_execution_schema", "design_defined", "closed", EXTRACT01 / "13_future_result_mart_schema_contract.csv", "Use 13-entity design as EXTRACT02 schema basis; physical table creation remains future work.", "no", "yes"),
    ]
    gap_rows = [{
        "gap_id": gid, "gap_category": category, "missing_element": missing,
        "extract01_status": old_status, "extract01a_status": new_status, "basis_artifact": rel(basis),
        "resolution_or_next_action": action, "blocks_extract02_precontract": precontract,
        "blocks_future_extraction": future, "notes": "No gap is closed without an explicit design artifact basis.",
    } for gid, category, missing, old_status, new_status, basis, action, precontract, future in gap_specs]

    prerequisite_candidates = [
        ("freeze_psi_or_feature_state_family", "Use phase_response_vector_family_from_F3 as primary candidate; freeze window, axes, norm, and lineage."),
        ("freeze_K_construction_mode", "Propose K_from_phase_response_vectors as primary mode; freeze Hermiticity/PSD tolerances."),
        ("freeze_ell0", "Retain not_frozen placeholder; human must freeze positive value and unit role."),
        ("freeze_epsilon", "Retain not_frozen epsilon_Gram; human must freeze numerical rule distinct from L2 epsilon_new."),
        ("freeze_distance_to_strength_transform", "Candidate s=exp(-d/ell_0) or explicitly unused; freeze one choice."),
        ("freeze_edge_threshold", "Freeze theta_s or theta_d source partition, direction, precision, and tie policy."),
        ("freeze_kernel_subset", "Propose invariance, gram_distance, shortest_path, and edge_candidate kernels."),
        ("freeze_cluster_protocol", "Propose D matrix, average linkage, complete-link diagnostic, split/bootstrap stability, fixed cut rule."),
        ("freeze_source_selection_query", "Freeze drafted metadata filters, eligibility, checksum, lineage, and gap behavior."),
        ("freeze_validation_matrix", "Freeze assembled start/runtime/output gates, severities, tolerances, and stop actions."),
    ]
    prerequisite_rows = []
    for row, (name, candidate) in zip(prerequisites, prerequisite_candidates):
        prerequisite_rows.append({
            "prerequisite_id": row["prerequisite_id"], "prerequisite_name": name,
            "extract01_status": "not_frozen_blocks_execution",
            "extract01a_status": "candidate_resolution_proposed_requires_human_freeze",
            "basis_artifact": rel(EXTRACT01 / "17_next_run_prerequisites.csv"),
            "candidate_resolution": candidate, "requires_human_freeze": "yes",
            "blocks_extract02_precontract": "no", "blocks_future_extraction": "yes",
            "notes": "May be carried into EXTRACT02 precontract; not authorized for execution.",
        })

    state_rows = [
        {"state_family_item": "feature_vector_family_from_H_I_L2", "candidate_source": "three locked aggregate feature columns", "candidate_definition": "pair-indexed normalized feature vectors with frozen schema/scaling", "basis_artifact": rel(REPO / "runs/QSB-INTERFACE01H/controlled_minimal_pilot_from_staged_delta_phi/03_pair_feature_table.csv"), "resolution_status": "candidate_available_not_recommended_primary", "adequacy_for_extract02_precontract": "adequate as diagnostic alternative only", "blocks_future_execution": "yes_until_human_freeze", "notes": "L2 fail prevents no use, but outcome-driven feature repair is forbidden."},
        {"state_family_item": "phase_response_vector_family_from_F3", "candidate_source": "F3 wrapped_delta_phi with cos/sin response channels", "candidate_definition": "pair-indexed phase-response vectors over a frozen x window/grid with declared weights and unit norm", "basis_artifact": rel(F3 / "09_delta_phi_staging_preflight.sqlite"), "resolution_status": "candidate_resolution_proposed_requires_human_freeze", "adequacy_for_extract02_precontract": "recommended primary candidate", "blocks_future_execution": "yes_until_window_normalization_and_lineage_freeze", "notes": "Broader than three aggregates; no vector or K computed here."},
        {"state_family_item": "explicit_psi_state_family", "candidate_source": "not present in audited DWH metadata", "candidate_definition": "unresolved", "basis_artifact": rel(META_DB), "resolution_status": "unresolved_metadata_gap", "adequacy_for_extract02_precontract": "not required if phase-response mode is explicitly selected", "blocks_future_execution": "yes_for_K_from_state_vectors", "notes": "Do not invent psi values or basis."},
    ]

    recommended_mode = "K_from_phase_response_vectors"
    mode_rows = []
    for row in gram_modes:
        mode = row["gram_mode"]
        if mode == recommended_mode:
            status, recommended, note = "candidate_resolution_proposed_requires_human_freeze", "yes_primary_candidate", "F3 phase-response channels and common x grid provide documented input lineage."
        elif mode == "K_from_feature_vectors":
            status, recommended, note = "deferred_to_extract02_precontract", "diagnostic_alternative_only", "Available feature lineage, but do not use as post-fail repair."
        elif mode == "K_from_windowed_signal_states":
            status, recommended, note = "deferred_to_extract02_precontract", "secondary_candidate", "Requires window semantics beyond current freeze."
        else:
            status, recommended, note = "blocked_missing_source", "no", "Required explicit state vectors or distributions are absent."
        mode_rows.append({
            "gram_mode": mode, "input_object": row["input_object"],
            "basis_artifact": rel(EXTRACT01 / "08_gram_construction_contract.csv"),
            "admissibility_requirements": f"{row['admissibility_checks']}; {row['hermiticity_check']}; {row['psd_check']}",
            "resolution_status": status, "recommended_for_extract02_precontract": recommended,
            "requires_human_freeze": "yes", "notes": note,
        })

    distance_by_item = {row["contract_item"]: row for row in distance_contract}
    distance_specs = [
        ("ell_0", "ell_0", "cost-distance scale", "not_frozen", "Human freeze positive value, unit, and dimensional interpretation.", "yes", "tune to create desired clusters"),
        ("epsilon", "epsilon_Gram", "log-domain guard", "not_frozen", "Human freeze dimensionless precision/domain rule distinct from L2 epsilon_new.", "yes", "reuse or tune L2 epsilon_new silently"),
        ("d_ij", "d_ij", "direct overlap-derived cost", "formula_defined_parameters_not_frozen", "Retain -ell_0 log(|K_ij|+epsilon_Gram); freeze diagonal/nonnegative policy.", "yes", "compute before K mode and parameters freeze"),
        ("D_i_j", "D(i,j)", "shortest-path reconstructed cost", "formula_defined_graph_not_frozen", "Freeze eligible edge graph, connectivity, symmetry, and unreachable policy.", "yes", "call D geometry without validation"),
        ("dominant_path_check", "p*", "path stability diagnostic", "not_frozen", "Freeze tie rule, path provenance, and competing-path margin.", "yes", "select attractive paths post hoc"),
        ("metric_readable_boundary", "metric_status", "later regime validation", "not_tested", "Require nonnegativity/identity/symmetry/triangle and stability audit before metric-readable label.", "yes", "assume spacetime or geometry"),
    ]
    distance_rows = [{
        "parameter": item, "symbol": symbol, "role": role, "current_status": status,
        "candidate_resolution": candidate, "requires_human_freeze": human,
        "forbidden_use": forbidden, "notes": f"Basis: {rel(EXTRACT01 / '09_distance_d_D_contract.csv')}; no numeric value computed.",
    } for item, symbol, role, status, candidate, human, forbidden in distance_specs]

    relation_by_rule = {row["rule_id"]: row for row in relation_contract}
    relation_names = ["small_d_high_similarity", "s_from_d_candidate", "theta_d_candidate", "theta_s_candidate", "edge_candidate_rule", "motif_candidate_rule"]
    relation_candidates = {
        "small_d_high_similarity": ("ordering only", "defined_requires_human_confirmation"),
        "s_from_d_candidate": ("candidate s=exp(-d/ell_0); alternative declare s unused", "candidate_not_frozen"),
        "theta_d_candidate": ("freeze upper d threshold using preregistered calibration partition", "candidate_not_frozen"),
        "theta_s_candidate": ("freeze lower s threshold using preregistered calibration partition", "candidate_not_frozen"),
        "edge_candidate_rule": ("select exactly one d- or s-based rule with tie policy", "candidate_not_frozen"),
        "motif_candidate_rule": ("require edge/cluster stability and contract-hash-derived motif ID", "candidate_not_frozen"),
    }
    relation_rows = []
    for name, source_row in zip(relation_names, relation_contract):
        candidate, status = relation_candidates[name]
        relation_rows.append({
            "item": name, "input_measure": source_row["input_measure"], "candidate_rule": candidate,
            "status": status, "requires_human_freeze": "yes", "allowed_future_use": "EXTRACT02 contract drafting only until frozen",
            "forbidden_use": "outcome-selected transform/threshold or L2 repair",
            "notes": "No transform or threshold evaluated on data.",
        })

    first_subset = {"invariance_kernel", "edge_candidate_kernel", "gram_distance_kernel", "shortest_path_kernel"}
    conditional_subset = {"cluster_dendrogram_kernel", "motif_stability_kernel"}
    kernel_rows = []
    for row in kernels:
        name = row["kernel_name"]
        if name in first_subset:
            recommended, status, why = "yes", "candidate_resolution_proposed_requires_human_freeze", "Minimal Gram/d/D execution and invariance/edge guards."
        elif name in conditional_subset:
            recommended, status, why = "conditional_if_cluster_scope_included", "deferred_to_extract02_precontract", "Requires frozen cluster protocol."
        else:
            recommended, status, why = "no_first_contract", "deferred", "Not required for first Gram/d/D contract or lacks eligible source."
        kernel_rows.append({
            "kernel_id": row["kernel_id"], "kernel_name": name, "extract01_role": f"{row['input_channels']} -> {row['output_channels']}",
            "recommended_for_first_extract02_contract": recommended, "resolution_status": status,
            "requires_human_freeze": "yes" if recommended != "no_first_contract" else "no_if_excluded",
            "why_or_why_not": why, "notes": "No kernel executed; subset recommendation is method-driven, not outcome-selected.",
        })

    cluster_candidates = [
        ("distance_matrix_source", "shortest_path_D primary; direct d diagnostic", "candidate_not_frozen", "Freeze D source hash and admissibility; direct d only as declared diagnostic."),
        ("linkage_method_options", "average linkage primary; complete linkage diagnostic", "candidate_not_frozen", "Freeze methods before outcomes; Ward only after Euclidean admissibility."),
        ("cluster_stability", "predefined membership stability plus cophenetic diagnostic", "candidate_not_frozen", "Freeze metric and minimum stability."),
        ("split_bootstrap_stability", "deterministic split/bootstrap membership overlap", "candidate_not_frozen", "Freeze resample unit, seed, repetitions, and score."),
        ("cluster_to_motif_mapping", "map only clusters passing all frozen stability gates", "candidate_not_frozen", "Freeze one-to-one membership checksum rule."),
        ("motif_id_generation", "hash(contract,source,membership)", "candidate_resolution_proposed", "Deterministic ID design can enter precontract."),
        ("claim_boundary", "candidate relational grouping only", "resolved_from_existing_artifacts", "EXTRACT01 claim boundary retained verbatim in precontract."),
    ]
    cluster_rows = [{
        "cluster_item": item, "method_or_requirement": method, "current_status": status,
        "candidate_resolution": resolution, "requires_human_freeze": "no" if item == "claim_boundary" else "yes",
        "blocks_future_execution": "yes", "notes": "No clustering performed.",
    } for item, method, status, resolution in cluster_candidates]

    source_query_specs = [
        ("EX01A-Q01", "staged_delta_phi_sources", "source_type/source_mode;status;schema_version;input_hash;claim_boundary", "authorized/eligible status; required fields; validation pass; immutable checksum", "angle_unit and dimensionless_angle; x unit/status explicit", "source/object/version IDs; input/file hash; selection predicate checksum", "emit extract_metadata_gap; block source", "candidate_resolution_proposed_requires_human_freeze", "F3 can serve as lineage example, not automatic selection."),
        ("EX01A-Q02", "feature_response_sources", "object/table role;feature schema;rule ID;source hash", "preregistered schema; no outcome-selected columns; finite validation", "per-feature unit/dimension registered", "feature object/version;transformation rule;record lineage", "block missing feature family", "candidate_resolution_proposed_requires_human_freeze", "H/L2 features are diagnostic alternatives only."),
        ("EX01A-Q03", "material_sensitive_sources", "material_id;isotope_id;source/evidence/claim status", "eligible audited source and human review", "material quantities carry unit and dimension metadata", "source hub object/file/ingest/relationship IDs", "record open gap; exclude material kernels", "unresolved_metadata_gap", "No eligible material-sensitive source frozen."),
        ("EX01A-Q04", "gram_ready_sources", "state_family_id;K_mode;normalization;axis compatibility;lineage", "candidate state family frozen; admissibility schema complete", "normalized K dimension status and input units declared", "source/state/window keys;rule IDs;contract hash", "block live K construction", "candidate_resolution_proposed_requires_human_freeze", "Draft only; no query executed."),
    ]
    query_rows = [{
        "query_contract_id": qid, "source_category": category, "metadata_filters_required": filters,
        "eligibility_conditions": eligibility, "unit_dimension_requirements": units,
        "lineage_requirements": lineage, "gap_handling": gap, "status": status, "notes": notes,
    } for qid, category, filters, eligibility, units, lineage, gap, status, notes in source_query_specs]

    freeze_checks = [
        "source_selection_query_frozen", "state_family_frozen", "K_mode_frozen", "ell0_frozen",
        "epsilon_frozen", "strength_transform_frozen", "edge_threshold_frozen", "kernel_subset_frozen",
        "cluster_protocol_frozen", "result_mart_schema_ready", "no_execution_in_extract01a",
    ]
    validation_rows = []
    for i, check in enumerate(freeze_checks, start=1):
        if check == "result_mart_schema_ready":
            status, candidate = "resolved_from_existing_artifacts", "Use 13-entity EXTRACT01 mart contract as schema basis; freeze physical DDL later."
        elif check == "no_execution_in_extract01a":
            status, candidate = "resolved_from_existing_artifacts", "Manifest and guards require all execution flags false."
        else:
            status, candidate = "candidate_resolution_proposed_requires_human_freeze", "Freeze proposed resolution and runtime failure action in EXTRACT02."
        validation_rows.append({
            "validation_id": f"EX01A-VF-{i:02d}", "validation_layer": "precontract" if i <= 9 else "output",
            "check_name": check, "required_before_extract02_precontract": "candidate definition required",
            "required_before_future_execution": "frozen pass gate required", "current_status": status,
            "candidate_resolution": candidate, "notes": "Design/review status is not runtime evidence.",
        })

    human_freeze_count = sum(row["requires_human_freeze"] == "yes" for row in prerequisite_rows)
    open_precontract_blockers = sum(row["blocks_extract02_precontract"] == "yes" for row in gap_rows)
    readiness_rows = [{
        "decision_id": "EX01A-READY-01", "readiness_decision": READINESS,
        "rationale": "All ten prerequisites have documented candidate resolutions that can be frozen in an EXTRACT02 precontract; none is authorized for execution. Material-sensitive sources and explicit psi remain scoped gaps.",
        "open_blockers_count": open_precontract_blockers, "human_freeze_items_count": human_freeze_count,
        "allowed_next_action": "prepare_extract02_pre_execution_contract",
        "forbidden_next_action": "execute_extraction_now;compute_live_K_d_D_now;run_clustering_now;tune_parameters_to_L2_fail",
        "notes": "Conditional readiness means contract drafting only, not extraction readiness.",
    }]

    guard_names = [
        "no_minimaltest_rerun", "no_nullmodel_rerun", "no_live_K_computation", "no_live_d_D_computation",
        "no_clustering_execution", "no_theta_epsilon_tuning", "no_feature_repair", "no_n4_change",
        "no_upstream_db_mutation", "no_physical_evidence_claim",
    ]
    guard_rows = [{
        "guard_id": f"EX01A-GUARD-{i:02d}", "guard_item": name, "status": "pass",
        "evidence": {
            "no_minimaltest_rerun": "minimaltest_rerun=false", "no_nullmodel_rerun": "nullmodels_rerun=false",
            "no_live_K_computation": "live_K_computed=false", "no_live_d_D_computation": "live_d_D_computed=false",
            "no_clustering_execution": "clustering_executed=false", "no_theta_epsilon_tuning": "theta_or_epsilon_tuned=false",
            "no_physical_evidence_claim": "physical_evidence_claim_made=false",
        }.get(name, "review rows only; upstream hashes unchanged"),
        "notes": "EXTRACT01A is review/preparation only.",
    } for i, name in enumerate(guard_names, start=1)]

    claim_specs = [
        ("EX01A-C01", "EXTRACT01A reviews design gaps", "review_statement", "The package classifies existing gaps and prerequisites.", "Treating review status as extraction output."),
        ("EX01A-C02", "K_from_phase_response_vectors is a candidate", "candidate_resolution", "The mode is proposed for human freeze in EXTRACT02.", "Calling the mode validated or selected for execution."),
        ("EX01A-C03", "ell_0 and epsilon require human freeze", "future_freeze_requirement", "No numeric value is selected in EXTRACT01A.", "Inferring values from L2 or desired clusters."),
        ("EX01A-C04", "EXTRACT01A proves the mechanism", "unsupported_claim", "No mechanism result follows from prerequisite review.", "EXTRACT01A proves the mechanism."),
        ("EX01A-C05", "EXTRACT01A reverses L2 fail", "unsupported_claim", "L2 remains fail.", "EXTRACT01A reverses L2 fail."),
        ("EX01A-C06", "EXTRACT01A demonstrates emergent geometry", "unsupported_claim", "No K/d/D or clustering result exists.", "EXTRACT01A demonstrates emergent geometry."),
        ("EX01A-C07", "EXTRACT01A demonstrates gravity", "unsupported_claim", "No gravity observable or validation is present.", "EXTRACT01A demonstrates gravity."),
        ("EX01A-C08", "Metadata gaps are resolved without evidence", "unsupported_claim", "Gaps close only with cited artifacts or future human freeze.", "Metadata gaps are resolved without evidence."),
    ]
    claim_rows = [{
        "statement_id": sid, "statement": statement, "classification": classification,
        "safe_wording": safe, "forbidden_wording": forbidden,
        "notes": "Readiness is for precontract drafting only.",
    } for sid, statement, classification, safe, forbidden in claim_specs]

    review_categories = [
        ("state_family", "Freeze phase-response state/window family or choose another documented family."),
        ("K_mode", "Human-freeze primary K mode and admissibility tolerances."),
        ("ell0", "Freeze positive ell_0 and unit role."),
        ("epsilon", "Freeze dimensionless epsilon_Gram distinct from L2 epsilon_new."),
        ("strength_transform", "Freeze s=f(d) or declare unused."),
        ("edge_threshold", "Freeze threshold source, direction, precision, and tie policy."),
        ("kernel_subset", "Approve minimal four-kernel subset and versions."),
        ("cluster_protocol", "Freeze distance, linkage, cut, and stability protocol."),
        ("source_selection_query", "Freeze metadata query text/hash and gap behavior."),
        ("validation_matrix", "Freeze checks, tolerances, severities, and stop actions."),
        ("result_mart_schema", "Approve 13-entity schema basis and future DDL migration."),
        ("material_sensitive_sources", "Retain exclusion or resolve with audited source metadata."),
    ]
    review_rows = [{
        "review_item_id": f"EX01A-REV-{i:02d}", "category": category, "description": description,
        "blocks_extract02_precontract": "no", "blocks_future_execution": "yes",
        "recommended_resolution": "record human freeze decision in EXTRACT02 precontract",
        "notes": "Material source item may remain excluded from first execution scope.",
    } for i, (category, description) in enumerate(review_categories, start=1)]

    note_de = f"""# QSB-EXTRACT01A Kurznotiz

## Ausgangspunkt

EXTRACT01 entwarf die DWH-/Gram-/Tensor-Schicht und ließ sechs explizite Metadata Gaps sowie zehn Ausführungsvoraussetzungen offen. EXTRACT01A prüft diese Punkte gegen F3-, H-, Metadata-Catalog- und Source-Hub-Kontext.

## Was geprüft wurde

Geprüft wurden Zustandsfamilien, fünf K-Modi, `ell_0`, Gram-`epsilon`, d/D-Verträge, Stärke-/Kantenregeln, alle 13 Kernel, Clusterstabilität, Source-Query, Validierungen und Result-Mart-Schema.

## Was aufgelöst werden konnte

Die F3-Phasenantworten tragen eine nachvollziehbare Kandidatenfamilie für `K_from_phase_response_vectors`. Query-, Kernel-, Cluster- und Validierungsverträge können konkret in einen EXTRACT02-Precontract übernommen werden. Das 13-Entitäten-Mart-Design ist als Schema-Basis geschlossen. All diese Punkte benötigen vor einer Ausführung weiterhin Human Freeze.

## Was offen bleibt

Numerische Werte für `ell_0` und Gram-`epsilon`, der endgültige K-Modus, Fensterung/Normierung, Stärke- und Edge-Regel sowie Clusterprotokoll bleiben unfrozen. Explizite ψ-Zustände und material-sensitive Quellen bleiben Metadata Gaps; sie können im ersten phase-response-basierten Scope ausgeschlossen werden.

## Readiness-Entscheidung

`{READINESS}`: EXTRACT02 darf als Pre-Execution-Vertrag vorbereitet werden. Das bedeutet nicht, dass Extraktion freigegeben ist. Zehn Human-Freeze-Entscheidungen blockieren weiterhin jede Live-Ausführung.

## Was ausdrücklich nicht getan wurde

EXTRACT01A ist ein Review- und Vorbereitungsblock. Es wurde keine Extraktion ausgeführt und der L2-Fail bleibt unverändert. Es wurden keine Live-K-, d-, D- oder Clusterwerte berechnet und keine Parameter getunt.
"""

    OUTPUT.mkdir(parents=True)
    manifest = {
        "work_package": "QSB-EXTRACT01A", "status": STATUS,
        "created_at_utc": datetime.now(timezone.utc).isoformat(), "repo_root": str(REPO),
        "extract01_seen": extract_seen, "extract01_design_only_confirmed": design_only,
        "readiness_decision": READINESS, "metadata_gaps_reviewed": len(gap_rows),
        "prerequisites_reviewed": len(prerequisite_rows), "extraction_executed": False,
        "minimaltest_rerun": False, "nullmodels_rerun": False, "live_K_computed": False,
        "live_d_D_computed": False, "clustering_executed": False,
        "theta_or_epsilon_tuned": False, "physical_evidence_claim_made": False,
        "upstream_modified": False, "claim_boundary": CLAIM_BOUNDARY,
    }
    (OUTPUT / "01_extract01a_run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_csv(OUTPUT / "02_upstream_inventory_and_hashes.csv", ["artifact_id", "upstream_block", "path", "exists", "sha256", "role", "used_for", "notes"], inventory_rows)
    write_csv(OUTPUT / "03_imported_extract01_gap_and_prerequisite_summary.csv", ["import_item_id", "source_file", "item_type", "item_name", "imported_value", "status_in_extract01", "extract01a_initial_status", "notes"], imported_rows)
    write_csv(OUTPUT / "04_metadata_gap_resolution_matrix.csv", ["gap_id", "gap_category", "missing_element", "extract01_status", "extract01a_status", "basis_artifact", "resolution_or_next_action", "blocks_extract02_precontract", "blocks_future_extraction", "notes"], gap_rows)
    write_csv(OUTPUT / "05_prerequisite_resolution_matrix.csv", ["prerequisite_id", "prerequisite_name", "extract01_status", "extract01a_status", "basis_artifact", "candidate_resolution", "requires_human_freeze", "blocks_extract02_precontract", "blocks_future_extraction", "notes"], prerequisite_rows)
    write_csv(OUTPUT / "06_state_family_resolution_review.csv", ["state_family_item", "candidate_source", "candidate_definition", "basis_artifact", "resolution_status", "adequacy_for_extract02_precontract", "blocks_future_execution", "notes"], state_rows)
    write_csv(OUTPUT / "07_K_construction_mode_resolution_review.csv", ["gram_mode", "input_object", "basis_artifact", "admissibility_requirements", "resolution_status", "recommended_for_extract02_precontract", "requires_human_freeze", "notes"], mode_rows)
    write_csv(OUTPUT / "08_distance_parameter_resolution_review.csv", ["parameter", "symbol", "role", "current_status", "candidate_resolution", "requires_human_freeze", "forbidden_use", "notes"], distance_rows)
    write_csv(OUTPUT / "09_strength_transform_and_edge_threshold_review.csv", ["item", "input_measure", "candidate_rule", "status", "requires_human_freeze", "allowed_future_use", "forbidden_use", "notes"], relation_rows)
    write_csv(OUTPUT / "10_kernel_subset_resolution_review.csv", ["kernel_id", "kernel_name", "extract01_role", "recommended_for_first_extract02_contract", "resolution_status", "requires_human_freeze", "why_or_why_not", "notes"], kernel_rows)
    write_csv(OUTPUT / "11_cluster_protocol_resolution_review.csv", ["cluster_item", "method_or_requirement", "current_status", "candidate_resolution", "requires_human_freeze", "blocks_future_execution", "notes"], cluster_rows)
    write_csv(OUTPUT / "12_source_selection_query_contract.csv", ["query_contract_id", "source_category", "metadata_filters_required", "eligibility_conditions", "unit_dimension_requirements", "lineage_requirements", "gap_handling", "status", "notes"], query_rows)
    write_csv(OUTPUT / "13_validation_matrix_freeze_review.csv", ["validation_id", "validation_layer", "check_name", "required_before_extract02_precontract", "required_before_future_execution", "current_status", "candidate_resolution", "notes"], validation_rows)
    write_csv(OUTPUT / "14_extract02_readiness_decision.csv", ["decision_id", "readiness_decision", "rationale", "open_blockers_count", "human_freeze_items_count", "allowed_next_action", "forbidden_next_action", "notes"], readiness_rows)
    write_csv(OUTPUT / "15_no_execution_guard.csv", ["guard_id", "guard_item", "status", "evidence", "notes"], guard_rows)
    write_csv(OUTPUT / "16_claim_boundary_matrix.csv", ["statement_id", "statement", "classification", "safe_wording", "forbidden_wording", "notes"], claim_rows)
    write_csv(OUTPUT / "17_review_items_for_extract02_precontract.csv", ["review_item_id", "category", "description", "blocks_extract02_precontract", "blocks_future_execution", "recommended_resolution", "notes"], review_rows)
    (OUTPUT / "18_short_review_note_de.md").write_text(note_de, encoding="utf-8")

    after_hashes = {key: sha256(path) for key, (_, path, _) in artifacts.items() if path.is_file()}
    upstream_unchanged = before_hashes == after_hashes
    manifest["upstream_modified"] = not upstream_unchanged
    (OUTPUT / "01_extract01a_run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    final_note = f"""# QSB-EXTRACT01A Final Result

## Status

`{STATUS}`

## Imported EXTRACT01 Gaps and Prerequisites

Imported: `{len(extract_gaps)}` exact EXTRACT01 gaps and `{len(prerequisites)}` exact prerequisites. The expanded review covers `{len(gap_rows)}` metadata-gap categories.

## Resolution Review

Phase-response vectors and `K_from_phase_response_vectors` are proposed as the first precontract candidates. Source query, four-kernel subset, cluster protocol, and validation matrix are drafted. Numeric distance/edge parameters and all ten prerequisite decisions remain subject to human freeze.

## Readiness Decision

`{READINESS}` with `{open_precontract_blockers}` blockers for contract drafting and `{human_freeze_count}` human-freeze items blocking live extraction.

## No-Execution Boundary

No extraction, Minimaltest, nullmodel, live K/d/D computation, clustering, parameter tuning, feature repair, or database mutation occurred. L2 remains fail.

## Next Allowed Action

Prepare an EXTRACT02 pre-execution contract that records all ten human-freeze decisions. Do not execute extraction until every future-execution blocker is resolved and authorized.
"""
    (OUTPUT / "FINAL_RESULT_NOTE.md").write_text(final_note, encoding="utf-8")

    actual = {path.name for path in OUTPUT.iterdir() if path.is_file()}
    if actual != EXPECTED_FILES:
        raise SystemExit(f"Output file-set mismatch: actual={sorted(actual)} expected={sorted(EXPECTED_FILES)}")
    checks = all([
        len(imported_rows) == 16, len(gap_rows) >= 12, len(prerequisite_rows) == 10,
        len(state_rows) >= 3, len(mode_rows) == 5, len(distance_rows) == 6,
        len(relation_rows) == 6, len(kernel_rows) == 13, len(cluster_rows) == 7,
        len(query_rows) == 4, len(validation_rows) == 11, len(guard_rows) == 10,
        len(review_rows) == 12, readiness_rows[0]["readiness_decision"] == READINESS,
        upstream_unchanged, manifest["extract01_design_only_confirmed"] is True,
        not any(manifest[key] for key in [
            "extraction_executed", "minimaltest_rerun", "nullmodels_rerun", "live_K_computed",
            "live_d_D_computed", "clustering_executed", "theta_or_epsilon_tuned",
            "physical_evidence_claim_made", "upstream_modified",
        ]),
    ])
    if not checks:
        raise SystemExit("EXTRACT01A review validation failed.")
    print(f"status={STATUS}")
    print(f"readiness_decision={READINESS}")
    print(f"metadata_gaps_reviewed={len(gap_rows)}")
    print(f"prerequisites_reviewed={len(prerequisite_rows)}")
    print(f"human_freeze_items={human_freeze_count}")
    print("execution=false")
    print(f"output_files={len(actual)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
