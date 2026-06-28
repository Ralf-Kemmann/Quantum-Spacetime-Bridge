#!/usr/bin/env python3
"""Create the INTERFACE01-J2 acceptance-rule addendum without data execution."""

from __future__ import annotations

import csv
import hashlib
import json
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
L = REPO / "runs/QSB-INTERFACE01L/separate_final_minimaltest_execution"
OUTPUT = REPO / "runs/QSB-INTERFACE01J2/minimaltest_acceptance_rule_addendum"

STATUS_OK = "interface01j2_acceptance_rule_addendum_completed_authorized_for_l_replay"
STATUS_NOT_AUTHORIZED = "interface01j2_acceptance_rule_addendum_completed_not_authorized"
STATUS_MISSING = "interface01j2_acceptance_rule_addendum_blocked_missing_upstream"
AUTHORIZED = "authorized_for_separate_minimaltest_execution_with_acceptance_rule"
NOT_AUTHORIZED = "not_authorized_acceptance_rule_unresolved"
BLOCKED = "blocked_missing_upstream_artifacts"
EXPECTED_L_STATUS = "interface01l_separate_final_minimaltest_execution_blocked_contract_incomplete"
EXPECTED_L_RESULT = "blocked_no_execution"
K_AUTHORIZATION = "authorized_for_separate_minimaltest_execution"
CLAIM_BOUNDARY = (
    "INTERFACE01-J2 adds a preregistered contract-level acceptance rule only. It executes no "
    "Minimaltest or nullmodel, computes no final comparison, performs no outcome-driven tuning, "
    "transfers no Phase-D threshold, and makes no physical-evidence claim."
)
EXPECTED_FILES = {
    "01_j2_run_manifest.json", "02_upstream_inventory_and_hashes.csv", "03_l_blocker_confirmation.csv",
    "04_locked_contract_scope.csv", "05_acceptance_rule_addendum.csv", "06_feature_acceptance_gates.csv",
    "07_nullmodel_acceptance_roles.csv", "08_result_decision_table.csv",
    "09_execution_authorization_after_j2.csv", "10_claim_boundary_and_forbidden_actions.csv",
    "11_j2_validation_results.csv", "12_review_items_remaining.csv", "FINAL_RESULT_NOTE.md",
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

    artifacts = {
        "f3_manifest": ("F3", F3 / "01_f3_run_manifest.json", "source status and scope"),
        "f3_db": ("F3", F3 / "09_delta_phi_staging_preflight.sqlite", "authorized staged source"),
        "g_manifest": ("G", G / "01_g_run_manifest.json", "profile status"),
        "g_contract": ("G", G / "07_minimaltest_input_contract.csv", "source and unit contract"),
        "h_manifest": ("H", H / "01_h_run_manifest.json", "pilot status and counts"),
        "h_features": ("H", H / "03_pair_feature_table.csv", "feature definitions and columns"),
        "h_nulls": ("H", H / "06_null_model_summary.csv", "nullmodel implementation summary"),
        "i_manifest": ("I", I / "01_i_run_manifest.json", "readiness status"),
        "i_nulls": ("I", I / "06_nullmodel_adequacy_matrix.csv", "nullmodel adequacy"),
        "j_manifest": ("J", J / "01_j_run_manifest.json", "pre-contract status"),
        "j_features": ("J", J / "04_feature_selection_precontract.csv", "feature pre-contract"),
        "j_nulls": ("J", J / "05_nullmodel_precontract.csv", "nullmodel pre-contract"),
        "j_split": ("J", J / "06_split_seed_precontract.csv", "split and seed rules"),
        "j_parameters": ("J", J / "07_theta_epsilon_calibration_precontract.csv", "parameter rules"),
        "k_manifest": ("K", K / "01_k_run_manifest.json", "execution authorization"),
        "k_features": ("K", K / "07_feature_contract_resolution.csv", "locked feature roles"),
        "k_nulls": ("K", K / "08_nullmodel_contract_resolution.csv", "locked nullmodel roles"),
        "k_parameters": ("K", K / "09_split_seed_theta_epsilon_resolution.csv", "locked split and parameter rules"),
        "l_manifest": ("L", L / "01_l_run_manifest.json", "blocked execution disposition"),
        "l_preflight": ("L", L / "02_upstream_authorization_preflight.csv", "L-G09 blocker"),
        "l_contract": ("L", L / "04_contract_lock_summary.csv", "missing acceptance criterion record"),
        "l_acceptance": ("L", L / "12_acceptance_gate_results.csv", "blocked final disposition"),
    }
    upstream_present = all(path.is_file() for _, path, _ in artifacts.values())
    before_hashes = {key: sha256(path) for key, (_, path, _) in artifacts.items() if path.is_file()}
    inventory_rows = []
    for number, (key, (block, path, use)) in enumerate(artifacts.items(), start=1):
        exists = path.is_file()
        inventory_rows.append({
            "artifact_id": f"J2-A{number:02d}", "upstream_block": block, "path": rel(path),
            "exists": "yes" if exists else "no", "sha256": before_hashes.get(key, "missing"),
            "role": "read-only upstream artifact", "used_for": use,
            "notes": "Hashed before J2; not modified." if exists else "Missing upstream artifact.",
        })

    k_manifest = load_json(artifacts["k_manifest"][1]) if artifacts["k_manifest"][1].is_file() else {}
    l_manifest = load_json(artifacts["l_manifest"][1]) if artifacts["l_manifest"][1].is_file() else {}
    l_preflight = read_csv(artifacts["l_preflight"][1]) if artifacts["l_preflight"][1].is_file() else []
    l_contract = read_csv(artifacts["l_contract"][1]) if artifacts["l_contract"][1].is_file() else []
    l_gate = {row.get("gate_id"): row for row in l_preflight}
    l_contract_by_item = {row.get("contract_item"): row for row in l_contract}
    blocker_text = l_contract_by_item.get("acceptance_criteria", {}).get("locked_value", "missing")
    l_blocker_confirmed = all([
        l_manifest.get("status") == EXPECTED_L_STATUS,
        l_manifest.get("minimaltest_contract_result") == EXPECTED_L_RESULT,
        l_manifest.get("minimaltest_started") is False,
        l_gate.get("L-G09", {}).get("status") == "fail",
        blocker_text == "missing_no_locked_pass_fail_rule_in_j_or_k",
    ])
    blocker_rows = [{
        "blocker_id": "J2-B01", "l_status_seen": l_manifest.get("status", "missing"),
        "l_result_seen": l_manifest.get("minimaltest_contract_result", "missing"),
        "blocker_text": "missing pre-specified pass/fail acceptance rule in J/K",
        "confirmed": "yes" if l_blocker_confirmed else "no", "blocking_layer": "L-G09 contract completeness",
        "notes": "L-G01 through L-G08 and L-G10 passed; L-G09 was the only failed hard start gate." if l_blocker_confirmed else "L blocker could not be confirmed exactly.",
    }]

    k_features = read_csv(artifacts["k_features"][1]) if artifacts["k_features"][1].is_file() else []
    feature_names = [row["feature_contract_item"] for row in k_features if row.get("used_in_future_execution") == "yes"]
    expected_features = {"mean_abs_cos_wrapped_delta", "signed_correlation_score", "abs_correlation_score"}
    features_ok = len(feature_names) == 3 and set(feature_names) == expected_features
    k_nulls = read_csv(artifacts["k_nulls"][1]) if artifacts["k_nulls"][1].is_file() else []
    null_by_id = {row["nullmodel_id"]: row for row in k_nulls}
    expected_nulls = {
        "N0_SIGN_FLIP", "N1_PAIR_LABEL_PERMUTE", "N2_X_INDEX_ROLL_SURROGATE",
        "N3_PAIR_DIRECTION_COLLAPSE", "N4_PHASE_RANDOM_REFERENCE", "N5_CONSTANT_ZERO_PHASE_REFERENCE",
    }
    nulls_ok = len(k_nulls) == 6 and set(null_by_id) == expected_nulls
    n2_ok = null_by_id.get("N2_X_INDEX_ROLL_SURROGATE", {}).get("adequacy_decision") == "invariance_check_only"
    n4_ok = (
        null_by_id.get("N4_PHASE_RANDOM_REFERENCE", {}).get("adequacy_decision") == "effective_perturbation"
        and null_by_id.get("N4_PHASE_RANDOM_REFERENCE", {}).get("mandatory_for_future_execution") == "yes"
    )
    parameters = {row["contract_item"]: row for row in read_csv(artifacts["k_parameters"][1])} if artifacts["k_parameters"][1].is_file() else {}
    parameter_items = {"split_rule", "seed", "theta_new_rule", "epsilon_new_rule", "phase_d_theta_transfer", "post_hoc_tuning_lock"}
    parameters_ok = parameter_items <= set(parameters)
    phase_d_locked = parameters.get("phase_d_theta_transfer", {}).get("decision") == "locked_prohibited"
    tuning_locked = parameters.get("post_hoc_tuning_lock", {}).get("decision") == "locked_prohibited"
    k_authorized = k_manifest.get("execution_authorization") == K_AUTHORIZATION

    metric_rule = "median(feature_value for pair_key in locked review_holdout split)"
    n4_rule = "median(N4_feature_value for same pair_keys in locked review_holdout split)"
    support_expression = (
        "isfinite(observed_metric_f) and isfinite(nullmodel_metric_f_N4) and "
        "abs(observed_metric_f-nullmodel_metric_f_N4) >= theta_new+epsilon_new and "
        "N4_executed and N4_role=='effective_perturbation'"
    )
    rule_rows = [
        {"rule_id": "J2-R01", "rule_layer": "start", "rule_name": "hard_start_gates", "rule_text": "All authorization, hash, source, contract, parameter, boundary, and tuning start gates must pass before execution.", "machine_readable_expression": "all(hard_start_gate_status[g]=='pass' for g in required_hard_start_gates)", "result_if_failed": "blocked_no_execution", "blocking": "yes", "notes": "Evaluated before any feature or nullmodel calculation."},
        {"rule_id": "J2-R02", "rule_layer": "feature", "rule_name": "feature_level_n4_support", "rule_text": "For each locked feature, compare review-holdout medians using unsigned contract distance.", "machine_readable_expression": support_expression, "result_if_failed": "feature_support_f=false", "blocking": "no", "notes": "No feature direction is assumed."},
        {"rule_id": "J2-R03", "rule_layer": "result", "rule_name": "overall_pass_2_of_3", "rule_text": "Pass only when all conclusive prerequisites hold and at least two of three N4 support flags are true.", "machine_readable_expression": "hard_start_passed and execution_complete and all_3_features_finite and N4_gate_valid and support_count_N4>=2 and not inconclusive_condition and not phase_d_transfer and not post_hoc_tuning and claim_boundary_scan_pass", "result_if_failed": "evaluate_fail_or_inconclusive", "blocking": "yes", "notes": "Pass is contract-level only."},
        {"rule_id": "J2-R04", "rule_layer": "result", "rule_name": "overall_fail", "rule_text": "Fail when execution is conclusive, N4 is valid, and fewer than two feature support flags are true.", "machine_readable_expression": "hard_start_passed and execution_complete and all_3_features_finite and N4_gate_valid and support_count_N4<2 and not inconclusive_condition and not phase_d_transfer and not post_hoc_tuning", "result_if_failed": "evaluate_inconclusive", "blocking": "yes", "notes": "No threshold or feature may be revised after this result."},
        {"rule_id": "J2-R05", "rule_layer": "result", "rule_name": "overall_inconclusive", "rule_text": "Inconclusive takes precedence over pass/fail after execution starts when a required interpretation condition is unavailable or contradictory.", "machine_readable_expression": "minimaltest_started and (not N4_gate_evaluable or not two_of_three_evaluable or nullmodel_adequacy_contradictory or finite_but_ambiguous or theta_epsilon_partial or acceptance_gates_disagree or N2_misused_or_only_signal_like_comparator or required_review_metadata_incomplete)", "result_if_failed": "continue_result_precedence", "blocking": "yes", "notes": "Inconclusive has precedence over pass and fail."},
        {"rule_id": "J2-R06", "rule_layer": "result", "rule_name": "blocked_no_execution", "rule_text": "Any failed hard start condition blocks execution.", "machine_readable_expression": "not all(hard_start_gate_status[g]=='pass' for g in required_hard_start_gates)", "result_if_failed": "continue_result_precedence", "blocking": "yes", "notes": "Blocked has highest precedence."},
        {"rule_id": "J2-R07", "rule_layer": "nullmodel", "rule_name": "n2_exclusion_from_pass", "rule_text": "N2 checks invariance only and cannot increment support_count_N4 or otherwise contribute to pass.", "machine_readable_expression": "N2_role=='invariance_check_only' and N2_used_in_acceptance_gate==false and N2_pass_contribution==0", "result_if_failed": "inconclusive_review", "blocking": "yes", "notes": "If detected before execution, block instead."},
        {"rule_id": "J2-R08", "rule_layer": "nullmodel", "rule_name": "n4_mandatory_comparator", "rule_text": "N4 must execute as the effective perturbation comparator for a conclusive result.", "machine_readable_expression": "N4_role=='effective_perturbation' and N4_executed and N4_status=='pass'", "result_if_failed": "inconclusive_review", "blocking": "yes", "notes": "If N4 contract is missing before execution, block."},
        {"rule_id": "J2-R09", "rule_layer": "boundary", "rule_name": "no_phase_d_theta_transfer", "rule_text": "Phase-D theta=0.0300 must not be used.", "machine_readable_expression": "phase_d_theta_transferred==false", "result_if_failed": "blocked_no_execution", "blocking": "yes", "notes": "If detected after start, stop without conclusive pass/fail."},
        {"rule_id": "J2-R10", "rule_layer": "boundary", "rule_name": "no_post_hoc_tuning", "rule_text": "Features, splits, parameters, and null roles must remain locked after outcome access.", "machine_readable_expression": "post_hoc_tuning_detected==false", "result_if_failed": "blocked_no_execution", "blocking": "yes", "notes": "No exception based on outcome."},
        {"rule_id": "J2-R11", "rule_layer": "boundary", "rule_name": "claim_boundary", "rule_text": "Output interpretation remains within the reduced local contract.", "machine_readable_expression": "claim_boundary_scan_pass==true and physical_evidence_claim_made==false", "result_if_failed": "inconclusive_review", "blocking": "yes", "notes": "A result cannot broaden the scientific claim."},
    ]
    rules_machine_readable = all(row["machine_readable_expression"].strip() for row in rule_rows)

    feature_rows = [{
        "feature_name": name, "feature_role": "locked_selected_candidate",
        "observed_metric_rule": metric_rule, "n4_comparator_rule": n4_rule,
        "support_expression": support_expression, "required_for_pass_count": "yes; one boolean vote",
        "direction_policy": "unsigned_contract_distance",
        "notes": "Computed on locked review_holdout pair keys only; final_audit remains audit-only and cannot tune the rule.",
    } for name in feature_names]

    null_specs = {
        "N0_SIGN_FLIP": ("diagnostic_comparator", "no", "false", "false", "May diagnose sign dependence; cannot create pass."),
        "N1_PAIR_LABEL_PERMUTE": ("non_execution_diagnostic", "no", "false", "false", "No registered label-sensitive endpoint; execution is not required."),
        "N2_X_INDEX_ROLL_SURROGATE": ("invariance_check_only", "yes", "false", "true", "Must show expected invariance and never contribute to pass."),
        "N3_PAIR_DIRECTION_COLLAPSE": ("non_execution_diagnostic", "no", "false", "false", "Directional sanity role only; non-execution diagnostic allowed."),
        "N4_PHASE_RANDOM_REFERENCE": ("effective_perturbation", "yes", "true", "true", "Mandatory comparator for all three feature support flags."),
        "N5_CONSTANT_ZERO_PHASE_REFERENCE": ("non_execution_diagnostic", "no", "false", "false", "Degenerate reference; non-execution diagnostic allowed."),
    }
    null_rows = []
    for model_id in sorted(expected_nulls):
        role, mandatory, pass_gate, inconclusive_gate, notes = null_specs[model_id]
        null_rows.append({
            "nullmodel_id": model_id, "role": role, "mandatory_for_execution": mandatory,
            "used_in_pass_gate": pass_gate, "used_in_inconclusive_gate": inconclusive_gate,
            "limitations": null_by_id.get(model_id, {}).get("limitations", "missing"), "notes": notes,
        })

    decision_rows = [
        {"result_value": "pass", "conditions": "All hard gates pass; execution complete; all 3 feature/N4 metrics finite; N4 valid; support_count_N4>=2; no inconclusive condition; boundary locks pass.", "meaning": "The reduced local INTERFACE01 acceptance criteria passed on the authorized staged source.", "allowed_next_action": "prepare contract-bounded result review", "forbidden_interpretation": "No physical, gravity, spacetime-emergence, or theory-validation inference."},
        {"result_value": "fail", "conditions": "All hard gates pass; execution conclusive; N4 valid; all 3 metrics finite; support_count_N4<2; no inconclusive condition.", "meaning": "The reduced local INTERFACE01 acceptance criteria did not pass.", "allowed_next_action": "prepare failure review without parameter changes", "forbidden_interpretation": "Do not tune features, splits, theta, epsilon, or nullmodels post hoc."},
        {"result_value": "inconclusive_review", "conditions": "Execution started and any required N4, 2-of-3, adequacy, finite-interpretation, parameter, metadata, or internal-consistency condition is unavailable or contradictory.", "meaning": "Execution does not support a contract-level pass/fail interpretation.", "allowed_next_action": "identify the contractual element preventing interpretation", "forbidden_interpretation": "Do not convert ambiguity into pass or fail by adding rules after execution."},
        {"result_value": "blocked_no_execution", "conditions": "Any hard start gate fails, including authorization, hashes, source, contract, parameters, acceptance rule, Phase-D, or tuning guards.", "meaning": "The Minimaltest must not start.", "allowed_next_action": "resolve the start-gate defect in a separate contract block", "forbidden_interpretation": "Do not report a Minimaltest outcome."},
    ]

    addendum_complete = all([
        upstream_present, l_blocker_confirmed, k_authorized, features_ok, nulls_ok, n2_ok, n4_ok,
        parameters_ok, phase_d_locked, tuning_locked, rules_machine_readable,
        len(feature_rows) == 3, len(null_rows) == 6, len(decision_rows) == 4,
    ])
    if not upstream_present:
        status, authorization = STATUS_MISSING, BLOCKED
    elif addendum_complete:
        status, authorization = STATUS_OK, AUTHORIZED
    else:
        status, authorization = STATUS_NOT_AUTHORIZED, NOT_AUTHORIZED

    scope_specs = [
        ("feature_count", "K", artifacts["k_features"][1], str(len(feature_names)), features_ok, "Exactly three locked candidates."),
        ("feature_names", "K", artifacts["k_features"][1], ";".join(feature_names), features_ok, "Names imported without reselection."),
        ("nullmodel_count", "K", artifacts["k_nulls"][1], str(len(k_nulls)), nulls_ok, "Six inherited nullmodel IDs."),
        ("N2_role", "K", artifacts["k_nulls"][1], "invariance_check_only", n2_ok, "Excluded from pass."),
        ("N4_role", "K", artifacts["k_nulls"][1], "effective_perturbation", n4_ok, "Mandatory pass comparator."),
        ("split_rule", "K", REPO / parameters.get("split_rule", {}).get("source_artifact", rel(artifacts["k_parameters"][1])), parameters.get("split_rule", {}).get("observed_value", "missing"), "split_rule" in parameters, "Locked assignment remains unchanged."),
        ("seed", "K", REPO / parameters.get("seed", {}).get("source_artifact", rel(artifacts["k_parameters"][1])), parameters.get("seed", {}).get("observed_value", "missing"), parameters.get("seed", {}).get("observed_value") == "20260620", "Locked seed."),
        ("theta_new_rule", "J/K", REPO / parameters.get("theta_new_rule", {}).get("source_artifact", rel(artifacts["k_parameters"][1])), parameters.get("theta_new_rule", {}).get("observed_value", "missing"), "theta_new_rule" in parameters, "Rule only; no value computed in J2."),
        ("epsilon_new_rule", "J/K", REPO / parameters.get("epsilon_new_rule", {}).get("source_artifact", rel(artifacts["k_parameters"][1])), parameters.get("epsilon_new_rule", {}).get("observed_value", "missing"), "epsilon_new_rule" in parameters, "Rule only; no value computed in J2."),
        ("acceptance_rule", "J2", artifacts["l_contract"][1], "review_holdout median; unsigned N4 distance; threshold theta_new+epsilon_new; pass if support_count_N4>=2 of 3", rules_machine_readable, "New addendum; result precedence is blocked, inconclusive, pass, fail."),
    ]
    scope_rows = []
    for item, block, path, value, readable, notes in scope_specs:
        scope_rows.append({
            "contract_item": item, "source_block": block, "source_artifact": rel(path),
            "source_hash": sha256(path) if path.is_file() else "missing", "locked_value": value,
            "machine_readable": "yes" if readable else "no", "required_for_future_execution": "yes",
            "notes": notes,
        })

    authorization_rows = [{
        "authorization_id": "J2-AUTH-01", "status_before_j2": k_manifest.get("execution_authorization", "missing"),
        "status_after_j2": authorization,
        "decision_basis": "L blocker confirmed; three features, six null roles, split/seed, theta/epsilon, result precedence, and 2-of-3 N4 rule are machine-readable." if addendum_complete else "One or more required addendum conditions are unresolved.",
        "allowed_next_action": "run a separate L2 or L-replay execution package using J2 acceptance rule" if authorization == AUTHORIZED else "resolve remaining J2 review items",
        "forbidden_next_action": "claim physical evidence or expand interpretation",
        "notes": "J2 itself performs no execution.",
    }]
    boundary_rows = [
        {"boundary_item": "no_minimaltest_in_j2", "status": "locked", "evidence": "minimaltest_started=false", "notes": "Contract addendum only."},
        {"boundary_item": "no_nullmodel_execution_in_j2", "status": "locked", "evidence": "nullmodels_executed=false", "notes": "Roles only."},
        {"boundary_item": "no_physical_evidence_claim", "status": "locked", "evidence": "physical_evidence_claim_made=false", "notes": "Contract-level language only."},
        {"boundary_item": "no_phase_d_theta_transfer", "status": "locked", "evidence": "phase_d_theta_transferred=false", "notes": "theta=0.0300 is not used."},
        {"boundary_item": "no_post_hoc_tuning", "status": "locked", "evidence": "post_hoc_tuning_detected=false", "notes": "No values are computed."},
        {"boundary_item": "no_upstream_mutation", "status": "checked", "evidence": "Upstream hashes compared before and after J2 writes.", "notes": "Any mismatch fails validation."},
        {"boundary_item": "no_synthetic_evidence", "status": "locked", "evidence": "No feature or null result is generated.", "notes": "Boolean rule definitions are not result data."},
        {"boundary_item": "contract_addendum_only", "status": "locked", "evidence": "J2 outputs contain scope, roles, and decision logic only.", "notes": "Execution belongs to a separate package."},
    ]
    remaining_rows = [] if authorization == AUTHORIZED else [{
        "review_item_id": "J2-REM-01", "category": "contract",
        "remaining_status": "blocking", "required_action": "Resolve failed J2 validation conditions.",
        "blocks_future_execution": "yes", "notes": "See J2 validation results.",
    }]

    OUTPUT.mkdir(parents=True)
    manifest = {
        "work_package": "QSB-INTERFACE01J2", "status": status,
        "created_at_utc": datetime.now(timezone.utc).isoformat(), "repo_root": str(REPO),
        "upstream_dirs": {"F3": rel(F3), "G": rel(G), "H": rel(H), "I": rel(I), "J": rel(J), "K": rel(K), "L": rel(L)},
        "l_blocker_confirmed": l_blocker_confirmed, "locked_feature_count": len(feature_names),
        "locked_nullmodel_count": len(k_nulls), "n2_role": "invariance_check_only" if n2_ok else "unresolved",
        "n4_role": "effective_perturbation" if n4_ok else "unresolved",
        "acceptance_rule_added": rules_machine_readable, "execution_authorization_after_j2": authorization,
        "minimaltest_started": False, "nullmodels_executed": False, "physical_evidence_claim_made": False,
        "phase_d_theta_transferred": False, "post_hoc_tuning_detected": False,
        "modified_existing_files": [], "claim_boundary": CLAIM_BOUNDARY,
    }
    (OUTPUT / "01_j2_run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_csv(OUTPUT / "02_upstream_inventory_and_hashes.csv", ["artifact_id", "upstream_block", "path", "exists", "sha256", "role", "used_for", "notes"], inventory_rows)
    write_csv(OUTPUT / "03_l_blocker_confirmation.csv", ["blocker_id", "l_status_seen", "l_result_seen", "blocker_text", "confirmed", "blocking_layer", "notes"], blocker_rows)
    write_csv(OUTPUT / "04_locked_contract_scope.csv", ["contract_item", "source_block", "source_artifact", "source_hash", "locked_value", "machine_readable", "required_for_future_execution", "notes"], scope_rows)
    write_csv(OUTPUT / "05_acceptance_rule_addendum.csv", ["rule_id", "rule_layer", "rule_name", "rule_text", "machine_readable_expression", "result_if_failed", "blocking", "notes"], rule_rows)
    write_csv(OUTPUT / "06_feature_acceptance_gates.csv", ["feature_name", "feature_role", "observed_metric_rule", "n4_comparator_rule", "support_expression", "required_for_pass_count", "direction_policy", "notes"], feature_rows)
    write_csv(OUTPUT / "07_nullmodel_acceptance_roles.csv", ["nullmodel_id", "role", "mandatory_for_execution", "used_in_pass_gate", "used_in_inconclusive_gate", "limitations", "notes"], null_rows)
    write_csv(OUTPUT / "08_result_decision_table.csv", ["result_value", "conditions", "meaning", "allowed_next_action", "forbidden_interpretation"], decision_rows)
    write_csv(OUTPUT / "09_execution_authorization_after_j2.csv", ["authorization_id", "status_before_j2", "status_after_j2", "decision_basis", "allowed_next_action", "forbidden_next_action", "notes"], authorization_rows)
    write_csv(OUTPUT / "10_claim_boundary_and_forbidden_actions.csv", ["boundary_item", "status", "evidence", "notes"], boundary_rows)
    write_csv(OUTPUT / "12_review_items_remaining.csv", ["review_item_id", "category", "remaining_status", "required_action", "blocks_future_execution", "notes"], remaining_rows)

    after_hashes = {key: sha256(path) for key, (_, path, _) in artifacts.items() if path.is_file()}
    upstream_unchanged = before_hashes == after_hashes
    validations: list[dict[str, Any]] = []

    def validate(identifier: str, name: str, passed: bool, observed: Any, expected: Any, message: str) -> None:
        validations.append({
            "validation_id": identifier, "validation_layer": "J2 contract preflight", "check_name": name,
            "status": "pass" if passed else "fail", "severity": "error", "observed_value": observed,
            "expected_value": expected, "message": message,
            "blocking_for_authorization": "no" if passed else "yes",
        })

    validate("J2-V01", "upstream_dirs_present", upstream_present, upstream_present, True, "Required F3-L artifacts checked.")
    validate("J2-V02", "l_blocker_confirmed", l_blocker_confirmed, l_blocker_confirmed, True, "L-G09-only blocker confirmed.")
    validate("J2-V03", "k_authorization_seen", k_authorized, k_manifest.get("execution_authorization", "missing"), K_AUTHORIZATION, "K authorization checked.")
    validate("J2-V04", "locked_feature_scope_identified", features_ok, ";".join(feature_names), ";".join(sorted(expected_features)), "Three exact features imported.")
    validate("J2-V05", "locked_nullmodel_scope_identified", nulls_ok, len(k_nulls), 6, "Six exact nullmodel IDs imported.")
    validate("J2-V06", "n2_invariance_only", n2_ok, null_by_id.get("N2_X_INDEX_ROLL_SURROGATE", {}).get("adequacy_decision", "missing"), "invariance_check_only", "N2 excluded from pass.")
    validate("J2-V07", "n4_effective_perturbation", n4_ok, null_by_id.get("N4_PHASE_RANDOM_REFERENCE", {}).get("adequacy_decision", "missing"), "effective_perturbation", "N4 mandatory comparator locked.")
    validate("J2-V08", "theta_epsilon_source_present", parameters_ok, "theta_new_rule" in parameters and "epsilon_new_rule" in parameters, True, "J/K parameter rules present; no values computed.")
    validate("J2-V09", "pass_rule_machine_readable", any(r["rule_name"] == "overall_pass_2_of_3" and r["machine_readable_expression"] for r in rule_rows), "present", "present", "Pass rule recorded.")
    validate("J2-V10", "fail_rule_machine_readable", any(r["rule_name"] == "overall_fail" and r["machine_readable_expression"] for r in rule_rows), "present", "present", "Fail rule recorded.")
    validate("J2-V11", "inconclusive_rule_machine_readable", any(r["rule_name"] == "overall_inconclusive" and r["machine_readable_expression"] for r in rule_rows), "present", "present", "Inconclusive rule recorded.")
    validate("J2-V12", "blocked_rule_machine_readable", any(r["rule_name"] == "blocked_no_execution" and r["machine_readable_expression"] for r in rule_rows), "present", "present", "Blocked rule recorded.")
    validate("J2-V13", "no_minimaltest_started", manifest["minimaltest_started"] is False, manifest["minimaltest_started"], False, "J2 performs no Minimaltest.")
    validate("J2-V14", "no_post_hoc_tuning", manifest["post_hoc_tuning_detected"] is False and tuning_locked, manifest["post_hoc_tuning_detected"], False, "Tuning lock preserved.")
    validate("J2-V15", "no_phase_d_theta_transfer", manifest["phase_d_theta_transferred"] is False and phase_d_locked, manifest["phase_d_theta_transferred"], False, "Legacy threshold not transferred.")
    validate("J2-V16", "claim_boundary_clean", manifest["physical_evidence_claim_made"] is False and bool(manifest["claim_boundary"]), manifest["physical_evidence_claim_made"], False, "Claim boundary present.")
    authorization_consistent = (authorization == AUTHORIZED and addendum_complete) or (authorization != AUTHORIZED and not addendum_complete)
    validate("J2-V17", "authorization_consistent", authorization_consistent, authorization, "consistent with addendum completeness", "Authorization follows all gates.")
    validate("J2-V18", "upstream_artifacts_unchanged", upstream_unchanged, upstream_unchanged, True, "F3-L artifact hashes unchanged after J2 writes.")
    write_csv(OUTPUT / "11_j2_validation_results.csv", ["validation_id", "validation_layer", "check_name", "status", "severity", "observed_value", "expected_value", "message", "blocking_for_authorization"], validations)

    next_action = "run a separate L2 or L-replay execution package using J2 acceptance rule" if authorization == AUTHORIZED else "resolve remaining J2 review items; do not execute Minimaltest"
    note = f"""# INTERFACE01-J2 Final Result

## Status

`{status}`

## L Blocker

Confirmed: L stopped with `blocked_no_execution` because J/K lacked a preregistered pass/fail acceptance rule.

## Acceptance Rule Addendum

For each locked feature, the unsigned distance between the observed and N4 review-holdout medians must be finite and at least `theta_new + epsilon_new`. A conclusive pass requires support from at least 2 of 3 features. Result precedence is blocked, inconclusive, pass, then fail.

## Locked Contract Scope

- features: `{'; '.join(feature_names)}`
- nullmodels: {len(k_nulls)} inherited roles
- N2: `invariance_check_only`; excluded from pass
- N4: `effective_perturbation`; mandatory comparator
- theta/epsilon source: unchanged J/K rules; no values computed in J2

## Execution Authorization After J2

`execution_authorization_after_j2 = {authorization}`

## Minimaltest

No Minimaltest was executed in J2.

## Claim Boundary

No physical evidence claim is made here.

## Next allowed action

{next_action}
"""
    (OUTPUT / "FINAL_RESULT_NOTE.md").write_text(note, encoding="utf-8")

    actual = {path.name for path in OUTPUT.iterdir() if path.is_file()}
    if actual != EXPECTED_FILES:
        raise SystemExit(f"Output file-set mismatch: actual={sorted(actual)} expected={sorted(EXPECTED_FILES)}")
    failures = [row["validation_id"] for row in validations if row["status"] == "fail"]
    if failures:
        raise SystemExit(f"J2 validation failures: {failures}")
    print(f"status={status}")
    print(f"execution_authorization_after_j2={authorization}")
    print(f"l_blocker_confirmed={str(l_blocker_confirmed).lower()}")
    print(f"locked_scope={len(feature_names)}_features/{len(k_nulls)}_nullmodels")
    print("minimaltest_started=false")
    print(f"output_files={len(actual)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
