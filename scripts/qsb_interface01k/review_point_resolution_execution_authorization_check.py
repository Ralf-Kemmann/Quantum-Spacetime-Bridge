#!/usr/bin/env python3
"""Resolve INTERFACE01-J review points and check later execution authorization.

This script reads F3/G/H/I/J audit artifacts. It does not execute a Minimaltest.
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REPO = Path(__file__).resolve().parents[2]
F3 = REPO / "runs/QSB-INTERFACE01F3/authorized_delta_phi_export_staging_preflight"
F3_INPUT = REPO / "runs/QSB-INTERFACE01F3/input_manifest/interface01f3_delta_phi_input_manifest.json"
G = REPO / "runs/QSB-INTERFACE01G/minimaltest_design_review_from_staged_delta_phi"
H = REPO / "runs/QSB-INTERFACE01H/controlled_minimal_pilot_from_staged_delta_phi"
I = REPO / "runs/QSB-INTERFACE01I/pilot_result_review_nullmodel_adequacy_decision"
J = REPO / "runs/QSB-INTERFACE01J/minimaltest_precontract"
OUTPUT = REPO / "runs/QSB-INTERFACE01K/review_point_resolution_execution_authorization_check"

STATUS_OK = "interface01k_review_point_resolution_completed_execution_authorization_checked"
STATUS_BLOCKED = "interface01k_review_point_resolution_blocked_missing_upstream"
AUTHORIZED = "authorized_for_separate_minimaltest_execution"
NOT_AUTHORIZED = "not_authorized_review_points_open"
BLOCKED = "blocked_missing_upstream_artifacts"

EXPECTED_STATUSES = {
    "F3": "interface01f3_authorized_delta_phi_export_staging_preflight_completed_export_staged",
    "G": "interface01g_minimaltest_design_review_completed_with_staged_source_profile",
    "H": "interface01h_controlled_minimal_pilot_completed_with_review_items",
    "I": "interface01i_pilot_result_review_completed_nullmodel_adequacy_assessed",
    "J": "interface01j_minimaltest_precontract_completed_conditional_no_execution",
}
EXPECTED_FILES = {
    "01_k_run_manifest.json",
    "02_upstream_artifact_inventory.csv",
    "03_upstream_status_summary.csv",
    "04_review_points_import.csv",
    "05_review_point_resolution_decisions.csv",
    "06_execution_authorization_gate.csv",
    "07_feature_contract_resolution.csv",
    "08_nullmodel_contract_resolution.csv",
    "09_split_seed_theta_epsilon_resolution.csv",
    "10_claim_boundary_and_forbidden_actions.csv",
    "11_k_validation_results.csv",
    "12_review_items_remaining.csv",
    "FINAL_RESULT_NOTE.md",
}
CLAIM_BOUNDARY = (
    "INTERFACE01-K resolves pre-execution contract questions only. It starts no final Minimaltest, "
    "makes no physical-evidence claim, changes no upstream artifact, performs no outcome-driven "
    "tuning, and transfers no Phase-D threshold."
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return str(path.relative_to(REPO))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    if OUTPUT.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {OUTPUT}")

    paths = {
        "f3_manifest": F3 / "01_f3_run_manifest.json",
        "f3_input_preflight": F3 / "04_input_manifest_preflight.csv",
        "f3_db": F3 / "09_delta_phi_staging_preflight.sqlite",
        "f3_gate": F3 / "11_g02_g13_decision.csv",
        "f3_input_manifest": F3_INPUT,
        "g_manifest": G / "01_g_run_manifest.json",
        "g_contract": G / "07_minimaltest_input_contract.csv",
        "g_split": G / "10_split_seed_plan.csv",
        "g_calibration": G / "11_theta_epsilon_calibration_plan.csv",
        "h_manifest": H / "01_h_run_manifest.json",
        "h_split": H / "04_split_assignment_summary.csv",
        "h_nulls": H / "06_null_model_summary.csv",
        "h_script": REPO / "scripts/qsb_interface01h/controlled_minimal_pilot_from_staged_delta_phi.py",
        "i_manifest": I / "01_i_run_manifest.json",
        "i_features": I / "05_feature_signal_stability_review.csv",
        "i_nulls": I / "06_nullmodel_adequacy_matrix.csv",
        "i_design": I / "08_split_seed_calibration_review.csv",
        "i_readiness": I / "09_minimaltest_readiness_decision.csv",
        "i_review": I / "11_review_items.csv",
        "j_manifest": J / "01_j_run_manifest.json",
        "j_features": J / "04_feature_selection_precontract.csv",
        "j_nulls": J / "05_nullmodel_precontract.csv",
        "j_split": J / "06_split_seed_precontract.csv",
        "j_calibration": J / "07_theta_epsilon_calibration_precontract.csv",
        "j_gate": J / "08_execution_gate_matrix.csv",
        "j_review": J / "09_review_item_resolution_contract.csv",
        "j_boundary": J / "11_forbidden_actions_claim_boundary.csv",
    }
    required_keys = set(paths) - {"h_script"}
    upstream_available = all(paths[key].is_file() for key in required_keys)
    before_hashes = {key: sha256(path) for key, path in paths.items() if path.is_file()}

    manifests: dict[str, dict[str, Any]] = {}
    if upstream_available:
        manifests = {
            "F3": load_json(paths["f3_manifest"]),
            "G": load_json(paths["g_manifest"]),
            "H": load_json(paths["h_manifest"]),
            "I": load_json(paths["i_manifest"]),
            "J": load_json(paths["j_manifest"]),
        }
    observed_statuses = {block: data.get("status", "missing") for block, data in manifests.items()}
    statuses_ok = upstream_available and all(
        observed_statuses.get(block) == expected for block, expected in EXPECTED_STATUSES.items()
    )

    review_rows = read_csv(paths["j_review"]) if paths["j_review"].is_file() else []
    expected_ids = {f"I-R{i:02d}" for i in range(1, 8)}
    seven_imported = len(review_rows) == 7 and {row.get("review_item_id") for row in review_rows} == expected_ids

    inventory_specs = [
        ("A01", "F3", "f3_manifest", "status and source scope"),
        ("A02", "F3", "f3_input_manifest", "authorized units, coordinates, and lineage"),
        ("A03", "F3", "f3_input_preflight", "unit and input-hash checks"),
        ("A04", "F3", "f3_db", "read-only staged source"),
        ("A05", "F3", "f3_gate", "G02 and G13 state"),
        ("A06", "G", "g_manifest", "profile status and seed"),
        ("A07", "G", "g_contract", "source and unit contract"),
        ("A08", "G", "g_split", "split and seed design"),
        ("A09", "G", "g_calibration", "legacy-threshold prohibition"),
        ("A10", "H", "h_manifest", "pilot-only status and counts"),
        ("A11", "H", "h_split", "realized deterministic assignments"),
        ("A12", "H", "h_nulls", "nullmodel implementation summary"),
        ("A13", "H", "h_script", "N4 implementation and seed"),
        ("A14", "I", "i_manifest", "readiness and N2 classification"),
        ("A15", "I", "i_features", "feature stability review"),
        ("A16", "I", "i_nulls", "nullmodel adequacy"),
        ("A17", "I", "i_design", "split and calibration review"),
        ("A18", "I", "i_review", "original seven review points"),
        ("A19", "J", "j_manifest", "pre-contract execution state"),
        ("A20", "J", "j_features", "feature pre-contract"),
        ("A21", "J", "j_nulls", "nullmodel pre-contract"),
        ("A22", "J", "j_split", "split and seed pre-contract"),
        ("A23", "J", "j_calibration", "theta and epsilon pre-contract"),
        ("A24", "J", "j_gate", "execution gates before K"),
        ("A25", "J", "j_review", "authoritative review-point import"),
        ("A26", "J", "j_boundary", "forbidden actions"),
    ]
    inventory = []
    for artifact_id, block, key, used_for in inventory_specs:
        path = paths[key]
        inventory.append({
            "artifact_id": artifact_id,
            "upstream_block": block,
            "path": relative(path),
            "exists": "yes" if path.is_file() else "no",
            "sha256": before_hashes.get(key, "missing"),
            "role": "read-only audit input",
            "used_for": used_for,
            "notes": "Hashed before resolution; not modified by K." if path.is_file() else "Required artifact missing.",
        })

    status_source = {"F3": paths["f3_manifest"], "G": paths["g_manifest"], "H": paths["h_manifest"],
                     "I": paths["i_manifest"], "J": paths["j_manifest"]}
    status_summary = []
    for block in ["F3", "G", "H", "I", "J"]:
        observed = observed_statuses.get(block, "missing")
        status_summary.append({
            "block": block,
            "expected_status": EXPECTED_STATUSES[block],
            "observed_status": observed,
            "status_source": relative(status_source[block]),
            "status_match": "yes" if observed == EXPECTED_STATUSES[block] else "no",
            "notes": "Upstream status preserved." if observed == EXPECTED_STATUSES[block] else "Status unavailable or mismatched.",
        })

    imported = []
    for row_number, row in enumerate(review_rows, start=2):
        imported.append({
            "review_point_id": row.get("review_item_id", "missing"),
            "source_block": "INTERFACE01-J",
            "source_path": relative(paths["j_review"]),
            "source_row_or_section": f"CSV row {row_number}",
            "upstream_exact_text": row.get("review_item_text", ""),
            "import_status": "imported_exact" if row.get("review_item_id") in expected_ids else "unexpected_id",
            "blocking_before_k": row.get("blocking_for_execution", "unknown"),
            "notes": "J is the source of truth; wording is copied without revision.",
        })

    principal = {
        "I-R01": "j_nulls", "I-R02": "j_nulls", "I-R03": "j_nulls",
        "I-R04": "j_calibration", "I-R05": "h_split", "I-R06": "j_features", "I-R07": "f3_input_manifest",
    }
    resolution_specs = {
        "I-R01": (
            "nullmodel", "accepted_with_condition",
            "N2 is locked as invariance_check_only and cannot satisfy effective-perturbation adequacy. The locked feature set is x-independent; x-position response is outside this execution contract.",
            "A later x-sensitive endpoint would require a revised contract.", "no",
            "Condition: do not promote N2 or infer x-position sensitivity."
        ),
        "I-R02": (
            "nullmodel", "accepted_resolved",
            "N3 is retained only as a directional consistency sanity check and is not counted as an active perturbation.",
            "N3 cannot satisfy effective-perturbation adequacy.", "no", "Role is locked without promotion."
        ),
        "I-R03": (
            "nullmodel", "not_applicable_with_reason",
            "No label-sensitive endpoint is registered in the frozen compact feature set, so N1 is excluded from mandatory comparators. N4 remains the mandatory effective perturbation comparator.",
            "Label-identity sensitivity is not tested by this contract.", "no", "Adding N1 later requires preregistration of a label-sensitive statistic."
        ),
        "I-R04": (
            "calibration", "accepted_resolved",
            "The J procedures are authorized unchanged: theta_new is the calibration-partition median of abs_correlation_score; epsilon_new is its median absolute deviation. Values are computed once only in a separate execution package and frozen before nullmodel comparison.",
            "No numeric theta_new or epsilon_new exists in K.", "no", "Holdout, final-audit, null outcomes, and Phase-D theta are forbidden inputs."
        ),
        "I-R05": (
            "split", "accepted_resolved",
            "The deterministic ordered-pair assignment with seed 20260620 is accepted with realized counts 20/14/5/3. H labels map to J roles as train_design/calibration/review_holdout/final_audit, with H null_control mapped to final_audit.",
            "Realized fractions differ from nominal 40/30/20/10 targets.", "no", "Pair keys and hash rule remain fixed; no rebalancing is allowed."
        ),
        "I-R06": (
            "feature", "accepted_resolved",
            "Near-flat and neutral outcomes remain visible as controls or diagnostics; none is removed because of pilot appearance. The compact candidate set is inherited unchanged from J.",
            "Controls are not discriminating endpoints.", "no", "No outcome-attractiveness selection is introduced by K."
        ),
        "I-R07": (
            "lineage", "accepted_with_condition",
            "p_i and p_j may be reconstructed only by authorized pair indices from the hashed F3 input manifest; they are not staging columns and no other source is permitted. Their interpretation remains in model units.",
            "Manifest-derived values are not independently staged columns.", "no", "x_dimension_status is preserved from the manifest as model_coordinate_unit_not_SI_converted."
        ),
    }
    decisions = []
    imported_by_id = {row["review_point_id"]: row for row in imported}
    if seven_imported and statuses_ok:
        for review_id in sorted(expected_ids):
            category, decision, basis, risk, blocks, notes = resolution_specs[review_id]
            key = principal[review_id]
            decisions.append({
                "review_point_id": review_id,
                "review_category": category,
                "upstream_exact_text": imported_by_id[review_id]["upstream_exact_text"],
                "resolution_decision": decision,
                "resolution_basis": basis,
                "required_artifact_reference": relative(paths[key]),
                "required_artifact_hash": before_hashes[key],
                "remaining_risk": risk,
                "blocks_execution_after_k": blocks,
                "notes": notes,
            })
    else:
        for row in imported:
            key = principal.get(row["review_point_id"], "j_review")
            decisions.append({
                "review_point_id": row["review_point_id"], "review_category": "unresolved",
                "upstream_exact_text": row["upstream_exact_text"], "resolution_decision": "still_blocking",
                "resolution_basis": "Required upstream state or exact seven-point import is unavailable.",
                "required_artifact_reference": relative(paths[key]), "required_artifact_hash": before_hashes.get(key, "missing"),
                "remaining_risk": "Resolution evidence is incomplete.", "blocks_execution_after_k": "yes",
                "notes": "No resolution inferred from incomplete inputs.",
            })

    accepted = {"accepted_resolved", "accepted_with_condition", "not_applicable_with_reason"}
    resolved_count = sum(row["resolution_decision"] in accepted for row in decisions)
    blocker_count = sum(row["blocks_execution_after_k"] == "yes" for row in decisions)
    if not upstream_available or not statuses_ok or not seven_imported:
        status, authorization = STATUS_BLOCKED, BLOCKED
    elif blocker_count:
        status, authorization = STATUS_OK, NOT_AUTHORIZED
    else:
        status, authorization = STATUS_OK, AUTHORIZED

    feature_rows = []
    if paths["j_features"].is_file():
        selected = {"mean_abs_cos_wrapped_delta", "signed_correlation_score", "abs_correlation_score"}
        for row in read_csv(paths["j_features"]):
            name = row["feature_name"]
            if name in selected:
                decision, future = "locked_selected_candidate", "yes"
            elif "control" in row["allowed_for_minimaltest_candidate"]:
                decision, future = "locked_visible_control", "control_only"
            else:
                decision, future = "locked_audit_or_diagnostic_only", "no"
            feature_rows.append({
                "feature_contract_item": name, "source_artifact": relative(paths["j_features"]),
                "source_hash": before_hashes["j_features"], "decision": decision,
                "used_in_future_execution": future,
                "notes": f"Inherited J status={row['variation_status']}; no K outcome-based reselection.",
            })

    null_rows = []
    if paths["j_nulls"].is_file():
        for row in read_csv(paths["j_nulls"]):
            model_id = row["nullmodel_id"]
            mandatory = "yes" if model_id == "N4_PHASE_RANDOM_REFERENCE" else "sanity_only" if model_id in {
                "N2_X_INDEX_ROLL_SURROGATE", "N3_PAIR_DIRECTION_COLLAPSE"} else "no"
            adequacy = row["adequacy_class"]
            if model_id == "N1_PAIR_LABEL_PERMUTE":
                adequacy = "excluded_no_registered_label_sensitive_endpoint"
            null_rows.append({
                "nullmodel_id": model_id,
                "role": row["nullmodel_role"],
                "adequacy_decision": adequacy,
                "mandatory_for_future_execution": mandatory,
                "limitations": row["limitations"],
                "notes": "N4 implementation is locked to seed 20260620 and the recorded H script hash." if model_id == "N4_PHASE_RANDOM_REFERENCE" else "J limitation preserved.",
            })

    j_calibration = {row["parameter"]: row for row in read_csv(paths["j_calibration"])} if paths["j_calibration"].is_file() else {}
    contract_rows = [
        {"contract_item": "split_rule", "source_artifact": relative(paths["h_split"]), "source_hash": before_hashes.get("h_split", "missing"),
         "observed_value": "sha256(pair_key|INTERFACE01-H|seed=20260620), first8 modulo 10; realized 20/14/5/3; null_control maps to final_audit",
         "decision": "locked_accepted_no_rebalancing", "blocks_execution": "no", "notes": "Ordered-pair assignments remain fixed."},
        {"contract_item": "seed", "source_artifact": relative(paths["j_split"]), "source_hash": before_hashes.get("j_split", "missing"),
         "observed_value": "20260620", "decision": "locked", "blocks_execution": "no", "notes": "Applies to split and deterministic N4 implementation."},
        {"contract_item": "theta_new_rule", "source_artifact": relative(paths["j_calibration"]), "source_hash": before_hashes.get("j_calibration", "missing"),
         "observed_value": j_calibration.get("theta_new", {}).get("calibration_rule", "missing"), "decision": "locked_rule_value_not_computed",
         "blocks_execution": "no", "notes": "Compute once in a separate execution package after source and split hashes are frozen."},
        {"contract_item": "epsilon_new_rule", "source_artifact": relative(paths["j_calibration"]), "source_hash": before_hashes.get("j_calibration", "missing"),
         "observed_value": j_calibration.get("epsilon_new", {}).get("calibration_rule", "missing"), "decision": "locked_rule_value_not_computed",
         "blocks_execution": "no", "notes": "Compute once in a separate execution package before nullmodel comparison."},
        {"contract_item": "post_hoc_tuning_lock", "source_artifact": relative(paths["j_calibration"]), "source_hash": before_hashes.get("j_calibration", "missing"),
         "observed_value": "true", "decision": "locked_prohibited", "blocks_execution": "no", "notes": "Outcome-driven revision is forbidden."},
        {"contract_item": "phase_d_theta_transfer", "source_artifact": relative(paths["g_calibration"]), "source_hash": before_hashes.get("g_calibration", "missing"),
         "observed_value": "theta=0.0300 from Phase D is not transferred", "decision": "locked_prohibited", "blocks_execution": "no", "notes": "No legacy threshold value enters calibration."},
        {"contract_item": "angle_unit", "source_artifact": relative(paths["g_contract"]), "source_hash": before_hashes.get("g_contract", "missing"),
         "observed_value": "rad", "decision": "locked", "blocks_execution": "no", "notes": "dimension_status=dimensionless_angle."},
        {"contract_item": "x_unit", "source_artifact": relative(paths["f3_input_manifest"]), "source_hash": before_hashes.get("f3_input_manifest", "missing"),
         "observed_value": "model_length_unit", "decision": "locked", "blocks_execution": "no", "notes": "x_dimension_status=model_coordinate_unit_not_SI_converted."},
    ]

    boundary_rows = [
        {"boundary_item": "no_final_minimaltest_in_k", "status": "locked", "evidence": "K creates contract-resolution artifacts only.", "notes": "No Minimaltest entry point is called."},
        {"boundary_item": "no_physical_evidence_claim", "status": "locked", "evidence": "Manifest flag is false.", "notes": "K makes an authorization decision only."},
        {"boundary_item": "no_phase_d_theta_transfer", "status": "locked", "evidence": "J calibration disallows Phase-D input.", "notes": "theta=0.0300 from Phase D is not transferred."},
        {"boundary_item": "no_post_hoc_tuning", "status": "locked", "evidence": "J calibration post_hoc_tuning_lock=true.", "notes": "Rules are unchanged and values are absent."},
        {"boundary_item": "no_upstream_mutation", "status": "checked", "evidence": "All hashed upstream files are compared before and after K generation.", "notes": "Any mismatch fails validation."},
        {"boundary_item": "no_synthetic_evidence", "status": "locked", "evidence": "K reads audit artifacts and generates no data rows for scientific inference.", "notes": "Nullmodel contracts are comparator definitions only."},
    ]

    gate_specs = [
        ("K-G01", "upstream_available", "required", upstream_available and statuses_ok, "F3-J required artifacts and statuses checked"),
        ("K-G02", "seven_review_points_imported", "7 blocking", seven_imported, "J review CSV imported exactly"),
        ("K-G03", "review_points_resolved_or_preserved", "0 resolved", blocker_count == 0 and resolved_count == 7, "Accepted-decision policy applied"),
        ("K-G04", "n2_n4_roles_locked", "pending", any(r["nullmodel_id"] == "N2_X_INDEX_ROLL_SURROGATE" and r["adequacy_decision"] == "invariance_check_only" for r in null_rows) and any(r["nullmodel_id"] == "N4_PHASE_RANDOM_REFERENCE" and r["adequacy_decision"] == "effective_perturbation" and r["mandatory_for_future_execution"] == "yes" for r in null_rows), "J/I classifications preserved"),
        ("K-G05", "feature_contract_locked", "proposed", len(feature_rows) == 15 and sum(r["used_in_future_execution"] == "yes" for r in feature_rows) == 3, "J compact candidates inherited"),
        ("K-G06", "split_seed_locked", "pending acceptance", authorization != BLOCKED, "H assignment and J seed explicitly accepted"),
        ("K-G07", "theta_epsilon_locked", "procedures not authorized", len(j_calibration) == 2, "J rules authorized without values"),
        ("K-G08", "claim_boundary_locked", "required", True, "Forbidden actions retained"),
        ("K-G09", "execution_authorization_decision", "not_authorized_pending_review_resolution", authorization == AUTHORIZED, "All K gates and review decisions checked"),
    ]
    gate_rows = []
    for gate_id, name, before, passed, basis in gate_specs:
        after = "satisfied" if passed else "not_satisfied"
        gate_rows.append({
            "gate_id": gate_id, "gate_name": name, "status_before_k": before, "status_after_k": after,
            "decision_basis": basis, "execution_authorization": authorization,
            "allowed_next_action": "prepare a separate execution package/prompt for the final Minimaltest; do not execute inside K" if authorization == AUTHORIZED else "resolve remaining review items; do not execute Minimaltest",
            "forbidden_next_action": "execute a final Minimaltest inside INTERFACE01-K",
        })

    remaining = []
    for row in decisions:
        if row["blocks_execution_after_k"] == "yes":
            remaining.append({
                "review_item_id": f"K-{row['review_point_id']}", "source_review_point_id": row["review_point_id"],
                "remaining_status": "blocking", "required_action": row["resolution_basis"],
                "blocks_execution": "yes", "notes": row["remaining_risk"],
            })

    OUTPUT.mkdir(parents=True)
    manifest = {
        "work_package": "QSB-INTERFACE01K", "status": status,
        "created_at_utc": datetime.now(timezone.utc).isoformat(), "repo_root": str(REPO),
        "upstream_dirs": {"F3": relative(F3), "G": relative(G), "H": relative(H), "I": relative(I), "J": relative(J)},
        "f3_status_seen": observed_statuses.get("F3", "missing"), "g_status_seen": observed_statuses.get("G", "missing"),
        "h_status_seen": observed_statuses.get("H", "missing"), "i_status_seen": observed_statuses.get("I", "missing"),
        "j_status_seen": observed_statuses.get("J", "missing"), "readiness_before_k": manifests.get("I", {}).get("readiness_decision", "missing"),
        "execution_authorization": authorization, "review_points_total": len(review_rows),
        "review_points_resolved_or_accepted": resolved_count, "review_points_remaining_blocking": blocker_count,
        "minimaltest_started": False, "physical_evidence_claim_made": False, "modified_existing_files": [],
        "claim_boundary": CLAIM_BOUNDARY,
    }
    (OUTPUT / "01_k_run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_csv(OUTPUT / "02_upstream_artifact_inventory.csv", ["artifact_id", "upstream_block", "path", "exists", "sha256", "role", "used_for", "notes"], inventory)
    write_csv(OUTPUT / "03_upstream_status_summary.csv", ["block", "expected_status", "observed_status", "status_source", "status_match", "notes"], status_summary)
    write_csv(OUTPUT / "04_review_points_import.csv", ["review_point_id", "source_block", "source_path", "source_row_or_section", "upstream_exact_text", "import_status", "blocking_before_k", "notes"], imported)
    write_csv(OUTPUT / "05_review_point_resolution_decisions.csv", ["review_point_id", "review_category", "upstream_exact_text", "resolution_decision", "resolution_basis", "required_artifact_reference", "required_artifact_hash", "remaining_risk", "blocks_execution_after_k", "notes"], decisions)
    write_csv(OUTPUT / "06_execution_authorization_gate.csv", ["gate_id", "gate_name", "status_before_k", "status_after_k", "decision_basis", "execution_authorization", "allowed_next_action", "forbidden_next_action"], gate_rows)
    write_csv(OUTPUT / "07_feature_contract_resolution.csv", ["feature_contract_item", "source_artifact", "source_hash", "decision", "used_in_future_execution", "notes"], feature_rows)
    write_csv(OUTPUT / "08_nullmodel_contract_resolution.csv", ["nullmodel_id", "role", "adequacy_decision", "mandatory_for_future_execution", "limitations", "notes"], null_rows)
    write_csv(OUTPUT / "09_split_seed_theta_epsilon_resolution.csv", ["contract_item", "source_artifact", "source_hash", "observed_value", "decision", "blocks_execution", "notes"], contract_rows)
    write_csv(OUTPUT / "10_claim_boundary_and_forbidden_actions.csv", ["boundary_item", "status", "evidence", "notes"], boundary_rows)
    write_csv(OUTPUT / "12_review_items_remaining.csv", ["review_item_id", "source_review_point_id", "remaining_status", "required_action", "blocks_execution", "notes"], remaining)

    after_hashes = {key: sha256(path) for key, path in paths.items() if path.is_file()}
    upstream_unchanged = before_hashes == after_hashes
    n2_ok = any(row["nullmodel_id"] == "N2_X_INDEX_ROLL_SURROGATE" and row["adequacy_decision"] == "invariance_check_only" for row in null_rows)
    n4_ok = any(row["nullmodel_id"] == "N4_PHASE_RANDOM_REFERENCE" and row["adequacy_decision"] == "effective_perturbation" and row["mandatory_for_future_execution"] == "yes" for row in null_rows)
    validations: list[dict[str, Any]] = []

    def validate(identifier: str, layer: str, name: str, passed: bool, observed: Any, expected: Any, message: str, blocking: str = "yes") -> None:
        validations.append({
            "validation_id": identifier, "validation_layer": layer, "check_name": name,
            "status": "pass" if passed else "fail", "severity": "error" if blocking == "yes" else "warning",
            "observed_value": observed, "expected_value": expected, "message": message,
            "blocking_for_execution": "no" if passed else blocking,
        })

    validate("K-V01", "upstream", "upstream_dirs_present", upstream_available, upstream_available, True, "Required upstream files are present.")
    f3_gate_ok = paths["f3_gate"].is_file() and any(r.get("gate") == "G02" and r.get("status_after") == "resolved_authorized_export_staged" for r in read_csv(paths["f3_gate"]))
    validate("K-V02", "upstream", "f3_g02_resolved", f3_gate_ok, f3_gate_ok, True, "F3 G02 state checked.")
    g_ok = manifests.get("G", {}).get("profile_checks_passed") is True and manifests.get("G", {}).get("source_row_counts", {}).get("spatial") == 168042
    validate("K-V03", "upstream", "g_profile_complete", g_ok, g_ok, True, "G profile and row count checked.")
    h_ok = manifests.get("H", {}).get("status") == EXPECTED_STATUSES["H"] and manifests.get("H", {}).get("pair_feature_rows") == 42 and manifests.get("H", {}).get("null_models") == 6
    validate("K-V04", "upstream", "h_pilot_complete", h_ok, h_ok, True, "H pilot counts checked.")
    i_ok = manifests.get("I", {}).get("readiness_decision") == "conditional_ready_with_review_items"
    validate("K-V05", "upstream", "i_readiness_conditional", i_ok, manifests.get("I", {}).get("readiness_decision", "missing"), "conditional_ready_with_review_items", "I readiness checked.")
    j_ok = manifests.get("J", {}).get("execution_clearance") == "not_authorized_pending_review_resolution" and manifests.get("J", {}).get("minimaltest_executed") is False
    validate("K-V06", "upstream", "j_precontract_no_execution", j_ok, j_ok, True, "J pre-contract boundary checked.")
    validate("K-V07", "review", "seven_review_points_imported", seven_imported, len(review_rows), 7, "Exact review IDs and count checked.")
    decisions_ok = len(decisions) == 7 and all(row["resolution_decision"] in accepted | {"revised_contract_required", "still_blocking"} for row in decisions)
    validate("K-V08", "review", "review_point_decisions_complete", decisions_ok, len(decisions), 7, "Every imported point has a permitted decision.")
    validate("K-V09", "nullmodel", "n2_invariance_only", n2_ok, n2_ok, True, "N2 remains invariance_check_only.")
    validate("K-V10", "nullmodel", "n4_effective_perturbation", n4_ok, n4_ok, True, "N4 is mandatory and remains effective_perturbation.")
    contract_ok = {r["contract_item"] for r in contract_rows} >= {"split_rule", "seed", "theta_new_rule", "epsilon_new_rule", "post_hoc_tuning_lock", "phase_d_theta_transfer"}
    validate("K-V11", "contract", "split_seed_theta_epsilon_recorded", contract_ok, contract_ok, True, "Required contract items recorded.")
    validate("K-V12", "boundary", "no_minimaltest_started", manifest["minimaltest_started"] is False, manifest["minimaltest_started"], False, "K did not start a Minimaltest.")
    phase_ok = any(r["contract_item"] == "phase_d_theta_transfer" and r["decision"] == "locked_prohibited" for r in contract_rows)
    validate("K-V13", "boundary", "no_phase_d_theta_transfer", phase_ok, phase_ok, True, "Phase-D theta transfer remains prohibited.")
    validate("K-V14", "boundary", "no_physical_evidence_claim", manifest["physical_evidence_claim_made"] is False, manifest["physical_evidence_claim_made"], False, "K makes no physical-evidence claim.")
    auth_consistent = (authorization == AUTHORIZED and blocker_count == 0 and resolved_count == 7) or (authorization != AUTHORIZED and (blocker_count > 0 or not upstream_available or not seven_imported or not statuses_ok))
    validate("K-V15", "authorization", "execution_authorization_consistent", auth_consistent, authorization, "consistent with blockers", "Authorization follows the decision policy.")
    validate("K-V16", "audit", "upstream_hashes_unchanged", upstream_unchanged, upstream_unchanged, True, "Upstream hashes are unchanged after K writes.")
    validate("K-V17", "units", "unit_contract_preserved", all(value in paths["f3_input_manifest"].read_text(encoding="utf-8") for value in ["model_length_unit", "model_coordinate_unit_not_SI_converted", "dimensionless_angle", '"rad"']), True, True, "Angle and model-coordinate units preserved.")
    write_csv(OUTPUT / "11_k_validation_results.csv", ["validation_id", "validation_layer", "check_name", "status", "severity", "observed_value", "expected_value", "message", "blocking_for_execution"], validations)

    next_action = "prepare a separate execution package/prompt for the final Minimaltest; do not execute inside K" if authorization == AUTHORIZED else "resolve remaining review items; do not execute Minimaltest"
    note = f"""# INTERFACE01-K Final Result

## Status

`{status}`

## Execution Authorization

`execution_authorization = {authorization}`

## Review Points

- total: {len(review_rows)}
- resolved/accepted: {resolved_count}
- remaining blocking: {blocker_count}

## Locked Decisions

- N2: `invariance_check_only`; sanity check only.
- N4: `effective_perturbation`; mandatory comparator with seed and implementation hash locked.
- feature contract: three J candidates frozen without outcome-based reselection; controls remain visible.
- split/seed: deterministic ordered-pair assignment, seed `20260620`, realized `20/14/5/3` accepted without rebalancing.
- theta/epsilon: J calibration rules frozen; no value computed in K; no post-hoc tuning.
- claim boundary: contract authorization only; no physical-evidence statement.
- units: `angle_unit=rad`, `dimension_status=dimensionless_angle`, `x_unit=model_length_unit`, `x_dimension_status=model_coordinate_unit_not_SI_converted`.
- Phase-D: `theta=0.0300 from Phase D is not transferred`.

## Minimaltest

No final Minimaltest was started.

## Next allowed action

{next_action}
"""
    (OUTPUT / "FINAL_RESULT_NOTE.md").write_text(note, encoding="utf-8")

    actual_files = {path.name for path in OUTPUT.iterdir() if path.is_file()}
    if actual_files != EXPECTED_FILES:
        raise SystemExit(f"Output file-set mismatch: actual={sorted(actual_files)} expected={sorted(EXPECTED_FILES)}")
    failed = [row["validation_id"] for row in validations if row["status"] == "fail"]
    if failed:
        raise SystemExit(f"K validation failures: {failed}")
    print(f"status={status}")
    print(f"execution_authorization={authorization}")
    print(f"review_points={len(review_rows)}/{resolved_count}/{blocker_count}")
    print(f"output_files={len(actual_files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
