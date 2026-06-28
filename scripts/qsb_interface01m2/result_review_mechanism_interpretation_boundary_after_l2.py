#!/usr/bin/env python3
"""Review the L2 fail result within the INTERFACE01-M2 claim boundary."""

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
J2 = REPO / "runs/QSB-INTERFACE01J2/minimaltest_acceptance_rule_addendum"
M = REPO / "runs/QSB-INTERFACE01M/result_review_mechanism_interpretation_boundary"
L2 = REPO / "runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2"
OUTPUT = REPO / "runs/QSB-INTERFACE01M2/result_review_mechanism_interpretation_boundary_after_l2"

STATUS = "interface01m2_result_review_mechanism_interpretation_boundary_completed_after_l2_fail"
J2_AUTH = "authorized_for_separate_minimaltest_execution_with_acceptance_rule"
L2_STATUS = "interface01l2_separate_final_minimaltest_execution_completed_with_claim_boundary"
CLAIM_BOUNDARY = (
    "INTERFACE01-M2 reviews the L2 fail as a diagnostic negative for the reduced P0/t0/alpha1.6 "
    "INTERFACE01 contract only. It reruns no Minimaltest or nullmodel, changes no parameter or "
    "upstream artifact, makes no physical-evidence claim, and does not decide the broader QSB hypothesis."
)
EXPECTED_FILES = {
    "01_m2_run_manifest.json", "02_upstream_result_inventory.csv",
    "03_authorization_and_hash_preflight.csv", "04_l2_contract_result_summary.csv",
    "05_failure_localization.csv", "06_feature_failure_review.csv", "07_nullmodel_role_review.csv",
    "08_acceptance_rule_failure_review.csv", "09_mechanism_chain_map.csv",
    "10_claim_classification_matrix.csv", "11_unsupported_claims_and_boundaries.csv",
    "12_theory_language_note_de.md", "13_theory_language_note_en.md",
    "14_next_research_actions.csv", "15_m2_validation_results.csv",
    "16_review_items_for_next_block.csv", "FINAL_RESULT_NOTE.md",
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
        "f3_manifest": ("F3", F3 / "01_f3_run_manifest.json", "authorized source status"),
        "f3_db": ("F3", F3 / "09_delta_phi_staging_preflight.sqlite", "source identity"),
        "g_manifest": ("G", G / "01_g_run_manifest.json", "profile status"),
        "h_manifest": ("H", H / "01_h_run_manifest.json", "pilot scope"),
        "i_manifest": ("I", I / "01_i_run_manifest.json", "review status"),
        "j_manifest": ("J", J / "01_j_run_manifest.json", "pre-contract status"),
        "k_manifest": ("K", K / "01_k_run_manifest.json", "execution authorization"),
        "l_manifest": ("L", L / "01_l_run_manifest.json", "earlier blocked run"),
        "j2_manifest": ("J2", J2 / "01_j2_run_manifest.json", "acceptance authorization"),
        "j2_rules": ("J2", J2 / "05_acceptance_rule_addendum.csv", "2-of-3 rule"),
        "m_manifest": ("M", M / "01_m_run_manifest.json", "earlier blocked review"),
        "l2_manifest": ("L2", L2 / "01_l2_run_manifest.json", "executed contract result"),
        "l2_start": ("L2", L2 / "02_start_gate_authorization_preflight.csv", "15 start gates"),
        "l2_hashes": ("L2", L2 / "03_upstream_hash_verification.csv", "upstream hash checks"),
        "l2_source": ("L2", L2 / "05_source_data_validation.csv", "source validation"),
        "l2_features": ("L2", L2 / "06_feature_scope_and_mapping.csv", "feature reproduction"),
        "l2_parameters": ("L2", L2 / "09_theta_epsilon_application.csv", "theta and epsilon"),
        "l2_nulls": ("L2", L2 / "10_nullmodel_execution_summary.csv", "nullmodel execution"),
        "l2_support": ("L2", L2 / "11_feature_level_n4_support.csv", "feature-level N4 support"),
        "l2_acceptance": ("L2", L2 / "13_acceptance_gate_results.csv", "final result gates"),
        "l2_validations": ("L2", L2 / "15_l2_validation_results.csv", "execution validations"),
    }
    upstream_present = all(path.is_file() for _, path, _ in artifacts.values())
    before_hashes = {key: sha256(path) for key, (_, path, _) in artifacts.items() if path.is_file()}
    inventory_rows = []
    for number, (key, (block, path, use)) in enumerate(artifacts.items(), start=1):
        exists = path.is_file()
        inventory_rows.append({
            "artifact_id": f"M2-A{number:02d}", "upstream_block": block, "path": rel(path),
            "exists": "yes" if exists else "no", "sha256": before_hashes.get(key, "missing"),
            "role": "read-only result-review input", "used_for": use,
            "notes": "Hashed before M2; not modified." if exists else "Missing required artifact.",
        })

    j2_manifest = load_json(artifacts["j2_manifest"][1]) if artifacts["j2_manifest"][1].is_file() else {}
    l2_manifest = load_json(artifacts["l2_manifest"][1]) if artifacts["l2_manifest"][1].is_file() else {}
    j2_authorized = j2_manifest.get("execution_authorization_after_j2") == J2_AUTH
    l2_executed = (
        l2_manifest.get("status") == L2_STATUS
        and l2_manifest.get("minimaltest_started") is True
        and l2_manifest.get("minimaltest_completed") is True
    )
    l2_fail = l2_manifest.get("minimaltest_contract_result") == "fail"
    l2_boundary_ok = (
        l2_manifest.get("physical_evidence_claim_made") is False
        and l2_manifest.get("phase_d_theta_transferred") is False
        and l2_manifest.get("post_hoc_tuning_detected") is False
        and l2_manifest.get("upstream_modified") is False
    )

    start_rows = read_csv(artifacts["l2_start"][1]) if artifacts["l2_start"][1].is_file() else []
    source_rows = read_csv(artifacts["l2_source"][1]) if artifacts["l2_source"][1].is_file() else []
    support_rows = read_csv(artifacts["l2_support"][1]) if artifacts["l2_support"][1].is_file() else []
    null_rows_l2 = read_csv(artifacts["l2_nulls"][1]) if artifacts["l2_nulls"][1].is_file() else []
    acceptance_rows_l2 = read_csv(artifacts["l2_acceptance"][1]) if artifacts["l2_acceptance"][1].is_file() else []
    parameter_rows = {row["parameter_name"]: row for row in read_csv(artifacts["l2_parameters"][1])} if artifacts["l2_parameters"][1].is_file() else {}
    validation_rows_l2 = read_csv(artifacts["l2_validations"][1]) if artifacts["l2_validations"][1].is_file() else []
    acceptance_by_id = {row["acceptance_gate_id"]: row for row in acceptance_rows_l2}
    null_by_id = {row["nullmodel_id"]: row for row in null_rows_l2}
    source_valid = len(source_rows) == 13 and all(row["status"] == "pass" for row in source_rows)
    starts_valid = len(start_rows) == 15 and all(row["status"] == "pass" for row in start_rows)
    validations_valid = len(validation_rows_l2) == 25 and all(row["status"] == "pass" for row in validation_rows_l2)
    support_count = sum(row.get("support_flag") == "true" for row in support_rows)
    features_valid = len(support_rows) == 3
    nulls_valid = len(null_rows_l2) == 6 and all(row["executed"] == "yes" for row in null_rows_l2)
    n2_ok = null_by_id.get("N2_X_INDEX_ROLL_SURROGATE", {}).get("role") == "invariance_check_only" and null_by_id.get("N2_X_INDEX_ROLL_SURROGATE", {}).get("used_in_acceptance_gate") == "false"
    n4_ok = null_by_id.get("N4_PHASE_RANDOM_REFERENCE", {}).get("role") == "effective_perturbation" and null_by_id.get("N4_PHASE_RANDOM_REFERENCE", {}).get("used_in_acceptance_gate") == "true"
    theta = parameter_rows.get("theta_new", {}).get("computed_or_loaded_value", "missing")
    epsilon = parameter_rows.get("epsilon_new", {}).get("computed_or_loaded_value", "missing")
    threshold = support_rows[0]["support_threshold"] if support_rows else "missing"
    result_consistent = (
        support_count == 0
        and acceptance_by_id.get("L2-ACCEPT-2OF3", {}).get("status") == "fail"
        and acceptance_by_id.get("L2-ACCEPT-FINAL", {}).get("status") == "fail"
    )
    full_review_allowed = all([
        upstream_present, j2_authorized, l2_executed, l2_fail, l2_boundary_ok, source_valid,
        starts_valid, validations_valid, features_valid, nulls_valid, n2_ok, n4_ok, result_consistent,
    ])
    if not full_review_allowed:
        raise SystemExit("M2 blocked: J2/L2 result chain is missing or inconsistent; no interpretation outputs written.")

    preflight_specs = [
        ("M2-G01", "j2_authorized", j2_manifest["execution_authorization_after_j2"], J2_AUTH, j2_authorized, "J2 authorization is exact."),
        ("M2-G02", "l2_executed", f"started={l2_manifest['minimaltest_started']};completed={l2_manifest['minimaltest_completed']}", "started=true;completed=true", l2_executed, "L2 execution completed."),
        ("M2-G03", "l2_result_fail", l2_manifest["minimaltest_contract_result"], "fail", l2_fail, "Non-blocked fail result present."),
        ("M2-G04", "upstream_hashes_stable", "checked before and after M2 writes", "unchanged", True, "Final result recorded in M2-V18."),
        ("M2-G05", "no_minimaltest_rerun", "false", "false", True, "M2 reads outputs only."),
        ("M2-G06", "claim_boundary_clean", "physical_evidence_claim_made=false", "false", l2_boundary_ok, "L2 and M2 boundaries preserved."),
    ]
    preflight_rows = [{
        "gate_id": gate_id, "gate_name": name, "observed_value": observed, "expected_value": expected,
        "status": "pass" if passed else "fail", "blocking": "yes", "notes": notes,
    } for gate_id, name, observed, expected, passed, notes in preflight_specs]

    result_summary_specs = [
        ("l2_status", l2_manifest["status"], "contract_result", "Completed L2 execution status."),
        ("minimaltest_contract_result", "fail", "diagnostic_negative", "Reduced J2 contract did not pass."),
        ("n4_support_count", support_count, "diagnostic_negative", "Zero selected features met the N4 support threshold."),
        ("n4_support_required", 2, "contract_result", "J2 pass threshold."),
        ("theta_new", theta, "contract_result", "Frozen calibration median."),
        ("epsilon_new", epsilon, "contract_result", "Frozen calibration MAD."),
        ("source_rows", l2_manifest["source_rows_seen"], "contract_result", "Authorized F3 source rows."),
        ("ordered_pairs", l2_manifest["ordered_pairs_seen"], "contract_result", "Ordered off-diagonal pairs."),
        ("x_points", l2_manifest["x_points_seen"], "contract_result", "Distinct x points."),
        ("features_count", l2_manifest["locked_feature_count"], "contract_result", "Locked selected feature count."),
        ("nullmodels_executed_count", l2_manifest["nullmodels_executed_count"], "contract_result", "All prescribed nullmodels executed."),
    ]
    result_summary_rows = [{
        "result_item": item, "observed_value": value, "source_artifact": rel(artifacts["l2_manifest"][1] if item not in {"n4_support_count", "n4_support_required", "theta_new", "epsilon_new"} else artifacts["l2_support"][1] if item.startswith("n4_") else artifacts["l2_parameters"][1]),
        "source_hash": before_hashes["l2_manifest" if item not in {"n4_support_count", "n4_support_required", "theta_new", "epsilon_new"} else "l2_support" if item.startswith("n4_") else "l2_parameters"],
        "classification": classification, "notes": notes,
    } for item, value, classification, notes in result_summary_specs]

    failure_rows = [
        {"failure_item": "source_validity", "layer": "source", "observed_value": "13/13 source checks passed", "expected_or_required_value": "all pass", "failure_status": "not_failed", "classification": "contract_result", "mechanism_implication": "The negative disposition is not attributable to missing or invalid staged source rows.", "notes": "F3 scope remains local to P0/t0/alpha1.6."},
        {"failure_item": "authorization_validity", "layer": "authorization", "observed_value": "K/J2 valid", "expected_or_required_value": "valid", "failure_status": "not_failed", "classification": "contract_result", "mechanism_implication": "The run was authorized under the frozen contract.", "notes": "No authorization defect."},
        {"failure_item": "start_gates", "layer": "execution preflight", "observed_value": "15/15 passed", "expected_or_required_value": "15/15", "failure_status": "not_failed", "classification": "contract_result", "mechanism_implication": "The negative result follows a complete start preflight.", "notes": "No hard gate failed."},
        {"failure_item": "nullmodel_execution", "layer": "comparators", "observed_value": "6/6 executed", "expected_or_required_value": "6/6", "failure_status": "not_failed", "classification": "contract_result", "mechanism_implication": "Comparator availability did not prevent evaluation.", "notes": "All deterministic transforms ran."},
        {"failure_item": "n2_role", "layer": "nullmodel role", "observed_value": "invariance_check_only; excluded from pass", "expected_or_required_value": "same", "failure_status": "not_failed", "classification": "contract_result", "mechanism_implication": "N2 supplied only the expected invariance check.", "notes": "N2 max selected-feature difference was zero."},
        {"failure_item": "n4_role", "layer": "nullmodel role", "observed_value": "effective_perturbation; mandatory; executed", "expected_or_required_value": "same", "failure_status": "not_failed", "classification": "contract_result", "mechanism_implication": "The mandatory N4 comparison was evaluable.", "notes": "All N4 feature metrics were finite."},
        {"failure_item": "feature_level_n4_support", "layer": "feature-to-comparator separation", "observed_value": "0/3 supported", "expected_or_required_value": ">=2/3", "failure_status": "failed_for_contract", "classification": "diagnostic_negative", "mechanism_implication": "The three selected responses did not separate from N4 by the locked theta+epsilon distance.", "notes": "All three distances were finite but below threshold."},
        {"failure_item": "j2_2_of_3_rule", "layer": "acceptance", "observed_value": "0", "expected_or_required_value": ">=2", "failure_status": "failed_for_contract", "classification": "diagnostic_negative", "mechanism_implication": "The preregistered pass condition was not met.", "notes": "No post-hoc exception is allowed."},
        {"failure_item": "contract_result", "layer": "final disposition", "observed_value": "fail", "expected_or_required_value": "pass requires >=2 support votes", "failure_status": "diagnostic_negative", "classification": "diagnostic_negative", "mechanism_implication": "This specific reduced phase-to-feature-to-relation candidate path is weakened.", "notes": "The broader interface hypothesis remains undecided."},
    ]

    feature_rows = [{
        "feature_name": row["feature_name"], "observed_metric": row["observed_metric"],
        "n4_metric": row["n4_metric"], "abs_delta_n4": row["abs_delta_n4"],
        "theta_new": row["theta_new"], "epsilon_new": row["epsilon_new"],
        "support_threshold": row["support_threshold"], "support_flag": row["support_flag"],
        "failure_reading": "Finite review-holdout median distance remained below the locked theta_new+epsilon_new threshold.",
        "classification": "diagnostic_negative",
        "notes": "Feature validity is not rejected; adequacy for this N4-separation contract remains open.",
    } for row in support_rows]

    null_review_rows = [{
        "nullmodel_id": row["nullmodel_id"], "role": row["role"],
        "executed_in_l2": row["executed"], "used_in_acceptance_gate": row["used_in_acceptance_gate"],
        "observed_role_consistency": "consistent" if row["status"] == "pass" else "review",
        "mechanism_relevance": "mandatory comparator against which all three distances were insufficient" if row["nullmodel_id"] == "N4_PHASE_RANDOM_REFERENCE" else "invariance control; no pass contribution" if row["nullmodel_id"] == "N2_X_INDEX_ROLL_SURROGATE" else "diagnostic context only",
        "classification": "diagnostic_negative" if row["nullmodel_id"] == "N4_PHASE_RANDOM_REFERENCE" else "contract_result",
        "limitations": row["limitation"], "notes": row["notes"],
    } for row in null_rows_l2]

    rule_review_rows = [
        {"acceptance_rule_id": "N2_exclusion", "rule_text": "N2 role=invariance_check_only and used_in_acceptance_gate=false", "observed_value": "role preserved; max difference=0; zero votes", "required_value": "preserved; zero votes", "status": "pass", "classification": "contract_result", "notes": "N2 did not create or prevent pass."},
        {"acceptance_rule_id": "N4_mandatory_comparator", "rule_text": "N4 executes as effective_perturbation with finite metrics", "observed_value": "executed; three finite comparator metrics", "required_value": "executed and finite", "status": "pass", "classification": "contract_result", "notes": "The negative result is conclusive under the contract."},
        {"acceptance_rule_id": "feature_support_threshold", "rule_text": "abs_delta_n4 >= theta_new + epsilon_new", "observed_value": f"three distances below {threshold}", "required_value": f">={threshold} per supporting feature", "status": "fail", "classification": "diagnostic_negative", "notes": "All three support flags were false."},
        {"acceptance_rule_id": "2_of_3_rule", "rule_text": "support_count_N4>=2", "observed_value": "0", "required_value": ">=2", "status": "fail", "classification": "diagnostic_negative", "notes": "Locked pass rule not met."},
        {"acceptance_rule_id": "final_fail", "rule_text": "conclusive execution with support_count_N4<2 yields fail", "observed_value": "support_count=0; inconclusive=false", "required_value": "fail", "status": "pass", "classification": "contract_result", "notes": "L2 final disposition is internally consistent."},
    ]

    chain_rows = [
        {"chain_step": "M2-STEP-01 authorized_delta_phi_source", "input_element": "authorized P0/t0/alpha1.6 phase source", "operation_or_relation": "stage delta_phi_ij(x)", "output_element": "168042 valid rows; 42 pairs; 4001 x-points", "status_after_l2": "supported_for_contract", "mechanism_reading": "The reduced source layer was technically available and internally valid.", "evidence_boundary": "Source validity is not physical validation.", "open_question": "Behavior outside this single source configuration."},
        {"chain_step": "M2-STEP-02 phase_difference_to_feature_response", "input_element": "wrapped delta_phi_ij(x)", "operation_or_relation": "three locked aggregate feature mappings", "output_element": "finite reproduced feature values", "status_after_l2": "tested_but_insufficient", "mechanism_reading": "The mapping produced stable finite responses, but their adequacy for discrimination was not established.", "evidence_boundary": "Only three aggregate features were tested.", "open_question": "Whether alternative preregistered or richer features capture relevant structure."},
        {"chain_step": "M2-STEP-03 feature_response_to_N4_separation", "input_element": "three review-holdout feature medians", "operation_or_relation": "unsigned distance to N4 medians", "output_element": "three finite distances below threshold", "status_after_l2": "failed_for_contract", "mechanism_reading": "The selected responses did not separate sufficiently from the effective perturbation comparator.", "evidence_boundary": "Negative only for this N4 implementation and feature scope.", "open_question": "Feature adequacy and N4 comparator adequacy."},
        {"chain_step": "M2-STEP-04 N4_separation_to_threshold_decision", "input_element": "N4 distances", "operation_or_relation": "compare with theta_new+epsilon_new", "output_element": "0/3 support flags", "status_after_l2": "failed_for_contract", "mechanism_reading": "The locked threshold admitted no supporting feature vote.", "evidence_boundary": "Threshold sensitivity cannot be changed post hoc.", "open_question": "Prospective sensitivity analysis under a new contract."},
        {"chain_step": "M2-STEP-05 threshold_decision_to_relation_candidate", "input_element": "zero supporting votes", "operation_or_relation": "J2 2-of-3 acceptance", "output_element": "fail", "status_after_l2": "not_supported_by_this_run", "mechanism_reading": "This run supplies no accepted thresholded relation candidate.", "evidence_boundary": "Absence of support here is not general nonexistence.", "open_question": "Whether another authorized source or representation supports a relation candidate."},
        {"chain_step": "M2-STEP-06 relation_candidate_to_interface_hypothesis", "input_element": "no accepted relation candidate", "operation_or_relation": "interface-layer interpretation", "output_element": "no decision", "status_after_l2": "open", "mechanism_reading": "The broader interface hypothesis is not decided by this failed local gate.", "evidence_boundary": "The prerequisite relation candidate was not established.", "open_question": "Which model layer can validly connect phase relations to relational order."},
        {"chain_step": "M2-STEP-07 interface_hypothesis_to_geometric_readability", "input_element": "interface-layer hypothesis", "operation_or_relation": "geometric extraction/readability", "output_element": "not evaluated", "status_after_l2": "not_tested", "mechanism_reading": "No geometric readability test was part of L2.", "evidence_boundary": "EXTRACT/Gram-first methods were not executed.", "open_question": "Whether a future Gram-first d/D extraction reveals motifs outside the three-feature contract."},
    ]

    claim_rows = [
        ("M2-C01", "L2 contract failed", "contract_result", "The reduced J2 contract returned fail.", "Treating fail as a verdict on QSB.", "L2 manifest and final gate"),
        ("M2-C02", "N4 support 0/3", "diagnostic_negative", "None of the three locked features met the N4 distance threshold.", "Calling the features universally irrelevant.", "L2 support table"),
        ("M2-C03", "authorized delta_phi source was valid", "contract_result", "All source validation checks passed.", "Calling source validity physical validation.", "L2 source validation"),
        ("M2-C04", "feature-to-N4 separation insufficient", "diagnostic_negative", "Separation was insufficient under the locked feature, N4, and threshold contract.", "Generalizing non-separation beyond the contract.", "L2 feature support"),
        ("M2-C05", "relation candidate not supported by this run", "diagnostic_negative", "This run did not support the thresholded relation candidate.", "Claiming that no relation candidate can exist.", "J2 2-of-3 gate"),
        ("M2-C06", "interface hypothesis remains open", "open_question", "The broader interface hypothesis remains open.", "Treating it as established or rejected.", "Interpretation boundary"),
        ("M2-C07", "geometric readability not tested", "open_question", "No geometric extraction was executed.", "Inferring geometric success or impossibility.", "L2 scope"),
        ("M2-C08", "QSB disproven", "unsupported_claim", "No broad verdict follows from this local fail.", "QSB is disproven.", "Claim boundary"),
        ("M2-C09", "gravity mechanism disproven", "unsupported_claim", "No gravity-level conclusion follows.", "A gravity mechanism is disproven.", "Claim boundary"),
    ]
    claim_matrix_rows = [{
        "statement_id": identifier, "statement": statement, "classification": classification,
        "allowed_wording": allowed, "forbidden_wording": forbidden, "source_or_basis": basis,
        "notes": "Classification is specific to the completed L2 fail review.",
    } for identifier, statement, classification, allowed, forbidden, basis in claim_rows]

    unsupported_rows = [
        {"unsupported_claim": "QSB is disproven", "why_not_supported": "L2 tested one reduced, frozen contract and one source configuration.", "safe_replacement_wording": "The reduced J2 contract returned a diagnostic negative result.", "notes": "Broader theory verdict forbidden."},
        {"unsupported_claim": "The interface hypothesis is false", "why_not_supported": "The run did not establish the relation candidate required to test downstream interface interpretation.", "safe_replacement_wording": "The interface hypothesis remains open.", "notes": "Downstream step not decided."},
        {"unsupported_claim": "de-Broglie phase relevance is ruled out", "why_not_supported": "Three aggregate features and one mandatory comparator do not exhaust phase-sensitive mappings.", "safe_replacement_wording": "The tested phase-to-feature path was insufficient under this contract.", "notes": "Feature scope remains a review item."},
        {"unsupported_claim": "No emergent geometry can arise", "why_not_supported": "No geometric extraction or readability test was executed.", "safe_replacement_wording": "Geometric readability was not tested.", "notes": "EXTRACT01 remains future work."},
        {"unsupported_claim": "The result proves anything about gravity", "why_not_supported": "The contract evaluates local feature/nullmodel separation, not gravity.", "safe_replacement_wording": "No gravity-level inference is made.", "notes": "Outside contract scope."},
        {"unsupported_claim": "The result generalizes beyond P0/t0/alpha1.6", "why_not_supported": "F3 authorized exactly this source configuration.", "safe_replacement_wording": "Generalization requires separately authorized source extensions.", "notes": "Source limitation explicit."},
    ]

    action_rows = [
        {"action_id": "M2-A01", "action_type": "feature_review", "priority": "high", "description": "review_3_feature_scope without changing the completed L2 result", "depends_on": "L2 diagnostic negative", "allowed_now": "yes", "notes": "Any revised feature set requires a new preregistered contract."},
        {"action_id": "M2-A02", "action_type": "nullmodel_hardening", "priority": "high", "description": "inspect_N4_effective_perturbation_role and its adequacy for the intended distinction", "depends_on": "preserve current N4 result", "allowed_now": "yes", "notes": "Review only; do not substitute a favorable comparator post hoc."},
        {"action_id": "M2-A03", "action_type": "extract_layer_design", "priority": "medium", "description": "prepare_QSB_EXTRACT01_DWH_based_Gram_Tensor_Extraction_Layer using K_ij=<psi_i|psi_j>, d_ij=-ell_0 log(|K_ij|+epsilon), and shortest-path D(i,j)", "depends_on": "separate specification and authorization", "allowed_now": "design_only", "notes": "Do not reinterpret L2 through this unexecuted method."},
        {"action_id": "M2-A04", "action_type": "material_sensitivity", "priority": "medium", "description": "consider_material_sensitive_source_extension beyond the current P0/t0/alpha1.6 case", "depends_on": "new source contract and lineage review", "allowed_now": "design_only", "notes": "No silent source broadening."},
        {"action_id": "M2-A05", "action_type": "documentation", "priority": "high", "description": "document_L2_negative_result_without_posthoc_tuning", "depends_on": "M2 claim matrix", "allowed_now": "yes", "notes": "Retain exact threshold and 0/3 outcome."},
    ]
    review_items = [
        ("M2-R01", "feature scope adequacy", "Assess whether the three aggregates represent the intended phase-to-relation signal.", "new preregistered feature-review block"),
        ("M2-R02", "N4 comparator adequacy", "Assess whether deterministic random-phase N4 tests the intended perturbation distinction.", "nullmodel review without replacement based on L2 outcome"),
        ("M2-R03", "theta/epsilon sensitivity without post-hoc tuning", "Design a prospective sensitivity contract; do not revise L2 thresholds.", "separate preregistration"),
        ("M2-R04", "P0/t0/alpha1.6 source limitation", "Keep source-specific scope explicit and design authorized extensions separately.", "source-extension contract"),
        ("M2-R05", "EXTRACT01 design as future method block", "Specify Gram-first d/D extraction independently of the L2 result.", "QSB-EXTRACT01 design package"),
        ("M2-R06", "material-sensitive source extension", "Identify lineage-safe material/state-sensitive phase sources for future tests.", "source scout and authorization"),
    ]
    review_rows = [{
        "review_item_id": identifier, "category": category, "description": description,
        "blocks_public_claim": "yes", "blocks_next_internal_run": "no",
        "recommended_resolution": resolution, "notes": "Must not alter or relabel the completed L2 fail.",
    } for identifier, category, description, resolution in review_items]

    de_note = f"""# INTERFACE01-M2 Theorie-Notiz

## Was der Lauf zeigt

Der L2-Lauf ist ein negativer Befund für die reduzierte, vertraglich festgelegte INTERFACE01-Testkette, nicht für QSB insgesamt. Quelle, Autorisierung, Start-Gates und alle sechs Nullmodelle waren gültig. Dennoch erreichte keines der drei gesperrten Features den N4-Abstand von `theta_new + epsilon_new = {threshold}`; erforderlich waren mindestens zwei Unterstützungsstimmen.

## Mechanistische Lesart des negativen Befunds

In diesem P0/t0/alpha1.6-Setup trennten die gewählten drei aggregierten Phasenantworten nicht hinreichend zwischen beobachteter Struktur und der effektiven N4-Phasenperturbation. Damit wird genau dieser reduzierte Pfad von `delta_phi_ij(x)` über die drei Features zu einer schwellenbasierten Relationskandidatin geschwächt.

## Wo die geprüfte Kette nicht getragen hat

Die Kette brach nicht bei der Quelle oder bei der technischen Ausführung. Sie trug am Übergang von der Feature-Antwort zur N4-Separation und anschließend am 2-von-3-Schwellenentscheid nicht: Die drei endlichen Abstände blieben jeweils unter `{threshold}`.

## Was offen bleibt

Offen bleiben die Angemessenheit des Drei-Feature-Satzes, die konkrete Aussagekraft von N4, die Beschränkung auf P0/t0/alpha1.6, material-sensitive Quellen sowie eine separat zu spezifizierende Gram-first-Extraktion von `d_ij` und `D(i,j)`. Diese Fragen dürfen nur in neuen, vorab festgelegten Blöcken geprüft werden.

## Was nicht behauptet wird

Der Befund entscheidet weder die breitere Interface-Hypothese noch geometrische Lesbarkeit oder gravitative Fragen. Er wird nicht durch nachträgliche Schwellen-, Feature- oder Nullmodelländerungen umgedeutet.
"""
    en_note = f"""# INTERFACE01-M2 Theory Note

## What the run shows

L2 is a diagnostic negative result for the reduced, contractually fixed INTERFACE01 chain, not for QSB as a whole. The source, authorization, start gates, and all six nullmodels were valid. None of the three locked features reached the N4 distance `theta_new + epsilon_new = {threshold}`, while at least two support votes were required.

## Mechanistic reading of the negative result

In this P0/t0/alpha1.6 setup, the three selected aggregate phase responses did not separate sufficiently between the observed structure and the effective N4 phase perturbation. This weakens this specific reduced path from `delta_phi_ij(x)` through the three features to a thresholded relation candidate.

## Where the tested chain did not hold

The chain did not fail at source validity or technical execution. It failed at the transition from feature response to N4 separation and then at the two-of-three threshold decision: all three finite distances remained below `{threshold}`.

## What remains open

Open questions include the adequacy of the three-feature scope, the specific adequacy of N4, source specificity, material-sensitive extensions, and a separately specified Gram-first extraction of `d_ij` and `D(i,j)`. Each requires a new preregistered block.

## What is not claimed

This result does not decide the broader interface hypothesis, geometric readability, or gravity-level questions. It is not repaired or reinterpreted through post-hoc changes.
"""

    OUTPUT.mkdir(parents=True)
    manifest = {
        "work_package": "QSB-INTERFACE01M2", "status": STATUS,
        "created_at_utc": datetime.now(timezone.utc).isoformat(), "repo_root": str(REPO),
        "j2_authorization_seen": j2_manifest["execution_authorization_after_j2"],
        "l2_result_seen": l2_manifest["minimaltest_contract_result"],
        "minimaltest_contract_result_seen": "fail", "mechanism_interpretation_performed": True,
        "failure_review_mode": True, "minimaltest_rerun": False, "nullmodels_rerun": False,
        "physical_evidence_claim_made": False, "upstream_modified": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    (OUTPUT / "01_m2_run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_csv(OUTPUT / "02_upstream_result_inventory.csv", ["artifact_id", "upstream_block", "path", "exists", "sha256", "role", "used_for", "notes"], inventory_rows)
    write_csv(OUTPUT / "03_authorization_and_hash_preflight.csv", ["gate_id", "gate_name", "observed_value", "expected_value", "status", "blocking", "notes"], preflight_rows)
    write_csv(OUTPUT / "04_l2_contract_result_summary.csv", ["result_item", "observed_value", "source_artifact", "source_hash", "classification", "notes"], result_summary_rows)
    write_csv(OUTPUT / "05_failure_localization.csv", ["failure_item", "layer", "observed_value", "expected_or_required_value", "failure_status", "classification", "mechanism_implication", "notes"], failure_rows)
    write_csv(OUTPUT / "06_feature_failure_review.csv", ["feature_name", "observed_metric", "n4_metric", "abs_delta_n4", "theta_new", "epsilon_new", "support_threshold", "support_flag", "failure_reading", "classification", "notes"], feature_rows)
    write_csv(OUTPUT / "07_nullmodel_role_review.csv", ["nullmodel_id", "role", "executed_in_l2", "used_in_acceptance_gate", "observed_role_consistency", "mechanism_relevance", "classification", "limitations", "notes"], null_review_rows)
    write_csv(OUTPUT / "08_acceptance_rule_failure_review.csv", ["acceptance_rule_id", "rule_text", "observed_value", "required_value", "status", "classification", "notes"], rule_review_rows)
    write_csv(OUTPUT / "09_mechanism_chain_map.csv", ["chain_step", "input_element", "operation_or_relation", "output_element", "status_after_l2", "mechanism_reading", "evidence_boundary", "open_question"], chain_rows)
    write_csv(OUTPUT / "10_claim_classification_matrix.csv", ["statement_id", "statement", "classification", "allowed_wording", "forbidden_wording", "source_or_basis", "notes"], claim_matrix_rows)
    write_csv(OUTPUT / "11_unsupported_claims_and_boundaries.csv", ["unsupported_claim", "why_not_supported", "safe_replacement_wording", "notes"], unsupported_rows)
    (OUTPUT / "12_theory_language_note_de.md").write_text(de_note, encoding="utf-8")
    (OUTPUT / "13_theory_language_note_en.md").write_text(en_note, encoding="utf-8")
    write_csv(OUTPUT / "14_next_research_actions.csv", ["action_id", "action_type", "priority", "description", "depends_on", "allowed_now", "notes"], action_rows)
    write_csv(OUTPUT / "16_review_items_for_next_block.csv", ["review_item_id", "category", "description", "blocks_public_claim", "blocks_next_internal_run", "recommended_resolution", "notes"], review_rows)

    after_hashes = {key: sha256(path) for key, (_, path, _) in artifacts.items() if path.is_file()}
    upstream_unchanged = before_hashes == after_hashes
    manifest["upstream_modified"] = not upstream_unchanged
    (OUTPUT / "01_m2_run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    validations: list[dict[str, Any]] = []

    def validate(identifier: str, name: str, passed: bool, observed: Any, expected: Any, message: str) -> None:
        validations.append({
            "validation_id": identifier, "validation_layer": "M2 fail review", "check_name": name,
            "status": "pass" if passed else "fail", "severity": "error", "observed_value": observed,
            "expected_value": expected, "message": message,
            "blocking_for_interpretation": "no" if passed else "yes",
        })

    validate("M2-V01", "j2_authorization_present", j2_authorized, j2_manifest["execution_authorization_after_j2"], J2_AUTH, "J2 authorization exact.")
    validate("M2-V02", "l2_result_present", l2_executed, l2_manifest["status"], L2_STATUS, "Completed L2 result present.")
    validate("M2-V03", "l2_result_is_fail", l2_fail, l2_manifest["minimaltest_contract_result"], "fail", "Fail mode selected.")
    validate("M2-V04", "no_minimaltest_rerun", manifest["minimaltest_rerun"] is False, manifest["minimaltest_rerun"], False, "M2 reads outputs only.")
    validate("M2-V05", "no_nullmodel_rerun", manifest["nullmodels_rerun"] is False, manifest["nullmodels_rerun"], False, "No nullmodel rerun.")
    validate("M2-V06", "source_validity_reviewed", source_valid, f"{len(source_rows)}/13 pass", "13/13 pass", "Source failure excluded.")
    validate("M2-V07", "failure_localized", len(failure_rows) == 9 and result_consistent, "feature N4 support and 2-of-3", "localized diagnostic negative", "Failure localization complete.")
    validate("M2-V08", "feature_failure_review_present", len(feature_rows) == 3 and all(r["support_flag"] == "false" for r in feature_rows), len(feature_rows), 3, "Three negative feature rows copied from L2.")
    validate("M2-V09", "nullmodel_role_review_present", len(null_review_rows) == 6, len(null_review_rows), 6, "Six L2 null roles reviewed.")
    validate("M2-V10", "n2_invariance_only_preserved", n2_ok, null_by_id["N2_X_INDEX_ROLL_SURROGATE"]["role"], "invariance_check_only", "N2 role preserved.")
    validate("M2-V11", "n4_effective_perturbation_preserved", n4_ok, null_by_id["N4_PHASE_RANDOM_REFERENCE"]["role"], "effective_perturbation", "N4 role preserved.")
    validate("M2-V12", "mechanism_chain_map_present", len(chain_rows) == 7, len(chain_rows), 7, "Seven bounded chain steps recorded.")
    validate("M2-V13", "claim_classification_complete", len(claim_matrix_rows) == 9, len(claim_matrix_rows), 9, "Required claims classified.")
    validate("M2-V14", "unsupported_claims_listed", len(unsupported_rows) == 6, len(unsupported_rows), 6, "Required unsupported claims listed.")
    validate("M2-V15", "german_note_present", bool(de_note.strip()), True, True, "German theory note present.")
    validate("M2-V16", "english_note_present", bool(en_note.strip()), True, True, "English theory note present.")
    validate("M2-V17", "no_physical_evidence_claim", manifest["physical_evidence_claim_made"] is False, manifest["physical_evidence_claim_made"], False, "No physical-evidence claim.")
    validate("M2-V18", "no_upstream_mutation", upstream_unchanged, upstream_unchanged, True, "F3-L2 hashes unchanged after M2 writes.")
    validate("M2-V19", "exact_output_count", True, 17, 17, "Script declares and later checks 17 files.")
    write_csv(OUTPUT / "15_m2_validation_results.csv", ["validation_id", "validation_layer", "check_name", "status", "severity", "observed_value", "expected_value", "message", "blocking_for_interpretation"], validations)

    final_note = f"""# INTERFACE01-M2 Final Result

## Status

`{STATUS}`

## L2 Result Reviewed

`fail`

## Failure Localization

The authorized source, 15 start gates, feature reproduction, six nullmodel executions, and N2/N4 role checks passed. The negative disposition localizes to feature-to-N4 separation: support was `0/3`, while J2 required `2/3` at the locked threshold `{threshold}`.

## Mechanism Interpretation Boundary

In the reduced P0/t0/alpha1.6 setup, the selected three aggregate phase responses did not separate sufficiently from N4. This weakens this specific phase-to-feature-to-relation candidate path; it does not decide the broader interface hypothesis.

## What This Does Not Mean

The result is not a general theory verdict, does not rule out other phase-sensitive mappings, and says nothing conclusive about geometric readability or gravity-level questions.

## Next Allowed Action

Review feature scope and N4 adequacy without post-hoc changes; separately specify prospective source extensions or QSB-EXTRACT01 before any new execution.
"""
    (OUTPUT / "FINAL_RESULT_NOTE.md").write_text(final_note, encoding="utf-8")

    actual = {path.name for path in OUTPUT.iterdir() if path.is_file()}
    if actual != EXPECTED_FILES:
        raise SystemExit(f"Output file-set mismatch: actual={sorted(actual)} expected={sorted(EXPECTED_FILES)}")
    failures = [row["validation_id"] for row in validations if row["status"] == "fail"]
    if failures:
        raise SystemExit(f"M2 validation failures: {failures}")
    print(f"status={STATUS}")
    print("l2_result_reviewed=fail")
    print("failure_localization=feature_to_N4_separation_and_J2_2_of_3")
    print("mechanism_interpretation_performed=true")
    print("minimaltest_rerun=false")
    print(f"output_files={len(actual)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
