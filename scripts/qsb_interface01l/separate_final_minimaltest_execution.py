#!/usr/bin/env python3
"""Preflight INTERFACE01-L and execute only with a complete J/K contract.

The current J/K contract has no locked pass/fail acceptance criterion. Therefore
this script emits a blocked, auditable L package and does not start the Minimaltest.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REPO = Path(__file__).resolve().parents[2]
F3 = REPO / "runs/QSB-INTERFACE01F3/authorized_delta_phi_export_staging_preflight"
G = REPO / "runs/QSB-INTERFACE01G/minimaltest_design_review_from_staged_delta_phi"
H = REPO / "runs/QSB-INTERFACE01H/controlled_minimal_pilot_from_staged_delta_phi"
I = REPO / "runs/QSB-INTERFACE01I/pilot_result_review_nullmodel_adequacy_decision"
J = REPO / "runs/QSB-INTERFACE01J/minimaltest_precontract"
K = REPO / "runs/QSB-INTERFACE01K/review_point_resolution_execution_authorization_check"
OUTPUT = REPO / "runs/QSB-INTERFACE01L/separate_final_minimaltest_execution"
DB = F3 / "09_delta_phi_staging_preflight.sqlite"

STATUS = "interface01l_separate_final_minimaltest_execution_blocked_contract_incomplete"
RESULT = "blocked_no_execution"
AUTHORIZATION = "authorized_for_separate_minimaltest_execution"
CLAIM_BOUNDARY = (
    "INTERFACE01-L stopped before Minimaltest execution because J/K do not lock a pass/fail "
    "acceptance criterion. This package reports a contract-level start-gate result only, makes "
    "no physical-evidence claim, performs no tuning, and changes no upstream artifact."
)
EXPECTED_FILES = {
    "01_l_run_manifest.json", "02_upstream_authorization_preflight.csv", "03_upstream_hash_status.csv",
    "04_contract_lock_summary.csv", "05_source_data_validation.csv", "06_feature_contract_application.csv",
    "07_final_pair_feature_table.csv", "08_split_assignment.csv", "09_theta_epsilon_application.csv",
    "10_nullmodel_execution_summary.csv", "11_observed_vs_nullmodel_results.csv",
    "12_acceptance_gate_results.csv", "13_claim_boundary_and_interpretation_limits.csv",
    "14_l_validation_results.csv", "FINAL_RESULT_NOTE.md",
}
EXPECTED_STATUSES = {
    "F3": "interface01f3_authorized_delta_phi_export_staging_preflight_completed_export_staged",
    "G": "interface01g_minimaltest_design_review_completed_with_staged_source_profile",
    "H": "interface01h_controlled_minimal_pilot_completed_with_review_items",
    "I": "interface01i_pilot_result_review_completed_nullmodel_adequacy_assessed",
    "J": "interface01j_minimaltest_precontract_completed_conditional_no_execution",
    "K": "interface01k_review_point_resolution_completed_execution_authorization_checked",
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

    manifests_paths = {
        "F3": F3 / "01_f3_run_manifest.json", "G": G / "01_g_run_manifest.json",
        "H": H / "01_h_run_manifest.json", "I": I / "01_i_run_manifest.json",
        "J": J / "01_j_run_manifest.json", "K": K / "01_k_run_manifest.json",
    }
    required_contract_paths = {
        "k_inventory": K / "02_upstream_artifact_inventory.csv",
        "k_features": K / "07_feature_contract_resolution.csv",
        "k_nulls": K / "08_nullmodel_contract_resolution.csv",
        "k_parameters": K / "09_split_seed_theta_epsilon_resolution.csv",
        "j_features": J / "04_feature_selection_precontract.csv",
        "j_nulls": J / "05_nullmodel_precontract.csv",
        "j_split": J / "06_split_seed_precontract.csv",
        "j_parameters": J / "07_theta_epsilon_calibration_precontract.csv",
        "h_split": H / "04_split_assignment_summary.csv",
    }
    all_required = list(manifests_paths.values()) + list(required_contract_paths.values()) + [DB]
    files_available = all(path.is_file() for path in all_required)
    before_hashes = {rel(path): sha256(path) for path in all_required if path.is_file()}
    manifests = {block: load_json(path) for block, path in manifests_paths.items() if path.is_file()}
    status_ok = {block: manifests.get(block, {}).get("status") == expected for block, expected in EXPECTED_STATUSES.items()}

    k_authorization = manifests.get("K", {}).get("execution_authorization", "missing")
    k_authorized = k_authorization == AUTHORIZATION
    k_reviews_ok = (
        manifests.get("K", {}).get("review_points_total") == 7
        and manifests.get("K", {}).get("review_points_resolved_or_accepted") == 7
        and manifests.get("K", {}).get("review_points_remaining_blocking") == 0
    )

    hash_rows = []
    hash_matches = True
    k_inventory = read_csv(required_contract_paths["k_inventory"]) if required_contract_paths["k_inventory"].is_file() else []
    for row in k_inventory:
        path = REPO / row["path"]
        current = sha256(path) if path.is_file() else "missing"
        recorded = row.get("sha256", "not_recorded_in_k") or "not_recorded_in_k"
        match = path.is_file() and recorded == current
        hash_matches = hash_matches and match
        hash_rows.append({
            "artifact_id": row["artifact_id"], "upstream_block": row["upstream_block"], "path": row["path"],
            "k_recorded_hash": recorded, "current_hash": current, "hash_match": "yes" if match else "no",
            "status": "pass" if match else "fail",
            "notes": "Current file matches the K inventory." if match else "Missing or changed artifact blocks execution.",
        })

    source = {
        "row_count": 0, "ordered_pair_count": 0, "x_point_count": 0, "diagonal_row_count": 0,
        "wrapped_min": "not_checked", "wrapped_max": "not_checked", "finite_values": False,
        "angle_unit": "missing", "dimension_status": "missing", "x_unit": "missing",
        "pair_mask_policy": "missing", "wrapped_interval": "missing",
    }
    if DB.is_file():
        connection = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
        row = connection.execute(
            """SELECT COUNT(*), COUNT(DISTINCT pair_i || ':' || pair_j), COUNT(DISTINCT x_index),
                      SUM(CASE WHEN pair_i=pair_j THEN 1 ELSE 0 END),
                      MIN(wrapped_delta_phi_ij_x), MAX(wrapped_delta_phi_ij_x),
                      SUM(CASE WHEN raw_delta_phi_ij_x IS NULL OR wrapped_delta_phi_ij_x IS NULL THEN 1 ELSE 0 END),
                      MIN(angle_unit), MAX(angle_unit), MIN(dimension_status), MAX(dimension_status),
                      MIN(x_unit), MAX(x_unit), MIN(pair_mask), MAX(pair_mask),
                      MIN(wrapping_interval), MAX(wrapping_interval)
               FROM stg_delta_phi_spatial"""
        ).fetchone()
        connection.close()
        source.update({
            "row_count": row[0], "ordered_pair_count": row[1], "x_point_count": row[2],
            "diagonal_row_count": row[3], "wrapped_min": row[4], "wrapped_max": row[5],
            "finite_values": row[6] == 0 and all(math.isfinite(value) for value in (row[4], row[5])),
            "angle_unit": row[8] if row[7] == row[8] else "mixed",
            "dimension_status": row[10] if row[9] == row[10] else "mixed",
            "x_unit": row[12] if row[11] == row[12] else "mixed",
            "pair_mask_policy": "all_accepted" if row[13] == row[14] == 1 else f"range_{row[13]}_{row[14]}",
            "wrapped_interval": row[16] if row[15] == row[16] else "mixed",
        })
    source_valid = all([
        source["row_count"] == 168042, source["ordered_pair_count"] == 42,
        source["x_point_count"] == 4001, source["diagonal_row_count"] == 0,
        source["finite_values"], source["wrapped_min"] >= -math.pi, source["wrapped_max"] < math.pi,
        source["angle_unit"] == "rad", source["dimension_status"] == "dimensionless_angle",
        source["x_unit"] == "model_length_unit", source["pair_mask_policy"] == "all_accepted",
    ])

    k_features = read_csv(required_contract_paths["k_features"]) if required_contract_paths["k_features"].is_file() else []
    selected_features = [row["feature_contract_item"] for row in k_features if row.get("used_in_future_execution") == "yes"]
    k_nulls = read_csv(required_contract_paths["k_nulls"]) if required_contract_paths["k_nulls"].is_file() else []
    n2_ok = any(row["nullmodel_id"] == "N2_X_INDEX_ROLL_SURROGATE" and row["adequacy_decision"] == "invariance_check_only" for row in k_nulls)
    n4_ok = any(row["nullmodel_id"] == "N4_PHASE_RANDOM_REFERENCE" and row["adequacy_decision"] == "effective_perturbation" and row["mandatory_for_future_execution"] == "yes" for row in k_nulls)
    k_parameters = {row["contract_item"]: row for row in read_csv(required_contract_paths["k_parameters"])} if required_contract_paths["k_parameters"].is_file() else {}
    parameter_contract_ok = all(item in k_parameters for item in ["split_rule", "seed", "theta_new_rule", "epsilon_new_rule", "post_hoc_tuning_lock", "phase_d_theta_transfer"])

    # J/K specify inputs, features, split, calibration, and null roles but no rule
    # that maps the locked endpoint/null comparisons to pass or fail.
    acceptance_criteria = "missing_no_locked_pass_fail_rule_in_j_or_k"
    acceptance_executable = False
    contract_complete = (
        len(selected_features) == 3 and n2_ok and n4_ok and parameter_contract_ok and acceptance_executable
    )

    hard_gates = [
        ("L-G01", "F3 staged source exists and status is valid", "F3", manifests_paths["F3"], status_ok.get("F3", False) and DB.is_file(), EXPECTED_STATUSES["F3"], manifests.get("F3", {}).get("status", "missing"), "F3 source and status checked."),
        ("L-G02", "G profile exists and status is valid", "G", manifests_paths["G"], status_ok.get("G", False), EXPECTED_STATUSES["G"], manifests.get("G", {}).get("status", "missing"), "G status checked."),
        ("L-G03", "H pilot exists and status is valid", "H", manifests_paths["H"], status_ok.get("H", False), EXPECTED_STATUSES["H"], manifests.get("H", {}).get("status", "missing"), "H status checked."),
        ("L-G04", "I review exists and status is valid", "I", manifests_paths["I"], status_ok.get("I", False), EXPECTED_STATUSES["I"], manifests.get("I", {}).get("status", "missing"), "I status checked."),
        ("L-G05", "J precontract exists and status is valid", "J", manifests_paths["J"], status_ok.get("J", False), EXPECTED_STATUSES["J"], manifests.get("J", {}).get("status", "missing"), "J status checked."),
        ("L-G06", "K separate execution authorization", "K", manifests_paths["K"], k_authorized, AUTHORIZATION, k_authorization, "K authorization is exact."),
        ("L-G07", "K review points accepted", "K", manifests_paths["K"], k_reviews_ok, "7/7 accepted; 0 blocking", f"{manifests.get('K', {}).get('review_points_resolved_or_accepted', 'missing')}/7 accepted; {manifests.get('K', {}).get('review_points_remaining_blocking', 'missing')} blocking", "K review counts checked."),
        ("L-G08", "upstream hashes match K inventory", "K", required_contract_paths["k_inventory"], hash_matches and len(hash_rows) > 0, "all recorded hashes match", f"{sum(r['hash_match']=='yes' for r in hash_rows)}/{len(hash_rows)} match", "Every K-recorded upstream artifact was checked."),
        ("L-G09", "machine-readable executable contract", "J/K", required_contract_paths["k_parameters"], contract_complete, "feature/null/split/parameter/acceptance rules complete", acceptance_criteria, "Blocking: no locked acceptance criterion maps endpoint/null comparisons to pass or fail."),
        ("L-G10", "no Phase-D theta transfer", "G/J/K", required_contract_paths["k_parameters"], k_parameters.get("phase_d_theta_transfer", {}).get("decision") == "locked_prohibited", "locked_prohibited", k_parameters.get("phase_d_theta_transfer", {}).get("decision", "missing"), "Legacy threshold transfer remains prohibited."),
    ]
    preflight_rows = [{
        "gate_id": gate_id, "gate_name": name, "source_block": block, "source_artifact": rel(path),
        "observed_value": observed, "expected_value": expected, "status": "pass" if passed else "fail",
        "blocking": "yes", "notes": notes,
    } for gate_id, name, block, path, passed, expected, observed, notes in hard_gates]
    hard_start_passed = all(item[4] for item in hard_gates)
    if hard_start_passed:
        raise SystemExit("Internal safety error: this blocked-package implementation must not execute a Minimaltest.")

    contract_rows = [
        {"contract_item": "feature_set", "source_block": "K", "source_artifact": rel(required_contract_paths["k_features"]), "source_hash": sha256(required_contract_paths["k_features"]), "locked_value": ";".join(selected_features), "executable": "yes", "blocking_if_missing": "yes", "notes": "Three selected endpoints are locked but not computed because a hard start gate fails."},
        {"contract_item": "nullmodels", "source_block": "K", "source_artifact": rel(required_contract_paths["k_nulls"]), "source_hash": sha256(required_contract_paths["k_nulls"]), "locked_value": ";".join(row["nullmodel_id"] for row in k_nulls), "executable": "yes", "blocking_if_missing": "yes", "notes": "Roles are machine-readable; execution was not started."},
        {"contract_item": "N2_role", "source_block": "K", "source_artifact": rel(required_contract_paths["k_nulls"]), "source_hash": sha256(required_contract_paths["k_nulls"]), "locked_value": "invariance_check_only", "executable": "yes", "blocking_if_missing": "yes", "notes": "Cannot be used as perturbation separation."},
        {"contract_item": "N4_role", "source_block": "K", "source_artifact": rel(required_contract_paths["k_nulls"]), "source_hash": sha256(required_contract_paths["k_nulls"]), "locked_value": "effective_perturbation; mandatory", "executable": "yes", "blocking_if_missing": "yes", "notes": "Mandatory comparator role is locked."},
        {"contract_item": "split_rule", "source_block": "K", "source_artifact": k_parameters.get("split_rule", {}).get("source_artifact", rel(required_contract_paths["h_split"])), "source_hash": k_parameters.get("split_rule", {}).get("source_hash", "missing"), "locked_value": k_parameters.get("split_rule", {}).get("observed_value", "missing"), "executable": "yes", "blocking_if_missing": "yes", "notes": "Not applied after L-G09 failed."},
        {"contract_item": "seed", "source_block": "K", "source_artifact": k_parameters.get("seed", {}).get("source_artifact", rel(required_contract_paths["j_split"])), "source_hash": k_parameters.get("seed", {}).get("source_hash", "missing"), "locked_value": k_parameters.get("seed", {}).get("observed_value", "missing"), "executable": "yes", "blocking_if_missing": "yes", "notes": "Seed is locked to 20260620."},
        {"contract_item": "theta_new_rule", "source_block": "J/K", "source_artifact": k_parameters.get("theta_new_rule", {}).get("source_artifact", rel(required_contract_paths["j_parameters"])), "source_hash": k_parameters.get("theta_new_rule", {}).get("source_hash", "missing"), "locked_value": k_parameters.get("theta_new_rule", {}).get("observed_value", "missing"), "executable": "yes", "blocking_if_missing": "yes", "notes": "Value not computed after L-G09 failed."},
        {"contract_item": "epsilon_new_rule", "source_block": "J/K", "source_artifact": k_parameters.get("epsilon_new_rule", {}).get("source_artifact", rel(required_contract_paths["j_parameters"])), "source_hash": k_parameters.get("epsilon_new_rule", {}).get("source_hash", "missing"), "locked_value": k_parameters.get("epsilon_new_rule", {}).get("observed_value", "missing"), "executable": "yes", "blocking_if_missing": "yes", "notes": "Value not computed after L-G09 failed."},
        {"contract_item": "acceptance_criteria", "source_block": "J/K", "source_artifact": rel(required_contract_paths["k_parameters"]), "source_hash": sha256(required_contract_paths["k_parameters"]), "locked_value": acceptance_criteria, "executable": "no", "blocking_if_missing": "yes", "notes": "No preregistered boolean or ordered decision rule links selected endpoints, theta/epsilon, and N4 to pass/fail."},
        {"contract_item": "claim_boundary", "source_block": "K", "source_artifact": rel(manifests_paths["K"]), "source_hash": sha256(manifests_paths["K"]), "locked_value": manifests["K"]["claim_boundary"], "executable": "yes", "blocking_if_missing": "yes", "notes": "Preserved by L."},
    ]

    source_expectations = [
        ("row_count", source["row_count"], 168042, source["row_count"] == 168042, "Exact staged row count."),
        ("ordered_pair_count", source["ordered_pair_count"], 42, source["ordered_pair_count"] == 42, "Distinct ordered pairs."),
        ("x_point_count", source["x_point_count"], 4001, source["x_point_count"] == 4001, "Distinct x indices."),
        ("diagonal_row_count", source["diagonal_row_count"], 0, source["diagonal_row_count"] == 0, "Diagonal pairs excluded."),
        ("wrapped_min", source["wrapped_min"], ">=-pi", source["wrapped_min"] != "not_checked" and source["wrapped_min"] >= -math.pi, "Observed read-only minimum."),
        ("wrapped_max", source["wrapped_max"], "<pi", source["wrapped_max"] != "not_checked" and source["wrapped_max"] < math.pi, "Observed read-only maximum."),
        ("wrapped_interval", source["wrapped_interval"], "[-pi, pi)", source["wrapped_interval"] == "[-pi, pi)", "Declared wrapping interval."),
        ("finite_values", source["finite_values"], True, source["finite_values"] is True, "Raw/wrapped values are non-null and extrema finite."),
        ("angle_unit", source["angle_unit"], "rad", source["angle_unit"] == "rad", "Angle unit preserved."),
        ("dimension_status", source["dimension_status"], "dimensionless_angle", source["dimension_status"] == "dimensionless_angle", "Angle dimension status preserved."),
        ("x_unit", source["x_unit"], "model_length_unit", source["x_unit"] == "model_length_unit", "Model coordinate unit preserved."),
        ("pair_mask_policy", source["pair_mask_policy"], "all_accepted", source["pair_mask_policy"] == "all_accepted", "All staged rows pass the pair mask."),
    ]
    source_rows = [{
        "validation_item": name, "observed_value": observed, "expected_value": expected,
        "status": "pass" if passed else "fail", "blocking": "yes", "notes": notes,
    } for name, observed, expected, passed, notes in source_expectations]

    feature_rows = []
    for row in k_features:
        feature_rows.append({
            "feature_name": row["feature_contract_item"],
            "source_rule": f"Inherited from {row['source_artifact']}; H computation not rerun after hard-gate failure.",
            "unit_status": "model coordinate or dimensionless aggregate as defined upstream",
            "dimension_status": "inherited_not_recomputed",
            "used_in_minimaltest": row["used_in_future_execution"],
            "application_status": "not_applied_contract_incomplete",
            "notes": "Feature role documented; no final feature value generated in L.",
        })

    null_rows = []
    for row in k_nulls:
        mandatory = row["mandatory_for_future_execution"]
        role = row["adequacy_decision"]
        null_rows.append({
            "nullmodel_id": row["nullmodel_id"], "role": role, "mandatory": mandatory,
            "executed": "no", "used_in_acceptance_gate": "no",
            "primary_metric": "not_computed", "primary_metric_value": "not_computed",
            "limitation": row["limitations"], "status": "not_executed_hard_start_gate_failed",
            "notes": "N2 remains invariance_check_only." if row["nullmodel_id"] == "N2_X_INDEX_ROLL_SURROGATE" else "No nullmodel executed after L-G09 failed.",
        })

    parameter_rows = [
        {"parameter_name": "theta_new", "rule": k_parameters.get("theta_new_rule", {}).get("observed_value", "missing"), "source_artifact": k_parameters.get("theta_new_rule", {}).get("source_artifact", "missing"), "source_hash": k_parameters.get("theta_new_rule", {}).get("source_hash", "missing"), "computed_value": "not_computed", "application_scope": "locked calibration partition only", "status": "not_applied_contract_incomplete", "notes": "Hard start gate failed before calibration."},
        {"parameter_name": "epsilon_new", "rule": k_parameters.get("epsilon_new_rule", {}).get("observed_value", "missing"), "source_artifact": k_parameters.get("epsilon_new_rule", {}).get("source_artifact", "missing"), "source_hash": k_parameters.get("epsilon_new_rule", {}).get("source_hash", "missing"), "computed_value": "not_computed", "application_scope": "locked calibration partition only", "status": "not_applied_contract_incomplete", "notes": "Hard start gate failed before calibration."},
        {"parameter_name": "phase_d_theta_0300_transfer_check", "rule": "theta=0.0300 from Phase D is not transferred", "source_artifact": k_parameters.get("phase_d_theta_transfer", {}).get("source_artifact", "missing"), "source_hash": k_parameters.get("phase_d_theta_transfer", {}).get("source_hash", "missing"), "computed_value": "not_transferred", "application_scope": "all L stages", "status": "pass", "notes": "Legacy value was not used."},
        {"parameter_name": "post_hoc_tuning_check", "rule": "post_hoc_tuning_lock=true", "source_artifact": k_parameters.get("post_hoc_tuning_lock", {}).get("source_artifact", "missing"), "source_hash": k_parameters.get("post_hoc_tuning_lock", {}).get("source_hash", "missing"), "computed_value": "none", "application_scope": "all L stages", "status": "pass", "notes": "No parameter was computed or revised."},
    ]

    acceptance_rows = []
    for gate_id, name, _, _, passed, expected, observed, notes in hard_gates:
        acceptance_rows.append({
            "acceptance_gate_id": gate_id, "gate_name": name, "rule": f"must equal {expected}",
            "observed_value": observed, "expected_or_threshold": expected,
            "status": "pass" if passed else "fail", "blocking": "yes", "notes": notes,
        })
    acceptance_rows.append({
        "acceptance_gate_id": "L-ACCEPT-FINAL", "gate_name": "final contract disposition",
        "rule": "all hard start gates pass before Minimaltest execution",
        "observed_value": "L-G09 failed; minimaltest_started=false", "expected_or_threshold": "all L-G01 through L-G10 pass",
        "status": RESULT, "blocking": "yes",
        "notes": "No pass/fail result is computed because the Minimaltest was not started.",
    })

    boundary_rows = [
        {"boundary_item": "contract_result_only", "status": "locked", "evidence": RESULT, "notes": "This is a start-gate disposition only."},
        {"boundary_item": "no_gravity_claim", "status": "locked", "evidence": "No such interpretation is made.", "notes": "Contract scope only."},
        {"boundary_item": "no_spacetime_emergence_claim", "status": "locked", "evidence": "No such interpretation is made.", "notes": "Contract scope only."},
        {"boundary_item": "no_quantum_gravity_claim", "status": "locked", "evidence": "No such interpretation is made.", "notes": "Contract scope only."},
        {"boundary_item": "no_phase_d_theta_transfer", "status": "pass", "evidence": "phase_d_theta_transferred=false", "notes": "Legacy threshold unused."},
        {"boundary_item": "no_post_hoc_tuning", "status": "pass", "evidence": "post_hoc_tuning_detected=false", "notes": "No calibration occurred."},
        {"boundary_item": "no_synthetic_evidence", "status": "pass", "evidence": "No feature or nullmodel execution rows generated.", "notes": "Source checks are metadata validation only."},
        {"boundary_item": "no_upstream_mutation", "status": "checked", "evidence": "Upstream hashes compared before and after output creation.", "notes": "Any mismatch is a validation failure."},
    ]

    OUTPUT.mkdir(parents=True)
    manifest = {
        "work_package": "QSB-INTERFACE01L", "status": STATUS,
        "created_at_utc": datetime.now(timezone.utc).isoformat(), "repo_root": str(REPO),
        "upstream_dirs": {"F3": rel(F3), "G": rel(G), "H": rel(H), "I": rel(I), "J": rel(J), "K": rel(K)},
        "k_execution_authorization_seen": k_authorization, "minimaltest_started": False,
        "minimaltest_completed": False, "minimaltest_contract_result": RESULT,
        "source_rows_seen": source["row_count"], "ordered_pairs_seen": source["ordered_pair_count"],
        "x_points_seen": source["x_point_count"], "features_used_count": 0,
        "nullmodels_required_count": sum(row["mandatory_for_future_execution"] == "yes" for row in k_nulls),
        "nullmodels_executed_count": 0, "phase_d_theta_transferred": False,
        "post_hoc_tuning_detected": False, "physical_evidence_claim_made": False,
        "modified_existing_files": [], "claim_boundary": CLAIM_BOUNDARY,
    }
    (OUTPUT / "01_l_run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_csv(OUTPUT / "02_upstream_authorization_preflight.csv", ["gate_id", "gate_name", "source_block", "source_artifact", "observed_value", "expected_value", "status", "blocking", "notes"], preflight_rows)
    write_csv(OUTPUT / "03_upstream_hash_status.csv", ["artifact_id", "upstream_block", "path", "k_recorded_hash", "current_hash", "hash_match", "status", "notes"], hash_rows)
    write_csv(OUTPUT / "04_contract_lock_summary.csv", ["contract_item", "source_block", "source_artifact", "source_hash", "locked_value", "executable", "blocking_if_missing", "notes"], contract_rows)
    write_csv(OUTPUT / "05_source_data_validation.csv", ["validation_item", "observed_value", "expected_value", "status", "blocking", "notes"], source_rows)
    write_csv(OUTPUT / "06_feature_contract_application.csv", ["feature_name", "source_rule", "unit_status", "dimension_status", "used_in_minimaltest", "application_status", "notes"], feature_rows)
    feature_fields = ["pair_key", "pair_i", "pair_j", "split_label"] + [row["feature_contract_item"] for row in k_features]
    write_csv(OUTPUT / "07_final_pair_feature_table.csv", feature_fields, [])
    write_csv(OUTPUT / "08_split_assignment.csv", ["pair_key", "pair_i", "pair_j", "split_label", "split_rule", "seed", "source_artifact", "source_hash", "notes"], [])
    write_csv(OUTPUT / "09_theta_epsilon_application.csv", ["parameter_name", "rule", "source_artifact", "source_hash", "computed_value", "application_scope", "status", "notes"], parameter_rows)
    write_csv(OUTPUT / "10_nullmodel_execution_summary.csv", ["nullmodel_id", "role", "mandatory", "executed", "used_in_acceptance_gate", "primary_metric", "primary_metric_value", "limitation", "status", "notes"], null_rows)
    write_csv(OUTPUT / "11_observed_vs_nullmodel_results.csv", ["comparison_id", "feature_or_metric", "observed_value", "nullmodel_id", "nullmodel_value", "difference", "effect_direction", "contract_relevance", "status", "notes"], [])
    write_csv(OUTPUT / "12_acceptance_gate_results.csv", ["acceptance_gate_id", "gate_name", "rule", "observed_value", "expected_or_threshold", "status", "blocking", "notes"], acceptance_rows)
    write_csv(OUTPUT / "13_claim_boundary_and_interpretation_limits.csv", ["boundary_item", "status", "evidence", "notes"], boundary_rows)

    after_hashes = {rel(path): sha256(path) for path in all_required if path.is_file()}
    upstream_unchanged = before_hashes == after_hashes
    validations = []

    def validate(identifier: str, name: str, passed: bool, observed: Any, expected: Any, message: str, severity: str = "error") -> None:
        validations.append({
            "validation_id": identifier, "validation_layer": "L preflight", "check_name": name,
            "status": "pass" if passed else "fail", "severity": severity,
            "observed_value": observed, "expected_value": expected, "message": message,
            "blocking_for_result": "no" if passed else "yes",
        })

    validate("L-V01", "f3_available_and_valid", status_ok.get("F3", False) and DB.is_file(), manifests.get("F3", {}).get("status", "missing"), EXPECTED_STATUSES["F3"], "F3 status and DB checked.")
    validate("L-V02", "g_available_and_valid", status_ok.get("G", False), manifests.get("G", {}).get("status", "missing"), EXPECTED_STATUSES["G"], "G status checked.")
    validate("L-V03", "h_available_and_valid", status_ok.get("H", False), manifests.get("H", {}).get("status", "missing"), EXPECTED_STATUSES["H"], "H status checked.")
    validate("L-V04", "i_available_and_valid", status_ok.get("I", False), manifests.get("I", {}).get("status", "missing"), EXPECTED_STATUSES["I"], "I status checked.")
    validate("L-V05", "j_available_and_valid", status_ok.get("J", False), manifests.get("J", {}).get("status", "missing"), EXPECTED_STATUSES["J"], "J status checked.")
    validate("L-V06", "k_authorized", k_authorized and k_reviews_ok, k_authorization, AUTHORIZATION, "K authorization and review counts checked.")
    validate("L-V07", "upstream_hashes_match_or_documented", hash_matches, f"{sum(r['hash_match']=='yes' for r in hash_rows)}/{len(hash_rows)}", f"{len(hash_rows)}/{len(hash_rows)}", "K inventory hashes checked.")
    validate("L-V08", "source_row_count_valid", source["row_count"] == 168042, source["row_count"], 168042, "Read-only source row count checked.")
    validate("L-V09", "pair_and_x_coverage_valid", source["ordered_pair_count"] == 42 and source["x_point_count"] == 4001, f"{source['ordered_pair_count']}/{source['x_point_count']}", "42/4001", "Pair and x coverage checked.")
    validate("L-V10", "feature_contract_applied", not hard_start_passed and all(r["application_status"] == "not_applied_contract_incomplete" for r in feature_rows), "not applied", "not applied after failed hard gate", "Feature computation correctly did not start.")
    validate("L-V11", "nullmodels_executed_or_documented", len(null_rows) == 6 and all(r["executed"] == "no" for r in null_rows), "6 documented; 0 executed", "no execution after failed hard gate", "Nullmodel roles documented without execution.")
    validate("L-V12", "n2_invariance_only", n2_ok, n2_ok, True, "N2 role preserved.")
    validate("L-V13", "n4_effective_perturbation", n4_ok, n4_ok, True, "N4 role preserved.")
    validate("L-V14", "theta_epsilon_contract_applied", all(r["computed_value"] == "not_computed" for r in parameter_rows[:2]), "not computed", "not computed after failed hard gate", "Calibration correctly did not start.")
    validate("L-V15", "no_phase_d_theta_transfer", manifest["phase_d_theta_transferred"] is False, manifest["phase_d_theta_transferred"], False, "Legacy threshold was not transferred.")
    validate("L-V16", "no_post_hoc_tuning", manifest["post_hoc_tuning_detected"] is False, manifest["post_hoc_tuning_detected"], False, "No tuning occurred.")
    validate("L-V17", "acceptance_gate_consistent", RESULT == "blocked_no_execution" and not hard_start_passed and manifest["minimaltest_started"] is False, RESULT, "blocked_no_execution", "Final disposition follows failed L-G09.")
    validate("L-V18", "no_physical_evidence_claim", manifest["physical_evidence_claim_made"] is False, manifest["physical_evidence_claim_made"], False, "No physical-evidence claim is made.")
    validate("L-V19", "no_upstream_mutation", upstream_unchanged, upstream_unchanged, True, "Upstream hashes unchanged after L output writes.")
    validate("L-V20", "acceptance_criteria_complete", acceptance_executable, acceptance_criteria, "locked executable pass/fail rule", "Contract incompleteness is the expected blocking condition.")
    write_csv(OUTPUT / "14_l_validation_results.csv", ["validation_id", "validation_layer", "check_name", "status", "severity", "observed_value", "expected_value", "message", "blocking_for_result"], validations)

    note = f"""# INTERFACE01-L Final Result

## Status

`{STATUS}`

## Minimaltest Contract Result

`{RESULT}`

## Execution Boundary

K authorized a separate execution package, but L-G09 failed because J/K contain no locked pass/fail acceptance criterion. The Minimaltest was not started.

## Input Source

The authorized F3 staging database was opened read-only for preflight metadata validation: `{source['row_count']}` rows, `{source['ordered_pair_count']}` ordered pairs, `{source['x_point_count']}` x-points.

## Contract Application

Feature roles, split/seed, and theta/epsilon rules were found and recorded. No feature values, split rows, or parameter values were generated after the hard-gate failure.

## Nullmodels

N2 remains `invariance_check_only`; N4 remains the mandatory `effective_perturbation` comparator. No nullmodel was executed.

## Acceptance Gates

L-G01 through L-G08 and L-G10 passed. L-G09 failed: no preregistered rule maps the selected endpoints and N4 comparison to `pass` or `fail`.

## Claim Boundary

No physical evidence claim is made here.

## Next allowed action

resolve blocking start gate; do not execute Minimaltest
"""
    (OUTPUT / "FINAL_RESULT_NOTE.md").write_text(note, encoding="utf-8")

    actual = {path.name for path in OUTPUT.iterdir() if path.is_file()}
    if actual != EXPECTED_FILES:
        raise SystemExit(f"Output file-set mismatch: actual={sorted(actual)} expected={sorted(EXPECTED_FILES)}")
    print(f"status={STATUS}")
    print(f"minimaltest_contract_result={RESULT}")
    print(f"k_authorization={k_authorization}")
    print(f"source={source['row_count']}/{source['ordered_pair_count']}/{source['x_point_count']}")
    print("minimaltest_started=false")
    print(f"output_files={len(actual)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
